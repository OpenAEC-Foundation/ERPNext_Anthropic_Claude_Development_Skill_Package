# Monitoring Reference

Complete referentie voor background job monitoring.

## RQ Worker DocType (Virtual)

Toont alle background workers.

**Toegang**: Search > RQ Worker

### Velden

| Veld | Beschrijving |
|------|--------------|
| Worker naam | Unieke worker identifier |
| Status | busy / idle |
| Current Job | Huidige job (als busy) |
| Successful Jobs | Aantal succesvol |
| Failed Jobs | Aantal mislukt |
| Total Working Time | Cumulatieve werktijd |

## RQ Job DocType (Virtual)

Toont alle background jobs.

**Toegang**: Search > RQ Job

### Filters

- **Queue**: short, default, long, of custom
- **Status**: queued, started, finished, failed

### Velden

| Veld | Beschrijving |
|------|--------------|
| Job ID | Unieke identifier |
| Queue | Target queue |
| Status | Job status |
| Method | Uitgevoerde functie |
| Arguments | Parameters |
| Exception | Error details (bij failure) |
| Created | Aanmaak timestamp |
| Started | Start timestamp |
| Ended | Eind timestamp |

## Job Statuses

| Status | Betekenis |
|--------|-----------|
| `queued` | In wachtrij, wacht op worker |
| `started` | Wordt uitgevoerd door worker |
| `finished` | Succesvol afgerond |
| `failed` | Mislukt (exception) |

## Scheduled Job Log

DocType dat scheduler job executions bijhoudt.

**Toegang**: Search > Scheduled Job Log

### Velden

| Veld | Beschrijving |
|------|--------------|
| Scheduled Job Type | Naam van scheduled job |
| Status | Complete / Failed |
| Method | Uitgevoerde method |
| Start | Start timestamp |
| End | Eind timestamp |
| Error | Error message (bij failure) |

## bench doctor

CLI commando voor scheduler diagnostiek.

```bash
bench doctor
```

### Output Voorbeeld

```
Scheduler Status for site1.local
   Scheduler is: enabled
   Workers are: running
   Pending tasks: 3

Scheduler Status for site2.local
   Scheduler is: enabled
   Workers are: running
   Pending tasks: 0
```

### Controleer specifieke site

```bash
bench --site mysite.local doctor
```

## Monitor Feature

### Activeren

In `sites/{site}/site_config.json`:

```json
{
    "monitor": 1
}
```

### Log Locatie

```
logs/monitor.json.log
```

### Log Format

```json
{
    "duration": 1364,
    "job": {
        "method": "frappe.ping",
        "scheduled": false,
        "wait": 90204
    },
    "site": "frappe.local",
    "timestamp": "2020-03-05 09:37:40.124682",
    "transaction_type": "job",
    "uuid": "8225ab76-8bee-462c-b9fc-a556406b1ee7"
}
```

### Velden

| Veld | Beschrijving |
|------|--------------|
| `duration` | Executie tijd (ms) |
| `job.method` | Uitgevoerde method |
| `job.scheduled` | Was scheduled job |
| `job.wait` | Wachttijd in queue (ms) |
| `site` | Site naam |
| `timestamp` | Execution timestamp |
| `transaction_type` | "job" voor background jobs |
| `uuid` | Unieke transaction ID |

## Stuck Worker Debug

Als een worker vastloopt:

```bash
# Vind worker PID
ps aux | grep "bench worker"

# Stuur SIGUSR1 voor stack trace
kill -SIGUSR1 <WORKER_PID>
```

Output gaat naar `logs/worker.error.log`.

## Log Files

| Log | Locatie | Inhoud |
|-----|---------|--------|
| Worker errors | `logs/worker.error.log` | Worker exceptions |
| Scheduler | `logs/scheduler.log` | Scheduler activity |
| Monitor | `logs/monitor.json.log` | Performance metrics |

### Log Tailing

```bash
# Worker errors live volgen
tail -f logs/worker.error.log

# Scheduler activity
tail -f logs/scheduler.log
```

## Programmatic Monitoring

### Queue Info

```python
from frappe.utils.background_jobs import get_queue_info

info = frappe.call('frappe.utils.background_jobs.get_queue_info')
# Returns queue statistics
```

### Job Status Check

```python
job = frappe.enqueue('myapp.tasks.process')
status = job.get_status()  # 'queued', 'started', 'finished', 'failed'
```

### Pending Jobs Count

```python
from frappe.utils.background_jobs import get_jobs

jobs = get_jobs(site='mysite.local', queue='default', status='queued')
pending_count = len(jobs)
```

## Realtime Progress Updates

```python
def long_running_task(items, user):
    """Task met progress updates."""
    total = len(items)
    
    for i, item in enumerate(items):
        process_item(item)
        
        # Update progress
        frappe.publish_realtime(
            'task_progress',
            {
                'progress': (i + 1) / total * 100,
                'current': i + 1,
                'total': total
            },
            user=user
        )
    
    frappe.publish_realtime(
        'task_complete',
        {'message': f'Processed {total} items'},
        user=user
    )
```

## Alerting Setup

### Via Error Log Monitoring

```python
# Scheduled task om error count te checken
def check_error_rate():
    hour_ago = frappe.utils.add_to_date(
        frappe.utils.now_datetime(),
        hours=-1
    )
    
    errors = frappe.db.count("Error Log", {
        "creation": [">=", hour_ago]
    })
    
    if errors > 100:
        frappe.sendmail(
            recipients=["admin@example.com"],
            subject="High Error Rate Alert",
            message=f"{errors} errors in the last hour"
        )
```

## Best Practices

1. **Monitor** queue depths via RQ Job doctype
2. **Stel alerts in** voor hoge error rates
3. **Gebruik** realtime updates voor lange tasks
4. **Check** `bench doctor` na deployments
5. **Review** Error Log regelmatig
6. **Analyseer** monitor.json.log voor performance insights
