# Scheduler & Background Jobs - Complete Decision Trees

> Detailed flowcharts for selecting the right scheduling approach.

---

## Decision Tree: Task Type Selection

```
WHAT TRIGGERS THE TASK?
│
├─► Time-based (runs automatically)?
│   │
│   │ IS IT A FIXED SCHEDULE?
│   │
│   ├─► Yes (hourly, daily, weekly, monthly)
│   │   └─► scheduler_events in hooks.py
│   │       │
│   │       │ WHICH EVENT TYPE?
│   │       │
│   │       ├─► Every scheduler tick
│   │       │   └─► "all"
│   │       │       ⚠️ Must complete in <60 seconds
│   │       │
│   │       ├─► Once per hour
│   │       │   ├─► < 5 min → "hourly"
│   │       │   └─► 5-25 min → "hourly_long"
│   │       │
│   │       ├─► Once per day
│   │       │   ├─► < 5 min → "daily"
│   │       │   └─► 5-25 min → "daily_long"
│   │       │
│   │       ├─► Once per week
│   │       │   ├─► < 5 min → "weekly"
│   │       │   └─► 5-25 min → "weekly_long"
│   │       │
│   │       └─► Once per month
│   │           ├─► < 5 min → "monthly"
│   │           └─► 5-25 min → "monthly_long"
│   │
│   └─► Specific time/day?
│       └─► cron scheduler_events
│           - "0 9 * * 1-5" = 9am weekdays
│           - "0 0 1 * *" = 1st of month midnight
│           - "*/30 * * * *" = every 30 minutes
│
├─► User action (button click, form submit)?
│   └─► frappe.enqueue() in your code
│       │
│       │ HOW HEAVY IS THE TASK?
│       │
│       ├─► Quick (<30s) → queue="short"
│       ├─► Medium (<5min) → queue="default"
│       └─► Heavy (5-25min) → queue="long"
│
├─► System event (doc save, submit)?
│   │
│   │ SHOULD IT BLOCK THE USER?
│   │
│   ├─► No (heavy processing)
│   │   └─► frappe.enqueue() from doc_event/controller
│   │
│   └─► Yes (quick, must complete before response)
│       └─► Direct execution in controller
│
└─► One-time task (run once, not recurring)?
    └─► frappe.enqueue() directly
        - No hooks.py needed
        - Can be called from console or script
```

---

## Decision Tree: Queue Selection

```
HOW LONG WILL THE TASK RUN?
│
├─► < 30 seconds?
│   │
│   │ IS QUICK RESPONSE NEEDED?
│   │
│   ├─► Yes (UI waiting)
│   │   └─► queue="short" (5 min timeout)
│   │       - Button callbacks
│   │       - Quick validations
│   │       - Small updates
│   │
│   └─► No (can wait)
│       └─► queue="default" (5 min timeout)
│
├─► 30 seconds - 5 minutes?
│   └─► queue="default" (5 min timeout)
│       - Most common tasks
│       - Standard scheduler events
│       - Medium datasets
│
├─► 5 - 25 minutes?
│   └─► queue="long" (25 min timeout)
│       - Large imports/exports
│       - Report generation
│       - Bulk operations
│       - Use *_long scheduler events
│
└─► > 25 minutes?
    └─► MUST split into chunks
        │
        │ CHUNKING STRATEGY:
        │
        ├─► Process batch, enqueue next batch
        │   - Self-chaining pattern
        │   - Track offset in arguments
        │
        ├─► Split by date range
        │   - Process one month at a time
        │   - Enqueue next month when done
        │
        └─► Split by record count
            - Process 1000 records per job
            - Use limit_start/limit_page_length
```

---

## Decision Tree: Deduplication Strategy

```
CAN DUPLICATE JOBS CAUSE PROBLEMS?
│
├─► Yes (data corruption, duplicate processing)?
│   │
│   │ FRAPPE VERSION?
│   │
│   ├─► V15+ (recommended)
│   │   └─► Use job_id + is_job_enqueued()
│   │       ```python
│   │       from frappe.utils.background_jobs import is_job_enqueued
│   │       
│   │       job_id = f"task::{unique_key}"
│   │       if not is_job_enqueued(job_id):
│   │           frappe.enqueue(..., job_id=job_id)
│   │       ```
│   │
│   └─► V14 (legacy)
│       └─► Use job_name + manual check
│           ```python
│           from frappe.core.page.background_jobs.background_jobs import get_info
│           enqueued = [d.get("job_name") for d in get_info()]
│           if name not in enqueued:
│               frappe.enqueue(..., job_name=name)
│           ```
│
├─► No (idempotent operation)?
│   └─► No deduplication needed
│       - Safe to run multiple times
│       - Each run produces same result
│
└─► Partially (some steps need protection)?
    └─► Deduplication at specific points
        - Dedup at enqueue time
        - Also check at execution start
        - Use database flags for critical sections
```

---

## Decision Tree: Error Handling Strategy

```
WHAT HAPPENS IF THE TASK FAILS?
│
├─► Single record processing?
│   │
│   │ IS IT OKAY TO SKIP FAILURES?
│   │
│   ├─► Yes (log and continue)
│   │   └─► Try-except per record
│   │       - Log error with context
│   │       - Continue to next record
│   │       - Commit successful records
│   │
│   └─► No (must process all or nothing)
│       └─► Transaction-based
│           - Process all in try block
│           - Rollback entire batch on error
│           - Retry or alert on failure
│
├─► External API call?
│   │
│   │ IS RETRY APPROPRIATE?
│   │
│   ├─► Yes (transient errors likely)
│   │   └─► Retry pattern with backoff
│   │       - Track attempt count
│   │       - Exponential delay
│   │       - Max retry limit
│   │
│   └─► No (permanent failure likely)
│       └─► Fail fast, log, alert
│
├─► Critical business process?
│   └─► Alert on failure
│       - Send email to admin
│       - Create ToDo/Issue
│       - Log with high visibility
│
└─► Non-critical cleanup?
    └─► Log and ignore
        - Just log error
        - Continue processing
        - Review logs periodically
```

---

## Decision Tree: Progress Reporting

```
SHOULD USER SEE PROGRESS?
│
├─► User-triggered task?
│   │
│   │ HOW LONG WILL IT TAKE?
│   │
│   ├─► < 10 seconds
│   │   └─► No progress needed
│   │       - Just show "Processing..."
│   │       - Show result when done
│   │
│   ├─► 10 seconds - 5 minutes
│   │   └─► Progress bar
│   │       ```python
│   │       frappe.publish_progress(
│   │           percent=50,
│   │           title="Processing..."
│   │       )
│   │       ```
│   │
│   └─► > 5 minutes
│       └─► Progress + notification on complete
│           - Progress bar during
│           - Email/realtime alert when done
│           - Link to results
│
├─► Scheduled task?
│   │
│   │ IS IT CRITICAL?
│   │
│   ├─► Yes (must know status)
│   │   └─► Log + optional alert
│   │       - Scheduled Job Log (automatic)
│   │       - Email summary for critical tasks
│   │
│   └─► No (routine maintenance)
│       └─► Scheduled Job Log only
│           - Automatic by scheduler
│           - Review periodically
│
└─► Background task (no user watching)?
    └─► Log only
        - frappe.logger().info()
        - Error Log for failures
```

---

## Decision Tree: User Context

```
WHO SHOULD THE TASK RUN AS?
│
├─► Scheduled task?
│   └─► Runs as Administrator (default)
│       │
│       │ NEED SPECIFIC USER CONTEXT?
│       │
│       ├─► No (system operations)
│       │   └─► Leave as Administrator
│       │       - Full permissions
│       │       - Can access everything
│       │
│       └─► Yes (user-specific data)
│           └─► Set user explicitly
│               ```python
│               def scheduled_task():
│                   frappe.set_user("user@example.com")
│                   # Now runs as that user
│               ```
│
├─► User-triggered task?
│   │
│   │ SHOULD IT USE USER'S PERMISSIONS?
│   │
│   ├─► Yes (respect permissions)
│   │   └─► Pass user, set in task
│   │       ```python
│   │       frappe.enqueue(..., user=frappe.session.user)
│   │       
│   │       def task(user):
│   │           frappe.set_user(user)
│   │       ```
│   │
│   └─► No (needs elevated permissions)
│       └─► Run as Administrator (default)
│           - Use ignore_permissions=True
│           - Log original user for audit
│
└─► System event task?
    └─► Consider context carefully
        - May need original user for audit
        - May need Administrator for access
        - Document which context is used
```

---

## Decision Tree: Monitoring Needs

```
HOW CRITICAL IS THE TASK?
│
├─► Business-critical (payments, invoices)?
│   └─► Full monitoring
│       - Scheduled Job Log (automatic)
│       - Custom success/failure logging
│       - Email alerts on failure
│       - Dashboard or report for status
│
├─► Important (sync, reports)?
│   └─► Standard monitoring
│       - Scheduled Job Log
│       - Error Log for failures
│       - Periodic manual review
│
├─► Routine (cleanup, maintenance)?
│   └─► Basic monitoring
│       - Scheduled Job Log only
│       - Review if problems reported
│
└─► Development/testing?
    └─► Debug logging
        - frappe.logger().debug()
        - Console output
        - Temporary, remove in production
```

---

## Quick Reference: Decision Summary

| Scenario | Solution |
|----------|----------|
| Daily cleanup | `scheduler_events["daily"]` |
| 9am weekday email | `scheduler_events["cron"]["0 9 * * 1-5"]` |
| User clicks "Export" | `frappe.enqueue(..., queue="long")` |
| Prevent duplicate jobs | `job_id` + `is_job_enqueued()` |
| Task > 25 min | Split into batches |
| Task fails | Try-except + log + optional retry |
| User needs progress | `frappe.publish_progress()` |
| Need user permissions | `frappe.set_user(user)` in task |
