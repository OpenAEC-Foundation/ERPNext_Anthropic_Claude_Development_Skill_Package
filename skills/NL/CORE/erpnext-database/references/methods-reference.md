# Database Methods Reference

## Document API

### frappe.get_doc
```python
# Bestaand document ophalen
doc = frappe.get_doc('DocType', 'name')

# Nieuw document maken
doc = frappe.get_doc({
    'doctype': 'Task',
    'subject': 'Nieuwe taak'
})

# Single DocType
settings = frappe.get_doc('System Settings')
```

### frappe.get_cached_doc
```python
# Cached versie - sneller voor frequent accessed docs
doc = frappe.get_cached_doc('Company', 'My Company')
```

### frappe.new_doc
```python
doc = frappe.new_doc('Task')
doc.subject = 'Nieuwe taak'
doc.insert()
```

### frappe.get_last_doc
```python
last = frappe.get_last_doc('Task')
last = frappe.get_last_doc('Task', filters={'status': 'Open'})
```

### frappe.delete_doc
```python
frappe.delete_doc('Task', 'TASK00001')
```

### frappe.rename_doc
```python
frappe.rename_doc('Task', 'OLD-NAME', 'NEW-NAME', merge=False)
```

---

## Document Methods

### Insert
```python
doc.insert(
    ignore_permissions=True,    # Bypass permissions
    ignore_links=True,          # Skip link validation
    ignore_if_duplicate=True,   # Geen error bij duplicate
    ignore_mandatory=True       # Skip verplichte velden
)
```

### Save
```python
doc.save(
    ignore_permissions=True,
    ignore_version=True         # Geen version record
)
```

### Delete
```python
doc.delete()
```

### db_set (Direct Update)
```python
# ⚠️ Bypassed validaties!
doc.db_set('status', 'Closed')
doc.db_set({'status': 'Closed', 'priority': 'High'})
doc.db_set('status', 'Closed', update_modified=False)
doc.db_set('status', 'Closed', commit=True)
doc.db_set('status', 'Closed', notify=True)
```

### Reload
```python
doc.reload()  # Herladen van database
```

### Get Previous State
```python
old_doc = doc.get_doc_before_save()
if doc.has_value_changed('status'):
    pass
```

---

## Database API (frappe.db.*)

### get_list / get_all
```python
# get_list - met permissions
tasks = frappe.db.get_list('Task',
    filters={'status': 'Open'},
    fields=['name', 'subject'],
    order_by='creation desc',
    start=0,
    page_length=20
)

# get_all - zonder permissions
all_tasks = frappe.get_all('Task', filters={'status': 'Open'})

# pluck - direct waarden
names = frappe.db.get_list('Task', pluck='name')
```

### get_value
```python
# Enkele waarde
subject = frappe.db.get_value('Task', 'TASK001', 'subject')

# Meerdere waarden
subject, status = frappe.db.get_value('Task', 'TASK001', ['subject', 'status'])

# Als dict
data = frappe.db.get_value('Task', 'TASK001', ['subject', 'status'], as_dict=True)

# Met filters
subject = frappe.db.get_value('Task', {'status': 'Open'}, 'subject')

# Met cache
value = frappe.db.get_value('Company', 'X', 'country', cache=True)
```

### get_single_value
```python
timezone = frappe.db.get_single_value('System Settings', 'time_zone')
```

### set_value
```python
# ⚠️ Bypassed ORM!
frappe.db.set_value('Task', 'TASK001', 'status', 'Closed')
frappe.db.set_value('Task', 'TASK001', {'status': 'Closed', 'priority': 'High'})
frappe.db.set_value('Task', 'TASK001', 'status', 'Closed', update_modified=False)
```

### exists
```python
exists = frappe.db.exists('User', 'admin@example.com')
exists = frappe.db.exists('User', {'email': 'admin@example.com'})
exists = frappe.db.exists('User', 'admin@example.com', cache=True)
```

### count
```python
total = frappe.db.count('Task')
open_count = frappe.db.count('Task', {'status': 'Open'})
```

### delete
```python
frappe.db.delete('Error Log', {'creation': ['<', '2024-01-01']})
```

### truncate
```python
# ⚠️ DDL - Kan niet worden teruggedraaid!
frappe.db.truncate('Error Log')
```

### sql
```python
results = frappe.db.sql("""
    SELECT name, subject FROM `tabTask`
    WHERE status = %(status)s
""", {'status': 'Open'}, as_dict=True)
```

### bulk_update (v15+)
```python
frappe.db.bulk_update('Task', {
    'TASK-0001': {'status': 'Closed'},
    'TASK-0002': {'status': 'Closed'}
}, chunk_size=100)
```

---

## Transactie Control

```python
frappe.db.commit()
frappe.db.rollback()
frappe.db.savepoint('my_savepoint')
frappe.db.rollback(save_point='my_savepoint')
```

### Transaction Hooks (v15+)
```python
frappe.db.before_commit.add(func)
frappe.db.after_commit.add(func)
frappe.db.before_rollback.add(func)
frappe.db.after_rollback.add(func)
```

---

## Index Management

```python
frappe.db.add_index('DocType', ['field1', 'field2'], 'index_name')
frappe.db.add_unique('DocType', ['field1', 'field2'])
```
