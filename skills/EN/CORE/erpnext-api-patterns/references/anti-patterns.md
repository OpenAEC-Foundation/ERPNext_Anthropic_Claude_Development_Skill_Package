# API Anti-Patterns

> Common mistakes and how to avoid them.

---

## 1. Hardcoded Credentials

### ❌ FOUT

```python
# Credentials in code
headers = {
    'Authorization': 'token abc123xyz:secret789'
}

# Of in configuratiebestand in repo
API_KEY = "abc123xyz"
API_SECRET = "secret789"
```

### ✅ CORRECT

```python
import os

# Uit environment variables
API_KEY = os.environ.get('FRAPPE_API_KEY')
API_SECRET = os.environ.get('FRAPPE_API_SECRET')

if not API_KEY or not API_SECRET:
    raise ValueError("API credentials not configured")

headers = {
    'Authorization': f'token {API_KEY}:{API_SECRET}'
}
```

```bash
# In .env bestand (NIET in git!)
FRAPPE_API_KEY=abc123xyz
FRAPPE_API_SECRET=secret789

# .gitignore
.env
*.env
```

---

## 2. Geen Error Handling

### ❌ FOUT

```javascript
// Blind vertrouwen op success
const data = await fetch('/api/resource/Customer').then(r => r.json());
console.log(data.data[0].name);  // Kan crashen
```

### ✅ CORRECT

```javascript
async function getCustomers() {
    const response = await fetch('/api/resource/Customer', {
        headers: { 'Authorization': `token ${API_KEY}:${API_SECRET}` }
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error._server_messages || `HTTP ${response.status}`);
    }
    
    const result = await response.json();
    return result.data || [];
}

try {
    const customers = await getCustomers();
    if (customers.length > 0) {
        console.log(customers[0].name);
    }
} catch (error) {
    console.error('API Error:', error.message);
}
```

---

## 3. Alle Velden Ophalen

### ❌ FOUT

```bash
# Haalt ALLE velden op - traag en veel data
GET /api/resource/Sales Order

# Of erger - alle records zonder limit
GET /api/resource/Sales Order?limit_page_length=0
```

### ✅ CORRECT

```bash
# Alleen benodigde velden
GET /api/resource/Sales Order?fields=["name","status","grand_total"]&limit_page_length=20
```

**Impact:**
- Minder data over de lijn
- Snellere response
- Minder server load

---

## 4. GET voor Data Wijzigingen

### ❌ FOUT

```python
# GET request die data wijzigt
@frappe.whitelist()
def update_status(docname, status):
    # Dit wordt aangeroepen met GET!
    frappe.db.set_value("Task", docname, "status", status)
    return {"success": True}

# Aanroep
GET /api/method/myapp.api.update_status?docname=TASK-001&status=Done
```

**Problemen:**
- Geen auto-commit na GET
- Kan gecached worden
- Kan door prefetch/bots triggered worden

### ✅ CORRECT

```python
@frappe.whitelist(methods=["POST"])
def update_status(docname, status):
    frappe.db.set_value("Task", docname, "status", status)
    return {"success": True}

# Aanroep
POST /api/method/myapp.api.update_status
{"docname": "TASK-001", "status": "Done"}
```

---

## 5. Geen Paginatie

### ❌ FOUT

```python
# Haalt potentieel miljoenen records op
all_orders = client.get_list('Sales Order', limit_page_length=0)

for order in all_orders:  # Memory overflow
    process(order)
```

### ✅ CORRECT

```python
def process_all_orders():
    offset = 0
    batch_size = 100
    
    while True:
        orders = client.get_list(
            'Sales Order',
            limit_start=offset,
            limit_page_length=batch_size
        )
        
        if not orders:
            break
        
        for order in orders:
            process(order)
        
        offset += batch_size
```

---

## 6. Synchrone Webhook Processing

### ❌ FOUT

```python
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_json()
    
    # Lange operatie - webhook timeout
    sync_to_erp(data)  # 30 seconden
    send_notifications(data)  # 10 seconden
    generate_reports(data)  # 20 seconden
    
    return 'OK'  # Te laat - al timeout
```

### ✅ CORRECT

```python
from celery import Celery

celery = Celery('tasks')

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_json()
    
    # Queue voor async processing
    process_webhook.delay(data)
    
    # Snel response
    return 'OK', 200

@celery.task
def process_webhook(data):
    sync_to_erp(data)
    send_notifications(data)
    generate_reports(data)
```

---

## 7. Geen Retry Logic

### ❌ FOUT

```python
def call_api(endpoint):
    response = requests.get(endpoint)
    return response.json()  # Faalt bij tijdelijke errors
```

### ✅ CORRECT

```python
import time
from requests.exceptions import RequestException

def call_api_with_retry(endpoint, max_retries=3, backoff_factor=2):
    for attempt in range(max_retries):
        try:
            response = requests.get(endpoint, timeout=30)
            response.raise_for_status()
            return response.json()
        
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = backoff_factor ** attempt
            print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
            time.sleep(wait_time)
```

---

## 8. Webhook Zonder Idempotency

### ❌ FOUT

```python
@app.route('/webhook', methods=['POST'])
def handle_order():
    data = request.get_json()
    
    # Dubbele verwerking bij retry
    create_invoice(data['order_id'])
    send_confirmation_email(data['customer'])
```

### ✅ CORRECT

```python
processed_webhooks = set()  # Of database

@app.route('/webhook', methods=['POST'])
def handle_order():
    data = request.get_json()
    
    webhook_id = f"{data['doctype']}:{data['name']}:{data['event']}"
    
    if webhook_id in processed_webhooks:
        return 'Already processed', 200
    
    # Process
    create_invoice(data['order_id'])
    send_confirmation_email(data['customer'])
    
    processed_webhooks.add(webhook_id)
    return 'OK', 200
```

---

## 9. Overmatige API Calls

### ❌ FOUT

```python
# N+1 query probleem
customers = client.get_list('Customer', fields=['name'])

for customer in customers:
    # Aparte call per customer
    details = client.get_doc('Customer', customer['name'])
    process(details)
```

### ✅ CORRECT

```python
# Alles in één call
customers = client.get_list(
    'Customer',
    fields=['name', 'customer_name', 'email_id', 'outstanding_amount'],
    limit_page_length=100
)

for customer in customers:
    process(customer)  # Alle data al beschikbaar
```

---

## 10. Secrets in Webhook URLs

### ❌ FOUT

```
# Secret in URL - zichtbaar in logs
Request URL: https://api.example.com/webhook?api_key=secret123
```

### ✅ CORRECT

```
# Secret in header
Request URL: https://api.example.com/webhook

Headers:
X-API-Key: secret123
X-Webhook-Signature: sha256=...
```

---

## 11. Geen Rate Limiting Handling

### ❌ FOUT

```python
# Bombardeert API zonder pauze
for i in range(10000):
    client.create_doc('Customer', {'name': f'Cust-{i}'})
```

### ✅ CORRECT

```python
import time

def batch_create_with_rate_limit(items, rate_per_second=10):
    delay = 1.0 / rate_per_second
    
    for item in items:
        try:
            client.create_doc('Customer', item)
        except Exception as e:
            if '429' in str(e):  # Rate limited
                time.sleep(60)  # Wait and retry
                client.create_doc('Customer', item)
        
        time.sleep(delay)
```

---

## Samenvatting Checklist

| Check | Beschrijving |
|-------|--------------|
| ☐ | Credentials uit environment |
| ☐ | Proper error handling |
| ☐ | Specifieke fields ophalen |
| ☐ | POST voor mutaties |
| ☐ | Paginatie geïmplementeerd |
| ☐ | Async webhook processing |
| ☐ | Retry logic met backoff |
| ☐ | Idempotent webhook handlers |
| ☐ | Batch operations waar mogelijk |
| ☐ | Secrets in headers, niet URLs |
| ☐ | Rate limiting handling |
