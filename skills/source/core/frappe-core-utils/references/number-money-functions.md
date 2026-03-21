# Number & Money Functions — frappe.utils

## Type Conversion

```python
from frappe.utils import flt, cint, cstr, sbool

# flt — safe float conversion with precision
flt(None)           # 0.0
flt("")             # 0.0
flt("123.456", 2)   # 123.46
flt(100)            # 100.0

# cint — safe integer conversion
cint(None)          # 0
cint("")            # 0
cint("42")          # 42
cint(3.7)           # 3

# cstr — safe string conversion
cstr(None)          # ""
cstr(42)            # "42"
cstr(["a", "b"])    # "['a', 'b']"

# sbool — flexible boolean ("Yes"/"No"/"1"/"0"/True/False)
sbool("Yes")        # True
sbool("No")         # False
sbool("1")          # True
sbool("0")          # False
sbool(True)         # True
sbool(None)         # False
```

## Rounding & Math

```python
from frappe.utils import rounded, safe_div

# rounded — banker's rounding (consistent with Frappe)
rounded(2.345, 2)    # 2.35
rounded(2.335, 2)    # 2.34 (banker's rounding)
rounded(100.5, 0)    # 100.0

# safe_div — zero-division protection [v15+]
safe_div(100, 3)           # 33.333...
safe_div(100, 0)           # 0.0 (default)
safe_div(100, 0, default=-1)  # -1
```

## Money Formatting

```python
from frappe.utils import fmt_money, money_in_words, in_words

# fmt_money — locale-aware currency formatting
fmt_money(2399.50, currency="USD")    # "$ 2,399.50"
fmt_money(2399.50, currency="EUR")    # "€ 2,399.50"
fmt_money(2399.50, precision=0)       # "2,400"

# money_in_words — amount to text
money_in_words(950, "USD")
# "USD Nine Hundred and Fifty only."

money_in_words(1234.56, "EUR")
# "EUR One Thousand, Two Hundred and Thirty Four and Fifty Six Cents only."

# in_words — integer to words (no currency)
in_words(50)          # "Fifty"
in_words(1234)        # "One Thousand, Two Hundred and Thirty Four"

# round_based_on_smallest_currency_fraction
from frappe.utils import round_based_on_smallest_currency_fraction
round_based_on_smallest_currency_fraction(99.999, "USD")  # 100.0
```

## Casting by Fieldtype

```python
from frappe.utils import cast

# Cast value to match Frappe fieldtype
cast("Currency", "123.45")    # 123.45 (float)
cast("Int", "42")             # 42 (int)
cast("Check", "1")            # True (bool)
cast("Date", "2024-03-15")    # datetime.date
```

## Common Patterns

### Safe Calculation with Precision

```python
# ALWAYS use flt() for arithmetic on document fields
total = flt(doc.qty, 2) * flt(doc.rate, 2)
doc.amount = flt(total, 2)

# NEVER do this — crashes on None fields
total = float(doc.qty) * float(doc.rate)  # TypeError if None
```

### Currency Display

```python
# In a print format or notification
formatted = fmt_money(doc.grand_total, currency=doc.currency)
words = money_in_words(doc.grand_total, doc.currency)
```

### Safe Division in Percentage Calculations

```python
# v15+: Use safe_div
completion = safe_div(completed_tasks, total_tasks) * 100

# v14: Guard manually
completion = (flt(completed_tasks) / flt(total_tasks) * 100) if total_tasks else 0
```
