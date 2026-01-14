---
name: erpnext-syntax-controllers
description: Deterministische syntax voor Frappe Document Controllers (Python server-side). Gebruik wanneer Claude code moet genereren voor DocType controllers, lifecycle hooks (validate, on_update, on_submit, etc.), document methods, of wanneer vragen gaan over controller structuur, naming conventions, autoname patterns, of het flags systeem. Triggers: "controller", "validate hook", "on_update", "on_submit", "lifecycle", "document class", "autoname", "flags".
---

# ERPNext Syntax: Document Controllers

Document Controllers zijn Python classes die de server-side logica van een DocType implementeren.

## Quick Reference

### Controller Basis Structuur

```python
import frappe
from frappe.model.document import Document

class SalesOrder(Document):
    def validate(self):
        """Hoofdvalidatie - draait bij elke save."""
        if not self.items:
            frappe.throw(_("Items required"))
        self.total = sum(item.amount for item in self.items)
    
    def on_update(self):
        """Na save - wijzigingen aan self worden NIET opgeslagen."""
        self.update_linked_docs()
```

### Locatie en Naming

| DocType | Class | Bestand |
|---------|-------|---------|
| Sales Order | `SalesOrder` | `selling/doctype/sales_order/sales_order.py` |
| Custom Doc | `CustomDoc` | `module/doctype/custom_doc/custom_doc.py` |

**Regel**: DocType naam â†’ PascalCase (spaties weg) â†’ snake_case bestandsnaam

---

## Meest Gebruikte Hooks

| Hook | Wanneer | Typisch Gebruik |
|------|---------|-----------------|
| `validate` | Voor elke save | Validatie, berekeningen |
| `on_update` | Na elke save | Notifications, linked docs |
| `after_insert` | Na nieuw doc | Alleen-bij-creatie acties |
| `on_submit` | Na submit | Ledger entries, stock |
| `on_cancel` | Na cancel | Reverse ledger entries |
| `on_trash` | Voor delete | Cleanup gerelateerde data |
| `autoname` | Bij naming | Custom document name |

**Complete lijst en execution order**: Zie [lifecycle-methods.md](references/lifecycle-methods.md)

---

## Kritieke Regels

### 1. Wijzigingen na on_update worden NIET opgeslagen

```python
# âŒ FOUT - wijziging verdwijnt
def on_update(self):
    self.status = "Completed"  # Wordt NIET opgeslagen

# âœ… GOED - gebruik db_set
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "status", "Completed")
```

### 2. Geen commits in controllers

```python
# âŒ FOUT - Frappe handelt commits af
def on_update(self):
    frappe.db.commit()  # NIET DOEN

# âœ… GOED - geen commit nodig
def on_update(self):
    self.update_related()  # Frappe commit automatisch
```

### 3. Vergelijk met vorige versie via get_doc_before_save()

```python
def validate(self):
    old = self.get_doc_before_save()
    if old is None:
        # NIEUW document
        self.created_by = frappe.session.user
    else:
        # UPDATE - check wijzigingen
        if old.customer != self.customer:
            frappe.throw(_("Cannot change customer"))
```

---

## Whitelisted Methods

Maak controller methods aanroepbaar vanuit JavaScript:

```python
class SalesOrder(Document):
    @frappe.whitelist()
    def calculate_taxes(self, include_shipping=False):
        """Aanroepbaar via frm.call()"""
        tax = self.total * 0.21
        if include_shipping:
            tax += 10
        return {"tax": tax}
```

```javascript
// Client-side aanroep
frm.call('calculate_taxes', { include_shipping: true })
    .then(r => frm.set_value('tax_amount', r.message.tax));
```

**Opties**:
- `@frappe.whitelist(allow_guest=True)` - Toegankelijk zonder login
- `@frappe.whitelist(methods=['POST'])` - Alleen POST requests

---

## Autoname Patterns

### Via DocType Configuratie

| Auto Name | Voorbeeld Resultaat |
|-----------|---------------------|
| `field:customer` | Waarde van customer veld |
| `naming_series:` | Dropdown voor series |
| `SO-.#####` | SO-00001, SO-00002 |
| `INV-.YYYY.-.#####` | INV-2025-00001 |
| `hash` | Random hash |
| `prompt` | Gebruiker vult in |

### Programmatisch

```python
def autoname(self):
    from frappe.model.naming import getseries
    prefix = f"P-{self.customer[:3].upper()}-"
    self.name = getseries(prefix, 3)  # P-ABC-001
```

---

## Flags Systeem

Gebruik flags voor permission bypass en inter-hook communicatie.

### Permission Bypass

```python
doc.flags.ignore_permissions = True
doc.flags.ignore_validate = True
doc.flags.ignore_mandatory = True
doc.save()
```

### Inter-Hook Communicatie

```python
def validate(self):
    if self.total > 10000:
        self.flags.high_value = True

def on_update(self):
    if self.flags.get('high_value'):
        self.notify_manager()
```

**Complete flags documentatie**: Zie [flags.md](references/flags.md)

---

## Decision Tree: Welke Hook?

```
Wat wil je doen?
â”‚
â”œâ”€â–º Velden valideren of berekenen?
â”‚   â””â”€â–º validate
â”‚
â”œâ”€â–º Actie na save (emails, linked docs)?
â”‚   â””â”€â–º on_update
â”‚
â”œâ”€â–º Alleen voor NIEUWE docs?
â”‚   â””â”€â–º after_insert
â”‚
â”œâ”€â–º Bij SUBMIT?
â”‚   â”œâ”€â–º Check vooraf? â†’ before_submit
â”‚   â””â”€â–º Actie achteraf? â†’ on_submit
â”‚
â”œâ”€â–º Bij CANCEL?
â”‚   â”œâ”€â–º Check vooraf? â†’ before_cancel
â”‚   â””â”€â–º Cleanup? â†’ on_cancel
â”‚
â”œâ”€â–º Custom document name?
â”‚   â””â”€â–º autoname
â”‚
â””â”€â–º Cleanup voor delete?
    â””â”€â–º on_trash
```

---

## Inheritance Patronen

### Standaard Controller

```python
from frappe.model.document import Document

class MyDocType(Document):
    pass
```

### Tree DocType

```python
from frappe.utils.nestedset import NestedSet

class Department(NestedSet):
    pass
```

### Extend Bestaande Controller

```python
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class CustomSalesOrder(SalesOrder):
    def validate(self):
        super().validate()  # Belangrijk!
        self.custom_validation()
```

---

## Type Annotations (v15+)

```python
class Person(Document):
    # begin: auto-generated types
    if TYPE_CHECKING:
        from frappe.types import DF
        first_name: DF.Data
        last_name: DF.Data
        birth_date: DF.Date
    # end: auto-generated types
    pass
```

Activeer in `hooks.py`:
```python
export_python_type_annotations = True
```

---

## Reference Bestanden

| Bestand | Inhoud |
|---------|--------|
| [lifecycle-methods.md](references/lifecycle-methods.md) | Alle hooks, execution order, voorbeelden |
| [methods.md](references/methods.md) | Alle doc.* methodes met signatures |
| [flags.md](references/flags.md) | Flags systeem documentatie |

---

## Versie Verschillen (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| Type annotations | âŒ | âœ… Auto-generated |
| `before_discard` hook | âŒ | âœ… Nieuw |
| `on_discard` hook | âŒ | âœ… Nieuw |
| `flags.notify_update` | âŒ | âœ… Nieuw |
