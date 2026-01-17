# Custom App Directory Structuur

> Complete directory structuur voor Frappe custom apps in v14 en v15.

---

## Volledige Structuur (v15 - pyproject.toml)

```
apps/my_custom_app/
├── README.md                          # App beschrijving
├── pyproject.toml                     # Build configuratie (v15)
├── my_custom_app/                     # Hoofd Python package
│   ├── __init__.py                    # Package init met __version__
│   ├── hooks.py                       # Frappe integration hooks
│   ├── modules.txt                    # Lijst van modules
│   ├── patches.txt                    # Database migratie patches
│   ├── config/                        # Configuratie bestanden
│   │   ├── __init__.py
│   │   ├── desktop.py                 # Desktop shortcuts (legacy)
│   │   └── docs.py                    # Documentatie configuratie
│   ├── my_custom_app/                 # Default module (zelfde naam als app)
│   │   ├── __init__.py
│   │   └── doctype/
│   │       └── my_doctype/
│   │           ├── __init__.py
│   │           ├── my_doctype.json
│   │           ├── my_doctype.py
│   │           └── my_doctype.js
│   ├── public/                        # Statische assets (client-side)
│   │   ├── css/
│   │   └── js/
│   ├── templates/                     # Jinja templates
│   │   ├── __init__.py
│   │   ├── includes/
│   │   └── pages/
│   │       └── __init__.py
│   └── www/                           # Portal/web pagina's
└── .git/                              # Git repository
```

---

## Directory Structuur (v14 - setup.py)

```
apps/my_custom_app/
├── MANIFEST.in                        # Package manifest
├── README.md
├── license.txt
├── requirements.txt                   # Python dependencies
├── dev-requirements.txt               # Development dependencies
├── setup.py                           # Build configuratie (v14)
├── package.json                       # Node dependencies
├── my_custom_app/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   └── [rest identiek aan v15]
└── my_custom_app.egg-info/            # Generated after install
    ├── PKG-INFO
    ├── SOURCES.txt
    ├── dependency_links.txt
    ├── not-zip-safe
    ├── requires.txt
    └── top_level.txt
```

---

## Verplichte vs Optionele Bestanden

| Bestand | v14 | v15 | Beschrijving |
|---------|:---:|:---:|--------------|
| `pyproject.toml` | ❌ | **Verplicht** | Build en metadata configuratie |
| `setup.py` | **Verplicht** | ❌ | Build configuratie (legacy) |
| `my_app/__init__.py` | **Verplicht** | **Verplicht** | Package definitie met `__version__` |
| `my_app/hooks.py` | **Verplicht** | **Verplicht** | Frappe integratie punten |
| `my_app/modules.txt` | **Verplicht** | **Verplicht** | Module registratie |
| `my_app/patches.txt` | Aanbevolen | Aanbevolen | Migratie tracking |
| `README.md` | Aanbevolen | Aanbevolen | Documentatie |
| `requirements.txt` | Aanbevolen | ❌ | Vervangen door pyproject.toml |
| `my_app/config/` | Optioneel | Optioneel | Extra configuratie |
| `my_app/public/` | Optioneel | Optioneel | Client-side assets |
| `my_app/templates/` | Optioneel | Optioneel | Jinja templates |
| `my_app/www/` | Optioneel | Optioneel | Portal pagina's |

---

## Module Directory Structuur

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

## DocType Directory Structuur

```
doctype/my_doctype/
├── __init__.py              # Leeg (verplicht)
├── my_doctype.json          # DocType definitie (UI-generated)
├── my_doctype.py            # Python controller
├── my_doctype.js            # Client script
├── test_my_doctype.py       # Unit tests (optioneel)
└── my_doctype_dashboard.py  # Dashboard config (optioneel)
```

---

## Report Directory Structuur

```
report/sales_summary/
├── __init__.py              # Leeg
├── sales_summary.json       # Report definitie
├── sales_summary.py         # Python (Query/Script Report)
├── sales_summary.js         # Client script (optioneel)
└── sales_summary.html       # Print format template (optioneel)
```

---

## Public Assets Structuur

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

## Templates Structuur

```
my_custom_app/
└── templates/
    ├── __init__.py
    ├── includes/
    │   └── footer.html           # Herbruikbare snippets
    └── pages/
        ├── __init__.py
        └── custom_page.html      # Standalone pagina's
```

---

## WWW (Portal) Structuur

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

## Patches Directory Structuur

```
my_custom_app/
└── patches/
    ├── __init__.py              # Verplicht
    ├── v1_0/
    │   ├── __init__.py          # Verplicht
    │   ├── migrate_data.py
    │   └── setup_defaults.py
    └── v2_0/
        ├── __init__.py
        └── schema_upgrade.py
```

---

## Config Directory Structuur

```
my_custom_app/
└── config/
    ├── __init__.py
    ├── desktop.py               # Module icons (legacy)
    └── docs.py                  # Documentatie setup
```

---

## Bench Folder Structuur (Context)

```
frappe-bench/
├── apps/                     # Alle apps hier
│   ├── frappe/
│   ├── erpnext/
│   └── my_custom_app/        # Jouw app
├── sites/
│   ├── apps.txt              # Geïnstalleerde apps op bench
│   └── mysite/
│       ├── site_config.json  # Site-specifieke config
│       └── public/           # Site uploads
└── env/                      # Python virtual environment
```

---

## Kritieke Paden

| Component | Pad | Belang |
|-----------|-----|--------|
| Package init | `my_app/__init__.py` | MOET `__version__` bevatten |
| Hooks | `my_app/hooks.py` | MOET in inner package |
| Modules | `my_app/modules.txt` | Registreert alle modules |
| Patches | `my_app/patches.txt` | Migratie scripts |
| Assets | `my_app/public/` | Toegankelijk via `/assets/` |

---

## Aanmaken Nieuwe App

```bash
# Vanuit frappe-bench directory
bench new-app my_custom_app

# Interactieve prompts:
# - App Title
# - App Description
# - App Publisher
# - App Email
# - App Icon (default: 'octicon octicon-file-directory')
# - App Color (default: 'grey')
# - App License (default: 'MIT')
```
