# frappe.enqueue API Reference

## frappe.enqueue

### Volledige Signature

```python
frappe.enqueue(
    method,                      # Python functie of module path (VERPLICHT)
    queue="default",             # Queue: "short", "default", "long", of custom
    timeout=None,                # Custom timeout in seconden
    is_async=True,               # False = execute direct (niet in worker)
    now=False,                   # True = execute via frappe.call() direct
    job_name=None,               # [DEPRECATED v15] Naam voor identificatie
    job_id=None,                 # [v15+] Unieke ID voor deduplicatie
    enqueue_after_commit=False,  # Wacht op DB commit voor enqueue
    at_front=False,              # Plaats job vooraan in queue
    on_success=None,             # Callback bij success
    on_failure=None,             # Callback bij failure
    **kwargs                     # Argumenten voor de method
)
```

### Parameter Details

| Parameter | Type | Default | Beschrijving |
|-----------|------|---------|--------------|
| `method` | str/callable | VERPLICHT | Module path of functie object |
| `queue` | str | "default" | Target queue naam |
| `timeout` | int/None | None | Override queue timeout (sec) |
| `is_async` | bool | True | False = synchrone executie |
| `now` | bool | False | True = direct via frappe.call() |
| `job_name` | str/None | None | **DEPRECATED v15** |
| `job_id` | str/None | None | **v15+** Unieke ID |
| `enqueue_after_commit` | bool | False | Wacht tot DB commit |
| `at_front` | bool | False | Priority placement |
| `on_success` | callable | None | Success callback |
| `on_failure` | callable | None | Failure callback |

### Return Value

```python
# Retourneert RQ Job object (als enqueue_after_commit=False)
job = frappe.enqueue("myapp.tasks.process", param="value")
print(job.id)      # Job ID
print(job.status)  # Job status

# Met enqueue_after_commit=True retourneert None
job = frappe.enqueue(..., enqueue_after_commit=True)
# job is None!
```

### Voorbeelden

```python
# Basis - module path
frappe.enqueue("myapp.tasks.process_data", customer="CUST-001")

# Basis - functie object
def my_task(name, value):
    pass

frappe.enqueue(my_task, name="test", value=123)

# Met custom timeout op long queue
frappe.enqueue(
    "myapp.tasks.heavy_report",
    queue="long",
    timeout=3600,  # 1 uur
    report_type="annual"
)

# Priority job (vooraan in queue)
frappe.enqueue(
    "myapp.tasks.urgent_task",
    at_front=True,
    priority="high"
)

# Na database commit
frappe.enqueue(
    "myapp.tasks.send_notification",
    enqueue_after_commit=True,
    user=frappe.session.user
)
```

---

## frappe.enqueue_doc

Enqueue een controller method van een specifiek document.

### Signature

```python
frappe.enqueue_doc(
    doctype,           # DocType naam (VERPLICHT)
    name=None,         # Document name
    method=None,       # Controller method naam
    queue="default",   # Queue naam
    timeout=300,       # Timeout in seconden
    now=False,         # Direct uitvoeren
    **kwargs           # Extra argumenten
)
```

### Voorbeeld

```python
# Controller method
class SalesInvoice(Document):
    @frappe.whitelist()
    def send_notification(self, recipient, message):
        # Langlopende operatie
        pass

# Aanroepen
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

Alternatief voor enqueue_doc vanuit controller:

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
        result: Return value van de job method
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

### Gebruik

```python
frappe.enqueue(
    "myapp.tasks.risky_operation",
    on_success=on_success_handler,
    on_failure=on_failure_handler,
    data=my_data
)
```

---

## Job Deduplicatie

### v15+ Pattern (Aanbevolen)

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
# ALLEEN voor legacy v14 code
from frappe.core.page.background_jobs.background_jobs import get_info

enqueued_jobs = [d.get("job_name") for d in get_info()]
if self.name not in enqueued_jobs:
    frappe.enqueue(..., job_name=self.name)
```
