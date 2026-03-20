# Examples Reference

Complete werkende voorbeelden van Document Controllers.

## Inhoudsopgave

1. [Basis Controller](#basis-controller)
2. [Submittable Controller](#submittable-controller)
3. [Controller Override](#controller-override)
4. [Virtual DocType Controller](#virtual-doctype-controller)
5. [Tree DocType Controller](#tree-doctype-controller)
6. [Complete Sales Flow Voorbeeld](#complete-sales-flow-voorbeeld)

---

## Basis Controller

### Minimale Controller

```python
# myapp/module/doctype/task/task.py
import frappe
from frappe.model.document import Document

class Task(Document):
    pass
```

### Controller met Validatie en Berekeningen

```python
# myapp/module/doctype/invoice/invoice.py
import frappe
from frappe import _
from frappe.model.document import Document

class Invoice(Document):
    def validate(self):
        """Draait bij elke save (nieuw en update)."""
        self.validate_dates()
        self.calculate_totals()
        self.set_status()
    
    def validate_dates(self):
        if self.due_date and self.posting_date:
            if self.due_date < self.posting_date:
                frappe.throw(_("Due Date cannot be before Posting Date"))
    
    def calculate_totals(self):
        self.total = 0
        for item in self.items:
            item.amount = item.qty * item.rate
            self.total += item.amount
        self.tax_amount = self.total * 0.21
        self.grand_total = self.total + self.tax_amount
    
    def set_status(self):
        if self.grand_total == 0:
            self.status = "Draft"
        elif self.is_new():
            self.status = "Unpaid"
```

### Controller met Change Detection

```python
# myapp/module/doctype/project/project.py
import frappe
from frappe import _
from frappe.model.document import Document

class Project(Document):
    def validate(self):
        old = self.get_doc_before_save()
        
        if old is None:
            # Nieuw document
            self.created_by_user = frappe.session.user
        else:
            # Bestaand document - check wijzigingen
            self.check_status_transition(old)
            self.check_protected_fields(old)
    
    def check_status_transition(self, old):
        """Controleer geldige status transities."""
        valid_transitions = {
            "Open": ["In Progress", "Cancelled"],
            "In Progress": ["Completed", "On Hold"],
            "On Hold": ["In Progress", "Cancelled"],
        }
        
        if old.status != self.status:
            allowed = valid_transitions.get(old.status, [])
            if self.status not in allowed:
                frappe.throw(
                    _("Cannot change status from {0} to {1}").format(
                        old.status, self.status
                    )
                )
    
    def check_protected_fields(self, old):
        """Voorkom wijziging van bepaalde velden."""
        protected = ["customer", "project_type"]
        for field in protected:
            if old.get(field) != self.get(field):
                frappe.throw(
                    _("Cannot change {0} after creation").format(field)
                )
    
    def on_update(self):
        """Acties na succesvolle save."""
        # LET OP: self.x = ... werkt hier NIET
        self.update_timeline()
        self.notify_team_members()
    
    def update_timeline(self):
        self.add_comment("Edit", f"Project updated by {frappe.session.user}")
    
    def notify_team_members(self):
        if self.flags.get('status_changed'):
            for member in self.team_members:
                frappe.sendmail(
                    recipients=member.user,
                    subject=f"Project {self.name} status changed",
                    message=f"New status: {self.status}"
                )
```

---

## Submittable Controller

### Complete Submit/Cancel Flow

```python
# myapp/module/doctype/purchase_order/purchase_order.py
import frappe
from frappe import _
from frappe.model.document import Document

class PurchaseOrder(Document):
    def validate(self):
        """Draait bij ELKE save (draft en submit)."""
        self.validate_items()
        self.calculate_totals()
    
    def validate_items(self):
        if not self.items:
            frappe.throw(_("At least one item is required"))
        
        for item in self.items:
            if item.qty <= 0:
                frappe.throw(_("Quantity must be positive for item {0}").format(item.item_code))
    
    def calculate_totals(self):
        self.total_qty = sum(item.qty for item in self.items)
        self.total_amount = sum(item.amount for item in self.items)
    
    def before_submit(self):
        """Validatie VOOR submit (kan submit blokkeren)."""
        # Approval check
        if self.total_amount > 50000 and not self.manager_approval:
            frappe.throw(_("Manager approval required for orders over 50,000"))
        
        # Supplier validation
        supplier = frappe.get_cached_doc("Supplier", self.supplier)
        if supplier.disabled:
            frappe.throw(_("Cannot submit order to disabled supplier"))
    
    def on_submit(self):
        """Acties NA succesvolle submit."""
        self.update_ordered_qty()
        self.create_bin_entries()
        self.notify_supplier()
    
    def update_ordered_qty(self):
        """Update ordered quantity in Item DocType."""
        for item in self.items:
            frappe.db.set_value(
                "Item", item.item_code, "ordered_qty",
                frappe.db.get_value("Item", item.item_code, "ordered_qty") + item.qty
            )
    
    def create_bin_entries(self):
        """Maak warehouse bin entries."""
        for item in self.items:
            self.update_bin_qty(item)
    
    def update_bin_qty(self, item):
        from erpnext.stock.utils import get_bin
        bin_doc = get_bin(item.item_code, item.warehouse)
        bin_doc.update_ordered_qty()
    
    def notify_supplier(self):
        """Stuur email naar supplier."""
        frappe.sendmail(
            recipients=frappe.db.get_value("Supplier", self.supplier, "email_id"),
            subject=f"New Purchase Order: {self.name}",
            message=f"Please confirm order {self.name} for {self.total_amount}"
        )
    
    def before_cancel(self):
        """Validatie VOOR cancel."""
        # Check linked documents
        linked_invoices = frappe.get_all(
            "Purchase Invoice Item",
            filters={"purchase_order": self.name, "docstatus": 1},
            pluck="parent"
        )
        if linked_invoices:
            frappe.throw(
                _("Cannot cancel - linked to Purchase Invoices: {0}").format(
                    ", ".join(set(linked_invoices))
                )
            )
    
    def on_cancel(self):
        """Cleanup NA cancel."""
        self.reverse_ordered_qty()
        self.add_comment("Cancelled", f"Order cancelled by {frappe.session.user}")
    
    def reverse_ordered_qty(self):
        """Reverse de ordered qty updates."""
        for item in self.items:
            frappe.db.set_value(
                "Item", item.item_code, "ordered_qty",
                frappe.db.get_value("Item", item.item_code, "ordered_qty") - item.qty
            )
    
    def on_update_after_submit(self):
        """
        Draait bij update van submitted document.
        Alleen voor velden met 'Allow on Submit' aan.
        """
        if self.status == "Closed":
            self.add_comment("Edit", "Order marked as closed")
```

---

## Controller Override

### Via override_doctype_class

```python
# hooks.py
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.sales_invoice.CustomSalesInvoice"
}
```

```python
# myapp/overrides/sales_invoice.py
import frappe
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    """Extended Sales Invoice met custom validatie."""
    
    def validate(self):
        # ALTIJD parent aanroepen eerst
        super().validate()
        
        # Custom validatie
        self.validate_credit_limit()
        self.apply_custom_discount()
    
    def validate_credit_limit(self):
        """Check customer credit limit."""
        if not self.customer:
            return
        
        customer = frappe.get_cached_doc("Customer", self.customer)
        if customer.credit_limit and self.grand_total > customer.credit_limit:
            frappe.throw(
                _("Order exceeds credit limit of {0}").format(customer.credit_limit)
            )
    
    def apply_custom_discount(self):
        """Automatische korting voor VIP klanten."""
        if frappe.db.get_value("Customer", self.customer, "customer_group") == "VIP":
            self.additional_discount_percentage = 5
            self.calculate_taxes_and_totals()
    
    def on_submit(self):
        # Parent on_submit uitvoeren
        super().on_submit()
        
        # Extra acties
        self.update_customer_stats()
    
    def update_customer_stats(self):
        """Update klant statistieken."""
        frappe.db.set_value(
            "Customer", self.customer, "last_purchase_date", self.posting_date
        )
```

### Via doc_events (Non-Intrusive)

```python
# hooks.py
doc_events = {
    "Sales Invoice": {
        "validate": "myapp.events.sales_invoice.validate",
        "on_submit": "myapp.events.sales_invoice.on_submit",
        "on_cancel": "myapp.events.sales_invoice.on_cancel",
    }
}
```

```python
# myapp/events/sales_invoice.py
import frappe
from frappe import _

def validate(doc, method=None):
    """
    Extra validatie handler.
    
    Args:
        doc: Het document object
        method: Naam van de method (optioneel)
    """
    # Check voor minimum order waarde
    if doc.grand_total < 100:
        frappe.msgprint(_("Order value is below minimum threshold"))
    
    # Custom field berekening
    if hasattr(doc, 'custom_commission_rate'):
        doc.custom_commission = doc.grand_total * (doc.custom_commission_rate / 100)

def on_submit(doc, method=None):
    """Acties na submit."""
    # Externe systeem sync
    sync_to_external_system(doc)
    
    # Loyalty points toekennen
    award_loyalty_points(doc)

def sync_to_external_system(doc):
    """Sync invoice naar extern systeem."""
    frappe.enqueue(
        'myapp.integrations.erp.sync_invoice',
        queue='short',
        invoice_name=doc.name
    )

def award_loyalty_points(doc):
    """Ken loyalty points toe aan klant."""
    points = int(doc.grand_total / 10)  # 1 punt per 10 euro
    if points > 0:
        frappe.get_doc({
            "doctype": "Loyalty Point Entry",
            "customer": doc.customer,
            "loyalty_points": points,
            "invoice": doc.name,
            "invoice_type": "Sales Invoice"
        }).insert(ignore_permissions=True)

def on_cancel(doc, method=None):
    """Cleanup bij cancel."""
    # Reverse loyalty points
    frappe.db.delete("Loyalty Point Entry", {"invoice": doc.name})
```

---

## Virtual DocType Controller

### Externe API Data

```python
# myapp/module/doctype/external_product/external_product.py
import frappe
import requests
from frappe.model.document import Document

class ExternalProduct(Document):
    """
    DocType dat data ophaalt van externe API.
    Vereist: Is Virtual = 1 in DocType settings.
    """
    
    API_BASE = "https://api.external-system.com/products"
    
    def load_from_db(self):
        """
        Laad document van externe bron.
        Wordt aangeroepen bij frappe.get_doc().
        """
        response = requests.get(
            f"{self.API_BASE}/{self.name}",
            headers=self.get_api_headers()
        )
        response.raise_for_status()
        
        data = response.json()
        # Initialiseer document met externe data
        super(Document, self).__init__(self.map_api_to_doc(data))
    
    def db_insert(self, *args, **kwargs):
        """
        Insert naar externe bron.
        Wordt aangeroepen bij doc.insert().
        """
        response = requests.post(
            self.API_BASE,
            json=self.map_doc_to_api(),
            headers=self.get_api_headers()
        )
        response.raise_for_status()
        
        # Set name van response
        self.name = response.json().get('id')
    
    def db_update(self, *args, **kwargs):
        """
        Update naar externe bron.
        Wordt aangeroepen bij doc.save().
        """
        response = requests.put(
            f"{self.API_BASE}/{self.name}",
            json=self.map_doc_to_api(),
            headers=self.get_api_headers()
        )
        response.raise_for_status()
    
    def delete(self):
        """Verwijder van externe bron."""
        response = requests.delete(
            f"{self.API_BASE}/{self.name}",
            headers=self.get_api_headers()
        )
        response.raise_for_status()
    
    @staticmethod
    def get_list(args):
        """
        Return lijst voor List View.
        
        Args:
            args: Dict met filters, order_by, start, page_length
        """
        response = requests.get(
            ExternalProduct.API_BASE,
            params={
                'limit': args.get('page_length', 20),
                'offset': args.get('start', 0),
            },
            headers=ExternalProduct.get_api_headers_static()
        )
        
        if response.ok:
            return [
                frappe._dict(ExternalProduct.map_api_to_doc_static(item))
                for item in response.json().get('items', [])
            ]
        return []
    
    @staticmethod
    def get_count(args):
        """Return totaal aantal voor pagination."""
        response = requests.get(
            f"{ExternalProduct.API_BASE}/count",
            headers=ExternalProduct.get_api_headers_static()
        )
        return response.json().get('count', 0) if response.ok else 0
    
    def get_api_headers(self):
        return self.get_api_headers_static()
    
    @staticmethod
    def get_api_headers_static():
        return {
            "Authorization": f"Bearer {frappe.conf.external_api_key}",
            "Content-Type": "application/json"
        }
    
    def map_api_to_doc(self, data):
        return self.map_api_to_doc_static(data)
    
    @staticmethod
    def map_api_to_doc_static(data):
        """Map API response naar DocType velden."""
        return {
            "name": data.get('id'),
            "doctype": "External Product",
            "product_name": data.get('name'),
            "description": data.get('description'),
            "price": data.get('unit_price'),
            "stock_qty": data.get('inventory_count'),
        }
    
    def map_doc_to_api(self):
        """Map DocType velden naar API format."""
        return {
            "name": self.product_name,
            "description": self.description,
            "unit_price": self.price,
            "inventory_count": self.stock_qty,
        }
```

---

## Tree DocType Controller

### HiÃ«rarchische Structuur

```python
# myapp/module/doctype/department/department.py
import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet

class Department(NestedSet):
    """
    HiÃ«rarchisch DocType voor afdelingen.
    Vereist: Is Tree = 1, parent_fieldname = "parent_department" in DocType.
    """
    
    # Vereiste configuratie voor NestedSet
    nsm_parent_field = "parent_department"
    
    def validate(self):
        self.validate_circular_reference()
    
    def validate_circular_reference(self):
        """Voorkom circulaire parent-child relatie."""
        if self.parent_department:
            parent = frappe.get_doc("Department", self.parent_department)
            ancestors = self.get_ancestors()
            
            if self.name in [a.name for a in parent.get_ancestors()]:
                frappe.throw(_("Circular reference detected"))
    
    def on_update(self):
        """Update tree na wijzigingen."""
        self.update_employee_count()
    
    def update_employee_count(self):
        """Tel medewerkers in afdeling + sub-afdelingen."""
        descendants = self.get_descendants()
        dept_names = [self.name] + [d.name for d in descendants]
        
        count = frappe.db.count("Employee", {"department": ["in", dept_names]})
        frappe.db.set_value("Department", self.name, "total_employees", count)
    
    def get_ancestors(self):
        """Krijg alle parent afdelingen."""
        ancestors = []
        current = self
        while current.parent_department:
            parent = frappe.get_doc("Department", current.parent_department)
            ancestors.append(parent)
            current = parent
        return ancestors
    
    def get_descendants(self, include_self=False):
        """Krijg alle child afdelingen (recursief)."""
        result = [self] if include_self else []
        
        children = frappe.get_all(
            "Department",
            filters={"parent_department": self.name},
            pluck="name"
        )
        
        for child_name in children:
            child = frappe.get_doc("Department", child_name)
            result.append(child)
            result.extend(child.get_descendants())
        
        return result
```

---

## Complete Sales Flow Voorbeeld

### Volledige Order Controller met Alle Patronen

```python
# myapp/selling/doctype/sales_order/sales_order.py
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import getseries

class SalesOrder(Document):
    """
    Complete Sales Order controller met:
    - Custom naming
    - Validatie met change detection
    - Submit/Cancel flow
    - Whitelisted methods
    - Flags gebruik
    """
    
    # =========== NAMING ===========
    
    def autoname(self):
        """Custom naming: SO-{CUSTOMER_CODE}-{SERIES}"""
        customer_code = frappe.db.get_value(
            "Customer", self.customer, "customer_code"
        ) or "GEN"
        prefix = f"SO-{customer_code[:3].upper()}-"
        self.name = getseries(prefix, 5)
    
    # =========== VALIDATION ===========
    
    def validate(self):
        """Hoofdvalidatie hook."""
        self.validate_customer()
        self.validate_items()
        self.calculate_totals()
        self.detect_changes()
    
    def validate_customer(self):
        customer = frappe.get_cached_doc("Customer", self.customer)
        if customer.disabled:
            frappe.throw(_("Customer {0} is disabled").format(self.customer))
    
    def validate_items(self):
        if not self.items:
            frappe.throw(_("At least one item required"))
        
        seen_items = set()
        for idx, item in enumerate(self.items, 1):
            # Check duplicates
            if item.item_code in seen_items:
                frappe.throw(_("Duplicate item {0} in row {1}").format(
                    item.item_code, idx
                ))
            seen_items.add(item.item_code)
            
            # Validate qty
            if item.qty <= 0:
                frappe.throw(_("Quantity must be positive in row {0}").format(idx))
            
            # Calculate amount
            item.amount = item.qty * item.rate
    
    def calculate_totals(self):
        self.total_qty = sum(item.qty for item in self.items)
        self.total_amount = sum(item.amount for item in self.items)
        self.tax_amount = self.total_amount * 0.21
        self.grand_total = self.total_amount + self.tax_amount
    
    def detect_changes(self):
        """Detecteer en valideer wijzigingen."""
        old = self.get_doc_before_save()
        if old:
            # Voorkom customer wijziging na creatie
            if old.customer != self.customer:
                frappe.throw(_("Cannot change customer after order creation"))
            
            # Track status wijziging voor notifications
            if old.status != self.status:
                self.flags.status_changed = True
                self.flags.old_status = old.status
    
    # =========== LIFECYCLE HOOKS ===========
    
    def after_insert(self):
        """Alleen bij nieuwe orders."""
        self.add_comment("Created", f"Order created by {frappe.session.user}")
    
    def on_update(self):
        """Na elke save."""
        if self.flags.get('status_changed'):
            self.notify_status_change()
    
    def notify_status_change(self):
        old_status = self.flags.get('old_status', 'Unknown')
        frappe.publish_realtime(
            'sales_order_status',
            {'name': self.name, 'old': old_status, 'new': self.status},
            doctype=self.doctype,
            docname=self.name
        )
    
    # =========== SUBMIT/CANCEL ===========
    
    def before_submit(self):
        """Validatie voor submit."""
        # Credit check
        if self.grand_total > 10000:
            credit_ok = self.check_customer_credit()
            if not credit_ok:
                frappe.throw(_("Order exceeds customer credit limit"))
    
    def check_customer_credit(self):
        customer = frappe.get_cached_doc("Customer", self.customer)
        return self.grand_total <= customer.get('credit_limit', float('inf'))
    
    def on_submit(self):
        """Acties na submit."""
        self.update_stock_reservation()
        self.create_payment_request()
        frappe.db.set_value(self.doctype, self.name, "submitted_at", frappe.utils.now())
    
    def update_stock_reservation(self):
        for item in self.items:
            frappe.get_doc({
                "doctype": "Stock Reservation",
                "item_code": item.item_code,
                "warehouse": item.warehouse,
                "reserved_qty": item.qty,
                "sales_order": self.name
            }).insert(ignore_permissions=True)
    
    def create_payment_request(self):
        if self.grand_total > 0:
            frappe.enqueue(
                'myapp.payments.create_payment_request',
                queue='short',
                order_name=self.name
            )
    
    def before_cancel(self):
        """Check voor cancel."""
        # Check voor delivery notes
        deliveries = frappe.get_all(
            "Delivery Note Item",
            filters={"against_sales_order": self.name, "docstatus": 1}
        )
        if deliveries:
            frappe.throw(_("Cannot cancel - has delivered items"))
    
    def on_cancel(self):
        """Cleanup na cancel."""
        self.release_stock_reservation()
        self.cancel_payment_request()
    
    def release_stock_reservation(self):
        frappe.db.delete("Stock Reservation", {"sales_order": self.name})
    
    def cancel_payment_request(self):
        for pr in frappe.get_all("Payment Request", {"reference_name": self.name}):
            doc = frappe.get_doc("Payment Request", pr.name)
            if doc.docstatus == 1:
                doc.cancel()
    
    # =========== WHITELISTED METHODS ===========
    
    @frappe.whitelist()
    def recalculate_totals(self):
        """
        Herbereken totalen - aanroepbaar via JavaScript.
        Returns dict met nieuwe totalen.
        """
        self.calculate_totals()
        return {
            "total_qty": self.total_qty,
            "total_amount": self.total_amount,
            "tax_amount": self.tax_amount,
            "grand_total": self.grand_total
        }
    
    @frappe.whitelist()
    def send_to_customer(self, include_terms=True):
        """Stuur order PDF naar klant."""
        from frappe.utils.print_format import download_pdf
        
        pdf = download_pdf(self.doctype, self.name, "Standard")
        
        frappe.sendmail(
            recipients=[self.contact_email],
            subject=f"Your Order {self.name}",
            message=f"Please find attached your order {self.name}",
            attachments=[{
                "fname": f"{self.name}.pdf",
                "fcontent": pdf
            }]
        )
        
        return {"status": "sent", "email": self.contact_email}
```

---

## JavaScript Aanroep Voorbeelden

```javascript
// In client script of form script
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // Herbereken knop
        frm.add_custom_button(__('Recalculate'), function() {
            frm.call('recalculate_totals').then(r => {
                frm.set_value('grand_total', r.message.grand_total);
                frappe.msgprint(__('Totals updated'));
            });
        });
        
        // Verstuur knop (alleen voor submitted)
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Send to Customer'), function() {
                frm.call('send_to_customer', { include_terms: true })
                    .then(r => {
                        frappe.msgprint(__('Email sent to {0}', [r.message.email]));
                    });
            });
        }
    }
});
```
