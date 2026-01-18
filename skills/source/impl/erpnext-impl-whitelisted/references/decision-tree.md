# API Selection Decision Tree

Complete guide for choosing the right API pattern in Frappe/ERPNext.

---

## Master Decision Tree

```
WHAT TYPE OF API ARE YOU BUILDING?
│
├─► PUBLIC endpoint (no login required)?
│   │
│   ├─► Contact/inquiry form?
│   │   └─► allow_guest=True, methods=["POST"]
│   │       + Input sanitization
│   │       + Rate limiting (v15+)
│   │       + CAPTCHA consideration
│   │
│   ├─► Status check / tracking?
│   │   └─► allow_guest=True, methods=["GET"]
│   │       + Validate tracking ID format
│   │       + Limit exposed fields
│   │
│   └─► Webhook receiver?
│       └─► allow_guest=True, methods=["POST"]
│           + Signature verification
│           + IP whitelist if possible
│
├─► AUTHENTICATED endpoint (login required)?
│   │
│   ├─► Any logged-in user can access?
│   │   └─► Default @frappe.whitelist()
│   │       + Document-level permission checks
│   │
│   ├─► Specific role(s) required?
│   │   └─► frappe.only_for("Role") inside method
│   │
│   └─► Based on document permissions?
│       └─► frappe.has_permission(doctype, ptype, doc)
│
├─► DOCUMENT-SPECIFIC method?
│   │
│   ├─► Called from form UI?
│   │   └─► Controller method with @frappe.whitelist()
│   │       Client: frm.call('method_name', args)
│   │
│   └─► Standalone but related to DocType?
│       └─► Separate API file
│           Client: frappe.call('path.method', args)
│
└─► INTEGRATION endpoint?
    │
    ├─► Receiving webhooks?
    │   └─► allow_guest=True + signature verification
    │
    └─► Sending data externally?
        └─► Internal API (authenticated)
            + Background job for heavy operations
```

---

## Permission Model Selection

```
WHO SHOULD BE ABLE TO CALL THIS API?
│
├─► ANYONE (public internet)?
│   │
│   │   @frappe.whitelist(allow_guest=True)
│   │
│   ├─► Considerations:
│   │   • Validate ALL input strictly
│   │   • Sanitize for XSS/injection
│   │   • Rate limit (v15+) or manual throttle
│   │   • Never expose internal errors
│   │   • Limit response data
│   │   • Consider CAPTCHA
│   │
│   └─► Common use cases:
│       • Contact forms
│       • Order tracking
│       • Public status pages
│       • Webhook receivers
│
├─► ANY LOGGED-IN USER?
│   │
│   │   @frappe.whitelist()  # Default
│   │
│   ├─► Still need:
│   │   • Document-level permission checks
│   │   • Input validation
│   │
│   └─► Common use cases:
│       • User profile updates
│       • Dashboard data
│       • General utilities
│
├─► SPECIFIC ROLE(S)?
│   │
│   │   @frappe.whitelist()
│   │   def method():
│   │       frappe.only_for("Role Name")
│   │       # or
│   │       frappe.only_for(["Role1", "Role2"])
│   │
│   └─► Common use cases:
│       • Admin functions
│       • HR data access
│       • Financial operations
│
└─► DOCUMENT-LEVEL PERMISSION?
    │
    │   @frappe.whitelist()
    │   def method(doctype, name):
    │       if not frappe.has_permission(doctype, "read", name):
    │           frappe.throw("Not permitted", frappe.PermissionError)
    │
    └─► Common use cases:
        • Document CRUD operations
        • Related document access
        • Field-level data retrieval
```

---

## HTTP Method Selection

```
WHAT DOES YOUR API DO?
│
├─► READ data only?
│   └─► methods=["GET"]
│       • Cacheable
│       • Safe to retry
│       • Parameters in URL
│
├─► CREATE or MODIFY data?
│   └─► methods=["POST"]
│       • Not cacheable
│       • Parameters in body
│       • CSRF protection applies
│
├─► Either read or write?
│   └─► methods=["GET", "POST"]  or  default (all)
│
└─► Specific REST semantics?
    ├─► Create → POST
    ├─► Read → GET
    ├─► Update → PUT/PATCH (via POST in Frappe)
    └─► Delete → DELETE (via POST in Frappe)
```

---

## Code Location Selection

```
WHERE SHOULD THE API CODE LIVE?
│
├─► DocType-specific, called from form?
│   │
│   │   myapp/
│   │   └── doctype/
│   │       └── my_doctype/
│   │           └── my_doctype.py  ← Controller method here
│   │
│   │   class MyDoctype(Document):
│   │       @frappe.whitelist()
│   │       def my_method(self, arg):
│   │           return result
│   │
│   └─► Client: frm.call('my_method', {arg: value})
│
├─► DocType-related but standalone?
│   │
│   │   myapp/
│   │   └── doctype/
│   │       └── my_doctype/
│   │           ├── my_doctype.py
│   │           └── my_doctype_api.py  ← API here
│   │
│   └─► Client: frappe.call('myapp.doctype.my_doctype.my_doctype_api.method')
│
├─► General app API?
│   │
│   │   myapp/
│   │   └── api.py  ← General APIs here
│   │
│   └─► Client: frappe.call('myapp.api.method')
│
├─► Multiple API modules?
│   │
│   │   myapp/
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── customers.py
│   │       ├── orders.py
│   │       └── reports.py
│   │
│   └─► Client: frappe.call('myapp.api.customers.get_customer')
│
└─► External integration?
    │
    │   myapp/
    │   └── integrations/
    │       ├── __init__.py
    │       ├── stripe.py
    │       └── shopify.py
    │
    └─► Client: frappe.call('myapp.integrations.stripe.process_webhook')
```

---

## Error Handling Selection

```
HOW SHOULD ERRORS BE HANDLED?
│
├─► User-facing validation error?
│   └─► frappe.throw(_("Message"), frappe.ValidationError)
│       • Returns HTTP 417
│       • Shows message to user
│
├─► Permission denied?
│   └─► frappe.throw(_("Not permitted"), frappe.PermissionError)
│       • Returns HTTP 403
│       • Standard access denied
│
├─► Resource not found?
│   └─► frappe.throw(_("Not found"), frappe.DoesNotExistError)
│       • Returns HTTP 404
│
├─► Duplicate entry?
│   └─► frappe.throw(_("Already exists"), frappe.DuplicateEntryError)
│       • Returns HTTP 409
│
├─► Internal error (unexpected)?
│   └─► try/except with:
│       • frappe.log_error() for debugging
│       • Generic message to user
│       • HTTP 500
│
└─► Custom HTTP status needed?
    └─► frappe.local.response["http_status_code"] = code
        return {"error": "message"}
```

---

## Response Format Selection

```
WHAT SHOULD THE API RETURN?
│
├─► Simple success/failure?
│   └─► return {"success": True/False}
│
├─► Single value?
│   └─► return value
│       # Response: {"message": value}
│
├─► Dictionary/object?
│   └─► return {"key": "value", ...}
│       # Response: {"message": {"key": "value", ...}}
│
├─► List of items?
│   └─► return [item1, item2, ...]
│       # Response: {"message": [...]}
│
├─► Paginated list?
│   └─► return {
│           "data": [...],
│           "total": count,
│           "page": current,
│           "page_size": size
│       }
│
├─► File download?
│   └─► frappe.response["filename"] = "file.csv"
│       frappe.response["filecontent"] = content
│       frappe.response["type"] = "download"
│
└─► Custom HTTP response?
    └─► frappe.local.response["http_status_code"] = 201
        return {"created": True, "id": doc.name}
```

---

## Client Call Selection

```
HOW WILL THE CLIENT CALL THIS API?
│
├─► From DocType form (frm available)?
│   │
│   ├─► Calling controller method?
│   │   └─► frm.call('method_name', {args})
│   │       • Automatically includes docname
│   │       • Permission checked by Frappe
│   │
│   └─► Calling standalone API?
│       └─► frappe.call({method: 'path.to.method', args: {}})
│
├─► From list view or other page?
│   └─► frappe.call({method: 'path.to.method', args: {}})
│
├─► From custom page/app?
│   └─► frappe.call() or fetch('/api/method/...')
│
├─► From external system?
│   └─► HTTP request to /api/method/path.to.method
│       • Include authentication header
│       • Use API keys or token
│
└─► Need loading indicator?
    └─► frappe.call({
            method: '...',
            freeze: true,
            freeze_message: __('Loading...')
        })
```

---

## Security Checklist by API Type

### Public API (allow_guest=True)

- [ ] Input validation for ALL parameters
- [ ] Input sanitization (strip_html, escape)
- [ ] Length limits on string inputs
- [ ] Type checking
- [ ] Rate limiting (v15+) or manual throttle
- [ ] No sensitive data in responses
- [ ] No internal error details exposed
- [ ] Consider CAPTCHA for forms
- [ ] Log suspicious activity

### Authenticated API (default)

- [ ] Document-level permission checks
- [ ] Input validation
- [ ] No SQL injection (parameterized queries)
- [ ] Appropriate error messages
- [ ] Audit logging for sensitive operations

### Role-Restricted API

- [ ] frappe.only_for() at start of method
- [ ] Still validate input
- [ ] Consider additional permission checks
- [ ] Audit logging

### Admin API

- [ ] frappe.only_for("System Manager")
- [ ] Extra confirmation for destructive operations
- [ ] Comprehensive audit logging
- [ ] Consider two-factor for critical operations
