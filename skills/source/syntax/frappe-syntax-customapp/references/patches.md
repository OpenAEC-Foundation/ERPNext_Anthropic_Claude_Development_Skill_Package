# Patches (Migration Scripts)

> Patches are Python scripts that execute data migrations during app updates.

---

## patches.txt Structure

**Location**: `{app}/{app}/patches.txt`

### Basic Syntax

```
# Simple patch reference (dotted path)
myapp.patches.v1_0.my_awesome_patch

# One-off Python statements
execute:frappe.delete_doc('Page', 'applications', ignore_missing=True)
```

### INI-Style Sections (v14+)

```ini
[pre_model_sync]
# Patches that run BEFORE DocType schema sync
# Have access to OLD schema (old fields still available)
myapp.patches.v1_0.migrate_old_field_data
myapp.patches.v1_0.backup_deprecated_records

[post_model_sync]
# Patches that run AFTER DocType schema sync
# Have access to NEW schema (new fields available)
# Do NOT need to call frappe.reload_doc
myapp.patches.v1_0.populate_new_field
myapp.patches.v1_0.cleanup_orphan_records
```

---

## Pre vs Post Model Sync

| Situation | Section | Reason |
|-----------|---------|--------|
| Migrate data from old field | `[pre_model_sync]` | Old fields still available |
| Populate new required fields | `[post_model_sync]` | New fields already exist |
| General data cleanup | `[post_model_sync]` | No schema dependency |
| Rename field and preserve data | `[pre_model_sync]` | Old field name still available |

---

## Patch Directory Structure

### Conventional Structure

```
myapp/
├── patches/
│   ├── __init__.py              # REQUIRED (empty)
│   ├── v1_0/
│   │   ├── __init__.py          # REQUIRED (empty)
│   │   ├── setup_defaults.py
│   │   └── migrate_data.py
│   └── v2_0/
│       ├── __init__.py          # REQUIRED
│       └── schema_upgrade.py
└── patches.txt
```

### Alternative Structure (bench create-patch)

```
myapp/
├── {module}/
│   └── doctype/
│       └── {doctype}/
│           └── patches/
│               ├── __init__.py
│               └── improve_indexing.py
└── patches.txt
```

---

## Patch Implementation

### Basic Template

```python
import frappe

def execute():
    """Patch description here."""
    # Patch logic
    pass
```

### Complete Example: Data Migration

```python
# myapp/patches/v1_0/migrate_customer_type.py
import frappe

def execute():
    """Migrate customer_type from Text to Link field."""
    
    type_mapping = {
        "individual": "Individual",
        "company": "Company", 
        "Individual": "Individual",
        "Company": "Company"
    }
    
    customers = frappe.get_all(
        "Customer",
        filters={"customer_type": ["in", list(type_mapping.keys())]},
        fields=["name", "customer_type"]
    )
    
    for customer in customers:
        new_type = type_mapping.get(customer.customer_type)
        if new_type:
            frappe.db.set_value(
                "Customer", 
                customer.name, 
                "customer_type", 
                new_type,
                update_modified=False
            )
    
    frappe.db.commit()
```

---

## Schema Reload in Pre-Model-Sync

```python
import frappe

def execute():
    """Patch that needs new schema in pre_model_sync."""
    
    # Load new DocType definition BEFORE schema sync runs
    frappe.reload_doc("module_name", "doctype", "doctype_name")
    
    # Now new fields are available
    frappe.db.sql("""
        UPDATE `tabMyDocType`
        SET new_field = old_field
        WHERE old_field IS NOT NULL
    """)
```

**Note**: In `[post_model_sync]`, `frappe.reload_doc()` is NOT needed.

---

## Patch Execution Rules

| Rule | Description |
|------|-------------|
| **Unique lines** | Each line in patches.txt must be unique |
| **One-time execution** | Patches run only once per site |
| **Order** | Patches run in the order they appear |
| **Tracking** | Executed patches are stored in `Patch Log` DocType |
| **Re-run** | Add comment to re-run a patch |

---

## Re-running a Patch

```
# Original
myapp.patches.v1_0.my_patch

# To re-run, add comment (makes line unique)
myapp.patches.v1_0.my_patch #2024-01-15
myapp.patches.v1_0.my_patch #run-again
```

---

## bench create-patch Command

```bash
$ bench create-patch
Select app for new patch (frappe, erpnext, myapp): myapp
Provide DocType name on which this patch will apply: Customer
Describe what this patch does: Improve customer indexing
Provide filename for this patch [improve_indexing.py]: 
Patch folder doesn't exist, create it? [Y/n]: y
Created patch file and updated patches.txt
```

---

## Error Handling

### Basic Try/Except

```python
import frappe

def execute():
    try:
        perform_migration()
    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Patch Error: migrate_customer_type"
        )
        raise  # Re-raise to mark patch as failed
```

### Atomic Operations

```python
import frappe

def execute():
    """Patch with transaction control."""
    
    try:
        for item in get_items_to_migrate():
            process_item(item)
        
        frappe.db.commit()
        
    except Exception:
        frappe.db.rollback()
        raise
```

---

## Batch Processing

```python
import frappe

def execute():
    """Patch with batch processing for large datasets."""
    
    batch_size = 1000
    offset = 0
    
    while True:
        items = frappe.db.sql("""
            SELECT name FROM `tabMyDocType`
            LIMIT %s OFFSET %s
        """, (batch_size, offset), as_dict=True)
        
        if not items:
            break
            
        for item in items:
            process_item(item)
        
        # Commit per batch
        frappe.db.commit()
        offset += batch_size
```

---

## bench migrate Workflow

The `bench migrate` command executes:

1. **before_migrate hooks** execute
2. **[pre_model_sync] patches** execute
3. **Database schema synchronize** (DocType JSON → database)
4. **[post_model_sync] patches** execute
5. **Fixtures synchronize**
6. **Background jobs synchronize**
7. **Translations update**
8. **Search index rebuild**
9. **after_migrate hooks** execute

### Migrate Command Options

```bash
# Standard migration
bench --site sitename migrate

# Skip failing patches (NOT for production!)
bench --site sitename migrate --skip-failing

# Skip search index rebuild (faster)
bench --site sitename migrate --skip-search-index
```

---

## Critical Rules

### ✅ ALWAYS

1. Include `__init__.py` in every patches directory
2. Implement error handling with logging
3. Use batch processing for large datasets
4. Call `frappe.db.commit()` after bulk updates
5. Test on development environment first

### ❌ NEVER

1. Hardcode site-specific values
2. Create patches without error handling
3. Process large datasets without batching
4. Duplicate the same patch line (it will be ignored)
5. Use pre-model-sync patch that needs new fields without `reload_doc`
