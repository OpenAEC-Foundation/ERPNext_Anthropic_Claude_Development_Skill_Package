# Error Handling Reference

Error patterns en exception types voor Whitelisted Methods.

## frappe.throw()

Toont error message aan gebruiker en stopt uitvoering.

### Basis Syntax

```python
frappe.throw(
    msg,              # Error message (gebruik _() voor vertaling)
    exc=None,         # Exception class (optioneel)
    title=None,       # Dialog titel (optioneel)
    is_minimizable=False,  # Minimizable dialog (optioneel)
    wide=False,       # Wide dialog (optioneel)
    as_list=False     # Message als list tonen (optioneel)
)
```

### Voorbeelden

```python
# Basis error
frappe.throw(_("Required field is missing"))

# Met titel
frappe.throw(
    _("Please fill all required fields"),
    title=_("Validation Error")
)

# Met exception type
frappe.throw(
    _("Not permitted to access this document"),
    frappe.PermissionError
)

# Met waarde in message
frappe.throw(
    _("Amount {0} exceeds maximum {1}").format(amount, max_amount),
    frappe.ValidationError
)
```

---

## Exception Types

### Beschikbare Exception Classes

| Exception | HTTP Code | Wanneer Gebruiken |
|-----------|-----------|-------------------|
| `frappe.ValidationError` | 417 | Input validatie fouten |
| `frappe.PermissionError` | 403 | Toegang geweigerd |
| `frappe.DoesNotExistError` | 404 | Document niet gevonden |
| `frappe.DuplicateEntryError` | 409 | Duplicate record |
| `frappe.AuthenticationError` | 401 | Niet geauthenticeerd |
| `frappe.OutgoingEmailError` | 500 | Email verzenden mislukt |
| `frappe.MandatoryError` | 417 | Verplicht veld ontbreekt |
| `frappe.TimestampMismatchError` | 409 | Document gewijzigd door ander |
| `frappe.DataError` | 417 | Data integriteits fout |

### Exception Gebruik

```python
@frappe.whitelist()
def process_order(order_id):
    # Document niet gevonden
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

Log errors naar Error Log DocType.

```python
@frappe.whitelist()
def external_api_call(data):
    try:
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        # Log volledige traceback
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
# Error log (standaard)
frappe.log_error("Something went wrong", "Module Error")

# Met traceback
frappe.log_error(frappe.get_traceback(), "Critical Error")

# Custom title voor filtering
frappe.log_error(
    f"Failed to process customer {customer_id}",
    "Customer Processing"
)
```

---

## Response Structuren

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

## Try/Except Patronen

### Basis Pattern

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

### Pattern met Cleanup

```python
@frappe.whitelist()
def transactional_operation(data):
    doc = None
    try:
        doc = frappe.get_doc(data)
        doc.insert()
        
        # Verdere operaties
        process_related(doc.name)
        
        return {"success": True, "name": doc.name}
        
    except Exception:
        # Cleanup bij fout
        if doc and doc.name:
            frappe.delete_doc(doc.doctype, doc.name, force=True)
        
        frappe.log_error(frappe.get_traceback(), "Transaction Error")
        frappe.throw(_("Operation failed and was rolled back"))
```

---

## Custom HTTP Status Codes

### Status Code Zetten

```python
@frappe.whitelist()
def api_with_status(param):
    if not param:
        frappe.local.response["http_status_code"] = 400
        return {"error": "Parameter required"}
    
    if not frappe.db.exists("Item", param):
        frappe.local.response["http_status_code"] = 404
        return {"error": "Item not found"}
    
    # Success - explicit 200 (optioneel, is default)
    frappe.local.response["http_status_code"] = 200
    return {"item": frappe.get_doc("Item", param).as_dict()}
```

### Veelgebruikte Codes

| Code | Betekenis | Wanneer |
|------|-----------|---------|
| 200 | OK | Success (default) |
| 201 | Created | Nieuw document aangemaakt |
| 400 | Bad Request | Input validatie fout |
| 401 | Unauthorized | Niet ingelogd |
| 403 | Forbidden | Geen permission |
| 404 | Not Found | Document bestaat niet |
| 409 | Conflict | Duplicate of versie conflict |
| 429 | Too Many Requests | Rate limit bereikt |
| 500 | Internal Server Error | Onverwachte fout |

---

## Validation Helpers

### Input Type Validatie

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

### 1. Nooit Raw Exceptions Tonen

```python
# ❌ FOUT
except Exception as e:
    frappe.throw(str(e))  # Kan stack traces lekken!

# ✅ GOED
except Exception:
    frappe.log_error(frappe.get_traceback(), "Error Title")
    frappe.throw(_("An error occurred. Please contact support."))
```

### 2. Specifieke Exceptions Eerst

```python
# ✅ GOED - specifiek naar algemeen
try:
    # code
except frappe.DoesNotExistError:
    # specifieke handling
except frappe.PermissionError:
    # specifieke handling
except Exception:
    # catch-all voor onverwachte errors
```

### 3. Informatieve Error Messages

```python
# ❌ FOUT - niet informatief
frappe.throw(_("Error"))

# ✅ GOED - context meegeven
frappe.throw(
    _("Cannot submit Sales Order {0}: status is {1}").format(doc.name, doc.status),
    title=_("Submission Failed")
)
```

### 4. Log Context Meegeven

```python
# ❌ FOUT - geen context
frappe.log_error(frappe.get_traceback(), "Error")

# ✅ GOED - context voor debugging
frappe.log_error(
    f"User: {frappe.session.user}\nDocType: {doctype}\nName: {name}\n\n{frappe.get_traceback()}",
    f"API Error: {doctype}"
)
```
