# Module Organization

> Modules structure your app into logical components. Every DocType MUST belong to a module.

---

## modules.txt Structure

**Location**: `{app}/{app}/modules.txt`

```
My Custom App
Integrations
Reports
Settings
```

**Rules:**
- One module name per line
- Module name = directory name with spaces instead of underscores
- Default module has the same name as the app
- Every DocType MUST belong to a registered module

---

## Module Name to Directory Mapping

| modules.txt | Directory | Example DocType Path |
|-------------|-----------|---------------------|
| My Custom App | my_custom_app | `.../my_custom_app/doctype/...` |
| Integrations | integrations | `.../integrations/doctype/...` |
| Sales Reports | sales_reports | `.../sales_reports/report/...` |
| HR Settings | hr_settings | `.../hr_settings/doctype/...` |

**Conversion rule**: Spaces → underscores, lowercase

---

## Module Directory Structure

```
my_custom_app/
├── modules.txt                  # Module registration
├── my_custom_app/               # Default module
│   ├── __init__.py              # REQUIRED
│   └── doctype/
│       └── my_doctype/
├── integrations/                # Extra module
│   ├── __init__.py              # REQUIRED
│   └── doctype/
│       └── api_settings/
├── reports/                     # Reports module
│   ├── __init__.py              # REQUIRED
│   └── report/
│       └── sales_summary/
└── settings/                    # Settings module
    ├── __init__.py              # REQUIRED
    └── doctype/
        └── app_settings/
```

---

## Adding a Module

### Step 1: Add to modules.txt

```
My Custom App
New Module
```

### Step 2: Create directory structure

```bash
mkdir -p my_custom_app/new_module/doctype
touch my_custom_app/new_module/__init__.py
```

### Step 3: Select module when creating DocType

When creating a new DocType via the UI:
- Select the correct module in the "Module" dropdown

---

## Module Components

Each module can contain:

| Component | Directory | Description |
|-----------|-----------|-------------|
| DocTypes | `doctype/` | Data models |
| Reports | `report/` | Query/Script Reports |
| Print Formats | `print_format/` | Print templates |
| Dashboards | `dashboard/` | Dashboard definitions |
| Workspace | `workspace/` | Module workspace |

---

## Module Icon Configuration

### Via config/desktop.py (Legacy)

```python
# my_custom_app/config/desktop.py

def get_data():
    return [
        {
            "module_name": "My Custom App",
            "color": "blue",
            "icon": "octicon octicon-package",
            "type": "module",
            "label": "My Custom App"
        },
        {
            "module_name": "Integrations",
            "color": "green",
            "icon": "octicon octicon-plug",
            "type": "module",
            "label": "Integrations"
        }
    ]
```

### Available Icons

Frappe supports Octicons: `octicon octicon-{name}`

Commonly used:
- `octicon-package` - Generic module
- `octicon-plug` - Integrations
- `octicon-graph` - Reports/Analytics
- `octicon-gear` - Settings
- `octicon-file` - Documents
- `octicon-person` - Users/HR

---

## Module Best Practices

### Logical Grouping

```
# GOOD - functional grouping
My Custom App          # Core functionality
Integrations           # External system connections
Settings               # Configuration
Reports                # Reporting
```

```
# AVOID - too generic or too specific
Module 1               # Unclear name
Everything             # Too broad
Customer Invoice PDF   # Too specific (not a module)
```

### Recommended Module Structure

| Module Type | Purpose | Examples |
|-------------|---------|----------|
| Core (app name) | Main DocTypes | Project, Task |
| Settings | Configuration | App Settings, Defaults |
| Integrations | API connections | API Settings, Webhooks |
| Reports | Reporting | Sales Summary, Analytics |
| Utilities | Helper functions | Import/Export tools |

---

## Module in DocType JSON

When you create a DocType, the module is stored:

```json
{
    "doctype": "DocType",
    "name": "My DocType",
    "module": "My Custom App",
    ...
}
```

**CRITICAL**: If module is not in modules.txt, the DocType won't work correctly.

---

## Module Workspace (v15+)

Workspaces replace the old desktop icons:

```json
// my_custom_app/my_custom_app/workspace/my_custom_app/my_custom_app.json
{
    "doctype": "Workspace",
    "name": "My Custom App",
    "module": "My Custom App",
    "label": "My Custom App",
    "is_standard": 1,
    "links": [
        {
            "label": "Documents",
            "links": [
                {
                    "type": "doctype",
                    "name": "My DocType",
                    "label": "My DocType"
                }
            ]
        }
    ]
}
```

---

## Critical Rules

### ✅ ALWAYS

1. Register each module in modules.txt
2. Include `__init__.py` in every module directory
3. Use module name consistently (with spaces in modules.txt)
4. Assign DocTypes to the correct module

### ❌ NEVER

1. Create DocTypes in unregistered modules
2. Use spaces in module directory names
3. Have empty lines or trailing spaces in modules.txt
4. Change module names after DocTypes have been created

---

## Troubleshooting

### DocType not visible

1. Check if module is in `modules.txt`
2. Check if module name is spelled correctly
3. Run `bench clear-cache`

### Module icon not visible

1. Check `config/desktop.py` syntax
2. Verify module_name matches exactly
3. Run `bench build` and `bench clear-cache`

### Import errors

1. Verify `__init__.py` in every directory
2. Check module name conversion (spaces → underscores)
