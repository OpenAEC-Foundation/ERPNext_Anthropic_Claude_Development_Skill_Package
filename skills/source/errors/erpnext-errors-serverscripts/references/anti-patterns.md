# Anti-Patterns - Server Script Error Handling

Common mistakes to avoid when handling errors in Frappe/ERPNext Server Scripts.

---

## 1. Using try/except in Server Scripts

### ❌ WRONG

```python
# This will NOT work in Server Scripts!
try:
    result = frappe.get_doc("Customer", doc.customer)
except Exception as e:
    frappe.log_error(str(e))
```

### ✅ CORRECT

```python
# Check before access
if frappe.db.exists("Customer", doc.customer):
    result = frappe.get_doc("Customer", doc.customer)
else:
    frappe.throw(f"Customer '{doc.customer}' not found")
```

**Why**: The RestrictedPython sandbox in Server Scripts blocks try/except statements. Use conditional checks instead.

---

## 2. Using raise Statement

### ❌ WRONG

```python
if not doc.customer:
    raise ValueError("Customer is required")
```

### ✅ CORRECT

```python
if not doc.customer:
    frappe.throw("Customer is required")
```

**Why**: The `raise` statement is blocked in the sandbox. Use `frappe.throw()` instead.

---

## 3. Using import Statements

### ❌ WRONG

```python
import json
from datetime import datetime

data = json.loads(doc.json_data)
today = datetime.now().date()
```

### ✅ CORRECT

```python
# Use frappe namespace directly
data = frappe.parse_json(doc.json_data)
today = frappe.utils.today()
```

**Why**: All imports are blocked in the sandbox. Use Frappe's built-in utilities through the `frappe` namespace.

---

## 4. Not Checking if Record Exists Before get_doc

### ❌ WRONG

```python
# Will crash if customer doesn't exist
customer = frappe.get_doc("Customer", doc.customer)
credit_limit = customer.credit_limit
```

### ✅ CORRECT

```python
# Check existence first
if not frappe.db.exists("Customer", doc.customer):
    frappe.throw(f"Customer '{doc.customer}' not found")

customer = frappe.get_doc("Customer", doc.customer)
credit_limit = customer.credit_limit
```

**Or use safe value lookup:**

```python
credit_limit = frappe.db.get_value("Customer", doc.customer, "credit_limit") or 0
```

**Why**: Without existence check, missing records cause cryptic errors instead of user-friendly messages.

---

## 5. Throwing on First Error

### ❌ WRONG

```python
if not doc.customer:
    frappe.throw("Customer is required")
# User has to save multiple times to find all errors
if not doc.delivery_date:
    frappe.throw("Delivery Date is required")
if not doc.items:
    frappe.throw("Items are required")
```

### ✅ CORRECT

```python
errors = []

if not doc.customer:
    errors.append("Customer is required")
if not doc.delivery_date:
    errors.append("Delivery Date is required")
if not doc.items:
    errors.append("At least one item is required")

if errors:
    frappe.throw("<br>".join(errors), title="Please fix these errors")
```

**Why**: Users shouldn't have to save multiple times to discover all validation errors.

---

## 6. Forgetting frappe.db.commit() in Scheduler

### ❌ WRONG

```python
# Type: Scheduler Event
for item in items:
    frappe.db.set_value("Item", item.name, "last_sync", frappe.utils.now())
# Changes are lost!
```

### ✅ CORRECT

```python
# Type: Scheduler Event
for item in items:
    frappe.db.set_value("Item", item.name, "last_sync", frappe.utils.now())

frappe.db.commit()  # REQUIRED!
```

**Why**: Scheduler scripts don't auto-commit. Without explicit commit, all database changes are lost.

---

## 7. Calling doc.save() in Before Save Event

### ❌ WRONG

```python
# Type: Document Event - Before Save
doc.status = "Validated"
doc.save()  # Causes infinite loop or error!
```

### ✅ CORRECT

```python
# Type: Document Event - Before Save
doc.status = "Validated"
# Just set the value - framework handles the save
```

**Why**: The document is already being saved. Calling `save()` again causes recursion or errors.

---

## 8. Not Escaping User Input in SQL

### ❌ WRONG

```python
# SQL injection vulnerability!
territory = frappe.form_dict.get("territory")
conditions = f"`tabCustomer`.territory = '{territory}'"
```

### ✅ CORRECT

```python
territory = frappe.form_dict.get("territory")
conditions = f"`tabCustomer`.territory = {frappe.db.escape(territory)}"
```

**Why**: Unescaped user input allows SQL injection attacks.

---

## 9. Not Adding Limits to Scheduler Queries

### ❌ WRONG

```python
# Type: Scheduler Event
# Could return millions of records!
all_customers = frappe.get_all("Customer", fields=["name", "email"])

for customer in all_customers:
    send_newsletter(customer)
```

### ✅ CORRECT

```python
# Type: Scheduler Event
BATCH_SIZE = 100

customers = frappe.get_all(
    "Customer",
    filters={"newsletter_sent": 0},
    fields=["name", "email"],
    limit=BATCH_SIZE
)

for customer in customers:
    send_newsletter(customer)
    frappe.db.set_value("Customer", customer.name, "newsletter_sent", 1)

frappe.db.commit()
```

**Why**: Unlimited queries can exhaust memory and crash the worker.

---

## 10. Exposing Technical Errors to Users

### ❌ WRONG

```python
if not customer_data:
    frappe.throw(f"KeyError: 'credit_limit' not found in dict for {doc.customer}")
```

### ✅ CORRECT

```python
if not customer_data:
    frappe.throw(f"Customer '{doc.customer}' not found. Please select a valid customer.")
```

**Why**: Technical error messages confuse users. Provide clear, actionable messages.

---

## 11. Silent Failures in Scheduler

### ❌ WRONG

```python
# Type: Scheduler Event
for invoice in invoices:
    if not invoice.customer:
        continue  # Silent skip - no one knows this failed
    process(invoice)
```

### ✅ CORRECT

```python
# Type: Scheduler Event
errors = []

for invoice in invoices:
    if not invoice.customer:
        errors.append(f"{invoice.name}: Missing customer")
        continue
    process(invoice)

if errors:
    frappe.log_error("\n".join(errors), "Invoice Processing Errors")

frappe.db.commit()
```

**Why**: Scheduler errors have no user to see them. Always log errors for debugging.

---

## 12. Using Blocking Operations in Document Events

### ❌ WRONG

```python
# Type: Document Event - After Save
# Slow external API call blocks the save response
import requests  # Won't work anyway
response = requests.post("https://external-api.com/sync", json=data)
```

### ✅ CORRECT

```python
# Type: Document Event - After Save
# Queue for background processing
frappe.enqueue(
    "myapp.tasks.sync_to_external",
    queue="short",
    doc_name=doc.name
)

# Or use Scheduler script for batch processing
```

**Why**: Document events should be fast. Long operations block the UI and may timeout.

---

## 13. Assuming Values Exist in Child Tables

### ❌ WRONG

```python
total = sum(item.qty * item.rate for item in doc.items)  # Crashes if qty/rate is None
```

### ✅ CORRECT

```python
total = sum(
    (item.qty or 0) * (item.rate or 0) 
    for item in (doc.items or [])
)
```

**Why**: Child table fields can be None. Always provide defaults.

---

## 14. Not Handling Empty API Parameters

### ❌ WRONG

```python
# Type: API
customer = frappe.form_dict.customer  # None if not provided
data = frappe.get_all("Sales Order", filters={"customer": customer})  # Bad filter!
```

### ✅ CORRECT

```python
# Type: API
customer = frappe.form_dict.get("customer")

if not customer:
    frappe.throw("Parameter 'customer' is required", exc=frappe.ValidationError)

data = frappe.get_all("Sales Order", filters={"customer": customer})
```

**Why**: Missing parameters should be caught early with clear error messages.

---

## 15. Ignoring Return Values

### ❌ WRONG

```python
frappe.db.get_value("Customer", doc.customer, "credit_limit")
# Value is discarded!

if credit_limit > doc.grand_total:  # credit_limit is undefined!
    frappe.throw("Credit limit exceeded")
```

### ✅ CORRECT

```python
credit_limit = frappe.db.get_value("Customer", doc.customer, "credit_limit") or 0

if credit_limit > 0 and doc.grand_total > credit_limit:
    frappe.throw(f"Credit limit exceeded. Limit: {credit_limit}")
```

**Why**: Database lookups must be assigned to variables to be used.

---

## 16. Wrong Exception Type for API Errors

### ❌ WRONG

```python
# Type: API
if not frappe.db.exists("Customer", customer):
    frappe.throw("Customer not found")  # Returns 417 (wrong!)
```

### ✅ CORRECT

```python
# Type: API
if not frappe.db.exists("Customer", customer):
    frappe.throw("Customer not found", exc=frappe.DoesNotExistError)  # Returns 404
```

**Why**: Correct HTTP status codes help API consumers handle errors properly.

---

## 17. Modifying doc After on_update

### ❌ WRONG

```python
# Type: Document Event - After Save (on_update)
doc.sync_status = "Synced"
doc.sync_date = frappe.utils.now()
# Changes are NOT saved!
```

### ✅ CORRECT

```python
# Type: Document Event - After Save (on_update)
frappe.db.set_value(doc.doctype, doc.name, {
    "sync_status": "Synced",
    "sync_date": frappe.utils.now()
})
```

**Why**: After the save event, changes to `doc` are not automatically persisted. Use `frappe.db.set_value()` instead.

---

## Quick Checklist: Server Script Error Handling Review

Before deploying server scripts, verify:

- [ ] No try/except statements (use conditional checks)
- [ ] No raise statements (use frappe.throw)
- [ ] No import statements (use frappe namespace)
- [ ] All database lookups have existence checks
- [ ] Multiple validation errors are collected and thrown together
- [ ] Scheduler scripts have frappe.db.commit()
- [ ] Scheduler scripts have query limits
- [ ] No doc.save() in Before Save events
- [ ] All user input is escaped in SQL conditions
- [ ] API scripts use correct exception types
- [ ] Scheduler errors are logged
- [ ] Technical errors are not exposed to users
- [ ] Child table values have defaults (or 0)
