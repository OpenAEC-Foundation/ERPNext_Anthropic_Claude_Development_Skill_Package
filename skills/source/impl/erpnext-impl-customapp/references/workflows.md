# Workflows - Custom App Implementation

Step-by-step implementation guides for Frappe/ERPNext custom apps.

---

## Workflow 1: Create New Frappe App (From Scratch)

### Prerequisites
- Bench installation with at least one site
- Target Frappe version (v14/v15/v16)

### Steps

```bash
# Step 1: Create app structure
cd ~/frappe-bench
bench new-app my_custom_app

# Interactive prompts:
# - App Title: My Custom App
# - App Description: Description of your app
# - App Publisher: Your Company Name
# - App Email: dev@yourcompany.com
# - App License: MIT (or your choice)
```

```python
# Step 2: Verify __init__.py has version
# my_custom_app/my_custom_app/__init__.py
__version__ = "0.0.1"
```

```toml
# Step 3: Configure pyproject.toml (v15+)
# my_custom_app/pyproject.toml

[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "my_custom_app"
authors = [
    { name = "Your Company", email = "dev@yourcompany.com" }
]
description = "Description of your app"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = []

[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
# Add if needed:
# erpnext = ">=15.0.0,<16.0.0"
```

```python
# Step 4: Configure minimal hooks.py
# my_custom_app/my_custom_app/hooks.py

app_name = "my_custom_app"
app_title = "My Custom App"
app_publisher = "Your Company"
app_description = "Description of your app"
app_email = "dev@yourcompany.com"
app_license = "MIT"

required_apps = ["frappe"]  # Or ["frappe", "erpnext"]

fixtures = []
```

```bash
# Step 5: Install on site
bench --site mysite install-app my_custom_app

# Step 6: Verify installation
bench --site mysite list-apps
# Should show: frappe, my_custom_app
```

### Verification Checklist
- [ ] App appears in `bench --site mysite list-apps`
- [ ] `__version__` defined in `__init__.py`
- [ ] `pyproject.toml` has `dynamic = ["version"]`
- [ ] `hooks.py` has `required_apps`

---

## Workflow 2: Add Module to Existing App

### When to Add a Module
- App has 5+ DocTypes in one module
- DocTypes fall into distinct functional areas
- Need to organize code by business domain

### Steps

```bash
# Step 1: Create module directory
mkdir -p my_custom_app/my_custom_app/new_module
mkdir -p my_custom_app/my_custom_app/new_module/doctype
```

```python
# Step 2: Add __init__.py (REQUIRED!)
# my_custom_app/my_custom_app/new_module/__init__.py
# (Can be empty file)
```

```text
# Step 3: Register in modules.txt
# my_custom_app/my_custom_app/modules.txt

My Custom App
New Module
```

```bash
# Step 4: Migrate to register module
bench --site mysite migrate
```

```bash
# Step 5: Verify module exists
bench --site mysite console
>>> frappe.get_all("Module Def", filters={"app_name": "my_custom_app"})
# Should show both modules
```

### Module Naming Convention

| modules.txt | Directory | Example DocType |
|-------------|-----------|-----------------|
| `My Custom App` | `my_custom_app/` | Core DocTypes |
| `New Module` | `new_module/` | Related DocTypes |
| `API Integrations` | `api_integrations/` | Integration DocTypes |

---

## Workflow 3: Create DocType with Controller

### Steps

```bash
# Step 1: Create DocType via UI or command
bench --site mysite new-doctype "My Document" --module "My Custom App"

# This creates:
# my_custom_app/my_custom_app/doctype/my_document/
# ├── my_document.json       # DocType definition
# ├── my_document.py         # Controller
# ├── my_document.js         # Client script
# └── test_my_document.py    # Tests
```

```python
# Step 2: Implement controller
# my_custom_app/my_custom_app/doctype/my_document/my_document.py

import frappe
from frappe.model.document import Document


class MyDocument(Document):
    def validate(self):
        """Runs on save, before database write."""
        self.validate_required_fields()
        self.calculate_totals()
    
    def before_save(self):
        """Runs after validate, before database write."""
        self.set_defaults()
    
    def on_submit(self):
        """Runs when document is submitted."""
        self.create_related_records()
    
    def validate_required_fields(self):
        if not self.customer:
            frappe.throw("Customer is required")
    
    def calculate_totals(self):
        self.total = sum(item.amount for item in self.items)
    
    def set_defaults(self):
        if not self.posting_date:
            self.posting_date = frappe.utils.today()
    
    def create_related_records(self):
        # Example: Create linked record on submit
        pass
```

```javascript
// Step 3: Implement client script
// my_custom_app/my_custom_app/doctype/my_document/my_document.js

frappe.ui.form.on("My Document", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Create Invoice"), function() {
                frm.trigger("create_invoice");
            });
        }
    },
    
    customer(frm) {
        if (frm.doc.customer) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Customer",
                    filters: { name: frm.doc.customer },
                    fieldname: ["customer_name", "territory"]
                },
                callback(r) {
                    if (r.message) {
                        frm.set_value("customer_name", r.message.customer_name);
                        frm.set_value("territory", r.message.territory);
                    }
                }
            });
        }
    },
    
    create_invoice(frm) {
        frappe.call({
            method: "my_custom_app.my_custom_app.doctype.my_document.my_document.create_invoice",
            args: { doc_name: frm.doc.name },
            callback(r) {
                if (r.message) {
                    frappe.set_route("Form", "Sales Invoice", r.message);
                }
            }
        });
    }
});
```

```bash
# Step 4: Migrate to apply changes
bench --site mysite migrate

# Step 5: Build assets
bench build --app my_custom_app
```

---

## Workflow 4: Write Database Migration Patch

### Scenario: Migrate data from old_field to new_field

### Steps

```bash
# Step 1: Create patch directory structure
mkdir -p my_custom_app/my_custom_app/patches/v1_1
touch my_custom_app/my_custom_app/patches/__init__.py
touch my_custom_app/my_custom_app/patches/v1_1/__init__.py
```

```python
# Step 2: Write the patch
# my_custom_app/my_custom_app/patches/v1_1/migrate_field_data.py

import frappe


def execute():
    """Migrate data from old_field to new_field."""
    
    # Check if migration needed
    if not frappe.db.has_column("My Document", "old_field"):
        return
    
    batch_size = 1000
    offset = 0
    total_updated = 0
    
    while True:
        # Get batch of records needing migration
        records = frappe.db.sql("""
            SELECT name, old_field
            FROM `tabMy Document`
            WHERE old_field IS NOT NULL
              AND (new_field IS NULL OR new_field = '')
            LIMIT %s OFFSET %s
        """, (batch_size, offset), as_dict=True)
        
        if not records:
            break
        
        for record in records:
            # Transform data if needed
            new_value = transform_value(record.old_field)
            
            # Update record
            frappe.db.set_value(
                "My Document",
                record.name,
                "new_field",
                new_value,
                update_modified=False
            )
            total_updated += 1
        
        # Commit batch to free memory
        frappe.db.commit()
        offset += batch_size
        
        # Log progress for large migrations
        if total_updated % 10000 == 0:
            frappe.publish_progress(
                percent=offset,
                title="Migrating field data",
                description=f"Updated {total_updated} records"
            )
    
    frappe.db.commit()
    print(f"Migration complete: {total_updated} records updated")


def transform_value(old_value):
    """Transform old field value to new format."""
    if not old_value:
        return None
    
    # Example: Convert comma-separated to JSON array
    # return frappe.as_json(old_value.split(","))
    
    return old_value
```

```ini
# Step 3: Register patch in patches.txt
# my_custom_app/my_custom_app/patches.txt

[post_model_sync]
my_custom_app.patches.v1_1.migrate_field_data
```

```bash
# Step 4: Test on development site
bench --site devsite migrate

# Step 5: Verify migration
bench --site devsite console
>>> frappe.db.count("My Document", {"new_field": ["is", "set"]})
```

### Patch Error Handling Pattern

```python
def execute():
    """Safe patch with error handling."""
    try:
        # Main migration logic
        do_migration()
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(
            title="Patch failed: migrate_field_data",
            message=str(e)
        )
        raise
```

---

## Workflow 5: Configure and Export Fixtures

### Scenario: Export Custom Fields and Property Setters

### Steps

```python
# Step 1: Configure fixtures in hooks.py
# my_custom_app/my_custom_app/hooks.py

fixtures = [
    # Custom Fields created by this app
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My Custom App"]]
    },
    
    # Property Setters for DocTypes we modify
    {
        "dt": "Property Setter",
        "filters": [
            ["module", "=", "My Custom App"]
        ]
    },
    
    # Our own configuration DocType (all records)
    "My Settings Category",
    
    # Workflows we created
    {
        "dt": "Workflow",
        "filters": [["document_type", "in", ["My Document"]]]
    },
    
    # Custom roles
    {
        "dt": "Role",
        "filters": [["name", "in", ["My Custom Role", "My Admin Role"]]]
    }
]
```

```bash
# Step 2: Make changes via UI
# - Add Custom Fields via Customize Form
# - Set Property Setters via field properties
# - Create Workflows via Workflow Builder
```

```bash
# Step 3: Export fixtures
bench --site mysite export-fixtures --app my_custom_app

# Creates:
# my_custom_app/my_custom_app/fixtures/
# ├── custom_field.json
# ├── property_setter.json
# ├── my_settings_category.json
# ├── workflow.json
# └── role.json
```

```bash
# Step 4: Verify JSON files
cat my_custom_app/my_custom_app/fixtures/custom_field.json
# Should show array of Custom Field documents
```

```bash
# Step 5: Test import on fresh site
bench new-site testsite
bench --site testsite install-app my_custom_app
bench --site testsite migrate
# Fixtures auto-import during migrate
```

### Fixture Verification Checklist
- [ ] JSON files created in fixtures/ directory
- [ ] Files contain only YOUR app's customizations
- [ ] No transactional data included
- [ ] Test import on fresh site works

---

## Workflow 6: Extend Existing ERPNext DocType (v14/v15)

### Scenario: Add validation to Sales Invoice

### Steps

```python
# Step 1: Create event handler
# my_custom_app/my_custom_app/events/sales_invoice.py

import frappe


def validate(doc, method):
    """Custom validation for Sales Invoice.
    
    Args:
        doc: The Sales Invoice document
        method: Event name ("validate")
    """
    validate_customer_credit(doc)
    validate_item_availability(doc)


def validate_customer_credit(doc):
    """Check customer credit limit before save."""
    if doc.is_return:
        return
    
    customer = frappe.get_doc("Customer", doc.customer)
    
    if customer.credit_limit:
        outstanding = get_customer_outstanding(doc.customer)
        if outstanding + doc.grand_total > customer.credit_limit:
            frappe.throw(
                f"Credit limit exceeded. "
                f"Outstanding: {outstanding}, "
                f"Limit: {customer.credit_limit}"
            )


def validate_item_availability(doc):
    """Check item stock for non-stock items."""
    for item in doc.items:
        if not frappe.db.get_value("Item", item.item_code, "is_stock_item"):
            continue
        
        available = get_available_qty(item.item_code, doc.set_warehouse)
        if available < item.qty:
            frappe.msgprint(
                f"Low stock for {item.item_code}: "
                f"Available {available}, Requested {item.qty}",
                alert=True
            )


def get_customer_outstanding(customer):
    """Get total outstanding for customer."""
    return frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0)
        FROM `tabSales Invoice`
        WHERE customer = %s
          AND docstatus = 1
          AND outstanding_amount > 0
    """, customer)[0][0]


def get_available_qty(item_code, warehouse):
    """Get available quantity from Bin."""
    return frappe.db.get_value(
        "Bin",
        {"item_code": item_code, "warehouse": warehouse},
        "actual_qty"
    ) or 0
```

```python
# Step 2: Register in hooks.py
# my_custom_app/my_custom_app/hooks.py

doc_events = {
    "Sales Invoice": {
        "validate": "my_custom_app.events.sales_invoice.validate"
    }
}
```

```bash
# Step 3: Clear cache and test
bench --site mysite clear-cache
# Create/save Sales Invoice to test validation
```

---

## Workflow 7: Extend Existing ERPNext DocType (v16)

### Scenario: Same as above, but using v16 extend_doctype_class

### Steps

```python
# Step 1: Create extension class
# my_custom_app/my_custom_app/overrides/sales_invoice.py

import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


class CustomSalesInvoice(SalesInvoice):
    """Extended Sales Invoice with custom validation."""
    
    def validate(self):
        # Call parent validation first
        super().validate()
        
        # Add custom validation
        self.validate_customer_credit()
        self.validate_item_availability()
    
    def validate_customer_credit(self):
        """Check customer credit limit before save."""
        if self.is_return:
            return
        
        customer = frappe.get_doc("Customer", self.customer)
        
        if customer.credit_limit:
            outstanding = self.get_customer_outstanding()
            if outstanding + self.grand_total > customer.credit_limit:
                frappe.throw(
                    f"Credit limit exceeded. "
                    f"Outstanding: {outstanding}, "
                    f"Limit: {customer.credit_limit}"
                )
    
    def validate_item_availability(self):
        """Check item stock."""
        for item in self.items:
            if not frappe.db.get_value("Item", item.item_code, "is_stock_item"):
                continue
            
            available = self.get_available_qty(item.item_code)
            if available < item.qty:
                frappe.msgprint(
                    f"Low stock for {item.item_code}",
                    alert=True
                )
    
    def get_customer_outstanding(self):
        """Get total outstanding for customer."""
        return frappe.db.sql("""
            SELECT COALESCE(SUM(outstanding_amount), 0)
            FROM `tabSales Invoice`
            WHERE customer = %s
              AND docstatus = 1
              AND outstanding_amount > 0
        """, self.customer)[0][0]
    
    def get_available_qty(self, item_code):
        """Get available quantity from Bin."""
        return frappe.db.get_value(
            "Bin",
            {"item_code": item_code, "warehouse": self.set_warehouse},
            "actual_qty"
        ) or 0
```

```python
# Step 2: Register in hooks.py (v16 syntax)
# my_custom_app/my_custom_app/hooks.py

extend_doctype_class = {
    "Sales Invoice": "my_custom_app.overrides.sales_invoice.CustomSalesInvoice"
}
```

```bash
# Step 3: Clear cache and test
bench --site mysite clear-cache
```

### v16 vs v14/v15 Comparison

| Aspect | v14/v15 (doc_events) | v16 (extend_doctype_class) |
|--------|---------------------|---------------------------|
| Inheritance | No class inheritance | Full class inheritance |
| Access to self | Via `doc` parameter | Via `self` directly |
| Override methods | Hook into events | Override any method |
| Call parent | Not applicable | `super().method()` |
| Recommended | Still works | Preferred approach |

---

## Workflow 8: App Version Upgrade (v14 to v15/v16)

### Steps

```bash
# Step 1: Backup current state
git checkout -b v14-backup
git push origin v14-backup
git checkout main
```

```toml
# Step 2: Convert setup.py to pyproject.toml
# Create my_custom_app/pyproject.toml

[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "my_custom_app"
authors = [
    { name = "Your Company", email = "dev@yourcompany.com" }
]
description = "Your app description"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]

# Copy dependencies from requirements.txt
dependencies = [
    "requests>=2.28.0"
]

[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
```

```python
# Step 3: Verify __init__.py has version
# my_custom_app/my_custom_app/__init__.py
__version__ = "2.0.0"  # Bump major version for breaking change
```

```bash
# Step 4: Remove old files (optional, keep for v14 compatibility)
# rm my_custom_app/setup.py
# rm my_custom_app/requirements.txt
```

```python
# Step 5: Update hooks.py for v16 features (optional)
# my_custom_app/my_custom_app/hooks.py

# Convert doc_events to extend_doctype_class if desired
# OLD (v14/v15):
# doc_events = {
#     "Sales Invoice": {
#         "validate": "my_custom_app.events.si.validate"
#     }
# }

# NEW (v16):
extend_doctype_class = {
    "Sales Invoice": "my_custom_app.overrides.sales_invoice.CustomSalesInvoice"
}
```

```bash
# Step 6: Test on v15/v16 bench
bench --site mysite migrate
bench build --app my_custom_app

# Step 7: Run tests
bench --site mysite run-tests --app my_custom_app
```

### Version Compatibility Matrix

| App Version | Frappe 14 | Frappe 15 | Frappe 16 |
|-------------|:---------:|:---------:|:---------:|
| 1.x (setup.py) | ✅ | ✅ | ✅ |
| 2.x (pyproject) | ❌ | ✅ | ✅ |
| 2.x + extend_doctype | ❌ | ❌ | ✅ |
