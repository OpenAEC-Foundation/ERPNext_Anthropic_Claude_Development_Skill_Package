# Permission Hooks Reference

## has_permission Hook

Add custom permission logic for a DocType.

### hooks.py Configuration

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.sales_order_permission"
}
```

### Handler Implementation

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

### Critical Rules for has_permission Hook

1. **Can only DENY** - `return False` denies, `return True/None` continues with standard checks
2. **Always receives doc** - Even in list views, called per document
3. **Performance impact** - Called frequently, keep logic fast
4. **Return None as default** - When in doubt, let standard checks decide

---

## permission_query_conditions Hook

Add WHERE clause conditions to `frappe.get_list()` queries.

### hooks.py Configuration

```python
# hooks.py
permission_query_conditions = {
    "ToDo": "myapp.permissions.todo_query"
}
```

### Handler Implementation

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

### Critical Rules for permission_query_conditions

1. **Only affects get_list** - Does NOT work with `frappe.get_all()`
2. **ALWAYS escape** - Use `frappe.db.escape()` for user input
3. **Return empty string** - `""` for no restrictions
4. **Valid SQL required** - Return must be valid WHERE clause
5. **Table prefix** - Use `` `tabDocType`.fieldname `` syntax

### Advanced Example: Hierarchical Permissions

```python
def territory_based_query(user):
    """Filter documents based on territory permissions."""
    if not user:
        user = frappe.session.user
    
    # System Manager sees everything
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # Get allowed territories
    territories = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "Territory"},
        pluck="for_value"
    )
    
    if not territories:
        return ""  # No restrictions if no user permissions
    
    # Build IN clause
    territory_list = ", ".join([frappe.db.escape(t) for t in territories])
    return f"`tabSales Order`.territory IN ({territory_list})"
```

---

## Combining Hooks

Both hooks can be used together for complete permission control:

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.check_sales_order_permission"
}

permission_query_conditions = {
    "Sales Order": "myapp.permissions.sales_order_query_conditions"
}
```

### Workflow

1. **List view** → `permission_query_conditions` filters the query
2. **Per document** → `has_permission` checks individual access
3. **Both** → Standard role/user permissions still apply

---

## Version Differences

| Feature | v14 | v15 |
|---------|-----|-----|
| has_permission return True | No effect | Can grant permission |
| Debug parameter | `verbose` | `debug` |
| Desk User role | Not available | Automatic role |

---

## Debugging Permission Hooks

```python
# Enable debug output in has_permission
frappe.has_permission("Sales Order", "read", doc, debug=True)

# View permission logs
print(frappe.local.permission_debug_log)

# Log in custom hook
def my_permission_hook(doc, ptype, user):
    frappe.logger().debug(f"Permission check: {doc.name}, {ptype}, {user}")
    return None
```
