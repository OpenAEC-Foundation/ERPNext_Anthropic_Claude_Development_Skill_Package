# Override Hooks Reference

Complete referentie voor override hooks in hooks.py.

---

## override_whitelisted_methods

Override bestaande API endpoints met custom implementaties.

### Syntax

```python
# In hooks.py
override_whitelisted_methods = {
    "frappe.client.get_count": "myapp.overrides.custom_get_count",
    "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice": 
        "myapp.overrides.custom_make_sales_invoice"
}
```

### Handler Implementatie

```python
# In myapp/overrides.py

def custom_get_count(doctype, filters=None, debug=False, cache=False):
    """
    KRITIEK: Method signature MOET identiek zijn aan origineel!
    
    Originele signature vinden:
    1. Zoek de functie in Frappe/ERPNext source
    2. Kopieer exact de parameters
    """
    # Custom logic
    count = frappe.db.count(doctype, filters)
    
    # Bijvoorbeeld: log elke count query
    frappe.log_error(f"Count query: {doctype}", "API Audit")
    
    return count
```

### Veel Overschreven Methods

| Method | Doel |
|--------|------|
| `frappe.client.get_count` | Record counting |
| `frappe.client.get_list` | List queries |
| `frappe.desk.search.search_link` | Link field search |
| `erpnext.*.make_*` | Document creation wizards |

---

## override_doctype_class

Vervang de controller class van een DocType volledig.

### Syntax

```python
# In hooks.py
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice",
    "ToDo": "myapp.overrides.todo.CustomToDo"
}
```

### Handler Implementatie

```python
# In myapp/overrides.py
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # KRITIEK: Altijd super() aanroepen!
        super().validate()
        self.custom_validation()
    
    def on_submit(self):
        super().on_submit()
        self.create_custom_ledger_entry()
    
    def custom_validation(self):
        if self.grand_total > 100000:
            frappe.msgprint("High value invoice - requires approval")
    
    def create_custom_ledger_entry(self):
        # Custom logic
        pass
```

### âš ï¸ Waarschuwingen

1. **Laatste app wint**: Bij meerdere apps die dezelfde DocType overschrijven, werkt alleen de laatst geÃ¯nstalleerde
2. **Breekbaar**: Updates aan de originele class kunnen je override breken
3. **Altijd super()**: Vergeten van `super()` breekt core functionaliteit

---

## extend_doctype_class (v16+)

Extend een controller zonder volledig te overschrijven. **Veiliger dan override!**

### Syntax

```python
# In hooks.py
extend_doctype_class = {
    "Address": ["myapp.extensions.address.AddressMixin"],
    "Contact": [
        "myapp.extensions.common.ValidationMixin",
        "myapp.extensions.contact.ContactMixin"
    ]
}
```

### Handler Implementatie

```python
# In myapp/extensions/address.py
from frappe.model.document import Document

class AddressMixin(Document):
    @property
    def full_address(self):
        """Computed property toegevoegd aan Address"""
        return f"{self.address_line1}, {self.city}, {self.country}"
    
    def validate(self):
        super().validate()
        self.validate_postal_code()
    
    def validate_postal_code(self):
        if self.country == "Netherlands" and self.pincode:
            if not re.match(r'^\d{4}\s?[A-Z]{2}$', self.pincode):
                frappe.throw("Invalid Dutch postal code format")
```

### Voordelen t.o.v. override_doctype_class

| Aspect | override_doctype_class | extend_doctype_class |
|--------|------------------------|----------------------|
| Meerdere apps | âŒ Laatste wint | âœ… Allemaal actief |
| Onderhoud | âŒ Breekbaar | âœ… Stabiel |
| Beschikbaarheid | v14+ | v16+ |

---

## doctype_js

Extend form scripts van bestaande DocTypes.

### Syntax

```python
# In hooks.py
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "ToDo": "public/js/todo.js"
}
```

### Script Implementatie

```javascript
// In public/js/sales_invoice.js
frappe.ui.form.on("Sales Invoice", {
    refresh: function(frm) {
        // Voeg custom button toe
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Send to ERP"), function() {
                frm.trigger("send_to_external_erp");
            });
        }
    },
    
    customer: function(frm) {
        // Hook op customer field change
        if (frm.doc.customer) {
            frappe.call({
                method: "myapp.api.get_customer_discount",
                args: { customer: frm.doc.customer },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("discount_percentage", r.message);
                    }
                }
            });
        }
    },
    
    send_to_external_erp: function(frm) {
        frappe.call({
            method: "myapp.api.send_invoice",
            args: { invoice: frm.doc.name },
            callback: function(r) {
                frappe.msgprint(__("Invoice sent successfully"));
            }
        });
    }
});
```

---

## Hooks Resolution Order

Bij meerdere apps die dezelfde hook gebruiken:

```
Override hooks (override_*): Laatste geÃ¯nstalleerde app wint
Extend hooks (extend_*, doc_events): Alle handlers draaien in installatievolgorde
```

### Volgorde Aanpassen

Ga naar: Setup â†’ Installed Applications â†’ Update Hooks Resolution Order

---

## Decision Tree: Welke Override?

```
Wil je bestaande functionaliteit aanpassen?
â”‚
â”œâ”€â–º API endpoint aanpassen?
â”‚   â””â”€â–º override_whitelisted_methods
â”‚
â”œâ”€â–º DocType controller aanpassen?
â”‚   â”‚
â”‚   â”œâ”€â–º Frappe v16+?
â”‚   â”‚   â””â”€â–º extend_doctype_class (aanbevolen)
â”‚   â”‚
â”‚   â””â”€â–º Frappe v14/v15?
â”‚       â””â”€â–º override_doctype_class (let op: laatste wint)
â”‚
â””â”€â–º Form UI aanpassen?
    â””â”€â–º doctype_js
```

---

## Versie Verschillen

| Hook | v14 | v15 | v16 |
|------|-----|-----|-----|
| override_whitelisted_methods | âœ… | âœ… | âœ… |
| override_doctype_class | âœ… | âœ… | âœ… |
| extend_doctype_class | âŒ | âŒ | âœ… |
| doctype_js | âœ… | âœ… | âœ… |
