# Query Patterns Reference

> Query Builder (frappe.qb), filter operators, raw SQL patterns. Verified against Frappe v14-v16 docs.

> **Note**: For comprehensive Query Builder coverage (advanced joins, HAVING, window functions, subquery patterns, cross-DB compatibility), see the dedicated **[frappe-syntax-query-builder](../../../syntax/frappe-syntax-query-builder/SKILL.md)** skill.

---

## Filter Operators

### Comparison
```python
{'status': 'Open'}                    # = (equality)
{'status': ['!=', 'Cancelled']}       # !=
{'amount': ['>', 1000]}               # >
{'amount': ['>=', 1000]}              # >=
{'amount': ['<', 5000]}               # <
{'amount': ['<=', 5000]}              # <=
```

### List Operators
```python
{'status': ['in', ['Open', 'Working', 'Pending']]}       # IN
{'status': ['not in', ['Cancelled', 'Closed']]}           # NOT IN
```

### Pattern Matching
```python
{'subject': ['like', '%urgent%']}       # LIKE
{'email': ['like', '%@example.com']}    # LIKE
```

### Range
```python
{'date': ['between', ['2024-01-01', '2024-12-31']]}  # BETWEEN
```

### NULL Checks
```python
{'description': ['is', 'set']}         # IS NOT NULL
{'description': ['is', 'not set']}     # IS NULL
```

### Combining Filters
```python
# AND — dict (all conditions ANDed)
filters = {'status': 'Open', 'priority': 'High'}

# AND — list format (allows duplicate field names)
filters = [
    ['status', '=', 'Open'],
    ['priority', '=', 'High']
]

# OR — separate parameter
or_filters = {'priority': 'Urgent', 'status': 'Overdue'}

# Combined AND + OR
frappe.get_all('Task',
    filters={'docstatus': 0},
    or_filters={'priority': 'Urgent', 'exp_end_date': ['<', today()]}
)
```

---

## Query Builder (frappe.qb)

The Query Builder wraps PyPika and generates parameterized SQL automatically. ALWAYS prefer over raw SQL.

### Basic Select
```python
Task = frappe.qb.DocType('Task')

results = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject, Task.status)
    .where(Task.status == 'Open')
).run(as_dict=True)
```

### DocType vs Table
```python
# DocType — adds `tab` prefix automatically
Task = frappe.qb.DocType('Task')        # → `tabTask`

# Table — NO prefix (for internal tables)
Auth = frappe.qb.Table('__Auth')        # → `__Auth`

# Field — standalone column reference
field = frappe.qb.Field('name')
```

### WHERE Conditions
```python
Task = frappe.qb.DocType('Task')

# AND — chain .where()
query = (
    frappe.qb.from_(Task)
    .select('*')
    .where(Task.status == 'Open')
    .where(Task.priority == 'High')
)

# OR — use pipe operator
query = (
    frappe.qb.from_(Task)
    .select('*')
    .where(
        (Task.status == 'Open') | (Task.status == 'Working')
    )
)

# Combined AND + OR
query = (
    frappe.qb.from_(Task)
    .select('*')
    .where(
        (Task.priority == 'High') | (Task.priority == 'Urgent')
    )
    .where(Task.docstatus == 0)  # AND
)

# LIKE
query.where(Task.subject.like('%urgent%'))

# IN
query.where(Task.status.isin(['Open', 'Working']))

# IS NULL / IS NOT NULL
query.where(Task.description.isnull())
query.where(Task.description.isnotnull())

# BETWEEN
query.where(Task.creation.between('2024-01-01', '2024-12-31'))
```

### INNER JOIN
```python
SI = frappe.qb.DocType('Sales Invoice')
Customer = frappe.qb.DocType('Customer')

results = (
    frappe.qb.from_(SI)
    .inner_join(Customer).on(SI.customer == Customer.name)
    .select(SI.name, SI.grand_total, Customer.customer_name)
    .where(SI.docstatus == 1)
).run(as_dict=True)
```

### LEFT JOIN
```python
results = (
    frappe.qb.from_(SI)
    .left_join(Customer).on(SI.customer == Customer.name)
    .select(SI.name, Customer.customer_name)
).run(as_dict=True)
```

### Aggregate Functions
```python
from frappe.query_builder.functions import Count, Sum, Avg, Max, Min

Task = frappe.qb.DocType('Task')

stats = (
    frappe.qb.from_(Task)
    .select(
        Task.status,
        Count(Task.name).as_('count'),
        Sum(Task.expected_time).as_('total_time'),
        Avg(Task.expected_time).as_('avg_time'),
        Max(Task.expected_time).as_('max_time'),
        Min(Task.expected_time).as_('min_time')
    )
    .groupby(Task.status)
).run(as_dict=True)
```

### Order, Limit, Offset
```python
results = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject)
    .orderby(Task.creation, order='desc')
    .limit(10)
    .offset(20)
).run(as_dict=True)
```

### Subquery
```python
User = frappe.qb.DocType('User')
Task = frappe.qb.DocType('Task')

subquery = (
    frappe.qb.from_(Task)
    .select(Task.assigned_to)
    .where(Task.status == 'Open')
)

results = (
    frappe.qb.from_(User)
    .select(User.name, User.full_name)
    .where(User.name.isin(subquery))
).run(as_dict=True)
```

### Inspect Generated SQL
```python
query = frappe.qb.from_(Task).select('*').where(Task.name == 'X')

# Parameterized form
sql, params = query.walk()
# ('SELECT * FROM `tabTask` WHERE `name`=%(param1)s', {'param1': 'X'})

# SQL string
sql_str = query.get_sql()
# Also: str(query)
```

### run() Options
```python
query.run()                    # Tuple of tuples (default)
query.run(as_dict=True)        # List of dicts
query.run(as_list=True)        # List of lists
query.run(debug=True)          # Print SQL to console
```

---

## Cross-Database Compatibility

### ImportMapper
Maps functions to correct database dialect automatically.
```python
from frappe.query_builder.utils import ImportMapper, db_type_is
from frappe.query_builder.custom import GROUP_CONCAT, STRING_AGG

GroupConcat = ImportMapper({
    db_type_is.MARIADB: GROUP_CONCAT,
    db_type_is.POSTGRES: STRING_AGG
})

# Use GroupConcat in queries — resolves to correct function per DB
```

### ConstantColumn
Adds a constant value as a pseudo-column.
```python
from frappe.query_builder.custom import ConstantColumn

results = (
    frappe.qb.from_('DocType')
    .select('name', ConstantColumn('admin').as_('created_by'))
).run(as_dict=True)
```

### Custom Functions
Extend PyPika for database-specific functions.
```python
from pypika import CustomFunction

DateDiff = CustomFunction('DATEDIFF', ['date1', 'date2'])

Task = frappe.qb.DocType('Task')
results = (
    frappe.qb.from_(Task)
    .select(Task.name, DateDiff(Task.exp_end_date, Task.exp_start_date).as_('duration'))
).run(as_dict=True)
```

### multisql for Raw SQL
When you MUST write database-specific raw SQL:
```python
results = frappe.db.multisql({
    'mariadb': """
        SELECT name, IFNULL(description, '') as description
        FROM `tabTask` WHERE status = %(status)s
    """,
    'postgres': """
        SELECT name, COALESCE(description, '') as description
        FROM "tabTask" WHERE status = %(status)s
    """
}, {'status': 'Open'}, as_dict=True)
```

---

## Raw SQL Patterns

### ALWAYS Use Parameterized Queries
```python
# ✅ CORRECT
results = frappe.db.sql("""
    SELECT name, subject FROM `tabTask`
    WHERE status = %(status)s AND owner = %(owner)s
""", {'status': 'Open', 'owner': frappe.session.user}, as_dict=True)

# ❌ NEVER — SQL injection vulnerability
frappe.db.sql(f"SELECT * FROM `tabTask` WHERE status = '{status}'")
```

### JOIN Pattern
```python
results = frappe.db.sql("""
    SELECT si.name, si.grand_total, c.customer_name
    FROM `tabSales Invoice` si
    INNER JOIN `tabCustomer` c ON si.customer = c.name
    WHERE si.docstatus = 1
    AND si.posting_date >= %(from_date)s
    ORDER BY si.grand_total DESC
    LIMIT %(limit)s
""", {'from_date': '2024-01-01', 'limit': 100}, as_dict=True)
```

### Aggregate Pattern
```python
results = frappe.db.sql("""
    SELECT status, COUNT(*) as count, SUM(expected_time) as total_time
    FROM `tabTask`
    GROUP BY status
    ORDER BY count DESC
""", as_dict=True)
```

### Table Name Rules
- ALWAYS use backtick-quoted `tab` prefix: `` `tabSales Invoice` ``
- Exact DocType name including spaces: `` `tabPayment Entry` ``
- Child tables: `` `tabSales Invoice Item` ``

---

## v16 Breaking Changes

### Aggregate Fields in get_list/get_all
```python
# v14/v15 — string-based aggregates
frappe.db.get_list('Task',
    fields=['count(name) as count', 'status'],
    group_by='status'
)

# v16 — dict-based aggregates
frappe.db.get_list('Task',
    fields=[{'COUNT': 'name', 'as': 'count'}, 'status'],
    group_by='status'
)
```

### run=False Behavior
```python
# v14/v15 — returns SQL string
sql = frappe.db.get_list('Task', run=False)

# v16 — returns Query Builder object
qb_obj = frappe.db.get_list('Task', run=False)
sql = qb_obj.get_sql()   # Get SQL string
qb_obj.run()              # Execute
```
