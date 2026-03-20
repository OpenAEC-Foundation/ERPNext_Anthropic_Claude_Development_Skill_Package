# Code Validation Examples

## Example 1: Server Script with Import Error

### Code Submitted for Validation

```python
# Server Script: Document Event - Before Save on Sales Invoice
from frappe.utils import nowdate, getdate
import json

if doc.posting_date < getdate(nowdate()):
    data = json.loads(doc.custom_data)
    if data.get("allow_backdating"):
        pass
    else:
        frappe.throw("Backdating not allowed")
```

### Validation Report

```markdown
## Code Validation Report

### Code Type: Server Script (Document Event)
### Target DocType: Sales Invoice
### Event: validate (Before Save)

---

### 🔴 CRITICAL ERRORS (Must Fix)

| Line | Issue | Fix |
|------|-------|-----|
| 2 | `from frappe.utils import` - Import blocked in sandbox | Use `frappe.utils.nowdate()` and `frappe.utils.getdate()` directly |
| 3 | `import json` - Import blocked in sandbox | Use `frappe.parse_json()` instead |

### 🟡 WARNINGS (Should Fix)

| Line | Issue | Recommendation |
|------|-------|----------------|
| 5 | No null check on `doc.custom_data` | Add: `if doc.custom_data:` before parse |
| 9 | Generic error message | Include date values in message for clarity |

### 🔵 SUGGESTIONS (Nice to Have)

| Line | Suggestion |
|------|------------|
| - | Consider using frappe's `_()` for translatable strings |

---

### Corrected Code

```python
# Server Script: Document Event - Before Save on Sales Invoice
# FIXED: Removed imports, using frappe namespace directly

if doc.posting_date < frappe.utils.getdate(frappe.utils.nowdate()):
    if doc.custom_data:
        data = frappe.parse_json(doc.custom_data)
        if not data.get("allow_backdating"):
            frappe.throw(f"Backdating not allowed. Posting date {doc.posting_date} is before today.")
    else:
        frappe.throw(f"Backdating not allowed. Posting date {doc.posting_date} is before today.")
```

### Version Compatibility

| Version | Status |
|---------|--------|
| v14 | ✅ Compatible |
| v15 | ✅ Compatible |
| v16 | ✅ Compatible |
```

---

## Example 2: Client Script with Async Issue

### Code Submitted for Validation

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        let customer_data = frappe.call({
            method: 'erpnext.selling.doctype.customer.customer.get_customer_details',
            args: { customer: frm.doc.customer }
        });
        
        if (customer_data.message.credit_limit > 0) {
            frm.set_value('credit_limit', customer_data.message.credit_limit);
        }
    }
});
```

### Validation Report

```markdown
## Code Validation Report

### Code Type: Client Script
### Target DocType: Sales Order
### Event: refresh

---

### 🔴 CRITICAL ERRORS (Must Fix)

| Line | Issue | Fix |
|------|-------|-----|
| 3-6 | `frappe.call()` without callback returns undefined | Use callback pattern or async/await |
| 8-10 | Accessing `.message` on undefined value | Will throw TypeError |

### 🟡 WARNINGS (Should Fix)

| Line | Issue | Recommendation |
|------|-------|----------------|
| 3 | Missing check for `frm.doc.customer` | Add null check before API call |
| 9 | No `refresh_field()` after `set_value()` | Add refresh to update UI |

---

### Corrected Code

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // FIXED: Check customer exists before API call
        if (!frm.doc.customer) return;
        
        // FIXED: Use callback pattern for async call
        frappe.call({
            method: 'erpnext.selling.doctype.customer.customer.get_customer_details',
            args: { customer: frm.doc.customer },
            callback: function(r) {
                if (r.message && r.message.credit_limit > 0) {
                    frm.set_value('credit_limit', r.message.credit_limit);
                    // FIXED: Refresh field after set_value
                    frm.refresh_field('credit_limit');
                }
            }
        });
    }
});
```

### Version Compatibility

| Version | Status |
|---------|--------|
| v14 | ✅ Compatible |
| v15 | ✅ Compatible |
| v16 | ✅ Compatible |
```

---

## Example 3: Controller with on_update Modification

### Code Submitted for Validation

```python
# sales_invoice.py controller override
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def on_update(self):
        # Update commission after save
        if self.sales_partner:
            commission = self.grand_total * 0.1
            self.commission_amount = commission
            self.custom_commission_status = "Calculated"
```

### Validation Report

```markdown
## Code Validation Report

### Code Type: Controller
### Target DocType: Sales Invoice
### Method: on_update

---

### 🔴 CRITICAL ERRORS (Must Fix)

| Line | Issue | Fix |
|------|-------|-----|
| 8-9 | Modifying `self.commission_amount` and `self.custom_commission_status` in on_update - changes will NOT be saved | Use `frappe.db.set_value()` or `self.db_set()` |

### 🟡 WARNINGS (Should Fix)

| Line | Issue | Recommendation |
|------|-------|----------------|
| 5 | Missing `super().on_update()` call | Add to preserve parent behavior |
| 7 | Hardcoded commission rate 0.1 | Consider making this configurable |

---

### Corrected Code

```python
# sales_invoice.py controller override
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def on_update(self):
        # FIXED: Call parent on_update first
        super().on_update()
        
        # Update commission after save
        if self.sales_partner:
            commission = self.grand_total * 0.1
            
            # FIXED: Use db_set for on_update modifications
            self.db_set({
                "commission_amount": commission,
                "custom_commission_status": "Calculated"
            })
```

### Version Compatibility

| Version | Status |
|---------|--------|
| v14 | ✅ Compatible |
| v15 | ✅ Compatible |
| v16 | ✅ Compatible |
```

---

## Example 4: Server Script Permission Query

### Code Submitted for Validation

```python
# Server Script: Permission Query on Customer
user = frappe.session.user

if frappe.db.get_value("User", user, "role_profile_name") == "Sales Person":
    territories = frappe.get_all("User Permission", 
        filters={"user": user, "allow": "Territory"},
        pluck="for_value")
    
    if territories:
        conditions = "territory in (" + ",".join(territories) + ")"
```

### Validation Report

```markdown
## Code Validation Report

### Code Type: Server Script (Permission Query)
### Target DocType: Customer

---

### 🔴 CRITICAL ERRORS (Must Fix)

| Line | Issue | Fix |
|------|-------|-----|
| 9 | SQL injection vulnerability - territories not escaped | Use `frappe.db.escape()` for each value |
| - | Missing `conditions` variable assignment if user is not Sales Person | Initialize `conditions` at start |

### 🟡 WARNINGS (Should Fix)

| Line | Issue | Recommendation |
|------|-------|----------------|
| 3 | Multiple DB calls could be slow | Consider caching or optimizing |

### 🔵 SUGGESTIONS (Nice to Have)

| Line | Suggestion |
|------|------------|
| 9 | Use formatted string with proper escaping for clarity |

---

### Corrected Code

```python
# Server Script: Permission Query on Customer
# FIXED: Initialize conditions and fix SQL injection

conditions = None  # Default: no additional filter
user = frappe.session.user

if frappe.db.get_value("User", user, "role_profile_name") == "Sales Person":
    territories = frappe.get_all("User Permission", 
        filters={"user": user, "allow": "Territory"},
        pluck="for_value")
    
    if territories:
        # FIXED: Properly escape each territory value
        escaped_territories = [frappe.db.escape(t) for t in territories]
        conditions = "`tabCustomer`.`territory` IN ({})".format(
            ",".join(escaped_territories)
        )
```

### Version Compatibility

| Version | Status |
|---------|--------|
| v14 | ✅ Compatible |
| v15 | ✅ Compatible |
| v16 | ✅ Compatible |
```

---

## Example 5: hooks.py with Version Issue

### Code Submitted for Validation

```python
# hooks.py
app_name = "custom_app"

doc_events = {
    "Sales Invoice": {
        "validate": "custom_app.overrides.sales_invoice.validate",
        "on_submit": "custom_app.overrides.sales_invoice.on_submit"
    }
}

extend_doctype_class = {
    "Sales Invoice": ["custom_app.overrides.sales_invoice_mixin.SalesInvoiceMixin"]
}

scheduler_events = {
    "daily": [
        "custom_app.tasks.daily_report"
    ]
}
```

### Validation Report

```markdown
## Code Validation Report

### Code Type: hooks.py
### App: custom_app

---

### 🔴 CRITICAL ERRORS (Must Fix)

| Line | Issue | Fix |
|------|-------|-----|
| 11-13 | `extend_doctype_class` is v16+ only | Remove if targeting v14/v15, or add version check |

### 🟡 WARNINGS (Should Fix)

| Line | Issue | Recommendation |
|------|-------|----------------|
| - | No error handling hooks defined | Consider adding `on_session_creation` for error logging |

### 🔵 SUGGESTIONS (Nice to Have)

| Line | Suggestion |
|------|------------|
| - | Add `app_include_js` and `app_include_css` if you have custom assets |

---

### Corrected Code (v14/v15 Compatible)

```python
# hooks.py
app_name = "custom_app"

doc_events = {
    "Sales Invoice": {
        "validate": "custom_app.overrides.sales_invoice.validate",
        "on_submit": "custom_app.overrides.sales_invoice.on_submit"
    }
}

# REMOVED: extend_doctype_class (v16 only)
# For v14/v15, use override_doctype_class instead:
override_doctype_class = {
    "Sales Invoice": "custom_app.overrides.sales_invoice.CustomSalesInvoice"
}

scheduler_events = {
    "daily": [
        "custom_app.tasks.daily_report"
    ]
}
```

### Corrected Code (v16 Only)

```python
# hooks.py - v16 ONLY
app_name = "custom_app"

doc_events = {
    "Sales Invoice": {
        "validate": "custom_app.overrides.sales_invoice.validate",
        "on_submit": "custom_app.overrides.sales_invoice.on_submit"
    }
}

# v16+ feature - allows multiple apps to extend same DocType
extend_doctype_class = {
    "Sales Invoice": ["custom_app.overrides.sales_invoice_mixin.SalesInvoiceMixin"]
}

scheduler_events = {
    "daily": [
        "custom_app.tasks.daily_report"
    ]
}
```

### Version Compatibility

| Version | Status | Notes |
|---------|--------|-------|
| v14 | ⚠️ Needs fix | Remove `extend_doctype_class` |
| v15 | ⚠️ Needs fix | Remove `extend_doctype_class` |
| v16 | ✅ Compatible | Original code works |
```

---

## Example 6: Clean Code (No Issues)

### Code Submitted for Validation

```python
# Server Script: Document Event - Before Save on Purchase Order
# Purpose: Auto-calculate estimated delivery date based on supplier lead time

if doc.supplier:
    supplier = frappe.get_doc("Supplier", doc.supplier)
    
    if supplier.lead_time_days and doc.transaction_date:
        from_date = frappe.utils.getdate(doc.transaction_date)
        delivery_date = frappe.utils.add_days(from_date, supplier.lead_time_days)
        doc.schedule_date = delivery_date
```

### Validation Report

```markdown
## Code Validation Report

### Code Type: Server Script (Document Event)
### Target DocType: Purchase Order
### Event: validate (Before Save)

---

### ✅ NO CRITICAL ERRORS

### ✅ NO WARNINGS

### 🔵 SUGGESTIONS (Nice to Have)

| Line | Suggestion |
|------|------------|
| 5 | Could use `frappe.db.get_value("Supplier", doc.supplier, "lead_time_days")` instead of `get_doc` for better performance since only one field is needed |

---

### Code Quality: EXCELLENT

The code:
- ✅ Uses frappe namespace correctly (no imports)
- ✅ Uses `doc.` for document access
- ✅ Has proper null checks
- ✅ Clear purpose documented in comment

### Version Compatibility

| Version | Status |
|---------|--------|
| v14 | ✅ Compatible |
| v15 | ✅ Compatible |
| v16 | ✅ Compatible |
```

---

## Quick Validation Patterns

### Pattern: Detect Import in Server Script

```
REGEX: ^import |^from .* import
SEVERITY: FATAL
MESSAGE: "Server Scripts cannot use import statements. Use frappe namespace directly."
```

### Pattern: Detect self in Server Script

```
REGEX: \bself\.\w+
SEVERITY: FATAL  
MESSAGE: "Server Scripts use 'doc', not 'self'. Replace 'self.' with 'doc.'"
```

### Pattern: Detect frappe.db in Client Script

```
REGEX: frappe\.db\.(get_value|set_value|sql|get_all|get_list)
SEVERITY: FATAL
MESSAGE: "frappe.db.* is server-side only. Use frappe.call() to invoke server methods."
```

### Pattern: Detect Async Issue in Client Script

```
REGEX: (let|const|var)\s+\w+\s*=\s*frappe\.call\s*\((?!.*callback)
SEVERITY: FATAL
MESSAGE: "frappe.call() is async. Use callback function or async/await pattern."
```

### Pattern: Detect on_update self modification

```
REGEX: def on_update\(self\):[\s\S]*?self\.\w+\s*=
SEVERITY: FATAL
MESSAGE: "Modifications to self.* in on_update() are not saved. Use self.db_set() or frappe.db.set_value()."
```
