# Permission API Reference

## frappe.has_permission()

Main function for permission checks.

```python
# Basic check
has_read = frappe.has_permission("Sales Order", "read")
has_read = frappe.has_permission("Sales Order", ptype="read")

# Check specific document
has_read = frappe.has_permission("Sales Order", "read", doc="SO-00001")
has_read = frappe.has_permission("Sales Order", "read", doc=doc_object)

# Check for specific user (default: current user)
has_read = frappe.has_permission("Sales Order", "read", user="john@example.com")

# Throw error if no permission
frappe.has_permission("Sales Order", "write", throw=True)

# Debug mode - prints permission check logs
has_read = frappe.has_permission("Sales Order", "read", debug=True)

# Custom permission type
has_approve = frappe.has_permission(doc, "approve")
```

## Document.has_permission()

Check permissions on document instance:

```python
doc = frappe.get_doc("Sales Order", "SO-00001")

# Check permission
if doc.has_permission("write"):
    doc.status = "Draft"
    doc.save()

# With debug output
doc.has_permission("write", debug=True)

# For specific user
doc.has_permission("read", user="jane@example.com")
```

## Document.check_permission()

Raises `frappe.PermissionError` if no permission:

```python
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.check_permission("write")  # Raises error if no permission
# Continue only if permission exists
```

## get_doc_permissions()

Get all permissions for a document:

```python
from frappe.permissions import get_doc_permissions

perms = get_doc_permissions(doc)
# Returns: {'read': 1, 'write': 1, 'create': 0, 'delete': 0, ...}

perms = get_doc_permissions(doc, user="john@example.com")
```

## get_role_permissions()

Get permissions based on roles (without user permissions):

```python
from frappe.permissions import get_role_permissions

meta = frappe.get_meta("Sales Order")
perms = get_role_permissions(meta)
perms = get_role_permissions(meta, user="john@example.com")
```

## get_user_permissions()

Get user permissions:

```python
from frappe.permissions import get_user_permissions

# Get all user permissions for current user
user_perms = get_user_permissions()
# Returns: {"Territory": [{"doc": "North", "is_default": 1}], ...}

# Get for specific user
user_perms = get_user_permissions(user="john@example.com")
```

## frappe.get_roles()

Get roles of a user:

```python
# Roles of specific user
user_roles = frappe.get_roles("user@example.com")
# Returns: ['Guest', 'All', 'Sales User', 'System Manager']

# Roles of current user
my_roles = frappe.get_roles()

# Check specific role
if "System Manager" in frappe.get_roles():
    # User has System Manager role
    pass
```

## User Permission Management

```python
from frappe.permissions import (
    add_user_permission,
    remove_user_permission,
    clear_user_permissions_for_doctype
)

# Add
add_user_permission(
    doctype="Territory",           # What to restrict
    name="North",                  # Allowed value
    user="john@example.com",       # Which user
    ignore_permissions=True,
    applicable_for="Sales Order"   # Optional: only for this DocType
)

# Remove
remove_user_permission("Company", "My Company", "john@example.com")

# Clear all for a doctype
clear_user_permissions_for_doctype("Company", "john@example.com")
```

## Role Permission Management

```python
from frappe.permissions import add_permission, update_permission_property, remove_permission, reset_perms

# Add role permission to DocType
add_permission("Sales Order", "Sales User", permlevel=0)

# Update specific permission property
update_permission_property("Sales Order", "Sales User", 0, "write", 1)
update_permission_property("Sales Order", "Sales User", 0, "if_owner", 1)

# Remove permission
remove_permission("Sales Order", "Sales User", permlevel=0)

# Reset to DocType defaults
reset_perms("Sales Order")
```

## Document Sharing

```python
from frappe.share import add as add_share, remove as remove_share, get_shared

# Share document
add_share(
    doctype="Sales Order",
    name="SO-00001",
    user="jane@example.com",
    read=1,
    write=1,
    share=0
)

# Remove share
remove_share("Sales Order", "SO-00001", "jane@example.com")

# Get users with shared access
shared_with = get_shared("Sales Order", "SO-00001")
```

## Ignoring Permissions

```python
# Via flags
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.flags.ignore_permissions = True
doc.save()

# Or pass directly
doc.save(ignore_permissions=True)

# get_doc with permission check
doc = frappe.get_doc("Sales Order", "SO-00001", check_permission="read")
```

## get_list vs get_all

| Method | User Permissions | permission_query_conditions |
|--------|------------------|----------------------------|
| `frappe.get_list()` | Applied | Applied |
| `frappe.get_all()` | **Ignored** | **Ignored** |
| `frappe.db.get_list()` | Applied | Applied |
| `frappe.db.get_all()` | **Ignored** | **Ignored** |
