# Server Script Anti-Patterns and Limitations

## Table of Contents

1. [Sandbox Limitations](#sandbox-limitations)
2. [Import Errors](#import-errors)
3. [Database Anti-Patterns](#database-anti-patterns)
4. [Performance Anti-Patterns](#performance-anti-patterns)
5. [Security Anti-Patterns](#security-anti-patterns)
6. [Logic Anti-Patterns](#logic-anti-patterns)
7. [Common Mistakes](#common-mistakes)

---

## Sandbox Limitations

### ❌ NO Imports Allowed

The Server Script sandbox completely blocks the Python `__import__` function.

```python
# ❌ WRONG - Every import gives error:
import json                           # ImportError: __import__ not found
from datetime import datetime         # ImportError: __import__ not found
import frappe                         # ImportError (even frappe!)
from frappe.utils import nowdate      # ImportError

# ✅ CORRECT - Use pre-loaded namespace:
data = frappe.parse_json(json_string)    # Instead of json.loads()
today = frappe.utils.nowdate()           # Directly available
now = frappe.utils.now_datetime()        # Instead of datetime.now()
```

### ❌ NO File System Access

```python
# ❌ WRONG:
open("/tmp/data.txt", "r")            # NameError: name 'open' is not defined
file = open("export.csv", "w")        # Not available

# ✅ ALTERNATIVE - Use Frappe's file handling:
# Create File doc for attachments, or log to Error Log
frappe.log_error(data, "Export Data")
```

### ❌ NO OS/System Commands

```python
# ❌ WRONG:
import os                              # ImportError
os.system("ls")                        # Not available
subprocess.run(["echo", "hi"])         # Not available

# ✅ ALTERNATIVE:
# Use whitelisted methods in a custom app for system operations
```

### ❌ NO Code Execution

```python
# ❌ WRONG - Blocked for security:
eval("1 + 1")                          # Blocked
exec("print('hello')")                 # Blocked
compile("code", "", "exec")            # Blocked

# ✅ ALTERNATIVE:
# Write the logic directly, no dynamic code execution
```

### ❌ NO External HTTP Requests

```python
# ❌ WRONG:
import requests                        # ImportError
requests.get("https://api.example.com")  # Not available

# ✅ ALTERNATIVE:
# Use background jobs in custom app with frappe.enqueue
# Or Server Script type API to expose endpoints
```

---

## Import Errors

### The most confusing error

```
ImportError: __import__ not found
```

**Cause**: ANY import statement in Server Scripts

**Wrong examples**:
```python
# ❌ All of these give ImportError:
import json
import re
import math
from datetime import date, timedelta
from collections import defaultdict
import frappe  # Yes, even this!
from frappe.utils import cint
```

**Solutions**:

| Instead of | Use |
|------------|-----|
| `import json` | `frappe.parse_json()`, `frappe.as_json()` |
| `from datetime import date` | `frappe.utils.today()`, `frappe.utils.now_datetime()` |
| `import math` | Python builtins: `sum()`, `min()`, `max()`, `round()` |
| `from collections import defaultdict` | Regular `dict` with `.get(key, default)` |
| `import re` | Not available - restructure logic |
| `from frappe.utils import cint` | `frappe.utils.cint()` (namespace already loaded) |

---

## Database Anti-Patterns

### ❌ SQL Injection Vulnerability

```python
# ❌ DANGEROUS - Never do this:
frappe.db.sql(f"SELECT * FROM tabUser WHERE name = '{user_input}'")
frappe.db.sql("SELECT * FROM tabUser WHERE name = '" + user_input + "'")

# ✅ SAFE - Always use parameterized queries:
frappe.db.sql("""
    SELECT * FROM `tabUser` 
    WHERE name = %(user)s
""", {"user": user_input}, as_dict=True)

# ✅ OR use get_all/get_value (automatically safe):
frappe.get_all("User", filters={"name": user_input})
```

### ❌ N+1 Query Problem

```python
# ❌ WRONG - Query in loop:
for item in doc.items:
    item_name = frappe.db.get_value("Item", item.item_code, "item_name")
    # This does N queries for N items!

# ✅ CORRECT - Batch fetch:
item_codes = [item.item_code for item in doc.items]
items_data = {d.name: d for d in frappe.get_all(
    "Item",
    filters={"name": ["in", item_codes]},
    fields=["name", "item_name"]
)}
for item in doc.items:
    item_name = items_data.get(item.item_code, {}).get("item_name")
```

### ❌ Unnecessary Commit in Document Events

```python
# ❌ WRONG in Document Event scripts:
doc.total = 100
frappe.db.commit()  # Not needed, framework does this!

# ✅ CORRECT:
doc.total = 100  # Framework handles commit

# ⚠️ EXCEPTION - In Scheduler scripts commit IS needed:
for record in records:
    frappe.db.set_value("Sales Order", record.name, "status", "Processed")
frappe.db.commit()  # Required in scheduler
```

### ❌ set_value for Complex Updates

```python
# ❌ RISKY - Bypasses all validation:
frappe.db.set_value("Sales Invoice", "SINV-001", "grand_total", 1000)
# This skips validate, permissions, and linked doc updates!

# ✅ BETTER - Full document flow:
inv = frappe.get_doc("Sales Invoice", "SINV-001")
inv.grand_total = 1000
inv.save()  # Triggers validate, permissions check, etc.
```

---

## Performance Anti-Patterns

### ❌ Fetching Entire Documents for One Field

```python
# ❌ INEFFICIENT:
customer = frappe.get_doc("Customer", doc.customer)
email = customer.email_id  # Fetches ALL fields

# ✅ EFFICIENT:
email = frappe.db.get_value("Customer", doc.customer, "email_id")
```

### ❌ SELECT * in Queries

```python
# ❌ INEFFICIENT:
orders = frappe.get_all("Sales Order", filters={...}, fields=["*"])

# ✅ EFFICIENT - Only needed fields:
orders = frappe.get_all("Sales Order", 
    filters={...}, 
    fields=["name", "grand_total", "status"])
```

### ❌ No Limits on Queries

```python
# ❌ DANGEROUS - Could return thousands of records:
all_invoices = frappe.get_all("Sales Invoice", filters={"docstatus": 1})

# ✅ SAFE - Always limit:
recent_invoices = frappe.get_all("Sales Invoice",
    filters={"docstatus": 1},
    limit=100,
    order_by="creation desc")
```

### ❌ Heavy Calculations in Before Save

```python
# ❌ PROBLEMATIC - Slows down every save:
def before_save():
    # Heavy aggregation over thousands of records
    total = frappe.db.sql("""
        SELECT SUM(grand_total) FROM `tabSales Invoice`
        WHERE customer = %(customer)s
    """, {"customer": doc.customer})[0][0]
    doc.lifetime_value = total

# ✅ BETTER - Do heavy calculations in background:
# Use Scheduler Event or background job
```

---

## Security Anti-Patterns

### ❌ Skipping Permission Checks

```python
# ❌ DANGEROUS - No permission check:
def api_get_customer(customer):
    return frappe.get_doc("Customer", customer).as_dict()
    # Any user can query any customer!

# ✅ SAFE:
def api_get_customer(customer):
    if not frappe.has_permission("Customer", "read", customer):
        frappe.throw("Access denied", frappe.PermissionError)
    return frappe.get_doc("Customer", customer).as_dict()
```

### ❌ ignore_permissions Everywhere

```python
# ❌ DANGEROUS - Avoid where possible:
doc.insert(ignore_permissions=True)
doc.save(ignore_permissions=True)
frappe.get_doc("Sensitive Doc", name).delete(ignore_permissions=True)

# ✅ CORRECT - Only with explicit reason:
# Only use for:
# - System-generated records (logs, audit trails)
# - Background jobs running as system
# - After explicit permission check on parent

# Example legitimate use:
if frappe.has_permission("Sales Order", "write", parent_doc.name):
    # ToDo may be created if user has write on parent
    todo = frappe.get_doc({...})
    todo.insert(ignore_permissions=True)
```

### ❌ Sensitive Data in Logs

```python
# ❌ WRONG:
frappe.log_error(f"Login attempt: user={user}, password={password}")

# ✅ CORRECT:
frappe.log_error(f"Failed login attempt for user: {user}")
```

---

## Logic Anti-Patterns

### ❌ Infinite Loops from Recursive Save

```python
# ❌ WRONG - Infinite loop:
# In Before Save:
doc.total = calculate_total(doc)
doc.save()  # Triggers Before Save again!

# ✅ CORRECT - Modify doc, don't save:
# In Before Save:
doc.total = calculate_total(doc)
# NO save() call - framework does this
```

### ❌ Throw After Database Changes

```python
# ❌ PROBLEMATIC:
def before_save():
    # First create something...
    frappe.get_doc({"doctype": "Log", ...}).insert()
    
    # Then validate...
    if doc.total < 0:
        frappe.throw("Invalid total")
    # The Log is already created, even though save fails!

# ✅ CORRECT - Validate BEFORE side effects:
def before_save():
    # First all validations
    if doc.total < 0:
        frappe.throw("Invalid total")
    
    # Then side effects
    frappe.get_doc({"doctype": "Log", ...}).insert()
```

### ❌ Relying on Event Order

```python
# ❌ FRAGILE:
# Script 1 (Before Save): doc.calculated_value = complex_calc()
# Script 2 (Before Save): doc.derived = doc.calculated_value * 2
# Order of Server Scripts is NOT guaranteed!

# ✅ ROBUST - Self-contained scripts:
# Each script should work independently
# Or combine logic in one script
```

---

## Common Mistakes

### Mistake 1: Forgetting that Before Save = validate

```python
# ❌ CONFUSION:
# Developer thinks: "Before Save runs before validate"
# But: Before Save IS validate!

# If you need code BEFORE validate:
# Use "Before Validate" in Server Script UI
```

### Mistake 2: Using doc.name in Before Insert

```python
# ❌ WRONG in Before Insert:
frappe.msgprint(f"Creating {doc.name}")  
# doc.name may not be set yet!

# ✅ CORRECT:
frappe.msgprint(f"Creating new {doc.doctype}")
# Or wait for After Insert for doc.name
```

### Mistake 3: Expecting changes in After Save to auto-save

```python
# ❌ WRONG in After Save:
doc.note = "Updated after save"
# This will NOT be saved!

# ✅ CORRECT:
doc.db_set("note", "Updated after save", update_modified=False)
# Or:
frappe.db.set_value(doc.doctype, doc.name, "note", "Updated")
```

### Mistake 4: Permission Query that over-filters

```python
# ❌ WRONG - Filters even for System Manager:
conditions = f"owner = {frappe.db.escape(user)}"

# ✅ CORRECT - Check roles first:
if "System Manager" in frappe.get_roles(user):
    conditions = ""
else:
    conditions = f"owner = {frappe.db.escape(user)}"
```

### Mistake 5: API without input validation

```python
# ❌ WRONG:
customer = frappe.form_dict.customer  # KeyError if not provided
data = frappe.get_doc("Customer", customer)  # Crash on None

# ✅ CORRECT:
customer = frappe.form_dict.get("customer")
if not customer:
    frappe.throw("Parameter 'customer' is required")
if not frappe.db.exists("Customer", customer):
    frappe.throw("Customer not found")
```

### Mistake 6: Scheduler without commit

```python
# ❌ WRONG in Scheduler Event:
for inv in invoices:
    frappe.db.set_value("Sales Invoice", inv.name, "reminder_sent", 1)
# Changes are NOT committed!

# ✅ CORRECT:
for inv in invoices:
    frappe.db.set_value("Sales Invoice", inv.name, "reminder_sent", 1)
frappe.db.commit()  # Required in scheduler scripts
```

---

## Quick Reference: Do's and Don'ts

| Don't ❌ | Do ✅ |
|----------|-------|
| `import json` | `frappe.parse_json()` |
| `from datetime import date` | `frappe.utils.today()` |
| `f"WHERE x = '{var}'"` | `"WHERE x = %(var)s", {"var": var}` |
| `doc.save()` in Before Save | Direct `doc.field = value` |
| `frappe.db.commit()` in Before Save | (framework does commit) |
| No limit on get_all | `limit=100` |
| `fields=["*"]` | `fields=["name", "status"]` |
| `ignore_permissions=True` everywhere | Explicitly check permissions |
| `doc.name` in Before Insert | Wait for After Insert |
