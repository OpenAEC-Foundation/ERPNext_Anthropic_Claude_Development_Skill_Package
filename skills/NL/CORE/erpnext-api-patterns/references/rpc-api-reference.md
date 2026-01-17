# RPC API Reference

## Basis Structuur

```
GET/POST /api/method/{dotted.path.to.function}
```

De functie MOET gemarkeerd zijn met `@frappe.whitelist()`.

---

## GET vs POST

| Method | Gebruik | Auto Commit |
|--------|---------|-------------|
| **GET** | Read-only operaties | Nee |
| **POST** | State-changing operaties | Ja |

---

## Whitelisted Method Schrijven

### Basis Pattern

```python
# my_app/api.py
import frappe

@frappe.whitelist()
def get_customer_balance(customer):
    """Haal openstaand saldo op voor klant."""
    balance = frappe.db.sql("""
        SELECT SUM(outstanding_amount)
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
    """, customer)[0][0] or 0
    
    return {"customer": customer, "balance": balance}
```

### Met Type Hints en Validatie

```python
@frappe.whitelist()
def create_payment(
    customer: str,
    amount: float,
    payment_type: str = "Receive"
) -> str:
    """Maak nieuwe Payment Entry."""
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

## Decorator Opties

### allow_guest

```python
@frappe.whitelist(allow_guest=True)
def public_endpoint():
    """Geen authenticatie vereist."""
    return {"status": "ok", "version": "1.0"}
```

### methods (v14+)

```python
@frappe.whitelist(methods=["POST"])
def only_post_allowed(data):
    """Alleen POST requests toegestaan."""
    return process_data(data)
```

### xss_safe

```python
@frappe.whitelist(xss_safe=True)
def return_html():
    """Response wordt niet XSS-escaped."""
    return "<h1>Safe HTML</h1>"
```

---

## API Calls

### Via cURL

```bash
# GET voor read-only
curl -X GET "https://erp.example.com/api/method/my_app.api.get_customer_balance?customer=CUST-00001" \
  -H "Authorization: token api_key:api_secret"

# POST voor state-changing
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

## Response Structuur

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

### frappe.call Opties

| Optie | Type | Beschrijving |
|-------|------|--------------|
| `method` | string | Python method path |
| `args` | object | Arguments |
| `callback` | function | Success callback |
| `error` | function | Error callback |
| `async` | bool | Async call (default: true) |
| `freeze` | bool | Freeze UI tijdens call |
| `freeze_message` | string | Message tijdens freeze |
| `btn` | jQuery | Button om te disablen |

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

### frappe.xcall (Simpler API - AANBEVOLEN)

```javascript
// Async/await - cleanest syntax
const result = await frappe.xcall('my_app.api.get_customer_balance', {
    customer: 'CUST-00001'
});
console.log(result.balance);

// Met error handling
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

Voor controller methods binnen een document:

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

**Controller vereiste:**
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

**ALTIJD** permissions checken in whitelisted methods:

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
    # Input validatie
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

Alternative voor whitelisted methods via UI:

1. Server Script → New
2. Script Type: "API"
3. API Method: `my_app.my_endpoint` (wordt `/api/method/my_app.my_endpoint`)
4. Enable Rate Limit (optioneel, v15+)

```python
# In Server Script
response = {
    "customer": frappe.form_dict.customer,
    "balance": get_balance(frappe.form_dict.customer)
}
frappe.response["message"] = response
```
