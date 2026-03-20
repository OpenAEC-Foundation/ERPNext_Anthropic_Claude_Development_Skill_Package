# Examples - Permission Error Handling

Complete working examples of permission error handling in Frappe/ERPNext.

---

## Example 1: Complete hooks.py Permission Configuration

```python
# myapp/hooks.py

app_name = "myapp"
app_title = "My App"

# Permission hooks
has_permission = {
    "Sales Order": "myapp.permissions.sales_order_has_permission",
    "Confidential Report": "myapp.permissions.confidential_has_permission"
}

permission_query_conditions = {
    "Sales Order": "myapp.permissions.sales_order_query",
    "Confidential Report": "myapp.permissions.confidential_query"
}
```

```python
# myapp/permissions.py
import frappe
from frappe import _

# =============================================================================
# SALES ORDER PERMISSIONS
# =============================================================================

def sales_order_has_permission(doc, ptype, user):
    """
    Sales Order document-level permission.
    
    Rules:
    - Cancelled orders are read-only except for System Manager
    - Orders > 100k need manager approval for submit
    - Territory restrictions apply
    """
    try:
        user = user or frappe.session.user
        
        if user == "Administrator":
            return None
        
        roles = frappe.get_roles(user)
        
        # System Manager bypasses custom checks
        if "System Manager" in roles:
            return None
        
        # Get document data safely
        docstatus = doc.get("docstatus") if hasattr(doc, "get") else getattr(doc, "docstatus", 0)
        grand_total = doc.get("grand_total") if hasattr(doc, "get") else getattr(doc, "grand_total", 0)
        
        # Rule 1: Cancelled documents are read-only
        if docstatus == 2 and ptype != "read":
            return False
        
        # Rule 2: Large orders need manager for submit
        if ptype == "submit" and grand_total > 100000:
            if "Sales Manager" not in roles:
                return False
        
        # Rule 3: Check territory access
        territory = doc.get("territory") if hasattr(doc, "get") else getattr(doc, "territory", None)
        if territory and ptype in ["read", "write"]:
            if not has_territory_access(user, territory):
                return False
        
        return None
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Sales Order permission error: {getattr(doc, 'name', 'unknown')}"
        )
        return None


def sales_order_query(user):
    """Sales Order list filter conditions."""
    try:
        if not user:
            user = frappe.session.user
        
        if user == "Administrator":
            return ""
        
        roles = frappe.get_roles(user)
        
        if "System Manager" in roles or "Sales Manager" in roles:
            return ""
        
        # Get user's territories
        territories = get_user_territories(user)
        
        if territories:
            escaped = ", ".join([frappe.db.escape(t) for t in territories])
            return f"""
                (`tabSales Order`.territory IN ({escaped})
                OR `tabSales Order`.owner = {frappe.db.escape(user)})
            """
        
        return f"`tabSales Order`.owner = {frappe.db.escape(user)}"
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Sales Order query error")
        return f"`tabSales Order`.owner = {frappe.db.escape(frappe.session.user)}"


# =============================================================================
# CONFIDENTIAL REPORT PERMISSIONS
# =============================================================================

def confidential_has_permission(doc, ptype, user):
    """
    Confidential Report - strict access control.
    
    Only explicitly granted users can access.
    """
    try:
        user = user or frappe.session.user
        
        if user == "Administrator":
            return None
        
        # Check if user is in access list
        doc_name = doc.get("name") if hasattr(doc, "get") else getattr(doc, "name", None)
        if not doc_name:
            return None
        
        # Owner always has access
        owner = doc.get("owner") if hasattr(doc, "get") else getattr(doc, "owner", None)
        if user == owner:
            return None
        
        # Check explicit access
        has_access = frappe.db.exists(
            "Confidential Report Access",
            {"parent": doc_name, "user": user}
        )
        
        if not has_access:
            # Log denied access attempt
            log_denied_access(doc_name, user, ptype)
            return False
        
        # Check access level
        access_record = frappe.db.get_value(
            "Confidential Report Access",
            {"parent": doc_name, "user": user},
            ["read_access", "write_access"],
            as_dict=True
        )
        
        if ptype == "read" and not access_record.read_access:
            return False
        
        if ptype in ["write", "delete"] and not access_record.write_access:
            return False
        
        return None
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Confidential permission error: {getattr(doc, 'name', 'unknown')}"
        )
        return False  # Deny on error for confidential docs


def confidential_query(user):
    """Confidential Report - show only accessible reports."""
    try:
        if not user:
            user = frappe.session.user
        
        if user == "Administrator":
            return ""
        
        # Show own reports + explicitly granted
        return f"""
            (`tabConfidential Report`.owner = {frappe.db.escape(user)}
            OR EXISTS (
                SELECT 1 FROM `tabConfidential Report Access`
                WHERE `tabConfidential Report Access`.parent = `tabConfidential Report`.name
                AND `tabConfidential Report Access`.user = {frappe.db.escape(user)}
                AND `tabConfidential Report Access`.read_access = 1
            ))
        """
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Confidential query error")
        return f"`tabConfidential Report`.owner = {frappe.db.escape(frappe.session.user)}"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def has_territory_access(user, territory):
    """Check if user has access to territory."""
    try:
        return frappe.db.exists(
            "User Permission",
            {
                "user": user,
                "allow": "Territory",
                "for_value": territory
            }
        ) or not frappe.db.count(
            "User Permission",
            {"user": user, "allow": "Territory"}
        )  # No territory restrictions = access all
    except Exception:
        return True  # Allow on error


def get_user_territories(user):
    """Get user's permitted territories."""
    try:
        return frappe.get_all(
            "User Permission",
            filters={"user": user, "allow": "Territory"},
            pluck="for_value"
        ) or []
    except Exception:
        return []


def log_denied_access(doc_name, user, ptype):
    """Log denied access for audit."""
    try:
        frappe.get_doc({
            "doctype": "Access Log",
            "document_type": "Confidential Report",
            "document_name": doc_name,
            "user": user,
            "permission_type": ptype,
            "status": "Denied",
            "timestamp": frappe.utils.now()
        }).insert(ignore_permissions=True)
    except Exception:
        pass  # Never break permission for logging
```

---

## Example 2: API Endpoints with Permission Handling

```python
# myapp/api.py
import frappe
from frappe import _

@frappe.whitelist()
def get_order_summary(order_name):
    """
    Get order summary with permission check.
    
    Returns filtered data based on user's access level.
    """
    # Validate input
    if not order_name:
        frappe.throw(_("Order name is required"), exc=frappe.ValidationError)
    
    # Check existence
    if not frappe.db.exists("Sales Order", order_name):
        frappe.throw(
            _("Sales Order {0} not found").format(order_name),
            exc=frappe.DoesNotExistError
        )
    
    # Check permission
    if not frappe.has_permission("Sales Order", "read", order_name):
        frappe.throw(
            _("You don't have permission to view this order"),
            exc=frappe.PermissionError
        )
    
    # Get document
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Base data everyone can see
    result = {
        "name": doc.name,
        "customer": doc.customer,
        "status": doc.status,
        "transaction_date": doc.transaction_date,
        "delivery_date": doc.delivery_date,
        "items_count": len(doc.items)
    }
    
    # Financial data for authorized roles
    financial_roles = ["Accounts User", "Accounts Manager", "Sales Manager", "System Manager"]
    if any(role in frappe.get_roles() for role in financial_roles):
        result.update({
            "total": doc.total,
            "grand_total": doc.grand_total,
            "taxes": doc.total_taxes_and_charges
        })
    
    # Cost/margin data for managers only
    if "Sales Manager" in frappe.get_roles() or "System Manager" in frappe.get_roles():
        result.update({
            "margin": doc.get("margin"),
            "margin_percent": doc.get("margin_percent")
        })
    
    return result


@frappe.whitelist()
def update_order_status(order_name, new_status):
    """
    Update order status with comprehensive permission handling.
    """
    # Validate inputs
    if not order_name or not new_status:
        frappe.throw(_("Order name and status are required"))
    
    valid_statuses = ["Draft", "To Deliver and Bill", "To Bill", "To Deliver", "Completed", "Cancelled"]
    if new_status not in valid_statuses:
        frappe.throw(_("Invalid status: {0}").format(new_status))
    
    # Check existence
    if not frappe.db.exists("Sales Order", order_name):
        frappe.throw(
            _("Sales Order {0} not found").format(order_name),
            exc=frappe.DoesNotExistError
        )
    
    # Get document
    doc = frappe.get_doc("Sales Order", order_name)
    
    # Check base write permission
    if not doc.has_permission("write"):
        frappe.throw(
            _("You don't have permission to modify this order"),
            exc=frappe.PermissionError
        )
    
    # Status-specific permission checks
    if new_status == "Cancelled":
        if "Sales Manager" not in frappe.get_roles():
            frappe.throw(
                _("Only Sales Managers can cancel orders"),
                exc=frappe.PermissionError
            )
    
    # Business rule checks
    if doc.docstatus == 1 and new_status not in ["Completed", "Cancelled"]:
        frappe.throw(_("Submitted orders can only be marked as Completed or Cancelled"))
    
    # Update status
    old_status = doc.status
    doc.status = new_status
    doc.save()
    
    # Log the change
    frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Info",
        "reference_doctype": "Sales Order",
        "reference_name": order_name,
        "content": f"Status changed from {old_status} to {new_status} by {frappe.session.user}"
    }).insert(ignore_permissions=True)
    
    return {
        "status": "success",
        "message": _("Status updated to {0}").format(new_status)
    }


@frappe.whitelist()
def delete_draft_orders(order_names):
    """
    Bulk delete draft orders with per-document permission check.
    """
    if not order_names:
        frappe.throw(_("No orders specified"))
    
    if isinstance(order_names, str):
        order_names = frappe.parse_json(order_names)
    
    results = {
        "deleted": [],
        "not_found": [],
        "permission_denied": [],
        "not_draft": [],
        "errors": []
    }
    
    for name in order_names:
        # Check existence
        if not frappe.db.exists("Sales Order", name):
            results["not_found"].append(name)
            continue
        
        # Check delete permission
        if not frappe.has_permission("Sales Order", "delete", name):
            results["permission_denied"].append(name)
            continue
        
        # Check if draft
        docstatus = frappe.db.get_value("Sales Order", name, "docstatus")
        if docstatus != 0:
            results["not_draft"].append(name)
            continue
        
        # Delete
        try:
            frappe.delete_doc("Sales Order", name)
            results["deleted"].append(name)
        except Exception as e:
            results["errors"].append({"name": name, "error": str(e)})
    
    frappe.db.commit()
    
    # Summary message
    messages = []
    if results["deleted"]:
        messages.append(_("{0} orders deleted").format(len(results["deleted"])))
    if results["permission_denied"]:
        messages.append(_("{0} orders: permission denied").format(len(results["permission_denied"])))
    if results["not_draft"]:
        messages.append(_("{0} orders: not in draft status").format(len(results["not_draft"])))
    if results["not_found"]:
        messages.append(_("{0} orders: not found").format(len(results["not_found"])))
    
    return {
        "results": results,
        "message": ". ".join(messages)
    }


@frappe.whitelist()
def export_orders(filters=None):
    """
    Export orders with permission-based filtering.
    """
    # Check export permission
    if not frappe.has_permission("Sales Order", "export"):
        frappe.throw(
            _("You don't have permission to export Sales Orders"),
            exc=frappe.PermissionError
        )
    
    # Parse filters
    if filters and isinstance(filters, str):
        filters = frappe.parse_json(filters)
    
    # Use get_list to respect permissions
    orders = frappe.get_list(
        "Sales Order",
        filters=filters,
        fields=["name", "customer", "transaction_date", "grand_total", "status"],
        order_by="transaction_date desc",
        limit=1000
    )
    
    # Log export
    frappe.get_doc({
        "doctype": "Export Log",
        "doctype_name": "Sales Order",
        "user": frappe.session.user,
        "filters": frappe.as_json(filters),
        "record_count": len(orders),
        "timestamp": frappe.utils.now()
    }).insert(ignore_permissions=True)
    
    return orders
```

---

## Example 3: Client-Side Permission Handling

```javascript
// myapp/public/js/sales_order.js

frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        // Add buttons based on permissions
        add_permission_based_buttons(frm);
        
        // Show/hide fields based on permissions
        toggle_sensitive_fields(frm);
    },
    
    before_save: function(frm) {
        // Validate before save
        return validate_permission_for_changes(frm);
    }
});

function add_permission_based_buttons(frm) {
    // Only show for saved documents
    if (frm.is_new()) return;
    
    // Approve button - for managers only
    if (frm.doc.status === "Pending Approval") {
        if (frappe.user.has_role("Sales Manager")) {
            frm.add_custom_button(__("Approve"), function() {
                approve_order(frm);
            }, __("Actions"));
        }
    }
    
    // Cancel button - check permission
    if (frm.doc.docstatus === 1) {
        frappe.call({
            method: "frappe.client.has_permission",
            args: {
                doctype: "Sales Order",
                docname: frm.doc.name,
                ptype: "cancel"
            },
            async: false,
            callback: function(r) {
                if (r.message) {
                    frm.add_custom_button(__("Cancel Order"), function() {
                        cancel_order(frm);
                    }, __("Actions"));
                }
            }
        });
    }
    
    // Delete button - only for drafts with delete permission
    if (frm.doc.docstatus === 0 && !frm.is_new()) {
        if (frappe.perm.has_perm("Sales Order", 0, "delete")) {
            frm.add_custom_button(__("Delete"), function() {
                delete_order(frm);
            }, __("Actions"));
        }
    }
}

function toggle_sensitive_fields(frm) {
    // Hide margin fields for non-managers
    const manager_roles = ["Sales Manager", "System Manager"];
    const is_manager = manager_roles.some(role => frappe.user.has_role(role));
    
    frm.toggle_display("margin", is_manager);
    frm.toggle_display("margin_percent", is_manager);
    frm.toggle_display("cost_center", is_manager);
}

function validate_permission_for_changes(frm) {
    return new Promise((resolve, reject) => {
        // Check if user changed sensitive fields
        const sensitive_fields = ["discount_percentage", "additional_discount_percentage"];
        let changed_sensitive = false;
        
        for (let field of sensitive_fields) {
            if (frm.doc[field] !== (frm.doc.__original && frm.doc.__original[field])) {
                changed_sensitive = true;
                break;
            }
        }
        
        if (changed_sensitive && !frappe.user.has_role("Sales Manager")) {
            frappe.msgprint({
                title: __("Permission Required"),
                message: __("You don't have permission to modify discount fields."),
                indicator: "red"
            });
            reject();
        } else {
            resolve();
        }
    });
}

function approve_order(frm) {
    frappe.call({
        method: "myapp.api.approve_order",
        args: { order_name: frm.doc.name },
        freeze: true,
        freeze_message: __("Approving..."),
        callback: function(r) {
            if (r.message && r.message.status === "success") {
                frappe.show_alert({
                    message: __("Order approved"),
                    indicator: "green"
                });
                frm.reload_doc();
            }
        },
        error: function(r) {
            if (r.exc_type === "PermissionError") {
                frappe.msgprint({
                    title: __("Permission Denied"),
                    message: __("You don't have permission to approve this order."),
                    indicator: "red"
                });
            }
        }
    });
}

function cancel_order(frm) {
    frappe.confirm(
        __("Are you sure you want to cancel this order?"),
        function() {
            frappe.call({
                method: "frappe.client.cancel",
                args: {
                    doctype: "Sales Order",
                    name: frm.doc.name
                },
                callback: function(r) {
                    frm.reload_doc();
                },
                error: function(r) {
                    if (r.exc_type === "PermissionError") {
                        frappe.msgprint({
                            title: __("Permission Denied"),
                            message: __("You don't have permission to cancel this order."),
                            indicator: "red"
                        });
                    }
                }
            });
        }
    );
}

function delete_order(frm) {
    frappe.confirm(
        __("Are you sure you want to delete this order? This cannot be undone."),
        function() {
            frappe.call({
                method: "frappe.client.delete",
                args: {
                    doctype: "Sales Order",
                    name: frm.doc.name
                },
                callback: function(r) {
                    frappe.set_route("List", "Sales Order");
                    frappe.show_alert({
                        message: __("Order deleted"),
                        indicator: "green"
                    });
                },
                error: function(r) {
                    if (r.exc_type === "PermissionError") {
                        frappe.msgprint({
                            title: __("Permission Denied"),
                            message: __("You don't have permission to delete this order."),
                            indicator: "red"
                        });
                    }
                }
            });
        }
    );
}
```

---

## Quick Reference: Permission Error Responses

```python
# 403 Forbidden - Standard permission denied
frappe.throw(_("Access denied"), exc=frappe.PermissionError)

# 403 with context
frappe.throw(
    _("You need {0} role to perform this action").format("Sales Manager"),
    exc=frappe.PermissionError
)

# Check and throw in one line
frappe.has_permission("Sales Order", "write", doc_name, throw=True)

# Role check that throws
frappe.only_for(["Manager", "Administrator"])

# Document-level check
doc.check_permission("write")  # Throws PermissionError if denied
```
