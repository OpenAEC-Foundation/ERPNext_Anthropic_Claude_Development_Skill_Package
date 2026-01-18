# Examples - Server Script Error Handling

Complete working examples of error handling in Frappe/ERPNext Server Scripts.

---

## Example 1: Sales Order Validation (Document Event)

Full validation script with error collection and warnings.

```python
# Type: Document Event
# Event: Before Save
# DocType: Sales Order

# ============================================
# SALES ORDER VALIDATION
# ============================================

errors = []
warnings = []

# -------------------------------------------
# 1. Required Field Validation
# -------------------------------------------
if not doc.customer:
    errors.append("Customer is required")

if not doc.company:
    errors.append("Company is required")

if not doc.delivery_date:
    errors.append("Delivery Date is required")
elif doc.delivery_date < frappe.utils.today():
    warnings.append("Delivery Date is in the past")

# -------------------------------------------
# 2. Customer Validation
# -------------------------------------------
if doc.customer:
    customer = frappe.db.get_value(
        "Customer",
        doc.customer,
        ["disabled", "credit_limit", "default_price_list"],
        as_dict=True
    )
    
    if not customer:
        errors.append(f"Customer '{doc.customer}' does not exist")
    elif customer.disabled:
        errors.append(f"Customer '{doc.customer}' is disabled")
    else:
        # Auto-fill price list if not set
        if not doc.selling_price_list and customer.default_price_list:
            doc.selling_price_list = customer.default_price_list
        
        # Credit limit check (warning only)
        if customer.credit_limit and customer.credit_limit > 0:
            outstanding = frappe.db.get_value(
                "Sales Invoice",
                {"customer": doc.customer, "docstatus": 1, "outstanding_amount": [">", 0]},
                "sum(outstanding_amount)"
            ) or 0
            
            total_exposure = outstanding + (doc.grand_total or 0)
            if total_exposure > customer.credit_limit:
                warnings.append(
                    f"Credit limit warning: Limit {customer.credit_limit}, "
                    f"Outstanding {outstanding}, This order {doc.grand_total}, "
                    f"Total exposure {total_exposure}"
                )

# -------------------------------------------
# 3. Items Validation
# -------------------------------------------
if not doc.items:
    errors.append("Please add at least one item")
else:
    seen_items = set()
    
    for idx, item in enumerate(doc.items, 1):
        # Item code required
        if not item.item_code:
            errors.append(f"Row {idx}: Item Code is required")
            continue
        
        # Check for duplicate items (warning)
        item_key = (item.item_code, item.warehouse or "")
        if item_key in seen_items:
            warnings.append(f"Row {idx}: Duplicate item '{item.item_code}'")
        seen_items.add(item_key)
        
        # Validate item exists
        item_doc = frappe.db.get_value(
            "Item",
            item.item_code,
            ["disabled", "is_sales_item", "has_variants", "item_name"],
            as_dict=True
        )
        
        if not item_doc:
            errors.append(f"Row {idx}: Item '{item.item_code}' not found")
            continue
        
        if item_doc.disabled:
            errors.append(f"Row {idx}: Item '{item.item_code}' is disabled")
        
        if not item_doc.is_sales_item:
            errors.append(f"Row {idx}: Item '{item.item_code}' is not a Sales Item")
        
        if item_doc.has_variants:
            errors.append(f"Row {idx}: Cannot sell template item '{item.item_code}'. Select a variant.")
        
        # Quantity validation
        if (item.qty or 0) <= 0:
            errors.append(f"Row {idx}: Quantity must be greater than zero")
        
        # Rate validation
        if (item.rate or 0) < 0:
            errors.append(f"Row {idx}: Rate cannot be negative")
        elif (item.rate or 0) == 0:
            warnings.append(f"Row {idx}: Rate is zero for '{item.item_code}'")

# -------------------------------------------
# 4. Amount Validation
# -------------------------------------------
if doc.grand_total and doc.grand_total < 0:
    errors.append("Order total cannot be negative")

if doc.discount_percentage and (doc.discount_percentage < 0 or doc.discount_percentage > 100):
    errors.append("Discount percentage must be between 0 and 100")

# -------------------------------------------
# 5. Show Results
# -------------------------------------------
if warnings:
    frappe.msgprint(
        "<b>Warnings:</b><br>" + "<br>".join(f"• {w}" for w in warnings),
        title="Please Review",
        indicator="orange"
    )

if errors:
    frappe.throw(
        "<br>".join(f"• {e}" for e in errors),
        title="Cannot Save - Please Fix These Errors"
    )
```

---

## Example 2: REST API with Full Error Handling

Complete API script with parameter validation, permission checks, and error responses.

```python
# Type: API
# Method: create_support_ticket
# Allow Guest: No

# ============================================
# CREATE SUPPORT TICKET API
# ============================================
# Endpoint: POST /api/method/create_support_ticket
# Parameters:
#   - subject (required): Ticket subject
#   - description (required): Issue description
#   - priority (optional): Low/Medium/High/Critical
#   - customer (optional): Customer ID

# -------------------------------------------
# 1. Extract Parameters
# -------------------------------------------
subject = frappe.form_dict.get("subject")
description = frappe.form_dict.get("description")
priority = frappe.form_dict.get("priority", "Medium")
customer = frappe.form_dict.get("customer")

# -------------------------------------------
# 2. Validate Required Parameters
# -------------------------------------------
if not subject:
    frappe.throw(
        "Parameter 'subject' is required",
        exc=frappe.ValidationError
    )

if not subject.strip():
    frappe.throw(
        "Subject cannot be empty",
        exc=frappe.ValidationError
    )

if len(subject) > 200:
    frappe.throw(
        "Subject cannot exceed 200 characters",
        exc=frappe.ValidationError
    )

if not description:
    frappe.throw(
        "Parameter 'description' is required",
        exc=frappe.ValidationError
    )

# -------------------------------------------
# 3. Validate Optional Parameters
# -------------------------------------------
valid_priorities = ["Low", "Medium", "High", "Critical"]
if priority not in valid_priorities:
    frappe.throw(
        f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}",
        exc=frappe.ValidationError
    )

if customer:
    if not frappe.db.exists("Customer", customer):
        frappe.throw(
            f"Customer '{customer}' not found",
            exc=frappe.DoesNotExistError
        )
    
    if not frappe.has_permission("Customer", "read", customer):
        frappe.throw(
            "You don't have permission to access this customer",
            exc=frappe.PermissionError
        )

# -------------------------------------------
# 4. Check Permission to Create
# -------------------------------------------
if not frappe.has_permission("Issue", "create"):
    frappe.throw(
        "You don't have permission to create support tickets",
        exc=frappe.PermissionError
    )

# -------------------------------------------
# 5. Create the Ticket
# -------------------------------------------
issue = frappe.get_doc({
    "doctype": "Issue",
    "subject": subject.strip(),
    "description": description,
    "priority": priority,
    "customer": customer,
    "raised_by": frappe.session.user
})
issue.insert()

# -------------------------------------------
# 6. Success Response
# -------------------------------------------
frappe.response["message"] = {
    "success": True,
    "ticket_id": issue.name,
    "status": issue.status,
    "message": f"Support ticket {issue.name} created successfully"
}
```

---

## Example 3: Scheduler with Comprehensive Error Handling

Daily task with batch processing, error isolation, and summary logging.

```python
# Type: Scheduler Event
# Event Frequency: Cron
# Cron Format: 0 6 * * * (daily at 6:00 AM)

# ============================================
# DAILY INVOICE REMINDER SCHEDULER
# ============================================

from datetime import datetime

BATCH_SIZE = 25
MAX_ERRORS_BEFORE_ABORT = 50

# Statistics tracking
stats = {
    "start_time": frappe.utils.now(),
    "invoices_found": 0,
    "reminders_created": 0,
    "emails_sent": 0,
    "skipped": 0,
    "errors": []
}

# -------------------------------------------
# 1. Get Overdue Invoices
# -------------------------------------------
today = frappe.utils.today()

overdue_invoices = frappe.get_all(
    "Sales Invoice",
    filters={
        "docstatus": 1,
        "status": ["in", ["Unpaid", "Overdue"]],
        "outstanding_amount": [">", 0],
        "due_date": ["<", today]
    },
    fields=[
        "name", "customer", "customer_name", "owner",
        "due_date", "grand_total", "outstanding_amount"
    ],
    order_by="due_date asc",
    limit=500  # Safety limit
)

stats["invoices_found"] = len(overdue_invoices)

if not overdue_invoices:
    frappe.log_error(
        "No overdue invoices found",
        "Invoice Reminder - No Action"
    )
    frappe.db.commit()
    # Exit early
    return

# -------------------------------------------
# 2. Process in Batches
# -------------------------------------------
for batch_start in range(0, len(overdue_invoices), BATCH_SIZE):
    # Check error threshold
    if len(stats["errors"]) >= MAX_ERRORS_BEFORE_ABORT:
        stats["errors"].append("--- ABORTED: Too many errors ---")
        break
    
    batch = overdue_invoices[batch_start:batch_start + BATCH_SIZE]
    
    for inv in batch:
        result = process_single_invoice(inv, today)
        
        if result["action"] == "created":
            stats["reminders_created"] += 1
        elif result["action"] == "emailed":
            stats["reminders_created"] += 1
            stats["emails_sent"] += 1
        elif result["action"] == "skipped":
            stats["skipped"] += 1
        elif result["action"] == "error":
            stats["errors"].append(f"{inv.name}: {result['reason']}")
    
    # Commit after each batch
    frappe.db.commit()

# -------------------------------------------
# 3. Generate Summary Report
# -------------------------------------------
stats["end_time"] = frappe.utils.now()
duration = frappe.utils.time_diff_in_seconds(stats["end_time"], stats["start_time"])

summary = f"""
Invoice Reminder Summary - {today}
{'=' * 50}

Duration: {duration:.1f} seconds
Invoices Found: {stats["invoices_found"]}
Reminders Created: {stats["reminders_created"]}
Emails Sent: {stats["emails_sent"]}
Skipped: {stats["skipped"]}
Errors: {len(stats["errors"])}
"""

if stats["errors"]:
    summary += f"""
Error Details (first 20):
{'-' * 30}
"""
    for error in stats["errors"][:20]:
        summary += f"• {error}\n"
    
    if len(stats["errors"]) > 20:
        summary += f"\n... and {len(stats["errors"]) - 20} more errors"

# Log summary
log_title = "Invoice Reminder - " + (
    "Success" if not stats["errors"] else 
    "Completed with Errors" if stats["reminders_created"] > 0 else
    "Failed"
)
frappe.log_error(summary, log_title)

# Final commit
frappe.db.commit()


# -------------------------------------------
# Helper Function
# -------------------------------------------
def process_single_invoice(inv, today):
    """Process a single invoice, return result dict."""
    
    # Check if customer exists
    if not frappe.db.exists("Customer", inv.customer):
        return {"action": "error", "reason": "Customer not found"}
    
    # Check if already reminded in last 7 days
    recent_todo = frappe.db.exists(
        "ToDo",
        {
            "reference_type": "Sales Invoice",
            "reference_name": inv.name,
            "date": [">=", frappe.utils.add_days(today, -7)],
            "status": "Open"
        }
    )
    
    if recent_todo:
        return {"action": "skipped", "reason": "Recently reminded"}
    
    # Calculate days overdue
    days_overdue = frappe.utils.date_diff(today, inv.due_date)
    
    # Determine priority
    if days_overdue > 60:
        priority = "High"
        send_email = True
    elif days_overdue > 30:
        priority = "Medium"
        send_email = True
    else:
        priority = "Low"
        send_email = False
    
    # Create reminder ToDo
    todo = frappe.get_doc({
        "doctype": "ToDo",
        "allocated_to": inv.owner,
        "reference_type": "Sales Invoice",
        "reference_name": inv.name,
        "priority": priority,
        "date": today,
        "description": (
            f"Follow up on overdue invoice {inv.name}\n"
            f"Customer: {inv.customer_name}\n"
            f"Amount: {inv.outstanding_amount}\n"
            f"Days Overdue: {days_overdue}"
        )
    })
    todo.insert(ignore_permissions=True)
    
    # Send email for high priority
    if send_email:
        customer_email = frappe.db.get_value("Customer", inv.customer, "email_id")
        
        if customer_email:
            frappe.sendmail(
                recipients=[customer_email],
                subject=f"Payment Reminder - Invoice {inv.name}",
                message=f"Dear {inv.customer_name},\n\nThis is a reminder that invoice {inv.name} for {inv.outstanding_amount} is {days_overdue} days overdue.\n\nPlease arrange payment at your earliest convenience.",
                reference_doctype="Sales Invoice",
                reference_name=inv.name
            )
            return {"action": "emailed"}
    
    return {"action": "created"}
```

---

## Example 4: Permission Query with Safe Fallbacks

```python
# Type: Permission Query
# DocType: Project

# ============================================
# PROJECT PERMISSION QUERY
# ============================================
# Filter projects based on user role and department

# -------------------------------------------
# 1. Get User Information Safely
# -------------------------------------------
user_roles = frappe.get_roles(user) or []
user_dept = frappe.db.get_value("User", user, "department") or ""
user_territory = frappe.db.get_value("User", user, "territory") or ""

# -------------------------------------------
# 2. Build Conditions Based on Role
# -------------------------------------------

# System Manager / Admin - full access
if "System Manager" in user_roles or "Administrator" in user_roles:
    conditions = ""

# Project Admin - all projects
elif "Projects Admin" in user_roles:
    conditions = ""

# Department Manager - department projects
elif "Projects Manager" in user_roles:
    if user_dept:
        # See own department's projects
        conditions = f"`tabProject`.department = {frappe.db.escape(user_dept)}"
    else:
        # No department assigned - log warning, show own only
        frappe.log_error(
            f"User {user} has Projects Manager role but no department",
            "Permission Configuration Warning"
        )
        conditions = f"`tabProject`.owner = {frappe.db.escape(user)}"

# Project User - own projects + assigned
elif "Projects User" in user_roles:
    # Own projects OR projects where user is a member
    conditions = f"""
        (`tabProject`.owner = {frappe.db.escape(user)}
         OR `tabProject`.name IN (
             SELECT parent FROM `tabProject User` 
             WHERE user = {frappe.db.escape(user)}
         ))
    """

# Sales User - projects for their territory
elif "Sales User" in user_roles:
    if user_territory:
        conditions = f"`tabProject`.territory = {frappe.db.escape(user_territory)}"
    else:
        conditions = f"`tabProject`.owner = {frappe.db.escape(user)}"

# Guest / No relevant role - no access
else:
    conditions = "1=0"
```

---

## Example 5: Document Event with External Integration

```python
# Type: Document Event
# Event: After Submit
# DocType: Sales Order

# ============================================
# SYNC ORDER TO EXTERNAL SYSTEM
# ============================================
# After sales order is submitted, sync to warehouse system

# -------------------------------------------
# 1. Check if Sync is Enabled
# -------------------------------------------
sync_enabled = frappe.db.get_single_value("Selling Settings", "enable_warehouse_sync")

if not sync_enabled:
    return  # Silent exit

# -------------------------------------------
# 2. Validate Required Data
# -------------------------------------------
if not doc.items:
    frappe.log_error(
        f"Sales Order {doc.name} has no items to sync",
        "Warehouse Sync Warning"
    )
    return

warehouse = doc.set_warehouse
if not warehouse:
    frappe.log_error(
        f"Sales Order {doc.name} has no warehouse set",
        "Warehouse Sync Warning"
    )
    frappe.msgprint(
        "Order saved but could not sync to warehouse: No warehouse specified",
        indicator="orange"
    )
    return

# -------------------------------------------
# 3. Prepare Sync Data
# -------------------------------------------
sync_items = []
for item in doc.items:
    if not item.item_code:
        continue
    
    # Get item details
    item_data = frappe.db.get_value(
        "Item",
        item.item_code,
        ["item_name", "stock_uom", "weight_per_unit"],
        as_dict=True
    )
    
    if not item_data:
        frappe.log_error(
            f"Item {item.item_code} not found during sync for {doc.name}",
            "Warehouse Sync Error"
        )
        continue
    
    sync_items.append({
        "item_code": item.item_code,
        "item_name": item_data.item_name,
        "qty": item.qty,
        "uom": item_data.stock_uom,
        "warehouse": item.warehouse or warehouse
    })

if not sync_items:
    frappe.log_error(
        f"No valid items to sync for {doc.name}",
        "Warehouse Sync Warning"
    )
    return

# -------------------------------------------
# 4. Call External API (Simulated)
# -------------------------------------------
sync_payload = {
    "order_id": doc.name,
    "customer": doc.customer,
    "delivery_date": str(doc.delivery_date),
    "items": sync_items
}

# Note: In real scenario, you'd use frappe.call to a whitelisted method
# that makes the actual HTTP request (imports not allowed in sandbox)

# Record sync attempt
frappe.get_doc({
    "doctype": "Comment",
    "comment_type": "Info",
    "reference_doctype": "Sales Order",
    "reference_name": doc.name,
    "content": f"Queued for warehouse sync: {len(sync_items)} items"
}).insert(ignore_permissions=True)

frappe.msgprint(
    f"Order submitted. {len(sync_items)} items queued for warehouse sync.",
    indicator="green"
)
```

---

## Quick Reference: Server Script Error Handling

```python
# ============================================
# ERROR HANDLING CHEAT SHEET
# ============================================

# --- Validation Error (stops save) ---
frappe.throw("Customer is required")
frappe.throw("Error message", title="Custom Title")

# --- API Error with HTTP code ---
frappe.throw("Not found", exc=frappe.DoesNotExistError)  # 404
frappe.throw("Access denied", exc=frappe.PermissionError)  # 403
frappe.throw("Invalid input", exc=frappe.ValidationError)  # 417

# --- Warning (doesn't stop save) ---
frappe.msgprint("This is a warning", indicator="orange")
frappe.msgprint("Info message", alert=True)  # Shows as toast

# --- Log Error (for debugging) ---
frappe.log_error("Error details", "Error Title")
frappe.log_error(f"Failed for {doc.name}: {error}", "Processing Error")

# --- Safe Database Access ---
value = frappe.db.get_value("DocType", name, "field") or default
exists = frappe.db.exists("DocType", name)
data = frappe.db.get_value("DocType", name, ["f1", "f2"], as_dict=True) or {}

# --- Scheduler Pattern ---
# Always commit!
for item in items:
    process(item)
frappe.db.commit()

# --- Collect Multiple Errors ---
errors = []
if not field1: errors.append("Field 1 required")
if not field2: errors.append("Field 2 required")
if errors:
    frappe.throw("<br>".join(errors))
```
