# Research Document: hooks.py Configuratie (Fase 2.2)

> **Doel**: VerifiÃ«ren, verdiepen en actualiseren van informatie uit erpnext-vooronderzoek.md sectie 4 (hooks.py Configuratie) voor Frappe v14/v15.

---

## Bronnen Geraadpleegd

| Bron | URL/Locatie | Type |
|------|-------------|------|
| Frappe Docs - Hooks | docs.frappe.io/framework/user/en/python-api/hooks | Primair |
| Frappe Docs - Jinja API | docs.frappe.io/framework/user/en/api/jinja | Primair |
| Frappe Docs - Background Jobs | docs.frappe.io/framework/user/en/api/background_jobs | Primair |
| erpnext-vooronderzoek.md | Project bestand | Basis |

---

## 1. DOC_EVENTS: Syntax en Alle Beschikbare Events

### Basis Syntax

```python
# In hooks.py
doc_events = {
    # Wildcard - van toepassing op ALLE doctypes
    "*": {
        "after_insert": "app.crud_events.after_insert_all"
    },
    # Specifieke doctype
    "ToDo": {
        "before_insert": "app.crud_events.before_insert_todo",
    },
    # Meerdere handlers per event mogelijk
    "Sales Invoice": {
        "validate": [
            "myapp.events.si_validate",
            "myapp.events.si_additional_validate"
        ],
        "on_submit": "myapp.events.si_on_submit",
    }
}
```

### Alle Beschikbare Document Events

| Event | Wanneer | Method Signature |
|-------|---------|------------------|
| `before_insert` | Voor nieuw document naar database | `def handler(doc, method=None):` |
| `after_insert` | Na nieuw document is opgeslagen | `def handler(doc, method=None):` |
| `before_validate` | Voor validatie begint | `def handler(doc, method=None):` |
| `validate` | Hoofdvalidatie (Before Save UI) | `def handler(doc, method=None):` |
| `on_update` | Na document succesvol opgeslagen | `def handler(doc, method=None):` |
| `on_change` | Na elke wijziging (ook db_set) | `def handler(doc, method=None):` |
| `before_rename` | Voor document hernoemen | `def handler(doc, method, old, new, merge):` |
| `after_rename` | Na document hernoemen | `def handler(doc, method, old, new, merge):` |
| `before_submit` | Voor document submit | `def handler(doc, method=None):` |
| `on_submit` | Na document submit | `def handler(doc, method=None):` |
| `before_cancel` | Voor document cancel | `def handler(doc, method=None):` |
| `on_cancel` | Na document cancel | `def handler(doc, method=None):` |
| `on_trash` | Voor document delete | `def handler(doc, method=None):` |
| `after_delete` | Na document delete | `def handler(doc, method=None):` |
| `before_update_after_submit` | Voor update submitted doc | `def handler(doc, method=None):` |
| `on_update_after_submit` | Na update submitted doc | `def handler(doc, method=None):` |

### Handler Implementatie

```python
# In myapp/events.py

def si_validate(doc, method=None):
    """
    Handler ontvangt:
    - doc: het document object
    - method: naam van het event ("validate")
    """
    if doc.grand_total < 0:
        frappe.throw("Invalid total")

def log_creation(doc, method=None):
    """Wildcard handler voor alle doctypes"""
    frappe.log_error(f"Created {doc.doctype}: {doc.name}")

def before_rename_handler(doc, method, old, new, merge):
    """Rename handlers krijgen extra argumenten"""
    frappe.log_error(f"Renaming {old} to {new}")
```

### Hooks Resolution Order

Hooks worden opgelost met "last writer wins" strategie. De laatst geÃ¯nstalleerde app heeft de hoogste prioriteit.

- Bij override hooks: alleen de laatste app's override werkt
- Bij extend hooks: extensies worden toegepast in volgorde van installatie

> **Tip**: Volgorde aanpassen via "Installed Applications" â†’ "Update Hooks Resolution Order"

---

## 2. SCHEDULER_EVENTS: Alle Types en Cron Syntax

### Basis Syntax

```python
# In hooks.py
scheduler_events = {
    # Standaard periodes
    "hourly": [
        "myapp.tasks.hourly_cleanup"
    ],
    "daily": [
        "myapp.tasks.daily_report"
    ],
    "weekly": [
        "myapp.tasks.weekly_summary"
    ],
    "monthly": [
        "myapp.tasks.monthly_archive"
    ],
    
    # Long worker queue versies
    "hourly_long": [
        "myapp.tasks.heavy_hourly_processing"
    ],
    "daily_long": [
        "myapp.tasks.take_backups_daily"
    ],
    "weekly_long": [
        "myapp.tasks.weekly_data_cleanup"
    ],
    "monthly_long": [
        "myapp.tasks.monthly_aggregation"
    ],
    
    # Elke scheduler tick (~60 seconden)
    "all": [
        "myapp.tasks.every_tick"
    ],
    
    # Cron syntax
    "cron": {
        "*/15 * * * *": [
            "myapp.tasks.every_15_min"
        ],
        "0 9 * * 1-5": [
            "myapp.tasks.weekday_morning"
        ],
        "0 0 1 * *": [
            "myapp.tasks.first_of_month"
        ],
        "15 18 * * *": [
            "myapp.tasks.daily_at_6_15_pm"
        ]
    }
}
```

### Scheduler Event Types

| Event | Frequentie | Queue |
|-------|------------|-------|
| `all` | Elke ~60 seconden | default |
| `hourly` | Elk uur | default |
| `daily` | Elke dag | default |
| `weekly` | Elke week | default |
| `monthly` | Elke maand | default |
| `hourly_long` | Elk uur | long |
| `daily_long` | Elke dag | long |
| `weekly_long` | Elke week | long |
| `monthly_long` | Elke maand | long |
| `cron` | Custom cron syntax | default |

### Cron Syntax Format

```
* * * * *
â”‚ â”‚ â”‚ â”‚ â”‚
â”‚ â”‚ â”‚ â”‚ â””â”€â”€ Day of week (0-6, Sunday=0)
â”‚ â”‚ â”‚ â””â”€â”€â”€â”€ Month (1-12)
â”‚ â”‚ â””â”€â”€â”€â”€â”€â”€ Day of month (1-31)
â”‚ â””â”€â”€â”€â”€â”€â”€â”€â”€ Hour (0-23)
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Minute (0-59)
```

### Voorbeelden Cron Patterns

```python
"cron": {
    "0 * * * *": [...],       # Elk uur op :00
    "*/5 * * * *": [...],     # Elke 5 minuten
    "0 9 * * *": [...],       # Dagelijks om 9:00
    "0 9 * * 1-5": [...],     # Werkdagen om 9:00
    "0 0 1 * *": [...],       # Eerste dag van de maand
    "0 0 * * 0": [...],       # Elke zondag om middernacht
    "30 14 * * *": [...],     # Dagelijks om 14:30
}
```

### Task Implementatie

```python
# In myapp/tasks.py

def update_database_usage():
    """Scheduled task - geen argumenten"""
    # Task logic
    pass

def heavy_processing():
    """Long running task - gebruik _long variant"""
    for record in large_dataset:
        process_record(record)
        frappe.db.commit()
```

**BELANGRIJK**: Na wijzigingen in scheduler_events moet `bench migrate` worden uitgevoerd!

### Queue Timeouts

| Queue | Timeout |
|-------|---------|
| short | 300 seconden |
| default | 300 seconden |
| long | 1500 seconden |

---

## 3. OVERRIDE HOOKS

### override_whitelisted_methods

Override standaard whitelisted methods:

```python
# In hooks.py
override_whitelisted_methods = {
    "frappe.client.get_count": "myapp.overrides.custom_get_count",
    "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice": 
        "myapp.overrides.custom_make_sales_invoice"
}
```

```python
# In myapp/overrides.py
def custom_get_count(doctype, filters=None, debug=False, cache=False):
    """Method signature MOET identiek zijn aan origineel"""
    # Custom implementatie
    pass
```

### override_doctype_class

Volledig vervangen van een DocType controller class:

```python
# In hooks.py
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice",
    "ToDo": "myapp.overrides.todo.CustomToDo"
}
```

```python
# In myapp/overrides.py
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # BELANGRIJK: roep parent aan
        self.custom_validation()
    
    def custom_validation(self):
        # Custom logic
        pass
```

> **Let op**: Bij meerdere apps die dezelfde doctype overschrijven werkt alleen de laatste!

### extend_doctype_class (v16+)

Extend bestaande controller zonder volledig te overschrijven:

```python
# In hooks.py
extend_doctype_class = {
    "Address": ["myapp.extensions.address.AddressMixin"],
    "Contact": [
        "myapp.extensions.common.ValidationMixin",
        "myapp.extensions.contact.ContactMixin"
    ]
}
```

```python
# In myapp/extensions/address.py
from frappe.model.document import Document

class AddressMixin(Document):
    @property
    def full_address(self):
        return f"{self.address_line1}, {self.city}, {self.country}"
    
    def validate(self):
        super().validate()
        self.custom_validation()
```

> **Voordeel**: Meerdere apps kunnen dezelfde DocType extenden zonder conflicten.

### doctype_js (Override Form Scripts)

```python
# In hooks.py
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "ToDo": "public/js/todo.js"
}
```

```javascript
// In public/js/sales_invoice.js
frappe.ui.form.on("Sales Invoice", {
    refresh: function(frm) {
        frm.trigger("my_custom_code");
    },
    my_custom_code: function(frm){
        console.log(frm.doc.name);
    }
});
```

---

## 4. PERMISSION HOOKS

### permission_query_conditions

Filter list views dynamisch:

```python
# In hooks.py
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_query_conditions",
    "ToDo": "myapp.permissions.todo_query_conditions"
}
```

```python
# In myapp/permissions.py
import frappe

def si_query_conditions(user):
    """
    Retourneert een SQL WHERE clause fragment.
    user kan None zijn - controleer dit!
    """
    if not user:
        user = frappe.session.user
    
    if "Sales Manager" in frappe.get_roles(user):
        return ""  # Geen restricties
    
    if "Sales User" in frappe.get_roles(user):
        # Alleen eigen facturen
        return f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
    
    return "1=0"  # Niets tonen
```

**BELANGRIJK**: Deze hook beÃ¯nvloedt alleen `frappe.db.get_list`, NIET `frappe.db.get_all`!

### has_permission

Custom document-level permission logic:

```python
# In hooks.py
has_permission = {
    "Sales Invoice": "myapp.permissions.si_has_permission",
    "Event": "myapp.permissions.event_has_permission"
}
```

```python
# In myapp/permissions.py
def si_has_permission(doc, user=None, permission_type=None):
    """
    Return True/False voor toegang, of None voor default gedrag.
    
    Args:
        doc: het document object
        user: de user (kan None zijn, dan frappe.session.user)
        permission_type: "read", "write", "submit", "cancel", etc.
    """
    if permission_type == "write" and doc.status == "Closed":
        return False
    
    return None  # Fallback naar default permission check

def event_has_permission(doc, user=None, permission_type=None):
    if permission_type == "read" and doc.event_type == "Public":
        return True
    if permission_type == "write" and doc.owner == user:
        return True
    return False
```

---

## 5. INCLUDE HOOKS (Assets)

### Desk Assets

```python
# In hooks.py

# Injecteren in desk.html (Desk interface)
app_include_js = "assets/myapp/js/myapp.min.js"
app_include_css = "assets/myapp/css/myapp.min.css"

# Meerdere bestanden
app_include_js = [
    "assets/myapp/js/app1.min.js",
    "assets/myapp/js/app2.min.js"
]
```

### Portal/Website Assets

```python
# Injecteren in web.html (Portal pagina's)
web_include_js = "assets/myapp/js/web.min.js"
web_include_css = "assets/myapp/css/web.min.css"
```

### WebForm Assets

```python
# Specifiek voor standaard Web Forms
webform_include_js = {
    "ToDo": "public/js/custom_todo.js"
}
webform_include_css = {
    "ToDo": "public/css/custom_todo.css"
}
```

### Page Assets

```python
# Custom JS voor standaard Desk Pages
page_js = {
    "background_jobs": "public/js/custom_background_jobs.js"
}
```

### DocType List JS

```python
# Custom JS voor list views
doctype_list_js = {
    "Sales Invoice": "public/js/sales_invoice_list.js"
}
```

---

## 6. BOOT HOOKS

### extend_bootinfo

Voeg globale waarden toe aan `frappe.boot`:

```python
# In hooks.py
extend_bootinfo = "myapp.boot.boot_session"
```

```python
# In myapp/boot.py
def boot_session(bootinfo):
    """
    bootinfo is een dict dat wordt geÃ¯njecteerd in frappe.boot
    """
    bootinfo.my_global_key = "my_global_value"
    bootinfo.company_settings = frappe.get_doc("Company Settings")
    bootinfo.user_preferences = get_user_preferences()
```

```javascript
// Beschikbaar in client-side JavaScript
console.log(frappe.boot.my_global_key);  // "my_global_value"
```

---

## 7. FIXTURES

### Basis Syntax

```python
# In hooks.py
fixtures = [
    # Exporteer alle records van deze DocType
    "Custom Field",
    "Property Setter",
    
    # Met filters
    {"dt": "Role", "filters": [["name", "like", "MyApp%"]]},
    
    # Single DocTypes
    "Website Settings",
    
    # Complex filters
    {
        "dt": "Custom Script",
        "filters": [
            ["dt", "=", "Sales Invoice"],
            ["enabled", "=", 1]
        ]
    }
]
```

### Export Command

```bash
bench --site sitename export-fixtures
```

Dit maakt JSON bestanden in de `fixtures/` folder van je app.

### Automatische Sync

Fixtures worden automatisch geÃ¯mporteerd bij:
- App installatie
- `bench update`
- `bench migrate`

### Velden die NIET worden geÃ«xporteerd

- `modified_by`
- `creation`
- `owner`
- `idx`
- `lft` en `rgt` (voor tree structures)

Voor child tables ook:
- `docstatus`
- `doctype`
- `modified`
- `name`

---

## 8. JENV (Jinja Environment Extensions)

### Methods en Filters Toevoegen

```python
# In hooks.py
jenv = {
    "methods": [
        "myapp.jinja.methods",           # Module - alle functies worden geÃ«xporteerd
        "myapp.utils.get_fullname"       # Enkele functie
    ],
    "filters": [
        "myapp.jinja.filters",
        "myapp.utils.format_currency"
    ]
}
```

```python
# In myapp/jinja/methods.py

def sum(a, b):
    """Beschikbaar als {{ sum(1, 2) }}"""
    return a + b

def multiply(a, b):
    """Beschikbaar als {{ multiply(3, 4) }}"""
    return a * b
```

```python
# In myapp/jinja/filters.py

def format_currency(value, currency):
    """Beschikbaar als {{ amount | format_currency("EUR") }}"""
    return f"{currency} {value:,.2f}"

def truncate_words(text, max_words=10):
    """Beschikbaar als {{ description | truncate_words(5) }}"""
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return text
```

### Gebruik in Templates

```jinja
{# Print Format of Email Template #}

<h1>Hi, {{ get_fullname(frappe.session.user) }}</h1>
<p>Your balance: {{ account_balance | format_currency("EUR") }}</p>
<p>1 + 2 = {{ sum(1, 2) }}</p>
<p>{{ description | truncate_words(20) }}</p>
```

### Standaard Beschikbare Jinja Methods

| Method | Beschrijving |
|--------|--------------|
| `frappe.format(value, df)` | Formatteer waarde per fieldtype |
| `frappe.format_date(date)` | Human-readable date |
| `frappe.get_doc(doctype, name)` | Fetch document |
| `frappe.get_all(doctype, filters, fields)` | Query records |
| `frappe.get_list(doctype, filters, fields)` | Query met permissions |
| `frappe.db.get_value(doctype, name, field)` | Get enkele waarde |
| `frappe.db.get_single_value(doctype, field)` | Get waarde van Single DocType |
| `frappe.get_url()` | Site URL |
| `frappe.get_meta(doctype)` | DocType meta data |
| `frappe.get_fullname(user)` | Full name van user |
| `frappe.render_template(template, context)` | Render sub-template |
| `_("text")` | Vertaling functie |
| `frappe.session.user` | Huidige session user |
| `frappe.session.csrf_token` | CSRF token |
| `frappe.form_dict` | Query parameters (in web request) |
| `frappe.lang` | Huidige taal code |

---

## 9. ANDERE ESSENTIÃ‹LE HOOKS

### Install/Uninstall Hooks

```python
# In hooks.py
before_install = "myapp.setup.install.before_install"
after_install = "myapp.setup.install.after_install"
after_sync = "myapp.setup.install.after_sync"

before_uninstall = "myapp.setup.uninstall.before_uninstall"
after_uninstall = "myapp.setup.uninstall.after_uninstall"
```

### Migrate Hooks

```python
before_migrate = "myapp.migrate.before_migrate"
after_migrate = "myapp.migrate.after_migrate"
```

### Test Hooks

```python
before_tests = "myapp.tests.before_tests"
```

### Clear Cache Hook

```python
clear_cache = "myapp.cache.clear_cache"
```

```python
def clear_cache():
    frappe.cache().hdel("app_specific_cache")
```

### Required Apps

```python
required_apps = ["erpnext"]
```

### Default Mail Footer

```python
default_mail_footer = """
<div>
    Sent via <a href="https://example.com">My App</a>
</div>
"""
```

### Website Hooks

```python
# Website context
website_context = {
    "favicon": "/assets/myapp/image/favicon.png"
}

# Dynamic context
update_website_context = "myapp.website.update_context"

# Homepage
homepage = "homepage"

# Role-based homepage
role_home_page = {
    "Customer": "orders",
    "Supplier": "bills"
}

# Website redirects
website_redirects = [
    {"source": "/old-page", "target": "/new-page"},
    {"source": r"/docs/(.*)", "target": r"https://docs.example.com/\1"}
]

# Route rules
website_route_rules = [
    {"from_route": "/projects/<name>", "to_route": "myapp/projects/project"}
]

# 404 page
website_catch_all = "not_found"
```

### Session Hooks

```python
on_login = "myapp.events.on_login"
on_session_creation = "myapp.events.on_session_creation"
on_logout = "myapp.events.on_logout"
```

### Auth Hooks

```python
auth_hooks = ["myapp.auth.validate_custom_jwt"]
```

### Sounds

```python
sounds = [
    {"name": "ping", "src": "/assets/myapp/sounds/ping.mp3", "volume": 0.2}
]
```

---

## 10. COMPLETE HOOKS REFERENCE TABEL

| Hook Naam | Functie | Type |
|-----------|---------|------|
| `doc_events` | Document CRUD events | Dict |
| `scheduler_events` | Periodieke taken | Dict |
| `override_whitelisted_methods` | Override API methods | Dict |
| `override_doctype_class` | Override controller | Dict |
| `extend_doctype_class` | Extend controller (v16+) | Dict |
| `doctype_js` | Extend form scripts | Dict |
| `permission_query_conditions` | Filter list queries | Dict |
| `has_permission` | Custom doc permissions | Dict |
| `app_include_js/css` | Desk assets | String/List |
| `web_include_js/css` | Portal assets | String/List |
| `extend_bootinfo` | Add to frappe.boot | String |
| `fixtures` | Data export/import | List |
| `jenv` | Jinja extensions | Dict |
| `before/after_install` | Install hooks | String |
| `before/after_migrate` | Migrate hooks | String |
| `before_tests` | Test setup | String |
| `clear_cache` | Cache clearing | String |
| `required_apps` | App dependencies | List |

---

## 11. ANTI-PATTERNS EN BEST PRACTICES

### âŒ Commit in hooks

```python
# FOUT - Frappe handelt commits automatisch af
def on_update(doc, method=None):
    frappe.db.commit()  # NIET DOEN
```

### âŒ Heavy operations in sync hooks

```python
# FOUT - blokkeert de gebruiker
def validate(doc, method=None):
    process_large_dataset()  # Kan minuten duren

# GOED - gebruik scheduler of enqueue
def on_update(doc, method=None):
    frappe.enqueue(
        'myapp.tasks.process_large_dataset',
        doc_name=doc.name,
        queue='long'
    )
```

### âŒ Vergeten super() aan te roepen

```python
# FOUT - override zonder parent call
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        self.custom_validation()  # Parent validate niet aangeroepen!

# GOED
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()
        self.custom_validation()
```

### âŒ Fixtures zonder filters

```python
# FOUT - exporteert ALLES
fixtures = ["Custom Field"]  # Potentieel honderden records

# GOED - filter op relevante records
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]}
]
```

### âœ… Best Practices

1. **Altijd `bench migrate` na scheduler_events wijzigingen**
2. **Gebruik `_long` varianten voor zware taken**
3. **Test permission hooks grondig**
4. **Documenteer alle custom hooks**
5. **Gebruik `extend_doctype_class` (v16+) i.p.v. `override_doctype_class`**

---

## 12. VERSIE VERSCHILLEN (v14 vs v15 vs v16)

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| `extend_doctype_class` | âŒ | âŒ | âœ… |
| `before_discard/on_discard` | âŒ | âœ… | âœ… |
| Type annotations export | âŒ | âœ… | âœ… |
| Alle standaard hooks | âœ… | âœ… | âœ… |

---

## Samenvatting voor Skill Creatie

### Key Learnings

1. **doc_events** is de primaire manier om document lifecycle events te hooken
2. **scheduler_events** biedt periodes EN cron syntax
3. **_long varianten** gebruiken voor zware taken
4. **permission_query_conditions** beÃ¯nvloedt alleen `get_list`, niet `get_all`
5. **jenv** voor Jinja methods Ã©n filters
6. **extend_doctype_class** (v16+) is veiliger dan `override_doctype_class`
7. **Hooks resolution** = "last writer wins"

### Skill References te Maken

1. `doc-events.md` - Alle document events met syntax
2. `scheduler-events.md` - Scheduler configuratie en cron
3. `override-hooks.md` - Override en extend patterns
4. `permission-hooks.md` - Permission customization
5. `asset-hooks.md` - JS/CSS includes
6. `jenv-hooks.md` - Jinja extensions
7. `examples.md` - Complete werkende voorbeelden
8. `anti-patterns.md` - Wat te vermijden
