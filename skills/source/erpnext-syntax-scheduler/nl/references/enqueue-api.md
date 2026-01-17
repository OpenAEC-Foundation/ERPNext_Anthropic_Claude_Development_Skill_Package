# frappe.enqueue API Reference

Complete referentie voor frappe.enqueue en frappe.enqueue_doc.

## frappe.enqueue - Alle Parameters

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

## Parameter Details

| Parameter | Type | Default | Beschrijving |
|-----------|------|---------|--------------|
| `method` | str/callable | - | Module path of functie object |
| `queue` | str | "default" | Target queue naam |
| `timeout` | int/None | None | Override queue timeout (seconden) |
| `is_async` | bool | True | False = synchrone executie |
| `now` | bool | False | True = direct via frappe.call() |
| `job_name` | str/None | None | **DEPRECATED v15** |
| `job_id` | str/None | None | **v15+** Unieke ID voor deduplicatie |
| `enqueue_after_commit` | bool | False | Wacht tot DB commit |
| `at_front` | bool | False | Priority placement |
| `on_success` | callable/None | None | Success callback |
| `on_failure` | callable/None | None | Failure callback |

## Return Value

```python
# Retourneert RQ Job object (als enqueue_after_commit=False)
job = frappe.enqueue('myapp.tasks.process', param='value')
print(job.id)  # Job ID
print(job.get_status())  # 'queued', 'started', 'finished', 'failed'
```

**Let op**: Met `enqueue_after_commit=True` retourneert de call `None`.

## Method Specificatie

### Als String (Aanbevolen)

```python
frappe.enqueue('myapp.tasks.process_data', customer='CUST-001')
```

### Als Functie Object

```python
def my_task(name, value):
    pass

frappe.enqueue(my_task, name='test', value=123)
```

## Voorbeelden

### Basis Gebruik

```python
frappe.enqueue('myapp.tasks.send_email', recipient='user@example.com')
```

### Met Custom Timeout

```python
frappe.enqueue(
    'myapp.tasks.heavy_report',
    queue='long',
    timeout=3600,  # 1 uur
    report_type='annual'
)
```

### Met Callbacks

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

### Na Database Commit

```python
# Belangrijk voor data integriteit
doc.save()
frappe.enqueue(
    'myapp.tasks.process_saved_doc',
    enqueue_after_commit=True,
    doc_name=doc.name
)
```

### Priority Placement

```python
# Job vooraan in queue plaatsen
frappe.enqueue(
    'myapp.tasks.urgent_task',
    at_front=True
)
```

### Synchrone Executie (Testing)

```python
# Voor debugging - draait NIET in worker
frappe.enqueue(
    'myapp.tasks.process',
    is_async=False  # Blokkeert totdat klaar
)
```

## frappe.enqueue_doc

Enqueue een controller method van een specifiek document.

### Syntax

```python
frappe.enqueue_doc(
    doctype,           # DocType naam
    name=None,         # Document name
    method=None,       # Controller method naam als string
    queue="default",   # Queue naam
    timeout=300,       # Timeout in seconden
    now=False,         # Direct uitvoeren
    **kwargs           # Extra argumenten voor method
)
```

### Voorbeeld

```python
# Controller
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
    message="Your invoice is ready"
)
```

## Document.queue_action

Alternatief via controller method:

```python
class SalesOrder(Document):
    def on_submit(self):
        self.queue_action('send_emails', emails=email_list)
    
    def send_emails(self, emails):
        # Heavy operation
        pass
```

## Job ID voor Deduplicatie (v15+)

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

## Versieverschillen

| Feature | v14 | v15 |
|---------|-----|-----|
| Deduplicatie | `job_name` | `job_id` |
| Check functie | get_info() parsing | `is_job_enqueued()` |
| Callbacks | Basis | Volledig ondersteund |
