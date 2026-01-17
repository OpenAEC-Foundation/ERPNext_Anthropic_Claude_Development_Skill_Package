# Anti-Patterns Reference

Veelgemaakte fouten en hoe ze te vermijden.

## ❌ Heavy Processing in Scheduler Callback

### Fout

```python
# hooks.py - FOUT!
scheduler_events = {
    "all": ["myapp.tasks.process_millions_of_records"]
}

# tasks.py
def process_millions_of_records():
    # Dit blokkeert de scheduler!
    records = frappe.get_all("Item", limit=0)  # Miljoen records
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
    """Heavy processing op long queue."""
    records = frappe.get_all("Item", limit=0)
    for record in records:
        heavy_processing(record)
```

---

## ❌ Geen Error Handling

### Fout

```python
def process_all(records):
    # FOUT - één error stopt alles
    for r in records:
        process(r)  # Exception = hele batch faalt
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

## ❌ Vergeten bench migrate

### Fout

```python
# hooks.py - aangepast
scheduler_events = {
    "hourly": ["myapp.tasks.new_task"]  # Nieuw toegevoegd
}

# Vergeten: bench migrate
# Nieuwe task wordt NIET uitgevoerd!
```

### Correct

```bash
# Na ELKE wijziging in hooks.py scheduler_events:
bench migrate
```

---

## ❌ Aannames Over Executie Volgorde

### Fout

```python
def task_a():
    create_data()

def task_b():
    # FOUT - aanname dat task_a eerst klaar is
    process_data()  # Data bestaat mogelijk nog niet!

# hooks.py
scheduler_events = {
    "hourly": ["myapp.task_a", "myapp.task_b"]
}
```

### Correct

```python
def task_a():
    create_data()
    # Expliciet volgende stap enqueuen
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

## ❌ Geen User Context Awareness

### Fout

```python
def scheduled_task():
    # FOUT - aanname over session user
    doc = frappe.new_doc("ToDo")
    doc.allocated_to = frappe.session.user  # = Administrator!
    doc.insert()
```

### Correct

```python
def scheduled_task():
    # Scheduler draait als Administrator
    doc = frappe.new_doc("ToDo")
    doc.allocated_to = "specific.user@example.com"  # Expliciet
    doc.owner = "specific.user@example.com"
    doc.insert(ignore_permissions=True)
```

---

## ❌ Synchrone Executie in Web Request

### Fout

```python
@frappe.whitelist()
def api_endpoint():
    # FOUT - blokkeert user 5+ minuten
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

## ❌ Blocking Wait op Job Completion

### Fout

```python
import time

@frappe.whitelist()
def api_with_wait():
    job = frappe.enqueue('myapp.heavy_task')
    
    # FOUT - blokkeert web request!
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

## ❌ job_name Gebruiken in v15+

### Fout (v14 pattern)

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

## ❌ Infinite Retry Zonder Backoff

### Fout

```python
def task_with_retry():
    try:
        external_api()
    except Exception:
        # FOUT - direct retry kan overload veroorzaken
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

## ❌ Alle Data in Memory Laden

### Fout

```python
def process_large_table():
    # FOUT - laadt alles in memory
    all_records = frappe.get_all("Big Table", limit=0)
    for record in all_records:  # MemoryError!
        process(record)
```

### Correct

```python
def process_large_table():
    # Verwerk in chunks
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

## ❌ Dubbele Job Executie

### Fout

```python
def on_submit(self):
    # FOUT - kan meerdere keren tegelijk draaien
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

## Samenvatting: Best Practices

| Aspect | DO | DON'T |
|--------|----|----|
| Heavy tasks | Enqueue naar long queue | Direct in scheduler callback |
| Error handling | Try/except per record | Hele batch in één try |
| hooks.py changes | `bench migrate` | Vergeten en verwachten dat het werkt |
| Job dependencies | Expliciet enqueuen | Aannames over volgorde |
| User context | Expliciet owner zetten | Aannemen dat session.user klopt |
| Web requests | Enqueue en return | Blocking wait |
| Deduplicatie (v15) | `job_id` + `is_job_enqueued()` | `job_name` (deprecated) |
| Retries | Exponential backoff | Infinite direct retry |
| Large datasets | Chunks/batches | Alles in memory |
