---
name: erpnext-api-patterns
description: Complete guide for Frappe/ERPNext API integration - REST API, authentication, webhooks and remote method calls
version: 1.0.0
author: OpenAEC Foundation
tags: [erpnext, frappe, api, rest, webhooks, authentication, integration]
frameworks: [frappe-14, frappe-15, frappe-16]
---

# ERPNext API Patterns Skill

> Deterministic patterns for building robust API integrations with Frappe/ERPNext.

---

## Overview

Frappe provides three primary API mechanisms:

| API Type | Endpoint | Usage |
|----------|----------|-------|
| **Resource API** | `/api/resource/:doctype` | CRUD operations on DocTypes |
| **Method API** | `/api/method/:path` | Whitelisted Python methods |
| **Webhooks** | UI Configuration | Event-driven callbacks |

---

## Quick Reference

### Authentication Methods

| Method | Header | Usage |
|--------|--------|-------|
| Token | `Authorization: token <key>:<secret>` | Server-to-server |
| OAuth 2.0 | `Authorization: Bearer <token>` | Third-party apps |
| Session | Cookie-based | Browser clients |

### REST Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List | GET | `/api/resource/:doctype` |
| Create | POST | `/api/resource/:doctype` |
| Read | GET | `/api/resource/:doctype/:name` |
| Update | PUT | `/api/resource/:doctype/:name` |
| Delete | DELETE | `/api/resource/:doctype/:name` |

---

## Essential Patterns

### 1. Token Authentication

```python
# Generate token via CLI
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

### 2. CRUD Operations

**Create:**
```bash
POST /api/resource/Customer
{
    "customer_name": "New Customer",
    "customer_type": "Company"
}
```

**Read with filters:**
```bash
GET /api/resource/Sales Order?fields=["name","status","grand_total"]&filters=[["status","=","Draft"]]
```

**Update:**
```bash
PUT /api/resource/Customer/CUST-00001
{
    "customer_name": "Updated Name"
}
```

### 3. Remote Method Calls

```python
# Server-side: whitelisted method
import frappe

@frappe.whitelist()
def get_customer_balance(customer):
    """Get customer balance via API"""
    return frappe.db.get_value("Customer", customer, "outstanding_amount")

@frappe.whitelist(allow_guest=True)
def public_status():
    """Publicly accessible endpoint"""
    return {"status": "online"}
```

```bash
# Client call
GET /api/method/myapp.api.get_customer_balance?customer=CUST-00001
```

### 4. Webhook Configuration

| Field | Value |
|-------|-------|
| DocType | Sales Order |
| Doc Event | on_submit |
| Request URL | https://external.api/webhook |
| Request Method | POST |
| Condition | `doc.grand_total > 1000` |

---

## Critical Rules

### ALWAYS

1. **Token auth** for server-to-server communication
2. **HTTPS** in production
3. **Specific fields** parameter - never fetch all fields
4. **Pagination** for large datasets
5. **Error handling** with status code checks

### NEVER

1. **Hardcoded credentials** in code
2. **GET requests** for data modifications
3. **Unlimited queries** without limit
4. **Unencrypted secrets** in webhooks

---

## HTTP Response Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process data |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify DocType/document |
| 409 | Conflict | Handle duplicate name |
| 417 | Validation Error | Validate input |
| 500 | Server Error | Check logs |

---

## Standard Client Methods

```python
# frappe.client endpoints for common operations
frappe.client.get_value      # Single field
frappe.client.get_list       # Document list
frappe.client.get            # Full document
frappe.client.insert         # Create
frappe.client.save           # Update
frappe.client.delete         # Delete
frappe.client.submit         # Submit
frappe.client.cancel         # Cancel
```

---

## Decision Tree: Which API to Use?

```
Goal?
├── CRUD on documents → Resource API (/api/resource/)
├── Custom business logic → Method API (/api/method/)
├── Real-time events → Webhooks
└── Authentication
    ├── Server-to-server → Token
    ├── Third-party app → OAuth 2.0
    └── Browser → Session/Cookie
```

---

## Reference Documents

| Document | Content |
|----------|---------|
| `authentication-reference.md` | All auth methods with examples |
| `resource-api-reference.md` | Complete REST API documentation |
| `method-api-reference.md` | Whitelisted methods and RPC |
| `webhooks-reference.md` | Webhook configuration and security |
| `examples.md` | Complete integration examples |
| `anti-patterns.md` | Common mistakes to avoid |

---

## Version Information

| Feature | v14 | v15 | v16 |
|---------|:---:|:---:|:---:|
| Token auth | ✅ | ✅ | ✅ |
| OAuth 2.0 | ✅ | ✅ | ✅ |
| `expand` param | ❌ | ✅ | ✅ |
| Rate limiting decorator | Basic | Enhanced | Enhanced |

---

*See reference documents for complete implementation details.*
