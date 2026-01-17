---
name: erpnext-syntax-customapp
version: 1.0.0
description: Deterministische syntax voor het bouwen van Frappe custom apps inclusief app structuur, pyproject.toml, modules, patches en fixtures
author: OpenAEC Foundation
tags: [erpnext, frappe, custom-app, pyproject, patches, fixtures, modules]
languages: [nl]
frappe_versions: [v14, v15]
---

# ERPNext Custom App Syntax Skill

> Complete syntax voor het bouwen van Frappe custom apps in v14/v15, inclusief build configuratie, module organisatie, patches en fixtures.

---

## Wanneer Deze Skill Gebruiken

GEBRUIK deze skill wanneer je:
- Een nieuwe Frappe/ERPNext custom app aanmaakt
- pyproject.toml of setup.py configureert
- Modules organiseert binnen een app
- Database migratie patches schrijft
- Fixtures configureert voor data export/import
- App dependencies beheert

GEBRUIK NIET voor:
- DocType controllers (gebruik erpnext-syntax-controllers)
- Client Scripts (gebruik erpnext-syntax-clientscripts)
- Server Scripts (gebruik erpnext-syntax-serverscripts)
- Hooks configuratie (gebruik erpnext-syntax-hooks)

---

## App Structuur Overzicht

### v15 (pyproject.toml - Primair)

```
apps/my_custom_app/
├── pyproject.toml                     # Build configuratie
├── README.md
├── my_custom_app/                     # Hoofd package
│   ├── __init__.py                    # MOET __version__ bevatten!
│   ├── hooks.py                       # Frappe integratie
│   ├── modules.txt                    # Module registratie
│   ├── patches.txt                    # Migratie scripts
│   ├── patches/                       # Patch bestanden
│   ├── my_custom_app/                 # Default module
│   │   └── doctype/
│   ├── public/                        # Client assets
│   └── templates/                     # Jinja templates
└── .git/
```

> **Zie**: `references/structure.md` voor volledige directory structuur.

---

## Kritieke Bestanden

### __init__.py (VERPLICHT)

```python
# my_custom_app/__init__.py
__version__ = "0.0.1"
```

**KRITIEK**: Zonder `__version__` faalt de flit build!

### pyproject.toml (v15)

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "my_custom_app"
authors = [
    { name = "Your Company", email = "dev@example.com" }
]
description = "Description of your app"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = []

[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
```

> **Zie**: `references/pyproject-toml.md` voor alle configuratie opties.

---

## Modules

### modules.txt

```
My Custom App
Integrations
Settings
Reports
```

**Regels:**
- Eén module per regel
- Spaties in naam → underscores in directory
- Elke DocType MOET tot een module behoren

### Module Directory

```
my_custom_app/
├── my_custom_app/       # "My Custom App" module
│   ├── __init__.py      # VERPLICHT
│   └── doctype/
├── integrations/        # "Integrations" module
│   ├── __init__.py      # VERPLICHT
│   └── doctype/
└── settings/            # "Settings" module
    ├── __init__.py      # VERPLICHT
    └── doctype/
```

> **Zie**: `references/modules.md` voor module organisatie.

---

## Patches (Migratie Scripts)

### patches.txt met INI Secties

```ini
[pre_model_sync]
# Vóór schema sync - oude velden nog beschikbaar
myapp.patches.v1_0.backup_old_data

[post_model_sync]
# Na schema sync - nieuwe velden beschikbaar
myapp.patches.v1_0.populate_new_fields
myapp.patches.v1_0.cleanup_data
```

### Patch Implementatie

```python
# myapp/patches/v1_0/populate_new_fields.py
import frappe

def execute():
    """Vul nieuwe velden met standaard waarden."""
    
    batch_size = 1000
    offset = 0
    
    while True:
        records = frappe.get_all(
            "MyDocType",
            filters={"new_field": ["is", "not set"]},
            fields=["name"],
            limit_page_length=batch_size,
            limit_start=offset
        )
        
        if not records:
            break
        
        for record in records:
            frappe.db.set_value(
                "MyDocType",
                record.name,
                "new_field",
                "default_value",
                update_modified=False
            )
        
        frappe.db.commit()
        offset += batch_size
```

### Wanneer Pre vs Post Model Sync?

| Situatie | Sectie |
|----------|--------|
| Data uit oud veld migreren | `[pre_model_sync]` |
| Nieuwe velden vullen | `[post_model_sync]` |
| Data cleanup | `[post_model_sync]` |

> **Zie**: `references/patches.md` voor complete patch documentatie.

---

## Fixtures

### hooks.py Configuratie

```python
fixtures = [
    # Alle records
    "Category",
    
    # Met filter
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My Custom App"]]
    },
    
    # Multiple filters
    {
        "dt": "Property Setter",
        "filters": [
            ["module", "=", "My Custom App"],
            ["doc_type", "in", ["Sales Invoice", "Sales Order"]]
        ]
    }
]
```

### Exporteren

```bash
bench --site mysite export-fixtures --app my_custom_app
```

### Veelgebruikte Fixture DocTypes

| DocType | Gebruik |
|---------|---------|
| `Custom Field` | Custom velden op bestaande DocTypes |
| `Property Setter` | Veld properties wijzigen |
| `Role` | Custom rollen |
| `Workflow` | Workflow definities |

> **Zie**: `references/fixtures.md` voor fixture configuratie.

---

## Minimale hooks.py

```python
app_name = "my_custom_app"
app_title = "My Custom App"
app_publisher = "Your Company"
app_description = "Description"
app_email = "dev@example.com"
app_license = "MIT"

required_apps = ["frappe"]  # Of ["frappe", "erpnext"]

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My Custom App"]]}
]
```

---

## App Aanmaken en Installeren

```bash
# Nieuwe app aanmaken
bench new-app my_custom_app

# Installeren op site
bench --site mysite install-app my_custom_app

# Migreren (patches + fixtures)
bench --site mysite migrate

# Assets bouwen
bench build --app my_custom_app
```

---

## Versie Verschillen

| Aspect | v14 | v15 |
|--------|-----|-----|
| Build config | setup.py | pyproject.toml |
| Dependencies | requirements.txt | In pyproject.toml |
| Build backend | setuptools | flit_core |
| Python minimum | >=3.10 | >=3.10 |
| INI patches | ✅ | ✅ |

---

## Kritieke Regels

### ✅ ALTIJD

1. `__version__` in `__init__.py` definiëren
2. `dynamic = ["version"]` in pyproject.toml
3. Modules registreren in `modules.txt`
4. `__init__.py` in ELKE directory
5. Frappe dependencies in `[tool.bench.frappe-dependencies]`
6. Error handling in patches
7. Batch processing voor grote datasets

### ❌ NOOIT

1. Frappe/ERPNext in project dependencies (niet op PyPI)
2. Patches zonder error handling
3. User/transactionele data in fixtures
4. Hardcoded site-specifieke waarden
5. Grote datasets zonder batching

---

## Fixtures vs Patches

| Wat | Fixtures | Patches |
|-----|:--------:|:-------:|
| Custom Fields | ✅ | ❌ |
| Property Setters | ✅ | ❌ |
| Rollen/Workflows | ✅ | ❌ |
| Data transformatie | ❌ | ✅ |
| Data cleanup | ❌ | ✅ |
| Eenmalige migratie | ❌ | ✅ |

---

## Reference Files

| Bestand | Inhoud |
|---------|--------|
| `references/structure.md` | Volledige directory structuur |
| `references/pyproject-toml.md` | Build configuratie opties |
| `references/modules.md` | Module organisatie |
| `references/patches.md` | Migratie scripts |
| `references/fixtures.md` | Data export/import |
| `references/examples.md` | Complete app voorbeelden |
| `references/anti-patterns.md` | Fouten te vermijden |

---

## Zie Ook

- `erpnext-syntax-hooks` - Voor hooks.py configuratie
- `erpnext-syntax-controllers` - Voor DocType controllers
- `erpnext-impl-customapp` - Voor implementatie patronen
