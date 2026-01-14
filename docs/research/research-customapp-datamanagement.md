# Research Document: Custom App Data Management (Fase 2.6.2)

> **Doel**: VerifiÃ«ren, verdiepen en actualiseren van informatie over patches (migratie scripts) en fixtures (data export/import) voor Frappe v14/v15.
> **Bouwt voort op**: Research Fase 2.6.1 (Basis Structuur)

---

## Bronnen Geraadpleegd

| Bron | URL/Locatie | Type |
|------|-------------|------|
| Frappe Docs - Database Migrations | docs.frappe.io/framework/user/en/database-migrations | Primair |
| Frappe Docs - Hooks (Fixtures) | docs.frappe.io/framework/user/en/python-api/hooks#fixtures | Primair |
| Frappe Docs - bench migrate | docs.frappe.io/framework/user/en/bench/reference/migrate | Primair |
| Frappe Docs - Migrations Guide | docs.frappe.io/framework/user/en/guides/deployment/migrations | Primair |
| Frappe Docs - Custom Fields Installation | docs.frappe.io/framework/user/en/guides/app-development/how-to-create-custom-fields-during-app-installation | Primair |
| erpnext-vooronderzoek.md | Project bestand | Basis |

---

## 1. PATCHES (Migratie Scripts)

### 1.1 Wat zijn Patches?

Patches zijn Python scripts die data migraties uitvoeren wanneer een app wordt geÃ¼pdatet. Ze worden gebruikt om:
- Bestaande data te transformeren naar nieuw formaat
- Standaard waarden toe te voegen aan nieuwe velden
- Data cleanup uit te voeren
- Configuratie migraties uit te voeren

**Versie v14/v15**: Identiek, met uitzondering van INI-style secties (v14+).

### 1.2 patches.txt Structuur

**Locatie**: `{app}/patches.txt` in de root van de app directory.

#### Basis Syntax

```
# Simpele patch verwijzing (dotted path)
myapp.patches.v1_0.my_awesome_patch

# One-off Python statements
execute:frappe.delete_doc('Page', 'applications', ignore_missing=True)
```

#### INI-Style Secties (v14+)

```ini
[pre_model_sync]
# Patches die VOOR DocType schema sync draaien
# Hebben toegang tot OLD schema (oude velden nog beschikbaar)
myapp.patches.v1_0.migrate_old_field_data
myapp.patches.v1_0.backup_deprecated_records

[post_model_sync]
# Patches die NA DocType schema sync draaien
# Hebben toegang tot NEW schema (nieuwe velden beschikbaar)
# Hoeven GEEN frappe.reload_doc aan te roepen
myapp.patches.v1_0.populate_new_field
myapp.patches.v1_0.cleanup_orphan_records
```

### 1.3 Wanneer Pre vs Post Model Sync?

| Situatie | Sectie | Reden |
|----------|--------|-------|
| Data uit oud veld migreren | `[pre_model_sync]` | Oude velden nog beschikbaar |
| Nieuwe verplichte velden vullen | `[post_model_sync]` | Nieuwe velden bestaan al |
| Algemene data cleanup | `[post_model_sync]` | Geen schema afhankelijkheid |
| Veld hernoemen en data behouden | `[pre_model_sync]` | Oude veldnaam nog beschikbaar |

### 1.4 Patch Bestand Structuur

**Directory conventie**:
```
myapp/
â”œâ”€â”€ patches/
â”‚   â”œâ”€â”€ __init__.py              # Leeg bestand (verplicht)
â”‚   â”œâ”€â”€ v1_0/
â”‚   â”‚   â”œâ”€â”€ __init__.py          # Leeg bestand (verplicht)
â”‚   â”‚   â””â”€â”€ my_patch.py
â”‚   â””â”€â”€ v2_0/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â””â”€â”€ another_patch.py
â””â”€â”€ patches.txt
```

**Alternatieve moderne structuur** (v14+, aangemaakt door `bench create-patch`):
```
myapp/
â”œâ”€â”€ {module}/
â”‚   â””â”€â”€ doctype/
â”‚       â””â”€â”€ {doctype}/
â”‚           â””â”€â”€ patches/
â”‚               â”œâ”€â”€ __init__.py
â”‚               â””â”€â”€ improve_indexing.py
â””â”€â”€ patches.txt
```

### 1.5 Patch Implementatie

#### Basis Template

```python
import frappe

def execute():
    """Patch beschrijving hier."""
    # Patch logica
    pass
```

#### Complete Voorbeeld: Data Migratie

```python
# myapp/patches/v1_0/migrate_customer_type.py
import frappe

def execute():
    """Migreer customer_type van Text naar Link veld."""
    
    # Mapping oude waarden naar nieuwe
    type_mapping = {
        "individual": "Individual",
        "company": "Company", 
        "Individual": "Individual",
        "Company": "Company"
    }
    
    # Haal alle customers op met oude waarden
    customers = frappe.get_all(
        "Customer",
        filters={"customer_type": ["in", list(type_mapping.keys())]},
        fields=["name", "customer_type"]
    )
    
    for customer in customers:
        new_type = type_mapping.get(customer.customer_type)
        if new_type:
            frappe.db.set_value(
                "Customer", 
                customer.name, 
                "customer_type", 
                new_type,
                update_modified=False
            )
    
    # Commit na bulk update
    frappe.db.commit()
```

#### Schema Reload in Pre-Model-Sync Patches

```python
import frappe

def execute():
    """Patch die nieuwe schema nodig heeft in pre_model_sync."""
    
    # Laad nieuwe DocType definitie VOORDAT schema sync draait
    frappe.reload_doc("module_name", "doctype", "doctype_name")
    
    # Nu zijn nieuwe velden beschikbaar
    frappe.db.sql("""
        UPDATE `tabMyDocType`
        SET new_field = old_field
        WHERE old_field IS NOT NULL
    """)
```

**Let op**: In `[post_model_sync]` is `frappe.reload_doc()` NIET nodig - alle DocTypes zijn al gesynchroniseerd.

### 1.6 Patch Uitvoering Regels

| Regel | Beschrijving |
|-------|--------------|
| **Unieke regels** | Elke regel in patches.txt moet uniek zijn |
| **Eenmalige uitvoering** | Patches draaien slechts Ã©Ã©n keer per site |
| **Volgorde** | Patches draaien in de volgorde waarin ze staan |
| **Tracking** | Uitgevoerde patches worden opgeslagen in `Patch Log` DocType |
| **Herdraaien** | Voeg commentaar toe om patch opnieuw te draaien |

#### Patch Opnieuw Draaien

```
# Origineel
myapp.patches.v1_0.my_patch

# Om opnieuw te draaien, voeg commentaar toe (maakt regel uniek)
myapp.patches.v1_0.my_patch #2024-01-15
```

### 1.7 bench create-patch Command

```bash
$ bench create-patch
Select app for new patch (frappe, erpnext, myapp): myapp
Provide DocType name on which this patch will apply: Customer
Describe what this patch does: Improve customer indexing
Provide filename for this patch [improve_indexing.py]: 
Patch folder '/path/to/myapp/module/doctype/customer/patches' doesn't exist, create it? [Y/n]: y
Created /path/to/myapp/.../patches/improve_indexing.py and updated patches.txt
```

### 1.8 bench migrate Gedrag

Het `bench migrate` commando voert de volgende stappen uit in volgorde:

1. **before_migrate hooks** uitvoeren
2. **[pre_model_sync] patches** uitvoeren
3. **Database schema synchroniseren** (DocType JSON â†’ database tabellen)
4. **[post_model_sync] patches** uitvoeren
5. **Fixtures synchroniseren**
6. **Background jobs synchroniseren**
7. **Vertalingen updaten**
8. **Search index rebuilden**
9. **after_migrate hooks** uitvoeren

#### Migrate Command Opties

```bash
# Standaard migratie
bench --site sitename migrate

# Skip falende patches (NIET aangeraden voor productie)
bench --site sitename migrate --skip-failing

# Skip search index rebuild (sneller)
bench --site sitename migrate --skip-search-index
```

### 1.9 Error Handling in Patches

#### Basis Try/Except Pattern

```python
import frappe

def execute():
    try:
        perform_migration()
    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Patch Error: migrate_customer_type"
        )
        raise  # Hergooi om patch als gefaald te markeren
```

#### Atomische Operaties

```python
import frappe

def execute():
    """Patch met transaction control."""
    
    # Alle wijzigingen in Ã©Ã©n transactie
    try:
        for item in get_items_to_migrate():
            process_item(item)
        
        # Expliciete commit na succes
        frappe.db.commit()
        
    except Exception:
        # Rollback bij fout
        frappe.db.rollback()
        raise
```

#### Batch Processing voor Grote Datasets

```python
import frappe

def execute():
    """Patch met batch processing voor grote datasets."""
    
    batch_size = 1000
    offset = 0
    
    while True:
        items = frappe.db.sql("""
            SELECT name FROM `tabMyDocType`
            LIMIT %s OFFSET %s
        """, (batch_size, offset), as_dict=True)
        
        if not items:
            break
            
        for item in items:
            process_item(item)
        
        # Commit per batch
        frappe.db.commit()
        offset += batch_size
```

---

## 2. FIXTURES (Data Export/Import)

### 2.1 Wat zijn Fixtures?

Fixtures zijn JSON bestanden die database records bevatten die automatisch worden geÃ¯mporteerd wanneer een app wordt geÃ¯nstalleerd of geÃ¼pdatet. Ze worden gebruikt voor:
- Standaard configuraties (Custom Fields, Property Setters, Roles)
- Seed data (standaard categorieÃ«n, sjablonen)
- App-specifieke instellingen

**Versie v14/v15**: Identiek.

### 2.2 Fixtures Hook Configuratie

**Locatie**: `hooks.py`

#### Basis Syntax

```python
# Export ALLE records van een DocType
fixtures = [
    "Category",
    "Custom Field"
]
```

#### Met Filters

```python
fixtures = [
    # Alle records van Category
    "Category",
    
    # Alleen specifieke records met filter
    {"dt": "Role", "filters": [["role_name", "like", "MyApp%"]]},
    
    # Multiple filters
    {
        "dt": "Custom Field",
        "filters": [
            ["module", "=", "MyApp"],
            ["dt", "in", ["Sales Invoice", "Sales Order"]]
        ]
    },
    
    # Or filters (v14+)
    {
        "dt": "Property Setter",
        "or_filters": [
            ["module", "=", "MyApp"],
            ["name", "like", "myapp%"]
        ]
    }
]
```

### 2.3 Fixtures Exporteren

#### Export Command

```bash
# Export alle fixtures voor een app
bench --site sitename export-fixtures --app myapp

# Export fixtures voor alle apps
bench --site sitename export-fixtures
```

#### Output Locatie

```
myapp/
â””â”€â”€ {module}/
    â””â”€â”€ fixtures/
        â”œâ”€â”€ category.json
        â”œâ”€â”€ role.json
        â””â”€â”€ custom_field.json
```

### 2.4 Fixture Bestand Structuur

**Voorbeeld: custom_field.json**

```json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_field_name",
        "dt": "Sales Invoice",
        "fieldname": "custom_field_name",
        "fieldtype": "Data",
        "label": "Custom Field",
        "insert_after": "customer"
    },
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-another_field",
        "dt": "Sales Invoice",
        "fieldname": "another_field",
        "fieldtype": "Link",
        "options": "Customer",
        "label": "Another Field"
    }
]
```

### 2.5 Velden die NIET worden GeÃ«xporteerd

De volgende velden worden automatisch uitgesloten van export (systeem velden):

| Veld | Reden |
|------|-------|
| `modified_by` | Systeem beheerd |
| `creation` | Systeem beheerd |
| `owner` | Site-specifiek |
| `idx` | Volgorde systeem beheerd |
| `lft` | Tree structure (intern) |
| `rgt` | Tree structure (intern) |

**Voor child table records worden ook uitgesloten:**
- `docstatus`
- `doctype`
- `modified`
- `name`

### 2.6 Fixtures Import Gedrag

Fixtures worden geÃ¯mporteerd tijdens:

1. **App installatie**: `bench --site sitename install-app myapp`
2. **Migratie**: `bench --site sitename migrate`
3. **Update**: `bench update`

#### Sync vs Insert

| Gedrag | Beschrijving |
|--------|--------------|
| **Insert** | Nieuwe records worden toegevoegd |
| **Update** | Bestaande records worden overschreven |
| **Delete** | Records NIET in fixture worden NIET verwijderd |

### 2.7 Veelgebruikte Fixture DocTypes

| DocType | Gebruik |
|---------|---------|
| `Custom Field` | Custom velden toevoegen aan bestaande DocTypes |
| `Property Setter` | Properties van bestaande velden wijzigen |
| `Role` | Custom rollen |
| `Custom DocPerm` | Aangepaste permissions |
| `Workflow` | Workflow definities |
| `Workflow State` | Workflow states |
| `Workflow Action` | Workflow acties |
| `Print Format` | Print templates |
| `Report` | Custom reports |

### 2.8 after_sync Hook

```python
# hooks.py
after_sync = "myapp.setup.after_sync"
```

```python
# myapp/setup.py
def after_sync():
    """Draait nadat fixtures zijn gesynchroniseerd."""
    # Voer post-fixture setup uit
    setup_default_values()
    create_default_records()
```

---

## 3. FIXTURES vs PATCHES: Wanneer Wat?

### Decision Matrix

| Scenario | Fixtures | Patches |
|----------|----------|---------|
| Custom Fields toevoegen | âœ… | âŒ |
| Property Setters | âœ… | âŒ |
| Standaard configuratie (Roles, Workflows) | âœ… | âŒ |
| Data transformatie | âŒ | âœ… |
| Data cleanup | âŒ | âœ… |
| Eenmalige data import | âŒ | âœ… |
| Veld waarde migratie | âŒ | âœ… |
| Standaard seed data | âœ… | âŒ (of after_install) |
| Permissions resetten | âœ… (met zorg) | âœ… |

### Belangrijke Overwegingen

#### Fixtures
- **Overschrijven**: Fixtures overschrijven bestaande records bij elke migratie
- **Geen user customizations**: User wijzigingen worden overschreven
- **Idempotent**: Kan veilig meerdere keren draaien
- **Declaratief**: Beschrijft gewenste state

#### Patches
- **Eenmalig**: Draaien slechts Ã©Ã©n keer
- **Imperatief**: Beschrijft HOE data te wijzigen
- **User data safe**: Kan user wijzigingen respecteren
- **Complexe logica**: Ondersteunt conditionele updates

---

## 4. COMPLETE APP VOORBEELDEN

### 4.1 Minimale App met Fixtures

**Directory structuur:**
```
minimal_app/
â”œâ”€â”€ minimal_app/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ hooks.py
â”‚   â””â”€â”€ minimal_module/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â””â”€â”€ fixtures/
â”‚           â””â”€â”€ role.json
â”œâ”€â”€ patches.txt           # Leeg of met basis patches
â””â”€â”€ pyproject.toml
```

**hooks.py:**
```python
app_name = "minimal_app"
app_title = "Minimal App"
app_publisher = "Your Company"
app_description = "A minimal Frappe app"
app_version = "0.0.1"

fixtures = [
    {"dt": "Role", "filters": [["name", "like", "Minimal%"]]}
]
```

**role.json:**
```json
[
    {
        "doctype": "Role",
        "name": "Minimal User",
        "desk_access": 1,
        "is_custom": 1
    }
]
```

### 4.2 App met Custom DocType en Patches

**Directory structuur:**
```
full_app/
â”œâ”€â”€ full_app/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ hooks.py
â”‚   â”œâ”€â”€ patches/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â””â”€â”€ v1_0/
â”‚   â”‚       â”œâ”€â”€ __init__.py
â”‚   â”‚       â”œâ”€â”€ setup_default_categories.py
â”‚   â”‚       â””â”€â”€ migrate_old_data.py
â”‚   â””â”€â”€ full_module/
â”‚       â”œâ”€â”€ __init__.py
â”‚       â”œâ”€â”€ doctype/
â”‚       â”‚   â””â”€â”€ my_doctype/
â”‚       â”‚       â”œâ”€â”€ my_doctype.json
â”‚       â”‚       â””â”€â”€ my_doctype.py
â”‚       â””â”€â”€ fixtures/
â”‚           â””â”€â”€ custom_field.json
â”œâ”€â”€ patches.txt
â””â”€â”€ pyproject.toml
```

**patches.txt:**
```ini
[pre_model_sync]
# Data backup voor schema wijziging
full_app.patches.v1_0.migrate_old_data

[post_model_sync]
# Setup na schema sync
full_app.patches.v1_0.setup_default_categories
```

**setup_default_categories.py:**
```python
import frappe

def execute():
    """Maak standaard categorieÃ«n aan."""
    categories = ["Category A", "Category B", "Category C"]
    
    for cat_name in categories:
        if not frappe.db.exists("Category", cat_name):
            frappe.get_doc({
                "doctype": "Category",
                "category_name": cat_name,
                "enabled": 1
            }).insert(ignore_permissions=True)
    
    frappe.db.commit()
```

### 4.3 ERPNext Extension App

**hooks.py:**
```python
app_name = "erpnext_extension"
app_title = "ERPNext Extension"
app_publisher = "Your Company"
app_description = "Extends ERPNext functionality"
app_version = "1.0.0"

required_apps = ["frappe", "erpnext"]

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "ERPNext Extension"]]
    },
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "ERPNext Extension"]]
    },
    {
        "dt": "Role",
        "filters": [["name", "like", "Extension%"]]
    }
]

# Document events
doc_events = {
    "Sales Invoice": {
        "validate": "erpnext_extension.overrides.si_validate"
    }
}
```

---

## 5. ANTI-PATTERNS EN VALKUILEN

### 5.1 Patches Anti-Patterns

#### âŒ Geen Error Handling

```python
# FOUT - crashes zonder logging
def execute():
    frappe.db.sql("DELETE FROM `tabOldTable`")
```

```python
# GOED - met error handling
def execute():
    try:
        frappe.db.sql("DELETE FROM `tabOldTable`")
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(title="Delete Old Table Failed")
        raise
```

#### âŒ Patch in Verkeerde Sectie

```python
# FOUT - pre_model_sync maar heeft nieuw veld nodig
# patches.txt: [pre_model_sync] myapp.patches.v1_0.fill_new_field

def execute():
    # new_field bestaat nog niet!
    frappe.db.sql("UPDATE `tabCustomer` SET new_field = 'value'")
```

```python
# GOED - in post_model_sync OF met reload_doc
# patches.txt: [post_model_sync] myapp.patches.v1_0.fill_new_field

def execute():
    frappe.db.sql("UPDATE `tabCustomer` SET new_field = 'value'")
```

#### âŒ Grote Dataset Zonder Batching

```python
# FOUT - kan out of memory gaan
def execute():
    all_records = frappe.get_all("HugeDocType", fields=["*"])  # 1M+ records
    for record in all_records:
        process(record)
```

```python
# GOED - batch processing
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

#### âŒ Hardcoded Values

```python
# FOUT - site-specifieke waarden
def execute():
    frappe.db.set_value("Company", "My Company Ltd", "default_currency", "USD")
```

```python
# GOED - dynamisch ophalen
def execute():
    companies = frappe.get_all("Company")
    for company in companies:
        if not frappe.db.get_value("Company", company.name, "default_currency"):
            frappe.db.set_value("Company", company.name, "default_currency", "USD")
```

### 5.2 Fixtures Anti-Patterns

#### âŒ User Data in Fixtures

```python
# FOUT - user specifieke data
fixtures = [
    "User",           # NIET DOEN - bevat passwords en user data
    "Communication"   # NIET DOEN - site specifieke data
]
```

```python
# GOED - alleen configuratie
fixtures = [
    "Custom Field",
    "Property Setter",
    "Role"
]
```

#### âŒ Fixtures voor Transactionele Data

```python
# FOUT - transactionele data
fixtures = [
    "Sales Invoice",  # NIET DOEN
    "Sales Order"     # NIET DOEN
]
```

#### âŒ Te Brede Filters

```python
# FOUT - exporteert mogelijk te veel
fixtures = [
    {"dt": "DocType"}  # Exporteert ALLE DocTypes!
]
```

```python
# GOED - specifieke filter
fixtures = [
    {"dt": "DocType", "filters": [["module", "=", "My Module"]]}
]
```

#### âŒ Permissions Fixture Zonder Overweging

```python
# LET OP - overschrijft user customizations!
fixtures = [
    "Custom DocPerm"  # Wees voorzichtig
]
```

### 5.3 Algemene Valkuilen

#### Patch Niet Uniek in patches.txt

```
# FOUT - duplicaat wordt genegeerd
myapp.patches.v1_0.my_patch
myapp.patches.v1_0.my_patch  # Wordt NIET opnieuw uitgevoerd
```

```
# GOED - maak uniek met commentaar
myapp.patches.v1_0.my_patch
myapp.patches.v1_0.my_patch #run-2024-01-15
```

#### Vergeten __init__.py

```
# FOUT - Python kan module niet vinden
myapp/
â””â”€â”€ patches/
    â””â”€â”€ v1_0/
        â””â”€â”€ my_patch.py  # ImportError!
```

```
# GOED - __init__.py in elke directory
myapp/
â””â”€â”€ patches/
    â”œâ”€â”€ __init__.py
    â””â”€â”€ v1_0/
        â”œâ”€â”€ __init__.py
        â””â”€â”€ my_patch.py
```

#### Fixture Circular Dependency

```python
# FOUT - Workflow hangt af van Workflow State, maar state komt later
fixtures = [
    "Workflow",        # Heeft states nodig
    "Workflow State"   # Komt te laat
]
```

```python
# GOED - juiste volgorde (Frappe handelt dit vaak automatisch af)
fixtures = [
    "Workflow State",
    "Workflow"
]
```

---

## 6. VERSIE VERSCHILLEN (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| INI-style patches.txt | âœ… GeÃ¯ntroduceerd | âœ… Beschikbaar |
| bench create-patch | âœ… | âœ… Verbeterd |
| or_filters in fixtures | âœ… | âœ… |
| Fixture sync gedrag | Standaard | Standaard |
| Patch tracking | Patch Log DocType | Patch Log DocType |

---

## 7. SAMENVATTING VOOR SKILL CREATIE

### Key Learnings

1. **patches.txt** ondersteunt INI-style secties: `[pre_model_sync]` en `[post_model_sync]`
2. **Pre-model-sync patches** hebben toegang tot oude schema (voor data migratie)
3. **Post-model-sync patches** hebben nieuwe schema (geen reload_doc nodig)
4. **Fixtures** zijn declaratief en worden bij elke migratie gesynchroniseerd
5. **Patches** zijn imperatief en draaien slechts Ã©Ã©n keer
6. **Error handling** is cruciaal in patches - log errors en hergooi excepties
7. **Batch processing** voor grote datasets voorkomt memory issues
8. **Fixtures overschrijven** bestaande records - wees voorzichtig met user customizations

### Skill References te Maken

1. `patches.md` - Patch structuur, INI secties, implementatie patterns
2. `fixtures.md` - Fixture configuratie, filters, export/import
3. `examples.md` - Complete werkende app voorbeelden met patches en fixtures
4. `anti-patterns.md` - Wat te vermijden bij data management
