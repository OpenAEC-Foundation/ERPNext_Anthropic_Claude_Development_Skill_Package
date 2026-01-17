# Scheduler Events Reference

## Event Types Overzicht

```python
# hooks.py - Complete syntax
scheduler_events = {
    # Standaard events (default queue)
    "all": ["myapp.tasks.every_tick"],
    "hourly": ["myapp.tasks.hourly_task"],
    "daily": ["myapp.tasks.daily_task"],
    "weekly": ["myapp.tasks.weekly_task"],
    "monthly": ["myapp.tasks.monthly_task"],
    
    # Long queue events (voor heavy processing)
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
┌───────────── minuut (0 - 59)
│ ┌───────────── uur (0 - 23)
│ │ ┌───────────── dag van maand (1 - 31)
│ │ │ ┌───────────── maand (1 - 12)
│ │ │ │ ┌───────────── dag van week (0 - 6, zondag = 0)
│ │ │ │ │
* * * * *
```

### Cron Symbolen

| Symbool | Betekenis | Voorbeeld |
|---------|-----------|-----------|
| `*` | Elke waarde | `* * * * *` = elke minuut |
| `,` | Lijst | `1,15 * * * *` = minuut 1 en 15 |
| `-` | Range | `1-5 * * * *` = minuut 1 t/m 5 |
| `/` | Interval | `*/10 * * * *` = elke 10 minuten |

### Veelgebruikte Cron Patronen

```python
scheduler_events = {
    "cron": {
        # Elke 5 minuten
        "*/5 * * * *": ["myapp.tasks.frequent_check"],
        
        # Elke werkdag om 9:00
        "0 9 * * 1-5": ["myapp.tasks.workday_morning"],
        
        # Elke maandag om 8:00
        "0 8 * * 1": ["myapp.tasks.monday_report"],
        
        # Eerste dag van de maand om middernacht
        "0 0 1 * *": ["myapp.tasks.monthly_cleanup"],
        
        # Elke dag om 18:15
        "15 18 * * *": ["myapp.tasks.evening_summary"],
        
        # Elk uur van 9-17 op werkdagen
        "0 9-17 * * 1-5": ["myapp.tasks.business_hours"],
        
        # Special string (jaarlijks)
        "annual": ["myapp.tasks.yearly_archive"]
    }
}
```

## Scheduler Tick Interval

| Versie | Interval | Config Key |
|--------|----------|------------|
| v14 | ~240 sec (4 min) | `scheduler_interval` |
| v15 | ~60 sec | `scheduler_tick_interval` |

### Custom Tick Interval

In `common_site_config.json`:

```json
{
    "scheduler_tick_interval": 120
}
```

## Meerdere Methods Per Event

```python
scheduler_events = {
    "daily": [
        "myapp.tasks.cleanup_logs",
        "myapp.tasks.send_daily_report",
        "myapp.tasks.sync_external_data"
    ]
}
```

**Let op**: Executievolgorde is NIET gegarandeerd!

## KRITIEK: bench migrate

Na ELKE wijziging in `scheduler_events`:

```bash
bench migrate
```

Zonder `bench migrate` worden wijzigingen NIET toegepast!

## Runtime Configureerbare Events

Voor events die zonder code-deploy aangepast moeten worden:

```python
# Maak Scheduler Event record
sch_eve = frappe.new_doc("Scheduler Event")
sch_eve.scheduled_against = "Payment Reconciliation"
sch_eve.save()

# Maak Scheduled Job Type
job = frappe.new_doc("Scheduled Job Type")
job.frequency = "Cron"
job.scheduler_event = sch_eve.name
job.cron_format = "0/5 * * * *"  # Elke 5 minuten
job.save()
```

## Event Debugging

```bash
# Check scheduler status
bench doctor

# Bekijk scheduled job log
bench --site mysite execute frappe.utils.scheduler.get_enabled_scheduler_events
```
