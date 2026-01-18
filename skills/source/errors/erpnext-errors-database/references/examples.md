# Examples - Database Error Handling

Complete working examples of error handling for Frappe/ERPNext database operations.

---

## Example 1: Customer Management with Full Error Handling

```python
# myapp/api/customer.py
import frappe
from frappe import _

@frappe.whitelist()
def get_customer(customer_name):
    """Get customer with error handling."""
    if not customer_name:
        frappe.throw(_("Customer name is required"))
    
    # Check existence first
    if not frappe.db.exists("Customer", customer_name):
        frappe.throw(
            _("Customer '{0}' not found").format(customer_name),
            exc=frappe.DoesNotExistError
        )
    
    # Get customer data
    customer = frappe.db.get_value(
        "Customer",
        customer_name,
        ["name", "customer_name", "customer_type", "credit_limit", "disabled"],
        as_dict=True
    )
    
    if customer.disabled:
        frappe.throw(_("Customer '{0}' is disabled").format(customer.customer_name))
    
    return customer


@frappe.whitelist()
def create_customer(customer_name, customer_type="Company", territory=None):
    """Create customer with duplicate handling."""
    if not customer_name:
        frappe.throw(_("Customer name is required"))
    
    # Check for existing
    existing = frappe.db.exists("Customer", {"customer_name": customer_name})
    if existing:
        frappe.throw(
            _("Customer '{0}' already exists").format(customer_name),
            exc=frappe.DuplicateEntryError
        )
    
    try:
        doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": customer_type,
            "territory": territory or frappe.db.get_single_value("Selling Settings", "territory")
        })
        doc.insert()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Customer created successfully")
        }
        
    except frappe.DuplicateEntryError:
        # Race condition - check again
        existing = frappe.db.get_value("Customer", {"customer_name": customer_name}, "name")
        frappe.throw(_("Customer '{0}' was just created by another user").format(customer_name))
        
    except frappe.ValidationError as e:
        frappe.throw(str(e))


@frappe.whitelist()
def update_customer(customer_name, updates):
    """Update customer with concurrent edit handling."""
    if not customer_name:
        frappe.throw(_("Customer name is required"))
    
    if not frappe.db.exists("Customer", customer_name):
        frappe.throw(
            _("Customer '{0}' not found").format(customer_name),
            exc=frappe.DoesNotExistError
        )
    
    try:
        doc = frappe.get_doc("Customer", customer_name)
        
        # Parse updates if string
        if isinstance(updates, str):
            updates = frappe.parse_json(updates)
        
        doc.update(updates)
        doc.save()
        
        return {
            "success": True,
            "name": doc.name,
            "message": _("Customer updated successfully")
        }
        
    except frappe.TimestampMismatchError:
        frappe.throw(
            _("Customer was modified by another user. Please refresh and try again."),
            title=_("Concurrent Edit")
        )
    except frappe.ValidationError as e:
        frappe.throw(str(e))


@frappe.whitelist()
def delete_customer(customer_name):
    """Delete customer with link handling."""
    if not customer_name:
        frappe.throw(_("Customer name is required"))
    
    if not frappe.db.exists("Customer", customer_name):
        return {"success": True, "message": _("Customer already deleted")}
    
    # Check for linked documents first
    linked_invoices = frappe.db.count("Sales Invoice", {"customer": customer_name})
    linked_orders = frappe.db.count("Sales Order", {"customer": customer_name})
    
    if linked_invoices or linked_orders:
        frappe.throw(
            _("Cannot delete customer. Linked documents exist:<br>"
              "• Sales Invoices: {0}<br>"
              "• Sales Orders: {1}").format(linked_invoices, linked_orders),
            title=_("Delete Error"),
            exc=frappe.LinkExistsError
        )
    
    try:
        frappe.delete_doc("Customer", customer_name)
        return {
            "success": True,
            "message": _("Customer deleted successfully")
        }
        
    except frappe.LinkExistsError:
        frappe.throw(_("Cannot delete customer. It is linked to other documents."))
```

---

## Example 2: Data Import with Error Tracking

```python
# myapp/imports/item_import.py
import frappe
from frappe import _

@frappe.whitelist()
def import_items(items_json):
    """
    Import items from JSON with comprehensive error handling.
    Returns detailed results.
    """
    if not items_json:
        frappe.throw(_("No items provided"))
    
    items = frappe.parse_json(items_json)
    if not items:
        frappe.throw(_("Invalid items data"))
    
    results = {
        "total": len(items),
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0,
        "details": []
    }
    
    for idx, item_data in enumerate(items, 1):
        item_code = item_data.get("item_code")
        
        if not item_code:
            results["failed"] += 1
            results["details"].append({
                "row": idx,
                "status": "failed",
                "error": "Item code is required"
            })
            continue
        
        try:
            # Check if exists
            if frappe.db.exists("Item", item_code):
                # Update existing
                doc = frappe.get_doc("Item", item_code)
                doc.update(item_data)
                doc.save()
                results["updated"] += 1
                results["details"].append({
                    "row": idx,
                    "item_code": item_code,
                    "status": "updated"
                })
            else:
                # Create new
                doc = frappe.get_doc({
                    "doctype": "Item",
                    **item_data
                })
                doc.insert()
                results["created"] += 1
                results["details"].append({
                    "row": idx,
                    "item_code": item_code,
                    "status": "created"
                })
                
        except frappe.DuplicateEntryError:
            results["skipped"] += 1
            results["details"].append({
                "row": idx,
                "item_code": item_code,
                "status": "skipped",
                "error": "Duplicate entry"
            })
            
        except frappe.ValidationError as e:
            results["failed"] += 1
            results["details"].append({
                "row": idx,
                "item_code": item_code,
                "status": "failed",
                "error": str(e)[:200]
            })
            
        except Exception as e:
            results["failed"] += 1
            frappe.log_error(
                frappe.get_traceback(),
                f"Item import error: {item_code}"
            )
            results["details"].append({
                "row": idx,
                "item_code": item_code,
                "status": "failed",
                "error": "Unexpected error - logged for review"
            })
        
        # Commit every 50 items
        if idx % 50 == 0:
            frappe.db.commit()
    
    # Final commit
    frappe.db.commit()
    
    # Summary message
    if results["failed"] > 0:
        frappe.msgprint(
            _("Import completed with errors. Created: {0}, Updated: {1}, Failed: {2}").format(
                results["created"], results["updated"], results["failed"]
            ),
            indicator="orange"
        )
    else:
        frappe.msgprint(
            _("Import completed successfully. Created: {0}, Updated: {1}").format(
                results["created"], results["updated"]
            ),
            indicator="green"
        )
    
    return results
```

---

## Example 3: Report Query with Error Handling

```python
# myapp/reports/sales_report.py
import frappe
from frappe import _

def execute(filters=None):
    """Sales report with query error handling."""
    columns = get_columns()
    
    try:
        data = get_data(filters)
    except frappe.db.InternalError as e:
        frappe.log_error(frappe.get_traceback(), "Sales Report Query Error")
        frappe.throw(_("Error generating report. Please try again or contact support."))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Sales Report Error")
        frappe.throw(_("An error occurred. Please try again."))
    
    return columns, data


def get_columns():
    return [
        {"label": _("Invoice"), "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": 120},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
    ]


def get_data(filters):
    """Get report data with safe query."""
    conditions = []
    values = {}
    
    # Build conditions safely
    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters.get("customer")
    
    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")
    
    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Safe parameterized query
    query = f"""
        SELECT
            si.name,
            si.customer,
            si.posting_date,
            si.grand_total
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
        AND {where_clause}
        ORDER BY si.posting_date DESC
        LIMIT 1000
    """
    
    return frappe.db.sql(query, values, as_dict=True)
```

---

## Example 4: Background Job with Database Operations

```python
# myapp/tasks/sync_task.py
import frappe
from frappe import _

def sync_customers_to_external():
    """
    Background task to sync customers.
    Proper error handling for background jobs.
    """
    results = {
        "synced": 0,
        "failed": 0,
        "errors": []
    }
    
    try:
        # Get customers to sync (ALWAYS limit!)
        customers = frappe.get_all(
            "Customer",
            filters={"sync_status": "Pending"},
            fields=["name", "customer_name", "email_id"],
            limit=200
        )
        
        if not customers:
            frappe.db.commit()
            return {"message": "No customers to sync"}
        
        for customer in customers:
            try:
                # Sync to external system
                external_id = sync_to_external(customer)
                
                # Update sync status
                frappe.db.set_value(
                    "Customer",
                    customer.name,
                    {
                        "sync_status": "Synced",
                        "external_id": external_id,
                        "last_sync": frappe.utils.now()
                    }
                )
                results["synced"] += 1
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "customer": customer.name,
                    "error": str(e)[:200]
                })
                
                # Mark as failed
                frappe.db.set_value(
                    "Customer",
                    customer.name,
                    {
                        "sync_status": "Failed",
                        "sync_error": str(e)[:500]
                    }
                )
                
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Customer sync error: {customer.name}"
                )
        
        # REQUIRED: Commit in background job
        frappe.db.commit()
        
    except frappe.db.InternalError as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Sync Task Database Error")
        results["fatal_error"] = str(e)
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Sync Task Error")
        results["fatal_error"] = str(e)
    
    # Log summary
    if results.get("failed") or results.get("fatal_error"):
        frappe.log_error(
            frappe.as_json(results),
            "Customer Sync Summary - With Errors"
        )
    
    return results


def sync_to_external(customer):
    """Sync customer to external system."""
    # Implementation
    return "EXT-001"
```

---

## Example 5: Controller with Database Error Handling

```python
# myapp/doctype/custom_order/custom_order.py
import frappe
from frappe import _
from frappe.model.document import Document

class CustomOrder(Document):
    def validate(self):
        """Validation with database lookups."""
        self.validate_customer()
        self.validate_items()
        self.calculate_totals()
    
    def validate_customer(self):
        """Validate customer with proper error handling."""
        if not self.customer:
            frappe.throw(_("Customer is required"))
        
        # Safe lookup
        customer_data = frappe.db.get_value(
            "Customer",
            self.customer,
            ["customer_name", "disabled", "credit_limit"],
            as_dict=True
        )
        
        if not customer_data:
            frappe.throw(
                _("Customer '{0}' not found").format(self.customer),
                exc=frappe.DoesNotExistError
            )
        
        if customer_data.disabled:
            frappe.throw(_("Customer '{0}' is disabled").format(customer_data.customer_name))
        
        # Credit check
        if customer_data.credit_limit:
            outstanding = self.get_customer_outstanding()
            if outstanding + self.grand_total > customer_data.credit_limit:
                frappe.msgprint(
                    _("Warning: This order will exceed customer credit limit"),
                    indicator="orange"
                )
    
    def validate_items(self):
        """Validate items with batch lookup."""
        if not self.items:
            frappe.throw(_("At least one item is required"))
        
        errors = []
        
        # Batch fetch items for efficiency
        item_codes = [row.item_code for row in self.items if row.item_code]
        if item_codes:
            existing_items = {
                d.name: d for d in frappe.get_all(
                    "Item",
                    filters={"name": ["in", item_codes]},
                    fields=["name", "item_name", "disabled", "is_sales_item"]
                )
            }
        else:
            existing_items = {}
        
        for idx, row in enumerate(self.items, 1):
            if not row.item_code:
                errors.append(_("Row {0}: Item code is required").format(idx))
                continue
            
            item = existing_items.get(row.item_code)
            if not item:
                errors.append(_("Row {0}: Item '{1}' not found").format(idx, row.item_code))
            elif item.disabled:
                errors.append(_("Row {0}: Item '{1}' is disabled").format(idx, item.item_name))
            elif not item.is_sales_item:
                errors.append(_("Row {0}: Item '{1}' is not a sales item").format(idx, item.item_name))
        
        if errors:
            frappe.throw("<br>".join(errors), title=_("Item Errors"))
    
    def calculate_totals(self):
        """Calculate totals."""
        self.total = sum(row.amount or 0 for row in self.items)
        self.grand_total = self.total - (self.discount_amount or 0)
    
    def get_customer_outstanding(self):
        """Get customer outstanding with error handling."""
        try:
            result = frappe.db.sql("""
                SELECT COALESCE(SUM(outstanding_amount), 0)
                FROM `tabSales Invoice`
                WHERE customer = %s AND docstatus = 1
            """, self.customer)
            return result[0][0] if result else 0
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Outstanding calculation error")
            return 0
    
    def on_submit(self):
        """Post-submit with error handling."""
        try:
            self.create_linked_records()
        except frappe.DuplicateEntryError:
            frappe.throw(_("Linked records already exist"))
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Submit error")
            frappe.throw(_("Error creating linked records: {0}").format(str(e)))
    
    def create_linked_records(self):
        """Create linked records."""
        pass
```

---

## Quick Reference: Database Error Handling

```python
# Check before get_doc
if frappe.db.exists("Customer", name):
    doc = frappe.get_doc("Customer", name)

# Catch DoesNotExistError
try:
    doc = frappe.get_doc("Customer", name)
except frappe.DoesNotExistError:
    frappe.throw(_("Customer not found"))

# Handle duplicates on insert
try:
    doc.insert()
except frappe.DuplicateEntryError:
    frappe.throw(_("Already exists"))

# Handle link errors on delete
try:
    frappe.delete_doc("Customer", name)
except frappe.LinkExistsError:
    frappe.throw(_("Cannot delete - linked documents exist"))

# Handle concurrent edits
try:
    doc.save()
except frappe.TimestampMismatchError:
    frappe.throw(_("Document modified. Please refresh."))

# Handle database errors
try:
    frappe.db.sql(query, values)
except frappe.db.InternalError:
    frappe.log_error(frappe.get_traceback(), "DB Error")
    frappe.throw(_("Database error"))

# Background job - always commit
frappe.db.commit()
```
