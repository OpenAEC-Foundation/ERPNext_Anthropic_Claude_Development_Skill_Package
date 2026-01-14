# Beschikbare Methods in Server Script Sandbox

## Inhoudsopgave

1. [Sandbox Overzicht](#sandbox-overzicht)
2. [Doc Object](#doc-object)
3. [frappe.db - Database](#frappedb---database)
4. [frappe Document Methods](#frappe-document-methods)
5. [frappe.utils - Utilities](#frappeutils---utilities)
6. [frappe Messaging](#frappe-messaging)
7. [frappe.session](#frappesession)
8. [API Script Specifiek](#api-script-specifiek)
9. [Python Builtins](#python-builtins)

---

## Sandbox Overzicht

Server Scripts draaien in een beveiligde sandbox met beperkte toegang:

### ✅ Beschikbaar

- `doc` object (bij Document Event)
- `frappe` namespace (beperkt)
- `frappe.db` database operaties
- `frappe.utils` utilities
- Beperkte Python builtins

### ❌ NIET Beschikbaar

```python
# FOUT - Deze werken NIET:
import json                    # ImportError
from datetime import date      # ImportError
import requests                # ImportError
open("/etc/passwd")            # Geen file access
os.system("ls")                # Geen os module
eval("code")                   # Geblokkeerd
exec("code")                   # Geblokkeerd
```

---

## Doc Object

Bij Document Event scripts is het `doc` object automatisch beschikbaar:

### Properties

```python
doc.name           # str: Document naam/ID
doc.doctype        # str: DocType naam
doc.docstatus      # int: 0=Draft, 1=Submitted, 2=Cancelled
doc.owner          # str: Aanmaker (email)
doc.modified_by    # str: Laatst gewijzigd door
doc.creation       # datetime: Aanmaakdatum
doc.modified       # datetime: Wijzigingsdatum

# Elk veld van het DocType
doc.customer       # Link veld
doc.grand_total    # Currency veld
doc.items          # Child table (lijst)
```

### Methods

```python
# Veilig veld ophalen (geen KeyError)
doc.get("fieldname")                    # Returns None als niet bestaat
doc.get("fieldname", "default")         # Met default waarde

# Check of veld bestaat/waarde heeft
doc.get("status")                       # Truthy check

# Child table iteratie
for item in doc.items:
    item.qty
    item.rate
    item.amount
```

### Velden Wijzigen

```python
# Direct toewijzen
doc.status = "Approved"
doc.total = 1000

# Meerdere velden
doc.update({
    "status": "Approved",
    "approved_by": frappe.session.user
})
```

---

## frappe.db - Database

### Enkele waarde ophalen

```python
# get_value(doctype, name, fieldname)
customer_name = frappe.db.get_value("Customer", "CUST-001", "customer_name")

# Meerdere velden
values = frappe.db.get_value("Customer", "CUST-001", 
    ["customer_name", "territory"], as_dict=True)
# Returns: {"customer_name": "...", "territory": "..."}

# Met filters (voor eerste match)
email = frappe.db.get_value("User", {"first_name": "John"}, "email")
```

### Waarde zetten

```python
# set_value(doctype, name, fieldname, value)
frappe.db.set_value("Customer", "CUST-001", "status", "Active")

# Meerdere velden
frappe.db.set_value("Customer", "CUST-001", {
    "status": "Active",
    "last_contact": frappe.utils.today()
})

# ⚠️ BELANGRIJK: set_value slaat direct op, bypass validatie!
```

### Meerdere records ophalen

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

### Aantal tellen

```python
count = frappe.db.count("Sales Invoice", 
    filters={"status": "Unpaid", "customer": doc.customer})
```

### Bestaat check

```python
if frappe.db.exists("Customer", "CUST-001"):
    # Customer bestaat
    pass

# Met filters
if frappe.db.exists("Sales Order", {"customer": doc.customer, "docstatus": 0}):
    # Draft order bestaat
    pass
```

### Raw SQL (voorzichtig!)

```python
# ALTIJD parameterized queries gebruiken!
results = frappe.db.sql("""
    SELECT name, grand_total 
    FROM `tabSales Invoice`
    WHERE customer = %(customer)s
    AND docstatus = 1
""", {"customer": doc.customer}, as_dict=True)

# ❌ NOOIT string formatting:
# frappe.db.sql(f"SELECT * FROM tab WHERE name = '{user_input}'")  # SQL INJECTION!
```

### Commit / Rollback

```python
# Na bulk operaties in Scheduler scripts
frappe.db.commit()

# Bij errors
frappe.db.rollback()

# ⚠️ In Document Event scripts: framework handelt commit/rollback af
```

---

## frappe Document Methods

### Document ophalen

```python
# Volledig document met alle velden
customer = frappe.get_doc("Customer", "CUST-001")
customer.customer_name
customer.save()

# Nieuw document
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
# Sneller voor frequent accessed data
customer = frappe.get_cached_doc("Customer", "CUST-001")
# ⚠️ Wijzigingen worden NIET opgeslagen!
```

### Nieuw document maken

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

### Datum functies

```python
# Huidige datum/tijd
frappe.utils.today()              # "2024-01-15" (string)
frappe.utils.now()                # "2024-01-15 10:30:00" (string)
frappe.utils.now_datetime()       # datetime object
frappe.utils.nowdate()            # Zelfde als today()
frappe.utils.nowtime()            # "10:30:00"

# Datum berekeningen
frappe.utils.add_days(date, 7)          # +7 dagen
frappe.utils.add_months(date, 1)        # +1 maand
frappe.utils.add_years(date, 1)         # +1 jaar
frappe.utils.date_diff(date1, date2)    # Verschil in dagen
frappe.utils.get_first_day(date)        # Eerste dag van maand
frappe.utils.get_last_day(date)         # Laatste dag van maand

# Formatteren
frappe.utils.formatdate(date, "dd-MM-yyyy")
frappe.utils.format_datetime(datetime)
```

### Getal functies

```python
frappe.utils.flt(value)           # Naar float, None → 0.0
frappe.utils.cint(value)          # Naar int, None → 0
frappe.utils.cstr(value)          # Naar string, None → ""

# Afronden op precision
frappe.utils.rounded(123.456, 2)  # 123.46

# Formatting
frappe.utils.fmt_money(1234.56, currency="EUR")  # "€ 1,234.56"
```

### String functies

```python
frappe.utils.cstr(value)          # Safe string conversion
frappe.utils.strip_html(html)     # Remove HTML tags
frappe.utils.escape_html(text)    # Escape HTML entities
```

### JSON (in plaats van import json)

```python
# Parsing
data = frappe.parse_json(json_string)

# Serializing
json_string = frappe.as_json(dict_or_list)
```

### Andere utilities

```python
frappe.utils.get_url()            # Site URL
frappe.utils.random_string(8)     # Random string
frappe.utils.get_fullname(user)   # User's full name
```

---

## frappe Messaging

### Error gooien (stopt executie)

```python
# Validatie error - toont message aan user
frappe.throw("Dit veld is verplicht")

# Met titel
frappe.throw("Bedrag te hoog", title="Validatie Error")

# Met error type
frappe.throw("Geen toegang", frappe.PermissionError)
```

### Informatie messages

```python
# Desktop notification
frappe.msgprint("Bewerking voltooid")

# Met opties
frappe.msgprint(
    msg="Record aangemaakt",
    title="Succes",
    indicator="green"  # green, blue, orange, red
)
```

### Logging

```python
# Error log (zichtbaar in Error Log list)
frappe.log_error(
    message="Details van de error",
    title="API Call Failed"
)

# Met traceback
try:
    risico_operatie()
except Exception:
    frappe.log_error(frappe.get_traceback(), "Operatie mislukt")
```

---

## frappe.session

### Huidige gebruiker info

```python
frappe.session.user              # "user@example.com" of "Guest"
frappe.session.sid               # Session ID

# Gebruiker rollen
frappe.get_roles()               # ["System Manager", "Sales User", ...]
frappe.get_roles("user@email")   # Rollen van specifieke user

# Check specifieke rol
if "Sales Manager" in frappe.get_roles():
    # Heeft rol
    pass
```

### Permissions

```python
# Check permission
if frappe.has_permission("Sales Invoice", "write"):
    # Mag schrijven
    pass

# Check voor specifiek document
if frappe.has_permission("Sales Invoice", "write", doc.name):
    pass

# Permission types: read, write, create, delete, submit, cancel, amend
```

---

## API Script Specifiek

Bij API type Server Scripts:

### Request data

```python
# Query parameters en POST data
customer = frappe.form_dict.get("customer")
data = frappe.form_dict.get("data")

# Veilig ophalen
limit = frappe.form_dict.get("limit", 10)  # Met default
```

### Response

```python
# Simpele response
frappe.response["message"] = {"status": "success", "data": result}

# Of direct return (alleen bij API scripts)
# Het return value wordt automatisch frappe.response["message"]
```

### Request context

```python
frappe.request               # Werkzeug request object
frappe.request.method        # "GET", "POST", etc.
frappe.request.headers       # Request headers
```

---

## Python Builtins

### Beschikbaar

```python
# Basis types
str, int, float, bool, list, dict, tuple, set

# Iteratie
range, enumerate, zip, map, filter

# Aggregatie  
sum, min, max, len, sorted, reversed

# Type checks
isinstance, type

# Logic
all, any

# Andere
print  # Gaat naar server log
```

### NIET beschikbaar

```python
# File I/O
open, file

# Code execution
eval, exec, compile

# System access
__import__  # Dus alle imports
globals, locals, vars

# Alle modules (os, sys, subprocess, etc.)
```
