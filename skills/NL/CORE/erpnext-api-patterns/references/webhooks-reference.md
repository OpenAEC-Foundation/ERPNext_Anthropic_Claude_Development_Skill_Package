# Webhooks Reference

Webhooks zijn "user-defined HTTP callbacks" die triggeren op document events.

---

## Webhook Configuratie (UI)

1. Webhook List → New
2. Selecteer DocType (bijv. "Sales Order")
3. Selecteer Event
4. Voer Request URL in
5. Optioneel: HTTP Headers toevoegen
6. Optioneel: Conditions instellen
7. Optioneel: Webhook Secret voor HMAC

---

## Beschikbare Events

| Event | Trigger Moment |
|-------|----------------|
| `after_insert` | Na nieuw document aangemaakt |
| `on_update` | Na elke save |
| `on_submit` | Na submit (docstatus: 1) |
| `on_cancel` | Na cancel (docstatus: 2) |
| `on_trash` | Voor delete |
| `on_update_after_submit` | Na amendment |
| `on_change` | Bij elke wijziging |

---

## Request Structuur

Frappe stuurt automatisch:

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
        ...alle velden...
    }
}
```

---

## Webhook Security

### HMAC Signature Verificatie

Als "Webhook Secret" is ingesteld, voegt Frappe een signature header toe:

```
X-Frappe-Webhook-Signature: base64_encoded_hmac_sha256_of_payload
```

### Python Verificatie

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

Conditions gebruiken Jinja2 syntax om te bepalen of webhook moet triggeren:

```jinja2
{# Alleen voor grote orders #}
{{ doc.grand_total > 10000 }}

{# Alleen premium klanten #}
{{ doc.customer_group == "Premium" }}

{# Specifieke statussen #}
{{ doc.status in ["Submitted", "Paid"] }}

{# Combinatie #}
{{ doc.grand_total > 5000 and doc.customer_group == "Premium" }}
```

---

## Request Data Formats

### Form-based (velden in tabel)

Configureer velden individueel in Webhook Data:

| Fieldname | Key |
|-----------|-----|
| `customer` | `customer` |
| `grand_total` | `amount` |

Output: `customer=Customer%20A&amount=1500`

### JSON-based (met Jinja)

Selecteer "JSON" als Request Structure en schrijf template:

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

## Webhook Handler Voorbeeld (Complete)

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
    
    # 4. Process (snel - queue lange operaties)
    try:
        if doctype == 'Sales Order':
            process_sales_order(docname, doc_data)
    except Exception as e:
        logger.error(f'Webhook processing failed: {e}')
        # Return 200 anyway to prevent retries
    
    # 5. Return snel
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
✅ Implementeer HMAC signature verificatie
✅ Return snel (< 30 sec) - queue lange operaties
✅ Implementeer retry logica voor failed webhooks
✅ Log webhook payloads voor debugging
✅ Return 200 ook bij processing errors (voorkom endless retries)
✅ Gebruik idempotent operaties (dezelfde webhook kan meerdere keren aankomen)

❌ NOOIT gevoelige data in webhook payloads zonder encryptie
❌ NOOIT vertrouwen op webhook delivery order
❌ NOOIT synchrone lange operaties in webhook handler
```

---

## Webhook Debugging

### In ERPNext

1. Webhook Logs: zie alle verzonden webhooks
2. Error Logs: zie gefaalde requests
3. Request Log: full request/response details

### Testing

```bash
# Test webhook endpoint locally met ngrok
ngrok http 5000

# Simuleer webhook
curl -X POST "http://localhost:5000/webhook/order" \
  -H "Content-Type: application/json" \
  -d '{"doctype":"Sales Order","name":"SO-00001","data":{"status":"Draft"}}'
```
