# Anti-Patterns Reference

Common mistakes and how to avoid them.

## ❌ Heavy Processing in Scheduler Callback

### Wrong

```python
# hooks.py - WRONG!
scheduler_events = {
    "all": ["myapp.tasks.process_millions_of_records"]
}

# tasks.py
def process_millions_of_records():
    # This blocks the scheduler!
    records = frappe.get_all("Item", limit=0)  # Million records
    for record in records:
        heavy_processing(record)
```

### Correct

```python
# hooks.py
scheduler_events = {
    "all": ["myapp.tasks.check_and_enqueue"]
}

# tasks.py
def check_and_enqueue():
    """Light check, enqueue heavy work."""
    if needs_processing():
        frappe.enqueue(
            'myapp.tasks.process_records',
            queue='long',
            timeout=3600
        )

def process_records():
    """Heavy processing on long queue."""
    records = frappe.get_all("Item", limit=0)
    for record in records:
        heavy_processing(record)
```

---

## ❌ No Error Handling

### Wrong

```python
def process_all(records):
    # WRONG - one error stops everything
    for r in records:
        process(r)  # Exception = entire batch fails
    frappe.db.commit()
```

### Correct

```python
def process_all(records):
    for r in records:
        try:
            process(r)
            frappe.db.commit()  # Commit per success
        except Exception:
            frappe.db.rollback()
            frappe.log_error(
                frappe.get_traceback(),
                f"Process Error: {r}"
            )
```

---

## ❌ Forgetting bench migrate

### Wrong

```python
# hooks.py - modified
scheduler_events = {
    "hourly": ["myapp.tasks.new_task"]  # Newly added
}

# Forgot: bench migrate
# New task will NOT run!
```

### Correct

```bash
# After EVERY change in hooks.py scheduler_events:
bench migrate
```

---

## ❌ Assumptions About Execution Order

### Wrong

```python
def task_a():
    create_data()

def task_b():
    # WRONG - assumes task_a finished first
    process_data()  # Data might not exist yet!

# hooks.py
scheduler_events = {
    "hourly": ["myapp.task_a", "myapp.task_b"]
}
```

### Correct

```python
def task_a():
    create_data()
    # Explicitly enqueue next step
    frappe.enqueue(
        'myapp.task_b',
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
    # WRONG - assumption about session user
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
    # WRONG - blocks user for 5+ minutes
    heavy_processing()
    return "Done"
```

### Correct

```python
@frappe.whitelist()
def api_endpoint():
    frappe.enqueue(
        'myapp.heavy_processing',
        queue='long'
    )
    return {"status": "Processing started"}
```

---

## ❌ Blocking Wait on Job Completion

### Wrong

```python
import time

@frappe.whitelist()
def api_with_wait():
    job = frappe.enqueue('myapp.heavy_task')
    
    # WRONG - blocks web request!
    while job.get_status() != 'finished':
        time.sleep(1)
    
    return job.result
```

### Correct

```python
@frappe.whitelist()
def start_task():
    """Start task, return job ID."""
    job = frappe.enqueue(
        'myapp.heavy_task',
        on_success=lambda j, c, r: notify_user(r)
    )
    return {"job_id": job.id}

def notify_user(result):
    frappe.publish_realtime('task_done', result)
```

---

## ❌ Using job_name in v15+

### Wrong (v14 pattern)

```python
# DEPRECATED in v15!
from frappe.core.page.background_jobs.background_jobs import get_info

enqueued_jobs = [d.get("job_name") for d in get_info()]
if self.name not in enqueued_jobs:
    frappe.enqueue(..., job_name=self.name)
```

### Correct (v15+)

```python
from frappe.utils.background_jobs import is_job_enqueued

job_id = f"data_import::{self.name}"
if not is_job_enqueued(job_id):
    frappe.enqueue(
        'myapp.tasks.import_data',
        job_id=job_id,
        doc_name=self.name
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
        # WRONG - immediate retry can cause overload
        frappe.enqueue('myapp.task_with_retry')
```

### Correct

```python
def task_with_retry(retry_count=0, max_retries=3):
    try:
        external_api()
    except Exception:
        if retry_count < max_retries:
            # Exponential backoff
            delay = 60 * (2 ** retry_count)
            frappe.enqueue(
                'myapp.task_with_retry',
                retry_count=retry_count + 1,
                enqueue_after_commit=True
            )
        else:
            frappe.log_error("Max retries exceeded")
            raise
```

---

## ❌ Loading All Data into Memory

### Wrong

```python
def process_large_table():
    # WRONG - loads everything into memory
    all_records = frappe.get_all("Big Table", limit=0)
    for record in all_records:  # MemoryError!
        process(record)
```

### Correct

```python
def process_large_table():
    # Process in chunks
    offset = 0
    batch_size = 1000
    
    while True:
        records = frappe.get_all(
            "Big Table",
            limit=batch_size,
            start=offset
        )
        
        if not records:
            break
        
        for record in records:
            process(record)
        
        frappe.db.commit()
        offset += batch_size
```

---

## ❌ Duplicate Job Execution

### Wrong

```python
def on_submit(self):
    # WRONG - can run multiple times simultaneously
    frappe.enqueue('myapp.process', doc_name=self.name)
```

### Correct

```python
from frappe.utils.background_jobs import is_job_enqueued

def on_submit(self):
    job_id = f"process::{self.name}"
    if not is_job_enqueued(job_id):
        frappe.enqueue(
            'myapp.process',
            job_id=job_id,
            doc_name=self.name
        )
```

---

## Summary: Best Practices

| Aspect | DO | DON'T |
|--------|----|----|
| Heavy tasks | Enqueue to long queue | Direct in scheduler callback |
| Error handling | Try/except per record | Entire batch in one try |
| hooks.py changes | `bench migrate` | Forget and expect it to work |
| Job dependencies | Explicitly enqueue | Assumptions about order |
| User context | Explicitly set owner | Assume session.user is correct |
| Web requests | Enqueue and return | Blocking wait |
| Deduplication (v15) | `job_id` + `is_job_enqueued()` | `job_name` (deprecated) |
| Retries | Exponential backoff | Infinite immediate retry |
| Large datasets | Chunks/batches | All in memory |
