# Research Document: Scheduler & Background Jobs (Fase 2.5)

> **Doel**: VerifiÃ«ren, verdiepen en actualiseren van informatie uit erpnext-vooronderzoek.md sectie 7 (Background Jobs & Scheduler) voor Frappe v14/v15.

---

## Bronnen Geraadpleegd

| Bron | URL/Locatie | Type |
|------|-------------|------|
| Frappe Docs - Background Jobs | docs.frappe.io/framework/user/en/api/background_jobs | Primair |
| Frappe Docs - Background Jobs v15 | docs.frappe.io/framework/v15/user/en/api/background_jobs | Primair |
| Frappe Docs - Running Background Jobs | docs.frappe.io/framework/user/en/guides/app-development/running-background-jobs | Primair |
| Frappe Docs - Hooks | docs.frappe.io/framework/user/en/python-api/hooks | Primair |
| Frappe Docs - Profiling and Monitoring | docs.frappe.io/framework/user/en/profiling | Primair |
| Frappe Docs - Diagnosing Scheduler | docs.frappe.io/framework/user/en/bench/guides/diagnosing-the-scheduler | Primair |
| Frappe Docs - Email Notifications Failed Jobs | docs.frappe.io/framework/v14/user/en/guides/deployment/email-notifications-for-failed-background-jobs | Primair |
| Frappe Docs - Directory Structure | docs.frappe.io/framework/user/en/basics/directory-structure | Primair |
| Frappe GitHub - background_jobs.py | github.com/frappe/frappe/blob/develop/frappe/utils/background_jobs.py | Verificatie |
| Frappe GitHub - Migrating to v15 | github.com/frappe/frappe/wiki/Migrating-to-Version-15 | Verificatie |
| erpnext-vooronderzoek.md | Project bestand | Basis |

---

## 1. SCHEDULER_EVENTS (hooks.py)

### Beschikbare Event Types

Scheduler events worden gedefinieerd in `hooks.py` en draaien periodiek op de achtergrond.

| Event Type | Frequentie | Worker Queue | Beschrijving |
|------------|------------|--------------|--------------|
| `all` | Elke scheduler tick | default | Meest frequente event |
| `hourly` | Elk uur | default | Standaard per-uur jobs |
| `daily` | Elke dag | default | Dagelijkse taken |
| `weekly` | Elke week | default | Wekelijkse taken |
| `monthly` | Elke maand | default | Maandelijkse taken |
| `hourly_long` | Elk uur | **long** | Langlopende per-uur jobs |
| `daily_long` | Elke dag | **long** | Langlopende dagelijkse jobs |
| `weekly_long` | Elke week | **long** | Langlopende wekelijkse jobs |
| `monthly_long` | Elke maand | **long** | Langlopende maandelijkse jobs |
| `cron` | Custom cron | Configureerbaar | Flexibele scheduling |

### Scheduler Tick Interval (VERSIEVERSCHIL!)

| Versie | `all` event interval | Config key |
|--------|---------------------|------------|
| v14 | ~4 minuten (240s) | `scheduler_interval` |
| v15 | ~60 seconden | `scheduler_tick_interval` |

**BELANGRIJK**: In v15 is de default scheduler tick verlaagd van 4 minuten naar 60 seconden!

### Basis Syntax

```python
# hooks.py
scheduler_events = {
    "all": [
        "myapp.tasks.every_tick"
    ],
    "hourly": [
        "myapp.tasks.hourly_cleanup"
    ],
    "daily": [
        "myapp.tasks.daily_report"
    ],
    "daily_long": [
        "myapp.tasks.heavy_processing"  # Draait op long queue
    ],
    "weekly": [
        "myapp.tasks.weekly_summary"
    ],
    "monthly": [
        "myapp.tasks.monthly_archive"
    ]
}
```

### Cron Syntax

Cron events gebruiken standaard cron syntax (5 velden) geparst door [croniter](https://pypi.org/project/croniter/).

```python
# hooks.py
scheduler_events = {
    "cron": {
        # Minuut Uur Dag Maand Weekdag
        "*/15 * * * *": [
            "myapp.tasks.every_15_minutes"
        ],
        "0 9 * * 1-5": [
            "myapp.tasks.weekday_morning_9am"
        ],
        "0 0 1 * *": [
            "myapp.tasks.first_of_month_midnight"
        ],
        "15 18 * * *": [
            "myapp.tasks.daily_at_6_15pm"
        ],
        # Special string (v14/v15)
        "annual": [
            "myapp.tasks.yearly_task"
        ]
    }
}
```

### Cron Syntax Referentie

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ minuut (0 - 59)
â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ uur (0 - 23)
â”‚ â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ dag van de maand (1 - 31)
â”‚ â”‚ â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ maand (1 - 12)
â”‚ â”‚ â”‚ â”‚ â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ dag van de week (0 - 6) (zondag = 0)
â”‚ â”‚ â”‚ â”‚ â”‚
* * * * *
```

| Symbool | Betekenis | Voorbeeld |
|---------|-----------|-----------|
| `*` | Elke waarde | `* * * * *` = elke minuut |
| `,` | Lijst | `1,15 * * * *` = minuut 1 en 15 |
| `-` | Range | `1-5 * * * *` = minuut 1 t/m 5 |
| `/` | Interval | `*/10 * * * *` = elke 10 minuten |

### BELANGRIJK: bench migrate na wijzigingen

```bash
# Na elke wijziging in scheduler_events:
bench migrate
```

Zonder `bench migrate` worden wijzigingen in `hooks.py` scheduler_events NIET toegepast!

---

## 2. FRAPPE.ENQUEUE - Complete API

### Alle Parameters (v14/v15 geverifieerd)

```python
frappe.enqueue(
    method,                      # Python functie of module path als string (VERPLICHT)
    queue="default",             # Queue: "short", "default", "long", of custom
    timeout=None,                # Custom timeout in seconden
    is_async=True,               # False = execute direct (niet in worker)
    now=False,                   # True = execute via frappe.call() direct
    job_name=None,               # [DEPRECATED in v15] Naam voor identificatie
    job_id=None,                 # [v15+] Unieke ID voor deduplicatie
    enqueue_after_commit=False,  # Wacht op DB commit voor enqueue
    at_front=False,              # Plaats job vooraan in queue
    on_success=None,             # Callback bij success
    on_failure=None,             # Callback bij failure
    **kwargs                     # Argumenten voor de method
)
```

### Parameter Details

| Parameter | Type | Default | Beschrijving |
|-----------|------|---------|--------------|
| `method` | str/callable | - | Module path of functie object |
| `queue` | str | "default" | Target queue naam |
| `timeout` | int/None | None | Override queue timeout (seconden) |
| `is_async` | bool | True | False = synchrone executie |
| `now` | bool | False | True = direct via frappe.call() |
| `job_name` | str/None | None | **DEPRECATED v15** - gebruik job_id |
| `job_id` | str/None | None | **v15+** Unieke ID voor deduplicatie |
| `enqueue_after_commit` | bool | False | Wacht tot DB commit |
| `at_front` | bool | False | Priority placement |
| `on_success` | callable/None | None | Success callback |
| `on_failure` | callable/None | None | Failure callback |
| `**kwargs` | any | - | Doorgegeven aan method |

### Return Value

```python
# frappe.enqueue retourneert een RQ Job object (als enqueue_after_commit=False)
job = frappe.enqueue('myapp.tasks.process', param='value')
print(job.id)  # Job ID
```

**Let op**: Als `enqueue_after_commit=True`, retourneert de call `None` omdat de job pas na commit wordt toegevoegd.

### Voorbeelden

```python
# Basis gebruik
frappe.enqueue('myapp.tasks.process_data', customer='CUST-001')

# Met functie object
def my_task(name, value):
    pass

frappe.enqueue(my_task, name='test', value=123)

# Met custom timeout op long queue
frappe.enqueue(
    'myapp.tasks.heavy_report',
    queue='long',
    timeout=3600,  # 1 uur
    report_type='annual'
)

# Met callbacks (v14/v15)
def on_success_handler(job, connection, result, *args, **kwargs):
    frappe.publish_realtime('show_alert', {'message': 'Job completed!'})

def on_failure_handler(job, connection, type, value, traceback):
    frappe.log_error(f"Job {job.id} failed: {value}")

frappe.enqueue(
    'myapp.tasks.risky_operation',
    on_success=on_success_handler,
    on_failure=on_failure_handler
)

# Enqueue na database commit
frappe.enqueue(
    'myapp.tasks.send_notification',
    enqueue_after_commit=True,  # Pas na commit
    user=frappe.session.user
)
```

---

## 3. FRAPPE.ENQUEUE_DOC

Enqueue een controller method van een specifiek document.

### Syntax

```python
frappe.enqueue_doc(
    doctype,           # DocType naam
    name=None,         # Document name (None voor nieuwe docs)
    method=None,       # Controller method naam als string
    queue="default",   # Queue naam
    timeout=300,       # Timeout in seconden
    now=False,         # Direct uitvoeren
    **kwargs           # Extra argumenten voor de method
)
```

### Voorbeeld

```python
# In controller
class SalesInvoice(Document):
    @frappe.whitelist()
    def send_notification(self, recipient, message):
        # Langlopende email operatie
        pass

# Aanroepen via enqueue_doc
frappe.enqueue_doc(
    "Sales Invoice",
    "SINV-00001",
    "send_notification",
    queue="long",
    timeout=600,
    recipient="user@example.com",
    message="Your invoice is ready"
)
```

### Document queue_action Method

Alternatieve manier om een controller method async uit te voeren:

```python
# In controller
class SalesOrder(Document):
    def on_submit(self):
        # Queue heavy processing
        self.queue_action('send_emails', emails=email_list, message='Howdy')
    
    def send_emails(self, emails, message):
        # Heavy operation
        pass
```

---

## 4. QUEUE TYPES EN TIMEOUTS

### Default Queues

| Queue | Default Timeout | Gebruik |
|-------|-----------------|---------|
| `short` | 300s (5 min) | Snelle taken, UI responses |
| `default` | 300s (5 min) | Standaard taken |
| `long` | 1500s (25 min) | Heavy processing, imports |

### Custom Queues Configureren

In `common_site_config.json`:

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
        }
    }
}
```

### Worker Processen

Default Procfile configuratie:

```
worker_short: bench worker --queue short --quiet
worker_default: bench worker --queue default --quiet
worker_long: bench worker --queue long --quiet
```

**Multi-queue consumption** (v14/v15):

```bash
# Worker consumeert van meerdere queues
bench worker --queue short,default
bench worker --queue long
```

### Burst Mode

Tijdelijke worker die stopt als queue leeg is:

```bash
bench worker --queue short --burst
```

---

## 5. JOB DEDUPLICATIE (VERSIEVERSCHIL!)

### v14: job_name (DEPRECATED)

```python
# v14 pattern - NIET MEER GEBRUIKEN
from frappe.core.page.background_jobs.background_jobs import get_info
enqueued_jobs = [d.get("job_name") for d in get_info()]
if self.name not in enqueued_jobs:
    frappe.enqueue(..., job_name=self.name)
```

### v15+: job_id met is_job_enqueued

```python
# v15+ pattern - AANBEVOLEN
from frappe.utils.background_jobs import is_job_enqueued

job_id = f"data_import::{self.name}"
if not is_job_enqueued(job_id):
    frappe.enqueue(
        'myapp.tasks.import_data',
        job_id=job_id,
        doc_name=self.name
    )
```

### is_job_enqueued Functie (v15+)

```python
from frappe.utils.background_jobs import is_job_enqueued

# Check of job al in queue staat
if is_job_enqueued(job_id="unique-job-id"):
    print("Job already queued")
```

---

## 6. ERROR HANDLING

### Wat Gebeurt Bij Job Failure

1. **Exception wordt gelogd** in:
   - `Scheduler Log` DocType (desk)
   - `logs/worker.error.log` bestand

2. **Lock file mechanisme**:
   - Scheduler houdt lock file bij
   - Bij crash blijft lock file bestaan
   - `LockTimeoutError` na 10 minuten inactieve lock

3. **Job status wordt "failed"** in RQ

### Correct Error Handling Pattern

```python
def process_records(records, notify_user=False):
    for record in records:
        try:
            process_single(record)
            frappe.db.commit()  # Commit per success
        except Exception:
            frappe.db.rollback()  # Rollback bij error
            frappe.log_error(
                frappe.get_traceback(),
                f"Process Error for {record}"
            )
    
    if notify_user:
        frappe.publish_realtime(
            'show_alert',
            {'message': 'Processing complete', 'indicator': 'green'},
            user=frappe.session.user
        )
```

### Email Notificaties voor Failed Jobs

In `sites/common_site_config.json`:

```json
{
    "celery_error_emails": {
        "ADMINS": [
            ["Admin Name", "admin@example.com"]
        ],
        "SERVER_EMAIL": "errors@example.com"
    }
}
```

**Let op**: Gebruikt lokale mailserver op port 25.

### frappe.log_error

```python
# Standaard error logging
frappe.log_error(
    message="Error processing record",
    title="Background Job Error"
)

# Met traceback
frappe.log_error(
    message=frappe.get_traceback(),
    title="Process Failed"
)
```

---

## 7. MONITORING

### RQ Worker DocType (Virtual)

Toont alle background workers:
- Worker naam
- Status (busy/idle)
- Successful/failed job counts
- Timing informatie

Toegang: **Search > RQ Worker**

### RQ Job DocType (Virtual)

Toont alle background jobs:
- Filter op queue
- Filter op status (queued, started, finished, failed)
- Job details en exception info

Toegang: **Search > RQ Job**

### Job Statuses

| Status | Betekenis |
|--------|-----------|
| `queued` | In wachtrij |
| `started` | Wordt uitgevoerd |
| `finished` | Succesvol afgerond |
| `failed` | Mislukt (exception) |

### Scheduled Job Log

DocType dat scheduler job executions bijhoudt:
- Execution time
- Method naam
- Status
- Error messages

### Bench Doctor Command

```bash
bench doctor
```

Output:
- Scheduler status per site
- Aantal workers
- Pending tasks

### Monitor Feature

In `site_config.json`:

```json
{
    "monitor": 1
}
```

Logt naar `logs/monitor.json.log`:

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

### Stuck Worker Debug

```bash
# Stuur SIGUSR1 naar worker voor stack trace
kill -SIGUSR1 <WORKER_PID>
```

Output gaat naar `logs/worker.error.log`.

---

## 8. CONFIGURABLE SCHEDULER EVENTS (Runtime)

Voor user-configureerbare intervallen zonder hooks.py:

```python
# Create Scheduler Event record
sch_eve = frappe.new_doc("Scheduler Event")
sch_eve.scheduled_against = "Process Payment Reconciliation"
sch_eve.save()

# Create Scheduled Job Type
job = frappe.new_doc("Scheduled Job Type")
job.frequency = "Cron"
job.scheduler_event = sch_eve.name
job.cron_format = "0/5 * * * *"  # Elke 5 minuten
job.save()
```

**Voordeel**: Interval kan later aangepast worden zonder `bench migrate`.

---

## 9. SCHEDULER USER CONTEXT

**BELANGRIJK**: Alle scheduled jobs draaien als **Administrator** user!

```python
# Jobs zijn owned by Administrator
def scheduled_task():
    print(frappe.session.user)  # "Administrator"
    
    # Documents gemaakt in scheduled job:
    doc = frappe.new_doc("ToDo")
    doc.description = "Created by scheduler"
    doc.insert()
    # doc.owner = "Administrator"
```

Om andere owner te zetten:

```python
def scheduled_task():
    doc = frappe.new_doc("ToDo")
    doc.owner = "specific.user@example.com"
    doc.insert(ignore_permissions=True)
```

---

## 10. BEST PRACTICES

### DO's

```python
# âœ… Commit per succesvol record
for record in records:
    try:
        process(record)
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        frappe.log_error()

# âœ… Gebruik juiste queue voor job duration
frappe.enqueue(..., queue='long')  # Voor heavy tasks

# âœ… Geef user feedback via realtime
frappe.publish_realtime('show_alert', {'message': 'Done!'})

# âœ… Gebruik job_id voor deduplicatie (v15)
frappe.enqueue(..., job_id=f"import::{doc.name}")

# âœ… Log errors met context
frappe.log_error(f"Failed for {record.name}: {error}")
```

### DON'Ts

```python
# âŒ Geen commit in short-running tasks
def quick_task():
    frappe.db.commit()  # Niet nodig, framework handelt het

# âŒ Geen blocking operations in web request
def api_handler():
    heavy_processing()  # Blokkeert user
    # Gebruik frappe.enqueue() in plaats

# âŒ job_name gebruiken voor deduplicatie (deprecated)
frappe.enqueue(..., job_name="my-job")  # v14 pattern

# âŒ Aannames over executie volgorde
# Jobs kunnen parallel draaien op meerdere workers!
```

---

## 11. VERSIE VERSCHILLEN (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| Scheduler tick interval | 4 min (~240s) | 60 sec |
| Config key | `scheduler_interval` | `scheduler_tick_interval` |
| Job deduplicatie | `job_name` | `job_id` + `is_job_enqueued()` |
| Callback support | Basic | `on_success`, `on_failure` |
| RQ Job/Worker doctypes | Beschikbaar | Verbeterd |

### Migratie v14 â†’ v15

```python
# v14 (deprecated)
from frappe.core.page.background_jobs.background_jobs import get_info
enqueued_jobs = [d.get("job_name") for d in get_info()]
if self.name not in enqueued_jobs:
    frappe.enqueue(..., job_name=self.name)

# v15 (aanbevolen)
from frappe.utils.background_jobs import is_job_enqueued
job_id = f"data_import::{self.name}"
if not is_job_enqueued(job_id):
    frappe.enqueue(..., job_id=job_id)
```

---

## 12. ANTI-PATTERNS

### âŒ Heavy processing in scheduler callback

```python
# FOUT - blokkeert scheduler
scheduler_events = {
    "all": ["myapp.tasks.process_millions_of_records"]
}

# GOED - enqueue naar long queue
def every_tick():
    frappe.enqueue('myapp.tasks.process_millions', queue='long')
```

### âŒ Infinite retry zonder backoff

```python
# FOUT - kan overload veroorzaken
def task_with_retry():
    try:
        external_api()
    except Exception:
        frappe.enqueue('myapp.task_with_retry')  # Direct retry
```

### âŒ Geen error handling

```python
# FOUT - hele batch faalt bij Ã©Ã©n error
def process_all(records):
    for r in records:
        process(r)  # Ã‰Ã©n failure stopt alles

# GOED - graceful degradation
def process_all(records):
    for r in records:
        try:
            process(r)
            frappe.db.commit()
        except Exception:
            frappe.log_error()
            frappe.db.rollback()
```

### âŒ Blocking wait op job completion

```python
# FOUT - blokkeert web request
job = frappe.enqueue('myapp.heavy_task')
while job.get_status() != 'finished':
    time.sleep(1)  # Blokkeert!

# GOED - gebruik realtime events of polling endpoint
frappe.enqueue(
    'myapp.heavy_task',
    on_success=lambda: frappe.publish_realtime('task_done')
)
```

---

## Samenvatting voor Skill Creatie

### Key Learnings

1. **Scheduler events** in hooks.py vereisen `bench migrate` na wijzigingen
2. **Drie default queues**: short, default, long met verschillende timeouts
3. **v15 breaking change**: `job_name` deprecated, gebruik `job_id` + `is_job_enqueued()`
4. **Scheduler tick interval** verlaagd van 4 min (v14) naar 60 sec (v15)
5. **Jobs draaien als Administrator** - expliciet owner zetten indien nodig
6. **Error handling**: altijd try/except met commit/rollback per record
7. **Monitoring via** RQ Worker/RQ Job virtual doctypes en bench doctor

### Skill References te Maken

1. `scheduler-events.md` - Alle event types met cron syntax
2. `enqueue-api.md` - Complete frappe.enqueue/enqueue_doc parameters
3. `queues.md` - Queue types, timeouts, custom queues
4. `error-handling.md` - Error patterns en logging
5. `monitoring.md` - RQ doctypes, bench commands, logging
6. `examples.md` - Complete werkende voorbeelden
7. `anti-patterns.md` - Wat te vermijden
