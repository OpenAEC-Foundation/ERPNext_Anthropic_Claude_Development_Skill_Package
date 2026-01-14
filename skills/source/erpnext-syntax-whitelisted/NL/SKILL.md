---
name: erpnext-syntax-whitelisted
description: Deterministische syntax voor Frappe Whitelisted Methods (Python API endpoints). Gebruik wanneer Claude code moet genereren voor API functies, REST endpoints, @frappe.whitelist() decorator, frappe.call() of frm.call() aanroepen, permission checks in APIs, error handling patterns, of wanneer vragen gaan over API structuur, response formats, of client-server communicatie. Triggers: "whitelisted", "API endpoint", "frappe.call", "frm.call", "REST API", "@frappe.whitelist", "allow_guest", "API method".
---

# ERPNext Syntax: Whitelisted Methods

Whitelisted Methods maken Python functies beschikbaar als REST API endpoints.

## Quick Reference

### Basis Whitelisted Method

```python
import frappe

@frappe.whitelist()
def get_customer_summary(customer):
    """Basis API endpoint - alleen voor ingelogde users."""
    if not frappe.has_permission("Customer", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return frappe.get_doc("Customer", customer).as_dict()
```

### Endpoint URL

`/api/method/myapp.api.get_customer_summary`

---

## Decorator Opties

| Parameter | Default | Beschrijving |
|-----------|---------|--------------|
| `allow_guest` | `False` | `True` = toegankelijk zonder login |
| `methods` | Alle | `["GET"]`, `["POST"]`, of combinatie |
| `xss_safe` | `False` | `True` = HTML niet escapen |

```python
# Public endpoint, alleen POST
@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_contact_form(name, email, message):
    # Valideer input extra zorgvuldig bij guest access!
    if not name or not email:
        frappe.throw(_("Name and email required"))
    return {"success": True}

# Read-only endpoint
@frappe.whitelist(methods=["GET"])
def get_status(order_id):
    return frappe.db.get_value("Sales Order", order_id, "status")
```

**Volledige opties**: Zie [decorator-options.md](references/decorator-options.md)

---

## Permission Patterns

### ALTIJD Permission Checken

```python
@frappe.whitelist()
def get_data(doctype, name):
    # Check VOORDAT data wordt opgehaald
    if not frappe.has_permission(doctype, "read", name):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    return frappe.get_doc(doctype, name).as_dict()
```

### Role-Based Access

```python
@frappe.whitelist()
def admin_function():
    frappe.only_for("System Manager")  # Throws als user geen System Manager is
    return {"admin_data": "sensitive"}

@frappe.whitelist()
def multi_role_function():
    frappe.only_for(["System Manager", "HR Manager"])
    return {"data": "value"}
```

**Security patterns**: Zie [permission-patterns.md](references/permission-patterns.md)

---

## Error Handling

### frappe.throw() voor User-Facing Errors

```python
@frappe.whitelist()
def process_order(order_id, amount):
    # Validation error
    if not order_id:
        frappe.throw(_("Order ID required"), title=_("Missing Data"))
    
    # Permission error
    if not frappe.has_permission("Sales Order", "write"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    # Business logic error
    if amount < 0:
        frappe.throw(
            _("Amount cannot be negative: {0}").format(amount),
            frappe.ValidationError
        )
```

### Exception Types en HTTP Codes

| Exception | HTTP Code | Wanneer |
|-----------|-----------|---------|
| `frappe.ValidationError` | 417 | Validation fouten |
| `frappe.PermissionError` | 403 | Geen toegang |
| `frappe.DoesNotExistError` | 404 | Niet gevonden |
| `frappe.DuplicateEntryError` | 409 | Duplicate |
| `frappe.AuthenticationError` | 401 | Niet ingelogd |

### Robust Error Pattern

```python
@frappe.whitelist()
def robust_api(param):
    try:
        result = process_data(param)
        return {"success": True, "data": result}
    except frappe.DoesNotExistError:
        frappe.local.response["http_status_code"] = 404
        return {"success": False, "error": "Not found"}
    except frappe.PermissionError:
        frappe.local.response["http_status_code"] = 403
        return {"success": False, "error": "Access denied"}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "API Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "error": "Internal error"}
```

**Volledige error patterns**: Zie [error-handling.md](references/error-handling.md)

---

## Response Patterns

### Return Value (Aanbevolen)

```python
@frappe.whitelist()
def get_summary(customer):
    return {
        "customer": customer,
        "total": 15000
    }
# Response: {"message": {"customer": "...", "total": 15000}}
```

### Custom HTTP Status

```python
@frappe.whitelist()
def create_item(data):
    if not data:
        frappe.local.response["http_status_code"] = 400
        return {"error": "Data required"}
    # ... create item
    frappe.local.response["http_status_code"] = 201
    return {"created": True}
```

**Volledige response patterns**: Zie [response-patterns.md](references/response-patterns.md)

---

## Client Aanroepen

### frappe.call() - Standalone APIs

```javascript
// Promise-based (aanbevolen)
frappe.call({
    method: 'myapp.api.get_customer_summary',
    args: { customer: 'CUST-00001' }
}).then(r => {
    console.log(r.message);
});

// Met loading indicator
frappe.call({
    method: 'myapp.api.process_data',
    args: { data: myData },
    freeze: true,
    freeze_message: __('Processing...')
});
```

### frm.call() - Controller Methods

```javascript
frm.call('calculate_taxes', {
    include_shipping: true
}).then(r => {
    frm.set_value('tax_amount', r.message.tax_amount);
});
```

**Volledige client patterns**: Zie [client-calls.md](references/client-calls.md)

---

## Decision Tree: Welke Opties?

```
Wie mag de API aanroepen?
│
├─► Iedereen (ook niet-ingelogd)?
│   └─► allow_guest=True + extra input validatie
│
└─► Alleen ingelogde users?
    │
    └─► Specifieke rol vereist?
        ├─► Ja → frappe.only_for("RolNaam") in method
        └─► Nee → frappe.has_permission() check

Welke HTTP methods?
│
├─► Alleen lezen?
│   └─► methods=["GET"]
│
├─► Alleen schrijven?
│   └─► methods=["POST"]
│
└─► Beide?
    └─► methods=["GET", "POST"] of default (alle)
```

---

## Security Checklist

Bij ELKE whitelisted method:

- [ ] Permission check aanwezig (`frappe.has_permission()` of `frappe.only_for()`)
- [ ] Input validatie (types, ranges, formats)
- [ ] Geen SQL injection (parameterized queries)
- [ ] Geen sensitive data in error messages
- [ ] `allow_guest=True` alleen met expliciete reden
- [ ] `ignore_permissions=True` alleen met role check
- [ ] HTTP method beperkt waar mogelijk

---

## Kritieke Regels

### 1. NOOIT Permission Check Overslaan

```python
# ❌ FOUT - iedereen kan alle data zien
@frappe.whitelist()
def get_all_salaries():
    return frappe.get_all("Salary Slip", fields=["*"])

# ✅ GOED
@frappe.whitelist()
def get_salaries():
    frappe.only_for("HR Manager")
    return frappe.get_all("Salary Slip", fields=["*"])
```

### 2. NOOIT User Input in SQL

```python
# ❌ FOUT - SQL injection!
@frappe.whitelist()
def search(term):
    return frappe.db.sql(f"SELECT * FROM tabCustomer WHERE name LIKE '%{term}%'")

# ✅ GOED - parameterized
@frappe.whitelist()
def search(term):
    return frappe.db.sql("""
        SELECT * FROM tabCustomer WHERE name LIKE %(term)s
    """, {"term": f"%{term}%"}, as_dict=True)
```

### 3. NOOIT Sensitive Data in Errors

```python
# ❌ FOUT - lekt interne informatie
except Exception as e:
    frappe.throw(str(e))  # Kan stack traces lekken!

# ✅ GOED
except Exception:
    frappe.log_error(frappe.get_traceback(), "API Error")
    frappe.throw(_("An error occurred"))
```

**Alle anti-patterns**: Zie [anti-patterns.md](references/anti-patterns.md)

---

## Versie Verschillen (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| Type annotations validation | ❌ | ✅ |
| API v2 endpoints | ❌ | ✅ `/api/v2/` |
| Rate limiting decorators | ❌ | ✅ `@rate_limit()` |
| Document method endpoint | N/A | `/api/v2/document/{dt}/{name}/method/{m}` |

### v15 Type Validation

```python
@frappe.whitelist()
def get_orders(customer: str, limit: int = 10) -> dict:
    """v15 valideert types automatisch bij request."""
    return {"orders": frappe.get_all("Sales Order", limit=limit)}
```

---

## Reference Bestanden

| Bestand | Inhoud |
|---------|--------|
| [decorator-options.md](references/decorator-options.md) | Alle @frappe.whitelist() parameters |
| [parameter-handling.md](references/parameter-handling.md) | Request parameters en type conversion |
| [response-patterns.md](references/response-patterns.md) | Response types en structuren |
| [client-calls.md](references/client-calls.md) | frappe.call() en frm.call() patronen |
| [permission-patterns.md](references/permission-patterns.md) | Security best practices |
| [error-handling.md](references/error-handling.md) | Error patterns en exception types |
| [examples.md](references/examples.md) | Complete werkende API voorbeelden |
| [anti-patterns.md](references/anti-patterns.md) | Wat te vermijden |
