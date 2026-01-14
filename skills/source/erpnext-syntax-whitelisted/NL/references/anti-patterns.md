# Anti-Patterns Reference

Veelgemaakte fouten bij Whitelisted Methods en correcte alternatieven.

## Inhoudsopgave

1. [Security Anti-Patterns](#security-anti-patterns)
2. [Input Validatie Fouten](#input-validatie-fouten)
3. [Error Handling Fouten](#error-handling-fouten)
4. [Response Anti-Patterns](#response-anti-patterns)
5. [Performance Anti-Patterns](#performance-anti-patterns)
6. [Client-Side Anti-Patterns](#client-side-anti-patterns)

---

## Security Anti-Patterns

### ❌ Geen Permission Check

**Probleem**: Iedereen kan alle data zien of wijzigen.

```python
# ❌ FOUT - geen permission check
@frappe.whitelist()
def get_all_salaries():
    return frappe.get_all("Salary Slip", fields=["*"])
```

**Gevolg**: Elke ingelogde user kan salarissen van iedereen zien.

```python
# ✅ GOED - met permission check
@frappe.whitelist()
def get_salaries():
    frappe.only_for("HR Manager")
    # Of: if not frappe.has_permission("Salary Slip", "read"):
    #         frappe.throw(_("Not permitted"), frappe.PermissionError)
    return frappe.get_all("Salary Slip", fields=["*"])
```

---

### ❌ SQL Injection Kwetsbaar

**Probleem**: User input direct in SQL query.

```python
# ❌ FOUT - SQL injection mogelijk!
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql(
        f"SELECT * FROM `tabCustomer` WHERE name LIKE '%{search_term}%'"
    )
```

**Aanval**: `search_term = "'; DROP TABLE tabCustomer; --"`

```python
# ✅ GOED - parameterized query
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql("""
        SELECT * FROM `tabCustomer` WHERE name LIKE %(search)s
    """, {"search": f"%{search_term}%"}, as_dict=True)

# ✅ OOK GOED - ORM methode
@frappe.whitelist()
def search_customers(search_term):
    return frappe.get_all(
        "Customer",
        filters={"name": ["like", f"%{search_term}%"]},
        fields=["name", "customer_name", "email_id"]
    )
```

---

### ❌ ignore_permissions Zonder Controle

**Probleem**: Bypass alle security zonder validatie.

```python
# ❌ FOUT - iedereen kan alles maken
@frappe.whitelist()
def create_anything(data):
    doc = frappe.get_doc(data)
    doc.insert(ignore_permissions=True)
    return doc.name
```

**Aanval**: User kan System Settings, User records, etc. aanmaken.

```python
# ✅ GOED - met strikte controle
@frappe.whitelist()
def create_allowed_doc(data):
    # Rol check
    frappe.only_for("System Manager")
    
    # Whitelist DocTypes
    allowed_doctypes = ["ToDo", "Note", "Communication"]
    if data.get("doctype") not in allowed_doctypes:
        frappe.throw(_("Cannot create this document type"))
    
    doc = frappe.get_doc(data)
    doc.insert()  # Normale permissions, of ignore_permissions met rol check
    return doc.name
```

---

### ❌ allow_guest Zonder Input Validatie

**Probleem**: Public endpoint zonder bescherming.

```python
# ❌ FOUT - geen validatie bij guest access
@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_form(data):
    doc = frappe.get_doc(data)
    doc.insert(ignore_permissions=True)
    return {"success": True}
```

**Aanval**: Spam, malicious content, resource exhaustion.

```python
# ✅ GOED - grondige validatie
@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_form(name, email, message):
    import re
    
    # Type check
    if not isinstance(name, str) or not isinstance(email, str):
        frappe.throw(_("Invalid input types"))
    
    # Lengte check
    if len(name) > 100 or len(message or "") > 5000:
        frappe.throw(_("Input too long"))
    
    # Email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        frappe.throw(_("Invalid email format"))
    
    # Sanitize
    name = frappe.utils.strip_html(name)
    message = frappe.utils.strip_html(message or "")
    
    # Alleen specifiek DocType, geen user input voor doctype
    doc = frappe.get_doc({
        "doctype": "Contact Form",  # Vaste waarde!
        "name1": name,
        "email": email,
        "message": message
    })
    doc.insert(ignore_permissions=True)
    return {"success": True}
```

---

## Input Validatie Fouten

### ❌ Geen Type Validatie

**Probleem**: Aanname over input types.

```python
# ❌ FOUT - crash bij verkeerde type
@frappe.whitelist()
def calculate(amount, rate):
    return amount * rate  # Wat als amount="abc"?
```

```python
# ✅ GOED - type conversie en validatie
@frappe.whitelist()
def calculate(amount, rate):
    try:
        amount = float(amount)
        rate = float(rate)
    except (TypeError, ValueError):
        frappe.throw(_("Amount and rate must be numbers"))
    
    if amount < 0 or rate < 0:
        frappe.throw(_("Values cannot be negative"))
    
    return amount * rate
```

---

### ❌ JSON Parsing Zonder Error Handling

**Probleem**: Crash bij ongeldige JSON.

```python
# ❌ FOUT - crash bij ongeldige JSON
@frappe.whitelist()
def process_data(data):
    import json
    parsed = json.loads(data)  # Crash als data geen valid JSON is
    return process(parsed)
```

```python
# ✅ GOED - veilige JSON parsing
@frappe.whitelist()
def process_data(data):
    if isinstance(data, str):
        try:
            data = frappe.parse_json(data)
        except Exception:
            frappe.throw(_("Invalid JSON data"))
    
    if not isinstance(data, dict):
        frappe.throw(_("Data must be a JSON object"))
    
    return process(data)
```

---

### ❌ Onbeperkte Lijst Input

**Probleem**: Resource exhaustion via grote lijsten.

```python
# ❌ FOUT - geen limiet
@frappe.whitelist()
def process_items(items):
    results = []
    for item in items:  # Wat als items 1 miljoen records heeft?
        results.append(heavy_operation(item))
    return results
```

```python
# ✅ GOED - met limiet
@frappe.whitelist()
def process_items(items):
    if isinstance(items, str):
        items = frappe.parse_json(items)
    
    if not isinstance(items, list):
        frappe.throw(_("Items must be a list"))
    
    # Limiet
    MAX_ITEMS = 100
    if len(items) > MAX_ITEMS:
        frappe.throw(_("Maximum {0} items allowed").format(MAX_ITEMS))
    
    results = []
    for item in items:
        results.append(process(item))
    return results
```

---

## Error Handling Fouten

### ❌ Stack Traces in Error Messages

**Probleem**: Interne informatie lekken.

```python
# ❌ FOUT - lekt interne informatie
@frappe.whitelist()
def risky_operation(data):
    try:
        result = complex_operation(data)
        return result
    except Exception as e:
        frappe.throw(str(e))  # Kan db credentials, paths lekken!
```

```python
# ✅ GOED - generieke message, details naar log
@frappe.whitelist()
def risky_operation(data):
    try:
        result = complex_operation(data)
        return result
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"risky_operation error for user {frappe.session.user}"
        )
        frappe.throw(_("Operation failed. Please contact support."))
```

---

### ❌ Geen Error Handling voor Externe Calls

**Probleem**: Timeouts en network errors niet afgehandeld.

```python
# ❌ FOUT - geen timeout, geen error handling
@frappe.whitelist()
def call_external_api(data):
    import requests
    response = requests.post(url, json=data)  # Kan eeuwig hangen
    return response.json()
```

```python
# ✅ GOED - timeout en error handling
@frappe.whitelist()
def call_external_api(data):
    import requests
    
    try:
        response = requests.post(
            url, 
            json=data, 
            timeout=30  # Max 30 seconden
        )
        response.raise_for_status()
        return response.json()
        
    except requests.Timeout:
        frappe.throw(_("External service timeout. Please try again."))
        
    except requests.ConnectionError:
        frappe.throw(_("Cannot connect to external service."))
        
    except requests.HTTPError as e:
        frappe.log_error(f"External API error: {e}", "External API")
        frappe.throw(_("External service error."))
        
    except Exception:
        frappe.log_error(frappe.get_traceback(), "External API")
        frappe.throw(_("Unexpected error occurred."))
```

---

## Response Anti-Patterns

### ❌ Sensitive Data in Response

**Probleem**: Te veel data retourneren.

```python
# ❌ FOUT - retourneert alles inclusief sensitive fields
@frappe.whitelist()
def get_user_info(user):
    return frappe.get_doc("User", user).as_dict()
    # Inclusief: api_key, api_secret, reset_password_key, etc!
```

```python
# ✅ GOED - alleen benodigde velden
@frappe.whitelist()
def get_user_info(user):
    doc = frappe.get_doc("User", user)
    return {
        "name": doc.name,
        "full_name": doc.full_name,
        "email": doc.email,
        "user_image": doc.user_image
        # Geen api keys, passwords, etc.
    }
```

---

### ❌ Inconsistente Response Format

**Probleem**: Moeilijk te parsen responses.

```python
# ❌ FOUT - inconsistent
@frappe.whitelist()
def get_data(type):
    if type == "list":
        return frappe.get_all("Item")  # Retourneert list
    else:
        return frappe.get_doc("Item", type)  # Retourneert dict
```

```python
# ✅ GOED - consistent format
@frappe.whitelist()
def get_data(type, name=None):
    if type == "list":
        return {
            "success": True,
            "data": frappe.get_all("Item"),
            "type": "list"
        }
    else:
        return {
            "success": True,
            "data": frappe.get_doc("Item", name).as_dict(),
            "type": "single"
        }
```

---

## Performance Anti-Patterns

### ❌ N+1 Query Pattern

**Probleem**: Te veel database queries.

```python
# ❌ FOUT - N+1 queries
@frappe.whitelist()
def get_orders_with_items():
    orders = frappe.get_all("Sales Order", limit=100)
    for order in orders:
        order["items"] = frappe.get_all(
            "Sales Order Item",
            filters={"parent": order.name}
        )  # 100 extra queries!
    return orders
```

```python
# ✅ GOED - batch query
@frappe.whitelist()
def get_orders_with_items():
    orders = frappe.get_all(
        "Sales Order",
        fields=["name", "customer", "grand_total"],
        limit=100
    )
    
    if orders:
        # Één query voor alle items
        all_items = frappe.get_all(
            "Sales Order Item",
            filters={"parent": ["in", [o.name for o in orders]]},
            fields=["parent", "item_code", "qty", "amount"]
        )
        
        # Group by parent
        items_by_parent = {}
        for item in all_items:
            items_by_parent.setdefault(item.parent, []).append(item)
        
        for order in orders:
            order["items"] = items_by_parent.get(order.name, [])
    
    return orders
```

---

### ❌ Geen Pagination

**Probleem**: Geheugen en performance issues.

```python
# ❌ FOUT - laadt alles
@frappe.whitelist()
def get_all_customers():
    return frappe.get_all("Customer")  # Kan 100.000+ records zijn
```

```python
# ✅ GOED - met pagination
@frappe.whitelist()
def get_customers(limit=20, offset=0, search=None):
    limit = min(int(limit), 100)  # Max 100 per request
    offset = int(offset)
    
    filters = {}
    if search:
        filters["customer_name"] = ["like", f"%{search}%"]
    
    data = frappe.get_all(
        "Customer",
        filters=filters,
        fields=["name", "customer_name", "email_id"],
        limit_page_length=limit,
        limit_start=offset
    )
    
    total = frappe.db.count("Customer", filters)
    
    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }
```

---

## Client-Side Anti-Patterns

### ❌ Synchrone Calls

**Probleem**: Blokkeert UI.

```javascript
// ❌ FOUT - blokkeert browser
frappe.call({
    method: 'myapp.api.get_data',
    async: false  // NOOIT DOEN!
});
```

```javascript
// ✅ GOED - async met callback of promise
frappe.call({
    method: 'myapp.api.get_data'
}).then(r => {
    // Handle response
});
```

---

### ❌ Geen Error Handling

**Probleem**: Stille failures.

```javascript
// ❌ FOUT - geen error handling
frappe.call({
    method: 'myapp.api.risky_operation',
    args: { data: myData }
});
// Wat als dit faalt?
```

```javascript
// ✅ GOED - error handling
frappe.call({
    method: 'myapp.api.risky_operation',
    args: { data: myData }
}).then(r => {
    if (r.message && r.message.success) {
        frappe.show_alert({
            message: __('Success!'),
            indicator: 'green'
        });
    }
}).catch(err => {
    frappe.show_alert({
        message: __('Operation failed'),
        indicator: 'red'
    });
    console.error(err);
});
```

---

### ❌ Hardcoded API Paths

**Probleem**: Moeilijk te onderhouden.

```javascript
// ❌ FOUT - hardcoded
frappe.call({
    method: 'erpnext.selling.doctype.sales_order.sales_order.get_stock'
});
```

```javascript
// ✅ GOED - via frm.call voor controller methods
frm.call('get_stock').then(r => {
    // Frappe bepaalt automatisch het juiste pad
});

// Of definieer constants
const API = {
    get_stock: 'myapp.api.inventory.get_stock',
    update_price: 'myapp.api.pricing.update_price'
};

frappe.call({
    method: API.get_stock
});
```

---

## Quick Security Checklist

| Check | Status |
|-------|--------|
| Permission check aanwezig | ☐ |
| Input types gevalideerd | ☐ |
| SQL queries geparameterized | ☐ |
| Error messages bevatten geen internals | ☐ |
| Response bevat alleen noodzakelijke data | ☐ |
| allow_guest alleen met goede reden | ☐ |
| ignore_permissions alleen met role check | ☐ |
| Externe calls hebben timeout | ☐ |
| Lijst inputs hebben limiet | ☐ |
| Pagination voor grote datasets | ☐ |
