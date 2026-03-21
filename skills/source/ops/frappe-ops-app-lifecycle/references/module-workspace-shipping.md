# Module Definition & Workspace Shipping

How to configure modules within a Frappe app and ship workspaces as part of the app distribution.

> For workspace builder UI, components, and customization, see skill `frappe-impl-workspace`.
> This reference focuses on the **ops side**: module registration, directory layout, and shipping.

---

## 1. Module Def DocType

Every Frappe module is represented by a **Module Def** document. When you create a module in developer mode, Frappe creates a `module.json` file in the module directory.

### Module Def Fields

| Field | Type | Purpose |
|---|---|---|
| `module_name` | Data | Human-readable name (e.g., "Inventory Management") |
| `app_name` | Data | The app this module belongs to (e.g., "my_custom_app") |
| `custom` | Check | 0 for standard modules shipped with an app, 1 for user-created |
| `restrict_to_domain` | Link → Domain | Limit module visibility to a specific domain |

### module.json Example

```json
{
    "app_name": "my_custom_app",
    "category": "",
    "color": "",
    "custom": 0,
    "docstatus": 0,
    "doctype": "Module Def",
    "icon": "",
    "idx": 0,
    "module_name": "Inventory Management",
    "name": "Inventory Management",
    "restrict_to_domain": ""
}
```

This file lives at: `my_custom_app/inventory_management/module.json`

---

## 2. modules.txt — Module Registration

The `modules.txt` file in the app's inner package directory is the **single source of truth** for which modules an app provides. Frappe reads this file during installation to create Module Def documents.

### Location

```
apps/my_custom_app/my_custom_app/modules.txt
```

### Format

One module name per line, matching the `module_name` field exactly:

```
Inventory Management
Warehouse Operations
Custom Reports
```

### Rules

- ALWAYS add a new line to `modules.txt` when creating a new module
- The name in `modules.txt` MUST match the `module_name` in `module.json`
- The directory name is the snake_case version of the module name (e.g., `inventory_management/`)
- Order in `modules.txt` determines the order modules appear in the module list
- NEVER remove a module from `modules.txt` if DocTypes depend on it — this breaks installations

### What Happens on Install

When `bench --site mysite install-app my_custom_app` runs:

1. Frappe reads `modules.txt`
2. For each module name, creates a `Module Def` document (if it does not exist)
3. Sets `app_name` to the installing app
4. Sets `custom = 0` (standard module)

---

## 3. Module Directory Structure

Each module declared in `modules.txt` MUST have a corresponding directory:

```
my_custom_app/
├── modules.txt
├── inventory_management/
│   ├── __init__.py
│   ├── module.json              # Module Def export
│   ├── doctype/                 # DocTypes belonging to this module
│   │   ├── warehouse_item/
│   │   │   ├── warehouse_item.json
│   │   │   ├── warehouse_item.py
│   │   │   └── warehouse_item.js
│   │   └── stock_entry_custom/
│   │       └── ...
│   ├── report/                  # Reports belonging to this module
│   │   └── stock_summary/
│   │       └── ...
│   ├── workspace/               # Workspaces for this module
│   │   └── inventory_management/
│   │       └── inventory_management.json
│   ├── page/                    # Custom pages
│   ├── dashboard_chart/         # Dashboard chart definitions
│   └── number_card/             # Number card definitions
```

### DocType ↔ Module Association

Every DocType belongs to exactly one module. The `module` field in the DocType JSON determines this:

```json
{
    "doctype": "DocType",
    "name": "Warehouse Item",
    "module": "Inventory Management",
    ...
}
```

ALWAYS set the `module` field to a module declared in your app's `modules.txt`. If you set it to another app's module (e.g., "Stock"), the DocType will be exported to that app's directory instead of yours.

---

## 4. Module Icons and Colors

Module Def supports `icon` and `color` fields, but these are primarily cosmetic in v14+ where Workspace icons have replaced module-based navigation.

### Setting via module.json

```json
{
    "module_name": "Inventory Management",
    "icon": "stock",
    "color": "#3498db"
}
```

### Where Icons Appear

- **Workspace sidebar**: The workspace's own `icon` field takes precedence
- **Module-based views** (legacy): Uses Module Def icon
- **Search results**: Module icon shown next to DocType results

In practice, ALWAYS set the icon on the **Workspace** document rather than relying on Module Def. The workspace icon is what users actually see in the sidebar.

---

## 5. Module-Based Permissions

Modules participate in the permission system through **Domain restrictions** and **Module visibility**:

### Domain Restriction

```json
{
    "module_name": "Manufacturing",
    "restrict_to_domain": "Manufacturing"
}
```

When a domain is deactivated, all modules restricted to that domain become invisible. Their DocTypes and workspaces are hidden from navigation.

### Module Visibility per User

Users can enable/disable modules in their user settings (**Setup > User > Module Access**). This controls:

- Which modules appear in the sidebar
- Which workspaces are visible
- Which module-specific search results appear

This does NOT override DocType-level permissions. A user with read access to a DocType can still access it via URL even if the module is hidden.

### Role-Based Module Access

Module visibility can also be controlled through the **Block Module** DocType:

```python
# Programmatically block a module for a user
frappe.get_doc({
    "doctype": "Block Module",
    "parent": "user@example.com",
    "parenttype": "User",
    "parentfield": "block_modules",
    "module": "Inventory Management"
}).insert()
```

---

## 6. Workspace Shipping — Ops Perspective

This section covers the operational aspects of shipping workspaces. For workspace builder UI details, see `frappe-impl-workspace` and its reference `references/shipping-with-app.md`.

### Directory Convention

```
{app_name}/{module_snake_case}/workspace/{workspace_snake_case}/{workspace_snake_case}.json
```

Example:
```
my_custom_app/inventory_management/workspace/inventory_dashboard/inventory_dashboard.json
```

### Auto-Export in Developer Mode

When `developer_mode = 1`:

1. Edit the workspace in the Workspace Builder UI
2. Click **Save**
3. Frappe writes the JSON to the app directory based on the workspace's `module` field
4. The file path is: `{app}/{module}/workspace/{name}/{name}.json`

ALWAYS verify the `module` field belongs to YOUR app. If it points to another app's module, the JSON exports to that app's directory.

### Manual Export

```bash
# In bench console
bench --site mysite console
>>> ws = frappe.get_doc("Workspace", "Inventory Dashboard")
>>> ws.export_doc()
```

### Shipping Dependent Documents

Workspace JSON references Number Cards, Dashboard Charts, and Custom HTML Blocks **by name**. These documents do NOT auto-export with the workspace.

ALWAYS ship dependencies using fixtures in `hooks.py`:

```python
# hooks.py
fixtures = [
    {
        "dt": "Number Card",
        "filters": [["module", "=", "Inventory Management"]]
    },
    {
        "dt": "Dashboard Chart",
        "filters": [["module", "=", "Inventory Management"]]
    },
    {
        "dt": "Custom HTML Block",
        "filters": [["name", "in", [
            "Inventory Overview Widget",
            "Stock Alert Panel"
        ]]]
    }
]
```

Then export:

```bash
bench --site mysite export-fixtures
# Creates: my_custom_app/fixtures/number_card.json
# Creates: my_custom_app/fixtures/dashboard_chart.json
# Creates: my_custom_app/fixtures/custom_html_block.json
```

### Installation Order

Frappe processes documents in this order during `install-app`:

1. **Module Def** documents (from `modules.txt` and `module.json`)
2. **DocTypes** and their schemas
3. **Fixtures** (Number Cards, Charts, Custom Blocks from `hooks.py`)
4. **Workspaces** (from `workspace/` directories)

This order guarantees dependencies exist before the workspace references them.

### ALWAYS Run After Changes

```bash
# After modifying workspace or its dependencies
bench --site mysite export-fixtures      # Export fixture changes
bench build --app my_custom_app          # Rebuild if JS assets changed
git -C apps/my_custom_app add -A         # Stage all changes
```

### Common Pitfalls

| Mistake | Result | Fix |
|---|---|---|
| Module not in `modules.txt` | Workspace has no parent module, export fails | Add module to `modules.txt`, run `bench migrate` |
| Forgot `export-fixtures` | Number Cards/Charts missing on target site | Run `bench export-fixtures` and commit JSON files |
| Workspace `module` points to another app | JSON exported to wrong app directory | Change workspace's `module` to your own module |
| `for_user` set in workspace JSON | Workspace is private, invisible to other users | Remove `for_user` field from the JSON |
| Fixture filter too broad | Exports other apps' Number Cards/Charts | Use module or name-based filters |

---

## 7. Complete Module + Workspace Shipping Checklist

- [ ] Module name added to `modules.txt`
- [ ] Module directory exists with `__init__.py` and `module.json`
- [ ] All DocTypes have correct `module` field pointing to your module
- [ ] Workspace JSON exists at `{module}/workspace/{name}/{name}.json`
- [ ] Workspace `module` field matches your module
- [ ] Workspace `for_user` is NOT set
- [ ] All Number Cards referenced by workspace are in fixtures
- [ ] All Dashboard Charts referenced by workspace are in fixtures
- [ ] All Custom HTML Blocks referenced by workspace are in fixtures
- [ ] `bench export-fixtures` has been run
- [ ] Fixture JSON files are committed
- [ ] Tested on a fresh site: `bench new-site test && bench install-app my_custom_app`
- [ ] Workspace renders correctly after `bench migrate` on the test site
