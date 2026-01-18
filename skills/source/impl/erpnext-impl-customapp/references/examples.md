# Examples - Custom App Implementation

Complete working examples for Frappe/ERPNext custom apps.

---

## Example 1: Simple Integration App

### Use Case
Integration with external shipping API to get tracking information.

### File Structure

```
shipping_integration/
├── pyproject.toml
├── README.md
├── shipping_integration/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   ├── shipping_integration/           # Module
│   │   ├── __init__.py
│   │   └── doctype/
│   │       └── shipping_settings/
│   │           ├── shipping_settings.json
│   │           └── shipping_settings.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── tracking.py
│   └── fixtures/
│       └── custom_field.json
```

### __init__.py

```python
# shipping_integration/shipping_integration/__init__.py
__version__ = "1.0.0"
```

### pyproject.toml

```toml
# shipping_integration/pyproject.toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "shipping_integration"
authors = [
    { name = "Your Company", email = "dev@example.com" }
]
description = "Shipping carrier API integration for ERPNext"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = [
    "requests>=2.28.0"
]

[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
```

### hooks.py

```python
# shipping_integration/shipping_integration/hooks.py
app_name = "shipping_integration"
app_title = "Shipping Integration"
app_publisher = "Your Company"
app_description = "Shipping carrier API integration"
app_email = "dev@example.com"
app_license = "MIT"

required_apps = ["frappe", "erpnext"]

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Shipping Integration"]]
    }
]

# Add tracking button to Delivery Note
doctype_js = {
    "Delivery Note": "public/js/delivery_note.js"
}
```

### modules.txt

```
Shipping Integration
```

### Settings DocType

```python
# shipping_integration/shipping_integration/doctype/shipping_settings/shipping_settings.py
import frappe
from frappe.model.document import Document


class ShippingSettings(Document):
    def validate(self):
        if self.enabled and not self.api_key:
            frappe.throw("API Key is required when integration is enabled")
```

### API Module

```python
# shipping_integration/shipping_integration/api/tracking.py
import frappe
import requests


@frappe.whitelist()
def get_tracking_info(tracking_number):
    """Get tracking information from shipping carrier.
    
    Args:
        tracking_number: The shipment tracking number
        
    Returns:
        dict: Tracking information with status and events
    """
    settings = frappe.get_single("Shipping Settings")
    
    if not settings.enabled:
        frappe.throw("Shipping integration is not enabled")
    
    try:
        response = requests.get(
            f"{settings.api_url}/track/{tracking_number}",
            headers={"Authorization": f"Bearer {settings.get_password('api_key')}"},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "status": data.get("status"),
            "location": data.get("current_location"),
            "estimated_delivery": data.get("eta"),
            "events": data.get("tracking_events", [])
        }
        
    except requests.RequestException as e:
        frappe.log_error(
            title="Shipping API Error",
            message=f"Failed to get tracking for {tracking_number}: {str(e)}"
        )
        frappe.throw(f"Could not retrieve tracking information: {str(e)}")


@frappe.whitelist()
def update_delivery_note_tracking(delivery_note, tracking_number):
    """Update Delivery Note with tracking information.
    
    Args:
        delivery_note: Delivery Note name
        tracking_number: Tracking number to save
    """
    doc = frappe.get_doc("Delivery Note", delivery_note)
    doc.custom_tracking_number = tracking_number
    
    tracking_info = get_tracking_info(tracking_number)
    doc.custom_shipping_status = tracking_info.get("status")
    doc.custom_estimated_delivery = tracking_info.get("estimated_delivery")
    
    doc.save()
    
    return {"message": "Tracking updated successfully"}
```

### Client Script

```javascript
// shipping_integration/shipping_integration/public/js/delivery_note.js
frappe.ui.form.on("Delivery Note", {
    refresh(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.custom_tracking_number) {
            frm.add_custom_button(__("Get Tracking Update"), function() {
                frappe.call({
                    method: "shipping_integration.api.tracking.get_tracking_info",
                    args: {
                        tracking_number: frm.doc.custom_tracking_number
                    },
                    callback(r) {
                        if (r.message) {
                            show_tracking_dialog(frm, r.message);
                        }
                    }
                });
            }, __("Shipping"));
        }
    }
});

function show_tracking_dialog(frm, tracking) {
    let events_html = tracking.events.map(e => 
        `<tr><td>${e.date}</td><td>${e.location}</td><td>${e.description}</td></tr>`
    ).join("");
    
    frappe.msgprint({
        title: __("Tracking Information"),
        indicator: "blue",
        message: `
            <p><strong>Status:</strong> ${tracking.status}</p>
            <p><strong>Location:</strong> ${tracking.location}</p>
            <p><strong>ETA:</strong> ${tracking.estimated_delivery || "Unknown"}</p>
            <table class="table table-bordered">
                <thead><tr><th>Date</th><th>Location</th><th>Event</th></tr></thead>
                <tbody>${events_html}</tbody>
            </table>
        `
    });
}
```

---

## Example 2: Multi-Module Business App

### Use Case
Project management app with separate modules for projects, tasks, and reports.

### File Structure

```
project_plus/
├── pyproject.toml
├── project_plus/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   ├── patches/
│   │   └── v1_0/
│   │       └── setup_default_statuses.py
│   ├── projects/                        # Module: Projects
│   │   ├── __init__.py
│   │   └── doctype/
│   │       ├── pp_project/
│   │       └── pp_milestone/
│   ├── tasks/                           # Module: Tasks
│   │   ├── __init__.py
│   │   └── doctype/
│   │       ├── pp_task/
│   │       └── pp_task_category/
│   ├── reports/                         # Module: Reports
│   │   ├── __init__.py
│   │   └── report/
│   │       └── project_summary/
│   └── settings/                        # Module: Settings
│       ├── __init__.py
│       └── doctype/
│           └── project_plus_settings/
```

### hooks.py

```python
# project_plus/project_plus/hooks.py
app_name = "project_plus"
app_title = "Project Plus"
app_publisher = "Your Company"
app_description = "Enhanced project management"
app_email = "dev@example.com"
app_license = "MIT"

required_apps = ["frappe"]

fixtures = [
    "PP Task Category",  # Export all categories
    {
        "dt": "Role",
        "filters": [["name", "like", "Project Plus%"]]
    }
]

# Scheduler for deadline reminders
scheduler_events = {
    "daily": [
        "project_plus.tasks.deadline_reminder.send_reminders"
    ]
}

# Permissions
permission_query_conditions = {
    "PP Project": "project_plus.projects.doctype.pp_project.pp_project.get_permission_query_conditions",
    "PP Task": "project_plus.tasks.doctype.pp_task.pp_task.get_permission_query_conditions"
}

has_permission = {
    "PP Project": "project_plus.projects.doctype.pp_project.pp_project.has_permission",
    "PP Task": "project_plus.tasks.doctype.pp_task.pp_task.has_permission"
}
```

### modules.txt

```
Projects
Tasks
Reports
Settings
```

### Project Controller

```python
# project_plus/project_plus/projects/doctype/pp_project/pp_project.py
import frappe
from frappe.model.document import Document
from frappe import _


class PPProject(Document):
    def validate(self):
        self.validate_dates()
        self.calculate_progress()
    
    def on_update(self):
        self.update_task_dates()
    
    def validate_dates(self):
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                frappe.throw(_("End Date cannot be before Start Date"))
    
    def calculate_progress(self):
        """Calculate project progress from tasks."""
        tasks = frappe.get_all(
            "PP Task",
            filters={"project": self.name},
            fields=["status", "progress"]
        )
        
        if not tasks:
            self.progress = 0
            return
        
        total_progress = sum(t.progress or 0 for t in tasks)
        self.progress = total_progress / len(tasks)
    
    def update_task_dates(self):
        """Update task constraints when project dates change."""
        if self.has_value_changed("start_date") or self.has_value_changed("end_date"):
            frappe.db.sql("""
                UPDATE `tabPP Task`
                SET 
                    expected_start = GREATEST(expected_start, %s),
                    expected_end = LEAST(expected_end, %s)
                WHERE project = %s
                  AND docstatus = 0
            """, (self.start_date, self.end_date, self.name))


def get_permission_query_conditions(user):
    """Return SQL conditions for list view filtering."""
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    return f"""(
        `tabPP Project`.owner = {frappe.db.escape(user)}
        OR `tabPP Project`.name IN (
            SELECT parent FROM `tabPP Project Team`
            WHERE user = {frappe.db.escape(user)}
        )
    )"""


def has_permission(doc, user, permission_type=None):
    """Check if user has permission on specific document."""
    if "System Manager" in frappe.get_roles(user):
        return True
    
    if doc.owner == user:
        return True
    
    # Check team membership
    return frappe.db.exists(
        "PP Project Team",
        {"parent": doc.name, "user": user}
    )
```

### Setup Patch

```python
# project_plus/project_plus/patches/v1_0/setup_default_statuses.py
import frappe


def execute():
    """Create default task categories."""
    categories = [
        {"category_name": "Development", "color": "#3498db"},
        {"category_name": "Design", "color": "#9b59b6"},
        {"category_name": "Testing", "color": "#e74c3c"},
        {"category_name": "Documentation", "color": "#2ecc71"},
        {"category_name": "Meeting", "color": "#f39c12"}
    ]
    
    for cat in categories:
        if not frappe.db.exists("PP Task Category", cat["category_name"]):
            doc = frappe.new_doc("PP Task Category")
            doc.update(cat)
            doc.insert(ignore_permissions=True)
    
    frappe.db.commit()
```

### patches.txt

```ini
[post_model_sync]
project_plus.patches.v1_0.setup_default_statuses
```

---

## Example 3: ERPNext Extension App

### Use Case
Add custom pricing rules and approval workflow to Sales Order.

### File Structure

```
sales_customization/
├── pyproject.toml
├── sales_customization/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   ├── sales_customization/
│   │   ├── __init__.py
│   │   └── doctype/
│   │       └── pricing_approval_settings/
│   ├── overrides/                      # v16 style
│   │   ├── __init__.py
│   │   └── sales_order.py
│   ├── events/                         # v14/v15 style
│   │   ├── __init__.py
│   │   └── sales_order.py
│   └── fixtures/
│       ├── custom_field.json
│       ├── property_setter.json
│       └── workflow.json
```

### hooks.py (v14/v15 Compatible)

```python
# sales_customization/sales_customization/hooks.py
app_name = "sales_customization"
app_title = "Sales Customization"
app_publisher = "Your Company"
app_description = "Custom pricing and approval for Sales"
app_email = "dev@example.com"
app_license = "MIT"

required_apps = ["frappe", "erpnext"]

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "Sales Customization"]]
    },
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "Sales Customization"]]
    },
    {
        "dt": "Workflow",
        "filters": [["document_type", "=", "Sales Order"]]
    },
    {
        "dt": "Workflow State",
        "filters": [["name", "like", "SO %"]]
    },
    {
        "dt": "Workflow Action Master",
        "filters": [["name", "in", ["Approve", "Reject", "Request Discount"]]]
    }
]

# v14/v15 style - works in all versions
doc_events = {
    "Sales Order": {
        "validate": "sales_customization.events.sales_order.validate",
        "on_submit": "sales_customization.events.sales_order.on_submit"
    }
}

# Uncomment for v16 only:
# extend_doctype_class = {
#     "Sales Order": "sales_customization.overrides.sales_order.CustomSalesOrder"
# }
```

### Event Handlers (v14/v15)

```python
# sales_customization/sales_customization/events/sales_order.py
import frappe
from frappe import _


def validate(doc, method):
    """Validate Sales Order with custom rules."""
    check_discount_approval(doc)
    calculate_profit_margin(doc)


def on_submit(doc, method):
    """Actions on Sales Order submit."""
    notify_high_value_order(doc)


def check_discount_approval(doc):
    """Check if discount requires approval."""
    settings = frappe.get_single("Pricing Approval Settings")
    
    if not settings.enable_discount_approval:
        return
    
    max_discount = settings.max_discount_without_approval or 10
    
    for item in doc.items:
        if item.discount_percentage and item.discount_percentage > max_discount:
            if not doc.custom_discount_approved:
                doc.workflow_state = "Pending Discount Approval"
                doc.custom_discount_approval_required = 1
                frappe.msgprint(
                    _("Discount of {0}% on {1} requires approval").format(
                        item.discount_percentage, item.item_code
                    ),
                    alert=True,
                    indicator="orange"
                )


def calculate_profit_margin(doc):
    """Calculate and store profit margin."""
    total_cost = 0
    
    for item in doc.items:
        valuation_rate = frappe.db.get_value(
            "Item",
            item.item_code,
            "valuation_rate"
        ) or 0
        total_cost += valuation_rate * item.qty
    
    if doc.grand_total:
        doc.custom_profit_margin = (
            (doc.grand_total - total_cost) / doc.grand_total * 100
        )


def notify_high_value_order(doc):
    """Send notification for high-value orders."""
    settings = frappe.get_single("Pricing Approval Settings")
    
    if not settings.notify_high_value_orders:
        return
    
    if doc.grand_total >= settings.high_value_threshold:
        frappe.sendmail(
            recipients=settings.notification_email,
            subject=f"High Value Order: {doc.name}",
            message=f"""
                <p>A high-value order has been submitted:</p>
                <p><strong>Order:</strong> {doc.name}</p>
                <p><strong>Customer:</strong> {doc.customer_name}</p>
                <p><strong>Total:</strong> {doc.currency} {doc.grand_total:,.2f}</p>
            """
        )
```

### Override Class (v16)

```python
# sales_customization/sales_customization/overrides/sales_order.py
import frappe
from frappe import _
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder


class CustomSalesOrder(SalesOrder):
    """Extended Sales Order with custom pricing rules."""
    
    def validate(self):
        super().validate()
        self.check_discount_approval()
        self.calculate_profit_margin()
    
    def on_submit(self):
        super().on_submit()
        self.notify_high_value_order()
    
    def check_discount_approval(self):
        """Check if discount requires approval."""
        settings = frappe.get_single("Pricing Approval Settings")
        
        if not settings.enable_discount_approval:
            return
        
        max_discount = settings.max_discount_without_approval or 10
        
        for item in self.items:
            if item.discount_percentage and item.discount_percentage > max_discount:
                if not self.custom_discount_approved:
                    self.workflow_state = "Pending Discount Approval"
                    self.custom_discount_approval_required = 1
    
    def calculate_profit_margin(self):
        """Calculate and store profit margin."""
        total_cost = sum(
            (frappe.db.get_value("Item", item.item_code, "valuation_rate") or 0) * item.qty
            for item in self.items
        )
        
        if self.grand_total:
            self.custom_profit_margin = (
                (self.grand_total - total_cost) / self.grand_total * 100
            )
    
    def notify_high_value_order(self):
        """Send notification for high-value orders."""
        settings = frappe.get_single("Pricing Approval Settings")
        
        if settings.notify_high_value_orders and self.grand_total >= settings.high_value_threshold:
            frappe.sendmail(
                recipients=settings.notification_email,
                subject=f"High Value Order: {self.name}",
                message=f"Order {self.name} for {self.customer_name}: {self.currency} {self.grand_total:,.2f}"
            )
```

---

## Example 4: Data Migration Patch

### Use Case
Migrate from old custom field structure to new DocType.

### File Structure

```
my_app/
└── patches/
    └── v2_0/
        ├── __init__.py
        └── migrate_to_new_structure.py
```

### Migration Patch

```python
# my_app/my_app/patches/v2_0/migrate_to_new_structure.py
"""
Migrate custom fields on Sales Invoice to dedicated child table.

Before: Sales Invoice had custom fields for line-item notes
After: Sales Invoice has child table "SI Custom Note" for notes

This is a [pre_model_sync] patch because we need to read the old
custom field values before they are removed.
"""
import frappe


def execute():
    # Check if migration needed
    if not frappe.db.has_column("Sales Invoice", "custom_line_notes"):
        print("Migration not needed: custom_line_notes column doesn't exist")
        return
    
    # Check if already migrated
    if frappe.db.exists("SI Custom Note", {"parenttype": "Sales Invoice"}):
        print("Migration already done: SI Custom Note records exist")
        return
    
    batch_size = 500
    offset = 0
    total_migrated = 0
    
    while True:
        # Get invoices with notes
        invoices = frappe.db.sql("""
            SELECT name, custom_line_notes
            FROM `tabSales Invoice`
            WHERE custom_line_notes IS NOT NULL
              AND custom_line_notes != ''
            LIMIT %s OFFSET %s
        """, (batch_size, offset), as_dict=True)
        
        if not invoices:
            break
        
        for inv in invoices:
            try:
                migrate_invoice_notes(inv)
                total_migrated += 1
            except Exception as e:
                frappe.log_error(
                    title=f"Migration failed for {inv.name}",
                    message=str(e)
                )
                continue
        
        frappe.db.commit()
        offset += batch_size
        print(f"Migrated {total_migrated} invoices...")
    
    frappe.db.commit()
    print(f"Migration complete: {total_migrated} invoices processed")


def migrate_invoice_notes(invoice):
    """Migrate notes from custom field to child table.
    
    Old format (custom_line_notes):
    "Item A: Check quality\nItem B: Rush order"
    
    New format (SI Custom Note child table):
    - item_code: "Item A", note: "Check quality"
    - item_code: "Item B", note: "Rush order"
    """
    notes_text = invoice.custom_line_notes
    
    # Parse old format
    for line in notes_text.split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        
        item_code, note = line.split(":", 1)
        item_code = item_code.strip()
        note = note.strip()
        
        # Create child record
        frappe.get_doc({
            "doctype": "SI Custom Note",
            "parent": invoice.name,
            "parenttype": "Sales Invoice",
            "parentfield": "custom_notes",
            "item_code": item_code,
            "note": note
        }).db_insert()
```

### patches.txt

```ini
[pre_model_sync]
my_app.patches.v2_0.migrate_to_new_structure
```

---

## Example 5: Fixture Export Configuration

### Complete hooks.py with Fixtures

```python
# my_app/my_app/hooks.py

fixtures = [
    # 1. Custom Fields - filter by module
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My App"]]
    },
    
    # 2. Property Setters - filter by module  
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "My App"]]
    },
    
    # 3. Roles created by this app
    {
        "dt": "Role",
        "filters": [["name", "in", ["My App User", "My App Manager"]]]
    },
    
    # 4. Workflows for our DocTypes
    {
        "dt": "Workflow",
        "filters": [["document_type", "in", ["My DocType", "My Other DocType"]]]
    },
    
    # 5. Workflow States (if custom)
    {
        "dt": "Workflow State",
        "filters": [["name", "like", "My App%"]]
    },
    
    # 6. Print Formats
    {
        "dt": "Print Format",
        "filters": [["module", "=", "My App"]]
    },
    
    # 7. Report (Script Reports)
    {
        "dt": "Report",
        "filters": [["module", "=", "My App"]]
    },
    
    # 8. Web Template (if any)
    {
        "dt": "Web Template",
        "filters": [["module", "=", "My App"]]
    },
    
    # 9. Notification templates
    {
        "dt": "Notification",
        "filters": [["module", "=", "My App"]]
    },
    
    # 10. Our own config DocType - all records
    "My App Settings",
    
    # 11. Lookup table - all records
    "My Category",
    
    # 12. Custom DocPerm for modified permissions
    {
        "dt": "Custom DocPerm",
        "filters": [
            ["parent", "in", ["Sales Invoice", "Sales Order"]],
            ["role", "in", ["My App User", "My App Manager"]]
        ]
    }
]
```

### Export and Verify

```bash
# Export
bench --site mysite export-fixtures --app my_app

# Check exported files
ls -la my_app/my_app/fixtures/
# custom_field.json
# property_setter.json
# role.json
# workflow.json
# my_app_settings.json
# my_category.json

# Verify a fixture file
cat my_app/my_app/fixtures/custom_field.json | python -m json.tool | head -50
```

---

## Quick Reference: App Creation Checklist

```bash
# 1. Create app
bench new-app my_app

# 2. Verify __init__.py
cat my_app/my_app/__init__.py
# Should show: __version__ = "0.0.1"

# 3. Configure pyproject.toml (v15+)
# Edit my_app/pyproject.toml

# 4. Configure hooks.py
# Edit my_app/my_app/hooks.py

# 5. Create modules
# Edit my_app/my_app/modules.txt
# Create module directories with __init__.py

# 6. Install on site
bench --site mysite install-app my_app

# 7. Create DocTypes
bench --site mysite new-doctype "My DocType" --module "My Module"

# 8. Build and migrate
bench --site mysite migrate
bench build --app my_app

# 9. Export fixtures
bench --site mysite export-fixtures --app my_app

# 10. Test on fresh site
bench new-site testsite
bench --site testsite install-app my_app
bench --site testsite migrate
```
