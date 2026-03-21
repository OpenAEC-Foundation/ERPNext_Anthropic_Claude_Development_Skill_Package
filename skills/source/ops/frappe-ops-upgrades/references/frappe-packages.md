# Frappe Packages — Complete Reference

## What Are Frappe Packages?

Frappe Packages (v14+) are lightweight applications built entirely from the Framework UI — no command-line app scaffolding required. A Package is a collection of **Module Defs** bundled together for distribution as a gzipped tarball. Packages can be imported into other Frappe sites, functioning like mini-apps.

**Key distinction**: Packages are NOT the same as Frappe Apps. They are UI-created bundles of customizations and modules, designed for portability without requiring a full app structure (`setup.py`/`pyproject.toml`, GitHub repo, etc.).

---

## What Can Be Packaged

A Package contains **Module Defs** — any module marked as "Custom" can be assigned to a Package. This includes:

| Component | Packageable | Notes |
|-----------|:-----------:|-------|
| Custom DocTypes | Yes | DocTypes created via UI |
| Server Scripts | Yes | API, Document Event, Permission Query |
| Client Scripts | Yes | Via Custom Module Def |
| Web Pages | Yes | Built in Framework UI |
| Reports | Yes | Script Reports, Query Reports |
| Print Formats | Yes | Custom print templates |
| Dashboards | Yes | Dashboard charts and shortcuts |
| Workflows | Yes | Workflow definitions and actions |
| Workspace | Yes | Custom workspace layouts |
| Notification | Yes | Email/system notifications |

### What CANNOT Be Packaged Directly

- **Custom Fields** on standard DocTypes — use **Fixtures** instead (see below)
- **Property Setters** — use Fixtures
- **Custom DocPerms** — use Fixtures
- Standard/core DocType modifications — these require a proper Frappe App

---

## Package Lifecycle

### 1. Create a Package

Create a **Package** document in the Frappe UI:
- Set package name, publisher, README, LICENSE
- The Package is designed to be pushed to a git repository

### 2. Assign Modules to the Package

For each Custom Module Def you want to include:
- Open the Module Def
- Set the **Package** field to your package name
- ONLY "Custom" type Module Defs can be assigned to a Package

### 3. Create a Package Release

Create a **Package Release** document:
- The system exports all associated modules to `[bench]/sites/[site]/packages/`
- Bundles the directory into `[package]-[version].tar.gz`
- Download the tarball for distribution

### 4. Import on Target Site

On the target site, create a **Package Import** document:
- Attach the `.tar.gz` file
- Check **Activate** to extract into `[bench]/sites/[sitename]/packages/`
- The system runs migrations (like an app migration)
- **Force** option: overwrites existing files; otherwise unchanged files are skipped
- A log records the operation output

---

## Fixtures: Exporting Customizations Without a Package

For exporting **Custom Fields**, **Property Setters**, **Custom DocPerms**, and other record-level customizations, use the **Fixtures** mechanism via `hooks.py` in a Frappe App.

### Define Fixtures in hooks.py

```python
# Export ALL Custom Fields
fixtures = [
    "Custom Field",
    "Property Setter",
    "Custom DocPerm",
    "Client Script",
    "Server Script",
    "Workflow",
    "Print Format",
]

# Export with filters (selective)
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My Custom Module"]]
    },
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "My Custom Module"]]
    },
    {
        "dt": "Client Script",
        "filters": [["module", "=", "My Custom Module"]]
    },
]
```

### Export and Import Commands

```bash
# Export fixtures to JSON files in your app
bench --site mysite export-fixtures --app myapp

# Fixtures auto-sync on install/update:
bench --site mysite install-app myapp
bench --site mysite migrate

# Import individual JSON documents
bench --site mysite import-doc /path/to/file.json

# Import all JSON files from a directory
bench --site mysite import-doc /path/to/directory/

# Export a single document as JSON
bench --site mysite export-json "Custom Field" "Sales Invoice-custom_field_name"
```

### Excluded Fields (Auto-stripped During Export)

These system fields are automatically excluded from fixture exports:
- `modified_by`, `creation`, `owner`, `idx`, `lft`, `rgt`
- Child table fields: `docstatus`, `doctype`, `modified`, `name`

---

## Decision Tree: Package vs App vs Fixtures

```
Need to move customizations between sites?
├── Only Custom Fields / Property Setters / DocPerms?
│   └── Use FIXTURES in a Frappe App's hooks.py
├── Custom DocTypes + Server Scripts + Web Pages (all built in UI)?
│   ├── Need a full development workflow (CI/CD, tests, versioning)?
│   │   └── Use a FRAPPE APP
│   └── Quick distribution without app scaffolding?
│       └── Use a FRAPPE PACKAGE
├── Modifying core/standard DocTypes?
│   └── ALWAYS use a FRAPPE APP (Packages cannot modify standard DocTypes)
├── Need pip-installable distribution?
│   └── Use a FRAPPE APP
└── One-off data transfer between staging and production?
    └── Use FIXTURES with export-fixtures / import-doc
```

---

## Limitations

1. **Not a replacement for proper apps** — Packages lack test infrastructure, CI/CD integration, pip packaging, and proper version management
2. **No version pinning** — Packages do not declare Frappe version dependencies; compatibility is the publisher's responsibility
3. **Custom Module Defs only** — You cannot package modifications to standard/core DocTypes
4. **No dependency resolution** — Packages cannot declare dependencies on other packages or apps
5. **No rollback mechanism** — Importing a package is a one-way operation; ALWAYS backup before importing
6. **No CLI commands** — Unlike apps, there is no `bench get-package` or `bench install-package`; everything goes through the UI (Package Import document)
7. **Limited migration control** — Package imports run migrations automatically; you cannot control patch execution order

---

## Best Practices

- **ALWAYS** backup the target site before importing a package
- **ALWAYS** test package imports on a staging site first
- **NEVER** use Packages for mission-critical production customizations — use a proper Frappe App instead
- **ALWAYS** use Fixtures (not Packages) for Custom Fields, Property Setters, and DocPerms on standard DocTypes
- **ALWAYS** include a README and LICENSE in your Package
- Use the **Force** option only when you explicitly want to overwrite existing files
- Keep Package Releases versioned — use semantic versioning in release names
