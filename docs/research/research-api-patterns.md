# Research Document: ERPNext API Patterns
> **Fase**: 3.3  
> **Skill**: erpnext-api-patterns  
> **Datum**: 2026-01-17  
> **Bronnen**: docs.frappe.io (REST API, Token Authentication, OAuth2, Webhooks, Rate Limiting)

---

## 1. Overzicht API Types in Frappe

Frappe biedt twee primaire API categorieën:

| Type | Prefix | Functie | Authenticatie |
|------|--------|---------|---------------|
| **REST API** | `/api/resource/` | CRUD operaties op DocTypes | Vereist |
| **RPC API** | `/api/method/` | Whitelisted Python methods | Optioneel (allow_guest) |

**Base URL**: `https://{your-instance}/`

---

## 2. Authenticatie Methods

### 2.1 Token Based Authentication (Aanbevolen voor API)

Meest gebruikte methode voor server-to-server integraties.

#### Token Genereren

1. Ga naar User list → Open een user
2. Klik op "Settings" tab
3. Expand "API Access" sectie
4. Klik "Generate Keys"
5. Kopieer de API Secret (wordt maar 1x getoond!)
6. API Key is zichtbaar in het veld

#### Token Gebruiken

```python
# Python requests voorbeeld
import requests

url = "https://erp.example.com/api/method/frappe.auth.get_logged_user"
headers = {
    'Authorization': 'token api_key:api_secret'
}
response = requests.get(url, headers=headers)
```

```javascript
// JavaScript fetch voorbeeld
fetch('https://erp.example.com/api/resource/Customer', {
    headers: {
        'Authorization': 'token api_key:api_secret',
        'Accept': 'application/json'
    }
})
.then(r => r.json())
.then(data => console.log(data));
```

```bash
# cURL voorbeeld
curl -X GET "https://erp.example.com/api/resource/Customer" \
  -H "Authorization: token api_key:api_secret" \
  -H "Accept: application/json"
```

#### Basic Authentication (Alternatief)

```python
import requests
import base64

credentials = base64.b64encode(b'api_key:api_secret').decode('utf-8')
headers = {
    'Authorization': f'Basic {credentials}'
}
```

### 2.2 Password Based Authentication (Session)

Voor browser-based applicaties die cookies gebruiken.

```python
import requests

# Login - krijgt session cookie
session = requests.Session()
login_response = session.post(
    'https://erp.example.com/api/method/login',
    json={
        'usr': 'username_or_email',
        'pwd': 'password'
    }
)

# Alle volgende requests gebruiken de session cookie automatisch
users = session.get('https://erp.example.com/api/resource/User')
```

**Response bij succes**:
```json
{
    "message": "Logged In",
    "home_page": "/app",
    "full_name": "Administrator"
}
```

**⚠️ WAARSCHUWING**: Session cookies verlopen na 3 dagen. Gebruik Token auth voor long-running integrations.

### 2.3 OAuth 2.0 (Voor Third-Party Apps)

#### Stap 1: OAuth Client Registreren

1. Ga naar OAuth Client List → New
2. Vul in: App Name, Redirect URIs, Default Redirect URI
3. Sla op → Krijg Client ID en Client Secret

#### Stap 2: Authorization Code Verkrijgen

```
GET /api/method/frappe.integrations.oauth2.authorize
?client_id={client_id}
&response_type=code
&scope=openid all
&redirect_uri={redirect_uri}
&state={random_state}
```

User wordt doorverwezen naar login pagina, dan terug naar redirect_uri met `?code=...`

#### Stap 3: Access Token Verkrijgen

```bash
POST /api/method/frappe.integrations.oauth2.get_token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code={authorization_code}
&redirect_uri={redirect_uri}
&client_id={client_id}
```

**Response**:
```json
{
    "access_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "...",
    "scope": "openid all"
}
```

#### Stap 4: API Calls met Bearer Token

```python
headers = {
    'Authorization': 'Bearer {access_token}'
}
response = requests.get('https://erp.example.com/api/resource/User', headers=headers)
```

#### Token Refresh

```bash
POST /api/method/frappe.integrations.oauth2.get_token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token={refresh_token}
&client_id={client_id}
```

---

## 3. REST API - Resource Endpoints

### 3.1 Standaard Headers

**ALTIJD** deze headers meesturen voor JSON responses:

```python
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'token api_key:api_secret'
}
```

### 3.2 List Documents (GET)

```
GET /api/resource/{doctype}
```

**Default gedrag**:
- Retourneert 20 records
- Alleen `name` veld

#### Parameters

| Parameter | Type | Beschrijving |
|-----------|------|--------------|
| `fields` | JSON array | Velden om op te halen |
| `filters` | JSON array | Filter condities |
| `or_filters` | JSON array | OR filter condities |
| `order_by` | string | Sortering (bijv. "modified desc") |
| `limit_start` | int | Offset voor paginering |
| `limit_page_length` | int | Aantal resultaten (alias: `limit`) |
| `as_dict` | bool | Response als dict (default) of list |
| `debug` | bool | Toon uitgevoerde SQL query |

#### Voorbeeld: Gefilterde lijst met velden

```bash
GET /api/resource/Sales Invoice?fields=["name","customer","grand_total","status"]&filters=[["status","=","Paid"]]&order_by=posting_date desc&limit_page_length=50
```

**Response**:
```json
{
    "data": [
        {
            "name": "SINV-00001",
            "customer": "Customer A",
            "grand_total": 1500.00,
            "status": "Paid"
        }
    ]
}
```

#### Filter Operators

| Operator | Beschrijving | Voorbeeld |
|----------|--------------|-----------|
| `=` | Gelijk aan | `["status", "=", "Open"]` |
| `!=` | Niet gelijk aan | `["status", "!=", "Cancelled"]` |
| `>`, `<` | Groter/kleiner dan | `["amount", ">", 1000]` |
| `>=`, `<=` | Groter/kleiner of gelijk | `["date", ">=", "2024-01-01"]` |
| `like` | SQL LIKE | `["name", "like", "%INV%"]` |
| `in` | In lijst | `["status", "in", ["Open", "Pending"]]` |
| `not in` | Niet in lijst | `["status", "not in", ["Cancelled"]]` |
| `is` | IS NULL check | `["reference", "is", "set"]` of `["reference", "is", "not set"]` |
| `between` | Tussen waarden | `["amount", "between", [100, 500]]` |

### 3.3 Create Document (POST)

```
POST /api/resource/{doctype}
```

**Body**: JSON object met velden

```python
import requests

data = {
    "doctype": "Customer",  # Optioneel in body
    "customer_name": "New Customer",
    "customer_type": "Company",
    "customer_group": "Commercial"
}

response = requests.post(
    'https://erp.example.com/api/resource/Customer',
    json=data,
    headers=headers
)
```

**Response**:
```json
{
    "data": {
        "name": "New Customer",
        "owner": "Administrator",
        "creation": "2024-01-15 10:30:00",
        "modified": "2024-01-15 10:30:00",
        "customer_name": "New Customer",
        "customer_type": "Company"
    }
}
```

### 3.4 Read Document (GET)

```
GET /api/resource/{doctype}/{name}
```

```bash
GET /api/resource/Customer/CUST-00001
```

**Response**:
```json
{
    "data": {
        "name": "CUST-00001",
        "customer_name": "Test Customer"
    }
}
```

### 3.5 Update Document (PUT)

```
PUT /api/resource/{doctype}/{name}
```

**Body**: Alleen de velden die gewijzigd moeten worden

```python
data = {
    "customer_group": "Premium"
}

response = requests.put(
    'https://erp.example.com/api/resource/Customer/CUST-00001',
    json=data,
    headers=headers
)
```

### 3.6 Delete Document (DELETE)

```
DELETE /api/resource/{doctype}/{name}
```

```bash
DELETE /api/resource/Customer/CUST-00001
```

**Response**:
```json
{
    "message": "ok"
}
```

### 3.7 Expand Link Fields (v15+)

Automatisch gerelateerde documenten ophalen.

```
GET /api/resource/Sales Invoice/SINV-00001?expand_links=True
```

Of bij listings:

```
GET /api/resource/Sales Invoice?expand=["customer"]
```

---

## 4. RPC API - Method Calls

### 4.1 Basis Structuur

```
GET/POST /api/method/{dotted.path.to.function}
```

De functie MOET gemarkeerd zijn met `@frappe.whitelist()`.

### 4.2 GET vs POST

| Method | Gebruik | Auto Commit |
|--------|---------|-------------|
| **GET** | Read-only operaties | Nee |
| **POST** | State-changing operaties | Ja |

### 4.3 Voorbeeld: Custom Whitelisted Method

**Python (server-side)**:
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

@frappe.whitelist()
def create_payment(customer, amount, payment_type="Receive"):
    """Maak nieuwe Payment Entry."""
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = payment_type
    pe.party_type = "Customer"
    pe.party = customer
    pe.paid_amount = amount
    pe.insert()
    return pe.name
```

**API Call**:
```bash
# GET voor read-only
GET /api/method/my_app.api.get_customer_balance?customer=CUST-00001

# POST voor state-changing
POST /api/method/my_app.api.create_payment
Content-Type: application/json
{"customer": "CUST-00001", "amount": 500}
```

### 4.4 Allow Guest Access

```python
@frappe.whitelist(allow_guest=True)
def public_endpoint():
    """Geen authenticatie vereist."""
    return {"status": "ok"}
```

### 4.5 Response Structure

**Succes**:
```json
{
    "message": "return_value_from_function"
}
```

**Error**:
```json
{
    "exc_type": "ValidationError",
    "exc": "Stack trace...",
    "_server_messages": "[{\"message\": \"Error message\"}]"
}
```

---

## 5. File Uploads

### 5.1 Upload Endpoint

```
POST /api/method/upload_file
Content-Type: multipart/form-data
```

### 5.2 cURL Voorbeeld

```bash
curl -X POST "https://erp.example.com/api/method/upload_file" \
  -H "Authorization: token api_key:api_secret" \
  -H "Accept: application/json" \
  -F "file=@/path/to/document.pdf" \
  -F "doctype=Customer" \
  -F "docname=CUST-00001"
```

### 5.3 Python Voorbeeld

```python
import requests

files = {
    'file': ('document.pdf', open('/path/to/document.pdf', 'rb'), 'application/pdf')
}
data = {
    'doctype': 'Customer',
    'docname': 'CUST-00001',
    'is_private': 1
}

response = requests.post(
    'https://erp.example.com/api/method/upload_file',
    files=files,
    data=data,
    headers={'Authorization': 'token api_key:api_secret'}
)
```

**Response**:
```json
{
    "message": {
        "name": "file_hash.pdf",
        "file_url": "/private/files/file_hash.pdf",
        "is_private": 1,
        "attached_to_doctype": "Customer",
        "attached_to_name": "CUST-00001"
    }
}
```

---

## 6. Webhooks

### 6.1 Webhook Configuratie

Webhooks zijn "user-defined HTTP callbacks" die triggeren op document events.

**Configuratie via UI**:
1. Ga naar Webhook List → New
2. Selecteer DocType (bijv. "Sales Order")
3. Selecteer Event (on_submit, on_update, etc.)
4. Voer Request URL in
5. Optioneel: voeg HTTP Headers toe
6. Optioneel: stel Conditions in

### 6.2 Beschikbare Events

| Event | Trigger |
|-------|---------|
| `after_insert` | Na nieuw document |
| `on_update` | Na elke save |
| `on_submit` | Na submit |
| `on_cancel` | Na cancel |
| `on_trash` | Voor delete |
| `on_update_after_submit` | Na amendment |
| `on_change` | Bij elke wijziging |

### 6.3 Request Structure

```
POST {webhook_url}
Content-Type: application/json

{
    "doctype": "Sales Order",
    "name": "SO-00001",
    "data": {
        "name": "SO-00001",
        "customer": "Customer A",
        "grand_total": 1500.00
    }
}
```

### 6.4 Webhook Security

#### HMAC Signature Verificatie

Als "Webhook Secret" is ingesteld, voegt Frappe een signature header toe:

```
X-Frappe-Webhook-Signature: base64_encoded_hmac_sha256_of_payload
```

**Verificatie in Python**:
```python
import hmac
import hashlib
import base64

def verify_webhook(payload, signature, secret):
    expected = base64.b64encode(
        hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).digest()
    ).decode()
    return hmac.compare_digest(expected, signature)
```

### 6.5 Webhook met Conditions

Conditions gebruiken Jinja2 syntax:

```
{{ doc.grand_total > 10000 }}
{{ doc.customer_group == "Premium" }}
{{ doc.status in ["Submitted", "Paid"] }}
```

### 6.6 Request Structures

**Form-based** (velden in tabel):
```
field1=value1&field2=value2
```

**JSON-based** (met Jinja):
```json
{
    "order_id": "{{ doc.name }}",
    "customer": "{{ doc.customer }}",
    "total": {{ doc.grand_total }}
}
```

---

## 7. Rate Limiting

### 7.1 Configuratie

Rate limiting wordt geconfigureerd in `site_config.json`:

```json
{
    "rate_limit": {
        "limit": 600,
        "window": 3600
    }
}
```

**Parameters**:
- `limit`: Maximaal toegestane request tijd in microseconds (600 = 600 seconden CPU tijd)
- `window`: Tijdvenster in seconden (3600 = 1 uur)

### 7.2 Response Headers

Elke response bevat rate limit info:

```
X-RateLimit-Limit: 600000000
X-RateLimit-Remaining: 518060453
X-RateLimit-Reset: 3513
X-RateLimit-Used: 100560
```

### 7.3 Over Limit Response

```
HTTP/1.1 429 Too Many Requests
```

### 7.4 Server Script Rate Limiting (v14+)

API Server Scripts kunnen eigen rate limits hebben:

```python
# In Server Script configuratie
Enable Rate Limit: ✓
Rate Limit Count: 100
Rate Limit Seconds: 60
```

---

## 8. Client-Side API Calls (frappe.call)

### 8.1 frappe.call Basis

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
    }
});
```

### 8.2 Promise-based Syntax (Aanbevolen)

```javascript
frappe.call({
    method: 'my_app.api.get_customer_balance',
    args: { customer: 'CUST-00001' }
}).then(r => {
    console.log('Balance:', r.message.balance);
});
```

### 8.3 frappe.call Opties

| Optie | Type | Beschrijving |
|-------|------|--------------|
| `method` | string | Python method path |
| `args` | object | Arguments voor de method |
| `callback` | function | Success callback |
| `error` | function | Error callback |
| `async` | bool | Async call (default: true) |
| `freeze` | bool | Freeze UI tijdens call |
| `freeze_message` | string | Message tijdens freeze |
| `btn` | jQuery | Button om te disablen |

### 8.4 frm.call (Form Context)

Voor controller methods:

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

**Controller vereiste**:
```python
class MyDocType(Document):
    @frappe.whitelist()
    def get_linked_doc(self, throw_if_missing=False):
        return frappe.get_doc(self.reference_type, self.reference_name)
```

### 8.5 frappe.xcall (Simpler Promise API)

```javascript
const balance = await frappe.xcall('my_app.api.get_customer_balance', {
    customer: 'CUST-00001'
});
console.log(balance);
```

---

## 9. Error Handling

### 9.1 HTTP Status Codes

| Code | Betekenis |
|------|-----------|
| `200` | Success |
| `400` | Bad Request (validatie fout) |
| `401` | Unauthorized (geen auth) |
| `403` | Forbidden (geen permissions) |
| `404` | Not Found (document bestaat niet) |
| `417` | Expectation Failed (server exception) |
| `429` | Too Many Requests (rate limit) |
| `500` | Internal Server Error |

### 9.2 Error Response Structuur

```json
{
    "exc_type": "ValidationError",
    "exc": "Traceback (most recent call last):\n...",
    "_server_messages": "[{\"message\": \"Customer Name is required\", \"indicator\": \"red\"}]"
}
```

### 9.3 Client-Side Error Handling

```javascript
frappe.call({
    method: 'my_app.api.risky_operation',
    args: { data: data },
    callback: function(r) {
        if (r.message) {
            frappe.show_alert('Success!');
        }
    },
    error: function(r) {
        frappe.msgprint({
            title: __('Error'),
            indicator: 'red',
            message: __('Operation failed. Please try again.')
        });
    }
});
```

### 9.4 Server-Side Error Response

```python
@frappe.whitelist()
def validated_operation(data):
    if not data:
        frappe.throw(_("Data is required"), frappe.MandatoryError)
    
    try:
        # operatie
        return {"status": "success"}
    except Exception as e:
        frappe.log_error(title="API Error", message=str(e))
        frappe.throw(_("Operation failed: {0}").format(str(e)))
```

---

## 10. Best Practices

### 10.1 Authentication

```
✅ Gebruik Token auth voor server-to-server integraties
✅ Gebruik OAuth2 voor third-party applicaties
✅ Genereer aparte API keys per integratie
✅ Roteer API secrets regelmatig
✅ Beperk user permissions tot benodigde DocTypes

❌ NOOIT credentials hardcoden
❌ NOOIT API secrets in version control
❌ NOOIT admin credentials gebruiken voor API
```

### 10.2 API Design

```
✅ Gebruik descriptive method names
✅ Valideer input parameters
✅ Return consistente response structures
✅ Log errors voor debugging
✅ Implementeer proper rate limiting

❌ NOOIT SQL injection vulnerable queries
❌ NOOIT sensitive data in responses zonder permission check
```

### 10.3 Performance

```
✅ Gebruik fields parameter om alleen benodigde velden op te halen
✅ Implementeer paginering voor grote datasets
✅ Gebruik frappe.get_cached_doc voor frequent accessed data
✅ Batch gerelateerde operaties

❌ NOOIT alle documenten ophalen zonder limit
❌ NOOIT overbodige API calls in loops
```

### 10.4 Webhooks

```
✅ Implementeer HMAC signature verificatie
✅ Return snel (< 30 sec) - queue lange operaties
✅ Implementeer retry logica voor failed webhooks
✅ Log webhook payloads voor debugging

❌ NOOIT gevoelige data in webhook payloads zonder encryptie
❌ NOOIT vertrouwen op webhook delivery order
```

---

## 11. Anti-Patterns

### 11.1 ❌ Geen Error Handling

```python
# FOUT - geen error handling
@frappe.whitelist()
def dangerous_operation(docname):
    doc = frappe.get_doc("Customer", docname)
    doc.delete()
    return "done"

# CORRECT - met error handling
@frappe.whitelist()
def safe_operation(docname):
    try:
        doc = frappe.get_doc("Customer", docname)
        doc.delete()
        return {"status": "success", "message": f"{docname} deleted"}
    except frappe.DoesNotExistError:
        frappe.throw(_("Customer {0} does not exist").format(docname))
    except frappe.PermissionError:
        frappe.throw(_("You don't have permission to delete this customer"))
```

### 11.2 ❌ SQL Injection Vulnerable

```python
# FOUT - SQL injection vulnerable
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql(f"SELECT * FROM tabCustomer WHERE name LIKE '%{search_term}%'")

# CORRECT - parameterized query
@frappe.whitelist()
def search_customers(search_term):
    return frappe.db.sql(
        "SELECT * FROM tabCustomer WHERE name LIKE %s",
        (f"%{search_term}%",),
        as_dict=True
    )
```

### 11.3 ❌ Geen Permission Check

```python
# FOUT - geen permission check
@frappe.whitelist()
def get_salary(employee):
    return frappe.db.get_value("Salary Slip", {"employee": employee}, "gross_pay")

# CORRECT - met permission check
@frappe.whitelist()
def get_salary(employee):
    if not frappe.has_permission("Salary Slip", "read"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    return frappe.db.get_value("Salary Slip", {"employee": employee}, "gross_pay")
```

### 11.4 ❌ Credentials Hardcoded

```python
# FOUT
API_KEY = "abc123"
API_SECRET = "secret456"

# CORRECT - gebruik site_config of env vars
api_key = frappe.conf.get("external_api_key")
api_secret = frappe.conf.get("external_api_secret")
```

### 11.5 ❌ Geen Rate Limiting op Heavy Endpoints

```python
# FOUT - heavy operation zonder rate limiting
@frappe.whitelist(allow_guest=True)
def generate_report():
    # Expensive operation
    return heavy_computation()

# CORRECT - met rate limiting (Server Script)
# Of in hooks.py rate_limit configuratie
```

---

## 12. Versie Verschillen (v14 vs v15)

### 12.1 Query Parameters

| Feature | v14 | v15 |
|---------|-----|-----|
| `expand` parameter | Niet beschikbaar | ✅ Ondersteund |
| `expand_links` | Niet beschikbaar | ✅ Ondersteund |
| `limit` alias | Niet beschikbaar | ✅ Alias voor `limit_page_length` |

### 12.2 Server Script API Rate Limiting

| Feature | v14 | v15 |
|---------|-----|-----|
| IP-based rate limiting | Niet beschikbaar | ✅ Per Server Script |
| Enable Rate Limit checkbox | Niet beschikbaar | ✅ Beschikbaar |

### 12.3 OAuth2

| Feature | v14 | v15 |
|---------|-----|-----|
| PKCE Support | Beperkt | ✅ Volledige ondersteuning |
| code_challenge | Optioneel | ✅ Aanbevolen |

---

## 13. Volledige Voorbeelden

### 13.1 Complete Integration Class

```python
# my_app/integration.py
import frappe
import requests
import json
from typing import Optional, Dict, Any, List

class ERPNextClient:
    """Client voor ERPNext API integratie."""
    
    def __init__(self, base_url: str, api_key: str, api_secret: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'token {api_key}:{api_secret}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling."""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        
        if response.status_code == 429:
            raise Exception("Rate limit exceeded")
        
        response.raise_for_status()
        return response.json()
    
    def get_list(
        self,
        doctype: str,
        fields: Optional[List[str]] = None,
        filters: Optional[list] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list:
        """Get list of documents."""
        params = {
            'limit_page_length': limit,
            'limit_start': offset
        }
        if fields:
            params['fields'] = json.dumps(fields)
        if filters:
            params['filters'] = json.dumps(filters)
        
        result = self._request('GET', f'/api/resource/{doctype}', params=params)
        return result.get('data', [])
    
    def get_doc(self, doctype: str, name: str) -> dict:
        """Get single document."""
        result = self._request('GET', f'/api/resource/{doctype}/{name}')
        return result.get('data', {})
    
    def create_doc(self, doctype: str, data: dict) -> dict:
        """Create new document."""
        result = self._request('POST', f'/api/resource/{doctype}', json=data)
        return result.get('data', {})
    
    def update_doc(self, doctype: str, name: str, data: dict) -> dict:
        """Update existing document."""
        result = self._request('PUT', f'/api/resource/{doctype}/{name}', json=data)
        return result.get('data', {})
    
    def delete_doc(self, doctype: str, name: str) -> bool:
        """Delete document."""
        self._request('DELETE', f'/api/resource/{doctype}/{name}')
        return True
    
    def call_method(self, method: str, **kwargs) -> Any:
        """Call whitelisted method."""
        result = self._request('POST', f'/api/method/{method}', json=kwargs)
        return result.get('message')


# Gebruik
client = ERPNextClient(
    base_url='https://erp.example.com',
    api_key=frappe.conf.get('external_api_key'),
    api_secret=frappe.conf.get('external_api_secret')
)

# List customers
customers = client.get_list('Customer', fields=['name', 'customer_name'], limit=50)

# Create order
order = client.create_doc('Sales Order', {
    'customer': 'CUST-00001',
    'items': [{'item_code': 'ITEM-001', 'qty': 5}]
})
```

### 13.2 Webhook Handler (Flask)

```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import base64

app = Flask(__name__)
WEBHOOK_SECRET = 'your_secret_here'

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify Frappe webhook signature."""
    expected = base64.b64encode(
        hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(expected, signature)

@app.route('/webhook/sales-order', methods=['POST'])
def handle_sales_order_webhook():
    # Verify signature
    signature = request.headers.get('X-Frappe-Webhook-Signature')
    if signature and not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    data = request.json
    doctype = data.get('doctype')
    docname = data.get('name')
    doc_data = data.get('data', {})
    
    # Process webhook
    print(f"Received {doctype}: {docname}")
    print(f"Status: {doc_data.get('status')}")
    
    # Queue async processing for long operations
    # process_order_async.delay(docname)
    
    return jsonify({'status': 'received'}), 200

if __name__ == '__main__':
    app.run(port=5000)
```

---

## 14. Bronnen

- [REST API Documentation](https://docs.frappe.io/framework/user/en/api/rest)
- [Token Based Authentication](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/token_based_authentication)
- [OAuth 2](https://docs.frappe.io/framework/user/en/guides/integration/rest_api/oauth-2)
- [Webhooks](https://docs.frappe.io/framework/user/en/guides/integration/webhooks)
- [Rate Limiting](https://docs.frappe.io/framework/user/en/rate-limiting)
- [Server Calls (AJAX)](https://docs.frappe.io/framework/user/en/api/server-calls)

---

**Regelcount**: ~680 regels
**Status**: Research compleet, klaar voor skill creatie
