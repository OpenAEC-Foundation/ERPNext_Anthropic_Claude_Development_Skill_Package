---
name: erpnext-impl-scheduler
description: "Implementation workflows and decision trees for Frappe scheduler events and background jobs. Use when determining HOW to implement scheduled tasks, background processing, cron jobs, job queues, or async operations. Covers scheduler_events in hooks.py, frappe.enqueue patterns, job deduplication, error handling, and monitoring. V14/V15/V16 compatible with version differences noted. Triggers: schedule task, background job, cron job, async processing, queue task, periodic task, hourly/daily/weekly task."
---

# ERPNext Scheduler & Background Jobs - Implementation

This skill helps you determine HOW to implement scheduled tasks and background processing. For exact syntax, see `erpnext-syntax-scheduler`.

**Version**: v14/v15/v16 compatible (with version differences noted)

## Main Decision: What Are You Trying to Do?

```
┌─────────────────────────────────────────────────────────────────────────┐
│ WHAT DO YOU WANT TO ACHIEVE?                                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ ► Run task periodically (hourly, daily, etc.)?                          │
│   └── scheduler_events in hooks.py                                      │
│                                                                         │
│ ► Run task at specific time (9am weekdays, 1st of month)?               │
│   └── cron scheduler_events                                             │
│                                                                         │
│ ► Offload heavy processing from user request?                           │
│   └── frappe.enqueue() in your code                                     │
│                                                                         │
│ ► Process multiple records asynchronously?                              │
│   └── frappe.enqueue() with batch pattern                               │
│                                                                         │
│ ► Ensure task runs only once (no duplicates)?                           │
│   └── Job deduplication with job_id                                     │
│                                                                         │
│ ► Handle long-running operations (>5 minutes)?                          │
│   └── long queue + chunked processing                                   │
│                                                                         │
│ ► Notify user when background task completes?                           │
│   └── Callbacks + frappe.publish_realtime                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Decision Tree: Scheduler Event vs frappe.enqueue

```
WHEN SHOULD THE TASK RUN?
│
├─► On a fixed schedule (hourly, daily, etc.)?
│   └─► scheduler_events in hooks.py
│       - Runs automatically by scheduler
│       - No user trigger needed
│       - Good for: cleanup, sync, reports
│
├─► Triggered by user action?
│   └─► frappe.enqueue() in controller/Server Script
│       - Called from your code
│       - Runs in background
│       - Good for: imports, exports, heavy calculations
│
├─► Both scheduled AND user-triggered?
│   └─► Create task function, call from both:
│       - scheduler_events → calls your function
│       - Button → frappe.enqueue → same function
│
└─► One-time task (not recurring)?
    └─► frappe.enqueue() directly
        - No hooks.py entry needed
```

---

## Decision Tree: Which Scheduler Event Type?

```
HOW OFTEN SHOULD IT RUN?
│
├─► Very frequently (near real-time)?
│   └─► "all" event
│       - v14: every ~4 minutes
│       - v15/v16: every ~60 seconds
│       ⚠️ Task MUST complete in <60 seconds!
│
├─► Hourly?
│   │
│   │ HOW LONG DOES IT TAKE?
│   ├─► < 5 minutes → "hourly"
│   └─► 5-25 minutes → "hourly_long"
│
├─► Daily?
│   │
│   │ HOW LONG DOES IT TAKE?
│   ├─► < 5 minutes → "daily"
│   └─► 5-25 minutes → "daily_long"
│
├─► Weekly?
│   │
│   │ HOW LONG DOES IT TAKE?
│   ├─► < 5 minutes → "weekly"
│   └─► 5-25 minutes → "weekly_long"
│
├─► Monthly?
│   │
│   │ HOW LONG DOES IT TAKE?
│   ├─► < 5 minutes → "monthly"
│   └─► 5-25 minutes → "monthly_long"
│
└─► Specific time/day?
    └─► "cron" with cron expression
        - "0 9 * * 1-5" = 9am weekdays
        - "0 0 1 * *" = midnight 1st of month
        - "*/15 * * * *" = every 15 minutes
```

---

## Decision Tree: Which Queue?

```
HOW LONG WILL THE TASK RUN?
│
├─► < 30 seconds (quick response needed)?
│   └─► "short" queue (5 min timeout)
│       - UI button responses
│       - Quick API calls
│       - Small record updates
│
├─► < 5 minutes (standard processing)?
│   └─► "default" queue (5 min timeout)
│       - Most tasks
│       - Scheduler events (non-long)
│       - Medium record sets
│
├─► 5-25 minutes (heavy processing)?
│   └─► "long" queue (25 min timeout)
│       - Large imports/exports
│       - Report generation
│       - Bulk operations
│
└─► > 25 minutes?
    └─► Split into chunks
        - Process in batches
        - Enqueue next batch from current
        - Track progress in database
```

---

## Implementation Workflow: Scheduled Task (Basic)

### Step 1: Create Task Module

```python
# myapp/tasks.py
import frappe

def daily_cleanup():
    """
    Clean up old logs daily.
    
    IMPORTANT: Scheduler tasks receive NO arguments!
    IMPORTANT: Runs as Administrator user!
    """
    cutoff = frappe.utils.add_days(None, -30)
    
    old_logs = frappe.get_all(
        "Error Log",
        filters={"creation": ["<", cutoff]},
        pluck="name",
        limit=1000  # Process in batches
    )
    
    for name in old_logs:
        frappe.delete_doc("Error Log", name, ignore_permissions=True)
    
    frappe.db.commit()
    
    frappe.logger().info(f"Cleaned up {len(old_logs)} old logs")
```

### Step 2: Register in hooks.py

```python
# myapp/hooks.py
scheduler_events = {
    "daily": [
        "myapp.tasks.daily_cleanup"
    ]
}
```

### Step 3: Deploy

```bash
bench --site sitename migrate  # REQUIRED after hooks.py change!
bench --site sitename scheduler enable
```

### Step 4: Verify

```bash
# Check scheduler status
bench --site sitename scheduler status

# Check in UI
# Setup > Scheduled Job Type - should show your task
# Scheduled Job Log - shows execution history
```

---

## Implementation Workflow: Cron Scheduled Task

### Step 1: Create Task

```python
# myapp/tasks.py
import frappe

def weekday_morning_report():
    """Send report at 9am on weekdays."""
    report = generate_daily_report()
    
    recipients = frappe.get_all(
        "User",
        filters={"user_type": "System User", "enabled": 1},
        pluck="email"
    )
    
    frappe.sendmail(
        recipients=recipients,
        subject=f"Daily Report - {frappe.utils.nowdate()}",
        message=report
    )
```

### Step 2: Register with Cron Expression

```python
# myapp/hooks.py
scheduler_events = {
    "cron": {
        # At 9:00 AM, Monday through Friday
        "0 9 * * 1-5": ["myapp.tasks.weekday_morning_report"],
        
        # At midnight on the 1st of each month
        "0 0 1 * *": ["myapp.tasks.monthly_summary"],
        
        # Every 15 minutes
        "*/15 * * * *": ["myapp.tasks.sync_external_system"]
    }
}
```

### Cron Expression Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday = 0)
│ │ │ │ │
* * * * *
```

| Expression | Meaning |
|------------|---------|
| `0 9 * * *` | 9:00 AM daily |
| `0 9 * * 1-5` | 9:00 AM weekdays |
| `0 0 * * 0` | Midnight on Sunday |
| `0 0 1 * *` | Midnight 1st of month |
| `*/15 * * * *` | Every 15 minutes |
| `0 */2 * * *` | Every 2 hours |
| `30 4 * * *` | 4:30 AM daily |

---

## Implementation Workflow: Background Job (User-Triggered)

### Step 1: Create Task Function

```python
# myapp/tasks.py
import frappe

def import_large_file(file_url, doctype, user):
    """
    Import records from file.
    
    Args passed via frappe.enqueue kwargs.
    """
    # Set user context (jobs run as Administrator)
    frappe.set_user(user)
    
    try:
        records = parse_file(file_url)
        total = len(records)
        
        for i, record in enumerate(records):
            try:
                doc = frappe.get_doc({"doctype": doctype, **record})
                doc.insert()
                
                # Commit per record for large imports
                if i % 100 == 0:
                    frappe.db.commit()
                    
                    # Update progress (optional)
                    frappe.publish_progress(
                        percent=int((i / total) * 100),
                        title="Importing records..."
                    )
                    
            except Exception as e:
                frappe.log_error(f"Import error row {i}: {e}")
                continue
        
        frappe.db.commit()
        
        # Notify user
        frappe.publish_realtime(
            "msgprint",
            {"message": f"Import complete! {total} records processed."},
            user=user
        )
        
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Import Failed")
        frappe.publish_realtime(
            "msgprint",
            {"message": "Import failed. Check Error Log."},
            user=user
        )
```

### Step 2: Enqueue from Controller/API

```python
# myapp/api.py
import frappe

@frappe.whitelist()
def start_import(file_url, doctype):
    """API endpoint to start import."""
    frappe.enqueue(
        "myapp.tasks.import_large_file",
        queue="long",
        timeout=3600,  # 1 hour
        file_url=file_url,
        doctype=doctype,
        user=frappe.session.user
    )
    
    return {"status": "Import started in background"}
```

### Step 3: Call from Client

```javascript
// In Client Script or custom page
frappe.call({
    method: "myapp.api.start_import",
    args: {
        file_url: "/files/data.csv",
        doctype: "Customer"
    },
    callback: function(r) {
        frappe.msgprint("Import started! You'll be notified when complete.");
    }
});
```

---

## Implementation Workflow: Job Deduplication

### Problem: Prevent Duplicate Jobs

```python
# ❌ Without deduplication - multiple clicks = multiple jobs
@frappe.whitelist()
def sync_inventory():
    frappe.enqueue("myapp.tasks.sync_all_inventory")
    # User clicks 5 times = 5 identical jobs queued!
```

### Solution: Use job_id (v15+)

```python
# myapp/api.py
import frappe
from frappe.utils.background_jobs import is_job_enqueued

@frappe.whitelist()
def sync_inventory():
    """Start inventory sync if not already running."""
    job_id = "sync_inventory"
    
    if is_job_enqueued(job_id):
        return {"status": "Sync already in progress"}
    
    frappe.enqueue(
        "myapp.tasks.sync_all_inventory",
        queue="long",
        job_id=job_id  # Unique identifier
    )
    
    return {"status": "Sync started"}
```

### Document-Specific Deduplication

```python
@frappe.whitelist()
def process_order(order_name):
    """Process order - prevent duplicate processing."""
    job_id = f"process_order::{order_name}"
    
    if is_job_enqueued(job_id):
        frappe.throw("This order is already being processed")
    
    frappe.enqueue(
        "myapp.tasks.process_single_order",
        queue="default",
        job_id=job_id,
        order_name=order_name
    )
```

### v14 Compatibility

```python
# For v14 (deprecated pattern)
def enqueue_with_dedup_v14(method, job_name, **kwargs):
    from frappe.core.page.background_jobs.background_jobs import get_info
    
    enqueued_jobs = [d.get("job_name") for d in get_info()]
    
    if job_name not in enqueued_jobs:
        frappe.enqueue(method, job_name=job_name, **kwargs)
        return True
    return False
```

---

## Implementation Workflow: Long-Running Task with Progress

### Step 1: Create Chunked Task

```python
# myapp/tasks.py
import frappe

def process_large_dataset(offset=0, batch_size=100, total=None):
    """
    Process records in chunks, enqueue next batch.
    """
    if total is None:
        total = frappe.db.count("Sales Invoice", {"status": "Draft"})
    
    records = frappe.get_all(
        "Sales Invoice",
        filters={"status": "Draft"},
        fields=["name"],
        limit_start=offset,
        limit_page_length=batch_size
    )
    
    if not records:
        # All done
        frappe.publish_realtime(
            "msgprint",
            {"message": f"Processing complete! {total} records processed."}
        )
        return
    
    # Process this batch
    for record in records:
        process_single_invoice(record.name)
    
    frappe.db.commit()
    
    # Update progress
    processed = offset + len(records)
    frappe.publish_progress(
        percent=int((processed / total) * 100),
        title=f"Processing invoices... ({processed}/{total})"
    )
    
    # Enqueue next batch
    frappe.enqueue(
        "myapp.tasks.process_large_dataset",
        queue="long",
        offset=offset + batch_size,
        batch_size=batch_size,
        total=total
    )
```

### Step 2: Start Processing

```python
@frappe.whitelist()
def start_batch_processing():
    frappe.enqueue(
        "myapp.tasks.process_large_dataset",
        queue="long",
        offset=0,
        batch_size=100
    )
    return {"status": "Processing started"}
```

---

## Implementation Workflow: Error Handling

### Pattern: Robust Task with Logging

```python
# myapp/tasks.py
import frappe

def robust_sync_task():
    """
    Sync with external system - handles errors gracefully.
    """
    success_count = 0
    error_count = 0
    
    records = get_records_to_sync()
    
    for record in records:
        try:
            sync_single_record(record)
            success_count += 1
            
            # Commit successful records
            frappe.db.commit()
            
        except Exception as e:
            error_count += 1
            
            # Rollback failed record
            frappe.db.rollback()
            
            # Log error with context
            frappe.log_error(
                message=frappe.get_traceback(),
                title=f"Sync Error: {record.get('name')}"
            )
            
            # Continue with next record
            continue
    
    # Final summary log
    frappe.logger().info(
        f"Sync completed: {success_count} success, {error_count} errors"
    )
    
    # Alert if too many errors
    if error_count > len(records) * 0.1:  # >10% failure
        frappe.sendmail(
            recipients=["admin@example.com"],
            subject="Sync Task: High Error Rate",
            message=f"Sync had {error_count} errors out of {len(records)} records"
        )
```

### Pattern: Retry on Failure

```python
def task_with_retry(record_name, attempt=1, max_attempts=3):
    """Retry task on failure."""
    try:
        process_record(record_name)
        frappe.db.commit()
        
    except Exception as e:
        frappe.db.rollback()
        
        if attempt < max_attempts:
            # Retry with exponential backoff
            delay = 60 * (2 ** attempt)  # 2min, 4min, 8min
            
            frappe.enqueue(
                "myapp.tasks.task_with_retry",
                queue="default",
                enqueue_after_commit=True,
                record_name=record_name,
                attempt=attempt + 1,
                max_attempts=max_attempts
            )
            
            frappe.logger().warning(
                f"Retry {attempt + 1}/{max_attempts} scheduled for {record_name}"
            )
        else:
            frappe.log_error(
                f"Task failed after {max_attempts} attempts: {record_name}"
            )
```

---

## Implementation Workflow: Callbacks

### Notify User on Completion

```python
# myapp/tasks.py
import frappe

def on_export_success(job, connection, result, *args, **kwargs):
    """Called when export job succeeds."""
    frappe.publish_realtime(
        "eval_js",
        'frappe.show_alert({message: "Export complete!", indicator: "green"})',
        user=kwargs.get("user")
    )

def on_export_failure(job, connection, type, value, traceback):
    """Called when export job fails."""
    frappe.log_error(f"Export failed: {value}", "Export Error")
    frappe.publish_realtime(
        "eval_js",
        'frappe.show_alert({message: "Export failed!", indicator: "red"})'
    )

def start_export(user):
    frappe.enqueue(
        "myapp.tasks.run_export",
        queue="long",
        on_success=on_export_success,
        on_failure=on_export_failure,
        user=user
    )
```

---

## Quick Reference: Scheduler Configuration

### Enable/Disable Scheduler

```bash
# Enable
bench --site sitename scheduler enable

# Disable
bench --site sitename scheduler disable

# Check status
bench --site sitename scheduler status

# Run scheduler manually (for testing)
bench --site sitename execute frappe.utils.scheduler.enqueue_events
```

### Check Scheduler Health

```bash
# Overall health check
bench doctor

# Worker status
bench --site sitename show-pending-jobs
```

---

## Critical Rules

### 1. ALWAYS migrate after hooks.py changes

```bash
bench --site sitename migrate
```

### 2. Scheduler tasks receive NO arguments

```python
# ❌ WRONG
scheduler_events = {
    "daily": ["myapp.tasks.cleanup(days=30)"]  # Won't work!
}

# ✅ CORRECT
def cleanup():
    days = 30  # Hardcoded or from settings
```

### 3. Jobs run as Administrator

```python
def my_task():
    # frappe.session.user == "Administrator"
    
    # Set specific user if needed:
    frappe.set_user("user@example.com")
```

### 4. Commit after batch, not per record

```python
# ❌ SLOW - commit per record
for record in records:
    process(record)
    frappe.db.commit()

# ✅ FAST - commit per batch
for i, record in enumerate(records):
    process(record)
    if i % 100 == 0:
        frappe.db.commit()
frappe.db.commit()  # Final commit
```

### 5. Use correct queue for task duration

```python
# < 5 min
frappe.enqueue(..., queue="default")

# 5-25 min
frappe.enqueue(..., queue="long")

# > 25 min
# Split into chunks!
```

---

## Version Differences

| Feature | V14 | V15 | V16 |
|---------|:---:|:---:|:---:|
| Scheduler tick | 4 min | 60 sec | 60 sec |
| Deduplication | `job_name` | `job_id` | `job_id` |
| `is_job_enqueued()` | ❌ | ✅ | ✅ |
| Config key | `scheduler_interval` | `scheduler_tick_interval` | `scheduler_tick_interval` |

---

## Reference Files

| File | Contents |
|------|----------|
| [decision-tree.md](references/decision-tree.md) | Complete task type selection flowcharts |
| [workflows.md](references/workflows.md) | Step-by-step implementation patterns |
| [examples.md](references/examples.md) | Complete working examples |
| [anti-patterns.md](references/anti-patterns.md) | Common mistakes to avoid |
