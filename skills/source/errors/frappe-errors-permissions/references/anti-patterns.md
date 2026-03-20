# Anti-Patterns - Permission Error Handling

Common mistakes to avoid when handling permission errors in Frappe/ERPNext.

---

## 1. Throwing Errors in has_permission Hook

### ❌ WRONG

```python
def has_permission(doc, ptype, user):
    if doc.status == "Locked":
        frappe.throw("Document is locked")  # BREAKS DOCUMENT ACCESS!
    
    if not check_access(user):
        frappe.throw("Access denied")  # DON'T DO THIS!
```

### ✅ CORRECT

```python
def has_permission(doc, ptype, user):
    try:
        if doc.get("status") == "Locked" and ptype != "read":
            return False  # Deny silently
        
        if not check_access(user):
            return False  # Deny silently
        
        return None  # Defer to default
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Permission Error")
        return None  # Safe fallback
```

**Why**: Throwing in has_permission breaks all document access, including read operations.

---

## 2. Returning True in has_permission

### ❌ WRONG

```python
def has_permission(doc, ptype, user):
    if user == doc.owner:
        return True  # WRONG - hooks can't grant!
    return None
```

### ✅ CORRECT

```python
def has_permission(doc, ptype, user):
    if user == doc.owner:
        return None  # Defer - let standard system grant
    
    # Can only deny, not grant
    if not meets_criteria(doc, user):
        return False
    
    return None
```

**Why**: has_permission hooks can only **deny** access, never **grant** it. Returning True has no effect.

---

## 3. SQL Injection in permission_query_conditions

### ❌ WRONG

```python
def query_conditions(user):
    # SQL INJECTION VULNERABILITY!
    return f"owner = '{user}'"
    
    # Also wrong:
    return f"territory = '{territory}'"
```

### ✅ CORRECT

```python
def query_conditions(user):
    # Always escape user input
    return f"owner = {frappe.db.escape(user)}"
    
    # For multiple values
    escaped = ", ".join([frappe.db.escape(t) for t in territories])
    return f"territory IN ({escaped})"
```

**Why**: Unescaped input allows SQL injection attacks that can bypass all permission controls.

---

## 4. Throwing in permission_query_conditions

### ❌ WRONG

```python
def query_conditions(user):
    if not user:
        frappe.throw("User required")  # BREAKS LIST VIEW!
    
    if "Sales User" not in frappe.get_roles(user):
        frappe.throw("Access denied")  # BREAKS LIST VIEW!
```

### ✅ CORRECT

```python
def query_conditions(user):
    try:
        if not user:
            user = frappe.session.user
        
        if "Sales User" not in frappe.get_roles(user):
            return "1=0"  # Return no records
        
        return f"owner = {frappe.db.escape(user)}"
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Query Error")
        return f"owner = {frappe.db.escape(frappe.session.user)}"
```

**Why**: Throwing in query conditions breaks the entire list view for all users.

---

## 5. Using Role Checks Instead of Permission API

### ❌ WRONG

```python
@frappe.whitelist()
def sensitive_action():
    # Checking roles directly - misses permission nuances!
    if "Manager" not in frappe.get_roles():
        frappe.throw("Access denied")
```

### ✅ CORRECT

```python
@frappe.whitelist()
def sensitive_action():
    # Use permission API - respects full permission system
    frappe.only_for(["Manager"])
    
    # Or for document-level:
    frappe.has_permission("DocType", "write", throw=True)
```

**Why**: Role checks bypass user permissions, sharing, and custom permission hooks.

---

## 6. Using get_all Instead of get_list

### ❌ WRONG

```python
@frappe.whitelist()
def get_user_orders():
    # get_all bypasses ALL permission checks!
    return frappe.get_all("Sales Order", 
        filters={"customer": customer})
```

### ✅ CORRECT

```python
@frappe.whitelist()
def get_user_orders():
    # get_list respects permissions
    return frappe.get_list("Sales Order",
        filters={"customer": customer})
```

**Why**: `frappe.get_all()` bypasses user permissions and permission_query_conditions.

---

## 7. No Error Handling in Permission Hooks

### ❌ WRONG

```python
def has_permission(doc, ptype, user):
    # If this crashes, document access breaks!
    territories = frappe.get_all("User Permission",
        filters={"user": user})
    
    if doc.territory not in territories:
        return False
```

### ✅ CORRECT

```python
def has_permission(doc, ptype, user):
    try:
        territories = frappe.get_all("User Permission",
            filters={"user": user, "allow": "Territory"},
            pluck="for_value"
        ) or []
        
        doc_territory = doc.get("territory")
        if doc_territory and territories and doc_territory not in territories:
            return False
        
        return None
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Permission Error")
        return None  # Defer to standard on error
```

**Why**: Unhandled exceptions in permission hooks break all document access.

---

## 8. Missing Permission Check in API

### ❌ WRONG

```python
@frappe.whitelist()
def update_salary(employee, new_salary):
    # No permission check - anyone can update!
    frappe.db.set_value("Employee", employee, "salary", new_salary)
```

### ✅ CORRECT

```python
@frappe.whitelist()
def update_salary(employee, new_salary):
    # Check permission first
    frappe.has_permission("Employee", "write", employee, throw=True)
    
    # Additional role check for sensitive operation
    frappe.only_for(["HR Manager"])
    
    frappe.db.set_value("Employee", employee, "salary", new_salary)
```

**Why**: Whitelisted methods are callable by any logged-in user - explicit permission checks are required.

---

## 9. Exposing Sensitive Info in Permission Errors

### ❌ WRONG

```python
def has_permission(doc, ptype, user):
    allowed_users = ["admin@company.com", "ceo@company.com"]
    
    if user not in allowed_users:
        # Exposes internal user list!
        frappe.throw(f"Only {allowed_users} can access this")
```

### ✅ CORRECT

```python
def has_permission(doc, ptype, user):
    allowed_users = get_allowed_users()
    
    if user not in allowed_users:
        return False  # Silent denial
    
    return None
```

**Why**: Error messages can leak sensitive information about system configuration.

---

## 10. Not Logging Permission Denials

### ❌ WRONG

```python
def has_permission(doc, ptype, user):
    if doc.is_confidential:
        if user not in allowed_list:
            return False  # Silent denial, no audit trail
```

### ✅ CORRECT

```python
def has_permission(doc, ptype, user):
    if doc.get("is_confidential"):
        if user not in get_allowed_list(doc):
            # Log for security audit
            log_access_denied(doc, user, ptype)
            return False
    return None

def log_access_denied(doc, user, ptype):
    try:
        frappe.get_doc({
            "doctype": "Security Log",
            "event": "Access Denied",
            "user": user,
            "document": doc.name,
            "permission_type": ptype
        }).insert(ignore_permissions=True)
    except Exception:
        pass  # Never break permission for logging
```

**Why**: Security audits require logging of denied access attempts.

---

## 11. Ignoring ignore_permissions Flag

### ❌ WRONG

```python
def process_documents():
    # Using ignore_permissions without justification
    docs = frappe.get_all("Confidential Doc")  # Already bypasses
    
    for doc in docs:
        d = frappe.get_doc("Confidential Doc", doc.name)
        d.flags.ignore_permissions = True  # Why?
        d.save()
```

### ✅ CORRECT

```python
def process_documents():
    """
    System process that requires bypassing permissions.
    
    WHY: This is a scheduled cleanup task that needs to process
    all documents regardless of the current user context.
    
    SECURITY: Only runs as system user in scheduler.
    """
    if frappe.session.user != "Administrator":
        frappe.throw("This function can only be called by system")
    
    docs = frappe.get_all("Doc", filters={"status": "Pending"})
    
    for doc in docs:
        d = frappe.get_doc("Doc", doc.name)
        # Document WHY permissions are bypassed
        d.flags.ignore_permissions = True  # System cleanup task
        d.process()
        d.save()
```

**Why**: Using ignore_permissions without documentation creates security risks.

---

## 12. Checking Permissions After Action

### ❌ WRONG

```python
@frappe.whitelist()
def delete_document(name):
    # Delete first, check later - WRONG!
    frappe.delete_doc("Important Doc", name)
    
    if not frappe.has_permission("Important Doc", "delete"):
        frappe.throw("No permission")  # Too late!
```

### ✅ CORRECT

```python
@frappe.whitelist()
def delete_document(name):
    # Check permission FIRST
    if not frappe.has_permission("Important Doc", "delete", name):
        frappe.throw(
            _("You don't have permission to delete this document"),
            exc=frappe.PermissionError
        )
    
    # Now safe to delete
    frappe.delete_doc("Important Doc", name)
```

**Why**: Always check permissions before performing actions, not after.

---

## 13. Inconsistent Permission Messages

### ❌ WRONG

```python
# Different messages for same error
frappe.throw("Access denied")
frappe.throw("Permission denied")
frappe.throw("You cannot do this")
frappe.throw("Unauthorized")
```

### ✅ CORRECT

```python
# Consistent, translatable messages
from frappe import _

frappe.throw(
    _("You don't have permission to {0} {1}").format(ptype, doctype),
    exc=frappe.PermissionError
)
```

**Why**: Consistent messages improve UX and make translation easier.

---

## 14. Blocking All Access on Partial Permission

### ❌ WRONG

```python
def has_permission(doc, ptype, user):
    # Blocks READ even when only WRITE should be blocked
    if doc.status == "Locked":
        return False  # Can't even view locked docs!
```

### ✅ CORRECT

```python
def has_permission(doc, ptype, user):
    if doc.get("status") == "Locked":
        # Only block modifications, allow reading
        if ptype in ["write", "delete", "submit", "cancel"]:
            return False
    return None
```

**Why**: Users often need to read documents they can't modify.

---

## 15. Not Handling None Values Safely

### ❌ WRONG

```python
def has_permission(doc, ptype, user):
    # Crashes if territory is None
    if doc.territory not in allowed_territories:
        return False
```

### ✅ CORRECT

```python
def has_permission(doc, ptype, user):
    territory = doc.get("territory") if hasattr(doc, "get") else getattr(doc, "territory", None)
    
    if territory and allowed_territories:
        if territory not in allowed_territories:
            return False
    
    return None
```

**Why**: Document fields can be None, causing crashes in permission hooks.

---

## Quick Checklist: Permission Implementation Review

Before deploying permission code:

- [ ] No `frappe.throw()` in has_permission hooks
- [ ] No `frappe.throw()` in permission_query_conditions
- [ ] Never return `True` in has_permission (only `False` or `None`)
- [ ] All SQL uses `frappe.db.escape()`
- [ ] All hooks wrapped in try/except
- [ ] `frappe.get_list()` used for user queries (not `get_all`)
- [ ] Permission checks before actions (not after)
- [ ] `ignore_permissions` usage documented
- [ ] Access denials logged for audit
- [ ] Consistent, translated error messages
- [ ] None values handled safely
- [ ] Read permission preserved when blocking write
