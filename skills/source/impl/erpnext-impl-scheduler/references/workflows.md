# Scheduler & Background Jobs - Implementation Workflows

> Step-by-step implementation patterns for all scheduling scenarios.

---

## Workflow 1: Basic Scheduled Task

**Goal**: Run a cleanup task daily

### Step 1: Create Task Module

```python
# myapp/tasks.py
import frappe

def daily_cleanup():
    """
    Clean up old temporary files daily.
    
    IMPORTANT:
    - NO arguments allowed for scheduler tasks!
    - Runs as Administrator user
    - Must be fast enough (<5 min for daily, <25 min for daily_long)
    """
    # Get cutoff date
    cutoff = frappe.utils.add_days(frappe.utils.nowdate(), -7)
    
    # Find old files
    old_files = frappe.get_all(
        "File",
        filters={
            "is_private": 1,
            "attached_to_doctype": "",
            "creation": ["<", cutoff]
        },
        pluck="name",
        limit=500  # Process in manageable batches
    )
    
    deleted = 0
    for file_name in old_files:
        try:
            frappe.delete_doc("File", file_name, ignore_permissions=True)
            deleted += 1
        except Exception:
            frappe.log_error(f"Could not delete file: {file_name}")
    
    frappe.db.commit()
    frappe.logger("scheduler").info(f"Daily cleanup: deleted {deleted} files")
```

### Step 2: Register in hooks.py

```python
# myapp/hooks.py
scheduler_events = {
    "daily": [
        "myapp.tasks.daily_cleanup"
    ]
}
```

### Step 3: Deploy and Enable

```bash
# REQUIRED: Migrate to register scheduler events
bench --site sitename migrate

# Enable scheduler if not already enabled
bench --site sitename scheduler enable

# Verify registration
bench --site sitename scheduler status
```

### Step 4: Verify in UI

```
1. Go to: Setup > Scheduled Job Type
2. Find: myapp.tasks.daily_cleanup
3. Check: Frequency = Daily, Stopped = No

4. Go to: Scheduled Job Log
5. After task runs, verify success/failure
```

---

## Workflow 2: Cron-Based Scheduled Task

**Goal**: Send summary email at 9am on weekdays

### Step 1: Create Task

```python
# myapp/tasks.py
import frappe

def weekday_summary_email():
    """Send daily summary at 9am weekdays."""
    
    # Generate summary data
    yesterday = frappe.utils.add_days(frappe.utils.nowdate(), -1)
    
    summary = {
        "new_orders": frappe.db.count(
            "Sales Order",
            {"creation": [">=", yesterday], "docstatus": 1}
        ),
        "new_invoices": frappe.db.count(
            "Sales Invoice",
            {"creation": [">=", yesterday], "docstatus": 1}
        ),
        "total_revenue": get_yesterday_revenue()
    }
    
    # Get recipients
    recipients = frappe.get_all(
        "User",
        filters={
            "enabled": 1,
            "user_type": "System User"
        },
        pluck="email"
    )
    
    # Send email
    frappe.sendmail(
        recipients=recipients,
        subject=f"Daily Summary - {yesterday}",
        message=frappe.render_template(
            "myapp/templates/emails/daily_summary.html",
            summary
        )
    )

def get_yesterday_revenue():
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND posting_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
    """)
    return result[0][0] if result else 0
```

### Step 2: Register with Cron Expression

```python
# myapp/hooks.py
scheduler_events = {
    "cron": {
        # At 9:00 AM, Monday through Friday
        "0 9 * * 1-5": [
            "myapp.tasks.weekday_summary_email"
        ]
    }
}
```

### Cron Expression Cheat Sheet

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *

Examples:
"0 9 * * 1-5"     → 9:00 AM, Monday-Friday
"0 0 * * *"       → Midnight daily
"0 0 1 * *"       → Midnight, 1st of month
"*/15 * * * *"    → Every 15 minutes
"0 */2 * * *"     → Every 2 hours
"30 8 * * 1"      → 8:30 AM every Monday
"0 18 * * 5"      → 6:00 PM every Friday
"0 0 15 * *"      → Midnight, 15th of month
```

### Step 3: Deploy

```bash
bench --site sitename migrate
```

---

## Workflow 3: User-Triggered Background Job

**Goal**: Export large dataset when user clicks button

### Step 1: Create Export Task

```python
# myapp/tasks.py
import frappe
import csv
from io import StringIO

def export_customers(user, filters=None):
    """
    Export customers to CSV file.
    
    Args:
        user: User who requested export (for notifications)
        filters: Optional dict of filters
    """
    # Set user context for permissions
    frappe.set_user(user)
    
    try:
        # Get data
        customers = frappe.get_all(
            "Customer",
            filters=filters or {},
            fields=["name", "customer_name", "customer_group", "territory", "email_id"],
            limit_page_length=0  # All records
        )
        
        if not customers:
            notify_user(user, "No customers found matching filters", "orange")
            return
        
        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=customers[0].keys())
        writer.writeheader()
        writer.writerows(customers)
        
        # Save file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"customers_export_{frappe.utils.nowdate()}.csv",
            "content": output.getvalue(),
            "is_private": 1
        })
        file_doc.insert(ignore_permissions=True)
        
        frappe.db.commit()
        
        # Notify user
        notify_user(
            user,
            f"Export complete! <a href='{file_doc.file_url}'>Download CSV</a> ({len(customers)} records)",
            "green"
        )
        
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Customer Export Failed")
        notify_user(user, "Export failed. Check Error Log.", "red")

def notify_user(user, message, indicator="blue"):
    """Send realtime notification to user."""
    frappe.publish_realtime(
        "msgprint",
        {"message": message, "indicator": indicator},
        user=user
    )
```

### Step 2: Create API Endpoint

```python
# myapp/api.py
import frappe
from frappe.utils.background_jobs import is_job_enqueued

@frappe.whitelist()
def start_customer_export(filters=None):
    """
    Start customer export in background.
    
    Args:
        filters: JSON string of filter dict
    """
    job_id = f"customer_export::{frappe.session.user}"
    
    # Prevent duplicate exports
    if is_job_enqueued(job_id):
        frappe.throw("An export is already in progress. Please wait.")
    
    # Parse filters
    if filters:
        filters = frappe.parse_json(filters)
    
    # Enqueue export
    frappe.enqueue(
        "myapp.tasks.export_customers",
        queue="long",
        timeout=1800,  # 30 minutes
        job_id=job_id,
        user=frappe.session.user,
        filters=filters
    )
    
    return {"message": "Export started. You'll be notified when complete."}
```

### Step 3: Create Client Interface

```javascript
// In Client Script or custom page
frappe.ui.form.on("Customer", {
    refresh: function(frm) {
        frm.add_custom_button(__("Export All Customers"), function() {
            frappe.call({
                method: "myapp.api.start_customer_export",
                args: {
                    filters: JSON.stringify({
                        "customer_group": frm.doc.customer_group
                    })
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: r.message.message,
                            indicator: "blue"
                        });
                    }
                }
            });
        });
    }
});
```

---

## Workflow 4: Long-Running Task with Chunking

**Goal**: Process 100,000+ records without timeout

### Step 1: Create Chunked Task

```python
# myapp/tasks.py
import frappe
from frappe.utils.background_jobs import is_job_enqueued

def process_invoices_batch(
    offset=0,
    batch_size=500,
    total=None,
    processed=0,
    errors=0,
    job_id=None
):
    """
    Process invoices in batches, chaining to next batch.
    
    Pattern:
    1. Process current batch
    2. If more records, enqueue next batch
    3. If done, send completion notification
    """
    
    # First call: count total
    if total is None:
        total = frappe.db.count(
            "Sales Invoice",
            {"status": "Draft", "custom_processed": 0}
        )
        job_id = f"process_invoices::{frappe.utils.now()}"
    
    # Get current batch
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={"status": "Draft", "custom_processed": 0},
        fields=["name"],
        limit_start=0,  # Always start at 0 since we mark processed
        limit_page_length=batch_size
    )
    
    if not invoices:
        # All done!
        frappe.logger("scheduler").info(
            f"Invoice processing complete: {processed} processed, {errors} errors"
        )
        return
    
    # Process batch
    batch_errors = 0
    for inv in invoices:
        try:
            process_single_invoice(inv.name)
            processed += 1
        except Exception:
            errors += 1
            batch_errors += 1
            frappe.log_error(
                frappe.get_traceback(),
                f"Invoice Processing Error: {inv.name}"
            )
    
    frappe.db.commit()
    
    # Log progress
    progress = int((processed / total) * 100) if total else 0
    frappe.logger("scheduler").info(
        f"Invoice processing: {progress}% ({processed}/{total})"
    )
    
    # Check if more to process
    remaining = frappe.db.count(
        "Sales Invoice",
        {"status": "Draft", "custom_processed": 0}
    )
    
    if remaining > 0:
        # Enqueue next batch
        frappe.enqueue(
            "myapp.tasks.process_invoices_batch",
            queue="long",
            job_id=job_id,
            offset=offset + batch_size,
            batch_size=batch_size,
            total=total,
            processed=processed,
            errors=errors
        )

def process_single_invoice(invoice_name):
    """Process a single invoice."""
    doc = frappe.get_doc("Sales Invoice", invoice_name)
    
    # Your processing logic here
    doc.custom_processed = 1
    doc.save(ignore_permissions=True)
```

### Step 2: Start Processing

```python
# myapp/api.py
@frappe.whitelist()
def start_invoice_processing():
    """Start batch invoice processing."""
    job_id = "process_invoices::batch"
    
    if is_job_enqueued(job_id):
        return {"message": "Processing already in progress"}
    
    frappe.enqueue(
        "myapp.tasks.process_invoices_batch",
        queue="long",
        job_id=job_id
    )
    
    return {"message": "Invoice processing started"}
```

---

## Workflow 5: External API Sync with Retry

**Goal**: Sync with external system, handle failures gracefully

### Step 1: Create Sync Task with Retry Logic

```python
# myapp/tasks.py
import frappe
import requests

def sync_to_external_system():
    """
    Sync pending records to external API.
    Scheduler task - runs hourly.
    """
    pending = frappe.get_all(
        "Sales Order",
        filters={
            "custom_sync_status": ["in", ["Pending", "Failed"]],
            "docstatus": 1
        },
        fields=["name", "custom_sync_attempts"],
        limit=100
    )
    
    for record in pending:
        sync_single_record_with_retry(
            record.name,
            attempt=record.custom_sync_attempts or 0
        )

def sync_single_record_with_retry(order_name, attempt=0, max_attempts=3):
    """
    Sync single record with retry on failure.
    """
    try:
        doc = frappe.get_doc("Sales Order", order_name)
        
        # Call external API
        response = requests.post(
            "https://api.external.com/orders",
            json=doc.as_dict(),
            timeout=30
        )
        response.raise_for_status()
        
        # Success
        frappe.db.set_value(
            "Sales Order", order_name,
            {
                "custom_sync_status": "Synced",
                "custom_sync_date": frappe.utils.now(),
                "custom_sync_attempts": attempt + 1
            }
        )
        frappe.db.commit()
        
    except requests.exceptions.Timeout:
        handle_sync_failure(order_name, "Timeout", attempt, max_attempts)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code >= 500:
            # Server error - retry
            handle_sync_failure(order_name, f"Server Error: {e}", attempt, max_attempts)
        else:
            # Client error - don't retry
            frappe.db.set_value(
                "Sales Order", order_name,
                {
                    "custom_sync_status": "Error",
                    "custom_sync_error": str(e)
                }
            )
            frappe.db.commit()
            
    except Exception as e:
        handle_sync_failure(order_name, str(e), attempt, max_attempts)

def handle_sync_failure(order_name, error, attempt, max_attempts):
    """Handle sync failure with optional retry."""
    frappe.db.rollback()
    
    if attempt < max_attempts:
        # Schedule retry with exponential backoff
        frappe.db.set_value(
            "Sales Order", order_name,
            {
                "custom_sync_status": "Retry Pending",
                "custom_sync_attempts": attempt + 1,
                "custom_sync_error": error
            }
        )
        frappe.db.commit()
        
        # Enqueue retry (will be picked up by next scheduler run)
        frappe.logger("sync").warning(
            f"Sync failed for {order_name}, attempt {attempt + 1}/{max_attempts}"
        )
    else:
        # Max attempts reached
        frappe.db.set_value(
            "Sales Order", order_name,
            {
                "custom_sync_status": "Failed",
                "custom_sync_attempts": attempt + 1,
                "custom_sync_error": f"Max attempts reached: {error}"
            }
        )
        frappe.db.commit()
        
        frappe.log_error(
            f"Sync failed permanently for {order_name} after {max_attempts} attempts: {error}",
            "External Sync Failed"
        )
```

### Step 2: Register in hooks.py

```python
# myapp/hooks.py
scheduler_events = {
    "hourly": [
        "myapp.tasks.sync_to_external_system"
    ]
}
```

---

## Workflow 6: Task with Progress and Notification

**Goal**: Show user progress during long operation

### Step 1: Create Task with Progress Reporting

```python
# myapp/tasks.py
import frappe

def generate_report_with_progress(report_type, user, params=None):
    """
    Generate report with progress updates.
    """
    frappe.set_user(user)
    
    try:
        # Initial notification
        frappe.publish_realtime(
            "msgprint",
            {"message": "Starting report generation...", "indicator": "blue"},
            user=user
        )
        
        # Get total records
        total = get_report_record_count(report_type, params)
        
        if total == 0:
            frappe.publish_realtime(
                "msgprint",
                {"message": "No data found for report", "indicator": "orange"},
                user=user
            )
            return
        
        # Process with progress
        results = []
        for i, record in enumerate(get_report_records(report_type, params)):
            results.append(process_record_for_report(record))
            
            # Update progress every 10%
            if i % max(1, total // 10) == 0:
                percent = int((i / total) * 100)
                frappe.publish_progress(
                    percent=percent,
                    title=f"Processing: {percent}%",
                    description=f"Record {i + 1} of {total}"
                )
        
        # Generate final report
        file_url = create_report_file(results, report_type)
        
        # Success notification
        frappe.publish_realtime(
            "msgprint",
            {
                "message": f"Report ready! <a href='{file_url}' target='_blank'>Download Report</a>",
                "indicator": "green"
            },
            user=user
        )
        
        # Also send email
        frappe.sendmail(
            recipients=[user],
            subject=f"Your {report_type} Report is Ready",
            message=f"Download your report: {file_url}"
        )
        
    except Exception:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), f"Report Generation Failed: {report_type}")
        
        frappe.publish_realtime(
            "msgprint",
            {"message": "Report generation failed. Check Error Log.", "indicator": "red"},
            user=user
        )
```

### Step 2: API to Start Report

```python
# myapp/api.py
@frappe.whitelist()
def generate_report(report_type, params=None):
    """Start report generation in background."""
    from frappe.utils.background_jobs import is_job_enqueued
    
    job_id = f"report::{report_type}::{frappe.session.user}"
    
    if is_job_enqueued(job_id):
        frappe.throw("A report is already being generated. Please wait.")
    
    frappe.enqueue(
        "myapp.tasks.generate_report_with_progress",
        queue="long",
        timeout=3600,
        job_id=job_id,
        report_type=report_type,
        user=frappe.session.user,
        params=frappe.parse_json(params) if params else None
    )
    
    return {"message": "Report generation started. You'll see progress updates."}
```

---

## Workflow 7: Scheduler with Callbacks

**Goal**: Execute follow-up actions on job completion

### Step 1: Define Callbacks

```python
# myapp/tasks.py
import frappe

def on_import_success(job, connection, result, *args, **kwargs):
    """Called when import job succeeds."""
    user = kwargs.get("user")
    import_id = kwargs.get("import_id")
    
    # Update import status
    frappe.db.set_value("Data Import", import_id, "status", "Success")
    frappe.db.commit()
    
    # Notify user
    frappe.publish_realtime(
        "eval_js",
        f'frappe.show_alert({{message: "Import {import_id} completed successfully!", indicator: "green"}})',
        user=user
    )
    
    # Send email
    frappe.sendmail(
        recipients=[user],
        subject=f"Import {import_id} Complete",
        message="Your data import has completed successfully."
    )

def on_import_failure(job, connection, type, value, traceback):
    """Called when import job fails."""
    # Extract kwargs from job
    import_id = job.kwargs.get("import_id")
    user = job.kwargs.get("user")
    
    # Update import status
    frappe.db.set_value(
        "Data Import", import_id,
        {
            "status": "Error",
            "error_message": str(value)
        }
    )
    frappe.db.commit()
    
    # Log error
    frappe.log_error(
        f"Import {import_id} failed: {value}\n{traceback}",
        "Import Failed"
    )
    
    # Notify user
    if user:
        frappe.publish_realtime(
            "eval_js",
            f'frappe.show_alert({{message: "Import {import_id} failed!", indicator: "red"}})',
            user=user
        )
```

### Step 2: Enqueue with Callbacks

```python
# myapp/api.py
@frappe.whitelist()
def start_import(import_id):
    """Start import with success/failure callbacks."""
    frappe.enqueue(
        "myapp.tasks.run_import",
        queue="long",
        timeout=3600,
        on_success="myapp.tasks.on_import_success",
        on_failure="myapp.tasks.on_import_failure",
        import_id=import_id,
        user=frappe.session.user
    )
    
    return {"message": "Import started"}
```

---

## Workflow 8: Monitoring and Alerting

**Goal**: Monitor scheduler health and alert on failures

### Step 1: Create Health Check Task

```python
# myapp/tasks.py
import frappe
from frappe.utils import now_datetime, get_datetime

def scheduler_health_check():
    """
    Check scheduler health and alert if issues found.
    Run every 15 minutes via cron.
    """
    issues = []
    
    # Check for failed jobs in last hour
    failed_jobs = frappe.db.count(
        "Scheduled Job Log",
        {
            "status": "Failed",
            "creation": [">=", frappe.utils.add_to_date(None, hours=-1)]
        }
    )
    
    if failed_jobs > 5:
        issues.append(f"{failed_jobs} scheduler jobs failed in last hour")
    
    # Check for stuck jobs (running > 30 min)
    stuck_jobs = frappe.db.sql("""
        SELECT name, scheduled_job_type, status
        FROM `tabScheduled Job Log`
        WHERE status = 'Running'
        AND creation < DATE_SUB(NOW(), INTERVAL 30 MINUTE)
    """, as_dict=True)
    
    if stuck_jobs:
        issues.append(f"{len(stuck_jobs)} jobs appear stuck")
    
    # Check worker status
    from frappe.utils.background_jobs import get_workers_status
    workers = get_workers_status()
    
    idle_workers = sum(1 for w in workers if w.get("status") == "idle")
    if idle_workers == 0 and len(workers) > 0:
        issues.append("All workers are busy - possible backlog")
    
    # Alert if issues found
    if issues:
        frappe.sendmail(
            recipients=["admin@example.com"],
            subject="⚠️ Scheduler Health Alert",
            message=f"""
            <h3>Scheduler Issues Detected</h3>
            <ul>
            {"".join(f"<li>{issue}</li>" for issue in issues)}
            </ul>
            <p>Check the Background Jobs page for details.</p>
            """
        )
        
        frappe.log_error(
            "\n".join(issues),
            "Scheduler Health Issues"
        )
```

### Step 2: Register Health Check

```python
# myapp/hooks.py
scheduler_events = {
    "cron": {
        "*/15 * * * *": ["myapp.tasks.scheduler_health_check"]
    }
}
```

---

## Quick Reference: Workflow Summary

| Scenario | Workflow | Key Pattern |
|----------|----------|-------------|
| Daily cleanup | Workflow 1 | `scheduler_events["daily"]` |
| Specific time | Workflow 2 | `scheduler_events["cron"]` |
| User-triggered export | Workflow 3 | `frappe.enqueue()` + dedup |
| Large dataset | Workflow 4 | Chunked + self-enqueue |
| External API | Workflow 5 | Retry with backoff |
| Progress reporting | Workflow 6 | `publish_progress()` |
| Follow-up actions | Workflow 7 | `on_success`/`on_failure` |
| Monitoring | Workflow 8 | Health check task |
