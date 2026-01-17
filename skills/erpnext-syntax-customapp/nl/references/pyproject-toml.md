# Build Configuratie: pyproject.toml en setup.py

> Complete configuratie voor Frappe app packaging in v14 (setup.py) en v15 (pyproject.toml).

---

## pyproject.toml (v15 - Primair)

### Minimale Configuratie

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

---

### Volledige Configuratie

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
license = "MIT"
keywords = ["frappe", "erpnext", "custom-app"]

# Python package dependencies (NOT Frappe/ERPNext!)
dependencies = [
    "requests~=2.31.0",
    "pandas~=2.0.0",
]

classifiers = [
    "Development Status :: 4 - Beta",
    "Framework :: Frappe",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
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
packages = ["libmagic1", "ffmpeg"]

# Ruff linter configuratie
[tool.ruff]
line-length = 110
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "B"]

[tool.ruff.lint.isort]
known-first-party = ["frappe", "erpnext", "my_custom_app"]
```

---

## Sectie Details

### [build-system] (VERPLICHT)

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"
```

| Veld | Waarde | Uitleg |
|------|--------|--------|
| `requires` | `["flit_core >=3.4,<4"]` | Frappe standaard build tool |
| `build-backend` | `"flit_core.buildapi"` | Flit leest `__version__` uit `__init__.py` |

**KRITIEK**: Flit vereist `dynamic = ["version"]` in [project] sectie.

---

### [project] Velden

| Veld | Type | Verplicht | Beschrijving |
|------|------|:---------:|--------------|
| `name` | string | ✅ | Package naam (MOET matchen met directory) |
| `authors` | list | ✅ | Auteur(s) met name en email |
| `description` | string | ✅ | Korte omschrijving |
| `requires-python` | string | ✅ | Python versie (`>=3.10` voor v14/v15) |
| `readme` | string | Aanbevolen | Pad naar README bestand |
| `dynamic` | list | ✅ | ALTIJD `["version"]` voor flit |
| `dependencies` | list | Optioneel | Python package dependencies |
| `license` | string | Optioneel | SPDX license identifier |
| `keywords` | list | Optioneel | Zoekwoorden |
| `classifiers` | list | Optioneel | PyPI classifiers |

---

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
    
    # Geen versie restrictie (VERMIJDEN)
    "requests",
]
```

**KRITIEK**: Frappe/ERPNext dependencies gaan NIET in `dependencies`!

---

### [tool.bench.frappe-dependencies]

```toml
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
hrms = ">=15.0.0,<16.0.0"
```

Deze worden gecontroleerd door `bench get-app`, niet door pip.

---

### [deploy.dependencies.apt]

```toml
[deploy.dependencies.apt]
packages = [
    "libmagic1",
    "ffmpeg",
    "wkhtmltopdf"
]
```

Voor Frappe Cloud deployments - installeert system packages.

---

## setup.py (v14 - Legacy)

### Minimale Configuratie

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

---

### Volledige Configuratie

```python
from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

with open("README.md") as f:
    long_description = f.read()

setup(
    name="my_custom_app",
    version="0.0.1",
    description="Description of your custom app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Company",
    author_email="developers@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Frappe",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
)
```

---

### requirements.txt (v14)

```
requests~=2.31.0
pandas>=2.0.0
python-dateutil>=2.8.0
```

### dev-requirements.txt (v14)

```
pytest>=7.0.0
black>=23.0.0
ruff>=0.0.280
```

**Noot**: Met `developer_mode=True` worden dev-requirements ook geïnstalleerd.

---

## __init__.py (VERPLICHT)

```python
# my_custom_app/__init__.py

__version__ = "0.0.1"
```

**KRITIEK**: De `__version__` variabele is VERPLICHT. Flit leest deze automatisch.

### Optionele Toevoegingen

```python
# my_custom_app/__init__.py

"""My Custom App - A brief description."""

__version__ = "0.0.1"
__title__ = "My Custom App"
__author__ = "Your Company"
__license__ = "MIT"
```

---

## Versie Nummering Conventie

| Formaat | Voorbeeld | Gebruik |
|---------|-----------|---------|
| Major.Minor.Patch | `1.2.3` | Stabiele releases |
| Major.Minor.Patch-dev | `1.2.3-dev` | Development versies |
| Major.x.x-develop | `15.x.x-develop` | Branch versies (ERPNext stijl) |

---

## Python Versie Vereisten

| Frappe Versie | Python Minimum |
|---------------|----------------|
| v14 | `>=3.10` |
| v15 | `>=3.10` |
| v16 | `>=3.14` |

---

## Migratie v14 → v15

1. **Maak pyproject.toml** met correcte structuur
2. **Verplaats dependencies** van requirements.txt naar pyproject.toml
3. **Controleer** `__version__` in `__init__.py`
4. **Verwijder** (optioneel): setup.py, MANIFEST.in, requirements.txt
5. **Test** met `bench get-app` en `bench install-app`

---

## Kritieke Regels

### ✅ ALTIJD

1. Package naam in pyproject.toml MOET matchen met directory naam
2. `dynamic = ["version"]` toevoegen voor flit
3. `__version__` in `__init__.py` definiëren
4. Frappe dependencies in `[tool.bench.frappe-dependencies]`

### ❌ NOOIT

1. Frappe/ERPNext in project dependencies zetten (staan niet op PyPI)
2. `__version__` vergeten (flit build faalt)
3. Andere build-backend dan flit_core gebruiken
