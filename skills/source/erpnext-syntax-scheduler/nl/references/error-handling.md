# Error Handling Reference

Complete referentie voor error handling in background jobs.

## Wat Gebeurt Bij Job Failure

1. **Exception wordt gelogd**:
   - `Scheduler Log` DocType (zichtbaar in desk)
   - `logs/worker.error.log` bestand

2. **Lock file mechanisme**:
   - Scheduler houdt lock file bij
   - Bij crash blijft lock file bestaan
   - `LockTimeoutError` na 10 minuten inactieve lock

3. **Job status wordt "failed"** in RQ

## Basis Error Handling Pattern

```python
def process_records(records):
    """Verwerk records met error handling per item."""
    success_count = 0
    error_count = 0
    
    for record in records:
        try:
            process_single(record)
            frappe.db.commit()  # Commit per success
            success_count += 1
        except Exception:
            frappe.db.rollback()  # Rollback bij error
            frappe.log_error(
                frappe.get_traceback(),
                f"Process Error for {record}"
            )
            error_count += 1
    
    return {"success": success_count, "errors": error_count}
```

## frappe.log_error

### Basis Gebruik

```python
frappe.log_error(
    message="Error processing record",
    title="Background Job Error"
)
```

### Met Traceback

```python
try:
    risky_operation()
except Exception:
    frappe.log_error(
        message=frappe.get_traceback(),
        title="Process Failed"
    )
```

### Met Context

```python
frappe.log_error(
    message=f"Failed for {doc.name}: {frappe.get_traceback()}",
    title=f"Process Error: {doc.doctype}"
)
```

## On-Failure Callbacks

```python
def on_failure_handler(job, connection, type, value, traceback):
    """Callback bij job failure."""
    frappe.log_error(
        message=f"Job {job.id} failed with {type.__name__}: {value}",
        title="Background Job Failed"
    )
    
    # Optioneel: notificatie sturen
    frappe.sendmail(
        recipients=["admin@example.com"],
        subject=f"Job Failed: {job.id}",
        message=f"Error: {value}"
    )

frappe.enqueue(
    'myapp.tasks.risky_operation',
    on_failure=on_failure_handler
)
```

## On-Success Callbacks

```python
def on_success_handler(job, connection, result, *args, **kwargs):
    """Callback bij job success."""
    frappe.publish_realtime(
        'show_alert',
        {'message': 'Processing complete!', 'indicator': 'green'},
        user=frappe.session.user
    )

frappe.enqueue(
    'myapp.tasks.process',
    on_success=on_success_handler
)
```

## Retry Pattern (Handmatig)

```python
def task_with_retry(data, retry_count=0, max_retries=3):
    """Task met exponential backoff retry."""
    try:
        external_api_call(data)
    except Exception as e:
        if retry_count < max_retries:
            # Exponential backoff: 60s, 120s, 240s
            delay = 60 * (2 ** retry_count)
            frappe.enqueue(
                'myapp.tasks.task_with_retry',
                queue='default',
                data=data,
                retry_count=retry_count + 1,
                max_retries=max_retries,
                enqueue_after_commit=True
            )
            frappe.log_error(
                f"Retry {retry_count + 1}/{max_retries} scheduled",
                f"Task Retry: {data}"
            )
        else:
            frappe.log_error(
                frappe.get_traceback(),
                f"Task Failed after {max_retries} retries: {data}"
            )
            raise
```

## Batch Processing met Graceful Degradation

```python
def process_batch(items, notify_user=None):
    """Verwerk batch met individuele error handling."""
    results = {"success": [], "failed": []}
    
    for item in items:
        try:
            result = process_item(item)
            results["success"].append({"item": item, "result": result})
            frappe.db.commit()
        except frappe.ValidationError as e:
            # Bekende validatie fout - log en ga door
            results["failed"].append({"item": item, "error": str(e)})
            frappe.db.rollback()
        except Exception:
            # Onbekende fout - log met traceback
            results["failed"].append({
                "item": item, 
                "error": frappe.get_traceback()
            })
            frappe.log_error(
                frappe.get_traceback(),
                f"Batch Item Failed: {item}"
            )
            frappe.db.rollback()
    
    # Rapporteer resultaten
    if notify_user:
        frappe.publish_realtime(
            'batch_complete',
            results,
            user=notify_user
        )
    
    return results
```

## Email Notificaties voor Failed Jobs

In `sites/common_site_config.json`:

```json
{
    "celery_error_emails": {
        "ADMINS": [
            ["Admin Name", "admin@example.com"]
        ],
        "SERVER_EMAIL": "errors@example.com"
    }
}
```

**Let op**: Gebruikt lokale mailserver op port 25.

## Error Logs Bekijken

### Via Desk

Zoek naar "Error Log" in de searchbar.

### Via CLI

```bash
# Recente errors
bench --site mysite.local execute frappe.get_list \
    --kwargs '{"doctype": "Error Log", "limit": 10}'

# Worker log
tail -f logs/worker.error.log
```

## Common Errors en Oplossingen

### LockTimeoutError

```python
# Oorzaak: Scheduler crash met lock file
# Oplossing:
frappe.utils.scheduler.enable_scheduler()
```

### TimeLimitExceeded

```python
# Oorzaak: Job duurt langer dan timeout
# Oplossing: Gebruik long queue of verhoog timeout
frappe.enqueue(..., queue='long', timeout=3600)
```

### MemoryError

```python
# Oorzaak: Te veel data in memory
# Oplossing: Verwerk in chunks
def process_large_dataset():
    offset = 0
    batch_size = 1000
    while True:
        items = frappe.get_all("Item", limit=batch_size, start=offset)
        if not items:
            break
        process_items(items)
        frappe.db.commit()
        offset += batch_size
```

## Best Practices

1. **ALTIJD** try/except met commit/rollback per record
2. **LOG** errors met context (document name, parameters)
3. **GEBRUIK** on_failure callback voor kritieke taken
4. **IMPLEMENTEER** retry logic voor externe API calls
5. **NOTIFICEER** users bij completion (success of failure)
6. **VERWERK** in chunks bij grote datasets
