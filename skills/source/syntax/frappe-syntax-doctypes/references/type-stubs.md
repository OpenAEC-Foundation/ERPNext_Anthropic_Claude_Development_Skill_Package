# Python Type Stubs for Frappe

The `frappe.types` module provides Python type hints for DocField values and common Frappe data structures. These types enable IDE autocompletion, static analysis, and self-documenting controllers.

## Module Structure

```
frappe/types/
├── __init__.py          # Re-exports: Filters, FilterSignature, FilterTuple, _dict
├── DF.py                # DocField type aliases (32 types)
├── filter.py            # Filter types: FilterTuple, Filters, FilterSignature
├── frappedict.py        # _dict class (attribute-access dict)
├── exporter.py          # TypeExporter -- auto-generates type stubs in controllers
└── lazytranslatedstring.py  # _LazyTranslate for deferred translations
```

## DF Module -- DocField Type Aliases

`frappe.types.DF` maps every Frappe fieldtype to a Python type:

| DF Type | Python Type | Fieldtype |
|---------|-------------|-----------|
| `DF.Data` | `str` | Data, Autocomplete, Attach, AttachImage, Barcode, Color, Link, DynamicLink, Password, Phone, ReadOnly |
| `DF.Text` | `str` | Text, Code, HTMLEditor, JSON, LongText, MarkdownEditor, SmallText, TextEditor |
| `DF.Int` | `int` | Int |
| `DF.Float` | `float` | Float |
| `DF.Currency` | `float` | Currency |
| `DF.Percent` | `float` | Percent |
| `DF.Rating` | `float` | Rating |
| `DF.Check` | `bool \| int` | Check |
| `DF.Duration` | `int` | Duration (seconds) |
| `DF.Date` | `str \| date` | Date |
| `DF.Datetime` | `str \| datetime` | Datetime |
| `DF.Time` | `str \| time` | Time |
| `DF.Select` | `Literal` | Select (parameterized with options) |
| `DF.Table` | `list` | Table (parameterized with child type) |
| `DF.TableMultiSelect` | `list` | Table MultiSelect |

## Auto-Generated Type Stubs (TypeExporter)

Frappe automatically generates type annotations in controller files when a DocType schema is saved. The `TypeExporter` class in `frappe/types/exporter.py` handles this.

### Generated Code Block

The exporter inserts a guarded block in the controller:

```python
class SalesInvoice(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from erpnext.stock.doctype.sales_invoice_item.sales_invoice_item import SalesInvoiceItem

        company: DF.Link
        customer: DF.Link
        customer_name: DF.Data | None
        grand_total: DF.Currency
        is_return: DF.Check
        items: DF.Table[SalesInvoiceItem]
        posting_date: DF.Date
        status: DF.Literal["Draft", "Submitted", "Paid", "Cancelled"]

    # end: auto-generated types
```

### Key Behaviors

- **Trigger**: Runs on DocType save (schema update)
- **Location**: Inserts into the controller `.py` file between `# begin: auto-generated types` and `# end: auto-generated types`
- **Idempotent**: Replaces existing block on re-export; adds after class definition if block is absent
- **Validation**: Parses generated code with `ast.parse()` before writing -- NEVER writes invalid Python
- **Indentation**: Auto-detects tabs vs spaces from the controller file

### Nullable vs Non-Nullable

Fields that are NOT nullable (NEVER `| None`):

- `Check`, `Currency`, `Float`, `Int`, `Percent`, `Rating` -- numeric defaults to 0
- `Select` -- defaults to first option
- `Table`, `Table MultiSelect` -- defaults to empty list
- Fields with `reqd=1` or `not_nullable=1`

All other fields include `| None` in their type annotation.

### Table Field Parameterization

Table fields include the child DocType's controller class as a generic parameter:

```python
if TYPE_CHECKING:
    from erpnext.stock.doctype.sales_invoice_item.sales_invoice_item import SalesInvoiceItem

    items: DF.Table[SalesInvoiceItem]
```

### Select Field Parameterization

Select fields use `DF.Literal` with the options list:

```python
status: DF.Literal["Draft", "Submitted", "Paid", "Cancelled"]
```

## The TYPE_CHECKING Guard Pattern

ALWAYS use `TYPE_CHECKING` to prevent runtime import overhead:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frappe.types import DF
```

This block is NEVER executed at runtime -- it only runs during static analysis (mypy, pyright, IDE indexing). This avoids circular imports and keeps controller startup fast.

## Filter Types

The `frappe.types.filter` module provides type-safe filter construction:

```python
from frappe.types import Filters, FilterTuple, FilterSignature

# FilterTuple -- single filter condition
f = FilterTuple(doctype="Sales Invoice", fieldname="status", operator="=", value="Draft")

# Filters -- collection of FilterTuple objects
filters = Filters([
    ("Sales Invoice", "status", "=", "Draft"),
    ("Sales Invoice", "docstatus", "=", 1),
])

# Filters.optimize() -- consolidates equality filters into "in" operator
filters.optimize()
```

### FilterSignature Type Alias

`FilterSignature` accepts multiple input formats:

```python
# All valid FilterSignature inputs:
filters: FilterSignature = Filters([...])                    # Filters object
filters: FilterSignature = [("doctype", "field", "=", "v")]  # List of tuples
filters: FilterSignature = {"field": "value"}                # Dict mapping
filters: FilterSignature = ("field", "=", "value")           # Single tuple
```

## The _dict Class

`frappe._dict` (re-exported from `frappe.types`) enables attribute-style access on dicts:

```python
from frappe import _dict

d = _dict(name="INV-001", status="Draft")
print(d.name)      # "INV-001" -- attribute access
print(d["name"])    # "INV-001" -- dict access
d.update(total=500) # returns self (chainable)
```

- `__getattr__` delegates to `dict.get` (returns `None` for missing keys, never raises `AttributeError`)
- `update()` returns `self` for method chaining
- NEVER use `hasattr()` to check key existence on `_dict` -- it always returns `True`. Use `key in d` instead.

## IDE Integration

### mypy Configuration

```ini
# mypy.ini or pyproject.toml [tool.mypy]
[mypy]
plugins = []
ignore_missing_imports = true
```

mypy recognizes the `TYPE_CHECKING` guard and processes `DF.*` annotations during analysis.

### pyright / Pylance (VS Code)

pyright natively understands `TYPE_CHECKING` blocks. The auto-generated stubs provide:
- Field name autocompletion on `self.fieldname`
- Type checking on assignments (`self.grand_total = "wrong"` flags as error)
- Go-to-definition on child table types

### Limitations

- Type stubs are generated per-DocType, NOT globally. Custom DocTypes need a schema save to generate stubs.
- `frappe.get_doc()` returns `Document` by default -- callers outside the controller do NOT get typed fields unless explicitly annotated.
- Customizations (Custom Fields, Property Setters) are NOT reflected in auto-generated stubs.

## Typing Patterns for Custom Code

### Pattern 1: Typed Controller Method

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frappe.types import DF

class MyDocType(Document):
    # auto-generated types here...

    def validate(self):
        # self.fieldname is now typed
        if self.status == "Draft":
            self.grand_total = sum(row.amount for row in self.items)
```

### Pattern 2: External Code with Explicit Annotation

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from myapp.doctype.my_doctype.my_doctype import MyDocType

def process_doc(name: str) -> None:
    doc: "MyDocType" = frappe.get_doc("My DocType", name)  # type: ignore
    print(doc.grand_total)  # IDE knows this is DF.Currency (float)
```

### Pattern 3: Whitelisted API with Return Type

```python
import frappe
from frappe import _dict

@frappe.whitelist()
def get_summary(doctype: str, name: str) -> _dict:
    doc = frappe.get_doc(doctype, name)
    return _dict(
        name=doc.name,
        status=doc.status,
        total=doc.grand_total,
    )
```

## Critical Rules

1. NEVER modify code between `# begin: auto-generated types` and `# end: auto-generated types` -- it will be overwritten on next DocType save.
2. ALWAYS use the `TYPE_CHECKING` guard for `DF` imports -- importing at runtime wastes startup time.
3. NEVER assume `frappe.get_doc()` returns a typed controller outside the controller file itself -- annotate explicitly.
4. ALWAYS re-save the DocType in the UI (or run bench migrate) after adding fields to regenerate type stubs.
5. NEVER use `hasattr()` on `frappe._dict` to check for keys -- use `key in d` or `d.get(key)`.

## Source Files

| File | Purpose |
|------|---------|
| `frappe/types/__init__.py` | Package exports: `Filters`, `FilterSignature`, `FilterTuple`, `_dict` |
| `frappe/types/DF.py` | 32 DocField type aliases |
| `frappe/types/filter.py` | `FilterTuple`, `Filters`, `FilterSignature` types |
| `frappe/types/frappedict.py` | `_dict` class with attribute access |
| `frappe/types/exporter.py` | `TypeExporter` -- auto-generates stubs in controllers |
| `frappe/types/lazytranslatedstring.py` | `_LazyTranslate` for deferred i18n |
