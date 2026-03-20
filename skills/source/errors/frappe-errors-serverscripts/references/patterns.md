# Error Handling Patterns - Server Scripts

Complete error handling patterns for Frappe/ERPNext Server Scripts.

---

## Pattern 1: Comprehensive Document Validation

```python
# Type: Document Event
# Event: Before Save
# DocType: Sales Order

def validate_sales_order():
    """Collect and report all validation errors at once."""
    errors = []
    warnings = []
    
    # === Required Fields ===
    if not doc.customer:
        errors.append("Customer is required")
    
    if not doc.delivery_date:
        errors.append("Delivery Date is required")
    elif doc.delivery_date < frappe.utils.today():
        errors.append("Delivery Date cannot be in the past")
    
    # === Customer Validation ===
    if doc.customer:
        customer = frappe.db.get_value(
            "Customer", doc.customer,
            ["disabled", "credit_limit", "territory"],
            as_dict=True
        )
        
        if not customer:
            errors.append(f"Customer '{doc.customer}' not found")
        elif customer.disabled:
            errors.append(f"Customer '{doc.customer}' is disabled")
        else:
            # Credit check (warning, not error)
            if customer.credit_limit and doc.grand_total > customer.credit_limit:
                warnings.append(
                    f"Order total ({doc.grand_total}) exceeds credit limit ({customer.credit_limit})"
                )
    
    # === Items Validation ===
    if not doc.items:
        errors.append("At least one item is required")
    else:
        for idx, item in enumerate(doc.items, 1):
            row_errors = validate_item_row(item, idx)
            errors.extend(row_errors)
    
    # === Amount Validation ===
    if doc.grand_total <= 0 and doc.items:
        errors.append("Order total must be greater than zero")
    
    # === Show warnings (non-blocking) ===
    if warnings:
        frappe.msgprint(
            "<br>".join(warnings),
            title="Warnings",
            indicator="orange"
        )
    
    # === Throw errors (blocking) ===
    if errors:
        frappe.throw(
            "<br>".join(errors),
            title="Please correct the following errors"
        )


def validate_item_row(item, idx):
    """Validate single item row, return list of errors."""
    errors = []
    
    if not item.item_code:
        errors.append(f"Row {idx}: Item Code is required")
        return errors  # Can't validate further without item
    
    # Check item exists and is active
    item_data = frappe.db.get_value(
        "Item", item.item_code,
        ["disabled", "is_sales_item", "item_name"],
        as_dict=True
    )
    
    if not item_data:
        errors.append(f"Row {idx}: Item '{item.item_code}' not found")
    elif item_data.disabled:
        errors.append(f"Row {idx}: Item '{item.item_code}' is disabled")
    elif not item_data.is_sales_item:
        errors.append(f"Row {idx}: Item '{item.item_code}' is not a sales item")
    
    # Quantity validation
    if (item.qty or 0) <= 0:
        errors.append(f"Row {idx}: Quantity must be positive")
    
    # Rate validation
    if (item.rate or 0) < 0:
        errors.append(f"Row {idx}: Rate cannot be negative")
    
    return errors


# Execute validation
validate_sales_order()
```

---

## Pattern 2: Safe Database Operations

```python
# Type: Document Event
# Event: Before Save

# === Pattern: Check before get ===
if doc.reference_doctype and doc.reference_name:
    # Verify the referenced document exists
    if not frappe.db.exists(doc.reference_doctype, doc.reference_name):
        frappe.throw(
            f"Referenced document {doc.reference_doctype} '{doc.reference_name}' not found"
        )
    
    # Safe to fetch now
    ref_doc = frappe.get_doc(doc.reference_doctype, doc.reference_name)
    doc.reference_status = ref_doc.status


# === Pattern: Safe value lookup with default ===
credit_limit = frappe.db.get_value("Customer", doc.customer, "credit_limit") or 0
outstanding = frappe.db.get_value(
    "Sales Invoice",
    {"customer": doc.customer, "docstatus": 1, "status": "Unpaid"},
    "sum(outstanding_amount)"
) or 0


# === Pattern: Safe dict lookup ===
customer_data = frappe.db.get_value(
    "Customer", doc.customer,
    ["credit_limit", "territory", "customer_group"],
    as_dict=True
)

if customer_data:
    doc.territory = customer_data.get("territory") or "Unknown"
    doc.customer_group = customer_data.get("customer_group")
else:
    frappe.throw(f"Customer '{doc.customer}' not found")


# === Pattern: Safe list iteration ===
items = frappe.get_all(
    "Sales Order Item",
    filters={"parent": doc.name},
    fields=["item_code", "qty"]
) or []  # Ensure always a list

for item in items:
    process_item(item)
```

---

## Pattern 3: API Script with Full Error Handling

```python
# Type: API
# Method: process_customer_order
# Endpoint: /api/method/process_customer_order

# === Parameter Extraction ===
customer = frappe.form_dict.get("customer")
items = frappe.form_dict.get("items")  # Expected: list of dicts
delivery_date = frappe.form_dict.get("delivery_date")

# === Input Validation ===
if not customer:
    frappe.throw(
        "Parameter 'customer' is required",
        exc=frappe.ValidationError
    )

if not items:
    frappe.throw(
        "Parameter 'items' is required (list of items)",
        exc=frappe.ValidationError
    )

# Parse items if JSON string
if isinstance(items, str):
    items = frappe.parse_json(items)

if not isinstance(items, list):
    frappe.throw(
        "Parameter 'items' must be a list",
        exc=frappe.ValidationError
    )

# === Entity Validation ===
if not frappe.db.exists("Customer", customer):
    frappe.throw(
        f"Customer '{customer}' not found",
        exc=frappe.DoesNotExistError
    )

# === Permission Check ===
if not frappe.has_permission("Sales Order", "create"):
    frappe.throw(
        "You don't have permission to create Sales Orders",
        exc=frappe.PermissionError
    )

# === Business Logic with Validation ===
order_items = []
for idx, item in enumerate(items, 1):
    item_code = item.get("item_code")
    qty = item.get("qty")
    
    if not item_code:
        frappe.throw(
            f"Item {idx}: 'item_code' is required",
            exc=frappe.ValidationError
        )
    
    if not frappe.db.exists("Item", item_code):
        frappe.throw(
            f"Item '{item_code}' not found",
            exc=frappe.DoesNotExistError
        )
    
    if not qty or frappe.utils.flt(qty) <= 0:
        frappe.throw(
            f"Item {idx}: 'qty' must be positive",
            exc=frappe.ValidationError
        )
    
    order_items.append({
        "item_code": item_code,
        "qty": frappe.utils.flt(qty)
    })

# === Create Document ===
so = frappe.get_doc({
    "doctype": "Sales Order",
    "customer": customer,
    "delivery_date": delivery_date or frappe.utils.add_days(frappe.utils.today(), 7),
    "items": order_items
})
so.insert()

# === Success Response ===
frappe.response["message"] = {
    "success": True,
    "sales_order": so.name,
    "grand_total": so.grand_total
}
```

---

## Pattern 4: Scheduler with Robust Error Handling

```python
# Type: Scheduler Event
# Cron: 0 8 * * * (daily at 8:00)

BATCH_SIZE = 50
MAX_ERRORS = 10  # Stop if too many errors

stats = {
    "processed": 0,
    "skipped": 0,
    "errors": []
}

# === Get items to process ===
pending_invoices = frappe.get_all(
    "Sales Invoice",
    filters={
        "status": "Unpaid",
        "docstatus": 1,
        "due_date": ["<", frappe.utils.today()]
    },
    fields=["name", "customer", "owner", "grand_total", "due_date"],
    limit=500  # ALWAYS limit in scheduler
)

# === Process in batches ===
for i in range(0, len(pending_invoices), BATCH_SIZE):
    # Check error threshold
    if len(stats["errors"]) >= MAX_ERRORS:
        frappe.log_error(
            f"Stopped processing: Too many errors ({MAX_ERRORS})",
            "Invoice Reminder - Aborted"
        )
        break
    
    batch = pending_invoices[i:i + BATCH_SIZE]
    
    for inv in batch:
        result = process_invoice_reminder(inv)
        
        if result["status"] == "processed":
            stats["processed"] += 1
        elif result["status"] == "skipped":
            stats["skipped"] += 1
        else:
            stats["errors"].append(f"{inv.name}: {result.get('error')}")
    
    # Commit after each batch
    frappe.db.commit()

# === Log Summary ===
summary = f"""
Invoice Reminder Summary
========================
Processed: {stats["processed"]}
Skipped: {stats["skipped"]}
Errors: {len(stats["errors"])}
"""

if stats["errors"]:
    summary += "\nError Details:\n" + "\n".join(stats["errors"][:20])
    if len(stats["errors"]) > 20:
        summary += f"\n... and {len(stats["errors"]) - 20} more errors"

frappe.log_error(summary, "Invoice Reminder Summary")

# Final commit
frappe.db.commit()


def process_invoice_reminder(inv):
    """Process single invoice, return status dict."""
    
    # Check customer exists
    if not frappe.db.exists("Customer", inv.customer):
        return {"status": "error", "error": "Customer not found"}
    
    # Check if already reminded recently
    recent_reminder = frappe.db.exists(
        "ToDo",
        {
            "reference_type": "Sales Invoice",
            "reference_name": inv.name,
            "date": [">=", frappe.utils.add_days(frappe.utils.today(), -7)]
        }
    )
    
    if recent_reminder:
        return {"status": "skipped", "reason": "Recently reminded"}
    
    # Create reminder
    days_overdue = frappe.utils.date_diff(frappe.utils.today(), inv.due_date)
    
    todo = frappe.get_doc({
        "doctype": "ToDo",
        "allocated_to": inv.owner,
        "reference_type": "Sales Invoice",
        "reference_name": inv.name,
        "description": f"Invoice {inv.name} is {days_overdue} days overdue. Amount: {inv.grand_total}",
        "priority": "High" if days_overdue > 30 else "Medium",
        "date": frappe.utils.today()
    })
    todo.insert(ignore_permissions=True)
    
    return {"status": "processed"}
```

---

## Pattern 5: Cross-Document Validation

```python
# Type: Document Event
# Event: Before Submit
# DocType: Sales Invoice

# === Validate Sales Order is not already invoiced ===
if doc.items:
    for item in doc.items:
        if item.sales_order and item.so_detail:
            # Check if already invoiced
            existing = frappe.db.get_value(
                "Sales Invoice Item",
                {
                    "sales_order": item.sales_order,
                    "so_detail": item.so_detail,
                    "docstatus": 1,
                    "parent": ["!=", doc.name]
                },
                "parent"
            )
            
            if existing:
                frappe.throw(
                    f"Row {item.idx}: Sales Order Item {item.so_detail} is already invoiced in {existing}"
                )

# === Validate stock availability ===
for item in doc.items:
    if item.item_code and frappe.db.get_value("Item", item.item_code, "is_stock_item"):
        available = get_available_stock(item.item_code, item.warehouse)
        
        if available < item.qty:
            frappe.throw(
                f"Row {item.idx}: Insufficient stock for {item.item_code}. "
                f"Available: {available}, Required: {item.qty}"
            )


def get_available_stock(item_code, warehouse):
    """Get available stock quantity."""
    if not warehouse:
        return 0
    
    qty = frappe.db.get_value(
        "Bin",
        {"item_code": item_code, "warehouse": warehouse},
        "actual_qty"
    )
    
    return frappe.utils.flt(qty)
```

---

## Pattern 6: Conditional Processing with Fallbacks

```python
# Type: Document Event
# Event: After Save

# === Try to send notification, don't fail document save ===
if doc.notify_customer and doc.customer_email:
    send_result = send_notification_safe(doc)
    
    if not send_result["success"]:
        # Log error but don't fail the save
        frappe.log_error(
            f"Failed to send notification for {doc.name}: {send_result['error']}",
            "Notification Error"
        )
        frappe.msgprint(
            "Document saved but notification could not be sent",
            indicator="orange"
        )
    else:
        frappe.msgprint("Notification sent successfully", indicator="green")


def send_notification_safe(doc):
    """Attempt to send notification, return result dict."""
    
    # Validate email
    if not doc.customer_email:
        return {"success": False, "error": "No customer email"}
    
    # Check email format (basic)
    if "@" not in doc.customer_email:
        return {"success": False, "error": "Invalid email format"}
    
    # Check if email template exists
    template = "Order Confirmation"
    if not frappe.db.exists("Email Template", template):
        return {"success": False, "error": f"Template '{template}' not found"}
    
    # Send email
    frappe.sendmail(
        recipients=[doc.customer_email],
        subject=f"Order Confirmation - {doc.name}",
        template=template,
        args={"doc": doc}
    )
    
    return {"success": True}
```

---

## Pattern 7: Permission Query with Error Handling

```python
# Type: Permission Query
# DocType: Project

# Get user info safely
user_roles = frappe.get_roles(user) or []
user_department = frappe.db.get_value("User", user, "department")

# Admin access
if "System Manager" in user_roles or "Projects Admin" in user_roles:
    conditions = ""

# Manager access - see department projects
elif "Projects Manager" in user_roles:
    if user_department:
        conditions = f"`tabProject`.department = {frappe.db.escape(user_department)}"
    else:
        # Manager without department - only own projects
        frappe.log_error(
            f"Projects Manager {user} has no department assigned",
            "Permission Query Warning"
        )
        conditions = f"`tabProject`.owner = {frappe.db.escape(user)}"

# User access - own projects only
elif "Projects User" in user_roles:
    conditions = f"`tabProject`.owner = {frappe.db.escape(user)}"

# No access
else:
    conditions = "1=0"
```

---

## Pattern 8: Dependent Field Calculation with Validation

```python
# Type: Document Event
# Event: Before Save
# DocType: Purchase Order

# === Calculate totals from items ===
if doc.items:
    doc.total_qty = 0
    doc.total_amount = 0
    
    for item in doc.items:
        # Validate item has required values
        if (item.qty or 0) <= 0:
            frappe.throw(f"Row {item.idx}: Quantity must be positive")
        
        if (item.rate or 0) < 0:
            frappe.throw(f"Row {item.idx}: Rate cannot be negative")
        
        # Calculate item amount
        item.amount = frappe.utils.flt(item.qty) * frappe.utils.flt(item.rate)
        
        # Add to totals
        doc.total_qty += item.qty
        doc.total_amount += item.amount

# === Apply discount ===
discount_pct = frappe.utils.flt(doc.discount_percentage)
if discount_pct < 0 or discount_pct > 100:
    frappe.throw("Discount percentage must be between 0 and 100")

doc.discount_amount = doc.total_amount * discount_pct / 100
doc.grand_total = doc.total_amount - doc.discount_amount

# === Tax calculation with validation ===
if doc.taxes:
    for tax in doc.taxes:
        if not tax.rate and not tax.tax_amount:
            frappe.throw(f"Tax row {tax.idx}: Either rate or amount is required")
        
        if tax.rate:
            tax.tax_amount = doc.grand_total * frappe.utils.flt(tax.rate) / 100
        
        doc.grand_total += tax.tax_amount

# === Final validation ===
if doc.grand_total < 0:
    frappe.throw("Grand total cannot be negative after discounts and taxes")
```

---

## Pattern 9: Linked Document Creation with Rollback Safety

```python
# Type: Document Event
# Event: After Submit
# DocType: Sales Order

# === Create linked documents after submit ===
# Note: If this fails, the Sales Order submit will also roll back

if doc.auto_create_delivery:
    # Validate warehouse exists
    if not doc.set_warehouse:
        frappe.throw("Warehouse is required for auto-creating Delivery Note")
    
    if not frappe.db.exists("Warehouse", doc.set_warehouse):
        frappe.throw(f"Warehouse '{doc.set_warehouse}' not found")
    
    # Create Delivery Note
    dn = frappe.get_doc({
        "doctype": "Delivery Note",
        "customer": doc.customer,
        "items": [
            {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": item.rate,
                "warehouse": doc.set_warehouse,
                "against_sales_order": doc.name,
                "so_detail": item.name
            }
            for item in doc.items
        ]
    })
    dn.insert()
    
    frappe.msgprint(
        f"Delivery Note {dn.name} created",
        indicator="green"
    )
```

---

## Pattern 10: Idempotent Scheduler Operations

```python
# Type: Scheduler Event
# Cron: */15 * * * * (every 15 minutes)

# === Pattern: Check if already processed ===
# Prevent duplicate processing if scheduler runs twice

LOCK_KEY = "sync_inventory_lock"
LOCK_TIMEOUT = 600  # 10 minutes

# Check if another instance is running
lock_time = frappe.cache().get_value(LOCK_KEY)
if lock_time:
    elapsed = frappe.utils.time_diff_in_seconds(frappe.utils.now(), lock_time)
    if elapsed < LOCK_TIMEOUT:
        frappe.log_error(
            f"Skipped: Another instance running (started {elapsed}s ago)",
            "Inventory Sync"
        )
        return

# Set lock
frappe.cache().set_value(LOCK_KEY, frappe.utils.now())

processed = 0

# Get items that need sync
items_to_sync = frappe.get_all(
    "Item",
    filters={
        "sync_status": "Pending",
        "disabled": 0
    },
    fields=["name"],
    limit=100
)

for item in items_to_sync:
    # Mark as processing first (idempotent)
    frappe.db.set_value("Item", item.name, "sync_status", "Processing")
    frappe.db.commit()
    
    # Do sync
    result = sync_item_inventory(item.name)
    
    # Update status
    new_status = "Synced" if result else "Failed"
    frappe.db.set_value("Item", item.name, {
        "sync_status": new_status,
        "last_synced": frappe.utils.now()
    })
    frappe.db.commit()
    
    if result:
        processed += 1

# Clear lock
frappe.cache().delete_value(LOCK_KEY)

frappe.log_error(f"Synced {processed} items", "Inventory Sync Complete")
frappe.db.commit()


def sync_item_inventory(item_name):
    """Sync single item, return True on success."""
    # Sync logic here
    return True
```
