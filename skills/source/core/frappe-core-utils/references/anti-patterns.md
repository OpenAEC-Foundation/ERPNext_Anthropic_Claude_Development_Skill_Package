# Anti-patterns — frappe.utils

## The Golden Rule

> **NEVER use Python stdlib for operations that frappe.utils provides.**
> Frappe utilities handle None/empty values, respect timezone settings,
> use locale-aware formatting, and work correctly in multi-tenant setups.

---

## Date/Time Anti-patterns

### Using datetime module directly

```python
# ❌ WRONG — ignores system timezone configuration
import datetime
today = datetime.date.today()
now = datetime.datetime.now()
formatted = now.strftime("%Y-%m-%d")

# ✅ CORRECT — respects system timezone
from frappe.utils import nowdate, now_datetime, get_datetime_str
today = nowdate()
now = now_datetime()
formatted = get_datetime_str(now)
```

### Using strftime for user-facing dates

```python
# ❌ WRONG — ignores user's date format preference
display = doc.posting_date.strftime("%d/%m/%Y")

# ✅ CORRECT — uses user's configured format
from frappe.utils import format_date
display = format_date(doc.posting_date)
```

### Manual month-end calculation

```python
# ❌ WRONG — reimplements what frappe.utils provides
import calendar
_, last_day = calendar.monthrange(2024, 2)
month_end = datetime.date(2024, 2, last_day)

# ✅ CORRECT
from frappe.utils import get_last_day
month_end = get_last_day("2024-02-15")
```

### Manual date arithmetic with relativedelta

```python
# ❌ WRONG — extra dependency, edge cases
from dateutil.relativedelta import relativedelta
next_quarter = date + relativedelta(months=3)

# ✅ CORRECT — handles month-end edge cases
from frappe.utils import add_months
next_quarter = add_months(date, 3)
```

---

## Number Anti-patterns

### Unsafe type conversion

```python
# ❌ WRONG — crashes on None, empty string, or invalid input
amount = float(doc.amount)    # TypeError: float() argument must be a string or a real number, not 'NoneType'
qty = int(doc.qty)            # ValueError: invalid literal for int() with base 10: ''

# ✅ CORRECT — handles None, empty, invalid gracefully
from frappe.utils import flt, cint
amount = flt(doc.amount, 2)   # 0.0 if None/empty
qty = cint(doc.qty)           # 0 if None/empty
```

### Unguarded division

```python
# ❌ WRONG — ZeroDivisionError
percentage = completed / total * 100

# ✅ CORRECT (v15+)
from frappe.utils import safe_div
percentage = safe_div(completed, total) * 100

# ✅ CORRECT (v14)
percentage = (flt(completed) / flt(total) * 100) if total else 0
```

### Manual currency formatting

```python
# ❌ WRONG — ignores locale, currency symbol, number format
display = "${:,.2f}".format(amount)
display = f"€ {amount:.2f}"

# ✅ CORRECT — locale-aware, respects system number format
from frappe.utils import fmt_money
display = fmt_money(amount, currency="USD")
display = fmt_money(amount, currency="EUR")
```

### Python round() instead of Frappe rounded()

```python
# ❌ WRONG — Python uses different rounding behavior
value = round(2.335, 2)  # 2.33 (Python banker's rounding)

# ✅ CORRECT — consistent with Frappe's rounding
from frappe.utils import rounded
value = rounded(2.335, 2)  # Frappe's consistent rounding
```

---

## String Anti-patterns

### Manual HTML stripping

```python
# ❌ WRONG — misses nested tags, attributes, edge cases
import re
clean = re.sub(r'<[^>]+>', '', html_content)

# ✅ CORRECT
from frappe.utils import strip_html
clean = strip_html(html_content)
```

### Manual list joining

```python
# ❌ WRONG — no localized "and", poor readability
names = ", ".join(user_list)

# ✅ CORRECT — "Alice, Bob, and Charlie"
from frappe.utils import comma_and
names = comma_and(user_list)
```

### Manual JSON handling

```python
# ❌ WRONG — crashes on None/empty/invalid
import json
data = json.loads(doc.json_field)      # ValueError on empty
output = json.dumps(result)

# ✅ CORRECT
from frappe.utils import parse_json
data = parse_json(doc.json_field)      # handles None/empty
output = frappe.as_json(result)

# v16+: With default fallback
from frappe.utils import safe_json_loads
data = safe_json_loads(doc.json_field, default={})
```

---

## File Path Anti-patterns

### Manual path construction

```python
# ❌ WRONG — breaks multi-tenancy, hardcodes structure
import os
path = os.path.join("/home/frappe/frappe-bench/sites", site_name, "public", "files")
private = os.path.join("/home/frappe/frappe-bench/sites", site_name, "private", "files")

# ✅ CORRECT — respects bench/site structure
from frappe.utils import get_files_path, get_site_path
path = get_files_path()                        # public files
private = get_files_path(is_private=True)      # private files
custom = get_site_path("private", "backups")   # any site subdirectory
```

---

## Server Script Anti-patterns

```python
# ❌ NEVER in Server Scripts (RestrictedPython blocks ALL imports)
from frappe.utils import nowdate, flt
import json
import datetime

# ✅ ALWAYS in Server Scripts — use frappe namespace directly
today = frappe.utils.nowdate()
amount = frappe.utils.flt(doc.amount, 2)
data = frappe.parse_json(doc.custom_json)
now = frappe.utils.now_datetime()
formatted = frappe.utils.fmt_money(doc.total, currency=doc.currency)
```

---

## Validation Anti-patterns

### Manual email regex

```python
# ❌ WRONG — incomplete regex, misses edge cases
import re
if re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
    pass

# ✅ CORRECT — RFC-compliant, handles multiple emails
from frappe.utils import validate_email_address
valid = validate_email_address(email)  # returns email or ""
```

### Manual URL validation

```python
# ❌ WRONG
if url.startswith("http"):
    pass

# ✅ CORRECT — validates scheme, structure
from frappe.utils import validate_url
if validate_url(url, valid_schemes=["https"]):
    pass
```

---

## Summary Rule

> If you find yourself importing `datetime`, `json`, `os.path`, `re`, `calendar`,
> `math`, or `humanize` — **STOP**. Check `frappe.utils` first.
> In 90% of cases, the function you need already exists and handles edge cases better.
