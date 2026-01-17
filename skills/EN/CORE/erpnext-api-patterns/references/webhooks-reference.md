# Webhooks Reference

> Event-driven callbacks to external systems.

---

## 1. Webhook Configuratie

### Via UI

1. Ga naar **Webhook** DocType
2. Maak nieuwe webhook
3. Configureer velden

### Webhook Velden

| Veld | Type | Beschrijving |
|------|------|--------------|
| Webhook Name | Data | Identificatie |
| DocType | Link | Te monitoren DocType |
| Doc Event | Select | Trigger event |
| Request URL | Data | Destination endpoint |
| Request Method | Select | HTTP method |
| Enabled | Check | Actief/inactief |
| Condition | Code | Python expressie |
| Headers | Table | HTTP headers |
| Data | Table | Payload mapping |

---

## 2. Beschikbare Doc Events

| Event | Trigger Moment | Gebruik |
|-------|----------------|---------|
| `after_insert` | Na document creatie | Nieuwe records |
| `on_update` | Na elke save | Wijzigingen |
| `on_submit` | Na submit | Submitted docs |
| `on_cancel` | Na cancel | Cancelled docs |
| `on_trash` | Bij delete | Verwijderingen |
| `on_update_after_submit` | Update na submit | Amendeer flows |
| `on_change` | Na elke wijziging | Alle changes |

---

## 3. Webhook Data Structure

### Default Payload

```json
{
    "event": "on_submit",
    "doctype": "Sales Order",
    "name": "SO-00001",
    "data": {
        "name": "SO-00001",
        "customer": "CUST-00001",
        "customer_name": "Example Corp",
        "grand_total": 15000.00,
        "items": [
            {
                "item_code": "ITEM-001",
                "qty": 10,
                "rate": 1500.00
            }
        ],
        "docstatus": 1
    }
}
```

### Custom Data Mapping

In Webhook Data table:

| Fieldname | Key |
|-----------|-----|
| customer | customerCode |
| grand_total | orderTotal |
| items | lineItems |

**Resultaat:**
```json
{
    "customerCode": "CUST-00001",
    "orderTotal": 15000.00,
    "lineItems": [...]
}
```

---

## 4. Webhook Conditions

### Syntax

Python expressie die True/False returnt. Beschikbare variabelen:
- `doc` - het document object
- `frappe` - frappe namespace

### Voorbeelden

```python
# Alleen submitted documents
doc.docstatus == 1

# Grand total boven drempel
doc.grand_total > 10000

# Specifieke customer group
doc.customer_group == "VIP"

# Combinaties
doc.docstatus == 1 and doc.grand_total > 5000

# Met frappe utils
doc.delivery_date and frappe.utils.date_diff(doc.delivery_date, frappe.utils.today()) < 7
```

---

## 5. HTTP Headers

| Header | Waarde | Gebruik |
|--------|--------|---------|
| Content-Type | application/json | Standaard |
| Authorization | Bearer {token} | Auth bij ontvanger |
| X-Webhook-Secret | {secret} | Signature verificatie |
| X-Request-ID | {uuid} | Request tracking |

---

## 6. Webhook Security

### Secret-based Verification

**Frappe kant:**
1. Configureer secret in Webhook Headers
2. Secret wordt meegestuurd als header

**Ontvanger kant (Python):**
```python
import hmac
import hashlib
from flask import Flask, request

app = Flask(__name__)
WEBHOOK_SECRET = 'your-secret-key'

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verkrijg signature uit header
    signature = request.headers.get('X-Webhook-Secret')
    
    # Bereken verwachte signature
    payload = request.get_data()
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # Vergelijk
    if not hmac.compare_digest(signature, expected):
        return 'Invalid signature', 401
    
    # Verwerk webhook
    data = request.get_json()
    process_webhook(data)
    
    return 'OK', 200
```

**Ontvanger kant (Node.js):**
```javascript
const crypto = require('crypto');
const express = require('express');
const app = express();

const WEBHOOK_SECRET = 'your-secret-key';

app.post('/webhook', express.raw({type: 'application/json'}), (req, res) => {
    const signature = req.headers['x-webhook-secret'];
    
    const expected = crypto
        .createHmac('sha256', WEBHOOK_SECRET)
        .update(req.body)
        .digest('hex');
    
    if (!crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expected)
    )) {
        return res.status(401).send('Invalid signature');
    }
    
    const data = JSON.parse(req.body);
    // Process webhook
    
    res.status(200).send('OK');
});
```

---

## 7. Retry Mechanisme

Frappe retries webhooks bij failure:

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 5 minuten |
| 3 | 30 minuten |
| 4 | 2 uur |
| 5 | Marked as failed |

### Webhook Request Log

Bekijk logs via:
- **Webhook Request Log** DocType
- Filter op Webhook naam
- Bekijk status, response, errors

---

## 8. Complete Webhook Voorbeeld

### Sales Order naar External CRM

**Webhook configuratie:**
```
Name: Sync to CRM
DocType: Sales Order
Doc Event: on_submit
Request URL: https://crm.example.com/api/orders
Request Method: POST
Condition: doc.customer_group == "Enterprise"
```

**Headers:**
| Key | Value |
|-----|-------|
| Authorization | Bearer crm_api_token |
| Content-Type | application/json |

**Data mapping:**
| Fieldname | Key |
|-----------|-----|
| name | order_id |
| customer | customer_code |
| customer_name | customer_name |
| grand_total | total_amount |
| transaction_date | order_date |

**Ontvangen payload:**
```json
{
    "order_id": "SO-00001",
    "customer_code": "CUST-00001",
    "customer_name": "Enterprise Corp",
    "total_amount": 50000.00,
    "order_date": "2024-01-15"
}
```

---

## 9. Webhook via Code

### Programmatisch Webhook Aanmaken

```python
import frappe

webhook = frappe.get_doc({
    "doctype": "Webhook",
    "webhook_name": "Order Notification",
    "webhook_doctype": "Sales Order",
    "webhook_docevent": "on_submit",
    "request_url": "https://api.example.com/orders",
    "request_method": "POST",
    "condition": "doc.grand_total > 1000",
    "enabled": 1,
    "webhook_headers": [
        {"key": "Authorization", "value": "Bearer token"}
    ],
    "webhook_data": [
        {"fieldname": "name", "key": "order_id"},
        {"fieldname": "grand_total", "key": "amount"}
    ]
})
webhook.insert()
```

### Webhook Handmatig Triggeren

```python
# Niet standaard ondersteund - gebruik doc events of custom method
@frappe.whitelist()
def trigger_webhook_manually(doctype, docname):
    doc = frappe.get_doc(doctype, docname)
    
    # Run webhooks voor dit document
    from frappe.integrations.doctype.webhook.webhook import run_webhooks
    run_webhooks(doc, "on_update")
```

---

## 10. Troubleshooting

| Probleem | Oorzaak | Oplossing |
|----------|---------|-----------|
| Webhook niet triggered | Condition False | Condition testen in console |
| 403 error | Auth probleem | Headers/token controleren |
| Timeout | Endpoint te traag | Async processing bij ontvanger |
| Data missing | Mapping fout | Fieldname spelling controleren |
| Duplicate calls | Retry mechanisme | Idempotency implementeren |
