# Queue Types Reference

Complete referentie voor Frappe queue configuratie.

## Default Queues

| Queue | Default Timeout | Gebruik |
|-------|-----------------|---------|
| `short` | 300s (5 min) | Snelle taken, UI responses |
| `default` | 300s (5 min) | Standaard taken |
| `long` | 1500s (25 min) | Heavy processing, imports |

## Queue Selectie Criteria

### short Queue

```python
# Snelle operaties die UI niet mogen blokkeren
frappe.enqueue('myapp.tasks.quick_update', queue='short')
```

Gebruik voor:
- Cache invalidation
- Kleine notificaties
- Quick lookups
- Taken < 1 minuut

### default Queue

```python
# Standaard taken
frappe.enqueue('myapp.tasks.process_order', queue='default')
```

Gebruik voor:
- Email verzending
- Document processing
- API calls
- Taken 1-5 minuten

### long Queue

```python
# Heavy processing
frappe.enqueue('myapp.tasks.generate_report', queue='long')
```

Gebruik voor:
- Data imports
- Bulk operaties
- Report generatie
- Taken > 5 minuten

## Custom Queues Configureren

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

### Gebruik Custom Queue

```python
frappe.enqueue(
    'myapp.tasks.generate_annual_report',
    queue='reports',
    timeout=7200
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
# Worker consumeert van meerdere queues
bench worker --queue short,default
bench worker --queue long
```

### Priority Volgorde

Worker verwerkt queues in opgegeven volgorde:

```bash
# short heeft prioriteit over default
bench worker --queue short,default
```

## Burst Mode

Tijdelijke worker die stopt als queue leeg is:

```bash
bench worker --queue short --burst
```

Gebruik voor:
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
    timeout=7200  # 2 uur (override 25 min default)
)
```

## Queue Monitoring

### Via Desk

- **RQ Worker**: Toont worker status
- **RQ Job**: Toont jobs per queue

### Via CLI

```bash
# Queue status
bench doctor

# Specifieke queue info
bench execute frappe.utils.background_jobs.get_queue_info
```

## Scheduler Events en Queues

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

1. **Match queue aan verwachte duration**
   - < 1 min → short
   - 1-5 min → default
   - > 5 min → long

2. **Gebruik timeout parameter voor uitzonderingen**
   ```python
   frappe.enqueue(..., queue='long', timeout=3600)
   ```

3. **Monitor queue depths**
   - Veel pending jobs = meer workers nodig
   - Veel failed jobs = error handling verbeteren

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
