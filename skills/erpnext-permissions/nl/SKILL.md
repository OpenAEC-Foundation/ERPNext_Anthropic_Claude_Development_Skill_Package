---
name: erpnext-permissions
description: Frappe/ERPNext permission systeem - role-based permissions, user permissions, perm levels, permission hooks, en permission API. Gebruik voor DocType permission configuratie, programmatische permission checks, user permission restricties, permission_query_conditions, has_permission hooks, en field-level access control via perm levels.
---

# ERPNext Permissions

## Architectuur Overzicht

Frappe's permission systeem bestaat uit vier lagen:

1. **Role Permissions** - Wat een rol MAG doen op een DocType
2. **User Permissions** - WELKE documenten een user mag zien (data filtering)
3. **Perm Levels** - Field-level toegangscontrole
4. **Permission Hooks** - Programmatische permission aanpassingen

### Permission Flow

```
User Request
    ↓
Role Permission Check (heeft rol read/write/etc?)
    ↓
User Permission Filter (welke documenten?)
    ↓
Perm Level Check (welke velden?)
    ↓
Permission Hooks (custom logica)
    ↓
Access Granted/Denied
```

## Quick Reference

### Permission Check

```python
# Basis check
if frappe.has_permission("Sales Order", "write"):
    # proceed

# Met document
if frappe.has_permission("Sales Order", "write", doc=doc):
    doc.save()

# Throw bij geen permission
frappe.has_permission("Sales Order", "write", throw=True)

# Check op document instance
doc.check_permission("write")  # Raises PermissionError indien geen toegang
```

### Rol Check

```python
# Haal rollen op
roles = frappe.get_roles()  # Huidige user
roles = frappe.get_roles("user@example.com")

# Check specifieke rol
if "Sales Manager" in frappe.get_roles():
    pass
```

### User Permissions

```python
from frappe.permissions import add_user_permission, remove_user_permission

# Beperk user tot specifieke waarde
add_user_permission("Territory", "North", "john@example.com")

# Verwijder restrictie
remove_user_permission("Territory", "North", "john@example.com")
```

## Essentiële API Methodes

| Methode | Doel |
|---------|------|
| `frappe.has_permission(doctype, ptype, doc)` | Check permission |
| `doc.has_permission(ptype)` | Check op document |
| `doc.check_permission(ptype)` | Check + throw |
| `frappe.get_roles(user)` | Haal user rollen |
| `add_user_permission()` | Voeg data restrictie toe |
| `frappe.get_list()` | Query MET permissions |
| `frappe.get_all()` | Query ZONDER permissions |

**Kritiek**: `get_list` past user permissions toe, `get_all` NIET.

## Permission Hooks

### has_permission Hook

Voeg custom permission logica toe:

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.check_so_permission"
}
```

```python
# myapp/permissions.py
def check_so_permission(doc, ptype, user):
    """
    Returns:
        None - Ga door met standaard checks
        False - Weiger permission
    """
    if doc.docstatus == 2 and "Manager" not in frappe.get_roles(user):
        return False
    return None
```

**KRITIEK**: Deze hook kan alleen permission WEIGEREN (return False), niet TOEKENNEN.

### permission_query_conditions Hook

Filter list queries:

```python
# hooks.py
permission_query_conditions = {
    "ToDo": "myapp.permissions.todo_query"
}
```

```python
# myapp/permissions.py
def todo_query(user):
    """Returns SQL WHERE clause fragment."""
    if not user:
        user = frappe.session.user
    return f"`tabToDo`.owner = {frappe.db.escape(user)}"
```

**KRITIEK**: ALTIJD `frappe.db.escape()` gebruiken voor user input!

## Perm Levels (Field-Level Access)

Groepeer velden voor gescheiden toegangscontrole:

1. Zet `permlevel` op veld (1-9)
2. Geef rol toegang tot dat level via Role Permission Manager

```python
# DocType field definitie
{
    "fieldname": "salary",
    "permlevel": 1  # Alleen rollen met level 1 access zien dit
}
```

**Regel**: Level 0 MOET worden toegekend voordat hogere levels kunnen worden toegekend.

## Decision Tree

### Welke Methode Gebruiken?

```
Wil je data filteren voor een user?
├─ Ja → User Permissions + get_list()
└─ Nee, actie beperken
   ├─ Standaard CRUD → Role Permissions in DocType
   ├─ Custom business logica → has_permission hook
   └─ Veld verbergen → Perm Levels
```

### get_list vs get_all

```
Is dit een user-facing query?
├─ Ja → frappe.get_list() (permissions toegepast)
└─ Nee, systeem operatie → frappe.get_all() (geen filter)
```

## Versie Verschillen

| Feature | v14 | v15+ |
|---------|-----|------|
| `select` permission | Geïntroduceerd | Beschikbaar |
| `Desk User` rol | Niet beschikbaar | Automatisch |
| has_permission return True | Geen effect | Kan permission toekennen |
| Debug parameter | `verbose` | `debug` |

## Kritieke Regels

1. **ALTIJD** `frappe.has_permission()` gebruiken, NIET hardcoded rol checks
2. **NOOIT** `get_all()` voor user-facing queries (negeert permissions)
3. **ALTIJD** `frappe.db.escape()` in permission_query_conditions
4. **ALTIJD** cache clearen na permission wijzigingen: `frappe.clear_cache()`
5. **DOCUMENTEER** waarom je `ignore_permissions=True` gebruikt

## Reference Files

- [Permission Types Reference](references/permission-types-reference.md) - Alle permission types en opties
- [Permission API Reference](references/permission-api-reference.md) - Complete API documentatie
- [Permission Hooks Reference](references/permission-hooks-reference.md) - Hook patterns en voorbeelden
- [Examples](references/examples.md) - Werkende code voorbeelden
- [Anti-Patterns](references/anti-patterns.md) - Veelgemaakte fouten en oplossingen
