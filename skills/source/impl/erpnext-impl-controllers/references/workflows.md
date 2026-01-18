# Controller Implementation Workflows

Extended patterns for common implementation scenarios.

## Workflow 1: Field Validation

### Simple Required Field

```python
def validate(self):
    if not self.customer:
        frappe.throw(_("Customer is required"))
```

### Conditional Required Field

```python
def validate(self):
    if self.is_recurring and not self.end_date:
        frappe.throw(_("End Date is required for recurring documents"))
```

### Cross-Field Validation

```python
def validate(self):
    if self.from_date and self.to_date:
        if self.from_date > self.to_date:
            frappe.throw(_("From Date cannot be after To Date"))
```

### Link Field Validation

```python
def validate(self):
    if self.customer:
        customer = frappe.get_cached_doc("Customer", self.customer)
        if customer.disabled:
            frappe.throw(_("Customer {0} is disabled").format(self.customer))
```

### Child Table Validation

```python
def validate(self):
    if not self.items:
        frappe.throw(_("At least one item is required"))
    
    for item in self.items:
        if item.qty <= 0:
            frappe.throw(_("Quantity must be greater than 0 for item {0}").format(item.item_code))
```

## Workflow 2: Auto-Calculations

### Sum Child Table

```python
def validate(self):
    self.total = sum(item.amount for item in self.items)
    self.total_qty = sum(item.qty for item in self.items)
```

### Calculate with Tax

```python
def validate(self):
    self.net_total = sum(item.amount for item in self.items)
    self.tax_amount = self.net_total * (self.tax_rate / 100)
    self.grand_total = self.net_total + self.tax_amount
```

### Calculate Child Row Values

```python
def validate(self):
    for item in self.items:
        item.amount = item.qty * item.rate
        item.net_amount = item.amount - (item.discount_amount or 0)
```

### Running Totals

```python
def validate(self):
    running_total = 0
    for item in self.items:
        running_total += item.amount
        item.running_total = running_total
```

## Workflow 3: Change Detection

### Detect Specific Field Change

```python
def validate(self):
    old_doc = self.get_doc_before_save()
    if old_doc and old_doc.status != self.status:
        self.status_changed_on = frappe.utils.now()
        self.flags.status_changed = True
```

### Track Multiple Fields

```python
def validate(self):
    old_doc = self.get_doc_before_save()
    if not old_doc:
        return  # New document
    
    changed_fields = []
    for field in ['status', 'priority', 'assigned_to']:
        if getattr(old_doc, field) != getattr(self, field):
            changed_fields.append(field)
    
    if changed_fields:
        self.flags.changed_fields = changed_fields
```

### Log Changes

```python
def on_update(self):
    old_doc = self.get_doc_before_save()
    if not old_doc:
        return
    
    changes = []
    for field in ['status', 'priority']:
        old_val = getattr(old_doc, field)
        new_val = getattr(self, field)
        if old_val != new_val:
            changes.append(f"{field}: {old_val} → {new_val}")
    
    if changes:
        self.add_comment("Edit", "\n".join(changes))
```

## Workflow 4: Notifications

### Email on Status Change

```python
def on_update(self):
    old_doc = self.get_doc_before_save()
    if old_doc and old_doc.status != self.status:
        self.send_status_notification()

def send_status_notification(self):
    frappe.sendmail(
        recipients=[self.owner],
        subject=f"{self.doctype} {self.name} status changed to {self.status}",
        message=f"Your document status has been updated to {self.status}."
    )
```

### Background Email (Non-blocking)

```python
def on_update(self):
    if self.flags.get('status_changed'):
        frappe.enqueue(
            'myapp.notifications.send_status_email',
            queue='short',
            doc_name=self.name,
            doctype=self.doctype
        )
```

## Workflow 5: Linked Documents

### Update Parent on Child Change

```python
# In child document controller
def on_update(self):
    if self.parent and self.parenttype:
        parent_doc = frappe.get_doc(self.parenttype, self.parent)
        parent_doc.run_method('update_totals')
        parent_doc.save()
```

### Create Related Document

```python
def after_insert(self):
    # Create Task when Project is created
    task = frappe.get_doc({
        "doctype": "Task",
        "subject": f"Initial setup for {self.name}",
        "project": self.name,
        "status": "Open"
    })
    task.insert(ignore_permissions=True)
```

### Sync Status to Linked Docs

```python
def on_update(self):
    old_doc = self.get_doc_before_save()
    if old_doc and old_doc.status != self.status:
        # Update all linked documents
        linked_docs = frappe.get_all(
            "Related DocType",
            filters={"parent_doc": self.name},
            pluck="name"
        )
        for doc_name in linked_docs:
            frappe.db.set_value("Related DocType", doc_name, 
                              "parent_status", self.status)
```

## Workflow 6: Custom Naming

### Prefix Based on Field

```python
from frappe.model.naming import getseries

def autoname(self):
    # P-CUST-001 or P-SUPP-001
    type_prefix = "CUST" if self.party_type == "Customer" else "SUPP"
    prefix = f"P-{type_prefix}-"
    self.name = getseries(prefix, 3)
```

### Date-Based Naming

```python
def autoname(self):
    year = frappe.utils.getdate(self.posting_date).year
    prefix = f"INV-{year}-"
    self.name = getseries(prefix, 5)  # INV-2025-00001
```

### Name from Multiple Fields

```python
def autoname(self):
    # Format: CUSTOMER-ITEM-001
    customer_code = self.customer[:3].upper()
    item_code = self.item[:3].upper()
    prefix = f"{customer_code}-{item_code}-"
    self.name = getseries(prefix, 3)
```

### Conditional Naming Series

```python
def before_naming(self):
    if self.is_priority:
        self.naming_series = "PRIORITY-.#####"
    else:
        self.naming_series = "STD-.#####"
```

## Workflow 7: Submittable Documents

### Complete Submittable Implementation

```python
class PurchaseOrder(Document):
    def validate(self):
        self.validate_items()
        self.calculate_totals()
    
    def validate_items(self):
        if not self.items:
            frappe.throw(_("Items are required"))
    
    def calculate_totals(self):
        self.total = sum(item.amount for item in self.items)
    
    def before_submit(self):
        # Validations only needed at submit time
        if self.total > 100000 and not self.manager_approval:
            frappe.throw(_("Manager approval required for POs over 100,000"))
        
        if not self.supplier_quotation:
            frappe.throw(_("Supplier Quotation reference is required"))
    
    def on_submit(self):
        # Actions that happen on submit
        self.update_ordered_qty()
        self.create_purchase_receipt_draft()
    
    def before_cancel(self):
        # Prevent cancel if conditions not met
        if self.has_linked_invoices():
            frappe.throw(_("Cannot cancel - linked invoices exist"))
    
    def on_cancel(self):
        # Reverse submit actions
        self.reverse_ordered_qty()
    
    def has_linked_invoices(self):
        return frappe.db.exists("Purchase Invoice", {
            "purchase_order": self.name,
            "docstatus": 1
        })
```

## Workflow 8: Controller Override

### Override with Custom Validation

```python
# hooks.py
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice"
}

# myapp/overrides.py
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # ALWAYS call parent first
        super().validate()
        
        # Then add custom logic
        self.validate_credit_limit()
        self.apply_custom_discounts()
    
    def validate_credit_limit(self):
        if not self.customer:
            return
        
        credit_limit = frappe.db.get_value("Customer", self.customer, "credit_limit")
        if credit_limit and self.outstanding_amount > credit_limit:
            frappe.throw(_("Credit limit exceeded"))
    
    def apply_custom_discounts(self):
        # Custom discount logic
        pass
```

### Add Method Without Override

```python
# hooks.py
doc_events = {
    "Sales Invoice": {
        "validate": "myapp.events.si_validate",
        "on_submit": "myapp.events.si_on_submit"
    }
}

# myapp/events.py
def si_validate(doc, method=None):
    """Additional validation for Sales Invoice"""
    validate_territory_discount(doc)

def si_on_submit(doc, method=None):
    """Additional actions on submit"""
    create_commission_record(doc)

def validate_territory_discount(doc):
    # Custom logic
    pass

def create_commission_record(doc):
    # Custom logic
    pass
```

## Workflow 9: Background Jobs

### Queue Heavy Operations

```python
def on_update(self):
    if self.requires_heavy_processing():
        frappe.enqueue(
            'myapp.tasks.process_document',
            queue='long',
            timeout=600,
            doc_name=self.name
        )

# myapp/tasks.py
def process_document(doc_name):
    doc = frappe.get_doc("MyDocType", doc_name)
    # Heavy processing here
    doc.processed = 1
    doc.db_update()
```

### Queue with Deduplication

```python
def on_update(self):
    frappe.enqueue(
        'myapp.tasks.sync_to_external',
        queue='default',
        job_id=f"sync_{self.doctype}_{self.name}",  # v15+ job_id, v14 job_name
        doc_name=self.name,
        deduplicate=True
    )
```

## Workflow 10: Permissions in Controller

### Check Permission Before Action

```python
def on_submit(self):
    if self.grand_total > 50000:
        if not frappe.has_permission(self.doctype, "submit", 
                                    user=frappe.session.user):
            frappe.throw(_("Not permitted to submit high-value documents"))
```

### Bypass Permissions (Use Carefully)

```python
def after_insert(self):
    # Create system document regardless of user permissions
    task = frappe.get_doc({
        "doctype": "Task",
        "subject": f"Follow up on {self.name}"
    })
    task.flags.ignore_permissions = True
    task.insert()
```
