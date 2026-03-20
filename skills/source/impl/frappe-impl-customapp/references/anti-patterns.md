# Anti-Patterns - Custom App Implementation

Common mistakes to avoid when building Frappe/ERPNext custom apps.

---

## 1. Build Configuration Errors

### ❌ Missing __version__ in __init__.py

```python
# my_app/my_app/__init__.py

# WRONG - Empty or missing __version__
# (file is empty or only has docstring)
```

```python
# CORRECT
__version__ = "1.0.0"
```

**Impact**: Build fails with cryptic flit error. App cannot be installed.

---

### ❌ Frappe/ERPNext in PyPI Dependencies

```toml
# WRONG - pyproject.toml
[project]
dependencies = [
    "frappe>=15.0.0",    # NOT ON PyPI!
    "erpnext>=15.0.0",   # NOT ON PyPI!
    "requests>=2.28.0"
]
```

```toml
# CORRECT
[project]
dependencies = [
    "requests>=2.28.0"   # Only PyPI packages here
]

[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
```

**Impact**: pip install fails because frappe/erpnext are not on PyPI.

---

### ❌ Missing dynamic = ["version"]

```toml
# WRONG
[project]
name = "my_app"
version = "1.0.0"  # Hardcoded version
```

```toml
# CORRECT
[project]
name = "my_app"
dynamic = ["version"]  # Read from __init__.py
```

**Impact**: Version in pyproject.toml and __init__.py can get out of sync.

---

## 2. Module Organization Errors

### ❌ Missing __init__.py in Module Directory

```
my_app/
└── my_module/
    └── doctype/           # Missing __init__.py!
        └── my_doctype/
```

```
# CORRECT
my_app/
└── my_module/
    ├── __init__.py        # Required!
    └── doctype/
        └── my_doctype/
```

**Impact**: Python cannot import from module; bench migrate fails.

---

### ❌ Module Not in modules.txt

```python
# Created doctype in "Reports" module
# But modules.txt only has:
# My App
```

```text
# CORRECT - modules.txt
My App
Reports
```

**Impact**: DocType doesn't appear in UI; "Module not found" errors.

---

### ❌ Module Name Mismatch

```text
# modules.txt
My Custom Reports

# Directory
my_app/my_reports/  # Should be my_custom_reports/!
```

**Rule**: `My Custom Reports` → `my_custom_reports/` (spaces → underscores, lowercase)

**Impact**: Module registration fails silently; DocTypes orphaned.

---

## 3. Patch Errors

### ❌ Patch Without Error Handling

```python
# WRONG
def execute():
    records = frappe.get_all("My DocType")
    for r in records:
        doc = frappe.get_doc("My DocType", r.name)
        doc.new_field = calculate_value(doc)
        doc.save()  # Could fail, leaves partial migration!
```

```python
# CORRECT
def execute():
    records = frappe.get_all("My DocType", pluck="name")
    
    for name in records:
        try:
            frappe.db.set_value(
                "My DocType",
                name,
                "new_field",
                calculate_value_sql(name),
                update_modified=False
            )
        except Exception as e:
            frappe.log_error(
                title=f"Patch failed for {name}",
                message=str(e)
            )
            continue
    
    frappe.db.commit()
```

**Impact**: Partial migration; data inconsistency; hard to re-run.

---

### ❌ Large Dataset Without Batching

```python
# WRONG - Loads ALL records into memory
def execute():
    records = frappe.get_all("Sales Invoice")  # Could be millions!
    for r in records:
        process(r)
```

```python
# CORRECT - Batch processing
def execute():
    batch_size = 1000
    offset = 0
    
    while True:
        records = frappe.get_all(
            "Sales Invoice",
            limit_page_length=batch_size,
            limit_start=offset
        )
        
        if not records:
            break
        
        for r in records:
            process(r)
        
        frappe.db.commit()  # Free memory after each batch
        offset += batch_size
```

**Impact**: Memory exhaustion; server crash; incomplete migration.

---

### ❌ Wrong Patch Timing Section

```ini
# WRONG - Trying to access field that doesn't exist yet
[pre_model_sync]
my_app.patches.populate_new_field  # new_field added in this release!
```

```ini
# CORRECT - Field exists after model sync
[post_model_sync]
my_app.patches.populate_new_field
```

**Impact**: "Column not found" error; patch fails.

---

### ❌ Not Checking If Patch Needed

```python
# WRONG - Runs every migrate even if not needed
def execute():
    # Always runs, even on fresh installs
    migrate_old_data()
```

```python
# CORRECT - Skip if not applicable
def execute():
    # Skip on fresh install (old column doesn't exist)
    if not frappe.db.has_column("My DocType", "old_field"):
        return
    
    # Skip if already migrated
    if frappe.db.count("My DocType", {"new_field": ["is", "set"]}):
        return
    
    migrate_old_data()
```

**Impact**: Wasted processing; potential data corruption on re-runs.

---

## 4. Fixture Errors

### ❌ Exporting All Records Without Filter

```python
# WRONG - Exports ALL Custom Fields, including from other apps!
fixtures = [
    "Custom Field"
]
```

```python
# CORRECT - Filter to YOUR app's customizations
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My App"]]
    }
]
```

**Impact**: Deploys other apps' customizations; fixture conflicts.

---

### ❌ Including Transactional Data

```python
# WRONG - Exports actual invoices!
fixtures = [
    "Sales Invoice"  # NO! This is transactional data
]
```

```python
# CORRECT - Only configuration DocTypes
fixtures = [
    "My Settings",      # Config only
    "My Category",      # Lookup data only
]
```

**Impact**: Data overwritten on migrate; privacy violations; bloated fixtures.

---

### ❌ Exporting User Data in Fixtures

```python
# WRONG
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["owner", "=", "Administrator"]]  # Don't filter by owner!
    }
]
```

**Impact**: Fixtures tied to specific user; fail on other installations.

---

### ❌ Missing Filter for DocType-Specific Fixtures

```python
# WRONG - Exports ALL workflows, including ERPNext's
fixtures = [
    "Workflow"
]
```

```python
# CORRECT
fixtures = [
    {
        "dt": "Workflow",
        "filters": [["document_type", "in", ["My DocType", "My Other DocType"]]]
    }
]
```

**Impact**: Overwrites standard ERPNext workflows; unexpected behavior.

---

## 5. Hook Errors

### ❌ Not Calling Super in extend_doctype_class (v16)

```python
# WRONG
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # Missing super()!
        self.custom_validation()
```

```python
# CORRECT
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # Call parent first!
        self.custom_validation()
```

**Impact**: Standard ERPNext validation skipped; data integrity issues.

---

### ❌ Infinite Loop in doc_events

```python
# WRONG - Triggers another validate!
def validate(doc, method):
    doc.custom_field = "value"
    doc.save()  # Triggers validate again → infinite loop!
```

```python
# CORRECT - Just set value, don't save
def validate(doc, method):
    doc.custom_field = "value"
    # doc.save() is called automatically after validate
```

**Impact**: Server hangs; maximum recursion error.

---

### ❌ Heavy Processing in Synchronous Hooks

```python
# WRONG - Blocks user while sending emails
def on_submit(doc, method):
    for customer in get_all_customers():
        send_email(customer, doc)  # Takes minutes!
```

```python
# CORRECT - Use background job
def on_submit(doc, method):
    frappe.enqueue(
        "my_app.tasks.notify_customers",
        doc_name=doc.name,
        queue="short"
    )
```

**Impact**: UI freezes; timeout errors; poor user experience.

---

## 6. Dependency Errors

### ❌ Missing required_apps in hooks.py

```python
# WRONG - App uses ERPNext DocTypes but doesn't declare dependency
required_apps = ["frappe"]

# Then in code:
from erpnext.selling.doctype.sales_order import SalesOrder  # Fails if ERPNext not installed!
```

```python
# CORRECT
required_apps = ["frappe", "erpnext"]
```

**Impact**: Import errors on installations without ERPNext.

---

### ❌ Circular Dependencies

```python
# my_app/hooks.py
required_apps = ["frappe", "other_app"]

# other_app/hooks.py
required_apps = ["frappe", "my_app"]  # Circular!
```

**Impact**: Installation fails; bench hangs.

---

## 7. Client-Side Errors

### ❌ Modifying Core ERPNext Files

```javascript
// WRONG - Editing erpnext/selling/doctype/sales_order/sales_order.js directly
// This will be overwritten on ERPNext upgrade!
```

```javascript
// CORRECT - Use doctype_js in hooks.py
// my_app/hooks.py
doctype_js = {
    "Sales Order": "public/js/sales_order.js"
}
```

**Impact**: Changes lost on upgrade; merge conflicts.

---

### ❌ Not Building After JS Changes

```bash
# Changed my_app/public/js/my_script.js
# But forgot to run:
bench build --app my_app
```

**Impact**: Old JS served from cache; "changes not working".

---

## 8. Permission Errors

### ❌ permission_query_conditions Blocking Administrators

```python
# WRONG - Even System Managers can't see records!
def get_permission_query_conditions(user):
    return f"owner = {frappe.db.escape(user)}"
```

```python
# CORRECT - Bypass for administrators
def get_permission_query_conditions(user):
    if "System Manager" in frappe.get_roles(user):
        return ""  # No restrictions
    
    return f"owner = {frappe.db.escape(user)}"
```

**Impact**: Admins can't see/debug records; support nightmare.

---

### ❌ SQL Injection in Permission Query

```python
# WRONG - User input not escaped!
def get_permission_query_conditions(user):
    return f"owner = '{user}'"  # SQL injection risk!
```

```python
# CORRECT - Always escape
def get_permission_query_conditions(user):
    return f"owner = {frappe.db.escape(user)}"
```

**Impact**: Security vulnerability; data breach risk.

---

## 9. Deployment Errors

### ❌ Hardcoded Site-Specific Values

```python
# WRONG
API_URL = "https://production.example.com/api"
ADMIN_EMAIL = "admin@mycompany.com"
```

```python
# CORRECT - Use settings DocType or site_config
settings = frappe.get_single("My Settings")
API_URL = settings.api_url

# Or from site_config.json
API_URL = frappe.conf.get("my_app_api_url")
```

**Impact**: Breaks on different environments; secrets in code.

---

### ❌ Not Testing on Fresh Site

```bash
# Developed on site with existing data
# Never tested fresh installation
bench --site newsite install-app my_app
# Fails because patch assumes existing data!
```

**Rule**: Always test your app installation on a fresh site.

**Impact**: Customers can't install; support tickets.

---

## 10. Version Compatibility Errors

### ❌ Using v16 Features Without Version Check

```python
# WRONG - Will fail on v14/v15
# hooks.py
extend_doctype_class = {
    "Sales Invoice": "my_app.overrides.sales_invoice.CustomSalesInvoice"
}
```

```python
# CORRECT - Support both v14/v15 and v16
# hooks.py

# v16+
extend_doctype_class = {
    "Sales Invoice": "my_app.overrides.sales_invoice.CustomSalesInvoice"
}

# v14/v15 fallback
doc_events = {
    "Sales Invoice": {
        "validate": "my_app.events.sales_invoice.validate"
    }
}
```

Or choose one version to support and document it clearly in README.

**Impact**: Installation fails on older Frappe versions.

---

## Quick Reference: Validation Checklist

Before releasing your app:

### Build
- [ ] `__version__` defined in `__init__.py`
- [ ] `dynamic = ["version"]` in pyproject.toml
- [ ] No frappe/erpnext in `[project].dependencies`
- [ ] Frappe deps in `[tool.bench.frappe-dependencies]`

### Modules
- [ ] All modules listed in `modules.txt`
- [ ] All module directories have `__init__.py`
- [ ] Module names match directory names (with underscores)

### Patches
- [ ] All patches have error handling
- [ ] Large datasets use batch processing
- [ ] Patches check if migration needed
- [ ] Correct section (pre/post model sync)

### Fixtures
- [ ] All fixtures have appropriate filters
- [ ] No transactional data in fixtures
- [ ] No user-specific filters

### Hooks
- [ ] `required_apps` includes all dependencies
- [ ] No infinite loops in event handlers
- [ ] Heavy processing uses background jobs
- [ ] v16 override classes call `super()`

### Permissions
- [ ] Administrators not blocked
- [ ] SQL properly escaped

### Testing
- [ ] Tested on fresh site installation
- [ ] Tested on target Frappe version(s)
- [ ] Assets built (`bench build`)
