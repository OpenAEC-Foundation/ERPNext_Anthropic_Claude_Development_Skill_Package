# Document Events Reference

Complete referentie voor `doc_events` in hooks.py.

---

## Syntax

```python
# In hooks.py
doc_events = {
    # Wildcard - alle DocTypes
    "*": {
        "after_insert": "myapp.events.log_creation"
    },
    # Specifieke DocType
    "Sales Invoice": {
        "validate": "myapp.events.si_validate",
        "on_submit": "myapp.events.si_on_submit"
    },
    # Meerdere handlers per event
    "Sales Order": {
        "validate": [
            "myapp.events.so_validate_stock",
            "myapp.events.so_validate_credit"
        ]
    }
}
```

---

## Alle Beschikbare Events

### Document Lifecycle

| Event | Trigger Moment | Signature |
|-------|----------------|-----------|
| `before_insert` | Voor INSERT naar database | `def handler(doc, method=None):` |
| `after_insert` | Na INSERT succesvol | `def handler(doc, method=None):` |
| `before_validate` | Voor validatie start | `def handler(doc, method=None):` |
| `validate` | Hoofdvalidatie (= Before Save UI) | `def handler(doc, method=None):` |
| `on_update` | Na UPDATE succesvol | `def handler(doc, method=None):` |
| `on_change` | Na elke wijziging (ook db_set) | `def handler(doc, method=None):` |

### Rename Events

| Event | Trigger Moment | Signature |
|-------|----------------|-----------|
| `before_rename` | Voor document hernoemen | `def handler(doc, method, old, new, merge):` |
| `after_rename` | Na document hernoemen | `def handler(doc, method, old, new, merge):` |

### Submit/Cancel Events

| Event | Trigger Moment | Signature |
|-------|----------------|-----------|
| `before_submit` | Voor submit (docstatus 0→1) | `def handler(doc, method=None):` |
| `on_submit` | Na submit succesvol | `def handler(doc, method=None):` |
| `before_cancel` | Voor cancel (docstatus 1→2) | `def handler(doc, method=None):` |
| `on_cancel` | Na cancel succesvol | `def handler(doc, method=None):` |
| `before_update_after_submit` | Voor update submitted doc | `def handler(doc, method=None):` |
| `on_update_after_submit` | Na update submitted doc | `def handler(doc, method=None):` |

### Delete Events

| Event | Trigger Moment | Signature |
|-------|----------------|-----------|
| `on_trash` | Voor document delete | `def handler(doc, method=None):` |
| `after_delete` | Na document delete | `def handler(doc, method=None):` |

---

## Execution Order

```
NEW DOCUMENT:
before_insert → before_validate → validate → after_insert → on_update → on_change

UPDATE DOCUMENT:
before_validate → validate → on_update → on_change

SUBMIT:
before_submit → on_submit → on_update → on_change

CANCEL:
before_cancel → on_cancel → on_update → on_change

DELETE:
on_trash → after_delete
```

---

## Handler Implementatie

### Standaard Handler

```python
# In myapp/events.py
import frappe

def si_validate(doc, method=None):
    """
    Args:
        doc: Document object (frappe.model.document.Document)
        method: Event naam als string ("validate")
    """
    if doc.grand_total < 0:
        frappe.throw("Total cannot be negative")
```

### Wildcard Handler

```python
def log_creation(doc, method=None):
    """Triggered voor ALLE DocTypes"""
    frappe.logger().info(f"Created {doc.doctype}: {doc.name}")
```

### Rename Handler (Extra Argumenten)

```python
def before_rename_handler(doc, method, old, new, merge):
    """
    Extra args:
        old: Oude document naam
        new: Nieuwe document naam
        merge: Boolean - of merge actief is
    """
    if doc.doctype == "Customer" and doc.status == "Active":
        frappe.throw("Cannot rename active customer")
```

---

## Hooks Resolution Order

Meerdere apps kunnen dezelfde DocType hooken. Resolutie:

1. **Override hooks** (override_whitelisted_methods): Laatste app wint
2. **Extend hooks** (doc_events): Alle handlers draaien in installatievolgorde

> **Tip**: Volgorde aanpassen via Setup → Installed Applications → Update Hooks Resolution Order

---

## Verschil met Controller Hooks

| Aspect | doc_events (hooks.py) | Controller Methods |
|--------|----------------------|-------------------|
| Locatie | hooks.py | doctype controller.py |
| Scope | Externe apps kunnen hooken | Alleen eigen DocType |
| Meerdere handlers | Ja (lijst mogelijk) | Nee (1 per DocType) |
| Prioriteit | Na controller method | Eerst |

**Execution**: Controller method → doc_events handlers

---

## Voorbeelden

### Validate met Cross-Document Check

```python
# hooks.py
doc_events = {
    "Sales Order": {
        "validate": "myapp.events.check_customer_credit"
    }
}

# myapp/events.py
def check_customer_credit(doc, method=None):
    credit_limit = frappe.db.get_value(
        "Customer", doc.customer, "credit_limit"
    )
    outstanding = get_customer_outstanding(doc.customer)
    
    if outstanding + doc.grand_total > credit_limit:
        frappe.throw(f"Credit limit exceeded for {doc.customer}")
```

### After Insert met Notification

```python
# hooks.py
doc_events = {
    "Issue": {
        "after_insert": "myapp.events.notify_support_team"
    }
}

# myapp/events.py
def notify_support_team(doc, method=None):
    frappe.sendmail(
        recipients=["support@example.com"],
        subject=f"New Issue: {doc.subject}",
        message=f"Issue {doc.name} created by {doc.raised_by}"
    )
```

### On Submit met Ledger Entry

```python
# hooks.py
doc_events = {
    "Sales Invoice": {
        "on_submit": "myapp.events.create_custom_ledger"
    }
}

# myapp/events.py
def create_custom_ledger(doc, method=None):
    # Alleen uitvoeren bij submit, niet bij cancel
    if doc.docstatus != 1:
        return
    
    ledger = frappe.new_doc("Custom Ledger Entry")
    ledger.reference_doctype = doc.doctype
    ledger.reference_name = doc.name
    ledger.amount = doc.grand_total
    ledger.insert(ignore_permissions=True)
```

---

## Anti-Patterns

### ❌ Commit in Handler

```python
# FOUT - Frappe handelt commits automatisch af
def on_update(doc, method=None):
    frappe.db.commit()  # NIET DOEN - kan transactie breken
```

### ❌ Heavy Operations in Sync

```python
# FOUT - blokkeert gebruiker
def validate(doc, method=None):
    process_1000_records()  # Te zwaar

# GOED - gebruik enqueue
def on_update(doc, method=None):
    frappe.enqueue(
        "myapp.tasks.process_records",
        doc_name=doc.name,
        queue="long"
    )
```

### ❌ Wijzigingen na on_update

```python
# FOUT - wijzigingen worden NIET opgeslagen
def on_update(doc, method=None):
    doc.status = "Processed"  # Verloren!

# GOED - gebruik db_set
def on_update(doc, method=None):
    frappe.db.set_value(doc.doctype, doc.name, "status", "Processed")
```
