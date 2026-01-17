---
name: erpnext-permissions
description: Complete handleiding voor Frappe/ERPNext permissiesysteem - rollen, gebruikerspermissies, permissieniveaus en permissie-hooks
version: 1.0.0
author: OpenAEC Foundation
tags: [erpnext, frappe, permissions, security, roles, access-control]
frameworks: [frappe-14, frappe-15, frappe-16]
---

# ERPNext Permissions Skill

> Deterministische patronen voor het implementeren van robuuste permissiesystemen in Frappe/ERPNext applicaties.

---

## Overzicht

Frappe's permissiesysteem heeft vier lagen:

| Laag | Bepaalt | Geconfigureerd Via |
|------|---------|-------------------|
| **Role Permissions** | Wat gebruikers KUNNEN doen | DocType permissions tabel |
| **User Permissions** | WELKE documenten gebruikers zien | User Permission records |
| **Perm Levels** | WELKE velden gebruikers zien | Field permlevel eigenschap |
| **Permission Hooks** | Aangepaste logica | hooks.py |

---

## Snelle Referentie

### Permissie Types

| Type | Check | Voor |
|------|-------|------|
| `read` | `frappe.has_permission(dt, "read")` | Document bekijken |
| `write` | `frappe.has_permission(dt, "write")` | Document bewerken |
| `create` | `frappe.has_permission(dt, "create")` | Nieuw aanmaken |
| `delete` | `frappe.has_permission(dt, "delete")` | Verwijderen |
| `submit` | `frappe.has_permission(dt, "submit")` | Indienen (alleen submittable) |
| `cancel` | `frappe.has_permission(dt, "cancel")` | Annuleren |
| `select` | `frappe.has_permission(dt, "select")` | Selecteren in Link (v14+) |

### Automatische Rollen

| Rol | Toegewezen Aan |
|-----|----------------|
| `Guest` | Iedereen (inclusief anoniem) |
| `All` | Alle geregistreerde gebruikers |
| `Administrator` | Alleen Administrator gebruiker |
| `Desk User` | Systeemgebruikers (v15+) |

---

## Essentiële API

### Permissie Controleren

```python
# DocType level
frappe.has_permission("Sales Order", "write")

# Document level
frappe.has_permission("Sales Order", "write", "SO-00001")
frappe.has_permission("Sales Order", "write", doc=doc)

# For specific user
frappe.has_permission("Sales Order", "read", user="john@example.com")

# Throw on denial
frappe.has_permission("Sales Order", "delete", throw=True)

# On document instance
doc = frappe.get_doc("Sales Order", "SO-00001")
if doc.has_permission("write"):
    doc.status = "Approved"
    doc.save()

# Raise error if no permission
doc.check_permission("write")
```

### Permissies Ophalen

```python
from frappe.permissions import get_doc_permissions

# Get all permissions for document
perms = get_doc_permissions(doc)
# {'read': 1, 'write': 1, 'create': 0, 'delete': 0, ...}
```

### Gebruikerspermissies

```python
from frappe.permissions import add_user_permission, remove_user_permission

# Restrict user to specific company
add_user_permission(
    doctype="Company",
    name="My Company",
    user="john@example.com",
    is_default=1
)

# Remove restriction
remove_user_permission("Company", "My Company", "john@example.com")

# Get user's permissions
from frappe.permissions import get_user_permissions
perms = get_user_permissions("john@example.com")
```

### Delen

```python
from frappe.share import add as add_share

# Share document with user
add_share(
    doctype="Sales Order",
    name="SO-00001",
    user="jane@example.com",
    read=1,
    write=1
)
```

---

## Permissie Hooks

### has_permission Hook

Voeg aangepaste permissielogica toe. Kan alleen **weigeren**, niet toekennen.

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.check_order_permission"
}
```

```python
# myapp/permissions.py
def check_order_permission(doc, ptype, user):
    """
    Returns:
        None: Ga door met standaard checks
        False: Weiger permissie
    """
    # Weiger bewerken van geannuleerde orders voor niet-managers
    if ptype == "write" and doc.docstatus == 2:
        if "Sales Manager" not in frappe.get_roles(user):
            return False
    
    return None  # ALTIJD None retourneren als standaard
```

### permission_query_conditions Hook

Filtert lijst-queries. Heeft alleen effect op `get_list()`, NIET op `get_all()`.

```python
# hooks.py
permission_query_conditions = {
    "Customer": "myapp.permissions.customer_query"
}
```

```python
# myapp/permissions.py
def customer_query(user):
    """Retourneer SQL WHERE clause fragment."""
    if not user:
        user = frappe.session.user
    
    # Managers zien alles
    if "Sales Manager" in frappe.get_roles(user):
        return ""
    
    # Anderen zien alleen hun eigen klanten
    return f"`tabCustomer`.owner = {frappe.db.escape(user)}"
```

**KRITIEK**: Gebruik altijd `frappe.db.escape()` - nooit string concatenatie!

---

## get_list vs get_all

| Methode | User Permissions | Query Hook |
|---------|------------------|------------|
| `frappe.get_list()` | ✅ Toegepast | ✅ Toegepast |
| `frappe.get_all()` | ❌ Genegeerd | ❌ Genegeerd |

```python
# Gebruiker-gerichte query - respecteert permissies
docs = frappe.get_list("Sales Order", filters={"status": "Open"})

# Systeem query - omzeilt permissies
docs = frappe.get_all("Sales Order", filters={"status": "Open"})
```

---

## Veld-Niveau Permissies (Perm Levels)

### Veld Configureren

```json
{
  "fieldname": "salary",
  "fieldtype": "Currency",
  "permlevel": 1
}
```

### Rol Toegang Configureren

```json
{
  "permissions": [
    {"role": "Employee", "permlevel": 0, "read": 1},
    {"role": "HR Manager", "permlevel": 0, "read": 1, "write": 1},
    {"role": "HR Manager", "permlevel": 1, "read": 1, "write": 1}
  ]
}
```

**Regel**: Level 0 MOET toegekend worden vóór hogere levels.

---

## Beslisboom

```
Toegang controleren nodig?
├── Tot hele DocType → Role Permissions
├── Tot specifieke documenten → User Permissions
├── Tot specifieke velden → Perm Levels
├── Met aangepaste logica → has_permission hook
└── Voor lijst queries → permission_query_conditions hook

Permissies controleren in code?
├── Vóór actie → frappe.has_permission() of doc.has_permission()
├── Error gooien → doc.check_permission() of throw=True
└── Bypass nodig → doc.flags.ignore_permissions = True (documenteer waarom!)
```

---

## Veelgebruikte Patronen

### Alleen Eigenaar Kan Bewerken

```json
{
  "role": "Sales User",
  "read": 1, "write": 1, "create": 1,
  "if_owner": 1
}
```

### Controleer Vóór Actie

```python
@frappe.whitelist()
def approve_order(order_name):
    doc = frappe.get_doc("Sales Order", order_name)
    
    if not doc.has_permission("write"):
        frappe.throw(_("No permission"), frappe.PermissionError)
    
    doc.status = "Approved"
    doc.save()
```

### Rol-Beperkt Endpoint

```python
@frappe.whitelist()
def sensitive_action():
    frappe.only_for(["Manager", "Administrator"])
    # Bereikt hier alleen als gebruiker de rol heeft
```

---

## Kritieke Regels

1. **ALTIJD permissie API gebruiken** - Niet rol checks
2. **ALTIJD SQL escapen** - `frappe.db.escape(user)`
3. **ALTIJD get_list gebruiken** - Voor gebruiker-gerichte queries
4. **ALTIJD None retourneren** - In has_permission hooks (niet True)
5. **ALTIJD documenteren** - Bij gebruik van ignore_permissions
6. **ALTIJD cache legen** - Na permissie wijzigingen: `frappe.clear_cache()`

---

## Anti-Patronen

| ❌ Niet Doen | ✅ Wel Doen |
|--------------|-------------|
| `if "Role" in frappe.get_roles()` | `frappe.has_permission(dt, ptype)` |
| `frappe.get_all()` voor gebruiker queries | `frappe.get_list()` |
| `return True` in has_permission | `return None` |
| `f"owner = '{user}'"` | `f"owner = {frappe.db.escape(user)}"` |
| `frappe.throw()` in hooks | `return False` |

---

## Versieverschillen

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| `select` permission | ✅ | ✅ | ✅ |
| `Desk User` role | ❌ | ✅ | ✅ |
| Custom Permission Types | ❌ | ❌ | ✅ (experimental) |
| Data Masking | ❌ | ❌ | ✅ (experimental) |

---

## Debugging

```python
# Debug output inschakelen
frappe.has_permission("Sales Order", "read", doc, debug=True)

# Logs bekijken
print(frappe.local.permission_debug_log)

# Effectieve permissies van gebruiker controleren
from frappe.permissions import get_doc_permissions
perms = get_doc_permissions(doc, user="john@example.com")
```

---

## Referentie Bestanden

Zie `references/` map voor:
- `permission-types-reference.md` - Alle permissie types
- `permission-api-reference.md` - Complete API referentie
- `permission-hooks-reference.md` - Hook patronen
- `examples.md` - Werkende voorbeelden
- `anti-patterns.md` - Veelgemaakte fouten

---

## Gerelateerde Skills

- `erpnext-database` - Database operaties die permissies respecteren
- `erpnext-syntax-controllers` - Controller permissie checks
- `erpnext-syntax-hooks` - Hook configuratie

---

*Laatst bijgewerkt: 2026-01-17 | Frappe v14/v15/v16*
