# Research Document: Frappe Database API

> **Fase**: 3.1  
> **Datum**: 2026-01-17  
> **Doel**: Uitgebreide documentatie van Frappe Database API voor erpnext-database skill  
> **Bronnen**: Officiële Frappe Framework documentatie (frappeframework.com)

---

## 1. Overzicht Database Architectuur

### 1.1 Ondersteunde Databases
- **MariaDB/MySQL**: Standaard database, meest gebruikt
- **PostgreSQL**: Ondersteund sinds v13

### 1.2 Database Tabellen Conventie
- Alle DocType tabellen krijgen prefix `tab`: `tabSales Order`, `tabCustomer`
- Interne tabellen gebruiken prefix `__`: `__Auth`, `__global_search`
- Single DocTypes slaan data op in `tabSingles` tabel

### 1.3 Standaard Velden (Alle DocTypes)
Elk DocType krijgt automatisch deze velden:

| Veld | Type | Beschrijving |
|------|------|--------------|
| `name` | varchar(140) | Primary key, unieke identifier |
| `creation` | datetime(6) | Timestamp aanmaak |
| `modified` | datetime(6) | Timestamp laatste wijziging |
| `modified_by` | varchar(140) | User die laatst wijzigde |
| `owner` | varchar(140) | User die document aanmaakte |
| `docstatus` | int(1) | 0=Draft, 1=Submitted, 2=Cancelled |
| `parent` | varchar(140) | Parent document name (child tables) |
| `parentfield` | varchar(140) | Field in parent linking to child |
| `parenttype` | varchar(140) | DocType van parent |
| `idx` | int(8) | Volgorde index (child tables) |

---

## 2. Document API (ORM Layer)

### 2.1 frappe.get_doc()

Haalt een bestaand document op of maakt een nieuw document object.

```python
# Bestaand document ophalen
doc = frappe.get_doc('Customer', 'CUST-00001')

# Nieuw document maken (nog niet in database)
doc = frappe.get_doc({
    'doctype': 'Customer',
    'customer_name': 'Test Company',
    'customer_type': 'Company'
})

# Single DocType (geen name nodig)
settings = frappe.get_doc('System Settings')
```

**Parameters:**
- `doctype` (str): DocType naam
- `name` (str): Document name (primary key)

**Returns:** Document object met alle velden als attributen

### 2.2 frappe.new_doc()

Alternatieve manier om nieuw document te maken.

```python
doc = frappe.new_doc('Task')
doc.subject = 'New Task'
doc.insert()
```

### 2.3 frappe.get_last_doc()

Haalt het laatst gewijzigde document op.

```python
last_user = frappe.get_last_doc('User')
```

### 2.4 frappe.get_cached_doc()

Zoekt eerst in cache voordat database wordt geraadpleegd.

```python
# Efficiënter voor vaak opgevraagde documenten
doc = frappe.get_cached_doc('Company', 'My Company')
```

### 2.5 Document Methods

#### doc.insert()
```python
doc = frappe.get_doc({
    'doctype': 'Task',
    'subject': 'New Task'
})
doc.insert()  # Slaat op in database, triggert controller events

# Met opties
doc.insert(
    ignore_permissions=True,    # Skip permission check
    ignore_if_duplicate=True,   # Geen error bij duplicate
    ignore_mandatory=True       # Skip mandatory veld check
)
```

#### doc.save()
```python
doc = frappe.get_doc('Task', 'TASK-0001')
doc.subject = 'Updated Subject'
doc.save()  # Triggert validate, on_update events

# Met opties
doc.save(ignore_permissions=True)
```

#### doc.delete()
```python
doc = frappe.get_doc('Task', 'TASK-0001')
doc.delete()  # Verwijdert document en children
```

#### doc.submit()
```python
# Alleen voor Submittable DocTypes
doc.submit()  # Zet docstatus naar 1
```

#### doc.cancel()
```python
# Alleen voor Submitted documents
doc.cancel()  # Zet docstatus naar 2
```

#### doc.reload()
```python
# Herlaad document van database
doc.reload()
```

#### doc.db_set()
```python
# Direct database update, GEEN controller triggers
doc.db_set('status', 'Closed')

# Met opties
doc.db_set('status', 'Closed', notify=True)           # Trigger realtime update
doc.db_set('status', 'Closed', commit=True)           # Direct commit
doc.db_set('status', 'Closed', update_modified=False) # Behoud modified timestamp
```

**⚠️ WAARSCHUWING**: `db_set()` bypassed alle validaties en controller methods!

#### doc.db_update()
```python
# Update alle dirty velden direct in database
doc.last_active = frappe.utils.now()
doc.db_update()
```

#### doc.append()
```python
# Child table rij toevoegen
doc.append('items', {
    'item_code': 'ITEM-001',
    'qty': 10,
    'rate': 100
})
doc.save()
```

#### doc.get_doc_before_save()
```python
# In controller: vergelijk met vorige waarden
def on_update(self):
    previous = self.get_doc_before_save()
    if previous and previous.status != self.status:
        # Status is gewijzigd
        pass
```

---

## 3. Database API (frappe.db)

### 3.1 Read Operations

#### frappe.db.get_list()
```python
# Basis query met permissions
tasks = frappe.db.get_list('Task',
    filters={'status': 'Open'},
    fields=['name', 'subject', 'priority'],
    order_by='creation desc',
    start=0,
    page_length=20
)
# Returns: [{'name': 'TASK-001', 'subject': '...', 'priority': '...'}]

# Met pluck voor enkele kolom
names = frappe.db.get_list('Task', pluck='name')
# Returns: ['TASK-001', 'TASK-002', ...]

# Als tuple list
tasks = frappe.db.get_list('Task',
    fields=['subject', 'date'],
    as_list=True
)
# Returns: [('Subject 1', '2024-01-01'), ...]
```

**Parameters:**
| Parameter | Type | Beschrijving |
|-----------|------|--------------|
| `doctype` | str | DocType naam |
| `filters` | dict/list | Filter condities |
| `or_filters` | dict/list | OR filter condities |
| `fields` | list | Velden om op te halen |
| `order_by` | str | Sortering (bijv. 'creation desc') |
| `group_by` | str | GROUP BY clause |
| `start` | int | Offset voor paginering |
| `page_length` | int | Aantal resultaten |
| `pluck` | str | Retourneer alleen deze kolom |
| `as_list` | bool | Return als tuple list |
| `ignore_ifnull` | bool | Negeer NULL waarden |
| `debug` | bool | Print SQL query |

#### frappe.db.get_all()
```python
# Zelfde als get_list maar ZONDER permission filtering
all_tasks = frappe.db.get_all('Task',
    filters={'status': 'Open'},
    fields=['name', 'subject']
)
```

**⚠️ Let op**: `get_list` past user permissions toe, `get_all` niet!

#### frappe.db.get_value()
```python
# Enkele waarde
subject = frappe.db.get_value('Task', 'TASK-001', 'subject')

# Meerdere waarden
subject, status = frappe.db.get_value('Task', 'TASK-001', ['subject', 'status'])

# Als dict
task = frappe.db.get_value('Task', 'TASK-001', ['subject', 'status'], as_dict=True)
# Returns: {'subject': '...', 'status': '...'}

# Met filters
subject = frappe.db.get_value('Task', {'status': 'Open'}, 'subject')
```

#### frappe.db.get_single_value()
```python
# Voor Single DocTypes
timezone = frappe.db.get_single_value('System Settings', 'time_zone')
loan_period = frappe.db.get_single_value('Library Settings', 'loan_period')
```

#### frappe.db.exists()
```python
# Check of document bestaat
if frappe.db.exists('Customer', 'CUST-001'):
    print('Customer exists')

# Met filters
if frappe.db.exists('Task', {'status': 'Open', 'assigned_to': 'john@example.com'}):
    print('Open task found')

# Retourneert name als gevonden, anders None
name = frappe.db.exists('Task', {'subject': 'Test'})
```

#### frappe.db.count()
```python
# Tel records
total = frappe.db.count('Task')

# Met filters
open_tasks = frappe.db.count('Task', {'status': 'Open'})
```

### 3.2 Filter Operators

```python
# Basis filters (dict - impliciet AND)
filters = {
    'status': 'Open',           # =
    'priority': ['!=', 'Low'],  # !=
    'date': ['>', '2024-01-01'] # >
}

# Ondersteunde operators:
# =, !=, <, >, <=, >=
# like, not like
# in, not in
# is, is not (voor NULL)
# between

# Voorbeelden
filters = {
    'subject': ['like', '%test%'],           # LIKE
    'status': ['in', ['Open', 'Working']],   # IN
    'date': ['between', ['2024-01-01', '2024-12-31']],  # BETWEEN
    'assigned_to': ['is', 'set'],            # IS NOT NULL
    'description': ['is', 'not set']         # IS NULL
}

# List syntax voor complexe queries
filters = [
    ['Task', 'status', '=', 'Open'],
    ['Task', 'priority', 'in', ['High', 'Urgent']]
]

# OR filters
or_filters = {
    'status': 'Open',
    'priority': 'High'
}
# WHERE status = 'Open' OR priority = 'High'
```

### 3.3 Write Operations

#### frappe.db.set_value()
```python
# Enkele waarde
frappe.db.set_value('Task', 'TASK-001', 'status', 'Closed')

# Meerdere waarden
frappe.db.set_value('Task', 'TASK-001', {
    'status': 'Closed',
    'priority': 'Low'
})

# Met filters (bulk update)
frappe.db.set_value('Task', {'status': 'Open'}, 'priority', 'Medium')

# Opties
frappe.db.set_value('Task', 'TASK-001', 'status', 'Closed',
    update_modified=False  # Behoud modified timestamp
)
```

**⚠️ WAARSCHUWING**: `db.set_value()` bypassed controller validaties!

#### frappe.db.delete()
```python
# Verwijder met filters
frappe.db.delete('Error Log', {
    'modified': ['<', '2024-01-01']
})

# Verwijder alle records
frappe.db.delete('Error Log')

# Verwijder specifiek document
frappe.db.delete('Task', 'TASK-001')
```

#### frappe.db.truncate()
```python
# Leegt hele tabel (TRUNCATE TABLE)
frappe.db.truncate('Error Log')
```

**⚠️ WAARSCHUWING**: Kan niet worden teruggedraaid! Triggert automatisch commit.

### 3.4 Raw SQL

#### frappe.db.sql()
```python
# Basis query
result = frappe.db.sql("""
    SELECT name, subject, status
    FROM `tabTask`
    WHERE status = 'Open'
""")
# Returns: [('TASK-001', 'Subject', 'Open'), ...]

# Als dict
result = frappe.db.sql("""
    SELECT name, subject, status
    FROM `tabTask`
    WHERE status = 'Open'
""", as_dict=True)
# Returns: [{'name': 'TASK-001', 'subject': '...', 'status': 'Open'}]

# Met parameters (ALTIJD gebruiken voor security!)
result = frappe.db.sql("""
    SELECT name, subject
    FROM `tabTask`
    WHERE status = %(status)s
    AND company = %(company)s
""", {
    'status': 'Open',
    'company': 'My Company'
}, as_dict=True)

# Met JOIN
result = frappe.db.sql("""
    SELECT gl.name, gl.debit, gl.credit, acc.account_number
    FROM `tabGL Entry` gl
    LEFT JOIN `tabAccount` acc ON gl.account = acc.name
    WHERE gl.company = %(company)s
""", {'company': 'My Company'}, as_dict=True)
```

**⚠️ BELANGRIJK**: 
- ALTIJD parameterized queries gebruiken (nooit string concatenation)
- `frappe.db.sql()` bypassed alle validaties en permissions

#### frappe.db.multisql()
```python
# Database-specifieke queries
result = frappe.db.multisql({
    'mariadb': "SELECT IFNULL(field, 0) FROM table",
    'postgres': "SELECT COALESCE(field, 0) FROM table"
})
```

---

## 4. Query Builder (frappe.qb)

Moderne, Pythonic manier om queries te bouwen. Gebaseerd op PyPika.

### 4.1 Basis Gebruik

```python
# DocType referentie maken
Task = frappe.qb.DocType('Task')

# SELECT query
query = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject, Task.status)
    .where(Task.status == 'Open')
    .orderby(Task.creation, order=frappe.qb.desc)
    .limit(10)
)
result = query.run(as_dict=True)

# Of direct uitvoeren
result = (
    frappe.qb.from_('Task')
    .select('name', 'subject')
    .where(Task.status == 'Open')
    .run(as_dict=True)
)
```

### 4.2 WHERE Condities

```python
Task = frappe.qb.DocType('Task')

# Vergelijkingen
query = frappe.qb.from_(Task).select('*').where(
    (Task.status == 'Open') &
    (Task.priority != 'Low') &
    (Task.date > '2024-01-01')
)

# OR condities
query = frappe.qb.from_(Task).select('*').where(
    (Task.status == 'Open') | (Task.priority == 'High')
)

# IN clause
query = frappe.qb.from_(Task).select('*').where(
    Task.status.isin(['Open', 'Working'])
)

# LIKE
query = frappe.qb.from_(Task).select('*').where(
    Task.subject.like('%urgent%')
)

# IS NULL / IS NOT NULL
query = frappe.qb.from_(Task).select('*').where(
    Task.assigned_to.isnotnull()
)
```

### 4.3 JOINs

```python
Task = frappe.qb.DocType('Task')
User = frappe.qb.DocType('User')

# INNER JOIN
query = (
    frappe.qb.from_(Task)
    .inner_join(User)
    .on(Task.assigned_to == User.name)
    .select(Task.name, Task.subject, User.full_name)
)

# LEFT JOIN
query = (
    frappe.qb.from_(Task)
    .left_join(User)
    .on(Task.assigned_to == User.name)
    .select(Task.name, User.full_name)
)
```

### 4.4 Aggregatie Functies

```python
from frappe.query_builder.functions import Count, Sum, Avg

Task = frappe.qb.DocType('Task')

# COUNT
query = (
    frappe.qb.from_(Task)
    .select(Count(Task.name).as_('total'))
    .where(Task.status == 'Open')
)

# GROUP BY met COUNT
query = (
    frappe.qb.from_(Task)
    .select(Task.status, Count(Task.name).as_('count'))
    .groupby(Task.status)
)

# SUM
query = (
    frappe.qb.from_(SalesOrder)
    .select(Sum(SalesOrder.grand_total).as_('total'))
)
```

### 4.5 Subqueries

```python
Task = frappe.qb.DocType('Task')
User = frappe.qb.DocType('User')

# Subquery in WHERE
subquery = (
    frappe.qb.from_(User)
    .select(User.name)
    .where(User.enabled == 1)
)

query = (
    frappe.qb.from_(Task)
    .select(Task.name)
    .where(Task.assigned_to.isin(subquery))
)
```

### 4.6 Debug & Uitvoeren

```python
# Debug - toon gegenereerde SQL
query.run(debug=True)

# Walk - toon query met parameters
sql, params = query.walk()
# Returns: ('SELECT * FROM `tabTask` WHERE `name`=%(param1)s', {'param1': 'TASK-001'})
```

---

## 5. Transaction Management

### 5.1 Automatisch Transaction Model

Frappe beheert transacties automatisch:

| Context | Gedrag |
|---------|--------|
| Web Request (POST/PUT) | Auto-commit bij success, auto-rollback bij error |
| Background Jobs | Auto-commit na elke job |
| Patches | Auto-commit na patch |
| Unit Tests | Rollback na elke test |

### 5.2 Handmatige Transacties

```python
# Commit (zelden nodig)
frappe.db.commit()

# Rollback
frappe.db.rollback()

# Savepoint
frappe.db.savepoint('my_savepoint')
try:
    # Operaties...
except:
    frappe.db.rollback(save_point='my_savepoint')
```

### 5.3 Transaction Hooks

```python
# Callback na commit
def after_commit_action():
    # Wordt alleen uitgevoerd als transactie succesvol is
    send_notification()

frappe.db.after_commit.add(after_commit_action)

# Callback na rollback
def cleanup_files():
    # Wordt uitgevoerd bij rollback
    delete_uploaded_file()

frappe.db.after_rollback.add(cleanup_files)
```

**Use Case**: Bestandsoperaties koppelen aan database transacties:

```python
class MyDoc(Document):
    def on_update(self):
        self.write_file()
        # Cleanup als database rollback
        frappe.db.after_rollback.add(self.delete_file)
    
    def write_file(self):
        # Bestand schrijven
        pass
    
    def delete_file(self):
        # Bestand verwijderen bij rollback
        pass
```

---

## 6. Child Tables

### 6.1 Kenmerken

- Eigen tabel met prefix `tab`
- `parent`: name van parent document
- `parentfield`: veldnaam in parent
- `parenttype`: DocType van parent
- `idx`: volgorde (1-indexed)

### 6.2 Werken met Child Tables

```python
# Document met child table ophalen
doc = frappe.get_doc('Sales Order', 'SO-0001')

# Itereren over child rows
for item in doc.items:
    print(item.item_code, item.qty)

# Child row toevoegen
doc.append('items', {
    'item_code': 'ITEM-001',
    'qty': 5,
    'rate': 100
})
doc.save()

# Child row verwijderen
doc.items = [item for item in doc.items if item.item_code != 'ITEM-001']
doc.save()

# Alle child rows vervangen
doc.set('items', [
    {'item_code': 'NEW-001', 'qty': 10},
    {'item_code': 'NEW-002', 'qty': 20}
])
doc.save()
```

### 6.3 Direct Query op Child Tables

```python
# Let op: WHERE moet parent referentie bevatten
items = frappe.db.get_all('Sales Order Item',
    filters={'parent': 'SO-0001'},
    fields=['item_code', 'qty']
)

# Met parent data (join via field reference)
items = frappe.db.get_list('Note',
    fields=['name', 'seen_by.user as seen_by_user']
)
```

---

## 7. Metadata (frappe.get_meta)

```python
# DocType metadata ophalen
meta = frappe.get_meta('Task')

# Veld informatie
meta.has_field('status')  # True/False
field = meta.get_field('status')
print(field.fieldtype, field.options)

# Alle velden
for field in meta.fields:
    print(field.fieldname, field.fieldtype)

# Custom fields
custom_fields = meta.get_custom_fields()

# DocType eigenschappen
meta.is_submittable  # True als submittable
meta.is_single  # True als Single DocType
meta.istable  # True als Child DocType
```

---

## 8. Caching

### 8.1 Document Cache

```python
# Cached document (raadpleegt cache eerst)
doc = frappe.get_cached_doc('Company', 'My Company')

# Cache invalideren
frappe.clear_cache(doctype='Company')
frappe.clear_document_cache('Company', 'My Company')
```

### 8.2 Algemene Cache

```python
# Waarde cachen
frappe.cache().set('my_key', 'my_value')
frappe.cache().set('my_key', 'my_value', expires_in_sec=3600)

# Waarde ophalen
value = frappe.cache().get('my_key')

# Met default
value = frappe.cache().get('my_key', default='fallback')

# Verwijderen
frappe.cache().delete('my_key')

# Hash operaties
frappe.cache().hset('hash_key', 'field', 'value')
value = frappe.cache().hget('hash_key', 'field')
```

---

## 9. Best Practices

### 9.1 Performance

```python
# ✅ GOED: Specifieke velden ophalen
tasks = frappe.db.get_list('Task', 
    fields=['name', 'subject'],
    page_length=100
)

# ❌ FOUT: Alle velden ophalen (onnodig)
tasks = frappe.db.get_list('Task', fields=['*'])

# ✅ GOED: Bulk operaties
for name in names:
    frappe.db.set_value('Task', name, 'status', 'Closed', update_modified=False)
frappe.db.commit()

# ❌ FOUT: Individuele saves in loop (langzaam)
for name in names:
    doc = frappe.get_doc('Task', name)
    doc.status = 'Closed'
    doc.save()
```

### 9.2 Security

```python
# ✅ GOED: Parameterized queries
frappe.db.sql("""
    SELECT * FROM `tabTask` WHERE status = %(status)s
""", {'status': user_input})

# ❌ FOUT: String concatenation (SQL injection risico!)
frappe.db.sql(f"SELECT * FROM `tabTask` WHERE status = '{user_input}'")

# ✅ GOED: Permission check
if frappe.has_permission('Task', 'read', doc.name):
    # Toegestaan
    pass

# ✅ GOED: get_list (past permissions toe)
tasks = frappe.db.get_list('Task', filters={'status': 'Open'})

# ⚠️ OPGELET: get_all bypassed permissions
tasks = frappe.db.get_all('Task', filters={'status': 'Open'})
```

### 9.3 Validatie Bewustzijn

```python
# Methodes die ORM triggers uitvoeren:
doc.insert()    # ✅ before_insert, validate, on_insert
doc.save()      # ✅ validate, before_save, on_update
doc.delete()    # ✅ on_trash

# Methodes die ORM triggers BYPASSEN:
doc.db_set()           # ❌ Geen triggers
doc.db_update()        # ❌ Geen triggers  
frappe.db.set_value()  # ❌ Geen triggers
frappe.db.sql()        # ❌ Geen triggers
frappe.db.delete()     # ❌ Geen triggers
```

---

## 10. Anti-Patterns

### 10.1 N+1 Query Problem

```python
# ❌ FOUT: N+1 queries
orders = frappe.db.get_list('Sales Order', fields=['name'])
for order in orders:
    doc = frappe.get_doc('Sales Order', order.name)  # N extra queries!
    print(doc.customer)

# ✅ GOED: Alle data in één query
orders = frappe.db.get_list('Sales Order', 
    fields=['name', 'customer', 'grand_total']
)
```

### 10.2 Onnodige Document Loads

```python
# ❌ FOUT: Volledig document laden voor één veld
doc = frappe.get_doc('Customer', 'CUST-001')
print(doc.customer_name)

# ✅ GOED: Direct veld ophalen
name = frappe.db.get_value('Customer', 'CUST-001', 'customer_name')
```

### 10.3 Vergeten van Permissions

```python
# ❌ FOUT: get_all zonder permission awareness
data = frappe.db.get_all('Salary Slip')  # Toont ALLE salaris data!

# ✅ GOED: get_list respecteert permissions
data = frappe.db.get_list('Salary Slip')
```

### 10.4 Inefficiënte Loops

```python
# ❌ FOUT: Individuele exists checks
for item in items:
    if frappe.db.exists('Item', item):
        # ...

# ✅ GOED: Bulk check
existing = set(frappe.db.get_list('Item', 
    filters={'name': ['in', items]},
    pluck='name'
))
for item in items:
    if item in existing:
        # ...
```

---

## 11. Versieverschillen v14/v15

### 11.1 Query Builder (v14+)
- `frappe.qb` volledig beschikbaar vanaf v14
- v13 had beperkte Query Builder support

### 11.2 Pluck Parameter (v14+)
```python
# v14+: pluck parameter
names = frappe.db.get_list('Task', pluck='name')

# v13: handmatig
names = [d.name for d in frappe.db.get_list('Task', fields=['name'])]
```

### 11.3 Child Table Fields in get_list (v14+)
```python
# v14+: Direct child table velden opvragen
items = frappe.db.get_list('Note',
    fields=['name', 'seen_by.user as seen_by_user']
)
```

### 11.4 Type Annotations (v15+)
```python
# v15: Auto-generated type annotations in controllers
class Person(Document):
    # begin: auto-generated types
    if TYPE_CHECKING:
        from frappe.types import DF
        first_name: DF.Data
        last_name: DF.Data
    # end: auto-generated types
```

---

## 12. Checklist voor Skill Development

### Onderwerpen voor SKILL.md:
- [ ] Document API basis (get_doc, new_doc, insert, save)
- [ ] Database queries (get_list, get_all, get_value)
- [ ] Filter operators
- [ ] Query Builder basics
- [ ] Child tables manipulatie
- [ ] Transaction awareness

### Reference Files:
1. `reference-document-api.md` - Alle document methods
2. `reference-database-queries.md` - get_list, get_all, get_value, filters
3. `reference-query-builder.md` - frappe.qb API
4. `reference-transactions.md` - Commit, rollback, savepoints
5. `reference-examples.md` - Complete werkende voorbeelden
6. `reference-anti-patterns.md` - Veelgemaakte fouten

---

## 13. Bronnen

- https://frappeframework.com/docs/v14/user/en/api/database
- https://frappeframework.com/docs/v14/user/en/api/document
- https://frappeframework.com/docs/v14/user/en/api/query-builder
- https://frappeframework.com/docs/user/en/basics/doctypes/child-doctype
- https://frappeframework.com/docs/v15/user/en/basics/doctypes/controllers

---

*Research document voltooid: 2026-01-17*
*Regels: ~700*
*Status: Klaar voor skill development*
