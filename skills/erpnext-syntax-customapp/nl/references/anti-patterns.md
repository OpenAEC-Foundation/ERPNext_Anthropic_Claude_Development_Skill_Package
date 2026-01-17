# Anti-Patterns en Veelgemaakte Fouten

> Fouten te vermijden bij het ontwikkelen van Frappe custom apps.

---

## Build Configuratie Anti-Patterns

### ❌ __version__ Ontbreekt

```python
# FOUT - geen version
# my_custom_app/__init__.py
pass
```

```python
# ✅ GOED
# my_custom_app/__init__.py
__version__ = "0.0.1"
```

**Gevolg**: Flit build faalt, app kan niet worden geïnstalleerd.

---

### ❌ Frappe in pyproject.toml Dependencies

```toml
# FOUT - frappe staat niet op PyPI
[project]
dependencies = [
    "frappe>=15.0.0",
    "erpnext>=15.0.0",
]
```

```toml
# ✅ GOED - gebruik tool.bench sectie
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
```

**Gevolg**: pip install faalt omdat frappe niet op PyPI staat.

---

### ❌ Package Naam Mismatch

```
# FOUT - pyproject.toml zegt "my_custom_app" maar directory is "my-custom-app"
apps/my-custom-app/        # Directory met streepje
├── pyproject.toml         # name = "my_custom_app" (underscore)
```

**Gevolg**: Package wordt niet gevonden, import errors.

---

### ❌ Verkeerde hooks.py Locatie

```
# FOUT - hooks.py in verkeerde directory
apps/my_custom_app/hooks.py         # Te hoog niveau

# ✅ GOED
apps/my_custom_app/my_custom_app/hooks.py  # In inner package
```

**Gevolg**: Hooks worden niet geladen, geen events triggeren.

---

## Module Anti-Patterns

### ❌ Module Niet Geregistreerd

```
# modules.txt - VERGETEN om new_module toe te voegen
My Custom App
# New Module  <- ontbreekt!
```

**Gevolg**: DocTypes in niet-geregistreerde modules werken niet correct.

---

### ❌ Ontbrekende __init__.py

```
# FOUT - geen __init__.py
my_custom_app/
└── new_module/
    └── doctype/           # ImportError!
```

```
# ✅ GOED - __init__.py in elke directory
my_custom_app/
└── new_module/
    ├── __init__.py        # Leeg bestand
    └── doctype/
        └── __init__.py
```

**Gevolg**: Python kan module niet importeren.

---

## Patches Anti-Patterns

### ❌ Geen Error Handling

```python
# FOUT - crashes zonder logging
def execute():
    frappe.db.sql("DELETE FROM `tabOldTable`")
```

```python
# ✅ GOED - met error handling
def execute():
    try:
        frappe.db.sql("DELETE FROM `tabOldTable`")
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(title="Delete Old Table Failed")
        raise
```

**Gevolg**: Patch faalt zonder diagnostische informatie.

---

### ❌ Verkeerde Model Sync Sectie

```python
# FOUT - pre_model_sync maar heeft nieuw veld nodig
# patches.txt: [pre_model_sync] myapp.patches.v1_0.fill_new_field

def execute():
    # new_field bestaat nog niet!
    frappe.db.sql("UPDATE `tabCustomer` SET new_field = 'value'")
```

```python
# ✅ GOED - in post_model_sync
# patches.txt: [post_model_sync] myapp.patches.v1_0.fill_new_field

def execute():
    frappe.db.sql("UPDATE `tabCustomer` SET new_field = 'value'")
```

**Gevolg**: SQL error omdat kolom niet bestaat.

---

### ❌ Grote Dataset Zonder Batching

```python
# FOUT - kan out of memory gaan
def execute():
    all_records = frappe.get_all("HugeDocType", fields=["*"])  # 1M+ records
    for record in all_records:
        process(record)
```

```python
# ✅ GOED - batch processing
def execute():
    batch_size = 1000
    offset = 0
    
    while True:
        records = frappe.get_all(
            "HugeDocType",
            fields=["name"],
            limit_page_length=batch_size,
            limit_start=offset
        )
        if not records:
            break
            
        for record in records:
            process(record)
        
        frappe.db.commit()
        offset += batch_size
```

**Gevolg**: Server memory exhaustion, process kill.

---

### ❌ Hardcoded Site-Specifieke Waarden

```python
# FOUT - site-specifieke waarden
def execute():
    frappe.db.set_value("Company", "My Company Ltd", "default_currency", "USD")
```

```python
# ✅ GOED - dynamisch ophalen
def execute():
    companies = frappe.get_all("Company")
    for company in companies:
        if not frappe.db.get_value("Company", company.name, "default_currency"):
            frappe.db.set_value("Company", company.name, "default_currency", "USD")
```

**Gevolg**: Patch faalt op andere sites waar "My Company Ltd" niet bestaat.

---

### ❌ Duplicate Patch Entry

```
# FOUT - duplicaat wordt genegeerd
myapp.patches.v1_0.my_patch
myapp.patches.v1_0.my_patch  # Wordt NIET opnieuw uitgevoerd
```

```
# ✅ GOED - maak uniek met commentaar
myapp.patches.v1_0.my_patch
myapp.patches.v1_0.my_patch #run-2024-01-15
```

**Gevolg**: Tweede entry wordt genegeerd, patch draait niet opnieuw.

---

### ❌ Ontbrekende __init__.py in Patches

```
# FOUT - Python kan module niet vinden
myapp/
└── patches/
    └── v1_0/
        └── my_patch.py  # ImportError!
```

```
# ✅ GOED - __init__.py in elke directory
myapp/
└── patches/
    ├── __init__.py
    └── v1_0/
        ├── __init__.py
        └── my_patch.py
```

---

## Fixtures Anti-Patterns

### ❌ User Data in Fixtures

```python
# FOUT - user specifieke data
fixtures = [
    "User",           # NIET DOEN - bevat passwords
    "Communication"   # NIET DOEN - site specifieke data
]
```

```python
# ✅ GOED - alleen configuratie
fixtures = [
    "Custom Field",
    "Property Setter",
    "Role"
]
```

**Gevolg**: Security risico, privacy schending, deployment problemen.

---

### ❌ Transactionele Data in Fixtures

```python
# FOUT - transactionele data
fixtures = [
    "Sales Invoice",  # NIET DOEN
    "Sales Order"     # NIET DOEN
]
```

**Gevolg**: Productie data overschreven, data verlies.

---

### ❌ Te Brede Filters

```python
# FOUT - exporteert mogelijk te veel
fixtures = [
    {"dt": "DocType"}  # Exporteert ALLE DocTypes!
]
```

```python
# ✅ GOED - specifieke filter
fixtures = [
    {"dt": "DocType", "filters": [["module", "=", "My Module"]]}
]
```

**Gevolg**: Onbedoelde system DocTypes worden overschreven.

---

### ❌ Circular Dependency in Fixtures

```python
# FOUT - Workflow hangt af van Workflow State
fixtures = [
    "Workflow",        # Heeft states nodig
    "Workflow State"   # Komt te laat
]
```

```python
# ✅ GOED - juiste volgorde
fixtures = [
    "Workflow State",
    "Workflow"
]
```

**Gevolg**: Import errors, incomplete workflows.

---

### ❌ Ontbrekende Module in Custom Fields

```json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_field",
        "dt": "Sales Invoice",
        "fieldname": "custom_field",
        "module": ""  // FOUT - geen module
    }
]
```

```json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_field",
        "dt": "Sales Invoice",
        "fieldname": "custom_field",
        "module": "My Custom App"  // ✅ GOED
    }
]
```

**Gevolg**: Custom field wordt niet correct geëxporteerd bij volgende export.

---

## Algemene Anti-Patterns

### ❌ Geen Versie Compatibiliteit Check

```python
# FOUT - geen versie check
def execute():
    # v15-only feature
    frappe.new_v15_function()
```

```python
# ✅ GOED - versie check
def execute():
    import frappe
    
    frappe_version = int(frappe.__version__.split('.')[0])
    
    if frappe_version >= 15:
        frappe.new_v15_function()
    else:
        frappe.legacy_function()
```

---

### ❌ Geen Commit Na Bulk Updates

```python
# FOUT - geen commit
def execute():
    for i in range(10000):
        frappe.db.set_value("DocType", name, "field", value)
    # Implicit rollback bij error!
```

```python
# ✅ GOED - expliciete commits
def execute():
    for i, item in enumerate(items):
        frappe.db.set_value("DocType", item.name, "field", value)
        
        if i % 100 == 0:
            frappe.db.commit()
    
    frappe.db.commit()
```

---

### ❌ Print Statements in Productie Code

```python
# FOUT - print verdwijnt in productie
def execute():
    print("Starting migration...")
```

```python
# ✅ GOED - gebruik logging
def execute():
    frappe.log_error(message="Starting migration", title="Migration Info")
    # Of voor niet-errors:
    frappe.logger().info("Starting migration...")
```

---

## Samenvatting: Top 10 Fouten

| # | Fout | Gevolg |
|---|------|--------|
| 1 | `__version__` ontbreekt | Build faalt |
| 2 | Frappe in pip dependencies | Install faalt |
| 3 | Module niet in modules.txt | DocTypes werken niet |
| 4 | `__init__.py` ontbreekt | Import errors |
| 5 | Patch zonder error handling | Geen diagnostiek |
| 6 | Verkeerde model sync sectie | SQL errors |
| 7 | Geen batch processing | Memory exhaustion |
| 8 | User data in fixtures | Security risico |
| 9 | Hardcoded waarden | Multi-site failures |
| 10 | Geen commits | Data rollback |
