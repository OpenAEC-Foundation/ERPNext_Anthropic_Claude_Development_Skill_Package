# Scheduler & Background Jobs - Complete Examples

> Production-ready examples for common scheduling scenarios.

---

## Example 1: Daily Database Maintenance

Complete solution for daily database cleanup and optimization.

### hooks.py

```python
scheduler_events = {
    "daily_long": [
        "myapp.maintenance.daily_database_maintenance"
    ]
}
```

### myapp/maintenance.py

```python
import frappe

def daily_database_maintenance():
    """
    Comprehensive daily database maintenance.
    Runs in long queue to allow up to 25 minutes.
    """
    stats = {
        "error_logs_deleted": 0,
        "activity_logs_deleted": 0,
        "email_queue_cleared": 0,
        "versions_cleaned": 0
    }
    
    try:
        # 1. Clean old Error Logs (>30 days)
        stats["error_logs_deleted"] = cleanup_old_records(
            doctype="Error Log",
            date_field="creation",
            days_old=30,
            batch_size=1000
        )
        
        # 2. Clean old Activity Logs (>90 days)
        stats["activity_logs_deleted"] = cleanup_old_records(
            doctype="Activity Log",
            date_field="creation",
            days_old=90,
            batch_size=1000
        )
        
        # 3. Clear sent/expired email queue (>7 days)
        stats["email_queue_cleared"] = cleanup_email_queue(days_old=7)
        
        # 4. Clean old document versions (>180 days, keep latest 5)
        stats["versions_cleaned"] = cleanup_document_versions(
            days_old=180,
            keep_latest=5
        )
        
        # Log summary
        frappe.logger("maintenance").info(
            f"Daily maintenance completed: {stats}"
        )
        
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "Daily Maintenance Failed"
        )

def cleanup_old_records(doctype, date_field, days_old, batch_size=500):
    """Generic cleanup for old records."""
    cutoff = frappe.utils.add_days(frappe.utils.nowdate(), -days_old)
    deleted = 0
    
    while True:
        records = frappe.get_all(
            doctype,
            filters={date_field: ["<", cutoff]},
            pluck="name",
            limit=batch_size
        )
        
        if not records:
            break
        
        for name in records:
            try:
                frappe.delete_doc(doctype, name, ignore_permissions=True)
                deleted += 1
            except Exception:
                pass  # Continue with next
        
        frappe.db.commit()
    
    return deleted

def cleanup_email_queue(days_old=7):
    """Clear old email queue entries."""
    cutoff = frappe.utils.add_days(frappe.utils.nowdate(), -days_old)
    
    deleted = frappe.db.sql("""
        DELETE FROM `tabEmail Queue`
        WHERE status IN ('Sent', 'Expired', 'Error')
        AND creation < %s
        LIMIT 5000
    """, cutoff)
    
    frappe.db.commit()
    return deleted

def cleanup_document_versions(days_old=180, keep_latest=5):
    """Clean old document versions, keeping recent ones."""
    cutoff = frappe.utils.add_days(frappe.utils.nowdate(), -days_old)
    
    # Get documents with many versions
    result = frappe.db.sql("""
        SELECT ref_doctype, docname, COUNT(*) as version_count
        FROM `tabVersion`
        WHERE creation < %s
        GROUP BY ref_doctype, docname
        HAVING version_count > %s
    """, (cutoff, keep_latest), as_dict=True)
    
    deleted = 0
    for row in result:
        # Get versions to delete (all except latest N)
        versions = frappe.db.sql("""
            SELECT name FROM `tabVersion`
            WHERE ref_doctype = %s AND docname = %s
            ORDER BY creation DESC
            LIMIT 999999 OFFSET %s
        """, (row.ref_doctype, row.docname, keep_latest), as_dict=True)
        
        for v in versions:
            frappe.delete_doc("Version", v.name, ignore_permissions=True)
            deleted += 1
        
        frappe.db.commit()
    
    return deleted
```

---

## Example 2: External System Sync

Complete bidirectional sync with external REST API.

### hooks.py

```python
scheduler_events = {
    "hourly": [
        "myapp.sync.sync_from_external"
    ],
    "cron": {
        # Push updates every 15 minutes
        "*/15 * * * *": ["myapp.sync.push_to_external"]
    }
}
```

### myapp/sync.py

```python
import frappe
import requests
from datetime import datetime

API_BASE = "https://api.external.com/v1"
API_KEY = frappe.conf.get("external_api_key")

def sync_from_external():
    """
    Pull new/updated records from external system.
    Runs hourly.
    """
    last_sync = get_last_sync_time("pull")
    
    try:
        # Fetch updates from API
        response = requests.get(
            f"{API_BASE}/orders",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"updated_since": last_sync.isoformat() if last_sync else None},
            timeout=60
        )
        response.raise_for_status()
        
        orders = response.json().get("data", [])
        
        synced = 0
        errors = 0
        
        for order_data in orders:
            try:
                sync_single_order(order_data)
                synced += 1
            except Exception as e:
                errors += 1
                frappe.log_error(
                    f"Sync error for order {order_data.get('id')}: {e}",
                    "External Sync Error"
                )
        
        frappe.db.commit()
        
        # Update sync timestamp
        set_last_sync_time("pull")
        
        frappe.logger("sync").info(
            f"Pull sync completed: {synced} synced, {errors} errors"
        )
        
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"API request failed: {e}", "External Sync Failed")

def push_to_external():
    """
    Push pending local changes to external system.
    Runs every 15 minutes.
    """
    pending = frappe.get_all(
        "Sales Order",
        filters={
            "custom_external_sync_pending": 1,
            "docstatus": 1
        },
        fields=["name", "custom_external_id"],
        limit=50
    )
    
    for order in pending:
        try:
            doc = frappe.get_doc("Sales Order", order.name)
            
            # Prepare payload
            payload = {
                "order_id": doc.name,
                "customer": doc.customer,
                "total": doc.grand_total,
                "items": [
                    {"sku": i.item_code, "qty": i.qty, "rate": i.rate}
                    for i in doc.items
                ]
            }
            
            # Create or update
            if order.custom_external_id:
                response = requests.put(
                    f"{API_BASE}/orders/{order.custom_external_id}",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json=payload,
                    timeout=30
                )
            else:
                response = requests.post(
                    f"{API_BASE}/orders",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json=payload,
                    timeout=30
                )
            
            response.raise_for_status()
            external_id = response.json().get("id")
            
            # Update local record
            frappe.db.set_value(
                "Sales Order", order.name,
                {
                    "custom_external_id": external_id,
                    "custom_external_sync_pending": 0,
                    "custom_last_synced": frappe.utils.now()
                }
            )
            
        except Exception as e:
            frappe.log_error(
                f"Push sync failed for {order.name}: {e}",
                "External Push Error"
            )
    
    frappe.db.commit()

def sync_single_order(order_data):
    """Create or update local order from external data."""
    external_id = order_data.get("id")
    
    # Check if exists
    existing = frappe.db.get_value(
        "Sales Order",
        {"custom_external_id": external_id},
        "name"
    )
    
    if existing:
        # Update existing
        doc = frappe.get_doc("Sales Order", existing)
        doc.custom_external_status = order_data.get("status")
        doc.save(ignore_permissions=True)
    else:
        # Create new
        doc = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": order_data.get("customer"),
            "custom_external_id": external_id,
            "custom_external_sync_pending": 0,
            # ... map other fields
        })
        doc.insert(ignore_permissions=True)

def get_last_sync_time(sync_type):
    """Get last sync timestamp."""
    return frappe.db.get_value(
        "Singles",
        {"doctype": "Sync Settings", "field": f"last_{sync_type}_sync"},
        "value"
    )

def set_last_sync_time(sync_type):
    """Update last sync timestamp."""
    frappe.db.set_value(
        "Sync Settings", None,
        f"last_{sync_type}_sync",
        frappe.utils.now()
    )
```

---

## Example 3: Bulk Data Import with Progress

Complete solution for importing large CSV files.

### myapp/api.py

```python
import frappe
from frappe.utils.background_jobs import is_job_enqueued

@frappe.whitelist()
def start_csv_import(file_url, doctype, update_existing=False):
    """
    Start CSV import in background.
    
    Args:
        file_url: URL of uploaded CSV file
        doctype: Target DocType
        update_existing: If True, update existing records
    """
    job_id = f"csv_import::{frappe.session.user}::{file_url}"
    
    if is_job_enqueued(job_id):
        frappe.throw("This file is already being imported")
    
    # Create import log
    import_log = frappe.get_doc({
        "doctype": "Data Import Log",
        "import_file": file_url,
        "reference_doctype": doctype,
        "status": "Queued",
        "started_by": frappe.session.user
    })
    import_log.insert(ignore_permissions=True)
    frappe.db.commit()
    
    frappe.enqueue(
        "myapp.importer.run_csv_import",
        queue="long",
        timeout=7200,  # 2 hours
        job_id=job_id,
        file_url=file_url,
        doctype=doctype,
        update_existing=update_existing,
        user=frappe.session.user,
        import_log_name=import_log.name
    )
    
    return {
        "message": "Import started",
        "import_log": import_log.name
    }
```

### myapp/importer.py

```python
import frappe
import csv
from io import StringIO

def run_csv_import(file_url, doctype, update_existing, user, import_log_name):
    """
    Main import function.
    """
    frappe.set_user(user)
    
    # Update status
    update_import_log(import_log_name, status="Running")
    
    try:
        # Read file
        file_content = frappe.get_doc("File", {"file_url": file_url}).get_content()
        
        if isinstance(file_content, bytes):
            file_content = file_content.decode("utf-8")
        
        reader = csv.DictReader(StringIO(file_content))
        rows = list(reader)
        total = len(rows)
        
        if total == 0:
            update_import_log(
                import_log_name,
                status="Error",
                error_message="No data rows found in file"
            )
            return
        
        # Process rows
        success = 0
        failed = 0
        errors = []
        
        for i, row in enumerate(rows):
            try:
                import_single_row(doctype, row, update_existing)
                success += 1
                
                # Commit every 100 rows
                if i % 100 == 0:
                    frappe.db.commit()
                    
                    # Update progress
                    percent = int((i / total) * 100)
                    frappe.publish_progress(
                        percent=percent,
                        title="Importing...",
                        description=f"Row {i + 1} of {total}"
                    )
                    
                    update_import_log(
                        import_log_name,
                        processed=i + 1,
                        success_count=success,
                        error_count=failed
                    )
                    
            except Exception as e:
                failed += 1
                errors.append({
                    "row": i + 2,  # +2 for header and 0-index
                    "error": str(e),
                    "data": row
                })
        
        frappe.db.commit()
        
        # Final status
        status = "Success" if failed == 0 else "Completed with Errors"
        
        update_import_log(
            import_log_name,
            status=status,
            processed=total,
            success_count=success,
            error_count=failed,
            errors=frappe.as_json(errors[:100])  # Store first 100 errors
        )
        
        # Notify user
        notify_import_complete(user, import_log_name, success, failed)
        
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), f"Import Failed: {import_log_name}")
        
        update_import_log(
            import_log_name,
            status="Error",
            error_message=str(e)
        )
        
        frappe.publish_realtime(
            "msgprint",
            {"message": "Import failed. Check Data Import Log.", "indicator": "red"},
            user=user
        )

def import_single_row(doctype, row, update_existing):
    """Import or update single row."""
    # Get identifying field (usually name or custom identifier)
    identifier = row.get("name") or row.get("id")
    
    if update_existing and identifier:
        existing = frappe.db.exists(doctype, identifier)
        if existing:
            doc = frappe.get_doc(doctype, identifier)
            doc.update(row)
            doc.save(ignore_permissions=True)
            return
    
    # Create new
    doc = frappe.get_doc({
        "doctype": doctype,
        **row
    })
    doc.insert(ignore_permissions=True)

def update_import_log(name, **kwargs):
    """Update import log record."""
    frappe.db.set_value("Data Import Log", name, kwargs)
    frappe.db.commit()

def notify_import_complete(user, import_log_name, success, failed):
    """Send completion notification."""
    indicator = "green" if failed == 0 else "orange"
    message = f"Import complete: {success} success, {failed} failed"
    
    frappe.publish_realtime(
        "msgprint",
        {
            "message": f"{message}. <a href='/app/data-import-log/{import_log_name}'>View Log</a>",
            "indicator": indicator
        },
        user=user
    )
```

---

## Example 4: Email Digest/Newsletter

Automated weekly summary email to users.

### hooks.py

```python
scheduler_events = {
    "cron": {
        # Every Monday at 8:00 AM
        "0 8 * * 1": ["myapp.newsletter.send_weekly_digest"]
    }
}
```

### myapp/newsletter.py

```python
import frappe

def send_weekly_digest():
    """
    Send weekly digest email to all subscribed users.
    """
    # Get digest data
    digest_data = compile_weekly_digest()
    
    # Get subscribers
    subscribers = frappe.get_all(
        "User",
        filters={
            "enabled": 1,
            "custom_weekly_digest": 1  # Custom checkbox field
        },
        fields=["name", "email", "full_name", "language"]
    )
    
    sent = 0
    for subscriber in subscribers:
        try:
            send_digest_to_user(subscriber, digest_data)
            sent += 1
        except Exception:
            frappe.log_error(
                f"Failed to send digest to {subscriber.email}",
                "Digest Send Error"
            )
    
    frappe.logger("newsletter").info(f"Weekly digest sent to {sent} subscribers")

def compile_weekly_digest():
    """Compile data for weekly digest."""
    last_week = frappe.utils.add_days(frappe.utils.nowdate(), -7)
    
    return {
        "period_start": last_week,
        "period_end": frappe.utils.nowdate(),
        
        "new_orders": frappe.db.count(
            "Sales Order",
            {"creation": [">=", last_week], "docstatus": 1}
        ),
        
        "total_revenue": get_weekly_revenue(last_week),
        
        "top_items": get_top_selling_items(last_week, limit=5),
        
        "new_customers": frappe.db.count(
            "Customer",
            {"creation": [">=", last_week]}
        ),
        
        "open_issues": frappe.db.count(
            "Issue",
            {"status": "Open"}
        )
    }

def get_weekly_revenue(since_date):
    """Get total revenue for the week."""
    result = frappe.db.sql("""
        SELECT COALESCE(SUM(grand_total), 0)
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND posting_date >= %s
    """, since_date)
    return result[0][0] if result else 0

def get_top_selling_items(since_date, limit=5):
    """Get top selling items for the week."""
    return frappe.db.sql("""
        SELECT 
            sii.item_code,
            sii.item_name,
            SUM(sii.qty) as total_qty,
            SUM(sii.amount) as total_amount
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON si.name = sii.parent
        WHERE si.docstatus = 1
        AND si.posting_date >= %s
        GROUP BY sii.item_code
        ORDER BY total_amount DESC
        LIMIT %s
    """, (since_date, limit), as_dict=True)

def send_digest_to_user(subscriber, digest_data):
    """Send personalized digest to user."""
    # Render template
    message = frappe.render_template(
        "myapp/templates/emails/weekly_digest.html",
        {
            "user": subscriber,
            "data": digest_data
        }
    )
    
    frappe.sendmail(
        recipients=[subscriber.email],
        subject=f"Weekly Digest - {digest_data['period_end']}",
        message=message,
        reference_doctype="User",
        reference_name=subscriber.name
    )
```

### myapp/templates/emails/weekly_digest.html

```jinja
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <h1 style="color: #2c3e50;">Weekly Digest</h1>
    <p>Hi {{ user.full_name }},</p>
    <p>Here's your weekly summary for {{ data.period_start }} to {{ data.period_end }}:</p>
    
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr style="background: #3498db; color: white;">
            <td style="padding: 15px; text-align: center;">
                <h2 style="margin: 0;">{{ data.new_orders }}</h2>
                <p style="margin: 5px 0 0;">New Orders</p>
            </td>
            <td style="padding: 15px; text-align: center;">
                <h2 style="margin: 0;">{{ frappe.format(data.total_revenue, {'fieldtype': 'Currency'}) }}</h2>
                <p style="margin: 5px 0 0;">Revenue</p>
            </td>
            <td style="padding: 15px; text-align: center;">
                <h2 style="margin: 0;">{{ data.new_customers }}</h2>
                <p style="margin: 5px 0 0;">New Customers</p>
            </td>
        </tr>
    </table>
    
    {% if data.top_items %}
    <h3>Top Selling Items</h3>
    <table style="width: 100%; border-collapse: collapse;">
        <tr style="background: #f5f5f5;">
            <th style="padding: 10px; text-align: left;">Item</th>
            <th style="padding: 10px; text-align: right;">Qty</th>
            <th style="padding: 10px; text-align: right;">Amount</th>
        </tr>
        {% for item in data.top_items %}
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{{ item.item_name }}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">{{ item.total_qty }}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                {{ frappe.format(item.total_amount, {'fieldtype': 'Currency'}) }}
            </td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
    
    <p style="color: #666; margin-top: 30px;">
        <a href="{{ frappe.utils.get_url() }}">Go to Dashboard</a>
    </p>
</div>
```

---

## Example 5: Document Expiry Notifications

Notify users about expiring documents (contracts, licenses, etc.).

### hooks.py

```python
scheduler_events = {
    "daily": [
        "myapp.expiry.check_expiring_documents"
    ]
}
```

### myapp/expiry.py

```python
import frappe

EXPIRY_CONFIGS = [
    {
        "doctype": "Contract",
        "date_field": "end_date",
        "days_before": [30, 7, 1],  # Notify 30, 7, 1 days before
        "notify_field": "contract_owner"  # User field to notify
    },
    {
        "doctype": "License",
        "date_field": "valid_till",
        "days_before": [60, 30, 7],
        "notify_field": "assigned_to"
    },
    {
        "doctype": "Insurance Policy",
        "date_field": "expiry_date",
        "days_before": [30, 14, 7],
        "notify_field": "owner"
    }
]

def check_expiring_documents():
    """
    Check for expiring documents and send notifications.
    """
    today = frappe.utils.nowdate()
    
    for config in EXPIRY_CONFIGS:
        check_doctype_expiry(config, today)

def check_doctype_expiry(config, today):
    """Check expiry for a specific DocType."""
    doctype = config["doctype"]
    date_field = config["date_field"]
    notify_field = config["notify_field"]
    
    for days in config["days_before"]:
        target_date = frappe.utils.add_days(today, days)
        
        # Find documents expiring on target date
        expiring = frappe.get_all(
            doctype,
            filters={
                date_field: target_date,
                "docstatus": ["!=", 2]  # Not cancelled
            },
            fields=["name", date_field, notify_field, "owner"]
        )
        
        for doc in expiring:
            # Check if notification already sent
            if was_notified(doctype, doc.name, days):
                continue
            
            # Get user to notify
            notify_user = doc.get(notify_field) or doc.get("owner")
            
            if notify_user:
                send_expiry_notification(
                    doctype=doctype,
                    doc_name=doc.name,
                    expiry_date=doc.get(date_field),
                    days_remaining=days,
                    user=notify_user
                )
                
                # Mark as notified
                mark_notified(doctype, doc.name, days)

def send_expiry_notification(doctype, doc_name, expiry_date, days_remaining, user):
    """Send expiry notification to user."""
    # Create system notification
    frappe.get_doc({
        "doctype": "Notification Log",
        "for_user": user,
        "type": "Alert",
        "document_type": doctype,
        "document_name": doc_name,
        "subject": f"{doctype} {doc_name} expires in {days_remaining} days",
        "email_content": f"""
            <p>The following {doctype} will expire on {expiry_date}:</p>
            <p><strong>{doc_name}</strong></p>
            <p><a href="/app/{frappe.scrub(doctype)}/{doc_name}">View Document</a></p>
        """
    }).insert(ignore_permissions=True)
    
    # Also send email
    user_email = frappe.db.get_value("User", user, "email")
    if user_email:
        frappe.sendmail(
            recipients=[user_email],
            subject=f"⚠️ {doctype} Expiring: {doc_name}",
            message=f"""
                <p>This is a reminder that the following {doctype} will expire in {days_remaining} days:</p>
                <p><strong>{doc_name}</strong></p>
                <p>Expiry Date: {expiry_date}</p>
                <p><a href="{frappe.utils.get_url()}/app/{frappe.scrub(doctype)}/{doc_name}">
                    View Document
                </a></p>
            """
        )
    
    frappe.db.commit()

def was_notified(doctype, doc_name, days):
    """Check if notification was already sent."""
    return frappe.db.exists(
        "Expiry Notification Log",
        {
            "reference_doctype": doctype,
            "reference_name": doc_name,
            "days_before": days
        }
    )

def mark_notified(doctype, doc_name, days):
    """Record that notification was sent."""
    frappe.get_doc({
        "doctype": "Expiry Notification Log",
        "reference_doctype": doctype,
        "reference_name": doc_name,
        "days_before": days,
        "sent_on": frappe.utils.nowdate()
    }).insert(ignore_permissions=True)
```

---

## Quick Reference: Example Summary

| Example | Use Case | Key Pattern |
|---------|----------|-------------|
| Database Maintenance | Daily cleanup | Batch delete with commit |
| External Sync | API integration | Retry + error handling |
| CSV Import | Large data import | Progress + chunking |
| Email Digest | Scheduled reports | Template + subscriber list |
| Expiry Notifications | Document monitoring | Date calculation + notification log |
