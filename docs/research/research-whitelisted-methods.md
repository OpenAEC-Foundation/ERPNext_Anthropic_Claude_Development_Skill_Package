# Research Document: Whitelisted Methods (Fase 2.3)

> **Doel**: VerifiÃ«ren, verdiepen en actualiseren van informatie uit erpnext-vooronderzoek.md sectie 5 (Whitelisted Methods) voor Frappe v14/v15.

---

## Bronnen Geraadpleegd

| Bron | URL/Locatie | Type |
|------|-------------|------|
| Frappe Docs - REST API | docs.frappe.io/framework/user/en/api/rest | Primair |
| Frappe Docs - REST API Guide | docs.frappe.io/framework/user/en/guides/integration/rest_api | Primair |
| Frappe Docs - Responses | docs.frappe.io/framework/user/en/python-api/response | Primair |
| Frappe Docs - Form Scripts | docs.frappe.io/framework/user/en/api/form | Primair |
| Frappe GitHub - __init__.py | github.com/frappe/frappe/.../frappe/__init__.py | Verificatie |
| Frappe GitHub - user.py | github.com/frappe/frappe/.../user/user.py | Verificatie |
| ERPNext Wiki - Security Guidelines | github.com/frappe/erpnext/wiki/Code-Security-Guidelines | Best Practices |
| erpnext-vooronderzoek.md | Project bestand | Basis |

---

## 1. DECORATOR OPTIES

### @frappe.whitelist() Signature (Geverifieerd uit GitHub source)

```python
def whitelist(
    allow_guest: bool = False,
    xss_safe: bool = False,
    methods: list[str] | None = None
) -> Callable
```

### Beschikbare Parameters

| Parameter | Type | Default | Beschrijving |
|-----------|------|---------|--------------|
| `allow_guest` | bool | `False` | Toegang voor niet-ingelogde gebruikers (Guest role) |
| `xss_safe` | bool | `False` | Schakelt HTML escaping uit in response |
| `methods` | list[str] | `["GET", "POST", "PUT", "DELETE"]` | Toegestane HTTP methods |

### Voorbeeld Gebruik

```python
import frappe

# Standaard - alleen authenticated users
@frappe.whitelist()
def get_data():
    return {"status": "ok"}

# Toegankelijk voor iedereen (ook niet-ingelogde)
@frappe.whitelist(allow_guest=True)
def public_endpoint():
    return {"public": True}

# Alleen POST requests toegestaan
@frappe.whitelist(methods=["POST"])
def create_record(data):
    doc = frappe.get_doc(data)
    doc.insert()
    return doc.name

# HTML content zonder escaping
@frappe.whitelist(xss_safe=True)
def get_html_content():
    return "<strong>HTML content</strong>"

# Combinatie van opties
@frappe.whitelist(allow_guest=True, methods=["POST"])
def public_submit(email):
    # Guest kan dit aanroepen met POST
    return {"received": email}
```

### Locatie van Whitelisted Methods

Methods kunnen op verschillende locaties worden gedefinieerd:

| Locatie | Pad | Voorbeeld URL |
|---------|-----|---------------|
| Custom API module | `myapp/api.py` | `/api/method/myapp.api.my_function` |
| DocType controller | `myapp/doctype/todo/todo.py` | Via `frm.call('method')` |
| __init__.py van app | `myapp/__init__.py` | `/api/method/myapp.my_function` |
| Elke Python module | `myapp/utils/helpers.py` | `/api/method/myapp.utils.helpers.my_function` |

**Best Practice**: Groepeer API functies in een dedicated `api.py` module.

---

## 2. PARAMETER HANDLING

### Toegang tot Request Parameters

```python
@frappe.whitelist()
def process_data(customer, items=None, include_draft=False):
    # Parameters worden automatisch doorgegeven als function arguments
    # Type conversion gebeurt automatisch waar mogelijk
    
    # Alternatief: direct via form_dict
    all_params = frappe.form_dict  # dict met alle request parameters
    customer = frappe.form_dict.get('customer')
    
    # Of via frappe.local
    customer = frappe.local.form_dict.get('customer')
    
    return {"customer": customer, "item_count": len(items or [])}
```

### Type Conversion

Frappe converteert automatisch string parameters naar de juiste types waar mogelijk:

| Input Type | Python Type | Opmerkingen |
|------------|-------------|-------------|
| String "123" | int | Als parameter hint of expliciet |
| String "true" | bool | `"true"`, `"1"` â†’ `True` |
| JSON array | list | Automatisch geparsed |
| JSON object | dict | Automatisch geparsed |

### JSON Data Parsing

```python
@frappe.whitelist(methods=["POST"])
def create_items(data):
    # data kan als JSON string binnenkomen
    if isinstance(data, str):
        data = frappe.parse_json(data)
    
    # Of gebruik json.loads direct
    import json
    if isinstance(data, str):
        data = json.loads(data)
    
    for item in data.get('items', []):
        # process items
        pass
    
    return {"processed": True}
```

### Type Annotations (v15+)

Frappe v15 ondersteunt type validation via type annotations:

```python
from typing import TYPE_CHECKING

@frappe.whitelist()
def get_customer_data(customer: str, limit: int = 10) -> dict:
    """
    Type annotations worden gevalideerd als request binnenkomt.
    Verkeerde types resulteren in ValidationError.
    """
    orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer},
        limit=limit
    )
    return {"orders": orders}
```

---

## 3. RESPONSE PATTERNS

### Return Value (Aanbevolen)

De meest eenvoudige manier - return value wordt automatisch JSON:

```python
@frappe.whitelist()
def get_customer_summary(customer):
    orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer, "docstatus": 1},
        fields=["sum(grand_total) as total", "count(name) as count"]
    )[0]
    
    # Return dict wordt automatisch {"message": {...}}
    return {
        "customer": customer,
        "total_orders": orders.count,
        "total_value": orders.total or 0
    }
```

**Response**:
```json
{
    "message": {
        "customer": "Customer ABC",
        "total_orders": 5,
        "total_value": 15000
    }
}
```

### frappe.response Object

Voor meer controle over de response:

```python
@frappe.whitelist()
def get_custom_data(param):
    # Zet response direct
    frappe.response["message"] = {"data": "value"}
    
    # Extra velden toevoegen
    frappe.response["count"] = 10
    frappe.response["status"] = "success"
    
    # Geen return nodig (maar kan wel)
```

### Response Types

| Type | Gebruik | Voorbeeld |
|------|---------|-----------|
| `json` (default) | API responses | Automatisch |
| `download` | File downloads | Zie onder |
| `csv` | CSV export | Via frappe.response.type |
| `pdf` | PDF download | Via frappe.response.type |
| `redirect` | HTTP redirect | Via frappe.response.type |
| `binary` | Binary data | Via frappe.response.type |

### File Download Response

```python
@frappe.whitelist()
def download_file(name):
    file = frappe.get_doc("File", name)
    
    frappe.response.filename = file.file_name
    frappe.response.filecontent = file.get_content()
    frappe.response.type = "download"
    frappe.response.display_content_as = "attachment"  # of "inline"
```

### HTTP Status Codes

```python
@frappe.whitelist()
def custom_endpoint(param):
    if not param:
        # Zet custom HTTP status code
        frappe.local.response["http_status_code"] = 400
        return {"error": "Parameter required"}
    
    # Success (default 200)
    return {"success": True}
```

**Beschikbare status code patterns**:

```python
# 400 Bad Request
frappe.local.response["http_status_code"] = 400

# 404 Not Found
frappe.local.response["http_status_code"] = 404

# 403 Forbidden
frappe.local.response["http_status_code"] = 403

# 429 Too Many Requests (rate limiting)
frappe.local.response["http_status_code"] = 429
```

---

## 4. PERMISSIONS

### frappe.has_permission()

```python
@frappe.whitelist()
def get_sensitive_data(doctype, name):
    # Check permission VOOR data ophalen
    if not frappe.has_permission(doctype, "read", name):
        frappe.throw(
            _("No permission to access {0}").format(name),
            frappe.PermissionError
        )
    
    doc = frappe.get_doc(doctype, name)
    return doc.as_dict()
```

**has_permission Parameters**:

```python
frappe.has_permission(
    doctype,           # DocType naam
    ptype="read",      # Permission type: read, write, create, submit, cancel, delete
    doc=None,          # Optioneel: specifiek document
    user=None,         # Optioneel: specifieke user (default: huidige)
    throw=False        # Als True, throw error ipv return False
)
```

### frappe.only_for()

Restrict method tot specifieke rollen:

```python
@frappe.whitelist()
def admin_only_function():
    # Alleen System Manager mag dit aanroepen
    frappe.only_for("System Manager")
    
    # Code hier wordt alleen uitgevoerd voor System Manager
    return {"admin_data": "sensitive"}

@frappe.whitelist()
def multi_role_function():
    # Meerdere rollen toegestaan
    frappe.only_for(["System Manager", "Administrator"])
    return {"data": "value"}
```

### Permission Error Handling

```python
@frappe.whitelist()
def secure_endpoint(doctype, name, action):
    # Pattern voor veilige permission check
    try:
        frappe.has_permission(doctype, action, name, throw=True)
    except frappe.PermissionError:
        frappe.throw(
            _("You don't have permission to {0} this {1}").format(action, doctype),
            frappe.PermissionError
        )
    
    # Doorgaan met operatie
    doc = frappe.get_doc(doctype, name)
    return doc.as_dict()
```

### Belangrijke Security Overwegingen

**WAARSCHUWING**: Veelgemaakte security fouten:

```python
# âŒ FOUT - Geen permission check
@frappe.whitelist()
def get_all_customers():
    return frappe.get_all("Customer")  # Iedereen kan alle customers zien!

# âœ… GOED - Met permission check
@frappe.whitelist()
def get_customers():
    if not frappe.has_permission("Customer", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    return frappe.get_all("Customer")

# âŒ FOUT - ignore_permissions zonder goede reden
@frappe.whitelist()
def create_document(values):
    doc = frappe.get_doc(values)
    doc.insert(ignore_permissions=True)  # SECURITY RISK!
    return doc.name

# âœ… GOED - Met expliciete role check
@frappe.whitelist()
def create_document(values):
    frappe.only_for("System Manager")  # Alleen admins
    
    # Valideer doctype
    if values.get('doctype') not in ('ToDo', 'Note'):
        frappe.throw(_('Invalid Document Type'))
    
    doc = frappe.get_doc(values)
    doc.insert()  # Normale permissions
    return doc.name
```

---

## 5. AANROEPEN VANUIT CLIENT

### frappe.call() - Algemeen gebruik

```javascript
// Basis syntax
frappe.call({
    method: 'myapp.api.get_customer_summary',
    args: {
        customer: 'CUST-00001',
        include_orders: true
    },
    callback: function(r) {
        if (r.message) {
            console.log(r.message);
        }
    }
});

// Met freeze (loading indicator)
frappe.call({
    method: 'myapp.api.process_data',
    args: { data: myData },
    freeze: true,
    freeze_message: __('Processing...'),
    callback: function(r) {
        frappe.show_alert({
            message: __('Done!'),
            indicator: 'green'
        });
    }
});

// Promise-based (modern)
frappe.call({
    method: 'myapp.api.get_data',
    args: { id: 123 }
}).then(r => {
    console.log(r.message);
}).catch(err => {
    console.error(err);
});

// Async/await
async function getData() {
    let r = await frappe.call({
        method: 'myapp.api.get_data',
        args: { id: 123 }
    });
    return r.message;
}
```

### frappe.call Parameters

| Parameter | Type | Default | Beschrijving |
|-----------|------|---------|--------------|
| `method` | string | - | Dotted path naar whitelisted method |
| `args` | object | `{}` | Arguments voor de method |
| `type` | string | `"POST"` | HTTP method: GET, POST, PUT, DELETE |
| `callback` | function | - | Success callback |
| `error` | function | - | Error callback |
| `always` | function | - | Always callback (success of error) |
| `freeze` | boolean | `false` | Toon loading indicator |
| `freeze_message` | string | - | Custom loading message |
| `async` | boolean | `true` | Async request |
| `btn` | jQuery | - | Button om te disablen tijdens call |

### frm.call() - Controller Methods

Voor methods op een DocType controller:

```javascript
// In Form Script
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        frm.add_custom_button(__('Calculate'), () => {
            frm.call('calculate_taxes', {
                include_shipping: true
            }).then(r => {
                if (r.message) {
                    frm.set_value('tax_amount', r.message.tax_amount);
                }
                frm.reload_doc();
            });
        });
    }
});
```

**Vereiste op server**:

```python
class SalesOrder(Document):
    @frappe.whitelist()
    def calculate_taxes(self, include_shipping=False):
        """Controller method moet @frappe.whitelist() hebben"""
        tax = self.total * 0.1
        if include_shipping:
            tax += 50
        return {"tax_amount": tax}
```

### Direct REST API Calls

```javascript
// Fetch API
fetch('/api/method/myapp.api.get_data', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': frappe.csrf_token
    },
    body: JSON.stringify({
        param1: 'value1'
    })
})
.then(r => r.json())
.then(data => console.log(data.message));
```

### API Endpoints

| Type | Endpoint Pattern |
|------|-----------------|
| Method call | `/api/method/dotted.path.to.function` |
| v15+ Method | `/api/v1/method/dotted.path.to.function` |
| v15 API v2 | `/api/v2/method/dotted.path.to.function` |
| Document method | `/api/v2/document/{doctype}/{name}/method/{method}` |

---

## 6. ERROR HANDLING

### frappe.throw() - User-Facing Errors

```python
@frappe.whitelist()
def validate_and_process(data):
    # Validation error (toont message aan gebruiker)
    if not data.get('required_field'):
        frappe.throw(
            _("Required field is missing"),
            title=_("Validation Error")
        )
    
    # Met specifieke exception type
    if not frappe.has_permission("Sales Order", "write"):
        frappe.throw(
            _("Not permitted"),
            frappe.PermissionError
        )
    
    # Validation met value indicator
    if data.get('amount', 0) < 0:
        frappe.throw(
            _("Amount cannot be negative: {0}").format(data.get('amount')),
            exc=frappe.ValidationError,
            title=_("Invalid Amount")
        )
```

### Exception Types

| Exception | HTTP Code | Gebruik |
|-----------|-----------|---------|
| `frappe.ValidationError` | 417 | Validation fouten |
| `frappe.PermissionError` | 403 | Permission denied |
| `frappe.DoesNotExistError` | 404 | Document niet gevonden |
| `frappe.DuplicateEntryError` | 409 | Duplicate entry |
| `frappe.AuthenticationError` | 401 | Authentication failed |
| `frappe.OutgoingEmailError` | 500 | Email sending failed |

### Error Logging

```python
@frappe.whitelist()
def risky_operation(data):
    try:
        result = external_api_call(data)
        return result
    except Exception as e:
        # Log error met volledige traceback
        frappe.log_error(
            frappe.get_traceback(),
            "External API Error"
        )
        
        # Throw user-friendly message
        frappe.throw(
            _("External service unavailable. Please try later."),
            title=_("Service Error")
        )
```

### Error Response Structuur

**Success response**:
```json
{
    "message": { "data": "value" }
}
```

**Error response**:
```json
{
    "exc_type": "ValidationError",
    "exc": "[Traceback string...]",
    "_server_messages": "[{\"message\": \"Error message\"}]"
}
```

### Try/Except Pattern voor APIs

```python
@frappe.whitelist()
def robust_api(param):
    try:
        # Business logic
        result = process_data(param)
        return {"success": True, "data": result}
        
    except frappe.DoesNotExistError:
        frappe.local.response["http_status_code"] = 404
        return {"success": False, "error": "Not found"}
        
    except frappe.PermissionError:
        frappe.local.response["http_status_code"] = 403
        return {"success": False, "error": "Access denied"}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "API Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "error": "Internal error"}
```

---

## 7. VERSIE VERSCHILLEN (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| API prefix | `/api/` | `/api/` of `/api/v1/` |
| API v2 | âŒ | âœ… `/api/v2/` |
| Type annotations validation | âŒ | âœ… |
| Rate limiting in Server Scripts | âŒ | âœ… |
| Document method endpoint | N/A | `/api/v2/document/{doctype}/{name}/method/{method}` |

### API v2 (v15+)

```python
# In v15, extra endpoints beschikbaar:

# Document method call via REST
# POST /api/v2/document/Sales Order/SO-00001/method/calculate_taxes

# Method endpoint
# POST /api/v2/method/myapp.api.my_function
```

---

## 8. BEST PRACTICES

### 1. Altijd Permission Checks

```python
@frappe.whitelist()
def get_data(doctype, name):
    # ALTIJD permission checken
    if not frappe.has_permission(doctype, "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return frappe.get_doc(doctype, name).as_dict()
```

### 2. Input Validatie

```python
@frappe.whitelist()
def process_input(email, amount):
    # Valideer input types
    if not isinstance(email, str) or not email:
        frappe.throw(_("Valid email required"))
    
    # Valideer email format
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        frappe.throw(_("Invalid email format"))
    
    # Valideer numerieke waarden
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        frappe.throw(_("Amount must be a number"))
    
    return {"email": email, "amount": amount}
```

### 3. Gebruik GET voor reads, POST voor writes

```python
# GET - alleen lezen
@frappe.whitelist(methods=["GET"])
def get_status(order_id):
    return frappe.db.get_value("Sales Order", order_id, "status")

# POST - database wijzigingen
@frappe.whitelist(methods=["POST"])
def update_status(order_id, status):
    frappe.db.set_value("Sales Order", order_id, "status", status)
    return {"updated": True}
```

### 4. Documenteer je APIs

```python
@frappe.whitelist()
def create_customer(customer_name: str, email: str, territory: str = "All Territories") -> dict:
    """
    Create a new customer record.
    
    Args:
        customer_name: Name of the customer (required)
        email: Customer email address (required)
        territory: Customer territory (optional, defaults to "All Territories")
    
    Returns:
        dict: {"name": customer_name, "success": True}
    
    Raises:
        ValidationError: If customer_name or email is missing
        PermissionError: If user doesn't have Customer create permission
    """
    frappe.has_permission("Customer", "create", throw=True)
    
    if not customer_name or not email:
        frappe.throw(_("Customer name and email are required"))
    
    doc = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": customer_name,
        "email_id": email,
        "territory": territory
    })
    doc.insert()
    
    return {"name": doc.name, "success": True}
```

### 5. Rate Limiting voor Public APIs

```python
# In Server Script (v15+) kun je rate limiting inschakelen
# Voor custom code, implementeer zelf:

from frappe.rate_limiter import rate_limit

@frappe.whitelist(allow_guest=True)
@rate_limit(limit=100, seconds=60*60)  # 100 calls per uur
def public_api(param):
    return {"data": "value"}
```

---

## 9. ANTI-PATTERNS

### âŒ Geen Permission Check

```python
# FOUT - iedereen kan alle data zien
@frappe.whitelist()
def get_all_salaries():
    return frappe.get_all("Salary Slip", fields=["*"])
```

### âŒ SQL Injection Kwetsbaar

```python
# FOUT - user input direct in query
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql(f"SELECT * FROM `tabCustomer` WHERE name LIKE '%{search_term}%'")

# GOED - parameterized query
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql("""
        SELECT * FROM `tabCustomer` WHERE name LIKE %(search)s
    """, {"search": f"%{search_term}%"}, as_dict=True)
```

### âŒ Overal ignore_permissions

```python
# FOUT - bypass alle security
@frappe.whitelist()
def create_anything(data):
    doc = frappe.get_doc(data)
    doc.insert(ignore_permissions=True)  # SECURITY RISK!
```

### âŒ Sensitive Data in Error Messages

```python
# FOUT - lekt interne informatie
@frappe.whitelist()
def process_data(data):
    try:
        result = complex_operation(data)
    except Exception as e:
        frappe.throw(str(e))  # Kan stack traces lekken!

# GOED - generieke error naar user, details naar log
@frappe.whitelist()
def process_data(data):
    try:
        result = complex_operation(data)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Process Error")
        frappe.throw(_("An error occurred. Please contact support."))
```

---

## 10. SAMENVATTING VOOR SKILL CREATIE

### Key Learnings

1. **@frappe.whitelist()** maakt Python functies beschikbaar als REST endpoints
2. **Drie parameters**: `allow_guest`, `methods`, `xss_safe`
3. **Endpoint**: `/api/method/dotted.path.to.function`
4. **Response**: Return value â†’ `{"message": ...}` of via `frappe.response`
5. **Permissions**: ALTIJD checken met `frappe.has_permission()` of `frappe.only_for()`
6. **Errors**: `frappe.throw()` voor user-facing, `frappe.log_error()` voor logging
7. **Client call**: `frappe.call({method: ..., args: ...})`
8. **Controller methods**: Zelfde decorator, aanroepen via `frm.call()`
9. **v15 additions**: Type validation, API v2, rate limiting

### Skill References te Maken

1. `decorator-options.md` - Alle decorator parameters met voorbeelden
2. `parameter-handling.md` - Request parameters en type conversion
3. `response-patterns.md` - Response types en structuren
4. `permission-patterns.md` - Security best practices
5. `client-calls.md` - frappe.call en frm.call voorbeelden
6. `error-handling.md` - Error patterns en exception types
7. `examples.md` - Complete werkende API voorbeelden
8. `anti-patterns.md` - Wat te vermijden
