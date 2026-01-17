# frappe.enqueue API Reference

Complete reference for frappe.enqueue and frappe.enqueue_doc.

## frappe.enqueue - All Parameters

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

## Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `method` | str/callable | - | Module path or function object |
| `queue` | str | "default" | Target queue name |
| `timeout` | int/None | None | Override queue timeout (seconds) |
| `is_async` | bool | True | False = synchronous execution |
| `now` | bool | False | True = direct via frappe.call() |
| `job_name` | str/None | None | **DEPRECATED v15** |
| `job_id` | str/None | None | **v15+** Unique ID for deduplication |
| `enqueue_after_commit` | bool | False | Wait until DB commit |
| `at_front` | bool | False | Priority placement |
| `on_success` | callable/None | None | Success callback |
| `on_failure` | callable/None | None | Failure callback |

## Return Value

```python
# Returns RQ Job object (if enqueue_after_commit=False)
job = frappe.enqueue('myapp.tasks.process', param='value')
print(job.id)  # Job ID
print(job.get_status())  # 'queued', 'started', 'finished', 'failed'
```

**Note**: With `enqueue_after_commit=True` the call returns `None`.

## Method Specification

### As String (Recommended)

```python
frappe.enqueue('myapp.tasks.process_data', customer='CUST-001')
```

### As Function Object

```python
def my_task(name, value):
    pass

frappe.enqueue(my_task, name='test', value=123)
```

## Examples

### Basic Usage

```python
frappe.enqueue('myapp.tasks.send_email', recipient='user@example.com')
```

### With Custom Timeout

```python
frappe.enqueue(
    'myapp.tasks.heavy_report',
    queue='long',
    timeout=3600,  # 1 hour
    report_type='annual'
)
```

### With Callbacks

```python
def on_success_handler(job, connection, result, *args, **kwargs):
    frappe.publish_realtime(
        'show_alert',
        {'message': 'Job completed!', 'indicator': 'green'}
    )

def on_failure_handler(job, connection, type, value, traceback):
    frappe.log_error(f"Job {job.id} failed: {value}")

frappe.enqueue(
    'myapp.tasks.risky_operation',
    on_success=on_success_handler,
    on_failure=on_failure_handler
)
```

### After Database Commit

```python
# Important for data integrity
doc.save()
frappe.enqueue(
    'myapp.tasks.process_saved_doc',
    enqueue_after_commit=True,
    doc_name=doc.name
)
```

### Priority Placement

```python
# Place job at front of queue
frappe.enqueue(
    'myapp.tasks.urgent_task',
    at_front=True
)
```

### Synchronous Execution (Testing)

```python
# For debugging - does NOT run in worker
frappe.enqueue(
    'myapp.tasks.process',
    is_async=False  # Blocks until complete
)
```

## frappe.enqueue_doc

Enqueue a controller method of a specific document.

### Syntax

```python
frappe.enqueue_doc(
    doctype,           # DocType name
    name=None,         # Document name
    method=None,       # Controller method name as string
    queue="default",   # Queue name
    timeout=300,       # Timeout in seconds
    now=False,         # Execute immediately
    **kwargs           # Extra arguments for method
)
```

### Example

```python
# Controller
class SalesInvoice(Document):
    @frappe.whitelist()
    def send_notification(self, recipient, message):
        # Long-running operation
        pass

# Call
frappe.enqueue_doc(
    "Sales Invoice",
    "SINV-00001",
    "send_notification",
    queue="long",
    timeout=600,
    recipient="user@example.com",
    message="Your invoice is ready"
)
```

## Document.queue_action

Alternative via controller method:

```python
class SalesOrder(Document):
    def on_submit(self):
        self.queue_action('send_emails', emails=email_list)
    
    def send_emails(self, emails):
        # Heavy operation
        pass
```

## Job ID for Deduplication (v15+)

```python
from frappe.utils.background_jobs import is_job_enqueued

job_id = f"process::{doc.name}"
if not is_job_enqueued(job_id):
    frappe.enqueue(
        'myapp.tasks.process',
        job_id=job_id,
        doc_name=doc.name
    )
```

## Version Differences

| Feature | v14 | v15 |
|---------|-----|-----|
| Deduplication | `job_name` | `job_id` |
| Check function | get_info() parsing | `is_job_enqueued()` |
| Callbacks | Basic | Fully supported |
