# frappe.enqueue API Reference

## frappe.enqueue

### Full Signature

```python
frappe.enqueue(
    method,                      # Python function or module path (REQUIRED)
    queue="default",             # Queue: "short", "default", "long", or custom
    timeout=None,                # Custom timeout in seconds
    is_async=True,               # False = execute directly (not in worker)
    now=False,                   # True = execute via frappe.call() directly
    job_name=None,               # [DEPRECATED v15] Name for identification
    job_id=None,                 # [v15+] Unique ID for deduplication
    enqueue_after_commit=False,  # Wait for DB commit before enqueue
    at_front=False,              # Place job at front of queue
    on_success=None,             # Callback on success
    on_failure=None,             # Callback on failure
    **kwargs                     # Arguments for the method
)
```

### Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `method` | str/callable | REQUIRED | Module path or function object |
| `queue` | str | "default" | Target queue name |
| `timeout` | int/None | None | Override queue timeout (sec) |
| `is_async` | bool | True | False = synchronous execution |
| `now` | bool | False | True = direct via frappe.call() |
| `job_name` | str/None | None | **DEPRECATED v15** |
| `job_id` | str/None | None | **v15+** Unique ID |
| `enqueue_after_commit` | bool | False | Wait for DB commit |
| `at_front` | bool | False | Priority placement |
| `on_success` | callable | None | Success callback |
| `on_failure` | callable | None | Failure callback |

### Return Value

```python
# Returns RQ Job object (if enqueue_after_commit=False)
job = frappe.enqueue("myapp.tasks.process", param="value")
print(job.id)      # Job ID
print(job.status)  # Job status

# With enqueue_after_commit=True returns None
job = frappe.enqueue(..., enqueue_after_commit=True)
# job is None!
```

### Examples

```python
# Basic - module path
frappe.enqueue("myapp.tasks.process_data", customer="CUST-001")

# Basic - function object
def my_task(name, value):
    pass

frappe.enqueue(my_task, name="test", value=123)

# With custom timeout on long queue
frappe.enqueue(
    "myapp.tasks.heavy_report",
    queue="long",
    timeout=3600,  # 1 hour
    report_type="annual"
)

# Priority job (front of queue)
frappe.enqueue(
    "myapp.tasks.urgent_task",
    at_front=True,
    priority="high"
)

# After database commit
frappe.enqueue(
    "myapp.tasks.send_notification",
    enqueue_after_commit=True,
    user=frappe.session.user
)
```

---

## frappe.enqueue_doc

Enqueue a controller method of a specific document.

### Signature

```python
frappe.enqueue_doc(
    doctype,           # DocType name (REQUIRED)
    name=None,         # Document name
    method=None,       # Controller method name
    queue="default",   # Queue name
    timeout=300,       # Timeout in seconds
    now=False,         # Execute directly
    **kwargs           # Extra arguments
)
```

### Example

```python
# Controller method
class SalesInvoice(Document):
    @frappe.whitelist()
    def send_notification(self, recipient, message):
        # Long-running operation
        pass

# Call it
frappe.enqueue_doc(
    "Sales Invoice",
    "SINV-00001",
    "send_notification",
    queue="long",
    timeout=600,
    recipient="user@example.com",
    message="Invoice ready"
)
```

---

## Document.queue_action

Alternative to enqueue_doc from controller:

```python
class SalesOrder(Document):
    def on_submit(self):
        # Queue heavy processing
        self.queue_action("send_emails", emails=email_list)
    
    def send_emails(self, emails):
        # Heavy operation
        for email in emails:
            send_mail(email)
```

---

## Callbacks

### Success Callback

```python
def on_success_handler(job, connection, result, *args, **kwargs):
    """
    Args:
        job: RQ Job object
        connection: Redis connection
        result: Return value of job method
    """
    frappe.publish_realtime(
        "show_alert",
        {"message": f"Job {job.id} completed!"}
    )
```

### Failure Callback

```python
def on_failure_handler(job, connection, type, value, traceback):
    """
    Args:
        job: RQ Job object
        connection: Redis connection
        type: Exception type
        value: Exception value
        traceback: Traceback object
    """
    frappe.log_error(
        f"Job {job.id} failed: {value}",
        "Background Job Error"
    )
```

### Usage

```python
frappe.enqueue(
    "myapp.tasks.risky_operation",
    on_success=on_success_handler,
    on_failure=on_failure_handler,
    data=my_data
)
```

---

## Job Deduplication

### v15+ Pattern (Recommended)

```python
from frappe.utils.background_jobs import is_job_enqueued

job_id = f"data_import::{self.name}"

if not is_job_enqueued(job_id):
    frappe.enqueue(
        "myapp.tasks.import_data",
        job_id=job_id,
        doc_name=self.name
    )
else:
    frappe.msgprint("Import already in progress")
```

### v14 Pattern (Deprecated)

```python
# ONLY for legacy v14 code
from frappe.core.page.background_jobs.background_jobs import get_info

enqueued_jobs = [d.get("job_name") for d in get_info()]
if self.name not in enqueued_jobs:
    frappe.enqueue(..., job_name=self.name)
```
