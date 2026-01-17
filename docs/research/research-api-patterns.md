# Research Document: ERPNext API Patterns
> **Fase**: 3.3  
> **Skill**: erpnext-api-patterns  
> **Datum**: 2026-01-17  
> **Bronnen**: docs.frappe.io (REST API, Authentication, Webhooks, Rate Limiting)

---

## 1. Overzicht API Typen in Frappe

Frappe biedt twee fundamentele API categorieën:

| Type | Endpoint Prefix | Functie | Authenticatie |
|------|-----------------|---------|---------------|
| **REST/Resource API** | `/api/resource/` | CRUD operaties op DocTypes | Vereist |
| **RPC/Method API** | `/api/method/` | Whitelisted Python functies aanroepen | Vereist* |

*Sommige methods kunnen `allow_guest=True` hebben

**GOUDEN REGEL**: Resource API voor document operaties, Method API voor custom business logic.

---

## 2. Authenticatie Methoden

### 2.1 Token-Based Authentication (Aanbevolen)

De meest robuuste methode voor API integraties.

**Token Genereren**:
1. Ga naar User list → Open user
2. Settings tab → API Access sectie
3. Klik "Generate Keys"
4. Kopieer API Secret (wordt maar één keer getoond)

**Token Formaat**:
```
token <api_key>:<api_secret>
```

**Gebruik in Request**:
```python
import requests

headers = {
    'Authorization': 'token api_key:api_secret',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

response = requests.get(
    'https://site.erpnext.com/api/resource/Customer',
    headers=headers
)
```

**cURL Voorbeeld**:
```bash
curl -X GET "https://site.erpnext.com/api/resource/Customer" \
  -H "Authorization: token api_key:api_secret" \
  -H "Accept: application/json"
```

**JavaScript Voorbeeld**:
```javascript
fetch('https://site.erpnext.com/api/resource/Customer', {
    headers: {
        'Authorization': 'token api_key:api_secret',
        'Accept': 'application/json'
    }
})
.then(r => r.json())
.then(data => console.log(data));
```

### 2.2 Basic Authentication

Alternatief voor token auth - credentials worden base64 encoded.

```python
import requests
import base64

credentials = base64.b64encode(b'api_key:api_secret').decode()
headers = {
    'Authorization': f'Basic {credentials}',
    'Accept': 'application/json'
}

response = requests.get(
    'https://site.erpnext.com/api/resource/Customer',
    headers=headers
)
```

### 2.3 Session-Based Authentication (Password)

Voor web applicaties - gebruikt cookies.

**Login Request**:
```bash
curl -X POST "https://site.erpnext.com/api/method/login" \
  -H "Content-Type: application/json" \
  -d '{"usr":"user@example.com","pwd":"password"}'
```

**Response**:
```json
{
    "message": "Logged In",
    "home_page": "/app",
    "full_name": "Test User"
}
```

De response bevat een `sid` cookie die meegezonden moet worden bij volgende requests.

**Sessie Duur**: 3 dagen (standaard)

**Logout**:
```bash
curl -X POST "https://site.erpnext.com/api/method/logout"
```

### 2.4 OAuth 2.0

Voor third-party applicaties met user consent flow.

**Stap 1: OAuth Client Registreren**
- Ga naar OAuth Client doctype
- Maak nieuwe client aan met redirect URI

**Stap 2: Authorization Code Verkrijgen**
```
GET /api/method/frappe.integrations.oauth2.authorize
    ?client_id=<client_id>
    &response_type=code
    &scope=all openid
    &redirect_uri=<callback_url>
    &state=<random_string>
```

**Stap 3: Token Ophalen**
```bash
POST /api/method/frappe.integrations.oauth2.get_token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=<authorization_code>
&redirect_uri=<callback_url>
&client_id=<client_id>
```

**Response**:
```json
{
    "access_token": "ZJD04ldyyvjuAngjgBrgHwxcOig4vW",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "2pBTDTGhjzs2EWRkcNV1N67yw0nizS",
    "scope": "all openid"
}
```

**Token Gebruiken**:
```python
headers = {
    'Authorization': 'Bearer <access_token>',
    'Accept': 'application/json'
}
```

**Token Refresh**:
```bash
POST /api/method/frappe.integrations.oauth2.get_token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token=<refresh_token>
&client_id=<client_id>
```

---

## 3. Resource API (REST CRUD)

Frappe genereert automatisch REST endpoints voor alle DocTypes.

### 3.1 List Documents (GET)

**Basis Request**:
```
GET /api/resource/{DocType}
```

**Response Formaat**:
```json
{
    "data": [
        {"name": "CUST-00001"},
        {"name": "CUST-00002"}
    ]
}
```

**Query Parameters**:

| Parameter | Type | Beschrijving | Default |
|-----------|------|--------------|---------|
| `fields` | JSON array | Welke velden ophalen | `["name"]` |
| `filters` | JSON array | Filter condities | Geen |
| `or_filters` | JSON array | OR filter condities | Geen |
| `order_by` | string | Sortering | `modified desc` |
| `limit_start` | int | Offset voor paginatie | 0 |
| `limit_page_length` | int | Aantal resultaten | 20 |
| `limit` | int | Alias voor limit_page_length (v13+) | 20 |
| `as_dict` | bool | Response als dict of list | true |
| `debug` | bool | Toon uitgevoerde SQL query | false |

**Voorbeelden**:

```bash
# Specifieke velden ophalen
GET /api/resource/Customer?fields=["name","customer_name","territory"]

# Met filters
GET /api/resource/Customer?filters=[["territory","=","Netherlands"]]

# Complexe filters
GET /api/resource/Task?filters=[["status","in",["Open","Working"]]]

# Met paginatie
GET /api/resource/Customer?limit_start=20&limit_page_length=10

# Sortering
GET /api/resource/Customer?order_by=creation desc

# Debug mode (toont SQL)
GET /api/resource/ToDo?debug=True
```

**Filter Operators**:

| Operator | Beschrijving | Voorbeeld |
|----------|--------------|-----------|
| `=` | Gelijk aan | `["status","=","Open"]` |
| `!=` | Niet gelijk aan | `["status","!=","Closed"]` |
| `>` | Groter dan | `["amount",">","1000"]` |
| `<` | Kleiner dan | `["amount","<","5000"]` |
| `>=` | Groter of gelijk | `["date",">=","2024-01-01"]` |
| `<=` | Kleiner of gelijk | `["date","<=","2024-12-31"]` |
| `like` | Pattern matching | `["name","like","%test%"]` |
| `not like` | Inverse pattern | `["name","not like","%draft%"]` |
| `in` | In lijst | `["status","in",["Open","Working"]]` |
| `not in` | Niet in lijst | `["status","not in",["Cancelled"]]` |
| `is` | IS NULL check | `["parent","is","not set"]` |
| `between` | Tussen waarden | `["date","between",["2024-01-01","2024-12-31"]]` |

### 3.2 Get Single Document (GET)

```
GET /api/resource/{DocType}/{name}
```

**Response**:
```json
{
    "data": {
        "name": "CUST-00001",
        "customer_name": "Test Customer",
        "territory": "Netherlands",
        "customer_group": "Commercial",
        "creation": "2024-01-15 10:30:00",
        "modified": "2024-01-15 10:30:00",
        "owner": "Administrator"
    }
}
```

### 3.3 Create Document (POST)

```
POST /api/resource/{DocType}
Content-Type: application/json

{
    "customer_name": "New Customer",
    "territory": "Netherlands",
    "customer_group": "Commercial"
}
```

**Response**:
```json
{
    "data": {
        "name": "CUST-00003",
        "customer_name": "New Customer",
        "territory": "Netherlands",
        "customer_group": "Commercial",
        "docstatus": 0,
        "creation": "2024-01-17 14:30:00",
        "modified": "2024-01-17 14:30:00",
        "owner": "api_user@example.com"
    }
}
```

**Met Child Tables**:
```json
{
    "doctype": "Sales Order",
    "customer": "CUST-00001",
    "delivery_date": "2024-02-01",
    "items": [
        {
            "item_code": "ITEM-001",
            "qty": 10,
            "rate": 100
        },
        {
            "item_code": "ITEM-002",
            "qty": 5,
            "rate": 200
        }
    ]
}
```

### 3.4 Update Document (PUT)

```
PUT /api/resource/{DocType}/{name}
Content-Type: application/json

{
    "territory": "Belgium"
}
```

**BELANGRIJK**: PUT werkt als PATCH - alleen meegegeven velden worden bijgewerkt.

**Response**:
```json
{
    "data": {
        "name": "CUST-00001",
        "customer_name": "Test Customer",
        "territory": "Belgium",
        "modified": "2024-01-17 15:00:00"
    }
}
```

### 3.5 Delete Document (DELETE)

```
DELETE /api/resource/{DocType}/{name}
```

**Response**:
```json
{
    "message": "ok"
}
```

---

## 4. Method API (RPC Calls)

Roep whitelisted Python functies aan via HTTP.

### 4.1 Basis Syntax

```
GET/POST /api/method/{dotted.path.to.method}
```

**Voorbeeld - Ingebouwde Methode**:
```bash
GET /api/method/frappe.auth.get_logged_user
```

**Response**:
```json
{
    "message": "user@example.com"
}
```

### 4.2 Custom Whitelisted Methods

**Python Definitie**:
```python
# In je_app/je_app/api.py

import frappe

@frappe.whitelist()
def get_customer_summary(customer):
    """Get summary for a customer"""
    doc = frappe.get_doc('Customer', customer)
    
    return {
        'name': doc.name,
        'customer_name': doc.customer_name,
        'outstanding_amount': frappe.db.sql("""
            SELECT SUM(outstanding_amount) 
            FROM `tabSales Invoice` 
            WHERE customer = %s AND docstatus = 1
        """, customer)[0][0] or 0
    }
```

**API Call**:
```bash
# GET voor read-only operaties
GET /api/method/je_app.api.get_customer_summary?customer=CUST-00001

# POST voor state-changing operaties
POST /api/method/je_app.api.get_customer_summary
Content-Type: application/json

{"customer": "CUST-00001"}
```

**Response**:
```json
{
    "message": {
        "name": "CUST-00001",
        "customer_name": "Test Customer",
        "outstanding_amount": 15000.00
    }
}
```

### 4.3 Guest Access

```python
@frappe.whitelist(allow_guest=True)
def public_endpoint():
    """Accessible without authentication"""
    return {"status": "public"}
```

### 4.4 Method Decorators

| Decorator | Functie |
|-----------|---------|
| `@frappe.whitelist()` | Maakt methode toegankelijk via API |
| `@frappe.whitelist(allow_guest=True)` | Geen authenticatie vereist |
| `@frappe.whitelist(methods=['POST'])` | Alleen POST requests |
| `@frappe.whitelist(xss_safe=True)` | Skip XSS sanitization |

### 4.5 Automatische Commit

**BELANGRIJK**: Na een succesvolle POST request wordt automatisch `frappe.db.commit()` aangeroepen.

---

## 5. File Upload API

### 5.1 Upload Endpoint

```
POST /api/method/upload_file
Content-Type: multipart/form-data
```

**cURL Voorbeeld**:
```bash
curl -X POST "https://site.erpnext.com/api/method/upload_file" \
  -H "Authorization: token api_key:api_secret" \
  -F "file=@/path/to/document.pdf" \
  -F "doctype=Sales Invoice" \
  -F "docname=SINV-00001" \
  -F "is_private=1"
```

**Parameters**:

| Parameter | Type | Beschrijving | Vereist |
|-----------|------|--------------|---------|
| `file` | binary | Het bestand | Ja |
| `doctype` | string | Koppel aan DocType | Nee |
| `docname` | string | Koppel aan document | Nee |
| `is_private` | int | 0=public, 1=private | Nee |
| `folder` | string | Target folder | Nee |
| `file_name` | string | Override filename | Nee |

**Response**:
```json
{
    "message": {
        "name": "file-hash-123",
        "file_name": "document.pdf",
        "file_url": "/private/files/document.pdf",
        "is_private": 1,
        "attached_to_doctype": "Sales Invoice",
        "attached_to_name": "SINV-00001"
    }
}
```

### 5.2 JavaScript File Upload

```javascript
// FormData approach
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('doctype', 'Sales Invoice');
formData.append('docname', 'SINV-00001');

fetch('/api/method/upload_file', {
    method: 'POST',
    headers: {
        'Authorization': 'token api_key:api_secret'
    },
    body: formData
})
.then(r => r.json())
.then(data => console.log(data.message));
```

---

## 6. Webhooks

### 6.1 Webhook Configuratie

Webhooks triggeren HTTP callbacks bij document events.

**Webhook DocType Velden**:

| Veld | Beschrijving |
|------|--------------|
| `doctype` | DocType om te monitoren |
| `doc_event` | Event trigger |
| `request_url` | Callback URL |
| `request_method` | POST (default) of andere |
| `condition` | Python conditie (optioneel) |
| `enabled` | Aan/uit toggle |

**Beschikbare Events**:

| Event | Trigger Moment |
|-------|----------------|
| `after_insert` | Na document aanmaken |
| `on_update` | Na document update |
| `on_submit` | Na document submit |
| `on_cancel` | Na document cancel |
| `on_trash` | Voordat document verwijderd wordt |
| `on_update_after_submit` | Na update van submitted doc |
| `on_change` | Bij elke wijziging |

### 6.2 Webhook Payload

**Standaard Payload**:
```json
{
    "doctype": "Sales Order",
    "name": "SO-00001",
    "owner": "Administrator",
    "creation": "2024-01-17 10:00:00",
    "modified": "2024-01-17 10:30:00",
    "customer": "CUST-00001",
    "grand_total": 5000.00,
    "items": [...]
}
```

### 6.3 Webhook met Condities

```python
# Alleen triggeren voor orders boven €1000
doc.grand_total > 1000

# Alleen voor specifieke customer group
doc.customer_group == "VIP"

# Combinatie
doc.grand_total > 1000 and doc.status == "Submitted"
```

### 6.4 Webhook Headers

Custom headers toevoegen (bijv. voor API authenticatie):

| Header | Value |
|--------|-------|
| `X-API-Key` | your-api-key |
| `Content-Type` | application/json |

### 6.5 Webhook Ontvanger Voorbeeld

```python
# Flask endpoint als webhook ontvanger
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.get_json()
    
    doctype = payload.get('doctype')
    name = payload.get('name')
    
    # Process webhook
    print(f"Received webhook for {doctype}: {name}")
    
    return 'OK', 200
```

---

## 7. Response Formats en Error Handling

### 7.1 Success Response Formats

**Resource API**:
```json
{
    "data": { ... }
}
```

**Method API**:
```json
{
    "message": ...
}
```

### 7.2 Error Response Formats

**Standaard Error**:
```json
{
    "exc_type": "ValidationError",
    "exc": "Traceback (most recent call last):\n...",
    "_server_messages": "[\"Error message\"]"
}
```

**Permission Error (403)**:
```json
{
    "exc_type": "PermissionError",
    "exc": "...",
    "_server_messages": "[\"Not permitted\"]"
}
```

**Not Found Error (404)**:
```json
{
    "exc_type": "DoesNotExistError",
    "exc": "...",
    "_server_messages": "[\"Customer CUST-99999 not found\"]"
}
```

### 7.3 HTTP Status Codes

| Code | Betekenis | Wanneer |
|------|-----------|---------|
| 200 | OK | Succesvolle request |
| 201 | Created | Document aangemaakt |
| 403 | Forbidden | Geen permissie |
| 404 | Not Found | Document bestaat niet |
| 409 | Conflict | Duplicate entry |
| 417 | Expectation Failed | Validation error |
| 500 | Server Error | Interne fout |

### 7.4 Error Handling in Client

```python
import requests

def api_call_with_error_handling(url, headers, data=None):
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 403:
            print("Permission denied")
        elif response.status_code == 404:
            print("Resource not found")
        elif response.status_code == 417:
            # Validation error
            error_data = response.json()
            messages = json.loads(error_data.get('_server_messages', '[]'))
            for msg in messages:
                print(f"Validation: {msg}")
        else:
            print(f"HTTP Error: {e}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
```

```javascript
// JavaScript error handling
fetch('/api/resource/Customer', {
    method: 'POST',
    headers: {
        'Authorization': 'token api_key:api_secret',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    body: JSON.stringify(data)
})
.then(response => {
    if (!response.ok) {
        return response.json().then(err => {
            throw {
                status: response.status,
                ...err
            };
        });
    }
    return response.json();
})
.then(data => {
    console.log('Success:', data);
})
.catch(error => {
    if (error.status === 403) {
        console.error('Permission denied');
    } else if (error.status === 417) {
        const messages = JSON.parse(error._server_messages || '[]');
        messages.forEach(msg => console.error('Validation:', msg));
    } else {
        console.error('Error:', error);
    }
});
```

---

## 8. Rate Limiting

### 8.1 Standaard Rate Limiting

Frappe implementeert fixed window rate limiting gebaseerd op request tijd.

**Configuratie in site_config.json**:
```json
{
    "rate_limit": {
        "limit": 100,
        "window": 60
    }
}
```

| Parameter | Beschrijving | Default |
|-----------|--------------|---------|
| `limit` | Totaal toegestane request tijd (sec) | Geen limiet |
| `window` | Reset window in seconden | 3600 (1 uur) |

### 8.2 Rate Limit Decorator

```python
from frappe.rate_limiter import rate_limit

@frappe.whitelist()
@rate_limit(limit=10, seconds=60)  # Max 10 calls per minuut
def expensive_operation():
    # Heavy processing
    pass
```

### 8.3 Rate Limit Response

Wanneer limiet bereikt:
```json
{
    "exc_type": "RateLimitExceeded",
    "_server_messages": "[\"Rate limit exceeded. Try again later.\"]"
}
```

HTTP Status: `429 Too Many Requests`

---

## 9. Versieverschillen v14 vs v15

### 9.1 API Endpoints

| Feature | v14 | v15 |
|---------|-----|-----|
| `limit` parameter | Alias voor `limit_page_length` | Alias voor `limit_page_length` |
| OAuth2 endpoints | Zelfde | Zelfde |
| `as_dict` parameter | Beschikbaar | Beschikbaar |
| `debug` parameter | Beschikbaar | Beschikbaar |

### 9.2 Authenticatie

| Feature | v14 | v15 |
|---------|-----|-----|
| Token auth | Volledig ondersteund | Volledig ondersteund |
| OAuth2 | Volledig ondersteund | Verbeterde PKCE support |
| API Key regeneratie | Handmatig | Handmatig |

### 9.3 Response Format

Geen significante wijzigingen tussen v14 en v15 voor REST API responses.

### 9.4 Rate Limiting

| Feature | v14 | v15 |
|---------|-----|-----|
| Fixed window | Ja | Ja |
| Per-user limits | Ja | Ja |
| Custom decorators | Ja | Ja |

---

## 10. Client-Side API (frappe.call)

### 10.1 frappe.call Syntax

```javascript
frappe.call({
    method: 'dotted.path.to.method',
    args: {
        param1: 'value1',
        param2: 'value2'
    },
    type: 'POST',  // GET, POST, PUT, DELETE
    freeze: true,  // Freeze screen tijdens request
    freeze_message: 'Loading...',
    btn: $('.btn-primary'),  // Disable button during request
    async: true,
    callback: function(r) {
        if (r.message) {
            console.log(r.message);
        }
    },
    error: function(r) {
        console.error('Error:', r);
    },
    always: function(r) {
        // Altijd uitgevoerd
    }
});
```

### 10.2 frappe.db Shortcuts

```javascript
// Get document
frappe.db.get_doc('Customer', 'CUST-00001')
    .then(doc => console.log(doc));

// Get list
frappe.db.get_list('Customer', {
    fields: ['name', 'customer_name'],
    filters: { territory: 'Netherlands' },
    limit: 20
}).then(records => console.log(records));

// Get value
frappe.db.get_value('Customer', 'CUST-00001', 'customer_name')
    .then(r => console.log(r.message.customer_name));

// Set value
frappe.db.set_value('Customer', 'CUST-00001', 'territory', 'Belgium')
    .then(r => console.log('Updated:', r.message));

// Count
frappe.db.count('Customer', { territory: 'Netherlands' })
    .then(count => console.log('Count:', count));

// Exists
frappe.db.exists('Customer', 'CUST-00001')
    .then(exists => console.log('Exists:', exists));

// Delete
frappe.db.delete_doc('Customer', 'CUST-00001');

// Insert
frappe.db.insert({
    doctype: 'Customer',
    customer_name: 'New Customer',
    territory: 'Netherlands'
}).then(doc => console.log('Created:', doc));
```

---

## 11. Best Practices

### 11.1 Authenticatie

```python
# ✅ CORRECT: Token auth voor integraties
headers = {
    'Authorization': 'token api_key:api_secret',
    'Accept': 'application/json'
}

# ❌ FOUT: Credentials in URL
url = 'https://site.com/api/resource/Customer?api_key=xxx&api_secret=yyy'

# ✅ CORRECT: Dedicated API user
# Maak een user specifiek voor API toegang met minimale rechten

# ❌ FOUT: Administrator gebruiken voor API
```

### 11.2 Error Handling

```python
# ✅ CORRECT: Robuuste error handling
def make_api_call(endpoint, data):
    try:
        response = requests.post(
            f'{base_url}{endpoint}',
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise

# ❌ FOUT: Geen error handling
response = requests.post(url, json=data)
return response.json()
```

### 11.3 Paginatie

```python
# ✅ CORRECT: Alle records ophalen met paginatie
def get_all_customers():
    customers = []
    limit = 100
    offset = 0
    
    while True:
        response = requests.get(
            f'{base_url}/api/resource/Customer',
            headers=headers,
            params={
                'limit_start': offset,
                'limit_page_length': limit,
                'fields': '["name","customer_name"]'
            }
        )
        data = response.json().get('data', [])
        
        if not data:
            break
            
        customers.extend(data)
        offset += limit
    
    return customers

# ❌ FOUT: Geen paginatie (krijgt alleen eerste 20)
response = requests.get(f'{base_url}/api/resource/Customer')
```

### 11.4 Filters

```python
# ✅ CORRECT: Server-side filtering
params = {
    'filters': json.dumps([
        ['status', '=', 'Active'],
        ['territory', '=', 'Netherlands']
    ])
}
response = requests.get(f'{base_url}/api/resource/Customer', params=params)

# ❌ FOUT: Client-side filtering (inefficiënt)
response = requests.get(f'{base_url}/api/resource/Customer')
customers = [c for c in response.json()['data'] if c.get('status') == 'Active']
```

### 11.5 Batch Operaties

```python
# ✅ CORRECT: Gebruik run_doc_method voor meerdere acties
@frappe.whitelist()
def bulk_update_status(customers, new_status):
    """Update status for multiple customers"""
    updated = []
    for customer_name in customers:
        doc = frappe.get_doc('Customer', customer_name)
        doc.status = new_status
        doc.save()
        updated.append(doc.name)
    
    frappe.db.commit()
    return updated

# ❌ FOUT: Individuele API calls voor elke update
for customer in customers:
    requests.put(f'/api/resource/Customer/{customer}', json={'status': 'Active'})
```

---

## 12. Anti-Patterns

### 12.1 Security Anti-Patterns

```python
# ❌ ANTI-PATTERN: Credentials in code
API_KEY = 'hardcoded_key'
API_SECRET = 'hardcoded_secret'

# ✅ CORRECT: Environment variables
import os
API_KEY = os.environ.get('ERPNEXT_API_KEY')
API_SECRET = os.environ.get('ERPNEXT_API_SECRET')
```

```python
# ❌ ANTI-PATTERN: Administrator account voor API
headers = {'Authorization': 'token admin_key:admin_secret'}

# ✅ CORRECT: Dedicated API user met minimale rechten
# Maak een user met alleen de benodigde DocType permissions
```

### 12.2 Performance Anti-Patterns

```python
# ❌ ANTI-PATTERN: N+1 queries via API
customers = get_all_customers()
for c in customers:
    invoices = requests.get(f'/api/resource/Sales Invoice?filters=[["customer","=","{c}"]]')

# ✅ CORRECT: Batch query
@frappe.whitelist()
def get_customers_with_invoices():
    return frappe.db.sql("""
        SELECT c.name, c.customer_name, 
               COUNT(si.name) as invoice_count
        FROM `tabCustomer` c
        LEFT JOIN `tabSales Invoice` si ON si.customer = c.name
        GROUP BY c.name
    """, as_dict=True)
```

```python
# ❌ ANTI-PATTERN: Geen paginatie
response = requests.get('/api/resource/Customer')  # Max 20 records!

# ✅ CORRECT: Altijd paginatie gebruiken
response = requests.get('/api/resource/Customer?limit_page_length=0')  # Alle records
```

### 12.3 Error Handling Anti-Patterns

```python
# ❌ ANTI-PATTERN: Exceptions negeren
try:
    response = requests.post(url, json=data)
except:
    pass  # Silent failure

# ✅ CORRECT: Log en handle errors
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    frappe.log_error(f"API call failed: {e}", "API Integration Error")
    raise
```

### 12.4 Data Anti-Patterns

```python
# ❌ ANTI-PATTERN: Vertrouwen op client-side data
@frappe.whitelist(allow_guest=True)
def process_order(order_data):
    # Geen validatie van order_data
    frappe.get_doc(order_data).insert()

# ✅ CORRECT: Server-side validatie
@frappe.whitelist(allow_guest=True)
def process_order(order_data):
    # Valideer en sanitize input
    if not isinstance(order_data, dict):
        frappe.throw("Invalid order data")
    
    allowed_fields = ['item_code', 'qty', 'customer']
    clean_data = {k: v for k, v in order_data.items() if k in allowed_fields}
    
    # Verdere validatie...
```

---

## 13. Complete Voorbeelden

### 13.1 Python Integration Client

```python
"""
ERPNext API Client
Complete voorbeeld van een API integratie
"""

import os
import json
import requests
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ERPNextClient:
    """Client voor ERPNext REST API"""
    
    def __init__(self, base_url: str, api_key: str, api_secret: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'token {api_key}:{api_secret}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _request(self, method: str, endpoint: str, 
                 params: Dict = None, data: Dict = None) -> Dict:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_data = {}
            try:
                error_data = response.json()
            except:
                pass
            
            logger.error(f"HTTP Error {response.status_code}: {e}")
            logger.error(f"Response: {error_data}")
            raise
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    # Resource API Methods
    
    def get_list(self, doctype: str, fields: List[str] = None,
                 filters: List = None, limit: int = 20,
                 offset: int = 0) -> List[Dict]:
        """Get list of documents"""
        params = {
            'limit_page_length': limit,
            'limit_start': offset
        }
        if fields:
            params['fields'] = json.dumps(fields)
        if filters:
            params['filters'] = json.dumps(filters)
        
        response = self._request('GET', f'/api/resource/{doctype}', params=params)
        return response.get('data', [])
    
    def get_all(self, doctype: str, fields: List[str] = None,
                filters: List = None, batch_size: int = 100) -> List[Dict]:
        """Get all documents with automatic pagination"""
        all_docs = []
        offset = 0
        
        while True:
            docs = self.get_list(
                doctype=doctype,
                fields=fields,
                filters=filters,
                limit=batch_size,
                offset=offset
            )
            
            if not docs:
                break
            
            all_docs.extend(docs)
            offset += batch_size
            
            logger.info(f"Fetched {len(all_docs)} {doctype} documents...")
        
        return all_docs
    
    def get_doc(self, doctype: str, name: str) -> Dict:
        """Get single document"""
        response = self._request('GET', f'/api/resource/{doctype}/{name}')
        return response.get('data', {})
    
    def create_doc(self, doctype: str, data: Dict) -> Dict:
        """Create new document"""
        response = self._request('POST', f'/api/resource/{doctype}', data=data)
        return response.get('data', {})
    
    def update_doc(self, doctype: str, name: str, data: Dict) -> Dict:
        """Update existing document"""
        response = self._request('PUT', f'/api/resource/{doctype}/{name}', data=data)
        return response.get('data', {})
    
    def delete_doc(self, doctype: str, name: str) -> Dict:
        """Delete document"""
        return self._request('DELETE', f'/api/resource/{doctype}/{name}')
    
    # Method API
    
    def call_method(self, method: str, args: Dict = None) -> any:
        """Call whitelisted method"""
        response = self._request('POST', f'/api/method/{method}', data=args or {})
        return response.get('message')
    
    # Convenience Methods
    
    def get_logged_user(self) -> str:
        """Get currently authenticated user"""
        return self.call_method('frappe.auth.get_logged_user')
    
    def run_report(self, report_name: str, filters: Dict = None) -> List[Dict]:
        """Run a report and get results"""
        return self.call_method(
            'frappe.desk.query_report.run',
            {
                'report_name': report_name,
                'filters': filters or {}
            }
        )


# Usage Example
if __name__ == '__main__':
    # Initialize client
    client = ERPNextClient(
        base_url=os.environ.get('ERPNEXT_URL', 'https://site.erpnext.com'),
        api_key=os.environ.get('ERPNEXT_API_KEY'),
        api_secret=os.environ.get('ERPNEXT_API_SECRET')
    )
    
    # Test connection
    user = client.get_logged_user()
    print(f"Connected as: {user}")
    
    # Get customers
    customers = client.get_list(
        doctype='Customer',
        fields=['name', 'customer_name', 'territory'],
        filters=[['territory', '=', 'Netherlands']],
        limit=10
    )
    print(f"Found {len(customers)} customers")
    
    # Create customer
    new_customer = client.create_doc('Customer', {
        'customer_name': 'API Test Customer',
        'customer_group': 'Commercial',
        'territory': 'Netherlands'
    })
    print(f"Created customer: {new_customer['name']}")
    
    # Update customer
    updated = client.update_doc('Customer', new_customer['name'], {
        'customer_group': 'Individual'
    })
    print(f"Updated customer group to: {updated['customer_group']}")
    
    # Delete customer
    client.delete_doc('Customer', new_customer['name'])
    print("Customer deleted")
```

### 13.2 Webhook Handler

```python
"""
Webhook Handler for ERPNext
Voorbeeld van een Flask webhook ontvanger
"""

from flask import Flask, request, jsonify
import hmac
import hashlib
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Webhook secret (configureer in ERPNext webhook)
WEBHOOK_SECRET = 'your-webhook-secret'


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature"""
    if not WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured
    
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


@app.route('/webhook/erpnext', methods=['POST'])
def handle_erpnext_webhook():
    """Handle incoming webhook from ERPNext"""
    
    # Verify signature if present
    signature = request.headers.get('X-Frappe-Webhook-Signature', '')
    if WEBHOOK_SECRET and not verify_signature(request.data, signature):
        logger.warning("Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Parse payload
    try:
        payload = request.get_json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        return jsonify({'error': 'Invalid JSON'}), 400
    
    # Extract common fields
    doctype = payload.get('doctype')
    docname = payload.get('name')
    event = request.headers.get('X-Frappe-Webhook-Event', 'unknown')
    
    logger.info(f"Received webhook: {event} for {doctype}/{docname}")
    
    # Route to appropriate handler
    handlers = {
        'Sales Order': handle_sales_order,
        'Sales Invoice': handle_sales_invoice,
        'Customer': handle_customer,
    }
    
    handler = handlers.get(doctype)
    if handler:
        try:
            handler(payload, event)
        except Exception as e:
            logger.error(f"Handler error: {e}")
            return jsonify({'error': str(e)}), 500
    else:
        logger.warning(f"No handler for doctype: {doctype}")
    
    return jsonify({'status': 'ok'}), 200


def handle_sales_order(payload: dict, event: str):
    """Process Sales Order webhooks"""
    name = payload.get('name')
    customer = payload.get('customer')
    grand_total = payload.get('grand_total')
    
    if event == 'on_submit':
        logger.info(f"Sales Order {name} submitted: {customer} - €{grand_total}")
        # Trigger external process...
        
    elif event == 'on_cancel':
        logger.info(f"Sales Order {name} cancelled")
        # Handle cancellation...


def handle_sales_invoice(payload: dict, event: str):
    """Process Sales Invoice webhooks"""
    name = payload.get('name')
    
    if event == 'on_submit':
        logger.info(f"Invoice {name} submitted - sending to accounting system")
        # Sync to external accounting...


def handle_customer(payload: dict, event: str):
    """Process Customer webhooks"""
    name = payload.get('name')
    customer_name = payload.get('customer_name')
    
    if event == 'after_insert':
        logger.info(f"New customer created: {customer_name}")
        # Sync to CRM...
        
    elif event == 'on_update':
        logger.info(f"Customer updated: {customer_name}")
        # Update external systems...


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 13.3 JavaScript Integration

```javascript
/**
 * ERPNext API Client for JavaScript
 * Browser/Node.js compatible
 */

class ERPNextAPI {
    constructor(baseUrl, apiKey, apiSecret) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.auth = `token ${apiKey}:${apiSecret}`;
    }
    
    async request(method, endpoint, data = null, params = null) {
        let url = `${this.baseUrl}${endpoint}`;
        
        if (params) {
            const searchParams = new URLSearchParams();
            for (const [key, value] of Object.entries(params)) {
                if (value !== null && value !== undefined) {
                    searchParams.append(key, 
                        typeof value === 'object' ? JSON.stringify(value) : value
                    );
                }
            }
            url += '?' + searchParams.toString();
        }
        
        const options = {
            method,
            headers: {
                'Authorization': this.auth,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        if (data && ['POST', 'PUT', 'PATCH'].includes(method)) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
            error.status = response.status;
            error.data = errorData;
            throw error;
        }
        
        return response.json();
    }
    
    // Resource API
    
    async getList(doctype, { fields, filters, limit = 20, offset = 0 } = {}) {
        const params = {
            limit_page_length: limit,
            limit_start: offset
        };
        if (fields) params.fields = fields;
        if (filters) params.filters = filters;
        
        const response = await this.request('GET', `/api/resource/${doctype}`, null, params);
        return response.data || [];
    }
    
    async getDoc(doctype, name) {
        const response = await this.request('GET', `/api/resource/${doctype}/${encodeURIComponent(name)}`);
        return response.data;
    }
    
    async createDoc(doctype, data) {
        const response = await this.request('POST', `/api/resource/${doctype}`, data);
        return response.data;
    }
    
    async updateDoc(doctype, name, data) {
        const response = await this.request('PUT', `/api/resource/${doctype}/${encodeURIComponent(name)}`, data);
        return response.data;
    }
    
    async deleteDoc(doctype, name) {
        return this.request('DELETE', `/api/resource/${doctype}/${encodeURIComponent(name)}`);
    }
    
    // Method API
    
    async call(method, args = {}) {
        const response = await this.request('POST', `/api/method/${method}`, args);
        return response.message;
    }
    
    // Convenience methods
    
    async getLoggedUser() {
        return this.call('frappe.auth.get_logged_user');
    }
    
    async searchLink(doctype, txt, filters = {}) {
        return this.call('frappe.desk.search.search_link', {
            doctype,
            txt,
            filters
        });
    }
}


// Usage example
async function example() {
    const api = new ERPNextAPI(
        'https://site.erpnext.com',
        'your-api-key',
        'your-api-secret'
    );
    
    try {
        // Test connection
        const user = await api.getLoggedUser();
        console.log('Connected as:', user);
        
        // Get customers
        const customers = await api.getList('Customer', {
            fields: ['name', 'customer_name', 'territory'],
            filters: [['territory', '=', 'Netherlands']],
            limit: 10
        });
        console.log('Customers:', customers);
        
        // Create customer
        const newCustomer = await api.createDoc('Customer', {
            customer_name: 'API Test Customer',
            customer_group: 'Commercial',
            territory: 'Netherlands'
        });
        console.log('Created:', newCustomer);
        
        // Update
        const updated = await api.updateDoc('Customer', newCustomer.name, {
            customer_group: 'Individual'
        });
        console.log('Updated:', updated);
        
        // Delete
        await api.deleteDoc('Customer', newCustomer.name);
        console.log('Deleted');
        
    } catch (error) {
        console.error('API Error:', error.message);
        if (error.data) {
            console.error('Details:', error.data);
        }
    }
}

// Run example
example();
```

---

## 14. Checklist voor API Integraties

### Planning
- [ ] API user aangemaakt met minimale rechten
- [ ] API keys veilig opgeslagen (niet in code)
- [ ] Rate limits bepaald en getest
- [ ] Error handling strategie gedefinieerd

### Implementatie
- [ ] Token-based auth gebruikt
- [ ] Paginatie geïmplementeerd voor lists
- [ ] Server-side filtering gebruikt
- [ ] Timeouts geconfigureerd
- [ ] Retry logic voor transient errors
- [ ] Logging geïmplementeerd

### Testing
- [ ] Alle CRUD operaties getest
- [ ] Error scenarios getest
- [ ] Permission errors getest
- [ ] Rate limiting getest
- [ ] Webhook delivery getest

### Production
- [ ] API keys geroteerd
- [ ] Monitoring ingesteld
- [ ] Alerts voor errors
- [ ] Documentatie up-to-date

---

## Bronvermelding

- [Frappe REST API Documentation](https://docs.frappe.io/framework/user/en/guides/integration/rest_api)
- [Token Based Authentication](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication)
- [OAuth 2](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/oauth-2)
- [Webhooks](https://docs.frappe.io/framework/user/en/guides/integration/webhooks)
- [Rate Limiting](https://docs.frappe.io/framework/v14/user/en/rate-limiting)
- [Server Calls (AJAX)](https://docs.frappe.io/framework/v14/user/en/api/server-calls)

---

*Document gegenereerd voor ERPNext Skills Package - Fase 3.3*
