---
name: erpnext-syntax-scheduler
description: Deterministic syntax reference for Frappe Scheduler Events and Background Jobs (frappe.enqueue). Use for scheduler_events in hooks.py, frappe.enqueue/enqueue_doc API, queue configuration, job deduplication, error handling and monitoring. Covers v14/v15 version differences including job_id (v15) vs job_name (v14 deprecated).
---

# ERPNext Syntax: Scheduler & Background Jobs

Deterministic syntax for scheduler events and background jobs in Frappe/ERPNext v14 and v15.

## When to Use This Skill

- Configure periodic tasks via `hooks.py`
- Execute long operations asynchronously with `frappe.enqueue`
- Configure queue types and timeouts
- Implement job deduplication
- Handle background job errors
- Monitor and debug jobs

## Critical Version Differences

| Aspect | v14 | v15 |
|--------|-----|-----|
| Scheduler tick | ~240 sec (4 min) | ~60 sec |
| Config key | `scheduler_interval` | `scheduler_tick_interval` |
| Job deduplication | `job_name` | `job_id` + `is_job_enqueued()` |

## Scheduler Events (hooks.py)

### Event Types

```python
# hooks.py
scheduler_events = {
    "all": ["myapp.tasks.every_tick"],       # Every scheduler tick
    "hourly": ["myapp.tasks.per_hour"],      # Every hour (default queue)
    "daily": ["myapp.tasks.daily"],          # Every day
    "weekly": ["myapp.tasks.weekly"],        # Every week
    "monthly": ["myapp.tasks.monthly"],      # Every month
    
    # Long queue variants (for heavy processing)
    "hourly_long": ["myapp.tasks.heavy_hourly"],
    "daily_long": ["myapp.tasks.heavy_daily"],
    "weekly_long": ["myapp.tasks.heavy_weekly"],
    "monthly_long": ["myapp.tasks.heavy_monthly"],
}
```

### Cron Syntax

```python
scheduler_events = {
    "cron": {
        "*/15 * * * *": ["myapp.tasks.every_15_min"],      # Every 15 min
        "0 9 * * 1-5": ["myapp.tasks.weekday_9am"],        # Mon-Fri 9:00
        "0 0 1 * *": ["myapp.tasks.first_of_month"],       # 1st of month
        "15 18 * * *": ["myapp.tasks.daily_6_15pm"],       # Daily 18:15
    }
}
```

**REQUIRED after changes:**
```bash
bench migrate
```

See [references/scheduler-events.md](references/scheduler-events.md) for complete cron syntax.

## frappe.enqueue API

### Basic Syntax

```python
frappe.enqueue(
    method,                      # Function or module path (REQUIRED)
    queue="default",             # "short", "default", "long"
    timeout=None,                # Override timeout (seconds)
    job_id=None,                 # v15: Unique ID for deduplication
    enqueue_after_commit=False,  # Wait for DB commit
    at_front=False,              # Priority placement
    on_success=None,             # Success callback
    on_failure=None,             # Failure callback
    **kwargs                     # Arguments for method
)
```

### Examples

```python
# Basic
frappe.enqueue('myapp.tasks.process', customer='CUST-001')

# With timeout on long queue
frappe.enqueue(
    'myapp.tasks.heavy_report',
    queue='long',
    timeout=3600,
    report_type='annual'
)

# With callbacks
frappe.enqueue(
    'myapp.tasks.risky_operation',
    on_success=lambda job, conn, result: notify_success(),
    on_failure=lambda job, conn, type, value, tb: log_failure()
)

# After database commit (for data integrity)
frappe.enqueue(
    'myapp.tasks.send_notification',
    enqueue_after_commit=True,
    user=frappe.session.user
)
```

See [references/enqueue-api.md](references/enqueue-api.md) for all parameters.

## frappe.enqueue_doc

Enqueue a controller method of a document:

```python
frappe.enqueue_doc(
    "Sales Invoice",
    "SINV-00001",
    "send_notification",
    queue="long",
    timeout=600,
    recipient="user@example.com"
)
```

## Queue Types

| Queue | Default Timeout | Usage |
|-------|-----------------|-------|
| `short` | 300s (5 min) | Quick tasks, UI responses |
| `default` | 300s (5 min) | Standard tasks |
| `long` | 1500s (25 min) | Heavy processing, imports |

See [references/queues.md](references/queues.md) for custom queue configuration.

## Job Deduplication

### v15+ (Recommended)

```python
from frappe.utils.background_jobs import is_job_enqueued

job_id = f"import::{self.name}"
if not is_job_enqueued(job_id):
    frappe.enqueue(
        'myapp.tasks.import_data',
        job_id=job_id,
        doc_name=self.name
    )
```

### v14 (Deprecated)

```python
# DO NOT USE IN NEW CODE
from frappe.core.page.background_jobs.background_jobs import get_info
enqueued = [d.get("job_name") for d in get_info()]
if self.name not in enqueued:
    frappe.enqueue(..., job_name=self.name)
```

## Error Handling

```python
def process_records(records):
    for record in records:
        try:
            process_single(record)
            frappe.db.commit()  # Commit per success
        except Exception:
            frappe.db.rollback()  # Rollback on error
            frappe.log_error(
                frappe.get_traceback(),
                f"Process Error: {record}"
            )
```

See [references/error-handling.md](references/error-handling.md) for patterns.

## Monitoring

- **RQ Worker**: Search > RQ Worker (worker status)
- **RQ Job**: Search > RQ Job (job status/errors)
- **bench doctor**: Scheduler status per site

```bash
bench doctor
```

See [references/monitoring.md](references/monitoring.md) for details.

## User Context

**IMPORTANT**: Scheduled jobs run as **Administrator**!

```python
def scheduled_task():
    print(frappe.session.user)  # "Administrator"
    
    # Explicitly set owner:
    doc = frappe.new_doc("ToDo")
    doc.owner = "specific.user@example.com"
    doc.insert(ignore_permissions=True)
```

## Best Practices

1. **ALWAYS** `bench migrate` after hooks.py scheduler_events changes
2. **USE** appropriate queue: short/default/long
3. **USE** `job_id` + `is_job_enqueued()` for deduplication (v15)
4. **IMPLEMENT** error handling with commit/rollback per record
5. **ENQUEUE** heavy tasks from scheduler events to long queue
6. **NEVER** blocking waits in web requests
7. **REMEMBER** that jobs run as Administrator

## Anti-Patterns

See [references/anti-patterns.md](references/anti-patterns.md) for mistakes to avoid:
- Heavy processing directly in scheduler callback
- No error handling (entire batch fails)
- Blocking wait on job completion
- Using `job_name` in v15+

## Complete Examples

See [references/examples.md](references/examples.md) for:
- Data import with progress tracking
- Email sending with retry logic
- Cleanup jobs with error recovery
- Report generation with notifications
