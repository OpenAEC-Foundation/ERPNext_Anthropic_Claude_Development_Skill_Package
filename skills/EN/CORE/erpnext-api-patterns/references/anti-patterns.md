# API Anti-Patterns

## ❌ No Error Handling

```python
# WRONG - no error handling
@frappe.whitelist()
def dangerous_operation(docname):
    doc = frappe.get_doc("Customer", docname)
    doc.delete()
    return "done"

# ✅ CORRECT - with error handling
@frappe.whitelist()
def safe_operation(docname):
    try:
        if not frappe.has_permission("Customer", "delete"):
            frappe.throw(_("Not permitted"), frappe.PermissionError)
        
        doc = frappe.get_doc("Customer", docname)
        doc.delete()
        return {"status": "success", "message": f"{docname} deleted"}
    
    except frappe.DoesNotExistError:
        frappe.throw(_("Customer {0} does not exist").format(docname))
    except frappe.PermissionError:
        raise  # Re-raise permission errors
    except Exception as e:
        frappe.log_error(title="Delete Customer Error")
        frappe.throw(_("Delete failed. Please try again."))
```

---

## ❌ SQL Injection Vulnerable

```python
# WRONG - SQL injection vulnerable
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql(
        f"SELECT * FROM tabCustomer WHERE name LIKE '%{search_term}%'"
    )

# ✅ CORRECT - parameterized query
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql(
        "SELECT * FROM tabCustomer WHERE name LIKE %s",
        (f"%{search_term}%",),
        as_dict=True
    )

# ✅ CORRECT - with get_all
@frappe.whitelist()
def search_customers(search_term):
    return frappe.get_all(
        "Customer",
        filters={"name": ["like", f"%{search_term}%"]},
        fields=["name", "customer_name"]
    )
```

---

## ❌ No Permission Check

```python
# WRONG - no permission check
@frappe.whitelist()
def get_salary(employee):
    return frappe.db.get_value("Salary Slip", {"employee": employee}, "gross_pay")

# ✅ CORRECT - with permission check
@frappe.whitelist()
def get_salary(employee):
    if not frappe.has_permission("Salary Slip", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return frappe.db.get_value("Salary Slip", {"employee": employee}, "gross_pay")
```

---

## ❌ Hardcoded Credentials

```python
# WRONG - hardcoded credentials
API_KEY = "abc123"
API_SECRET = "secret456"

def call_external_api():
    headers = {'Authorization': f'token {API_KEY}:{API_SECRET}'}
    ...

# ✅ CORRECT - from site_config
def call_external_api():
    api_key = frappe.conf.get("external_api_key")
    api_secret = frappe.conf.get("external_api_secret")
    
    if not api_key or not api_secret:
        frappe.throw(_("API credentials not configured"))
    
    headers = {'Authorization': f'token {api_key}:{api_secret}'}
    ...
```

**In site_config.json:**
```json
{
    "external_api_key": "abc123",
    "external_api_secret": "secret456"
}
```

---

## ❌ No Rate Limiting on Heavy Endpoints

```python
# WRONG - heavy operation without limitation
@frappe.whitelist(allow_guest=True)
def generate_report():
    return expensive_computation()  # DoS risk!

# ✅ CORRECT - with rate limiting (via Server Script)
# Server Script > Enable Rate Limit = True
# Rate Limit Count = 10
# Rate Limit Seconds = 60

# Or: permission check to block guests
@frappe.whitelist()  # No allow_guest
def generate_report():
    return expensive_computation()
```

---

## ❌ No Pagination for Large Datasets

```python
# WRONG - retrieve all records
@frappe.whitelist()
def get_all_invoices():
    return frappe.get_all("Sales Invoice")  # Could be thousands!

# ✅ CORRECT - with pagination
@frappe.whitelist()
def get_invoices(page=0, page_size=20):
    page_size = min(page_size, 100)  # Max limit
    
    return frappe.get_all(
        "Sales Invoice",
        fields=["name", "customer", "grand_total"],
        limit_start=page * page_size,
        limit_page_length=page_size,
        order_by="modified desc"
    )
```

---

## ❌ Sensitive Data in Logs

```python
# WRONG - credentials in logs
@frappe.whitelist()
def authenticate(username, password):
    frappe.logger().info(f"Login attempt: {username}:{password}")  # NEVER!
    ...

# ✅ CORRECT - only non-sensitive info
@frappe.whitelist()
def authenticate(username, password):
    frappe.logger().info(f"Login attempt for user: {username}")
    ...
```

---

## ❌ Synchronous Long Operations

```python
# WRONG - blocks worker
@frappe.whitelist()
def process_large_file(file_url):
    # 5 minutes processing...
    return heavy_processing(file_url)

# ✅ CORRECT - queue background job
@frappe.whitelist()
def process_large_file(file_url):
    frappe.enqueue(
        "my_app.tasks.heavy_processing",
        file_url=file_url,
        queue="long",
        timeout=1800
    )
    return {"status": "queued", "message": "Processing started"}
```

---

## ❌ Inconsistent Response Formats

```python
# WRONG - inconsistent
@frappe.whitelist()
def get_customer(name):
    if not name:
        return "Error: name required"  # String
    doc = frappe.get_doc("Customer", name)
    return doc.as_dict()  # Dict

# ✅ CORRECT - consistent format
@frappe.whitelist()
def get_customer(name):
    if not name:
        frappe.throw(_("Customer name is required"))
    
    return {
        "status": "success",
        "data": frappe.get_doc("Customer", name).as_dict()
    }
```

---

## ❌ No Input Validation

```python
# WRONG - no validation
@frappe.whitelist()
def create_order(customer, amount):
    # Direct use without checks
    order = frappe.new_doc("Sales Order")
    order.customer = customer
    order.grand_total = amount
    order.insert()

# ✅ CORRECT - with validation
@frappe.whitelist()
def create_order(customer, amount):
    # Validate inputs
    if not customer:
        frappe.throw(_("Customer is required"))
    
    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer {0} does not exist").format(customer))
    
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        frappe.throw(_("Amount must be a number"))
    
    if amount <= 0:
        frappe.throw(_("Amount must be positive"))
    
    # Now safe to use
    order = frappe.new_doc("Sales Order")
    order.customer = customer
    order.grand_total = amount
    order.insert()
    
    return {"name": order.name}
```

---

## ❌ Admin Credentials for API

```python
# WRONG - admin user for integration
api_key = "Administrator_api_key"  # NEVER!

# ✅ CORRECT - dedicated API user with limited rights
# 1. Create "API User" role
# 2. Grant only required permissions
# 3. Create dedicated user with that role
# 4. Generate API keys for that user
```

---

## ❌ No Timeout for External Calls

```python
# WRONG - no timeout
response = requests.get(external_url)  # Could hang forever

# ✅ CORRECT - with timeout
response = requests.get(external_url, timeout=30)
```

---

## Checklist for API Development

```
□ Permission check present?
□ Input validation complete?
□ SQL queries parameterized?
□ Error handling implemented?
□ Sensitive data not logged?
□ Response format consistent?
□ Rate limiting where needed?
□ Pagination for lists?
□ Credentials from config?
□ Timeouts set?
```
