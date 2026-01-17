# Permission Types Reference

## Standaard Permission Types

| Permission | Beschrijving | Van Toepassing Op |
|------------|--------------|-------------------|
| `read` | Document bekijken | Alle DocTypes |
| `write` | Document bewerken | Alle DocTypes |
| `create` | Nieuw document maken | Alle DocTypes |
| `delete` | Document verwijderen | Alle DocTypes |
| `submit` | Document indienen | Alleen Submittable DocTypes |
| `cancel` | Ingediend document annuleren | Alleen Submittable DocTypes |
| `amend` | Geannuleerd document wijzigen | Alleen Submittable DocTypes |
| `report` | Bekijken in Report Builder | Alle DocTypes |
| `export` | Exporteren naar Excel/CSV | Alle DocTypes |
| `import` | Importeren via Data Import | Alle DocTypes |
| `share` | Document delen met anderen | Alle DocTypes |
| `print` | Document printen/PDF genereren | Alle DocTypes |
| `email` | E-mail versturen voor document | Alle DocTypes |
| `select` | Selecteren in Link veld (v14+) | Alle DocTypes |

## Speciale Permission Opties

| Optie | Beschrijving |
|-------|--------------|
| `if_owner` | Permission geldt alleen als gebruiker het document heeft gemaakt |
| `set_user_permissions` | Kan user permissions instellen voor andere gebruikers |

## Permission Levels (Perm Levels)

Perm Levels groeperen velden voor gescheiden toegangscontrole:

- **Level 0**: Standaard niveau, alle velden starten hier
- **Levels 1-9**: Custom groeperingen voor beperkte velden

**Kritieke Regel**: Level 0 MOET worden toegekend voordat hogere levels kunnen worden toegekend.

### Voorbeeld: Salaris Veld Verbergen

```python
# In Customize Form of DocType JSON
{
    "fieldname": "salary",
    "fieldtype": "Currency",
    "permlevel": 1  # Alleen rollen met Level 1 access kunnen zien/bewerken
}
```

## DocType Permissions Configuratie

```json
{
  "permissions": [
    {
      "role": "Sales User",
      "permlevel": 0,
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 0,
      "submit": 0,
      "cancel": 0,
      "amend": 0,
      "report": 1,
      "export": 1,
      "import": 0,
      "share": 1,
      "print": 1,
      "email": 1,
      "if_owner": 0
    }
  ]
}
```

## Automatische Rollen

| Rol | Toegewezen Aan | Doel |
|-----|----------------|------|
| `Guest` | Iedereen (incl. niet-geauthenticeerd) | Publieke toegang |
| `All` | Alle geregistreerde gebruikers | Catch-all voor geauthenticeerde gebruikers |
| `Administrator` | Alleen `Administrator` user | Volledige systeemtoegang |
| `Desk User` | Users met `user_type = "System User"` (v15+) | Desk toegang |

## Custom Permission Types (v16+, Experimenteel)

```python
# Check custom permission in code
if frappe.has_permission(doc, "approve"):
    approve_document(doc)
else:
    frappe.throw("Not permitted", frappe.PermissionError)
```

**Setup voor Custom Permission Types**:
1. Enable developer mode
2. Maak Permission Type record
3. Wijs toe via Role Permission Manager
4. Exporteer als fixture
