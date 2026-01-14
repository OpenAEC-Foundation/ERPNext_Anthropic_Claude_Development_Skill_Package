# Fixtures Reference

Complete referentie voor fixtures in hooks.py.

---

## Wat Zijn Fixtures?

Fixtures exporteren configuratie-data uit de database naar JSON bestanden in je app. Deze data wordt automatisch geÃ¯mporteerd bij:
- App installatie
- `bench update`
- `bench migrate`

**Typisch gebruik**: Custom Fields, Property Setters, Roles, Custom Scripts, etc.

---

## Basis Syntax

```python
# In hooks.py
fixtures = [
    # Eenvoudig: exporteer alle records
    "Custom Field",
    "Property Setter",
    
    # Met filters
    {"dt": "Role", "filters": [["name", "like", "MyApp%"]]},
    
    # Single DocTypes (hele document)
    "Website Settings",
    
    # Complex filters
    {
        "dt": "Custom Script",
        "filters": [
            ["dt", "=", "Sales Invoice"],
            ["enabled", "=", 1]
        ]
    }
]
```

---

## Filter Syntax

### Operators

| Operator | Voorbeeld | Betekenis |
|----------|-----------|-----------|
| `=` | `["status", "=", "Active"]` | Exact gelijk |
| `!=` | `["status", "!=", "Disabled"]` | Niet gelijk |
| `like` | `["name", "like", "MyApp%"]` | Pattern match |
| `in` | `["status", "in", ["A", "B"]]` | In lijst |
| `not in` | `["status", "not in", ["X"]]` | Niet in lijst |
| `>`, `<`, `>=`, `<=` | `["idx", ">", 0]` | Vergelijking |

### Voorbeelden

```python
fixtures = [
    # Alle Custom Fields voor specifieke module
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My App"]]
    },
    
    # Custom Fields voor specifieke DocTypes
    {
        "dt": "Custom Field",
        "filters": [["dt", "in", ["Sales Invoice", "Purchase Invoice"]]]
    },
    
    # Property Setters die iets verbergen
    {
        "dt": "Property Setter",
        "filters": [
            ["property", "=", "hidden"],
            ["value", "=", "1"]
        ]
    },
    
    # Roles die beginnen met app prefix
    {
        "dt": "Role",
        "filters": [["name", "like", "MyApp%"]]
    },
    
    # Actieve custom scripts
    {
        "dt": "Custom Script",
        "filters": [
            ["module", "=", "My App"],
            ["enabled", "=", 1]
        ]
    }
]
```

---

## Export en Import

### Exporteren

```bash
# Exporteer alle geconfigureerde fixtures
bench --site sitename export-fixtures

# Output: myapp/myapp/fixtures/*.json
```

### Automatische Import

Fixtures worden automatisch geÃ¯mporteerd bij:
```bash
bench --site sitename install-app myapp
bench --site sitename migrate
bench update
```

### Handmatige Import

```bash
# Importeer fixtures van specifieke app
bench --site sitename import-fixtures --app myapp
```

---

## Velden die NIET Worden GeÃ«xporteerd

### Standaard Uitgesloten

| Veld | Reden |
|------|-------|
| `modified_by` | Site-specifiek |
| `creation` | Timestamp |
| `owner` | Site-specifiek |
| `idx` | Volgorde kan verschillen |
| `lft`, `rgt` | Tree structure specifiek |

### Voor Child Tables Ook

| Veld | Reden |
|------|-------|
| `docstatus` | Status kan verschillen |
| `doctype` | Redundant |
| `modified` | Timestamp |
| `name` | Auto-generated |

---

## Veelgebruikte Fixture Patterns

### Custom Fields

```python
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [["module", "=", "My App"]]
    }
]
```

### Property Setters

```python
fixtures = [
    {
        "dt": "Property Setter",
        "filters": [["module", "=", "My App"]]
    }
]
```

### Custom Scripts (Client Scripts)

```python
fixtures = [
    {
        "dt": "Client Script",
        "filters": [["module", "=", "My App"]]
    }
]
```

### Server Scripts

```python
fixtures = [
    {
        "dt": "Server Script",
        "filters": [["module", "=", "My App"]]
    }
]
```

### Roles en Permissions

```python
fixtures = [
    {
        "dt": "Role",
        "filters": [["name", "like", "MyApp%"]]
    },
    {
        "dt": "Custom DocPerm",
        "filters": [["parent", "in", ["My DocType 1", "My DocType 2"]]]
    }
]
```

### Workflows

```python
fixtures = [
    {
        "dt": "Workflow",
        "filters": [["name", "like", "MyApp%"]]
    },
    {
        "dt": "Workflow State",
        "filters": [["name", "like", "MyApp%"]]
    },
    {
        "dt": "Workflow Action Master",
        "filters": [["name", "like", "MyApp%"]]
    }
]
```

### Print Formats

```python
fixtures = [
    {
        "dt": "Print Format",
        "filters": [["module", "=", "My App"]]
    }
]
```

---

## Single DocTypes

Voor Single DocTypes (settings), exporteer simpelweg de naam:

```python
fixtures = [
    "Website Settings",
    "System Settings",
    "My App Settings"
]
```

Dit exporteert het hele document inclusief alle velden.

---

## Fixture Bestand Structuur

Na export krijg je JSON bestanden:

```
myapp/
â””â”€â”€ myapp/
    â””â”€â”€ fixtures/
        â”œâ”€â”€ custom_field.json
        â”œâ”€â”€ property_setter.json
        â”œâ”€â”€ role.json
        â””â”€â”€ my_app_settings.json
```

### JSON Formaat

```json
[
    {
        "doctype": "Custom Field",
        "dt": "Sales Invoice",
        "fieldname": "custom_field_1",
        "fieldtype": "Data",
        "label": "Custom Field 1",
        "insert_after": "customer"
    },
    {
        "doctype": "Custom Field",
        "dt": "Sales Invoice",
        "fieldname": "custom_field_2",
        "fieldtype": "Link",
        "options": "Customer",
        "label": "Custom Field 2"
    }
]
```

---

## Anti-Patterns

### âŒ Fixtures Zonder Filters

```python
# FOUT - exporteert ALLES, mogelijk honderden records
fixtures = ["Custom Field"]

# GOED - alleen relevante records
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]}
]
```

### âŒ Site-Specifieke Data

```python
# FOUT - data die per site verschilt
fixtures = ["User", "Company"]

# GOED - alleen configuratie, geen transacties
fixtures = ["Role", "Custom Field", "Property Setter"]
```

### âŒ Transactionele Data

```python
# FOUT - nooit transacties exporteren
fixtures = ["Sales Invoice", "Stock Entry"]
```

---

## Fixtures vs Patches

| Aspect | Fixtures | Patches |
|--------|----------|---------|
| Doel | Configuratie sync | Data migratie |
| Timing | Elke migrate | Eenmalig |
| Richting | App â†’ Site | Code â†’ Database |
| Gebruik | Custom Fields, Roles | Schema changes, data updates |

### Wanneer Fixtures?

- Custom Fields toevoegen
- Property Setters
- Roles en permissions
- Workflows
- Print formats
- Settings (Single DocTypes)

### Wanneer Patches?

- Bestaande data updaten
- Schema migraties
- Eenmalige transformaties
- Complex data seeding

---

## Debugging

### Check GeÃ«xporteerde Fixtures

```bash
# Bekijk wat er geÃ«xporteerd zou worden
bench --site sitename export-fixtures --dry-run

# Of bekijk bestaande fixture files
cat myapp/myapp/fixtures/custom_field.json | python -m json.tool
```

### Import Problemen

```python
# In bench console
from frappe.modules.import_file import import_file_by_path
import_file_by_path("/path/to/fixture.json", force=True)
```

---

## Versie Verschillen

| Feature | v14 | v15 |
|---------|-----|-----|
| fixtures hook | âœ… | âœ… |
| Filter syntax | âœ… | âœ… |
| --dry-run export | âœ… | âœ… |
| Auto-import on migrate | âœ… | âœ… |
