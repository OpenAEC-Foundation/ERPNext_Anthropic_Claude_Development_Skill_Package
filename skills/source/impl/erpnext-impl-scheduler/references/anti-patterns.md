# Scheduler & Background Jobs - Anti-Patterns

> Common mistakes and how to avoid them.

---

## Anti-Pattern 1: Passing Arguments to Scheduler Tasks

### ❌ Wrong

```python
# hooks.py
scheduler_events = {
    "daily": ["myapp.tasks.cleanup(days=30)"]  # Won't work!
}

# Or trying to pass in the function definition
def cleanup(days=30):
    ...
```

**Error**: Arguments are ignored; task may fail or use wrong values

### ✅ Correct

```python
# hooks.py
scheduler_events = {
    "daily": ["myapp.tasks.cleanup"]
}

# myapp/tasks.py
def cleanup():
    """Scheduler tasks receive NO arguments."""
    days = 30  # Hardcode or get from settings
    # Or:
    days = frappe.db.get_single_value("Cleanup Settings", "retention_days") or 30
```

### Rule

**Scheduler tasks CANNOT receive arguments.** Use hardcoded values, settings, or database lookups.

---

## Anti-Pattern 2: Forgetting to Migrate After hooks.py Changes

### ❌ Wrong

```python
# Add new scheduler event to hooks.py
scheduler_events = {
    "daily": ["myapp.tasks.new_task"]
}

# Restart bench and expect it to work
# bench restart
```

**Error**: Task never runs because it's not registered

### ✅ Correct

```bash
# ALWAYS migrate after hooks.py changes
bench --site sitename migrate

# Then optionally restart
bench restart
```

### Rule

**ALWAYS run `bench migrate` after ANY hooks.py change.** This registers scheduler events in the database.

---

## Anti-Pattern 3: Using Wrong Queue for Task Duration

### ❌ Wrong

```python
# 10-minute task in default queue (5 min timeout)
frappe.enqueue(
    "myapp.tasks.heavy_import",
    queue="default"  # Will timeout!
)

# Or quick task in long queue (wastes resources)
frappe.enqueue(
    "myapp.tasks.send_notification",
    queue="long"  # Overkill for 1-second task
)
```

**Error**: Task times out or wastes worker resources

### ✅ Correct

```python
# Match queue to task duration
# < 30 sec: short
frappe.enqueue("myapp.tasks.quick_task", queue="short")

# < 5 min: default
frappe.enqueue("myapp.tasks.medium_task", queue="default")

# 5-25 min: long
frappe.enqueue("myapp.tasks.heavy_task", queue="long")

# > 25 min: split into chunks!
```

### Rule

| Duration | Queue |
|----------|-------|
| < 30 sec | `short` |
| < 5 min | `default` |
| 5-25 min | `long` |
| > 25 min | Split task |

---

## Anti-Pattern 4: No Deduplication for User-Triggered Jobs

### ❌ Wrong

```python
@frappe.whitelist()
def start_export():
    # User clicks 5 times = 5 identical jobs!
    frappe.enqueue("myapp.tasks.export_data")
```

**Error**: Multiple identical jobs queue up, waste resources, may cause data issues

### ✅ Correct

```python
from frappe.utils.background_jobs import is_job_enqueued

@frappe.whitelist()
def start_export():
    job_id = f"export::{frappe.session.user}"
    
    if is_job_enqueued(job_id):
        return {"message": "Export already in progress"}
    
    frappe.enqueue(
        "myapp.tasks.export_data",
        job_id=job_id,
        user=frappe.session.user
    )
    return {"message": "Export started"}
```

### Rule

**Always deduplicate user-triggered background jobs** using `job_id` and `is_job_enqueued()`.

---

## Anti-Pattern 5: Committing After Every Record

### ❌ Wrong

```python
def process_records():
    records = get_all_records()  # 10,000 records
    
    for record in records:
        process(record)
        frappe.db.commit()  # 10,000 commits = SLOW!
```

**Error**: Extremely slow due to database overhead per commit

### ✅ Correct

```python
def process_records():
    records = get_all_records()
    
    for i, record in enumerate(records):
        process(record)
        
        # Commit every 100 records
        if i % 100 == 0:
            frappe.db.commit()
    
    # Final commit
    frappe.db.commit()
```

### Rule

**Commit in batches, not per record.** Every 100-500 records is typically optimal.

---

## Anti-Pattern 6: No Error Handling in Scheduler Tasks

### ❌ Wrong

```python
def sync_all_orders():
    orders = get_pending_orders()
    
    for order in orders:
        sync_to_external(order)  # If one fails, entire task fails!
```

**Error**: One failure stops all processing; partial data may be inconsistent

### ✅ Correct

```python
def sync_all_orders():
    orders = get_pending_orders()
    success = 0
    errors = 0
    
    for order in orders:
        try:
            sync_to_external(order)
            success += 1
            frappe.db.commit()  # Commit successful ones
        except Exception as e:
            errors += 1
            frappe.db.rollback()  # Rollback failed one
            frappe.log_error(
                f"Sync failed for {order}: {e}",
                "Order Sync Error"
            )
    
    frappe.logger("sync").info(f"Sync: {success} success, {errors} errors")
```

### Rule

**Always wrap record processing in try-except.** Log errors and continue with remaining records.

---

## Anti-Pattern 7: Assuming User Context in Scheduler Tasks

### ❌ Wrong

```python
def scheduled_task():
    # Creates document owned by Administrator!
    doc = frappe.get_doc({"doctype": "Task", "subject": "Auto-created"})
    doc.insert()
    
    # Permission check will use Administrator permissions!
    frappe.get_list("Private Doc")  # May return ALL records
```

**Error**: Wrong ownership, unexpected permission behavior

### ✅ Correct

```python
def scheduled_task():
    # Explicitly set user if needed
    frappe.set_user("system@example.com")
    
    # Or explicitly set owner
    doc = frappe.get_doc({
        "doctype": "Task",
        "subject": "Auto-created",
        "owner": "target_user@example.com"
    })
    doc.insert(ignore_permissions=True)
```

### Rule

**Scheduler tasks run as Administrator.** Explicitly set user context or owner when needed.

---

## Anti-Pattern 8: Long-Running Task in Short/Default Queue

### ❌ Wrong

```python
# hooks.py
scheduler_events = {
    "hourly": ["myapp.tasks.heavy_report"]  # Uses default queue!
}

# This will timeout after 5 minutes
def heavy_report():
    # 30-minute report generation
    ...
```

**Error**: Task times out, incomplete processing

### ✅ Correct

```python
# hooks.py
scheduler_events = {
    "hourly_long": ["myapp.tasks.heavy_report"]  # Uses long queue
}

# Or for user-triggered
frappe.enqueue(
    "myapp.tasks.heavy_report",
    queue="long",
    timeout=3600  # 1 hour
)
```

### Rule

**Use `*_long` scheduler events or `queue="long"` for tasks over 5 minutes.**

---

## Anti-Pattern 9: No Progress Feedback for User-Triggered Tasks

### ❌ Wrong

```python
@frappe.whitelist()
def start_import():
    frappe.enqueue("myapp.tasks.import_10000_records")
    return {"message": "Started"}
    # User has no idea what's happening for 10 minutes!
```

**Error**: Poor UX, user may restart task thinking it failed

### ✅ Correct

```python
def import_records(user):
    total = 10000
    
    for i, record in enumerate(records):
        process(record)
        
        if i % 100 == 0:
            frappe.publish_progress(
                percent=int((i / total) * 100),
                title="Importing records..."
            )
    
    frappe.publish_realtime(
        "msgprint",
        {"message": "Import complete!", "indicator": "green"},
        user=user
    )
```

### Rule

**Provide progress feedback for long user-triggered tasks** using `publish_progress` and `publish_realtime`.

---

## Anti-Pattern 10: Infinite Retry Without Limit

### ❌ Wrong

```python
def sync_with_retry(record):
    try:
        sync_external(record)
    except Exception:
        # Retry forever if external system is down!
        frappe.enqueue("myapp.tasks.sync_with_retry", record=record)
```

**Error**: Infinite loop if external system is permanently down

### ✅ Correct

```python
def sync_with_retry(record, attempt=1, max_attempts=3):
    try:
        sync_external(record)
    except Exception as e:
        if attempt < max_attempts:
            frappe.enqueue(
                "myapp.tasks.sync_with_retry",
                record=record,
                attempt=attempt + 1,
                max_attempts=max_attempts
            )
        else:
            frappe.log_error(
                f"Sync failed permanently: {record}",
                "Max Retries Exceeded"
            )
```

### Rule

**Always limit retry attempts.** Log permanently failing tasks for manual review.

---

## Anti-Pattern 11: Using "all" Event for Heavy Tasks

### ❌ Wrong

```python
# hooks.py
scheduler_events = {
    "all": ["myapp.tasks.sync_external"]  # Runs every 60 seconds!
}

def sync_external():
    # Takes 2 minutes to complete
    ...
```

**Error**: Task can't complete before next run, queue backup

### ✅ Correct

```python
# For tasks that take time, use appropriate frequency
scheduler_events = {
    "hourly": ["myapp.tasks.sync_external"]
}

# Or use cron for specific intervals
scheduler_events = {
    "cron": {
        "*/5 * * * *": ["myapp.tasks.sync_external"]  # Every 5 minutes
    }
}
```

### Rule

**"all" event is for quick tasks only (<60 seconds).** Use `hourly` or `cron` for longer tasks.

---

## Anti-Pattern 12: Not Using enqueue_after_commit

### ❌ Wrong

```python
def on_submit(self):
    # Job might start before this transaction commits!
    frappe.enqueue("myapp.tasks.process", doc_name=self.name)
```

**Error**: Background job may not find the document (not committed yet)

### ✅ Correct

```python
def on_submit(self):
    frappe.enqueue(
        "myapp.tasks.process",
        enqueue_after_commit=True,  # Wait for transaction to commit
        doc_name=self.name
    )
```

### Rule

**Use `enqueue_after_commit=True` when enqueueing from document events** to ensure data is available.

---

## Anti-Pattern 13: Ignoring Scheduler Status

### ❌ Wrong

```python
# Deploy and assume scheduler is working
# Never check if tasks are actually running
```

**Error**: Tasks silently fail, issues discovered too late

### ✅ Correct

```bash
# Regular health checks
bench --site sitename scheduler status

# Check for failed jobs
bench --site sitename show-failed-jobs

# Monitor in UI
# Setup > Scheduled Job Log
```

```python
# Add monitoring task
def scheduler_health_check():
    failed_count = frappe.db.count(
        "Scheduled Job Log",
        {"status": "Failed", "creation": [">=", frappe.utils.add_days(None, -1)]}
    )
    
    if failed_count > 10:
        alert_admin("Many scheduler failures!")
```

### Rule

**Actively monitor scheduler health.** Check Scheduled Job Log regularly.

---

## Anti-Pattern 14: Heavy Computation in Scheduler Event Handler

### ❌ Wrong

```python
# hooks.py
scheduler_events = {
    "daily": ["myapp.tasks.generate_all_reports"]
}

def generate_all_reports():
    # 2-hour task directly in scheduler event
    for report in get_all_reports():
        generate_report(report)  # Timeout!
```

**Error**: Scheduler event handler times out

### ✅ Correct

```python
# Scheduler event just enqueues the actual work
def generate_all_reports():
    """Scheduler event handler - enqueues actual work."""
    reports = get_all_reports()
    
    for report in reports:
        frappe.enqueue(
            "myapp.tasks.generate_single_report",
            queue="long",
            report=report
        )

def generate_single_report(report):
    """Actual work in background job."""
    # Heavy processing here
    ...
```

### Rule

**Scheduler events should be thin wrappers.** Enqueue heavy work to appropriate queues.

---

## Quick Reference: Anti-Pattern Summary

| Anti-Pattern | Fix |
|--------------|-----|
| Arguments to scheduler tasks | Use settings or hardcode |
| No migrate after hooks.py | Always `bench migrate` |
| Wrong queue for duration | Match queue to task time |
| No deduplication | Use `job_id` + `is_job_enqueued()` |
| Commit per record | Commit in batches |
| No error handling | Try-except per record |
| Assuming user context | `frappe.set_user()` or explicit owner |
| Long task in short queue | Use `*_long` or `queue="long"` |
| No progress feedback | `publish_progress()` |
| Infinite retry | Limit attempts |
| Heavy task in "all" | Use hourly or cron |
| No enqueue_after_commit | Add flag for doc events |
| No monitoring | Check Scheduled Job Log |
| Heavy computation in handler | Enqueue to background |
