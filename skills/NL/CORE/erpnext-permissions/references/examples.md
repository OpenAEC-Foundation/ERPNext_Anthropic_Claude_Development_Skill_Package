# Permission Examples

> Reference for erpnext-permissions skill

---

## Example 1: Basic Permission Check

### Scenario
Check if user can edit a Sales Order before updating.

### Code

```python
@frappe.whitelist()
def update_order_status(order_name, new_status):
    """Update Sales Order status with permission check."""
    
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Check write permission
    if not doc.has_permission("write"):
        frappe.throw(
            _("You don't have permission to edit this Sales Order"),
            frappe.PermissionError
        )
    
    doc.status = new_status
    doc.save()
    
    return {"status": "success"}
```

### Alternative: Using check_permission

```python
@frappe.whitelist()
def update_order_status(order_name, new_status):
    """Update Sales Order status - raises error if no permission."""
    
    doc = frappe.get_doc("Sales Order", order_name)
    doc.check_permission("write")  # Raises PermissionError if denied
    
    doc.status = new_status
    doc.save()
    
    return {"status": "success"}
```

---

## Example 2: Owner-Only Edit Pattern

### Scenario
Users can only edit documents they created, managers can edit all.

### DocType Configuration

```json
{
  "permissions": [
    {
      "role": "Sales User",
      "permlevel": 0,
      "read": 1,
      "write": 1,
      "create": 1,
      "if_owner": 1
    },
    {
      "role": "Sales Manager",
      "permlevel": 0,
      "read": 1,
      "write": 1,
      "create": 1,
      "delete": 1,
      "if_owner": 0
    }
  ]
}
```

### Effect
- Sales User: Can read/write/create only their own documents
- Sales Manager: Can read/write/create/delete all documents

---

## Example 3: Field-Level Permissions

### Scenario
Hide salary information from regular users, show to HR only.

### Step 1: Set Perm Level on Fields

```json
// In Employee DocType
{
  "fields": [
    {"fieldname": "employee_name", "permlevel": 0},
    {"fieldname": "department", "permlevel": 0},
    {"fieldname": "salary", "permlevel": 1},
    {"fieldname": "bank_account", "permlevel": 1}
  ]
}
```

### Step 2: Configure Role Permissions

```json
{
  "permissions": [
    {
      "role": "Employee Self Service",
      "permlevel": 0,
      "read": 1
    },
    {
      "role": "HR Manager",
      "permlevel": 0,
      "read": 1,
      "write": 1
    },
    {
      "role": "HR Manager",
      "permlevel": 1,
      "read": 1,
      "write": 1
    }
  ]
}
```

### Effect
- Employee Self Service: Sees name and department only
- HR Manager: Sees all fields including salary

---

## Example 4: User Permissions for Multi-Company

### Scenario
Restrict users to see only documents from their assigned companies.

### Setup Code

```python
def setup_user_company_restriction(user, company):
    """Restrict user to specific company."""
    from frappe.permissions import add_user_permission
    
    add_user_permission(
        doctype="Company",
        name=company,
        user=user,
        ignore_permissions=True,
        is_default=1  # Set as default for new documents
    )
```

### Bulk Setup

```python
def setup_company_restrictions():
    """Setup company restrictions for all users."""
    
    user_companies = [
        ("john@example.com", "Company A"),
        ("jane@example.com", "Company B"),
        ("bob@example.com", "Company A"),
    ]
    
    for user, company in user_companies:
        setup_user_company_restriction(user, company)
```

### Effect
- Each user only sees documents linked to their company
- New documents auto-select their default company

---

## Example 5: Custom Permission Hook

### Scenario
Deny editing of invoices older than 30 days for non-accountants.

### hooks.py

```python
has_permission = {
    "Sales Invoice": "myapp.permissions.invoice_permission"
}
```

### Permission Function

```python
# myapp/permissions.py
import frappe
from frappe.utils import date_diff, today

def invoice_permission(doc, ptype, user):
    """
    Deny editing invoices older than 30 days.
    Accountants exempt from this restriction.
    """
    if ptype not in ("write", "cancel"):
        return None  # Only restrict write and cancel
    
    # Accountants can always edit
    if "Accounts Manager" in frappe.get_roles(user):
        return None
    
    # Check invoice age
    if doc.posting_date:
        age = date_diff(today(), doc.posting_date)
        if age > 30:
            return False  # Deny permission
    
    return None  # Allow - continue standard checks
```

---

## Example 6: Dynamic Query Conditions

### Scenario
Sales Users see only customers in their assigned territories.

### hooks.py

```python
permission_query_conditions = {
    "Customer": "myapp.permissions.customer_territory_query"
}
```

### Query Function

```python
# myapp/permissions.py
import frappe

def customer_territory_query(user):
    """Filter customers by user's territory assignments."""
    if not user:
        user = frappe.session.user
    
    # Managers see all customers
    if "Sales Manager" in frappe.get_roles(user):
        return ""
    
    # Get user's territories from User Permissions
    territories = frappe.get_all(
        "User Permission",
        filters={
            "user": user,
            "allow": "Territory",
            "apply_to_all_doctypes": 1
        },
        pluck="for_value"
    )
    
    if not territories:
        # No territory restrictions
        return ""
    
    # Build SQL IN clause
    escaped_territories = [frappe.db.escape(t) for t in territories]
    territory_list = ", ".join(escaped_territories)
    
    return f"`tabCustomer`.territory IN ({territory_list})"
```

---

## Example 7: Document Sharing

### Scenario
Share a specific Sales Order with an external reviewer.

### Code

```python
from frappe.share import add as add_share, remove as remove_share

def share_order_for_review(order_name, reviewer_email):
    """Share Sales Order with reviewer (read-only)."""
    
    add_share(
        doctype="Sales Order",
        name=order_name,
        user=reviewer_email,
        read=1,
        write=0,
        share=0,
        notify=1  # Send email notification
    )
    
    frappe.msgprint(f"Shared with {reviewer_email}")


def revoke_reviewer_access(order_name, reviewer_email):
    """Remove reviewer's access."""
    
    remove_share(
        doctype="Sales Order",
        name=order_name,
        user=reviewer_email
    )
```

---

## Example 8: Checking Permissions in Controller

### Scenario
Validate user has approval authority before allowing status change.

### Controller Code

```python
# my_doctype/my_doctype.py
class MyDocType(Document):
    def validate(self):
        self.validate_approver_permission()
    
    def validate_approver_permission(self):
        """Check if user can approve this document."""
        
        if self.has_value_changed("status"):
            if self.status == "Approved":
                # Check custom approval permission
                if not frappe.has_permission(self.doctype, "write", self):
                    frappe.throw(
                        _("You don't have permission to approve"),
                        frappe.PermissionError
                    )
                
                # Additional business logic
                if self.amount > 50000:
                    if "Finance Manager" not in frappe.get_roles():
                        frappe.throw(
                            _("Finance Manager approval required for amounts > 50,000")
                        )
```

---

## Example 9: Programmatic Permission Setup

### Scenario
Create a new role with specific permissions during app installation.

### Setup Code

```python
def after_install():
    """Setup permissions after app installation."""
    create_custom_role()
    setup_role_permissions()


def create_custom_role():
    """Create Custom Reviewer role."""
    if not frappe.db.exists("Role", "Custom Reviewer"):
        role = frappe.new_doc("Role")
        role.role_name = "Custom Reviewer"
        role.desk_access = 1
        role.insert(ignore_permissions=True)


def setup_role_permissions():
    """Setup permissions for Custom Reviewer."""
    from frappe.permissions import add_permission, update_permission_property
    
    # Add permission to Sales Order
    add_permission("Sales Order", "Custom Reviewer", permlevel=0)
    
    # Configure permission details
    update_permission_property("Sales Order", "Custom Reviewer", 0, "read", 1)
    update_permission_property("Sales Order", "Custom Reviewer", 0, "write", 0)
    update_permission_property("Sales Order", "Custom Reviewer", 0, "report", 1)
    update_permission_property("Sales Order", "Custom Reviewer", 0, "export", 1)
    
    # Clear cache
    frappe.clear_cache()
```

---

## Example 10: API Endpoint with Role Restriction

### Scenario
Create API endpoint accessible only to specific roles.

### Code

```python
@frappe.whitelist()
def get_confidential_report():
    """API endpoint restricted to Managers."""
    
    # Method 1: Using only_for
    frappe.only_for(["Sales Manager", "System Manager"])
    
    # If we reach here, user has required role
    return generate_report()


@frappe.whitelist()
def approve_all_pending():
    """Approve all pending orders - restricted endpoint."""
    
    # Method 2: Manual check
    allowed_roles = ["Approver", "System Manager"]
    user_roles = frappe.get_roles()
    
    if not any(role in user_roles for role in allowed_roles):
        frappe.throw(
            _("Only Approvers can perform this action"),
            frappe.PermissionError
        )
    
    # Proceed with bulk approval
    pending = frappe.get_all(
        "Sales Order",
        filters={"status": "Pending Approval"},
        pluck="name"
    )
    
    for name in pending:
        doc = frappe.get_doc("Sales Order", name)
        doc.status = "Approved"
        doc.save(ignore_permissions=True)  # System action
    
    return {"approved": len(pending)}
```

---

## Example 11: Combined Hook System

### Complete Example

```python
# hooks.py
has_permission = {
    "Project": "myapp.project_permissions.check_permission"
}

permission_query_conditions = {
    "Project": "myapp.project_permissions.get_query_conditions"
}
```

```python
# myapp/project_permissions.py
import frappe

def check_permission(doc, ptype, user):
    """
    Permission logic:
    - Project Managers: full access
    - Team members: read/write
    - Others: no access
    """
    if not user:
        user = frappe.session.user
    
    # Managers have full access
    if "Projects Manager" in frappe.get_roles(user):
        return None
    
    # Check team membership
    if is_team_member(doc.name, user):
        if ptype in ("read", "write"):
            return None  # Allow
        return False  # Deny delete, etc.
    
    return False  # Not a team member


def get_query_conditions(user):
    """
    List filter: show only projects user is member of.
    """
    if not user:
        user = frappe.session.user
    
    # Managers see all
    if "Projects Manager" in frappe.get_roles(user):
        return ""
    
    return """
        `tabProject`.name IN (
            SELECT parent FROM `tabProject User`
            WHERE user = {user}
        )
    """.format(user=frappe.db.escape(user))


def is_team_member(project, user):
    """Check if user is a project team member."""
    return frappe.db.exists(
        "Project User",
        {"parent": project, "user": user}
    )
```
