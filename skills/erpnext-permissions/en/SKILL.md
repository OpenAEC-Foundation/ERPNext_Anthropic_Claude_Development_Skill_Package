---
name: erpnext-permissions
description: Frappe/ERPNext permission system - role-based permissions, user permissions, perm levels, permission hooks, and permission API. Use for DocType permission configuration, programmatic permission checks, user permission restrictions, permission_query_conditions, has_permission hooks, and field-level access control via perm levels.
---

# ERPNext Permissions

## Architecture Overview

Frappe's permission system consists of four layers:

1. **Role Permissions** - What a role CAN do on a DocType
2. **User Permissions** - WHICH documents a user can access (data filtering)
3. **Perm Levels** - Field-level access control
4. **Permission Hooks** - Programmatic permission customization

### Permission Flow

```
User Request
    ↓
Role Permission Check (does role have read/write/etc?)
    ↓
User Permission Filter (which documents?)
    ↓
Perm Level Check (which fields?)
    ↓
Permission Hooks (custom logic)
    ↓
Access Granted/Denied
```

## Quick Reference

### Permission Check

```python
# Basic check
if frappe.has_permission("Sales Order", "write"):
    # proceed

# With document
if frappe.has_permission("Sales Order", "write", doc=doc):
    doc.save()

# Throw if no permission
frappe.has_permission("Sales Order", "write", throw=True)

# Check on document instance
doc.check_permission("write")  # Raises PermissionError if no access
```

### Role Check

```python
# Get roles
roles = frappe.get_roles()  # Current user
roles = frappe.get_roles("user@example.com")

# Check specific role
if "Sales Manager" in frappe.get_roles():
    pass
```

### User Permissions

```python
from frappe.permissions import add_user_permission, remove_user_permission

# Restrict user to specific value
add_user_permission("Territory", "North", "john@example.com")

# Remove restriction
remove_user_permission("Territory", "North", "john@example.com")
```

## Essential API Methods

| Method | Purpose |
|--------|---------|
| `frappe.has_permission(doctype, ptype, doc)` | Check permission |
| `doc.has_permission(ptype)` | Check on document |
| `doc.check_permission(ptype)` | Check + throw |
| `frappe.get_roles(user)` | Get user roles |
| `add_user_permission()` | Add data restriction |
| `frappe.get_list()` | Query WITH permissions |
| `frappe.get_all()` | Query WITHOUT permissions |

**Critical**: `get_list` applies user permissions, `get_all` does NOT.

## Permission Hooks

### has_permission Hook

Add custom permission logic:

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
        None - Continue with standard checks
        False - Deny permission
    """
    if doc.docstatus == 2 and "Manager" not in frappe.get_roles(user):
        return False
    return None
```

**CRITICAL**: This hook can only DENY permission (return False), not GRANT it.

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

**CRITICAL**: ALWAYS use `frappe.db.escape()` for user input!

## Perm Levels (Field-Level Access)

Group fields for separate access control:

1. Set `permlevel` on field (1-9)
2. Grant role access to that level via Role Permission Manager

```python
# DocType field definition
{
    "fieldname": "salary",
    "permlevel": 1  # Only roles with level 1 access can see this
}
```

**Rule**: Level 0 MUST be granted before higher levels can be granted.

## Decision Tree

### Which Method to Use?

```
Need to filter data for a user?
├─ Yes → User Permissions + get_list()
└─ No, restrict action
   ├─ Standard CRUD → Role Permissions in DocType
   ├─ Custom business logic → has_permission hook
   └─ Hide field → Perm Levels
```

### get_list vs get_all

```
Is this a user-facing query?
├─ Yes → frappe.get_list() (permissions applied)
└─ No, system operation → frappe.get_all() (no filter)
```

## Version Differences

| Feature | v14 | v15+ |
|---------|-----|------|
| `select` permission | Introduced | Available |
| `Desk User` role | Not available | Automatic |
| has_permission return True | No effect | Can grant permission |
| Debug parameter | `verbose` | `debug` |

## Critical Rules

1. **ALWAYS** use `frappe.has_permission()`, NOT hardcoded role checks
2. **NEVER** use `get_all()` for user-facing queries (ignores permissions)
3. **ALWAYS** use `frappe.db.escape()` in permission_query_conditions
4. **ALWAYS** clear cache after permission changes: `frappe.clear_cache()`
5. **DOCUMENT** why you use `ignore_permissions=True`

## Reference Files

- [Permission Types Reference](references/permission-types-reference.md) - All permission types and options
- [Permission API Reference](references/permission-api-reference.md) - Complete API documentation
- [Permission Hooks Reference](references/permission-hooks-reference.md) - Hook patterns and examples
- [Examples](references/examples.md) - Working code examples
- [Anti-Patterns](references/anti-patterns.md) - Common mistakes and solutions
