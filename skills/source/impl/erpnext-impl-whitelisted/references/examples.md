# Complete Working Examples

Production-ready examples for Whitelisted Methods.

---

## Example 1: Complete API Module

```python
# myapp/api.py
"""
Main API module for MyApp.
All endpoints are authenticated unless marked allow_guest.
"""
import frappe
from frappe import _
from frappe.utils import nowdate, add_days, flt

# =============================================================================
# CUSTOMER APIs
# =============================================================================

@frappe.whitelist()
def get_customer_summary(customer):
    """
    Get customer summary including balance and recent orders.
    
    Args:
        customer: Customer ID
    
    Returns:
        dict: Customer summary data
    """
    if not frappe.has_permission("Customer", "read", customer):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Get customer details
    cust = frappe.get_doc("Customer", customer)
    
    # Get outstanding balance
    balance = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0) as balance
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
    """, customer)[0][0]
    
    # Get recent orders
    recent_orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer, "docstatus": 1},
        fields=["name", "transaction_date", "grand_total", "status"],
        order_by="transaction_date desc",
        limit=5
    )
    
    return {
        "customer": customer,
        "customer_name": cust.customer_name,
        "customer_group": cust.customer_group,
        "territory": cust.territory,
        "outstanding_balance": flt(balance, 2),
        "credit_limit": flt(cust.credit_limit, 2),
        "recent_orders": recent_orders
    }

@frappe.whitelist()
def search_customers(query, limit=10):
    """
    Search customers by name or ID.
    
    Args:
        query: Search term
        limit: Max results (default 10)
    
    Returns:
        list: Matching customers
    """
    if not query or len(query) < 2:
        return []
    
    limit = min(50, int(limit))
    
    return frappe.get_all(
        "Customer",
        filters=[
            ["Customer", "disabled", "=", 0],
            ["Customer", "customer_name", "like", f"%{query}%"]
        ],
        or_filters=[
            ["Customer", "name", "like", f"%{query}%"]
        ],
        fields=["name", "customer_name", "customer_group", "territory"],
        limit=limit
    )

# =============================================================================
# ORDER APIs
# =============================================================================

@frappe.whitelist()
def create_sales_order(customer, items, delivery_date=None):
    """
    Create a new sales order.
    
    Args:
        customer: Customer ID
        items: List of items [{item_code, qty, rate}]
        delivery_date: Optional delivery date
    
    Returns:
        dict: Created order details
    """
    # Permission check
    if not frappe.has_permission("Sales Order", "create"):
        frappe.throw(_("Not permitted to create Sales Orders"), frappe.PermissionError)
    
    # Validate customer
    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer not found"), frappe.DoesNotExistError)
    
    # Validate items
    if not items or not isinstance(items, list):
        frappe.throw(_("Items are required"), frappe.ValidationError)
    
    # Parse items if string
    if isinstance(items, str):
        items = frappe.parse_json(items)
    
    # Create order
    order = frappe.new_doc("Sales Order")
    order.customer = customer
    order.delivery_date = delivery_date or add_days(nowdate(), 7)
    
    for item in items:
        order.append("items", {
            "item_code": item.get("item_code"),
            "qty": flt(item.get("qty", 1)),
            "rate": flt(item.get("rate")) if item.get("rate") else None
        })
    
    order.insert()
    
    return {
        "success": True,
        "order": order.name,
        "customer": customer,
        "total": flt(order.grand_total, 2)
    }

@frappe.whitelist()
def get_order_status(order_id):
    """Get order status and tracking info."""
    if not frappe.has_permission("Sales Order", "read", order_id):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    order = frappe.get_doc("Sales Order", order_id)
    
    # Get delivery notes
    deliveries = frappe.get_all(
        "Delivery Note Item",
        filters={"against_sales_order": order_id, "docstatus": 1},
        fields=["parent", "qty"],
        group_by="parent"
    )
    
    return {
        "order": order_id,
        "status": order.status,
        "delivery_status": order.delivery_status,
        "billing_status": order.billing_status,
        "deliveries": [d.parent for d in deliveries]
    }

# =============================================================================
# PUBLIC APIs (Guest Access)
# =============================================================================

@frappe.whitelist(allow_guest=True, methods=["GET"])
def track_order(tracking_id):
    """
    Public order tracking - no login required.
    Limited information exposed.
    """
    # Validate tracking ID format
    if not tracking_id or not tracking_id.startswith("SO-"):
        frappe.local.response["http_status_code"] = 400
        return {"error": "Invalid tracking ID"}
    
    # Check if order exists
    if not frappe.db.exists("Sales Order", tracking_id):
        frappe.local.response["http_status_code"] = 404
        return {"error": "Order not found"}
    
    # Get limited public info only
    order = frappe.db.get_value(
        "Sales Order",
        tracking_id,
        ["status", "delivery_status", "delivery_date"],
        as_dict=True
    )
    
    return {
        "tracking_id": tracking_id,
        "status": order.status,
        "delivery_status": order.delivery_status,
        "expected_delivery": str(order.delivery_date) if order.delivery_date else None
    }

@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_inquiry(name, email, phone=None, message=None):
    """Public inquiry form submission."""
    # Strict validation for guest API
    if not name or not email:
        frappe.throw(_("Name and email are required"))
    
    from frappe.utils import validate_email_address, strip_html
    
    if not validate_email_address(email):
        frappe.throw(_("Invalid email address"))
    
    # Sanitize
    name = strip_html(name)[:100]
    email = email.strip().lower()[:200]
    phone = strip_html(phone)[:20] if phone else None
    message = strip_html(message)[:2000] if message else None
    
    # Create lead
    lead = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": name,
        "email_id": email,
        "phone": phone,
        "notes": message,
        "source": "Website"
    })
    lead.insert(ignore_permissions=True)
    
    return {"success": True, "message": _("Thank you for your inquiry")}

# =============================================================================
# ADMIN APIs
# =============================================================================

@frappe.whitelist()
def get_dashboard_stats():
    """Dashboard statistics - managers only."""
    frappe.only_for(["System Manager", "Sales Manager"])
    
    today = nowdate()
    month_start = frappe.utils.get_first_day(today)
    
    return {
        "today": {
            "orders": frappe.db.count("Sales Order", {
                "transaction_date": today, "docstatus": 1
            }),
            "revenue": get_revenue(today, today)
        },
        "month": {
            "orders": frappe.db.count("Sales Order", {
                "transaction_date": [">=", month_start], "docstatus": 1
            }),
            "revenue": get_revenue(month_start, today)
        },
        "pending_orders": frappe.db.count("Sales Order", {
            "status": ["in", ["To Deliver", "To Deliver and Bill"]]
        })
    }

def get_revenue(from_date, to_date):
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0)
        FROM `tabSales Invoice`
        WHERE posting_date BETWEEN %s AND %s
        AND docstatus = 1
    """, (from_date, to_date))
    return flt(result[0][0], 2)
```

---

## Example 2: Controller Methods

```python
# myapp/doctype/project/project.py
import frappe
from frappe import _
from frappe.model.document import Document

class Project(Document):
    @frappe.whitelist()
    def get_task_summary(self):
        """Get summary of project tasks."""
        tasks = frappe.get_all(
            "Task",
            filters={"project": self.name},
            fields=["status", "count(*) as count"],
            group_by="status"
        )
        
        summary = {t.status: t.count for t in tasks}
        
        return {
            "total": sum(summary.values()),
            "open": summary.get("Open", 0),
            "working": summary.get("Working", 0),
            "completed": summary.get("Completed", 0),
            "cancelled": summary.get("Cancelled", 0)
        }
    
    @frappe.whitelist()
    def add_team_member(self, user, role="Team Member"):
        """Add a user to the project team."""
        # Validate user exists
        if not frappe.db.exists("User", user):
            frappe.throw(_("User not found"), frappe.DoesNotExistError)
        
        # Check not already added
        existing = [m.user for m in self.users]
        if user in existing:
            frappe.throw(_("User already in team"))
        
        # Add member
        self.append("users", {
            "user": user,
            "role": role
        })
        self.save()
        
        # Send notification
        frappe.sendmail(
            recipients=[user],
            subject=f"Added to Project: {self.project_name}",
            message=f"You have been added to project {self.project_name} as {role}."
        )
        
        return {"success": True, "message": _("Team member added")}
    
    @frappe.whitelist()
    def complete_project(self, completion_notes=None):
        """Mark project as completed."""
        if self.status == "Completed":
            frappe.throw(_("Project already completed"))
        
        # Check all tasks completed
        open_tasks = frappe.db.count("Task", {
            "project": self.name,
            "status": ["not in", ["Completed", "Cancelled"]]
        })
        
        if open_tasks > 0:
            frappe.throw(
                _("{0} tasks still open. Complete or cancel them first.").format(open_tasks)
            )
        
        self.status = "Completed"
        self.completion_date = frappe.utils.nowdate()
        self.completion_notes = completion_notes
        self.save()
        
        return {
            "success": True,
            "message": _("Project completed"),
            "completion_date": str(self.completion_date)
        }
```

```javascript
// myapp/doctype/project/project.js
frappe.ui.form.on('Project', {
    refresh: function(frm) {
        // Task summary button
        frm.add_custom_button(__('Task Summary'), function() {
            frm.call('get_task_summary').then(r => {
                const s = r.message;
                frappe.msgprint(`
                    <h4>Task Summary</h4>
                    <table class="table table-bordered">
                        <tr><td>Total</td><td>${s.total}</td></tr>
                        <tr><td>Open</td><td>${s.open}</td></tr>
                        <tr><td>Working</td><td>${s.working}</td></tr>
                        <tr><td>Completed</td><td>${s.completed}</td></tr>
                    </table>
                `);
            });
        });
        
        // Add team member
        frm.add_custom_button(__('Add Team Member'), function() {
            frappe.prompt([
                {
                    fieldname: 'user',
                    fieldtype: 'Link',
                    options: 'User',
                    label: __('User'),
                    reqd: 1
                },
                {
                    fieldname: 'role',
                    fieldtype: 'Select',
                    options: 'Team Member\nProject Manager\nConsultant',
                    label: __('Role'),
                    default: 'Team Member'
                }
            ], function(values) {
                frm.call('add_team_member', values).then(r => {
                    if (r.message?.success) {
                        frappe.msgprint(r.message.message);
                        frm.reload_doc();
                    }
                });
            }, __('Add Team Member'));
        }, __('Team'));
        
        // Complete project button (only if not completed)
        if (frm.doc.status !== 'Completed') {
            frm.add_custom_button(__('Complete Project'), function() {
                frappe.prompt({
                    fieldname: 'notes',
                    fieldtype: 'Text',
                    label: __('Completion Notes')
                }, function(values) {
                    frm.call('complete_project', {
                        completion_notes: values.notes
                    }).then(r => {
                        if (r.message?.success) {
                            frappe.msgprint(r.message.message);
                            frm.reload_doc();
                        }
                    });
                }, __('Complete Project'));
            }).addClass('btn-primary');
        }
    }
});
```

---

## Example 3: Robust Error Handling

```python
# myapp/api/robust.py
import frappe
from frappe import _

@frappe.whitelist()
def process_payment(invoice, amount, payment_method):
    """
    Process payment with comprehensive error handling.
    """
    try:
        # Input validation
        if not invoice:
            raise frappe.ValidationError(_("Invoice is required"))
        
        amount = validate_amount(amount)
        payment_method = validate_payment_method(payment_method)
        
        # Permission check
        if not frappe.has_permission("Sales Invoice", "write", invoice):
            raise frappe.PermissionError(_("Not permitted to process payment"))
        
        # Get invoice
        inv = frappe.get_doc("Sales Invoice", invoice)
        
        # Business validation
        if inv.docstatus != 1:
            raise frappe.ValidationError(_("Invoice must be submitted"))
        
        if amount > inv.outstanding_amount:
            raise frappe.ValidationError(
                _("Amount {0} exceeds outstanding {1}").format(
                    amount, inv.outstanding_amount
                )
            )
        
        # Process payment
        payment = create_payment_entry(inv, amount, payment_method)
        payment.submit()
        
        return {
            "success": True,
            "payment": payment.name,
            "amount": amount,
            "remaining": inv.outstanding_amount - amount
        }
        
    except frappe.ValidationError as e:
        # Known validation error - return 417
        raise
        
    except frappe.PermissionError as e:
        # Permission denied - return 403
        raise
        
    except frappe.DoesNotExistError as e:
        # Not found - return 404
        frappe.throw(_("Invoice not found"), frappe.DoesNotExistError)
        
    except PaymentGatewayError as e:
        # External service error
        frappe.log_error(str(e), "Payment Gateway Error")
        frappe.throw(_("Payment processing failed. Please try again."))
        
    except Exception as e:
        # Unexpected error - log and return generic message
        frappe.log_error(frappe.get_traceback(), "Payment Processing Error")
        frappe.local.response["http_status_code"] = 500
        return {
            "success": False,
            "error": _("An unexpected error occurred. Please try again.")
        }

def validate_amount(amount):
    """Validate and convert amount."""
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        raise frappe.ValidationError(_("Invalid amount"))
    
    if amount <= 0:
        raise frappe.ValidationError(_("Amount must be positive"))
    
    return amount

def validate_payment_method(method):
    """Validate payment method."""
    valid_methods = ["Cash", "Card", "Bank Transfer", "Check"]
    if method not in valid_methods:
        raise frappe.ValidationError(
            _("Invalid payment method. Must be one of: {0}").format(
                ", ".join(valid_methods)
            )
        )
    return method

def create_payment_entry(invoice, amount, method):
    """Create payment entry document."""
    return frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": "Receive",
        "party_type": "Customer",
        "party": invoice.customer,
        "paid_amount": amount,
        "received_amount": amount,
        "reference_no": invoice.name,
        "mode_of_payment": method,
        "references": [{
            "reference_doctype": "Sales Invoice",
            "reference_name": invoice.name,
            "allocated_amount": amount
        }]
    }).insert()

class PaymentGatewayError(Exception):
    """Custom exception for payment gateway errors."""
    pass
```

---

## Example 4: Rate-Limited Public API (v15+)

```python
# myapp/api/public_v15.py
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

@frappe.whitelist(allow_guest=True, methods=["GET"])
@rate_limit(limit=30, seconds=60)  # 30 requests per minute
def get_product_info(product_id):
    """
    Public product information - rate limited.
    """
    if not product_id:
        frappe.local.response["http_status_code"] = 400
        return {"error": "Product ID required"}
    
    # Get only public fields
    product = frappe.db.get_value(
        "Item",
        product_id,
        ["item_name", "description", "standard_rate", "image"],
        as_dict=True
    )
    
    if not product:
        frappe.local.response["http_status_code"] = 404
        return {"error": "Product not found"}
    
    return {
        "id": product_id,
        "name": product.item_name,
        "description": product.description,
        "price": product.standard_rate,
        "image": product.image
    }

@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=60)  # 5 submissions per minute
def submit_review(product_id, rating, comment=None, name=None, email=None):
    """
    Submit product review - stricter rate limit.
    """
    from frappe.utils import strip_html, validate_email_address
    
    # Validate rating
    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            raise ValueError
    except (ValueError, TypeError):
        frappe.throw(_("Rating must be 1-5"))
    
    # Validate product exists
    if not frappe.db.exists("Item", product_id):
        frappe.throw(_("Product not found"), frappe.DoesNotExistError)
    
    # Sanitize inputs
    comment = strip_html(comment)[:1000] if comment else None
    name = strip_html(name)[:100] if name else "Anonymous"
    
    if email and not validate_email_address(email):
        frappe.throw(_("Invalid email"))
    
    # Create review
    review = frappe.get_doc({
        "doctype": "Product Review",
        "item": product_id,
        "rating": rating,
        "comment": comment,
        "reviewer_name": name,
        "reviewer_email": email
    })
    review.insert(ignore_permissions=True)
    
    return {"success": True, "message": _("Thank you for your review")}
```

---

## Example 5: Batch Operations API

```python
# myapp/api/batch.py
import frappe
from frappe import _

@frappe.whitelist()
def bulk_update_status(doctype, names, status):
    """
    Update status for multiple documents.
    
    Args:
        doctype: Document type
        names: List of document names (or JSON string)
        status: New status value
    """
    frappe.only_for(["System Manager", "Stock Manager"])
    
    # Parse names if JSON string
    if isinstance(names, str):
        names = frappe.parse_json(names)
    
    if not names:
        frappe.throw(_("No documents specified"))
    
    if not isinstance(names, list):
        frappe.throw(_("Names must be a list"))
    
    # Limit batch size
    if len(names) > 100:
        frappe.throw(_("Maximum 100 documents per batch"))
    
    # Process updates
    results = {"success": [], "failed": []}
    
    for name in names:
        try:
            if frappe.has_permission(doctype, "write", name):
                frappe.db.set_value(doctype, name, "status", status)
                results["success"].append(name)
            else:
                results["failed"].append({
                    "name": name,
                    "error": "Permission denied"
                })
        except Exception as e:
            results["failed"].append({
                "name": name,
                "error": str(e)
            })
    
    frappe.db.commit()
    
    return {
        "total": len(names),
        "updated": len(results["success"]),
        "failed": len(results["failed"]),
        "details": results
    }

@frappe.whitelist()
def bulk_delete(doctype, names, force=False):
    """
    Delete multiple documents.
    """
    frappe.only_for("System Manager")
    
    if isinstance(names, str):
        names = frappe.parse_json(names)
    
    if len(names) > 50:
        frappe.throw(_("Maximum 50 documents per batch"))
    
    # Confirm destructive action
    if not force:
        frappe.throw(_("Set force=True to confirm deletion"))
    
    results = {"deleted": [], "failed": []}
    
    for name in names:
        try:
            doc = frappe.get_doc(doctype, name)
            doc.delete()
            results["deleted"].append(name)
        except Exception as e:
            results["failed"].append({"name": name, "error": str(e)})
    
    return results
```
