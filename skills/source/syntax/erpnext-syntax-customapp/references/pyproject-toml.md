# Build Configuration: pyproject.toml and setup.py

> Complete configuration for Frappe app packaging in v14 (setup.py) and v15 (pyproject.toml).

---

## pyproject.toml (v15 - Primary)

### Minimal Configuration

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

### Full Configuration

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

# Ruff linter configuration
[tool.ruff]
line-length = 110
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "B"]

[tool.ruff.lint.isort]
known-first-party = ["frappe", "erpnext", "my_custom_app"]
```

---

## Section Details

### [build-system] (REQUIRED)

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"
```

| Field | Value | Explanation |
|-------|-------|-------------|
| `requires` | `["flit_core >=3.4,<4"]` | Frappe standard build tool |
| `build-backend` | `"flit_core.buildapi"` | Flit reads `__version__` from `__init__.py` |

**CRITICAL**: Flit requires `dynamic = ["version"]` in [project] section.

---

### [project] Fields

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `name` | string | ✅ | Package name (MUST match directory) |
| `authors` | list | ✅ | Author(s) with name and email |
| `description` | string | ✅ | Short description |
| `requires-python` | string | ✅ | Python version (`>=3.10` for v14/v15) |
| `readme` | string | Recommended | Path to README file |
| `dynamic` | list | ✅ | ALWAYS `["version"]` for flit |
| `dependencies` | list | Optional | Python package dependencies |
| `license` | string | Optional | SPDX license identifier |
| `keywords` | list | Optional | Keywords |
| `classifiers` | list | Optional | PyPI classifiers |

---

### Dependencies Syntax

```toml
dependencies = [
    # Exact version
    "requests==2.31.0",
    
    # Compatible version (2.31.x)
    "requests~=2.31.0",
    
    # Minimum version
    "requests>=2.31.0",
    
    # Version range
    "requests>=2.28.0,<3.0.0",
    
    # No version restriction (AVOID)
    "requests",
]
```

**CRITICAL**: Frappe/ERPNext dependencies do NOT go in `dependencies`!

---

### [tool.bench.frappe-dependencies]

```toml
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
hrms = ">=15.0.0,<16.0.0"
```

These are checked by `bench get-app`, not by pip.

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

For Frappe Cloud deployments - installs system packages.

---

## setup.py (v14 - Legacy)

### Minimal Configuration

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

### Full Configuration

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

**Note**: With `developer_mode=True`, dev-requirements are also installed.

---

## __init__.py (REQUIRED)

```python
# my_custom_app/__init__.py

__version__ = "0.0.1"
```

**CRITICAL**: The `__version__` variable is REQUIRED. Flit reads this automatically.

### Optional Additions

```python
# my_custom_app/__init__.py

"""My Custom App - A brief description."""

__version__ = "0.0.1"
__title__ = "My Custom App"
__author__ = "Your Company"
__license__ = "MIT"
```

---

## Version Numbering Convention

| Format | Example | Usage |
|--------|---------|-------|
| Major.Minor.Patch | `1.2.3` | Stable releases |
| Major.Minor.Patch-dev | `1.2.3-dev` | Development versions |
| Major.x.x-develop | `15.x.x-develop` | Branch versions (ERPNext style) |

---

## Python Version Requirements

| Frappe Version | Python Minimum |
|----------------|----------------|
| v14 | `>=3.10` |
| v15 | `>=3.10` |
| v16 | `>=3.14` |

---

## Migration v14 → v15

1. **Create pyproject.toml** with correct structure
2. **Move dependencies** from requirements.txt to pyproject.toml
3. **Verify** `__version__` in `__init__.py`
4. **Remove** (optional): setup.py, MANIFEST.in, requirements.txt
5. **Test** with `bench get-app` and `bench install-app`

---

## Critical Rules

### ✅ ALWAYS

1. Package name in pyproject.toml MUST match directory name
2. Add `dynamic = ["version"]` for flit
3. Define `__version__` in `__init__.py`
4. Frappe dependencies in `[tool.bench.frappe-dependencies]`

### ❌ NEVER

1. Put Frappe/ERPNext in project dependencies (not on PyPI)
2. Forget `__version__` (flit build fails)
3. Use build-backend other than flit_core
