# Research Document: ERPNext Database Operations
> **Fase**: 3.1  
> **Skill**: erpnext-database  
> **Datum**: 2026-01-17  
> **Bronnen**: docs.frappe.io (Database API, Document API, Query Builder, Caching)

---

## 1. Overzicht Database Lagen in Frappe

Frappe biedt drie abstractieniveaus voor database operaties:

| Niveau | API | Use Case | Permissions |
|--------|-----|----------|-------------|
| **High-level ORM** | `frappe.get_doc`, `frappe.new_doc` | Document CRUD met validaties | Toegepast |
| **Mid-level Query** | `frappe.db.get_list`, `frappe.db.get_value` | Lezen met filters | Optioneel |
| **Low-level SQL** | `frappe.db.sql`, `frappe.qb` | Complexe queries, reports | Geen |

**GOUDEN REGEL**: Gebruik altijd het hoogste abstractieniveau dat geschikt is voor je use case.

---

## 2. Document API (High-Level ORM)

### 2.1 frappe.get_doc

Haalt een bestaand document op of maakt een nieuw document object.

```python
# Bestaand document ophalen
doc = frappe.get_doc('Sales Invoice', 'SINV-00001')

# Nieuw document maken (nog niet in database)
doc = frappe.get_doc({
    'doctype': 'Task',
    'subject': 'New Task',
    'status': 'Open'
})

# Met keyword arguments
doc = frappe.get_doc(doctype='User', email='test@example.com')

# Single DocType (geen name nodig)
settings = frappe.get_doc('System Settings')
```

**Parameters**:
- `doctype` (str): DocType naam
- `name` (str): Document naam/ID
- OF `dict`: Dictionary met doctype en velden

**Returns**: `Document` object

**Raises**: `frappe.DoesNotExistError` als document niet bestaat

### 2.2 frappe.get_cached_doc

Zelfde als `frappe.get_doc` maar kijkt eerst in cache.

```python
# Cached versie - sneller voor frequent accessed documenten
doc = frappe.get_cached_doc('Company', 'My Company')
```

**Gebruik wanneer**:
- Document wijzigt niet vaak
- Document wordt frequent opgevraagd
- Read-only operaties

**NIET gebruiken wanneer**:
- Document moet altijd actueel zijn
- Direct na wijzigingen

### 2.3 frappe.new_doc

Alternatieve manier om nieuw document te maken.

```python
doc = frappe.new_doc('Task')
doc.subject = 'New Task'
doc.status = 'Open'
doc.insert()
```

### 2.4 frappe.get_last_doc

Haalt het laatst aangemaakte document op.

```python
# Laatste Task
last_task = frappe.get_last_doc('Task')

# Met filters
last_cancelled = frappe.get_last_doc('Task', filters={'status': 'Cancelled'})

# Andere sortering
last_by_timestamp = frappe.get_last_doc('Task', order_by='timestamp desc')
```

### 2.5 Document Methods

#### Insert
```python
doc.insert(
    ignore_permissions=True,    # Bypass permission checks
    ignore_links=True,          # Skip Link field validation
    ignore_if_duplicate=True,   # Don't error on duplicate
    ignore_mandatory=True       # Skip required field checks
)
```

#### Save
```python
doc.save(
    ignore_permissions=True,    # Bypass permission checks
    ignore_version=True         # Don't create version record
)
```

#### Delete
```python
doc.delete()
# Of via frappe
frappe.delete_doc('Task', 'TASK00002')
```

#### db_set (Direct Database Update)
```python
# Bypass ORM - geen validate/on_update triggers!
doc.db_set('status', 'Closed')

# Meerdere velden
doc.db_set({'status': 'Closed', 'priority': 'High'})

# Zonder modified timestamp update
doc.db_set('status', 'Closed', update_modified=False)

# Met commit
doc.db_set('status', 'Closed', commit=True)

# Met realtime notify
doc.db_set('status', 'Closed', notify=True)
```

**⚠️ WAARSCHUWING**: `db_set` bypassed alle validaties en controller methods!

#### Reload
```python
# Herladen van database na externe wijzigingen
doc.reload()
```

#### Get Previous State
```python
# In validate/before_save
old_doc = doc.get_doc_before_save()
if old_doc.status != doc.status:
    # Status is gewijzigd
    pass

# Alternatief
if doc.has_value_changed('status'):
    pass
```

---

## 3. Database API (frappe.db.*)

### 3.1 frappe.db.get_list / frappe.get_all

Query records met filters. `get_list` past user permissions toe, `get_all` niet.

```python
# Basis query
tasks = frappe.db.get_list('Task')
# Output: [{'name': 'TASK001'}, {'name': 'TASK002'}]

# Met pluck - direct lijst van waarden
names = frappe.db.get_list('Task', pluck='name')
# Output: ['TASK001', 'TASK002']

# Complete query met alle opties
tasks = frappe.db.get_list('Task',
    filters={'status': 'Open'},
    or_filters={'priority': ['in', ['High', 'Urgent']]},
    fields=['name', 'subject', 'status', 'priority'],
    order_by='creation desc',
    group_by='status',
    start=0,
    page_length=20
)

# get_all - zonder permission filtering
all_tasks = frappe.get_all('Task', 
    filters={'status': 'Open'},
    fields=['name', 'subject']
)
```

**Parameters**:
| Parameter | Type | Beschrijving |
|-----------|------|--------------|
| `doctype` | str | DocType naam |
| `filters` | dict/list | AND filters |
| `or_filters` | dict/list | OR filters |
| `fields` | list | Velden om op te halen |
| `order_by` | str | Sortering |
| `group_by` | str | Groepering |
| `start` | int | Offset voor paginering |
| `page_length` | int | Aantal records |
| `pluck` | str | Haal direct veldwaarde als lijst |
| `as_list` | bool | Return als tuples i.p.v. dicts |
| `ignore_ifnull` | bool | Negeer NULL waarden in filters |

### 3.2 Filter Operators

```python
# Gelijkheid
{'status': 'Open'}

# Niet gelijk
{'status': ['!=', 'Cancelled']}

# Groter/kleiner dan
{'amount': ['>', 1000]}
{'amount': ['>=', 1000]}
{'amount': ['<', 5000]}
{'amount': ['<=', 5000]}

# IN lijst
{'status': ['in', ['Open', 'Working', 'Pending']]}
{'status': ['not in', ['Cancelled', 'Closed']]}

# LIKE (pattern matching)
{'subject': ['like', '%urgent%']}
{'email': ['like', '%@example.com']}

# BETWEEN
{'date': ['between', ['2024-01-01', '2024-12-31']]}

# IS NULL / IS NOT NULL
{'description': ['is', 'set']}      # IS NOT NULL
{'description': ['is', 'not set']}  # IS NULL

# Nested filters (AND binnen OR)
filters = [
    ['status', '=', 'Open'],
    ['priority', 'in', ['High', 'Urgent']]
]
```

### 3.3 frappe.db.get_value

Haalt specifieke veld(en) van één document op.

```python
# Enkele waarde
subject = frappe.db.get_value('Task', 'TASK00002', 'subject')

# Meerdere waarden (tuple)
subject, status = frappe.db.get_value('Task', 'TASK00002', ['subject', 'status'])

# Als dictionary
task_dict = frappe.db.get_value('Task', 'TASK00002', 
    ['subject', 'status'], as_dict=True)
# {'subject': '...', 'status': '...'}

# Met filters (eerste match)
subject = frappe.db.get_value('Task', {'status': 'Open'}, 'subject')

# Met cache
company = frappe.db.get_value('Company', 'My Company', 'country', cache=True)
```

### 3.4 frappe.db.get_single_value

Voor Single DocTypes.

```python
timezone = frappe.db.get_single_value('System Settings', 'time_zone')
company = frappe.db.get_single_value('Global Defaults', 'default_company')
```

### 3.5 frappe.db.set_value

Direct database update zonder ORM.

```python
# Enkele waarde
frappe.db.set_value('Task', 'TASK00002', 'status', 'Closed')

# Meerdere waarden
frappe.db.set_value('Task', 'TASK00002', {
    'status': 'Closed',
    'completed_on': frappe.utils.now()
})

# Zonder modified timestamp update
frappe.db.set_value('Task', 'TASK00002', 'status', 'Closed', 
    update_modified=False)
```

**⚠️ WAARSCHUWING**: Bypassed ORM triggers (validate, on_update). Gebruik alleen voor:
- Hidden fields
- Bulk updates waar performance kritiek is
- Background jobs waar je weet wat je doet

### 3.6 frappe.db.exists

Check of document bestaat.

```python
# Met name
exists = frappe.db.exists('User', 'admin@example.com')

# Met filters
exists = frappe.db.exists('User', {'email': 'admin@example.com'})

# Dict syntax
exists = frappe.db.exists({'doctype': 'User', 'email': 'admin@example.com'})

# Met cache
exists = frappe.db.exists('User', 'admin@example.com', cache=True)
```

### 3.7 frappe.db.count

Tel records.

```python
# Totaal aantal
total = frappe.db.count('Task')

# Met filters
open_tasks = frappe.db.count('Task', {'status': 'Open'})
```

### 3.8 frappe.db.delete

Verwijder records direct (DML - kan worden teruggedraaid).

```python
# Met filters
frappe.db.delete('Error Log', {
    'creation': ['<', '2024-01-01']
})

# Alle records (voorzichtig!)
frappe.db.delete('Error Log')
```

### 3.9 frappe.db.truncate

Leeg tabel (DDL - kan NIET worden teruggedraaid, commit gebeurt automatisch).

```python
frappe.db.truncate('Error Log')
```

---

## 4. Raw SQL (frappe.db.sql)

Voor complexe queries die niet via ORM kunnen.

```python
# Basis query
results = frappe.db.sql("""
    SELECT name, subject, status
    FROM `tabTask`
    WHERE status = 'Open'
""")
# Returns: tuple of tuples

# Als dictionaries
results = frappe.db.sql("""
    SELECT name, subject, status
    FROM `tabTask`
    WHERE status = 'Open'
""", as_dict=True)
# Returns: list of dicts

# Met parameters (SQL injection preventie!)
results = frappe.db.sql("""
    SELECT name, subject
    FROM `tabTask`
    WHERE status = %(status)s
    AND owner = %(owner)s
""", {
    'status': 'Open',
    'owner': frappe.session.user
}, as_dict=True)

# JOIN voorbeeld
results = frappe.db.sql("""
    SELECT 
        si.name,
        si.grand_total,
        c.customer_name
    FROM `tabSales Invoice` si
    LEFT JOIN `tabCustomer` c ON si.customer = c.name
    WHERE si.docstatus = 1
    AND si.posting_date >= %(from_date)s
""", {'from_date': '2024-01-01'}, as_dict=True)
```

**⚠️ KRITIEK - SQL INJECTION PREVENTIE**:
```python
# ❌ NOOIT - SQL Injection kwetsbaar!
status = "Open'; DROP TABLE tabTask; --"
frappe.db.sql(f"SELECT * FROM `tabTask` WHERE status = '{status}'")

# ✅ ALTIJD - Parameterized queries
frappe.db.sql("SELECT * FROM `tabTask` WHERE status = %(status)s", 
    {'status': status})
```

### 4.1 frappe.db.multisql

Voor database-specifieke queries.

```python
results = frappe.db.multisql({
    'mariadb': "SELECT DATE_FORMAT(creation, '%Y-%m') as month FROM `tabTask`",
    'postgres': "SELECT TO_CHAR(creation, 'YYYY-MM') as month FROM \"tabTask\""
})
```

---

## 5. Query Builder (frappe.qb)

Moderne, type-safe query builder gebaseerd op PyPika.

```python
# Basis select
Task = frappe.qb.DocType('Task')
query = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject, Task.status)
    .where(Task.status == 'Open')
)
results = query.run(as_dict=True)

# Met JOIN
SalesInvoice = frappe.qb.DocType('Sales Invoice')
Customer = frappe.qb.DocType('Customer')

query = (
    frappe.qb.from_(SalesInvoice)
    .inner_join(Customer)
    .on(SalesInvoice.customer == Customer.name)
    .select(
        SalesInvoice.name,
        SalesInvoice.grand_total,
        Customer.customer_name
    )
    .where(SalesInvoice.docstatus == 1)
)
results = query.run(as_dict=True)

# Aggregate functies
from frappe.query_builder.functions import Count, Sum, Avg

query = (
    frappe.qb.from_(Task)
    .select(
        Task.status,
        Count(Task.name).as_('count'),
        Sum(Task.expected_time).as_('total_time')
    )
    .groupby(Task.status)
)

# Parameterisatie check
query = frappe.qb.from_(Task).select('*').where(Task.name == 'test')
sql, params = query.walk()
# sql: 'SELECT * FROM `tabTask` WHERE `name`=%(param1)s'
# params: {'param1': 'test'}
```

### 5.1 v16 Breaking Changes

In v16 is de fields syntax gewijzigd voor aggregaties:

```python
# v14/v15
frappe.db.get_list('Task',
    fields=['count(name) as count', 'status'],
    group_by='status'
)

# v16+
frappe.db.get_list('Task',
    fields=[{'COUNT': 'name', 'as': 'count'}, 'status'],
    group_by='status'
)
```

---

## 6. Transactie Management

### 6.1 Automatische Transacties

Frappe beheert transacties automatisch:

| Context | Commit | Rollback |
|---------|--------|----------|
| POST/PUT request | Na succesvolle afhandeling | Bij uncaught exception |
| Background job | Na succesvolle afhandeling | Bij uncaught exception |
| Patch | Na execute() | Bij uncaught exception |
| GET request | Geen automatische commit | - |

### 6.2 Handmatige Transactie Control

```python
# Commit
frappe.db.commit()

# Rollback
frappe.db.rollback()

# Savepoint
frappe.db.savepoint('my_savepoint')
# ... operaties ...
frappe.db.rollback(save_point='my_savepoint')  # Partial rollback
```

### 6.3 Transaction Hooks (v15+)

```python
def my_function():
    # Doe database operaties
    doc.save()
    
    # Registreer cleanup voor rollback
    frappe.db.after_rollback.add(cleanup_files)
    
    # Registreer actie na commit
    frappe.db.after_commit.add(send_notification)

def cleanup_files():
    # Wordt aangeroepen als transactie wordt teruggedraaid
    pass

def send_notification():
    # Wordt aangeroepen na succesvolle commit
    pass
```

**Beschikbare hooks**:
- `frappe.db.before_commit.add(func)`
- `frappe.db.after_commit.add(func)`
- `frappe.db.before_rollback.add(func)`
- `frappe.db.after_rollback.add(func)`

---

## 7. Caching

### 7.1 Redis Cache Basis

```python
# Set/Get
frappe.cache.set_value('my_key', {'data': 'value'})
result = frappe.cache.get_value('my_key')

# Met expiry
frappe.cache.set_value('my_key', 'value', expires_in_sec=3600)  # 1 uur

# Delete
frappe.cache.delete_value('my_key')
```

### 7.2 Hash Operations

```python
# Set hash fields
frappe.cache.hset('user|admin', 'name', 'Admin')
frappe.cache.hset('user|admin', 'email', 'admin@example.com')

# Get single field
name = frappe.cache.hget('user|admin', 'name')

# Get all fields
user_data = frappe.cache.hgetall('user|admin')
# {'name': 'Admin', 'email': 'admin@example.com'}

# Delete hash field
frappe.cache.hdel('user|admin', 'email')
```

### 7.3 Cached Document Access

```python
# Cached document
doc = frappe.get_cached_doc('Company', 'My Company')

# Cached value
country = frappe.get_cached_value('Company', 'My Company', 'country')
```

### 7.4 @redis_cache Decorator

```python
from frappe.utils.caching import redis_cache

@redis_cache
def expensive_calculation(param1, param2):
    # Tijdrovende berekening
    return result

# Met TTL
@redis_cache(ttl=300)  # 5 minuten
def get_dashboard_data(user):
    return calculate_dashboard(user)

# Cache invalideren
expensive_calculation.clear_cache()
```

### 7.5 Client-side Cache

Frappe implementeert automatisch client-side caching in `frappe.local.cache` om herhaalde Redis calls binnen één request te voorkomen.

---

## 8. Performance Best Practices

### 8.1 N+1 Query Problem Vermijden

```python
# ❌ FOUT - N+1 queries
for item in items:
    customer = frappe.get_doc('Customer', item.customer)
    print(customer.customer_name)

# ✅ CORRECT - Batch fetch
customer_names = [i.customer for i in items]
customers = {c.name: c for c in frappe.get_all(
    'Customer', 
    filters={'name': ['in', customer_names]}, 
    fields=['name', 'customer_name']
)}
for item in items:
    print(customers[item.customer].customer_name)
```

### 8.2 Field Selection

```python
# ❌ FOUT - Alle velden ophalen
docs = frappe.get_all('Sales Invoice', fields=['*'])

# ✅ CORRECT - Alleen benodigde velden
docs = frappe.get_all('Sales Invoice', 
    fields=['name', 'customer', 'grand_total'])
```

### 8.3 Paginering

```python
# ✅ Altijd pagineren voor grote datasets
page = 0
page_size = 100
while True:
    batch = frappe.get_all('Sales Invoice',
        filters={'docstatus': 1},
        fields=['name', 'grand_total'],
        start=page * page_size,
        page_length=page_size
    )
    if not batch:
        break
    process_batch(batch)
    page += 1
```

### 8.4 Indexen

```python
# Index toevoegen voor vaak gefilterde velden
frappe.db.add_index('Sales Invoice', ['customer', 'posting_date'])

# Unique constraint
frappe.db.add_unique('My DocType', ['field1', 'field2'])
```

### 8.5 Bulk Updates

```python
# v15+ bulk_update
frappe.db.bulk_update('Task', {
    'TASK-0001': {'status': 'Closed'},
    'TASK-0002': {'status': 'Closed'},
    'TASK-0003': {'status': 'Closed'}
}, chunk_size=100)
```

---

## 9. Anti-Patterns

### 9.1 Commit in Controller Hooks

```python
# ❌ NOOIT - Framework handelt commits af
def validate(self):
    frappe.db.commit()  # FOUT!

# ✅ Laat framework het doen
def validate(self):
    # Validatie logica, geen commit
    pass
```

### 9.2 String Formatting in SQL

```python
# ❌ SQL Injection risico
frappe.db.sql(f"SELECT * FROM `tabUser` WHERE name = '{user_input}'")

# ✅ Parameterized
frappe.db.sql("SELECT * FROM `tabUser` WHERE name = %(name)s", 
    {'name': user_input})
```

### 9.3 get_doc in Loops

```python
# ❌ Performance killer
for name in names:
    doc = frappe.get_doc('Customer', name)

# ✅ Batch met get_all
docs = frappe.get_all('Customer', 
    filters={'name': ['in', names]}, 
    fields=['*'])
```

### 9.4 Ignore Flags Misbruik

```python
# ❌ Te breed
doc.insert(ignore_permissions=True, ignore_mandatory=True, ignore_links=True)

# ✅ Alleen wat nodig is
doc.flags.ignore_permissions = True
doc.insert()
```

---

## 10. Decision Tree: Welke Method Gebruiken?

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
├─ Enkele veldwaarde(s)?
│  ├─ Regular DocType → frappe.db.get_value()
│  └─ Single DocType → frappe.db.get_single_value()
│
├─ Direct update zonder triggers?
│  ├─ Op document object → doc.db_set()
│  └─ Via doctype/name → frappe.db.set_value()
│
├─ Complexe query met JOINs?
│  ├─ Type-safe nodig? → frappe.qb (Query Builder)
│  └─ Anders → frappe.db.sql() met parameters
│
└─ Bulk operaties?
   ├─ Bulk update → frappe.db.bulk_update() (v15+)
   └─ Bulk delete → frappe.db.delete() met filters
```

---

## 11. Versie Verschillen (v14 vs v15 vs v16)

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| Transaction hooks | ❌ | ✅ | ✅ |
| bulk_update | ❌ | ✅ | ✅ |
| get_list run=False | Returns SQL | Returns SQL | Returns QB object |
| Aggregate fields syntax | String | String | Dict format |

---

## 12. Bronnen

- [Frappe Database API](https://docs.frappe.io/framework/user/en/api/database)
- [Frappe Document API](https://docs.frappe.io/framework/user/en/api/document)
- [Frappe Query Builder](https://docs.frappe.io/framework/user/en/api/query-builder)
- [Frappe Caching Guide](https://docs.frappe.io/framework/user/en/guides/caching)
- [v16 Migration Guide](https://github.com/frappe/frappe/wiki/query-builder-migration)

---

## 13. Checklist voor Skill

- [x] Document API methods
- [x] Database API methods  
- [x] Filter operators
- [x] Query Builder
- [x] Raw SQL met parameters
- [x] Transaction management
- [x] Caching patterns
- [x] Performance best practices
- [x] Anti-patterns
- [x] Decision tree
- [x] Versie verschillen

**Regels**: ~680 (binnen 700 limiet)
