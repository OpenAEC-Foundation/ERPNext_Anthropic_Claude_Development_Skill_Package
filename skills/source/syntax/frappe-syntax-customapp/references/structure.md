# Custom App Directory Structure

> Complete directory structure for Frappe custom apps in v14 and v15.

---

## Full Structure (v15 - pyproject.toml)

```
apps/my_custom_app/
├── README.md                          # App description
├── pyproject.toml                     # Build configuration (v15)
├── my_custom_app/                     # Main Python package
│   ├── __init__.py                    # Package init with __version__
│   ├── hooks.py                       # Frappe integration hooks
│   ├── modules.txt                    # List of modules
│   ├── patches.txt                    # Database migration patches
│   ├── config/                        # Configuration files
│   │   ├── __init__.py
│   │   ├── desktop.py                 # Desktop shortcuts (legacy)
│   │   └── docs.py                    # Documentation configuration
│   ├── my_custom_app/                 # Default module (same name as app)
│   │   ├── __init__.py
│   │   └── doctype/
│   │       └── my_doctype/
│   │           ├── __init__.py
│   │           ├── my_doctype.json
│   │           ├── my_doctype.py
│   │           └── my_doctype.js
│   ├── public/                        # Static assets (client-side)
│   │   ├── css/
│   │   └── js/
│   ├── templates/                     # Jinja templates
│   │   ├── __init__.py
│   │   ├── includes/
│   │   └── pages/
│   │       └── __init__.py
│   └── www/                           # Portal/web pages
└── .git/                              # Git repository
```

---

## Directory Structure (v14 - setup.py)

```
apps/my_custom_app/
├── MANIFEST.in                        # Package manifest
├── README.md
├── license.txt
├── requirements.txt                   # Python dependencies
├── dev-requirements.txt               # Development dependencies
├── setup.py                           # Build configuration (v14)
├── package.json                       # Node dependencies
├── my_custom_app/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   └── [rest identical to v15]
└── my_custom_app.egg-info/            # Generated after install
    ├── PKG-INFO
    ├── SOURCES.txt
    ├── dependency_links.txt
    ├── not-zip-safe
    ├── requires.txt
    └── top_level.txt
```

---

## Required vs Optional Files

| File | v14 | v15 | Description |
|------|:---:|:---:|-------------|
| `pyproject.toml` | ❌ | **Required** | Build and metadata configuration |
| `setup.py` | **Required** | ❌ | Build configuration (legacy) |
| `my_app/__init__.py` | **Required** | **Required** | Package definition with `__version__` |
| `my_app/hooks.py` | **Required** | **Required** | Frappe integration points |
| `my_app/modules.txt` | **Required** | **Required** | Module registration |
| `my_app/patches.txt` | Recommended | Recommended | Migration tracking |
| `README.md` | Recommended | Recommended | Documentation |
| `requirements.txt` | Recommended | ❌ | Replaced by pyproject.toml |
| `my_app/config/` | Optional | Optional | Extra configuration |
| `my_app/public/` | Optional | Optional | Client-side assets |
| `my_app/templates/` | Optional | Optional | Jinja templates |
| `my_app/www/` | Optional | Optional | Portal pages |

---

## Module Directory Structure

```
my_custom_app/
├── my_custom_app/           # Default module
│   ├── __init__.py
│   └── doctype/
│       └── my_doctype/
│           ├── __init__.py
│           ├── my_doctype.py
│           ├── my_doctype.json
│           └── my_doctype.js
├── integrations/            # Extra module
│   ├── __init__.py
│   └── doctype/
│       └── api_settings/
│           └── ...
├── reports/                 # Reports module
│   ├── __init__.py
│   └── report/
│       └── sales_summary/
│           └── ...
└── settings/                # Settings module
    ├── __init__.py
    └── doctype/
        └── app_settings/
            └── ...
```

---

## DocType Directory Structure

```
doctype/my_doctype/
├── __init__.py              # Empty (required)
├── my_doctype.json          # DocType definition (UI-generated)
├── my_doctype.py            # Python controller
├── my_doctype.js            # Client script
├── test_my_doctype.py       # Unit tests (optional)
└── my_doctype_dashboard.py  # Dashboard config (optional)
```

---

## Report Directory Structure

```
report/sales_summary/
├── __init__.py              # Empty
├── sales_summary.json       # Report definition
├── sales_summary.py         # Python (Query/Script Report)
├── sales_summary.js         # Client script (optional)
└── sales_summary.html       # Print format template (optional)
```

---

## Public Assets Structure

```
my_custom_app/
└── public/
    ├── js/
    │   ├── my_custom_app.js      # Main desk JS
    │   ├── website.js            # Website JS
    │   └── sales_invoice.js      # DocType-specific
    ├── css/
    │   ├── my_custom_app.css     # Main desk CSS
    │   └── website.css           # Website CSS
    └── images/
        └── logo.png
```

**Assets URL**: `/assets/my_custom_app/**/*`

---

## Templates Structure

```
my_custom_app/
└── templates/
    ├── __init__.py
    ├── includes/
    │   └── footer.html           # Reusable snippets
    └── pages/
        ├── __init__.py
        └── custom_page.html      # Standalone pages
```

---

## WWW (Portal) Structure

```
my_custom_app/
└── www/
    ├── projects/
    │   ├── index.html            # Template
    │   └── index.py              # Context controller
    └── contact/
        ├── index.html
        └── index.py
```

**URL**: `/projects` → `www/projects/index.html`

---

## Patches Directory Structure

```
my_custom_app/
└── patches/
    ├── __init__.py              # Required
    ├── v1_0/
    │   ├── __init__.py          # Required
    │   ├── migrate_data.py
    │   └── setup_defaults.py
    └── v2_0/
        ├── __init__.py
        └── schema_upgrade.py
```

---

## Config Directory Structure

```
my_custom_app/
└── config/
    ├── __init__.py
    ├── desktop.py               # Module icons (legacy)
    └── docs.py                  # Documentation setup
```

---

## Bench Folder Structure (Context)

```
frappe-bench/
├── apps/                     # All apps here
│   ├── frappe/
│   ├── erpnext/
│   └── my_custom_app/        # Your app
├── sites/
│   ├── apps.txt              # Installed apps on bench
│   └── mysite/
│       ├── site_config.json  # Site-specific config
│       └── public/           # Site uploads
└── env/                      # Python virtual environment
```

---

## Critical Paths

| Component | Path | Importance |
|-----------|------|------------|
| Package init | `my_app/__init__.py` | MUST contain `__version__` |
| Hooks | `my_app/hooks.py` | MUST be in inner package |
| Modules | `my_app/modules.txt` | Registers all modules |
| Patches | `my_app/patches.txt` | Migration scripts |
| Assets | `my_app/public/` | Accessible via `/assets/` |

---

## Creating a New App

```bash
# From frappe-bench directory
bench new-app my_custom_app

# Interactive prompts:
# - App Title
# - App Description
# - App Publisher
# - App Email
# - App Icon (default: 'octicon octicon-file-directory')
# - App Color (default: 'grey')
# - App License (default: 'MIT')
```
