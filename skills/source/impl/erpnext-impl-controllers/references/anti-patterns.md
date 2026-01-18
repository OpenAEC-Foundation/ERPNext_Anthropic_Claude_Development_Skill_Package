# Controller Anti-Patterns

Common mistakes to avoid when implementing Frappe controllers.

## Anti-Pattern 1: Modifying self After on_update

### ❌ Wrong

```python
def on_update(self):
    self.status = "Completed"  # NOT SAVED!
    self.processed_date = frappe.utils.today()  # NOT SAVED!
```

**Why it fails**: After `on_update`, the document has already been written to the database. Changes to `self` are only in memory and will be lost.

### ✅ Correct

```python
def on_update(self):
    # Use db_set for post-save changes
    frappe.db.set_value(self.doctype, self.name, {
        "status": "Completed",
        "processed_date": frappe.utils.today()
    })
    
    # Or single field
    frappe.db.set_value(self.doctype, self.name, "status", "Completed")
```

## Anti-Pattern 2: Calling self.save() in on_update

### ❌ Wrong

```python
def on_update(self):
    self.counter = (self.counter or 0) + 1
    self.save()  # INFINITE LOOP!
```

**Why it fails**: `save()` triggers `on_update` again, creating an infinite loop that will crash the system.

### ✅ Correct

```python
def on_update(self):
    # Use db_set which doesn't trigger hooks
    new_counter = (self.counter or 0) + 1
    frappe.db.set_value(self.doctype, self.name, "counter", new_counter, 
                       update_modified=False)
```

## Anti-Pattern 3: Manual Commits

### ❌ Wrong

```python
def validate(self):
    self.do_something()
    frappe.db.commit()  # DON'T DO THIS

def on_update(self):
    self.update_related()
    frappe.db.commit()  # DON'T DO THIS
```

**Why it fails**: Frappe manages transactions automatically. Manual commits can break rollback behavior and cause partial updates on errors.

### ✅ Correct

```python
def validate(self):
    self.do_something()
    # No commit needed - Frappe handles it

def on_update(self):
    self.update_related()
    # No commit needed - Frappe handles it
```

## Anti-Pattern 4: Heavy Operations in validate

### ❌ Wrong

```python
def validate(self):
    # This blocks the save for the user
    self.process_large_dataset()  # Takes 30 seconds
    self.generate_reports()  # Takes 1 minute
    self.sync_to_external_api()  # Network calls
```

**Why it fails**: `validate` runs synchronously before save. Long operations block the UI and can timeout.

### ✅ Correct

```python
def validate(self):
    # Only quick validations
    self.validate_required_fields()
    self.calculate_totals()

def on_update(self):
    # Queue heavy operations for background
    if self.needs_processing:
        frappe.enqueue(
            'myapp.tasks.process_document',
            queue='long',
            timeout=300,
            doc_name=self.name
        )
```

## Anti-Pattern 5: Not Calling super() in Override

### ❌ Wrong

```python
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # Missing super().validate()!
        self.custom_validation()
```

**Why it fails**: Standard ERPNext validations and calculations are skipped, leading to inconsistent data and broken functionality.

### ✅ Correct

```python
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # ALWAYS call parent first
        self.custom_validation()
```

## Anti-Pattern 6: Assuming Hook Execution Order Across Documents

### ❌ Wrong

```python
def on_update(self):
    # Assuming other_doc's hooks have completed
    other_doc = frappe.get_doc("Other", self.link)
    other_doc.some_field = "value"
    other_doc.save()  # This triggers OTHER doc's hooks
    
    # Assuming other_doc.on_update has run
    result = frappe.db.get_value("Other", self.link, "computed_field")
```

**Why it fails**: Each document has its own hook cycle. Saving another document from within your hooks creates nested cycles that are hard to reason about.

### ✅ Correct

```python
def on_update(self):
    # Use db_set to avoid triggering other doc's hooks
    frappe.db.set_value("Other", self.link, "some_field", "value")
    
    # Or use flags to prevent recursive updates
    other_doc = frappe.get_doc("Other", self.link)
    other_doc.flags.from_parent_update = True
    other_doc.some_field = "value"
    other_doc.save()

# In Other doctype's controller
def on_update(self):
    if self.flags.get('from_parent_update'):
        return  # Skip to prevent recursion
    # Normal processing
```

## Anti-Pattern 7: Ignoring Permissions Without Reason

### ❌ Wrong

```python
def after_insert(self):
    # Always bypassing permissions "just to be safe"
    doc = frappe.get_doc({"doctype": "Task", "subject": "Test"})
    doc.flags.ignore_permissions = True
    doc.insert()
```

**Why it fails**: Bypassing permissions can create security holes and audit trail issues.

### ✅ Correct

```python
def after_insert(self):
    # Only bypass when there's a valid reason
    doc = frappe.get_doc({"doctype": "Task", "subject": "Test"})
    
    # System-generated documents may need permission bypass
    if self.is_system_generated:
        doc.flags.ignore_permissions = True
    
    doc.insert()
```

## Anti-Pattern 8: Using get_doc Without Caching

### ❌ Wrong

```python
def validate(self):
    for item in self.items:
        # Fetches same customer doc multiple times!
        customer = frappe.get_doc("Customer", self.customer)
        item.credit_limit = customer.credit_limit
```

**Why it fails**: `get_doc` queries the database every time. In loops, this creates N queries for the same document.

### ✅ Correct

```python
def validate(self):
    # Cache the document for reuse
    customer = frappe.get_cached_doc("Customer", self.customer)
    
    for item in self.items:
        item.credit_limit = customer.credit_limit

# Or for single values
def validate(self):
    credit_limit = frappe.db.get_value("Customer", self.customer, "credit_limit")
    for item in self.items:
        item.credit_limit = credit_limit
```

## Anti-Pattern 9: Swallowing All Exceptions

### ❌ Wrong

```python
def on_update(self):
    try:
        self.send_notification()
        self.update_external_system()
        self.process_data()
    except:
        pass  # Silent failure - no idea what went wrong
```

**Why it fails**: Errors are hidden, making debugging impossible. You won't know when things break.

### ✅ Correct

```python
def on_update(self):
    # Non-critical operations should log errors
    try:
        self.send_notification()
    except Exception:
        frappe.log_error(f"Failed to send notification for {self.name}")
    
    # Critical operations should fail loudly
    self.update_ledger()  # Let it throw if it fails
```

## Anti-Pattern 10: Duplicate Code in validate and before_submit

### ❌ Wrong

```python
def validate(self):
    if not self.items:
        frappe.throw(_("Items required"))
    self.total = sum(item.amount for item in self.items)

def before_submit(self):
    # Duplicating validation from validate!
    if not self.items:
        frappe.throw(_("Items required"))
    self.total = sum(item.amount for item in self.items)
```

**Why it fails**: `validate` already runs before `before_submit`. Duplicating logic is wasteful and error-prone when one is updated but not the other.

### ✅ Correct

```python
def validate(self):
    # Common validations and calculations
    self.validate_items()
    self.calculate_totals()

def validate_items(self):
    if not self.items:
        frappe.throw(_("Items required"))

def calculate_totals(self):
    self.total = sum(item.amount for item in self.items)

def before_submit(self):
    # ONLY submit-specific validations
    if self.total > 50000 and not self.approval:
        frappe.throw(_("Approval required for high value"))
```

## Anti-Pattern 11: Using datetime Instead of frappe.utils

### ❌ Wrong

```python
from datetime import datetime, timedelta

def validate(self):
    self.created_date = datetime.now()
    self.due_date = datetime.now() + timedelta(days=30)
```

**Why it fails**: Timezone issues, format incompatibilities with Frappe's date handling, and doesn't respect user's date format preferences.

### ✅ Correct

```python
def validate(self):
    self.created_date = frappe.utils.now()
    self.due_date = frappe.utils.add_days(frappe.utils.today(), 30)
```

## Anti-Pattern 12: Hardcoded Values

### ❌ Wrong

```python
def validate(self):
    if self.amount > 50000:
        self.requires_approval = 1
    
    self.tax_rate = 0.18  # 18% VAT
```

**Why it fails**: Values change, and changes require code deployments. Different companies/sites may need different values.

### ✅ Correct

```python
def validate(self):
    settings = frappe.get_cached_doc("My Settings", "My Settings")
    
    if self.amount > settings.approval_threshold:
        self.requires_approval = 1
    
    self.tax_rate = settings.default_tax_rate
```

## Anti-Pattern 13: Sending Emails Synchronously

### ❌ Wrong

```python
def on_submit(self):
    # Blocks until all emails are sent
    for recipient in self.get_all_recipients():
        frappe.sendmail(
            recipients=[recipient],
            subject=f"Document {self.name} submitted",
            message="Your document has been submitted."
        )
```

**Why it fails**: Sending many emails blocks the request. Email server issues will fail the submit.

### ✅ Correct

```python
def on_submit(self):
    # Queue emails for background sending
    frappe.enqueue(
        'myapp.notifications.send_submit_notifications',
        queue='short',
        doc_name=self.name,
        doctype=self.doctype
    )

# Or use Frappe's built-in async
def on_submit(self):
    frappe.sendmail(
        recipients=self.get_all_recipients(),
        subject=f"Document {self.name} submitted",
        message="Your document has been submitted.",
        now=False  # Queue for background sending
    )
```

## Quick Reference: What NOT To Do

| Don't | Do Instead |
|-------|------------|
| `self.x = y` in on_update | `frappe.db.set_value(...)` |
| `self.save()` in on_update | `frappe.db.set_value(...)` |
| `frappe.db.commit()` anywhere | Let framework handle it |
| Heavy processing in validate | Use `frappe.enqueue()` |
| Skip `super().validate()` | Always call parent first |
| `except: pass` | Log errors properly |
| `frappe.get_doc()` in loops | Use `frappe.get_cached_doc()` |
| Hardcode thresholds/rates | Use Settings DocType |
| Synchronous emails | Use `now=False` or enqueue |
| Duplicate logic across hooks | Refactor to shared methods |
