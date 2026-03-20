# Error Handling Patterns - Permissions

Complete error handling patterns for Frappe/ERPNext permission system.

---

## Pattern 1: Comprehensive has_permission Hook

```python
# myapp/permissions.py
import frappe

def sales_order_has_permission(doc, ptype, user):
    """
    Complete has_permission implementation with error handling.
    
    Args:
        doc: Document object or dict
        ptype: Permission type (read, write, create, delete, submit, cancel)
        user: User email or None for current user
    
    Returns:
        None: Defer to standard permission system
        False: Deny permission
        
    NEVER return True - hooks can only restrict, not grant.
    """
    try:
        user = user or frappe.session.user
        
        # Skip for Administrator
        if user == "Administrator":
            return None
        
        roles = frappe.get_roles(user)
        
        # System Manager has full access
        if "System Manager" in roles:
            return None
        
        # Get document status safely
        status = doc.get("status") if hasattr(doc, "get") else getattr(doc, "status", None)
        docstatus = doc.get("docstatus") if hasattr(doc, "get") else getattr(doc, "docstatus", 0)
        
        # Rule 1: No editing cancelled documents
        if ptype == "write" and docstatus == 2:
            return False
        
        # Rule 2: Only managers can delete
        if ptype == "delete":
            if "Sales Manager" not in roles:
                return False
        
        # Rule 3: Locked documents are read-only
        if status == "Locked" and ptype in ["write", "delete", "cancel"]:
            if "Sales Manager" not in roles:
                return False
        
        # Rule 4: Confidential documents
        is_confidential = doc.get("is_confidential") if hasattr(doc, "get") else getattr(doc, "is_confidential", 0)
        if is_confidential:
            allowed = get_confidential_access_list(doc)
            if user not in allowed:
                return False
        
        # Rule 5: Territory-based access
        if ptype == "read":
            territory_access = check_territory_access(doc, user)
            if territory_access is False:
                return False
        
        # Defer to standard permission system
        return None
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"has_permission error: {getattr(doc, 'name', 'unknown')}"
        )
        # Safe fallback - defer to standard system
        return None


def get_confidential_access_list(doc):
    """Get users with confidential access - returns empty list on error."""
    try:
        doc_name = doc.get("name") if hasattr(doc, "get") else getattr(doc, "name", None)
        if not doc_name:
            return []
        
        # Document owner always has access
        owner = doc.get("owner") if hasattr(doc, "get") else getattr(doc, "owner", None)
        allowed = [owner] if owner else []
        
        # Add explicitly allowed users
        allowed_records = frappe.get_all(
            "Sales Order Access",
            filters={"parent": doc_name},
            pluck="user"
        )
        allowed.extend(allowed_records or [])
        
        return allowed
        
    except Exception:
        return []


def check_territory_access(doc, user):
    """Check territory-based access - returns None on error."""
    try:
        doc_territory = doc.get("territory") if hasattr(doc, "get") else getattr(doc, "territory", None)
        if not doc_territory:
            return None  # No territory restriction
        
        user_territories = frappe.get_all(
            "User Permission",
            filters={
                "user": user,
                "allow": "Territory",
                "applicable_for": ["in", ["", "Sales Order"]]
            },
            pluck="for_value"
        )
        
        if not user_territories:
            return None  # No territory restrictions for user
        
        if doc_territory not in user_territories:
            return False  # Deny - territory mismatch
        
        return None  # Allow - territory matches
        
    except Exception:
        return None  # Error - defer to standard
```

---

## Pattern 2: Comprehensive permission_query_conditions

```python
# myapp/permissions.py
import frappe

def sales_order_query_conditions(user):
    """
    Complete permission query implementation.
    
    Args:
        user: User email or None for current user
    
    Returns:
        str: SQL WHERE clause fragment (empty string for no restriction)
        
    NEVER throw errors - return restrictive fallback.
    """
    try:
        if not user:
            user = frappe.session.user
        
        # Guest users see nothing
        if user == "Guest":
            return "1=0"
        
        # Administrator sees all
        if user == "Administrator":
            return ""
        
        roles = frappe.get_roles(user)
        
        # System Manager sees all
        if "System Manager" in roles:
            return ""
        
        conditions = []
        
        # Sales Manager sees all non-confidential + assigned
        if "Sales Manager" in roles:
            conditions.append(f"""
                (`tabSales Order`.is_confidential = 0
                OR `tabSales Order`.owner = {frappe.db.escape(user)}
                OR EXISTS (
                    SELECT 1 FROM `tabSales Order Access`
                    WHERE `tabSales Order Access`.parent = `tabSales Order`.name
                    AND `tabSales Order Access`.user = {frappe.db.escape(user)}
                ))
            """)
        
        # Sales User sees own + team (if team configured)
        elif "Sales User" in roles:
            team_condition = get_team_condition(user)
            if team_condition:
                conditions.append(f"""
                    (`tabSales Order`.owner = {frappe.db.escape(user)}
                    OR {team_condition})
                    AND `tabSales Order`.is_confidential = 0
                """)
            else:
                conditions.append(f"""
                    `tabSales Order`.owner = {frappe.db.escape(user)}
                    AND `tabSales Order`.is_confidential = 0
                """)
        
        # Default: own non-confidential records
        else:
            conditions.append(f"""
                `tabSales Order`.owner = {frappe.db.escape(user)}
                AND `tabSales Order`.is_confidential = 0
            """)
        
        # Add territory filter if applicable
        territory_condition = get_territory_condition(user)
        if territory_condition:
            conditions.append(territory_condition)
        
        return " AND ".join([f"({c.strip()})" for c in conditions])
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Query conditions error for {user}"
        )
        # SAFE FALLBACK: Most restrictive
        return f"`tabSales Order`.owner = {frappe.db.escape(frappe.session.user)}"


def get_team_condition(user):
    """Get team-based filter condition - returns None on error."""
    try:
        # Get user's department/team
        department = frappe.db.get_value("User", user, "department")
        if not department:
            return None
        
        # Get team members
        team_members = frappe.get_all(
            "User",
            filters={"department": department, "enabled": 1},
            pluck="name"
        )
        
        if not team_members or len(team_members) <= 1:
            return None
        
        escaped = ", ".join([frappe.db.escape(u) for u in team_members])
        return f"`tabSales Order`.owner IN ({escaped})"
        
    except Exception:
        return None


def get_territory_condition(user):
    """Get territory-based filter condition - returns None on error."""
    try:
        territories = frappe.get_all(
            "User Permission",
            filters={
                "user": user,
                "allow": "Territory",
                "applicable_for": ["in", ["", "Sales Order"]]
            },
            pluck="for_value"
        )
        
        if not territories:
            return None
        
        escaped = ", ".join([frappe.db.escape(t) for t in territories])
        return f"(`tabSales Order`.territory IN ({escaped}) OR `tabSales Order`.territory IS NULL)"
        
    except Exception:
        return None
```

---

## Pattern 3: API Endpoint with Permission Handling

```python
# myapp/api.py
import frappe
from frappe import _

@frappe.whitelist()
def get_order_details(order_name):
    """
    API endpoint with comprehensive permission handling.
    """
    # Validate input
    if not order_name:
        frappe.throw(
            _("Order name is required"),
            exc=frappe.ValidationError
        )
    
    # Check existence
    if not frappe.db.exists("Sales Order", order_name):
        frappe.throw(
            _("Sales Order {0} not found").format(order_name),
            exc=frappe.DoesNotExistError
        )
    
    # Check permission - throws PermissionError automatically
    frappe.has_permission("Sales Order", "read", order_name, throw=True)
    
    # Get document
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Filter fields based on permission level
    result = {
        "name": doc.name,
        "customer": doc.customer,
        "status": doc.status,
        "grand_total": doc.grand_total
    }
    
    # Add sensitive fields only for managers
    if "Sales Manager" in frappe.get_roles():
        result["margin"] = doc.get("margin")
        result["cost"] = doc.get("cost")
    
    return result


@frappe.whitelist()
def approve_order(order_name):
    """
    Approval endpoint with role check and audit.
    """
    # Role restriction
    frappe.only_for(["Sales Manager", "General Manager"])
    
    # Get document
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Check document-level permission
    if not doc.has_permission("write"):
        frappe.throw(
            _("You don't have permission to approve this order"),
            exc=frappe.PermissionError
        )
    
    # Check business rules
    if doc.status != "Pending Approval":
        frappe.throw(
            _("Only orders with 'Pending Approval' status can be approved"),
            exc=frappe.ValidationError
        )
    
    # Perform action
    doc.status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approved_on = frappe.utils.now()
    doc.save()
    
    # Audit log
    frappe.get_doc({
        "doctype": "Activity Log",
        "subject": f"Order {order_name} approved",
        "reference_doctype": "Sales Order",
        "reference_name": order_name,
        "content": f"Approved by {frappe.session.user}"
    }).insert(ignore_permissions=True)
    
    return {"status": "success", "message": _("Order approved successfully")}


@frappe.whitelist()
def bulk_update_orders(orders, status):
    """
    Bulk operation with per-document permission check.
    """
    if not orders:
        frappe.throw(_("No orders specified"))
    
    results = {
        "success": [],
        "failed": [],
        "permission_denied": []
    }
    
    for order_name in orders:
        # Check existence
        if not frappe.db.exists("Sales Order", order_name):
            results["failed"].append({
                "name": order_name,
                "error": "Not found"
            })
            continue
        
        # Check permission
        if not frappe.has_permission("Sales Order", "write", order_name):
            results["permission_denied"].append(order_name)
            continue
        
        # Update
        try:
            frappe.db.set_value("Sales Order", order_name, "status", status)
            results["success"].append(order_name)
        except Exception as e:
            results["failed"].append({
                "name": order_name,
                "error": str(e)
            })
    
    frappe.db.commit()
    
    # Notify if any permission denied
    if results["permission_denied"]:
        frappe.msgprint(
            _("You don't have permission to update: {0}").format(
                ", ".join(results["permission_denied"])
            ),
            indicator="orange"
        )
    
    return results
```

---

## Pattern 4: Controller with Permission Checks

```python
# myapp/doctype/confidential_document/confidential_document.py
import frappe
from frappe import _
from frappe.model.document import Document

class ConfidentialDocument(Document):
    def validate(self):
        """Validate with permission checks."""
        # Check if user can set confidential flag
        if self.is_confidential and not self.is_new():
            old_doc = self.get_doc_before_save()
            if old_doc and not old_doc.is_confidential:
                # Changing to confidential - need special permission
                if not self.has_confidential_permission():
                    frappe.throw(
                        _("You don't have permission to mark documents as confidential"),
                        exc=frappe.PermissionError
                    )
    
    def has_confidential_permission(self):
        """Check if user can set confidential flag."""
        allowed_roles = ["System Manager", "Compliance Manager"]
        return any(role in frappe.get_roles() for role in allowed_roles)
    
    def before_save(self):
        """Additional permission checks before save."""
        if self.is_new():
            return
        
        # Check if user is trying to access others' confidential doc
        if self.is_confidential and self.owner != frappe.session.user:
            if not self.is_in_access_list(frappe.session.user):
                frappe.throw(
                    _("You don't have permission to modify this confidential document"),
                    exc=frappe.PermissionError
                )
    
    def is_in_access_list(self, user):
        """Check if user is in access list."""
        try:
            return frappe.db.exists(
                "Confidential Document Access",
                {"parent": self.name, "user": user}
            )
        except Exception:
            return False
    
    @frappe.whitelist()
    def grant_access(self, user):
        """Grant access to user with permission check."""
        # Only owner or admin can grant access
        if self.owner != frappe.session.user:
            if "System Manager" not in frappe.get_roles():
                frappe.throw(
                    _("Only the document owner can grant access"),
                    exc=frappe.PermissionError
                )
        
        # Validate user exists
        if not frappe.db.exists("User", user):
            frappe.throw(_("User {0} not found").format(user))
        
        # Add to access list
        if not self.is_in_access_list(user):
            self.append("access_list", {"user": user})
            self.save()
        
        return {"status": "success"}
    
    @frappe.whitelist()
    def revoke_access(self, user):
        """Revoke access from user with permission check."""
        if self.owner != frappe.session.user:
            if "System Manager" not in frappe.get_roles():
                frappe.throw(
                    _("Only the document owner can revoke access"),
                    exc=frappe.PermissionError
                )
        
        # Remove from access list
        self.access_list = [d for d in self.access_list if d.user != user]
        self.save()
        
        return {"status": "success"}
```

---

## Pattern 5: Graceful Permission Degradation

```python
# myapp/api.py
import frappe
from frappe import _

@frappe.whitelist()
def get_dashboard_data():
    """
    Return dashboard data based on user permissions.
    No errors - just returns what user can see.
    """
    data = {
        "widgets": [],
        "stats": {},
        "recent_items": []
    }
    
    # Sales widget - if has Sales Order read permission
    if frappe.has_permission("Sales Order", "read"):
        try:
            data["widgets"].append({
                "type": "sales",
                "data": get_sales_summary()
            })
            data["stats"]["sales"] = get_sales_stats()
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Dashboard: Sales Widget Error")
    
    # Purchase widget - if has Purchase Order read permission
    if frappe.has_permission("Purchase Order", "read"):
        try:
            data["widgets"].append({
                "type": "purchase",
                "data": get_purchase_summary()
            })
            data["stats"]["purchase"] = get_purchase_stats()
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Dashboard: Purchase Widget Error")
    
    # HR widget - if has Employee read permission
    if frappe.has_permission("Employee", "read"):
        try:
            data["widgets"].append({
                "type": "hr",
                "data": get_hr_summary()
            })
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Dashboard: HR Widget Error")
    
    # Recent items - filter by permission
    try:
        data["recent_items"] = get_recent_items_with_permission()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Dashboard: Recent Items Error")
    
    return data


def get_recent_items_with_permission():
    """Get recent items user has access to."""
    recent = []
    
    doctypes = ["Sales Order", "Purchase Order", "Quotation"]
    
    for dt in doctypes:
        if not frappe.has_permission(dt, "read"):
            continue
        
        try:
            # Use get_list to respect permissions
            items = frappe.get_list(
                dt,
                fields=["name", "modified", "status"],
                order_by="modified desc",
                limit=5
            )
            
            for item in items:
                recent.append({
                    "doctype": dt,
                    "name": item.name,
                    "modified": item.modified,
                    "status": item.status
                })
        except Exception:
            pass  # Skip this doctype on error
    
    # Sort by modified date
    recent.sort(key=lambda x: x["modified"], reverse=True)
    
    return recent[:10]
```

---

## Pattern 6: Security Audit Logging

```python
# myapp/permissions.py
import frappe

def log_permission_check(doc, ptype, user, result):
    """Log permission checks for audit."""
    if not should_log_permission(doc, ptype):
        return
    
    try:
        frappe.get_doc({
            "doctype": "Permission Audit Log",
            "user": user,
            "doctype_name": doc.doctype if hasattr(doc, "doctype") else "Unknown",
            "document": doc.name if hasattr(doc, "name") else "Unknown",
            "permission_type": ptype,
            "result": "Allowed" if result is None else "Denied",
            "timestamp": frappe.utils.now()
        }).insert(ignore_permissions=True)
    except Exception:
        # Never break permission check for logging failure
        pass


def should_log_permission(doc, ptype):
    """Determine if this permission check should be logged."""
    # Log sensitive operations
    sensitive_doctypes = ["Employee", "Salary Slip", "Bank Account"]
    sensitive_ptypes = ["write", "delete", "submit", "cancel"]
    
    doctype = doc.doctype if hasattr(doc, "doctype") else None
    
    return doctype in sensitive_doctypes or ptype in sensitive_ptypes


def log_access_denied(doc, ptype, user, reason):
    """Log access denied events."""
    try:
        frappe.get_doc({
            "doctype": "Security Event",
            "event_type": "Access Denied",
            "user": user,
            "reference_doctype": doc.doctype if hasattr(doc, "doctype") else None,
            "reference_name": doc.name if hasattr(doc, "name") else None,
            "details": f"Permission: {ptype}, Reason: {reason}",
            "timestamp": frappe.utils.now(),
            "ip_address": frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None
        }).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Security Event Log Error")
```

---

## Quick Reference: Permission Error Handling

| Scenario | Method | Error Type |
|----------|--------|------------|
| Check before action | `frappe.has_permission(throw=True)` | PermissionError |
| Document check | `doc.check_permission()` | PermissionError |
| Role restriction | `frappe.only_for()` | PermissionError |
| Custom denial | `frappe.throw(exc=PermissionError)` | PermissionError |
| has_permission hook | `return False` | N/A (silent deny) |
| query_conditions | Return restrictive SQL | N/A (filter only) |
