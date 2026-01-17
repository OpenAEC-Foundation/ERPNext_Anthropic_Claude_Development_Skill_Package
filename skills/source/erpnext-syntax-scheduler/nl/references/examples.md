# Complete Voorbeelden

Werkende voorbeelden voor scheduler en background jobs.

## 1. Data Import met Progress Tracking

### hooks.py

```python
# hooks.py
scheduler_events = {
    "daily": ["myapp.tasks.check_pending_imports"]
}
```

### tasks.py

```python
# myapp/tasks.py
import frappe
from frappe.utils.background_jobs import is_job_enqueued

def check_pending_imports():
    """Dagelijkse check voor pending imports."""
    pending = frappe.get_all(
        "Data Import",
        filters={"status": "Pending"},
        pluck="name"
    )
    
    for import_name in pending:
        job_id = f"data_import::{import_name}"
        if not is_job_enqueued(job_id):
            frappe.enqueue(
                'myapp.tasks.process_import',
                queue='long',
                timeout=3600,
                job_id=job_id,
                import_name=import_name
            )


def process_import(import_name):
    """Verwerk data import met progress tracking."""
    doc = frappe.get_doc("Data Import", import_name)
    doc.db_set("status", "Processing")
    
    user = doc.owner
    items = get_import_items(doc)
    total = len(items)
    success = 0
    failed = 0
    
    for i, item in enumerate(items):
        try:
            create_record(item)
            frappe.db.commit()
            success += 1
        except Exception:
            frappe.db.rollback()
            frappe.log_error(
                frappe.get_traceback(),
                f"Import Error: {import_name} - Row {i+1}"
            )
            failed += 1
        
        # Progress update elke 10 items
        if (i + 1) % 10 == 0:
            frappe.publish_realtime(
                'import_progress',
                {
                    'import_name': import_name,
                    'progress': (i + 1) / total * 100,
                    'current': i + 1,
                    'total': total,
                    'success': success,
                    'failed': failed
                },
                user=user
            )
    
    # Finaliseer
    doc.db_set("status", "Completed" if failed == 0 else "Completed with Errors")
    doc.db_set("success_count", success)
    doc.db_set("error_count", failed)
    
    frappe.publish_realtime(
        'import_complete',
        {
            'import_name': import_name,
            'success': success,
            'failed': failed
        },
        user=user
    )
```

## 2. Email Verzending met Retry Logic

### tasks.py

```python
# myapp/tasks.py
import frappe

def send_bulk_emails(email_queue_name, retry_count=0):
    """Verzend bulk emails met retry logic."""
    max_retries = 3
    
    queue = frappe.get_doc("Email Queue", email_queue_name)
    recipients = frappe.get_all(
        "Email Queue Recipient",
        filters={"parent": email_queue_name, "status": "Pending"},
        fields=["name", "recipient"]
    )
    
    for rec in recipients:
        try:
            frappe.sendmail(
                recipients=[rec.recipient],
                subject=queue.subject,
                message=queue.message,
                now=True
            )
            frappe.db.set_value(
                "Email Queue Recipient", 
                rec.name, 
                "status", 
                "Sent"
            )
            frappe.db.commit()
            
        except Exception as e:
            frappe.db.rollback()
            
            if "rate limit" in str(e).lower() and retry_count < max_retries:
                # Rate limited - schedule retry
                delay = 60 * (2 ** retry_count)  # Exponential backoff
                frappe.enqueue(
                    'myapp.tasks.send_bulk_emails',
                    queue='default',
                    job_id=f"email_retry::{email_queue_name}::{retry_count + 1}",
                    email_queue_name=email_queue_name,
                    retry_count=retry_count + 1,
                    enqueue_after_commit=True
                )
                frappe.log_error(
                    f"Rate limited, retry {retry_count + 1} scheduled",
                    f"Email Retry: {email_queue_name}"
                )
                return  # Stop huidige run
            else:
                # Andere error of max retries bereikt
                frappe.db.set_value(
                    "Email Queue Recipient",
                    rec.name,
                    "status",
                    "Error"
                )
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Email Failed: {rec.recipient}"
                )
                frappe.db.commit()
    
    # Update queue status
    pending = frappe.db.count(
        "Email Queue Recipient",
        {"parent": email_queue_name, "status": "Pending"}
    )
    if pending == 0:
        queue.db_set("status", "Sent")
```

## 3. Cleanup Job met Error Recovery

### hooks.py

```python
# hooks.py
scheduler_events = {
    "daily": ["myapp.tasks.cleanup_old_records"],
    "weekly_long": ["myapp.tasks.deep_cleanup"]
}
```

### tasks.py

```python
# myapp/tasks.py
import frappe
from frappe.utils import add_days, nowdate

def cleanup_old_records():
    """Dagelijkse cleanup van oude records."""
    cutoff_date = add_days(nowdate(), -30)
    
    # Cleanup in batches
    batch_size = 100
    deleted = 0
    errors = 0
    
    while True:
        records = frappe.get_all(
            "Log Entry",
            filters={"creation": ["<", cutoff_date]},
            limit=batch_size,
            pluck="name"
        )
        
        if not records:
            break
        
        for name in records:
            try:
                frappe.delete_doc("Log Entry", name, force=True)
                frappe.db.commit()
                deleted += 1
            except Exception:
                frappe.db.rollback()
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Cleanup Error: Log Entry {name}"
                )
                errors += 1
    
    # Log resultaat
    frappe.logger().info(f"Cleanup complete: {deleted} deleted, {errors} errors")


def deep_cleanup():
    """Wekelijkse diepe cleanup - draait op long queue."""
    doctypes_to_clean = [
        ("Error Log", 7),      # 7 dagen
        ("Activity Log", 30),  # 30 dagen
        ("Version", 90),       # 90 dagen
    ]
    
    results = {}
    
    for doctype, days in doctypes_to_clean:
        cutoff = add_days(nowdate(), -days)
        deleted = 0
        
        while True:
            records = frappe.get_all(
                doctype,
                filters={"creation": ["<", cutoff]},
                limit=500,
                pluck="name"
            )
            
            if not records:
                break
            
            for name in records:
                try:
                    frappe.delete_doc(doctype, name, force=True)
                    deleted += 1
                except Exception:
                    frappe.log_error(
                        f"Failed to delete {doctype} {name}",
                        "Deep Cleanup Error"
                    )
            
            frappe.db.commit()
        
        results[doctype] = deleted
    
    # Email rapport
    frappe.sendmail(
        recipients=["admin@example.com"],
        subject="Weekly Cleanup Report",
        message=f"Cleanup results: {results}"
    )
```

## 4. Report Generatie met Notifications

### API Endpoint

```python
# myapp/api.py
import frappe
from frappe.utils.background_jobs import is_job_enqueued

@frappe.whitelist()
def generate_report(report_type, filters):
    """Start report generatie in background."""
    job_id = f"report::{report_type}::{frappe.session.user}"
    
    if is_job_enqueued(job_id):
        frappe.throw("Report wordt al gegenereerd")
    
    frappe.enqueue(
        'myapp.tasks.generate_report_task',
        queue='long',
        timeout=1800,
        job_id=job_id,
        report_type=report_type,
        filters=filters,
        user=frappe.session.user
    )
    
    return {"status": "started", "job_id": job_id}
```

### tasks.py

```python
# myapp/tasks.py
import frappe

def generate_report_task(report_type, filters, user):
    """Genereer rapport en notificeer user."""
    try:
        # Progress start
        frappe.publish_realtime(
            'report_status',
            {'status': 'generating', 'report_type': report_type},
            user=user
        )
        
        # Genereer rapport data
        data = generate_report_data(report_type, filters)
        
        # Maak PDF of Excel
        file_url = create_report_file(report_type, data)
        
        # Notificeer user
        frappe.publish_realtime(
            'report_ready',
            {
                'status': 'complete',
                'report_type': report_type,
                'file_url': file_url
            },
            user=user
        )
        
        # Stuur ook email
        frappe.sendmail(
            recipients=[user],
            subject=f"Report Ready: {report_type}",
            message=f"Your report is ready: {file_url}"
        )
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Report Generation Failed: {report_type}"
        )
        
        frappe.publish_realtime(
            'report_failed',
            {
                'status': 'failed',
                'report_type': report_type,
                'error': 'Report generation failed. Check error logs.'
            },
            user=user
        )
```

## 5. External API Sync met Rate Limiting

### hooks.py

```python
# hooks.py
scheduler_events = {
    "hourly": ["myapp.tasks.sync_external_data"]
}
```

### tasks.py

```python
# myapp/tasks.py
import frappe
import time
from frappe.utils.background_jobs import is_job_enqueued

def sync_external_data():
    """Sync data van externe API met rate limiting."""
    job_id = "external_sync::main"
    
    if is_job_enqueued(job_id):
        return  # Al bezig
    
    # Haal items die sync nodig hebben
    items = frappe.get_all(
        "Sync Item",
        filters={"needs_sync": 1},
        limit=100,
        pluck="name"
    )
    
    if not items:
        return
    
    api_calls = 0
    max_calls_per_run = 50  # Rate limit
    
    for item_name in items:
        if api_calls >= max_calls_per_run:
            # Volgende batch schedulen
            frappe.enqueue(
                'myapp.tasks.sync_external_data',
                queue='default',
                job_id=job_id,
                enqueue_after_commit=True
            )
            break
        
        try:
            item = frappe.get_doc("Sync Item", item_name)
            
            # API call
            result = call_external_api(item.external_id)
            api_calls += 1
            
            # Update local record
            item.update(result)
            item.needs_sync = 0
            item.last_sync = frappe.utils.now()
            item.save()
            frappe.db.commit()
            
            # Rate limiting
            time.sleep(0.5)  # 2 calls per seconde max
            
        except Exception:
            frappe.db.rollback()
            frappe.log_error(
                frappe.get_traceback(),
                f"Sync Failed: {item_name}"
            )
    
    frappe.logger().info(f"Sync complete: {api_calls} API calls made")
```

## 6. Document Controller met queue_action

```python
# myapp/doctype/sales_order/sales_order.py
import frappe
from frappe.model.document import Document

class SalesOrder(Document):
    def on_submit(self):
        # Queue heavy operations
        self.queue_action(
            'process_submission',
            notify_user=frappe.session.user
        )
    
    def process_submission(self, notify_user):
        """Background processing na submit."""
        # Heavy operations
        self.create_delivery_note()
        self.send_confirmation_email()
        self.update_inventory()
        
        # Notificeer user
        frappe.publish_realtime(
            'show_alert',
            {
                'message': f'Order {self.name} fully processed',
                'indicator': 'green'
            },
            user=notify_user
        )
    
    def create_delivery_note(self):
        # Implementation
        pass
    
    def send_confirmation_email(self):
        # Implementation
        pass
    
    def update_inventory(self):
        # Implementation
        pass
```
