# Anti-Patterns - Hooks Error Handling

Common mistakes to avoid when handling errors in Frappe/ERPNext hooks.py configurations.

---

## 1. Throwing Errors in permission_query_conditions

### ❌ WRONG

```python
def query_conditions(user):
    if not user:
        frappe.throw("User is required")  # BREAKS LIST VIEW!
    
    if "Sales User" not in frappe.get_roles(user):
        frappe.throw("Access denied")  # BREAKS LIST VIEW!
    
    return f"owner = '{user}'"
```

### ✅ CORRECT

```python
def query_conditions(user):
    try:
        if not user:
            user = frappe.session.user
        
        if "Sales Manager" in frappe.get_roles(user):
            return ""  # Full access
        
        return f"owner = {frappe.db.escape(user)}"
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Query Conditions Error")
        # Safe fallback
        return f"owner = {frappe.db.escape(frappe.session.user)}"
```

**Why**: Throwing in permission_query_conditions breaks list views completely.

---

## 2. Throwing Errors in has_permission

### ❌ WRONG

```python
def has_permission(doc, user=None, permission_type=None):
    if doc.status == "Locked":
        frappe.throw("Document is locked")  # BREAKS DOCUMENT ACCESS!
    
    if not user:
        frappe.throw("User required")  # DON'T DO THIS!
```

### ✅ CORRECT

```python
def has_permission(doc, user=None, permission_type=None):
    try:
        user = user or frappe.session.user
        
        if doc.status == "Locked" and permission_type == "write":
            return False  # Deny access silently
        
        return None  # Defer to default
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Has Permission Error")
        return None  # Safe fallback
```

**Why**: Throwing in has_permission breaks document access.

---

## 3. Missing frappe.db.commit() in Scheduler

### ❌ WRONG

```python
def daily_task():
    records = frappe.get_all("Item", limit=100)
    for record in records:
        frappe.db.set_value("Item", record.name, "synced", 1)
    
    # Missing commit - ALL CHANGES LOST!
```

### ✅ CORRECT

```python
def daily_task():
    records = frappe.get_all("Item", limit=100)
    for record in records:
        frappe.db.set_value("Item", record.name, "synced", 1)
    
    frappe.db.commit()  # REQUIRED!
```

**Why**: Scheduler tasks don't auto-commit. Without explicit commit, changes are lost.

---

## 4. Not Logging Errors in Scheduler

### ❌ WRONG

```python
def daily_sync():
    try:
        sync_records()
    except Exception:
        pass  # Silent failure - impossible to debug!
```

### ✅ CORRECT

```python
def daily_sync():
    try:
        sync_records()
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Daily Sync Error"
        )
```

**Why**: Scheduler has no user - logging is your ONLY debugging tool.

---

## 5. Not Calling super() in Override Class

### ❌ WRONG

```python
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # Missing super()! All parent validation skipped!
        self.custom_validation()
```

### ✅ CORRECT

```python
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # ALWAYS call parent first
        self.custom_validation()
```

**Why**: Skipping super() bypasses all parent class logic.

---

## 6. Unprotected extend_bootinfo

### ❌ WRONG

```python
def extend_boot(bootinfo):
    # If this fails, ENTIRE DESK BREAKS!
    settings = frappe.get_single("My Settings")
    bootinfo.my_config = settings.config
```

### ✅ CORRECT

```python
def extend_boot(bootinfo):
    try:
        if frappe.db.exists("My Settings", "My Settings"):
            settings = frappe.get_single("My Settings")
            bootinfo.my_config = settings.config or {}
        else:
            bootinfo.my_config = {}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Bootinfo Error")
        bootinfo.my_config = {}  # Safe fallback
```

**Why**: Errors in extend_bootinfo break the entire desk/page load.

---

## 7. Committing in doc_events

### ❌ WRONG

```python
def on_update(doc, method=None):
    frappe.db.set_value("Counter", "main", "count", 100)
    frappe.db.commit()  # BREAKS TRANSACTION!
```

### ✅ CORRECT

```python
def on_update(doc, method=None):
    frappe.db.set_value("Counter", "main", "count", 100)
    # No commit - Frappe handles it automatically
```

**Why**: Manual commits in doc_events break the transaction and can cause partial saves.

---

## 8. Not Isolating Non-Critical Operations

### ❌ WRONG

```python
def on_submit(doc, method=None):
    # If email fails, external sync never runs!
    send_notification_email(doc)
    sync_to_external_system(doc)
    update_dashboard_stats(doc)
```

### ✅ CORRECT

```python
def on_submit(doc, method=None):
    # Isolate each operation
    try:
        send_notification_email(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Email Error")
    
    try:
        sync_to_external_system(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Sync Error")
    
    try:
        update_dashboard_stats(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Stats Error")
```

**Why**: Independent operations should not block each other.

---

## 9. Breaking Other Apps in Wildcard Handler

### ❌ WRONG

```python
# hooks.py
doc_events = {
    "*": {
        "on_update": "myapp.audit.log_all"
    }
}

# audit.py
def log_all(doc, method=None):
    # Error here breaks ALL saves in the system!
    frappe.get_doc({
        "doctype": "Audit Log",
        "doc": doc.name
    }).insert()
```

### ✅ CORRECT

```python
def log_all(doc, method=None):
    # NEVER break other apps' saves
    try:
        # Skip audit doctypes
        if doc.doctype in ["Audit Log", "Error Log"]:
            return
        
        frappe.get_doc({
            "doctype": "Audit Log",
            "doc": doc.name
        }).insert(ignore_permissions=True)
        
    except Exception:
        # Log but never propagate
        frappe.log_error(
            frappe.get_traceback(),
            f"Audit log error: {doc.doctype}/{doc.name}"
        )
```

**Why**: Wildcard handlers run on ALL documents - errors affect the entire system.

---

## 10. No Limit in Scheduler Queries

### ❌ WRONG

```python
def daily_sync():
    # Could return millions of records!
    records = frappe.get_all("Item")
    for record in records:
        process(record)
```

### ✅ CORRECT

```python
def daily_sync():
    # Always limit!
    records = frappe.get_all("Item", limit=1000)
    for record in records:
        process(record)
    
    frappe.db.commit()
```

**Why**: Unbounded queries can cause memory issues and timeouts.

---

## 11. Swallowing Parent Errors in Override

### ❌ WRONG

```python
class CustomDoc(OriginalDoc):
    def validate(self):
        try:
            super().validate()
        except Exception:
            pass  # Swallowed parent validation!
        
        self.custom_check()
```

### ✅ CORRECT

```python
class CustomDoc(OriginalDoc):
    def validate(self):
        try:
            super().validate()
        except frappe.ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Parent Error")
            raise  # Re-raise unexpected errors too
        
        self.custom_check()
```

**Why**: Parent validation errors should propagate to the user.

---

## 12. SQL Injection in Permission Query

### ❌ WRONG

```python
def query_conditions(user):
    # SQL INJECTION VULNERABILITY!
    return f"owner = '{user}'"
```

### ✅ CORRECT

```python
def query_conditions(user):
    # Escape user input
    return f"owner = {frappe.db.escape(user)}"
```

**Why**: Unescaped user input allows SQL injection attacks.

---

## 13. Using frappe.throw() to Show Warnings

### ❌ WRONG

```python
def validate(doc, method=None):
    if doc.discount > 20:
        frappe.throw("High discount applied")  # Blocks save!
```

### ✅ CORRECT

```python
def validate(doc, method=None):
    if doc.discount > 20:
        frappe.msgprint(
            _("High discount applied - please verify"),
            indicator="orange"
        )
```

**Why**: Use `frappe.throw()` only for blocking errors, `frappe.msgprint()` for warnings.

---

## 14. Not Handling Multiple Handlers

### ❌ WRONG

```python
# Assumes only this handler runs
def validate(doc, method=None):
    doc.custom_calculated = calculate_value()
    # Other apps may have handlers that run after!
```

### ✅ CORRECT

```python
def validate(doc, method=None):
    # Be aware of handler chain
    doc.custom_calculated = calculate_value()
    
    # If you need to ensure values persist, use flags
    doc.flags.custom_calculated_by_myapp = True
```

**Why**: Multiple apps can register handlers - don't assume you're alone.

---

## 15. Heavy Operations in Sync Handler

### ❌ WRONG

```python
def on_update(doc, method=None):
    # Blocks the UI while running!
    sync_all_items()  # Takes 30 seconds
    generate_reports()  # Takes 20 seconds
```

### ✅ CORRECT

```python
def on_update(doc, method=None):
    # Queue heavy operations
    frappe.enqueue(
        "myapp.tasks.sync_all_items",
        queue="long",
        job_id=f"sync_{doc.name}"
    )
```

**Why**: Heavy operations in sync handlers make the UI unresponsive.

---

## Quick Checklist: Hook Review

Before deploying hooks:

- [ ] No `frappe.throw()` in permission hooks
- [ ] `frappe.db.commit()` in scheduler tasks
- [ ] `frappe.log_error()` for all caught exceptions
- [ ] `super()` called in override classes
- [ ] `try/except` wrapper in extend_bootinfo
- [ ] No `frappe.db.commit()` in doc_events
- [ ] Non-critical operations isolated
- [ ] Wildcard handlers never break saves
- [ ] Queries have limits in scheduler
- [ ] User input escaped in SQL
- [ ] Warnings use `msgprint()`, not `throw()`
- [ ] Heavy operations enqueued
