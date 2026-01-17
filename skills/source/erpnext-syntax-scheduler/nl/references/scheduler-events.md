# Scheduler Events Reference

Complete referentie voor scheduler_events in hooks.py.

## Event Types

| Event Type | Frequentie | Queue | Beschrijving |
|------------|------------|-------|--------------|
| `all` | Elke scheduler tick | default | Meest frequente event |
| `hourly` | Elk uur | default | Standaard per-uur jobs |
| `daily` | Elke dag | default | Dagelijkse taken |
| `weekly` | Elke week | default | Wekelijkse taken |
| `monthly` | Elke maand | default | Maandelijkse taken |
| `hourly_long` | Elk uur | **long** | Langlopende per-uur jobs |
| `daily_long` | Elke dag | **long** | Langlopende dagelijkse jobs |
| `weekly_long` | Elke week | **long** | Langlopende wekelijkse jobs |
| `monthly_long` | Elke maand | **long** | Langlopende maandelijkse jobs |
| `cron` | Custom | Configureerbaar | Flexibele scheduling |

## Scheduler Tick Interval

| Versie | Interval | Config Key |
|--------|----------|------------|
| v14 | ~240 sec (4 min) | `scheduler_interval` |
| v15 | ~60 sec | `scheduler_tick_interval` |

## Complete Syntax

```python
# hooks.py
scheduler_events = {
    # Standaard events
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
┌─────────────── minuut (0 - 59)
│ ┌───────────── uur (0 - 23)
│ │ ┌─────────── dag van maand (1 - 31)
│ │ │ ┌───────── maand (1 - 12)
│ │ │ │ ┌─────── dag van week (0 - 6, zondag = 0)
│ │ │ │ │
* * * * *
```

### Symbolen

| Symbool | Betekenis | Voorbeeld |
|---------|-----------|-----------|
| `*` | Elke waarde | `* * * * *` = elke minuut |
| `,` | Lijst | `1,15 * * * *` = minuut 1 en 15 |
| `-` | Range | `1-5 * * * *` = minuut 1 t/m 5 |
| `/` | Interval | `*/10 * * * *` = elke 10 minuten |

### Voorbeelden

| Cron Expression | Betekenis |
|-----------------|-----------|
| `*/15 * * * *` | Elke 15 minuten |
| `0 * * * *` | Elk uur op :00 |
| `0 9 * * *` | Dagelijks om 9:00 |
| `0 9 * * 1-5` | Werkdagen om 9:00 |
| `0 0 * * 0` | Zondag om middernacht |
| `0 0 1 * *` | Eerste dag van maand |
| `0 0 1 1 *` | 1 januari om middernacht |
| `30 4 1,15 * *` | 1e en 15e van maand om 4:30 |

### Special Strings (v14/v15)

```python
"cron": {
    "annual": ["myapp.tasks.yearly_task"]  # Jaarlijks
}
```

## BELANGRIJK: bench migrate

Na ELKE wijziging in scheduler_events:

```bash
bench migrate
```

Zonder `bench migrate` worden wijzigingen NIET toegepast!

## Task Functie Structuur

```python
# myapp/tasks.py

def hourly_cleanup():
    """Scheduled task - draait als Administrator."""
    # Geen parameters nodig
    records = frappe.get_all("Log Entry", filters={"age": [">", 30]})
    for record in records:
        frappe.delete_doc("Log Entry", record.name)
    frappe.db.commit()

def daily_report():
    """Dagelijkse rapport generatie."""
    # Heavy work naar long queue
    frappe.enqueue(
        'myapp.tasks.generate_full_report',
        queue='long'
    )
```

## Meerdere Apps

Als meerdere apps dezelfde scheduler events definiëren:

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

**Resultaat**: Beide tasks draaien - ze worden samengevoegd.
