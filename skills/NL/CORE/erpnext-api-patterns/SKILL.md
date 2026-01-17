---
name: erpnext-api-patterns
description: Complete gids voor ERPNext/Frappe API integraties inclusief REST API, RPC API, authenticatie, webhooks en rate limiting. Gebruik wanneer code nodig is voor externe API calls naar ERPNext, API endpoints ontwerpen, webhooks configureren, authenticatie implementeren (token/OAuth2/session), of bij vragen over frappe.call, frappe.xcall en REST endpoints. Triggers: "API integratie", "REST endpoint", "webhook", "token authenticatie", "OAuth", "frappe.call", "externe koppeling", "API response", "rate limiting".
---

# ERPNext API Patterns

## API Type Decision Tree

```
Wat wil je bereiken?
│
├─► CRUD operaties op documenten
│   └─► REST API: /api/resource/{doctype}
│
├─► Custom business logic aanroepen
│   └─► RPC API: /api/method/{path}
│
├─► Externe systemen notificeren bij events
│   └─► Webhooks configureren
│
└─► Client-side server calls (JavaScript)
    └─► frappe.call() of frappe.xcall()
```

## Quick Reference

### Authenticatie Headers

```python
# Token Auth (AANBEVOLEN voor integraties)
headers = {
    'Authorization': 'token api_key:api_secret',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Bearer Token (OAuth2)
headers = {'Authorization': 'Bearer {access_token}'}
```

### REST API CRUD

| Operatie | Method | Endpoint |
|----------|--------|----------|
| List | `GET` | `/api/resource/{doctype}` |
| Create | `POST` | `/api/resource/{doctype}` |
| Read | `GET` | `/api/resource/{doctype}/{name}` |
| Update | `PUT` | `/api/resource/{doctype}/{name}` |
| Delete | `DELETE` | `/api/resource/{doctype}/{name}` |

### Filter Operators

```python
# Basis filters
filters = [["status", "=", "Open"]]
filters = [["amount", ">", 1000]]
filters = [["status", "in", ["Open", "Pending"]]]
filters = [["date", "between", ["2024-01-01", "2024-12-31"]]]
filters = [["reference", "is", "set"]]  # NOT NULL
```

### RPC Method Call

```python
# Server-side: markeer met decorator
@frappe.whitelist()
def my_function(param1, param2):
    return {"result": "value"}

# API call
POST /api/method/my_app.api.my_function
{"param1": "value1", "param2": "value2"}
```

### Client-Side Calls (JavaScript)

```javascript
// Async/await pattern (AANBEVOLEN)
const result = await frappe.xcall('my_app.api.my_function', {
    param1: 'value'
});

// Promise pattern
frappe.call({
    method: 'my_app.api.my_function',
    args: {param1: 'value'},
    freeze: true,
    freeze_message: __('Processing...')
}).then(r => console.log(r.message));
```

## Response Structuur

**REST API Success:**
```json
{"data": {...}}
```

**RPC API Success:**
```json
{"message": "return_value"}
```

**Error Response:**
```json
{
    "exc_type": "ValidationError",
    "_server_messages": "[{\"message\": \"Error details\"}]"
}
```

## HTTP Status Codes

| Code | Betekenis |
|------|-----------|
| `200` | Success |
| `400` | Validatie fout |
| `401` | Geen authenticatie |
| `403` | Geen permissies |
| `404` | Document niet gevonden |
| `417` | Server exception |
| `429` | Rate limit overschreden |

## Kritieke Regels

1. **ALTIJD** `Accept: application/json` header meesturen
2. **ALTIJD** permission checks in whitelisted methods
3. **NOOIT** credentials hardcoden - gebruik `frappe.conf`
4. **NOOIT** SQL injection vulnerable queries schrijven
5. **GET** voor read-only, **POST** voor state-changing operaties

## Reference Files

| File | Inhoud |
|------|--------|
| [authentication-methods.md](references/authentication-methods.md) | Token, Session, OAuth2 implementatie |
| [rest-api-reference.md](references/rest-api-reference.md) | Complete REST API met filters en paginering |
| [rpc-api-reference.md](references/rpc-api-reference.md) | Whitelisted methods en frappe.call patterns |
| [webhooks-reference.md](references/webhooks-reference.md) | Webhook configuratie en security |
| [anti-patterns.md](references/anti-patterns.md) | Veelvoorkomende fouten en fixes |

## Versie Notities (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| `expand_links` parameter | ❌ | ✅ |
| Server Script rate limiting | ❌ | ✅ |
| PKCE voor OAuth2 | Beperkt | ✅ |
