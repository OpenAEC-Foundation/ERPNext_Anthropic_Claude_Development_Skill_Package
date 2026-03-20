# Hook Anti-Patterns

Common mistakes and their solutions when implementing hooks.

---

## Anti-Pattern 1: Committing in doc_events

### ❌ Wrong
```python
def on_update(doc, method=None):
    create_related_record(doc)
    frappe.db.commit()  # BREAKS TRANSACTION!
```

### Why It's Wrong
- Frappe wraps document operations in transactions
- Manual commit breaks the transaction boundary
- If later code fails, partial changes are saved
- Can cause data inconsistency

### ✅ Correct
```python
def on_update(doc, method=None):
    create_related_record(doc)
    # Frappe commits automatically after all handlers complete
```

---

## Anti-Pattern 2: Modifying doc After on_update

### ❌ Wrong
```python
def on_update(doc, method=None):
    doc.status = "Processed"  # Change is LOST!
```

### Why It's Wrong
- on_update runs AFTER the document is saved
- Changes to `doc` object are not persisted
- Document is already in database

### ✅ Correct
```python
def on_update(doc, method=None):
    frappe.db.set_value(
        doc.doctype, 
        doc.name, 
        "status", 
        "Processed"
    )
```

Or use flags to do it in validate:
```python
def validate(doc, method=None):
    if doc.flags.mark_processed:
        doc.status = "Processed"  # This WILL be saved
```

---

## Anti-Pattern 3: Scheduler Task with Arguments

### ❌ Wrong
```python
# hooks.py
scheduler_events = {
    "daily": ["myapp.tasks.process_records"]
}

# tasks.py
def process_records(doctype, filters):  # WRONG - args not passed!
    pass
```

### Why It's Wrong
- Scheduler calls tasks with NO arguments
- Function signature must be empty
- Arguments are silently dropped

### ✅ Correct
```python
def process_records():
    # Fetch data INSIDE the function
    doctype = "Sales Invoice"
    filters = {"status": "Draft"}
    records = frappe.get_all(doctype, filters=filters)
    for record in records:
        process(record)
```

---

## Anti-Pattern 4: Heavy Task in Default Queue

### ❌ Wrong
```python
scheduler_events = {
    "daily": ["myapp.tasks.sync_all_data"]  # May take 20 minutes
}
```

### Why It's Wrong
- Default queue timeout is 5 minutes
- Task gets killed mid-execution
- Data may be left in inconsistent state

### ✅ Correct
```python
scheduler_events = {
    "daily_long": ["myapp.tasks.sync_all_data"]  # 25 min timeout
}
```

Or split into smaller tasks:
```python
scheduler_events = {
    "hourly": ["myapp.tasks.sync_batch"]  # Process in chunks
}

def sync_batch():
    # Process only 100 records per run
    records = get_unsynced_records(limit=100)
    for record in records:
        sync_record(record)
```

---

## Anti-Pattern 5: Forgetting super() in Override

### ❌ Wrong
```python
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        self.my_validation()  # Core validation SKIPPED!
```

### Why It's Wrong
- Parent class validation is completely skipped
- Core business logic doesn't run
- GL entries, stock updates may fail
- Breaks ERPNext functionality

### ✅ Correct
```python
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # ALWAYS call parent first
        self.my_validation()
```

---

## Anti-Pattern 6: Using get_all with permission_query

### ❌ Wrong
```python
# hooks.py
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_query"
}

# Somewhere in code
invoices = frappe.db.get_all("Sales Invoice")  # NOT FILTERED!
```

### Why It's Wrong
- `permission_query_conditions` only works with `get_list`
- `get_all` bypasses permission filters entirely
- Users may see data they shouldn't

### ✅ Correct
```python
# Use get_list for permission-filtered results
invoices = frappe.db.get_list("Sales Invoice")

# get_all is for system/admin operations only
# (when you intentionally want to bypass permissions)
```

---

## Anti-Pattern 7: Sensitive Data in bootinfo

### ❌ Wrong
```python
def extend_boot(bootinfo):
    bootinfo.api_secret = frappe.conf.api_secret  # EXPOSED!
    bootinfo.db_password = frappe.conf.db_password  # DISASTER!
```

### Why It's Wrong
- bootinfo is sent to browser
- Anyone can see it in Developer Tools
- Credentials are exposed to all users

### ✅ Correct
```python
def extend_boot(bootinfo):
    # Only PUBLIC configuration
    bootinfo.my_app = {
        "feature_enabled": True,
        "public_api_url": "https://api.example.com"
    }
    # Never include: passwords, secrets, tokens, internal URLs
```

---

## Anti-Pattern 8: Fixtures Without Filters

### ❌ Wrong
```python
fixtures = [
    "Custom Field",  # ALL custom fields from ALL apps!
    "Role"  # ALL roles!
]
```

### Why It's Wrong
- Exports customizations from OTHER apps
- Creates conflicts on import
- May overwrite other apps' settings
- Huge fixture files

### ✅ Correct
```python
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My App"]]
    },
    {
        "dt": "Role",
        "filters": [["name", "like", "MyApp%"]]
    }
]
```

---

## Anti-Pattern 9: No Migrate After Hooks Change

### ❌ Wrong
```bash
# Edit hooks.py
# Expect changes to work immediately
```

### Why It's Wrong
- Scheduler events are registered at migrate
- Permission hooks are cached
- Changes don't take effect

### ✅ Correct
```bash
# After ANY hooks.py change:
bench --site sitename migrate

# For scheduler specifically:
bench --site sitename scheduler enable
```

---

## Anti-Pattern 10: Infinite Loop with on_change

### ❌ Wrong
```python
def on_change(doc, method=None):
    # This triggers on_change again → infinite loop!
    frappe.db.set_value(doc.doctype, doc.name, "modified", now())
```

### Why It's Wrong
- `on_change` fires on ANY change, including `db_set_value`
- Setting a value triggers on_change again
- Infinite recursion until stack overflow

### ✅ Correct
```python
def on_change(doc, method=None):
    # Check flag to prevent recursion
    if doc.flags.in_change_handler:
        return
    
    doc.flags.in_change_handler = True
    frappe.db.set_value(
        doc.doctype, doc.name, "modified", now(),
        update_modified=False  # Prevents triggering on_change
    )
```

Or use on_update instead (doesn't fire on db_set_value).

---

## Anti-Pattern 11: has_permission Trying to Grant Access

### ❌ Wrong
```python
def has_permission(doc, user=None, permission_type=None):
    if is_special_user(user):
        return True  # Trying to GRANT access - doesn't work!
```

### Why It's Wrong
- `has_permission` can only DENY access
- Returning True doesn't grant additional permissions
- User must already have base permission

### ✅ Correct
```python
def has_permission(doc, user=None, permission_type=None):
    # Can only DENY
    if should_deny_access(doc, user):
        return False
    
    # Return None to use default permission system
    return None

# To grant additional access, use Role Permissions Manager
# or create proper permission rules
```

---

## Anti-Pattern 12: Wrong Handler Signature for Rename

### ❌ Wrong
```python
def before_rename(doc, method=None):  # Missing required args!
    pass
```

### Why It's Wrong
- Rename handlers receive additional arguments
- Missing args cause errors or unexpected behavior

### ✅ Correct
```python
def before_rename(doc, method, old, new, merge):
    """
    Args:
        doc: Document object
        method: "before_rename"
        old: Old name
        new: New name
        merge: Whether this is a merge operation
    """
    if new.startswith("_"):
        frappe.throw("Names cannot start with underscore")
```

---

## Anti-Pattern 13: Multiple Apps Overriding Same DocType

### ❌ Problem
```python
# app1/hooks.py
override_doctype_class = {
    "Sales Invoice": "app1.CustomSI"
}

# app2/hooks.py (installed later)
override_doctype_class = {
    "Sales Invoice": "app2.CustomSI"  # WINS, app1 ignored!
}
```

### Why It's Wrong (V14/V15)
- Only the last installed app's override works
- app1's customizations are completely ignored
- No warning or error

### ✅ Correct (V16+)
```python
# Use extend_doctype_class instead
extend_doctype_class = {
    "Sales Invoice": ["app1.SIMixin"]  # Both work!
}

extend_doctype_class = {
    "Sales Invoice": ["app2.SIMixin"]  # Both active!
}
```

### ✅ Workaround (V14/V15)
```python
# app2 must inherit from app1's override
from app1.overrides import CustomSI as App1SI

class CustomSI(App1SI):  # Chain the overrides
    def validate(self):
        super().validate()
        self.app2_validation()
```

---

## Anti-Pattern 14: Not Handling None User

### ❌ Wrong
```python
def si_query_conditions(user):
    roles = frappe.get_roles(user)  # Error if user is None!
```

### Why It's Wrong
- `user` parameter can be None
- Causes errors in background jobs
- Breaks permission checks

### ✅ Correct
```python
def si_query_conditions(user):
    if not user:
        user = frappe.session.user
    
    roles = frappe.get_roles(user)
```

---

## Anti-Pattern 15: Blocking UI with Heavy Validation

### ❌ Wrong
```python
def validate(doc, method=None):
    # Heavy operation blocks form save
    for item in doc.items:
        response = call_external_api(item)  # Slow!
        validate_response(response)
```

### Why It's Wrong
- User waits while external API is called
- Network issues cause save failures
- Poor user experience

### ✅ Correct
```python
def validate(doc, method=None):
    # Quick validation only
    if not all(item.item_code for item in doc.items):
        frappe.throw("All items must have item code")

def on_submit(doc, method=None):
    # Queue heavy operations
    frappe.enqueue(
        "myapp.tasks.validate_with_external",
        queue="long",
        doc_name=doc.name
    )
```

---

## Summary Table

| Anti-Pattern | Risk | Solution |
|--------------|------|----------|
| Commit in doc_events | Data inconsistency | Let Frappe commit |
| Modify doc in on_update | Lost changes | Use db_set_value |
| Scheduler args | Silent failure | No args, fetch inside |
| Heavy task in default | Timeout kill | Use _long queue |
| Missing super() | Broken core | Always call super() first |
| get_all with perms | Data leak | Use get_list |
| Secrets in bootinfo | Security breach | Only public config |
| Fixtures no filter | App conflicts | Always filter by module |
| No migrate | Changes ignored | Always bench migrate |
| on_change loop | Stack overflow | Use flags or on_update |
| Grant via has_permission | Doesn't work | Can only deny |
| Wrong rename signature | Errors | Include all 5 args |
| Multiple overrides | One ignored | Use extend (V16) |
| None user | Errors | Default to session.user |
| Heavy validation | Poor UX | Queue heavy tasks |
