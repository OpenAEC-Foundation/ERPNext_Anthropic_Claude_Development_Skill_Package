---
name: erpnext-api-patterns
description: Complete handleiding voor Frappe/ERPNext API integratie - REST API, authenticatie, webhooks en remote method calls
version: 1.0.0
author: OpenAEC Foundation
tags: [erpnext, frappe, api, rest, webhooks, authentication, integration]
frameworks: [frappe-14, frappe-15, frappe-16]
---

# ERPNext API Patterns Skill

> Deterministische patronen voor het bouwen van robuuste API integraties met Frappe/ERPNext.

---

## Overzicht

Frappe biedt drie primaire API-mechanismen:

| API Type | Endpoint | Gebruik |
|----------|----------|---------|
| **Resource API** | `/api/resource/:doctype` | CRUD operaties op DocTypes |
| **Method API** | `/api/method/:path` | Whitelisted Python methods |
| **Webhooks** | Configuratie in UI | Event-driven callbacks |

---

## Snelle Referentie

### Authenticatie Methoden

| Methode | Header | Gebruik |
|---------|--------|---------|
| Token | `Authorization: token <key>:<secret>` | Server-to-server |
| OAuth 2.0 | `Authorization: Bearer <token>` | Third-party apps |
| Session | Cookie-based | Browser clients |

### REST Endpoints

| Operatie | Method | Endpoint |
|----------|--------|----------|
| List | GET | `/api/resource/:doctype` |
| Create | POST | `/api/resource/:doctype` |
| Read | GET | `/api/resource/:doctype/:name` |
| Update | PUT | `/api/resource/:doctype/:name` |
| Delete | DELETE | `/api/resource/:doctype/:name` |

---

## Essentiële Patronen

### 1. Token Authenticatie

```python
# Token genereren via CLI
# bench execute frappe.core.doctype.user.user.generate_keys --args ['api_user']
```

```javascript
// JavaScript client
const response = await fetch('https://site.local/api/resource/Customer', {
    headers: {
        'Authorization': 'token api_key:api_secret',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
});
```

```bash
# cURL
curl -H "Authorization: token api_key:api_secret" \
     -H "Accept: application/json" \
     https://site.local/api/resource/Customer
```

### 2. CRUD Operaties

**Create:**
```bash
POST /api/resource/Customer
{
    "customer_name": "Nieuwe Klant",
    "customer_type": "Company"
}
```

**Read met filters:**
```bash
GET /api/resource/Sales Order?fields=["name","status","grand_total"]&filters=[["status","=","Draft"]]
```

**Update:**
```bash
PUT /api/resource/Customer/CUST-00001
{
    "customer_name": "Bijgewerkte Naam"
}
```

### 3. Remote Method Calls

```python
# Server-side: whitelisted method
import frappe

@frappe.whitelist()
def get_customer_balance(customer):
    """Haal klant saldo op via API"""
    return frappe.db.get_value("Customer", customer, "outstanding_amount")

@frappe.whitelist(allow_guest=True)
def public_status():
    """Publiek toegankelijk endpoint"""
    return {"status": "online"}
```

```bash
# Client call
GET /api/method/myapp.api.get_customer_balance?customer=CUST-00001
```

### 4. Webhook Configuratie

| Veld | Waarde |
|------|--------|
| DocType | Sales Order |
| Doc Event | on_submit |
| Request URL | https://external.api/webhook |
| Request Method | POST |
| Condition | `doc.grand_total > 1000` |

---

## Kritieke Regels

### ALTIJD

1. **Token auth** voor server-to-server communicatie
2. **HTTPS** in productie
3. **Specifieke fields** parameter - nooit alle velden ophalen
4. **Paginatie** voor grote datasets
5. **Error handling** met status code controle

### NOOIT

1. **Hardcoded credentials** in code
2. **GET requests** voor data wijzigingen
3. **Onbeperkte queries** zonder limit
4. **Onversleutelde secrets** in webhooks

---

## HTTP Response Codes

| Code | Betekenis | Actie |
|------|-----------|-------|
| 200 | Success | Data verwerken |
| 403 | Forbidden | Permissions controleren |
| 404 | Not Found | DocType/document controleren |
| 409 | Conflict | Duplicate name handling |
| 417 | Validation Error | Input valideren |
| 500 | Server Error | Logs controleren |

---

## Standaard Client Methods

```python
# frappe.client endpoints voor veelvoorkomende operaties
frappe.client.get_value      # Single field
frappe.client.get_list       # Document lijst
frappe.client.get            # Full document
frappe.client.insert         # Create
frappe.client.save           # Update
frappe.client.delete         # Delete
frappe.client.submit         # Submit
frappe.client.cancel         # Cancel
```

---

## Beslisboom: Welke API Gebruiken?

```
Doel?
├── CRUD op documents → Resource API (/api/resource/)
├── Custom business logic → Method API (/api/method/)
├── Real-time events → Webhooks
└── Authenticatie
    ├── Server-to-server → Token
    ├── Third-party app → OAuth 2.0
    └── Browser → Session/Cookie
```

---

## Reference Documenten

| Document | Inhoud |
|----------|--------|
| `authentication-reference.md` | Alle auth methoden met voorbeelden |
| `resource-api-reference.md` | Complete REST API documentatie |
| `method-api-reference.md` | Whitelisted methods en RPC |
| `webhooks-reference.md` | Webhook configuratie en security |
| `examples.md` | Complete integratie voorbeelden |
| `anti-patterns.md` | Veelvoorkomende fouten |

---

## Versie Informatie

| Feature | v14 | v15 | v16 |
|---------|:---:|:---:|:---:|
| Token auth | ✅ | ✅ | ✅ |
| OAuth 2.0 | ✅ | ✅ | ✅ |
| `expand` param | ❌ | ✅ | ✅ |
| Rate limiting decorator | Basic | Enhanced | Enhanced |

---

*Zie reference documenten voor volledige implementatiedetails.*
