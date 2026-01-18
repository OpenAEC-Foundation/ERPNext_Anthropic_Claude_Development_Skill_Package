# Server Script Implementation Examples

## Example 1: Complete Invoice Validation

**Use Case**: Validate Sales Invoice before save with multiple business rules.

```python
# Configuration:
#   Type: Document Event
#   DocType Event: Before Save
#   Reference DocType: Sales Invoice

# ═══════════════════════════════════════════════════════════
# SALES INVOICE VALIDATION - Before Save
# ═══════════════════════════════════════════════════════════

errors = []

# 1. Customer validation
if not doc.customer:
    errors.append("Customer is required")
else:
    customer = frappe.db.get_value("Customer", doc.customer,
        ["disabled", "is_frozen"], as_dict=True)
    
    if customer and customer.disabled:
        errors.append(f"Customer {doc.customer} is disabled")
    if customer and customer.is_frozen:
        errors.append(f"Customer {doc.customer} is frozen")

# 2. Date validation
if doc.posting_date:
    if doc.posting_date > frappe.utils.today():
        errors.append("Posting date cannot be in the future")
    
    # Check fiscal year
    fiscal_year = frappe.db.get_value("Fiscal Year",
        filters={
            "year_start_date": ["<=", doc.posting_date],
            "year_end_date": [">=", doc.posting_date]
        })
    if not fiscal_year:
        errors.append(f"No fiscal year found for date {doc.posting_date}")

# 3. Items validation
if not doc.items:
    errors.append("At least one item is required")
else:
    for item in doc.items:
        if item.qty <= 0:
            errors.append(f"Row {item.idx}: Quantity must be greater than zero")
        if item.rate < 0:
            errors.append(f"Row {item.idx}: Rate cannot be negative")
        
        # Check item exists and is not disabled
        item_doc = frappe.db.get_value("Item", item.item_code,
            ["disabled", "is_sales_item"], as_dict=True)
        if not item_doc:
            errors.append(f"Row {item.idx}: Item {item.item_code} not found")
        elif item_doc.disabled:
            errors.append(f"Row {item.idx}: Item {item.item_code} is disabled")
        elif not item_doc.is_sales_item:
            errors.append(f"Row {item.idx}: Item {item.item_code} is not a sales item")

# 4. Amount validation
if doc.grand_total < 0:
    errors.append("Grand Total cannot be negative")

if doc.discount_percentage and doc.discount_percentage > 50:
    errors.append("Discount cannot exceed 50%")

# Throw all errors
if errors:
    frappe.throw("<br>".join(errors), title="Validation Errors")
```

## Example 2: Auto-Numbering with Prefix

**Use Case**: Generate custom naming series with prefix based on type.

```python
# Configuration:
#   Type: Document Event
#   DocType Event: Before Insert
#   Reference DocType: Project

# ═══════════════════════════════════════════════════════════
# PROJECT AUTO-NUMBERING - Before Insert
# ═══════════════════════════════════════════════════════════

# Determine prefix based on project type
prefix_map = {
    "Internal": "INT",
    "External": "EXT",
    "Maintenance": "MNT",
    "Development": "DEV"
}

prefix = prefix_map.get(doc.project_type, "PRJ")
year = frappe.utils.nowdate()[:4]

# Get next number
key = f"project_{prefix}_{year}"
current = frappe.db.get_single_value("Naming Series Counter", key) or 0
next_num = current + 1

# Update counter (create if not exists)
if not frappe.db.exists("Naming Series Counter", key):
    frappe.get_doc({
        "doctype": "Naming Series Counter",
        "name": key,
        "current": next_num
    }).insert(ignore_permissions=True)
else:
    frappe.db.set_value("Naming Series Counter", key, "current", next_num)

# Set project name
doc.name = f"{prefix}-{year}-{next_num:05d}"
```

## Example 3: Stock Availability Check

**Use Case**: Validate stock before Sales Order submission.

```python
# Configuration:
#   Type: Document Event
#   DocType Event: Before Submit
#   Reference DocType: Sales Order

# ═══════════════════════════════════════════════════════════
# STOCK AVAILABILITY CHECK - Before Submit
# ═══════════════════════════════════════════════════════════

errors = []

for item in doc.items:
    # Skip non-stock items
    is_stock = frappe.db.get_value("Item", item.item_code, "is_stock_item")
    if not is_stock:
        continue
    
    # Get available quantity
    available = frappe.db.get_value("Bin",
        filters={
            "item_code": item.item_code,
            "warehouse": item.warehouse
        },
        fieldname="actual_qty"
    ) or 0
    
    # Get already reserved quantity
    reserved = frappe.db.sql("""
        SELECT COALESCE(SUM(soi.qty - soi.delivered_qty), 0)
        FROM `tabSales Order Item` soi
        JOIN `tabSales Order` so ON soi.parent = so.name
        WHERE soi.item_code = %(item)s
        AND soi.warehouse = %(warehouse)s
        AND so.docstatus = 1
        AND so.name != %(exclude)s
    """, {
        "item": item.item_code,
        "warehouse": item.warehouse,
        "exclude": doc.name
    })[0][0] or 0
    
    available_for_order = available - reserved
    
    if item.qty > available_for_order:
        errors.append(
            f"Row {item.idx}: {item.item_code} - "
            f"Required: {item.qty}, Available: {available_for_order} "
            f"(Stock: {available}, Reserved: {reserved})"
        )

if errors:
    frappe.throw(
        "Insufficient stock:<br>" + "<br>".join(errors),
        title="Stock Validation Error"
    )
```

## Example 4: Cascading Status Update

**Use Case**: Update parent document status when child changes.

```python
# Configuration:
#   Type: Document Event
#   DocType Event: After Save
#   Reference DocType: Task

# ═══════════════════════════════════════════════════════════
# UPDATE PROJECT STATUS - After Task Save
# ═══════════════════════════════════════════════════════════

if not doc.project:
    return

# Get all tasks for this project
tasks = frappe.get_all("Task",
    filters={"project": doc.project},
    fields=["status", "is_milestone"]
)

if not tasks:
    return

# Calculate progress
total = len(tasks)
completed = len([t for t in tasks if t.status == "Completed"])
in_progress = len([t for t in tasks if t.status == "Working"])

# Determine project status
if completed == total:
    project_status = "Completed"
elif completed > 0 or in_progress > 0:
    project_status = "Open"
else:
    project_status = "Pending"

# Calculate percentage
percent_complete = (completed / total * 100) if total > 0 else 0

# Update project (using db_set to avoid triggering events)
frappe.db.set_value("Project", doc.project, {
    "status": project_status,
    "percent_complete": percent_complete
}, update_modified=False)
```

## Example 5: Approval Workflow Logic

**Use Case**: Implement approval logic based on amount thresholds.

```python
# Configuration:
#   Type: Document Event
#   DocType Event: Before Save
#   Reference DocType: Purchase Order

# ═══════════════════════════════════════════════════════════
# APPROVAL WORKFLOW LOGIC - Before Save
# ═══════════════════════════════════════════════════════════

# Define approval matrix
APPROVAL_MATRIX = [
    {"min": 0, "max": 10000, "role": None},           # Auto-approve
    {"min": 10000, "max": 50000, "role": "Purchase Manager"},
    {"min": 50000, "max": 100000, "role": "Finance Manager"},
    {"min": 100000, "max": float('inf'), "role": "Director"}
]

# Determine required approval
required_role = None
for level in APPROVAL_MATRIX:
    if level["min"] <= doc.grand_total < level["max"]:
        required_role = level["role"]
        break

# Set approval requirements
if required_role is None:
    # Auto-approve small orders
    doc.approval_status = "Approved"
    doc.approved_by = frappe.session.user
    doc.approval_date = frappe.utils.today()
else:
    # Check if already approved
    if doc.approval_status == "Approved":
        # Validate approver has correct role
        if doc.approved_by:
            approver_roles = frappe.get_roles(doc.approved_by)
            if required_role not in approver_roles:
                frappe.throw(
                    f"Order requires approval from {required_role}. "
                    f"Current approver {doc.approved_by} does not have this role."
                )
    else:
        # Set pending approval
        doc.approval_status = "Pending"
        doc.required_approver_role = required_role

# Prevent submission without approval
if doc.docstatus == 1 and doc.approval_status != "Approved":
    frappe.throw("Order must be approved before submission")
```

## Example 6: Complete REST API with CRUD

**Use Case**: Full CRUD API for custom object.

```python
# Configuration:
#   Type: API
#   API Method: manage_bookmark
#   Allow Guest: No

# ═══════════════════════════════════════════════════════════
# BOOKMARK CRUD API
# Endpoint: /api/method/manage_bookmark
# ═══════════════════════════════════════════════════════════

action = frappe.form_dict.get("action")
user = frappe.session.user

if action == "list":
    # GET all bookmarks for current user
    bookmarks = frappe.get_all("Bookmark",
        filters={"owner": user},
        fields=["name", "title", "url", "category", "creation"],
        order_by="creation desc",
        limit=50
    )
    frappe.response["message"] = {"bookmarks": bookmarks}

elif action == "get":
    # GET single bookmark
    bookmark_id = frappe.form_dict.get("id")
    if not bookmark_id:
        frappe.throw("Bookmark ID required")
    
    bookmark = frappe.get_doc("Bookmark", bookmark_id)
    if bookmark.owner != user:
        frappe.throw("Access denied", frappe.PermissionError)
    
    frappe.response["message"] = bookmark.as_dict()

elif action == "create":
    # CREATE new bookmark
    title = frappe.form_dict.get("title")
    url = frappe.form_dict.get("url")
    category = frappe.form_dict.get("category", "General")
    
    if not title or not url:
        frappe.throw("Title and URL are required")
    
    bookmark = frappe.get_doc({
        "doctype": "Bookmark",
        "title": title,
        "url": url,
        "category": category,
        "owner": user
    })
    bookmark.insert()
    
    frappe.response["message"] = {
        "success": True,
        "id": bookmark.name
    }

elif action == "update":
    # UPDATE existing bookmark
    bookmark_id = frappe.form_dict.get("id")
    if not bookmark_id:
        frappe.throw("Bookmark ID required")
    
    bookmark = frappe.get_doc("Bookmark", bookmark_id)
    if bookmark.owner != user:
        frappe.throw("Access denied", frappe.PermissionError)
    
    # Update fields
    if frappe.form_dict.get("title"):
        bookmark.title = frappe.form_dict.get("title")
    if frappe.form_dict.get("url"):
        bookmark.url = frappe.form_dict.get("url")
    if frappe.form_dict.get("category"):
        bookmark.category = frappe.form_dict.get("category")
    
    bookmark.save()
    frappe.response["message"] = {"success": True}

elif action == "delete":
    # DELETE bookmark
    bookmark_id = frappe.form_dict.get("id")
    if not bookmark_id:
        frappe.throw("Bookmark ID required")
    
    bookmark = frappe.get_doc("Bookmark", bookmark_id)
    if bookmark.owner != user:
        frappe.throw("Access denied", frappe.PermissionError)
    
    bookmark.delete()
    frappe.response["message"] = {"success": True}

else:
    frappe.throw("Invalid action. Use: list, get, create, update, delete")
```

## Example 7: Comprehensive Scheduler Job

**Use Case**: Daily customer health scoring.

```python
# Configuration:
#   Type: Scheduler Event
#   Event Frequency: Cron
#   Cron Format: 0 4 * * *  (daily at 4:00 AM)

# ═══════════════════════════════════════════════════════════
# DAILY CUSTOMER HEALTH SCORING
# ═══════════════════════════════════════════════════════════

BATCH_SIZE = 50
processed = 0
errors = 0

# Get all active customers
customers = frappe.get_all("Customer",
    filters={"disabled": 0},
    pluck="name"
)

for i in range(0, len(customers), BATCH_SIZE):
    batch = customers[i:i + BATCH_SIZE]
    
    for customer in batch:
        try:
            # Calculate metrics
            today = frappe.utils.today()
            year_ago = frappe.utils.add_days(today, -365)
            
            # Orders in last year
            orders = frappe.db.sql("""
                SELECT COUNT(*) as count, COALESCE(SUM(grand_total), 0) as total
                FROM `tabSales Order`
                WHERE customer = %(customer)s
                AND transaction_date >= %(year_ago)s
                AND docstatus = 1
            """, {"customer": customer, "year_ago": year_ago}, as_dict=True)[0]
            
            # Outstanding amount
            outstanding = frappe.db.get_value("Sales Invoice",
                filters={"customer": customer, "docstatus": 1, "status": "Unpaid"},
                fieldname="sum(outstanding_amount)"
            ) or 0
            
            # Last order date
            last_order = frappe.db.get_value("Sales Order",
                filters={"customer": customer, "docstatus": 1},
                fieldname="max(transaction_date)"
            )
            
            # Calculate score (0-100)
            score = 50  # Base score
            
            # Order frequency bonus
            if orders.count >= 12:
                score += 20
            elif orders.count >= 6:
                score += 10
            elif orders.count >= 3:
                score += 5
            
            # Revenue bonus
            if orders.total >= 100000:
                score += 15
            elif orders.total >= 50000:
                score += 10
            elif orders.total >= 10000:
                score += 5
            
            # Outstanding penalty
            if outstanding > 50000:
                score -= 20
            elif outstanding > 10000:
                score -= 10
            
            # Recency bonus/penalty
            if last_order:
                days_since = frappe.utils.date_diff(today, last_order)
                if days_since <= 30:
                    score += 15
                elif days_since <= 90:
                    score += 5
                elif days_since > 180:
                    score -= 10
            
            # Clamp score
            score = max(0, min(100, score))
            
            # Update customer
            frappe.db.set_value("Customer", customer, {
                "health_score": score,
                "last_score_date": today,
                "orders_last_year": orders.count,
                "revenue_last_year": orders.total
            }, update_modified=False)
            
            processed += 1
            
        except Exception:
            frappe.log_error(
                f"Failed to score customer {customer}",
                "Customer Health Scoring Error"
            )
            errors += 1
    
    # Commit each batch
    frappe.db.commit()

# Log completion
frappe.log_error(
    f"Customer Health Scoring Complete\n"
    f"Processed: {processed}\n"
    f"Errors: {errors}",
    "Customer Health Scoring"
)
```

## Example 8: Dynamic Permission with Date Range

**Use Case**: Users can only see documents from current month.

```python
# Configuration:
#   Type: Permission Query
#   Reference DocType: Expense Claim

# ═══════════════════════════════════════════════════════════
# EXPENSE CLAIM PERMISSION - Current Month Only
# ═══════════════════════════════════════════════════════════

user_roles = frappe.get_roles(user)

if "System Manager" in user_roles or "HR Manager" in user_roles:
    # Full access for managers
    conditions = ""

elif "Expense Approver" in user_roles:
    # Approvers see their team's claims
    team_members = frappe.get_all("Employee",
        filters={"reports_to": frappe.db.get_value("Employee", {"user_id": user}, "name")},
        pluck="user_id"
    )
    team_members.append(user)  # Include self
    
    user_list = ", ".join(frappe.db.escape(u) for u in team_members if u)
    conditions = f"`tabExpense Claim`.owner IN ({user_list})"

else:
    # Regular users: only own claims from current month
    month_start = frappe.utils.get_first_day(frappe.utils.today())
    
    conditions = (
        f"`tabExpense Claim`.owner = {frappe.db.escape(user)} "
        f"AND `tabExpense Claim`.posting_date >= {frappe.db.escape(month_start)}"
    )
```

## Example 9: Linked Document Prevention

**Use Case**: Prevent deletion of item with linked transactions.

```python
# Configuration:
#   Type: Document Event
#   DocType Event: Before Delete
#   Reference DocType: Item

# ═══════════════════════════════════════════════════════════
# ITEM DELETION CHECK - Before Delete
# ═══════════════════════════════════════════════════════════

linked = []

# Check Sales Orders
so_count = frappe.db.count("Sales Order Item", {"item_code": doc.name})
if so_count:
    linked.append(f"Sales Orders: {so_count} line(s)")

# Check Purchase Orders
po_count = frappe.db.count("Purchase Order Item", {"item_code": doc.name})
if po_count:
    linked.append(f"Purchase Orders: {po_count} line(s)")

# Check Stock Entries
se_count = frappe.db.count("Stock Entry Detail", {"item_code": doc.name})
if se_count:
    linked.append(f"Stock Entries: {se_count} line(s)")

# Check Invoices
si_count = frappe.db.count("Sales Invoice Item", {"item_code": doc.name})
if si_count:
    linked.append(f"Sales Invoices: {si_count} line(s)")

pi_count = frappe.db.count("Purchase Invoice Item", {"item_code": doc.name})
if pi_count:
    linked.append(f"Purchase Invoices: {pi_count} line(s)")

# Check current stock
stock = frappe.db.get_value("Bin",
    filters={"item_code": doc.name},
    fieldname="sum(actual_qty)"
) or 0

if stock != 0:
    linked.append(f"Current Stock: {stock}")

# Prevent deletion if linked
if linked:
    frappe.throw(
        f"Cannot delete Item {doc.name}. Found linked documents:<br>" +
        "<br>".join(linked),
        title="Deletion Blocked"
    )
```

## Example 10: Audit Trail Logger

**Use Case**: Log all changes to sensitive documents.

```python
# Configuration:
#   Type: Document Event
#   DocType Event: After Save
#   Reference DocType: Employee

# ═══════════════════════════════════════════════════════════
# EMPLOYEE AUDIT TRAIL - After Save
# ═══════════════════════════════════════════════════════════

# Fields to track
TRACKED_FIELDS = [
    "employee_name", "department", "designation",
    "status", "employment_type", "branch",
    "reports_to", "leave_approver"
]

# Get previous values (if exists)
if not doc.is_new():
    # Fetch old values
    old_doc = frappe.db.get_value("Employee", doc.name, TRACKED_FIELDS, as_dict=True)
    
    changes = []
    for field in TRACKED_FIELDS:
        old_val = old_doc.get(field) if old_doc else None
        new_val = doc.get(field)
        
        if old_val != new_val:
            changes.append({
                "field": field,
                "old_value": str(old_val) if old_val else "",
                "new_value": str(new_val) if new_val else ""
            })
    
    if changes:
        # Create audit log
        frappe.get_doc({
            "doctype": "Audit Log",
            "reference_doctype": "Employee",
            "reference_name": doc.name,
            "action": "Update",
            "changed_by": frappe.session.user,
            "changed_on": frappe.utils.now(),
            "changes": frappe.as_json(changes)
        }).insert(ignore_permissions=True)
else:
    # New document
    frappe.get_doc({
        "doctype": "Audit Log",
        "reference_doctype": "Employee",
        "reference_name": doc.name,
        "action": "Create",
        "changed_by": frappe.session.user,
        "changed_on": frappe.utils.now(),
        "changes": frappe.as_json({"action": "New employee created"})
    }).insert(ignore_permissions=True)
```
