# Migration Guide — Raw SQL to frappe.qb

## frappe.get_all / frappe.get_list Migration

### Aggregation in fields

```python
# ❌ OLD — raw SQL string in fields
frappe.get_all("Stock Ledger Entry",
    fields=["sum(actual_qty) as qty"],
    filters={"item_code": "ITEM-001"}
)

# ✅ NEW — dict syntax
frappe.get_all("Stock Ledger Entry",
    fields=[{"SUM": "actual_qty", "as": "qty"}],
    filters={"item_code": "ITEM-001"}
)

# ✅ NEW — function objects
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum
sle = DocType("Stock Ledger Entry")
frappe.get_all("Stock Ledger Entry",
    fields=[(Sum(sle.actual_qty)).as_("qty")],
    filters={"item_code": "ITEM-001"}
)
```

### IFNULL in filters

```python
# ❌ OLD — raw SQL in filter key
frappe.get_all("Item",
    filters={"ifnull(is_stock_item, 0)": 0}
)

# ✅ NEW — IfNull function
from frappe.query_builder import Field
from frappe.query_builder.functions import IfNull
frappe.get_all("Item",
    filters=[IfNull(Field("is_stock_item"), 0) == 0]
)
```

### DISTINCT

```python
# ❌ OLD
frappe.get_all("Stock Ledger Entry",
    fields=["distinct batch_no"]
)

# ✅ NEW
frappe.get_all("Stock Ledger Entry",
    fields=["batch_no"],
    distinct=True
)
```

### Literal values as fields

```python
# ❌ OLD
frappe.get_all("Leave Application",
    fields=["'Leave Application' as doctype", "name"]
)

# ✅ NEW
from pypika.terms import ValueWrapper
frappe.get_all("Leave Application",
    fields=[ValueWrapper("Leave Application").as_("doctype"), "name"]
)
```

### ORDER BY with functions

```python
# ❌ OLD
frappe.get_all("Stock Ledger Entry",
    order_by="timestamp(posting_date, posting_time), creation"
)

# ✅ NEW — full qb query
from frappe.query_builder.functions import Timestamp
sle = frappe.qb.DocType("Stock Ledger Entry")
result = (
    frappe.qb.from_(sle)
    .select(sle.star)
    .orderby(Timestamp(sle.posting_date, sle.posting_time))
    .orderby(sle.creation)
    .run(as_dict=True)
)
```

## run=False Behavior Change

```python
# In v14+, run=False returns a QueryBuilder object, NOT a SQL string
query = frappe.get_all("Sales Order", run=False)
type(query)       # <class 'frappe.query_builder.builder.MariaDB'>

# To get the SQL string:
sql_string = query.get_sql()
```

## frappe.db.sql Migration

### Simple SELECT

```python
# ❌ OLD — raw SQL
result = frappe.db.sql("""
    SELECT name, customer, grand_total
    FROM `tabSales Order`
    WHERE status = %s AND docstatus = 1
    ORDER BY creation DESC
    LIMIT 20
""", ("To Deliver and Bill",), as_dict=True)

# ✅ NEW — query builder
from pypika import Order
so = frappe.qb.DocType("Sales Order")
result = (
    frappe.qb.from_(so)
    .select(so.name, so.customer, so.grand_total)
    .where(so.status == "To Deliver and Bill")
    .where(so.docstatus == 1)
    .orderby(so.creation, order=Order.desc)
    .limit(20)
    .run(as_dict=True)
)
```

### JOIN query

```python
# ❌ OLD
result = frappe.db.sql("""
    SELECT so.name, so.customer, soi.item_code, soi.qty
    FROM `tabSales Order` so
    LEFT JOIN `tabSales Order Item` soi ON soi.parent = so.name
    WHERE so.docstatus = 1
""", as_dict=True)

# ✅ NEW
so = frappe.qb.DocType("Sales Order")
soi = frappe.qb.DocType("Sales Order Item")
result = (
    frappe.qb.from_(so)
    .left_join(soi).on(soi.parent == so.name)
    .select(so.name, so.customer, soi.item_code, soi.qty)
    .where(so.docstatus == 1)
    .run(as_dict=True)
)
```

### GROUP BY with aggregation

```python
# ❌ OLD
result = frappe.db.sql("""
    SELECT account, SUM(debit) as total_debit, COUNT(*) as entries
    FROM `tabGL Entry`
    WHERE docstatus = 1
    GROUP BY account
    HAVING SUM(debit) > 0
""", as_dict=True)

# ✅ NEW
from frappe.query_builder.functions import Count, Sum
gl = frappe.qb.DocType("GL Entry")
total_debit = Sum(gl.debit).as_("total_debit")
result = (
    frappe.qb.from_(gl)
    .select(gl.account, total_debit, Count("*").as_("entries"))
    .where(gl.docstatus == 1)
    .groupby(gl.account)
    .having(Sum(gl.debit) > 0)
    .run(as_dict=True)
)
```

## When to Keep Using frappe.db.sql

Some queries are too complex for the query builder:

- **UNION queries** with different structures
- **Complex nested subqueries** with multiple levels
- **Database-specific syntax** not covered by PyPika
- **Temporary tables or CTEs** (Common Table Expressions)

For these cases, ALWAYS use parameterized queries:

```python
# ✅ Safe raw SQL with parameterized values
result = frappe.db.sql("""
    SELECT name FROM `tabSales Order`
    WHERE customer = %(customer)s
    AND creation > %(date)s
""", {"customer": customer, "date": start_date}, as_dict=True)

# ❌ NEVER interpolate values into SQL
result = frappe.db.sql(f"SELECT * FROM `tabSales Order` WHERE customer = '{customer}'")
```
