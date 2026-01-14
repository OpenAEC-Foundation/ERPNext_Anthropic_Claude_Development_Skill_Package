# Examples Reference

Complete werkende voorbeelden van Whitelisted Methods.

## Inhoudsopgave

1. [CRUD API](#crud-api)
2. [Public API](#public-api)
3. [Dashboard API](#dashboard-api)
4. [File Upload API](#file-upload-api)
5. [Batch Processing API](#batch-processing-api)
6. [External Integration API](#external-integration-api)
7. [Report API](#report-api)
8. [Controller Method Voorbeeld](#controller-method-voorbeeld)

---

## CRUD API

Complete Create-Read-Update-Delete API voor een DocType.

### api.py

```python
# myapp/api.py
import frappe
from frappe import _

# CREATE
@frappe.whitelist(methods=["POST"])
def create_task(subject, description=None, assigned_to=None):
    """
    Create a new Task.
    
    Args:
        subject: Task subject (required)
        description: Task description (optional)
        assigned_to: User to assign to (optional)
    
    Returns:
        dict: Created task details
    """
    if not frappe.has_permission("ToDo", "create"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    if not subject:
        frappe.throw(_("Subject is required"), frappe.ValidationError)
    
    doc = frappe.get_doc({
        "doctype": "ToDo",
        "description": subject,
        "allocated_to": assigned_to or frappe.session.user,
        "reference_type": None,
        "reference_name": None
    })
    
    if description:
        doc.description = f"{subject}\n\n{description}"
    
    doc.insert()
    
    return {
        "success": True,
        "name": doc.name,
        "status": doc.status
    }


# READ (single)
@frappe.whitelist(methods=["GET"])
def get_task(name):
    """
    Get a specific task by name.
    """
    if not frappe.has_permission("ToDo", "read", name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    doc = frappe.get_doc("ToDo", name)
    return {
        "name": doc.name,
        "description": doc.description,
        "status": doc.status,
        "allocated_to": doc.allocated_to,
        "date": doc.date
    }


# READ (list)
@frappe.whitelist(methods=["GET"])
def get_tasks(status=None, limit=20, offset=0):
    """
    Get list of tasks with optional filtering.
    """
    if not frappe.has_permission("ToDo", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    filters = {"allocated_to": frappe.session.user}
    if status:
        filters["status"] = status
    
    tasks = frappe.get_all(
        "ToDo",
        filters=filters,
        fields=["name", "description", "status", "date"],
        limit_page_length=int(limit),
        limit_start=int(offset),
        order_by="modified desc"
    )
    
    total = frappe.db.count("ToDo", filters)
    
    return {
        "data": tasks,
        "total": total,
        "limit": int(limit),
        "offset": int(offset)
    }


# UPDATE
@frappe.whitelist(methods=["POST"])
def update_task(name, status=None, description=None):
    """
    Update an existing task.
    """
    if not frappe.has_permission("ToDo", "write", name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    doc = frappe.get_doc("ToDo", name)
    
    if status:
        doc.status = status
    if description:
        doc.description = description
    
    doc.save()
    
    return {
        "success": True,
        "name": doc.name,
        "status": doc.status
    }


# DELETE
@frappe.whitelist(methods=["POST"])
def delete_task(name):
    """
    Delete a task.
    """
    if not frappe.has_permission("ToDo", "delete", name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    frappe.delete_doc("ToDo", name)
    
    return {"success": True, "deleted": name}
```

---

## Public API

API toegankelijk zonder login (voor websites, formulieren).

```python
# myapp/public_api.py
import frappe
from frappe import _
import re

@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_contact_form(name, email, phone=None, message=None):
    """
    Public contact form submission.
    Extra validatie vereist omdat guests kunnen aanroepen.
    """
    # Valideer verplichte velden
    if not name or not email:
        frappe.throw(_("Name and email are required"), frappe.ValidationError)
    
    # Valideer email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        frappe.throw(_("Invalid email format"), frappe.ValidationError)
    
    # Valideer lengte (spam preventie)
    if len(name) > 100:
        frappe.throw(_("Name too long"), frappe.ValidationError)
    if message and len(message) > 5000:
        frappe.throw(_("Message too long"), frappe.ValidationError)
    
    # Sanitize input
    name = frappe.utils.strip_html(name)
    message = frappe.utils.strip_html(message) if message else ""
    
    # Maak Communication record (ignore_permissions omdat guest)
    doc = frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "communication_medium": "Email",
        "subject": f"Contact Form: {name}",
        "content": f"From: {name}\nEmail: {email}\nPhone: {phone or 'N/A'}\n\n{message}",
        "sender": email,
        "recipients": frappe.db.get_single_value("System Settings", "email_footer_address") or "info@example.com"
    })
    doc.insert(ignore_permissions=True)
    
    # Stuur notificatie (optioneel)
    try:
        frappe.sendmail(
            recipients=[doc.recipients],
            subject=doc.subject,
            message=doc.content
        )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Contact Form Email Failed")
    
    return {"success": True, "message": _("Thank you for contacting us!")}


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_public_items(category=None, search=None, limit=20):
    """
    Get publicly visible items for website.
    Alleen publieke velden retourneren!
    """
    filters = {"show_on_website": 1, "disabled": 0}
    
    if category:
        filters["item_group"] = category
    
    if search:
        # Sanitize search term
        search = frappe.utils.strip_html(search)[:100]
    
    items = frappe.get_all(
        "Item",
        filters=filters,
        or_filters={
            "item_name": ["like", f"%{search}%"],
            "description": ["like", f"%{search}%"]
        } if search else None,
        fields=[
            "name", "item_name", "item_group", 
            "description", "image", "standard_rate"
        ],  # Alleen publieke velden!
        limit_page_length=int(limit),
        order_by="item_name"
    )
    
    return {"items": items, "count": len(items)}
```

---

## Dashboard API

API voor dashboard statistieken.

```python
# myapp/dashboard_api.py
import frappe
from frappe import _
from frappe.utils import nowdate, add_days, getdate

@frappe.whitelist(methods=["GET"])
def get_sales_dashboard():
    """
    Sales dashboard statistics.
    """
    frappe.only_for(["Sales Manager", "System Manager"])
    
    today = nowdate()
    month_start = getdate(today).replace(day=1)
    
    # Totals
    total_orders = frappe.db.count("Sales Order", {
        "docstatus": 1,
        "transaction_date": [">=", month_start]
    })
    
    # Aggregate met SQL voor performance
    revenue = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSales Order`
        WHERE docstatus = 1 AND transaction_date >= %s
    """, [month_start])[0][0]
    
    # Status breakdown
    status_counts = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabSales Order`
        WHERE docstatus = 1 AND transaction_date >= %s
        GROUP BY status
    """, [month_start], as_dict=True)
    
    # Top customers
    top_customers = frappe.db.sql("""
        SELECT customer, SUM(grand_total) as total
        FROM `tabSales Order`
        WHERE docstatus = 1 AND transaction_date >= %s
        GROUP BY customer
        ORDER BY total DESC
        LIMIT 5
    """, [month_start], as_dict=True)
    
    return {
        "period": {
            "start": str(month_start),
            "end": today
        },
        "total_orders": total_orders,
        "revenue": float(revenue),
        "by_status": {row.status: row.count for row in status_counts},
        "top_customers": top_customers
    }


@frappe.whitelist(methods=["GET"])
def get_daily_stats(days=7):
    """
    Daily statistics for chart.
    """
    if not frappe.has_permission("Sales Order", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    days = min(int(days), 90)  # Max 90 dagen
    start_date = add_days(nowdate(), -days)
    
    daily = frappe.db.sql("""
        SELECT 
            DATE(transaction_date) as date,
            COUNT(*) as orders,
            SUM(grand_total) as revenue
        FROM `tabSales Order`
        WHERE docstatus = 1 AND transaction_date >= %s
        GROUP BY DATE(transaction_date)
        ORDER BY date
    """, [start_date], as_dict=True)
    
    return {
        "labels": [str(row.date) for row in daily],
        "datasets": {
            "orders": [row.orders for row in daily],
            "revenue": [float(row.revenue or 0) for row in daily]
        }
    }
```

---

## File Upload API

API voor file uploads en downloads.

```python
# myapp/file_api.py
import frappe
from frappe import _
import base64

@frappe.whitelist(methods=["POST"])
def upload_attachment(doctype, docname, filename, filedata, is_private=True):
    """
    Upload file attachment to a document.
    
    Args:
        doctype: Target DocType
        docname: Target document name
        filename: Original filename
        filedata: Base64 encoded file content
        is_private: Whether file should be private
    """
    # Permission check op target document
    if not frappe.has_permission(doctype, "write", docname):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Valideer bestandstype
    allowed_extensions = ["pdf", "png", "jpg", "jpeg", "doc", "docx", "xls", "xlsx"]
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in allowed_extensions:
        frappe.throw(_("File type not allowed: {0}").format(ext))
    
    # Decode en sla op
    try:
        content = base64.b64decode(filedata)
    except Exception:
        frappe.throw(_("Invalid file data"))
    
    # Max file size (5MB)
    if len(content) > 5 * 1024 * 1024:
        frappe.throw(_("File too large (max 5MB)"))
    
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": filename,
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
        "is_private": int(is_private),
        "content": content
    })
    file_doc.save()
    
    return {
        "success": True,
        "file_name": file_doc.name,
        "file_url": file_doc.file_url
    }


@frappe.whitelist(methods=["GET"])
def download_file(file_name):
    """
    Download a file - returns file content.
    """
    file_doc = frappe.get_doc("File", file_name)
    
    # Check permission via attached document
    if file_doc.attached_to_doctype and file_doc.attached_to_name:
        if not frappe.has_permission(
            file_doc.attached_to_doctype, "read", 
            file_doc.attached_to_name
        ):
            frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Set response voor download
    frappe.response.filename = file_doc.file_name
    frappe.response.filecontent = file_doc.get_content()
    frappe.response.type = "download"
```

---

## Batch Processing API

API voor bulk operaties.

```python
# myapp/batch_api.py
import frappe
from frappe import _

@frappe.whitelist(methods=["POST"])
def batch_update_status(doctype, names, new_status):
    """
    Update status for multiple documents.
    
    Args:
        doctype: DocType name
        names: List of document names (JSON string)
        new_status: New status value
    """
    frappe.only_for("System Manager")
    
    # Parse names als het een string is
    if isinstance(names, str):
        names = frappe.parse_json(names)
    
    if not isinstance(names, list) or not names:
        frappe.throw(_("Names must be a non-empty list"))
    
    # Limiteer batch size
    if len(names) > 100:
        frappe.throw(_("Maximum 100 documents per batch"))
    
    # Valideer DocType
    if doctype not in frappe.get_all("DocType", pluck="name"):
        frappe.throw(_("Invalid DocType"))
    
    # Check permission
    if not frappe.has_permission(doctype, "write"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    results = {"success": [], "failed": []}
    
    for name in names:
        try:
            doc = frappe.get_doc(doctype, name)
            doc.status = new_status
            doc.save()
            results["success"].append(name)
        except Exception as e:
            results["failed"].append({
                "name": name,
                "error": str(e)
            })
    
    return {
        "total": len(names),
        "updated": len(results["success"]),
        "failed": len(results["failed"]),
        "details": results
    }


@frappe.whitelist(methods=["POST"])
def bulk_delete(doctype, names):
    """
    Delete multiple documents.
    """
    frappe.only_for("System Manager")
    
    if isinstance(names, str):
        names = frappe.parse_json(names)
    
    if len(names) > 50:
        frappe.throw(_("Maximum 50 documents per delete operation"))
    
    if not frappe.has_permission(doctype, "delete"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    deleted = []
    errors = []
    
    for name in names:
        try:
            frappe.delete_doc(doctype, name)
            deleted.append(name)
        except Exception as e:
            errors.append({"name": name, "error": str(e)})
    
    return {
        "deleted": len(deleted),
        "failed": len(errors),
        "errors": errors
    }
```

---

## External Integration API

API voor externe service integraties.

```python
# myapp/integration_api.py
import frappe
from frappe import _
import requests

@frappe.whitelist(methods=["POST"])
def sync_with_external(doc_name, external_id=None):
    """
    Sync document with external system.
    """
    frappe.only_for(["System Manager", "Integration Manager"])
    
    doc = frappe.get_doc("Customer", doc_name)
    
    # Haal API credentials op (veilig opgeslagen)
    settings = frappe.get_single("Integration Settings")
    if not settings.api_key:
        frappe.throw(_("Integration not configured"))
    
    try:
        response = requests.post(
            f"{settings.api_url}/customers",
            json={
                "name": doc.customer_name,
                "email": doc.email_id,
                "external_id": external_id
            },
            headers={
                "Authorization": f"Bearer {settings.get_password('api_key')}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Update lokaal document met external ID
        if result.get("id"):
            doc.db_set("external_id", result["id"])
        
        return {
            "success": True,
            "external_id": result.get("id"),
            "synced_at": frappe.utils.now()
        }
        
    except requests.Timeout:
        frappe.log_error(f"Timeout syncing {doc_name}", "External Sync")
        frappe.throw(_("External service timeout"))
        
    except requests.RequestException as e:
        frappe.log_error(f"Error syncing {doc_name}: {str(e)}", "External Sync")
        frappe.throw(_("External service error"))
```

---

## Report API

API voor custom reports.

```python
# myapp/report_api.py
import frappe
from frappe import _

@frappe.whitelist(methods=["GET"])
def get_sales_report(from_date, to_date, customer=None, item_group=None):
    """
    Generate sales report data.
    """
    if not frappe.has_permission("Sales Invoice", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Bouw filters dynamisch
    conditions = ["si.docstatus = 1", "si.posting_date BETWEEN %s AND %s"]
    values = [from_date, to_date]
    
    if customer:
        conditions.append("si.customer = %s")
        values.append(customer)
    
    if item_group:
        conditions.append("i.item_group = %s")
        values.append(item_group)
    
    where_clause = " AND ".join(conditions)
    
    # Parameterized query (veilig!)
    data = frappe.db.sql(f"""
        SELECT 
            si.customer,
            sii.item_code,
            sii.item_name,
            i.item_group,
            SUM(sii.qty) as total_qty,
            SUM(sii.amount) as total_amount
        FROM `tabSales Invoice Item` sii
        INNER JOIN `tabSales Invoice` si ON sii.parent = si.name
        INNER JOIN `tabItem` i ON sii.item_code = i.name
        WHERE {where_clause}
        GROUP BY si.customer, sii.item_code
        ORDER BY total_amount DESC
    """, values, as_dict=True)
    
    # Summary
    totals = frappe.db.sql(f"""
        SELECT 
            COUNT(DISTINCT si.name) as invoice_count,
            SUM(si.grand_total) as total_revenue
        FROM `tabSales Invoice` si
        WHERE {" AND ".join(conditions[:2 if not customer else 3])}
    """, values[:2 if not customer else 3], as_dict=True)[0]
    
    return {
        "filters": {
            "from_date": from_date,
            "to_date": to_date,
            "customer": customer,
            "item_group": item_group
        },
        "summary": {
            "invoice_count": totals.invoice_count,
            "total_revenue": float(totals.total_revenue or 0)
        },
        "data": data
    }
```

---

## Controller Method Voorbeeld

Whitelisted method op DocType controller.

### Server (sales_order.py)

```python
# myapp/doctype/custom_sales_order/custom_sales_order.py
import frappe
from frappe import _
from frappe.model.document import Document

class CustomSalesOrder(Document):
    @frappe.whitelist()
    def calculate_commission(self, rate=None):
        """
        Calculate sales commission for this order.
        Callable via frm.call('calculate_commission')
        """
        if not rate:
            rate = frappe.db.get_value(
                "Sales Person", 
                self.sales_person, 
                "commission_rate"
            ) or 0.05
        
        commission = self.grand_total * float(rate)
        
        return {
            "sales_person": self.sales_person,
            "order_total": self.grand_total,
            "rate": float(rate),
            "commission": commission
        }
    
    @frappe.whitelist()
    def send_confirmation_email(self):
        """
        Send order confirmation to customer.
        """
        if not self.contact_email:
            frappe.throw(_("No customer email found"))
        
        frappe.sendmail(
            recipients=[self.contact_email],
            subject=_("Order Confirmation: {0}").format(self.name),
            template="order_confirmation",
            args={
                "doc": self,
                "items": self.items
            }
        )
        
        return {"sent_to": self.contact_email}
```

### Client (custom_sales_order.js)

```javascript
frappe.ui.form.on('Custom Sales Order', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Calculate Commission'), () => {
                frm.call('calculate_commission', {
                    rate: 0.10  // 10% override
                }).then(r => {
                    if (r.message) {
                        frappe.msgprint({
                            title: __('Commission'),
                            indicator: 'green',
                            message: __('Commission: {0}', [
                                format_currency(r.message.commission)
                            ])
                        });
                    }
                });
            });
            
            frm.add_custom_button(__('Send Confirmation'), () => {
                frm.call({
                    method: 'send_confirmation_email',
                    freeze: true,
                    freeze_message: __('Sending email...')
                }).then(r => {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Email sent to {0}', [r.message.sent_to]),
                            indicator: 'green'
                        });
                    }
                });
            }, __('Actions'));
        }
    }
});
```
