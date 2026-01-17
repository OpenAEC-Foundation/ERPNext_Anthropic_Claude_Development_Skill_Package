# Permission Examples

## 1. Check Permission Voordat Actie Uitgevoerd Wordt

```python
@frappe.whitelist()
def approve_order(order_name):
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Check custom permission
    if not frappe.has_permission(doc.doctype, "write", doc):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Check aanvullende business logica
    if "Approver" not in frappe.get_roles():
        frappe.throw(_("Only Approvers can approve orders"))
    
    doc.status = "Approved"
    doc.save()
```

## 2. Owner-Only Access Pattern

```python
# Optie A: Via DocType permissions, set if_owner = 1 voor een rol

# Optie B: Programmatisch checken
def can_edit(doc):
    if doc.owner == frappe.session.user:
        return True
    if "Manager" in frappe.get_roles():
        return True
    return False
```

## 3. Hiërarchische Permission Check

```python
def check_territory_access(doc, user=None):
    """Check of user toegang heeft tot document's territory."""
    if not user:
        user = frappe.session.user
    
    user_territories = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "Territory"},
        pluck="for_value"
    )
    
    if not user_territories:
        return True  # Geen restricties
    
    return doc.territory in user_territories
```

## 4. User Permission Toevoegen bij Document Creatie

```python
# In DocType controller
class Employee(Document):
    def after_insert(self):
        # Geef employee toegang tot eigen record
        if self.user_id:
            from frappe.permissions import add_user_permission
            add_user_permission(
                "Employee",
                self.name,
                self.user_id,
                ignore_permissions=True
            )
```

## 5. Permission Query voor Multi-Tenant Setup

```python
# hooks.py
permission_query_conditions = {
    "Customer": "myapp.permissions.customer_query"
}

# myapp/permissions.py
def customer_query(user):
    if not user:
        user = frappe.session.user
    
    # Admin ziet alles
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # Haal company van user op
    company = frappe.db.get_value("User", user, "default_company")
    if not company:
        return "1=0"  # Geen toegang als geen company
    
    return f"`tabCustomer`.company = {frappe.db.escape(company)}"
```

## 6. Conditional Field Access via Perm Levels

```python
# Stap 1: Zet permlevel op veld in DocType/Customize Form
{
    "fieldname": "internal_notes",
    "fieldtype": "Text",
    "permlevel": 1
}

# Stap 2: Geef alleen specifieke rollen level 1 access
# Via Role Permission Manager:
# - Sales Manager: Level 0 + Level 1 (read, write)
# - Sales User: Level 0 alleen (kan internal_notes niet zien)
```

## 7. Share Document Programmatisch

```python
def share_with_approvers(doc):
    """Deel document met alle gebruikers in Approver rol."""
    from frappe.share import add as add_share
    
    approvers = frappe.get_all(
        "Has Role",
        filters={"role": "Approver", "parenttype": "User"},
        pluck="parent"
    )
    
    for approver in approvers:
        if approver != doc.owner:  # Niet delen met eigenaar
            add_share(
                doctype=doc.doctype,
                name=doc.name,
                user=approver,
                read=1,
                write=0,
                share=0
            )
```

## 8. Permission Check in Web Form/Portal

```python
# Controller voor portal pagina
def get_context(context):
    # Check of user toegang heeft
    if not frappe.has_permission("Sales Order", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Haal alleen documenten op die user mag zien
    context.orders = frappe.get_list(
        "Sales Order",
        filters={"customer": frappe.session.user},
        fields=["name", "status", "grand_total"]
    )
```

## 9. Bypass Permissions voor Systeem Operaties

```python
def system_update_status(docname, new_status):
    """Systeem update die permissions moet bypassen."""
    # Documenteer WAAROM permissions worden genegeerd
    # Dit is een geplande systeem operatie, niet user-initiated
    
    doc = frappe.get_doc("Sales Order", docname)
    doc.flags.ignore_permissions = True
    doc.status = new_status
    doc.save()
    
    # OF gebruik db_set voor directe update
    frappe.db.set_value(
        "Sales Order", 
        docname, 
        "status", 
        new_status,
        update_modified=False  # db operaties negeren standaard perms
    )
```

## 10. Dynamic Permission Based on Document State

```python
# hooks.py
has_permission = {
    "Purchase Order": "myapp.permissions.po_permission"
}

# myapp/permissions.py
def po_permission(doc, ptype, user):
    """
    Beperk write access tot drafts voor niet-managers.
    Submitted/cancelled orders zijn read-only voor iedereen behalve managers.
    """
    if ptype != "write":
        return None  # Ga door met standaard checks
    
    # Managers kunnen altijd schrijven
    if "Purchase Manager" in frappe.get_roles(user):
        return None
    
    # Niet-managers kunnen alleen drafts bewerken
    if doc.docstatus != 0:
        return False
    
    return None
```
