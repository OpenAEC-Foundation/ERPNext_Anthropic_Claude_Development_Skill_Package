# Queue Types Reference

Complete reference for Frappe queue configuration.

## Default Queues

| Queue | Default Timeout | Usage |
|-------|-----------------|-------|
| `short` | 300s (5 min) | Quick tasks, UI responses |
| `default` | 300s (5 min) | Standard tasks |
| `long` | 1500s (25 min) | Heavy processing, imports |

## Queue Selection Criteria

### short Queue

```python
# Quick operations that shouldn't block UI
frappe.enqueue('myapp.tasks.quick_update', queue='short')
```

Use for:
- Cache invalidation
- Small notifications
- Quick lookups
- Tasks < 1 minute

### default Queue

```python
# Standard tasks
frappe.enqueue('myapp.tasks.process_order', queue='default')
```

Use for:
- Email sending
- Document processing
- API calls
- Tasks 1-5 minutes

### long Queue

```python
# Heavy processing
frappe.enqueue('myapp.tasks.generate_report', queue='long')
```

Use for:
- Data imports
- Bulk operations
- Report generation
- Tasks > 5 minutes

## Custom Queue Configuration

In `sites/common_site_config.json`:

```json
{
    "workers": {
        "myqueue": {
            "timeout": 5000,
            "background_workers": 4
        },
        "priority": {
            "timeout": 60,
            "background_workers": 2
        },
        "reports": {
            "timeout": 7200,
            "background_workers": 1
        }
    }
}
```

### Using Custom Queue

```python
frappe.enqueue(
    'myapp.tasks.generate_annual_report',
    queue='reports',
    timeout=7200
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
# Worker consumes from multiple queues
bench worker --queue short,default
bench worker --queue long
```

### Priority Order

Worker processes queues in specified order:

```bash
# short has priority over default
bench worker --queue short,default
```

## Burst Mode

Temporary worker that stops when queue is empty:

```bash
bench worker --queue short --burst
```

Use for:
- One-time batch processing
- Testing
- Deployment scripts

## Timeout Override

Per-job timeout override:

```python
# Override queue default
frappe.enqueue(
    'myapp.tasks.very_long_task',
    queue='long',
    timeout=7200  # 2 hours (override 25 min default)
)
```

## Queue Monitoring

### Via Desk

- **RQ Worker**: Shows worker status
- **RQ Job**: Shows jobs per queue

### Via CLI

```bash
# Queue status
bench doctor

# Specific queue info
bench execute frappe.utils.background_jobs.get_queue_info
```

## Scheduler Events and Queues

| Event | Queue |
|-------|-------|
| `all`, `hourly`, `daily`, `weekly`, `monthly` | default |
| `hourly_long`, `daily_long`, `weekly_long`, `monthly_long` | long |

```python
scheduler_events = {
    "daily": ["myapp.tasks.quick_daily"],      # → default queue
    "daily_long": ["myapp.tasks.heavy_daily"]  # → long queue
}
```

## Best Practices

1. **Match queue to expected duration**
   - < 1 min → short
   - 1-5 min → default
   - > 5 min → long

2. **Use timeout parameter for exceptions**
   ```python
   frappe.enqueue(..., queue='long', timeout=3600)
   ```

3. **Monitor queue depths**
   - Many pending jobs = need more workers
   - Many failed jobs = improve error handling

4. **Scale workers per queue**
   ```json
   {
       "workers": {
           "long": {
               "background_workers": 2
           }
       }
   }
   ```
