# Email System — Deep Reference

## Email Account DocType

The Email Account DocType manages both incoming and outgoing email for a Frappe site.

### Key Fields

| Field Group | Fields | Purpose |
|-------------|--------|---------|
| Identity | `email_id`, `email_account_name`, `domain` | Account identification |
| Incoming (IMAP/POP3) | `email_server`, `incoming_port`, `use_imap`, `use_ssl`, `use_starttls` | Inbound mail retrieval |
| Outgoing (SMTP) | `smtp_server`, `smtp_port`, `use_ssl_for_outgoing`, `no_smtp_authentication` | Outbound mail delivery |
| Authentication | `auth_method` (Basic/OAuth), `password`, `login_id`, `api_key`, `api_secret` | Credentials |
| Sync | `email_sync_option` (ALL/UNSEEN), `initial_sync_count`, `imap_folder` (child table) | What to pull |
| Linking | `enable_automatic_linking`, `append_to` (per IMAP folder) | Document association |
| Defaults | `default_incoming`, `default_outgoing` | Site-wide fallback account |
| Auto-reply | `enable_auto_reply`, `auto_reply_message` | Template-rendered replies |
| Sender | `always_use_account_email_id_as_sender`, `always_use_account_name_as_sender_name` | Sender override |

### IMAP Folder Configuration

Each Email Account has a child table `imap_folder` with rows containing:

- `folder_name` — The IMAP mailbox name (e.g., "INBOX", "Support")
- `append_to` — Target DocType for incoming emails (e.g., "Issue", "Lead")

ALWAYS configure at least one IMAP folder when `use_imap` is enabled — without it, no emails are pulled.

### Outgoing Account Selection

When Frappe sends email, it selects the outgoing account in this order:

1. Match recipient email to an account's domain
2. Match target DocType to an account's `append_to` field
3. Fall back to the account with `default_outgoing` enabled
4. Raise error if no outgoing account is configured

### Failed Connection Handling

After 5+ consecutive connection failures, the Email Account auto-disables via background job. The `no_failed` counter resets on successful connection. ALWAYS monitor Email Account status in production — silent disabling causes email blackouts.

### OAuth Support

Set `auth_method` to "OAuth" and link a **Connected App** DocType. Frappe retrieves access tokens automatically. No password validation occurs when OAuth is active.

### Site Config Fallback

Legacy `mail_server`, `mail_port`, `mail_login`, `mail_password` keys in `site_config.json` are read as fallback via `get_account_details_from_site_config()`. ALWAYS prefer Email Account DocType over site config — site config is deprecated for email.

---

## Email Domain DocType

Email Domain stores shared server settings that propagate to linked Email Accounts.

### Fields

| Field | Purpose |
|-------|---------|
| `domain_name` | Domain identifier (e.g., "example.com") |
| `email_server` | Incoming server host |
| `use_imap`, `use_ssl`, `use_starttls`, `use_tls` | Incoming protocol flags |
| `incoming_port` | Incoming server port |
| `smtp_server`, `smtp_port`, `use_ssl_for_outgoing` | Outgoing server settings |
| `attachment_limit` | Max attachment size |
| `append_emails_to_sent_folder` | Copy sent emails to IMAP Sent folder |

### Propagation

On `on_update()`, ALL 13 domain fields propagate to every Email Account linked via the `domain` field. Changing the Email Domain updates all linked accounts automatically.

### Connection Validation

During save, Frappe validates both incoming (IMAP/POP3) and outgoing (SMTP) connections with a 15-second timeout. Validation is skipped during patches, tests, and installation.

**Port conventions:**
- IMAP SSL: 993 | IMAP: 143
- POP3 SSL: 995 | POP3: 110
- SMTP SSL: 465 | SMTP TLS: 587 | SMTP plain: 25

---

## Email Queue

All emails pass through the Email Queue before delivery (unless `now=True` is set).

### Queue Flow

```
frappe.sendmail(delayed=True)
  → Email Queue record created (status: "Not Sent")
    → Scheduler calls flush() every minute
      → get_queue() fetches batch (default: 500)
        → EmailQueue.send() transmits via SMTP
          → Status: "Sent" / "Error" / "Partially Sent"
```

### Email Queue DocType Fields

| Field | Purpose |
|-------|---------|
| `status` | Not Sent, Sending, Sent, Partially Sent, Error |
| `sender` | From address |
| `message` | Full email content |
| `reference_doctype`, `reference_name` | Linked document |
| `send_after` | Delayed send timestamp (NULL = immediate) |
| `priority` | Higher priority processed first |
| `retry` | Current retry count |
| `email_account` | Outgoing account used |
| `error` | Traceback on failure |

### Recipient Child Table

Each Email Queue has `Email Queue Recipient` children tracking per-recipient delivery status. The `build_message()` method personalizes each email (unsubscribe URLs, tracking pixels).

### Batch Processing

```python
batch_size = cint(frappe.conf.email_queue_batch_size) or 500
```

Processing order: `priority DESC, retry ASC, creation ASC` — high-priority emails go first, retried emails go last.

### Failure Protection

The queue aborts the entire batch if failures exceed BOTH:
- 33% of the batch (`EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_PERCENT = 0.33`)
- 10 absolute failures (`EMAIL_QUEUE_BATCH_FAILURE_THRESHOLD_COUNT = 10`)

This prevents hammering a broken SMTP server with hundreds of attempts.

### Retry Logic

```python
email_retry_limit = cint(frappe.db.get_system_setting("email_retry_limit")) or 3
```

Emails stuck in "Sending" for >15 minutes are reset by `retry_sending_emails()`. After exhausting retries, status becomes "Error" and a Notification Log entry is created for the queue owner.

### Race Condition Guard

Emails must exist for 10+ seconds before processing (`creation < undo_window`). This prevents sending emails that the user might still be editing/cancelling.

### Monitoring

```python
# Check pending emails
pending = frappe.get_all("Email Queue", filters={"status": "Not Sent"}, limit=20)

# Check failed emails
failed = frappe.get_all("Email Queue",
    filters={"status": "Error"},
    fields=["name", "sender", "error", "creation"],
    order_by="creation desc", limit=10)

# Count today's emails
from frappe.email.queue import get_emails_sent_today
count = get_emails_sent_today()
```

---

## Communication DocType — Email-to-Document Linking

Every email (sent or received) creates a **Communication** record. This is how Frappe threads emails onto document timelines.

### Key Fields

| Field | Purpose |
|-------|---------|
| `communication_medium` | Email, Phone, Chat, etc. |
| `communication_type` | Communication, Automated Message, etc. |
| `sent_or_received` | "Sent" or "Received" |
| `sender`, `sender_full_name` | From address |
| `recipients`, `cc`, `bcc` | To/CC/BCC addresses |
| `subject`, `content`, `text_content` | Email content |
| `reference_doctype`, `reference_name` | Linked document (appears on timeline) |
| `message_id` | Email Message-ID header |
| `in_reply_to` | Parent Communication for threading |
| `email_account` | Which account sent/received this |
| `delivery_status` | Sending, Sent, Bounced, Error, Opened |
| `read_by_recipient` | Read receipt tracking |

### Incoming Email Flow

```
Email Account pulls via IMAP
  → InboundMail parses raw message
    → Communication record created (sent_or_received="Received")
      → Linked to document via append_to DocType matching
        → Appears on document timeline
          → Auto-reply sent if enabled
```

### Outgoing Email Flow

```
User composes email / frappe.sendmail() called
  → Communication record created (sent_or_received="Sent")
    → Email Queue record created for delivery
      → delivery_status tracks: Sending → Sent / Error / Bounced
```

### Email Threading

Threading works through `message_id` and `in_reply_to`:

1. Outgoing emails store a unique `message_id`
2. Replies include `In-Reply-To` header referencing parent `message_id`
3. Frappe matches incoming `In-Reply-To` to existing Communication records
4. Matched emails link to the same document, creating a thread

ALWAYS set `reference_doctype` and `reference_name` in `frappe.sendmail()` — this creates the Communication link. Without it, the email is orphaned and does not appear on any document timeline.

### Append-To Linking

DocTypes eligible for email linking must have `email_append_to = 1` in their definition or via Property Setter customization:

```python
# Programmatic check for valid append-to doctypes
valid_doctypes = frappe.get_all("DocType",
    filters={"istable": 0, "issingle": 0, "email_append_to": 1})
```

### Timeline Links

Communications auto-create `timeline_links` child records, linking the email to:
- The reference document
- Associated contacts (if `create_contact` is enabled)

`deduplicate_timeline_links()` prevents duplicate entries.

---

## Bulk Email — Newsletter DocType

The Newsletter DocType handles mass email campaigns to Email Groups.

### Setup

1. Create **Email Group** DocType records (subscriber lists)
2. Add subscribers via **Email Group Member** child table or import
3. Create Newsletter with content and select target Email Groups
4. Submit and send

### Sending Pattern

```python
# Newsletter creates one Email Queue record per recipient
# Each recipient gets a personalized email with:
# - Unsubscribe link (mandatory, auto-appended)
# - Tracking pixel (if enabled)
# - Personalized greeting (if template uses {{ subscriber_name }})
```

### Unsubscribe Handling

ALWAYS include an unsubscribe mechanism — Frappe auto-appends unsubscribe links to Newsletter emails. The `unsubscribe()` endpoint removes the subscriber from the Email Group.

### Programmatic Bulk Email

For bulk email outside Newsletter, use `frappe.sendmail()` with `delayed=True`:

```python
for recipient in recipient_list:
    frappe.sendmail(
        recipients=[recipient],
        subject="Monthly Report",
        template="monthly_report",
        args={"user": recipient},
        reference_doctype="Monthly Report",
        reference_name=report_name,
        delayed=True,  # ALWAYS use delayed for bulk
        unsubscribe_message="Unsubscribe from monthly reports",
    )
```

NEVER send bulk emails with `now=True` — this blocks the HTTP request and may timeout.

---

## Notification Log vs Email

Frappe has two parallel notification channels that serve different purposes.

### Notification Log (In-App)

| Aspect | Detail |
|--------|--------|
| DocType | `Notification Log` |
| Location | `frappe/desk/doctype/notification_log/` |
| Delivery | Real-time via socket.io (bell icon in navbar) |
| Types | Mention, Assignment, Share, Alert |
| Persistence | Stored in database, auto-cleaned after 180 days |
| Read tracking | `read` field, `mark_as_read()`, `mark_all_as_read()` |

### When Each Is Used

| Trigger | Notification Log | Email |
|---------|------------------|-------|
| `@mention` in comment | Yes | Conditional (user preference) |
| Document assignment | Yes (type: Assignment) | Conditional |
| Document share | Yes (type: Share) | Conditional |
| Notification DocType (System channel) | Yes | No |
| Notification DocType (Email channel) | No | Yes |
| `frappe.sendmail()` | No | Yes |
| `frappe.publish_realtime()` | No (transient) | No |
| Email Queue failure | Yes (for queue owner) | No |

### Creating Notification Logs Programmatically

```python
from frappe.desk.doctype.notification_log.notification_log import (
    enqueue_create_notification,
)

notification_doc = {
    "type": "Alert",
    "document_type": "Sales Invoice",
    "document_name": "SINV-00001",
    "subject": "Invoice requires attention",
    "from_user": frappe.session.user,
    "email_content": "<p>Please review this invoice.</p>",
}

enqueue_create_notification(
    users=["user1@example.com", "user2@example.com"],
    doc=notification_doc,
)
```

The `enqueue_create_notification` function queues a background job. Individual `Notification Log` records are created per user (skipping the sender unless type is "Alert").

### Email From Notification Log

After inserting a Notification Log, `send_notification_email()` is called IF the user has email notifications enabled for that notification type. This means a single event can produce BOTH an in-app notification AND an email.

---

## Email Templates

### Jinja Templates in frappe.sendmail()

```python
frappe.sendmail(
    recipients=["user@example.com"],
    subject="Status Update",
    template="status_update",       # looks up Email Template DocType
    args={                           # context variables for Jinja
        "customer_name": "ACME Corp",
        "status": "Approved",
        "doc": doc,
    },
)
```

### Email Template DocType

Store reusable email templates in the **Email Template** DocType:

| Field | Purpose |
|-------|---------|
| `name` | Template identifier (used in `template=` parameter) |
| `subject` | Jinja-rendered subject line |
| `response` | Jinja-rendered HTML body |
| `use_html` | Toggle between rich text and raw HTML |

### Template Context Variables

All templates receive:
- `{{ doc }}` — The linked document (if `reference_doctype`/`reference_name` set)
- `{{ frappe.utils }}` — Utility functions
- `{{ nowdate() }}`, `{{ now() }}` — Current date/datetime
- Custom args passed via `args={}` parameter

### Auto-Email on Status Change Pattern

```python
# In hooks.py
doc_events = {
    "Sales Invoice": {
        "on_submit": "myapp.notifications.send_invoice_email"
    }
}

# In myapp/notifications.py
def send_invoice_email(doc, method):
    if doc.status == "Submitted":
        frappe.sendmail(
            recipients=[doc.contact_email],
            subject=f"Invoice {doc.name} Submitted",
            template="invoice_submitted",
            args={"doc": doc},
            reference_doctype=doc.doctype,
            reference_name=doc.name,
        )
```

### Notification DocType with Jinja Template

For no-code email on status change, use Notification DocType:

1. Set **Channel** = Email
2. Set **Document Type** = target DocType
3. Set **Event** = Value Change
4. Set **Value Changed** = status
5. Set **Condition** = `doc.status == "Approved"`
6. Write Jinja template in **Message** field

```html
<h3>{{ doc.doctype }} {{ doc.name }} Approved</h3>
<p>Dear {{ doc.owner }},</p>
<p>Your {{ doc.doctype }} has been approved on {{ frappe.utils.formatdate(frappe.utils.nowdate()) }}.</p>
<table>
  <tr><td>Amount:</td><td>{{ doc.grand_total }}</td></tr>
  <tr><td>Status:</td><td>{{ doc.status }}</td></tr>
</table>
```

---

## Common Patterns

### Check Email Account Health

```python
# Verify outgoing email is configured
account = frappe.db.get_value("Email Account",
    {"enable_outgoing": 1, "default_outgoing": 1}, "name")
if not account:
    frappe.throw("No default outgoing Email Account configured")

# Check for failed accounts
disabled = frappe.get_all("Email Account",
    filters={"enable_incoming": 0, "no_failed": [">", 0]},
    fields=["name", "no_failed"])
```

### Resend Failed Emails

```python
# Reset failed emails for retry
frappe.db.sql("""
    UPDATE `tabEmail Queue`
    SET status='Not Sent', retry=0, error=NULL
    WHERE status='Error'
    AND creation > DATE_SUB(NOW(), INTERVAL 1 DAY)
""")
frappe.db.commit()
```

### Link Existing Email to Document

```python
# Create Communication manually to link email to document
comm = frappe.get_doc({
    "doctype": "Communication",
    "communication_medium": "Email",
    "communication_type": "Communication",
    "sent_or_received": "Sent",
    "sender": "user@example.com",
    "recipients": "client@example.com",
    "subject": "Follow up",
    "content": "<p>Email body</p>",
    "reference_doctype": "Lead",
    "reference_name": "LEAD-00001",
}).insert(ignore_permissions=True)
```
