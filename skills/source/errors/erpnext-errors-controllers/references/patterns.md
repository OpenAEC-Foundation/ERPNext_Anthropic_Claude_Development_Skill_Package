# Error Handling Patterns - Controllers

Complete error handling patterns for Frappe/ERPNext Document Controllers.

---

## Pattern 1: Comprehensive Validation Class

```python
import frappe
from frappe import _

class DocumentValidator:
    """Reusable validation helper for controllers."""
    
    def __init__(self, doc):
        self.doc = doc
        self.errors = []
        self.warnings = []
    
    def require(self, field, label=None):
        """Validate required field."""
        label = label or field.replace("_", " ").title()
        if not self.doc.get(field):
            self.errors.append(_("{0} is required").format(label))
    
    def positive(self, field, label=None):
        """Validate field is positive."""
        label = label or field.replace("_", " ").title()
        value = self.doc.get(field) or 0
        if value <= 0:
            self.errors.append(_("{0} must be greater than zero").format(label))
    
    def max_value(self, field, max_val, label=None):
        """Validate maximum value."""
        label = label or field.replace("_", " ").title()
        value = self.doc.get(field) or 0
        if value > max_val:
            self.errors.append(_("{0} cannot exceed {1}").format(label, max_val))
    
    def date_not_past(self, field, label=None):
        """Validate date is not in past."""
        label = label or field.replace("_", " ").title()
        value = self.doc.get(field)
        if value and str(value) < frappe.utils.today():
            self.errors.append(_("{0} cannot be in the past").format(label))
    
    def exists(self, doctype, field, label=None):
        """Validate linked document exists."""
        label = label or field.replace("_", " ").title()
        value = self.doc.get(field)
        if value and not frappe.db.exists(doctype, value):
            self.errors.append(_("{0} '{1}' does not exist").format(label, value))
    
    def child_table_not_empty(self, table_field, label=None):
        """Validate child table has rows."""
        label = label or table_field.replace("_", " ").title()
        if not self.doc.get(table_field):
            self.errors.append(_("At least one {0} row is required").format(label))
    
    def validate_child_rows(self, table_field, validate_fn):
        """Validate each row in child table."""
        for idx, row in enumerate(self.doc.get(table_field) or [], 1):
            error = validate_fn(row, idx)
            if error:
                self.errors.append(error)
    
    def add_warning(self, message):
        """Add a non-blocking warning."""
        self.warnings.append(message)
    
    def throw_if_errors(self, title=None):
        """Show warnings and throw errors."""
        # Show warnings first
        if self.warnings:
            frappe.msgprint(
                "<br>".join(self.warnings),
                title=_("Warnings"),
                indicator="orange"
            )
        
        # Throw errors
        if self.errors:
            frappe.throw(
                "<br>".join(self.errors),
                title=title or _("Validation Error")
            )


# Usage in controller
class SalesOrder(Document):
    def validate(self):
        v = DocumentValidator(self)
        
        v.require("customer")
        v.require("delivery_date")
        v.date_not_past("delivery_date")
        v.exists("Customer", "customer")
        v.child_table_not_empty("items", "Item")
        v.max_value("discount_percent", 50, "Discount")
        
        v.validate_child_rows("items", self.validate_item_row)
        
        # Business warnings
        if self.grand_total > 100000:
            v.add_warning(_("Large order - may require approval"))
        
        v.throw_if_errors()
    
    def validate_item_row(self, row, idx):
        if not row.item_code:
            return _("Row {0}: Item Code is required").format(idx)
        if (row.qty or 0) <= 0:
            return _("Row {0}: Quantity must be positive").format(idx)
        return None
```

---

## Pattern 2: External Service Integration

```python
import frappe
from frappe import _
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

class PaymentGateway(Document):
    def validate(self):
        if self.auto_verify and self.is_new():
            self.verify_credentials()
    
    def verify_credentials(self):
        """Verify gateway credentials with proper error handling."""
        try:
            response = requests.post(
                self.api_endpoint,
                json={"api_key": self.api_key},
                timeout=10  # Always set timeout!
            )
            
            if response.status_code == 401:
                frappe.throw(_("Invalid API credentials"))
            elif response.status_code == 403:
                frappe.throw(_("API access denied. Check your subscription."))
            elif response.status_code >= 500:
                frappe.throw(_("Payment gateway is temporarily unavailable"))
            elif response.status_code != 200:
                frappe.throw(_("Verification failed: {0}").format(response.text[:200]))
            
            self.verified = 1
            self.last_verified = frappe.utils.now()
            
        except Timeout:
            frappe.throw(
                _("Connection timed out. The payment gateway may be slow. Please try again.")
            )
        except ConnectionError:
            frappe.throw(
                _("Could not connect to payment gateway. Please check your network.")
            )
        except RequestException as e:
            frappe.log_error(frappe.get_traceback(), "Payment Gateway Error")
            frappe.throw(
                _("Connection error: {0}").format(str(e)[:100])
            )
    
    def on_update(self):
        """Sync settings to gateway (non-critical)."""
        if not self.auto_sync:
            return
        
        try:
            self.sync_to_gateway()
        except Timeout:
            frappe.msgprint(
                _("Settings saved locally. Gateway sync timed out - will retry."),
                indicator="orange"
            )
            self.queue_sync_retry()
        except RequestException:
            frappe.log_error(frappe.get_traceback(), "Gateway Sync Error")
            frappe.msgprint(
                _("Settings saved. Gateway sync failed - will retry automatically."),
                indicator="orange"
            )
            self.queue_sync_retry()
    
    def queue_sync_retry(self):
        frappe.enqueue(
            "myapp.payment.retry_gateway_sync",
            gateway=self.name,
            queue="short",
            job_id=f"gateway_sync_{self.name}"
        )
```

---

## Pattern 3: Batch Processing with Error Isolation

```python
class BulkOperation(Document):
    def on_submit(self):
        """Process items in batch with isolated error handling."""
        results = {
            "success": [],
            "failed": [],
            "skipped": []
        }
        
        for item in self.items:
            try:
                # Validate before processing
                if not self.can_process(item):
                    results["skipped"].append({
                        "item": item.item_code,
                        "reason": "Not eligible for processing"
                    })
                    continue
                
                # Process with savepoint for partial rollback
                frappe.db.savepoint(f"item_{item.idx}")
                
                self.process_item(item)
                results["success"].append(item.item_code)
                
            except frappe.ValidationError as e:
                frappe.db.rollback(save_point=f"item_{item.idx}")
                results["failed"].append({
                    "item": item.item_code,
                    "error": str(e)
                })
            except Exception as e:
                frappe.db.rollback(save_point=f"item_{item.idx}")
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Bulk Processing Error: {item.item_code}"
                )
                results["failed"].append({
                    "item": item.item_code,
                    "error": "Unexpected error - logged for review"
                })
        
        # Update document with results
        self.db_set("processed_count", len(results["success"]))
        self.db_set("failed_count", len(results["failed"]))
        self.db_set("skipped_count", len(results["skipped"]))
        
        # Generate report
        self.create_processing_report(results)
        
        # Show summary
        if results["failed"]:
            failed_summary = "<br>".join([
                f"{f['item']}: {f['error']}" for f in results["failed"][:10]
            ])
            if len(results["failed"]) > 10:
                failed_summary += f"<br>... and {len(results['failed']) - 10} more"
            
            frappe.msgprint(
                _("Completed: {0} success, {1} failed, {2} skipped<br><br>Failed items:<br>{3}").format(
                    len(results["success"]),
                    len(results["failed"]),
                    len(results["skipped"]),
                    failed_summary
                ),
                title=_("Processing Complete"),
                indicator="orange"
            )
        else:
            frappe.msgprint(
                _("All {0} items processed successfully").format(len(results["success"])),
                title=_("Success"),
                indicator="green"
            )
```

---

## Pattern 4: Controller Override with Safe Extension

```python
# myapp/overrides/sales_invoice.py
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
import frappe
from frappe import _

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        """Extend validation with proper error handling."""
        # ALWAYS call parent first
        try:
            super().validate()
        except frappe.ValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            # Log unexpected parent errors
            frappe.log_error(frappe.get_traceback(), "Parent Validate Error")
            raise
        
        # Custom validation
        self.validate_credit_limit()
        self.validate_customer_status()
    
    def validate_credit_limit(self):
        """Custom credit limit check."""
        if not self.customer:
            return
        
        try:
            credit_limit = frappe.db.get_value(
                "Customer", self.customer, "credit_limit"
            ) or 0
            
            if credit_limit and self.grand_total > credit_limit:
                frappe.throw(
                    _("Invoice amount {0} exceeds credit limit {1}").format(
                        frappe.format_value(self.grand_total, {"fieldtype": "Currency"}),
                        frappe.format_value(credit_limit, {"fieldtype": "Currency"})
                    )
                )
        except frappe.DoesNotExistError:
            frappe.throw(_("Customer {0} not found").format(self.customer))
    
    def validate_customer_status(self):
        """Check customer is active."""
        if not self.customer:
            return
        
        customer_data = frappe.db.get_value(
            "Customer", self.customer,
            ["disabled", "is_frozen"],
            as_dict=True
        )
        
        if not customer_data:
            return  # Already validated in parent
        
        if customer_data.disabled:
            frappe.throw(_("Customer {0} is disabled").format(self.customer))
        
        if customer_data.is_frozen:
            frappe.throw(_("Customer {0} account is frozen").format(self.customer))
    
    def on_submit(self):
        """Extend submit with custom integration."""
        try:
            super().on_submit()
        except Exception:
            # Re-raise parent errors
            raise
        
        # Custom post-submit (non-critical)
        try:
            self.sync_to_external_erp()
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"External ERP sync failed for {self.name}"
            )
            # Don't throw - invoice is already submitted
            frappe.msgprint(
                _("Invoice submitted. External sync will be retried."),
                indicator="orange"
            )
```

---

## Pattern 5: Async Operation with Error Recovery

```python
class DataImport(Document):
    def on_submit(self):
        """Start async import with error tracking."""
        # Validate file exists
        if not self.import_file:
            frappe.throw(_("Import file is required"))
        
        file_doc = frappe.get_doc("File", {"file_url": self.import_file})
        if not file_doc:
            frappe.throw(_("Import file not found"))
        
        # Queue the import
        frappe.enqueue(
            "myapp.imports.process_import",
            queue="long",
            timeout=3600,
            job_id=f"import_{self.name}",
            import_name=self.name,
            file_path=file_doc.get_full_path()
        )
        
        self.db_set("status", "Processing")
        frappe.msgprint(
            _("Import started. You will be notified when complete."),
            indicator="blue"
        )


# myapp/imports.py
def process_import(import_name, file_path):
    """Background import with comprehensive error handling."""
    import_doc = frappe.get_doc("Data Import", import_name)
    
    try:
        # Read file
        try:
            data = read_import_file(file_path)
        except FileNotFoundError:
            raise ImportError(_("Import file not found"))
        except PermissionError:
            raise ImportError(_("Cannot read import file - permission denied"))
        except Exception as e:
            raise ImportError(_("Error reading file: {0}").format(str(e)))
        
        # Process rows
        success_count = 0
        error_rows = []
        
        for idx, row in enumerate(data, 1):
            try:
                process_row(row)
                success_count += 1
            except frappe.ValidationError as e:
                error_rows.append({"row": idx, "error": str(e)})
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Import Row {idx} Error")
                error_rows.append({"row": idx, "error": "Unexpected error"})
            
            # Commit periodically
            if idx % 100 == 0:
                frappe.db.commit()
        
        # Update status
        import_doc.db_set("status", "Completed" if not error_rows else "Completed with Errors")
        import_doc.db_set("success_count", success_count)
        import_doc.db_set("error_count", len(error_rows))
        
        if error_rows:
            create_error_log(import_name, error_rows)
        
        frappe.db.commit()
        
        # Notify user
        frappe.publish_realtime(
            "import_complete",
            {"import_name": import_name, "status": import_doc.status},
            user=import_doc.owner
        )
        
    except ImportError as e:
        import_doc.db_set("status", "Failed")
        import_doc.db_set("error_message", str(e))
        frappe.db.commit()
        
        frappe.publish_realtime(
            "import_failed",
            {"import_name": import_name, "error": str(e)},
            user=import_doc.owner
        )
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Import Failed: {import_name}")
        import_doc.db_set("status", "Failed")
        import_doc.db_set("error_message", "Unexpected error - see Error Log")
        frappe.db.commit()
```

---

## Pattern 6: Change Detection with Safe Comparison

```python
class Contract(Document):
    def validate(self):
        """Detect and validate changes."""
        if self.is_new():
            self.validate_new_contract()
        else:
            self.validate_changes()
    
    def validate_changes(self):
        """Handle changes with proper error handling."""
        try:
            old_doc = self.get_doc_before_save()
        except Exception:
            # If we can't get old doc, skip change detection
            frappe.log_error(
                frappe.get_traceback(),
                f"Could not get previous version of {self.name}"
            )
            return
        
        if not old_doc:
            return
        
        # Track changes
        changes = []
        
        # Safe comparison - handle None values
        if (old_doc.get("status") or "") != (self.status or ""):
            changes.append(("status", old_doc.status, self.status))
            self.validate_status_transition(old_doc.status, self.status)
        
        if (old_doc.get("contract_value") or 0) != (self.contract_value or 0):
            changes.append(("value", old_doc.contract_value, self.contract_value))
            self.validate_value_change(old_doc.contract_value, self.contract_value)
        
        # Store for on_update
        if changes:
            self.flags.changes = changes
    
    def validate_status_transition(self, old_status, new_status):
        """Validate status changes are allowed."""
        allowed_transitions = {
            "Draft": ["Active", "Cancelled"],
            "Active": ["Completed", "Suspended"],
            "Suspended": ["Active", "Cancelled"],
        }
        
        if old_status and new_status:
            allowed = allowed_transitions.get(old_status, [])
            if new_status not in allowed:
                frappe.throw(
                    _("Cannot change status from {0} to {1}").format(old_status, new_status)
                )
    
    def validate_value_change(self, old_value, new_value):
        """Validate value changes within limits."""
        if not old_value:
            return
        
        change_percent = abs(new_value - old_value) / old_value * 100
        
        if change_percent > 25:
            frappe.throw(
                _("Contract value change of {0}% exceeds 25% limit. Requires new contract.").format(
                    round(change_percent, 1)
                )
            )
    
    def on_update(self):
        """Log changes after save."""
        if self.flags.get("changes"):
            for field, old_val, new_val in self.flags.changes:
                try:
                    self.log_change(field, old_val, new_val)
                except Exception:
                    frappe.log_error(
                        frappe.get_traceback(),
                        f"Failed to log change for {self.name}"
                    )
```

---

## Pattern 7: Linked Document Updates

```python
class SalesOrder(Document):
    def on_update(self):
        """Update linked documents with error isolation."""
        errors = []
        
        # Update quotation
        if self.quotation:
            try:
                self.update_quotation_status()
            except Exception as e:
                errors.append(f"Quotation update: {str(e)}")
                frappe.log_error(frappe.get_traceback(), "Quotation Update Error")
        
        # Update opportunity
        if self.opportunity:
            try:
                self.update_opportunity_status()
            except Exception as e:
                errors.append(f"Opportunity update: {str(e)}")
                frappe.log_error(frappe.get_traceback(), "Opportunity Update Error")
        
        # Update customer stats
        try:
            self.update_customer_order_stats()
        except Exception as e:
            errors.append(f"Customer stats: {str(e)}")
            frappe.log_error(frappe.get_traceback(), "Customer Stats Error")
        
        # Show collected errors
        if errors:
            frappe.msgprint(
                _("Order saved. Some updates failed:<br>{0}").format("<br>".join(errors)),
                title=_("Warning"),
                indicator="orange"
            )
    
    def update_quotation_status(self):
        """Update quotation to ordered."""
        quotation = frappe.get_doc("Quotation", self.quotation)
        if quotation.docstatus == 1 and quotation.status != "Ordered":
            quotation.db_set("status", "Ordered")
    
    def update_opportunity_status(self):
        """Update opportunity to converted."""
        opp = frappe.get_doc("Opportunity", self.opportunity)
        if opp.status not in ["Converted", "Lost"]:
            opp.db_set("status", "Converted")
    
    def update_customer_order_stats(self):
        """Update customer last order date."""
        frappe.db.set_value(
            "Customer", self.customer,
            "last_order_date", self.transaction_date
        )
```

---

## Quick Reference: Error Handling by Scenario

| Scenario | Approach |
|----------|----------|
| Required field missing | `frappe.throw(_("Field is required"))` |
| Database lookup might fail | Check `frappe.db.exists()` first |
| External API call | `try/except` with specific exceptions |
| Non-critical post-save | `try/except` + `log_error` + continue |
| Linked doc update | Isolate each update in try/except |
| Batch processing | Savepoints + error collection |
| File operations | Check existence, handle permissions |
| Change detection | `get_doc_before_save()` with None checks |
