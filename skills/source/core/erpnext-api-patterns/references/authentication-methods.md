# Authentication Methods Reference

## 1. Token Based Authentication (RECOMMENDED)

Most commonly used method for server-to-server integrations.

### Generate Token

1. User list → Open user → Settings tab
2. Expand "API Access" section
3. Click "Generate Keys"
4. Copy API Secret (shown only once!)

### Using Token

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

### Basic Auth Alternative

```python
import base64

credentials = base64.b64encode(b'api_key:api_secret').decode('utf-8')
headers = {'Authorization': f'Basic {credentials}'}
```

---

## 2. Password Based Authentication (Session)

For browser-based applications using cookies.

```python
import requests

session = requests.Session()

# Login - receives session cookie
login_response = session.post(
    'https://erp.example.com/api/method/login',
    json={
        'usr': 'username_or_email',
        'pwd': 'password'
    }
)

# Subsequent requests use session cookie automatically
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

**⚠️ WARNING**: Session cookies expire after 3 days. Use Token auth for long-running integrations.

---

## 3. OAuth 2.0 (Third-Party Apps)

### Step 1: Register OAuth Client

OAuth Client List → New → Fill in:
- App Name
- Redirect URIs
- Default Redirect URI
- Save → Get Client ID and Client Secret

### Step 2: Get Authorization Code

```
GET /api/method/frappe.integrations.oauth2.authorize
    ?client_id={client_id}
    &response_type=code
    &scope=openid all
    &redirect_uri={redirect_uri}
    &state={random_state}
```

User is redirected to login, then back to redirect_uri with `?code=...`

### Step 3: Get Access Token

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

### Step 4: API Calls with Bearer Token

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

## Authentication Choice Matrix

| Use Case | Recommended Method |
|----------|-------------------|
| Server-to-server integration | Token Auth |
| Mobile app | OAuth 2.0 |
| Single Page Application | OAuth 2.0 + PKCE |
| Quick scripting/testing | Token Auth |
| Browser session (short) | Password/Session |

---

## Security Best Practices

```
✅ Generate separate API keys per integration
✅ Rotate API secrets regularly
✅ Limit user permissions to required DocTypes
✅ Always use HTTPS

❌ NEVER hardcode credentials
❌ NEVER put API secrets in version control
❌ NEVER use admin credentials for API
❌ NEVER put credentials in URL query parameters
```

## Credential Storage Pattern

```python
# CORRECT: use site_config.json or environment variables
api_key = frappe.conf.get("external_api_key")
api_secret = frappe.conf.get("external_api_secret")

# In site_config.json:
# {
#     "external_api_key": "abc123",
#     "external_api_secret": "secret456"
# }
```
