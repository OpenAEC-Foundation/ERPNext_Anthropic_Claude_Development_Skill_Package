# Queue Types & Configuration

## Default Queues

| Queue | Default Timeout | Usage |
|-------|-----------------|-------|
| `short` | 300s (5 min) | Quick tasks, UI responses |
| `default` | 300s (5 min) | Standard tasks |
| `long` | 1500s (25 min) | Heavy processing, imports, exports |

## Queue Selection Guidelines

```python
# SHORT queue - quick operations
frappe.enqueue(
    "myapp.tasks.update_status",
    queue="short",
    doc_name=doc.name
)

# DEFAULT queue - standard tasks
frappe.enqueue(
    "myapp.tasks.send_email",
    # queue="default" is implicit
    recipient=email
)

# LONG queue - heavy processing
frappe.enqueue(
    "myapp.tasks.generate_report",
    queue="long",
    timeout=3600,  # 1 hour
    report_type="annual"
)
```

## Custom Queue Timeout

```python
# Override default timeout
frappe.enqueue(
    "myapp.tasks.medium_task",
    queue="default",
    timeout=900,  # 15 minutes instead of 5
    data=large_data
)
```

## Custom Queues Configuration

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

### Using Custom Queue

```python
frappe.enqueue(
    "myapp.tasks.generate_large_report",
    queue="reports",
    report_id=report.name
)
```

## Worker Configuration

### Default Procfile

```
worker_short: bench worker --queue short --quiet
worker_default: bench worker --queue default --quiet
worker_long: bench worker --queue long --quiet
```

### Multi-Queue Worker

```bash
# One worker consumes from multiple queues
bench worker --queue short,default
bench worker --queue long
```

### Burst Mode

Temporary worker that stops when queue is empty:

```bash
bench worker --queue short --burst
```

Useful for:
- One-time batch processing
- Development/testing
- Temporary extra capacity

## Queue Priority

Jobs are processed in FIFO order within each queue.

```python
# Place at front of queue (priority)
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

# View queue status
bench --site mysite show-pending-jobs

# Specific queue
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

### Choosing the Right Queue

| Task Duration | Queue |
|---------------|-------|
| < 30 seconds | `short` |
| 30s - 5 minutes | `default` |
| 5 - 25 minutes | `long` |
| > 25 minutes | `long` + custom timeout |

### Avoid Queue Blocking

```python
# WRONG - blocks short queue
frappe.enqueue(
    "myapp.tasks.heavy_task",
    queue="short"  # Timeout after 5 min!
)

# RIGHT - use long queue
frappe.enqueue(
    "myapp.tasks.heavy_task",
    queue="long",
    timeout=3600
)
```

### Worker Scaling

```bash
# More workers for specific queue
# In supervisor config or Procfile:
worker_long_1: bench worker --queue long --quiet
worker_long_2: bench worker --queue long --quiet
worker_long_3: bench worker --queue long --quiet
```
