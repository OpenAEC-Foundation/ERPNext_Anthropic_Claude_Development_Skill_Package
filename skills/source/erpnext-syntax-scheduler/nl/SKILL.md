---
name: erpnext-syntax-scheduler
description: Deterministische syntax referentie voor Frappe Scheduler Events en Background Jobs (frappe.enqueue). Gebruik voor scheduler_events in hooks.py, frappe.enqueue/enqueue_doc API, queue configuratie, job deduplicatie, error handling en monitoring. Dekt v14/v15 versieverschillen inclusief job_id (v15) vs job_name (v14 deprecated).
---

# ERPNext Syntax: Scheduler & Background Jobs

Deterministische syntax voor scheduler events en background jobs in Frappe/ERPNext v14 en v15.

## Wanneer Deze Skill Gebruiken

- Periodieke taken configureren via `hooks.py`
- Lange operaties async uitvoeren met `frappe.enqueue`
- Queue types en timeouts configureren
- Job deduplicatie implementeren
- Background job errors afhandelen
- Jobs monitoren en debuggen

## Kritieke Versieverschillen

| Aspect | v14 | v15 |
|--------|-----|-----|
| Scheduler tick | ~240 sec (4 min) | ~60 sec |
| Config key | `scheduler_interval` | `scheduler_tick_interval` |
| Job deduplicatie | `job_name` | `job_id` + `is_job_enqueued()` |

## Scheduler Events (hooks.py)

### Event Types

```python
# hooks.py
scheduler_events = {
    "all": ["myapp.tasks.every_tick"],       # Elke scheduler tick
    "hourly": ["myapp.tasks.per_uur"],       # Elk uur (default queue)
    "daily": ["myapp.tasks.dagelijks"],      # Elke dag
    "weekly": ["myapp.tasks.wekelijks"],     # Elke week
    "monthly": ["myapp.tasks.maandelijks"],  # Elke maand
    
    # Long queue variants (voor heavy processing)
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
        "*/15 * * * *": ["myapp.tasks.every_15_min"],      # Elke 15 min
        "0 9 * * 1-5": ["myapp.tasks.weekday_9am"],        # Ma-Vr 9:00
        "0 0 1 * *": ["myapp.tasks.first_of_month"],       # 1e van maand
        "15 18 * * *": ["myapp.tasks.daily_6_15pm"],       # Dagelijks 18:15
    }
}
```

**VERPLICHT na wijzigingen:**
```bash
bench migrate
```

Zie [references/scheduler-events.md](references/scheduler-events.md) voor complete cron syntax.

## frappe.enqueue API

### Basis Syntax

```python
frappe.enqueue(
    method,                      # Functie of module path (VERPLICHT)
    queue="default",             # "short", "default", "long"
    timeout=None,                # Override timeout (seconden)
    job_id=None,                 # v15: Unieke ID voor deduplicatie
    enqueue_after_commit=False,  # Wacht op DB commit
    at_front=False,              # Priority placement
    on_success=None,             # Success callback
    on_failure=None,             # Failure callback
    **kwargs                     # Argumenten voor method
)
```

### Voorbeelden

```python
# Basis
frappe.enqueue('myapp.tasks.process', customer='CUST-001')

# Met timeout op long queue
frappe.enqueue(
    'myapp.tasks.heavy_report',
    queue='long',
    timeout=3600,
    report_type='annual'
)

# Met callbacks
frappe.enqueue(
    'myapp.tasks.risky_operation',
    on_success=lambda job, conn, result: notify_success(),
    on_failure=lambda job, conn, type, value, tb: log_failure()
)

# Na database commit (voor data integriteit)
frappe.enqueue(
    'myapp.tasks.send_notification',
    enqueue_after_commit=True,
    user=frappe.session.user
)
```

Zie [references/enqueue-api.md](references/enqueue-api.md) voor alle parameters.

## frappe.enqueue_doc

Enqueue een controller method van een document:

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

| Queue | Default Timeout | Gebruik |
|-------|-----------------|---------|
| `short` | 300s (5 min) | Snelle taken, UI responses |
| `default` | 300s (5 min) | Standaard taken |
| `long` | 1500s (25 min) | Heavy processing, imports |

Zie [references/queues.md](references/queues.md) voor custom queue configuratie.

## Job Deduplicatie

### v15+ (Aanbevolen)

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
# NIET GEBRUIKEN IN NIEUW CODE
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
            frappe.db.rollback()  # Rollback bij error
            frappe.log_error(
                frappe.get_traceback(),
                f"Process Error: {record}"
            )
```

Zie [references/error-handling.md](references/error-handling.md) voor patterns.

## Monitoring

- **RQ Worker**: Search > RQ Worker (worker status)
- **RQ Job**: Search > RQ Job (job status/errors)
- **bench doctor**: Scheduler status per site

```bash
bench doctor
```

Zie [references/monitoring.md](references/monitoring.md) voor details.

## User Context

**BELANGRIJK**: Scheduled jobs draaien als **Administrator**!

```python
def scheduled_task():
    print(frappe.session.user)  # "Administrator"
    
    # Expliciet owner zetten:
    doc = frappe.new_doc("ToDo")
    doc.owner = "specific.user@example.com"
    doc.insert(ignore_permissions=True)
```

## Best Practices

1. **ALTIJD** `bench migrate` na hooks.py scheduler_events wijzigingen
2. **GEBRUIK** juiste queue: short/default/long
3. **GEBRUIK** `job_id` + `is_job_enqueued()` voor deduplicatie (v15)
4. **IMPLEMENTEER** error handling met commit/rollback per record
5. **ENQUEUE** heavy tasks vanuit scheduler events naar long queue
6. **NOOIT** blocking waits in web requests
7. **ONTHOUD** dat jobs als Administrator draaien

## Anti-Patterns

Zie [references/anti-patterns.md](references/anti-patterns.md) voor fouten te vermijden:
- Heavy processing direct in scheduler callback
- Geen error handling (hele batch faalt)
- Blocking wait op job completion
- `job_name` gebruiken in v15+

## Complete Voorbeelden

Zie [references/examples.md](references/examples.md) voor:
- Data import met progress tracking
- Email verzending met retry logic
- Cleanup jobs met error recovery
- Report generatie met notifications
