# Permission Anti-Patterns

> Reference for erpnext-permissions skill

---

## 1. Checking Role Instead of Permission

### ❌ Wrong

```python
def update_document(doc_name):
    # Bypasses entire permission system!
    if "Sales Manager" in frappe.get_roles():
        doc = frappe.get_doc("Sales Order", doc_name)
        doc.status = "Approved"
        doc.save(ignore_permissions=True)
```

### ✅ Correct

```python
def update_document(doc_name):
    doc = frappe.get_doc("Sales Order", doc_name)
    
    # Uses permission system
    if not doc.has_permission("write"):
        frappe.throw(_("No permission to edit"), frappe.PermissionError)
    
    doc.status = "Approved"
    doc.save()
```

### Why It Matters
- Role checks bypass User Permissions
- Role checks bypass has_permission hooks
- Role checks bypass if_owner restrictions
- Hard to audit and maintain

---

## 2. Hardcoding Administrator Bypass

### ❌ Wrong

```python
def sensitive_operation():
    if frappe.session.user == "Administrator":
        # Do anything without checks
        perform_operation()
    else:
        frappe.throw("Access Denied")
```

### ✅ Correct

```python
def sensitive_operation():
    # Check actual permission
    if not frappe.has_permission("Sensitive DocType", "write"):
        frappe.throw("Access Denied", frappe.PermissionError)
    
    perform_operation()
```

### Why It Matters
- Security risk if Administrator account compromised
- Other admin-level roles can't perform operation
- No audit trail of permission checks

---

## 3. Ignoring Permissions Without Documentation

### ❌ Wrong

```python
def process_order(order_name):
    doc = frappe.get_doc("Sales Order", order_name)
    doc.status = "Processed"
    doc.save(ignore_permissions=True)  # Why?
```

### ✅ Correct

```python
def process_order(order_name):
    """
    Process order via background job.
    
    Note: ignore_permissions used because this is a system-triggered
    action that runs as Administrator in the job queue.
    """
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Document the reason
    doc.add_comment("Info", "System: Auto-processed by scheduler")
    
    doc.flags.ignore_permissions = True
    doc.status = "Processed"
    doc.save()
```

### Why It Matters
- Makes code reviewable
- Documents security decisions
- Helps future maintenance

---

## 4. SQL Injection in Permission Query

### ❌ Wrong

```python
# hooks.py
permission_query_conditions = {
    "Customer": "myapp.permissions.customer_query"
}

# permissions.py
def customer_query(user):
    # VULNERABLE TO SQL INJECTION!
    return f"owner = '{user}'"
```

### ✅ Correct

```python
def customer_query(user):
    if not user:
        user = frappe.session.user
    
    # Always escape user input
    return f"`tabCustomer`.owner = {frappe.db.escape(user)}"
```

### Attack Example
```python
# Malicious user value: "' OR '1'='1"
# Results in: owner = '' OR '1'='1'  (returns all records!)
```

---

## 5. Forgetting Table Prefix in Query

### ❌ Wrong

```python
def my_query(user):
    # Ambiguous column reference
    return f"owner = {frappe.db.escape(user)}"
```

### ✅ Correct

```python
def my_query(user):
    # Explicit table prefix
    return f"`tabSales Order`.owner = {frappe.db.escape(user)}"
```

### Why It Matters
- Joins may have same column in multiple tables
- Results in SQL errors or wrong filtering
- Breaks when query complexity increases

---

## 6. Throwing Errors in has_permission Hook

### ❌ Wrong

```python
def my_permission(doc, ptype, user):
    if not is_allowed(doc, user):
        frappe.throw("You cannot access this!")  # DON'T DO THIS
```

### ✅ Correct

```python
def my_permission(doc, ptype, user):
    if not is_allowed(doc, user):
        return False  # Return False to deny
    
    return None  # Continue with standard checks
```

### Why It Matters
- Throwing interrupts permission evaluation
- Prevents proper error handling
- May expose sensitive information

---

## 7. Expecting get_all to Respect Permissions

### ❌ Wrong

```python
def get_user_orders():
    # User permissions NOT applied!
    orders = frappe.get_all("Sales Order", filters={"status": "Open"})
    return orders
```

### ✅ Correct

```python
def get_user_orders():
    # User permissions ARE applied
    orders = frappe.get_list("Sales Order", filters={"status": "Open"})
    return orders
```

### Key Difference
| Method | User Permissions | permission_query_conditions |
|--------|------------------|----------------------------|
| `get_list` | ✅ Applied | ✅ Applied |
| `get_all` | ❌ Ignored | ❌ Ignored |

---

## 8. Granting Perm Level 1+ Without Level 0

### ❌ Wrong

```json
{
  "permissions": [
    {
      "role": "HR User",
      "permlevel": 1,
      "read": 1,
      "write": 1
    }
  ]
}
```

**Error**: "Permission at level 0 must be set before higher levels are set"

### ✅ Correct

```json
{
  "permissions": [
    {
      "role": "HR User",
      "permlevel": 0,
      "read": 1
    },
    {
      "role": "HR User",
      "permlevel": 1,
      "read": 1,
      "write": 1
    }
  ]
}
```

---

## 9. Using db_set Without Understanding Implications

### ❌ Wrong

```python
def quick_update(doc_name, field, value):
    # Bypasses permissions AND validation
    frappe.db.set_value("DocType", doc_name, field, value)
```

### ✅ Correct

```python
def quick_update(doc_name, field, value):
    doc = frappe.get_doc("DocType", doc_name)
    
    # Check permission
    if not doc.has_permission("write"):
        frappe.throw(_("No permission"), frappe.PermissionError)
    
    # For system fields only, with documentation
    if field == "last_sync_time":
        # System field updated by background job
        frappe.db.set_value("DocType", doc_name, field, value, 
                           update_modified=False)
    else:
        doc.set(field, value)
        doc.save()
```

### db_set/set_value Bypasses
- Permission checks
- Validate methods
- Before/after save hooks
- Child table validation

---

## 10. Not Clearing Cache After Permission Changes

### ❌ Wrong

```python
def add_new_permission():
    from frappe.permissions import add_permission
    add_permission("Sales Order", "New Role")
    # Permission may not take effect immediately!
```

### ✅ Correct

```python
def add_new_permission():
    from frappe.permissions import add_permission
    add_permission("Sales Order", "New Role")
    frappe.clear_cache()  # Clear permission cache
```

---

## 11. Exposing Sensitive Data in Error Messages

### ❌ Wrong

```python
def get_confidential(doc_name):
    doc = frappe.get_doc("Employee", doc_name)
    if not doc.has_permission("read"):
        # Leaks information!
        frappe.throw(f"You cannot view {doc.employee_name}'s salary: {doc.salary}")
```

### ✅ Correct

```python
def get_confidential(doc_name):
    doc = frappe.get_doc("Employee", doc_name)
    if not doc.has_permission("read"):
        frappe.throw(_("Permission denied"), frappe.PermissionError)
```

---

## 12. Assuming has_permission Hook Can Grant Access

### ❌ Wrong (in most versions)

```python
def my_permission(doc, ptype, user):
    # This WON'T grant permission in most versions!
    if is_special_user(user):
        return True  # Has no effect!
    return None
```

### ✅ Correct Understanding

```python
def my_permission(doc, ptype, user):
    """
    IMPORTANT: This hook can only DENY permission.
    
    Returns:
        None - Continue with standard permission checks
        False - Deny permission
        True - No effect (does NOT grant permission in most versions)
    """
    if should_deny(doc, user):
        return False
    
    return None  # Let standard checks decide
```

---

## 13. Mixing User Permissions with Role Checks

### ❌ Wrong

```python
def get_my_customers():
    # Checks role but ignores user permissions
    if "Sales User" in frappe.get_roles():
        return frappe.get_all("Customer")  # Returns ALL customers!
```

### ✅ Correct

```python
def get_my_customers():
    # Uses get_list which respects user permissions
    return frappe.get_list(
        "Customer",
        fields=["name", "customer_name", "territory"]
    )
```

---

## Summary: Permission Checklist

Before deploying permission-related code:

- [ ] Using `has_permission()` instead of role checks?
- [ ] Using `get_list()` instead of `get_all()` for user queries?
- [ ] All SQL inputs escaped with `frappe.db.escape()`?
- [ ] Table prefixes used in query conditions?
- [ ] `ignore_permissions` usage documented?
- [ ] Permission cache cleared after changes?
- [ ] Error messages don't leak sensitive data?
- [ ] Level 0 granted before higher levels?
- [ ] Hooks return `None` or `False`, not throw errors?
- [ ] Tested with non-admin user account?
