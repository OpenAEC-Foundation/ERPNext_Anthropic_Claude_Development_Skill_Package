# Research Document: Frappe API Patterns

> **Project**: ERPNext Skills Package  
> **Fase**: 3.3  
> **Datum**: 2026-01-17  
> **Bronnen**: Officiële Frappe documentatie (docs.frappe.io), GitHub source code

---

## 1. Overzicht

Frappe biedt drie primaire API-mechanismen:

| API Type | Endpoint Prefix | Gebruik |
|----------|-----------------|---------|
| **Resource API** | `/api/resource/` | CRUD operaties op DocTypes |
| **Method API** | `/api/method/` | Aanroepen van whitelisted Python methods |
| **Webhooks** | DocType configuratie | Event-driven callbacks naar externe systemen |

---

## 2. Authenticatie Methoden

### 2.1 Token Based Authentication (Aanbevolen)

```python
# Token genereren
# Via UI: User → Settings → API Access → Generate Keys
# Via CLI: bench execute frappe.core.doctype.user.user.generate_keys --args ['user_name']
# Via RPC: /api/method/frappe.core.doctype.user.user.generate_keys?user="user_name"
```

**Request format:**
```
Authorization: token <api_key>:<api_secret>
```

**JavaScript voorbeeld:**
```javascript
fetch('http://site.local/api/method/frappe.auth.get_logged_user', {
    headers: {
        'Authorization': 'token api_key:api_secret'
    }
})
.then(r => r.json())
.then(r => console.log(r));
```

**cURL voorbeeld:**
```bash
curl http://site.local/api/resource/Customer \
  -H "Authorization: token api_key:api_secret" \
  -H "Accept: application/json"
```

### 2.2 Password Based Authentication (Session-based)

```javascript
fetch('http://site.local/api/method/login', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        usr: 'username_or_email',
        pwd: 'password'
    })
})
```

**Belangrijk**: Session-based auth vereist cookie handling.

### 2.3 OAuth 2.0

**Authorization Code Flow:**
```
1. GET /api/method/frappe.integrations.oauth2.authorize
   - client_id, redirect_uri, response_type=code, scope

2. POST /api/method/frappe.integrations.oauth2.get_token
   - grant_type=authorization_code, code, redirect_uri, client_id

3. Use Bearer token:
   Authorization: Bearer <access_token>
```

**Endpoints:**
| Endpoint | Functie |
|----------|---------|
| `/api/method/frappe.integrations.oauth2.authorize` | Authorization request |
| `/api/method/frappe.integrations.oauth2.get_token` | Token exchange |
| `/api/method/frappe.integrations.oauth2.revoke_token` | Token revocation |
| `/api/method/frappe.integrations.oauth2.introspect_token` | Token introspection |
| `/api/method/frappe.integrations.oauth2.openid_profile` | User profile |

---

## 3. Resource API (REST CRUD)

### 3.1 Basis Endpoints

| Operatie | Method | Endpoint |
|----------|--------|----------|
| List | GET | `/api/resource/:doctype` |
| Create | POST | `/api/resource/:doctype` |
| Read | GET | `/api/resource/:doctype/:name` |
| Update | PUT | `/api/resource/:doctype/:name` |
| Delete | DELETE | `/api/resource/:doctype/:name` |

### 3.2 Verplichte Headers

```json
{
    "Accept": "application/json",
    "Content-Type": "application/json"
}
```

### 3.3 List Parameters

| Parameter | Type | Beschrijving |
|-----------|------|--------------|
| `fields` | JSON array | Velden om op te halen: `["name", "status"]` |
| `filters` | JSON array | Filter condities: `[["status", "=", "Open"]]` |
| `or_filters` | JSON array | OR filter condities |
| `order_by` | string | Sortering: `"modified desc"` |
| `limit_start` | int | Offset voor paginatie |
| `limit_page_length` | int | Aantal records (default: 20) |
| `limit` | int | Alias voor limit_page_length (v13+) |
| `as_dict` | boolean | False = List[List], True = List[dict] |
| `debug` | boolean | Toon SQL query in response |
| `expand` | JSON array | Expand Link fields naar volledige objecten |

### 3.4 Filter Operators

| Operator | Betekenis |
|----------|-----------|
| `=` | Gelijk aan |
| `!=` | Niet gelijk aan |
| `<` | Kleiner dan |
| `>` | Groter dan |
| `<=` | Kleiner of gelijk |
| `>=` | Groter of gelijk |
| `like` | Pattern matching (gebruik %) |
| `not like` | Inverse pattern matching |
| `in` | In lijst |
| `not in` | Niet in lijst |
| `is` | IS NULL / IS NOT NULL |
| `between` | Tussen twee waarden |

**Voorbeeld complex filter:**
```
GET /api/resource/Sales Order?filters=[
    ["status", "in", ["Draft", "Submitted"]],
    ["grand_total", ">", 1000],
    ["transaction_date", "between", ["2024-01-01", "2024-12-31"]]
]
```

### 3.5 CRUD Voorbeelden

**Create:**
```bash
POST /api/resource/Customer
Content-Type: application/json

{
    "customer_name": "Test Customer",
    "customer_type": "Company",
    "customer_group": "Commercial"
}
```

**Response:**
```json
{
    "data": {
        "name": "CUST-00001",
        "customer_name": "Test Customer",
        "doctype": "Customer",
        ...
    }
}
```

**Read met link expansion:**
```
GET /api/resource/Sales Order/SO-00001?expand_links=True
```

**Update (partial):**
```bash
PUT /api/resource/Customer/CUST-00001

{
    "customer_name": "Updated Name"
}
```

**Delete:**
```bash
DELETE /api/resource/Customer/CUST-00001
```

Response: `{"message": "ok"}`

---

## 4. Method API (RPC)

### 4.1 Basis Gebruik

```
GET/POST /api/method/<dotted.path.to.method>
```

**Voorbeeld:**
```bash
GET /api/method/frappe.auth.get_logged_user

# Response:
{"message": "john@doe.com"}
```

### 4.2 Whitelisted Methods

Methods MOETEN gemarkeerd zijn met `@frappe.whitelist()`:

```python
# In your_app/api.py
import frappe

@frappe.whitelist()
def get_customer_balance(customer):
    """Public API endpoint"""
    return frappe.db.get_value("Customer", customer, "outstanding_amount")

@frappe.whitelist(allow_guest=True)
def public_endpoint():
    """Accessible without authentication"""
    return {"status": "ok"}

@frappe.whitelist(methods=["POST"])
def create_something(data):
    """Only accepts POST requests"""
    # frappe.db.commit() wordt automatisch aangeroepen na POST
    return frappe.get_doc(data).insert()
```

### 4.3 HTTP Method Conventies

| Situatie | HTTP Method | Auto-commit |
|----------|-------------|-------------|
| Data ophalen | GET | Nee |
| Data wijzigen | POST | Ja (`frappe.db.commit()`) |

### 4.4 Response Format

**Success:**
```json
{
    "message": "<return_value>"
}
```

**Error:**
```json
{
    "exc_type": "ValidationError",
    "exc": "<stack_trace>",
    "_server_messages": "[\"Error message\"]"
}
```

### 4.5 Parameters Doorgeven

**Via Query String (GET):**
```
GET /api/method/myapp.api.get_data?customer=CUST-001&limit=10
```

**Via Body (POST):**
```bash
POST /api/method/myapp.api.create_record
Content-Type: application/json

{
    "doctype": "Customer",
    "customer_name": "New Customer"
}
```

---

## 5. Webhooks

### 5.1 Configuratie

Webhooks worden geconfigureerd via het **Webhook DocType**:

| Veld | Beschrijving |
|------|--------------|
| DocType | DocType om te monitoren |
| Doc Event | Trigger event (on_insert, on_update, etc.) |
| Request URL | Destination endpoint |
| Request Method | POST (default), GET, PUT, DELETE |
| Condition | Optional Python expression |
| Headers | Custom HTTP headers |
| Data | Webhook payload structure |

### 5.2 Beschikbare Doc Events

| Event | Trigger |
|-------|---------|
| `after_insert` | Na document creatie |
| `on_update` | Na document update |
| `on_submit` | Na document submit |
| `on_cancel` | Na document cancel |
| `on_trash` | Bij document delete |
| `on_update_after_submit` | Na update van submitted doc |
| `on_change` | Bij elke wijziging |

### 5.3 Webhook Data Structure

**Default payload:**
```json
{
    "doctype": "Sales Order",
    "name": "SO-00001",
    "data": {
        // Full document data
    }
}
```

**Custom data mapping:**
```
lineItems → items
customerName → customer
```

### 5.4 Webhook Security

**Secret-based validation:**
```python
# In receiving endpoint
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### 5.5 Webhook Conditions

```python
# Alleen voor submitted documents met grand_total > 10000
doc.docstatus == 1 and doc.grand_total > 10000
```

---

## 6. File Uploads

### 6.1 Upload Endpoint

```bash
POST /api/method/upload_file
Content-Type: multipart/form-data

-F file=@/path/to/file.pdf
-F doctype=Customer
-F docname=CUST-00001
-F fieldname=attachment
```

### 6.2 Response

```json
{
    "message": {
        "name": "file_hash",
        "file_name": "file.pdf",
        "file_url": "/files/file.pdf"
    }
}
```

---

## 7. Standaard Frappe Methods

### 7.1 Veel Gebruikte Endpoints

| Endpoint | Functie |
|----------|---------|
| `frappe.auth.get_logged_user` | Huidige user |
| `frappe.client.get_count` | Document count |
| `frappe.client.get_value` | Single field value |
| `frappe.client.get_list` | Document list |
| `frappe.client.get` | Full document |
| `frappe.client.insert` | Create document |
| `frappe.client.save` | Update document |
| `frappe.client.delete` | Delete document |
| `frappe.client.submit` | Submit document |
| `frappe.client.cancel` | Cancel document |
| `run_doc_method` | Run document method |

### 7.2 frappe.client Voorbeelden

**get_value:**
```bash
POST /api/method/frappe.client.get_value
{
    "doctype": "Customer",
    "filters": {"name": "CUST-00001"},
    "fieldname": ["customer_name", "outstanding_amount"]
}
```

**get_list:**
```bash
POST /api/method/frappe.client.get_list
{
    "doctype": "Sales Order",
    "filters": {"status": "Draft"},
    "fields": ["name", "customer", "grand_total"],
    "limit_page_length": 50
}
```

**run_doc_method:**
```bash
POST /api/method/run_doc_method
{
    "dt": "Sales Order",
    "dn": "SO-00001",
    "method": "get_taxes_and_charges"
}
```

---

## 8. Error Handling

### 8.1 HTTP Status Codes

| Code | Betekenis |
|------|-----------|
| 200 | Success |
| 403 | Forbidden (permission denied) |
| 404 | Not Found |
| 409 | Conflict (duplicate name) |
| 417 | Validation Error |
| 500 | Server Error |

### 8.2 Error Response Format

```json
{
    "exc_type": "frappe.exceptions.ValidationError",
    "exc": "Traceback (most recent call last):\n...",
    "_server_messages": "[{\"message\": \"Customer Name is required\"}]"
}
```

### 8.3 Client-side Error Handling

```javascript
fetch('/api/resource/Customer', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'token api_key:api_secret'
    },
    body: JSON.stringify(data)
})
.then(response => {
    if (!response.ok) {
        return response.json().then(err => {
            throw new Error(err._server_messages || err.exc_type);
        });
    }
    return response.json();
})
.then(data => console.log(data))
.catch(error => console.error('API Error:', error));
```

---

## 9. Rate Limiting

### 9.1 Standaard Limieten

Frappe heeft ingebouwde rate limiting:

```python
# In site_config.json
{
    "rate_limit": {
        "limit": 600,  # requests per window
        "window": 300  # window in seconds (5 min)
    }
}
```

### 9.2 Custom Rate Limits

```python
# Per method
@frappe.whitelist(rate_limit={"limit": 10, "window": 60})
def limited_endpoint():
    pass
```

---

## 10. Best Practices

### 10.1 Security

1. **ALTIJD Token auth** voor server-to-server communicatie
2. **OAuth 2.0** voor third-party applicaties
3. **HTTPS** verplicht in productie
4. **Minimale permissions** voor API users
5. **Webhook secrets** voor verificatie

### 10.2 Performance

1. Gebruik `fields` parameter - haal alleen noodzakelijke velden op
2. Implementeer paginatie voor grote datasets
3. Cache responses waar mogelijk
4. Batch operaties in plaats van individuele calls
5. Gebruik `run_doc_method` voor server-side logic

### 10.3 Error Handling

1. Controleer HTTP status codes
2. Parse `_server_messages` voor user-friendly errors
3. Log `exc` voor debugging
4. Implementeer retry logic met exponential backoff

---

## 11. Versie Verschillen

### 11.1 v14 vs v15

| Feature | v14 | v15 |
|---------|-----|-----|
| `limit` alias | ✅ | ✅ |
| `expand_links` | ✅ | ✅ |
| `expand` param | ❌ | ✅ |
| Rate limiting decorator | Basic | Enhanced |

### 11.2 v15 Nieuwe Features

- `expand` parameter voor selectieve link expansion
- Verbeterde error messages
- Better rate limiting controls
- Enhanced OAuth 2.0 support

---

## 12. Anti-patterns

### 12.1 ❌ Hardcoded Credentials

```python
# FOUT
headers = {"Authorization": "token abc123:xyz789"}
```

### 12.2 ❌ Geen Error Handling

```javascript
// FOUT
fetch('/api/resource/Customer').then(r => r.json()).then(console.log)
```

### 12.3 ❌ Alle Velden Ophalen

```bash
# FOUT - haalt alle velden op
GET /api/resource/Sales Order

# GOED - alleen noodzakelijke velden
GET /api/resource/Sales Order?fields=["name","status","grand_total"]
```

### 12.4 ❌ GET voor Data Wijzigingen

```bash
# FOUT - wijzigt data met GET
GET /api/method/myapp.api.update_status?status=Done

# GOED
POST /api/method/myapp.api.update_status
{"status": "Done"}
```

### 12.5 ❌ Geen Paginatie

```bash
# FOUT - kan duizenden records retourneren
GET /api/resource/Sales Order?limit_page_length=0

# GOED
GET /api/resource/Sales Order?limit_page_length=100&limit_start=0
```

---

## 13. Samenvatting

| Aspect | Aanbeveling |
|--------|-------------|
| **Auth** | Token voor servers, OAuth voor apps |
| **CRUD** | `/api/resource/` endpoints |
| **RPC** | `/api/method/` + @frappe.whitelist() |
| **Events** | Webhooks met secret verification |
| **Files** | `/api/method/upload_file` |
| **Errors** | Check status codes + _server_messages |

---

## Referenties

1. https://docs.frappe.io/framework/user/en/api/rest
2. https://docs.frappe.io/framework/user/en/guides/integration/rest_api
3. https://docs.frappe.io/framework/user/en/guides/integration/webhooks
4. https://docs.frappe.io/framework/user/en/guides/integration/rest_api/oauth-2
5. https://github.com/frappe/frappe/tree/develop/frappe/integrations

---

*Document aangemaakt: 2026-01-17*  
*Regelcount: ~550 regels*
