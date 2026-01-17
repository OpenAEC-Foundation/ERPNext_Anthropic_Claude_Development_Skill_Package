---
name: erpnext-database
version: 1.0.0
description: Database operaties en ORM patterns voor ERPNext/Frappe v14-v16
author: OpenAEC-Foundation
triggers:
  - frappe database
  - frappe.db
  - frappe.get_doc
  - database query
  - SQL frappe
  - ORM frappe
  - caching frappe
  - database performance
---

# ERPNext Database Operations

## Snel Overzicht

Frappe biedt drie abstractieniveaus voor database operaties:

| Niveau | API | Gebruik |
|--------|-----|---------|
| **High-level ORM** | `frappe.get_doc`, `frappe.new_doc` | Document CRUD met validaties |
| **Mid-level Query** | `frappe.db.get_list`, `frappe.db.get_value` | Lezen met filters |
| **Low-level SQL** | `frappe.db.sql`, `frappe.qb` | Complexe queries, reports |

**REGEL**: Gebruik altijd het hoogste abstractieniveau dat geschikt is.

---

## Decision Tree

```
Wat wil je doen?
│
├─ Document maken/wijzigen/verwijderen?
│  └─ frappe.get_doc() + .insert()/.save()/.delete()
│
├─ Eén document ophalen?
│  ├─ Wijzigt frequent? → frappe.get_doc()
│  └─ Wijzigt zelden? → frappe.get_cached_doc()
│
├─ Lijst van documenten?
│  ├─ Met user permissions? → frappe.db.get_list()
│  └─ Zonder permissions? → frappe.get_all()
│
├─ Enkele veldwaarde?
│  ├─ Regular DocType → frappe.db.get_value()
│  └─ Single DocType → frappe.db.get_single_value()
│
├─ Direct update zonder triggers?
│  └─ frappe.db.set_value() of doc.db_set()
│
└─ Complexe query met JOINs?
   └─ frappe.qb (Query Builder) of frappe.db.sql()
```

---

## Meest Gebruikte Patterns

### Document Ophalen
```python
# Met ORM (triggers validaties)
doc = frappe.get_doc('Sales Invoice', 'SINV-00001')

# Cached (sneller voor frequent accessed docs)
doc = frappe.get_cached_doc('Company', 'My Company')
```

### Lijst Query
```python
# Met user permissions
tasks = frappe.db.get_list('Task',
    filters={'status': 'Open'},
    fields=['name', 'subject'],
    order_by='creation desc',
    page_length=50
)

# Zonder permissions
all_tasks = frappe.get_all('Task', filters={'status': 'Open'})
```

### Enkele Waarde
```python
# Enkele veld
status = frappe.db.get_value('Task', 'TASK001', 'status')

# Meerdere velden
subject, status = frappe.db.get_value('Task', 'TASK001', ['subject', 'status'])

# Als dict
data = frappe.db.get_value('Task', 'TASK001', ['subject', 'status'], as_dict=True)
```

### Document Maken
```python
doc = frappe.get_doc({
    'doctype': 'Task',
    'subject': 'New Task',
    'status': 'Open'
})
doc.insert()
```

### Document Updaten
```python
# Via ORM (met validaties)
doc = frappe.get_doc('Task', 'TASK001')
doc.status = 'Completed'
doc.save()

# Direct (zonder validaties) - voorzichtig!
frappe.db.set_value('Task', 'TASK001', 'status', 'Completed')
```

---

## Filter Operators

```python
{'status': 'Open'}                          # =
{'status': ['!=', 'Cancelled']}             # !=
{'amount': ['>', 1000]}                     # >
{'amount': ['>=', 1000]}                    # >=
{'status': ['in', ['Open', 'Working']]}     # IN
{'date': ['between', ['2024-01-01', '2024-12-31']]}  # BETWEEN
{'subject': ['like', '%urgent%']}           # LIKE
{'description': ['is', 'set']}              # IS NOT NULL
{'description': ['is', 'not set']}          # IS NULL
```

---

## Query Builder (frappe.qb)

```python
Task = frappe.qb.DocType('Task')

results = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject)
    .where(Task.status == 'Open')
    .orderby(Task.creation, order='desc')
    .limit(10)
).run(as_dict=True)
```

### Met JOIN
```python
SI = frappe.qb.DocType('Sales Invoice')
Customer = frappe.qb.DocType('Customer')

results = (
    frappe.qb.from_(SI)
    .inner_join(Customer)
    .on(SI.customer == Customer.name)
    .select(SI.name, Customer.customer_name)
    .where(SI.docstatus == 1)
).run(as_dict=True)
```

---

## Caching

### Basis
```python
# Set/Get
frappe.cache.set_value('key', 'value')
value = frappe.cache.get_value('key')

# Met expiry
frappe.cache.set_value('key', 'value', expires_in_sec=3600)

# Delete
frappe.cache.delete_value('key')
```

### @redis_cache Decorator
```python
from frappe.utils.caching import redis_cache

@redis_cache(ttl=300)  # 5 minuten
def get_dashboard_data(user):
    return expensive_calculation(user)

# Cache invalideren
get_dashboard_data.clear_cache()
```

---

## Transacties

Framework beheert transacties automatisch:

| Context | Commit | Rollback |
|---------|--------|----------|
| POST/PUT request | Na success | Bij exception |
| Background job | Na success | Bij exception |

### Handmatig (zelden nodig)
```python
frappe.db.savepoint('my_savepoint')
try:
    # operaties
    frappe.db.commit()
except:
    frappe.db.rollback(save_point='my_savepoint')
```

---

## Kritieke Regels

### 1. NOOIT String Formatting in SQL
```python
# ❌ SQL Injection risico!
frappe.db.sql(f"SELECT * FROM `tabUser` WHERE name = '{user_input}'")

# ✅ Parameterized
frappe.db.sql("SELECT * FROM `tabUser` WHERE name = %(name)s", {'name': user_input})
```

### 2. NOOIT Commit in Controller Hooks
```python
# ❌ FOUT
def validate(self):
    frappe.db.commit()  # Nooit doen!

# ✅ Framework handelt commits af
```

### 3. ALTIJD Pagineren
```python
# ✅ Limiteer altijd
docs = frappe.get_all('Sales Invoice', page_length=100)
```

### 4. N+1 Queries Vermijden
```python
# ❌ N+1 problem
for name in names:
    doc = frappe.get_doc('Customer', name)

# ✅ Batch fetch
docs = frappe.get_all('Customer', filters={'name': ['in', names]})
```

---

## Versie Verschillen

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| Transaction hooks | ❌ | ✅ | ✅ |
| bulk_update | ❌ | ✅ | ✅ |
| Aggregate syntax | String | String | Dict |

### v16 Aggregate Syntax
```python
# v14/v15
fields=['count(name) as count']

# v16
fields=[{'COUNT': 'name', 'as': 'count'}]
```

---

## Reference Files

Zie de `references/` folder voor gedetailleerde documentatie:

- **methods-reference.md** - Alle Database en Document API methods
- **query-patterns.md** - Filter operators en Query Builder syntax
- **caching-patterns.md** - Redis cache patterns en @redis_cache
- **examples.md** - Complete werkende voorbeelden
- **anti-patterns.md** - Veelgemaakte fouten en hoe te vermijden

---

## Quick Reference

| Actie | Method |
|-------|--------|
| Document ophalen | `frappe.get_doc(doctype, name)` |
| Cached document | `frappe.get_cached_doc(doctype, name)` |
| Nieuw document | `frappe.new_doc(doctype)` of `frappe.get_doc({...})` |
| Document opslaan | `doc.save()` |
| Document invoegen | `doc.insert()` |
| Document verwijderen | `doc.delete()` of `frappe.delete_doc()` |
| Lijst ophalen | `frappe.db.get_list()` / `frappe.get_all()` |
| Enkele waarde | `frappe.db.get_value()` |
| Single waarde | `frappe.db.get_single_value()` |
| Direct update | `frappe.db.set_value()` / `doc.db_set()` |
| Bestaat check | `frappe.db.exists()` |
| Tel records | `frappe.db.count()` |
| Raw SQL | `frappe.db.sql()` |
| Query Builder | `frappe.qb.from_()` |
