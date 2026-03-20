# Anti-Patterns - Controller Error Handling

Common mistakes to avoid when handling errors in Frappe/ERPNext Document Controllers.

---

## 1. Assuming on_update Changes Are Saved

### ❌ WRONG

```python
def on_update(self):
    """This change is LOST - document already saved!"""
    self.status = "Processed"
    self.processed_date = frappe.utils.now()
```

### ✅ CORRECT

```python
def on_update(self):
    """Use db_set for changes after save."""
    frappe.db.set_value(
        self.doctype, self.name,
        {"status": "Processed", "processed_date": frappe.utils.now()}
    )
    # Or use self.db_set()
    self.db_set("status", "Processed")
```

**Why**: After `on_update`, the document is already written to database. Changes to `self` are not saved.

---

## 2. Calling frappe.db.commit() in Controller

### ❌ WRONG

```python
def validate(self):
    self.calculate_totals()
    frappe.db.commit()  # BREAKS TRANSACTION!

def on_update(self):
    self.update_linked_docs()
    frappe.db.commit()  # DON'T DO THIS
```

### ✅ CORRECT

```python
def validate(self):
    self.calculate_totals()
    # No commit - framework handles it

def on_update(self):
    self.update_linked_docs()
    # No commit - framework handles it
```

**Why**: Frappe wraps requests in transactions. Manual commits can cause partial saves and break rollback.

---

## 3. Not Calling super() in Override

### ❌ WRONG

```python
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # Missing super()! Parent validation skipped!
        self.custom_validation()
```

### ✅ CORRECT

```python
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # ALWAYS call parent
        self.custom_validation()
```

**Why**: Skipping `super()` bypasses all parent class logic including critical validations.

---

## 4. Swallowing Errors Silently

### ❌ WRONG

```python
def validate(self):
    try:
        self.critical_validation()
    except Exception:
        pass  # Error silently ignored!
```

### ✅ CORRECT

```python
def validate(self):
    try:
        self.critical_validation()
    except frappe.ValidationError:
        raise  # Re-raise validation errors
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Validation Error")
        frappe.throw(_("Validation failed: {0}").format(str(e)))
```

**Why**: Silent errors make debugging impossible and can lead to data corruption.

---

## 5. Throwing on First Error

### ❌ WRONG

```python
def validate(self):
    if not self.customer:
        frappe.throw(_("Customer is required"))
    
    if not self.items:
        frappe.throw(_("Items are required"))
    
    # User sees errors one at a time
```

### ✅ CORRECT

```python
def validate(self):
    errors = []
    
    if not self.customer:
        errors.append(_("Customer is required"))
    
    if not self.items:
        errors.append(_("Items are required"))
    
    if errors:
        frappe.throw("<br>".join(errors))
```

**Why**: Users should see all validation errors at once, not one at a time.

---

## 6. Not Handling None/Empty Values

### ❌ WRONG

```python
def validate(self):
    # Crashes if customer doesn't exist!
    credit_limit = frappe.get_doc("Customer", self.customer).credit_limit
    
    # Division by zero if total is 0
    margin = self.profit / self.total * 100
```

### ✅ CORRECT

```python
def validate(self):
    from frappe.utils import flt
    
    # Check existence first
    if self.customer and frappe.db.exists("Customer", self.customer):
        credit_limit = frappe.db.get_value("Customer", self.customer, "credit_limit") or 0
    else:
        credit_limit = 0
    
    # Safe division
    margin = flt(self.profit) / flt(self.total) * 100 if flt(self.total) else 0
```

**Why**: Always assume values can be None, empty, or zero.

---

## 7. Critical Logic in on_submit Instead of before_submit

### ❌ WRONG

```python
def on_submit(self):
    # If this fails, document is ALREADY submitted (docstatus=1)!
    if not self.has_stock():
        frappe.throw(_("Insufficient stock"))
```

### ✅ CORRECT

```python
def before_submit(self):
    # Last chance to abort cleanly
    if not self.has_stock():
        frappe.throw(_("Insufficient stock"))

def on_submit(self):
    # Only non-blocking operations here
    self.create_stock_entries()
```

**Why**: In `on_submit`, the document is already submitted. Throwing creates an inconsistent state.

---

## 8. Not Isolating Errors in on_update

### ❌ WRONG

```python
def on_update(self):
    # If email fails, CRM sync and notifications also don't run
    self.send_confirmation_email()
    self.sync_to_crm()
    self.send_internal_notifications()
```

### ✅ CORRECT

```python
def on_update(self):
    errors = []
    
    try:
        self.send_confirmation_email()
    except Exception:
        errors.append("Email failed")
        frappe.log_error(frappe.get_traceback(), "Email Error")
    
    try:
        self.sync_to_crm()
    except Exception:
        errors.append("CRM sync failed")
        frappe.log_error(frappe.get_traceback(), "CRM Error")
    
    try:
        self.send_internal_notifications()
    except Exception:
        errors.append("Notifications failed")
        frappe.log_error(frappe.get_traceback(), "Notification Error")
    
    if errors:
        frappe.msgprint(
            _("Document saved. Some operations failed: {0}").format(", ".join(errors)),
            indicator="orange"
        )
```

**Why**: Independent operations should not block each other.

---

## 9. Exposing Technical Errors

### ❌ WRONG

```python
def validate(self):
    try:
        result = external_api_call()
    except Exception as e:
        frappe.throw(str(e))  # Exposes stack trace!
        # Or: frappe.throw(frappe.get_traceback())
```

### ✅ CORRECT

```python
def validate(self):
    try:
        result = external_api_call()
    except Timeout:
        frappe.throw(_("External service timed out. Please try again."))
    except ConnectionError:
        frappe.throw(_("Could not connect to external service."))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "External API Error")
        frappe.throw(_("External service error. Please contact support."))
```

**Why**: Technical details confuse users and may expose sensitive information.

---

## 10. Calling self.save() in Hooks

### ❌ WRONG

```python
def on_update(self):
    self.status = "Updated"
    self.save()  # INFINITE LOOP!
```

### ✅ CORRECT

```python
def on_update(self):
    # Use db_set instead
    self.db_set("status", "Updated")
    
    # Or frappe.db.set_value
    frappe.db.set_value(self.doctype, self.name, "status", "Updated")
```

**Why**: Calling `save()` triggers `on_update` again, creating infinite recursion.

---

## 11. Not Using Translation Wrapper

### ❌ WRONG

```python
def validate(self):
    frappe.throw("Customer is required")
    frappe.msgprint("Order saved successfully")
```

### ✅ CORRECT

```python
def validate(self):
    frappe.throw(_("Customer is required"))
    frappe.msgprint(_("Order saved successfully"))
```

**Why**: Without `_()`, messages won't be translated for non-English users.

---

## 12. Forgetting to Log Errors

### ❌ WRONG

```python
def on_update(self):
    try:
        self.sync_external()
    except Exception:
        pass  # No log - debugging impossible
```

### ✅ CORRECT

```python
def on_update(self):
    try:
        self.sync_external()
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"External sync failed for {self.name}"
        )
```

**Why**: Without logs, tracking down issues in production is nearly impossible.

---

## 13. Broad Exception Handling Without Specificity

### ❌ WRONG

```python
def validate(self):
    try:
        # Many operations
        self.check_customer()
        self.validate_items()
        self.calculate_totals()
    except Exception:
        frappe.throw(_("Validation failed"))
```

### ✅ CORRECT

```python
def validate(self):
    try:
        self.check_customer()
    except frappe.DoesNotExistError:
        frappe.throw(_("Customer not found"))
    
    try:
        self.validate_items()
    except frappe.ValidationError:
        raise  # Re-raise validation errors
    
    self.calculate_totals()  # Let errors propagate
```

**Why**: Specific exception handling provides better error messages and debugging.

---

## 14. Not Checking Database Results

### ❌ WRONG

```python
def validate(self):
    # Assumes record exists
    customer = frappe.get_doc("Customer", self.customer)
    
    # Assumes query returns results
    prices = frappe.db.sql("SELECT price FROM tabPrices WHERE item=%s", self.item)
    price = prices[0][0]  # IndexError if empty!
```

### ✅ CORRECT

```python
def validate(self):
    if not frappe.db.exists("Customer", self.customer):
        frappe.throw(_("Customer not found"))
    customer = frappe.get_doc("Customer", self.customer)
    
    prices = frappe.db.sql("SELECT price FROM tabPrices WHERE item=%s", self.item)
    price = prices[0][0] if prices else 0
```

**Why**: Always verify data exists before accessing it.

---

## 15. Heavy Operations in validate

### ❌ WRONG

```python
def validate(self):
    # Slow operations block save
    self.sync_all_items_to_external_api()  # Takes 30 seconds!
    self.generate_pdf_report()
    self.send_emails_to_all_stakeholders()
```

### ✅ CORRECT

```python
def validate(self):
    # Only validation logic here
    self.validate_items()

def on_update(self):
    # Queue heavy operations
    frappe.enqueue(
        "myapp.tasks.sync_items",
        doctype=self.doctype,
        name=self.name,
        queue="long"
    )
```

**Why**: Heavy operations in `validate` make the UI unresponsive and can timeout.

---

## 16. Using frappe.throw() in on_cancel for Cleanup

### ❌ WRONG

```python
def on_cancel(self):
    # If this throws, later cleanup doesn't run!
    self.reverse_stock_entries()  # throws on error
    self.reverse_gl_entries()     # never reached
    self.update_linked_docs()     # never reached
```

### ✅ CORRECT

```python
def on_cancel(self):
    errors = []
    
    try:
        self.reverse_stock_entries()
    except Exception as e:
        errors.append(f"Stock: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "Stock Reversal Error")
    
    try:
        self.reverse_gl_entries()
    except Exception as e:
        errors.append(f"GL: {str(e)}")
        frappe.log_error(frappe.get_traceback(), "GL Reversal Error")
    
    try:
        self.update_linked_docs()
    except Exception as e:
        errors.append(f"Linked docs: {str(e)}")
    
    if errors:
        frappe.msgprint(
            _("Cancelled with errors: {0}").format("<br>".join(errors)),
            indicator="orange"
        )
```

**Why**: Cancel cleanup should try to complete all operations, logging errors for manual review.

---

## Quick Checklist: Controller Review

Before deploying controllers:

- [ ] `super()` called in all overridden methods
- [ ] No `frappe.db.commit()` calls
- [ ] No `self.save()` in hooks
- [ ] Changes in `on_update` use `db_set()`
- [ ] Multiple errors collected before throwing
- [ ] Exceptions logged with `frappe.log_error()`
- [ ] User-facing messages use `_()`
- [ ] None/empty values handled safely
- [ ] Critical validations in `before_submit` not `on_submit`
- [ ] Independent `on_update` operations isolated in try/except
- [ ] Heavy operations enqueued, not inline
- [ ] Database results checked before access
- [ ] Specific exceptions caught before generic `Exception`
