# Shipping Workspaces with a Custom App

Complete guide for packaging workspaces and their dependencies for distribution.

---

## Directory Structure

Frappe expects workspace JSON files in a specific location within your app:

```
myapp/
├── mymodule/
│   ├── workspace/
│   │   └── my_workspace/
│   │       └── my_workspace.json
│   └── module.json
├── hooks.py
└── fixtures/          # For Number Cards, Charts, Custom Blocks
```

### Naming Convention

- Directory name = workspace name (snake_case)
- JSON file name = workspace name (snake_case)
- The `name` field inside the JSON MUST match the directory/file name
- NEVER use spaces in directory or file names

---

## JSON File Format

The workspace JSON is a standard Frappe document export. Key fields:

```json
{
    "name": "my_workspace",
    "doctype": "Workspace",
    "label": "My Workspace",
    "module": "My Module",
    "icon": "chart-line",
    "type": "Workspace",
    "sequence_id": 10,
    "content": "[{\"id\":\"abc123\",\"type\":\"header\",\"data\":{\"text\":\"Overview\",\"col\":12}}]",
    "charts": [
        {"chart": "My Chart Name"}
    ],
    "shortcuts": [
        {
            "label": "New Order",
            "type": "DocType",
            "link_to": "Sales Order",
            "color": "Blue"
        }
    ],
    "links": [
        {
            "type": "Card Break",
            "label": "Reports"
        },
        {
            "type": "Link",
            "label": "Sales Analytics",
            "link_to": "Sales Analytics",
            "link_type": "Report"
        }
    ],
    "number_cards": [
        {"number_card_name": "Open Orders"}
    ],
    "custom_blocks": [
        {"custom_block_name": "My Custom Block"}
    ],
    "quick_lists": [],
    "roles": [
        {"role": "Sales Manager"}
    ]
}
```

### Critical Notes on the JSON

- The `content` field is a **stringified JSON array** (JSON within JSON)
- Child table arrays (`charts`, `shortcuts`, `links`, etc.) MUST be consistent with `content`
- NEVER include `for_user` in shipped workspaces — it makes the workspace private
- NEVER include `owner` or `modified_by` fields — Frappe sets these on install

---

## Auto-Export in Developer Mode

When `developer_mode = 1` in `site_config.json`:

1. Open the workspace in Workspace Builder
2. Make changes and click **Save**
3. Frappe automatically writes the JSON to your app directory
4. The file path is determined by the workspace's `module` field

### Requirements

- The workspace's `module` MUST belong to your app
- The app MUST be installed on the site
- Developer mode MUST be enabled

### Manual Export (if auto-export fails)

```python
# In bench console
workspace = frappe.get_doc("Workspace", "My Workspace")
workspace.export_doc()
```

---

## Shipping Dependencies

### The Problem

A workspace JSON references Number Cards, Dashboard Charts, and Custom HTML Blocks **by name**. These are separate DocType documents that do NOT auto-export with the workspace.

If you ship only the workspace JSON, the referenced components will be missing on the target site, resulting in empty blocks or errors.

### Solution: Use Fixtures

Add dependent documents to `hooks.py`:

```python
# hooks.py

fixtures = [
    # Number Cards for your module
    {
        "dt": "Number Card",
        "filters": [["module", "=", "My Module"]]
    },
    # Dashboard Charts for your module
    {
        "dt": "Dashboard Chart",
        "filters": [["module", "=", "My Module"]]
    },
    # Custom HTML Blocks (filter by specific names)
    {
        "dt": "Custom HTML Block",
        "filters": [["name", "in", [
            "My Status Widget",
            "My KPI Panel"
        ]]]
    }
]
```

### Exporting Fixtures

```bash
# Export all fixtures defined in hooks.py
bench --site mysite.local export-fixtures

# This creates JSON files in:
# myapp/fixtures/number_card.json
# myapp/fixtures/dashboard_chart.json
# myapp/fixtures/custom_html_block.json
```

### Import Order on Installation

Frappe processes in this order during `bench --site mysite.local install-app myapp`:

1. Module definitions (`module.json`)
2. DocTypes and their configurations
3. **Fixtures** (Number Cards, Charts, Custom Blocks)
4. **Workspaces** (from `workspace/` directories)

This order ensures dependencies exist before the workspace references them.

---

## Alternative: Programmatic Setup in after_install

For complex setups, use a Python hook:

```python
# hooks.py
after_install = "myapp.setup.install.after_install"

# myapp/setup/install.py
import frappe
import json

def after_install():
    create_number_cards()
    create_dashboard_charts()
    # Workspace JSON is auto-imported — no need to create it here

def create_number_cards():
    if not frappe.db.exists("Number Card", "Active Projects"):
        card = frappe.new_doc("Number Card")
        card.label = "Active Projects"
        card.document_type = "Project"
        card.function = "Count"
        card.filters_json = json.dumps([["Project", "status", "=", "Open"]])
        card.is_public = 1
        card.insert(ignore_permissions=True)
```

### When to Use after_install vs Fixtures

| Approach | Use When |
|----------|----------|
| **Fixtures** | Simple documents that don't need conditional logic |
| **after_install** | Complex setup with conditions, defaults based on site config |
| **Both** | Fixtures for static data + after_install for dynamic setup |

---

## Update / Migration Strategy

### On App Update (`bench --site mysite.local migrate`)

- Workspace JSON: **Auto-reimported** (overwrites existing)
- Fixtures: **Auto-reimported** based on hooks.py definition
- Custom user modifications to public workspaces: **Overwritten** on migrate

### Preserving User Customizations

Users who want to customize a shipped workspace should:
1. Duplicate the workspace (creates a private copy)
2. Customize the private copy
3. The original public workspace will update on migration without affecting the copy

### Version-Specific Workspace Updates

```python
# hooks.py — use after_migrate for version-aware updates
after_migrate = ["myapp.setup.migrate.after_migrate"]

# myapp/setup/migrate.py
def after_migrate():
    # Check if new components need to be added
    if not frappe.db.exists("Number Card", "New KPI Card"):
        # Create the new dependency
        create_new_kpi_card()
```

---

## Checklist: Shipping a Complete Workspace

- [ ] Workspace JSON exists at `myapp/mymodule/workspace/name/name.json`
- [ ] `module` field is set to your app's module
- [ ] `for_user` is NOT set (would make it private)
- [ ] `sequence_id` is reasonable (not hardcoded to 0 or 1)
- [ ] All referenced Number Cards are in fixtures
- [ ] All referenced Dashboard Charts are in fixtures
- [ ] All referenced Custom HTML Blocks are in fixtures
- [ ] `bench export-fixtures` has been run after any changes
- [ ] Fixture JSON files are committed to version control
- [ ] Tested on a fresh site with `bench install-app`
- [ ] Verified workspace renders correctly after `bench migrate`
