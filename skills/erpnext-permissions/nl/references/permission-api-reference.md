# Permission API Reference

## frappe.has_permission()

Hoofdfunctie voor permission checks.

```python
# Basis check
has_read = frappe.has_permission("Sales Order", "read")
has_read = frappe.has_permission("Sales Order", ptype="read")

# Check specifiek document
has_read = frappe.has_permission("Sales Order", "read", doc="SO-00001")
has_read = frappe.has_permission("Sales Order", "read", doc=doc_object)

# Check voor specifieke user (default: huidige user)
has_read = frappe.has_permission("Sales Order", "read", user="john@example.com")

# Throw error bij geen permission
frappe.has_permission("Sales Order", "write", throw=True)

# Debug mode - print permission check logs
has_read = frappe.has_permission("Sales Order", "read", debug=True)

# Custom permission type
has_approve = frappe.has_permission(doc, "approve")
```

## Document.has_permission()

Check permissions op document instance:

```python
doc = frappe.get_doc("Sales Order", "SO-00001")

# Check permission
if doc.has_permission("write"):
    doc.status = "Draft"
    doc.save()

# Met debug output
doc.has_permission("write", debug=True)

# Voor specifieke user
doc.has_permission("read", user="jane@example.com")
```

## Document.check_permission()

Raises `frappe.PermissionError` als geen permission:

```python
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.check_permission("write")  # Raises error als geen permission
# Ga alleen verder als permission bestaat
```

## get_doc_permissions()

Haal alle permissions voor een document op:

```python
from frappe.permissions import get_doc_permissions

perms = get_doc_permissions(doc)
# Returns: {'read': 1, 'write': 1, 'create': 0, 'delete': 0, ...}

perms = get_doc_permissions(doc, user="john@example.com")
```

## get_role_permissions()

Haal permissions op basis van rollen (zonder user permissions):

```python
from frappe.permissions import get_role_permissions

meta = frappe.get_meta("Sales Order")
perms = get_role_permissions(meta)
perms = get_role_permissions(meta, user="john@example.com")
```

## get_user_permissions()

Haal user permissions op:

```python
from frappe.permissions import get_user_permissions

# Haal alle user permissions voor huidige user
user_perms = get_user_permissions()
# Returns: {"Territory": [{"doc": "North", "is_default": 1}], ...}

# Haal voor specifieke user
user_perms = get_user_permissions(user="john@example.com")
```

## frappe.get_roles()

Haal rollen van een user op:

```python
# Rollen van specifieke user
user_roles = frappe.get_roles("user@example.com")
# Returns: ['Guest', 'All', 'Sales User', 'System Manager']

# Rollen van huidige user
my_roles = frappe.get_roles()

# Check specifieke rol
if "System Manager" in frappe.get_roles():
    # User heeft System Manager rol
    pass
```

## User Permission Management

```python
from frappe.permissions import (
    add_user_permission,
    remove_user_permission,
    clear_user_permissions_for_doctype
)

# Toevoegen
add_user_permission(
    doctype="Territory",           # Wat te beperken
    name="North",                  # Toegestane waarde
    user="john@example.com",       # Welke user
    ignore_permissions=True,
    applicable_for="Sales Order"   # Optioneel: alleen voor dit DocType
)

# Verwijderen
remove_user_permission("Company", "My Company", "john@example.com")

# Wis alle voor een doctype
clear_user_permissions_for_doctype("Company", "john@example.com")
```

## Role Permission Management

```python
from frappe.permissions import add_permission, update_permission_property, remove_permission, reset_perms

# Voeg role permission toe aan DocType
add_permission("Sales Order", "Sales User", permlevel=0)

# Update specifieke permission property
update_permission_property("Sales Order", "Sales User", 0, "write", 1)
update_permission_property("Sales Order", "Sales User", 0, "if_owner", 1)

# Verwijder permission
remove_permission("Sales Order", "Sales User", permlevel=0)

# Reset naar DocType defaults
reset_perms("Sales Order")
```

## Document Sharing

```python
from frappe.share import add as add_share, remove as remove_share, get_shared

# Deel document
add_share(
    doctype="Sales Order",
    name="SO-00001",
    user="jane@example.com",
    read=1,
    write=1,
    share=0
)

# Verwijder share
remove_share("Sales Order", "SO-00001", "jane@example.com")

# Haal users met shared access op
shared_with = get_shared("Sales Order", "SO-00001")
```

## Ignoring Permissions

```python
# Via flags
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.flags.ignore_permissions = True
doc.save()

# Of direct doorgeven
doc.save(ignore_permissions=True)

# get_doc met permission check
doc = frappe.get_doc("Sales Order", "SO-00001", check_permission="read")
```

## get_list vs get_all

| Methode | User Permissions | permission_query_conditions |
|---------|------------------|----------------------------|
| `frappe.get_list()` | Toegepast | Toegepast |
| `frappe.get_all()` | **Genegeerd** | **Genegeerd** |
| `frappe.db.get_list()` | Toegepast | Toegepast |
| `frappe.db.get_all()` | **Genegeerd** | **Genegeerd** |
