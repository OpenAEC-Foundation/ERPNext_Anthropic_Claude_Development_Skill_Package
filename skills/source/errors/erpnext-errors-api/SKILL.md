---
name: erpnext-errors-api
version: 1.0.0
description: Error handling patterns for Frappe/ERPNext API development. Covers whitelisted method errors, REST API responses, frappe.call client handling, authentication failures, rate limiting, and webhook error handling. Includes proper HTTP status codes, error response formats, and retry patterns. V14/V15/V16 compatible. Triggers: API error, whitelisted method error, frappe.call error, REST API error, 401 unauthorized, 403 forbidden, 404 not found, 417 exception, rate limit, webhook error, API timeout, authentication error.
author: OpenAEC Foundation
tags: [erpnext, frappe, api, error-handling, rest, webhooks, authentication]
languages: [en]
frappe_versions: [v14, v15, v16]
---

# ERPNext API - Error Handling

This skill covers error handling patterns for Frappe/ERPNext API development. For API syntax, see `erpnext-api-patterns`.

**Version**: v14/v15/v16 compatible

---

## API Error Handling Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│ API ERRORS NEED CLIENT-FRIENDLY RESPONSES                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Server-Side (Whitelisted Methods):                                  │
│ ✅ Use frappe.throw() with proper exception types                   │
│ ✅ Return proper HTTP status codes (400, 403, 404, etc.)            │
│ ✅ Validate inputs before processing                                │
│ ✅ Log errors with context for debugging                            │
│                                                                     │
│ Client-Side (frappe.call):                                          │
│ ✅ Always provide error callback                                    │
│ ✅ Check r.exc_type for specific error handling                     │
│ ✅ Show user-friendly messages                                      │
│ ✅ Handle network errors separately                                 │
│                                                                     │
│ External Integrations:                                              │
│ ✅ Handle authentication failures gracefully                        │
│ ✅ Implement retry logic with exponential backoff                   │
│ ✅ Log API responses for debugging                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## HTTP Status Codes Reference

| Code | Meaning | When to Use |
|------|---------|-------------|
| `200` | Success | Request completed successfully |
| `400` | Bad Request | Validation error, invalid input |
| `401` | Unauthorized | Missing or invalid authentication |
| `403` | Forbidden | Valid auth but no permission |
| `404` | Not Found | Document/resource doesn't exist |
| `409` | Conflict | Duplicate, version conflict |
| `417` | Expectation Failed | Server exception (frappe.throw) |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Server Error | Unexpected server error |

---

## Server-Side Error Handling

### Pattern 1: Whitelisted Method with Validation

```python
import frappe
from frappe import _

@frappe.whitelist()
def create_order(customer, items):
    """
    Create order with comprehensive error handling.
    
    Returns:
        dict: {"name": order_name, "status": "success"}
        
    Raises:
        frappe.ValidationError: Invalid input (HTTP 417)
        frappe.PermissionError: No permission (HTTP 403)
        frappe.DoesNotExistError: Customer not found (HTTP 404)
    """
    # 1. Validate required inputs
    if not customer:
        frappe.throw(
            _("Customer is required"),
            exc=frappe.ValidationError
        )
    
    if not items:
        frappe.throw(
            _("At least one item is required"),
            exc=frappe.ValidationError
        )
    
    # 2. Parse JSON if string
    if isinstance(items, str):
        try:
            items = frappe.parse_json(items)
        except Exception:
            frappe.throw(
                _("Invalid items format - expected JSON array"),
                exc=frappe.ValidationError
            )
    
    # 3. Check customer exists
    if not frappe.db.exists("Customer", customer):
        frappe.throw(
            _("Customer {0} not found").format(customer),
            exc=frappe.DoesNotExistError
        )
    
    # 4. Check permission
    if not frappe.has_permission("Sales Order", "create"):
        frappe.throw(
            _("You don't have permission to create orders"),
            exc=frappe.PermissionError
        )
    
    # 5. Process request
    try:
        order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer,
            "items": items
        })
        order.insert()
        
        return {
            "name": order.name,
            "status": "success",
            "message": _("Order created successfully")
        }
        
    except frappe.DuplicateEntryError:
        frappe.throw(
            _("Duplicate order detected"),
            exc=frappe.DuplicateEntryError
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Order Creation Error")
        frappe.throw(
            _("Failed to create order: {0}").format(str(e))
        )
```

### Pattern 2: Bulk Operation with Partial Failure

```python
@frappe.whitelist()
def bulk_update_status(doc_names, new_status):
    """
    Bulk update with per-item error handling.
    Returns results even if some items fail.
    """
    if not doc_names:
        frappe.throw(_("No documents specified"))
    
    if isinstance(doc_names, str):
        doc_names = frappe.parse_json(doc_names)
    
    results = {
        "success": [],
        "failed": [],
        "permission_denied": []
    }
    
    for name in doc_names:
        try:
            # Check existence
            if not frappe.db.exists("Sales Order", name):
                results["failed"].append({
                    "name": name,
                    "error": _("Not found")
                })
                continue
            
            # Check permission
            if not frappe.has_permission("Sales Order", "write", name):
                results["permission_denied"].append(name)
                continue
            
            # Update
            frappe.db.set_value("Sales Order", name, "status", new_status)
            results["success"].append(name)
            
        except Exception as e:
            results["failed"].append({
                "name": name,
                "error": str(e)
            })
    
    frappe.db.commit()
    
    # Return partial success - don't throw if some succeeded
    return results
```

---

## Client-Side Error Handling

### JavaScript: frappe.call Error Handling

```javascript
// Pattern 1: Complete error handling
frappe.call({
    method: "myapp.api.create_order",
    args: {
        customer: frm.doc.customer,
        items: frm.doc.items
    },
    freeze: true,
    freeze_message: __("Creating order..."),
    callback: function(r) {
        if (r.message && r.message.status === "success") {
            frappe.show_alert({
                message: __("Order {0} created", [r.message.name]),
                indicator: "green"
            });
            frm.reload_doc();
        }
    },
    error: function(r) {
        // Handle specific error types
        handle_api_error(r);
    }
});

function handle_api_error(r) {
    let title = __("Error");
    let message = __("An error occurred");
    let indicator = "red";
    
    // Check error type
    if (r.exc_type === "ValidationError") {
        title = __("Validation Error");
        message = get_error_message(r);
    }
    else if (r.exc_type === "PermissionError") {
        title = __("Permission Denied");
        message = __("You don't have permission to perform this action");
    }
    else if (r.exc_type === "DoesNotExistError") {
        title = __("Not Found");
        message = get_error_message(r);
    }
    else if (r.exc_type === "DuplicateEntryError") {
        title = __("Duplicate Entry");
        message = __("A record with this name already exists");
    }
    else if (r.status === 429) {
        title = __("Rate Limit");
        message = __("Too many requests. Please wait and try again.");
        indicator = "orange";
    }
    else if (!r.status) {
        title = __("Network Error");
        message = __("Unable to connect to server. Check your internet connection.");
    }
    else {
        message = get_error_message(r) || __("An unexpected error occurred");
    }
    
    frappe.msgprint({
        title: title,
        message: message,
        indicator: indicator
    });
}

function get_error_message(r) {
    // Extract message from server response
    if (r._server_messages) {
        try {
            let messages = JSON.parse(r._server_messages);
            if (messages.length > 0) {
                let msg = JSON.parse(messages[0]);
                return msg.message || msg;
            }
        } catch (e) {}
    }
    return r.exc || r.message || null;
}
```

### JavaScript: frappe.xcall with async/await

```javascript
// Pattern 2: Modern async/await with try/catch
async function createOrderAsync() {
    try {
        frappe.freeze(__("Creating order..."));
        
        const result = await frappe.xcall("myapp.api.create_order", {
            customer: cur_frm.doc.customer,
            items: cur_frm.doc.items
        });
        
        frappe.unfreeze();
        
        if (result.status === "success") {
            frappe.show_alert({
                message: __("Order created: {0}", [result.name]),
                indicator: "green"
            });
        }
        
        return result;
        
    } catch (error) {
        frappe.unfreeze();
        
        // error is the response object
        handle_api_error(error);
        throw error;  // Re-throw if caller needs to handle
    }
}
```

---

## External API Integration Errors

### Pattern: External API with Retry

```python
import frappe
import requests
from frappe import _

def call_external_api(endpoint, data, max_retries=3):
    """
    Call external API with retry logic and error handling.
    """
    settings = frappe.get_single("External API Settings")
    
    headers = {
        "Authorization": f"Bearer {settings.get_password('api_key')}",
        "Content-Type": "application/json"
    }
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{settings.base_url}{endpoint}",
                json=data,
                headers=headers,
                timeout=30
            )
            
            # Success
            if response.status_code == 200:
                return response.json()
            
            # Client errors - don't retry
            if 400 <= response.status_code < 500:
                error_detail = parse_api_error(response)
                
                if response.status_code == 401:
                    frappe.throw(
                        _("Authentication failed. Check API credentials."),
                        exc=frappe.AuthenticationError
                    )
                elif response.status_code == 403:
                    frappe.throw(
                        _("Access denied: {0}").format(error_detail),
                        exc=frappe.PermissionError
                    )
                elif response.status_code == 404:
                    frappe.throw(
                        _("Resource not found: {0}").format(endpoint),
                        exc=frappe.DoesNotExistError
                    )
                elif response.status_code == 429:
                    # Rate limit - wait and retry
                    retry_after = int(response.headers.get("Retry-After", 60))
                    frappe.log_error(
                        f"Rate limited, retry after {retry_after}s",
                        "External API Rate Limit"
                    )
                    import time
                    time.sleep(min(retry_after, 120))
                    continue
                else:
                    frappe.throw(
                        _("API error ({0}): {1}").format(
                            response.status_code, error_detail
                        )
                    )
            
            # Server errors - retry
            if response.status_code >= 500:
                last_error = f"Server error: {response.status_code}"
                wait_time = (2 ** attempt) * 1  # Exponential backoff
                import time
                time.sleep(wait_time)
                continue
                
        except requests.exceptions.Timeout:
            last_error = "Request timed out"
            continue
            
        except requests.exceptions.ConnectionError:
            last_error = "Connection failed"
            continue
            
        except Exception as e:
            last_error = str(e)
            frappe.log_error(frappe.get_traceback(), "External API Error")
            break
    
    # All retries failed
    frappe.log_error(
        f"External API failed after {max_retries} attempts: {last_error}",
        "External API Failure"
    )
    frappe.throw(
        _("External service unavailable. Please try again later.")
    )


def parse_api_error(response):
    """Parse error message from API response."""
    try:
        data = response.json()
        return data.get("error", {}).get("message") or data.get("message") or str(data)
    except Exception:
        return response.text[:200]
```

---

## Webhook Error Handling

### Pattern: Webhook with Error Response

```python
@frappe.whitelist(allow_guest=True)
def webhook_handler():
    """
    Handle incoming webhook with proper error responses.
    """
    try:
        # Verify webhook signature
        signature = frappe.request.headers.get("X-Webhook-Signature")
        if not verify_signature(signature, frappe.request.data):
            frappe.local.response["http_status_code"] = 401
            return {"error": "Invalid signature"}
        
        # Parse payload
        try:
            payload = frappe.parse_json(frappe.request.data)
        except Exception:
            frappe.local.response["http_status_code"] = 400
            return {"error": "Invalid JSON payload"}
        
        # Validate required fields
        if not payload.get("event"):
            frappe.local.response["http_status_code"] = 400
            return {"error": "Missing 'event' field"}
        
        # Process webhook
        result = process_webhook_event(payload)
        
        return {
            "status": "success",
            "processed": result
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Webhook Error")
        frappe.local.response["http_status_code"] = 500
        return {"error": "Internal server error"}


def verify_signature(signature, payload):
    """Verify webhook signature."""
    if not signature:
        return False
    
    import hmac
    import hashlib
    
    secret = frappe.get_single("Webhook Settings").get_password("secret")
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)
```

---

## Critical Rules

### ✅ ALWAYS

1. **Validate inputs first** - Before any processing
2. **Use proper exception types** - ValidationError, PermissionError, etc.
3. **Provide error callbacks** - In frappe.call on client
4. **Log errors with context** - Document name, user, operation
5. **Return structured errors** - Include error type and message
6. **Implement retry for external APIs** - With exponential backoff

### ❌ NEVER

1. **Don't expose internal errors** - Sanitize messages for users
2. **Don't ignore network errors** - Handle timeouts and connection failures
3. **Don't retry 4xx errors** - They won't succeed (except 429)
4. **Don't hardcode credentials** - Use frappe.conf or settings
5. **Don't skip permission checks** - Even in whitelisted methods

---

## Quick Reference: Error Responses

| Error Type | HTTP Code | Client Handling |
|------------|:---------:|-----------------|
| ValidationError | 417 | Show validation message |
| PermissionError | 403 | Show permission denied |
| DoesNotExistError | 404 | Show not found |
| DuplicateEntryError | 409 | Show duplicate message |
| AuthenticationError | 401 | Redirect to login |
| Rate Limited | 429 | Wait and retry |
| Network Error | - | Check connection |

---

## Reference Files

| File | Contents |
|------|----------|
| `references/patterns.md` | Complete error handling patterns |
| `references/examples.md` | Full working examples |
| `references/anti-patterns.md` | Common mistakes to avoid |

---

## See Also

- `erpnext-api-patterns` - API syntax and patterns
- `erpnext-errors-permissions` - Permission error handling
- `erpnext-syntax-whitelisted` - Whitelisted methods syntax
