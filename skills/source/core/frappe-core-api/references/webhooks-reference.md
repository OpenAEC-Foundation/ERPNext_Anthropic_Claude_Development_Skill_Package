# Webhooks Reference

Webhooks are "user-defined HTTP callbacks" that trigger on document events.

---

## Webhook Configuration (UI)

1. Webhook List → New
2. Select DocType (e.g., "Sales Order")
3. Select Event
4. Enter Request URL
5. Optional: Add HTTP Headers
6. Optional: Set Conditions
7. Optional: Webhook Secret for HMAC

---

## Available Events

| Event | Trigger Moment |
|-------|----------------|
| `after_insert` | After new document created |
| `on_update` | After every save |
| `on_submit` | After submit (docstatus: 1) |
| `on_cancel` | After cancel (docstatus: 2) |
| `on_trash` | Before delete |
| `on_update_after_submit` | After amendment |
| `on_change` | On every change |

---

## Request Structure

Frappe sends automatically:

```
POST {webhook_url}
Content-Type: application/json

{
    "doctype": "Sales Order",
    "name": "SO-00001",
    "data": {
        "name": "SO-00001",
        "customer": "Customer A",
        "grand_total": 1500.00,
        "status": "Draft",
        ...all fields...
    }
}
```

---

## Webhook Security

### HMAC Signature Verification

If "Webhook Secret" is set, Frappe adds a signature header:

```
X-Frappe-Webhook-Signature: base64_encoded_hmac_sha256_of_payload
```

### Python Verification

```python
import hmac
import hashlib
import base64

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Frappe webhook HMAC signature."""
    expected = base64.b64encode(
        hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).digest()
    ).decode()
    return hmac.compare_digest(expected, signature)

# Flask example
from flask import Flask, request, jsonify

app = Flask(__name__)
WEBHOOK_SECRET = 'your_secret_here'

@app.route('/webhook/sales-order', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Frappe-Webhook-Signature')
    
    if signature:
        if not verify_webhook_signature(request.data, signature, WEBHOOK_SECRET):
            return jsonify({'error': 'Invalid signature'}), 401
    
    data = request.json
    process_webhook(data)
    
    return jsonify({'status': 'received'}), 200
```

---

## Webhook Conditions

Conditions use Jinja2 syntax to determine if webhook should trigger:

```jinja2
{# Only for large orders #}
{{ doc.grand_total > 10000 }}

{# Only premium customers #}
{{ doc.customer_group == "Premium" }}

{# Specific statuses #}
{{ doc.status in ["Submitted", "Paid"] }}

{# Combination #}
{{ doc.grand_total > 5000 and doc.customer_group == "Premium" }}
```

---

## Request Data Formats

### Form-based (fields in table)

Configure fields individually in Webhook Data:

| Fieldname | Key |
|-----------|-----|
| `customer` | `customer` |
| `grand_total` | `amount` |

Output: `customer=Customer%20A&amount=1500`

### JSON-based (with Jinja)

Select "JSON" as Request Structure and write template:

```json
{
    "order_id": "{{ doc.name }}",
    "customer": "{{ doc.customer }}",
    "total": {{ doc.grand_total }},
    "items": [
        {% for item in doc.items %}
        {
            "item_code": "{{ item.item_code }}",
            "qty": {{ item.qty }}
        }{% if not loop.last %},{% endif %}
        {% endfor %}
    ]
}
```

---

## Webhook Handler Example (Complete)

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import base64
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEBHOOK_SECRET = 'your_secret_here'

def verify_signature(payload: bytes, signature: str) -> bool:
    expected = base64.b64encode(
        hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(expected, signature)

@app.route('/webhook/order', methods=['POST'])
def handle_order_webhook():
    # 1. Verify signature
    signature = request.headers.get('X-Frappe-Webhook-Signature')
    if signature and not verify_signature(request.data, signature):
        logger.warning('Invalid webhook signature')
        return jsonify({'error': 'Invalid signature'}), 401
    
    # 2. Parse data
    try:
        data = request.json
        doctype = data.get('doctype')
        docname = data.get('name')
        doc_data = data.get('data', {})
    except Exception as e:
        logger.error(f'Failed to parse webhook: {e}')
        return jsonify({'error': 'Invalid payload'}), 400
    
    # 3. Log receipt
    logger.info(f'Received webhook: {doctype}/{docname}')
    
    # 4. Process (fast - queue long operations)
    try:
        if doctype == 'Sales Order':
            process_sales_order(docname, doc_data)
    except Exception as e:
        logger.error(f'Webhook processing failed: {e}')
        # Return 200 anyway to prevent retries
    
    # 5. Return quickly
    return jsonify({'status': 'received'}), 200

def process_sales_order(name, data):
    """Process Sales Order webhook."""
    status = data.get('status')
    grand_total = data.get('grand_total', 0)
    
    if status == 'To Deliver and Bill' and grand_total > 10000:
        # Notify sales team for large orders
        send_notification(name, grand_total)

if __name__ == '__main__':
    app.run(port=5000)
```

---

## Best Practices

```
✅ Implement HMAC signature verification
✅ Return quickly (< 30 sec) - queue long operations
✅ Implement retry logic for failed webhooks
✅ Log webhook payloads for debugging
✅ Return 200 even on processing errors (prevent endless retries)
✅ Use idempotent operations (same webhook may arrive multiple times)

❌ NEVER put sensitive data in webhook payloads without encryption
❌ NEVER rely on webhook delivery order
❌ NEVER do synchronous long operations in webhook handler
```

---

## Webhook Debugging

### In ERPNext

1. Webhook Logs: see all sent webhooks
2. Error Logs: see failed requests
3. Request Log: full request/response details

### Testing

```bash
# Test webhook endpoint locally with ngrok
ngrok http 5000

# Simulate webhook
curl -X POST "http://localhost:5000/webhook/order" \
  -H "Content-Type: application/json" \
  -d '{"doctype":"Sales Order","name":"SO-00001","data":{"status":"Draft"}}'
```
