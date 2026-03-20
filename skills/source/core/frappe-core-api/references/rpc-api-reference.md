# RPC API Reference

## Basic Structure

```
GET/POST /api/method/{dotted.path.to.function}
```

The function MUST be marked with `@frappe.whitelist()`.

---

## GET vs POST

| Method | Usage | Auto Commit |
|--------|-------|-------------|
| **GET** | Read-only operations | No |
| **POST** | State-changing operations | Yes |

---

## Writing Whitelisted Methods

### Basic Pattern

```python
# my_app/api.py
import frappe

@frappe.whitelist()
def get_customer_balance(customer):
    """Get outstanding balance for customer."""
    balance = frappe.db.sql("""
        SELECT SUM(outstanding_amount)
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
    """, customer)[0][0] or 0
    
    return {"customer": customer, "balance": balance}
```

### With Type Hints and Validation

```python
@frappe.whitelist()
def create_payment(
    customer: str,
    amount: float,
    payment_type: str = "Receive"
) -> str:
    """Create new Payment Entry."""
    if not customer:
        frappe.throw(_("Customer is required"))
    
    if amount <= 0:
        frappe.throw(_("Amount must be positive"))
    
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = payment_type
    pe.party_type = "Customer"
    pe.party = customer
    pe.paid_amount = amount
    pe.insert()
    
    return pe.name
```

---

## Decorator Options

### allow_guest

```python
@frappe.whitelist(allow_guest=True)
def public_endpoint():
    """No authentication required."""
    return {"status": "ok", "version": "1.0"}
```

### methods (v14+)

```python
@frappe.whitelist(methods=["POST"])
def only_post_allowed(data):
    """Only POST requests allowed."""
    return process_data(data)
```

### xss_safe

```python
@frappe.whitelist(xss_safe=True)
def return_html():
    """Response will not be XSS-escaped."""
    return "<h1>Safe HTML</h1>"
```

---

## API Calls

### Via cURL

```bash
# GET for read-only
curl -X GET "https://erp.example.com/api/method/my_app.api.get_customer_balance?customer=CUST-00001" \
  -H "Authorization: token api_key:api_secret"

# POST for state-changing
curl -X POST "https://erp.example.com/api/method/my_app.api.create_payment" \
  -H "Authorization: token api_key:api_secret" \
  -H "Content-Type: application/json" \
  -d '{"customer": "CUST-00001", "amount": 500}'
```

### Via Python

```python
import requests

# GET
response = requests.get(
    'https://erp.example.com/api/method/my_app.api.get_customer_balance',
    params={'customer': 'CUST-00001'},
    headers=headers
)

# POST
response = requests.post(
    'https://erp.example.com/api/method/my_app.api.create_payment',
    json={'customer': 'CUST-00001', 'amount': 500},
    headers=headers
)
```

---

## Response Structure

**Success:**
```json
{"message": "return_value_from_function"}
```

**Error:**
```json
{
    "exc_type": "ValidationError",
    "exc": "Traceback...",
    "_server_messages": "[{\"message\": \"Error message\"}]"
}
```

---

## Client-Side Calls (JavaScript)

### frappe.call (Callback)

```javascript
frappe.call({
    method: 'my_app.api.get_customer_balance',
    args: {
        customer: 'CUST-00001'
    },
    callback: function(r) {
        if (r.message) {
            console.log('Balance:', r.message.balance);
        }
    },
    error: function(r) {
        frappe.msgprint(__('Failed to get balance'));
    }
});
```

### frappe.call Options

| Option | Type | Description |
|--------|------|-------------|
| `method` | string | Python method path |
| `args` | object | Arguments |
| `callback` | function | Success callback |
| `error` | function | Error callback |
| `async` | bool | Async call (default: true) |
| `freeze` | bool | Freeze UI during call |
| `freeze_message` | string | Message during freeze |
| `btn` | jQuery | Button to disable |

### frappe.call (Promise)

```javascript
frappe.call({
    method: 'my_app.api.get_customer_balance',
    args: {customer: 'CUST-00001'}
}).then(r => {
    if (r.message) {
        console.log('Balance:', r.message.balance);
    }
});
```

### frappe.xcall (Simpler API - RECOMMENDED)

```javascript
// Async/await - cleanest syntax
const result = await frappe.xcall('my_app.api.get_customer_balance', {
    customer: 'CUST-00001'
});
console.log(result.balance);

// With error handling
try {
    const result = await frappe.xcall('my_app.api.create_payment', {
        customer: 'CUST-00001',
        amount: 500
    });
    frappe.show_alert(__('Payment created: {0}', [result]));
} catch (e) {
    frappe.msgprint(__('Payment failed'));
}
```

---

## frm.call (Form Context)

For controller methods within a document:

```javascript
// Client Script
frm.call('get_linked_doc', {
    throw_if_missing: true
}).then(r => {
    if (r.message) {
        console.log('Linked doc:', r.message);
    }
});
```

**Controller requirement:**
```python
class MyDocType(Document):
    @frappe.whitelist()
    def get_linked_doc(self, throw_if_missing=False):
        if not self.reference_name:
            if throw_if_missing:
                frappe.throw(_("No linked document"))
            return None
        return frappe.get_doc(self.reference_type, self.reference_name)
```

---

## Permission Checks

**ALWAYS** check permissions in whitelisted methods:

```python
@frappe.whitelist()
def get_salary(employee):
    # Check permission
    if not frappe.has_permission("Salary Slip", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    
    return frappe.db.get_value(
        "Salary Slip",
        {"employee": employee},
        "gross_pay"
    )
```

---

## Error Response Pattern

```python
@frappe.whitelist()
def validated_operation(data):
    # Input validation
    if not data:
        frappe.throw(_("Data is required"), frappe.MandatoryError)
    
    try:
        result = process_data(data)
        return {"status": "success", "result": result}
    except frappe.DoesNotExistError as e:
        frappe.throw(_("Record not found: {0}").format(str(e)))
    except Exception as e:
        frappe.log_error(title="API Error", message=str(e))
        frappe.throw(_("Operation failed. Please try again."))
```

---

## Server Script API Type

Alternative to whitelisted methods via UI:

1. Server Script → New
2. Script Type: "API"
3. API Method: `my_app.my_endpoint` (becomes `/api/method/my_app.my_endpoint`)
4. Enable Rate Limit (optional, v15+)

```python
# In Server Script
response = {
    "customer": frappe.form_dict.customer,
    "balance": get_balance(frappe.form_dict.customer)
}
frappe.response["message"] = response
```
