# Anti-Patterns and Common Mistakes

Common mistakes when implementing Whitelisted Methods and how to fix them.

---

## Anti-Pattern 1: No Permission Check

### ❌ Wrong

```python
@frappe.whitelist()
def get_all_salaries():
    """Anyone can see all salaries!"""
    return frappe.get_all("Salary Slip", fields=["*"])
```

**Problem**: Any logged-in user can access sensitive salary data.

### ✅ Correct

```python
@frappe.whitelist()
def get_all_salaries():
    """HR only."""
    frappe.only_for("HR Manager")
    return frappe.get_all("Salary Slip", fields=["*"])
```

Or with document-level checks:

```python
@frappe.whitelist()
def get_salary(employee):
    if not frappe.has_permission("Salary Slip", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    return frappe.get_all("Salary Slip", filters={"employee": employee})
```

---

## Anti-Pattern 2: SQL Injection

### ❌ Wrong

```python
@frappe.whitelist()
def search_items(term):
    """SQL injection vulnerability!"""
    return frappe.db.sql(f"""
        SELECT * FROM tabItem 
        WHERE item_name LIKE '%{term}%'
    """, as_dict=True)
```

**Problem**: User can inject SQL: `term = "'; DROP TABLE tabItem; --"`

### ✅ Correct

```python
@frappe.whitelist()
def search_items(term):
    """Parameterized query - safe."""
    return frappe.db.sql("""
        SELECT * FROM tabItem 
        WHERE item_name LIKE %(term)s
    """, {"term": f"%{term}%"}, as_dict=True)
```

Or use ORM:

```python
@frappe.whitelist()
def search_items(term):
    return frappe.get_all(
        "Item",
        filters={"item_name": ["like", f"%{term}%"]},
        fields=["name", "item_name"]
    )
```

---

## Anti-Pattern 3: Sensitive Data in Guest API

### ❌ Wrong

```python
@frappe.whitelist(allow_guest=True)
def get_order(order_id):
    """Exposes all order details to public!"""
    return frappe.get_doc("Sales Order", order_id).as_dict()
```

**Problem**: Exposes customer info, pricing, internal notes to anyone.

### ✅ Correct

```python
@frappe.whitelist(allow_guest=True)
def get_order_status(order_id):
    """Limited public information only."""
    # Validate format
    if not order_id or not order_id.startswith("SO-"):
        frappe.local.response["http_status_code"] = 400
        return {"error": "Invalid order ID"}
    
    # Return only public fields
    order = frappe.db.get_value(
        "Sales Order",
        order_id,
        ["status", "delivery_status"],
        as_dict=True
    )
    
    if not order:
        frappe.local.response["http_status_code"] = 404
        return {"error": "Order not found"}
    
    return {"status": order.status, "delivery": order.delivery_status}
```

---

## Anti-Pattern 4: Leaking Internal Errors

### ❌ Wrong

```python
@frappe.whitelist()
def process_data(data):
    try:
        result = complex_operation(data)
        return result
    except Exception as e:
        frappe.throw(str(e))  # Exposes stack trace!
```

**Problem**: Internal errors, file paths, and stack traces exposed to users.

### ✅ Correct

```python
@frappe.whitelist()
def process_data(data):
    try:
        result = complex_operation(data)
        return {"success": True, "data": result}
    except frappe.ValidationError:
        raise  # Known error - let Frappe handle
    except Exception:
        # Log details for debugging
        frappe.log_error(frappe.get_traceback(), "Process Data Error")
        # Generic message to user
        frappe.throw(_("Unable to process. Please try again."))
```

---

## Anti-Pattern 5: No Input Validation for Guest APIs

### ❌ Wrong

```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_lead(data):
    """Trusts all input!"""
    lead = frappe.get_doc(data)
    lead.insert(ignore_permissions=True)
    return {"id": lead.name}
```

**Problem**: Attacker can create any DocType, set any field, bypass validation.

### ✅ Correct

```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_lead(name, email, phone=None, message=None):
    """Explicit parameters, validated."""
    from frappe.utils import validate_email_address, strip_html
    
    # Required fields
    if not name or not email:
        frappe.throw(_("Name and email required"))
    
    # Email validation
    if not validate_email_address(email):
        frappe.throw(_("Invalid email"))
    
    # Sanitize
    name = strip_html(name)[:100]
    email = email.strip().lower()[:200]
    phone = strip_html(phone)[:20] if phone else None
    message = strip_html(message)[:2000] if message else None
    
    # Create with explicit fields only
    lead = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": name,
        "email_id": email,
        "phone": phone,
        "notes": message,
        "source": "Website"
    })
    lead.insert(ignore_permissions=True)
    
    return {"success": True}
```

---

## Anti-Pattern 6: Using ignore_permissions Without Role Check

### ❌ Wrong

```python
@frappe.whitelist()
def get_confidential_data():
    """Any user bypasses all permissions!"""
    return frappe.get_all("Salary Slip", ignore_permissions=True)
```

**Problem**: Permission system completely bypassed.

### ✅ Correct

```python
@frappe.whitelist()
def get_confidential_data():
    """Role check BEFORE bypassing permissions."""
    frappe.only_for("HR Manager")
    return frappe.get_all("Salary Slip", ignore_permissions=True)
```

---

## Anti-Pattern 7: Wrong Method Restriction

### ❌ Wrong

```python
@frappe.whitelist(methods=["GET"])  # But modifies data!
def update_status(item, status):
    """Modifies data via GET request!"""
    frappe.db.set_value("Item", item, "status", status)
    return {"updated": True}
```

**Problem**: Data modification via GET can be triggered by image tags, cached, etc.

### ✅ Correct

```python
@frappe.whitelist(methods=["POST"])  # POST for modifications
def update_status(item, status):
    frappe.db.set_value("Item", item, "status", status)
    return {"updated": True}
```

---

## Anti-Pattern 8: Missing CSRF Protection Awareness

### ❌ Wrong

```javascript
// Calling from external site
fetch('/api/method/myapp.api.delete_user', {
    method: 'POST',
    body: JSON.stringify({user: 'victim@example.com'})
});
```

**Problem**: If CSRF token not required, attackers can trigger actions via user's session.

### ✅ Correct

```javascript
// Include CSRF token
fetch('/api/method/myapp.api.delete_user', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': frappe.csrf_token
    },
    body: JSON.stringify({user: 'victim@example.com'})
});
```

For legitimate external calls, use API keys or token authentication.

---

## Anti-Pattern 9: Inconsistent Error Handling

### ❌ Wrong

```python
@frappe.whitelist()
def mixed_errors(param):
    if not param:
        return {"error": "Missing param"}  # Returns 200!
    
    if param == "bad":
        frappe.throw("Bad value")  # Returns 417
    
    if param == "denied":
        raise Exception("Access denied")  # Returns 500!
```

**Problem**: Different error formats, inconsistent HTTP codes.

### ✅ Correct

```python
@frappe.whitelist()
def consistent_errors(param):
    if not param:
        frappe.throw(_("Parameter required"), frappe.ValidationError)
    
    if param == "bad":
        frappe.throw(_("Invalid value"), frappe.ValidationError)
    
    if param == "denied":
        frappe.throw(_("Access denied"), frappe.PermissionError)
    
    return {"success": True, "data": process(param)}
```

---

## Anti-Pattern 10: Exposing Internal IDs/Paths

### ❌ Wrong

```python
@frappe.whitelist(allow_guest=True)
def get_file(file_id):
    """Exposes internal file path!"""
    file = frappe.get_doc("File", file_id)
    return {
        "path": file.file_url,  # /private/files/salary_2024.pdf
        "content": file.get_content()
    }
```

**Problem**: Path enumeration, access to private files.

### ✅ Correct

```python
@frappe.whitelist()  # Authenticated only
def get_file(file_id):
    """Check permissions, return content only."""
    file = frappe.get_doc("File", file_id)
    
    # Check if user can access attached document
    if file.attached_to_doctype and file.attached_to_name:
        if not frappe.has_permission(
            file.attached_to_doctype, "read", file.attached_to_name
        ):
            frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return {
        "name": file.file_name,
        "type": file.file_type,
        "url": file.file_url if not file.is_private else None
    }
```

---

## Anti-Pattern 11: No Rate Limiting for Guest APIs

### ❌ Wrong

```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
def send_otp(phone):
    """No rate limit - can be abused!"""
    otp = generate_otp()
    send_sms(phone, otp)
    return {"sent": True}
```

**Problem**: Attacker can flood users with SMS, exhaust SMS credits.

### ✅ Correct (v15+)

```python
from frappe.rate_limiter import rate_limit

@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=3, seconds=300)  # 3 per 5 minutes
def send_otp(phone):
    otp = generate_otp()
    send_sms(phone, otp)
    return {"sent": True}
```

For v14, implement manual throttling:

```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
def send_otp(phone):
    # Manual rate limit check
    cache_key = f"otp_attempts:{phone}"
    attempts = frappe.cache().get(cache_key) or 0
    
    if attempts >= 3:
        frappe.throw(_("Too many attempts. Try again later."))
    
    frappe.cache().set(cache_key, attempts + 1, expires_in_sec=300)
    
    otp = generate_otp()
    send_sms(phone, otp)
    return {"sent": True}
```

---

## Anti-Pattern 12: Returning Too Much Data

### ❌ Wrong

```python
@frappe.whitelist()
def get_customers():
    """Returns ALL customers with ALL fields!"""
    return frappe.get_all("Customer")  # Default gets everything
```

**Problem**: Slow response, memory issues, exposes unnecessary data.

### ✅ Correct

```python
@frappe.whitelist()
def get_customers(page=1, page_size=20):
    """Paginated with specific fields."""
    page = max(1, int(page))
    page_size = min(100, int(page_size))
    
    return frappe.get_all(
        "Customer",
        fields=["name", "customer_name", "customer_group"],  # Specific fields
        filters={"disabled": 0},
        order_by="customer_name",
        start=(page - 1) * page_size,
        limit=page_size
    )
```

---

## Quick Reference: Security Checklist

| Check | ❌ Don't | ✅ Do |
|-------|----------|-------|
| Permissions | Skip checks | Always check permissions |
| SQL | String interpolation | Parameterized queries |
| Guest APIs | Trust input | Validate everything |
| Errors | Expose internals | Log details, generic message |
| ignore_permissions | Use freely | Check role first |
| HTTP Methods | GET for changes | POST for modifications |
| Rate Limiting | Unlimited | Rate limit guest APIs |
| Response Data | Return everything | Specific fields only |
| Sensitive Data | Expose in guest API | Authenticated APIs only |
| Error Formats | Inconsistent | Use frappe exceptions |
