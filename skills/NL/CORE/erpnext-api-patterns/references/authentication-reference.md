# Authentication Reference

> Alle authenticatie methoden voor Frappe API toegang.

---

## 1. Token Based Authentication

### Token Genereren

**Via UI:**
1. Ga naar User list
2. Open de user
3. Settings tab → API Access → Generate Keys
4. Kopieer API Secret (wordt maar één keer getoond)

**Via CLI:**
```bash
bench execute frappe.core.doctype.user.user.generate_keys --args ['api_user@example.com']
```

**Via RPC:**
```bash
POST /api/method/frappe.core.doctype.user.user.generate_keys
{"user": "api_user@example.com"}
```

### Token Gebruiken

**Header format:**
```
Authorization: token <api_key>:<api_secret>
```

**JavaScript:**
```javascript
const API_KEY = process.env.FRAPPE_API_KEY;
const API_SECRET = process.env.FRAPPE_API_SECRET;

async function callFrappeAPI(endpoint) {
    const response = await fetch(`https://site.local${endpoint}`, {
        headers: {
            'Authorization': `token ${API_KEY}:${API_SECRET}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error._server_messages || response.statusText);
    }
    
    return response.json();
}
```

**Python:**
```python
import requests
import os

API_KEY = os.environ.get('FRAPPE_API_KEY')
API_SECRET = os.environ.get('FRAPPE_API_SECRET')
BASE_URL = 'https://site.local'

def call_frappe_api(endpoint, method='GET', data=None):
    headers = {
        'Authorization': f'token {API_KEY}:{API_SECRET}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    response = requests.request(
        method,
        f'{BASE_URL}{endpoint}',
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()
```

**cURL:**
```bash
curl -X GET "https://site.local/api/resource/Customer" \
  -H "Authorization: token api_key:api_secret" \
  -H "Accept: application/json"
```

---

## 2. Basic Authentication

**Header format:**
```
Authorization: Basic <base64(api_key:api_secret)>
```

**Python:**
```python
import base64

credentials = base64.b64encode(f'{API_KEY}:{API_SECRET}'.encode()).decode()
headers = {
    'Authorization': f'Basic {credentials}'
}
```

---

## 3. OAuth 2.0

### Setup OAuth Client

1. Ga naar **OAuth Client** DocType
2. Maak nieuwe client:
   - App Name: Your App
   - Redirect URIs: https://yourapp.com/callback
   - Default Redirect URI: https://yourapp.com/callback
   - Grant Type: Authorization Code
   - Scopes: all (of specifieke scopes)

### Authorization Code Flow

**Stap 1: Authorization Request**
```
GET /api/method/frappe.integrations.oauth2.authorize
    ?client_id=<client_id>
    &response_type=code
    &scope=openid all
    &redirect_uri=https://yourapp.com/callback
    &state=<random_state>
```

**Stap 2: User geeft toestemming → redirect met code**
```
https://yourapp.com/callback?code=<auth_code>&state=<state>
```

**Stap 3: Exchange code voor token**
```bash
POST /api/method/frappe.integrations.oauth2.get_token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=<auth_code>
&redirect_uri=https://yourapp.com/callback
&client_id=<client_id>
```

**Response:**
```json
{
    "access_token": "token_string",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "refresh_token_string",
    "scope": "openid all"
}
```

**Stap 4: Gebruik Bearer token**
```
Authorization: Bearer <access_token>
```

### Token Refresh

```bash
POST /api/method/frappe.integrations.oauth2.get_token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token=<refresh_token>
&client_id=<client_id>
```

### Token Revocation

```bash
POST /api/method/frappe.integrations.oauth2.revoke_token
Content-Type: application/x-www-form-urlencoded

token=<access_token>
```

### Token Introspection

```bash
POST /api/method/frappe.integrations.oauth2.introspect_token
Content-Type: application/x-www-form-urlencoded

token=<access_token>
&token_type_hint=access_token
```

---

## 4. Session/Cookie Authentication

**Login:**
```javascript
const response = await fetch('https://site.local/api/method/login', {
    method: 'POST',
    credentials: 'include',  // Belangrijk voor cookies
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        usr: 'user@example.com',
        pwd: 'password'
    })
});
```

**Volgende requests:**
```javascript
// Cookies worden automatisch meegestuurd
const data = await fetch('https://site.local/api/resource/Customer', {
    credentials: 'include'
});
```

**Logout:**
```javascript
await fetch('https://site.local/api/method/logout', {
    method: 'POST',
    credentials: 'include'
});
```

---

## 5. Beslisboom

| Scenario | Methode |
|----------|---------|
| Server-to-server integratie | Token |
| Third-party applicatie | OAuth 2.0 |
| Single Page Application | Session + CSRF |
| Mobile app | OAuth 2.0 |
| Webhook ontvanger | API Key validatie |

---

## 6. Security Best Practices

### ALTIJD

```python
# Credentials uit environment variables
API_KEY = os.environ.get('FRAPPE_API_KEY')
API_SECRET = os.environ.get('FRAPPE_API_SECRET')
```

### NOOIT

```python
# ❌ FOUT - hardcoded credentials
headers = {'Authorization': 'token abc123:xyz789'}
```

### Token Rotatie

```python
# Periodiek nieuwe tokens genereren
# bench execute frappe.core.doctype.user.user.generate_keys --args ['user']
# Oude tokens worden automatisch geïnvalideerd
```

### Minimale Permissions

Maak dedicated API users met alleen de benodigde rollen en permissions.

---

## 7. Troubleshooting

| Error | Oorzaak | Oplossing |
|-------|---------|-----------|
| 403 Forbidden | Ongeldige/verlopen token | Token controleren/regenereren |
| 403 Forbidden | Onvoldoende permissions | User roles controleren |
| 401 Unauthorized | Geen/verkeerde auth header | Header format controleren |
| CSRF token missing | Session auth zonder CSRF | CSRF token toevoegen of Token auth gebruiken |
