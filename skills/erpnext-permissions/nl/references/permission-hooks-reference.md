# Permission Hooks Reference

## has_permission Hook

Voeg custom permission logica toe voor een DocType.

### hooks.py Configuratie

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.sales_order_permission"
}
```

### Handler Implementatie

```python
# myapp/permissions.py
def sales_order_permission(doc, ptype, user):
    """
    Custom permission check voor Sales Order.
    
    Args:
        doc: Het document dat gecontroleerd wordt
        ptype: Permission type (read, write, etc.)
        user: User die gecontroleerd wordt
    
    Returns:
        None: Geen effect, ga door met standaard checks
        False: Weiger permission
        True: In v15+, kan permission toekennen (check versie)
    
    BELANGRIJK: In de meeste versies heeft True retourneren GEEN effect.
    Deze hook kan alleen permission WEIGEREN, niet toekennen.
    """
    # Voorbeeld: Weiger toegang tot geannuleerde orders voor niet-managers
    if doc.docstatus == 2 and "Sales Manager" not in frappe.get_roles(user):
        return False
    
    # Return None om door te gaan met standaard permission checks
    return None
```

### Kritieke Regels voor has_permission Hook

1. **Kan alleen WEIGEREN** - `return False` weigert, `return True/None` gaat door met standaard checks
2. **Altijd doc ontvangen** - Zelfs bij list views wordt doc per document aangeroepen
3. **Performance impact** - Wordt vaak aangeroepen, houd logica snel
4. **Return None als default** - Bij twijfel, laat standaard checks beslissen

---

## permission_query_conditions Hook

Voeg WHERE clause condities toe aan `frappe.get_list()` queries.

### hooks.py Configuratie

```python
# hooks.py
permission_query_conditions = {
    "ToDo": "myapp.permissions.todo_query"
}
```

### Handler Implementatie

```python
# myapp/permissions.py
def todo_query(user):
    """
    Returns SQL WHERE clause fragment voor filteren van ToDo lijst.
    
    Args:
        user: User die de query uitvoert (kan None zijn)
    
    Returns:
        str: Geldige SQL WHERE clause fragment
    """
    if not user:
        user = frappe.session.user
    
    # Toon alleen ToDos owned by of assigned by user
    return """
        (`tabToDo`.owner = {user} OR `tabToDo`.assigned_by = {user})
    """.format(user=frappe.db.escape(user))
```

### Kritieke Regels voor permission_query_conditions

1. **Alleen get_list** - Werkt NIET met `frappe.get_all()`
2. **ALTIJD escapen** - Gebruik `frappe.db.escape()` voor user input
3. **Return lege string** - `""` voor geen restricties
4. **Geldige SQL** - Return moet geldige WHERE clause zijn
5. **Tabel prefix** - Gebruik `` `tabDocType`.fieldname `` syntax

### Geavanceerd Voorbeeld: Hiërarchische Permissies

```python
def territory_based_query(user):
    """Filter documenten op basis van territory permissies."""
    if not user:
        user = frappe.session.user
    
    # System Manager ziet alles
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # Haal toegestane territories op
    territories = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "Territory"},
        pluck="for_value"
    )
    
    if not territories:
        return ""  # Geen restricties als geen user permissions
    
    # Bouw IN clause
    territory_list = ", ".join([frappe.db.escape(t) for t in territories])
    return f"`tabSales Order`.territory IN ({territory_list})"
```

---

## Combineren van Hooks

Beide hooks kunnen samen worden gebruikt voor complete permission controle:

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.check_sales_order_permission"
}

permission_query_conditions = {
    "Sales Order": "myapp.permissions.sales_order_query_conditions"
}
```

### Workflow

1. **List view** → `permission_query_conditions` filtert de query
2. **Per document** → `has_permission` checkt individuele toegang
3. **Beide** → Standaard role/user permissions blijven van toepassing

---

## Versie Verschillen

| Feature | v14 | v15 |
|---------|-----|-----|
| has_permission return True | Geen effect | Kan permission toekennen |
| Debug parameter | `verbose` | `debug` |
| Desk User rol | Niet beschikbaar | Automatische rol |

---

## Debugging Permission Hooks

```python
# Enable debug output in has_permission
frappe.has_permission("Sales Order", "read", doc, debug=True)

# Bekijk permission logs
print(frappe.local.permission_debug_log)

# Log in custom hook
def my_permission_hook(doc, ptype, user):
    frappe.logger().debug(f"Permission check: {doc.name}, {ptype}, {user}")
    return None
```
