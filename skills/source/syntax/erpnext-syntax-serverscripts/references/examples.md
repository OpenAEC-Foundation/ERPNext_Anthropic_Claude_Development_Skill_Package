# Server Script Examples

## Table of Contents

1. [Document Event Examples](#document-event-examples)
2. [API Examples](#api-examples)
3. [Scheduler Event Examples](#scheduler-event-examples)
4. [Permission Query Examples](#permission-query-examples)

---

## Document Event Examples

### 1. Validation with error message

**Script Type**: Document Event  
**DocType Event**: Before Save  
**Reference DocType**: Sales Invoice

```python
# Validate minimum order amount
if doc.grand_total < 100:
    frappe.throw("Minimum order amount is $100")

# Validate percentage
if doc.discount_percentage and doc.discount_percentage > 50:
    frappe.throw("Discount cannot exceed 50%", title="Validation Error")
```

### 2. Auto-calculate fields

**Script Type**: Document Event  
**DocType Event**: Before Save  
**Reference DocType**: Sales Order

```python
# Calculate total from child items
doc.total_qty = sum(item.qty or 0 for item in doc.items)
doc.total_weight = sum((item.qty or 0) * (item.weight_per_unit or 0) for item in doc.items)

# Set status based on total
if doc.grand_total > 10000:
    doc.priority = "High"
    doc.requires_approval = 1
```

### 3. Auto-fill related data

**Script Type**: Document Event  
**DocType Event**: Before Save  
**Reference DocType**: Sales Invoice

```python
# Fetch customer data if not set
if doc.customer and not doc.customer_name:
    doc.customer_name = frappe.db.get_value("Customer", doc.customer, "customer_name")

# Fetch territory from customer
if doc.customer and not doc.territory:
    doc.territory = frappe.db.get_value("Customer", doc.customer, "territory")
```

### 4. Create related document

**Script Type**: Document Event  
**DocType Event**: After Insert  
**Reference DocType**: Sales Order

```python
# Create ToDo for sales team
frappe.get_doc({
    "doctype": "ToDo",
    "allocated_to": doc.owner,
    "reference_type": "Sales Order",
    "reference_name": doc.name,
    "description": f"New order {doc.name} - Follow up with customer",
    "date": frappe.utils.add_days(frappe.utils.today(), 1)
}).insert(ignore_permissions=True)
```

### 5. Pre-submit validation

**Script Type**: Document Event  
**DocType Event**: Before Submit  
**Reference DocType**: Purchase Order

```python
# Check budget approval for large orders
if doc.grand_total > 50000:
    if not doc.budget_approval:
        frappe.throw("Budget approval required for orders over $50,000")
    
    # Check that approver is not the creator
    if doc.approved_by == doc.owner:
        frappe.throw("Order cannot be approved by its creator")
```

### 6. Post-submit actions

**Script Type**: Document Event  
**DocType Event**: After Submit  
**Reference DocType**: Sales Invoice

```python
# Update customer statistics
customer_doc = frappe.get_doc("Customer", doc.customer)

# Count total invoices
total_invoices = frappe.db.count("Sales Invoice", 
    filters={"customer": doc.customer, "docstatus": 1})

# Update custom field
frappe.db.set_value("Customer", doc.customer, "total_invoices", total_invoices)

# Send notification for high-value invoice
if doc.grand_total > 10000:
    frappe.msgprint(f"High-value invoice {doc.name} created", alert=True)
```

### 7. Cancel validation

**Script Type**: Document Event  
**DocType Event**: Before Cancel  
**Reference DocType**: Sales Invoice

```python
# Check if there are payments
payments = frappe.get_all("Payment Entry Reference",
    filters={
        "reference_doctype": "Sales Invoice",
        "reference_name": doc.name,
        "docstatus": 1
    },
    fields=["parent"]
)

if payments:
    frappe.throw(
        f"Cannot cancel: invoice has {len(payments)} linked payment(s). "
        "Cancel the payments first.",
        title="Cancellation Blocked"
    )
```

### 8. Audit logging

**Script Type**: Document Event  
**DocType Event**: After Save  
**Reference DocType**: Sales Order

```python
# Log important changes
log_msg = f"Sales Order {doc.name} updated\n"
log_msg += f"Status: {doc.status}\n"
log_msg += f"Total: {doc.grand_total}\n"
log_msg += f"Modified by: {frappe.session.user}"

frappe.log_error(log_msg, "Sales Order Audit")
```

---

## API Examples

### 9. Basic GET endpoint

**Script Type**: API  
**API Method**: get_customer_orders  
**Allow Guest**: No

```python
# Endpoint: /api/method/get_customer_orders?customer=CUST-001

customer = frappe.form_dict.get("customer")
if not customer:
    frappe.throw("Parameter 'customer' is required")

# Check permissions
if not frappe.has_permission("Sales Order", "read"):
    frappe.throw("Access denied", frappe.PermissionError)

orders = frappe.get_all("Sales Order",
    filters={
        "customer": customer,
        "docstatus": 1
    },
    fields=["name", "transaction_date", "grand_total", "status"],
    order_by="transaction_date desc",
    limit=20
)

frappe.response["message"] = {
    "customer": customer,
    "orders": orders,
    "count": len(orders)
}
```

### 10. POST endpoint with data processing

**Script Type**: API  
**API Method**: update_order_status  
**Allow Guest**: No

```python
# Endpoint: POST /api/method/update_order_status
# Body: {"order": "SO-001", "status": "Completed"}

order_name = frappe.form_dict.get("order")
new_status = frappe.form_dict.get("status")

if not order_name or not new_status:
    frappe.throw("Parameters 'order' and 'status' are required")

# Validate status value
valid_statuses = ["Open", "Completed", "On Hold", "Cancelled"]
if new_status not in valid_statuses:
    frappe.throw(f"Invalid status. Choose from: {', '.join(valid_statuses)}")

# Check permission for specific document
if not frappe.has_permission("Sales Order", "write", order_name):
    frappe.throw("No write permission for this order", frappe.PermissionError)

# Update status
frappe.db.set_value("Sales Order", order_name, "status", new_status)

frappe.response["message"] = {
    "success": True,
    "order": order_name,
    "new_status": new_status
}
```

### 11. Dashboard data endpoint

**Script Type**: API  
**API Method**: get_sales_dashboard  
**Allow Guest**: No

```python
# Endpoint: /api/method/get_sales_dashboard

today = frappe.utils.today()
month_start = frappe.utils.get_first_day(today)

# Orders today
orders_today = frappe.db.count("Sales Order",
    filters={"transaction_date": today, "docstatus": 1})

# Revenue this month
month_sales = frappe.db.sql("""
    SELECT COALESCE(SUM(grand_total), 0) as total
    FROM `tabSales Invoice`
    WHERE posting_date >= %(month_start)s
    AND docstatus = 1
""", {"month_start": month_start}, as_dict=True)

# Top 5 customers
top_customers = frappe.get_all("Sales Invoice",
    filters={"posting_date": [">=", month_start], "docstatus": 1},
    fields=["customer", "sum(grand_total) as total"],
    group_by="customer",
    order_by="total desc",
    limit=5
)

frappe.response["message"] = {
    "orders_today": orders_today,
    "month_sales": month_sales[0].total if month_sales else 0,
    "top_customers": top_customers
}
```

### 12. Public endpoint (guest access)

**Script Type**: API  
**API Method**: check_product_availability  
**Allow Guest**: Yes

```python
# Endpoint: /api/method/check_product_availability?item=ITEM-001

item_code = frappe.form_dict.get("item")
if not item_code:
    frappe.throw("Parameter 'item' is required")

# Only show published items
item = frappe.db.get_value("Item", item_code, 
    ["item_name", "stock_uom", "is_stock_item", "disabled"],
    as_dict=True)

if not item or item.disabled:
    frappe.response["message"] = {
        "available": False,
        "message": "Product not found"
    }
else:
    # Get stock (simplified)
    stock = frappe.db.get_value("Bin",
        {"item_code": item_code},
        "sum(actual_qty) as qty") or 0
    
    frappe.response["message"] = {
        "available": stock > 0,
        "item_name": item.item_name,
        "stock_qty": stock,
        "uom": item.stock_uom
    }
```

---

## Scheduler Event Examples

### 13. Daily reminder

**Script Type**: Scheduler Event  
**Event Frequency**: Cron  
**Cron Format**: `0 9 * * *` (daily at 9:00)

```python
# Send reminders for overdue invoices
today = frappe.utils.today()

overdue_invoices = frappe.get_all("Sales Invoice",
    filters={
        "status": "Unpaid",
        "due_date": ["<", today],
        "docstatus": 1
    },
    fields=["name", "customer", "grand_total", "due_date", "owner"]
)

for inv in overdue_invoices:
    days_overdue = frappe.utils.date_diff(today, inv.due_date)
    
    # Create ToDo for sales rep
    if not frappe.db.exists("ToDo", {
        "reference_type": "Sales Invoice",
        "reference_name": inv.name,
        "status": "Open"
    }):
        frappe.get_doc({
            "doctype": "ToDo",
            "allocated_to": inv.owner,
            "reference_type": "Sales Invoice",
            "reference_name": inv.name,
            "description": f"Invoice {inv.name} is {days_overdue} days overdue. Total: {inv.grand_total}"
        }).insert(ignore_permissions=True)

frappe.db.commit()
```

### 14. Weekly cleanup

**Script Type**: Scheduler Event  
**Event Frequency**: Cron  
**Cron Format**: `0 2 * * 0` (Sunday 02:00)

```python
# Delete old draft documents (older than 30 days)
cutoff_date = frappe.utils.add_days(frappe.utils.today(), -30)

# Find old drafts
old_drafts = frappe.get_all("Sales Order",
    filters={
        "docstatus": 0,
        "modified": ["<", cutoff_date]
    },
    fields=["name"],
    limit=100  # Batch limit
)

deleted_count = 0
for draft in old_drafts:
    try:
        frappe.delete_doc("Sales Order", draft.name, force=True)
        deleted_count += 1
    except Exception:
        frappe.log_error(
            f"Could not delete draft {draft.name}",
            "Cleanup Error"
        )

frappe.db.commit()

if deleted_count > 0:
    frappe.log_error(
        f"Cleanup: {deleted_count} old drafts deleted",
        "Weekly Cleanup"
    )
```

### 15. Every 15 minutes sync

**Script Type**: Scheduler Event  
**Event Frequency**: Cron  
**Cron Format**: `*/15 * * * *` (every 15 minutes)

```python
# Sync external data (example: exchange rates)
# This is a placeholder - external API calls don't work in sandbox

last_sync = frappe.db.get_single_value("Sync Settings", "last_sync") or ""
now = frappe.utils.now()

# Check if sync is needed
if last_sync:
    minutes_since = frappe.utils.time_diff_in_seconds(now, last_sync) / 60
    if minutes_since < 14:  # Skip if recently synced
        return

# Log sync attempt
frappe.log_error(f"Sync started at {now}", "External Sync")

# Update last sync time
frappe.db.set_single_value("Sync Settings", "last_sync", now)
frappe.db.commit()
```

### 16. Monthly reporting

**Script Type**: Scheduler Event  
**Event Frequency**: Cron  
**Cron Format**: `0 6 1 * *` (1st of month at 06:00)

```python
# Generate monthly sales summary
last_month_start = frappe.utils.add_months(
    frappe.utils.get_first_day(frappe.utils.today()), -1)
last_month_end = frappe.utils.get_last_day(last_month_start)

# Sales totals
summary = frappe.db.sql("""
    SELECT 
        COUNT(*) as invoice_count,
        COALESCE(SUM(grand_total), 0) as total_revenue,
        COUNT(DISTINCT customer) as unique_customers
    FROM `tabSales Invoice`
    WHERE posting_date BETWEEN %(start)s AND %(end)s
    AND docstatus = 1
""", {"start": last_month_start, "end": last_month_end}, as_dict=True)[0]

# Create report record
report_msg = f"""
Monthly Sales Summary
Period: {last_month_start} to {last_month_end}

Invoices: {summary.invoice_count}
Revenue: ${summary.total_revenue:,.2f}
Unique customers: {summary.unique_customers}
"""

frappe.log_error(report_msg, "Monthly Sales Report")
frappe.db.commit()
```

---

## Permission Query Examples

### 17. Basic role-based filtering

**Script Type**: Permission Query  
**Reference DocType**: Sales Invoice

```python
# Filter documents based on user role
user_roles = frappe.get_roles(user)

if "System Manager" in user_roles or "Accounts Manager" in user_roles:
    # Full access
    conditions = ""
elif "Sales User" in user_roles:
    # Only own invoices
    conditions = f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
else:
    # No access
    conditions = "1=0"
```

### 18. Territory-based filtering

**Script Type**: Permission Query  
**Reference DocType**: Customer

```python
# Filter customers based on user's territory
user_territory = frappe.db.get_value("User", user, "territory")

if not user_territory:
    # If no territory, show nothing (or everything for managers)
    if "Sales Manager" in frappe.get_roles(user):
        conditions = ""
    else:
        conditions = "1=0"
else:
    # Only customers in user's territory
    conditions = f"`tabCustomer`.territory = {frappe.db.escape(user_territory)}"
```

### 19. Company-based filtering

**Script Type**: Permission Query  
**Reference DocType**: Sales Order

```python
# Filter based on allowed companies
allowed_companies = frappe.get_all("User Permission",
    filters={"user": user, "allow": "Company"},
    pluck="for_value"
)

if not allowed_companies:
    # If no company permissions, use default company
    default_company = frappe.db.get_single_value("Global Defaults", "default_company")
    if default_company:
        conditions = f"`tabSales Order`.company = {frappe.db.escape(default_company)}"
    else:
        conditions = ""
elif len(allowed_companies) == 1:
    conditions = f"`tabSales Order`.company = {frappe.db.escape(allowed_companies[0])}"
else:
    company_list = ", ".join(frappe.db.escape(c) for c in allowed_companies)
    conditions = f"`tabSales Order`.company IN ({company_list})"
```

### 20. Status-based filtering

**Script Type**: Permission Query  
**Reference DocType**: Task

```python
# Show only open tasks to normal users
user_roles = frappe.get_roles(user)

if "Project Manager" in user_roles:
    # Managers see everything
    conditions = ""
else:
    # Others see only their own open tasks
    conditions = f"""
        (`tabTask`.owner = {frappe.db.escape(user)} 
         OR `tabTask`.assigned_to = {frappe.db.escape(user)})
        AND `tabTask`.status NOT IN ('Cancelled', 'Completed')
    """
```
