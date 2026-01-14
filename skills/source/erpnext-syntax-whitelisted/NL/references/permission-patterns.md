# Permission Patterns Reference

Security best practices voor Whitelisted Methods.

## frappe.has_permission()

### Signature

```python
frappe.has_permission(
    doctype,           # DocType naam
    ptype="read",      # Permission type: read, write, create, submit, cancel, delete
    doc=None,          # Optioneel: specifiek document of document naam
    user=None,         # Optioneel: specifieke user (default: huidige)
    throw=False        # Als True, throw error ipv return False
)
```

### Basis Gebruik

```python
@frappe.whitelist()
def get_customer(name):
    # Check permission voor DocType
    if not frappe.has_permission("Customer", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return frappe.get_doc("Customer", name).as_dict()
```

### Document-Level Check

```python
@frappe.whitelist()
def get_specific_order(order_id):
    # Check permission voor specifiek document
    if not frappe.has_permission("Sales Order", "read", order_id):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return frappe.get_doc("Sales Order", order_id).as_dict()
```

### Met throw=True

```python
@frappe.whitelist()
def get_data(doctype, name):
    # Throws automatisch als geen permission
    frappe.has_permission(doctype, "read", name, throw=True)
    
    return frappe.get_doc(doctype, name).as_dict()
```

### Permission Types

| Type | Beschrijving | Wanneer Gebruiken |
|------|--------------|-------------------|
| `read` | Document lezen | GET endpoints |
| `write` | Document wijzigen | PUT/PATCH endpoints |
| `create` | Nieuw document | POST endpoints voor nieuwe docs |
| `delete` | Document verwijderen | DELETE endpoints |
| `submit` | Document indienen | Submit workflows |
| `cancel` | Document annuleren | Cancel workflows |

---

## frappe.only_for()

Restricteert functie tot specifieke rollen.

### Enkele Rol

```python
@frappe.whitelist()
def admin_function():
    frappe.only_for("System Manager")
    # Code wordt alleen uitgevoerd als user System Manager rol heeft
    return {"admin_data": "sensitive"}
```

### Meerdere Rollen

```python
@frappe.whitelist()
def hr_or_admin_function():
    frappe.only_for(["System Manager", "HR Manager"])
    # Toegestaan als user ÉÉN van de rollen heeft
    return {"data": "value"}
```

### Combinatie met Permission Check

```python
@frappe.whitelist()
def restricted_update(doctype, name, values):
    # Rol check voor functie toegang
    frappe.only_for("System Manager")
    
    # Permission check voor specifieke operatie
    if not frappe.has_permission(doctype, "write", name):
        frappe.throw(_("Not permitted to write"), frappe.PermissionError)
    
    doc = frappe.get_doc(doctype, name)
    doc.update(values)
    doc.save()
    return doc.as_dict()
```

---

## Permission Error Handling

### Expliciete Error Messages

```python
@frappe.whitelist()
def secure_endpoint(doctype, name, action):
    try:
        frappe.has_permission(doctype, action, name, throw=True)
    except frappe.PermissionError:
        frappe.throw(
            _("You don't have permission to {0} this {1}").format(action, doctype),
            frappe.PermissionError
        )
    
    doc = frappe.get_doc(doctype, name)
    return doc.as_dict()
```

### Custom Permission Logic

```python
@frappe.whitelist()
def check_owner_or_admin(doctype, name):
    doc = frappe.get_doc(doctype, name)
    
    # Custom logic: owner of document OR System Manager
    is_owner = doc.owner == frappe.session.user
    is_admin = "System Manager" in frappe.get_roles()
    
    if not (is_owner or is_admin):
        frappe.throw(_("Only owner or admin can access"), frappe.PermissionError)
    
    return doc.as_dict()
```

---

## Veelgebruikte Patronen

### Read-Only API

```python
@frappe.whitelist(methods=["GET"])
def get_dashboard_stats():
    # Permission check voor relevante DocTypes
    if not frappe.has_permission("Sales Order", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return {
        "total_orders": frappe.db.count("Sales Order"),
        "pending": frappe.db.count("Sales Order", {"status": "Draft"})
    }
```

### Write API met Validatie

```python
@frappe.whitelist(methods=["POST"])
def create_customer(customer_name, email, territory="All Territories"):
    # Permission check
    if not frappe.has_permission("Customer", "create"):
        frappe.throw(_("Not permitted to create customer"), frappe.PermissionError)
    
    # Input validatie
    if not customer_name or not email:
        frappe.throw(_("Customer name and email required"))
    
    doc = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": customer_name,
        "email_id": email,
        "territory": territory
    })
    doc.insert()
    
    return {"name": doc.name, "success": True}
```

### Public API met Beperkte Data

```python
@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_public_products():
    """Public endpoint - alleen publieke velden retourneren."""
    return frappe.get_all(
        "Item",
        filters={"show_on_website": 1},
        fields=["name", "item_name", "description", "standard_rate"]
        # NIET: cost_price, supplier, etc.
    )
```

---

## Security Overwegingen

### ignore_permissions Vermijden

```python
# ❌ FOUT - bypass alle security
@frappe.whitelist()
def create_anything(data):
    doc = frappe.get_doc(data)
    doc.insert(ignore_permissions=True)  # SECURITY RISK!
    return doc.name

# ✅ GOED - expliciete role check
@frappe.whitelist()
def admin_create(data):
    frappe.only_for("System Manager")  # Alleen admins
    
    # Valideer DocType whitelist
    allowed = ["ToDo", "Note", "Communication"]
    if data.get("doctype") not in allowed:
        frappe.throw(_("Invalid Document Type"))
    
    doc = frappe.get_doc(data)
    doc.insert()  # Normale permissions
    return doc.name
```

### Wanneer ignore_permissions Acceptabel Is

```python
@frappe.whitelist()
def create_system_log(message):
    """System logs moeten altijd kunnen worden gemaakt."""
    frappe.only_for("System Manager")  # Role check VEREIST
    
    doc = frappe.get_doc({
        "doctype": "Error Log",  # Specifiek, beperkt DocType
        "method": "API Log",
        "error": message
    })
    doc.insert(ignore_permissions=True)  # Acceptabel met role check
    return doc.name
```

---

## Checklist Permission Implementatie

Bij elke API method:

1. **Bepaal access level**
   - Public (allow_guest=True) → Extra input validatie
   - Authenticated → Basis permission check
   - Role-restricted → frappe.only_for()

2. **Kies juiste check methode**
   - DocType level: `frappe.has_permission(doctype, ptype)`
   - Document level: `frappe.has_permission(doctype, ptype, doc)`
   - Role level: `frappe.only_for(role)`

3. **Valideer input**
   - Nooit user input vertrouwen
   - Whitelist toegestane waarden
   - Sanitize voor SQL queries

4. **Beperk output**
   - Alleen benodigde velden retourneren
   - Geen interne/sensitive velden

5. **Log verdachte activiteit**
   - Mislukte permission checks
   - Ongebruikelijke patronen
