# Server Script Events - Complete Reference

## Table of Contents

1. [Event Name Mapping](#event-name-mapping)
2. [Document Lifecycle Order](#document-lifecycle-order)
3. [Event Details](#event-details)
4. [Special Events](#special-events)

---

## Event Name Mapping

### CRITICAL: UI Names vs Internal Hooks

The Server Script UI displays different event names than the internal Frappe hooks. This is essential to understand for correct operation:

| Server Script UI | Internal Hook | Controller Method |
|------------------|---------------|-------------------|
| Before Insert | `before_insert` | `before_insert()` |
| After Insert | `after_insert` | `after_insert()` |
| Before Validate | `before_validate` | `before_validate()` |
| **Before Save** | **`validate`** | `validate()` |
| After Save | `on_update` | `on_update()` |
| Before Submit | `before_submit` | `before_submit()` |
| After Submit | `on_submit` | `on_submit()` |
| Before Cancel | `before_cancel` | `before_cancel()` |
| After Cancel | `on_cancel` | `on_cancel()` |
| Before Delete | `on_trash` | `on_trash()` |
| After Delete | `after_delete` | `after_delete()` |

### Why "Before Save" = `validate`?

In Frappe's architecture:
- `validate` is the primary hook for pre-save validation and calculations
- `before_save` also exists but runs AFTER `validate`
- The UI chose "Before Save" as a more intuitive name for `validate`

---

## Document Lifecycle Order

### New Document Insert

```
1. before_insert      ← "Before Insert"
2. before_naming
3. autoname
4. before_validate    ← "Before Validate"
5. validate           ← "Before Save" ⚠️
6. before_save
7. [DB INSERT]
8. after_insert       ← "After Insert"
9. on_update          ← "After Save"
10. on_change
```

### Existing Document Update

```
1. before_validate    ← "Before Validate"
2. validate           ← "Before Save" ⚠️
3. before_save
4. [DB UPDATE]
5. on_update          ← "After Save"
6. on_change
```

### Document Submit

```
1. before_validate    ← "Before Validate"
2. validate           ← "Before Save" ⚠️
3. before_submit      ← "Before Submit"
4. [DB UPDATE: docstatus=1]
5. on_update          ← "After Save"
6. on_submit          ← "After Submit"
7. on_change
```

### Document Cancel

```
1. before_cancel      ← "Before Cancel"
2. [DB UPDATE: docstatus=2]
3. on_cancel          ← "After Cancel"
4. on_change
```

### Document Delete

```
1. on_trash           ← "Before Delete"
2. [DB DELETE]
3. after_delete       ← "After Delete"
```

---

## Event Details

### Before Insert

**When**: Only for NEW documents, before DB insert
**Use**: Set initial values, pre-insert validation
**doc.name**: NOT yet available (unless manually set)

```python
# Example: Default values for new document
if not doc.priority:
    doc.priority = "Medium"

doc.created_by_script = 1
```

### After Insert

**When**: Immediately after first DB insert
**Use**: Create related records, notifications
**doc.name**: Now available

```python
# Example: Create related ToDo
frappe.get_doc({
    "doctype": "ToDo",
    "reference_type": doc.doctype,
    "reference_name": doc.name,
    "description": f"Review {doc.name}"
}).insert(ignore_permissions=True)
```

### Before Validate / Before Save (validate)

**When**: Before every save (new and update)
**Use**: Validation, calculations, auto-fill fields
**Throw errors here**: Prevents save

```python
# Before Validate: before framework validation
# Before Save (validate): for custom validation

if doc.discount_percentage > 50:
    frappe.throw("Discount cannot exceed 50%")

# Auto-calculation
doc.total = sum(item.amount for item in doc.items)
```

### After Save (on_update)

**When**: After successful save to DB
**Use**: Side effects, sync with external systems
**Note**: Changes to doc are NOT automatically saved

```python
# Example: Update related document
if doc.status == "Approved":
    linked = frappe.get_doc("Project", doc.project)
    linked.approval_date = frappe.utils.today()
    linked.save(ignore_permissions=True)
```

### Before Submit / After Submit

**When**: Only for submittable documents (with docstatus)
**Before Submit**: Last chance to validate/modify
**After Submit**: Document is now immutable

```python
# Before Submit
if doc.grand_total > 100000 and not doc.manager_approval:
    frappe.throw("Manager approval required for amounts over 100,000")

# After Submit
frappe.sendmail(
    recipients=[doc.owner],
    subject=f"{doc.name} submitted",
    message=f"Document {doc.name} has been successfully submitted."
)
```

### Before Cancel / After Cancel

**When**: When cancelling submitted document
**Before Cancel**: Validate if cancel is allowed
**After Cancel**: Cleanup, reverse effects

```python
# Before Cancel
linked_docs = frappe.get_all("Payment Entry",
    filters={"reference_name": doc.name, "docstatus": 1})
if linked_docs:
    frappe.throw("Cannot cancel: there are linked payments")

# After Cancel
doc.add_comment("Info", "Document cancelled by system")
```

### Before Delete / After Delete

**When**: When permanently deleting
**Before Delete (on_trash)**: Last chance to block
**After Delete**: Cleanup external references

```python
# Before Delete
if doc.has_linked_documents:
    frappe.throw("Delete linked documents first")

# After Delete
frappe.log_error(f"Document {doc.name} deleted", "Audit Log")
```

---

## Special Events

### on_change

Runs after EVERY change (save, submit, cancel). Useful for audit logging:

```python
# Triggered by save, submit, AND cancel
frappe.log_error(
    f"Document {doc.name} changed to status {doc.docstatus}",
    "Change Log"
)
```

### Not available in Server Scripts

The following events are only available in Document Controllers, NOT in Server Scripts:

- `autoname` - Custom naming logic
- `before_naming` - Pre-naming hook
- `db_insert` / `db_update` - Immediately after DB operation
- `get_feed` - Activity feed customization

---

## Common Patterns

### Only on status change

```python
# In After Save: check if status changed
# Note: get_doc_before_save() not available in Server Scripts
# Alternative: use flags or custom field

if doc.status == "Approved" and doc.previous_status != "Approved":
    # Action on approval
    pass
```

### Prevent infinite loops

```python
# Use flags to prevent recursive saves
if doc.flags.get("skip_custom_logic"):
    # Skip to prevent loop
    pass
else:
    # Normal logic
    doc.flags.skip_custom_logic = True
    # ... changes
```
