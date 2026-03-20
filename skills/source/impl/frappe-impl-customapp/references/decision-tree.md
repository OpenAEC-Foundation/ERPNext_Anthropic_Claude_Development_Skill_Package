# Decision Trees - Custom App Implementation

Complete decision flowcharts for building Frappe/ERPNext custom apps.

---

## Decision 1: Custom App vs Alternative Solution

```
┌─────────────────────────────────────────────────────────────────────────┐
│ START: What do you want to achieve?                                     │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Add or modify fields on existing DocType?                               │
├──────────────────────────┬──────────────────────────────────────────────┤
│ YES                      │ NO                                           │
│                          │                                              │
│ ► Custom Field via UI    │                     │                        │
│ ► Property Setter via UI │                     ▼                        │
│ ► Export as fixtures     │ ┌────────────────────────────────────────┐   │
│                          │ │ Add validation/automation?             │   │
│ NO CUSTOM APP NEEDED     │ └────────────────┬───────────────────────┘   │
│                          │                  │                           │
└──────────────────────────┘                  ▼                           │
                            ┌─────────────────────────────────────────────┐
                            │ Simple logic? (< 50 lines, no complex deps) │
                            ├──────────────────────────┬──────────────────┤
                            │ YES                      │ NO               │
                            │                          │                  │
                            │ ► Server Script          │        │         │
                            │ ► Client Script          │        ▼         │
                            │                          │ ┌────────────┐   │
                            │ NO CUSTOM APP NEEDED     │ │ New DocType│   │
                            │                          │ │ needed?    │   │
                            └──────────────────────────┘ └─────┬──────┘   │
                                                               │          │
                                          ┌────────────────────┴──────┐   │
                                          │                           │   │
                                          ▼                           ▼   │
                                ┌─────────────────┐         ┌─────────────┐
                                │ YES             │         │ NO          │
                                │                 │         │             │
                                │ CUSTOM APP      │         │ Server      │
                                │ REQUIRED        │         │ Script +    │
                                │                 │         │ Fixtures    │
                                └─────────────────┘         └─────────────┘
```

### Summary Table

| Requirement | Solution | Custom App? |
|-------------|----------|:-----------:|
| Add fields to existing DocType | Custom Field | ❌ |
| Change field properties | Property Setter | ❌ |
| Simple validation (< 50 lines) | Server Script | ❌ |
| Simple UI logic | Client Script | ❌ |
| Complex validation | Controller + Custom App | ✅ |
| New DocType with logic | Custom App | ✅ |
| Python API integrations | Whitelisted methods + Custom App | ✅ |
| Scheduled background jobs | Custom App | ✅ |
| Custom reports (Script Report) | Server Script or Custom App | Depends |

---

## Decision 2: Extension Strategy Flowchart

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HOW TO EXTEND EXISTING ERPNext FUNCTIONALITY?                           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ What type of extension?                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────────────┐                                                     │
│ │ A. Add fields   │                                                     │
│ └────────┬────────┘                                                     │
│          ▼                                                              │
│ ┌─────────────────────────────────────────────────────────────┐         │
│ │ Create Custom Field via:                                    │         │
│ │ ► UI: Customize Form > Add Field                            │         │
│ │ ► Fixture: Add to fixtures list in hooks.py                 │         │
│ │                                                             │         │
│ │ For behavior: Add Property Setter                           │         │
│ └─────────────────────────────────────────────────────────────┘         │
│                                                                         │
│ ┌─────────────────┐                                                     │
│ │ B. Modify logic │                                                     │
│ └────────┬────────┘                                                     │
│          ▼                                                              │
│ ┌─────────────────────────────────────────────────────────────┐         │
│ │ Which Frappe version?                                       │         │
│ ├────────────────────┬────────────────────────────────────────┤         │
│ │ v16+               │ v14/v15                                │         │
│ │                    │                                        │         │
│ │ Use hook:          │ Use hook:                              │         │
│ │ extend_doctype_    │ doc_events = {                         │         │
│ │ class = {          │   "Sales Invoice": {                   │         │
│ │   "Sales Invoice": │     "validate": "myapp.events.fn"      │         │
│ │   "myapp.si"       │   }                                    │         │
│ │ }                  │ }                                      │         │
│ └────────────────────┴────────────────────────────────────────┘         │
│                                                                         │
│ ┌─────────────────┐                                                     │
│ │ C. Override UI  │                                                     │
│ └────────┬────────┘                                                     │
│          ▼                                                              │
│ ┌─────────────────────────────────────────────────────────────┐         │
│ │ Form UI → Client Script (form_script in fixtures)           │         │
│ │ List UI → Client Script (list_script)                       │         │
│ │ Portal  → Override template via hooks.py                    │         │
│ │ Print   → Custom Print Format                               │         │
│ └─────────────────────────────────────────────────────────────┘         │
│                                                                         │
│ ┌─────────────────┐                                                     │
│ │ D. Add related  │                                                     │
│ │    DocType      │                                                     │
│ └────────┬────────┘                                                     │
│          ▼                                                              │
│ ┌─────────────────────────────────────────────────────────────┐         │
│ │ 1. Create DocType in YOUR app's module                      │         │
│ │ 2. Add Link field to parent OR                              │         │
│ │ 3. Add child table to parent via Custom Field               │         │
│ │ 4. Register link via links property (for Related section)   │         │
│ └─────────────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Decision 3: Patch Timing Flowchart

```
┌─────────────────────────────────────────────────────────────────────────┐
│ WHEN SHOULD THE PATCH RUN?                                              │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Are you deleting or renaming a field/DocType?                           │
├───────────────────────────────┬─────────────────────────────────────────┤
│ YES                           │ NO                                      │
│                               │                                         │
│ ┌───────────────────────┐     │                   │                     │
│ │ [pre_model_sync]      │     │                   ▼                     │
│ │                       │     │ ┌───────────────────────────────────┐   │
│ │ BACKUP DATA FIRST!    │     │ │ Are you populating a NEW field?   │   │
│ │                       │     │ ├───────────────────┬───────────────┤   │
│ │ 1. Read old values    │     │ │ YES               │ NO            │   │
│ │ 2. Store in new field │     │ │                   │               │   │
│ │    or Custom Field    │     │ │ [post_model_sync] │               │   │
│ │ 3. Commit             │     │ │                   │               │   │
│ │                       │     │ │ Field must exist  │ Data cleanup? │   │
│ │ Then delete field in  │     │ │ before we can     │               │   │
│ │ JSON/model            │     │ │ populate it       │ Either works  │   │
│ └───────────────────────┘     │ └───────────────────┴───────────────┘   │
└───────────────────────────────┴─────────────────────────────────────────┘

                    EXECUTION ORDER
                    ═══════════════
                    
    ┌─────────────────────────────────────────┐
    │ 1. [pre_model_sync] patches run         │
    │    (Old schema still present)           │
    └────────────────────┬────────────────────┘
                         ▼
    ┌─────────────────────────────────────────┐
    │ 2. Model sync (schema changes applied)  │
    │    (New fields added, old removed)      │
    └────────────────────┬────────────────────┘
                         ▼
    ┌─────────────────────────────────────────┐
    │ 3. [post_model_sync] patches run        │
    │    (New schema available)               │
    └────────────────────┬────────────────────┘
                         ▼
    ┌─────────────────────────────────────────┐
    │ 4. Fixtures imported                    │
    │    (Custom Fields, Property Setters)    │
    └─────────────────────────────────────────┘
```

### Patch Timing Quick Reference

| Scenario | Section | Reason |
|----------|---------|--------|
| Backup data from field being deleted | `[pre_model_sync]` | Field still exists |
| Migrate data between existing fields | Either | Fields exist in both |
| Populate newly added field | `[post_model_sync]` | Field must exist first |
| Data cleanup/validation | `[post_model_sync]` | After schema stable |
| Rename DocType | `[pre_model_sync]` | Preserve relationships |
| Transform data format | `[post_model_sync]` | On stable schema |

---

## Decision 4: Module Organization Flowchart

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HOW MANY MODULES FOR YOUR APP?                                          │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ How many DocTypes will you have?                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌───────────────────────────────────────────────────────────────────┐   │
│ │ 1-5 DocTypes                                                      │   │
│ ├───────────────────────────────────────────────────────────────────┤   │
│ │ ► ONE module with app name                                        │   │
│ │                                                                   │   │
│ │ my_app/                                                           │   │
│ │ └── my_app/                 # Module "My App"                     │   │
│ │     └── doctype/                                                  │   │
│ │         ├── doctype_a/                                            │   │
│ │         └── doctype_b/                                            │   │
│ └───────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│ ┌───────────────────────────────────────────────────────────────────┐   │
│ │ 6-15 DocTypes                                                     │   │
│ ├───────────────────────────────────────────────────────────────────┤   │
│ │ ► 2-4 modules by FUNCTIONAL AREA                                  │   │
│ │                                                                   │   │
│ │ my_app/                                                           │   │
│ │ ├── core/                   # Module "Core" - main DocTypes       │   │
│ │ │   └── doctype/                                                  │   │
│ │ ├── settings/               # Module "Settings" - config          │   │
│ │ │   └── doctype/                                                  │   │
│ │ └── integrations/           # Module "Integrations" - external    │   │
│ │     └── doctype/                                                  │   │
│ └───────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│ ┌───────────────────────────────────────────────────────────────────┐   │
│ │ 15+ DocTypes                                                      │   │
│ ├───────────────────────────────────────────────────────────────────┤   │
│ │ ► Modules by BUSINESS DOMAIN                                      │   │
│ │                                                                   │   │
│ │ my_erp/                                                           │   │
│ │ ├── sales/                  # Module "Sales"                      │   │
│ │ │   └── doctype/                                                  │   │
│ │ ├── purchasing/             # Module "Purchasing"                 │   │
│ │ │   └── doctype/                                                  │   │
│ │ ├── inventory/              # Module "Inventory"                  │   │
│ │ │   └── doctype/                                                  │   │
│ │ └── settings/               # Module "Settings"                   │   │
│ │     └── doctype/                                                  │   │
│ └───────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Module Naming Rules

| modules.txt Entry | Directory Name | Notes |
|-------------------|----------------|-------|
| `My Custom App` | `my_custom_app/` | Spaces → underscores |
| `Sales` | `sales/` | Simple lowercase |
| `API Integrations` | `api_integrations/` | Multi-word |

---

## Decision 5: Dependency Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│ WHAT DEPENDENCIES DOES YOUR APP HAVE?                                   │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Does it need Frappe only or ERPNext too?                                │
├────────────────────────────────┬────────────────────────────────────────┤
│ FRAPPE ONLY                    │ FRAPPE + ERPNEXT                       │
│                                │                                        │
│ # hooks.py                     │ # hooks.py                             │
│ required_apps = ["frappe"]     │ required_apps = ["frappe", "erpnext"]  │
│                                │                                        │
│ # pyproject.toml               │ # pyproject.toml                       │
│ [tool.bench.frappe-deps]       │ [tool.bench.frappe-deps]               │
│ frappe = ">=15.0.0"            │ frappe = ">=15.0.0"                    │
│                                │ erpnext = ">=15.0.0"                   │
└────────────────────────────────┴────────────────────────────────────────┘

                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Does it need Python packages (requests, pandas, etc.)?                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ # pyproject.toml                                                        │
│ [project]                                                               │
│ dependencies = [                                                        │
│     "requests>=2.28.0",     # PyPI packages go here                     │
│     "pandas>=1.5.0",                                                    │
│ ]                                                                       │
│                                                                         │
│ ⚠️  NEVER put frappe or erpnext in [project].dependencies!              │
│     They are NOT on PyPI.                                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Decision 6: Fixture Filter Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HOW TO FILTER FIXTURES?                                                 │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ What are you exporting?                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────┐     │
│ │ Custom Fields created by your app                               │     │
│ ├─────────────────────────────────────────────────────────────────┤     │
│ │ {"dt": "Custom Field",                                          │     │
│ │  "filters": [["module", "=", "My Custom App"]]}                 │     │
│ └─────────────────────────────────────────────────────────────────┘     │
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────┐     │
│ │ Property Setters for specific DocTypes                          │     │
│ ├─────────────────────────────────────────────────────────────────┤     │
│ │ {"dt": "Property Setter",                                       │     │
│ │  "filters": [["doc_type", "in", ["Sales Invoice", "Customer"]]]}│     │
│ └─────────────────────────────────────────────────────────────────┘     │
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────┐     │
│ │ Your own DocType records (lookup/master data)                   │     │
│ ├─────────────────────────────────────────────────────────────────┤     │
│ │ {"dt": "My Settings",                                           │     │
│ │  "filters": [["is_standard", "=", 1]]}                          │     │
│ │                                                                 │     │
│ │ OR all records if it's pure configuration:                      │     │
│ │ "My Category"  # exports all records                            │     │
│ └─────────────────────────────────────────────────────────────────┘     │
│                                                                         │
│ ┌─────────────────────────────────────────────────────────────────┐     │
│ │ Workflows for specific DocTypes                                 │     │
│ ├─────────────────────────────────────────────────────────────────┤     │
│ │ {"dt": "Workflow",                                              │     │
│ │  "filters": [["document_type", "=", "My DocType"]]}             │     │
│ └─────────────────────────────────────────────────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

⚠️  NEVER EXPORT:
    - User DocType (user accounts)
    - Communication (emails/notes)
    - Any transactional data (invoices, orders, etc.)
    - Versions (audit trail)
    - Activity Log
```

---

## Decision 7: Release Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HOW TO VERSION AND RELEASE YOUR APP?                                    │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Version numbering (Semantic Versioning)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ MAJOR.MINOR.PATCH  →  1.2.3                                             │
│                                                                         │
│ MAJOR (1.x.x → 2.0.0)                                                   │
│ ► Breaking changes                                                      │
│ ► Schema changes requiring data migration                               │
│ ► Removed features                                                      │
│                                                                         │
│ MINOR (1.1.x → 1.2.0)                                                   │
│ ► New features                                                          │
│ ► New DocTypes                                                          │
│ ► New fields (backward compatible)                                      │
│                                                                         │
│ PATCH (1.2.0 → 1.2.1)                                                   │
│ ► Bug fixes                                                             │
│ ► Security fixes                                                        │
│ ► No schema changes                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Patch organization by version                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ my_app/                                                                 │
│ └── patches/                                                            │
│     ├── v1_0/              # Patches for v1.0.x                         │
│     │   ├── initial_data_setup.py                                       │
│     │   └── populate_defaults.py                                        │
│     ├── v1_1/              # Patches for v1.1.x                         │
│     │   └── add_new_field_values.py                                     │
│     └── v2_0/              # Patches for v2.0.x (breaking)              │
│         ├── migrate_old_structure.py                                    │
│         └── cleanup_deprecated.py                                       │
│                                                                         │
│ # patches.txt                                                           │
│ [pre_model_sync]                                                        │
│ my_app.patches.v2_0.migrate_old_structure                               │
│                                                                         │
│ [post_model_sync]                                                       │
│ my_app.patches.v1_0.initial_data_setup                                  │
│ my_app.patches.v1_0.populate_defaults                                   │
│ my_app.patches.v1_1.add_new_field_values                                │
│ my_app.patches.v2_0.cleanup_deprecated                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```
