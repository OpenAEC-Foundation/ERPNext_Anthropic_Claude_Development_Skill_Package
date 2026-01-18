# Error Handling Reference

Error patterns and exception types for Whitelisted Methods.

## frappe.throw()

Shows error message to user and stops execution.

### Basic Syntax

```python
frappe.throw(
    msg,              # Error message (use _() for translation)
    exc=None,         # Exception class (optional)
    title=None,       # Dialog title (optional)
    is_minimizable=False,  # Minimizable dialog (optional)
    wide=False,       # Wide dialog (optional)
    as_list=False     # Show message as list (optional)
)
```

### Examples

```python
# Basic error
frappe.throw(_("Required field is missing"))

# With title
frappe.throw(
    _("Please fill all required fields"),
    title=_("Validation Error")
)

# With exception type
frappe.throw(
    _("Not permitted to access this document"),
    frappe.PermissionError
)

# With value in message
frappe.throw(
    _("Amount {0} exceeds maximum {1}").format(amount, max_amount),
    frappe.ValidationError
)
```

---

## Exception Types

### Available Exception Classes

| Exception | HTTP Code | When to Use |
|-----------|-----------|-------------|
| `frappe.ValidationError` | 417 | Input validation errors |
| `frappe.PermissionError` | 403 | Access denied |
| `frappe.DoesNotExistError` | 404 | Document not found |
| `frappe.DuplicateEntryError` | 409 | Duplicate record |
| `frappe.AuthenticationError` | 401 | Not authenticated |
| `frappe.OutgoingEmailError` | 500 | Email sending failed |
| `frappe.MandatoryError` | 417 | Required field missing |
| `frappe.TimestampMismatchError` | 409 | Document modified by another |
| `frappe.DataError` | 417 | Data integrity error |

### Exception Usage

```python
@frappe.whitelist()
def process_order(order_id):
    # Document not found
    if not frappe.db.exists("Sales Order", order_id):
        frappe.throw(
            _("Order {0} not found").format(order_id),
            frappe.DoesNotExistError
        )
    
    # Permission check
    if not frappe.has_permission("Sales Order", "write", order_id):
        frappe.throw(
            _("Not permitted to modify this order"),
            frappe.PermissionError
        )
    
    # Validation
    doc = frappe.get_doc("Sales Order", order_id)
    if doc.status == "Closed":
        frappe.throw(
            _("Cannot modify closed order"),
            frappe.ValidationError
        )
```

---

## Error Logging

### frappe.log_error()

Log errors to Error Log DocType.

```python
@frappe.whitelist()
def external_api_call(data):
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        # Log full traceback
        frappe.log_error(
            frappe.get_traceback(),
            "External API Error"
        )
        
        # User-friendly message
        frappe.throw(
            _("External service unavailable. Please try later."),
            title=_("Service Error")
        )
```

### Log Levels

```python
# Error log (default)
frappe.log_error("Something went wrong", "Module Error")

# With traceback
frappe.log_error(frappe.get_traceback(), "Critical Error")

# Custom title for filtering
frappe.log_error(
    f"Failed to process customer {customer_id}",
    "Customer Processing"
)
```

---

## Response Structures

### Success Response

```json
{
    "message": {
        "success": true,
        "data": { ... }
    }
}
```

### Error Response (frappe.throw)

```json
{
    "exc_type": "ValidationError",
    "exc": "[Traceback string...]",
    "_server_messages": "[{\"message\": \"Error message\"}]"
}
```

---

## Try/Except Patterns

### Basic Pattern

```python
@frappe.whitelist()
def safe_operation(param):
    try:
        result = process_data(param)
        return {"success": True, "data": result}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Operation Error")
        frappe.throw(_("Operation failed"))
```

### Comprehensive Pattern

```python
@frappe.whitelist()
def robust_api(doctype, name):
    try:
        # Business logic
        doc = frappe.get_doc(doctype, name)
        result = doc.run_method("process")
        return {"success": True, "data": result}
        
    except frappe.DoesNotExistError:
        frappe.local.response["http_status_code"] = 404
        return {"success": False, "error": "Document not found"}
        
    except frappe.PermissionError:
        frappe.local.response["http_status_code"] = 403
        return {"success": False, "error": "Access denied"}
        
    except frappe.ValidationError as e:
        frappe.local.response["http_status_code"] = 400
        return {"success": False, "error": str(e)}
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"API Error: {doctype}/{name}")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "error": "Internal server error"}
```

### Pattern with Cleanup

```python
@frappe.whitelist()
def transactional_operation(data):
    doc = None
    try:
        doc = frappe.get_doc(data)
        doc.insert()
        
        # Further operations
        process_related(doc.name)
        
        return {"success": True, "name": doc.name}
        
    except Exception:
        # Cleanup on error
        if doc and doc.name:
            frappe.delete_doc(doc.doctype, doc.name, force=True)
        
        frappe.log_error(frappe.get_traceback(), "Transaction Error")
        frappe.throw(_("Operation failed and was rolled back"))
```

---

## Custom HTTP Status Codes

### Setting Status Code

```python
@frappe.whitelist()
def api_with_status(param):
    if not param:
        frappe.local.response["http_status_code"] = 400
        return {"error": "Parameter required"}
    
    if not frappe.db.exists("Item", param):
        frappe.local.response["http_status_code"] = 404
        return {"error": "Item not found"}
    
    # Success - explicit 200 (optional, is default)
    frappe.local.response["http_status_code"] = 200
    return {"item": frappe.get_doc("Item", param).as_dict()}
```

### Common Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Success (default) |
| 201 | Created | New document created |
| 400 | Bad Request | Input validation error |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | No permission |
| 404 | Not Found | Document doesn't exist |
| 409 | Conflict | Duplicate or version conflict |
| 429 | Too Many Requests | Rate limit reached |
| 500 | Internal Server Error | Unexpected error |

---

## Validation Helpers

### Input Type Validation

```python
@frappe.whitelist()
def validate_input(email, amount, date_str):
    # Email format
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        frappe.throw(_("Invalid email format"), frappe.ValidationError)
    
    # Numeric
    try:
        amount = float(amount)
        if amount < 0:
            frappe.throw(_("Amount cannot be negative"))
    except (TypeError, ValueError):
        frappe.throw(_("Amount must be a number"))
    
    # Date
    from frappe.utils import getdate
    try:
        date = getdate(date_str)
    except Exception:
        frappe.throw(_("Invalid date format"))
    
    return {"email": email, "amount": amount, "date": str(date)}
```

### Required Fields Check

```python
@frappe.whitelist()
def check_required(**kwargs):
    required = ["customer", "item", "qty"]
    missing = [f for f in required if not kwargs.get(f)]
    
    if missing:
        frappe.throw(
            _("Missing required fields: {0}").format(", ".join(missing)),
            frappe.ValidationError
        )
```

---

## Best Practices

### 1. Never Show Raw Exceptions

```python
# ❌ WRONG
except Exception as e:
    frappe.throw(str(e))  # May leak stack traces!

# ✅ CORRECT
except Exception:
    frappe.log_error(frappe.get_traceback(), "Error Title")
    frappe.throw(_("An error occurred. Please contact support."))
```

### 2. Specific Exceptions First

```python
# ✅ CORRECT - specific to general
try:
    # code
except frappe.DoesNotExistError:
    # specific handling
except frappe.PermissionError:
    # specific handling
except Exception:
    # catch-all for unexpected errors
```

### 3. Informative Error Messages

```python
# ❌ WRONG - not informative
frappe.throw(_("Error"))

# ✅ CORRECT - with context
frappe.throw(
    _("Cannot submit Sales Order {0}: status is {1}").format(doc.name, doc.status),
    title=_("Submission Failed")
)
```

### 4. Include Context in Logs

```python
# ❌ WRONG - no context
frappe.log_error(frappe.get_traceback(), "Error")

# ✅ CORRECT - context for debugging
frappe.log_error(
    f"User: {frappe.session.user}\nDocType: {doctype}\nName: {name}\n\n{frappe.get_traceback()}",
    f"API Error: {doctype}"
)
```
