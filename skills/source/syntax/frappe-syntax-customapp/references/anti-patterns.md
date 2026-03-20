# Anti-Patterns and Common Mistakes

> Mistakes to avoid when developing Frappe custom apps.

---

## Build Configuration Anti-Patterns

### ❌ Missing __version__

```python
# WRONG - no version
# my_custom_app/__init__.py
pass
```

```python
# ✅ CORRECT
# my_custom_app/__init__.py
__version__ = "0.0.1"
```

**Result**: Flit build fails, app cannot be installed.

---

### ❌ Frappe in pyproject.toml Dependencies

```toml
# WRONG - frappe is not on PyPI
[project]
dependencies = [
    "frappe>=15.0.0",
    "erpnext>=15.0.0",
]
```

```toml
# ✅ CORRECT - use tool.bench section
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
```

**Result**: pip install fails because frappe is not on PyPI.

---

### ❌ Package Name Mismatch

```
# WRONG - pyproject.toml says "my_custom_app" but directory is "my-custom-app"
apps/my-custom-app/        # Directory with hyphen
├── pyproject.toml         # name = "my_custom_app" (underscore)
```

**Result**: Package not found, import errors.

---

### ❌ Wrong hooks.py Location

```
# WRONG - hooks.py in wrong directory
apps/my_custom_app/hooks.py         # Too high level

# ✅ CORRECT
apps/my_custom_app/my_custom_app/hooks.py  # In inner package
```

**Result**: Hooks not loaded, no events trigger.

---

## Module Anti-Patterns

### ❌ Module Not Registered

```
# modules.txt - FORGOT to add new_module
My Custom App
# New Module  <- missing!
```

**Result**: DocTypes in unregistered modules don't work correctly.

---

### ❌ Missing __init__.py

```
# WRONG - no __init__.py
my_custom_app/
└── new_module/
    └── doctype/           # ImportError!
```

```
# ✅ CORRECT - __init__.py in every directory
my_custom_app/
└── new_module/
    ├── __init__.py        # Empty file
    └── doctype/
        └── __init__.py
```

**Result**: Python cannot import the module.

---

## Patches Anti-Patterns

### ❌ No Error Handling

```python
# WRONG - crashes without logging
def execute():
    frappe.db.sql("DELETE FROM `tabOldTable`")
```

```python
# ✅ CORRECT - with error handling
def execute():
    try:
        frappe.db.sql("DELETE FROM `tabOldTable`")
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(title="Delete Old Table Failed")
        raise
```

**Result**: Patch fails without diagnostic information.

---

### ❌ Wrong Model Sync Section

```python
# WRONG - pre_model_sync but needs new field
# patches.txt: [pre_model_sync] myapp.patches.v1_0.fill_new_field

def execute():
    # new_field doesn't exist yet!
    frappe.db.sql("UPDATE `tabCustomer` SET new_field = 'value'")
```

```python
# ✅ CORRECT - in post_model_sync
# patches.txt: [post_model_sync] myapp.patches.v1_0.fill_new_field

def execute():
    frappe.db.sql("UPDATE `tabCustomer` SET new_field = 'value'")
```

**Result**: SQL error because column doesn't exist.

---

### ❌ Large Dataset Without Batching

```python
# WRONG - can run out of memory
def execute():
    all_records = frappe.get_all("HugeDocType", fields=["*"])  # 1M+ records
    for record in all_records:
        process(record)
```

```python
# ✅ CORRECT - batch processing
def execute():
    batch_size = 1000
    offset = 0
    
    while True:
        records = frappe.get_all(
            "HugeDocType",
            fields=["name"],
            limit_page_length=batch_size,
            limit_start=offset
        )
        if not records:
            break
            
        for record in records:
            process(record)
        
        frappe.db.commit()
        offset += batch_size
```

**Result**: Server memory exhaustion, process kill.

---

### ❌ Hardcoded Site-Specific Values

```python
# WRONG - site-specific values
def execute():
    frappe.db.set_value("Company", "My Company Ltd", "default_currency", "USD")
```

```python
# ✅ CORRECT - dynamic lookup
def execute():
    companies = frappe.get_all("Company")
    for company in companies:
        if not frappe.db.get_value("Company", company.name, "default_currency"):
            frappe.db.set_value("Company", company.name, "default_currency", "USD")
```

**Result**: Patch fails on other sites where "My Company Ltd" doesn't exist.

---

### ❌ Duplicate Patch Entry

```
# WRONG - duplicate is ignored
myapp.patches.v1_0.my_patch
myapp.patches.v1_0.my_patch  # Will NOT run again
```

```
# ✅ CORRECT - make unique with comment
myapp.patches.v1_0.my_patch
myapp.patches.v1_0.my_patch #run-2024-01-15
```

**Result**: Second entry is ignored, patch doesn't re-run.

---

### ❌ Missing __init__.py in Patches

```
# WRONG - Python cannot find module
myapp/
└── patches/
    └── v1_0/
        └── my_patch.py  # ImportError!
```

```
# ✅ CORRECT - __init__.py in every directory
myapp/
└── patches/
    ├── __init__.py
    └── v1_0/
        ├── __init__.py
        └── my_patch.py
```

---

## Fixtures Anti-Patterns

### ❌ User Data in Fixtures

```python
# WRONG - user specific data
fixtures = [
    "User",           # DON'T - contains passwords
    "Communication"   # DON'T - site specific data
]
```

```python
# ✅ CORRECT - configuration only
fixtures = [
    "Custom Field",
    "Property Setter",
    "Role"
]
```

**Result**: Security risk, privacy violation, deployment problems.

---

### ❌ Transactional Data in Fixtures

```python
# WRONG - transactional data
fixtures = [
    "Sales Invoice",  # DON'T
    "Sales Order"     # DON'T
]
```

**Result**: Production data overwritten, data loss.

---

### ❌ Overly Broad Filters

```python
# WRONG - may export too much
fixtures = [
    {"dt": "DocType"}  # Exports ALL DocTypes!
]
```

```python
# ✅ CORRECT - specific filter
fixtures = [
    {"dt": "DocType", "filters": [["module", "=", "My Module"]]}
]
```

**Result**: Unintended system DocTypes get overwritten.

---

### ❌ Circular Dependency in Fixtures

```python
# WRONG - Workflow depends on Workflow State
fixtures = [
    "Workflow",        # Needs states
    "Workflow State"   # Comes too late
]
```

```python
# ✅ CORRECT - proper order
fixtures = [
    "Workflow State",
    "Workflow"
]
```

**Result**: Import errors, incomplete workflows.

---

### ❌ Missing Module in Custom Fields

```json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_field",
        "dt": "Sales Invoice",
        "fieldname": "custom_field",
        "module": ""  // WRONG - no module
    }
]
```

```json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_field",
        "dt": "Sales Invoice",
        "fieldname": "custom_field",
        "module": "My Custom App"  // ✅ CORRECT
    }
]
```

**Result**: Custom field not exported correctly on next export.

---

## General Anti-Patterns

### ❌ No Version Compatibility Check

```python
# WRONG - no version check
def execute():
    # v15-only feature
    frappe.new_v15_function()
```

```python
# ✅ CORRECT - version check
def execute():
    import frappe
    
    frappe_version = int(frappe.__version__.split('.')[0])
    
    if frappe_version >= 15:
        frappe.new_v15_function()
    else:
        frappe.legacy_function()
```

---

### ❌ No Commit After Bulk Updates

```python
# WRONG - no commit
def execute():
    for i in range(10000):
        frappe.db.set_value("DocType", name, "field", value)
    # Implicit rollback on error!
```

```python
# ✅ CORRECT - explicit commits
def execute():
    for i, item in enumerate(items):
        frappe.db.set_value("DocType", item.name, "field", value)
        
        if i % 100 == 0:
            frappe.db.commit()
    
    frappe.db.commit()
```

---

### ❌ Print Statements in Production Code

```python
# WRONG - print disappears in production
def execute():
    print("Starting migration...")
```

```python
# ✅ CORRECT - use logging
def execute():
    frappe.log_error(message="Starting migration", title="Migration Info")
    # Or for non-errors:
    frappe.logger().info("Starting migration...")
```

---

## Summary: Top 10 Mistakes

| # | Mistake | Result |
|---|---------|--------|
| 1 | Missing `__version__` | Build fails |
| 2 | Frappe in pip dependencies | Install fails |
| 3 | Module not in modules.txt | DocTypes don't work |
| 4 | Missing `__init__.py` | Import errors |
| 5 | Patch without error handling | No diagnostics |
| 6 | Wrong model sync section | SQL errors |
| 7 | No batch processing | Memory exhaustion |
| 8 | User data in fixtures | Security risk |
| 9 | Hardcoded values | Multi-site failures |
| 10 | No commits | Data rollback |
