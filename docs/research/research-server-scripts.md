# Research Document: Server Scripts (Fase 1.2)

> **Status**: Geverifieerd en geactualiseerd voor Frappe v14/v15
> **Datum**: Januari 2026
> **Bronnen**: OfficiÃ«le Frappe documentatie, GitHub source code, community bevestigingen

---

## 1. Server Script Types

Frappe biedt **vier** Server Script types die elk een specifiek doel dienen:

| Type | Doel | Configuratie Velden |
|------|------|---------------------|
| **DocType Event** | Reageren op document lifecycle events | Reference DocType, Event Name |
| **API** | REST endpoints maken | API Method, Allow Guest, Enable Rate Limit |
| **Scheduler Event** | Geplande taken uitvoeren | Cron Format (of Event Frequency) |
| **Permission Query** | Dynamische row-level filtering | Reference DocType |

### 1.1 DocType Event Scripts

**Configuratie:**
- Reference DocType: Het DocType waarop het script reageert
- Doctype Event: Het specifieke event (zie Event Mapping hieronder)

**Beschikbare variabelen:**
- `doc` - Het document object (kan gelezen en gewijzigd worden)
- `frappe` - De Frappe API (beperkte sandbox versie)
- `method` - De naam van het event (bijv. "validate")

### 1.2 API Scripts

**Configuratie:**
- API Method: Endpoint naam (bijv. "get-customer-data")
- Allow Guest: Checkbox - indien aangevinkt, geen authenticatie vereist
- Enable Rate Limit: Checkbox - IP-based rate limiting
- Rate Limit Count: Aantal toegestane calls
- Rate Limit Seconds: Tijdvenster in seconden

**Endpoint URL:** `/api/method/{api_method}`

**Response instellen:**
```python
# Via frappe.response
frappe.response['message'] = {"status": "success", "data": result}

# Of direct return (wordt automatisch frappe.response['message'])
# NIET beschikbaar in Server Scripts, alleen in whitelisted methods
```

### 1.3 Scheduler Event Scripts

**Configuratie:**
- Event Frequency: Dropdown met opties OF
- Cron Format: Standaard cron syntax

**Event Frequency opties:**
- All (elke scheduler tick, ~4 minuten)
- Hourly
- Daily
- Weekly
- Monthly
- Yearly
- Cron (custom format)

**Cron syntax voorbeelden:**
```
*/15 * * * *     # Elke 15 minuten
0 9 * * *        # Dagelijks om 9:00
0 9 * * 1-5      # Werkdagen om 9:00
0 0 1 * *        # Eerste dag van de maand om middernacht
```

### 1.4 Permission Query Scripts

**Configuratie:**
- Reference DocType: DocType waarvoor query conditions gelden

**Verwachte output:**
Het script moet de variabele `conditions` zetten met een SQL WHERE clause fragment:
```python
# Voorbeeld: Alleen eigen records tonen
conditions = f"`tab{doctype}`.owner = {frappe.db.escape(user)}"

# Of geen beperking
conditions = ""

# Of niets tonen
conditions = "1=0"
```

**Belangrijk:** Dit beÃ¯nvloedt alleen `frappe.db.get_list`, NIET `frappe.db.get_all`.

---

## 2. Event Mapping (UI â†’ Intern)

Server Scripts tonen gebruiksvriendelijke event namen in de UI, maar deze mappen naar interne hook namen:

| UI Event Naam | Interne Hook | Wanneer Getriggerd |
|---------------|--------------|---------------------|
| Before Insert | `before_insert` | Nieuw document, vÃ³Ã³r database insert |
| After Insert | `after_insert` | Nieuw document, na database insert |
| Before Validate | `before_validate` | VÃ³Ã³r validatie logica draait |
| **Before Save** | `validate` | VÃ³Ã³r opslaan (meest gebruikte voor validatie) |
| After Save | `on_update` | Na succesvol opslaan |
| Before Submit | `before_submit` | VÃ³Ã³r document submission |
| After Submit | `on_submit` | Na document submission |
| Before Cancel | `before_cancel` | VÃ³Ã³r cancellation |
| After Cancel | `on_cancel` | Na cancellation |
| Before Delete | `on_trash` | VÃ³Ã³r document deletion |
| After Delete | `after_delete` | Na document deletion |
| Before Save (Submitted Document) | `before_update_after_submit` | Wijziging na submit, vÃ³Ã³r save |
| After Save (Submitted Document) | `on_update_after_submit` | Wijziging na submit, na save |

**KRITIEKE OPMERKING (v14+):**
- "Before Save" in de UI = `validate` intern
- Dit is de plek voor validatie logica met `frappe.throw()`
- `on_update` (After Save) is NIET geschikt voor validatie - document is al opgeslagen

---

## 3. Sandbox Environment (RestrictedPython)

Frappe gebruikt **RestrictedPython** om Server Scripts in een sandbox uit te voeren. Dit beperkt drastisch welke Python functionaliteit beschikbaar is.

### 3.1 Beschikbare Globals

```python
# Basis Python
json          # json module
dict          # dict builtin
_             # Translator functie (__())
_dict         # frappe._dict internal method

# Flags
frappe.flags  # Global flags object

# Formatting
frappe.format          # frappe.format_value(value, df)
frappe.format_value    # frappe.format_value(value, dict(fieldtype='Currency'))
frappe.date_format     # Default date format string
frappe.format_date     # Returns date as "1st September 2019"

# Session
frappe.form_dict       # Form / request parameters (voor API scripts)
frappe.request         # Request object
frappe.response        # Response object
frappe.session.user    # Current user
frappe.session.csrf_token  # CSRF token
frappe.user            # Current user (alias)
frappe.get_fullname    # Fullname van current user
frappe.get_gravatar    # frappe.utils.get_gravatar_url
frappe.full_name       # Fullname van current user
```

### 3.2 ORM (Document) Methods

```python
# Document ophalen
frappe.get_meta(doctype)              # Metadata object
frappe.new_doc(doctype)               # Nieuw document maken
frappe.get_doc(doctype, name)         # Document ophalen
frappe.get_doc(dict)                  # Document van dict maken
frappe.get_last_doc(doctype, filters) # Laatste document ophalen
frappe.get_cached_doc(doctype, name)  # Gecached document
frappe.get_mapped_doc(...)            # Gemapped document

# Document acties
frappe.rename_doc(doctype, old, new)  # Hernoemen
frappe.delete_doc(doctype, name)      # Verwijderen

# Systeem
frappe.get_system_settings(key)       # System settings waarde
```

### 3.3 Database Methods

```python
# Lezen
frappe.db.get_list(doctype, filters, fields, order_by, ...)
frappe.db.get_all(doctype, filters, fields, ...)  # Zonder permission check
frappe.db.get_value(doctype, filters, fieldname, as_dict=False)
frappe.db.get_single_value(doctype, fieldname)
frappe.db.get_default(key)
frappe.db.exists(doctype, name_or_filters)
frappe.db.count(doctype, filters)

# SQL (gebruik parameterized queries!)
frappe.db.sql(query, values, as_dict=False)

# Schrijven
frappe.db.set_value(doctype, name, fieldname, value)

# Escape
frappe.db.escape(value)  # Voor veilige SQL strings

# Transacties (ALLEEN in Scheduler Events/API, NIET in DocType Events)
frappe.db.commit()       # Explicit commit
frappe.db.rollback()     # Explicit rollback
```

### 3.4 Query Builder (v14+)

```python
# PyPika-based query builder
frappe.qb.from_("Task").select("*").run()

# Complexere query
(frappe.qb
    .from_("Task")
    .select("name", "subject")
    .where(frappe.qb.Field("status") == "Open")
    .run())
```

### 3.5 Utilities

```python
# Messaging
frappe.msgprint(message)              # Toon melding in UI
frappe.throw(message, exc)            # Raise exception met melding
frappe.log_error(message, title)      # Log naar Error Log

# Template rendering
frappe.render_template(template, context)

# URL
frappe.get_url()                      # Site URL
frappe.get_url_to_form(doctype, name) # URL naar form

# Utils module (veelgebruikte utilities)
frappe.utils.now()                    # Current datetime
frappe.utils.today()                  # Current date
frappe.utils.nowdate()                # Current date string
frappe.utils.nowtime()                # Current time string
frappe.utils.cint(value)              # Convert to int
frappe.utils.flt(value, precision)    # Convert to float
frappe.utils.cstr(value)              # Convert to string
frappe.utils.getdate(date)            # Parse to date
frappe.utils.get_datetime(datetime)   # Parse to datetime
frappe.utils.date_diff(date1, date2)  # Days difference
frappe.utils.add_days(date, days)     # Add days
frappe.utils.add_months(date, months) # Add months

# API calls
frappe.make_get_request(url)          # External GET request
frappe.make_post_request(url, data)   # External POST request
frappe.make_put_request(url, headers) # External PUT request

# Email
frappe.sendmail(recipients, sender, subject, message, ...)

# Hooks
frappe.get_hooks(hook_name)           # Get hook values
```

### 3.6 Cache Methods

```python
frappe.cache().set_value(key, value)      # Set cache value
frappe.cache().get_value(key)              # Get cache value
frappe.cache().hset(name, key, value)      # Hash set
frappe.cache().hget(name, key)             # Hash get
```

### 3.7 Extra beschikbaar

```python
# Andere beschikbare items
run_script        # Run another script (v15+)
socketio_port     # Socket.io port number
style.border_color # Style helpers
guess_mimetype    # Mimetype guesser
html2text         # HTML to text converter
dev_server        # Boolean: is dev server
FrappeClient      # Client voor remote Frappe instances
```

---

## 4. NIET Beschikbaar in Sandbox

**De volgende Python features zijn NIET beschikbaar:**

### 4.1 Geblokkeerde Builtins
- `compile` - Geen code compilatie
- `dir` - Geen introspection
- `eval` / `exec` - Geen dynamic code execution
- `execfile` - Geen file execution
- `file` / `open` - Geen direct I/O
- `globals` / `locals` / `vars` - Geen namespace access
- `input` / `raw_input` - Geen user input
- `__import__` - Geen dynamic imports

### 4.2 Geblokkeerde Modules
- `os` - Geen OS toegang
- `sys` - Geen systeem toegang
- `subprocess` - Geen shell commands
- `socket` - Geen netwerk (behalve via frappe.make_*_request)
- `multiprocessing` / `threading` - Geen parallellisme

### 4.3 Geblokkeerde Attributen
- Underscore prefixed attributes (`_*`)
- `__class__`, `__bases__`, `__dict__`, etc.
- Generator frame access (`gi_frame`) - geblokkeerd sinds v14.40+

---

## 5. doc Object Properties en Methods

In DocType Event scripts is het `doc` object beschikbaar:

### 5.1 Standaard Properties

```python
# Identificatie
doc.name              # Document naam/ID
doc.doctype           # DocType naam
doc.docstatus         # 0=Draft, 1=Submitted, 2=Cancelled

# Metadata
doc.owner             # Aanmaker
doc.creation          # Aanmaakdatum
doc.modified          # Laatste wijziging
doc.modified_by       # Laatste wijziger

# Alle velden van het DocType zijn direct beschikbaar
doc.customer          # Voorbeeld: Customer veld
doc.grand_total       # Voorbeeld: Grand Total veld
doc.items             # Voorbeeld: Child table
```

### 5.2 Beschikbare Methods

```python
# Basis operaties
doc.get(fieldname, default=None)      # Get field value
doc.set(fieldname, value)             # Set field value (alternatief voor direct assignment)
doc.update(dict)                      # Update meerdere velden
doc.as_dict()                         # Convert naar dict
doc.as_json()                         # Convert naar JSON string

# Child tables
doc.append(tablename, dict)           # Voeg rij toe aan child table
doc.get(tablename)                    # Get child table als list

# Veld checks
doc.get_valid_dict()                  # Dict met alleen geldige velden
doc.is_new()                          # Boolean: is nieuw document?
doc.has_value_changed(fieldname)      # Boolean: is veld gewijzigd?
doc.get_doc_before_save()             # Vorige versie (voor vergelijking)

# Database operaties (beschikbaar op doc)
doc.insert()                          # Insert nieuw document
doc.save()                            # Save document
doc.submit()                          # Submit document
doc.cancel()                          # Cancel document
doc.delete()                          # Delete document
doc.reload()                          # Reload from database

# Permissions
doc.has_permission(ptype)             # Check permission
```

### 5.3 Flags

```python
# Built-in flags (voorzichtig gebruiken!)
doc.flags.ignore_permissions = True   # Bypass permission checks
doc.flags.ignore_validate = True      # Skip validation
doc.flags.ignore_mandatory = True     # Skip required field checks
doc.flags.ignore_links = True         # Skip link validation

# Custom flags (voor inter-event communicatie)
doc.flags.my_custom_flag = True       # Eigen flag zetten
if doc.flags.get('my_custom_flag'):   # Eigen flag lezen
    pass
```

---

## 6. Beperkingen: Server Scripts vs Controllers

| Aspect | Server Script | Document Controller |
|--------|--------------|---------------------|
| Locatie | UI (Setup â†’ Server Script) | Python file in app |
| Python access | Sandbox (RestrictedPython) | Volledige Python |
| Imports | Niet mogelijk | Onbeperkt |
| Custom classes | Niet mogelijk | Wel mogelijk |
| db.commit/rollback | Alleen in Scheduler/API | Wel (maar niet in hooks) |
| Performance | Iets trager (sandbox overhead) | Sneller |
| Debugging | Beperkt (frappe.log_error) | Volledig |
| Version control | Niet native | Git integratie |
| Multiple scripts | Meerdere per event mogelijk | EÃ©n controller per DocType |

### 6.1 Wanneer Server Script gebruiken?

âœ… **Gebruik Server Scripts voor:**
- Snelle validaties en auto-calculations
- Simpele API endpoints
- Permission filtering
- Scheduled tasks (eenvoudig)
- Prototyping voordat je naar controller migreert

âŒ **Gebruik GEEN Server Scripts voor:**
- Complexe business logic
- Wanneer je externe Python packages nodig hebt
- Performance-kritieke operaties
- Code die version control vereist
- Wanneer je unit tests wilt schrijven

---

## 7. Best Practices

### 7.1 Error Handling

```python
# GOED: Gebruik frappe.throw voor user-facing errors
if doc.amount < 0:
    frappe.throw("Amount cannot be negative")

# GOED: Log errors voor debugging
try:
    external_call()
except Exception as e:
    frappe.log_error(f"External call failed: {str(e)}", "API Error")
    frappe.throw("External service unavailable")

# SLECHT: Bare except zonder logging
try:
    risky_operation()
except:
    pass  # Never do this!
```

### 7.2 Database Queries

```python
# GOED: Parameterized queries
results = frappe.db.sql("""
    SELECT name FROM `tabCustomer` 
    WHERE territory = %(territory)s
""", {"territory": territory}, as_dict=True)

# SLECHT: String formatting (SQL injection risk!)
results = frappe.db.sql(f"""
    SELECT name FROM `tabCustomer` 
    WHERE territory = '{territory}'
""")

# GOED: Gebruik ORM waar mogelijk
customers = frappe.db.get_all("Customer", 
    filters={"territory": territory},
    fields=["name", "customer_name"])
```

### 7.3 Performance

```python
# GOED: Batch fetching
names = [item.customer for item in doc.items]
customers = frappe.db.get_all("Customer",
    filters={"name": ["in", names]},
    fields=["name", "credit_limit"])
customer_map = {c.name: c for c in customers}

# SLECHT: N+1 queries
for item in doc.items:
    customer = frappe.get_doc("Customer", item.customer)  # Query per item!
```

### 7.4 Commits in Server Scripts

```python
# NOOIT commit in DocType Event scripts - framework handelt dit af

# ALLEEN in Scheduler Event / API scripts:
for record in large_batch:
    process(record)
    frappe.db.commit()  # Commit per batch om memory te besparen
```

---

## 8. Volledige Voorbeelden

### 8.1 Before Save (Validatie)

```python
# Script Type: DocType Event
# Reference DocType: Sales Invoice
# Doctype Event: Before Save

# Valideer totaal
if doc.grand_total < 0:
    frappe.throw("Grand total cannot be negative")

# Auto-set veld
if doc.grand_total > 10000:
    doc.requires_approval = 1

# Fetch gerelateerde data
if doc.customer and not doc.customer_name:
    doc.customer_name = frappe.db.get_value("Customer", doc.customer, "customer_name")
```

### 8.2 After Submit (Follow-up acties)

```python
# Script Type: DocType Event
# Reference DocType: Sales Order
# Doctype Event: After Submit

# Maak ToDo voor high-value orders
if doc.grand_total > 5000:
    frappe.get_doc({
        'doctype': 'ToDo',
        'allocated_to': doc.owner,
        'reference_type': doc.doctype,
        'reference_name': doc.name,
        'description': f'Follow up on high-value order {doc.name}'
    }).insert(ignore_permissions=True)
```

### 8.3 API Endpoint

```python
# Script Type: API
# API Method: get_customer_orders
# Allow Guest: No

customer = frappe.form_dict.get("customer")

if not customer:
    frappe.throw("Customer parameter required")

# Permission check
if not frappe.has_permission("Sales Order", "read"):
    frappe.throw("Permission denied", frappe.PermissionError)

orders = frappe.db.get_all(
    "Sales Order",
    filters={"customer": customer, "docstatus": 1},
    fields=["name", "grand_total", "transaction_date", "status"],
    order_by="transaction_date desc",
    limit=20
)

frappe.response['orders'] = orders
frappe.response['count'] = len(orders)
```

### 8.4 Scheduler Event

```python
# Script Type: Scheduler Event
# Cron Format: 0 9 * * * (dagelijks om 9:00)

# Vind overdue invoices
pending = frappe.db.get_all(
    "Sales Invoice",
    filters={
        "status": "Unpaid", 
        "due_date": ["<", frappe.utils.today()]
    },
    fields=["name", "customer", "grand_total", "contact_email"]
)

for inv in pending:
    if inv.contact_email:
        frappe.sendmail(
            recipients=[inv.contact_email],
            subject=f"Payment Reminder: {inv.name}",
            message=f"Invoice {inv.name} for {inv.grand_total} is overdue."
        )

# Commit is nodig in scheduler scripts
frappe.db.commit()
```

### 8.5 Permission Query

```python
# Script Type: Permission Query
# Reference DocType: Sales Invoice

user = frappe.session.user
user_roles = frappe.get_roles(user)

if "Sales Manager" in user_roles:
    conditions = ""  # Geen restricties voor managers
elif "Sales User" in user_roles:
    # Alleen eigen facturen + facturen van eigen klanten
    conditions = f"""
        `tabSales Invoice`.owner = {frappe.db.escape(user)}
        OR `tabSales Invoice`.customer IN (
            SELECT name FROM `tabCustomer` WHERE account_manager = {frappe.db.escape(user)}
        )
    """
else:
    conditions = "1=0"  # Niets tonen voor andere rollen
```

---

## 9. Bronvermelding

| Bron | URL | Versie |
|------|-----|--------|
| Frappe Server Script Docs | docs.frappe.io/framework/v15/user/en/desk/scripting/server-script | v15 |
| Frappe Script API | docs.frappe.io/framework/v15/user/en/desk/scripting/script-api | v15 |
| Database API | docs.frappe.io/framework/v15/user/en/api/database | v15 |
| Frappe GitHub (safe_exec.py) | github.com/frappe/frappe/blob/develop/frappe/utils/safe_exec.py | develop |
| RestrictedPython | restrictedpython.readthedocs.io | 8.x |

---

## 10. Verificatie Status

| Item | Status | Bron |
|------|--------|------|
| Script Types (4) | âœ… Geverifieerd | OfficiÃ«le docs + source |
| Event Mapping | âœ… Geverifieerd | Community + source |
| Sandbox Methods | âœ… Geverifieerd | Script API docs + safe_exec.py |
| Geblokkeerde functies | âœ… Geverifieerd | RestrictedPython + safe_exec.py |
| doc Object | âœ… Geverifieerd | OfficiÃ«le docs + community |
| Beperkingen vs Controllers | âœ… Geverifieerd | OfficiÃ«le docs + community |
