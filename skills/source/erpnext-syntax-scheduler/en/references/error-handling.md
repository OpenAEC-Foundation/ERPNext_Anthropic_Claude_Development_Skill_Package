# Error Handling Reference

Complete reference for error handling in background jobs.

## What Happens on Job Failure

1. **Exception is logged**:
   - `Scheduler Log` DocType (visible in desk)
   - `logs/worker.error.log` file

2. **Lock file mechanism**:
   - Scheduler maintains lock file
   - On crash, lock file remains
   - `LockTimeoutError` after 10 minutes of inactive lock

3. **Job status becomes "failed"** in RQ

## Basic Error Handling Pattern

```python
def process_records(records):
    """Process records with error handling per item."""
    success_count = 0
    error_count = 0
    
    for record in records:
        try:
            process_single(record)
            frappe.db.commit()  # Commit per success
            success_count += 1
        except Exception:
            frappe.db.rollback()  # Rollback on error
            frappe.log_error(
                frappe.get_traceback(),
                f"Process Error for {record}"
            )
            error_count += 1
    
    return {"success": success_count, "errors": error_count}
```

## frappe.log_error

### Basic Usage

```python
frappe.log_error(
    message="Error processing record",
    title="Background Job Error"
)
```

### With Traceback

```python
try:
    risky_operation()
except Exception:
    frappe.log_error(
        message=frappe.get_traceback(),
        title="Process Failed"
    )
```

### With Context

```python
frappe.log_error(
    message=f"Failed for {doc.name}: {frappe.get_traceback()}",
    title=f"Process Error: {doc.doctype}"
)
```

## On-Failure Callbacks

```python
def on_failure_handler(job, connection, type, value, traceback):
    """Callback on job failure."""
    frappe.log_error(
        message=f"Job {job.id} failed with {type.__name__}: {value}",
        title="Background Job Failed"
    )
    
    # Optional: send notification
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
    """Callback on job success."""
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

## Retry Pattern (Manual)

```python
def task_with_retry(data, retry_count=0, max_retries=3):
    """Task with exponential backoff retry."""
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

## Batch Processing with Graceful Degradation

```python
def process_batch(items, notify_user=None):
    """Process batch with individual error handling."""
    results = {"success": [], "failed": []}
    
    for item in items:
        try:
            result = process_item(item)
            results["success"].append({"item": item, "result": result})
            frappe.db.commit()
        except frappe.ValidationError as e:
            # Known validation error - log and continue
            results["failed"].append({"item": item, "error": str(e)})
            frappe.db.rollback()
        except Exception:
            # Unknown error - log with traceback
            results["failed"].append({
                "item": item, 
                "error": frappe.get_traceback()
            })
            frappe.log_error(
                frappe.get_traceback(),
                f"Batch Item Failed: {item}"
            )
            frappe.db.rollback()
    
    # Report results
    if notify_user:
        frappe.publish_realtime(
            'batch_complete',
            results,
            user=notify_user
        )
    
    return results
```

## Email Notifications for Failed Jobs

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

**Note**: Uses local mail server on port 25.

## Viewing Error Logs

### Via Desk

Search for "Error Log" in the searchbar.

### Via CLI

```bash
# Recent errors
bench --site mysite.local execute frappe.get_list \
    --kwargs '{"doctype": "Error Log", "limit": 10}'

# Worker log
tail -f logs/worker.error.log
```

## Common Errors and Solutions

### LockTimeoutError

```python
# Cause: Scheduler crash with lock file
# Solution:
frappe.utils.scheduler.enable_scheduler()
```

### TimeLimitExceeded

```python
# Cause: Job takes longer than timeout
# Solution: Use long queue or increase timeout
frappe.enqueue(..., queue='long', timeout=3600)
```

### MemoryError

```python
# Cause: Too much data in memory
# Solution: Process in chunks
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

1. **ALWAYS** try/except with commit/rollback per record
2. **LOG** errors with context (document name, parameters)
3. **USE** on_failure callback for critical tasks
4. **IMPLEMENT** retry logic for external API calls
5. **NOTIFY** users on completion (success or failure)
6. **PROCESS** in chunks for large datasets
