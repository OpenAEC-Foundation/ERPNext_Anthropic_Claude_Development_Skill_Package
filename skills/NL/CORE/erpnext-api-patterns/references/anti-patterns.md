# API Anti-Patterns

## ❌ Geen Error Handling

```python
# FOUT - geen error handling
@frappe.whitelist()
def dangerous_operation(docname):
    doc = frappe.get_doc("Customer", docname)
    doc.delete()
    return "done"

# ✅ CORRECT - met error handling
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
# FOUT - SQL injection vulnerable
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

# ✅ CORRECT - met get_all
@frappe.whitelist()
def search_customers(search_term):
    return frappe.get_all(
        "Customer",
        filters={"name": ["like", f"%{search_term}%"]},
        fields=["name", "customer_name"]
    )
```

---

## ❌ Geen Permission Check

```python
# FOUT - geen permission check
@frappe.whitelist()
def get_salary(employee):
    return frappe.db.get_value("Salary Slip", {"employee": employee}, "gross_pay")

# ✅ CORRECT - met permission check
@frappe.whitelist()
def get_salary(employee):
    if not frappe.has_permission("Salary Slip", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return frappe.db.get_value("Salary Slip", {"employee": employee}, "gross_pay")
```

---

## ❌ Credentials Hardcoded

```python
# FOUT - hardcoded credentials
API_KEY = "abc123"
API_SECRET = "secret456"

def call_external_api():
    headers = {'Authorization': f'token {API_KEY}:{API_SECRET}'}
    ...

# ✅ CORRECT - uit site_config
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

## ❌ Geen Rate Limiting op Heavy Endpoints

```python
# FOUT - heavy operation zonder beperking
@frappe.whitelist(allow_guest=True)
def generate_report():
    return expensive_computation()  # DoS risk!

# ✅ CORRECT - met rate limiting (via Server Script)
# Server Script > Enable Rate Limit = True
# Rate Limit Count = 10
# Rate Limit Seconds = 60

# Of: permission check om guests te blokkeren
@frappe.whitelist()  # Geen allow_guest
def generate_report():
    return expensive_computation()
```

---

## ❌ Geen Paginering bij Grote Datasets

```python
# FOUT - alle records ophalen
@frappe.whitelist()
def get_all_invoices():
    return frappe.get_all("Sales Invoice")  # Kan duizenden records zijn!

# ✅ CORRECT - met paginering
@frappe.whitelist()
def get_invoices(page=0, page_size=20):
    page_size = min(page_size, 100)  # Max limiet
    
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
# FOUT - credentials in logs
@frappe.whitelist()
def authenticate(username, password):
    frappe.logger().info(f"Login attempt: {username}:{password}")  # NOOIT!
    ...

# ✅ CORRECT - alleen non-sensitive info
@frappe.whitelist()
def authenticate(username, password):
    frappe.logger().info(f"Login attempt for user: {username}")
    ...
```

---

## ❌ Synchrone Lange Operaties

```python
# FOUT - blokkeert worker
@frappe.whitelist()
def process_large_file(file_url):
    # 5 minuten processing...
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

## ❌ Inconsistente Response Formats

```python
# FOUT - inconsistent
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

## ❌ Geen Input Validatie

```python
# FOUT - geen validatie
@frappe.whitelist()
def create_order(customer, amount):
    # Direct gebruiken zonder checks
    order = frappe.new_doc("Sales Order")
    order.customer = customer
    order.grand_total = amount
    order.insert()

# ✅ CORRECT - met validatie
@frappe.whitelist()
def create_order(customer, amount):
    # Valideer inputs
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
    
    # Nu veilig gebruiken
    order = frappe.new_doc("Sales Order")
    order.customer = customer
    order.grand_total = amount
    order.insert()
    
    return {"name": order.name}
```

---

## ❌ Admin Credentials voor API

```python
# FOUT - admin user voor integratie
api_key = "Administrator_api_key"  # NOOIT!

# ✅ CORRECT - dedicated API user met beperkte rechten
# 1. Maak "API User" role
# 2. Geef alleen benodigde permissions
# 3. Maak dedicated user met die role
# 4. Genereer API keys voor die user
```

---

## ❌ Geen Timeout bij Externe Calls

```python
# FOUT - geen timeout
response = requests.get(external_url)  # Kan eeuwig hangen

# ✅ CORRECT - met timeout
response = requests.get(external_url, timeout=30)
```

---

## Checklist voor API Development

```
□ Permission check aanwezig?
□ Input validatie compleet?
□ SQL queries geparameteriseerd?
□ Error handling implemented?
□ Sensitive data niet gelogd?
□ Response format consistent?
□ Rate limiting waar nodig?
□ Paginering voor lijsten?
□ Credentials uit config?
□ Timeouts ingesteld?
```
