# Cross-DB Patterns — frappe.qb

## The Problem

Frappe supports both **MariaDB** and **PostgreSQL**. Some SQL functions have
different names or syntax between databases. Writing raw SQL locks you to one DB.

## ImportMapper — The Solution

`ImportMapper` automatically selects the correct function based on `frappe.conf.db_type`.

```python
from frappe.query_builder.utils import ImportMapper, db_type_is
```

### db_type_is Enum

| Value | Database |
|-------|----------|
| `db_type_is.MARIADB` | MariaDB / MySQL |
| `db_type_is.POSTGRES` | PostgreSQL |
| `db_type_is.SQLITE` | SQLite [v16+] |

## Common ImportMapper Patterns

### GROUP_CONCAT / STRING_AGG

```python
from frappe.query_builder.custom import GROUP_CONCAT, STRING_AGG

GroupConcat = ImportMapper({
    db_type_is.MARIADB: GROUP_CONCAT,
    db_type_is.POSTGRES: STRING_AGG,
})

dt = frappe.qb.DocType("Has Role")
result = (
    frappe.qb.from_(dt)
    .select(dt.parent, GroupConcat(dt.role))
    .groupby(dt.parent)
    .run(as_dict=True)
)
# MariaDB:   GROUP_CONCAT(`role`)
# PostgreSQL: STRING_AGG(`role`, ',')
```

### Full-Text Search

```python
from frappe.query_builder.custom import MATCH, TO_TSVECTOR

FullTextSearch = ImportMapper({
    db_type_is.MARIADB: MATCH,
    db_type_is.POSTGRES: TO_TSVECTOR,
})

dt = frappe.qb.DocType("Web Page")
# MariaDB:   MATCH(`content`) AGAINST('search term')
# PostgreSQL: TO_TSVECTOR(`content`) @@ PLAINTO_TSQUERY('search term')
```

### String Position

```python
from frappe.query_builder.functions import Locate, Strpos

StringPosition = ImportMapper({
    db_type_is.MARIADB: Locate,
    db_type_is.POSTGRES: Strpos,
})
```

## Auto-Handled Differences

These functions are automatically translated by the query builder — no ImportMapper needed:

| Function | MariaDB | PostgreSQL | Action |
|----------|---------|-----------|--------|
| `Timestamp(date, time)` | `TIMESTAMP(date, time)` | `date + time` arithmetic | Auto |
| `UnixTimestamp(field)` | `UNIX_TIMESTAMP(field)` | `EXTRACT(EPOCH FROM field)` | Auto |
| `Cast_()` with VARCHAR | `CONCAT(value, '')` workaround | Standard `CAST` | Auto |

## PostgreSQL-Specific Field Translations

The Postgres builder automatically maps system table queries:

| MariaDB | PostgreSQL |
|---------|-----------|
| `table_name` | `relname` |
| `table_rows` | `n_tup_ins` |
| `information_schema.tables` | `pg_stat_all_tables` |

## Building Cross-DB Compatible Code

### Rule 1: ALWAYS use DocType(), NEVER raw table names

```python
# ✅ CORRECT — DocType adds "tab" prefix correctly per DB
dt = frappe.qb.DocType("Sales Order")

# ❌ WRONG — no "tab" prefix, may break
from pypika import Table
dt = Table("tabSales Order")  # Don't do this
```

### Rule 2: Use ImportMapper for DB-specific functions

```python
# ✅ CORRECT — works on both MariaDB and PostgreSQL
GroupConcat = ImportMapper({
    db_type_is.MARIADB: GROUP_CONCAT,
    db_type_is.POSTGRES: STRING_AGG,
})

# ❌ WRONG — breaks on PostgreSQL
from frappe.query_builder.custom import GROUP_CONCAT
# Direct use only works on MariaDB
```

### Rule 3: Avoid DB-specific SQL in frappe.db.sql

```python
# ❌ WRONG — MariaDB-only syntax
frappe.db.sql("SELECT GROUP_CONCAT(role) FROM `tabHas Role`")

# ✅ CORRECT — use query builder with ImportMapper
GroupConcat = ImportMapper({...})
frappe.qb.from_(dt).select(GroupConcat(dt.role)).run()
```

### Rule 4: Test on both databases when possible

If your Frappe app claims PostgreSQL support, test queries on both databases.
The query builder handles most differences, but edge cases can slip through
with custom functions or raw SQL fragments.

## Checking Current Database Type

```python
# In Python
db_type = frappe.conf.db_type  # "mariadb" or "postgres"

# Conditional logic (when ImportMapper isn't enough)
if frappe.conf.db_type == "mariadb":
    # MariaDB-specific logic
    pass
elif frappe.conf.db_type == "postgres":
    # PostgreSQL-specific logic
    pass
```
