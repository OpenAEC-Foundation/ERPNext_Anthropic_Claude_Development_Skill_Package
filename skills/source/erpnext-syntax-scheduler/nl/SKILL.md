---
name: erpnext-syntax-scheduler
description: Scheduler en background jobs syntax voor Frappe/ERPNext v14/v15. Gebruik voor scheduler_events in hooks.py, frappe.enqueue() voor async jobs, queue configuratie, job deduplicatie, error handling, en monitoring. Triggers op vragen over scheduled tasks, background processing, cron jobs, RQ workers, job queues, async taken.
---

# ERPNext Syntax: Scheduler & Background Jobs

Deterministische syntax referentie voor Frappe scheduler events en background job processing.

## Quick Reference

### Scheduler Events (hooks.py)

```python
# hooks.py
scheduler_events = {
    "all": ["myapp.tasks.every_tick"],
    "hourly": ["myapp.tasks.hourly_task"],
    "daily": ["myapp.tasks.daily_task"],
    "weekly": ["myapp.tasks.weekly_task"],
    "monthly": ["myapp.tasks.monthly_task"],
    "daily_long": ["myapp.tasks.heavy_daily"],  # Long queue
    "cron": {
        "0 9 * * 1-5": ["myapp.tasks.weekday_9am"],
        "*/15 * * * *": ["myapp.tasks.every_15_min"]
    }
}
```

**KRITIEK**: Na ELKE wijziging in scheduler_events: `bench migrate`

### frappe.enqueue Basis

```python
# Eenvoudig
frappe.enqueue("myapp.tasks.process", customer="CUST-001")

# Met queue en timeout
frappe.enqueue(
    "myapp.tasks.heavy_task",
    queue="long",
    timeout=3600,
    param="value"
)

# Met deduplicatie (v15)
from frappe.utils.background_jobs import is_job_enqueued

job_id = f"import::{doc.name}"
if not is_job_enqueued(job_id):
    frappe.enqueue("myapp.tasks.import_data", job_id=job_id, doc=doc.name)
```

## Scheduler Event Types

| Event | Frequentie | Queue |
|-------|------------|-------|
| `all` | Elke tick (v14: 4min, v15: 60s) | default |
| `hourly` | Per uur | default |
| `daily` | Per dag | default |
| `weekly` | Per week | default |
| `monthly` | Per maand | default |
| `hourly_long` | Per uur | **long** |
| `daily_long` | Per dag | **long** |
| `weekly_long` | Per week | **long** |
| `monthly_long` | Per maand | **long** |
| `cron` | Custom schedule | configureerbaar |

**Versieverschil scheduler tick**:
- v14: ~240 seconden (4 min)
- v15: ~60 seconden

## Queue Types

| Queue | Timeout | Gebruik |
|-------|---------|---------|
| `short` | 300s (5 min) | Snelle taken, UI responses |
| `default` | 300s (5 min) | Standaard taken |
| `long` | 1500s (25 min) | Heavy processing, imports |

## frappe.enqueue Parameters

```python
frappe.enqueue(
    method,                      # VERPLICHT: functie of module path
    queue="default",             # Queue naam
    timeout=None,                # Override timeout (seconden)
    is_async=True,               # False = direct uitvoeren
    now=False,                   # True = via frappe.call()
    job_id=None,                 # v15: unieke ID voor deduplicatie
    enqueue_after_commit=False,  # Wacht op DB commit
    at_front=False,              # Vooraan in queue plaatsen
    on_success=None,             # Success callback
    on_failure=None,             # Failure callback
    **kwargs                     # Argumenten voor method
)
```

## Job Deduplicatie

### v15+ (Aanbevolen)

```python
from frappe.utils.background_jobs import is_job_enqueued

job_id = f"process::{doc.name}"
if not is_job_enqueued(job_id):
    frappe.enqueue(
        "myapp.tasks.process",
        job_id=job_id,
        doc_name=doc.name
    )
```

### v14 (Deprecated)

```python
# NIET MEER GEBRUIKEN - alleen voor legacy code
from frappe.core.page.background_jobs.background_jobs import get_info
enqueued = [d.get("job_name") for d in get_info()]
if name not in enqueued:
    frappe.enqueue(..., job_name=name)
```

## Error Handling Pattern

```python
def process_records(records):
    for record in records:
        try:
            process_single(record)
            frappe.db.commit()  # Commit per success
        except Exception:
            frappe.db.rollback()  # Rollback bij error
            frappe.log_error(
                frappe.get_traceback(),
                f"Process Error: {record}"
            )
```

## Callbacks

```python
def on_success_handler(job, connection, result, *args, **kwargs):
    frappe.publish_realtime("show_alert", {"message": "Klaar!"})

def on_failure_handler(job, connection, type, value, traceback):
    frappe.log_error(f"Job {job.id} failed: {value}")

frappe.enqueue(
    "myapp.tasks.risky_task",
    on_success=on_success_handler,
    on_failure=on_failure_handler
)
```

## User Context

**BELANGRIJK**: Scheduler jobs draaien als **Administrator**!

```python
def scheduled_task():
    # frappe.session.user = "Administrator"
    
    # Expliciete owner zetten:
    doc = frappe.new_doc("ToDo")
    doc.owner = "user@example.com"
    doc.insert(ignore_permissions=True)
```

## Monitoring

| Tool | Beschrijving |
|------|--------------|
| RQ Worker (DocType) | Worker status, busy/idle |
| RQ Job (DocType) | Job status, queue filter |
| `bench doctor` | Scheduler status overzicht |
| Scheduled Job Log | Executie historie |

## Versieverschillen v14 vs v15

| Feature | v14 | v15 |
|---------|-----|-----|
| Tick interval | 4 min | 60 sec |
| Config key | `scheduler_interval` | `scheduler_tick_interval` |
| Deduplicatie | `job_name` | `job_id` + `is_job_enqueued()` |

## Reference Files

- **[scheduler-events.md](references/scheduler-events.md)**: Alle event types, cron syntax, configuratie
- **[enqueue-api.md](references/enqueue-api.md)**: Complete frappe.enqueue/enqueue_doc API
- **[queues.md](references/queues.md)**: Queue types, timeouts, custom queues, workers
- **[examples.md](references/examples.md)**: Complete werkende voorbeelden
- **[anti-patterns.md](references/anti-patterns.md)**: Veelgemaakte fouten en correcties

## Kritieke Regels

1. **ALTIJD** `bench migrate` na hooks.py scheduler_events wijzigingen
2. **GEBRUIK** `job_id` + `is_job_enqueued()` voor deduplicatie (v15)
3. **KIES** juiste queue: short/default/long op basis van duration
4. **COMMIT** per succesvol record, rollback bij error
5. **ONTHOUD** dat jobs als Administrator draaien
6. **ENQUEUE** heavy tasks vanuit scheduler events, niet direct uitvoeren
