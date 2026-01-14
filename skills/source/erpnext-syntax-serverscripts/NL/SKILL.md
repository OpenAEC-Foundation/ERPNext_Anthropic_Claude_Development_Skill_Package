---
name: erpnext-syntax-serverscripts
description: Complete syntax referentie voor Frappe Server Scripts. Gebruik deze skill wanneer Claude Python code moet schrijven voor Server Scripts in ERPNext/Frappe, inclusief Document Events, API endpoints, Scheduler Events en Permission Queries. Dekt sandbox beperkingen, beschikbare frappe.* methods, event name mapping, en correcte syntax voor v14/v15.
---

# ERPNext Server Scripts Syntax

Server Scripts zijn Python scripts die draaien binnen Frappe's beveiligde sandbox omgeving. Ze worden beheerd via **Setup → Server Script** in de ERPNext UI.

## KRITIEK: Sandbox Beperkingen

```
┌─────────────────────────────────────────────────────────────────────┐
│ ⚠️  GEEN IMPORTS TOEGESTAAN                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ De sandbox blokkeert ALLE import statements:                       │
│   import json        → ImportError: __import__ not found           │
│   from datetime import date  → ImportError                         │
│                                                                     │
│ OPLOSSING: Gebruik Frappe's pre-loaded namespace:                  │
│   frappe.utils.nowdate()     niet: from frappe.utils import nowdate│
│   frappe.parse_json(data)    niet: import json; json.loads(data)   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Server Script Types

| Type | Gebruik | Trigger |
|------|---------|---------|
| **Document Event** | Reageer op document lifecycle | Save, Submit, Cancel, etc. |
| **API** | Custom REST endpoint | HTTP request naar `/api/method/{naam}` |
| **Scheduler Event** | Geplande taken | Cron schedule |
| **Permission Query** | Dynamische list filtering | Document list view |

## Event Name Mapping (Document Event)

**BELANGRIJK**: De UI event namen verschillen van de interne hook namen:

| UI Naam (Server Script) | Interne Hook | Wanneer |
|-------------------------|--------------|---------|
| Before Insert | `before_insert` | Voor nieuw doc naar DB |
| After Insert | `after_insert` | Na nieuw doc opgeslagen |
| Before Validate | `before_validate` | Voor validatie |
| **Before Save** | **`validate`** | Voor save (nieuw of update) |
| After Save | `on_update` | Na succesvol opslaan |
| Before Submit | `before_submit` | Voor submit |
| After Submit | `on_submit` | Na submit |
| Before Cancel | `before_cancel` | Voor cancel |
| After Cancel | `on_cancel` | Na cancel |
| Before Delete | `on_trash` | Voor delete |
| After Delete | `after_delete` | Na delete |

## Quick Reference: Beschikbare API

### Altijd beschikbaar in sandbox

```python
# Document object (bij Document Event scripts)
doc                      # Huidig document
doc.name                 # Document naam
doc.doctype              # DocType naam
doc.fieldname            # Veld waarde
doc.get("fieldname")     # Veilig veld ophalen
doc.items                # Child table (lijst)

# Frappe namespace
frappe.db                # Database operaties
frappe.get_doc()         # Document ophalen
frappe.get_all()         # Meerdere documents
frappe.throw()           # Validatie error
frappe.msgprint()        # User message
frappe.log_error()       # Error logging
frappe.utils.*           # Utility functies
frappe.session.user      # Huidige gebruiker
frappe.form_dict         # Request parameters (API)
frappe.response          # Response object (API)
```

## Decision Tree: Welk Script Type?

```
Wat wil je bereiken?
│
├─► Reageren op document save/submit/cancel?
│   └─► Document Event script
│
├─► REST API endpoint maken?
│   └─► API script
│
├─► Taak op schema uitvoeren?
│   └─► Scheduler Event script
│
└─► Document list view filteren per user/role?
    └─► Permission Query script
```

## Basis Syntax per Type

### Document Event

```python
# Configuratie:
#   Reference DocType: Sales Invoice
#   DocType Event: Before Save (= validate)

if doc.grand_total < 0:
    frappe.throw("Totaal kan niet negatief zijn")

if doc.grand_total > 10000:
    doc.requires_approval = 1
```

### API

```python
# Configuratie:
#   API Method: get_customer_info
#   Allow Guest: No
# Endpoint: /api/method/get_customer_info

customer = frappe.form_dict.get("customer")
if not customer:
    frappe.throw("Customer parameter verplicht")

data = frappe.get_all(
    "Sales Order",
    filters={"customer": customer, "docstatus": 1},
    fields=["name", "grand_total"],
    limit=10
)
frappe.response["message"] = data
```

### Scheduler Event

```python
# Configuratie:
#   Event Frequency: Cron
#   Cron Format: 0 9 * * * (dagelijks om 9:00)

overdue = frappe.get_all(
    "Sales Invoice",
    filters={"status": "Unpaid", "due_date": ["<", frappe.utils.today()]},
    fields=["name", "customer"]
)

for inv in overdue:
    frappe.log_error(f"Overdue: {inv.name}", "Invoice Reminder")

frappe.db.commit()
```

### Permission Query

```python
# Configuratie:
#   Reference DocType: Sales Invoice
# Output: conditions string voor WHERE clause

user_roles = frappe.get_roles(user)

if "Sales Manager" in user_roles:
    conditions = ""  # Alles zichtbaar
elif "Sales User" in user_roles:
    conditions = f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
else:
    conditions = "1=0"  # Niets zichtbaar
```

## References

- **[references/events.md](references/events.md)** - Complete event mapping en execution order
- **[references/methods.md](references/methods.md)** - Alle beschikbare frappe.* methods in sandbox
- **[references/examples.md](references/examples.md)** - 10+ werkende voorbeelden per script type
- **[references/anti-patterns.md](references/anti-patterns.md)** - Sandbox beperkingen en veelgemaakte fouten

## Versie Informatie

- **Frappe v14+**: Server Scripts volledig ondersteund
- **Activatie vereist**: `bench --site [site] set-config server_script_enabled true`
- **Frappe v15**: Geen significante syntax wijzigingen voor Server Scripts
