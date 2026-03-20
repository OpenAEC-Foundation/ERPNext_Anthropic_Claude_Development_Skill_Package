# Examples - Controller Error Handling

Complete working examples of error handling in Frappe/ERPNext Document Controllers.

---

## Example 1: Sales Order Controller (Full Implementation)

Complete controller with comprehensive error handling across all hooks.

```python
# myapp/selling/doctype/sales_order/sales_order.py
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, today


class SalesOrder(Document):
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def validate(self):
        """Main validation - runs on every save."""
        self.validate_customer()
        self.validate_items()
        self.validate_dates()
        self.calculate_totals()
        self.check_credit_limit()
    
    def validate_customer(self):
        """Validate customer exists and is active."""
        if not self.customer:
            frappe.throw(_("Customer is required"))
        
        customer = frappe.db.get_value(
            "Customer", self.customer,
            ["disabled", "is_frozen", "customer_name"],
            as_dict=True
        )
        
        if not customer:
            frappe.throw(_("Customer '{0}' not found").format(self.customer))
        
        if customer.disabled:
            frappe.throw(_("Customer '{0}' is disabled").format(customer.customer_name))
        
        if customer.is_frozen:
            frappe.throw(_("Customer '{0}' account is frozen").format(customer.customer_name))
    
    def validate_items(self):
        """Validate items with error collection."""
        if not self.items:
            frappe.throw(_("At least one item is required"))
        
        errors = []
        item_codes = [row.item_code for row in self.items if row.item_code]
        
        # Batch fetch item data for efficiency
        if item_codes:
            items_data = {
                d.name: d for d in frappe.get_all(
                    "Item",
                    filters={"name": ["in", item_codes]},
                    fields=["name", "item_name", "disabled", "is_sales_item", "stock_uom"]
                )
            }
        else:
            items_data = {}
        
        for idx, row in enumerate(self.items, 1):
            if not row.item_code:
                errors.append(_("Row {0}: Item Code is required").format(idx))
                continue
            
            item = items_data.get(row.item_code)
            
            if not item:
                errors.append(_("Row {0}: Item '{1}' not found").format(idx, row.item_code))
                continue
            
            if item.disabled:
                errors.append(_("Row {0}: Item '{1}' is disabled").format(idx, item.item_name))
            
            if not item.is_sales_item:
                errors.append(_("Row {0}: Item '{1}' is not a sales item").format(idx, item.item_name))
            
            if flt(row.qty) <= 0:
                errors.append(_("Row {0}: Quantity must be greater than zero").format(idx))
            
            if flt(row.rate) < 0:
                errors.append(_("Row {0}: Rate cannot be negative").format(idx))
        
        if errors:
            frappe.throw("<br>".join(errors), title=_("Item Errors"))
    
    def validate_dates(self):
        """Validate date fields."""
        if self.delivery_date and str(self.delivery_date) < today():
            frappe.throw(_("Delivery Date cannot be in the past"))
        
        if self.valid_till and self.transaction_date:
            if str(self.valid_till) < str(self.transaction_date):
                frappe.throw(_("Valid Till cannot be before Order Date"))
    
    def calculate_totals(self):
        """Calculate order totals."""
        self.total = sum(flt(item.amount) for item in self.items)
        self.tax_amount = flt(self.total) * flt(self.tax_rate or 0) / 100
        self.grand_total = flt(self.total) + flt(self.tax_amount) - flt(self.discount_amount or 0)
    
    def check_credit_limit(self):
        """Check credit limit - warning only."""
        if not self.customer:
            return
        
        credit_limit = frappe.db.get_value("Customer", self.customer, "credit_limit") or 0
        
        if credit_limit and flt(self.grand_total) > flt(credit_limit):
            frappe.msgprint(
                _("Order total ({0}) exceeds credit limit ({1})").format(
                    frappe.format_value(self.grand_total, {"fieldtype": "Currency"}),
                    frappe.format_value(credit_limit, {"fieldtype": "Currency"})
                ),
                title=_("Credit Warning"),
                indicator="orange"
            )
    
    # =========================================================================
    # POST-SAVE
    # =========================================================================
    
    def on_update(self):
        """After save actions with error isolation."""
        # Critical: Update linked quotation
        if self.quotation:
            self.update_quotation()
        
        # Non-critical: External sync
        try:
            self.sync_to_crm()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"CRM sync failed for {self.name}"
            )
        
        # Non-critical: Notifications
        try:
            self.send_notifications()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Notification failed for {self.name}"
            )
    
    def update_quotation(self):
        """Update quotation status."""
        if not frappe.db.exists("Quotation", self.quotation):
            frappe.msgprint(
                _("Linked quotation {0} not found").format(self.quotation),
                indicator="orange"
            )
            return
        
        frappe.db.set_value("Quotation", self.quotation, "status", "Ordered")
    
    def sync_to_crm(self):
        """Sync to external CRM."""
        pass  # Implementation
    
    def send_notifications(self):
        """Send notifications."""
        pass  # Implementation
    
    # =========================================================================
    # SUBMIT
    # =========================================================================
    
    def before_submit(self):
        """Last validation before submit."""
        # Check stock availability
        for item in self.items:
            if item.warehouse:
                available = self.get_available_stock(item.item_code, item.warehouse)
                if available < flt(item.qty):
                    frappe.throw(
                        _("Row {0}: Insufficient stock for {1}. Available: {2}, Required: {3}").format(
                            item.idx, item.item_code, available, item.qty
                        )
                    )
        
        # Check approvals
        if flt(self.grand_total) > 100000 and not self.manager_approval:
            frappe.throw(_("Manager approval required for orders over 100,000"))
    
    def on_submit(self):
        """Post-submit actions."""
        try:
            self.reserve_stock()
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Stock Reservation Error")
            frappe.throw(_("Stock reservation failed: {0}").format(str(e)))
        
        # Update customer last order (non-critical)
        try:
            frappe.db.set_value(
                "Customer", self.customer,
                "last_order_date", self.transaction_date
            )
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Customer Update Error")
    
    def get_available_stock(self, item_code, warehouse):
        """Get available stock quantity."""
        result = frappe.db.sql("""
            SELECT COALESCE(actual_qty, 0) - COALESCE(reserved_qty, 0)
            FROM `tabBin`
            WHERE item_code = %s AND warehouse = %s
        """, (item_code, warehouse))
        return flt(result[0][0]) if result else 0
    
    def reserve_stock(self):
        """Reserve stock for order."""
        pass  # Implementation
    
    # =========================================================================
    # CANCEL
    # =========================================================================
    
    def before_cancel(self):
        """Validate cancellation is allowed."""
        # Check for linked delivery notes
        deliveries = frappe.get_all(
            "Delivery Note Item",
            filters={"against_sales_order": self.name, "docstatus": 1},
            pluck="parent"
        )
        
        if deliveries:
            frappe.throw(
                _("Cannot cancel. Linked Delivery Notes exist: {0}").format(
                    ", ".join(set(deliveries))
                )
            )
    
    def on_cancel(self):
        """Cleanup after cancel."""
        errors = []
        
        # Release stock reservation
        try:
            self.release_stock_reservation()
        except Exception as e:
            errors.append(_("Stock release: {0}").format(str(e)))
            frappe.log_error(frappe.get_traceback(), "Stock Release Error")
        
        # Update quotation
        if self.quotation:
            try:
                frappe.db.set_value("Quotation", self.quotation, "status", "Open")
            except Exception as e:
                errors.append(_("Quotation update: {0}").format(str(e)))
        
        if errors:
            frappe.msgprint(
                _("Order cancelled with errors:<br>{0}").format("<br>".join(errors)),
                indicator="orange"
            )
    
    def release_stock_reservation(self):
        """Release reserved stock."""
        pass  # Implementation
```

---

## Example 2: Payment Processing Controller

Controller with external API integration and transaction handling.

```python
# myapp/payments/doctype/payment_request/payment_request.py
import frappe
from frappe import _
from frappe.model.document import Document
import requests
from requests.exceptions import RequestException, Timeout


class PaymentRequest(Document):
    def validate(self):
        """Validate payment request."""
        self.validate_amount()
        self.validate_reference()
    
    def validate_amount(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Amount must be greater than zero"))
        
        if flt(self.amount) > 1000000:
            frappe.throw(_("Amount exceeds maximum limit of 1,000,000"))
    
    def validate_reference(self):
        if not self.reference_doctype or not self.reference_name:
            frappe.throw(_("Reference document is required"))
        
        if not frappe.db.exists(self.reference_doctype, self.reference_name):
            frappe.throw(
                _("Reference {0} {1} does not exist").format(
                    self.reference_doctype, self.reference_name
                )
            )
    
    def on_submit(self):
        """Process payment on submit."""
        self.process_payment()
    
    def process_payment(self):
        """Process payment with gateway."""
        gateway = self.get_payment_gateway()
        
        # Prepare request
        payload = {
            "amount": self.amount,
            "currency": self.currency,
            "reference": self.name,
            "customer_email": self.email
        }
        
        try:
            response = requests.post(
                gateway.api_endpoint,
                json=payload,
                headers={"Authorization": f"Bearer {gateway.api_key}"},
                timeout=30
            )
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                self.db_set("payment_id", data.get("payment_id"))
                self.db_set("status", "Completed")
                self.db_set("completed_on", frappe.utils.now())
                
            elif response.status_code == 400:
                error = response.json().get("error", "Invalid request")
                frappe.throw(_("Payment failed: {0}").format(error))
                
            elif response.status_code == 401:
                frappe.log_error(
                    f"Gateway authentication failed for {gateway.name}",
                    "Payment Gateway Error"
                )
                frappe.throw(_("Payment gateway authentication failed"))
                
            elif response.status_code == 402:
                frappe.throw(_("Payment declined by bank"))
                
            elif response.status_code >= 500:
                frappe.throw(_("Payment gateway temporarily unavailable. Please try again."))
                
            else:
                frappe.log_error(
                    f"Unexpected response {response.status_code}: {response.text[:500]}",
                    "Payment Gateway Error"
                )
                frappe.throw(_("Payment processing failed"))
                
        except Timeout:
            frappe.throw(
                _("Payment gateway timed out. Please check your payment status before retrying.")
            )
            
        except requests.ConnectionError:
            frappe.throw(
                _("Could not connect to payment gateway. Please check your internet connection.")
            )
            
        except RequestException as e:
            frappe.log_error(frappe.get_traceback(), "Payment Request Error")
            frappe.throw(_("Payment processing error: {0}").format(str(e)[:100]))
            
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Unexpected Payment Error")
            frappe.throw(_("An unexpected error occurred. Please contact support."))
    
    def get_payment_gateway(self):
        """Get configured payment gateway."""
        if not self.payment_gateway:
            frappe.throw(_("Payment gateway not configured"))
        
        try:
            gateway = frappe.get_doc("Payment Gateway", self.payment_gateway)
        except frappe.DoesNotExistError:
            frappe.throw(_("Payment gateway {0} not found").format(self.payment_gateway))
        
        if not gateway.enabled:
            frappe.throw(_("Payment gateway {0} is disabled").format(self.payment_gateway))
        
        return gateway
    
    def on_cancel(self):
        """Refund payment on cancel."""
        if self.status != "Completed" or not self.payment_id:
            return
        
        try:
            self.process_refund()
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Refund Error")
            frappe.msgprint(
                _("Payment cancelled but refund failed: {0}. Manual refund may be required.").format(str(e)),
                indicator="red"
            )
    
    def process_refund(self):
        """Process refund with gateway."""
        gateway = self.get_payment_gateway()
        
        try:
            response = requests.post(
                f"{gateway.api_endpoint}/refund",
                json={"payment_id": self.payment_id},
                headers={"Authorization": f"Bearer {gateway.api_key}"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.db_set("refund_id", response.json().get("refund_id"))
                self.db_set("status", "Refunded")
            else:
                raise Exception(f"Refund failed: {response.text[:200]}")
                
        except Exception:
            raise
```

---

## Example 3: Data Migration Controller

Controller for handling data migrations with detailed error tracking.

```python
# myapp/migrations/doctype/data_migration/data_migration.py
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint


class DataMigration(Document):
    def validate(self):
        if not self.source_doctype or not self.target_doctype:
            frappe.throw(_("Source and Target DocTypes are required"))
        
        for dt in [self.source_doctype, self.target_doctype]:
            if not frappe.db.exists("DocType", dt):
                frappe.throw(_("DocType '{0}' does not exist").format(dt))
    
    def on_submit(self):
        """Start migration."""
        self.db_set("status", "In Progress")
        self.db_set("started_on", frappe.utils.now())
        
        # Run migration
        try:
            self.run_migration()
        except Exception as e:
            self.db_set("status", "Failed")
            self.db_set("error_message", str(e)[:1000])
            frappe.log_error(frappe.get_traceback(), f"Migration Failed: {self.name}")
            frappe.throw(_("Migration failed: {0}").format(str(e)))
    
    def run_migration(self):
        """Execute migration with detailed error tracking."""
        batch_size = cint(self.batch_size) or 100
        
        # Get source records
        source_records = frappe.get_all(
            self.source_doctype,
            filters=self.get_source_filters(),
            fields=["*"],
            limit=cint(self.record_limit) or None
        )
        
        if not source_records:
            self.db_set("status", "Completed")
            self.db_set("message", "No records to migrate")
            return
        
        # Track progress
        total = len(source_records)
        migrated = 0
        failed = 0
        error_details = []
        
        # Process in batches
        for i in range(0, total, batch_size):
            batch = source_records[i:i + batch_size]
            
            for record in batch:
                frappe.db.savepoint(f"record_{record.name}")
                
                try:
                    self.migrate_record(record)
                    migrated += 1
                except frappe.DuplicateEntryError:
                    frappe.db.rollback(save_point=f"record_{record.name}")
                    if self.skip_duplicates:
                        failed += 1
                        error_details.append({
                            "source": record.name,
                            "error": "Duplicate entry - skipped"
                        })
                    else:
                        raise
                except frappe.ValidationError as e:
                    frappe.db.rollback(save_point=f"record_{record.name}")
                    failed += 1
                    error_details.append({
                        "source": record.name,
                        "error": str(e)[:200]
                    })
                except Exception as e:
                    frappe.db.rollback(save_point=f"record_{record.name}")
                    failed += 1
                    error_details.append({
                        "source": record.name,
                        "error": "Unexpected error"
                    })
                    frappe.log_error(
                        frappe.get_traceback(),
                        f"Migration record error: {record.name}"
                    )
            
            # Commit batch
            frappe.db.commit()
            
            # Update progress
            self.db_set("progress", round((i + len(batch)) / total * 100, 1))
        
        # Final status
        self.db_set("records_migrated", migrated)
        self.db_set("records_failed", failed)
        self.db_set("completed_on", frappe.utils.now())
        
        if failed == 0:
            self.db_set("status", "Completed")
        elif migrated > 0:
            self.db_set("status", "Completed with Errors")
        else:
            self.db_set("status", "Failed")
        
        # Create error log if errors
        if error_details:
            self.create_error_log(error_details)
            frappe.msgprint(
                _("Migration completed. {0} succeeded, {1} failed. See Error Log for details.").format(
                    migrated, failed
                ),
                indicator="orange"
            )
        else:
            frappe.msgprint(
                _("Migration completed successfully. {0} records migrated.").format(migrated),
                indicator="green"
            )
    
    def migrate_record(self, source):
        """Migrate single record."""
        # Transform data
        target_data = self.transform_record(source)
        
        # Create target
        target = frappe.new_doc(self.target_doctype)
        target.update(target_data)
        target.flags.ignore_permissions = True
        target.insert()
        
        return target.name
    
    def transform_record(self, source):
        """Transform source record to target format."""
        # Use field mapping
        target_data = {}
        for mapping in self.field_mappings:
            source_value = source.get(mapping.source_field)
            if source_value is not None:
                target_data[mapping.target_field] = source_value
        return target_data
    
    def get_source_filters(self):
        """Get filters for source query."""
        filters = {}
        if self.source_filters:
            try:
                filters = frappe.parse_json(self.source_filters)
            except Exception:
                frappe.throw(_("Invalid source filters JSON"))
        return filters
    
    def create_error_log(self, errors):
        """Create detailed error log."""
        log = frappe.new_doc("Data Migration Log")
        log.migration = self.name
        log.errors = frappe.as_json(errors[:500])  # Limit size
        log.error_count = len(errors)
        log.insert(ignore_permissions=True)
```

---

## Quick Reference: Controller Error Patterns

```python
# Validation error - stop save
frappe.throw(_("Error message"))

# Warning - continue save
frappe.msgprint(_("Warning message"), indicator="orange")

# Log error silently
frappe.log_error(frappe.get_traceback(), "Error Title")

# Catch specific exception
try:
    operation()
except frappe.DoesNotExistError:
    frappe.throw(_("Record not found"))
except frappe.DuplicateEntryError:
    frappe.throw(_("Record already exists"))

# Non-critical operation
try:
    non_critical_operation()
except Exception:
    frappe.log_error(frappe.get_traceback(), "Non-critical Error")
    # Continue execution

# Check existence before operation
if frappe.db.exists("DocType", name):
    doc = frappe.get_doc("DocType", name)
else:
    frappe.throw(_("Document not found"))
```
