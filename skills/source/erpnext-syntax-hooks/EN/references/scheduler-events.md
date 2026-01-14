# Scheduler Events Reference

Complete referentie voor `scheduler_events` in hooks.py.

---

## Syntax

```python
# In hooks.py
scheduler_events = {
    # Standaard periodes
    "hourly": [
        "myapp.tasks.hourly_cleanup"
    ],
    "daily": [
        "myapp.tasks.daily_report"
    ],
    
    # Long worker queue (voor zware taken)
    "daily_long": [
        "myapp.tasks.heavy_daily_task"
    ],
    
    # Cron syntax voor precise timing
    "cron": {
        "0 9 * * 1-5": [
            "myapp.tasks.weekday_morning_report"
        ]
    }
}
```

---

## Alle Event Types

### Standaard Periodes (Default Queue)

| Event | Frequentie | Timeout |
|-------|------------|---------|
| `all` | Elke ~60 seconden | 300s |
| `hourly` | Elk uur (:00) | 300s |
| `daily` | Elke dag (00:00) | 300s |
| `weekly` | Elke week (zondag 00:00) | 300s |
| `monthly` | Eerste dag van de maand (00:00) | 300s |

### Long Queue Varianten

| Event | Frequentie | Timeout |
|-------|------------|---------|
| `hourly_long` | Elk uur | 1500s |
| `daily_long` | Elke dag | 1500s |
| `weekly_long` | Elke week | 1500s |
| `monthly_long` | Elke maand | 1500s |

### Cron (Custom Timing)

| Syntax | Betekenis |
|--------|-----------|
| `"cron"` | Dict met cron expressions als keys |

---

## Cron Syntax

```
* * * * *
│ │ │ │ │
│ │ │ │ └── Dag van week (0-6, zondag=0)
│ │ │ └──── Maand (1-12)
│ │ └────── Dag van maand (1-31)
│ └──────── Uur (0-23)
└────────── Minuut (0-59)
```

### Cron Voorbeelden

```python
"cron": {
    # Elke 5 minuten
    "*/5 * * * *": ["myapp.tasks.frequent_check"],
    
    # Elk uur op :00
    "0 * * * *": ["myapp.tasks.hourly_exact"],
    
    # Dagelijks om 09:00
    "0 9 * * *": ["myapp.tasks.morning_report"],
    
    # Werkdagen om 09:00 (ma-vr)
    "0 9 * * 1-5": ["myapp.tasks.weekday_report"],
    
    # Elke zondag om 23:00
    "0 23 * * 0": ["myapp.tasks.weekly_cleanup"],
    
    # Eerste dag van de maand om 06:00
    "0 6 1 * *": ["myapp.tasks.monthly_report"],
    
    # Elke 15 minuten tijdens kantooruren
    "*/15 9-17 * * 1-5": ["myapp.tasks.business_hours_sync"],
    
    # Om 14:30 elke dag
    "30 14 * * *": ["myapp.tasks.afternoon_task"]
}
```

### Speciale Cron Waarden

| Waarde | Betekenis |
|--------|-----------|
| `*` | Elk (elke minuut, elk uur, etc.) |
| `*/n` | Elke n (*/5 = elke 5) |
| `n-m` | Range (1-5 = 1 t/m 5) |
| `n,m` | Lijst (1,15 = op 1 en 15) |

---

## Task Implementatie

### Basis Task

```python
# In myapp/tasks.py
import frappe

def daily_report():
    """Scheduled task - geen argumenten"""
    report = generate_report()
    frappe.sendmail(
        recipients=["manager@example.com"],
        subject="Daily Report",
        message=report
    )
```

### Task met Error Handling

```python
def hourly_sync():
    """Met error handling en logging"""
    try:
        records = frappe.get_all("Sync Queue", filters={"status": "Pending"})
        for record in records:
            process_sync(record.name)
            frappe.db.commit()  # Commit per record voor grote batches
    except Exception as e:
        frappe.log_error(
            title="Hourly Sync Failed",
            message=frappe.get_traceback()
        )
```

### Long Running Task

```python
def monthly_aggregation():
    """Gebruik _long variant voor zware taken"""
    # Dit kan tot 25 minuten duren (1500s timeout)
    for company in frappe.get_all("Company"):
        aggregate_data(company.name)
        frappe.db.commit()  # Commit per iteratie
```

---

## Queue Selectie

| Scenario | Gebruik | Reden |
|----------|---------|-------|
| Snelle check (<5 min) | `hourly`, `daily`, etc. | Default queue, 5 min timeout |
| Zware verwerking (5-25 min) | `hourly_long`, `daily_long`, etc. | Long queue, 25 min timeout |
| Precise timing nodig | `cron` | Exacte controle over timing |
| Zeer frequent (<1 uur) | `cron` met `*/n * * * *` | Standaard events zijn minimaal uur |

---

## Belangrijke Regels

### 1. bench migrate na Wijzigingen

```bash
# VERPLICHT na scheduler_events wijzigingen
bench --site sitename migrate
```

Scheduler events worden gecached. Zonder migrate worden wijzigingen niet opgepikt.

### 2. Geen Argumenten

```python
# FOUT - tasks krijgen geen argumenten
def my_task(some_arg):
    pass

# GOED - geen argumenten
def my_task():
    pass
```

### 3. Commit bij Lange Loops

```python
def process_all_invoices():
    invoices = frappe.get_all("Sales Invoice", limit=0)
    for inv in invoices:
        process_invoice(inv.name)
        frappe.db.commit()  # Voorkom memory buildup
```

---

## Complete Voorbeeld

```python
# hooks.py
scheduler_events = {
    # Snelle taken
    "hourly": [
        "myapp.tasks.check_pending_orders"
    ],
    "daily": [
        "myapp.tasks.send_daily_digest",
        "myapp.tasks.cleanup_temp_files"
    ],
    
    # Zware taken
    "daily_long": [
        "myapp.tasks.recalculate_all_balances"
    ],
    "weekly_long": [
        "myapp.tasks.generate_weekly_analytics"
    ],
    
    # Precise timing
    "cron": {
        # Werkdagen 09:00 - reminder emails
        "0 9 * * 1-5": [
            "myapp.tasks.send_payment_reminders"
        ],
        # Elke 30 min - sync met extern systeem
        "*/30 * * * *": [
            "myapp.tasks.sync_external_api"
        ],
        # Vrijdag 17:00 - week report
        "0 17 * * 5": [
            "myapp.tasks.weekly_summary"
        ]
    }
}
```

```python
# myapp/tasks.py
import frappe

def check_pending_orders():
    pending = frappe.db.count("Sales Order", {"status": "Draft"})
    if pending > 100:
        frappe.sendmail(
            recipients=["sales@example.com"],
            subject=f"Alert: {pending} pending orders"
        )

def send_daily_digest():
    for user in frappe.get_all("User", {"enabled": 1}):
        digest = compile_digest(user.name)
        if digest:
            frappe.sendmail(
                recipients=[user.name],
                subject="Your Daily Digest",
                message=digest
            )

def recalculate_all_balances():
    """Long running - use daily_long"""
    customers = frappe.get_all("Customer")
    for customer in customers:
        recalculate_balance(customer.name)
        frappe.db.commit()
```

---

## Debugging

### Handmatig Uitvoeren

```python
# In bench console
frappe.get_doc("Scheduled Job Type", "myapp.tasks.daily_report").execute()
```

### Logs Bekijken

```bash
# Scheduler logs
tail -f ~/frappe-bench/logs/scheduler.log

# Worker logs
tail -f ~/frappe-bench/logs/worker.log
```

### Status Checken

```python
# Check of scheduler draait
frappe.get_doc("Scheduled Job Type", "myapp.tasks.daily_report")
```

---

## Versie Verschillen

| Feature | v14 | v15 |
|---------|-----|-----|
| Alle standaard events | ✅ | ✅ |
| Cron syntax | ✅ | ✅ |
| `_long` varianten | ✅ | ✅ |
| Scheduler UI vernieuwd | - | ✅ |
