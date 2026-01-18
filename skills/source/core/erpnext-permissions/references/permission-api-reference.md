# Permission API Reference

> Reference for erpnext-permissions skill

---

## Core Permission Checks

### frappe.has_permission()

Main permission check function.

```python
frappe.has_permission(
    doctype,                    # Required: DocType name
    ptype="read",              # Permission type
    doc=None,                  # Document name or object
    user=None,                 # User (default: current)
    throw=False,               # Raise error if no permission
    debug=False,               # Print debug logs
    parent_doctype=None        # For checking child table permissions
)
# Returns: bool
```

**Examples**:

```python
# Check DocType-level permission
frappe.has_permission("Sales Order", "create")

# Check document-level permission
frappe.has_permission("Sales Order", "write", "SO-00001")
frappe.has_permission("Sales Order", "write", doc=doc_object)

# Check for specific user
frappe.has_permission("Sales Order", "read", user="john@example.com")

# Throw error if no permission
frappe.has_permission("Sales Order", "delete", throw=True)

# Debug mode
frappe.has_permission("Sales Order", "read", debug=True)
```

---

### Document.has_permission()

Check permission on document instance.

```python
doc.has_permission(
    permtype="read",    # Permission type
    debug=False,        # Print debug logs  
    user=None           # User (default: current)
)
# Returns: bool
```

**Examples**:

```python
doc = frappe.get_doc("Sales Order", "SO-00001")

# Basic check
if doc.has_permission("write"):
    doc.status = "Draft"
    doc.save()

# Debug output
doc.has_permission("read", debug=True)

# Check for other user
doc.has_permission("read", user="jane@example.com")
```

**Note**: Respects `doc.flags.ignore_permissions` flag.

---

### Document.check_permission()

Raises error if no permission.

```python
doc.check_permission(
    permtype="read",    # Permission type
    permlevel=None      # Optional: specific perm level
)
# Returns: None (raises frappe.PermissionError if denied)
```

**Example**:

```python
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.check_permission("write")  # Raises error if no permission
# Only reaches here if permission exists
doc.status = "Closed"
doc.save()
```

---

## Permission Query Functions

### get_doc_permissions()

Get all permissions for a document.

```python
from frappe.permissions import get_doc_permissions

get_doc_permissions(
    doc,            # Document object
    user=None,      # User (default: current)
    ptype=None      # Optional: specific permission type
)
# Returns: dict {"read": 1, "write": 1, "create": 0, ...}
```

**Example**:

```python
from frappe.permissions import get_doc_permissions

doc = frappe.get_doc("Sales Order", "SO-00001")
perms = get_doc_permissions(doc)
# {'read': 1, 'write': 1, 'create': 0, 'delete': 0, 'submit': 0, ...}

perms = get_doc_permissions(doc, user="john@example.com")
```

---

### get_role_permissions()

Get permissions based on roles (without user permissions).

```python
from frappe.permissions import get_role_permissions

get_role_permissions(
    doctype_meta,   # DocType meta object
    user=None       # User (default: current)
)
# Returns: dict {"read": 1, "write": 0, ...}
```

**Example**:

```python
from frappe.permissions import get_role_permissions

meta = frappe.get_meta("Sales Order")
perms = get_role_permissions(meta)
perms = get_role_permissions(meta, user="john@example.com")
```

---

## User Permission Functions

### get_user_permissions()

Get all user permissions for a user.

```python
from frappe.permissions import get_user_permissions

get_user_permissions(user=None)
# Returns: dict by doctype
```

**Example**:

```python
from frappe.permissions import get_user_permissions

user_perms = get_user_permissions()
# {
#   "Company": [{"doc": "My Company", "is_default": 1}],
#   "Territory": [{"doc": "North", "is_default": 0}]
# }

user_perms = get_user_permissions(user="john@example.com")
```

---

### add_user_permission()

Add user permission programmatically.

```python
from frappe.permissions import add_user_permission

add_user_permission(
    doctype,              # DocType to restrict
    name,                 # Value to allow
    user,                 # User to apply restriction
    ignore_permissions=False,
    applicable_for=None,  # Apply only to specific DocType
    is_default=0,         # Use as default value
    hide_descendants=0    # For tree doctypes
)
```

**Example**:

```python
from frappe.permissions import add_user_permission

# Basic user permission
add_user_permission("Company", "My Company", "john@example.com")

# With options
add_user_permission(
    "Territory",
    "North",
    "john@example.com",
    ignore_permissions=True,
    applicable_for="Sales Order",
    is_default=1
)
```

---

### remove_user_permission()

Remove specific user permission.

```python
from frappe.permissions import remove_user_permission

remove_user_permission(doctype, name, user)
```

**Example**:

```python
from frappe.permissions import remove_user_permission

remove_user_permission("Company", "My Company", "john@example.com")
```

---

### clear_user_permissions_for_doctype()

Clear all user permissions for a doctype.

```python
from frappe.permissions import clear_user_permissions_for_doctype

clear_user_permissions_for_doctype(doctype, user=None)
```

**Example**:

```python
from frappe.permissions import clear_user_permissions_for_doctype

# Clear for specific user
clear_user_permissions_for_doctype("Company", "john@example.com")

# Clear for all users
clear_user_permissions_for_doctype("Company")
```

---

## Role Permission Management

### add_permission()

Add role permission to DocType.

```python
from frappe.permissions import add_permission

add_permission(doctype, role, permlevel=0)
```

**Example**:

```python
from frappe.permissions import add_permission

add_permission("Sales Order", "Custom Role", permlevel=0)
```

---

### update_permission_property()

Update specific permission property.

```python
from frappe.permissions import update_permission_property

update_permission_property(doctype, role, permlevel, ptype, value)
```

**Example**:

```python
from frappe.permissions import update_permission_property

update_permission_property("Sales Order", "Sales User", 0, "write", 1)
update_permission_property("Sales Order", "Sales User", 0, "delete", 0)
update_permission_property("Sales Order", "Sales User", 0, "if_owner", 1)
```

---

### remove_permission()

Remove role permission.

```python
from frappe.permissions import remove_permission

remove_permission(doctype, role, permlevel=0)
```

---

### reset_perms()

Reset permissions to DocType defaults.

```python
from frappe.permissions import reset_perms

reset_perms(doctype)
```

---

## Sharing Functions

### frappe.share.add()

Share document with user.

```python
from frappe.share import add as add_share

add_share(
    doctype,
    name,
    user,
    read=1,
    write=0,
    share=0,
    everyone=0,
    notify=0
)
```

**Example**:

```python
from frappe.share import add as add_share

add_share(
    "Sales Order",
    "SO-00001",
    "jane@example.com",
    read=1,
    write=1,
    share=0
)
```

---

### frappe.share.remove()

Remove document share.

```python
from frappe.share import remove as remove_share

remove_share(doctype, name, user)
```

---

### frappe.share.get_shared()

Get users with shared access.

```python
from frappe.share import get_shared

users = get_shared(doctype, name)
# Returns list of users
```

---

## Utility Functions

### frappe.get_roles()

Get roles for user.

```python
roles = frappe.get_roles(user=None)
# Returns: list of role names
```

**Example**:

```python
# Current user's roles
roles = frappe.get_roles()
# ['Guest', 'All', 'Sales User', 'System Manager']

# Specific user's roles
roles = frappe.get_roles("john@example.com")

# Check specific role
if "Sales Manager" in frappe.get_roles():
    pass
```

---

### frappe.only_for()

Restrict function to specific roles.

```python
@frappe.whitelist()
def my_function():
    frappe.only_for(["Sales Manager", "System Manager"])
    # Only reaches here if user has one of these roles
```

---

## Bypass Permissions

### ignore_permissions Flag

```python
# On document
doc.flags.ignore_permissions = True
doc.save()

# On save method
doc.save(ignore_permissions=True)
```

### Set User Temporarily

```python
original_user = frappe.session.user
frappe.set_user("Administrator")
# ... privileged operations ...
frappe.set_user(original_user)
```

### System Flags

```python
# Bypass many permission checks
frappe.flags.in_setup_wizard = True
frappe.flags.in_install = True
frappe.flags.in_migrate = True
```

**Warning**: Use sparingly and document why.
