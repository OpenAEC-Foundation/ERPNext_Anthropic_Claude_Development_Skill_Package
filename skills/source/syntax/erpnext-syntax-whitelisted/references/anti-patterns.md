# Anti-Patterns Reference

Common mistakes in Whitelisted Methods and correct alternatives.

## Table of Contents

1. [Security Anti-Patterns](#security-anti-patterns)
2. [Input Validation Mistakes](#input-validation-mistakes)
3. [Error Handling Mistakes](#error-handling-mistakes)
4. [Response Anti-Patterns](#response-anti-patterns)
5. [Performance Anti-Patterns](#performance-anti-patterns)
6. [Client-Side Anti-Patterns](#client-side-anti-patterns)

---

## Security Anti-Patterns

### ❌ No Permission Check

**Problem**: Anyone can view or modify all data.

```python
# ❌ WRONG - no permission check
@frappe.whitelist()
def get_all_salaries():
    return frappe.get_all("Salary Slip", fields=["*"])
```

**Consequence**: Any logged-in user can see everyone's salaries.

```python
# ✅ CORRECT - with permission check
@frappe.whitelist()
def get_salaries():
    frappe.only_for("HR Manager")
    return frappe.get_all("Salary Slip", fields=["*"])
```

---

### ❌ SQL Injection Vulnerable

**Problem**: User input directly in SQL query.

```python
# ❌ WRONG - SQL injection possible!
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql(
        f"SELECT * FROM `tabCustomer` WHERE name LIKE '%{search_term}%'"
    )
```

**Attack**: `search_term = "'; DROP TABLE tabCustomer; --"`

```python
# ✅ CORRECT - parameterized query
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql("""
        SELECT * FROM `tabCustomer` WHERE name LIKE %(search)s
    """, {"search": f"%{search_term}%"}, as_dict=True)

# ✅ ALSO CORRECT - ORM method
@frappe.whitelist()
def search_customers(search_term):
    return frappe.get_all(
        "Customer",
        filters={"name": ["like", f"%{search_term}%"]},
        fields=["name", "customer_name", "email_id"]
    )
```

---

### ❌ ignore_permissions Without Control

**Problem**: Bypasses all security without validation.

```python
# ❌ WRONG - anyone can create anything
@frappe.whitelist()
def create_anything(data):
    doc = frappe.get_doc(data)
    doc.insert(ignore_permissions=True)
    return doc.name
```

**Attack**: User can create System Settings, User records, etc.

```python
# ✅ CORRECT - with strict control
@frappe.whitelist()
def create_allowed_doc(data):
    # Role check
    frappe.only_for("System Manager")
    
    # Whitelist DocTypes
    allowed_doctypes = ["ToDo", "Note", "Communication"]
    if data.get("doctype") not in allowed_doctypes:
        frappe.throw(_("Cannot create this document type"))
    
    doc = frappe.get_doc(data)
    doc.insert()
    return doc.name
```

---

### ❌ allow_guest Without Input Validation

**Problem**: Public endpoint without protection.

```python
# ❌ WRONG - no validation with guest access
@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_form(data):
    doc = frappe.get_doc(data)
    doc.insert(ignore_permissions=True)
    return {"success": True}
```

**Attack**: Spam, malicious content, resource exhaustion.

```python
# ✅ CORRECT - thorough validation
@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_form(name, email, message):
    import re
    
    # Type check
    if not isinstance(name, str) or not isinstance(email, str):
        frappe.throw(_("Invalid input types"))
    
    # Length check
    if len(name) > 100 or len(message or "") > 5000:
        frappe.throw(_("Input too long"))
    
    # Email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        frappe.throw(_("Invalid email format"))
    
    # Sanitize
    name = frappe.utils.strip_html(name)
    message = frappe.utils.strip_html(message or "")
    
    # Only specific DocType, no user input for doctype
    doc = frappe.get_doc({
        "doctype": "Contact Form",  # Fixed value!
        "name1": name,
        "email": email,
        "message": message
    })
    doc.insert(ignore_permissions=True)
    return {"success": True}
```

---

## Input Validation Mistakes

### ❌ No Type Validation

**Problem**: Assumptions about input types.

```python
# ❌ WRONG - crashes with wrong type
@frappe.whitelist()
def calculate(amount, rate):
    return amount * rate  # What if amount="abc"?
```

```python
# ✅ CORRECT - type conversion and validation
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

### ❌ JSON Parsing Without Error Handling

**Problem**: Crashes with invalid JSON.

```python
# ❌ WRONG - crashes with invalid JSON
@frappe.whitelist()
def process_data(data):
    import json
    parsed = json.loads(data)  # Crashes if data isn't valid JSON
    return process(parsed)
```

```python
# ✅ CORRECT - safe JSON parsing
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

### ❌ Unlimited List Input

**Problem**: Resource exhaustion via large lists.

```python
# ❌ WRONG - no limit
@frappe.whitelist()
def process_items(items):
    results = []
    for item in items:  # What if items has 1 million records?
        results.append(heavy_operation(item))
    return results
```

```python
# ✅ CORRECT - with limit
@frappe.whitelist()
def process_items(items):
    if isinstance(items, str):
        items = frappe.parse_json(items)
    
    if not isinstance(items, list):
        frappe.throw(_("Items must be a list"))
    
    # Limit
    MAX_ITEMS = 100
    if len(items) > MAX_ITEMS:
        frappe.throw(_("Maximum {0} items allowed").format(MAX_ITEMS))
    
    results = []
    for item in items:
        results.append(process(item))
    return results
```

---

## Error Handling Mistakes

### ❌ Stack Traces in Error Messages

**Problem**: Leaking internal information.

```python
# ❌ WRONG - leaks internal information
@frappe.whitelist()
def risky_operation(data):
    try:
        result = complex_operation(data)
        return result
    except Exception as e:
        frappe.throw(str(e))  # May leak db credentials, paths!
```

```python
# ✅ CORRECT - generic message, details to log
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

### ❌ No Error Handling for External Calls

**Problem**: Timeouts and network errors not handled.

```python
# ❌ WRONG - no timeout, no error handling
@frappe.whitelist()
def call_external_api(data):
    import requests
    response = requests.post(url, json=data)  # May hang forever
    return response.json()
```

```python
# ✅ CORRECT - timeout and error handling
@frappe.whitelist()
def call_external_api(data):
    import requests
    
    try:
        response = requests.post(
            url, 
            json=data, 
            timeout=30  # Max 30 seconds
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
```

---

## Response Anti-Patterns

### ❌ Sensitive Data in Response

**Problem**: Returning too much data.

```python
# ❌ WRONG - returns everything including sensitive fields
@frappe.whitelist()
def get_user_info(user):
    return frappe.get_doc("User", user).as_dict()
    # Includes: api_key, api_secret, reset_password_key, etc!
```

```python
# ✅ CORRECT - only needed fields
@frappe.whitelist()
def get_user_info(user):
    doc = frappe.get_doc("User", user)
    return {
        "name": doc.name,
        "full_name": doc.full_name,
        "email": doc.email,
        "user_image": doc.user_image
        # No api keys, passwords, etc.
    }
```

---

## Performance Anti-Patterns

### ❌ N+1 Query Pattern

**Problem**: Too many database queries.

```python
# ❌ WRONG - N+1 queries
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
# ✅ CORRECT - batch query
@frappe.whitelist()
def get_orders_with_items():
    orders = frappe.get_all(
        "Sales Order",
        fields=["name", "customer", "grand_total"],
        limit=100
    )
    
    if orders:
        # One query for all items
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

### ❌ No Pagination

**Problem**: Memory and performance issues.

```python
# ❌ WRONG - loads everything
@frappe.whitelist()
def get_all_customers():
    return frappe.get_all("Customer")  # Could be 100,000+ records
```

```python
# ✅ CORRECT - with pagination
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

### ❌ Synchronous Calls

**Problem**: Blocks UI.

```javascript
// ❌ WRONG - blocks browser
frappe.call({
    method: 'myapp.api.get_data',
    async: false  // NEVER DO THIS!
});
```

```javascript
// ✅ CORRECT - async with callback or promise
frappe.call({
    method: 'myapp.api.get_data'
}).then(r => {
    // Handle response
});
```

---

### ❌ No Error Handling

**Problem**: Silent failures.

```javascript
// ❌ WRONG - no error handling
frappe.call({
    method: 'myapp.api.risky_operation',
    args: { data: myData }
});
// What if this fails?
```

```javascript
// ✅ CORRECT - error handling
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

## Quick Security Checklist

| Check | Status |
|-------|--------|
| Permission check present | ☐ |
| Input types validated | ☐ |
| SQL queries parameterized | ☐ |
| Error messages contain no internals | ☐ |
| Response contains only necessary data | ☐ |
| allow_guest only with good reason | ☐ |
| ignore_permissions only with role check | ☐ |
| External calls have timeout | ☐ |
| List inputs have limit | ☐ |
| Pagination for large datasets | ☐ |
