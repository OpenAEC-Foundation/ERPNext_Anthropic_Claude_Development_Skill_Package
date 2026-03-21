# Document API Complete Reference

Comprehensive reference for ALL `frappe.model.document.Document` class methods.
This consolidates the full Document API in one place for quick lookup.

Source: [Frappe Document API](https://docs.frappe.io/framework/user/en/api/document)

---

## 1. CRUD Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `insert` | `insert(ignore_permissions=False, ignore_links=False, ignore_if_duplicate=False, ignore_mandatory=False, set_name=None, set_child_names=True)` | `self` | Insert new document. Runs full lifecycle: before_insert → validate → db_insert → after_insert → on_update. |
| `save` | `save(ignore_permissions=False, ignore_version=False)` | `self` | Save existing document. Runs: before_validate → validate → before_save → db_update → on_update. |
| `submit` | `submit()` | `self` | Submit document (docstatus 0→1). ONLY for submittable DocTypes. Runs validate then on_submit. |
| `cancel` | `cancel()` | `self` | Cancel submitted document (docstatus 1→2). Runs before_cancel → on_cancel. |
| `amend_doc` | `amend_doc()` | `Document` | Create amended copy from cancelled document. Sets `amended_from` on the new doc. |
| `delete` | `delete(ignore_permissions=False, force=False, ignore_doctypes=None, for_reload=False)` | `None` | Delete document and linked records. Runs on_trash → after_delete. |

### CRUD via `frappe` module (not doc methods)

| Function | Signature | Returns | Description |
|---|---|---|---|
| `frappe.get_doc` | `get_doc(doctype, name=None, **kwargs)` | `Document` | Retrieve existing doc or create new in memory from dict. |
| `frappe.new_doc` | `new_doc(doctype, **kwargs)` | `Document` | Create a new document in memory with defaults applied. |
| `frappe.get_last_doc` | `get_last_doc(doctype, filters=None, order_by="creation desc")` | `Document` | Return most recently created document matching filters. |
| `frappe.get_cached_doc` | `get_cached_doc(doctype, name)` | `Document` | Retrieve from cache first, database second. Read-only — NEVER modify and save. |
| `frappe.delete_doc` | `delete_doc(doctype, name, force=0, ignore_doctypes=None, for_reload=False, ignore_permissions=False, flags=None)` | `None` | Delete document by doctype and name. |
| `frappe.rename_doc` | `rename_doc(doctype, old_name, new_name, force=False, merge=False, ignore_permissions=False, ignore_if_exists=False)` | `str` | Rename document (changes primary key). Returns new name. |
| `frappe.copy_doc` | `copy_doc(doc, ignore_no_copy=True)` | `Document` | Deep copy document. Clears name, amended_from, and "No Copy" fields. |

---

## 2. Field Access Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `get` | `get(fieldname, default=None)` | `any` | Safely retrieve field value. Returns child table as list. |
| `set` | `set(fieldname, value)` | `None` | Set field value. For child tables, pass list of dicts to replace all rows. |
| `as_dict` | `as_dict(no_nulls=False, no_default_fields=False)` | `dict` | Serialize document to dictionary. |
| `update` | `update(d)` | `None` | Bulk-update fields from dictionary `d`. |
| `get_valid_dict` | `get_valid_dict(sanitize=True, convert_dates_to_str=False)` | `dict` | Return dict with only fields defined in DocType meta. |
| `is_new` | `is_new()` | `bool` | True if document has not yet been saved to database. |
| `has_value_changed` | `has_value_changed(fieldname)` | `bool` | True if field value differs from saved version. Available from validate onwards. |
| `get_doc_before_save` | `get_doc_before_save()` | `Document \| None` | Return document state before current modifications. None for new documents. |

### Direct attribute access

```python
# These are equivalent:
value = doc.get("customer")
value = doc.customer

# Setting:
doc.set("status", "Completed")
doc.status = "Completed"
```

---

## 3. Database Shortcut Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `db_set` | `db_set(fieldname, value=None, notify=True, commit=False, update_modified=True)` | `None` | Direct DB field update. Use in post-save hooks (on_update, on_submit). Also accepts a dict: `db_set({"field1": val1, "field2": val2})`. |
| `reload` | `reload()` | `None` | Refresh all fields from database. Discards in-memory changes. |
| `get_doc_before_save` | `get_doc_before_save()` | `Document \| None` | Returns a snapshot of the document as it was before the current save operation. |
| `db_insert` | `db_insert(*args, **kwargs)` | `None` | Low-level insert. Bypasses ALL hooks and validation. Use only for bulk ops or Virtual DocTypes. |
| `db_update` | `db_update()` | `None` | Low-level update. Bypasses ALL hooks and validation. Use only for performance-critical bulk ops. |

### When to use `db_set` vs `save`

```
Need to update a field AFTER on_update?  → db_set()
Need full validation and hooks?          → save()
Need to update another document?         → frappe.db.set_value()
Bulk update thousands of records?        → frappe.db.sql() or db_update()
```

---

## 4. Permission Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `has_permission` | `has_permission(permtype="read", user=None)` | `bool` | Check if user has specified permission on this document. |
| `check_permission` | `check_permission(permtype="read")` | `None` | Same as has_permission but raises `frappe.PermissionError` if denied. |
| `raise_no_permission_to` | `raise_no_permission_to(perm_type)` | `None` | Raise a formatted permission error for the given permission type. |
| `add_comment` | `add_comment(comment_type="Comment", text=None, comment_email=None, comment_by=None)` | `Comment` | Add a comment to the document timeline. |

### Comment types

`Comment`, `Edit`, `Created`, `Submitted`, `Cancelled`, `Info`, `Label`, `Shared`, `Assigned`, `Attachment`, `Like`

### Permission check pattern

```python
def validate(self):
    if self.total > 100000:
        if not frappe.has_permission("Sales Order", "submit", user=frappe.session.user):
            frappe.throw(_("Not authorized for high-value orders"))
```

---

## 5. Flags

Flags are runtime-only attributes (NOT saved to database) that control behavior during the current request.

### doc.flags (per-document)

| Flag | Type | Description |
|---|---|---|
| `ignore_permissions` | `bool` | Skip all permission checks for this document. |
| `ignore_validate` | `bool` | Skip the `validate` controller method. |
| `ignore_mandatory` | `bool` | Skip mandatory field checks. |
| `ignore_links` | `bool` | Skip Link field validation. |
| `in_insert` | `bool` | Set by Frappe during insert. True inside before_insert through after_insert. |
| `ignore_if_duplicate` | `bool` | Silently skip insert if DuplicateEntryError. |
| `ignore_update_after_submit` | `bool` | Allow field changes on submitted documents. |
| `ignore_validate_update_after_submit` | `bool` | Skip update-after-submit field restrictions. |
| `notify_update` | `bool` | [v15+] Trigger realtime update notification after db_set. |
| `from_linked_doc` | `bool` | Custom flag — use to prevent recursion between linked docs. |

### frappe.flags (global, per-request)

| Flag | Type | Description |
|---|---|---|
| `frappe.flags.in_import` | `bool` | True during data import. |
| `frappe.flags.in_install` | `bool` | True during app installation. |
| `frappe.flags.in_migrate` | `bool` | True during bench migrate. |
| `frappe.flags.in_test` | `bool` | True during test execution. |
| `frappe.flags.mute_emails` | `bool` | Suppress all email sending. |
| `frappe.flags.mute_messages` | `bool` | Suppress all msgprint output. |

### Usage pattern

```python
doc.flags.ignore_permissions = True
doc.save()
# Or inline:
doc.insert(ignore_permissions=True)

# Custom flag for recursion prevention:
def on_update(self):
    if self.flags.get("skip_cascade"):
        return
    linked = frappe.get_doc("Other Doc", self.linked_name)
    linked.flags.skip_cascade = True
    linked.save()
```

---

## 6. Workflow and Docstatus

### doc.docstatus

| Value | State | Description |
|---|---|---|
| `0` | Draft | Default state. Fully editable. |
| `1` | Submitted | Locked. Only "Allow on Submit" fields editable. |
| `2` | Cancelled | Fully locked. Cannot be edited or re-submitted. |

### Docstatus transitions

```
0 (Draft) --submit()--> 1 (Submitted) --cancel()--> 2 (Cancelled)
                                                         |
                                                    amend_doc()
                                                         |
                                                         v
                                                    0 (New Draft with amended_from set)
```

### Workflow state (separate from docstatus)

```python
doc.workflow_state           # Current workflow state name (str)
frappe.model.workflow.apply_workflow(doc, action)  # Trigger workflow action
```

NEVER set `doc.docstatus` directly. ALWAYS use `doc.submit()` and `doc.cancel()`.

---

## 7. Child Table Methods

Child table rows are instances of `Document` with extra fields: `parent`, `parenttype`, `parentfield`, `idx`.

| Method | Signature | Returns | Description |
|---|---|---|---|
| `append` | `append(fieldname, value=None)` | `Document` | Add one row to child table. Returns the new row object. |
| `extend` | `extend(fieldname, rows)` | `None` | Add multiple rows from a list of dicts. |
| `remove` | `remove(row)` | `None` | Remove a specific row object from its child table. |
| `get` (with filters) | `get(fieldname, filters=None, limit=0)` | `list` | Get child rows, optionally filtered by dict. |
| `set` | `set(fieldname, value)` | `None` | Replace entire child table with list of dicts. |

### Examples

```python
# Append single row
row = self.append("items", {
    "item_code": "ITEM-001",
    "qty": 10,
    "rate": 100.0
})
row.warehouse = "Main - WH"  # Can set more fields on returned row

# Extend with multiple rows
self.extend("items", [
    {"item_code": "ITEM-001", "qty": 10},
    {"item_code": "ITEM-002", "qty": 5},
])

# Get with filters
pending = self.get("items", filters={"status": "Pending"})
# Equivalent list comprehension (more common):
pending = [row for row in self.items if row.status == "Pending"]

# Remove a row
for row in self.items:
    if row.qty == 0:
        self.remove(row)

# Replace entire child table
self.set("items", [{"item_code": "NEW-001", "qty": 1}])

# Clear child table
self.set("items", [])

# Iterate
for idx, row in enumerate(self.items):
    row.idx = idx + 1  # Re-index after removal

# Count
total_qty = sum(row.qty for row in self.items)
```

### Child table special fields

| Field | Type | Description |
|---|---|---|
| `parent` | `str` | Name of the parent document. |
| `parenttype` | `str` | DocType of the parent document. |
| `parentfield` | `str` | Fieldname of the table field in parent. |
| `idx` | `int` | Row index (1-based). Frappe auto-manages this. |
| `name` | `str` | Unique row identifier (auto-generated hash). |

---

## 8. Utility Methods

| Method | Signature | Returns | Description |
|---|---|---|---|
| `run_method` | `run_method(method, *args, **kwargs)` | `any` | Execute controller method AND trigger associated doc_events and server scripts. |
| `get_title` | `get_title()` | `str` | Return document title based on `title_field` meta configuration. |
| `get_url` | `get_url()` | `str` | Return desk URL path (e.g., `/app/sales-order/SO-00001`). |
| `notify_update` | `notify_update()` | `None` | Publish realtime event so open browser forms refresh. |
| `queue_action` | `queue_action(action, **kwargs)` | `None` | Execute controller method asynchronously in background worker. |
| `add_seen` | `add_seen(user=None)` | `None` | Mark document as seen by user (updates `_seen` field). |
| `add_viewed` | `add_viewed(user=None)` | `None` | Log a view access for the user. |
| `add_tag` | `add_tag(tag)` | `None` | Associate a tag with this document. |
| `get_tags` | `get_tags()` | `list[str]` | Return all tags associated with this document. |
| `get_url` | `get_url()` | `str` | Return URL path for this document in Frappe Desk. |
| `get_signature` | `get_signature()` | `str` | Return email signature of document owner. |
| `get_liked_by` | `get_liked_by()` | `list[str]` | Return list of users who liked this document. |

### run_method vs direct call

```python
# Direct call — runs ONLY the controller method:
doc.validate()

# run_method — runs controller method + doc_events + server scripts:
doc.run_method("validate")
```

ALWAYS use `run_method()` when you need hooks to fire. Use direct calls only inside the controller itself.

### queue_action pattern

```python
class HeavyDoc(Document):
    def on_submit(self):
        # Run email sending in background worker
        self.queue_action("send_notifications", recipients=self.get_recipients())

    def send_notifications(self, recipients):
        for r in recipients:
            frappe.sendmail(recipients=[r], subject="Submitted", message="Done")
```

---

## 9. Naming

### autoname property (set in DocType definition)

| Pattern | Example Config | Example Output | Version |
|---|---|---|---|
| `field:fieldname` | `field:customer_name` | `ABC Company` | All |
| `naming_series:` | `naming_series:` | `SO-2024-00001` | All |
| Expression | `PRE-.#####` | `PRE-00001` | All |
| `hash` | `hash` | `a1b2c3d4e5` | All |
| `Prompt` | `Prompt` | User-entered | All |
| `autoincrement` | `autoincrement` | `1`, `2`, `3` | All |
| `UUID` | `UUID` | `550e8400-e29b-...` | v16+ |
| Format string | `INV-{YYYY}-{####}` | `INV-2024-0001` | Deprecated v16 |
| Controller method | `autoname()` | Any | All |

### doc.name

- Set during insert, between `before_naming` and `autoname` hooks.
- Immutable after insert (use `frappe.rename_doc()` to change).
- ALWAYS a string. Acts as primary key in the database.

### Custom autoname in controller

```python
from frappe.model.naming import getseries, make_autoname

class Project(Document):
    def autoname(self):
        # Option 1: getseries (counter-based)
        prefix = f"P-{self.customer[:3].upper()}-"
        self.name = getseries(prefix, 3)  # P-ACM-001

        # Option 2: make_autoname (pattern-based)
        self.name = make_autoname("PRJ-.YYYY.-.#####")  # PRJ-2024-00001
```

### naming_series

When `autoname = "naming_series:"`, the DocType gets a `naming_series` field. Users select from options defined in DocType or Property Setter.

```python
# In DocType JSON or via Property Setter:
# naming_series options: "SO-.YYYY.-\nSO-NEW-.YYYY.-"

# Programmatic naming series override:
doc.naming_series = "CUSTOM-.####"
doc.insert()
```

---

## Method Quick-Lookup Table

| Category | Method | Modifies DB | Runs Hooks |
|---|---|---|---|
| **CRUD** | `insert()` | Yes | Yes |
| | `save()` | Yes | Yes |
| | `submit()` | Yes | Yes |
| | `cancel()` | Yes | Yes |
| | `delete()` | Yes | Yes |
| | `amend_doc()` | No (creates copy) | No |
| **Field** | `get()` | No | No |
| | `set()` | No | No |
| | `as_dict()` | No | No |
| | `update()` | No | No |
| | `is_new()` | No | No |
| | `has_value_changed()` | No | No |
| | `get_doc_before_save()` | No | No |
| **DB Shortcut** | `db_set()` | Yes | No (notify optional) |
| | `reload()` | No | No |
| | `db_insert()` | Yes | No |
| | `db_update()` | Yes | No |
| **Permission** | `has_permission()` | No | No |
| | `check_permission()` | No | No |
| | `raise_no_permission_to()` | No | No |
| **Child Table** | `append()` | No | No |
| | `extend()` | No | No |
| | `remove()` | No | No |
| **Utility** | `run_method()` | Depends | Yes |
| | `queue_action()` | Depends | Yes (async) |
| | `notify_update()` | No | No |
| | `add_comment()` | Yes | No |
| | `get_title()` | No | No |
| | `get_url()` | No | No |
| | `add_tag()` | Yes | No |
| | `get_tags()` | No | No |
