# Error Handling Patterns - API

Complete error handling patterns for Frappe/ERPNext API development.

---

## Pattern 1: Complete Whitelisted Method

```python
# myapp/api.py
import frappe
from frappe import _

@frappe.whitelist()
def process_payment(invoice_name, payment_method, amount):
    """
    Process payment with comprehensive validation and error handling.
    
    Args:
        invoice_name: Sales Invoice name
        payment_method: Payment method (Cash, Card, Bank Transfer)
        amount: Payment amount
        
    Returns:
        dict: Payment result with entry name
        
    HTTP Status Codes:
        200: Success
        400/417: Validation error
        403: Permission denied
        404: Invoice not found
        500: Server error
    """
    # =========================================
    # 1. INPUT VALIDATION
    # =========================================
    
    errors = []
    
    if not invoice_name:
        errors.append(_("Invoice name is required"))
    
    if not payment_method:
        errors.append(_("Payment method is required"))
    
    valid_methods = ["Cash", "Card", "Bank Transfer", "Check"]
    if payment_method and payment_method not in valid_methods:
        errors.append(
            _("Invalid payment method. Must be one of: {0}").format(
                ", ".join(valid_methods)
            )
        )
    
    # Validate amount
    try:
        amount = float(amount) if amount else 0
        if amount <= 0:
            errors.append(_("Amount must be greater than zero"))
    except (ValueError, TypeError):
        errors.append(_("Invalid amount format"))
    
    if errors:
        frappe.throw("<br>".join(errors), exc=frappe.ValidationError)
    
    # =========================================
    # 2. EXISTENCE CHECK
    # =========================================
    
    if not frappe.db.exists("Sales Invoice", invoice_name):
        frappe.throw(
            _("Sales Invoice {0} not found").format(invoice_name),
            exc=frappe.DoesNotExistError
        )
    
    # =========================================
    # 3. PERMISSION CHECK
    # =========================================
    
    if not frappe.has_permission("Payment Entry", "create"):
        frappe.throw(
            _("You don't have permission to create payments"),
            exc=frappe.PermissionError
        )
    
    # =========================================
    # 4. BUSINESS LOGIC VALIDATION
    # =========================================
    
    invoice = frappe.get_doc("Sales Invoice", invoice_name)
    
    if invoice.docstatus != 1:
        frappe.throw(
            _("Invoice must be submitted before payment"),
            exc=frappe.ValidationError
        )
    
    outstanding = invoice.outstanding_amount
    if amount > outstanding:
        frappe.throw(
            _("Payment amount ({0}) exceeds outstanding amount ({1})").format(
                frappe.format_value(amount, {"fieldtype": "Currency"}),
                frappe.format_value(outstanding, {"fieldtype": "Currency"})
            ),
            exc=frappe.ValidationError
        )
    
    # =========================================
    # 5. PROCESS REQUEST
    # =========================================
    
    try:
        payment = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",
            "party_type": "Customer",
            "party": invoice.customer,
            "paid_amount": amount,
            "received_amount": amount,
            "mode_of_payment": payment_method,
            "references": [{
                "reference_doctype": "Sales Invoice",
                "reference_name": invoice_name,
                "allocated_amount": amount
            }]
        })
        
        payment.insert()
        payment.submit()
        
        return {
            "status": "success",
            "payment_entry": payment.name,
            "message": _("Payment of {0} recorded successfully").format(
                frappe.format_value(amount, {"fieldtype": "Currency"})
            )
        }
        
    except frappe.DuplicateEntryError:
        frappe.throw(
            _("A payment for this invoice is already being processed"),
            exc=frappe.DuplicateEntryError
        )
        
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            f"Payment Processing Error: {invoice_name}"
        )
        frappe.throw(
            _("Payment processing failed. Please try again or contact support.")
        )
```

---

## Pattern 2: API Response Wrapper

```python
# myapp/api_utils.py
import frappe
from frappe import _
from functools import wraps

def api_response(func):
    """
    Decorator for consistent API response format.
    
    Success: {"status": "success", "data": ...}
    Error: {"status": "error", "message": ..., "type": ...}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return {
                "status": "success",
                "data": result
            }
            
        except frappe.ValidationError as e:
            frappe.local.response["http_status_code"] = 400
            return {
                "status": "error",
                "type": "ValidationError",
                "message": str(e)
            }
            
        except frappe.PermissionError as e:
            frappe.local.response["http_status_code"] = 403
            return {
                "status": "error",
                "type": "PermissionError",
                "message": str(e) or _("Permission denied")
            }
            
        except frappe.DoesNotExistError as e:
            frappe.local.response["http_status_code"] = 404
            return {
                "status": "error",
                "type": "NotFound",
                "message": str(e) or _("Resource not found")
            }
            
        except frappe.DuplicateEntryError as e:
            frappe.local.response["http_status_code"] = 409
            return {
                "status": "error",
                "type": "Conflict",
                "message": str(e) or _("Duplicate entry")
            }
            
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "API Error")
            frappe.local.response["http_status_code"] = 500
            return {
                "status": "error",
                "type": "ServerError",
                "message": _("An unexpected error occurred")
            }
    
    return wrapper


# Usage
@frappe.whitelist()
@api_response
def get_customer_orders(customer):
    """Get customer orders - uses response wrapper."""
    if not customer:
        raise frappe.ValidationError(_("Customer is required"))
    
    if not frappe.db.exists("Customer", customer):
        raise frappe.DoesNotExistError(_("Customer not found"))
    
    return frappe.get_all(
        "Sales Order",
        filters={"customer": customer},
        fields=["name", "transaction_date", "grand_total", "status"]
    )
```

---

## Pattern 3: Client-Side Error Handler Class

```javascript
// myapp/public/js/api_handler.js

class APIHandler {
    /**
     * Centralized API error handling for frappe.call
     */
    
    static async call(options) {
        const defaults = {
            freeze: true,
            freeze_message: __("Processing...")
        };
        
        return new Promise((resolve, reject) => {
            frappe.call({
                ...defaults,
                ...options,
                callback: (r) => {
                    if (r.message && r.message.status === "error") {
                        // Server returned error in response body
                        this.handleError(r.message);
                        reject(r.message);
                    } else {
                        resolve(r.message);
                    }
                },
                error: (r) => {
                    this.handleError(r);
                    reject(r);
                }
            });
        });
    }
    
    static handleError(error) {
        const errorInfo = this.parseError(error);
        
        // Log for debugging
        console.error("API Error:", errorInfo);
        
        // Show user-friendly message
        frappe.msgprint({
            title: errorInfo.title,
            message: errorInfo.message,
            indicator: errorInfo.indicator
        });
        
        // Special handling for certain errors
        if (errorInfo.type === "PermissionError") {
            // Maybe redirect to permission request page
        } else if (errorInfo.type === "SessionExpired") {
            frappe.session_expired();
        }
    }
    
    static parseError(error) {
        let title = __("Error");
        let message = __("An error occurred");
        let indicator = "red";
        let type = "Unknown";
        
        // Check for structured error response
        if (error.type) {
            type = error.type;
            message = error.message || message;
        }
        
        // Check exc_type from frappe.throw
        if (error.exc_type) {
            type = error.exc_type;
        }
        
        // Extract server messages
        if (error._server_messages) {
            try {
                const messages = JSON.parse(error._server_messages);
                if (messages.length > 0) {
                    const msg = JSON.parse(messages[0]);
                    message = msg.message || msg;
                }
            } catch (e) {}
        }
        
        // Set title based on type
        switch (type) {
            case "ValidationError":
                title = __("Validation Error");
                break;
            case "PermissionError":
                title = __("Permission Denied");
                break;
            case "DoesNotExistError":
            case "NotFound":
                title = __("Not Found");
                break;
            case "DuplicateEntryError":
            case "Conflict":
                title = __("Duplicate Entry");
                indicator = "orange";
                break;
            case "RateLimitError":
                title = __("Rate Limit Exceeded");
                message = __("Too many requests. Please wait and try again.");
                indicator = "orange";
                break;
        }
        
        // Network errors
        if (!error.status && !error.type) {
            title = __("Network Error");
            message = __("Unable to connect to server. Check your connection.");
            indicator = "orange";
        }
        
        return { title, message, indicator, type };
    }
}

// Usage example
async function processOrder(orderName) {
    try {
        const result = await APIHandler.call({
            method: "myapp.api.process_order",
            args: { order_name: orderName },
            freeze_message: __("Processing order...")
        });
        
        frappe.show_alert({
            message: __("Order processed successfully"),
            indicator: "green"
        });
        
        return result;
        
    } catch (error) {
        // Error already handled by APIHandler
        // Additional handling if needed
        return null;
    }
}
```

---

## Pattern 4: External API Client with Retry

```python
# myapp/integrations/api_client.py
import frappe
import requests
from frappe import _
import time

class ExternalAPIClient:
    """
    External API client with comprehensive error handling.
    """
    
    def __init__(self, settings_doctype="External API Settings"):
        self.settings = frappe.get_single(settings_doctype)
        self.base_url = self.settings.base_url.rstrip("/")
        self.max_retries = 3
        self.timeout = 30
    
    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.settings.get_password('api_key')}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def request(self, method, endpoint, data=None, params=None):
        """
        Make API request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body for POST/PUT
            params: Query parameters for GET
            
        Returns:
            dict: API response data
            
        Raises:
            frappe.AuthenticationError: Auth failed
            frappe.ValidationError: Client error (4xx)
            Exception: Server error after retries
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                # Log request for debugging
                self._log_request(method, url, response.status_code)
                
                # Success
                if response.status_code in [200, 201]:
                    return response.json()
                
                # Handle specific error codes
                if response.status_code == 401:
                    self._handle_auth_error(response)
                
                elif response.status_code == 403:
                    self._handle_permission_error(response)
                
                elif response.status_code == 404:
                    self._handle_not_found(endpoint, response)
                
                elif response.status_code == 429:
                    # Rate limit - wait and retry
                    wait_time = self._get_retry_wait(response, attempt)
                    frappe.log_error(
                        f"Rate limited on {endpoint}, waiting {wait_time}s",
                        "API Rate Limit"
                    )
                    time.sleep(wait_time)
                    continue
                
                elif 400 <= response.status_code < 500:
                    # Client error - don't retry
                    error_msg = self._parse_error(response)
                    frappe.throw(
                        _("API Error: {0}").format(error_msg),
                        exc=frappe.ValidationError
                    )
                
                elif response.status_code >= 500:
                    # Server error - retry
                    last_error = f"Server error {response.status_code}"
                    wait_time = (2 ** attempt) * 1
                    time.sleep(wait_time)
                    continue
                
            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                time.sleep(2 ** attempt)
                continue
                
            except requests.exceptions.ConnectionError:
                last_error = "Connection failed"
                time.sleep(2 ** attempt)
                continue
                
            except frappe.ValidationError:
                raise  # Don't retry validation errors
                
            except Exception as e:
                last_error = str(e)
                frappe.log_error(frappe.get_traceback(), "API Client Error")
                break
        
        # All retries exhausted
        frappe.log_error(
            f"API request failed after {self.max_retries} attempts: {last_error}",
            "API Client Failure"
        )
        frappe.throw(_("External service unavailable. Please try again later."))
    
    def _handle_auth_error(self, response):
        """Handle authentication errors."""
        frappe.log_error(
            f"Authentication failed: {response.text[:500]}",
            "API Auth Error"
        )
        frappe.throw(
            _("API authentication failed. Please check credentials."),
            exc=frappe.AuthenticationError
        )
    
    def _handle_permission_error(self, response):
        """Handle permission errors."""
        error_msg = self._parse_error(response)
        frappe.throw(
            _("API access denied: {0}").format(error_msg),
            exc=frappe.PermissionError
        )
    
    def _handle_not_found(self, endpoint, response):
        """Handle not found errors."""
        frappe.throw(
            _("Resource not found: {0}").format(endpoint),
            exc=frappe.DoesNotExistError
        )
    
    def _get_retry_wait(self, response, attempt):
        """Get wait time for retry."""
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return min(int(retry_after), 120)
            except ValueError:
                pass
        return (2 ** attempt) * 5
    
    def _parse_error(self, response):
        """Extract error message from response."""
        try:
            data = response.json()
            return (
                data.get("error", {}).get("message") or
                data.get("message") or
                data.get("detail") or
                str(data)
            )
        except Exception:
            return response.text[:200]
    
    def _log_request(self, method, url, status_code):
        """Log API request for debugging."""
        if frappe.conf.get("developer_mode"):
            frappe.logger("api").debug(
                f"{method} {url} -> {status_code}"
            )
    
    # Convenience methods
    def get(self, endpoint, params=None):
        return self.request("GET", endpoint, params=params)
    
    def post(self, endpoint, data):
        return self.request("POST", endpoint, data=data)
    
    def put(self, endpoint, data):
        return self.request("PUT", endpoint, data=data)
    
    def delete(self, endpoint):
        return self.request("DELETE", endpoint)
```

---

## Pattern 5: Webhook Handler with Validation

```python
# myapp/webhooks.py
import frappe
from frappe import _
import hmac
import hashlib
import json

@frappe.whitelist(allow_guest=True)
def stripe_webhook():
    """
    Handle Stripe webhook with full error handling.
    """
    # 1. Get raw payload for signature verification
    payload = frappe.request.data
    signature = frappe.request.headers.get("Stripe-Signature")
    
    # 2. Verify signature
    if not verify_stripe_signature(payload, signature):
        frappe.local.response["http_status_code"] = 401
        return {"error": "Invalid signature"}
    
    # 3. Parse payload
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        frappe.local.response["http_status_code"] = 400
        return {"error": "Invalid JSON"}
    
    # 4. Validate event structure
    event_type = event.get("type")
    event_data = event.get("data", {}).get("object")
    
    if not event_type or not event_data:
        frappe.local.response["http_status_code"] = 400
        return {"error": "Missing event type or data"}
    
    # 5. Check for duplicate (idempotency)
    event_id = event.get("id")
    if is_duplicate_event(event_id):
        return {"status": "already_processed"}
    
    # 6. Process event
    try:
        result = process_stripe_event(event_type, event_data)
        
        # Mark as processed
        mark_event_processed(event_id)
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        # Log error but return 200 to prevent Stripe retries
        # for business logic errors
        frappe.log_error(
            f"Webhook processing error: {str(e)}\n\nEvent: {event_type}\n\n{frappe.get_traceback()}",
            "Stripe Webhook Error"
        )
        
        # Return 500 only for critical errors that should be retried
        if should_retry_error(e):
            frappe.local.response["http_status_code"] = 500
            return {"error": "Processing failed, will retry"}
        
        return {"status": "error", "message": str(e)}


def verify_stripe_signature(payload, signature):
    """Verify Stripe webhook signature."""
    if not signature:
        return False
    
    try:
        secret = frappe.get_single("Payment Settings").get_password("stripe_webhook_secret")
        
        # Parse signature header
        parts = dict(item.split("=") for item in signature.split(","))
        timestamp = parts.get("t")
        expected_sig = parts.get("v1")
        
        if not timestamp or not expected_sig:
            return False
        
        # Create signed payload
        signed_payload = f"{timestamp}.{payload.decode()}"
        
        # Calculate signature
        computed_sig = hmac.new(
            secret.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_sig, expected_sig)
        
    except Exception as e:
        frappe.log_error(f"Signature verification failed: {e}", "Webhook Auth")
        return False


def is_duplicate_event(event_id):
    """Check if event was already processed."""
    return frappe.db.exists("Webhook Event Log", {"event_id": event_id})


def mark_event_processed(event_id):
    """Mark event as processed."""
    frappe.get_doc({
        "doctype": "Webhook Event Log",
        "event_id": event_id,
        "processed_at": frappe.utils.now()
    }).insert(ignore_permissions=True)
    frappe.db.commit()


def process_stripe_event(event_type, event_data):
    """Process different Stripe event types."""
    handlers = {
        "payment_intent.succeeded": handle_payment_success,
        "payment_intent.failed": handle_payment_failed,
        "customer.subscription.created": handle_subscription_created,
        "customer.subscription.deleted": handle_subscription_cancelled
    }
    
    handler = handlers.get(event_type)
    if not handler:
        return {"skipped": True, "reason": "Unhandled event type"}
    
    return handler(event_data)


def should_retry_error(error):
    """Determine if error should trigger webhook retry."""
    # Database errors, connection errors should retry
    retry_errors = (
        frappe.db.DatabaseError,
        ConnectionError,
        TimeoutError
    )
    return isinstance(error, retry_errors)
```

---

## Quick Reference: Error Handling Checklist

### Server-Side (Python)

```python
# 1. Validate inputs
if not param:
    frappe.throw(_("Param required"), exc=frappe.ValidationError)

# 2. Check existence
if not frappe.db.exists("DocType", name):
    frappe.throw(_("Not found"), exc=frappe.DoesNotExistError)

# 3. Check permission
if not frappe.has_permission("DocType", "write"):
    frappe.throw(_("No permission"), exc=frappe.PermissionError)

# 4. Wrap processing in try/except
try:
    result = process()
except Exception as e:
    frappe.log_error(frappe.get_traceback(), "Error Context")
    frappe.throw(_("Operation failed"))
```

### Client-Side (JavaScript)

```javascript
frappe.call({
    method: "...",
    args: {...},
    callback: (r) => { /* success */ },
    error: (r) => {
        // Check error type
        if (r.exc_type === "ValidationError") {...}
        else if (r.exc_type === "PermissionError") {...}
        // Show message
        frappe.msgprint({title: __("Error"), message: ..., indicator: "red"});
    }
});
```
