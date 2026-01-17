# Module Organisatie

> Modules structureren je app in logische componenten. Elke DocType MOET tot een module behoren.

---

## modules.txt Structuur

**Locatie**: `{app}/{app}/modules.txt`

```
My Custom App
Integrations
Reports
Settings
```

**Regels:**
- Eén module naam per regel
- Module naam = directory naam met spaties i.p.v. underscores
- Default module heeft dezelfde naam als de app
- Elke DocType MOET tot een geregistreerde module behoren

---

## Module Naam naar Directory Mapping

| modules.txt | Directory | Voorbeeld DocType Pad |
|-------------|-----------|----------------------|
| My Custom App | my_custom_app | `.../my_custom_app/doctype/...` |
| Integrations | integrations | `.../integrations/doctype/...` |
| Sales Reports | sales_reports | `.../sales_reports/report/...` |
| HR Settings | hr_settings | `.../hr_settings/doctype/...` |

**Conversie regel**: Spaties → underscores, lowercase

---

## Module Directory Structuur

```
my_custom_app/
├── modules.txt                  # Module registratie
├── my_custom_app/               # Default module
│   ├── __init__.py              # VERPLICHT
│   └── doctype/
│       └── my_doctype/
├── integrations/                # Extra module
│   ├── __init__.py              # VERPLICHT
│   └── doctype/
│       └── api_settings/
├── reports/                     # Reports module
│   ├── __init__.py              # VERPLICHT
│   └── report/
│       └── sales_summary/
└── settings/                    # Settings module
    ├── __init__.py              # VERPLICHT
    └── doctype/
        └── app_settings/
```

---

## Module Toevoegen

### Stap 1: Voeg toe aan modules.txt

```
My Custom App
New Module
```

### Stap 2: Maak directory structuur

```bash
mkdir -p my_custom_app/new_module/doctype
touch my_custom_app/new_module/__init__.py
```

### Stap 3: Selecteer module bij DocType aanmaken

Bij het maken van een nieuwe DocType via de UI:
- Selecteer de juiste module in het "Module" dropdown

---

## Module Componenten

Elke module kan bevatten:

| Component | Directory | Beschrijving |
|-----------|-----------|--------------|
| DocTypes | `doctype/` | Data modellen |
| Reports | `report/` | Query/Script Reports |
| Print Formats | `print_format/` | Print templates |
| Dashboards | `dashboard/` | Dashboard definities |
| Workspace | `workspace/` | Module workspace |

---

## Module Icoon Configuratie

### Via config/desktop.py (Legacy)

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
        },
        {
            "module_name": "Integrations",
            "color": "green",
            "icon": "octicon octicon-plug",
            "type": "module",
            "label": "Integrations"
        }
    ]
```

### Beschikbare Iconen

Frappe ondersteunt Octicons: `octicon octicon-{name}`

Veel gebruikte:
- `octicon-package` - Generic module
- `octicon-plug` - Integrations
- `octicon-graph` - Reports/Analytics
- `octicon-gear` - Settings
- `octicon-file` - Documents
- `octicon-person` - Users/HR

---

## Module Best Practices

### Logische Groepering

```
# GOED - functionele groepering
My Custom App          # Core functionaliteit
Integrations           # Externe systeem koppelingen
Settings               # Configuratie
Reports                # Rapportages
```

```
# VERMIJDEN - te generiek of te specifiek
Module 1               # Onduidelijke naam
Everything             # Te breed
Customer Invoice PDF   # Te specifiek (is geen module)
```

### Aanbevolen Module Structuur

| Module Type | Doel | Voorbeelden |
|-------------|------|-------------|
| Core (app naam) | Hoofd DocTypes | Project, Task |
| Settings | Configuratie | App Settings, Defaults |
| Integrations | API koppelingen | API Settings, Webhooks |
| Reports | Rapportages | Sales Summary, Analytics |
| Utilities | Helper functies | Import/Export tools |

---

## Module in DocType JSON

Wanneer je een DocType maakt, wordt de module opgeslagen:

```json
{
    "doctype": "DocType",
    "name": "My DocType",
    "module": "My Custom App",
    ...
}
```

**KRITIEK**: Als module niet in modules.txt staat, werkt de DocType niet correct.

---

## Module Workspace (v15+)

Workspaces vervangen de oude desktop iconen:

```json
// my_custom_app/my_custom_app/workspace/my_custom_app/my_custom_app.json
{
    "doctype": "Workspace",
    "name": "My Custom App",
    "module": "My Custom App",
    "label": "My Custom App",
    "is_standard": 1,
    "links": [
        {
            "label": "Documents",
            "links": [
                {
                    "type": "doctype",
                    "name": "My DocType",
                    "label": "My DocType"
                }
            ]
        }
    ]
}
```

---

## Kritieke Regels

### ✅ ALTIJD

1. Elke module in modules.txt registreren
2. `__init__.py` in elke module directory
3. Module naam consistent gebruiken (met spaties in modules.txt)
4. DocTypes aan de juiste module toewijzen

### ❌ NOOIT

1. DocTypes maken in niet-geregistreerde modules
2. Module directory naam met spaties gebruiken
3. modules.txt lege regels of spaties aan het eind
4. Module namen wijzigen na DocTypes zijn aangemaakt

---

## Troubleshooting

### DocType niet zichtbaar

1. Check of module in `modules.txt` staat
2. Check of module naam correct is gespeld
3. Run `bench clear-cache`

### Module icoon niet zichtbaar

1. Check `config/desktop.py` syntax
2. Verify module_name exact matcht
3. Run `bench build` en `bench clear-cache`

### Import errors

1. Controleer `__init__.py` in elke directory
2. Check module naam conversie (spaties → underscores)
