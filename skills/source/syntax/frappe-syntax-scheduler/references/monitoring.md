# Monitoring Reference

Complete reference for background job monitoring.

## RQ Worker DocType (Virtual)

Shows all background workers.

**Access**: Search > RQ Worker

### Fields

| Field | Description |
|-------|-------------|
| Worker name | Unique worker identifier |
| Status | busy / idle |
| Current Job | Current job (if busy) |
| Successful Jobs | Success count |
| Failed Jobs | Failure count |
| Total Working Time | Cumulative work time |

## RQ Job DocType (Virtual)

Shows all background jobs.

**Access**: Search > RQ Job

### Filters

- **Queue**: short, default, long, or custom
- **Status**: queued, started, finished, failed

### Fields

| Field | Description |
|-------|-------------|
| Job ID | Unique identifier |
| Queue | Target queue |
| Status | Job status |
| Method | Executed function |
| Arguments | Parameters |
| Exception | Error details (on failure) |
| Created | Creation timestamp |
| Started | Start timestamp |
| Ended | End timestamp |

## Job Statuses

| Status | Meaning |
|--------|---------|
| `queued` | In queue, waiting for worker |
| `started` | Being executed by worker |
| `finished` | Successfully completed |
| `failed` | Failed (exception) |

## Scheduled Job Log

DocType that tracks scheduler job executions.

**Access**: Search > Scheduled Job Log

### Fields

| Field | Description |
|-------|-------------|
| Scheduled Job Type | Name of scheduled job |
| Status | Complete / Failed |
| Method | Executed method |
| Start | Start timestamp |
| End | End timestamp |
| Error | Error message (on failure) |

## bench doctor

CLI command for scheduler diagnostics.

```bash
bench doctor
```

### Example Output

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

### Check specific site

```bash
bench --site mysite.local doctor
```

## Monitor Feature

### Enable

In `sites/{site}/site_config.json`:

```json
{
    "monitor": 1
}
```

### Log Location

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

### Fields

| Field | Description |
|-------|-------------|
| `duration` | Execution time (ms) |
| `job.method` | Executed method |
| `job.scheduled` | Was scheduled job |
| `job.wait` | Wait time in queue (ms) |
| `site` | Site name |
| `timestamp` | Execution timestamp |
| `transaction_type` | "job" for background jobs |
| `uuid` | Unique transaction ID |

## Stuck Worker Debug

If a worker is stuck:

```bash
# Find worker PID
ps aux | grep "bench worker"

# Send SIGUSR1 for stack trace
kill -SIGUSR1 <WORKER_PID>
```

Output goes to `logs/worker.error.log`.

## Log Files

| Log | Location | Content |
|-----|----------|---------|
| Worker errors | `logs/worker.error.log` | Worker exceptions |
| Scheduler | `logs/scheduler.log` | Scheduler activity |
| Monitor | `logs/monitor.json.log` | Performance metrics |

### Log Tailing

```bash
# Follow worker errors live
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
    """Task with progress updates."""
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
# Scheduled task to check error count
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
2. **Set up alerts** for high error rates
3. **Use** realtime updates for long tasks
4. **Check** `bench doctor` after deployments
5. **Review** Error Log regularly
6. **Analyze** monitor.json.log for performance insights
