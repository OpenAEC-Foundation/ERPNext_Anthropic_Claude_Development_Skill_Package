# Fixtures (Data Export/Import)

> Fixtures zijn JSON bestanden die automatisch worden geïmporteerd bij app installatie of migratie.

---

## Fixtures Hook Configuratie

**Locatie**: `hooks.py`

### Basis Syntax

```python
# Export ALLE records van een DocType
fixtures = [
    "Category",
    "Custom Field"
]
```

### Met Filters

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

---

## Fixtures Exporteren

### Export Command

```bash
# Export alle fixtures voor een app
bench --site sitename export-fixtures --app myapp

# Export fixtures voor alle apps
bench --site sitename export-fixtures
```

### Output Locatie

```
myapp/
└── {module}/
    └── fixtures/
        ├── category.json
        ├── role.json
        └── custom_field.json
```

---

## Fixture Bestand Structuur

### Voorbeeld: custom_field.json

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

---

## Velden die NIET worden Geëxporteerd

De volgende systeem velden worden automatisch uitgesloten:

| Veld | Reden |
|------|-------|
| `modified_by` | Systeem beheerd |
| `creation` | Systeem beheerd |
| `owner` | Site-specifiek |
| `idx` | Volgorde systeem beheerd |
| `lft` | Tree structure (intern) |
| `rgt` | Tree structure (intern) |

**Voor child table records ook:**
- `docstatus`
- `doctype`
- `modified`
- `name`

---

## Fixtures Import Gedrag

Fixtures worden geïmporteerd tijdens:

1. **App installatie**: `bench --site sitename install-app myapp`
2. **Migratie**: `bench --site sitename migrate`
3. **Update**: `bench update`

### Sync Gedrag

| Actie | Beschrijving |
|-------|--------------|
| **Insert** | Nieuwe records worden toegevoegd |
| **Update** | Bestaande records worden overschreven |
| **Delete** | Records NIET in fixture worden NIET verwijderd |

---

## Veelgebruikte Fixture DocTypes

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

---

## Custom Field Fixture Voorbeeld

### hooks.py

```python
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My Custom App"]]
    }
]
```

### fixtures/custom_field.json

```json
[
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_reference",
        "dt": "Sales Invoice",
        "module": "My Custom App",
        "fieldname": "custom_reference",
        "fieldtype": "Data",
        "label": "Custom Reference",
        "insert_after": "naming_series",
        "translatable": 0
    },
    {
        "doctype": "Custom Field",
        "name": "Sales Invoice-custom_category",
        "dt": "Sales Invoice",
        "module": "My Custom App",
        "fieldname": "custom_category",
        "fieldtype": "Link",
        "options": "Category",
        "label": "Category",
        "insert_after": "custom_reference"
    }
]
```

---

## Property Setter Fixture Voorbeeld

```json
[
    {
        "doctype": "Property Setter",
        "name": "Sales Invoice-customer-reqd",
        "doc_type": "Sales Invoice",
        "module": "My Custom App",
        "field_name": "customer",
        "property": "reqd",
        "property_type": "Check",
        "value": "1"
    },
    {
        "doctype": "Property Setter",
        "name": "Sales Invoice-main-default_print_format",
        "doc_type": "Sales Invoice",
        "module": "My Custom App",
        "field_name": null,
        "property": "default_print_format",
        "property_type": "Data",
        "value": "My Custom Format"
    }
]
```

---

## after_sync Hook

```python
# hooks.py
after_sync = "myapp.setup.after_sync"
```

```python
# myapp/setup.py
def after_sync():
    """Draait nadat fixtures zijn gesynchroniseerd."""
    setup_default_values()
    create_default_records()
```

---

## Fixtures vs Patches: Wanneer Wat?

| Scenario | Fixtures | Patches |
|----------|:--------:|:-------:|
| Custom Fields toevoegen | ✅ | ❌ |
| Property Setters | ✅ | ❌ |
| Standaard configuratie (Roles, Workflows) | ✅ | ❌ |
| Data transformatie | ❌ | ✅ |
| Data cleanup | ❌ | ✅ |
| Eenmalige data import | ❌ | ✅ |
| Veld waarde migratie | ❌ | ✅ |
| Standaard seed data | ✅ | ❌ (of after_install) |

---

## Filter Syntax

### Vergelijkingsoperators

| Operator | Voorbeeld |
|----------|-----------|
| `=` | `["field", "=", "value"]` |
| `!=` | `["field", "!=", "value"]` |
| `like` | `["field", "like", "prefix%"]` |
| `not like` | `["field", "not like", "%pattern%"]` |
| `in` | `["field", "in", ["val1", "val2"]]` |
| `not in` | `["field", "not in", ["val1", "val2"]]` |
| `is` | `["field", "is", "set"]` of `["field", "is", "not set"]` |

---

## Kritieke Regels

### ✅ ALTIJD

1. `module` veld zetten bij Custom Fields/Property Setters
2. Specifieke filters gebruiken (niet alle records exporteren)
3. Fixtures testen na export met clean install
4. Fixtures volgorde respecteren bij dependencies

### ❌ NOOIT

1. User data in fixtures (User, Communication)
2. Transactionele data (Sales Invoice, Sales Order)
3. Te brede filters (exporteert mogelijk te veel)
4. Site-specifieke waarden in fixtures

### ⚠️ VOORZICHTIG

1. Custom DocPerm - overschrijft user customizations
2. Workflow - kan actieve workflows beïnvloeden
3. Records met dependencies (juiste volgorde!)
