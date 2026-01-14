# Server Script Anti-Patterns en Beperkingen

## Inhoudsopgave

1. [Sandbox Beperkingen](#sandbox-beperkingen)
2. [Import Errors](#import-errors)
3. [Database Anti-Patterns](#database-anti-patterns)
4. [Performance Anti-Patterns](#performance-anti-patterns)
5. [Security Anti-Patterns](#security-anti-patterns)
6. [Logic Anti-Patterns](#logic-anti-patterns)
7. [Veelgemaakte Fouten](#veelgemaakte-fouten)

---

## Sandbox Beperkingen

### ❌ GEEN Imports Toegestaan

De Server Script sandbox blokkeert de Python `__import__` functie volledig.

```python
# ❌ FOUT - Elke import geeft error:
import json                           # ImportError: __import__ not found
from datetime import datetime         # ImportError: __import__ not found
import frappe                         # ImportError (zelfs frappe!)
from frappe.utils import nowdate      # ImportError

# ✅ CORRECT - Gebruik pre-loaded namespace:
data = frappe.parse_json(json_string)    # In plaats van json.loads()
today = frappe.utils.nowdate()           # Direct beschikbaar
now = frappe.utils.now_datetime()        # In plaats van datetime.now()
```

### ❌ GEEN File System Access

```python
# ❌ FOUT:
open("/tmp/data.txt", "r")            # NameError: name 'open' is not defined
file = open("export.csv", "w")        # Niet beschikbaar

# ✅ ALTERNATIEF - Gebruik Frappe's file handling:
# Maak File doc voor attachments, of log naar Error Log
frappe.log_error(data, "Export Data")
```

### ❌ GEEN OS/System Commands

```python
# ❌ FOUT:
import os                              # ImportError
os.system("ls")                        # Niet beschikbaar
subprocess.run(["echo", "hi"])         # Niet beschikbaar

# ✅ ALTERNATIEF:
# Gebruik whitelisted methods in een custom app voor systeem operaties
```

### ❌ GEEN Code Execution

```python
# ❌ FOUT - Geblokkeerd voor veiligheid:
eval("1 + 1")                          # Geblokkeerd
exec("print('hello')")                 # Geblokkeerd
compile("code", "", "exec")            # Geblokkeerd

# ✅ ALTERNATIEF:
# Schrijf de logica direct uit, geen dynamic code execution
```

### ❌ GEEN External HTTP Requests

```python
# ❌ FOUT:
import requests                        # ImportError
requests.get("https://api.example.com")  # Niet beschikbaar

# ✅ ALTERNATIEF:
# Gebruik background jobs in custom app met frappe.enqueue
# Of Server Script type API om endpoints te exposen
```

---

## Import Errors

### De meest verwarrende error

```
ImportError: __import__ not found
```

**Oorzaak**: ELKE import statement in Server Scripts

**Fout voorbeelden**:
```python
# ❌ Al deze geven ImportError:
import json
import re
import math
from datetime import date, timedelta
from collections import defaultdict
import frappe  # Ja, zelfs dit!
from frappe.utils import cint
```

**Oplossingen**:

| In plaats van | Gebruik |
|---------------|---------|
| `import json` | `frappe.parse_json()`, `frappe.as_json()` |
| `from datetime import date` | `frappe.utils.today()`, `frappe.utils.now_datetime()` |
| `import math` | Python builtins: `sum()`, `min()`, `max()`, `round()` |
| `from collections import defaultdict` | Gewone `dict` met `.get(key, default)` |
| `import re` | Niet beschikbaar - herstructureer logica |
| `from frappe.utils import cint` | `frappe.utils.cint()` (namespace al geladen) |

---

## Database Anti-Patterns

### ❌ SQL Injection Kwetsbaarheid

```python
# ❌ GEVAARLIJK - Nooit doen:
frappe.db.sql(f"SELECT * FROM tabUser WHERE name = '{user_input}'")
frappe.db.sql("SELECT * FROM tabUser WHERE name = '" + user_input + "'")

# ✅ VEILIG - Altijd parameterized queries:
frappe.db.sql("""
    SELECT * FROM `tabUser` 
    WHERE name = %(user)s
""", {"user": user_input}, as_dict=True)

# ✅ OF gebruik get_all/get_value (automatisch veilig):
frappe.get_all("User", filters={"name": user_input})
```

### ❌ N+1 Query Probleem

```python
# ❌ FOUT - Query in loop:
for item in doc.items:
    item_name = frappe.db.get_value("Item", item.item_code, "item_name")
    # Dit doet N queries voor N items!

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

### ❌ Onnodig Commit in Document Events

```python
# ❌ FOUT in Document Event scripts:
doc.total = 100
frappe.db.commit()  # Niet nodig, framework doet dit!

# ✅ CORRECT:
doc.total = 100  # Framework handelt commit af

# ⚠️ UITZONDERING - In Scheduler scripts IS commit nodig:
for record in records:
    frappe.db.set_value("Sales Order", record.name, "status", "Processed")
frappe.db.commit()  # Verplicht in scheduler
```

### ❌ set_value voor Complexe Updates

```python
# ❌ RISICOVOL - Bypass alle validatie:
frappe.db.set_value("Sales Invoice", "SINV-001", "grand_total", 1000)
# Dit skip validate, permissions, en linked doc updates!

# ✅ BETER - Volledige document flow:
inv = frappe.get_doc("Sales Invoice", "SINV-001")
inv.grand_total = 1000
inv.save()  # Triggert validate, permissions check, etc.
```

---

## Performance Anti-Patterns

### ❌ Hele Documenten Ophalen voor Één Veld

```python
# ❌ INEFFICIËNT:
customer = frappe.get_doc("Customer", doc.customer)
email = customer.email_id  # Haalt ALLE velden op

# ✅ EFFICIËNT:
email = frappe.db.get_value("Customer", doc.customer, "email_id")
```

### ❌ SELECT * in Queries

```python
# ❌ INEFFICIËNT:
orders = frappe.get_all("Sales Order", filters={...}, fields=["*"])

# ✅ EFFICIËNT - Alleen benodigde velden:
orders = frappe.get_all("Sales Order", 
    filters={...}, 
    fields=["name", "grand_total", "status"])
```

### ❌ Geen Limits op Queries

```python
# ❌ GEVAARLIJK - Kan duizenden records returnen:
all_invoices = frappe.get_all("Sales Invoice", filters={"docstatus": 1})

# ✅ VEILIG - Altijd limit:
recent_invoices = frappe.get_all("Sales Invoice",
    filters={"docstatus": 1},
    limit=100,
    order_by="creation desc")
```

### ❌ Zware Berekeningen in Before Save

```python
# ❌ PROBLEMATISCH - Vertraagt elke save:
def before_save():
    # Zware aggregatie over duizenden records
    total = frappe.db.sql("""
        SELECT SUM(grand_total) FROM `tabSales Invoice`
        WHERE customer = %(customer)s
    """, {"customer": doc.customer})[0][0]
    doc.lifetime_value = total

# ✅ BETER - Doe zware berekeningen in background:
# Gebruik Scheduler Event of background job
```

---

## Security Anti-Patterns

### ❌ Permission Checks Overslaan

```python
# ❌ GEVAARLIJK - Geen permission check:
def api_get_customer(customer):
    return frappe.get_doc("Customer", customer).as_dict()
    # Elke user kan elke customer opvragen!

# ✅ VEILIG:
def api_get_customer(customer):
    if not frappe.has_permission("Customer", "read", customer):
        frappe.throw("Geen toegang", frappe.PermissionError)
    return frappe.get_doc("Customer", customer).as_dict()
```

### ❌ ignore_permissions Overal

```python
# ❌ GEVAARLIJK - Vermijd waar mogelijk:
doc.insert(ignore_permissions=True)
doc.save(ignore_permissions=True)
frappe.get_doc("Sensitive Doc", name).delete(ignore_permissions=True)

# ✅ CORRECT - Alleen met expliciete reden:
# Alleen gebruiken voor:
# - System-generated records (logs, audit trails)
# - Background jobs die namens system draaien
# - Na expliciete permission check op parent

# Voorbeeld legitiem gebruik:
if frappe.has_permission("Sales Order", "write", parent_doc.name):
    # ToDo mag aangemaakt worden als user write heeft op parent
    todo = frappe.get_doc({...})
    todo.insert(ignore_permissions=True)
```

### ❌ Sensitive Data in Logs

```python
# ❌ FOUT:
frappe.log_error(f"Login attempt: user={user}, password={password}")

# ✅ CORRECT:
frappe.log_error(f"Failed login attempt for user: {user}")
```

---

## Logic Anti-Patterns

### ❌ Oneindige Loops door Recursieve Save

```python
# ❌ FOUT - Infinite loop:
# In Before Save:
doc.total = calculate_total(doc)
doc.save()  # Triggert Before Save opnieuw!

# ✅ CORRECT - Wijzig doc, niet save:
# In Before Save:
doc.total = calculate_total(doc)
# GEEN save() aanroepen - framework doet dit
```

### ❌ Throw na Database Wijzigingen

```python
# ❌ PROBLEMATISCH:
def before_save():
    # Maak eerst iets aan...
    frappe.get_doc({"doctype": "Log", ...}).insert()
    
    # Dan valideer...
    if doc.total < 0:
        frappe.throw("Ongeldige total")
    # De Log is al aangemaakt, ook al faalt de save!

# ✅ CORRECT - Valideer VOOR side effects:
def before_save():
    # Eerst alle validaties
    if doc.total < 0:
        frappe.throw("Ongeldige total")
    
    # Dan pas side effects
    frappe.get_doc({"doctype": "Log", ...}).insert()
```

### ❌ Vertrouwen op Event Volgorde

```python
# ❌ FRAGIEL:
# Script 1 (Before Save): doc.calculated_value = complex_calc()
# Script 2 (Before Save): doc.derived = doc.calculated_value * 2
# Volgorde van Server Scripts is NIET gegarandeerd!

# ✅ ROBUUST - Zelfstandige scripts:
# Elk script moet onafhankelijk werken
# Of combineer logica in één script
```

---

## Veelgemaakte Fouten

### Fout 1: Vergeten dat Before Save = validate

```python
# ❌ VERWARRING:
# Developer denkt: "Before Save draait voor validate"
# Maar: Before Save IS validate!

# Als je code nodig hebt VOOR validate:
# Gebruik "Before Validate" in Server Script UI
```

### Fout 2: doc.name gebruiken in Before Insert

```python
# ❌ FOUT in Before Insert:
frappe.msgprint(f"Creating {doc.name}")  
# doc.name is mogelijk nog niet gezet!

# ✅ CORRECT:
frappe.msgprint(f"Creating new {doc.doctype}")
# Of wacht op After Insert voor doc.name
```

### Fout 3: Verwachten dat wijzigingen in After Save automatisch opslaan

```python
# ❌ FOUT in After Save:
doc.note = "Updated after save"
# Dit wordt NIET opgeslagen!

# ✅ CORRECT:
doc.db_set("note", "Updated after save", update_modified=False)
# Of:
frappe.db.set_value(doc.doctype, doc.name, "note", "Updated")
```

### Fout 4: Permission Query die te veel filtert

```python
# ❌ FOUT - Filtert ook voor System Manager:
conditions = f"owner = {frappe.db.escape(user)}"

# ✅ CORRECT - Check rollen eerst:
if "System Manager" in frappe.get_roles(user):
    conditions = ""
else:
    conditions = f"owner = {frappe.db.escape(user)}"
```

### Fout 5: API zonder input validatie

```python
# ❌ FOUT:
customer = frappe.form_dict.customer  # KeyError als niet meegegeven
data = frappe.get_doc("Customer", customer)  # Crash bij None

# ✅ CORRECT:
customer = frappe.form_dict.get("customer")
if not customer:
    frappe.throw("Parameter 'customer' is verplicht")
if not frappe.db.exists("Customer", customer):
    frappe.throw("Customer niet gevonden")
```

### Fout 6: Scheduler zonder commit

```python
# ❌ FOUT in Scheduler Event:
for inv in invoices:
    frappe.db.set_value("Sales Invoice", inv.name, "reminder_sent", 1)
# Wijzigingen zijn NIET gecommit!

# ✅ CORRECT:
for inv in invoices:
    frappe.db.set_value("Sales Invoice", inv.name, "reminder_sent", 1)
frappe.db.commit()  # Verplicht in scheduler scripts
```

---

## Quick Reference: Do's and Don'ts

| Don't ❌ | Do ✅ |
|----------|-------|
| `import json` | `frappe.parse_json()` |
| `from datetime import date` | `frappe.utils.today()` |
| `f"WHERE x = '{var}'"` | `"WHERE x = %(var)s", {"var": var}` |
| `doc.save()` in Before Save | Direct `doc.field = value` |
| `frappe.db.commit()` in Before Save | (framework doet commit) |
| Geen limit op get_all | `limit=100` |
| `fields=["*"]` | `fields=["name", "status"]` |
| `ignore_permissions=True` overal | Expliciet permission checken |
| `doc.name` in Before Insert | Wacht op After Insert |
