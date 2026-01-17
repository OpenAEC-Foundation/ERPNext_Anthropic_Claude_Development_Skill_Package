# Permission Hooks Reference

> Reference for erpnext-permissions skill

---

## has_permission Hook

### Purpose

Add custom permission logic for a DocType. Can only **deny** permission, not grant it.

### Configuration

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.sales_order_permission",
    "Customer": "myapp.permissions.customer_permission"
}
```

### Function Signature

```python
def my_permission_check(doc, ptype, user):
    """
    Custom permission check.
    
    Args:
        doc: Document object being checked
        ptype: Permission type (read, write, create, delete, etc.)
        user: User being checked
    
    Returns:
        None: No effect, continue standard checks
        False: DENY permission
        True: No effect in most versions (can grant in v15+)
    """
    pass
```

### Examples

#### Deny Access to Cancelled Documents

```python
# myapp/permissions.py
def sales_order_permission(doc, ptype, user):
    """Deny non-managers access to cancelled orders."""
    if doc.docstatus == 2:  # Cancelled
        if "Sales Manager" not in frappe.get_roles(user):
            return False
    return None
```

#### Time-Based Access Control

```python
def time_based_permission(doc, ptype, user):
    """Deny write access outside business hours."""
    if ptype == "write":
        hour = frappe.utils.now_datetime().hour
        if hour < 9 or hour > 18:
            if "System Manager" not in frappe.get_roles(user):
                return False
    return None
```

#### Hierarchical Approval

```python
def approval_permission(doc, ptype, user):
    """Only allow department head to approve high-value orders."""
    if ptype == "write" and doc.status == "Pending Approval":
        if doc.grand_total > 100000:
            if user != doc.department_head:
                return False
    return None
```

### Critical Rules

1. **Can only deny** - Returning `True` has no effect in most versions
2. **Return None by default** - To continue with standard checks
3. **Don't throw errors** - Return `False` instead
4. **Performance matters** - Called frequently, keep it fast
5. **Check ptype** - Don't apply write logic to read checks

---

## permission_query_conditions Hook

### Purpose

Add WHERE clause conditions to `frappe.get_list()` queries.

### Configuration

```python
# hooks.py
permission_query_conditions = {
    "ToDo": "myapp.permissions.todo_query",
    "Sales Order": "myapp.permissions.sales_order_query"
}
```

### Function Signature

```python
def my_query_conditions(user):
    """
    Return SQL WHERE clause fragment.
    
    Args:
        user: User making the query (can be None)
    
    Returns:
        str: Valid SQL WHERE clause fragment, or empty string
    """
    pass
```

### Examples

#### Owner-Based Filter

```python
# myapp/permissions.py
def todo_query(user):
    """Show only ToDos owned by or assigned by user."""
    if not user:
        user = frappe.session.user
    
    return """
        (`tabToDo`.owner = {user} OR `tabToDo`.assigned_by = {user})
    """.format(user=frappe.db.escape(user))
```

#### Role-Based Filter

```python
def sales_order_query(user):
    """Filter Sales Orders based on user role."""
    if not user:
        user = frappe.session.user
    
    roles = frappe.get_roles(user)
    
    # Managers see all
    if "Sales Manager" in roles:
        return ""
    
    # Regular users see only their own
    return "`tabSales Order`.owner = {user}".format(
        user=frappe.db.escape(user)
    )
```

#### Territory-Based Filter

```python
def customer_query(user):
    """Filter customers by user's allowed territories."""
    if not user:
        user = frappe.session.user
    
    # Get user's territories from user permissions
    territories = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "Territory"},
        pluck="for_value"
    )
    
    if not territories:
        return ""  # No restriction
    
    # Build IN clause
    territory_list = ", ".join([frappe.db.escape(t) for t in territories])
    return "`tabCustomer`.territory IN ({})".format(territory_list)
```

#### Date-Based Filter

```python
def quotation_query(user):
    """Only show quotations from last 90 days for regular users."""
    if not user:
        user = frappe.session.user
    
    if "Sales Manager" in frappe.get_roles(user):
        return ""
    
    cutoff = frappe.utils.add_days(frappe.utils.today(), -90)
    return "`tabQuotation`.creation >= '{}'".format(cutoff)
```

### Critical Rules

1. **Only affects get_list** - Does NOT affect `frappe.get_all()`
2. **Always escape input** - Use `frappe.db.escape()`
3. **Return empty string for no filter** - Not `None`
4. **Use backticks for identifiers** - `` `tabDocType`.fieldname ``
5. **Handle None user** - Check and default to session user

---

## get_list vs get_all Behavior

| Method | User Permissions | permission_query_conditions |
|--------|------------------|----------------------------|
| `frappe.get_list()` | ✅ Applied | ✅ Applied |
| `frappe.get_all()` | ❌ Ignored | ❌ Ignored |
| `frappe.db.get_list()` | ✅ Applied | ✅ Applied |
| `frappe.db.get_all()` | ❌ Ignored | ❌ Ignored |

### When to Use Which

```python
# For user-facing queries - respects permissions
docs = frappe.get_list("Sales Order", filters={"status": "Draft"})

# For system queries - bypasses permissions
docs = frappe.get_all("Sales Order", filters={"status": "Draft"})
```

---

## Combining Hooks

### Example: Complete Permission System

```python
# hooks.py
has_permission = {
    "Project": "myapp.permissions.project_permission"
}

permission_query_conditions = {
    "Project": "myapp.permissions.project_query"
}
```

```python
# myapp/permissions.py

def project_permission(doc, ptype, user):
    """
    Custom permission check for individual projects.
    """
    if not user:
        user = frappe.session.user
    
    # Managers have full access
    if "Projects Manager" in frappe.get_roles(user):
        return None
    
    # Check if user is project member
    is_member = frappe.db.exists(
        "Project User",
        {"parent": doc.name, "user": user}
    )
    
    if not is_member:
        return False
    
    return None


def project_query(user):
    """
    Filter project list to only show accessible projects.
    """
    if not user:
        user = frappe.session.user
    
    # Managers see all
    if "Projects Manager" in frappe.get_roles(user):
        return ""
    
    # Others see only projects they're members of
    return """
        EXISTS (
            SELECT 1 FROM `tabProject User`
            WHERE `tabProject User`.parent = `tabProject`.name
            AND `tabProject User`.user = {user}
        )
    """.format(user=frappe.db.escape(user))
```

---

## Hook Registration Order

1. Hooks from all installed apps are collected
2. Order follows app installation order in `apps.txt`
3. For `has_permission`: ALL hooks must pass (any False = denied)
4. For `permission_query_conditions`: conditions are AND-ed together

---

## Debugging Hooks

### Log Permission Checks

```python
def sales_order_permission(doc, ptype, user):
    frappe.logger().debug(
        f"Permission check: {doc.doctype} {doc.name}, "
        f"ptype={ptype}, user={user}"
    )
    # ... permission logic ...
```

### Test Query Conditions

```python
# In console
from myapp.permissions import sales_order_query
print(sales_order_query("john@example.com"))
# Output: `tabSales Order`.owner = 'john@example.com'
```

---

## Common Mistakes

### ❌ SQL Injection

```python
# WRONG
def bad_query(user):
    return f"owner = '{user}'"  # Vulnerable!

# CORRECT
def good_query(user):
    return f"owner = {frappe.db.escape(user)}"
```

### ❌ Forgetting Table Prefix

```python
# WRONG
def bad_query(user):
    return f"owner = {frappe.db.escape(user)}"  # Ambiguous!

# CORRECT
def good_query(user):
    return f"`tabSales Order`.owner = {frappe.db.escape(user)}"
```

### ❌ Throwing Errors in Hook

```python
# WRONG
def bad_permission(doc, ptype, user):
    if not allowed:
        frappe.throw("Not allowed!")  # Don't do this!

# CORRECT
def good_permission(doc, ptype, user):
    if not allowed:
        return False  # Just return False
```
