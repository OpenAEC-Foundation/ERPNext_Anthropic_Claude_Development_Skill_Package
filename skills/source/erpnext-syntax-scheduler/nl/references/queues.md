# Queue Types & Configuration

## Default Queues

| Queue | Default Timeout | Gebruik |
|-------|-----------------|---------|
| `short` | 300s (5 min) | Snelle taken, UI responses |
| `default` | 300s (5 min) | Standaard taken |
| `long` | 1500s (25 min) | Heavy processing, imports, exports |

## Queue Selectie Guidelines

```python
# SHORT queue - snelle operaties
frappe.enqueue(
    "myapp.tasks.update_status",
    queue="short",
    doc_name=doc.name
)

# DEFAULT queue - standaard taken
frappe.enqueue(
    "myapp.tasks.send_email",
    # queue="default" is implicit
    recipient=email
)

# LONG queue - heavy processing
frappe.enqueue(
    "myapp.tasks.generate_report",
    queue="long",
    timeout=3600,  # 1 uur
    report_type="annual"
)
```

## Custom Queue Timeout

```python
# Override default timeout
frappe.enqueue(
    "myapp.tasks.medium_task",
    queue="default",
    timeout=900,  # 15 minuten ipv 5
    data=large_data
)
```

## Custom Queues Configureren

In `common_site_config.json`:

```json
{
    "workers": {
        "priority": {
            "timeout": 60,
            "background_workers": 2
        },
        "reports": {
            "timeout": 7200,
            "background_workers": 1
        },
        "imports": {
            "timeout": 5000,
            "background_workers": 4
        }
    }
}
```

### Custom Queue Gebruiken

```python
frappe.enqueue(
    "myapp.tasks.generate_large_report",
    queue="reports",
    report_id=report.name
)
```

## Worker Configuratie

### Default Procfile

```
worker_short: bench worker --queue short --quiet
worker_default: bench worker --queue default --quiet
worker_long: bench worker --queue long --quiet
```

### Multi-Queue Worker

```bash
# Eén worker consumeert van meerdere queues
bench worker --queue short,default
bench worker --queue long
```

### Burst Mode

Tijdelijke worker die stopt als queue leeg is:

```bash
bench worker --queue short --burst
```

Handig voor:
- One-time batch processing
- Development/testing
- Tijdelijke extra capaciteit

## Queue Prioriteit

Jobs worden verwerkt in FIFO volgorde binnen elke queue.

```python
# Vooraan in queue plaatsen (priority)
frappe.enqueue(
    "myapp.tasks.urgent_task",
    at_front=True,
    task_id=task.name
)
```

## Queue Monitoring

### Bench Commands

```bash
# Scheduler status
bench doctor

# Queue status bekijken
bench --site mysite show-pending-jobs

# Specifieke queue
bench --site mysite show-pending-jobs --queue long
```

### Via DocTypes

- **RQ Worker**: Worker status (busy/idle)
- **RQ Job**: Job status per queue

### Via Code

```python
from frappe.utils.background_jobs import get_queue

# Queue stats
queue = get_queue("default")
print(f"Jobs in queue: {len(queue)}")

# Job status
from rq.job import Job
job = Job.fetch(job_id, connection=frappe.cache())
print(job.get_status())
```

## Queue Best Practices

### Juiste Queue Kiezen

| Task Duration | Queue |
|---------------|-------|
| < 30 seconden | `short` |
| 30s - 5 minuten | `default` |
| 5 - 25 minuten | `long` |
| > 25 minuten | `long` + custom timeout |

### Vermijd Queue Blocking

```python
# FOUT - blokkeert short queue
frappe.enqueue(
    "myapp.tasks.heavy_task",
    queue="short"  # Timeout na 5 min!
)

# GOED - gebruik long queue
frappe.enqueue(
    "myapp.tasks.heavy_task",
    queue="long",
    timeout=3600
)
```

### Worker Scaling

```bash
# Meer workers voor specifieke queue
# In supervisor config of Procfile:
worker_long_1: bench worker --queue long --quiet
worker_long_2: bench worker --queue long --quiet
worker_long_3: bench worker --queue long --quiet
```
