# Anti-Patterns - API Error Handling

Common mistakes to avoid when handling API errors in Frappe/ERPNext.

---

## 1. No Input Validation

### ❌ WRONG

```python
@frappe.whitelist()
def process_order(customer, amount):
    # Directly use inputs without validation!
    order = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": customer,
        "items": [{"item_code": "ITEM", "qty": 1, "rate": amount}]
    })
    order.insert()
```

### ✅ CORRECT

```python
@frappe.whitelist()
def process_order(customer, amount):
    # Validate all inputs first
    if not customer:
        frappe.throw(_("Customer is required"), exc=frappe.ValidationError)
    
    if not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer not found"), exc=frappe.DoesNotExistError)
    
    try:
        amount = float(amount)
        if amount <= 0:
            frappe.throw(_("Amount must be positive"), exc=frappe.ValidationError)
    except (ValueError, TypeError):
        frappe.throw(_("Invalid amount"), exc=frappe.ValidationError)
    
    # Now safe to proceed
    order = frappe.get_doc({...})
    order.insert()
```

**Why**: Unvalidated inputs cause cryptic errors and potential security issues.

---

## 2. Missing Error Callback in frappe.call

### ❌ WRONG

```javascript
frappe.call({
    method: "myapp.api.process",
    args: { data: data },
    callback: function(r) {
        frappe.show_alert("Done!");
    }
    // No error handler!
});
```

### ✅ CORRECT

```javascript
frappe.call({
    method: "myapp.api.process",
    args: { data: data },
    callback: function(r) {
        if (r.message) {
            frappe.show_alert({message: "Done!", indicator: "green"});
        }
    },
    error: function(r) {
        frappe.msgprint({
            title: __("Error"),
            message: get_error_message(r),
            indicator: "red"
        });
    }
});
```

**Why**: Without error callback, users see no feedback when API fails.

---

## 3. Exposing Internal Errors to Users

### ❌ WRONG

```python
@frappe.whitelist()
def calculate_price(item_code):
    try:
        return get_price(item_code)
    except Exception as e:
        # Exposes internal error details!
        frappe.throw(str(e))
```

### ✅ CORRECT

```python
@frappe.whitelist()
def calculate_price(item_code):
    try:
        return get_price(item_code)
    except Exception as e:
        # Log for debugging
        frappe.log_error(frappe.get_traceback(), "Price Calculation Error")
        # User-friendly message
        frappe.throw(_("Unable to calculate price. Please try again."))
```

**Why**: Internal errors may expose sensitive information and confuse users.

---

## 4. No Permission Check in API

### ❌ WRONG

```python
@frappe.whitelist()
def delete_record(doctype, name):
    # Anyone can call this and delete any record!
    frappe.delete_doc(doctype, name)
```

### ✅ CORRECT

```python
@frappe.whitelist()
def delete_record(doctype, name):
    # Validate inputs
    if not doctype or not name:
        frappe.throw(_("DocType and name required"), exc=frappe.ValidationError)
    
    # Check permission
    if not frappe.has_permission(doctype, "delete", name):
        frappe.throw(
            _("You don't have permission to delete this record"),
            exc=frappe.PermissionError
        )
    
    frappe.delete_doc(doctype, name)
```

**Why**: Whitelisted methods are callable by any logged-in user.

---

## 5. Retrying 4xx Errors

### ❌ WRONG

```python
def call_api(url, data):
    for attempt in range(3):
        response = requests.post(url, json=data)
        if response.status_code != 200:
            time.sleep(2 ** attempt)
            continue  # Retries ALL errors including 400, 401, 403
        return response.json()
```

### ✅ CORRECT

```python
def call_api(url, data):
    for attempt in range(3):
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        
        # Don't retry client errors (except rate limit)
        if 400 <= response.status_code < 500:
            if response.status_code == 429:  # Rate limit
                time.sleep(int(response.headers.get("Retry-After", 60)))
                continue
            frappe.throw(f"API error: {response.status_code}")
        
        # Retry server errors
        if response.status_code >= 500:
            time.sleep(2 ** attempt)
            continue
```

**Why**: 4xx errors indicate client problems - retrying won't help.

---

## 6. Swallowing Errors Silently

### ❌ WRONG

```python
@frappe.whitelist()
def sync_data():
    try:
        perform_sync()
    except Exception:
        pass  # Silent failure - no logging, no user feedback!
```

### ✅ CORRECT

```python
@frappe.whitelist()
def sync_data():
    try:
        perform_sync()
        return {"status": "success"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Sync Error")
        frappe.throw(_("Sync failed: {0}").format(str(e)))
```

**Why**: Silent failures make debugging impossible.

---

## 7. Hardcoded API Credentials

### ❌ WRONG

```python
def get_data():
    headers = {
        "Authorization": "Bearer sk_live_abc123xyz"  # Hardcoded!
    }
    return requests.get(url, headers=headers)
```

### ✅ CORRECT

```python
def get_data():
    settings = frappe.get_single("API Settings")
    headers = {
        "Authorization": f"Bearer {settings.get_password('api_key')}"
    }
    return requests.get(url, headers=headers)
```

**Why**: Hardcoded credentials are a security risk and can't be rotated.

---

## 8. No Timeout on External Requests

### ❌ WRONG

```python
def fetch_external_data():
    # Can hang forever!
    response = requests.get("https://api.example.com/data")
    return response.json()
```

### ✅ CORRECT

```python
def fetch_external_data():
    try:
        response = requests.get(
            "https://api.example.com/data",
            timeout=30  # 30 second timeout
        )
        return response.json()
    except requests.exceptions.Timeout:
        frappe.throw(_("Request timed out. Please try again."))
    except requests.exceptions.ConnectionError:
        frappe.throw(_("Unable to connect to service."))
```

**Why**: Requests without timeout can hang indefinitely.

---

## 9. Wrong HTTP Status for Error Type

### ❌ WRONG

```python
@frappe.whitelist()
def get_item(name):
    if not frappe.db.exists("Item", name):
        # Returns 200 with error message!
        return {"error": "Not found"}
```

### ✅ CORRECT

```python
@frappe.whitelist()
def get_item(name):
    if not frappe.db.exists("Item", name):
        frappe.throw(
            _("Item not found"),
            exc=frappe.DoesNotExistError  # Returns 404
        )
    
    return frappe.get_doc("Item", name)
```

**Why**: Proper HTTP status codes help clients handle errors correctly.

---

## 10. Not Parsing JSON Input

### ❌ WRONG

```python
@frappe.whitelist()
def update_items(items):
    # Assumes items is already a list - crashes if string!
    for item in items:
        update_item(item)
```

### ✅ CORRECT

```python
@frappe.whitelist()
def update_items(items):
    # Handle both string and list input
    if isinstance(items, str):
        try:
            items = frappe.parse_json(items)
        except Exception:
            frappe.throw(_("Invalid JSON format"), exc=frappe.ValidationError)
    
    if not isinstance(items, list):
        frappe.throw(_("Items must be a list"), exc=frappe.ValidationError)
    
    for item in items:
        update_item(item)
```

**Why**: API inputs may be JSON strings depending on how they're sent.

---

## 11. Blocking UI Without Feedback

### ❌ WRONG

```javascript
async function processLargeData() {
    // No loading indicator - UI appears frozen!
    const result = await frappe.xcall("myapp.api.process_large");
    console.log(result);
}
```

### ✅ CORRECT

```javascript
async function processLargeData() {
    try {
        frappe.freeze(__("Processing large dataset..."));
        const result = await frappe.xcall("myapp.api.process_large");
        frappe.show_alert({message: __("Complete!"), indicator: "green"});
        return result;
    } catch (e) {
        frappe.msgprint({title: __("Error"), message: e.message, indicator: "red"});
    } finally {
        frappe.unfreeze();
    }
}
```

**Why**: Users need feedback during long operations.

---

## 12. No Rate Limit Handling

### ❌ WRONG

```python
def sync_all_records():
    records = get_records()
    for record in records:
        # Rapid-fire requests - will hit rate limits!
        call_external_api(record)
```

### ✅ CORRECT

```python
def sync_all_records():
    records = get_records()
    for i, record in enumerate(records):
        try:
            call_external_api(record)
        except RateLimitError as e:
            # Wait and retry
            wait_time = e.retry_after or 60
            time.sleep(wait_time)
            call_external_api(record)
        
        # Throttle requests
        if i % 10 == 0:
            time.sleep(1)
```

**Why**: APIs have rate limits that must be respected.

---

## 13. Inconsistent Error Response Format

### ❌ WRONG

```python
# Different endpoints return errors differently
@frappe.whitelist()
def endpoint1():
    if error:
        return {"error": True, "msg": "Failed"}

@frappe.whitelist()
def endpoint2():
    if error:
        return {"success": False, "message": "Error occurred"}

@frappe.whitelist()  
def endpoint3():
    if error:
        frappe.throw("Something went wrong")
```

### ✅ CORRECT

```python
# Consistent error handling across all endpoints
@frappe.whitelist()
def endpoint1():
    if error:
        frappe.throw(_("Failed"), exc=frappe.ValidationError)

@frappe.whitelist()
def endpoint2():
    if error:
        frappe.throw(_("Error occurred"), exc=frappe.ValidationError)

@frappe.whitelist()
def endpoint3():
    if error:
        frappe.throw(_("Something went wrong"), exc=frappe.ValidationError)
```

**Why**: Consistent format makes client-side handling easier.

---

## 14. Ignoring Network Errors on Client

### ❌ WRONG

```javascript
frappe.call({
    method: "myapp.api.save",
    callback: function(r) {
        frappe.show_alert("Saved!");
    },
    error: function(r) {
        // Only handles server errors, not network failures
        frappe.msgprint(r._server_messages);
    }
});
```

### ✅ CORRECT

```javascript
frappe.call({
    method: "myapp.api.save",
    callback: function(r) {
        frappe.show_alert({message: "Saved!", indicator: "green"});
    },
    error: function(r) {
        if (!r.status) {
            // Network error
            frappe.msgprint({
                title: __("Network Error"),
                message: __("Unable to connect. Check your internet connection."),
                indicator: "orange"
            });
        } else {
            // Server error
            frappe.msgprint({
                title: __("Error"),
                message: get_server_message(r),
                indicator: "red"
            });
        }
    }
});
```

**Why**: Network errors need different handling than server errors.

---

## 15. Not Logging API Errors

### ❌ WRONG

```python
def external_sync():
    try:
        return call_external_api()
    except Exception as e:
        frappe.throw(str(e))  # No logging - can't debug!
```

### ✅ CORRECT

```python
def external_sync():
    try:
        return call_external_api()
    except Exception as e:
        # Log with full context
        frappe.log_error(
            f"External sync failed\n\nError: {str(e)}\n\n{frappe.get_traceback()}",
            "External API Sync Error"
        )
        frappe.throw(_("Sync failed. Please try again."))
```

**Why**: Logging is essential for debugging production issues.

---

## Quick Checklist: API Implementation Review

Before deploying API endpoints:

- [ ] All inputs validated before use
- [ ] Permission checks in place
- [ ] Proper exception types used (ValidationError, PermissionError, etc.)
- [ ] Error callback provided in frappe.call
- [ ] Internal errors logged, not exposed to users
- [ ] No hardcoded credentials
- [ ] Timeouts set on external requests
- [ ] Rate limiting handled
- [ ] JSON inputs parsed safely
- [ ] Network errors handled separately
- [ ] Loading indicators for long operations
- [ ] Consistent error response format
