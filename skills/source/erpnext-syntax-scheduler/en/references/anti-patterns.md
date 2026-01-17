# Anti-Patterns: What to Avoid

## ❌ No Error Handling

### Wrong

```python
def process_all(records):
    for record in records:
        process_single(record)  # One failure stops EVERYTHING
```

### Correct

```python
def process_all(records):
    for record in records:
        try:
            process_single(record)
            frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            frappe.log_error(
                frappe.get_traceback(),
                f"Process failed: {record}"
            )
```

---

## ❌ Heavy Processing Directly in Scheduler Event

### Wrong

```python
# hooks.py
scheduler_events = {
    "all": ["myapp.tasks.process_millions_of_records"]
}

def process_millions_of_records():
    # WRONG - blocks scheduler tick
    for record in frappe.get_all("BigTable"):
        heavy_operation(record)
```

### Correct

```python
# hooks.py
scheduler_events = {
    "all": ["myapp.tasks.trigger_processing"]
}

def trigger_processing():
    # Scheduler only triggers, enqueue does the work
    frappe.enqueue(
        "myapp.tasks.process_millions_of_records",
        queue="long",
        timeout=3600
    )
```

---

## ❌ Forgetting bench migrate

### Wrong

```python
# hooks.py modified
scheduler_events = {
    "hourly": ["myapp.tasks.new_task"]  # Newly added
}

# WRONG - forgot bench migrate
# New task will NOT be executed!
```

### Correct

```bash
# After EVERY change to hooks.py scheduler_events:
bench migrate
```

---

## ❌ Assumptions About Execution Order

### Wrong

```python
def task_a():
    create_data()

def task_b():
    # WRONG - assumes task_a is finished first
    process_data()  # Data may not exist yet!

# hooks.py
scheduler_events = {
    "hourly": ["myapp.task_a", "myapp.task_b"]
}
```

### Correct

```python
def task_a():
    create_data()
    # Explicitly trigger next step
    frappe.enqueue(
        "myapp.task_b",
        enqueue_after_commit=True
    )

def task_b():
    if not data_exists():
        return  # Graceful handling
    process_data()
```

---

## ❌ No User Context Awareness

### Wrong

```python
def scheduled_task():
    doc = frappe.new_doc("ToDo")
    doc.allocated_to = frappe.session.user  # = Administrator!
    doc.insert()
```

### Correct

```python
def scheduled_task():
    # Scheduler runs as Administrator
    doc = frappe.new_doc("ToDo")
    doc.allocated_to = "specific.user@example.com"  # Explicit
    doc.owner = "specific.user@example.com"
    doc.insert(ignore_permissions=True)
```

---

## ❌ Synchronous Execution in Web Request

### Wrong

```python
@frappe.whitelist()
def api_endpoint():
    heavy_processing()  # Blocks user for 5+ minutes
    return "Done"
```

### Correct

```python
@frappe.whitelist()
def api_endpoint():
    frappe.enqueue(
        "myapp.heavy_processing",
        queue="long"
    )
    return "Processing started"
```

---

## ❌ Blocking Wait for Job Completion

### Wrong

```python
import time

@frappe.whitelist()
def start_and_wait():
    job = frappe.enqueue("myapp.heavy_task")
    
    # WRONG - blocks web request
    while job.get_status() != "finished":
        time.sleep(1)
    
    return "Done"
```

### Correct

```python
@frappe.whitelist()
def start_task():
    frappe.enqueue(
        "myapp.heavy_task",
        on_success=lambda j,c,r: frappe.publish_realtime(
            "task_done",
            {"result": r},
            user=frappe.session.user
        )
    )
    return "Started - you will be notified"
```

---

## ❌ Using job_name (v15 Deprecated)

### Wrong

```python
# v14 pattern - DO NOT USE in v15
frappe.enqueue(
    "myapp.tasks.process",
    job_name="my-unique-job"
)
```

### Correct

```python
# v15+ pattern
from frappe.utils.background_jobs import is_job_enqueued

job_id = "my-unique-job"
if not is_job_enqueued(job_id):
    frappe.enqueue(
        "myapp.tasks.process",
        job_id=job_id
    )
```

---

## ❌ Infinite Retry Without Backoff

### Wrong

```python
def task_with_retry():
    try:
        external_api()
    except Exception:
        # WRONG - immediate retry without delay
        frappe.enqueue("myapp.task_with_retry")
```

### Correct

```python
def task_with_retry(retry_count=0):
    try:
        external_api()
    except Exception:
        if retry_count >= 3:
            frappe.log_error("Max retries exceeded")
            return
        
        # Exponential backoff
        delay = 2 ** retry_count  # 1, 2, 4 minutes
        
        frappe.enqueue(
            "myapp.task_with_retry",
            retry_count=retry_count + 1
        )
```

---

## ❌ Wrong Queue for Task Duration

### Wrong

```python
# Task takes 30 minutes but uses short queue
frappe.enqueue(
    "myapp.tasks.long_running_task",
    queue="short"  # Timeout after 5 min!
)
```

### Correct

```python
frappe.enqueue(
    "myapp.tasks.long_running_task",
    queue="long",
    timeout=2400  # 40 minutes
)
```

---

## ❌ No Commit Per Record

### Wrong

```python
def process_batch(records):
    for record in records:
        update_record(record)
    
    frappe.db.commit()  # One failure = everything lost
```

### Correct

```python
def process_batch(records):
    for record in records:
        try:
            update_record(record)
            frappe.db.commit()  # Commit per success
        except Exception:
            frappe.db.rollback()
            frappe.log_error()
```

---

## Summary: Best Practices

1. **ALWAYS** error handling with commit/rollback per record
2. **ALWAYS** `bench migrate` after hooks.py changes
3. **USE** `job_id` + `is_job_enqueued()` for deduplication (v15)
4. **CHOOSE** correct queue: short/default/long
5. **ENQUEUE** heavy tasks from scheduler events
6. **NEVER** blocking waits in web requests
7. **REMEMBER** that jobs run as Administrator
8. **IMPLEMENT** retry with exponential backoff
