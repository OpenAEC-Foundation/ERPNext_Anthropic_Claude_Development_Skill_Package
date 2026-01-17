# Patches (Migratie Scripts)

> Patches zijn Python scripts die data migraties uitvoeren tijdens app updates.

---

## patches.txt Structuur

**Locatie**: `{app}/{app}/patches.txt`

### Basis Syntax

```
# Simpele patch verwijzing (dotted path)
myapp.patches.v1_0.my_awesome_patch

# One-off Python statements
execute:frappe.delete_doc('Page', 'applications', ignore_missing=True)
```

### INI-Style Secties (v14+)

```ini
[pre_model_sync]
# Patches die VÓÓR DocType schema sync draaien
# Hebben toegang tot OLD schema (oude velden beschikbaar)
myapp.patches.v1_0.migrate_old_field_data
myapp.patches.v1_0.backup_deprecated_records

[post_model_sync]
# Patches die NA DocType schema sync draaien
# Hebben toegang tot NEW schema (nieuwe velden beschikbaar)
# Hoeven GEEN frappe.reload_doc aan te roepen
myapp.patches.v1_0.populate_new_field
myapp.patches.v1_0.cleanup_orphan_records
```

---

## Pre vs Post Model Sync

| Situatie | Sectie | Reden |
|----------|--------|-------|
| Data uit oud veld migreren | `[pre_model_sync]` | Oude velden nog beschikbaar |
| Nieuwe verplichte velden vullen | `[post_model_sync]` | Nieuwe velden bestaan al |
| Algemene data cleanup | `[post_model_sync]` | Geen schema afhankelijkheid |
| Veld hernoemen en data behouden | `[pre_model_sync]` | Oude veldnaam nog beschikbaar |

---

## Patch Directory Structuur

### Conventionele Structuur

```
myapp/
├── patches/
│   ├── __init__.py              # VERPLICHT (leeg)
│   ├── v1_0/
│   │   ├── __init__.py          # VERPLICHT (leeg)
│   │   ├── setup_defaults.py
│   │   └── migrate_data.py
│   └── v2_0/
│       ├── __init__.py          # VERPLICHT
│       └── schema_upgrade.py
└── patches.txt
```

### Alternatieve Structuur (bench create-patch)

```
myapp/
├── {module}/
│   └── doctype/
│       └── {doctype}/
│           └── patches/
│               ├── __init__.py
│               └── improve_indexing.py
└── patches.txt
```

---

## Patch Implementatie

### Basis Template

```python
import frappe

def execute():
    """Patch beschrijving hier."""
    # Patch logica
    pass
```

### Complete Voorbeeld: Data Migratie

```python
# myapp/patches/v1_0/migrate_customer_type.py
import frappe

def execute():
    """Migreer customer_type van Text naar Link veld."""
    
    type_mapping = {
        "individual": "Individual",
        "company": "Company", 
        "Individual": "Individual",
        "Company": "Company"
    }
    
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
    
    frappe.db.commit()
```

---

## Schema Reload in Pre-Model-Sync

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

**Let op**: In `[post_model_sync]` is `frappe.reload_doc()` NIET nodig.

---

## Patch Uitvoering Regels

| Regel | Beschrijving |
|-------|--------------|
| **Unieke regels** | Elke regel in patches.txt moet uniek zijn |
| **Eenmalige uitvoering** | Patches draaien slechts één keer per site |
| **Volgorde** | Patches draaien in de volgorde waarin ze staan |
| **Tracking** | Uitgevoerde patches worden opgeslagen in `Patch Log` DocType |
| **Herdraaien** | Voeg commentaar toe om patch opnieuw te draaien |

---

## Patch Opnieuw Draaien

```
# Origineel
myapp.patches.v1_0.my_patch

# Om opnieuw te draaien, voeg commentaar toe (maakt regel uniek)
myapp.patches.v1_0.my_patch #2024-01-15
myapp.patches.v1_0.my_patch #run-again
```

---

## bench create-patch Command

```bash
$ bench create-patch
Select app for new patch (frappe, erpnext, myapp): myapp
Provide DocType name on which this patch will apply: Customer
Describe what this patch does: Improve customer indexing
Provide filename for this patch [improve_indexing.py]: 
Patch folder doesn't exist, create it? [Y/n]: y
Created patch file and updated patches.txt
```

---

## Error Handling

### Basis Try/Except

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

### Atomische Operaties

```python
import frappe

def execute():
    """Patch met transaction control."""
    
    try:
        for item in get_items_to_migrate():
            process_item(item)
        
        frappe.db.commit()
        
    except Exception:
        frappe.db.rollback()
        raise
```

---

## Batch Processing

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

## bench migrate Workflow

Het `bench migrate` commando voert uit:

1. **before_migrate hooks** uitvoeren
2. **[pre_model_sync] patches** uitvoeren
3. **Database schema synchroniseren** (DocType JSON → database)
4. **[post_model_sync] patches** uitvoeren
5. **Fixtures synchroniseren**
6. **Background jobs synchroniseren**
7. **Vertalingen updaten**
8. **Search index rebuilden**
9. **after_migrate hooks** uitvoeren

### Migrate Command Opties

```bash
# Standaard migratie
bench --site sitename migrate

# Skip falende patches (NIET voor productie!)
bench --site sitename migrate --skip-failing

# Skip search index rebuild (sneller)
bench --site sitename migrate --skip-search-index
```

---

## Kritieke Regels

### ✅ ALTIJD

1. `__init__.py` in elke patches directory
2. Error handling met logging
3. Batch processing voor grote datasets
4. `frappe.db.commit()` na bulk updates
5. Testen op development omgeving eerst

### ❌ NOOIT

1. Hardcoded site-specifieke waarden
2. Patch zonder error handling
3. Grote datasets zonder batching
4. Dezelfde patch regel tweemaal (wordt genegeerd)
5. Pre-model-sync patch die nieuwe velden nodig heeft zonder `reload_doc`
