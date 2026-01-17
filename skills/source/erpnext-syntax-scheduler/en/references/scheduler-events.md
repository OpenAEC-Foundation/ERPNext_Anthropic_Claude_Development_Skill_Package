# Scheduler Events Reference

Complete reference for scheduler_events in hooks.py.

## Event Types

| Event Type | Frequency | Queue | Description |
|------------|-----------|-------|-------------|
| `all` | Every scheduler tick | default | Most frequent event |
| `hourly` | Every hour | default | Standard hourly jobs |
| `daily` | Every day | default | Daily tasks |
| `weekly` | Every week | default | Weekly tasks |
| `monthly` | Every month | default | Monthly tasks |
| `hourly_long` | Every hour | **long** | Long-running hourly jobs |
| `daily_long` | Every day | **long** | Long-running daily jobs |
| `weekly_long` | Every week | **long** | Long-running weekly jobs |
| `monthly_long` | Every month | **long** | Long-running monthly jobs |
| `cron` | Custom | Configurable | Flexible scheduling |

## Scheduler Tick Interval

| Version | Interval | Config Key |
|---------|----------|------------|
| v14 | ~240 sec (4 min) | `scheduler_interval` |
| v15 | ~60 sec | `scheduler_tick_interval` |

## Complete Syntax

```python
# hooks.py
scheduler_events = {
    # Standard events
    "all": [
        "myapp.tasks.every_tick"
    ],
    "hourly": [
        "myapp.tasks.hourly_cleanup",
        "myapp.tasks.sync_external_data"
    ],
    "daily": [
        "myapp.tasks.daily_report",
        "myapp.tasks.cleanup_old_records"
    ],
    "weekly": [
        "myapp.tasks.weekly_summary"
    ],
    "monthly": [
        "myapp.tasks.monthly_archive"
    ],
    
    # Long queue variants
    "daily_long": [
        "myapp.tasks.heavy_processing",
        "myapp.tasks.full_reindex"
    ],
    
    # Cron events
    "cron": {
        "*/15 * * * *": [
            "myapp.tasks.every_15_minutes"
        ],
        "0 9 * * 1-5": [
            "myapp.tasks.weekday_morning_9am"
        ],
        "0 0 1 * *": [
            "myapp.tasks.first_of_month"
        ]
    }
}
```

## Cron Syntax

```
┌─────────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌─────────── day of month (1 - 31)
│ │ │ ┌───────── month (1 - 12)
│ │ │ │ ┌─────── day of week (0 - 6, Sunday = 0)
│ │ │ │ │
* * * * *
```

### Symbols

| Symbol | Meaning | Example |
|--------|---------|---------|
| `*` | Every value | `* * * * *` = every minute |
| `,` | List | `1,15 * * * *` = minute 1 and 15 |
| `-` | Range | `1-5 * * * *` = minute 1 through 5 |
| `/` | Interval | `*/10 * * * *` = every 10 minutes |

### Examples

| Cron Expression | Meaning |
|-----------------|---------|
| `*/15 * * * *` | Every 15 minutes |
| `0 * * * *` | Every hour at :00 |
| `0 9 * * *` | Daily at 9:00 |
| `0 9 * * 1-5` | Weekdays at 9:00 |
| `0 0 * * 0` | Sunday at midnight |
| `0 0 1 * *` | First day of month |
| `0 0 1 1 *` | January 1st at midnight |
| `30 4 1,15 * *` | 1st and 15th of month at 4:30 |

### Special Strings (v14/v15)

```python
"cron": {
    "annual": ["myapp.tasks.yearly_task"]  # Yearly
}
```

## IMPORTANT: bench migrate

After EVERY change in scheduler_events:

```bash
bench migrate
```

Without `bench migrate` changes will NOT be applied!

## Task Function Structure

```python
# myapp/tasks.py

def hourly_cleanup():
    """Scheduled task - runs as Administrator."""
    # No parameters needed
    records = frappe.get_all("Log Entry", filters={"age": [">", 30]})
    for record in records:
        frappe.delete_doc("Log Entry", record.name)
    frappe.db.commit()

def daily_report():
    """Daily report generation."""
    # Heavy work to long queue
    frappe.enqueue(
        'myapp.tasks.generate_full_report',
        queue='long'
    )
```

## Multiple Apps

If multiple apps define the same scheduler events:

```python
# app_a/hooks.py
scheduler_events = {
    "daily": ["app_a.tasks.task_a"]
}

# app_b/hooks.py  
scheduler_events = {
    "daily": ["app_b.tasks.task_b"]
}
```

**Result**: Both tasks run - they are merged.
