# Functions & Aggregates — frappe.qb

## Standard Aggregates

```python
from frappe.query_builder.functions import Count, Sum, Avg, Min, Max

dt = frappe.qb.DocType("GL Entry")

# Count
Count("*")                        # COUNT(*)
Count(dt.name).as_("total")       # COUNT(`name`) AS `total`

# Sum
Sum(dt.debit).as_("total_debit")  # SUM(`debit`) AS `total_debit`

# Average
Avg(dt.amount).as_("avg_amount")  # AVG(`amount`) AS `avg_amount`

# Min / Max
Min(dt.creation).as_("oldest")
Max(dt.creation).as_("newest")
```

## Shortcut Aggregation Methods

```python
# Patched onto frappe.qb — convenience wrappers
frappe.qb.sum("GL Entry", "debit", filters={"account": "Sales"})
frappe.qb.max("Stock Ledger Entry", "actual_qty", filters={"item_code": "ITEM-001"})
frappe.qb.min("Sales Order", "creation", filters={"status": "Open"})
frappe.qb.avg("Sales Invoice Item", "rate", filters={"item_code": "ITEM-001"})
```

## Built-in Functions (frappe.query_builder.functions)

| Function | Signature | Description |
|----------|-----------|-------------|
| `Count` | `Count(field)` | Row count |
| `Sum` | `Sum(field)` | Sum values |
| `Avg` | `Avg(field)` | Average |
| `Min` | `Min(field)` | Minimum |
| `Max` | `Max(field)` | Maximum |
| `IfNull` | `IfNull(field, default)` | NULL coalescing |
| `Coalesce` | `Coalesce(f1, f2, ...)` | Multi-value NULL coalescing |
| `Timestamp` | `Timestamp(date, time)` | Combine date + time fields |
| `Round` | `Round(field, decimals)` | Round value |
| `Truncate` | `Truncate(field, decimals)` | Truncate decimals |
| `Cast_` | `Cast_(value, as_type)` | Type casting (note underscore) |
| `Concat_ws` | `Concat_ws(sep, *fields)` | Concat with separator |
| `Locate` | `Locate(needle, haystack)` | String search (MariaDB) |
| `Strpos` | `Strpos(needle, haystack)` | String search (PostgreSQL) |
| `YearWeek` | `YearWeek(field)` | Year-week number |
| `UnixTimestamp` | `UnixTimestamp(field)` | Unix timestamp |

## Custom Functions (frappe.query_builder.custom)

| Function | Signature | Description |
|----------|-----------|-------------|
| `ConstantColumn` | `ConstantColumn(value)` | Pseudo-column with constant value |
| `GROUP_CONCAT` | `GROUP_CONCAT(field)` | Group concat (MariaDB only) |
| `STRING_AGG` | `STRING_AGG(field, sep)` | String aggregate (PostgreSQL only) |
| `MATCH` | `MATCH(field).Against(text)` | Full-text search (MariaDB) |
| `TO_TSVECTOR` | `TO_TSVECTOR(field).Against(text)` | Full-text search (PostgreSQL) |
| `MonthName` | `MonthName(field)` | Month name from date |
| `Quarter` | `Quarter(field)` | Quarter number from date |
| `Month` | `Month(field)` | Month number from date |

## Case Expressions

```python
from pypika.terms import Case

# Simple CASE
case = (
    Case()
    .when(dt.status == "Open", "Active")
    .when(dt.status == "Closed", "Inactive")
    .else_("Unknown")
    .as_("status_label")
)

# CASE with aggregation
case_unique = Case().when(dt.is_unique == "1", "1")
count_unique = Count(case_unique).as_("unique_visits")

# Full query with CASE
result = (
    frappe.qb.from_(dt)
    .select(dt.name, case)
    .run(as_dict=True)
)
```

## Subqueries

```python
from frappe.query_builder.terms import SubQuery

# Subquery in WHERE ... IN
soi = frappe.qb.DocType("Sales Order Item")
so = frappe.qb.DocType("Sales Order")

inner = (
    frappe.qb.from_(soi)
    .select(soi.parent)
    .where(soi.item_code == "ITEM-001")
)

orders = (
    frappe.qb.from_(so)
    .select(so.name, so.customer)
    .where(so.name.isin(SubQuery(inner)))
    .run(as_dict=True)
)

# Subquery as computed field
count_sub = SubQuery(
    frappe.qb.from_(soi)
    .select(Count("*"))
    .where(soi.parent == so.name)
)

result = (
    frappe.qb.from_(so)
    .select(so.name, count_sub.as_("item_count"))
    .run(as_dict=True)
)
```

## ValueWrapper & ConstantColumn

```python
from pypika.terms import ValueWrapper
from frappe.query_builder.custom import ConstantColumn

# Literal value as field
result = (
    frappe.qb.from_(dt)
    .select(dt.name, ValueWrapper("Sales Order").as_("doctype"))
    .run(as_dict=True)
)
# Returns: [{"name": "SO-001", "doctype": "Sales Order"}, ...]

# ConstantColumn — similar but for column-like constants
result = (
    frappe.qb.from_(dt)
    .select(dt.name, ConstantColumn("Active").as_("status"))
    .run(as_dict=True)
)
```

## Custom PyPika Functions

```python
from pypika import CustomFunction

# Define custom SQL function
JsonExtract = CustomFunction("JSON_EXTRACT", ["field", "path"])

dt = frappe.qb.DocType("Custom DocType")
result = (
    frappe.qb.from_(dt)
    .select(dt.name, JsonExtract(dt.json_field, "$.key").as_("value"))
    .run(as_dict=True)
)
```

## Query Execution

```python
query = frappe.qb.from_(dt).select(dt.name).where(dt.status == "Open")

# Execute and get results
tuples = query.run()                    # [(name,), ...]
dicts = query.run(as_dict=True)         # [{"name": "..."}, ...]

# Get SQL string (for debugging)
sql = query.get_sql()                   # "SELECT `name` FROM `tabSales Order` WHERE ..."

# NEVER do this — bypasses parameterization:
# frappe.db.sql(query.get_sql())  # ❌ WRONG
```
