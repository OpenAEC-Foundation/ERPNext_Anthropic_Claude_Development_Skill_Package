# Server Script Implementation Workflows

## Workflow Patterns by Category

### Category 1: Document Validation Patterns

#### Pattern: Multi-Field Validation

```python
# Type: Document Event | Event: Before Save | DocType: Sales Order

errors = []

# Field validations
if not doc.customer:
    errors.append("Customer is required")

if doc.delivery_date and doc.delivery_date < frappe.utils.today():
    errors.append("Delivery date cannot be in the past")

if doc.grand_total < 0:
    errors.append("Total cannot be negative")

# Child table validation
if not doc.items or len(doc.items) == 0:
    errors.append("At least one item is required")

for item in doc.items:
    if item.qty <= 0:
        errors.append(f"Row {item.idx}: Quantity must be positive")

# Throw all errors at once
if errors:
    frappe.throw("<br>".join(errors), title="Validation Error")
```

#### Pattern: Cross-Document Validation

```python
# Type: Document Event | Event: Before Save | DocType: Delivery Note

# Check that Sales Order exists and is submitted
if doc.sales_order:
    so_status = frappe.db.get_value("Sales Order", doc.sales_order, 
        ["docstatus", "status"], as_dict=True)
    
    if not so_status:
        frappe.throw(f"Sales Order {doc.sales_order} not found")
    
    if so_status.docstatus != 1:
        frappe.throw(f"Sales Order {doc.sales_order} is not submitted")
    
    if so_status.status == "Closed":
        frappe.throw(f"Sales Order {doc.sales_order} is closed")
```

#### Pattern: Conditional Required Fields

```python
# Type: Document Event | Event: Before Save | DocType: Sales Invoice

# If payment terms exist, due_date is auto-calculated
# Otherwise, due_date is required
if not doc.payment_terms_template and not doc.due_date:
    frappe.throw("Due Date is required when Payment Terms is not set")

# If shipping is required, shipping address is mandatory
if doc.is_shipping_required and not doc.shipping_address:
    frappe.throw("Shipping Address is required when shipping is enabled")
```

### Category 2: Auto-Calculation Patterns

#### Pattern: Child Table Aggregation

```python
# Type: Document Event | Event: Before Save | DocType: Purchase Order

# Initialize totals
total_qty = 0
total_amount = 0
total_tax = 0

for item in doc.items:
    # Calculate row amount
    item.amount = (item.qty or 0) * (item.rate or 0)
    item.net_amount = item.amount - (item.discount_amount or 0)
    
    # Accumulate
    total_qty += item.qty or 0
    total_amount += item.net_amount or 0

# Calculate tax
tax_rate = frappe.db.get_value("Tax Template", doc.tax_template, "rate") or 0
total_tax = total_amount * (tax_rate / 100)

# Set document fields
doc.total_qty = total_qty
doc.net_total = total_amount
doc.tax_amount = total_tax
doc.grand_total = total_amount + total_tax
```

#### Pattern: Date Calculations

```python
# Type: Document Event | Event: Before Save | DocType: Project

# Calculate end date from start date and duration
if doc.expected_start_date and doc.estimated_days:
    doc.expected_end_date = frappe.utils.add_days(
        doc.expected_start_date, 
        doc.estimated_days
    )

# Calculate working days
if doc.actual_start_date and doc.actual_end_date:
    doc.actual_days = frappe.utils.date_diff(
        doc.actual_end_date, 
        doc.actual_start_date
    )
```

#### Pattern: Running Totals / Balances

```python
# Type: Document Event | Event: After Submit | DocType: Payment Entry

# Update customer outstanding
if doc.party_type == "Customer":
    # Get current outstanding
    outstanding = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0)
        FROM `tabSales Invoice`
        WHERE customer = %(customer)s AND docstatus = 1
    """, {"customer": doc.party}, as_dict=False)[0][0]
    
    # Update customer master
    frappe.db.set_value("Customer", doc.party, "outstanding_amount", outstanding)
```

### Category 3: Notification Patterns

#### Pattern: Conditional Notification

```python
# Type: Document Event | Event: After Submit | DocType: Sales Order

# Notify sales manager for high-value orders
if doc.grand_total > 100000:
    managers = frappe.get_all("User",
        filters={"role": "Sales Manager", "enabled": 1},
        pluck="name"
    )
    
    for manager in managers:
        frappe.get_doc({
            "doctype": "Notification Log",
            "subject": f"High-Value Order: {doc.name}",
            "for_user": manager,
            "type": "Alert",
            "document_type": "Sales Order",
            "document_name": doc.name,
            "email_content": f"Order {doc.name} worth {doc.grand_total} submitted"
        }).insert(ignore_permissions=True)
```

#### Pattern: Send Email Notification

```python
# Type: Document Event | Event: After Submit | DocType: Purchase Order

# Send PO to supplier (using Frappe's email queue)
supplier_email = frappe.db.get_value("Supplier", doc.supplier, "email_id")

if supplier_email:
    frappe.sendmail(
        recipients=[supplier_email],
        subject=f"Purchase Order {doc.name}",
        message=f"""
Dear {doc.supplier_name},

Please find attached Purchase Order {doc.name} for {doc.grand_total}.

Best regards
        """,
        reference_doctype="Purchase Order",
        reference_name=doc.name
    )
```

### Category 4: Status Management Patterns

#### Pattern: Auto-Status Based on Child Items

```python
# Type: Document Event | Event: Before Save | DocType: Sales Order

# Calculate delivered quantities
total_ordered = sum(item.qty or 0 for item in doc.items)
total_delivered = sum(item.delivered_qty or 0 for item in doc.items)

# Set delivery status
if total_delivered == 0:
    doc.delivery_status = "Not Delivered"
elif total_delivered < total_ordered:
    doc.delivery_status = "Partially Delivered"
else:
    doc.delivery_status = "Fully Delivered"
```

#### Pattern: Workflow Transition Validation

```python
# Type: Document Event | Event: Before Save | DocType: Leave Application

# Validate status transitions
old_status = frappe.db.get_value("Leave Application", doc.name, "status")

allowed_transitions = {
    "Draft": ["Applied"],
    "Applied": ["Approved", "Rejected"],
    "Approved": ["Cancelled"],
    "Rejected": []
}

if old_status and doc.status != old_status:
    if doc.status not in allowed_transitions.get(old_status, []):
        frappe.throw(f"Cannot change status from {old_status} to {doc.status}")
```

### Category 5: API Patterns

#### Pattern: Paginated List API

```python
# Type: API | Method: get_orders | Allow Guest: No

page = frappe.utils.cint(frappe.form_dict.get("page", 1))
page_size = min(frappe.utils.cint(frappe.form_dict.get("page_size", 20)), 100)
customer = frappe.form_dict.get("customer")

filters = {"docstatus": 1}
if customer:
    filters["customer"] = customer

# Permission filter
if "Sales Manager" not in frappe.get_roles():
    filters["owner"] = frappe.session.user

orders = frappe.get_all("Sales Order",
    filters=filters,
    fields=["name", "customer", "grand_total", "status", "transaction_date"],
    order_by="transaction_date desc",
    limit_start=(page - 1) * page_size,
    limit_page_length=page_size
)

total = frappe.db.count("Sales Order", filters)

frappe.response["message"] = {
    "data": orders,
    "page": page,
    "page_size": page_size,
    "total": total,
    "pages": -(-total // page_size)  # Ceiling division
}
```

#### Pattern: Action API with Validation

```python
# Type: API | Method: approve_order | Allow Guest: No

order_name = frappe.form_dict.get("order")
if not order_name:
    frappe.throw("Order parameter is required")

# Check permission
if not frappe.has_permission("Sales Order", "write", order_name):
    frappe.throw("No permission to approve this order", frappe.PermissionError)

# Check role
if "Sales Manager" not in frappe.get_roles():
    frappe.throw("Only Sales Managers can approve orders")

# Get and validate order
order = frappe.get_doc("Sales Order", order_name)

if order.docstatus != 0:
    frappe.throw("Only draft orders can be approved")

if order.approval_status == "Approved":
    frappe.throw("Order is already approved")

# Perform action
order.approval_status = "Approved"
order.approved_by = frappe.session.user
order.approved_on = frappe.utils.now()
order.save()

frappe.response["message"] = {
    "success": True,
    "order": order_name,
    "approved_by": frappe.session.user
}
```

### Category 6: Scheduler Patterns

#### Pattern: Batch Processing with Chunking

```python
# Type: Scheduler Event | Cron: 0 3 * * * (daily 3:00 AM)

BATCH_SIZE = 100
processed = 0

# Process in batches to avoid memory issues
while True:
    records = frappe.get_all("Sales Invoice",
        filters={
            "status": "Unpaid",
            "due_date": ["<", frappe.utils.add_days(frappe.utils.today(), -30)],
            "overdue_notified": 0
        },
        fields=["name", "customer", "grand_total"],
        limit=BATCH_SIZE
    )
    
    if not records:
        break
    
    for record in records:
        try:
            # Process each record
            frappe.db.set_value("Sales Invoice", record.name, "overdue_notified", 1)
            processed += 1
        except Exception:
            frappe.log_error(f"Failed to process {record.name}", "Overdue Processing")
    
    frappe.db.commit()  # Commit each batch

frappe.log_error(f"Processed {processed} overdue invoices", "Overdue Processing Complete")
```

#### Pattern: Data Synchronization

```python
# Type: Scheduler Event | Cron: */30 * * * * (every 30 minutes)

# Sync stock levels to external system (log-based, no external calls in sandbox)
last_sync = frappe.db.get_single_value("Sync Settings", "last_stock_sync") or "2000-01-01"

# Get items modified since last sync
modified_items = frappe.get_all("Bin",
    filters={"modified": [">", last_sync]},
    fields=["item_code", "warehouse", "actual_qty", "reserved_qty"],
    limit=500
)

if modified_items:
    # Log for external processing (actual sync would be done by external worker)
    frappe.get_doc({
        "doctype": "Sync Queue",
        "sync_type": "Stock",
        "data": frappe.as_json(modified_items),
        "status": "Pending"
    }).insert(ignore_permissions=True)
    
    # Update last sync time
    frappe.db.set_single_value("Sync Settings", "last_stock_sync", frappe.utils.now())
    frappe.db.commit()
```

#### Pattern: Report Generation

```python
# Type: Scheduler Event | Cron: 0 7 * * 1 (Monday 7:00 AM)

# Generate weekly sales report
week_start = frappe.utils.add_days(frappe.utils.today(), -7)
week_end = frappe.utils.add_days(frappe.utils.today(), -1)

# Aggregate data
summary = frappe.db.sql("""
    SELECT 
        COUNT(*) as total_orders,
        SUM(grand_total) as total_revenue,
        COUNT(DISTINCT customer) as unique_customers,
        AVG(grand_total) as avg_order_value
    FROM `tabSales Order`
    WHERE transaction_date BETWEEN %(start)s AND %(end)s
    AND docstatus = 1
""", {"start": week_start, "end": week_end}, as_dict=True)[0]

# Top customers
top_customers = frappe.get_all("Sales Order",
    filters={
        "transaction_date": ["between", [week_start, week_end]],
        "docstatus": 1
    },
    fields=["customer", "sum(grand_total) as total"],
    group_by="customer",
    order_by="total desc",
    limit=5
)

# Store report
frappe.get_doc({
    "doctype": "Weekly Report",
    "report_date": frappe.utils.today(),
    "period_start": week_start,
    "period_end": week_end,
    "total_orders": summary.total_orders,
    "total_revenue": summary.total_revenue,
    "unique_customers": summary.unique_customers,
    "avg_order_value": summary.avg_order_value,
    "top_customers": frappe.as_json(top_customers)
}).insert(ignore_permissions=True)

frappe.db.commit()
```

### Category 7: Permission Query Patterns

#### Pattern: Hierarchical Territory Access

```python
# Type: Permission Query | DocType: Customer

def get_child_territories(territory):
    """Get all child territories recursively"""
    children = frappe.get_all("Territory",
        filters={"parent_territory": territory},
        pluck="name"
    )
    all_territories = [territory]
    for child in children:
        all_territories.extend(get_child_territories(child))
    return all_territories

# Get user's territory
user_territory = frappe.db.get_value("User", user, "territory")
user_roles = frappe.get_roles(user)

if "System Manager" in user_roles:
    conditions = ""
elif user_territory:
    # Include all child territories
    territories = get_child_territories(user_territory)
    territory_list = ", ".join(frappe.db.escape(t) for t in territories)
    conditions = f"`tabCustomer`.territory IN ({territory_list})"
else:
    conditions = f"`tabCustomer`.owner = {frappe.db.escape(user)}"
```

#### Pattern: Multi-Company Access

```python
# Type: Permission Query | DocType: Sales Invoice

# Get user's allowed companies
allowed = frappe.get_all("User Permission",
    filters={"user": user, "allow": "Company"},
    pluck="for_value"
)

user_roles = frappe.get_roles(user)

if "System Manager" in user_roles:
    conditions = ""
elif allowed:
    company_list = ", ".join(frappe.db.escape(c) for c in allowed)
    conditions = f"`tabSales Invoice`.company IN ({company_list})"
else:
    # Default company only
    default = frappe.db.get_single_value("Global Defaults", "default_company")
    if default:
        conditions = f"`tabSales Invoice`.company = {frappe.db.escape(default)}"
    else:
        conditions = "1=0"  # No access
```
