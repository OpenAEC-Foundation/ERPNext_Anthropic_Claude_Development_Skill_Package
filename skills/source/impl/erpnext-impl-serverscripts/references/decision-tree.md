# Server Script Decision Trees

## Complete Decision: Which Implementation Approach?

```
START: What do you need to implement?
│
├─► Document automation (validation, auto-fill, notifications)
│   │
│   ├─► Need external libraries or complex transactions?
│   │   │
│   │   ├─► YES → Use Controller in custom app
│   │   │         (See erpnext-syntax-controllers)
│   │   │
│   │   └─► NO → Server Script: Document Event
│   │             └─► Continue to "Which Event?" below
│   │
│   └─► Need to run on multiple doctypes?
│       │
│       ├─► YES → hooks.py doc_events
│       │         (See erpnext-syntax-hooks)
│       │
│       └─► NO → Server Script: Document Event
│
├─► Custom REST API endpoint
│   │
│   ├─► Need file uploads or complex processing?
│   │   │
│   │   ├─► YES → @frappe.whitelist() in custom app
│   │   │         (See erpnext-syntax-whitelisted)
│   │   │
│   │   └─► NO → Server Script: API
│   │             └─► Allow Guest: based on auth needs
│   │
│   └─► Needs database transaction control?
│       │
│       ├─► YES → Controller whitelisted method
│       │
│       └─► NO → Server Script: API
│
├─► Scheduled/background task
│   │
│   ├─► Simple task (< 100 records, no external calls)?
│   │   └─► Server Script: Scheduler Event
│   │
│   ├─► Complex task or external integrations?
│   │   └─► hooks.py scheduler_events + custom method
│   │
│   └─► Need to enqueue background job?
│       └─► Controller with frappe.enqueue()
│
└─► Dynamic permission filtering
    │
    ├─► Filter list view per user/role?
    │   └─► Server Script: Permission Query
    │
    └─► Custom has_permission logic?
        └─► hooks.py has_permission
            (See erpnext-permissions)
```

## Decision: Which Document Event?

```
WHAT ACTION TRIGGERS YOUR CODE?
│
├─► BEFORE document operations
│   │
│   ├─► Before any validation runs?
│   │   └─► Before Validate (before_validate)
│   │       Use for: Pre-processing, setting defaults
│   │
│   ├─► Validate data / Auto-calculate before save?
│   │   └─► Before Save (validate)           ← MOST COMMON
│   │       Use for: Validation, calculations, auto-fill
│   │
│   ├─► Check conditions before submit?
│   │   └─► Before Submit (before_submit)
│   │       Use for: Submit-time validation, approval checks
│   │
│   └─► Prevent or validate cancel?
│       └─► Before Cancel (before_cancel)
│           Use for: Check linked docs, prevent cancel
│
├─► AFTER document operations
│   │
│   ├─► React to new document (first save)?
│   │   └─► After Insert (after_insert)
│   │       Use for: Welcome emails, create related docs
│   │
│   ├─► React to any save (new or update)?
│   │   └─► After Save (on_update)
│   │       Use for: Audit logs, notifications, sync
│   │
│   ├─► React to submission?
│   │   └─► After Submit (on_submit)
│   │       Use for: Stock ledger, GL entries, workflows
│   │
│   └─► React to cancellation?
│       └─► After Cancel (on_cancel)
│           Use for: Reverse entries, cleanup
│
└─► DELETE operations
    │
    ├─► Prevent or validate delete?
    │   └─► Before Delete (on_trash)
    │       Use for: Check dependencies, prevent delete
    │
    └─► Cleanup after delete?
        └─► After Delete (after_delete)
            Use for: Remove related records, cleanup files
```

## Decision: Validation Location

```
WHERE SHOULD VALIDATION HAPPEN?
│
├─► UX feedback only (can be bypassed)?
│   └─► Client Script validate event
│
├─► MUST always run, even via API/import?
│   │
│   ├─► Simple validation (single doctype, no imports)?
│   │   └─► Server Script: Before Save
│   │
│   └─► Complex validation or multiple doctypes?
│       └─► Controller validate method
│
└─► Data integrity (can never be violated)?
    └─► BOTH client + server validation
        (Server is authoritative)
```

## Decision: API Authentication

```
WHO CAN ACCESS YOUR API?
│
├─► Anyone (public, no login)?
│   └─► Server Script API with Allow Guest: Yes
│       ⚠️ Still validate/sanitize all inputs!
│
├─► Any logged-in user?
│   └─► Server Script API with Allow Guest: No
│       Add: Permission check in script
│
├─► Specific roles only?
│   └─► Server Script API with Allow Guest: No
│       Add: frappe.has_permission() or role check
│
└─► External systems (API key auth)?
    └─► @frappe.whitelist() in custom app
        Use: frappe.get_request_header("Authorization")
```

## Decision: Scheduler Frequency

| Cron Pattern | Meaning | Use Case |
|--------------|---------|----------|
| `* * * * *` | Every minute | Real-time sync (use sparingly) |
| `*/15 * * * *` | Every 15 min | Status updates, queue processing |
| `0 * * * *` | Every hour | Aggregations, cache refresh |
| `0 9 * * *` | Daily 9:00 | Morning reports, reminders |
| `0 2 * * *` | Daily 2:00 | Nightly cleanup, backups |
| `0 9 * * 1` | Monday 9:00 | Weekly reports |
| `0 6 1 * *` | 1st of month | Monthly reports |

## Quick Reference: Event Timing

```
Document Lifecycle Order:
────────────────────────────────────────────────────────────

NEW DOCUMENT:
  before_insert → before_validate → validate → after_insert → on_update

EXISTING DOCUMENT:
  before_validate → validate → on_update

SUBMIT:
  before_submit → on_submit

CANCEL:
  before_cancel → on_cancel

DELETE:
  on_trash → after_delete

────────────────────────────────────────────────────────────
```
