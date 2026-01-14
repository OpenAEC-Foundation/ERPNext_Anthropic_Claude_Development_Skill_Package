# Permission Hooks Reference

Complete referentie voor permission hooks in hooks.py.

---

## permission_query_conditions

Filter list views dynamisch op basis van user/role.

### Syntax

```python
# In hooks.py
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_query_conditions",
    "ToDo": "myapp.permissions.todo_query_conditions",
    "Project": "myapp.permissions.project_query_conditions"
}
```

### Handler Implementatie

```python
# In myapp/permissions.py
import frappe

def si_query_conditions(user):
    """
    Retourneert een SQL WHERE clause fragment.
    
    Args:
        user: kan None zijn - controleer dit ALTIJD!
    
    Returns:
        str: SQL WHERE fragment (zonder WHERE keyword)
             "" = geen restricties
             "1=0" = niets tonen
    """
    if not user:
        user = frappe.session.user
    
    # Administrator ziet alles
    if user == "Administrator":
        return ""
    
    roles = frappe.get_roles(user)
    
    # Sales Manager ziet alles
    if "Sales Manager" in roles:
        return ""
    
    # Sales User ziet alleen eigen facturen
    if "Sales User" in roles:
        return f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
    
    # Anderen zien niets
    return "1=0"


def project_query_conditions(user):
    """Voorbeeld: filter op basis van project members"""
    if not user:
        user = frappe.session.user
    
    if "Projects Manager" in frappe.get_roles(user):
        return ""
    
    # Alleen projecten waar user member is
    return f"""
        `tabProject`.name IN (
            SELECT parent FROM `tabProject User`
            WHERE user = {frappe.db.escape(user)}
        )
    """
```

### âš ï¸ KRITIEK: get_list vs get_all

| Method | permission_query_conditions | Gedrag |
|--------|----------------------------|--------|
| `frappe.db.get_list` | âœ… Toegepast | Respecteert permissions |
| `frappe.db.get_all` | âŒ NIET toegepast | Negeert permissions |

```python
# Respecteert permission_query_conditions
frappe.db.get_list("Sales Invoice", filters={"status": "Unpaid"})

# NEGEERT permission_query_conditions - toont ALLES
frappe.db.get_all("Sales Invoice", filters={"status": "Unpaid"})
```

---

## has_permission

Custom document-level permission logic.

### Syntax

```python
# In hooks.py
has_permission = {
    "Sales Invoice": "myapp.permissions.si_has_permission",
    "Event": "myapp.permissions.event_has_permission",
    "Project": "myapp.permissions.project_has_permission"
}
```

### Handler Implementatie

```python
# In myapp/permissions.py

def si_has_permission(doc, user=None, permission_type=None):
    """
    Document-level permission check.
    
    Args:
        doc: het document object
        user: de user (kan None zijn, gebruik dan frappe.session.user)
        permission_type: "read", "write", "submit", "cancel", "delete", etc.
    
    Returns:
        True: toegang verlenen
        False: toegang weigeren
        None: fallback naar default permission check
    """
    if not user:
        user = frappe.session.user
    
    # Gesloten facturen kunnen niet bewerkt worden
    if permission_type == "write" and doc.status == "Closed":
        return False
    
    # Geannuleerde facturen kunnen niet verwijderd worden
    if permission_type == "delete" and doc.docstatus == 2:
        return False
    
    # Fallback naar standaard permissions
    return None


def event_has_permission(doc, user=None, permission_type=None):
    """Voorbeeld: public events zijn leesbaar voor iedereen"""
    if not user:
        user = frappe.session.user
    
    # Public events zijn voor iedereen leesbaar
    if permission_type == "read" and doc.event_type == "Public":
        return True
    
    # Private events alleen voor owner
    if doc.event_type == "Private":
        if doc.owner == user:
            return True
        return False
    
    return None


def project_has_permission(doc, user=None, permission_type=None):
    """Voorbeeld: project members hebben toegang"""
    if not user:
        user = frappe.session.user
    
    # Check of user project member is
    is_member = frappe.db.exists("Project User", {
        "parent": doc.name,
        "user": user
    })
    
    if permission_type == "read" and is_member:
        return True
    
    if permission_type == "write" and doc.project_manager == user:
        return True
    
    return None
```

### Permission Types

| Type | Wanneer Gecheckt |
|------|------------------|
| `read` | Document openen, list view |
| `write` | Document bewerken |
| `create` | Nieuw document maken |
| `delete` | Document verwijderen |
| `submit` | Document submitten |
| `cancel` | Document cancelen |
| `amend` | Document amenderen |
| `print` | Document printen |
| `email` | Document emailen |
| `share` | Document delen |

---

## Combineren van Permission Hooks

### Volgorde van Evaluatie

```
1. has_permission hook (document-level)
   â†“
2. Role Permissions (DocType level)
   â†“
3. User Permissions (field-level restrictions)
   â†“
4. permission_query_conditions (list filtering)
```

### Voorbeeld: Complete Permission Setup

```python
# hooks.py
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_query"
}
has_permission = {
    "Sales Invoice": "myapp.permissions.si_permission"
}

# myapp/permissions.py
def si_query(user):
    """List view filter"""
    if not user:
        user = frappe.session.user
    
    if "Accounts Manager" in frappe.get_roles(user):
        return ""
    
    # Toon alleen facturen van eigen company
    default_company = frappe.defaults.get_user_default("Company")
    if default_company:
        return f"`tabSales Invoice`.company = {frappe.db.escape(default_company)}"
    
    return "1=0"


def si_permission(doc, user=None, permission_type=None):
    """Document-level check"""
    if not user:
        user = frappe.session.user
    
    # Extra check: submitted invoices niet bewerken
    if permission_type == "write" and doc.docstatus == 1:
        return False
    
    return None
```

---

## Debugging Permissions

### In Code

```python
# Check of user permission heeft
has_perm = frappe.has_permission("Sales Invoice", "read", doc=invoice)

# Get alle permissions voor een doctype
perms = frappe.permissions.get_doc_permissions(doc)

# Debug output
print(frappe.permissions.get_user_perms("Sales Invoice", user))
```

### Bench Console

```python
# Test permission_query_conditions
from myapp.permissions import si_query_conditions
print(si_query_conditions("user@example.com"))

# Test has_permission
doc = frappe.get_doc("Sales Invoice", "SI-00001")
from myapp.permissions import si_has_permission
print(si_has_permission(doc, "user@example.com", "write"))
```

---

## Best Practices

### âœ… DO

```python
def my_query_conditions(user):
    # Altijd user None check
    if not user:
        user = frappe.session.user
    
    # Gebruik frappe.db.escape voor SQL injection preventie
    return f"owner = {frappe.db.escape(user)}"
```

### âŒ DON'T

```python
def my_query_conditions(user):
    # FOUT: Geen None check
    # FOUT: SQL injection kwetsbaar
    return f"owner = '{user}'"
```

---

## Versie Verschillen

| Feature | v14 | v15 |
|---------|-----|-----|
| permission_query_conditions | âœ… | âœ… |
| has_permission | âœ… | âœ… |
| Werkt alleen met get_list | âœ… | âœ… |
