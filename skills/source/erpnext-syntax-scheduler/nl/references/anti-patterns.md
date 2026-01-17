# Anti-Patterns: Wat te Vermijden

## ❌ Geen Error Handling

### Fout

```python
def process_all(records):
    for record in records:
        process_single(record)  # Eén failure stopt ALLES
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

## ❌ Heavy Processing Direct in Scheduler Event

### Fout

```python
# hooks.py
scheduler_events = {
    "all": ["myapp.tasks.process_millions_of_records"]
}

def process_millions_of_records():
    # FOUT - blokkeert scheduler tick
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
    # Scheduler triggert alleen, enqueue doet het werk
    frappe.enqueue(
        "myapp.tasks.process_millions_of_records",
        queue="long",
        timeout=3600
    )
```

---

## ❌ Vergeten bench migrate

### Fout

```python
# hooks.py gewijzigd
scheduler_events = {
    "hourly": ["myapp.tasks.new_task"]  # Nieuw toegevoegd
}

# FOUT - vergeten bench migrate
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
    # Expliciet volgende stap triggeren
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

## ❌ Geen User Context Awareness

### Fout

```python
def scheduled_task():
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
    heavy_processing()  # Blokkeert user 5+ minuten
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

## ❌ Blocking Wait op Job Completion

### Fout

```python
import time

@frappe.whitelist()
def start_and_wait():
    job = frappe.enqueue("myapp.heavy_task")
    
    # FOUT - blokkeert web request
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

## ❌ job_name Gebruiken (v15 Deprecated)

### Fout

```python
# v14 pattern - NIET GEBRUIKEN in v15
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

## ❌ Infinite Retry Zonder Backoff

### Fout

```python
def task_with_retry():
    try:
        external_api()
    except Exception:
        # FOUT - direct retry zonder delay
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
        delay = 2 ** retry_count  # 1, 2, 4 minuten
        
        frappe.enqueue(
            "myapp.task_with_retry",
            retry_count=retry_count + 1
        )
```

---

## ❌ Verkeerde Queue voor Task Duration

### Fout

```python
# Task duurt 30 minuten maar gebruikt short queue
frappe.enqueue(
    "myapp.tasks.long_running_task",
    queue="short"  # Timeout na 5 min!
)
```

### Correct

```python
frappe.enqueue(
    "myapp.tasks.long_running_task",
    queue="long",
    timeout=2400  # 40 minuten
)
```

---

## ❌ Geen Commit Per Record

### Fout

```python
def process_batch(records):
    for record in records:
        update_record(record)
    
    frappe.db.commit()  # Eén failure = alles weg
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

## Samenvatting: Best Practices

1. **ALTIJD** error handling met commit/rollback per record
2. **ALTIJD** `bench migrate` na hooks.py wijzigingen
3. **GEBRUIK** `job_id` + `is_job_enqueued()` voor deduplicatie (v15)
4. **KIES** juiste queue: short/default/long
5. **ENQUEUE** heavy tasks vanuit scheduler events
6. **NOOIT** blocking waits in web requests
7. **ONTHOUD** dat jobs als Administrator draaien
8. **IMPLEMENTEER** retry met exponential backoff
