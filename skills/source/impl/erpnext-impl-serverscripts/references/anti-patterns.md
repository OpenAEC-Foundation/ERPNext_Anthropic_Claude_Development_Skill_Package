# Server Scripts Anti-Patterns

Common mistakes and how to avoid them.

## Sandbox Violations

### Anti-Pattern 1: Using Import Statements

```python
# ❌ WRONG - All imports are blocked
import json
from datetime import datetime
from frappe.utils import nowdate

data = json.loads(doc.custom_json)
today = datetime.now()
date = nowdate()
```

```python
# ✅ CORRECT - Use frappe's pre-loaded namespace
data = frappe.parse_json(doc.custom_json)
today = frappe.utils.now()
date = frappe.utils.nowdate()
```

**Why**: Server Scripts run in RestrictedPython sandbox. The `__import__` builtin is blocked for security.

### Anti-Pattern 2: File System Access

```python
# ❌ WRONG - open() is blocked
with open('/tmp/data.json', 'r') as f:
    data = f.read()
```

```python
# ✅ CORRECT - Use Frappe's file handling
# For attachments:
file_doc = frappe.get_doc("File", {"file_url": doc.attachment})
content = file_doc.get_content()

# For configuration:
config = frappe.db.get_single_value("My Settings", "config_json")
```

### Anti-Pattern 3: Dynamic Code Execution

```python
# ❌ WRONG - eval/exec blocked
formula = doc.price_formula
result = eval(formula)
```

```python
# ✅ CORRECT - Use explicit logic or safe evaluation
# Option 1: Predefined formulas
if doc.price_type == "markup":
    result = doc.cost * (1 + doc.markup_percent / 100)
elif doc.price_type == "fixed":
    result = doc.fixed_price

# Option 2: Use frappe.safe_eval for simple expressions (v15+)
result = frappe.safe_eval(formula, eval_locals={"cost": doc.cost})
```

---

## Database Mistakes

### Anti-Pattern 4: SQL Injection

```python
# ❌ WRONG - String formatting allows SQL injection
customer = frappe.form_dict.get("customer")
results = frappe.db.sql(f"""
    SELECT * FROM `tabSales Invoice` 
    WHERE customer = '{customer}'
""")
```

```python
# ✅ CORRECT - Use parameterized queries
customer = frappe.form_dict.get("customer")
results = frappe.db.sql("""
    SELECT * FROM `tabSales Invoice` 
    WHERE customer = %(customer)s
""", {"customer": customer}, as_dict=True)

# Or use ORM
results = frappe.db.get_all(
    "Sales Invoice",
    filters={"customer": customer}
)
```

### Anti-Pattern 5: N+1 Query Problem

```python
# ❌ WRONG - Query inside loop
for item in doc.items:
    # One query per item = N queries
    stock = frappe.db.get_value("Bin", 
        {"item_code": item.item_code, "warehouse": doc.warehouse},
        "actual_qty"
    )
    item.available_qty = stock
```

```python
# ✅ CORRECT - Batch fetch
# One query for all items
item_codes = [item.item_code for item in doc.items]
stock_data = frappe.db.get_all(
    "Bin",
    filters={
        "item_code": ["in", item_codes],
        "warehouse": doc.warehouse
    },
    fields=["item_code", "actual_qty"]
)

# Create lookup map
stock_map = {s["item_code"]: s["actual_qty"] for s in stock_data}

# Apply to items
for item in doc.items:
    item.available_qty = stock_map.get(item.item_code, 0)
```

### Anti-Pattern 6: Commit in DocType Events

```python
# ❌ WRONG - Never commit in document events
# Script Type: DocType Event, Event: Before Save

doc.total = calculate_total(doc)
frappe.db.commit()  # BAD! Framework handles this
```

```python
# ✅ CORRECT - Let framework handle commit
# Script Type: DocType Event, Event: Before Save

doc.total = calculate_total(doc)
# No commit needed - framework commits after successful save
```

**Why**: DocType Events run within a transaction. Premature commit can cause partial data or interfere with validation rollback.

### Anti-Pattern 7: Missing Commit in Scheduler

```python
# ❌ WRONG - No commit in scheduler script
# Script Type: Scheduler Event

for invoice in overdue_invoices:
    invoice.status = "Overdue"
    invoice.save()
# Changes may not persist!
```

```python
# ✅ CORRECT - Always commit in scheduler scripts
# Script Type: Scheduler Event

for invoice in overdue_invoices:
    invoice.status = "Overdue"
    invoice.save()

frappe.db.commit()  # Required in scheduler scripts
```

---

## Event Selection Mistakes

### Anti-Pattern 8: Validation in After Save

```python
# ❌ WRONG - Validation in After Save (too late!)
# Script Type: DocType Event, Event: After Save

if doc.grand_total < 0:
    frappe.throw("Total cannot be negative")  # Document already saved!
```

```python
# ✅ CORRECT - Validation in Before Save
# Script Type: DocType Event, Event: Before Save

if doc.grand_total < 0:
    frappe.throw("Total cannot be negative")  # Prevents save
```

### Anti-Pattern 9: Creating Documents in Before Save

```python
# ❌ WRONG - Creating docs in Before Save
# Script Type: DocType Event, Event: Before Save

frappe.get_doc({
    "doctype": "ToDo",
    "reference_type": doc.doctype,
    "reference_name": doc.name  # doc.name might not exist yet!
}).insert()
```

```python
# ✅ CORRECT - Create related docs in After Save/Submit
# Script Type: DocType Event, Event: After Save

frappe.get_doc({
    "doctype": "ToDo",
    "reference_type": doc.doctype,
    "reference_name": doc.name  # Now doc.name is guaranteed
}).insert()
```

### Anti-Pattern 10: Wrong Event for New vs Existing

```python
# ❌ WRONG - Before Insert for all documents
# Script Type: DocType Event, Event: Before Insert

doc.custom_sequence = get_next_sequence()
# This only runs for NEW documents, not updates!
```

```python
# ✅ CORRECT - Check document state
# Script Type: DocType Event, Event: Before Save

if doc.is_new():
    doc.custom_sequence = get_next_sequence()
else:
    # Handle update case if needed
    pass
```

---

## API Script Mistakes

### Anti-Pattern 11: Missing Permission Check

```python
# ❌ WRONG - No permission validation
# Script Type: API

customer = frappe.form_dict.get("customer")
data = frappe.get_doc("Customer", customer).as_dict()
frappe.response["message"] = data  # Anyone can access!
```

```python
# ✅ CORRECT - Check permissions
# Script Type: API

customer = frappe.form_dict.get("customer")

if not frappe.has_permission("Customer", "read", customer):
    frappe.throw("Permission denied", frappe.PermissionError)

data = frappe.get_doc("Customer", customer).as_dict()
frappe.response["message"] = data
```

### Anti-Pattern 12: Exposing Sensitive Data

```python
# ❌ WRONG - Returning entire document
# Script Type: API

customer = frappe.get_doc("Customer", customer_name)
frappe.response["message"] = customer.as_dict()  # Includes all fields!
```

```python
# ✅ CORRECT - Return only needed fields
# Script Type: API

customer_data = frappe.db.get_value(
    "Customer",
    customer_name,
    ["name", "customer_name", "territory"],  # Only public fields
    as_dict=True
)
frappe.response["message"] = customer_data
```

### Anti-Pattern 13: Not Validating Input

```python
# ❌ WRONG - Trusting user input
# Script Type: API

limit = frappe.form_dict.get("limit")
items = frappe.db.get_all("Item", limit=limit)  # Could be 1000000!
```

```python
# ✅ CORRECT - Validate and sanitize input
# Script Type: API

limit = frappe.utils.cint(frappe.form_dict.get("limit", 20))
limit = min(limit, 100)  # Cap at 100

items = frappe.db.get_all("Item", limit=limit)
```

---

## Permission Query Mistakes

### Anti-Pattern 14: Using get_all in Permission Query

```python
# ❌ WRONG - Permission Query only affects get_list
# This won't be filtered:
docs = frappe.db.get_all("Sales Invoice")  # Bypasses permission query!
```

```python
# ✅ CORRECT - Use get_list for filtered results
docs = frappe.db.get_list("Sales Invoice")  # Applies permission query
```

**Note**: `frappe.db.get_all` intentionally bypasses permission checks. Permission Query only affects `frappe.db.get_list`.

### Anti-Pattern 15: Complex Subqueries

```python
# ❌ WRONG - Complex conditions cause performance issues
conditions = f"""
    `tabSales Invoice`.customer IN (
        SELECT c.name FROM `tabCustomer` c
        JOIN `tabTerritory` t ON c.territory = t.name
        WHERE t.parent_territory IN (
            SELECT territory FROM `tabUser Territory` WHERE user = {frappe.db.escape(user)}
        )
    )
"""
```

```python
# ✅ CORRECT - Pre-calculate and simplify
# Get allowed customers once
allowed = frappe.db.sql("""
    SELECT DISTINCT c.name
    FROM `tabCustomer` c
    JOIN `tabTerritory` t ON c.territory = t.name
    JOIN `tabUser Territory` ut ON t.lft >= ut.lft AND t.rgt <= ut.rgt
    WHERE ut.user = %(user)s
""", {"user": user}, pluck="name")

if allowed:
    customer_list = ", ".join([frappe.db.escape(c) for c in allowed])
    conditions = f"`tabSales Invoice`.customer IN ({customer_list})"
else:
    conditions = "1=0"
```

---

## General Mistakes

### Anti-Pattern 16: Ignoring Errors

```python
# ❌ WRONG - Silent failure
try:
    external_api_call()
except:
    pass  # Error silently ignored
```

```python
# ✅ CORRECT - Log and handle appropriately
try:
    external_api_call()
except Exception as e:
    frappe.log_error(f"External API failed: {str(e)}", "API Integration")
    # Either re-raise or handle gracefully
    frappe.throw("External service unavailable. Please try again later.")
```

### Anti-Pattern 17: Hardcoded Values

```python
# ❌ WRONG - Hardcoded values
if doc.grand_total > 10000:  # Magic number
    doc.requires_approval = 1

tax_amount = doc.total * 0.21  # Hardcoded tax rate
```

```python
# ✅ CORRECT - Use configurable settings
approval_threshold = frappe.db.get_single_value(
    "Selling Settings", 
    "approval_threshold"
) or 10000

if doc.grand_total > approval_threshold:
    doc.requires_approval = 1

tax_rate = frappe.db.get_value(
    "Tax Rate", 
    {"is_default": 1}, 
    "rate"
) or 0.21

tax_amount = doc.total * tax_rate
```

### Anti-Pattern 18: Infinite Loops via save()

```python
# ❌ WRONG - Calling save() in Before Save triggers infinite loop
# Script Type: DocType Event, Event: Before Save

if doc.needs_recalculation:
    recalculate_totals(doc)
    doc.save()  # Triggers Before Save again → infinite loop!
```

```python
# ✅ CORRECT - Modify doc directly, let framework save
# Script Type: DocType Event, Event: Before Save

if doc.needs_recalculation:
    recalculate_totals(doc)
    # Don't call save() - framework handles it
```

### Anti-Pattern 19: Using msgprint for Validation

```python
# ❌ WRONG - msgprint doesn't stop save
if doc.grand_total < 0:
    frappe.msgprint("Total cannot be negative")
    # Document still saves!
```

```python
# ✅ CORRECT - throw() stops execution and prevents save
if doc.grand_total < 0:
    frappe.throw("Total cannot be negative")
    # Execution stops, save is prevented
```

---

## Quick Reference: Do's and Don'ts

| Don't | Do |
|-------|-----|
| `import json` | `frappe.parse_json()` |
| `import datetime` | `frappe.utils.getdate()` |
| `open(file)` | `frappe.get_doc("File")` |
| `eval(expr)` | Explicit logic |
| SQL string formatting | Parameterized queries |
| Query in loop | Batch fetch |
| `frappe.db.commit()` in events | Let framework handle |
| Validate in After Save | Validate in Before Save |
| Create docs in Before Save | Create in After Save |
| `get_all` for user data | `get_list` with permissions |
| `except: pass` | Log and handle errors |
| Hardcoded values | Settings/configuration |
| `doc.save()` in Before Save | Direct modification |
| `msgprint` for errors | `throw` for validation |
