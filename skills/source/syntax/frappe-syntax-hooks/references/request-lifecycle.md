# Request Lifecycle & Routing

How Frappe processes HTTP requests from WSGI entry to response, and how
hooks.py integrates at each stage.

---

## 1. Request Lifecycle Overview

Every HTTP request follows this pipeline:

```
Client Request
    │
    ▼
┌─────────────────────────────────┐
│  WSGI Entry                     │
│  frappe.app.application()       │
│  - Creates frappe.local context │
│  - Initializes request recorder │
│  - Applies rate limiting        │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│  before_request hooks           │
│  (all handlers from all apps)   │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│  Route Resolution               │
│  1. Check website_redirects     │
│  2. Match website_route_rules   │
│  3. Match dynamic routes        │
│  4. Select page renderer        │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│  Handler Execution              │
│  - API: /api/* → REST handler   │
│  - Files: /files/* → download   │
│  - Pages: page renderer chain   │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│  after_request hooks            │
│  (all handlers from all apps)   │
└───────────┬─────────────────────┘
            │
            ▼
        Response
```

### Three Request Types

| URL Pattern | Handler | Description |
|-------------|---------|-------------|
| `/api/*` | REST API handler | JSON responses for `frappe.call`, `get_list`, etc. |
| `/backups/*`, `/files/*`, `/private/files/*` | File download handler | Serves files as downloads |
| Everything else | Website router | HTML pages via page renderer chain |

---

## 2. WSGI Entry Point

Frappe is a standard WSGI application. The entry point is `frappe.app.application()`.

```python
# Gunicorn calls this for every HTTP request:
# frappe/app.py
def application(environ, start_response):
    # 1. Initialize frappe.local (thread-local request context)
    # 2. Connect to site database
    # 3. Run before_request hooks
    # 4. Route and dispatch the request
    # 5. Run after_request hooks
    # 6. Return WSGI response
```

`frappe.local` is a thread-local namespace that stores ALL request state:
- `frappe.local.request` — the Werkzeug Request object
- `frappe.local.response` — response dict (built during handling)
- `frappe.local.session` — current session data
- `frappe.local.db` — database connection for this request
- `frappe.local.form_dict` — parsed request parameters

NEVER store state outside `frappe.local` — it leaks between requests in
multi-threaded Gunicorn workers.

---

## 3. Request Middleware Hooks

### before_request

Runs BEFORE route resolution. Use for authentication checks, request
logging, or request modification.

```python
# hooks.py
before_request = ["myapp.middleware.check_maintenance_mode"]
```

```python
# myapp/middleware.py
import frappe

def check_maintenance_mode():
    """Block non-admin requests during maintenance."""
    if frappe.cache.get_value("maintenance_mode"):
        if frappe.session.user != "Administrator":
            frappe.throw("Site is under maintenance", frappe.PermissionError)
```

Rules:
- ALWAYS define as a list of dotted paths (even for a single handler)
- Handlers receive NO arguments — access request via `frappe.local.request`
- To abort a request, raise an exception (`frappe.throw`)
- ALL apps' `before_request` handlers run in app installation order
- NEVER run heavy queries here — this runs on EVERY request

### after_request

Runs AFTER the response is generated but BEFORE it is sent to the client.
Use for response headers, logging, or cleanup.

```python
# hooks.py
after_request = ["myapp.middleware.add_custom_headers"]
```

```python
# myapp/middleware.py
import frappe

def add_custom_headers():
    """Add security headers to every response."""
    frappe.local.response.headers["X-Content-Type-Options"] = "nosniff"
    frappe.local.response.headers["X-Frame-Options"] = "SAMEORIGIN"
```

Rules:
- Handlers receive NO arguments
- Access response via `frappe.local.response`
- NEVER raise exceptions here — the response is already committed
- Use for logging, metrics, header injection

### before_job / after_job

Same pattern but for background jobs (RQ workers), NOT HTTP requests:

```python
before_job = ["myapp.middleware.before_background_job"]
after_job = ["myapp.middleware.after_background_job"]
```

---

## 4. Route Resolution Pipeline

When the website router handles a request (non-API, non-file), route
resolution happens in three sequential steps:

### Step 1: Redirect Check

The router checks `website_redirects` hook and Website Settings redirects:

```python
# hooks.py
website_redirects = [
    {"source": "/old-page", "target": "/new-page"},
    {"source": "/docs(/.*)?", "target": "https://docs.example.com/\\1"}  # regex
]
```

Rules:
- `source` supports regex patterns
- If matched, returns HTTP 301/302 redirect immediately
- Checked BEFORE route rules

### Step 2: Route Rules

The router matches against `website_route_rules`:

```python
# hooks.py
website_route_rules = [
    {"from_route": "/custom-page/<name>", "to_route": "Custom Page"},
    {"from_route": "/shop/<category>", "to_route": "Product Category"},
    {"from_route": "/api-docs", "to_route": "API Documentation"}
]
```

Also checks dynamic routes from DocTypes with `has_web_view = 1`.

### Step 3: Renderer Selection

The resolved path is evaluated against page renderers. The first renderer
whose `can_render()` returns `True` handles the request.

---

## 5. Page Renderer Architecture

Page renderers are Python classes that determine if and how a route should
be rendered.

### Standard Renderers (evaluated in order)

| Renderer | Purpose |
|----------|---------|
| `StaticPage` | Non-markup files (PDFs, images) from `www/` folders |
| `TemplatePage` | HTML/Markdown from `www/` folders or `index` files |
| `WebformPage` | Web Forms matching the request route |
| `DocumentPage` | DocType templates from `/templates/[doctype].html` |
| `ListPage` | List templates from DocType `/templates/` folders |
| `PrintPage` | Print views (standard or custom print formats) |
| `NotFoundPage` | 404 responses (fallback) |
| `NotPermittedPage` | 403 responses |

### Custom Page Renderer

Register a custom renderer via `page_renderer` hook. Custom renderers are
evaluated BEFORE all standard renderers:

```python
# hooks.py
page_renderer = "myapp.renderers.custom_page.CustomPage"
```

```python
# myapp/renderers/custom_page.py
from frappe.website.page_renderers.base_renderer import BaseRenderer

class CustomPage(BaseRenderer):
    def can_render(self):
        """Return True if this renderer handles the current path."""
        return self.path.startswith("my-custom-section")

    def render(self):
        """Generate and return the HTTP response."""
        html = "<h1>Custom rendered page</h1>"
        return self.build_response(html)
```

Rules:
- ALWAYS extend `BaseRenderer` from `frappe.website.page_renderers.base_renderer`
- `can_render()` MUST return a boolean — NEVER raise exceptions
- Use `self.path` to access the current route path
- Use `self.build_response(html)` to create a proper Werkzeug response
- Custom renderers get priority over ALL standard renderers

---

## 6. Router API (Client-Side JavaScript)

### frappe.get_route()

Returns the current route as a list of path segments:

```javascript
// URL: /app/sales-invoice/SI-001
let route = frappe.get_route();
// Returns: ["sales-invoice", "SI-001"]

// URL: /app/query-report/General Ledger
let route = frappe.get_route();
// Returns: ["query-report", "General Ledger"]
```

### frappe.set_route()

Navigate to a new route (client-side, no full page reload):

```javascript
// Navigate to a document
frappe.set_route("sales-invoice", "SI-001");

// Navigate to a list view
frappe.set_route("List", "Sales Invoice");

// Navigate to a report
frappe.set_route("query-report", "General Ledger");

// Navigate with query parameters
frappe.set_route("List", "Sales Invoice", {"company": "My Company"});
```

### frappe.route_options

Set filters before navigating to a list:

```javascript
frappe.route_options = {"customer": "CUST-001", "status": "Unpaid"};
frappe.set_route("List", "Sales Invoice");
// List opens pre-filtered by customer and status
```

ALWAYS set `frappe.route_options` BEFORE calling `frappe.set_route()`.
The options are consumed once and cleared automatically.

---

## 7. Website Routing Hooks Reference

### website_route_rules

Map custom URL patterns to DocType or page controllers:

```python
website_route_rules = [
    {"from_route": "/custom/<name>", "to_route": "Custom Page"}
]
```

### website_redirects

Redirect old URLs to new ones (supports regex):

```python
website_redirects = [
    {"source": "/compare", "target": "/comparison"},
    {"source": "/docs(/.*)?", "target": "https://docs.example.com/\\1"}
]
```

### website_path_resolver (v15+)

Override standard route resolution entirely:

```python
website_path_resolver = "myapp.routing.custom_resolver"
```

### base_template_map

Apply different base templates to different URL patterns using regex:

```python
base_template_map = {
    r"docs.*": "myapp/templates/doc_template.html",
    r"blog.*": "myapp/templates/blog_template.html"
}
```

### before_write_file

Hook into file upload processing before the file is saved:

```python
before_write_file = "myapp.files.validate_upload"
```

```python
# myapp/files.py
import frappe

def validate_upload(**kwargs):
    """Validate file before saving."""
    file_name = kwargs.get("file_name", "")
    content = kwargs.get("content", b"")

    if len(content) > 10 * 1024 * 1024:  # 10 MB
        frappe.throw("File too large. Maximum size is 10 MB.")

    blocked_extensions = [".exe", ".bat", ".cmd", ".sh"]
    if any(file_name.endswith(ext) for ext in blocked_extensions):
        frappe.throw(f"File type not allowed: {file_name}")
```

---

## 8. Anti-Patterns

| Wrong | Correct |
|-------|---------|
| Heavy DB queries in `before_request` | Cache results, check only when needed |
| Storing state in module globals | ALWAYS use `frappe.local` or `frappe.cache` |
| Raising exceptions in `after_request` | Log errors, NEVER throw in after_request |
| Using `page_renderer` without `can_render()` guard | ALWAYS return `False` for unhandled paths |
| Setting `frappe.route_options` after `set_route()` | ALWAYS set route_options BEFORE set_route |
| Regex in `website_redirects` without escaping | ALWAYS escape special regex characters |

---

## Sources

- Frappe Hooks API: https://docs.frappe.io/framework/user/en/python-api/hooks
- Frappe Routing & Rendering: https://docs.frappe.io/framework/user/en/python-api/routing-and-rendering
- Frappe Source: `frappe/app.py`, `frappe/website/router.py`
