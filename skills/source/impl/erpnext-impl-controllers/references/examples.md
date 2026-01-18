# Controller Examples

Complete working examples for common use cases.

## Example 1: Basic Document Controller

**Scenario**: Custom Employee Leave Request

```python
# apps/myapp/myapp/hr/doctype/leave_request/leave_request.py

import frappe
from frappe import _
from frappe.model.document import Document

class LeaveRequest(Document):
    def validate(self):
        self.validate_dates()
        self.calculate_days()
        self.check_balance()
    
    def validate_dates(self):
        if self.from_date > self.to_date:
            frappe.throw(_("From Date cannot be after To Date"))
        
        if frappe.utils.getdate(self.from_date) < frappe.utils.today():
            frappe.throw(_("Cannot apply for past dates"))
    
    def calculate_days(self):
        self.total_days = frappe.utils.date_diff(self.to_date, self.from_date) + 1
    
    def check_balance(self):
        balance = self.get_leave_balance()
        if self.total_days > balance:
            frappe.throw(_("Insufficient leave balance. Available: {0}").format(balance))
    
    def get_leave_balance(self):
        # Simplified balance calculation
        return frappe.db.get_value("Leave Allocation", 
            {"employee": self.employee, "leave_type": self.leave_type},
            "total_leaves_allocated") or 0
    
    def on_update(self):
        self.notify_manager()
    
    def notify_manager(self):
        manager = frappe.db.get_value("Employee", self.employee, "reports_to")
        if manager:
            manager_user = frappe.db.get_value("Employee", manager, "user_id")
            if manager_user:
                frappe.sendmail(
                    recipients=[manager_user],
                    subject=_("Leave Request from {0}").format(self.employee_name),
                    message=_("Leave request for {0} days from {1} to {2}").format(
                        self.total_days, self.from_date, self.to_date
                    )
                )
```

## Example 2: Submittable Document

**Scenario**: Expense Claim with Approval Workflow

```python
# apps/myapp/myapp/expense/doctype/expense_claim/expense_claim.py

import frappe
from frappe import _
from frappe.model.document import Document

class ExpenseClaim(Document):
    def validate(self):
        self.validate_amounts()
        self.calculate_totals()
        self.set_status()
    
    def validate_amounts(self):
        for item in self.expenses:
            if item.amount <= 0:
                frappe.throw(_("Amount must be positive for row {0}").format(item.idx))
            
            # Validate receipt for amounts over threshold
            if item.amount > 500 and not item.receipt:
                frappe.throw(_("Receipt required for amounts over 500 in row {0}").format(item.idx))
    
    def calculate_totals(self):
        self.total_amount = sum(item.amount for item in self.expenses)
        self.total_approved = sum(item.approved_amount or 0 for item in self.expenses)
    
    def set_status(self):
        if self.docstatus == 0:
            self.status = "Draft"
        elif self.docstatus == 1:
            if self.total_approved == self.total_amount:
                self.status = "Approved"
            elif self.total_approved > 0:
                self.status = "Partially Approved"
            else:
                self.status = "Submitted"
        elif self.docstatus == 2:
            self.status = "Cancelled"
    
    def before_submit(self):
        # Validation only at submit time
        if self.total_amount > 5000 and not self.manager_approval:
            frappe.throw(_("Manager approval required for claims over 5,000"))
    
    def on_submit(self):
        self.create_journal_entry()
        self.update_employee_advance()
    
    def create_journal_entry(self):
        if self.total_approved > 0:
            je = frappe.get_doc({
                "doctype": "Journal Entry",
                "voucher_type": "Expense Claim",
                "posting_date": self.posting_date,
                "accounts": [
                    {
                        "account": self.expense_account,
                        "debit_in_account_currency": self.total_approved
                    },
                    {
                        "account": self.payable_account,
                        "credit_in_account_currency": self.total_approved,
                        "party_type": "Employee",
                        "party": self.employee
                    }
                ]
            })
            je.flags.ignore_permissions = True
            je.submit()
            
            # Store reference (using db_set since we're in on_submit)
            frappe.db.set_value(self.doctype, self.name, "journal_entry", je.name)
    
    def update_employee_advance(self):
        if self.advance_reference:
            frappe.db.set_value("Employee Advance", self.advance_reference,
                              "claimed_amount", self.total_approved)
    
    def before_cancel(self):
        if self.journal_entry:
            je_status = frappe.db.get_value("Journal Entry", self.journal_entry, "docstatus")
            if je_status == 1:
                frappe.throw(_("Cancel the Journal Entry {0} first").format(self.journal_entry))
    
    def on_cancel(self):
        # Reset employee advance
        if self.advance_reference:
            frappe.db.set_value("Employee Advance", self.advance_reference,
                              "claimed_amount", 0)
```

## Example 3: Auto-Naming Controller

**Scenario**: Project with Custom Naming

```python
# apps/myapp/myapp/projects/doctype/project/project.py

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import getseries

class Project(Document):
    def autoname(self):
        """
        Naming format: PRJ-{CUSTOMER_CODE}-{YEAR}-{SERIAL}
        Example: PRJ-ABC-2025-001
        """
        customer_code = self.get_customer_code()
        year = frappe.utils.getdate(self.start_date or frappe.utils.today()).year
        prefix = f"PRJ-{customer_code}-{year}-"
        self.name = getseries(prefix, 3)
    
    def get_customer_code(self):
        if not self.customer:
            return "GEN"
        
        # Get existing code or generate from name
        code = frappe.db.get_value("Customer", self.customer, "customer_code")
        if code:
            return code[:3].upper()
        
        # Generate from customer name
        return self.customer[:3].upper().replace(" ", "")
    
    def validate(self):
        self.validate_dates()
        self.set_percent_complete()
    
    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                frappe.throw(_("Start Date cannot be after End Date"))
    
    def set_percent_complete(self):
        if self.tasks:
            completed = sum(1 for t in self.tasks if t.status == "Completed")
            self.percent_complete = (completed / len(self.tasks)) * 100
        else:
            self.percent_complete = 0
```

## Example 4: Change Detection with Audit

**Scenario**: Contract with Change Logging

```python
# apps/myapp/myapp/legal/doctype/contract/contract.py

import frappe
from frappe import _
from frappe.model.document import Document

class Contract(Document):
    # Fields to track for changes
    TRACKED_FIELDS = ['status', 'contract_value', 'end_date', 'party']
    
    def validate(self):
        self.detect_changes()
        self.validate_contract_value()
    
    def detect_changes(self):
        """Detect and flag important field changes"""
        old_doc = self.get_doc_before_save()
        if not old_doc:
            self.flags.is_new = True
            return
        
        changes = []
        for field in self.TRACKED_FIELDS:
            old_val = getattr(old_doc, field)
            new_val = getattr(self, field)
            if old_val != new_val:
                changes.append({
                    'field': field,
                    'old': old_val,
                    'new': new_val
                })
        
        if changes:
            self.flags.changes = changes
            # Special flag for critical changes
            if any(c['field'] == 'contract_value' for c in changes):
                self.flags.value_changed = True
    
    def validate_contract_value(self):
        if self.contract_value and self.contract_value < 0:
            frappe.throw(_("Contract value cannot be negative"))
    
    def on_update(self):
        self.log_changes()
        self.notify_on_critical_change()
    
    def log_changes(self):
        """Create audit log entry for tracked changes"""
        if not self.flags.get('changes'):
            return
        
        change_log = []
        for change in self.flags.changes:
            change_log.append(
                f"{frappe.bold(change['field'])}: {change['old']} → {change['new']}"
            )
        
        self.add_comment("Edit", "<br>".join(change_log))
    
    def notify_on_critical_change(self):
        """Notify legal team on contract value change"""
        if not self.flags.get('value_changed'):
            return
        
        for change in self.flags.changes:
            if change['field'] == 'contract_value':
                frappe.sendmail(
                    recipients=["legal@company.com"],
                    subject=f"Contract Value Changed: {self.name}",
                    message=f"Contract value changed from {change['old']} to {change['new']}"
                )
                break
```

## Example 5: Controller Override

**Scenario**: Extend Sales Invoice with Custom Discount

```python
# hooks.py
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.sales_invoice.CustomSalesInvoice"
}

# apps/myapp/myapp/overrides/sales_invoice.py

import frappe
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # ALWAYS call parent first
        super().validate()
        
        # Then custom logic
        self.apply_loyalty_discount()
        self.validate_credit_limit()
    
    def apply_loyalty_discount(self):
        """Apply automatic discount based on customer loyalty tier"""
        if not self.customer:
            return
        
        loyalty_tier = frappe.db.get_value("Customer", self.customer, "loyalty_tier")
        discount_map = {
            "Gold": 10,
            "Silver": 5,
            "Bronze": 2
        }
        
        discount_percent = discount_map.get(loyalty_tier, 0)
        if discount_percent and not self.loyalty_discount_applied:
            self.additional_discount_percentage = discount_percent
            self.loyalty_discount_applied = 1
    
    def validate_credit_limit(self):
        """Custom credit limit validation"""
        if not self.customer or self.is_return:
            return
        
        credit_limit = frappe.db.get_value("Customer", self.customer, "credit_limit") or 0
        if not credit_limit:
            return
        
        # Get outstanding including this invoice
        outstanding = self.get_customer_outstanding()
        if outstanding + self.grand_total > credit_limit:
            frappe.throw(
                _("Credit limit ({0}) exceeded. Outstanding: {1}, This invoice: {2}").format(
                    credit_limit, outstanding, self.grand_total
                )
            )
    
    def get_customer_outstanding(self):
        return frappe.db.sql("""
            SELECT SUM(outstanding_amount)
            FROM `tabSales Invoice`
            WHERE customer = %s AND docstatus = 1 AND name != %s
        """, (self.customer, self.name))[0][0] or 0
    
    def on_submit(self):
        # Call parent first
        super().on_submit()
        
        # Custom actions
        self.update_loyalty_points()
    
    def update_loyalty_points(self):
        """Award loyalty points on invoice submission"""
        if not self.customer:
            return
        
        points = int(self.grand_total / 100)  # 1 point per 100
        if points > 0:
            frappe.db.set_value(
                "Customer", self.customer, "loyalty_points",
                frappe.db.get_value("Customer", self.customer, "loyalty_points") + points
            )
```

## Example 6: Virtual DocType

**Scenario**: API-backed Document

```python
# apps/myapp/myapp/integrations/doctype/external_product/external_product.py

import frappe
from frappe import _
from frappe.model.document import Document
import requests

class ExternalProduct(Document):
    """Virtual DocType that reads from external API"""
    
    @staticmethod
    def get_list(args):
        """Return list of products from external API"""
        response = requests.get(
            "https://api.external.com/products",
            headers={"Authorization": f"Bearer {get_api_key()}"}
        )
        
        if response.status_code != 200:
            frappe.throw(_("Failed to fetch products from external API"))
        
        products = response.json()
        return [frappe._dict(p) for p in products]
    
    @staticmethod
    def get_count(args):
        """Return count of products"""
        products = ExternalProduct.get_list(args)
        return len(products)
    
    def load_from_db(self):
        """Load single product from API"""
        response = requests.get(
            f"https://api.external.com/products/{self.name}",
            headers={"Authorization": f"Bearer {get_api_key()}"}
        )
        
        if response.status_code != 200:
            frappe.throw(_("Product not found"))
        
        data = response.json()
        super(Document, self).__init__(data)
    
    def db_insert(self, *args, **kwargs):
        """Create product in external API"""
        data = self.get_valid_dict(convert_dates_to_str=True)
        response = requests.post(
            "https://api.external.com/products",
            json=data,
            headers={"Authorization": f"Bearer {get_api_key()}"}
        )
        
        if response.status_code != 201:
            frappe.throw(_("Failed to create product"))
        
        result = response.json()
        self.name = result.get('id')
    
    def db_update(self, *args, **kwargs):
        """Update product in external API"""
        data = self.get_valid_dict(convert_dates_to_str=True)
        response = requests.put(
            f"https://api.external.com/products/{self.name}",
            json=data,
            headers={"Authorization": f"Bearer {get_api_key()}"}
        )
        
        if response.status_code != 200:
            frappe.throw(_("Failed to update product"))

def get_api_key():
    return frappe.db.get_single_value("External API Settings", "api_key")
```

## Example 7: Tree DocType Controller

**Scenario**: Organization Hierarchy

```python
# apps/myapp/myapp/org/doctype/department/department.py

import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet

class Department(NestedSet):
    # Required for NestedSet
    nsm_parent_field = "parent_department"
    
    def validate(self):
        self.validate_parent()
        self.set_full_path()
    
    def validate_parent(self):
        """Prevent circular references"""
        if self.parent_department:
            if self.parent_department == self.name:
                frappe.throw(_("Department cannot be its own parent"))
            
            # Check for circular reference
            parent = self.parent_department
            visited = set()
            while parent:
                if parent in visited:
                    frappe.throw(_("Circular reference detected"))
                visited.add(parent)
                parent = frappe.db.get_value("Department", parent, "parent_department")
    
    def set_full_path(self):
        """Set full path like Company > Division > Department"""
        path_parts = [self.department_name]
        parent = self.parent_department
        
        while parent:
            parent_name = frappe.db.get_value("Department", parent, "department_name")
            path_parts.insert(0, parent_name)
            parent = frappe.db.get_value("Department", parent, "parent_department")
        
        self.full_path = " > ".join(path_parts)
    
    def on_update(self):
        """Update children when parent changes"""
        # NestedSet handles lft/rgt automatically
        self.update_children_paths()
    
    def update_children_paths(self):
        """Recursively update full_path for all children"""
        for child in self.get_children():
            child_doc = frappe.get_doc("Department", child.name)
            child_doc.set_full_path()
            frappe.db.set_value("Department", child.name, "full_path", child_doc.full_path)
            child_doc.update_children_paths()
    
    def on_trash(self):
        """Prevent delete if has employees"""
        employee_count = frappe.db.count("Employee", {"department": self.name})
        if employee_count:
            frappe.throw(
                _("Cannot delete department with {0} employees").format(employee_count)
            )
```

## Example 8: Whitelisted Methods

**Scenario**: Controller with Client-Callable Methods

```python
# apps/myapp/myapp/sales/doctype/quotation/quotation.py

import frappe
from frappe import _
from frappe.model.document import Document

class Quotation(Document):
    def validate(self):
        self.calculate_totals()
    
    def calculate_totals(self):
        self.total = sum(item.amount for item in self.items)
    
    @frappe.whitelist()
    def apply_discount(self, discount_percent):
        """
        Apply discount and return updated totals.
        Called from client: frm.call('apply_discount', {discount_percent: 10})
        """
        if discount_percent < 0 or discount_percent > 100:
            frappe.throw(_("Discount must be between 0 and 100"))
        
        discount_amount = self.total * (discount_percent / 100)
        self.discount_amount = discount_amount
        self.grand_total = self.total - discount_amount
        
        # Save changes
        self.save()
        
        return {
            "discount_amount": self.discount_amount,
            "grand_total": self.grand_total
        }
    
    @frappe.whitelist()
    def get_available_items(self, warehouse=None):
        """
        Get items with stock availability.
        Called from client for item selection.
        """
        filters = {"is_sales_item": 1, "disabled": 0}
        
        items = frappe.get_all(
            "Item",
            filters=filters,
            fields=["name", "item_name", "stock_uom"]
        )
        
        if warehouse:
            for item in items:
                item['available_qty'] = frappe.db.get_value(
                    "Bin",
                    {"item_code": item['name'], "warehouse": warehouse},
                    "actual_qty"
                ) or 0
        
        return items
    
    @frappe.whitelist()
    def create_sales_order(self):
        """
        Convert quotation to sales order.
        Called from client button.
        """
        if self.docstatus != 1:
            frappe.throw(_("Quotation must be submitted"))
        
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": self.party_name,
            "quotation": self.name,
            "items": [
                {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "rate": item.rate
                }
                for item in self.items
            ]
        })
        so.insert()
        
        return so.name
```

**Client-side usage:**

```javascript
// Apply discount
frm.call('apply_discount', {discount_percent: 10}).then(r => {
    frm.reload_doc();
});

// Get available items
frm.call('get_available_items', {warehouse: 'Main Warehouse'}).then(r => {
    console.log(r.message);  // [{name: 'ITEM-001', available_qty: 50}, ...]
});

// Create sales order
frm.call('create_sales_order').then(r => {
    frappe.set_route('Form', 'Sales Order', r.message);
});
```
