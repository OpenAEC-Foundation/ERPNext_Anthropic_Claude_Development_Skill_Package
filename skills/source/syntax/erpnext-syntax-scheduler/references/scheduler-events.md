# Scheduler Events Reference

## Event Types Overview

```python
# hooks.py - Complete syntax
scheduler_events = {
    # Standard events (default queue)
    "all": ["myapp.tasks.every_tick"],
    "hourly": ["myapp.tasks.hourly_task"],
    "daily": ["myapp.tasks.daily_task"],
    "weekly": ["myapp.tasks.weekly_task"],
    "monthly": ["myapp.tasks.monthly_task"],
    
    # Long queue events (for heavy processing)
    "hourly_long": ["myapp.tasks.hourly_heavy"],
    "daily_long": ["myapp.tasks.daily_heavy"],
    "weekly_long": ["myapp.tasks.weekly_heavy"],
    "monthly_long": ["myapp.tasks.monthly_heavy"],
    
    # Cron events (custom scheduling)
    "cron": {
        "*/15 * * * *": ["myapp.tasks.every_15_minutes"],
        "0 9 * * 1-5": ["myapp.tasks.weekday_9am"],
        "0 0 1 * *": ["myapp.tasks.first_of_month"]
    }
}
```

## Cron Syntax

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6, Sunday = 0)
│ │ │ │ │
* * * * *
```

### Cron Symbols

| Symbol | Meaning | Example |
|--------|---------|---------|
| `*` | Any value | `* * * * *` = every minute |
| `,` | List | `1,15 * * * *` = minute 1 and 15 |
| `-` | Range | `1-5 * * * *` = minute 1 through 5 |
| `/` | Interval | `*/10 * * * *` = every 10 minutes |

### Common Cron Patterns

```python
scheduler_events = {
    "cron": {
        # Every 5 minutes
        "*/5 * * * *": ["myapp.tasks.frequent_check"],
        
        # Every weekday at 9:00
        "0 9 * * 1-5": ["myapp.tasks.workday_morning"],
        
        # Every Monday at 8:00
        "0 8 * * 1": ["myapp.tasks.monday_report"],
        
        # First day of month at midnight
        "0 0 1 * *": ["myapp.tasks.monthly_cleanup"],
        
        # Every day at 18:15
        "15 18 * * *": ["myapp.tasks.evening_summary"],
        
        # Every hour from 9-17 on weekdays
        "0 9-17 * * 1-5": ["myapp.tasks.business_hours"],
        
        # Special string (annual)
        "annual": ["myapp.tasks.yearly_archive"]
    }
}
```

## Scheduler Tick Interval

| Version | Interval | Config Key |
|---------|----------|------------|
| v14 | ~240 sec (4 min) | `scheduler_interval` |
| v15 | ~60 sec | `scheduler_tick_interval` |

### Custom Tick Interval

In `common_site_config.json`:

```json
{
    "scheduler_tick_interval": 120
}
```

## Multiple Methods Per Event

```python
scheduler_events = {
    "daily": [
        "myapp.tasks.cleanup_logs",
        "myapp.tasks.send_daily_report",
        "myapp.tasks.sync_external_data"
    ]
}
```

**Note**: Execution order is NOT guaranteed!

## CRITICAL: bench migrate

After EVERY change to `scheduler_events`:

```bash
bench migrate
```

Without `bench migrate` changes are NOT applied!

## Runtime Configurable Events

For events that need to be adjusted without code deploy:

```python
# Create Scheduler Event record
sch_eve = frappe.new_doc("Scheduler Event")
sch_eve.scheduled_against = "Payment Reconciliation"
sch_eve.save()

# Create Scheduled Job Type
job = frappe.new_doc("Scheduled Job Type")
job.frequency = "Cron"
job.scheduler_event = sch_eve.name
job.cron_format = "0/5 * * * *"  # Every 5 minutes
job.save()
```

## Event Debugging

```bash
# Check scheduler status
bench doctor

# View scheduled job log
bench --site mysite execute frappe.utils.scheduler.get_enabled_scheduler_events
```
