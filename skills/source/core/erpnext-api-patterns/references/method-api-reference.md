# Method API Reference

> Remote Procedure Calls via whitelisted Python methods.

---

## 1. Endpoint Structuur

```
/api/method/<dotted.path.to.method>
```

---

## 2. Whitelisted Methods

### Basis Decorator

```python
import frappe

@frappe.whitelist()
def my_api_function(param1, param2):
    """
    Toegankelijk via:
    /api/method/myapp.api.my_api_function
    """
    return {"result": param1 + param2}
```

### Decorator Opties

```python
@frappe.whitelist()
def standard_method():
    """Vereist authenticatie"""
    pass

@frappe.whitelist(allow_guest=True)
def public_method():
    """Toegankelijk zonder authenticatie"""
    pass

@frappe.whitelist(methods=["POST"])
def post_only():
    """Accepteert alleen POST requests"""
    pass

@frappe.whitelist(methods=["GET", "POST"])
def get_or_post():
    """Accepteert GET en POST"""
    pass

# v15+ rate limiting
@frappe.whitelist(rate_limit={"limit": 10, "window": 60})
def rate_limited():
    """Max 10 calls per 60 seconden"""
    pass
```

---

## 3. HTTP Method Conventies

| Actie | HTTP Method | Auto-commit | Wanneer |
|-------|-------------|-------------|---------|
| Data lezen | GET | Nee | Query operaties |
| Data schrijven | POST | Ja | Insert/Update/Delete |

```python
@frappe.whitelist()
def get_customer_info(customer):
    """GET request - geen auto-commit"""
    return frappe.get_doc("Customer", customer).as_dict()

@frappe.whitelist(methods=["POST"])
def update_customer_status(customer, status):
    """POST request - auto-commit na return"""
    doc = frappe.get_doc("Customer", customer)
    doc.status = status
    doc.save()
    return doc.as_dict()
```

---

## 4. Parameter Handling

### Via Query String (GET)

```bash
GET /api/method/myapp.api.get_data?customer=CUST-001&limit=10
```

```python
@frappe.whitelist()
def get_data(customer, limit=20):
    # limit wordt automatisch naar int geconverteerd indien mogelijk
    return frappe.get_list("Sales Order", 
        filters={"customer": customer},
        limit_page_length=int(limit)
    )
```

### Via Request Body (POST)

```bash
POST /api/method/myapp.api.create_order
Content-Type: application/json

{
    "customer": "CUST-001",
    "items": [
        {"item_code": "ITEM-001", "qty": 5}
    ]
}
```

```python
@frappe.whitelist(methods=["POST"])
def create_order(customer, items):
    # items wordt automatisch geparsed als JSON list
    doc = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": customer,
        "items": items
    })
    doc.insert()
    return doc.as_dict()
```

### Complex Data Types

```python
@frappe.whitelist()
def process_data(data):
    # data komt als string binnen - parse indien nodig
    if isinstance(data, str):
        data = frappe.parse_json(data)
    
    return {"processed": data}
```

---

## 5. Response Formats

### Success Response

```python
@frappe.whitelist()
def simple_response():
    return "Hello World"
# {"message": "Hello World"}

@frappe.whitelist()
def dict_response():
    return {"name": "John", "age": 30}
# {"message": {"name": "John", "age": 30}}

@frappe.whitelist()
def list_response():
    return [1, 2, 3]
# {"message": [1, 2, 3]}
```

### Error Response

```python
@frappe.whitelist()
def validate_input(value):
    if not value:
        frappe.throw("Value is required")  # HTTP 417
    
    if value < 0:
        frappe.throw("Value must be positive", frappe.ValidationError)
    
    return {"valid": True}
```

**Error response format:**
```json
{
    "exc_type": "ValidationError",
    "exc": "<stack_trace>",
    "_server_messages": "[{\"message\": \"Value must be positive\"}]"
}
```

---

## 6. Standaard frappe.client Methods

### frappe.client.get_value

```bash
POST /api/method/frappe.client.get_value
{
    "doctype": "Customer",
    "filters": {"name": "CUST-00001"},
    "fieldname": "customer_name"
}
# {"message": "Example Corp"}

POST /api/method/frappe.client.get_value
{
    "doctype": "Customer",
    "filters": {"name": "CUST-00001"},
    "fieldname": ["customer_name", "outstanding_amount"]
}
# {"message": {"customer_name": "Example Corp", "outstanding_amount": 5000}}
```

### frappe.client.get_list

```bash
POST /api/method/frappe.client.get_list
{
    "doctype": "Sales Order",
    "filters": {"status": "Draft"},
    "fields": ["name", "customer", "grand_total"],
    "order_by": "creation desc",
    "limit_page_length": 10
}
```

### frappe.client.get

```bash
POST /api/method/frappe.client.get
{
    "doctype": "Customer",
    "name": "CUST-00001"
}
```

### frappe.client.insert

```bash
POST /api/method/frappe.client.insert
{
    "doc": {
        "doctype": "Customer",
        "customer_name": "New Customer",
        "customer_type": "Company"
    }
}
```

### frappe.client.save

```bash
POST /api/method/frappe.client.save
{
    "doc": {
        "doctype": "Customer",
        "name": "CUST-00001",
        "customer_name": "Updated Name"
    }
}
```

### frappe.client.delete

```bash
POST /api/method/frappe.client.delete
{
    "doctype": "Customer",
    "name": "CUST-00001"
}
```

### frappe.client.submit / cancel

```bash
POST /api/method/frappe.client.submit
{
    "doc": {
        "doctype": "Sales Order",
        "name": "SO-00001"
    }
}
```

### frappe.client.get_count

```bash
POST /api/method/frappe.client.get_count
{
    "doctype": "Sales Order",
    "filters": {"status": "Draft"}
}
# {"message": 42}
```

---

## 7. Run Document Method

```bash
POST /api/method/run_doc_method
{
    "dt": "Sales Order",
    "dn": "SO-00001",
    "method": "get_taxes_and_charges"
}
```

```python
# In Sales Order controller
class SalesOrder(Document):
    @frappe.whitelist()
    def get_taxes_and_charges(self):
        return calculate_taxes(self)
```

---

## 8. Utility Methods

### frappe.auth.get_logged_user

```bash
GET /api/method/frappe.auth.get_logged_user
# {"message": "user@example.com"}
```

### frappe.ping

```bash
GET /api/method/frappe.ping
# {"message": "pong"}
```

---

## 9. Foutafhandeling in Methods

```python
@frappe.whitelist()
def safe_operation(docname):
    try:
        doc = frappe.get_doc("Sales Order", docname)
        doc.submit()
        return {"success": True, "name": doc.name}
    
    except frappe.DoesNotExistError:
        frappe.throw(f"Document {docname} not found", frappe.DoesNotExistError)
    
    except frappe.ValidationError as e:
        frappe.throw(str(e), frappe.ValidationError)
    
    except Exception as e:
        frappe.log_error(message=str(e), title="API Error")
        frappe.throw("An error occurred", frappe.ServerError)
```

---

## 10. Permissions in Methods

```python
@frappe.whitelist()
def restricted_operation(customer):
    # Check expliciet permissions
    if not frappe.has_permission("Customer", "write", customer):
        frappe.throw("Permission denied", frappe.PermissionError)
    
    # Of gebruik permission check decorator
    doc = frappe.get_doc("Customer", customer)
    doc.check_permission("write")
    
    # Operatie uitvoeren
    doc.status = "Active"
    doc.save()
    return doc.as_dict()
```
