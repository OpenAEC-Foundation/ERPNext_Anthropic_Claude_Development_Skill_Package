---
name: erpnext-syntax-controllers
description: >
  Deterministic syntax for Frappe Document Controllers (Python server-side).
  Use when Claude needs to generate code for DocType controllers, lifecycle
  hooks (validate, on_update, on_submit, etc.), document methods, controller
  override, submittable documents, or when questions concern controller structure,
  naming conventions, autoname patterns, or the flags system.
  Triggers: controller, validate hook, on_update, on_submit, lifecycle,
  document class, autoname, flags, override controller, doc_events,
  submittable, virtual doctype.
---

# ERPNext Syntax: Document Controllers

Document Controllers are Python classes that implement the server-side logic of a DocType.

## Quick Reference

### Controller Basic Structure

```python
import frappe
from frappe.model.document import Document

class SalesOrder(Document):
    def validate(self):
        """Main validation - runs on every save."""
        if not self.items:
            frappe.throw(_("Items are required"))
        self.total = sum(item.amount for item in self.items)
    
    def on_update(self):
        """After save - changes to self are NOT saved."""
        self.update_linked_docs()
```

### Location and Naming

| DocType | Class | File |
|---------|-------|------|
| Sales Order | `SalesOrder` | `selling/doctype/sales_order/sales_order.py` |
| Custom Doc | `CustomDoc` | `module/doctype/custom_doc/custom_doc.py` |

**Rule**: DocType name → PascalCase (remove spaces) → snake_case filename

---

## Most Used Hooks

| Hook | When | Typical Use |
|------|------|-------------|
| `validate` | Before every save | Validation, calculations |
| `on_update` | After every save | Notifications, linked docs |
| `after_insert` | After new doc | Creation-only actions |
| `on_submit` | After submit | Ledger entries, stock |
| `on_cancel` | After cancel | Reverse ledger entries |
| `on_trash` | Before delete | Cleanup related data |
| `autoname` | On naming | Custom document name |

**Complete list and execution order**: See [lifecycle-methods.md](references/lifecycle-methods.md)

---

## Hook Selection Decision Tree

```
What do you want to do?
│
├─► Validate or calculate fields?
│   └─► validate
│
├─► Action after save (emails, linked docs)?
│   └─► on_update
│
├─► Only for NEW docs?
│   └─► after_insert
│
├─► On SUBMIT?
│   ├─► Check beforehand? → before_submit
│   └─► Action afterwards? → on_submit
│
├─► On CANCEL?
│   ├─► Check beforehand? → before_cancel
│   └─► Cleanup? → on_cancel
│
├─► Custom document name?
│   └─► autoname
│
└─► Cleanup before delete?
    └─► on_trash
```

---

## Critical Rules

### 1. Changes after on_update are NOT saved

```python
# ❌ WRONG - change is lost
def on_update(self):
    self.status = "Completed"  # NOT saved

# ✅ CORRECT - use db_set
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "status", "Completed")
```

### 2. No commits in controllers

```python
# ❌ WRONG - Frappe handles commits
def on_update(self):
    frappe.db.commit()  # DON'T DO THIS

# ✅ CORRECT - no commit needed
def on_update(self):
    self.update_related()  # Frappe commits automatically
```

### 3. Always call super() when overriding

```python
# ❌ WRONG - parent logic is skipped
def validate(self):
    self.custom_check()

# ✅ CORRECT - parent logic is preserved
def validate(self):
    super().validate()
    self.custom_check()
```

### 4. Use flags for recursion prevention

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

**Choice**: `override_doctype_class` for full control, `doc_events` for individual hooks.

---

## Submittable Documents

Documents with `is_submittable = 1` have a docstatus lifecycle:

| docstatus | Status | Editable | Can go to |
|-----------|--------|----------|-----------|
| 0 | Draft | ✅ Yes | 1 (Submit) |
| 1 | Submitted | ❌ No | 2 (Cancel) |
| 2 | Cancelled | ❌ No | - |

```python
class StockEntry(Document):
    def on_submit(self):
        """After submit - create stock ledger entries."""
        self.update_stock_ledger()
    
    def on_cancel(self):
        """After cancel - reverse the entries."""
        self.reverse_stock_ledger()
```

---

## Virtual DocTypes

For external data sources (no database table):

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

## Inheritance Patterns

### Standard Controller
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

### Extend Existing Controller
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

Enable in `hooks.py`:
```python
export_python_type_annotations = True
```

---

## Reference Files

| File | Contents |
|------|----------|
| [lifecycle-methods.md](references/lifecycle-methods.md) | All hooks, execution order, examples |
| [methods.md](references/methods.md) | All doc.* methods with signatures |
| [flags.md](references/flags.md) | Flags system documentation |
| [examples.md](references/examples.md) | Complete working controller examples |
| [anti-patterns.md](references/anti-patterns.md) | Common mistakes and corrections |

---

## Version Differences (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| Type annotations | ❌ | ✅ Auto-generated |
| `before_discard` hook | ❌ | ✅ New |
| `on_discard` hook | ❌ | ✅ New |
| `flags.notify_update` | ❌ | ✅ New |

---

## Anti-Patterns

### ❌ Direct field change after on_update
```python
def on_update(self):
    self.status = "Done"  # Will be lost!
```

### ❌ frappe.db.commit() in controller
```python
def validate(self):
    frappe.db.commit()  # Breaks transaction!
```

### ❌ Forgetting to call super()
```python
def validate(self):
    self.my_check()  # Parent validate is skipped
```

→ See [anti-patterns.md](references/anti-patterns.md) for complete list.

---

## Related Skills

- `erpnext-syntax-serverscripts` – Server Scripts (sandbox alternative)
- `erpnext-syntax-hooks` – hooks.py configuration
- `erpnext-impl-controllers` – Implementation workflows
