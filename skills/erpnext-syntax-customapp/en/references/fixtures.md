# Fixtures (Data Export/Import)

> Fixtures are JSON files that are automatically imported during app installation or migration.

---

## Fixtures Hook Configuration

**Location**: `hooks.py`

### Basic Syntax

```python
# Export ALL records of a DocType
fixtures = [
    "Category",
    "Custom Field"
]
```

### With Filters

```python
fixtures = [
    # All records of Category
    "Category",
    
    # Only specific records with filter
    {"dt": "Role", "filters": [["role_name", "like", "MyApp%"]]},
    
    # Multiple filters
    {
        "dt": "Custom Field",
        "filters": [
            ["module", "=", "MyApp"],
            ["dt", "in", ["Sales Invoice", "Sales Order"]]
        ]
    },
    
    # Or filters (v14+)
    {
        "dt": "Property Setter",
        "or_filters": [
            ["module", "=", "MyApp"],
            ["name", "like", "myapp%"]
        ]
    }
]
```

---

## Exporting Fixtures

### Export Command

```bash
# Export all fixtures for an app
bench --site sitename export-fixtures --app myapp

# Export fixtures for all apps
bench --site sitename export-fixtures
```

### Output Location

```
myapp/
└── {module}/
    └── fixtures/
        ├── category.json
        ├── role.json
        └── custom_field.json
```

---

## Fixture File Structure

### Example: custom_field.json

```json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_field_name",
        "dt": "Sales Invoice",
        "fieldname": "custom_field_name",
        "fieldtype": "Data",
        "label": "Custom Field",
        "insert_after": "customer"
    },
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-another_field",
        "dt": "Sales Invoice",
        "fieldname": "another_field",
        "fieldtype": "Link",
        "options": "Customer",
        "label": "Another Field"
    }
]
```

---

## Fields NOT Exported

The following system fields are automatically excluded:

| Field | Reason |
|-------|--------|
| `modified_by` | System managed |
| `creation` | System managed |
| `owner` | Site-specific |
| `idx` | Order system managed |
| `lft` | Tree structure (internal) |
| `rgt` | Tree structure (internal) |

**For child table records also:**
- `docstatus`
- `doctype`
- `modified`
- `name`

---

## Fixtures Import Behavior

Fixtures are imported during:

1. **App installation**: `bench --site sitename install-app myapp`
2. **Migration**: `bench --site sitename migrate`
3. **Update**: `bench update`

### Sync Behavior

| Action | Description |
|--------|-------------|
| **Insert** | New records are added |
| **Update** | Existing records are overwritten |
| **Delete** | Records NOT in fixture are NOT deleted |

---

## Commonly Used Fixture DocTypes

| DocType | Usage |
|---------|-------|
| `Custom Field` | Add custom fields to existing DocTypes |
| `Property Setter` | Modify properties of existing fields |
| `Role` | Custom roles |
| `Custom DocPerm` | Custom permissions |
| `Workflow` | Workflow definitions |
| `Workflow State` | Workflow states |
| `Workflow Action` | Workflow actions |
| `Print Format` | Print templates |
| `Report` | Custom reports |

---

## Custom Field Fixture Example

### hooks.py

```python
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My Custom App"]]
    }
]
```

### fixtures/custom_field.json

```json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_reference",
        "dt": "Sales Invoice",
        "module": "My Custom App",
        "fieldname": "custom_reference",
        "fieldtype": "Data",
        "label": "Custom Reference",
        "insert_after": "naming_series",
        "translatable": 0
    },
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_category",
        "dt": "Sales Invoice",
        "module": "My Custom App",
        "fieldname": "custom_category",
        "fieldtype": "Link",
        "options": "Category",
        "label": "Category",
        "insert_after": "custom_reference"
    }
]
```

---

## Property Setter Fixture Example

```json
[
    {
        "doctype": "Property Setter",
        "name": "Sales Invoice-customer-reqd",
        "doc_type": "Sales Invoice",
        "module": "My Custom App",
        "field_name": "customer",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
    },
    {
        "doctype": "Property Setter",
        "name": "Sales Invoice-main-default_print_format",
        "doc_type": "Sales Invoice",
        "module": "My Custom App",
        "field_name": null,
        "property": "default_print_format",
        "property_type": "Data",
        "value": "My Custom Format"
    }
]
```

---

## after_sync Hook

```python
# hooks.py
after_sync = "myapp.setup.after_sync"
```

```python
# myapp/setup.py
def after_sync():
    """Runs after fixtures are synchronized."""
    setup_default_values()
    create_default_records()
```

---

## Fixtures vs Patches: When to Use What?

| Scenario | Fixtures | Patches |
|----------|:--------:|:-------:|
| Add Custom Fields | ✅ | ❌ |
| Property Setters | ✅ | ❌ |
| Standard configuration (Roles, Workflows) | ✅ | ❌ |
| Data transformation | ❌ | ✅ |
| Data cleanup | ❌ | ✅ |
| One-time data import | ❌ | ✅ |
| Field value migration | ❌ | ✅ |
| Default seed data | ✅ | ❌ (or after_install) |

---

## Filter Syntax

### Comparison Operators

| Operator | Example |
|----------|---------|
| `=` | `["field", "=", "value"]` |
| `!=` | `["field", "!=", "value"]` |
| `like` | `["field", "like", "prefix%"]` |
| `not like` | `["field", "not like", "%pattern%"]` |
| `in` | `["field", "in", ["val1", "val2"]]` |
| `not in` | `["field", "not in", ["val1", "val2"]]` |
| `is` | `["field", "is", "set"]` or `["field", "is", "not set"]` |

---

## Critical Rules

### ✅ ALWAYS

1. Set `module` field for Custom Fields/Property Setters
2. Use specific filters (don't export all records)
3. Test fixtures after export with clean install
4. Respect fixtures order for dependencies

### ❌ NEVER

1. User data in fixtures (User, Communication)
2. Transactional data (Sales Invoice, Sales Order)
3. Overly broad filters (may export too much)
4. Site-specific values in fixtures

### ⚠️ USE WITH CAUTION

1. Custom DocPerm - overwrites user customizations
2. Workflow - can affect active workflows
3. Records with dependencies (correct order!)
