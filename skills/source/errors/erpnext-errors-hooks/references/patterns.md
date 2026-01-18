# Error Handling Patterns - Hooks

Complete error handling patterns for Frappe/ERPNext hooks.py configurations.

---

## Pattern 1: doc_events Multi-Operation Handler

```python
# myapp/events/sales_invoice.py
import frappe
from frappe import _

def on_submit(doc, method=None):
    """
    Post-submit handler with isolated operations.
    Document is already submitted - errors won't roll back.
    """
    errors = []
    
    # Operation 1: Update linked quotation (critical)
    try:
        if doc.quotation:
            update_quotation_status(doc.quotation)
    except Exception as e:
        errors.append(f"Quotation update: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Quotation Update Error")
    
    # Operation 2: Create payment schedule (critical)
    try:
        create_payment_schedule(doc)
    except Exception as e:
        errors.append(f"Payment schedule: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Payment Schedule Error")
    
    # Operation 3: Send notification (non-critical)
    try:
        send_invoice_notification(doc)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Invoice notification failed: {doc.name}"
        )
        # Don't add to errors - non-critical
    
    # Operation 4: Sync to external system (non-critical)
    try:
        sync_to_accounting_system(doc)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"External sync failed: {doc.name}"
        )
        # Queue for retry
        frappe.enqueue(
            "myapp.tasks.retry_sync",
            doctype="Sales Invoice",
            name=doc.name,
            queue="short"
        )
    
    # Report critical errors
    if errors:
        frappe.msgprint(
            _("Invoice submitted with errors:<br>{0}").format("<br>".join(errors)),
            title=_("Warning"),
            indicator="orange"
        )


def update_quotation_status(quotation_name):
    """Update quotation to ordered."""
    if frappe.db.exists("Quotation", quotation_name):
        frappe.db.set_value("Quotation", quotation_name, "status", "Ordered")


def create_payment_schedule(doc):
    """Create payment schedule entries."""
    # Implementation
    pass


def send_invoice_notification(doc):
    """Send invoice email notification."""
    # Implementation
    pass


def sync_to_accounting_system(doc):
    """Sync to external accounting system."""
    # Implementation
    pass
```

---

## Pattern 2: Scheduler Task with Full Error Tracking

```python
# myapp/tasks.py
import frappe
from frappe.utils import now_datetime

def sync_inventory():
    """
    Scheduled inventory sync with comprehensive error handling.
    
    hooks.py:
    scheduler_events = {
        "daily_long": ["myapp.tasks.sync_inventory"]
    }
    """
    # Initialize tracking
    job_log = {
        "started": now_datetime(),
        "items_processed": 0,
        "items_failed": 0,
        "errors": [],
        "status": "Running"
    }
    
    try:
        # Get items to sync (ALWAYS limit!)
        items = frappe.get_all(
            "Item",
            filters={"sync_enabled": 1},
            fields=["name", "item_code", "warehouse"],
            limit=1000
        )
        
        if not items:
            job_log["status"] = "Completed"
            job_log["message"] = "No items to sync"
            save_job_log(job_log)
            frappe.db.commit()
            return
        
        # Process each item
        for item in items:
            try:
                sync_item(item)
                job_log["items_processed"] += 1
                
            except frappe.ValidationError as e:
                # Expected validation errors
                job_log["items_failed"] += 1
                job_log["errors"].append({
                    "item": item.name,
                    "error": str(e),
                    "type": "validation"
                })
                
            except Exception as e:
                # Unexpected errors
                job_log["items_failed"] += 1
                job_log["errors"].append({
                    "item": item.name,
                    "error": str(e)[:200],
                    "type": "unexpected"
                })
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Inventory sync error: {item.name}"
                )
            
            # Commit every 100 items
            if (job_log["items_processed"] + job_log["items_failed"]) % 100 == 0:
                frappe.db.commit()
        
        # Final status
        if job_log["items_failed"] == 0:
            job_log["status"] = "Completed"
        else:
            job_log["status"] = "Completed with Errors"
        
    except Exception as e:
        job_log["status"] = "Failed"
        job_log["fatal_error"] = str(e)
        frappe.log_error(frappe.get_traceback(), "Inventory Sync Fatal Error")
    
    finally:
        job_log["completed"] = now_datetime()
        save_job_log(job_log)
        frappe.db.commit()


def sync_item(item):
    """Sync single item - raises exceptions on failure."""
    # Implementation
    pass


def save_job_log(job_log):
    """Save job execution log."""
    # Truncate errors for storage
    if len(job_log.get("errors", [])) > 100:
        job_log["errors"] = job_log["errors"][:100]
        job_log["errors_truncated"] = True
    
    frappe.get_doc({
        "doctype": "Scheduled Job Log",
        "job_name": "sync_inventory",
        "status": job_log["status"],
        "started": job_log["started"],
        "completed": job_log.get("completed"),
        "details": frappe.as_json(job_log)
    }).insert(ignore_permissions=True)
```

---

## Pattern 3: Permission Query with Safe Fallback

```python
# myapp/permissions.py
import frappe

def sales_invoice_query_conditions(user):
    """
    Permission query for Sales Invoice list view.
    
    CRITICAL: Never throw errors - return safe fallback.
    
    hooks.py:
    permission_query_conditions = {
        "Sales Invoice": "myapp.permissions.sales_invoice_query_conditions"
    }
    """
    try:
        if not user:
            user = frappe.session.user
        
        # System Manager sees all
        user_roles = frappe.get_roles(user)
        if "System Manager" in user_roles:
            return ""
        
        # Accounts Manager sees all active invoices
        if "Accounts Manager" in user_roles:
            return "`tabSales Invoice`.docstatus < 2"
        
        # Sales Manager sees team's invoices
        if "Sales Manager" in user_roles:
            team = get_user_team(user)
            if team:
                team_users = get_team_members(team)
                if team_users:
                    users_str = ", ".join([frappe.db.escape(u) for u in team_users])
                    return f"`tabSales Invoice`.owner IN ({users_str})"
        
        # Default: own invoices only
        return f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Permission query error for user {user}"
        )
        # SAFE FALLBACK: Restrict to own records
        return f"`tabSales Invoice`.owner = {frappe.db.escape(frappe.session.user)}"


def get_user_team(user):
    """Get user's team - returns None on error."""
    try:
        return frappe.db.get_value("User", user, "department")
    except Exception:
        return None


def get_team_members(team):
    """Get team member list - returns empty list on error."""
    try:
        return frappe.get_all(
            "User",
            filters={"department": team, "enabled": 1},
            pluck="name"
        )
    except Exception:
        return []
```

---

## Pattern 4: has_permission with Graceful Degradation

```python
# myapp/permissions.py
import frappe

def project_has_permission(doc, user=None, permission_type=None):
    """
    Document-level permission for Project.
    
    CRITICAL: Never throw - return False to deny, None to defer.
    
    hooks.py:
    has_permission = {
        "Project": "myapp.permissions.project_has_permission"
    }
    """
    try:
        user = user or frappe.session.user
        
        # System Manager always has access
        if "System Manager" in frappe.get_roles(user):
            return None  # Defer to default (allow)
        
        # Check document status
        status = doc.status if hasattr(doc, 'status') else None
        
        # Archived projects: read-only
        if status == "Archived":
            if permission_type in ["write", "delete", "submit", "cancel"]:
                return False
            return None  # Allow read
        
        # Confidential projects: only assigned users
        if doc.get("is_confidential"):
            assigned_users = get_project_members(doc.name)
            if user not in assigned_users:
                return False
        
        # Write permission: check project manager
        if permission_type == "write":
            if doc.get("project_manager"):
                manager_user = frappe.db.get_value(
                    "Employee", doc.project_manager, "user_id"
                )
                if user == manager_user:
                    return None  # Allow
        
        # Defer to default permission system
        return None
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Project permission error: {doc.name if hasattr(doc, 'name') else 'unknown'}"
        )
        # SAFE: Defer to default permission system
        return None


def get_project_members(project_name):
    """Get project team members - returns empty list on error."""
    try:
        return frappe.get_all(
            "Project User",
            filters={"parent": project_name},
            pluck="user"
        ) or []
    except Exception:
        return []
```

---

## Pattern 5: Override Class with Parent Error Handling

```python
# myapp/overrides/sales_invoice.py
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
import frappe
from frappe import _

class CustomSalesInvoice(SalesInvoice):
    """
    Custom Sales Invoice with proper parent error handling.
    
    hooks.py:
    override_doctype_class = {
        "Sales Invoice": "myapp.overrides.sales_invoice.CustomSalesInvoice"
    }
    """
    
    def validate(self):
        """Override validate with parent error handling."""
        # Call parent - let validation errors propagate
        try:
            super().validate()
        except frappe.ValidationError:
            # Re-raise validation errors unchanged
            raise
        except Exception as e:
            # Log unexpected parent errors
            frappe.log_error(
                frappe.get_traceback(),
                f"Parent validate error: {self.name}"
            )
            # Re-raise with context
            frappe.throw(
                _("Validation error: {0}").format(str(e)),
                title=_("System Error")
            )
        
        # Custom validation
        self.validate_credit_terms()
        self.validate_custom_fields()
    
    def validate_credit_terms(self):
        """Validate credit terms with error collection."""
        if not self.payment_terms_template:
            return
        
        errors = []
        
        # Check credit limit
        if self.customer:
            credit_data = self.get_customer_credit_data()
            if credit_data:
                if credit_data.get("is_frozen"):
                    errors.append(_("Customer account is frozen"))
                
                credit_limit = credit_data.get("credit_limit", 0)
                if credit_limit and self.grand_total > credit_limit:
                    errors.append(
                        _("Amount {0} exceeds credit limit {1}").format(
                            self.grand_total, credit_limit
                        )
                    )
        
        if errors:
            frappe.throw("<br>".join(errors), title=_("Credit Check Failed"))
    
    def validate_custom_fields(self):
        """Validate custom fields."""
        if self.custom_requires_po and not self.po_no:
            frappe.throw(_("PO Number is required for this customer"))
    
    def get_customer_credit_data(self):
        """Get customer credit data with error handling."""
        try:
            return frappe.db.get_value(
                "Customer",
                self.customer,
                ["credit_limit", "is_frozen"],
                as_dict=True
            )
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Customer credit lookup error: {self.customer}"
            )
            return None
    
    def on_submit(self):
        """Override on_submit with isolated operations."""
        # Call parent first
        try:
            super().on_submit()
        except Exception:
            # Parent on_submit errors are critical
            raise
        
        # Custom post-submit (non-critical)
        try:
            self.create_custom_entries()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Custom entries failed: {self.name}"
            )
            frappe.msgprint(
                _("Invoice submitted. Custom entries will be created later."),
                indicator="orange"
            )
    
    def create_custom_entries(self):
        """Create custom accounting entries."""
        # Implementation
        pass
```

---

## Pattern 6: extend_bootinfo with Safe Loading

```python
# myapp/boot.py
import frappe

def extend_boot(bootinfo):
    """
    Extend boot info with error-safe data loading.
    
    CRITICAL: Errors here break the entire desk!
    
    hooks.py:
    extend_bootinfo = "myapp.boot.extend_boot"
    """
    # Initialize with defaults
    bootinfo.myapp_config = {}
    bootinfo.myapp_permissions = {}
    
    # Load app settings
    try:
        if frappe.db.exists("My App Settings", "My App Settings"):
            settings = frappe.get_single("My App Settings")
            bootinfo.myapp_config = {
                "feature_enabled": settings.feature_enabled or False,
                "default_view": settings.default_view or "list",
                "max_items": settings.max_items or 100
            }
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Bootinfo: Failed to load app settings"
        )
        # Keep defaults
    
    # Load user-specific data
    try:
        user = frappe.session.user
        if user and user != "Guest":
            bootinfo.myapp_permissions = {
                "can_approve": has_approval_permission(user),
                "can_export": has_export_permission(user),
                "dashboard_access": get_dashboard_access(user)
            }
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Bootinfo: Failed to load user permissions"
        )
        # Keep defaults
    
    # Load cached data
    try:
        cached_data = frappe.cache().get_value("myapp_global_cache")
        if cached_data:
            bootinfo.myapp_cache = cached_data
    except Exception:
        # Cache errors are non-critical
        pass


def has_approval_permission(user):
    """Check approval permission - returns False on error."""
    try:
        return "Approver" in frappe.get_roles(user)
    except Exception:
        return False


def has_export_permission(user):
    """Check export permission - returns False on error."""
    try:
        return frappe.has_permission("Sales Invoice", "export", user=user)
    except Exception:
        return False


def get_dashboard_access(user):
    """Get dashboard access list - returns empty list on error."""
    try:
        return frappe.get_all(
            "Dashboard Access",
            filters={"user": user, "enabled": 1},
            pluck="dashboard"
        ) or []
    except Exception:
        return []
```

---

## Pattern 7: Wildcard doc_events Handler

```python
# myapp/events/audit.py
import frappe

def log_all_changes(doc, method=None):
    """
    Audit log for all document changes.
    
    hooks.py:
    doc_events = {
        "*": {
            "on_update": "myapp.events.audit.log_all_changes",
            "on_trash": "myapp.events.audit.log_all_changes"
        }
    }
    """
    # Skip certain doctypes
    skip_doctypes = [
        "Audit Log", "Error Log", "Activity Log",
        "Communication", "Email Queue", "Version"
    ]
    
    if doc.doctype in skip_doctypes:
        return
    
    # Wrap entire operation - NEVER break other apps' saves
    try:
        log_entry = {
            "doctype": "Audit Log",
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "action": method,
            "user": frappe.session.user,
            "timestamp": frappe.utils.now()
        }
        
        # Get changed fields (on_update only)
        if method == "on_update":
            try:
                old_doc = doc.get_doc_before_save()
                if old_doc:
                    log_entry["changes"] = get_changes(old_doc, doc)
            except Exception:
                pass  # Ignore change detection errors
        
        # Insert log
        frappe.get_doc(log_entry).insert(ignore_permissions=True)
        
    except Exception:
        # NEVER let audit logging break the actual save
        frappe.log_error(
            frappe.get_traceback(),
            f"Audit log error: {doc.doctype}/{doc.name}"
        )


def get_changes(old_doc, new_doc):
    """Compare documents and return changes dict."""
    changes = {}
    for field in new_doc.meta.get_valid_columns():
        old_val = old_doc.get(field)
        new_val = new_doc.get(field)
        if old_val != new_val:
            changes[field] = {"old": old_val, "new": new_val}
    return frappe.as_json(changes) if changes else None
```

---

## Quick Reference: Hook Error Handling

| Hook | Error Strategy | Fallback |
|------|---------------|----------|
| doc_events (validate) | Collect, throw once | N/A |
| doc_events (on_update) | Isolate, log non-critical | Continue |
| scheduler_events | Try/except all, log everything | Commit partial |
| permission_query_conditions | Never throw | Return user filter |
| has_permission | Never throw | Return None |
| extend_bootinfo | Never throw | Return defaults |
| override class | super() in try/except | Re-raise |
| wildcard (*) events | Never break saves | Log and continue |
