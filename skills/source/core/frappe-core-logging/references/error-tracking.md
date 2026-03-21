# Error Tracking — Error Log, Sentry, Monitoring

## Error Log DocType

### Creating Error Log Entries

```python
# ALWAYS use keyword arguments
frappe.log_error(
    title="Short description",              # 140 chars max
    message="Full traceback or details",    # Unlimited
    reference_doctype="Sales Order",        # Optional: related DocType
    reference_name="SO-00001"               # Optional: related document
)

# Minimal — auto-captures current traceback
try:
    process_order(order)
except Exception:
    frappe.log_error(title=f"Order processing failed: {order.name}")

# With explicit traceback
import traceback
try:
    risky_call()
except Exception:
    frappe.log_error(
        title="External API failure",
        message=frappe.get_traceback(with_context=True)
    )
```

### Error Log Schema

| Field | Type | Notes |
|-------|------|-------|
| `method` | Data | Title/short description (140 char max) |
| `error` | Code | Full traceback text |
| `reference_doctype` | Link → DocType | Related DocType |
| `reference_name` | Data | Related document name |
| `seen` | Check | Auto-set to 1 on first view |
| `trace_id` | Data | Request trace ID [v15+] |
| `metadata` | Code | JSON: request/job context [v15+] |

### Querying Error Logs

```python
# Recent errors for a specific module
errors = frappe.get_all("Error Log",
    filters={"method": ["like", "%payment%"]},
    fields=["name", "method", "creation"],
    order_by="creation desc",
    limit=10
)

# Errors for a specific document
errors = frappe.get_all("Error Log",
    filters={
        "reference_doctype": "Sales Order",
        "reference_name": "SO-00001"
    }
)
```

### Cleanup

```python
# Auto-cleanup: 30 days default
from frappe.core.doctype.error_log.error_log import ErrorLog
ErrorLog.clear_old_logs(days=30)

# Manual full cleanup (System Manager only)
# Via Desk: Error Log list → Menu → Clear Error Logs
# Via API: frappe.client.clear_error_logs()
```

### Auto-Captured Exceptions

Unhandled exceptions returning HTTP 500+ are automatically captured.

**NOT auto-captured:**
- `frappe.AuthenticationError` — expected for login failures
- `frappe.CSRFTokenError` — expected for token mismatches
- `frappe.SecurityException` — expected for access violations
- `frappe.InReadOnlyMode` — expected during maintenance

**Disable auto-capture:**
```json
// site_config.json
{"disable_error_snapshot": true}
```

---

## Sentry Integration

### Setup

```bash
# Set DSN as environment variable
export FRAPPE_SENTRY_DSN="https://key@sentry.io/project"

# Optional: database monitoring
export ENABLE_SENTRY_DB_MONITORING=1

# Optional: performance tracing
export SENTRY_TRACING_SAMPLE_RATE=0.1    # 10% of requests

# Optional: profiling
export SENTRY_PROFILING_SAMPLE_RATE=0.01  # 1% of requests
```

**Requirement:** `enable_telemetry` system setting must be enabled.

### What Gets Captured

- Unhandled exceptions (excluding ValidationError, PermissionError)
- Request context (JSON body, form data — auto-sanitized)
- User and site identification
- SQL queries as spans (when DB monitoring enabled)
- Trace ID propagation via `X-Frappe-Request-Id` header

### Filtered Exceptions (NOT sent to Sentry)

```python
FILTERED_EXCEPTIONS = [
    frappe.AuthenticationError,
    frappe.CSRFTokenError,
    frappe.SecurityException,
    frappe.ValidationError,      # User input errors
    frappe.PermissionError,      # Access control
]
```

---

## Request Monitoring

### Enable

```json
// site_config.json
{"monitor": true}
```

### What Gets Logged

**HTTP Requests:**
- Timestamp, UUID, trace_id
- Duration (microseconds)
- Client IP, HTTP method, path
- Response status code, size

**Background Jobs:**
- Method name, queue
- Duration, wait time
- Success/failure

### Output

JSON lines in `logs/monitor.json.log`. Data buffered in Redis, flushed periodically.
Max 1M entries in Redis before trimming.

### Parsing Monitor Data

```python
import json

with open("logs/monitor.json.log") as f:
    for line in f:
        entry = json.loads(line)
        if entry.get("duration", 0) > 5_000_000:  # > 5 seconds
            print(f"Slow request: {entry['path']} took {entry['duration']/1e6:.1f}s")
```

---

## Request Logging

### Enable

```json
// site_config.json
{"enable_frappe_logger": true}
```

### Output

Logs to `logs/frappe.web.log` with fields:
- Site name, remote IP, PID
- Username, URL, HTTP method
- Scheme, HTTP status code

---

## Debug Helpers (Development Only)

```python
# Print to console (development only — NOT for production)
frappe.errprint(variable)    # → stderr + frappe.error_log (request-scoped)
frappe.log("debug message")  # → stderr + frappe.debug_log (request-scoped)

# These are returned in API responses during development:
# frappe.error_log → response.exc
# frappe.debug_log → response._debug_messages
```

**NEVER use frappe.errprint() or frappe.log() in production code.**
They are request-scoped debug helpers that don't persist.

---

## Common Production Setup

```json
// site_config.json — recommended production settings
{
    "enable_frappe_logger": true,
    "monitor": true,
    "logging": 0
}
```

```bash
# Environment — recommended for production
export FRAPPE_SENTRY_DSN="https://..."
export SENTRY_TRACING_SAMPLE_RATE=0.05

# For Docker/containers
export FRAPPE_STREAM_LOGGING=1
```
