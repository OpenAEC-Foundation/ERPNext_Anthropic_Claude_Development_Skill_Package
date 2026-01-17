# Authentication Methods Reference

## 1. Token Based Authentication (AANBEVOLEN)

Meest gebruikte methode voor server-to-server integraties.

### Token Genereren

1. User list → Open user → Settings tab
2. Expand "API Access" sectie
3. Klik "Generate Keys"
4. Kopieer API Secret (wordt maar 1x getoond!)

### Token Gebruiken

```python
import requests

headers = {
    'Authorization': 'token api_key:api_secret',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://erp.example.com/api/resource/Customer',
    headers=headers
)
```

```bash
# cURL
curl -X GET "https://erp.example.com/api/resource/Customer" \
  -H "Authorization: token api_key:api_secret" \
  -H "Accept: application/json"
```

### Basic Auth Alternatief

```python
import base64

credentials = base64.b64encode(b'api_key:api_secret').decode('utf-8')
headers = {'Authorization': f'Basic {credentials}'}
```

---

## 2. Password Based Authentication (Session)

Voor browser-based applicaties met cookies.

```python
import requests

session = requests.Session()

# Login - krijgt session cookie
login_response = session.post(
    'https://erp.example.com/api/method/login',
    json={
        'usr': 'username_or_email',
        'pwd': 'password'
    }
)

# Volgende requests gebruiken session cookie automatisch
users = session.get('https://erp.example.com/api/resource/User')
```

**Success Response:**
```json
{
    "message": "Logged In",
    "home_page": "/app",
    "full_name": "Administrator"
}
```

**⚠️ WAARSCHUWING**: Session cookies verlopen na 3 dagen. Gebruik Token auth voor long-running integrations.

---

## 3. OAuth 2.0 (Third-Party Apps)

### Stap 1: OAuth Client Registreren

OAuth Client List → New → Vul in:
- App Name
- Redirect URIs
- Default Redirect URI
- Sla op → Krijg Client ID en Client Secret

### Stap 2: Authorization Code Verkrijgen

```
GET /api/method/frappe.integrations.oauth2.authorize
    ?client_id={client_id}
    &response_type=code
    &scope=openid all
    &redirect_uri={redirect_uri}
    &state={random_state}
```

User wordt doorverwezen naar login, dan terug naar redirect_uri met `?code=...`

### Stap 3: Access Token Verkrijgen

```bash
POST /api/method/frappe.integrations.oauth2.get_token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code={authorization_code}
&redirect_uri={redirect_uri}
&client_id={client_id}
```

**Response:**
```json
{
    "access_token": "...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "...",
    "scope": "openid all"
}
```

### Stap 4: API Calls met Bearer Token

```python
headers = {'Authorization': 'Bearer {access_token}'}
response = requests.get(
    'https://erp.example.com/api/resource/User',
    headers=headers
)
```

### Token Refresh

```bash
POST /api/method/frappe.integrations.oauth2.get_token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token={refresh_token}
&client_id={client_id}
```

---

## Authenticatie Keuze Matrix

| Use Case | Aanbevolen Method |
|----------|-------------------|
| Server-to-server integratie | Token Auth |
| Mobile app | OAuth 2.0 |
| Single Page Application | OAuth 2.0 + PKCE |
| Quick scripting/testing | Token Auth |
| Browser session (kort) | Password/Session |

---

## Security Best Practices

```
✅ Genereer aparte API keys per integratie
✅ Roteer API secrets regelmatig
✅ Beperk user permissions tot benodigde DocTypes
✅ Gebruik HTTPS altijd

❌ NOOIT credentials hardcoden
❌ NOOIT API secrets in version control
❌ NOOIT admin credentials gebruiken voor API
❌ NOOIT credentials in URL query parameters
```

## Credential Storage Pattern

```python
# CORRECT: gebruik site_config.json of environment variables
api_key = frappe.conf.get("external_api_key")
api_secret = frappe.conf.get("external_api_secret")

# In site_config.json:
# {
#     "external_api_key": "abc123",
#     "external_api_secret": "secret456"
# }
```
