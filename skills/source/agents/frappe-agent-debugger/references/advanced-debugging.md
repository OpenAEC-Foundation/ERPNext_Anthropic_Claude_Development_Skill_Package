# Advanced Debugging Reference

## VS Code Debug Adapter Protocol (DAP)

### launch.json for Frappe Bench

Create `.vscode/launch.json` in the `frappe-bench/apps/frappe` directory:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Bench Web",
            "type": "python",
            "request": "launch",
            "justMyCode": false,
            "program": "${workspaceFolder}/frappe/frappe/utils/bench_helper.py",
            "args": [
                "frappe", "serve", "--port", "8000", "--noreload", "--nothreading"
            ],
            "python": "${workspaceFolder}/../env/bin/python",
            "cwd": "${workspaceFolder}/../sites",
            "env": {
                "DEV_SERVER": "1"
            }
        }
    ]
}
```

### Configuration Notes

| Flag | Why Required |
|------|-------------|
| `--noreload` | Disables Werkzeug autoreload — VS Code debugger cannot attach to reloaded processes |
| `--nothreading` | Disables multithreading — breakpoints only work reliably in single-threaded mode |
| `DEV_SERVER: "1"` | Required for Socket.io when running `bench serve` directly instead of `bench start` |
| `justMyCode: false` | Allows stepping into Frappe framework code, not just your app code |

### Attaching to Gunicorn Workers

For production-like debugging, attach to a running gunicorn worker:

```json
{
    "name": "Attach to Gunicorn",
    "type": "python",
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    },
    "justMyCode": false,
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}",
            "remoteRoot": "/home/frappe/frappe-bench/apps/frappe"
        }
    ]
}
```

To enable, add `debugpy` to the gunicorn worker:

```python
# In your app's __init__.py or a startup hook (TEMPORARY — remove after debugging)
import debugpy
debugpy.listen(("0.0.0.0", 5678))
# debugpy.wait_for_client()  # Uncomment to pause until debugger connects
```

Install debugpy: `bench pip install debugpy`

**WARNING**: NEVER leave debugpy in production code. ALWAYS remove after debugging.

### Debug Configuration for Background Workers

Background jobs (RQ workers) run in separate processes. To debug:

```json
{
    "name": "Bench Worker",
    "type": "python",
    "request": "launch",
    "justMyCode": false,
    "program": "${workspaceFolder}/../env/bin/bench",
    "args": [
        "worker", "--queue", "default"
    ],
    "python": "${workspaceFolder}/../env/bin/python",
    "cwd": "${workspaceFolder}/../sites",
    "env": {
        "DEV_SERVER": "1"
    }
}
```

### Breakpoints in Python Controllers

1. Open the controller file (e.g., `apps/erpnext/erpnext/accounts/doctype/sales_invoice/sales_invoice.py`)
2. Set breakpoints on lines inside lifecycle methods (`validate`, `on_submit`, etc.)
3. Start the "Bench Web" debug configuration
4. Trigger the action in browser (save, submit the document)
5. VS Code pauses at the breakpoint — inspect `self.doc`, `frappe.session`, local variables

**Alternative — pdb inline breakpoints** (when VS Code is not available):

```python
def validate(self):
    import pdb; pdb.set_trace()  # Execution pauses here in terminal
    # Or for Python 3.7+:
    breakpoint()
```

ALWAYS use `--noreload --nothreading` with pdb, otherwise the terminal is unusable.

---

## bench console — Advanced Usage

### Starting the Console

```bash
bench --site mysite console
```

Opens an iPython shell (or standard Python shell) with Frappe initialized and connected to the site database.

### Document Inspection Patterns

```python
# Fetch and inspect a document
doc = frappe.get_doc("Sales Invoice", "SINV-00001")
doc.as_dict()              # Full document as dictionary
doc.items                  # Child table rows
doc.docstatus              # 0=Draft, 1=Submitted, 2=Cancelled
doc.meta.get_field("customer")  # Field metadata

# List documents with filters
frappe.get_all("Sales Invoice",
    filters={"docstatus": 1, "customer": "Test Customer"},
    fields=["name", "grand_total", "posting_date"],
    order_by="posting_date desc",
    limit=10
)

# Check if document exists
frappe.db.exists("Sales Invoice", "SINV-00001")

# Get single value
frappe.db.get_value("Sales Invoice", "SINV-00001", "grand_total")
```

### Direct SQL Queries

```python
# Raw SQL (returns list of tuples)
frappe.db.sql("SELECT name, grand_total FROM `tabSales Invoice` LIMIT 5")

# With as_dict for named access
frappe.db.sql("SELECT name, grand_total FROM `tabSales Invoice` LIMIT 5", as_dict=True)

# Parameterized queries (ALWAYS use this — prevents SQL injection)
frappe.db.sql(
    "SELECT name FROM `tabSales Invoice` WHERE customer = %s AND docstatus = %s",
    ("Test Customer", 1),
    as_dict=True
)

# Count records
frappe.db.count("Sales Invoice", filters={"docstatus": 1})
```

### Permission Testing

```python
# Switch user context for permission testing
frappe.set_user("user@example.com")

# Check what this user can see
frappe.get_all("Sales Invoice", limit=5)  # Respects user permissions

# Check specific permission
frappe.has_permission("Sales Invoice", "read", doc="SINV-00001")
frappe.has_permission("Sales Invoice", "write", user="user@example.com")

# Inspect user roles
frappe.get_roles("user@example.com")

# Reset back to Administrator
frappe.set_user("Administrator")
```

### Hook and Configuration Inspection

```python
# View all doc_events hooks
import json
print(json.dumps(frappe.get_hooks("doc_events"), indent=2))

# View scheduler events
print(json.dumps(frappe.get_hooks("scheduler_events"), indent=2))

# View active Server Scripts
frappe.get_all("Server Script",
    filters={"disabled": 0},
    fields=["name", "script_type", "reference_doctype", "doctype_event"]
)

# View site configuration
frappe.conf  # Entire site_config.json as object
frappe.conf.db_name
frappe.conf.get("monitor")
```

### Running Methods Directly

```python
# Call a whitelisted method
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
result = make_delivery_note("SINV-00001")

# Trigger a document method
doc = frappe.get_doc("Sales Invoice", "SINV-00001")
doc.run_method("validate")  # Run validate without saving

# Test enqueued jobs
from myapp.mymodule import my_long_task
my_long_task()  # Run synchronously in console for debugging
```

---

## mariadb Console — Direct Database Access

### Starting the Console

```bash
bench --site mysite mariadb
```

Opens a MariaDB/MySQL shell connected to the site database.

### Common Diagnostic Queries

```sql
-- Check table structure
DESCRIBE `tabSales Invoice`;
SHOW CREATE TABLE `tabSales Invoice`;

-- Check indexes (important for query performance)
SHOW INDEX FROM `tabSales Invoice`;

-- Check table sizes
SELECT
    table_name,
    ROUND(data_length / 1024 / 1024, 2) AS data_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_mb,
    table_rows
FROM information_schema.tables
WHERE table_schema = DATABASE()
ORDER BY data_length DESC
LIMIT 20;

-- Recent Error Log entries
SELECT name, method, error, creation
FROM `tabError Log`
ORDER BY creation DESC
LIMIT 10;

-- Check recent schema changes (Patch Log)
SELECT name, creation
FROM `tabPatch Log`
ORDER BY creation DESC
LIMIT 10;

-- Find orphaned child table records
SELECT ct.name
FROM `tabSales Invoice Item` ct
LEFT JOIN `tabSales Invoice` p ON ct.parent = p.name
WHERE p.name IS NULL;

-- Check active sessions
SELECT user, device, last_request, status
FROM `tabSessions`
WHERE TIMESTAMPDIFF(MINUTE, last_request, NOW()) < 30;

-- Inspect naming series counters
SELECT * FROM `tabSeries` WHERE name LIKE 'SINV%';

-- Check for locked documents
SELECT name, modified_by, modified
FROM `tabSales Invoice`
WHERE _locked = 1;
```

### Schema Verification

```sql
-- Verify a column exists after bench migrate
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'tabSales Invoice'
  AND COLUMN_NAME = 'custom_field_name';

-- Compare DocType definition vs actual table
-- (run in bench console, not mariadb)
-- frappe.get_meta("Sales Invoice").get_field("fieldname")
```

---

## Profiling and Monitoring

### Frappe Recorder — Request/SQL Profiler

The Recorder captures requests and background jobs with full SQL query details.

**How to use:**

1. Login as Administrator
2. Open "Recorder" from Awesomebar
3. Click **Start** (optionally enable cProfile for Python profiling)
4. Perform the action to profile in another browser tab
5. Click **Stop**
6. Click on a captured request to inspect

**What each capture shows:**

| Field | Description |
|-------|-------------|
| Path | URL or API endpoint hit |
| Command | Dotted path to the Python method executed |
| Duration | Total request time |
| Queries | Number of SQL queries |
| Query time | Time spent in database |
| Headers | Full request headers |
| Form data | POST data sent |

**Per-query details:**

- Exact SQL query text
- Query duration
- Full Python stack trace (shows which code triggered the query)
- `EXPLAIN` output (query execution plan)

**cProfile mode**: Enable the cProfile checkbox to get Python function-level profiling. This adds significant overhead — disable immediately after debugging.

**Export/Import**: Captures can be exported as JSON and imported on another site for offline analysis.

**WARNING**: Recorder adds overhead. NEVER leave it running in production.

### bench CLI Profiling

Profile a specific method from the command line:

```bash
# Profile a server method
bench --site mysite --profile execute erpnext.projects.doctype.task.task.set_tasks_as_overdue

# Profile a database method
bench --site mysite execute frappe.db.get_database_size
```

### bench doctor — Health Check

```bash
bench doctor
```

Checks:
- Scheduler status (enabled/disabled)
- Worker status (running/stopped)
- Failed background jobs in RQ queues
- Pending jobs count

Use this FIRST when diagnosing scheduler or background job issues.

### Monitor Module

Enable request/job monitoring by adding to `site_config.json`:

```json
{
    "monitor": 1
}
```

Logs request and job metadata to `sites/{site}/logs/monitor.json.log`.

**Sample request entry:**
```json
{
    "duration": 807142,
    "request": {
        "ip": "127.0.0.1",
        "method": "GET",
        "path": "/api/method/frappe.realtime.get_user_info"
    },
    "transaction_type": "request"
}
```

**Sample job entry:**
```json
{
    "duration": 1364,
    "job": {
        "method": "frappe.ping",
        "scheduled": false
    },
    "transaction_type": "job"
}
```

Data is buffered in Redis and flushed periodically via `frappe.monitor.flush`.

### System Health Report

Search "System Health Report" in the Awesomebar. Checks:
- Background jobs status
- Scheduler health
- Database connectivity
- Cache (Redis) status
- Email queue
- Error log volume
- Storage usage
- Backup status

### RQ Job Monitoring

Two virtual doctypes accessible from the Desk:

- **RQ Worker**: Shows all workers, their status, current job, and job counts
- **RQ Job**: Shows all background jobs, filterable by queue and status (queued, started, failed, finished)

### Debugging Stuck Processes

Send SIGUSR1 to print thread stack traces:

```bash
kill -SIGUSR1 <PID>
```

Stack traces appear in:
- Web workers: `bench/logs/web.error.log`
- Background workers: `bench/logs/worker.error.log`
- Scheduler: `bench/logs/schedule.error.log`

---

## Quick Reference: Which Tool When

| Scenario | Tool |
|----------|------|
| Python error in controller | VS Code breakpoints + bench console |
| Slow API response | Frappe Recorder (check SQL count + query time) |
| Background job failing | `bench doctor` + worker logs |
| Permission issue | `bench console` + `frappe.set_user()` + `frappe.has_permission()` |
| Schema mismatch | `bench mariadb` + `DESCRIBE` + `bench migrate` |
| Memory/CPU issues | Monitor module + System Health Report |
| Stuck process | `kill -SIGUSR1 <PID>` + error logs |
| Intermittent failure | Monitor module (`monitor.json.log`) + Error Log DocType |
