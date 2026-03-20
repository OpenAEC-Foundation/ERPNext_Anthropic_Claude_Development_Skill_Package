# Available Methods in Server Script Sandbox

## Table of Contents

1. [Sandbox Overview](#sandbox-overview)
2. [Doc Object](#doc-object)
3. [frappe.db - Database](#frappedb---database)
4. [frappe Document Methods](#frappe-document-methods)
5. [frappe.utils - Utilities](#frappeutils---utilities)
6. [frappe Messaging](#frappe-messaging)
7. [frappe.session](#frappesession)
8. [API Script Specific](#api-script-specific)
9. [Python Builtins](#python-builtins)

---

## Sandbox Overview

Server Scripts run in a secure sandbox with limited access:

### ✅ Available

- `doc` object (in Document Event)
- `frappe` namespace (limited)
- `frappe.db` database operations
- `frappe.utils` utilities
- Limited Python builtins

### ❌ NOT Available

```python
# WRONG - These do NOT work:
import json                    # ImportError
from datetime import date      # ImportError
import requests                # ImportError
open("/etc/passwd")            # No file access
os.system("ls")                # No os module
eval("code")                   # Blocked
exec("code")                   # Blocked
```

---

## Doc Object

In Document Event scripts, the `doc` object is automatically available:

### Properties

```python
doc.name           # str: Document name/ID
doc.doctype        # str: DocType name
doc.docstatus      # int: 0=Draft, 1=Submitted, 2=Cancelled
doc.owner          # str: Creator (email)
doc.modified_by    # str: Last modified by
doc.creation       # datetime: Creation date
doc.modified       # datetime: Modification date

# Every field from the DocType
doc.customer       # Link field
doc.grand_total    # Currency field
doc.items          # Child table (list)
```

### Methods

```python
# Safe field access (no KeyError)
doc.get("fieldname")                    # Returns None if not exists
doc.get("fieldname", "default")         # With default value

# Check if field exists/has value
doc.get("status")                       # Truthy check

# Child table iteration
for item in doc.items:
    item.qty
    item.rate
    item.amount
```

### Modifying Fields

```python
# Direct assignment
doc.status = "Approved"
doc.total = 1000

# Multiple fields
doc.update({
    "status": "Approved",
    "approved_by": frappe.session.user
})
```

---

## frappe.db - Database

### Get single value

```python
# get_value(doctype, name, fieldname)
customer_name = frappe.db.get_value("Customer", "CUST-001", "customer_name")

# Multiple fields
values = frappe.db.get_value("Customer", "CUST-001", 
    ["customer_name", "territory"], as_dict=True)
# Returns: {"customer_name": "...", "territory": "..."}

# With filters (for first match)
email = frappe.db.get_value("User", {"first_name": "John"}, "email")
```

### Set value

```python
# set_value(doctype, name, fieldname, value)
frappe.db.set_value("Customer", "CUST-001", "status", "Active")

# Multiple fields
frappe.db.set_value("Customer", "CUST-001", {
    "status": "Active",
    "last_contact": frappe.utils.today()
})

# ⚠️ IMPORTANT: set_value saves directly, bypasses validation!
```

### Get multiple records

```python
# get_all(doctype, filters, fields, ...)
orders = frappe.get_all("Sales Order",
    filters={"customer": "CUST-001", "docstatus": 1},
    fields=["name", "grand_total", "transaction_date"],
    order_by="transaction_date desc",
    limit=10
)
# Returns: [{"name": "...", "grand_total": ...}, ...]

# Filter operators
filters = {
    "grand_total": [">", 1000],           # Greater than
    "status": ["in", ["Open", "Active"]], # In list
    "due_date": ["<", frappe.utils.today()], # Less than
    "name": ["like", "SO-%"],             # Pattern match
    "customer": ["is", "set"]             # Is not null
}
```

### Count

```python
count = frappe.db.count("Sales Invoice", 
    filters={"status": "Unpaid", "customer": doc.customer})
```

### Exists check

```python
if frappe.db.exists("Customer", "CUST-001"):
    # Customer exists
    pass

# With filters
if frappe.db.exists("Sales Order", {"customer": doc.customer, "docstatus": 0}):
    # Draft order exists
    pass
```

### Raw SQL (use carefully!)

```python
# ALWAYS use parameterized queries!
results = frappe.db.sql("""
    SELECT name, grand_total 
    FROM `tabSales Invoice`
    WHERE customer = %(customer)s
    AND docstatus = 1
""", {"customer": doc.customer}, as_dict=True)

# ❌ NEVER use string formatting:
# frappe.db.sql(f"SELECT * FROM tab WHERE name = '{user_input}'")  # SQL INJECTION!
```

### Commit / Rollback

```python
# After bulk operations in Scheduler scripts
frappe.db.commit()

# On errors
frappe.db.rollback()

# ⚠️ In Document Event scripts: framework handles commit/rollback
```

---

## frappe Document Methods

### Fetch document

```python
# Full document with all fields
customer = frappe.get_doc("Customer", "CUST-001")
customer.customer_name
customer.save()

# New document
new_todo = frappe.get_doc({
    "doctype": "ToDo",
    "description": "Follow up",
    "reference_type": doc.doctype,
    "reference_name": doc.name
})
new_todo.insert(ignore_permissions=True)
```

### Cached document (read-only)

```python
# Faster for frequently accessed data
customer = frappe.get_cached_doc("Customer", "CUST-001")
# ⚠️ Changes will NOT be saved!
```

### Create new document

```python
# Via get_doc
new_doc = frappe.get_doc({
    "doctype": "Sales Invoice",
    "customer": doc.customer,
    "items": [{
        "item_code": "ITEM-001",
        "qty": 1
    }]
})
new_doc.insert()

# Via new_doc helper
new_doc = frappe.new_doc("Sales Invoice")
new_doc.customer = doc.customer
new_doc.append("items", {
    "item_code": "ITEM-001",
    "qty": 1
})
new_doc.insert()
```

---

## frappe.utils - Utilities

### Date functions

```python
# Current date/time
frappe.utils.today()              # "2024-01-15" (string)
frappe.utils.now()                # "2024-01-15 10:30:00" (string)
frappe.utils.now_datetime()       # datetime object
frappe.utils.nowdate()            # Same as today()
frappe.utils.nowtime()            # "10:30:00"

# Date calculations
frappe.utils.add_days(date, 7)          # +7 days
frappe.utils.add_months(date, 1)        # +1 month
frappe.utils.add_years(date, 1)         # +1 year
frappe.utils.date_diff(date1, date2)    # Difference in days
frappe.utils.get_first_day(date)        # First day of month
frappe.utils.get_last_day(date)         # Last day of month

# Formatting
frappe.utils.formatdate(date, "dd-MM-yyyy")
frappe.utils.format_datetime(datetime)
```

### Number functions

```python
frappe.utils.flt(value)           # To float, None → 0.0
frappe.utils.cint(value)          # To int, None → 0
frappe.utils.cstr(value)          # To string, None → ""

# Round to precision
frappe.utils.rounded(123.456, 2)  # 123.46

# Formatting
frappe.utils.fmt_money(1234.56, currency="EUR")  # "€ 1,234.56"
```

### String functions

```python
frappe.utils.cstr(value)          # Safe string conversion
frappe.utils.strip_html(html)     # Remove HTML tags
frappe.utils.escape_html(text)    # Escape HTML entities
```

### JSON (instead of import json)

```python
# Parsing
data = frappe.parse_json(json_string)

# Serializing
json_string = frappe.as_json(dict_or_list)
```

### Other utilities

```python
frappe.utils.get_url()            # Site URL
frappe.utils.random_string(8)     # Random string
frappe.utils.get_fullname(user)   # User's full name
```

---

## frappe Messaging

### Throw error (stops execution)

```python
# Validation error - shows message to user
frappe.throw("This field is required")

# With title
frappe.throw("Amount too high", title="Validation Error")

# With error type
frappe.throw("Access denied", frappe.PermissionError)
```

### Information messages

```python
# Desktop notification
frappe.msgprint("Operation completed")

# With options
frappe.msgprint(
    msg="Record created",
    title="Success",
    indicator="green"  # green, blue, orange, red
)
```

### Logging

```python
# Error log (visible in Error Log list)
frappe.log_error(
    message="Error details",
    title="API Call Failed"
)

# With traceback
try:
    risky_operation()
except Exception:
    frappe.log_error(frappe.get_traceback(), "Operation failed")
```

---

## frappe.session

### Current user info

```python
frappe.session.user              # "user@example.com" or "Guest"
frappe.session.sid               # Session ID

# User roles
frappe.get_roles()               # ["System Manager", "Sales User", ...]
frappe.get_roles("user@email")   # Roles of specific user

# Check specific role
if "Sales Manager" in frappe.get_roles():
    # Has role
    pass
```

### Permissions

```python
# Check permission
if frappe.has_permission("Sales Invoice", "write"):
    # Can write
    pass

# Check for specific document
if frappe.has_permission("Sales Invoice", "write", doc.name):
    pass

# Permission types: read, write, create, delete, submit, cancel, amend
```

---

## API Script Specific

In API type Server Scripts:

### Request data

```python
# Query parameters and POST data
customer = frappe.form_dict.get("customer")
data = frappe.form_dict.get("data")

# Safe retrieval
limit = frappe.form_dict.get("limit", 10)  # With default
```

### Response

```python
# Simple response
frappe.response["message"] = {"status": "success", "data": result}

# Or direct return (only in API scripts)
# The return value automatically becomes frappe.response["message"]
```

### Request context

```python
frappe.request               # Werkzeug request object
frappe.request.method        # "GET", "POST", etc.
frappe.request.headers       # Request headers
```

---

## Python Builtins

### Available

```python
# Basic types
str, int, float, bool, list, dict, tuple, set

# Iteration
range, enumerate, zip, map, filter

# Aggregation  
sum, min, max, len, sorted, reversed

# Type checks
isinstance, type

# Logic
all, any

# Other
print  # Goes to server log
```

### NOT available

```python
# File I/O
open, file

# Code execution
eval, exec, compile

# System access
__import__  # So all imports
globals, locals, vars

# All modules (os, sys, subprocess, etc.)
```
