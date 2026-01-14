# Research Document: Custom App Structure (Fase 2.6.1)

> **Doel**: Onderzoeken en documenteren van Frappe custom app basis structuur voor v14/v15.
> **Focus**: App structuur, pyproject.toml, __init__.py, modules, en dependencies.

---

## Bronnen Geraadpleegd

| Bron | URL/Locatie | Type |
|------|-------------|------|
| Frappe Docs - Create an App | docs.frappe.io/framework/user/en/tutorial/create-an-app | Primair |
| Frappe Docs - Apps | docs.frappe.io/framework/user/en/basics/apps | Primair |
| Frappe Docs - Modules | docs.frappe.io/framework/user/en/basics/doctypes/modules | Primair |
| Frappe Docs - Directory Structure | docs.frappe.io/framework/user/en/basics/directory-structure | Primair |
| ERPNext GitHub - pyproject.toml | github.com/frappe/erpnext/blob/develop/pyproject.toml | Verificatie |
| Frappe HRMS GitHub - pyproject.toml | github.com/frappe/hrms pyproject.toml | Verificatie |
| Flit Documentation | github.com/pypa/flit | Verificatie |
| erpnext-vooronderzoek.md | Project bestand | Basis |

---

## 1. APP STRUCTUUR

### Aanmaken van een Nieuwe App

```bash
# Vanuit frappe-bench directory
bench new-app my_custom_app
```

**Interactieve prompts:**
- App Title (default: My Custom App)
- App Description
- App Publisher
- App Email
- App Icon (default: 'octicon octicon-file-directory')
- App Color (default: 'grey')
- App License (default: 'MIT')

### Volledige Directory Structuur (v15 - pyproject.toml)

```
apps/my_custom_app/
â”œâ”€â”€ README.md                          # App beschrijving voor GitHub/PyPI
â”œâ”€â”€ pyproject.toml                     # Build configuratie (v15 primair)
â”œâ”€â”€ my_custom_app/                     # Hoofd Python package
â”‚   â”œâ”€â”€ __init__.py                    # Package init met __version__
â”‚   â”œâ”€â”€ hooks.py                       # Frappe integration hooks
â”‚   â”œâ”€â”€ modules.txt                    # Lijst van modules
â”‚   â”œâ”€â”€ patches.txt                    # Database migratie patches
â”‚   â”œâ”€â”€ config/                        # Configuratie bestanden
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ desktop.py                 # Desktop shortcuts (legacy)
â”‚   â”‚   â””â”€â”€ docs.py                    # Documentatie configuratie
â”‚   â”œâ”€â”€ my_custom_app/                 # Default module (zelfde naam als app)
â”‚   â”‚   â””â”€â”€ __init__.py
â”‚   â”œâ”€â”€ public/                        # Statische assets (client-side)
â”‚   â”‚   â”œâ”€â”€ css/
â”‚   â”‚   â””â”€â”€ js/
â”‚   â”œâ”€â”€ templates/                     # Jinja templates
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ includes/
â”‚   â”‚   â””â”€â”€ pages/
â”‚   â”‚       â””â”€â”€ __init__.py
â”‚   â””â”€â”€ www/                           # Portal/web pagina's
â””â”€â”€ .git/                              # Git repository (auto-created)
```

### Directory Structuur (v14 - setup.py)

```
apps/my_custom_app/
â”œâ”€â”€ MANIFEST.in                        # Package manifest
â”œâ”€â”€ README.md
â”œâ”€â”€ license.txt
â”œâ”€â”€ requirements.txt                   # Python dependencies
â”œâ”€â”€ dev-requirements.txt               # Development dependencies
â”œâ”€â”€ setup.py                           # Build configuratie (v14)
â”œâ”€â”€ package.json                       # Node dependencies
â”œâ”€â”€ my_custom_app/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ hooks.py
â”‚   â”œâ”€â”€ modules.txt
â”‚   â”œâ”€â”€ patches.txt
â”‚   â””â”€â”€ [rest identical to v15]
â””â”€â”€ my_custom_app.egg-info/            # Generated after install
    â”œâ”€â”€ PKG-INFO
    â”œâ”€â”€ SOURCES.txt
    â”œâ”€â”€ dependency_links.txt
    â”œâ”€â”€ not-zip-safe
    â”œâ”€â”€ requires.txt
    â””â”€â”€ top_level.txt
```

### Verplichte vs Optionele Bestanden

| Bestand | Status | Beschrijving |
|---------|--------|--------------|
| `pyproject.toml` | **Verplicht** (v15) | Build en metadata configuratie |
| `setup.py` | **Verplicht** (v14) | Build configuratie (legacy) |
| `my_app/__init__.py` | **Verplicht** | Package definitie met `__version__` |
| `my_app/hooks.py` | **Verplicht** | Frappe integratie punten |
| `my_app/modules.txt` | **Verplicht** | Module registratie |
| `my_app/patches.txt` | Aanbevolen | Migratie tracking |
| `README.md` | Aanbevolen | Documentatie |
| `license.txt` | Optioneel | Licentie bestand |
| `my_app/config/` | Optioneel | Extra configuratie |
| `my_app/public/` | Optioneel | Client-side assets |
| `my_app/templates/` | Optioneel | Jinja templates |
| `my_app/www/` | Optioneel | Portal pagina's |

---

## 2. PYPROJECT.TOML (v15 - Primair)

### Minimale pyproject.toml

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "my_custom_app"
authors = [
    { name = "Your Company", email = "developers@example.com" }
]
description = "Description of your custom app"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = []
```

### Volledige pyproject.toml met Dependencies

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "my_custom_app"
authors = [
    { name = "Your Company", email = "developers@example.com" }
]
description = "Description of your custom app"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]

# Python package dependencies
dependencies = [
    "requests~=2.31.0",
    "pandas~=2.0.0",
]

[project.urls]
Homepage = "https://example.com"
Repository = "https://github.com/your-org/my_custom_app.git"
"Bug Reports" = "https://github.com/your-org/my_custom_app/issues"

# Frappe app dependencies (bench manages these)
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"

# APT dependencies for Frappe Cloud
[deploy.dependencies.apt]
packages = [
    "libmagic1",
]
```

### Build-System Sectie (Verplicht)

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"
```

**Uitleg:**
- Frappe gebruikt **flit_core** als build backend
- `flit_core` leest `__version__` uit `__init__.py` automatisch
- Vereist `dynamic = ["version"]` in project sectie

### Project Sectie - Alle Opties

| Veld | Type | Beschrijving |
|------|------|--------------|
| `name` | string | Package naam (moet matchen met directory) |
| `authors` | list | Auteur(s) met name en email |
| `description` | string | Korte omschrijving |
| `requires-python` | string | Python versie vereiste (v14: `>=3.10`, v15: `>=3.10`, v16: `>=3.14`) |
| `readme` | string | Pad naar README bestand |
| `dynamic` | list | Dynamisch bepaalde velden (altijd `["version"]`) |
| `dependencies` | list | Python package dependencies |
| `license` | string | SPDX license identifier (bijv. "MIT") |
| `keywords` | list | Zoekwoorden voor PyPI |
| `classifiers` | list | PyPI classifiers |

### Dependencies Syntax

```toml
dependencies = [
    # Exacte versie
    "requests==2.31.0",
    
    # Compatibele versie (2.31.x)
    "requests~=2.31.0",
    
    # Minimum versie
    "requests>=2.31.0",
    
    # Versie range
    "requests>=2.28.0,<3.0.0",
    
    # Geen versie restrictie
    "requests",
]
```

**BELANGRIJK**: Frappe/ERPNext dependencies worden NIET in `dependencies` gezet maar in `[tool.bench.frappe-dependencies]` omdat ze niet op PyPI staan.

### Frappe-Specifieke Tool Secties

```toml
# Frappe app versie dependencies
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"

# Ruff linter configuratie
[tool.ruff]
line-length = 110
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "B"]

# Ruff import sorting
[tool.ruff.lint.isort]
known-first-party = ["frappe", "erpnext", "my_custom_app"]

# Frappe Cloud APT dependencies
[deploy.dependencies.apt]
packages = ["ffmpeg", "libmagic1"]
```

---

## 3. SETUP.PY (v14 - Legacy)

### Minimale setup.py

```python
from setuptools import setup, find_packages

setup(
    name="my_custom_app",
    version="0.0.1",
    description="Description of your custom app",
    author="Your Company",
    author_email="developers@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
)
```

### Volledige setup.py met Dependencies

```python
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="my_custom_app",
    version="0.0.1",
    description="Description of your custom app",
    author="Your Company",
    author_email="developers@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.10",
)
```

### requirements.txt (v14)

```
requests==2.31.0
pandas>=2.0.0
```

### dev-requirements.txt (v14)

```
pytest>=7.0.0
black>=23.0.0
ruff>=0.0.280
```

**Noot**: In v14, bij `developer_mode=True` worden dev-requirements.txt dependencies ook geÃ¯nstalleerd.

---

## 4. __INIT__.PY

### Verplichte Structuur

```python
# my_custom_app/__init__.py

__version__ = "0.0.1"
```

**KRITIEK**: De `__version__` variabele is VERPLICHT. Flit leest deze om de package versie te bepalen.

### Optionele Toevoegingen

```python
# my_custom_app/__init__.py

"""My Custom App - A brief description."""

__version__ = "0.0.1"
__title__ = "My Custom App"
__author__ = "Your Company"
__license__ = "MIT"

# Optioneel: imports voor gemakkelijke toegang
# from my_custom_app.api import some_function
```

### Versie Nummering Conventie

| Formaat | Voorbeeld | Gebruik |
|---------|-----------|---------|
| Major.Minor.Patch | `1.2.3` | Stabiele releases |
| Major.Minor.Patch-dev | `1.2.3-dev` | Development versies |
| Major.x.x-develop | `15.x.x-develop` | Branch versies (ERPNext stijl) |

### Module __init__.py Files

Elke module directory vereist ook een `__init__.py` (kan leeg zijn):

```python
# my_custom_app/my_module/__init__.py
# Kan leeg zijn, maakt directory een Python package
```

---

## 5. MODULES

### modules.txt Structuur

```
My Custom App
Integrations
Reports
Settings
```

**Regels:**
- EÃ©n module naam per regel
- Module naam = directory naam met spaties i.p.v. underscores
- Default module heeft dezelfde naam als de app
- Elke DocType MOET tot een module behoren

### Module Directory Structuur

```
my_custom_app/
â”œâ”€â”€ my_custom_app/           # Default module
â”‚   â”œâ”€â”€ __init__.py
â”‚   â””â”€â”€ doctype/
â”‚       â””â”€â”€ my_doctype/
â”‚           â”œâ”€â”€ __init__.py
â”‚           â”œâ”€â”€ my_doctype.py
â”‚           â”œâ”€â”€ my_doctype.json
â”‚           â””â”€â”€ my_doctype.js
â”œâ”€â”€ integrations/            # Extra module
â”‚   â”œâ”€â”€ __init__.py
â”‚   â””â”€â”€ doctype/
â”‚       â””â”€â”€ api_settings/
â”‚           â””â”€â”€ ...
â”œâ”€â”€ reports/                 # Reports module
â”‚   â”œâ”€â”€ __init__.py
â”‚   â””â”€â”€ report/
â”‚       â””â”€â”€ sales_summary/
â”‚           â””â”€â”€ ...
â””â”€â”€ settings/                # Settings module
    â”œâ”€â”€ __init__.py
    â””â”€â”€ doctype/
        â””â”€â”€ app_settings/
            â””â”€â”€ ...
```

### Module Naam naar Directory Mapping

| modules.txt naam | Directory naam |
|------------------|----------------|
| My Custom App | my_custom_app |
| Integrations | integrations |
| Sales Reports | sales_reports |
| HR Settings | hr_settings |

### Module Toevoegen Stappen

1. **Voeg naam toe aan modules.txt:**
   ```
   My Custom App
   New Module
   ```

2. **Maak directory structuur:**
   ```bash
   mkdir -p my_custom_app/new_module/doctype
   touch my_custom_app/new_module/__init__.py
   ```

3. **Bij DocType aanmaken:** Selecteer de module in de Module dropdown

### Module Icoon Configuratie

Modules krijgen automatisch een icoon in de Desk. Custom iconen via `config/desktop.py`:

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
        }
    ]
```

---

## 6. DEPENDENCIES

### Python Package Dependencies

**In pyproject.toml (v15):**
```toml
[project]
dependencies = [
    "requests~=2.31.0",
    "python-dateutil>=2.8.0",
]
```

**In requirements.txt (v14):**
```
requests~=2.31.0
python-dateutil>=2.8.0
```

### Frappe/ERPNext App Dependencies

**BELANGRIJK**: Frappe apps zijn NIET op PyPI gepubliceerd. Gebruik daarom:

```toml
# pyproject.toml
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
```

Deze dependencies worden gecontroleerd door `bench get-app`, niet door pip.

### Node/JavaScript Dependencies

**In package.json:**
```json
{
  "name": "my_custom_app",
  "version": "0.0.1",
  "dependencies": {
    "chart.js": "^4.0.0"
  },
  "devDependencies": {
    "eslint": "^8.0.0"
  }
}
```

### Client-Side Asset Includes

**In hooks.py:**
```python
# Include custom JS/CSS in desk
app_include_js = "/assets/my_custom_app/js/my_custom_app.js"
app_include_css = "/assets/my_custom_app/css/my_custom_app.css"

# Include in website
web_include_js = "/assets/my_custom_app/js/website.js"
web_include_css = "/assets/my_custom_app/css/website.css"

# DocType-specific includes
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js"
}

doctype_list_js = {
    "Sales Invoice": "public/js/sales_invoice_list.js"
}
```

### Locatie van Assets

```
my_custom_app/
â””â”€â”€ public/
    â”œâ”€â”€ js/
    â”‚   â”œâ”€â”€ my_custom_app.js      # Main desk JS
    â”‚   â”œâ”€â”€ website.js            # Website JS
    â”‚   â””â”€â”€ sales_invoice.js      # DocType-specific
    â””â”€â”€ css/
        â”œâ”€â”€ my_custom_app.css     # Main desk CSS
        â””â”€â”€ website.css           # Website CSS
```

Assets zijn toegankelijk via: `/assets/my_custom_app/**/*`

---

## 7. HOOKS.PY BASIS STRUCTUUR

### Minimale hooks.py

```python
app_name = "my_custom_app"
app_title = "My Custom App"
app_publisher = "Your Company"
app_description = "Description of your custom app"
app_email = "developers@example.com"
app_license = "MIT"
app_version = "0.0.1"
```

**Noot**: `app_version` in hooks.py wordt door sommige tools gelezen, maar de autoritaire versie komt uit `__init__.py.__version__`.

### Volledig hooks.py Template

```python
app_name = "my_custom_app"
app_title = "My Custom App"
app_publisher = "Your Company"
app_description = "Description of your custom app"
app_email = "developers@example.com"
app_license = "MIT"

# App includes
app_include_js = "/assets/my_custom_app/js/my_custom_app.js"
app_include_css = "/assets/my_custom_app/css/my_custom_app.css"

# DocType JavaScript
doctype_js = {"Sales Invoice": "public/js/sales_invoice.js"}

# Document Events (zie erpnext-syntax-hooks skill)
doc_events = {}

# Scheduler Events (zie erpnext-syntax-scheduler skill)
scheduler_events = {}

# Fixtures
fixtures = []

# Installation hooks
after_install = "my_custom_app.setup.after_install"
before_uninstall = "my_custom_app.setup.before_uninstall"
```

---

## 8. VERSIE VERSCHILLEN SAMENVATTING

| Aspect | v14 | v15 |
|--------|-----|-----|
| Build config | setup.py | pyproject.toml |
| Dependencies file | requirements.txt | In pyproject.toml |
| Dev dependencies | dev-requirements.txt | Optional in pyproject.toml |
| Build backend | setuptools | flit_core |
| Python minimum | 3.10 | 3.10 (v16: 3.14) |
| Package manifest | MANIFEST.in | Niet nodig |
| Node deps | package.json | package.json |

### Migratie van v14 naar v15

1. Maak pyproject.toml aan met juiste structuur
2. Verplaats dependencies van requirements.txt naar pyproject.toml
3. Verwijder setup.py, MANIFEST.in, requirements.txt (optioneel)
4. Controleer dat `__version__` in `__init__.py` staat

---

## 9. APP INSTALLATIE WORKFLOW

### Nieuwe App

```bash
# 1. Maak app
bench new-app my_custom_app

# 2. App wordt automatisch geÃ¯nstalleerd in bench
# (pip install -e ./apps/my_custom_app)

# 3. Installeer op site
bench --site mysite install-app my_custom_app

# 4. Migreer database
bench --site mysite migrate
```

### Bestaande App van Git

```bash
# 1. Haal app op
bench get-app https://github.com/org/my_custom_app

# 2. Installeer op site
bench --site mysite install-app my_custom_app

# 3. Migreer
bench --site mysite migrate
```

### App Bestanden Locatie

```
frappe-bench/
â”œâ”€â”€ apps/                     # Alle apps hier
â”‚   â”œâ”€â”€ frappe/
â”‚   â”œâ”€â”€ erpnext/
â”‚   â””â”€â”€ my_custom_app/        # Jouw app
â”œâ”€â”€ sites/
â”‚   â”œâ”€â”€ apps.txt              # Lijst van geÃ¯nstalleerde apps op bench
â”‚   â””â”€â”€ mysite/
â”‚       â””â”€â”€ site_config.json  # Site-specifieke config
â””â”€â”€ env/                      # Python virtual environment
```

---

## 10. ANTI-PATTERNS EN COMMON MISTAKES

### âŒ __version__ Ontbreekt

```python
# FOUT - geen version
# my_custom_app/__init__.py
pass
```

```python
# GOED
# my_custom_app/__init__.py
__version__ = "0.0.1"
```

### âŒ Frappe in pyproject.toml dependencies

```toml
# FOUT - frappe staat niet op PyPI
[project]
dependencies = [
    "frappe>=15.0.0",
]
```

```toml
# GOED - gebruik tool.bench sectie
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
```

### âŒ Module niet in modules.txt

```
# modules.txt VERGETEN om new_module toe te voegen
My Custom App
# New Module  <- ontbreekt!
```

DocTypes in niet-geregistreerde modules werken niet correct.

### âŒ Directory naam mismatch

```
# FOUT - pyproject.toml zegt "my_custom_app" maar directory is "my-custom-app"
[project]
name = "my_custom_app"
```

Package naam MOET exact matchen met directory naam.

### âŒ Verkeerde hooks.py locatie

```
# FOUT - hooks.py in verkeerde directory
apps/my_custom_app/hooks.py  # Moet in inner package

# GOED
apps/my_custom_app/my_custom_app/hooks.py
```

---

## Samenvatting voor Skill Creatie

### Key Learnings

1. **v15 gebruikt pyproject.toml** met flit_core als build backend
2. **__version__** in `__init__.py` is VERPLICHT
3. **modules.txt** registreert alle modules - DocTypes moeten tot een module behoren
4. **Frappe dependencies** gaan in `[tool.bench.frappe-dependencies]`, niet in project dependencies
5. **Directory structuur** is strikt: app_name/app_name/hooks.py
6. **Assets** in public/ zijn toegankelijk via /assets/app_name/

### Skill References te Maken

1. `structure.md` - Volledige directory structuur met uitleg
2. `pyproject-toml.md` - Alle configuratie opties voor pyproject.toml
3. `modules.md` - Module organisatie en best practices

### Versie Compatibiliteit

- v14: setup.py + requirements.txt
- v15: pyproject.toml + flit_core (primair voor deze skill)
- v16: pyproject.toml + Python 3.14 requirement
