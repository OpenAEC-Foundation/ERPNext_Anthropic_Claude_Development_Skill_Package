# Complete App Voorbeelden

> Werkende voorbeelden van Frappe custom apps met alle componenten.

---

## Voorbeeld 1: Minimale App (v15)

### Directory Structuur

```
minimal_app/
├── pyproject.toml
├── README.md
├── minimal_app/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   └── minimal_app/
│       ├── __init__.py
│       └── fixtures/
│           └── role.json
└── .git/
```

### pyproject.toml

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "minimal_app"
authors = [
    { name = "Your Company", email = "dev@example.com" }
]
description = "A minimal Frappe app"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = []

[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
```

### minimal_app/__init__.py

```python
__version__ = "0.0.1"
```

### minimal_app/hooks.py

```python
app_name = "minimal_app"
app_title = "Minimal App"
app_publisher = "Your Company"
app_description = "A minimal Frappe app"
app_email = "dev@example.com"
app_license = "MIT"

fixtures = [
    {"dt": "Role", "filters": [["name", "like", "Minimal%"]]}
]
```

### minimal_app/modules.txt

```
Minimal App
```

### minimal_app/patches.txt

```
# Patches here
```

### minimal_app/minimal_app/fixtures/role.json

```json
[
    {
        "doctype": "Role",
        "name": "Minimal User",
        "desk_access": 1,
        "is_custom": 1
    }
]
```

---

## Voorbeeld 2: ERPNext Extension App

### Directory Structuur

```
erpnext_extension/
├── pyproject.toml
├── README.md
├── erpnext_extension/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   ├── patches/
│   │   ├── __init__.py
│   │   └── v1_0/
│   │       ├── __init__.py
│   │       └── setup_custom_fields.py
│   ├── overrides/
│   │   ├── __init__.py
│   │   └── sales_invoice.py
│   ├── erpnext_extension/
│   │   ├── __init__.py
│   │   ├── doctype/
│   │   │   └── extension_settings/
│   │   │       ├── __init__.py
│   │   │       ├── extension_settings.json
│   │   │       └── extension_settings.py
│   │   └── fixtures/
│   │       ├── custom_field.json
│   │       └── property_setter.json
│   └── public/
│       └── js/
│           └── sales_invoice.js
└── .git/
```

### pyproject.toml

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "erpnext_extension"
authors = [
    { name = "Your Company", email = "dev@example.com" }
]
description = "Extends ERPNext functionality"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = []

[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
```

### erpnext_extension/__init__.py

```python
__version__ = "1.0.0"
```

### erpnext_extension/hooks.py

```python
app_name = "erpnext_extension"
app_title = "ERPNext Extension"
app_publisher = "Your Company"
app_description = "Extends ERPNext functionality"
app_email = "dev@example.com"
app_license = "MIT"

required_apps = ["frappe", "erpnext"]

# Fixtures
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "ERPNext Extension"]]
    },
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "ERPNext Extension"]]
    },
    {
        "dt": "Role",
        "filters": [["name", "like", "Extension%"]]
    }
]

# Document events
doc_events = {
    "Sales Invoice": {
        "validate": "erpnext_extension.overrides.sales_invoice.validate",
        "on_submit": "erpnext_extension.overrides.sales_invoice.on_submit"
    }
}

# DocType specific JavaScript
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js"
}
```

### erpnext_extension/modules.txt

```
ERPNext Extension
```

### erpnext_extension/patches.txt

```ini
[post_model_sync]
erpnext_extension.patches.v1_0.setup_custom_fields
```

### erpnext_extension/patches/v1_0/setup_custom_fields.py

```python
import frappe

def execute():
    """Setup default values for custom fields."""
    
    # Set default value for existing invoices
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={"custom_extension_status": ["is", "not set"]},
        fields=["name"]
    )
    
    for inv in invoices:
        frappe.db.set_value(
            "Sales Invoice",
            inv.name,
            "custom_extension_status",
            "Pending",
            update_modified=False
        )
    
    frappe.db.commit()
```

### erpnext_extension/overrides/sales_invoice.py

```python
import frappe

def validate(doc, method):
    """Validate Sales Invoice extensions."""
    if doc.custom_extension_status == "Approved":
        if not doc.custom_approved_by:
            frappe.throw("Approved By is required when status is Approved")

def on_submit(doc, method):
    """Handle Sales Invoice submission."""
    if doc.custom_extension_status != "Approved":
        frappe.throw("Cannot submit invoice without approval")
```

### erpnext_extension/public/js/sales_invoice.js

```javascript
frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Request Approval'), function() {
                frm.set_value('custom_extension_status', 'Pending Approval');
                frm.save();
            }, __('Extension'));
        }
    },
    
    custom_extension_status: function(frm) {
        if (frm.doc.custom_extension_status === 'Approved') {
            frm.set_value('custom_approved_by', frappe.session.user);
        }
    }
});
```

### erpnext_extension/erpnext_extension/fixtures/custom_field.json

```json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_extension_status",
        "dt": "Sales Invoice",
        "module": "ERPNext Extension",
        "fieldname": "custom_extension_status",
        "fieldtype": "Select",
        "options": "\nPending\nPending Approval\nApproved\nRejected",
        "label": "Extension Status",
        "insert_after": "status",
        "translatable": 0
    },
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_approved_by",
        "dt": "Sales Invoice",
        "module": "ERPNext Extension",
        "fieldname": "custom_approved_by",
        "fieldtype": "Link",
        "options": "User",
        "label": "Approved By",
        "insert_after": "custom_extension_status",
        "read_only": 1,
        "translatable": 0
    }
]
```

---

## Voorbeeld 3: App met Patches (Data Migratie)

### patches.txt

```ini
[pre_model_sync]
# Data backup voor veld verwijdering
myapp.patches.v2_0.backup_old_field_data

[post_model_sync]
# Migreer naar nieuw formaat
myapp.patches.v2_0.migrate_to_new_format
myapp.patches.v2_0.cleanup_temp_data
```

### patches/v2_0/backup_old_field_data.py

```python
import frappe
import json

def execute():
    """Backup data van old_field voordat het wordt verwijderd."""
    
    records = frappe.get_all(
        "MyDocType",
        filters={"old_field": ["is", "set"]},
        fields=["name", "old_field"]
    )
    
    if records:
        # Bewaar in tijdelijke tabel of log
        frappe.db.sql("""
            CREATE TABLE IF NOT EXISTS `_backup_old_field` (
                `name` VARCHAR(140),
                `old_field` TEXT,
                PRIMARY KEY (`name`)
            )
        """)
        
        for record in records:
            frappe.db.sql("""
                INSERT INTO `_backup_old_field` (name, old_field)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE old_field = VALUES(old_field)
            """, (record.name, record.old_field))
        
        frappe.db.commit()
```

### patches/v2_0/migrate_to_new_format.py

```python
import frappe

def execute():
    """Migreer data van backup naar nieuw veld formaat."""
    
    # Check of backup tabel bestaat
    if not frappe.db.table_exists("_backup_old_field"):
        return
    
    batch_size = 500
    offset = 0
    
    while True:
        records = frappe.db.sql("""
            SELECT name, old_field FROM `_backup_old_field`
            LIMIT %s OFFSET %s
        """, (batch_size, offset), as_dict=True)
        
        if not records:
            break
        
        for record in records:
            try:
                new_value = transform_value(record.old_field)
                frappe.db.set_value(
                    "MyDocType",
                    record.name,
                    "new_field",
                    new_value,
                    update_modified=False
                )
            except Exception as e:
                frappe.log_error(
                    f"Migration failed for {record.name}: {str(e)}",
                    "Data Migration Error"
                )
        
        frappe.db.commit()
        offset += batch_size

def transform_value(old_value):
    """Transform old format to new format."""
    # Implementeer transformatie logica
    return old_value.upper() if old_value else None
```

### patches/v2_0/cleanup_temp_data.py

```python
import frappe

def execute():
    """Verwijder tijdelijke backup tabel."""
    
    if frappe.db.table_exists("_backup_old_field"):
        frappe.db.sql("DROP TABLE `_backup_old_field`")
        frappe.db.commit()
```

---

## Installatie Workflow

```bash
# 1. App aanmaken
cd frappe-bench
bench new-app my_custom_app

# 2. App installeren op site
bench --site mysite install-app my_custom_app

# 3. Migreren (fixtures laden)
bench --site mysite migrate

# 4. Cache legen
bench --site mysite clear-cache

# 5. Assets bouwen
bench build --app my_custom_app
```

---

## Bestaande App van Git

```bash
# 1. App ophalen
bench get-app https://github.com/org/my_custom_app

# 2. Installeren
bench --site mysite install-app my_custom_app

# 3. Migreren
bench --site mysite migrate
```
