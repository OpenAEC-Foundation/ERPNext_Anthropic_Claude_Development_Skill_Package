# Research Document: Frappe Permissions System

> **Project**: ERPNext/Frappe Skills Package  
> **Phase**: 3.2 - erpnext-permissions  
> **Date**: 2026-01-17  
> **Status**: Research Complete

---

## 1. Overview

Frappe Framework provides a comprehensive, multi-layered permission system that controls access to documents, fields, and actions. The system combines:

1. **Role-based permissions** - What a user CAN do based on assigned roles
2. **User permissions** - Restricting WHICH documents a user can access
3. **Permission levels (Perm Levels)** - Field-level access control
4. **Permission hooks** - Programmatic permission customization

---

## 2. Core Concepts

### 2.1 Users and Roles

A **User** represents an authenticated person who can perform actions in the system. Each user can have multiple **Roles** assigned.

A **Role** defines what actions a user can perform on a DocType. Permissions are always granted through roles, never directly to users.

```python
# Check user's roles
user_roles = frappe.get_roles("user@example.com")
# Returns: ['Guest', 'All', 'Sales User', 'System Manager']

# Check if current user has a specific role
if "System Manager" in frappe.get_roles():
    # User has System Manager role
    pass
```

### 2.2 Automatic Roles

Frappe has built-in automatic roles that are assigned based on user type:

| Role | Assigned To | Purpose |
|------|-------------|---------|
| `Guest` | Everyone (including unauthenticated) | Catch-all for public access |
| `All` | All registered users | Catch-all for authenticated users |
| `Administrator` | Only `Administrator` user | Full system access |
| `Desk User` | Users with `user_type = "System User"` (v15+) | Desk access |

**Important**: These roles are automatically hidden in the Role Permission Manager but can be used in DocType permissions.

---

## 3. Permission Types

### 3.1 Standard Permission Types

| Permission | Description | Applies To |
|------------|-------------|------------|
| `read` | View document | All DocTypes |
| `write` | Edit document | All DocTypes |
| `create` | Create new document | All DocTypes |
| `delete` | Delete document | All DocTypes |
| `submit` | Submit document | Submittable DocTypes only |
| `cancel` | Cancel submitted document | Submittable DocTypes only |
| `amend` | Amend cancelled document | Submittable DocTypes only |
| `report` | View in Report Builder | All DocTypes |
| `export` | Export to Excel/CSV | All DocTypes |
| `import` | Import via Data Import | All DocTypes |
| `share` | Share document with others | All DocTypes |
| `print` | Print document/generate PDF | All DocTypes |
| `email` | Send email for document | All DocTypes |
| `select` | Select in Link field (v14+) | All DocTypes |

### 3.2 Special Permission Options

| Option | Description |
|--------|-------------|
| `if_owner` | Permission applies only if user created the document |
| `set_user_permissions` | Can apply user permissions for other users |

### 3.3 Custom Permission Types (v16+, Experimental)

You can create custom permission types for granular action control:

```python
# Check custom permission in code
if frappe.has_permission(doc, "approve"):
    # User can approve this document
    approve_document(doc)
else:
    frappe.throw("Not permitted", frappe.PermissionError)
```

**Setup**:
1. Enable developer mode
2. Create Permission Type record
3. Assign via Role Permission Manager
4. Export as fixture

---

## 4. DocType Permissions Configuration

### 4.1 Permissions Table in DocType

Permissions are configured in the DocType's `permissions` table:

```json
{
  "permissions": [
    {
      "role": "Sales User",
      "permlevel": 0,
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 0,
      "submit": 0,
      "cancel": 0,
      "amend": 0,
      "report": 1,
      "export": 1,
      "import": 0,
      "share": 1,
      "print": 1,
      "email": 1,
      "if_owner": 0
    }
  ]
}
```

### 4.2 Permission Levels (Perm Levels)

Perm Levels group fields for separate permission control:

- **Level 0**: Default level, all fields start here
- **Levels 1-9**: Custom groupings for restricted fields

**Example**: Hide salary field from regular users:
1. Set `permlevel = 1` on the salary field
2. Grant Level 1 read/write to HR Manager role only

```python
# In Customize Form or DocType JSON
{
    "fieldname": "salary",
    "fieldtype": "Currency",
    "permlevel": 1  # Only roles with Level 1 access can see/edit
}
```

**Critical Rule**: Level 0 permission MUST be granted before higher levels. You cannot grant Level 1 without Level 0.

---

## 5. User Permissions

### 5.1 Concept

User Permissions restrict access to specific documents based on Link field values. They work WITH role permissions, not instead of them.

**Example**: Sales User can access ALL Sales Orders (role permission), but User Permission restricts them to only Sales Orders where `territory = "North"`.

### 5.2 Configuration

```python
# Programmatically add user permission
from frappe.permissions import add_user_permission

add_user_permission(
    doctype="Territory",           # What to restrict
    name="North",                  # Allowed value
    user="john@example.com",       # Which user
    ignore_permissions=True,
    applicable_for="Sales Order"   # Optional: only apply to this DocType
)
```

### 5.3 User Permission Options

| Option | Description |
|--------|-------------|
| `is_default` | Use this value as default in new documents |
| `apply_to_all_doctypes` | Apply restriction to all DocTypes with this Link |
| `applicable_for` | Apply only to specific DocType |
| `hide_descendants` | For tree DocTypes, don't include child records |

### 5.4 Ignore User Permissions

On specific fields in Customize Form, check "Ignore User Permissions" to exempt that field from user permission restrictions.

---

## 6. Permission API

### 6.1 frappe.has_permission()

The main permission check function:

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

### 6.2 Document.has_permission()

Check permissions on a document instance:

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

### 6.3 Document.check_permission()

Raises `frappe.PermissionError` if no permission:

```python
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.check_permission("write")  # Raises error if no permission
# Continue only if permission exists
```

### 6.4 get_doc_permissions()

Get all permissions for a document:

```python
from frappe.permissions import get_doc_permissions

perms = get_doc_permissions(doc)
# Returns: {'read': 1, 'write': 1, 'create': 0, 'delete': 0, ...}

perms = get_doc_permissions(doc, user="john@example.com")
```

### 6.5 get_role_permissions()

Get permissions based on roles (without user permissions):

```python
from frappe.permissions import get_role_permissions

meta = frappe.get_meta("Sales Order")
perms = get_role_permissions(meta)
perms = get_role_permissions(meta, user="john@example.com")
```

### 6.6 User Permission Queries

```python
from frappe.permissions import get_user_permissions

# Get all user permissions for current user
user_perms = get_user_permissions()
# Returns: {"Territory": [{"doc": "North", "is_default": 1}], ...}

# Get for specific user
user_perms = get_user_permissions(user="john@example.com")
```

---

## 7. Permission Hooks

### 7.1 has_permission Hook

Add custom permission logic for a DocType:

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.sales_order_permission"
}
```

```python
# myapp/permissions.py
def sales_order_permission(doc, ptype, user):
    """
    Custom permission check for Sales Order.
    
    Args:
        doc: The document being checked
        ptype: Permission type (read, write, etc.)
        user: User being checked
    
    Returns:
        None: No effect, continue with standard checks
        False: Deny permission
        True: In v15+, can grant permission (check version)
    
    IMPORTANT: In most versions, returning True has NO effect.
    This hook can only DENY permission, not grant it.
    """
    # Example: Deny access to cancelled orders for non-managers
    if doc.docstatus == 2 and "Sales Manager" not in frappe.get_roles(user):
        return False
    
    # Return None to continue with standard permission checks
    return None
```

**Critical**: The `has_permission` hook can only **deny** permission (by returning `False`), not grant it. Returning `True` or `None` continues with standard checks.

### 7.2 permission_query_conditions Hook

Add WHERE clause conditions to `frappe.get_list()` queries:

```python
# hooks.py
permission_query_conditions = {
    "ToDo": "myapp.permissions.todo_query"
}
```

```python
# myapp/permissions.py
def todo_query(user):
    """
    Returns SQL WHERE clause fragment for filtering ToDo list.
    
    Args:
        user: User making the query (can be None)
    
    Returns:
        str: Valid SQL WHERE clause fragment
    """
    if not user:
        user = frappe.session.user
    
    # Only show ToDos owned by or assigned by user
    return """
        (`tabToDo`.owner = {user} OR `tabToDo`.assigned_by = {user})
    """.format(user=frappe.db.escape(user))
```

**Important**: 
- This only affects `frappe.get_list()`, NOT `frappe.get_all()`
- Always escape user input with `frappe.db.escape()`
- Return empty string `""` for no restrictions

### 7.3 Difference: get_list vs get_all

| Method | User Permissions | permission_query_conditions |
|--------|------------------|----------------------------|
| `frappe.get_list()` | Applied | Applied |
| `frappe.get_all()` | **Ignored** | **Ignored** |
| `frappe.db.get_list()` | Applied | Applied |
| `frappe.db.get_all()` | **Ignored** | **Ignored** |

---

## 8. Programmatic Permission Management

### 8.1 Adding Permissions

```python
from frappe.permissions import add_permission, update_permission_property

# Add role permission to DocType
add_permission("Sales Order", "Sales User", permlevel=0)

# Update specific permission property
update_permission_property("Sales Order", "Sales User", 0, "write", 1)
update_permission_property("Sales Order", "Sales User", 0, "if_owner", 1)
```

### 8.2 Removing Permissions

```python
from frappe.permissions import remove_permission

remove_permission("Sales Order", "Sales User", permlevel=0)
```

### 8.3 Resetting Permissions

```python
from frappe.permissions import reset_perms

# Reset to DocType defaults
reset_perms("Sales Order")
```

### 8.4 User Permission Management

```python
from frappe.permissions import (
    add_user_permission,
    remove_user_permission,
    clear_user_permissions_for_doctype
)

# Add
add_user_permission("Company", "My Company", "john@example.com")

# Remove
remove_user_permission("Company", "My Company", "john@example.com")

# Clear all for a doctype
clear_user_permissions_for_doctype("Company", "john@example.com")
```

---

## 9. Ignoring Permissions

### 9.1 In Code

```python
# Using ignore_permissions flag
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.flags.ignore_permissions = True
doc.save()

# Or pass to save directly
doc.save(ignore_permissions=True)

# For database operations
frappe.db.set_value("Sales Order", "SO-00001", "status", "Closed",
                    update_modified=False)  # db operations ignore perms by default

# For get_doc with permission check
doc = frappe.get_doc("Sales Order", "SO-00001", check_permission="read")
```

### 9.2 Running as Administrator

```python
# Temporarily run as Administrator
frappe.set_user("Administrator")
# ... do privileged operations ...
frappe.set_user(original_user)

# Or use flags
frappe.flags.in_setup_wizard = True  # Bypasses many checks
```

**Warning**: Always restore the original user and use sparingly.

---

## 10. Sharing

### 10.1 Document Sharing

Share specific documents with users who don't have role permission:

```python
from frappe.share import add as add_share, remove as remove_share

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
```

### 10.2 Check Shared Permissions

```python
from frappe.share import get_shared

# Get users who have shared access
shared_with = get_shared("Sales Order", "SO-00001")
```

---

## 11. Version Differences

### 11.1 v14 vs v15 Changes

| Feature | v14 | v15 |
|---------|-----|-----|
| `select` permission | Introduced | Available |
| `Desk User` role | Not available | Automatic role |
| Permission debugging | `verbose` parameter | `debug` parameter |
| has_permission return | True has no effect | May grant permission |

### 11.2 v16 Features (Experimental)

- Custom Permission Types
- Data Masking (mask sensitive fields based on permissions)
- Enhanced `extend_doctype_class` for permission overrides

---

## 12. Common Patterns

### 12.1 Check Permission Before Action

```python
@frappe.whitelist()
def approve_order(order_name):
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Check custom permission
    if not frappe.has_permission(doc.doctype, "write", doc):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Check additional business logic
    if "Approver" not in frappe.get_roles():
        frappe.throw(_("Only Approvers can approve orders"))
    
    doc.status = "Approved"
    doc.save()
```

### 12.2 Owner-Only Access Pattern

```python
# In DocType permissions, set if_owner = 1 for a role

# Or check programmatically
def can_edit(doc):
    if doc.owner == frappe.session.user:
        return True
    if "Manager" in frappe.get_roles():
        return True
    return False
```

### 12.3 Hierarchical Permission Check

```python
def check_territory_access(doc, user=None):
    """Check if user has access to document's territory."""
    if not user:
        user = frappe.session.user
    
    user_territories = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "Territory"},
        pluck="for_value"
    )
    
    if not user_territories:
        return True  # No restrictions
    
    return doc.territory in user_territories
```

---

## 13. Anti-Patterns

### 13.1 ❌ Checking Role Instead of Permission

```python
# ❌ WRONG - Bypasses permission system
if "Sales Manager" in frappe.get_roles():
    doc.save()

# ✅ CORRECT - Uses permission system
if frappe.has_permission(doc.doctype, "write", doc):
    doc.save()
```

### 13.2 ❌ Hardcoding Administrator Bypass

```python
# ❌ WRONG - Security risk
if frappe.session.user == "Administrator":
    # do anything

# ✅ CORRECT - Check actual permission
if frappe.has_permission("DocType", "write"):
    # proceed
```

### 13.3 ❌ Ignoring Permissions Without Reason

```python
# ❌ WRONG - No justification
doc.save(ignore_permissions=True)

# ✅ CORRECT - Documented reason
# System-generated update that requires elevated privileges
doc.flags.ignore_permissions = True
doc.db_set("system_field", value, update_modified=False)
```

### 13.4 ❌ SQL Injection in Permission Query

```python
# ❌ WRONG - SQL injection vulnerability
def my_query(user):
    return f"owner = '{user}'"  # NEVER do this

# ✅ CORRECT - Escaped input
def my_query(user):
    return f"owner = {frappe.db.escape(user)}"
```

---

## 14. Debugging Permissions

### 14.1 Debug Mode

```python
# Enable debug output
frappe.has_permission("Sales Order", "read", doc, debug=True)

# View permission logs
print(frappe.local.permission_debug_log)
```

### 14.2 Permitted Documents Report

Use the "Permitted Documents for User" report in ERPNext to see which documents a user can access.

### 14.3 Common Permission Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Not permitted" on create | Missing `create` permission for role | Add via Role Permission Manager |
| Can't see documents | User permission restricting | Check User Permissions list |
| Field not visible | Perm Level mismatch | Grant role access to that level |
| permission_query not working | Using get_all instead of get_list | Switch to get_list |

---

## 15. Best Practices

1. **Always use permission API** - Don't bypass with direct role checks
2. **Grant minimum necessary** - Follow principle of least privilege
3. **Use User Permissions for data isolation** - Not custom code
4. **Document permission requirements** - In DocType or README
5. **Test with non-admin users** - Verify actual permission behavior
6. **Escape all user input** - In permission_query_conditions
7. **Prefer returning None** - In has_permission hooks
8. **Clear cache after changes** - `frappe.clear_cache()`

---

## 16. Source References

### Official Documentation
- https://docs.frappe.io/framework/user/en/basics/users-and-permissions
- https://docs.frappe.io/framework/permission-types
- https://docs.frappe.io/erpnext/user/manual/en/user-permissions

### GitHub Source Code
- https://github.com/frappe/frappe/blob/develop/frappe/permissions.py
- https://github.com/frappe/frappe/blob/develop/frappe/model/document.py
- https://github.com/frappe/frappe/blob/develop/frappe/core/doctype/user_permission/

---

## 17. Skill Structure Planning

### Reference Files Needed (5)
1. `permission-types-reference.md` - All permission types and options
2. `permission-api-reference.md` - API methods with signatures
3. `permission-hooks-reference.md` - Hook patterns and examples
4. `examples.md` - Complete working examples
5. `anti-patterns.md` - Common mistakes and solutions

### SKILL.md Sections
1. Overview & Architecture
2. Quick Reference Tables
3. Essential API Methods
4. Hook Integration
5. Decision Tree (when to use what)
6. Version Considerations

---

*Document complete: ~680 lines*
*Ready for skill creation phase*
