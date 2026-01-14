---
name: erpnext-syntax-controllers
description: >
  Deterministische syntax voor Frappe Document Controllers (Python server-side).
  Gebruik wanneer Claude code moet genereren voor DocType controllers, lifecycle
  hooks (validate, on_update, on_submit, etc.), document methods, controller
  override, submittable documents, of bij vragen over controller structuur,
  naamgevingsconventies, autoname patronen, of het flags systeem.
  Triggers: controller, validate hook, on_update, on_submit, lifecycle,
  document class, autoname, flags, override controller, doc_events,
  submittable, virtual doctype.
---

# ERPNext Syntax: Document Controllers

Document Controllers zijn Python classes die de server-side logica van een DocType implementeren.

## Quick Reference

### Controller Basisstructuur

```python
import frappe
from frappe.model.document import Document

class SalesOrder(Document):
    def validate(self):
        """Hoofdvalidatie - draait bij elke save."""
        if not self.items:
            frappe.throw(_("Items zijn verplicht"))
        self.total = sum(item.amount for item in self.items)
    
    def on_update(self):
        """Na save - wijzigingen aan self worden NIET opgeslagen."""
        self.update_linked_docs()
```

### Locatie en Naamgeving

| DocType | Class | Bestand |
|---------|-------|---------|
| Sales Order | `SalesOrder` | `selling/doctype/sales_order/sales_order.py` |
| Custom Doc | `CustomDoc` | `module/doctype/custom_doc/custom_doc.py` |

**Regel**: DocType naam → PascalCase (verwijder spaties) → snake_case bestandsnaam

---

## Meest Gebruikte Hooks

| Hook | Wanneer | Typisch Gebruik |
|------|---------|-----------------|
| `validate` | Voor elke save | Validatie, berekeningen |
| `on_update` | Na elke save | Notificaties, linked docs |
| `after_insert` | Na nieuw doc | Alleen-bij-creatie acties |
| `on_submit` | Na submit | Ledger entries, voorraad |
| `on_cancel` | Na cancel | Reverse ledger entries |
| `on_trash` | Voor delete | Cleanup gerelateerde data |
| `autoname` | Bij naamgeving | Custom document naam |

**Complete lijst en execution order**: Zie [lifecycle-methods.md](references/lifecycle-methods.md)

---

## Hook Selectie Decision Tree

```
Wat wil je doen?
│
├─► Velden valideren of berekenen?
│   └─► validate
│
├─► Actie na save (emails, linked docs)?
│   └─► on_update
│
├─► Alleen voor NIEUWE docs?
│   └─► after_insert
│
├─► Bij SUBMIT?
│   ├─► Check vooraf? → before_submit
│   └─► Actie achteraf? → on_submit
│
├─► Bij CANCEL?
│   ├─► Check vooraf? → before_cancel
│   └─► Cleanup? → on_cancel
│
├─► Custom document naam?
│   └─► autoname
│
└─► Cleanup voor delete?
    └─► on_trash
```

---

## Kritieke Regels

### 1. Wijzigingen na on_update worden NIET opgeslagen

```python
# ❌ FOUT - wijziging gaat verloren
def on_update(self):
    self.status = "Completed"  # NIET opgeslagen

# ✅ CORRECT - gebruik db_set
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "status", "Completed")
```

### 2. Geen commits in controllers

```python
# ❌ FOUT - Frappe handelt commits af
def on_update(self):
    frappe.db.commit()  # DOE DIT NIET

# ✅ CORRECT - geen commit nodig
def on_update(self):
    self.update_related()  # Frappe commit automatisch
```

### 3. Altijd super() aanroepen bij override

```python
# ❌ FOUT - parent logica wordt overgeslagen
def validate(self):
    self.custom_check()

# ✅ CORRECT - parent logica blijft behouden
def validate(self):
    super().validate()
    self.custom_check()
```

### 4. Gebruik flags voor recursie-preventie

```python
def on_update(self):
    if self.flags.get('from_linked_doc'):
        return
    
    linked = frappe.get_doc("Linked Doc", self.linked_doc)
    linked.flags.from_linked_doc = True
    linked.save()
```

---

## Controller Override

### Via hooks.py (override_doctype_class)

```python
# hooks.py
override_doctype_class = {
    "Sales Order": "custom_app.overrides.CustomSalesOrder"
}

# custom_app/overrides.py
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class CustomSalesOrder(SalesOrder):
    def validate(self):
        super().validate()
        self.custom_validation()
```

### Via doc_events (hooks.py)

```python
# hooks.py
doc_events = {
    "Sales Order": {
        "validate": "custom_app.events.validate_sales_order",
        "on_submit": "custom_app.events.on_submit_sales_order"
    }
}

# custom_app/events.py
def validate_sales_order(doc, method):
    if doc.total > 100000:
        doc.requires_approval = 1
```

**Keuze**: `override_doctype_class` voor volledige controle, `doc_events` voor losse hooks.

---

## Submittable Documents

Documents met `is_submittable = 1` hebben een docstatus lifecycle:

| docstatus | Status | Bewerkbaar | Kan naar |
|-----------|--------|------------|----------|
| 0 | Draft | ✅ Ja | 1 (Submit) |
| 1 | Submitted | ❌ Nee | 2 (Cancel) |
| 2 | Cancelled | ❌ Nee | - |

```python
class StockEntry(Document):
    def on_submit(self):
        """Na submit - maak stock ledger entries."""
        self.update_stock_ledger()
    
    def on_cancel(self):
        """Na cancel - reverse de entries."""
        self.reverse_stock_ledger()
```

---

## Virtual DocTypes

Voor externe databronnen (geen database tabel):

```python
class ExternalCustomer(Document):
    @staticmethod
    def get_list(args):
        return external_api.get_customers(args.get("filters"))
    
    @staticmethod
    def get_count(args):
        return external_api.count_customers(args.get("filters"))
    
    @staticmethod
    def get_stats(args):
        return {}
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
        super().validate()
        self.custom_validation()
```

---

## Type Annotations (v15+)

```python
class Person(Document):
    if TYPE_CHECKING:
        from frappe.types import DF
        first_name: DF.Data
        last_name: DF.Data
        birth_date: DF.Date
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
| [examples.md](references/examples.md) | Complete werkende controller voorbeelden |
| [anti-patterns.md](references/anti-patterns.md) | Veelgemaakte fouten en correcties |

---

## Versie Verschillen (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| Type annotations | ❌ | ✅ Auto-generated |
| `before_discard` hook | ❌ | ✅ Nieuw |
| `on_discard` hook | ❌ | ✅ Nieuw |
| `flags.notify_update` | ❌ | ✅ Nieuw |

---

## Anti-Patterns

### ❌ Direct veld wijzigen na on_update
```python
def on_update(self):
    self.status = "Done"  # Gaat verloren!
```

### ❌ frappe.db.commit() in controller
```python
def validate(self):
    frappe.db.commit()  # Breekt transactie!
```

### ❌ Vergeten super() aan te roepen
```python
def validate(self):
    self.my_check()  # Parent validate wordt overgeslagen
```

→ Zie [anti-patterns.md](references/anti-patterns.md) voor complete lijst.

---

## Gerelateerde Skills

- `erpnext-syntax-serverscripts` – Server Scripts (sandbox alternatief)
- `erpnext-syntax-hooks` – hooks.py configuratie
- `erpnext-impl-controllers` – Implementatie workflows
