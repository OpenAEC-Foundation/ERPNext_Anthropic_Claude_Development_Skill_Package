# Query Patterns Reference

## Filter Operators

### Basis Vergelijkingen
```python
# Gelijkheid
{'status': 'Open'}

# Niet gelijk
{'status': ['!=', 'Cancelled']}

# Groter/kleiner
{'amount': ['>', 1000]}
{'amount': ['>=', 1000]}
{'amount': ['<', 5000]}
{'amount': ['<=', 5000]}
```

### Lijst Operators
```python
# IN
{'status': ['in', ['Open', 'Working', 'Pending']]}

# NOT IN
{'status': ['not in', ['Cancelled', 'Closed']]}
```

### Pattern Matching
```python
# LIKE
{'subject': ['like', '%urgent%']}
{'email': ['like', '%@example.com']}
```

### Bereik
```python
# BETWEEN
{'date': ['between', ['2024-01-01', '2024-12-31']]}
```

### NULL Checks
```python
# IS NOT NULL
{'description': ['is', 'set']}

# IS NULL
{'description': ['is', 'not set']}
```

### Gecombineerde Filters
```python
# AND (dict)
filters = {
    'status': 'Open',
    'priority': 'High'
}

# AND (list)
filters = [
    ['status', '=', 'Open'],
    ['priority', '=', 'High']
]

# OR filters
or_filters = {
    'priority': 'High',
    'status': 'Urgent'
}
```

---

## Query Builder (frappe.qb)

### Basis Select
```python
Task = frappe.qb.DocType('Task')

query = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject, Task.status)
    .where(Task.status == 'Open')
)
results = query.run(as_dict=True)
```

### Met Filters
```python
query = (
    frappe.qb.from_(Task)
    .select('*')
    .where(Task.status == 'Open')
    .where(Task.priority == 'High')
)
```

### JOIN
```python
SI = frappe.qb.DocType('Sales Invoice')
Customer = frappe.qb.DocType('Customer')

query = (
    frappe.qb.from_(SI)
    .inner_join(Customer)
    .on(SI.customer == Customer.name)
    .select(
        SI.name,
        SI.grand_total,
        Customer.customer_name
    )
    .where(SI.docstatus == 1)
)
```

### LEFT JOIN
```python
query = (
    frappe.qb.from_(SI)
    .left_join(Customer)
    .on(SI.customer == Customer.name)
    .select(SI.name, Customer.customer_name)
)
```

### Aggregate Functies
```python
from frappe.query_builder.functions import Count, Sum, Avg, Max, Min

query = (
    frappe.qb.from_(Task)
    .select(
        Task.status,
        Count(Task.name).as_('count'),
        Sum(Task.expected_time).as_('total_time'),
        Avg(Task.expected_time).as_('avg_time')
    )
    .groupby(Task.status)
)
```

### Order en Limit
```python
query = (
    frappe.qb.from_(Task)
    .select('*')
    .orderby(Task.creation, order='desc')
    .limit(10)
    .offset(20)
)
```

### Subquery
```python
subquery = (
    frappe.qb.from_(Task)
    .select(Task.assigned_to)
    .where(Task.status == 'Open')
)

query = (
    frappe.qb.from_(User)
    .select('*')
    .where(User.name.isin(subquery))
)
```

---

## Raw SQL met Parameters

### Basis
```python
results = frappe.db.sql("""
    SELECT name, subject
    FROM `tabTask`
    WHERE status = %(status)s
    AND owner = %(owner)s
""", {
    'status': 'Open',
    'owner': frappe.session.user
}, as_dict=True)
```

### JOIN
```python
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

### Aggregate
```python
results = frappe.db.sql("""
    SELECT 
        status,
        COUNT(*) as count,
        SUM(expected_time) as total_time
    FROM `tabTask`
    GROUP BY status
""", as_dict=True)
```

### Return Types
```python
# Tuple of tuples (default)
results = frappe.db.sql("SELECT name FROM `tabTask`")
# (('TASK001',), ('TASK002',))

# List of dicts
results = frappe.db.sql("SELECT name FROM `tabTask`", as_dict=True)
# [{'name': 'TASK001'}, {'name': 'TASK002'}]

# List of lists
results = frappe.db.sql("SELECT name FROM `tabTask`", as_list=True)
# [['TASK001'], ['TASK002']]
```

---

## v16 Syntax Wijzigingen

### Aggregate Fields
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

### run=False
```python
# v14/v15 - returns SQL string
query = frappe.db.get_list('Task', run=False)

# v16 - returns Query Builder object
query = frappe.db.get_list('Task', run=False)
sql = query.get_sql()  # Voor SQL string
```
