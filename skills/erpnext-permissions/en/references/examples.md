# Permission Examples

## 1. Check Permission Before Action

```python
@frappe.whitelist()
def approve_order(order_name):
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Check custom permission
    if not frappe.has_permission(doc.doctype, "write", doc):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Check additional business logic
    if "Approver" not in frappe.get_roles():
        frappe.throw(_("Only Approvers can approve orders"))
    
    doc.status = "Approved"
    doc.save()
```

## 2. Owner-Only Access Pattern

```python
# Option A: Via DocType permissions, set if_owner = 1 for a role

# Option B: Check programmatically
def can_edit(doc):
    if doc.owner == frappe.session.user:
        return True
    if "Manager" in frappe.get_roles():
        return True
    return False
```

## 3. Hierarchical Permission Check

```python
def check_territory_access(doc, user=None):
    """Check if user has access to document's territory."""
    if not user:
        user = frappe.session.user
    
    user_territories = frappe.get_all(
        "User Permission",
        filters={"user": user, "allow": "Territory"},
        pluck="for_value"
    )
    
    if not user_territories:
        return True  # No restrictions
    
    return doc.territory in user_territories
```

## 4. Add User Permission on Document Creation

```python
# In DocType controller
class Employee(Document):
    def after_insert(self):
        # Give employee access to their own record
        if self.user_id:
            from frappe.permissions import add_user_permission
            add_user_permission(
                "Employee",
                self.name,
                self.user_id,
                ignore_permissions=True
            )
```

## 5. Permission Query for Multi-Tenant Setup

```python
# hooks.py
permission_query_conditions = {
    "Customer": "myapp.permissions.customer_query"
}

# myapp/permissions.py
def customer_query(user):
    if not user:
        user = frappe.session.user
    
    # Admin sees everything
    if "System Manager" in frappe.get_roles(user):
        return ""
    
    # Get user's company
    company = frappe.db.get_value("User", user, "default_company")
    if not company:
        return "1=0"  # No access if no company
    
    return f"`tabCustomer`.company = {frappe.db.escape(company)}"
```

## 6. Conditional Field Access via Perm Levels

```python
# Step 1: Set permlevel on field in DocType/Customize Form
{
    "fieldname": "internal_notes",
    "fieldtype": "Text",
    "permlevel": 1
}

# Step 2: Grant only specific roles level 1 access
# Via Role Permission Manager:
# - Sales Manager: Level 0 + Level 1 (read, write)
# - Sales User: Level 0 only (cannot see internal_notes)
```

## 7. Share Document Programmatically

```python
def share_with_approvers(doc):
    """Share document with all users in Approver role."""
    from frappe.share import add as add_share
    
    approvers = frappe.get_all(
        "Has Role",
        filters={"role": "Approver", "parenttype": "User"},
        pluck="parent"
    )
    
    for approver in approvers:
        if approver != doc.owner:  # Don't share with owner
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
# Controller for portal page
def get_context(context):
    # Check if user has access
    if not frappe.has_permission("Sales Order", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Get only documents user can see
    context.orders = frappe.get_list(
        "Sales Order",
        filters={"customer": frappe.session.user},
        fields=["name", "status", "grand_total"]
    )
```

## 9. Bypass Permissions for System Operations

```python
def system_update_status(docname, new_status):
    """System update that must bypass permissions."""
    # Document WHY permissions are being ignored
    # This is a scheduled system operation, not user-initiated
    
    doc = frappe.get_doc("Sales Order", docname)
    doc.flags.ignore_permissions = True
    doc.status = new_status
    doc.save()
    
    # OR use db_set for direct update
    frappe.db.set_value(
        "Sales Order", 
        docname, 
        "status", 
        new_status,
        update_modified=False  # db operations ignore perms by default
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
    Restrict write access to drafts for non-managers.
    Submitted/cancelled orders are read-only for everyone except managers.
    """
    if ptype != "write":
        return None  # Continue with standard checks
    
    # Managers can always write
    if "Purchase Manager" in frappe.get_roles(user):
        return None
    
    # Non-managers can only edit drafts
    if doc.docstatus != 0:
        return False
    
    return None
```
