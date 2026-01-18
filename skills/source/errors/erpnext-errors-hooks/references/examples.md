# Examples - Hooks Error Handling

Complete working examples of error handling in Frappe/ERPNext hooks.py configurations.

---

## Example 1: Complete hooks.py with Error-Safe Handlers

```python
# myapp/hooks.py

app_name = "myapp"
app_title = "My App"
app_publisher = "My Company"

# Document Events
doc_events = {
    # Wildcard for audit (NEVER breaks saves)
    "*": {
        "on_update": "myapp.events.audit.log_change",
        "on_trash": "myapp.events.audit.log_delete"
    },
    # Specific DocType handlers
    "Sales Invoice": {
        "validate": "myapp.events.sales_invoice.validate",
        "on_submit": "myapp.events.sales_invoice.on_submit",
        "on_cancel": "myapp.events.sales_invoice.on_cancel"
    },
    "Sales Order": {
        "validate": "myapp.events.sales_order.validate",
        "on_update": "myapp.events.sales_order.on_update"
    }
}

# Scheduler Events
scheduler_events = {
    "daily": [
        "myapp.tasks.daily_cleanup"
    ],
    "daily_long": [
        "myapp.tasks.sync_inventory"
    ],
    "cron": {
        "0 9 * * 1-5": ["myapp.tasks.weekday_morning_report"]
    }
}

# Permission Hooks
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_query_conditions",
    "Project": "myapp.permissions.project_query_conditions"
}

has_permission = {
    "Sales Invoice": "myapp.permissions.si_has_permission",
    "Project": "myapp.permissions.project_has_permission"
}

# Boot Extension
extend_bootinfo = "myapp.boot.extend_boot"

# Override
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice"
}
```

---

## Example 2: Sales Invoice Event Handlers

```python
# myapp/events/sales_invoice.py
import frappe
from frappe import _

def validate(doc, method=None):
    """
    Validate handler - errors prevent save.
    Runs AFTER controller validate.
    """
    errors = []
    warnings = []
    
    # Custom field validation
    if doc.custom_requires_approval:
        if not doc.custom_approver:
            errors.append(_("Approver is required when approval is enabled"))
        elif not frappe.db.exists("User", doc.custom_approver):
            errors.append(_("Approver '{0}' not found").format(doc.custom_approver))
    
    # Cross-field validation
    if doc.custom_discount_reason and not doc.discount_amount:
        warnings.append(_("Discount reason provided but no discount applied"))
    
    # External validation (wrapped)
    try:
        validate_with_external_system(doc)
    except Exception as e:
        # Log but allow save
        frappe.log_error(
            frappe.get_traceback(),
            f"External validation error: {doc.name}"
        )
        warnings.append(_("External validation unavailable - please verify manually"))
    
    # Show warnings
    if warnings:
        frappe.msgprint(
            "<br>".join(warnings),
            title=_("Warnings"),
            indicator="orange"
        )
    
    # Throw errors
    if errors:
        frappe.throw("<br>".join(errors), title=_("Validation Error"))


def on_submit(doc, method=None):
    """
    Post-submit handler - document already submitted.
    Errors show message but don't roll back.
    """
    # Critical: Create accounting entries
    try:
        create_custom_gl_entries(doc)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"GL Entry Error: {doc.name}")
        frappe.throw(
            _("Accounting entries failed: {0}. Please contact support.").format(str(e))
        )
    
    # Non-critical: Notifications
    try:
        send_submit_notification(doc)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Submit notification failed: {doc.name}"
        )
    
    # Non-critical: External sync (queue for reliability)
    frappe.enqueue(
        "myapp.tasks.sync_invoice",
        invoice=doc.name,
        queue="short",
        job_id=f"sync_invoice_{doc.name}"
    )


def on_cancel(doc, method=None):
    """
    Cancel handler - reverse operations.
    Try to complete all cleanup even if some fail.
    """
    cleanup_errors = []
    
    # Reverse GL entries
    try:
        reverse_custom_gl_entries(doc)
    except Exception as e:
        cleanup_errors.append(f"GL reversal: {str(e)}")
        frappe.log_error(frappe.get_traceback(), f"GL Reversal Error: {doc.name}")
    
    # Cancel external sync
    try:
        cancel_external_sync(doc)
    except Exception as e:
        cleanup_errors.append(f"External sync: {str(e)}")
        frappe.log_error(frappe.get_traceback(), f"External Cancel Error: {doc.name}")
    
    # Send cancellation notice
    try:
        send_cancel_notification(doc)
    except Exception:
        # Non-critical - just log
        frappe.log_error(
            frappe.get_traceback(),
            f"Cancel notification failed: {doc.name}"
        )
    
    if cleanup_errors:
        frappe.msgprint(
            _("Invoice cancelled with cleanup errors:<br>{0}").format(
                "<br>".join(cleanup_errors)
            ),
            title=_("Warning"),
            indicator="orange"
        )


# Helper functions
def validate_with_external_system(doc):
    """Validate with external system."""
    pass

def create_custom_gl_entries(doc):
    """Create custom GL entries."""
    pass

def reverse_custom_gl_entries(doc):
    """Reverse custom GL entries."""
    pass

def send_submit_notification(doc):
    """Send submit notification."""
    pass

def send_cancel_notification(doc):
    """Send cancel notification."""
    pass

def cancel_external_sync(doc):
    """Cancel external system sync."""
    pass
```

---

## Example 3: Scheduler Task with Full Error Tracking

```python
# myapp/tasks.py
import frappe
from frappe.utils import now_datetime, add_days, today

def daily_cleanup():
    """
    Daily cleanup task with comprehensive error handling.
    
    hooks.py:
    scheduler_events = {
        "daily": ["myapp.tasks.daily_cleanup"]
    }
    """
    results = {
        "started": now_datetime(),
        "deleted_logs": 0,
        "deleted_temp_files": 0,
        "errors": []
    }
    
    # Task 1: Clean old error logs
    try:
        cutoff = add_days(today(), -30)
        count = frappe.db.count("Error Log", {"creation": ["<", cutoff]})
        
        if count > 0:
            frappe.db.delete("Error Log", {"creation": ["<", cutoff]})
            results["deleted_logs"] = count
        
        frappe.db.commit()
        
    except Exception as e:
        results["errors"].append(f"Error log cleanup: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Cleanup: Error Log")
        frappe.db.rollback()
    
    # Task 2: Clean temp files
    try:
        temp_files = frappe.get_all(
            "File",
            filters={
                "is_private": 1,
                "attached_to_doctype": "",
                "creation": ["<", add_days(today(), -7)]
            },
            limit=500
        )
        
        for f in temp_files:
            try:
                frappe.delete_doc("File", f.name, ignore_permissions=True)
                results["deleted_temp_files"] += 1
            except Exception:
                # Log individual file errors but continue
                pass
        
        frappe.db.commit()
        
    except Exception as e:
        results["errors"].append(f"Temp file cleanup: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Cleanup: Temp Files")
    
    # Task 3: Archive old records
    try:
        archive_old_records()
        frappe.db.commit()
    except Exception as e:
        results["errors"].append(f"Archive: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Cleanup: Archive")
    
    # Log summary
    results["completed"] = now_datetime()
    
    if results["errors"]:
        frappe.log_error(
            frappe.as_json(results),
            "Daily Cleanup - Completed with Errors"
        )
    else:
        # Optional: Log success for monitoring
        frappe.logger("cleanup").info(
            f"Daily cleanup completed: {results['deleted_logs']} logs, "
            f"{results['deleted_temp_files']} temp files"
        )


def weekday_morning_report():
    """
    Send morning report on weekdays.
    
    hooks.py:
    scheduler_events = {
        "cron": {
            "0 9 * * 1-5": ["myapp.tasks.weekday_morning_report"]
        }
    }
    """
    try:
        # Get report data
        report_data = compile_morning_report()
        
        # Get recipients
        recipients = get_report_recipients()
        
        if not recipients:
            frappe.log_error(
                "No recipients configured for morning report",
                "Morning Report - No Recipients"
            )
            return
        
        # Send report
        for recipient in recipients:
            try:
                send_report_email(recipient, report_data)
            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Morning Report - Failed for {recipient}"
                )
        
        frappe.db.commit()
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Morning Report - Fatal Error"
        )


def archive_old_records():
    """Archive old records."""
    pass

def compile_morning_report():
    """Compile morning report data."""
    return {}

def get_report_recipients():
    """Get list of report recipients."""
    return []

def send_report_email(recipient, data):
    """Send report email."""
    pass
```

---

## Example 4: Permission Hooks (Full Implementation)

```python
# myapp/permissions.py
import frappe

def si_query_conditions(user):
    """
    Sales Invoice list filter conditions.
    
    CRITICAL: Never throw - return safe filter.
    """
    try:
        if not user:
            user = frappe.session.user
        
        roles = frappe.get_roles(user)
        
        # Admins see all
        if "System Manager" in roles or "Accounts Manager" in roles:
            return ""
        
        # Sales Manager sees team
        if "Sales Manager" in roles:
            return get_team_condition(user, "Sales Invoice")
        
        # Default: own records
        return f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "SI Query Conditions Error")
        return f"`tabSales Invoice`.owner = {frappe.db.escape(frappe.session.user)}"


def si_has_permission(doc, user=None, permission_type=None):
    """
    Sales Invoice document-level permission.
    
    CRITICAL: Never throw - return False or None.
    """
    try:
        user = user or frappe.session.user
        roles = frappe.get_roles(user)
        
        # Admins have full access
        if "System Manager" in roles:
            return None
        
        # No write/delete on submitted invoices (except cancel)
        if doc.docstatus == 1:
            if permission_type in ["write", "delete"]:
                return False
        
        # Cancelled invoices are read-only
        if doc.docstatus == 2:
            if permission_type != "read":
                return False
        
        # Large invoice special handling
        if doc.grand_total and doc.grand_total > 100000:
            if permission_type == "submit" and "Invoice Approver" not in roles:
                return False
        
        return None  # Defer to default
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"SI Has Permission Error: {doc.name if hasattr(doc, 'name') else 'unknown'}"
        )
        return None


def project_query_conditions(user):
    """Project list filter conditions."""
    try:
        if not user:
            user = frappe.session.user
        
        roles = frappe.get_roles(user)
        
        if "System Manager" in roles or "Projects Manager" in roles:
            return ""
        
        # Users see their assigned projects
        return f"""
            EXISTS (
                SELECT 1 FROM `tabProject User`
                WHERE `tabProject User`.parent = `tabProject`.name
                AND `tabProject User`.user = {frappe.db.escape(user)}
            )
            OR `tabProject`.owner = {frappe.db.escape(user)}
        """
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Project Query Conditions Error")
        return f"`tabProject`.owner = {frappe.db.escape(frappe.session.user)}"


def project_has_permission(doc, user=None, permission_type=None):
    """Project document-level permission."""
    try:
        user = user or frappe.session.user
        roles = frappe.get_roles(user)
        
        if "System Manager" in roles:
            return None
        
        # Completed projects are read-only
        if doc.status == "Completed" and permission_type != "read":
            if "Projects Manager" not in roles:
                return False
        
        # Confidential projects
        if doc.get("is_confidential"):
            members = frappe.get_all(
                "Project User",
                filters={"parent": doc.name},
                pluck="user"
            ) or []
            
            if user not in members and doc.owner != user:
                return False
        
        return None
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Project Has Permission Error: {doc.name if hasattr(doc, 'name') else 'unknown'}"
        )
        return None


def get_team_condition(user, doctype):
    """Get team-based filter condition."""
    try:
        team = frappe.db.get_value("User", user, "department")
        if not team:
            return f"`tab{doctype}`.owner = {frappe.db.escape(user)}"
        
        team_users = frappe.get_all(
            "User",
            filters={"department": team, "enabled": 1},
            pluck="name"
        ) or [user]
        
        users_str = ", ".join([frappe.db.escape(u) for u in team_users])
        return f"`tab{doctype}`.owner IN ({users_str})"
        
    except Exception:
        return f"`tab{doctype}`.owner = {frappe.db.escape(user)}"
```

---

## Example 5: Boot Extension (Error-Safe)

```python
# myapp/boot.py
import frappe

def extend_boot(bootinfo):
    """
    Extend boot info - NEVER let errors break page load!
    """
    # Initialize all with safe defaults
    bootinfo.myapp = {
        "settings": {},
        "user_config": {},
        "notifications": [],
        "feature_flags": {}
    }
    
    # Load app settings
    try:
        settings = load_app_settings()
        bootinfo.myapp["settings"] = settings
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Bootinfo: Settings Load Error"
        )
    
    # Load user configuration
    try:
        user_config = load_user_config(frappe.session.user)
        bootinfo.myapp["user_config"] = user_config
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Bootinfo: User Config Error"
        )
    
    # Load pending notifications count
    try:
        bootinfo.myapp["notifications"] = get_notification_counts()
    except Exception:
        # Non-critical - fail silently
        pass
    
    # Load feature flags
    try:
        bootinfo.myapp["feature_flags"] = get_feature_flags()
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Bootinfo: Feature Flags Error"
        )


def load_app_settings():
    """Load app settings with defaults."""
    if not frappe.db.exists("My App Settings", "My App Settings"):
        return {
            "default_view": "list",
            "items_per_page": 20,
            "enable_notifications": True
        }
    
    settings = frappe.get_single("My App Settings")
    return {
        "default_view": settings.default_view or "list",
        "items_per_page": settings.items_per_page or 20,
        "enable_notifications": settings.enable_notifications
    }


def load_user_config(user):
    """Load user-specific configuration."""
    if user == "Guest":
        return {}
    
    config = frappe.db.get_value(
        "User",
        user,
        ["sidebar_collapsed", "default_landing_page"],
        as_dict=True
    ) or {}
    
    return {
        "sidebar_collapsed": config.get("sidebar_collapsed", False),
        "landing_page": config.get("default_landing_page", "/app")
    }


def get_notification_counts():
    """Get notification counts for current user."""
    return {
        "unread": frappe.db.count(
            "Notification Log",
            {"for_user": frappe.session.user, "read": 0}
        ),
        "total": frappe.db.count(
            "Notification Log",
            {"for_user": frappe.session.user}
        )
    }


def get_feature_flags():
    """Get feature flags."""
    return {
        "new_dashboard": True,
        "beta_features": False
    }
```

---

## Quick Reference: Hook Error Patterns

```python
# doc_events validate - collect and throw
def validate(doc, method=None):
    errors = []
    if not doc.field:
        errors.append(_("Field required"))
    if errors:
        frappe.throw("<br>".join(errors))

# doc_events on_update - isolate operations
def on_update(doc, method=None):
    try:
        non_critical_operation()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Error")

# scheduler - always try/except and commit
def scheduled_task():
    try:
        do_work()
        frappe.db.commit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Task Error")

# permission_query_conditions - never throw
def query_conditions(user):
    try:
        return build_condition(user)
    except Exception:
        return f"owner = {frappe.db.escape(frappe.session.user)}"

# has_permission - never throw
def has_permission(doc, user=None, permission_type=None):
    try:
        return check_permission(doc, user)
    except Exception:
        return None

# extend_bootinfo - never throw
def extend_boot(bootinfo):
    try:
        bootinfo.data = load_data()
    except Exception:
        bootinfo.data = {}
```
