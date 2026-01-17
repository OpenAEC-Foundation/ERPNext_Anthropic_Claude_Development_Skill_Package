# Complete Werkende Voorbeelden

## 1. Dagelijkse Data Sync

### hooks.py

```python
scheduler_events = {
    "daily": [
        "myapp.tasks.sync.daily_sync"
    ]
}
```

### myapp/tasks/sync.py

```python
import frappe

def daily_sync():
    """Synchroniseer data van externe API dagelijks."""
    customers = frappe.get_all("Customer", filters={"sync_enabled": 1})
    
    for customer in customers:
        try:
            sync_customer_data(customer.name)
            frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            frappe.log_error(
                frappe.get_traceback(),
                f"Sync failed: {customer.name}"
            )
    
    frappe.publish_realtime(
        "show_alert",
        {"message": f"Sync complete: {len(customers)} customers"}
    )

def sync_customer_data(customer_name):
    """Sync single customer."""
    customer = frappe.get_doc("Customer", customer_name)
    # ... sync logic
    customer.last_synced = frappe.utils.now()
    customer.save(ignore_permissions=True)
```

---

## 2. Email Queue met Deduplicatie (v15)

### Controller

```python
class Newsletter(Document):
    def on_submit(self):
        from frappe.utils.background_jobs import is_job_enqueued
        
        job_id = f"newsletter::{self.name}"
        
        if is_job_enqueued(job_id):
            frappe.msgprint("Newsletter wordt al verzonden")
            return
        
        frappe.enqueue(
            "myapp.tasks.email.send_newsletter",
            job_id=job_id,
            queue="long",
            timeout=3600,
            newsletter=self.name,
            on_success=notify_completion,
            on_failure=notify_failure
        )
        
        frappe.msgprint("Newsletter verzending gestart")

def notify_completion(job, connection, result, *args, **kwargs):
    frappe.publish_realtime(
        "show_alert",
        {"message": "Newsletter verzonden!", "indicator": "green"}
    )

def notify_failure(job, connection, type, value, traceback):
    frappe.log_error(f"Newsletter failed: {value}")
```

### Task

```python
# myapp/tasks/email.py
import frappe

def send_newsletter(newsletter):
    """Send newsletter to all subscribers."""
    doc = frappe.get_doc("Newsletter", newsletter)
    subscribers = get_subscribers(doc)
    
    sent = 0
    failed = 0
    
    for subscriber in subscribers:
        try:
            send_email(doc, subscriber)
            sent += 1
            frappe.db.commit()
        except Exception:
            failed += 1
            frappe.db.rollback()
            frappe.log_error(
                frappe.get_traceback(),
                f"Email failed: {subscriber.email}"
            )
    
    # Update newsletter status
    doc.db_set("sent_count", sent)
    doc.db_set("failed_count", failed)
    doc.db_set("status", "Sent")
    
    return {"sent": sent, "failed": failed}
```

---

## 3. Heavy Report Generatie

### API Endpoint

```python
@frappe.whitelist()
def generate_annual_report(year, company):
    """Start report generation in background."""
    from frappe.utils.background_jobs import is_job_enqueued
    
    job_id = f"annual_report::{company}::{year}"
    
    if is_job_enqueued(job_id):
        return {"status": "already_running"}
    
    frappe.enqueue(
        "myapp.tasks.reports.create_annual_report",
        job_id=job_id,
        queue="long",
        timeout=7200,  # 2 uur
        year=year,
        company=company,
        user=frappe.session.user
    )
    
    return {"status": "started", "job_id": job_id}
```

### Task

```python
# myapp/tasks/reports.py
import frappe

def create_annual_report(year, company, user):
    """Generate comprehensive annual report."""
    frappe.set_user(user)  # Set correct user context
    
    try:
        # Notify start
        frappe.publish_realtime(
            "report_progress",
            {"status": "started", "message": "Collecting data..."},
            user=user
        )
        
        # Collect data
        data = collect_annual_data(year, company)
        
        frappe.publish_realtime(
            "report_progress",
            {"status": "processing", "message": "Generating report..."},
            user=user
        )
        
        # Create report document
        report = frappe.new_doc("Annual Report")
        report.year = year
        report.company = company
        report.data = frappe.as_json(data)
        report.owner = user
        report.insert(ignore_permissions=True)
        
        # Generate PDF
        pdf = frappe.get_print("Annual Report", report.name, as_pdf=True)
        
        # Attach PDF
        frappe.get_doc({
            "doctype": "File",
            "file_name": f"Annual_Report_{year}.pdf",
            "attached_to_doctype": "Annual Report",
            "attached_to_name": report.name,
            "content": pdf
        }).insert(ignore_permissions=True)
        
        frappe.db.commit()
        
        # Notify completion
        frappe.publish_realtime(
            "report_progress",
            {
                "status": "completed",
                "message": "Report ready!",
                "report_name": report.name
            },
            user=user
        )
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Annual Report Failed")
        
        frappe.publish_realtime(
            "report_progress",
            {"status": "failed", "message": str(e)},
            user=user
        )
        raise
```

---

## 4. Cron Job: Elk Kwartier Cleanup

### hooks.py

```python
scheduler_events = {
    "cron": {
        "*/15 * * * *": [
            "myapp.tasks.cleanup.cleanup_temp_files"
        ]
    }
}
```

### Task

```python
# myapp/tasks/cleanup.py
import frappe
import os
from frappe.utils import get_files_path

def cleanup_temp_files():
    """Remove temporary files older than 1 hour."""
    temp_path = get_files_path("temp")
    
    if not os.path.exists(temp_path):
        return
    
    cutoff = frappe.utils.add_to_date(None, hours=-1)
    removed = 0
    
    for filename in os.listdir(temp_path):
        filepath = os.path.join(temp_path, filename)
        
        try:
            mtime = os.path.getmtime(filepath)
            if mtime < cutoff.timestamp():
                os.remove(filepath)
                removed += 1
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Cleanup failed: {filename}"
            )
    
    if removed > 0:
        frappe.logger().info(f"Cleaned up {removed} temp files")
```

---

## 5. Document Processing met enqueue_doc

### Controller

```python
class DataImport(Document):
    def on_submit(self):
        """Start import in background."""
        frappe.enqueue_doc(
            self.doctype,
            self.name,
            "process_import",
            queue="long",
            timeout=1800
        )
        frappe.msgprint("Import gestart op achtergrond")
    
    @frappe.whitelist()
    def process_import(self):
        """Process the import file."""
        rows = self.get_import_rows()
        total = len(rows)
        
        for i, row in enumerate(rows):
            try:
                self.import_row(row)
                frappe.db.commit()
                
                # Progress update elke 100 rows
                if i % 100 == 0:
                    self.db_set("progress", f"{i}/{total}")
                    frappe.publish_realtime(
                        "import_progress",
                        {"current": i, "total": total},
                        doctype=self.doctype,
                        docname=self.name
                    )
                    
            except Exception:
                frappe.db.rollback()
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Import row {i} failed"
                )
        
        self.db_set("status", "Completed")
        self.db_set("progress", f"{total}/{total}")
```

---

## 6. Retry Pattern met Backoff

```python
import frappe
from frappe.utils import now_datetime, add_to_date

def call_external_api_with_retry(endpoint, data, retry_count=0, max_retries=3):
    """Call API with exponential backoff retry."""
    try:
        response = make_api_call(endpoint, data)
        frappe.db.commit()
        return response
        
    except Exception as e:
        frappe.db.rollback()
        
        if retry_count >= max_retries:
            frappe.log_error(
                f"API call failed after {max_retries} retries: {e}",
                "API Error"
            )
            raise
        
        # Exponential backoff: 1min, 2min, 4min
        delay_minutes = 2 ** retry_count
        
        frappe.enqueue(
            "myapp.tasks.api.call_external_api_with_retry",
            queue="default",
            enqueue_after_commit=True,
            endpoint=endpoint,
            data=data,
            retry_count=retry_count + 1,
            max_retries=max_retries
        )
        
        frappe.log_error(
            f"API call failed, retry {retry_count + 1} in {delay_minutes} min",
            "API Retry"
        )
```
