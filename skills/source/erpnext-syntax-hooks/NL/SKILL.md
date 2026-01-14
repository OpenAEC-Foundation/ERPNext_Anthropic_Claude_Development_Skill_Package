---
name: erpnext-syntax-hooks
description: >
  Deterministische syntax voor alle Frappe hooks.py configuratie. Event hooks (doc_events, scheduler_events, 
  extend_bootinfo), override hooks (override_doctype_class, override_whitelisted_methods), permission hooks 
  (permission_query_conditions, has_permission), fixtures, en asset includes. Triggers: hooks.py, doc_events, 
  scheduler_events, cron job, override controller, permission hook, fixtures, app_include_js, doctype_js.
---

# ERPNext Syntax: Event Hooks (hooks.py)

Event Hooks in hooks.py stellen custom apps in staat om te reageren op systeem- en document-events.

## Quick Reference

### doc_events - Document Lifecycle

```python
# In hooks.py
doc_events = {
    "*": {
        "after_insert": "myapp.events.log_all_inserts"
    },
    "Sales Invoice": {
        "validate": "myapp.events.si_validate",
        "on_submit": "myapp.events.si_on_submit"
    }
}
```

```python
# In myapp/events.py
import frappe

def si_validate(doc, method=None):
    """doc = document object, method = event naam"""
    if doc.grand_total < 0:
        frappe.throw("Total cannot be negative")
```

### scheduler_events - Periodieke Taken

```python
# In hooks.py
scheduler_events = {
    "daily": ["myapp.tasks.daily_cleanup"],
    "hourly_long": ["myapp.tasks.heavy_sync"],
    "cron": {
        "0 9 * * 1-5": ["myapp.tasks.weekday_morning"]
    }
}
```

```python
# In myapp/tasks.py
def daily_cleanup():
    """Geen argumenten - wordt automatisch aangeroepen"""
    frappe.db.delete("Log", {"creation": ["<", one_month_ago()]})
```

### extend_bootinfo - Client Data Injectie

```python
# In hooks.py
extend_bootinfo = "myapp.boot.extend_boot"
```

```python
# In myapp/boot.py
def extend_boot(bootinfo):
    """bootinfo = dict die naar frappe.boot gaat"""
    bootinfo.my_setting = frappe.get_single("My Settings").value
```

```javascript
// Client-side
console.log(frappe.boot.my_setting);
```

---

## Meest Gebruikte doc_events

| Event | Wanneer | Gebruik |
|-------|---------|---------|
| `validate` | Voor elke save | Validatie, berekeningen |
| `on_update` | Na elke save | Notifications, sync |
| `after_insert` | Na nieuw doc | Alleen-bij-creatie acties |
| `on_submit` | Na submit | Ledger entries |
| `on_cancel` | Na cancel | Reverse entries |
| `on_trash` | Voor delete | Cleanup |

**Complete lijst**: Zie [doc-events.md](references/doc-events.md)

---

## Scheduler Event Types

| Event | Frequentie | Queue/Timeout |
|-------|------------|---------------|
| `hourly` | Elk uur | default / 5 min |
| `daily` | Elke dag | default / 5 min |
| `weekly` | Elke week | default / 5 min |
| `monthly` | Elke maand | default / 5 min |
| `hourly_long` | Elk uur | long / 25 min |
| `daily_long` | Elke dag | long / 25 min |
| `cron` | Custom timing | default / 5 min |

**Cron syntax en voorbeelden**: Zie [scheduler-events.md](references/scheduler-events.md)

---

## Kritieke Regels

### 1. bench migrate na scheduler wijzigingen

```bash
# VERPLICHT - anders worden wijzigingen niet opgepikt
bench --site sitename migrate
```

### 2. Geen commits in doc_events

```python
# ❌ FOUT
def on_update(doc, method=None):
    frappe.db.commit()  # Breekt transactie

# ✅ GOED - Frappe commit automatisch
def on_update(doc, method=None):
    update_related_docs(doc)
```

### 3. Wijzigingen na on_update via db_set

```python
# ❌ FOUT - wijziging verdwijnt
def on_update(doc, method=None):
    doc.status = "Processed"

# ✅ GOED
def on_update(doc, method=None):
    frappe.db.set_value(doc.doctype, doc.name, "status", "Processed")
```

### 4. Zware taken naar _long queue

```python
# ❌ FOUT - timeout na 5 min
scheduler_events = {
    "daily": ["myapp.tasks.process_all_records"]  # Kan 20 min duren
}

# ✅ GOED - 25 min timeout
scheduler_events = {
    "daily_long": ["myapp.tasks.process_all_records"]
}
```

### 5. Tasks krijgen geen argumenten

```python
# ❌ FOUT
def my_task(some_arg):
    pass

# ✅ GOED
def my_task():
    # Haal data op binnen de functie
    pass
```

---

## Cron Syntax Cheatsheet

```
* * * * *
│ │ │ │ │
│ │ │ │ └── Dag van week (0-6, zo=0)
│ │ │ └──── Maand (1-12)
│ │ └────── Dag van maand (1-31)
│ └──────── Uur (0-23)
└────────── Minuut (0-59)
```

| Pattern | Betekenis |
|---------|-----------|
| `*/5 * * * *` | Elke 5 minuten |
| `0 9 * * *` | Dagelijks 09:00 |
| `0 9 * * 1-5` | Werkdagen 09:00 |
| `0 0 1 * *` | Eerste dag v/d maand |
| `0 17 * * 5` | Vrijdag 17:00 |

---

## Decision Tree: Welke Hook?

```
Waar moet de code draaien?
│
├─► In een CUSTOM APP die ANDERE doctypes hooked?
│   └─► doc_events in hooks.py
│       │
│       ├─► Voor save validatie? → validate
│       ├─► Na save actie? → on_update
│       ├─► Alleen nieuwe docs? → after_insert
│       ├─► Bij submit? → on_submit
│       └─► Bij delete? → on_trash
│
├─► Als PERIODIEKE TAAK?
│   └─► scheduler_events in hooks.py
│       │
│       ├─► Standaard interval? → hourly/daily/weekly/monthly
│       ├─► Zware taak (>5 min)? → hourly_long/daily_long
│       └─► Specifieke tijd? → cron
│
└─► DATA naar CLIENT sturen bij page load?
    └─► extend_bootinfo
```

---

## doc_events vs Controller Hooks

| Aspect | doc_events (hooks.py) | Controller Methods |
|--------|----------------------|-------------------|
| Locatie | `hooks.py` | `doctype/xxx/xxx.py` |
| Scope | Hook op ANDERE doctypes | Alleen EIGEN doctype |
| Meerdere handlers | ✅ Ja (lijst) | ❌ Nee |
| Prioriteit | Na controller | Eerst |
| Wildcard (`*`) | ✅ Ja | ❌ Nee |

**Gebruik doc_events wanneer**:
- Je vanuit een custom app andermans DocTypes wilt hooken
- Je op ALLE DocTypes wilt reageren (wildcard)
- Je meerdere handlers wilt registreren

**Gebruik controller methods wanneer**:
- Je aan je eigen DocType werkt
- Je volledige controle wilt over de lifecycle

**Voorbeelden**: Zie [examples.md](references/examples.md) voor complete werkende voorbeelden.

---

## Reference Bestanden

| Bestand | Inhoud |
|---------|--------|
| [doc-events.md](references/doc-events.md) | Alle document events, signatures, execution order |
| [scheduler-events.md](references/scheduler-events.md) | Scheduler types, cron syntax, timeouts |
| [bootinfo.md](references/bootinfo.md) | extend_bootinfo, session hooks |
| [overrides.md](references/overrides.md) | Override en extend patterns |
| [permissions.md](references/permissions.md) | Permission hooks |
| [fixtures.md](references/fixtures.md) | Fixtures configuratie |
| [examples.md](references/examples.md) | Complete hooks.py voorbeelden |
| [anti-patterns.md](references/anti-patterns.md) | Fouten en correcties |

---

## Configuration Hooks

### Override DocType Controller

```python
# In hooks.py
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice"
}
```

```python
# In myapp/overrides.py
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # KRITIEK: altijd super() aanroepen!
        self.custom_validation()
```

**Waarschuwing**: Laatste geïnstalleerde app wint bij meerdere overrides.

### Override Whitelisted Methods

```python
# In hooks.py
override_whitelisted_methods = {
    "frappe.client.get_count": "myapp.overrides.custom_get_count"
}
```

```python
# Method signature MOET identiek zijn aan origineel!
def custom_get_count(doctype, filters=None, debug=False, cache=False):
    # Custom implementatie
    return frappe.db.count(doctype, filters)
```

### Permission Hooks

```python
# In hooks.py
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_query_conditions"
}
has_permission = {
    "Sales Invoice": "myapp.permissions.si_has_permission"
}
```

```python
# In myapp/permissions.py
def si_query_conditions(user):
    """Retourneert SQL WHERE fragment voor list filtering"""
    if not user:
        user = frappe.session.user
    
    if "Sales Manager" in frappe.get_roles(user):
        return ""  # Geen restricties
    
    return f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"

def si_has_permission(doc, user=None, permission_type=None):
    """Document-level permission check"""
    if permission_type == "write" and doc.status == "Closed":
        return False
    return None  # Fallback naar default
```

**Let op**: `permission_query_conditions` werkt alleen met `get_list`, NIET met `get_all`!

### Fixtures

```python
# In hooks.py
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "My App"]]},
    {"dt": "Role", "filters": [["name", "like", "MyApp%"]]}
]
```

```bash
# Exporteer fixtures naar JSON
bench --site sitename export-fixtures
```

### Asset Includes

```python
# In hooks.py

# Desk (backend) assets
app_include_js = "/assets/myapp/js/myapp.min.js"
app_include_css = "/assets/myapp/css/myapp.min.css"

# Website/Portal assets
web_include_js = "/assets/myapp/js/web.min.js"
web_include_css = "/assets/myapp/css/web.min.css"

# Form script extensions
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js"
}
```

### Install/Migrate Hooks

```python
# In hooks.py
after_install = "myapp.setup.after_install"
after_migrate = "myapp.setup.after_migrate"
```

```python
# In myapp/setup.py
def after_install():
    create_default_roles()
    
def after_migrate():
    clear_custom_cache()
```

---

## Complete Decision Tree

```
Wat wil je bereiken?
│
├─► REAGEREN op document events van ANDERE apps?
│   └─► doc_events
│
├─► PERIODIEKE taken uitvoeren?
│   └─► scheduler_events
│       ├─► < 5 min → hourly/daily/weekly/monthly
│       ├─► > 5 min → hourly_long/daily_long/etc.
│       └─► Specifieke tijd → cron
│
├─► DATA naar CLIENT sturen bij page load?
│   └─► extend_bootinfo
│
├─► CONTROLLER van bestaand DocType aanpassen?
│   ├─► Frappe v16+ → extend_doctype_class (aanbevolen)
│   └─► Frappe v14/v15 → override_doctype_class
│
├─► API ENDPOINT aanpassen?
│   └─► override_whitelisted_methods
│
├─► PERMISSIONS customizen?
│   ├─► List filtering → permission_query_conditions
│   └─► Document-level → has_permission
│
├─► CONFIGURATIE exporteren/importeren?
│   └─► fixtures
│
├─► JS/CSS TOEVOEGEN aan desk of portal?
│   ├─► Desk → app_include_js/css
│   ├─► Portal → web_include_js/css
│   └─► Form specifiek → doctype_js
│
└─► SETUP bij install/migrate?
    └─► after_install, after_migrate
```

---

## Versie Verschillen

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| doc_events | ✅ | ✅ | ✅ |
| scheduler_events | ✅ | ✅ | ✅ |
| extend_bootinfo | ✅ | ✅ | ✅ |
| override_doctype_class | ✅ | ✅ | ✅ |
| extend_doctype_class | ❌ | ❌ | ✅ |
| permission_query_conditions | ✅ | ✅ | ✅ |
| has_permission | ✅ | ✅ | ✅ |
| fixtures | ✅ | ✅ | ✅ |

---

## Anti-Patterns Samenvatting

| ❌ Fout | ✅ Correct |
|---------|-----------|
| `frappe.db.commit()` in handler | Frappe commit automatisch |
| `doc.field = x` in on_update | `frappe.db.set_value()` |
| Zware taak in `daily` | Gebruik `daily_long` |
| Scheduler wijzigen zonder migrate | Altijd `bench migrate` |
| Gevoelige data in bootinfo | Alleen publieke config |
| Override zonder `super()` | Altijd `super().method()` eerst |
| `get_all` met permission_query | Gebruik `get_list` |
| Fixtures zonder filters | Filter op module/app |

**Volledige anti-patterns**: Zie [anti-patterns.md](references/anti-patterns.md)
