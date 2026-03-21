# Date/Time Functions — frappe.utils

## Current Date/Time

```python
from frappe.utils import nowdate, now_datetime, nowtime, today

nowdate()        # datetime.date — current date in system timezone
today()          # datetime.date — alias for nowdate()
now_datetime()   # datetime.datetime — current datetime in system timezone
now()            # str "yyyy-mm-dd hh:mm:ss" — current datetime as string
nowtime()        # str — current time as formatted string
```

## Parsing

```python
from frappe.utils import getdate, get_datetime, get_timedelta, get_timestamp

getdate("2024-03-15")           # datetime.date(2024, 3, 15)
getdate(None)                   # datetime.date.today()
get_datetime("2024-03-15 10:30:00")  # datetime.datetime
get_timedelta("5:30:00")        # datetime.timedelta
get_timestamp(datetime_obj)     # float — Unix timestamp
```

## Formatting

```python
from frappe.utils import (
    get_datetime_str, get_date_str, get_time_str,
    format_date, format_time, format_datetime,
    format_duration, pretty_date
)

# Internal format (for storage/API)
get_datetime_str(dt)    # "2024-03-15 10:30:00"
get_date_str(dt)        # "2024-03-15"
get_time_str(dt)        # "10:30:00"

# User-facing format (respects user preferences)
format_date(dt)              # "15-03-2024" (per user date_format)
format_date(dt, "dd/mm/yyyy") # Force specific format
format_time(dt)              # "10:30 AM"
format_datetime(dt)          # "15-03-2024 10:30 AM"

# Duration
format_duration(10000)                # "2h 46m 40s"
format_duration(100000, hide_days=False)  # "1d 3h 46m 40s"

# Relative time
pretty_date("2024-03-15 10:00:00")  # "2 hours ago", "just now", etc.
```

## Arithmetic

```python
from frappe.utils import add_days, add_months, add_years, add_to_date

add_days("2024-03-15", 10)     # datetime.date(2024, 3, 25)
add_days("2024-03-15", -5)     # datetime.date(2024, 3, 10)
add_months("2024-01-31", 1)    # datetime.date(2024, 2, 29) — handles month-end
add_years("2024-02-29", 1)     # datetime.date(2025, 2, 28) — handles leap years

# Full arithmetic with add_to_date
add_to_date("2024-01-15",
    years=1, months=2, weeks=1, days=3,
    hours=5, minutes=30, seconds=15,
    as_string=False,    # return datetime object
    as_datetime=True    # return datetime (not date)
)
```

## Differences

```python
from frappe.utils import date_diff, month_diff, time_diff_in_seconds, time_diff_in_hours

date_diff("2024-03-20", "2024-03-15")       # 5 (int days)
month_diff("2024-06-15", "2024-01-15")       # 5.0 (float months)
time_diff_in_seconds("10:30:00", "10:00:00") # 1800.0
time_diff_in_hours("18:00:00", "09:00:00")   # 9.0
```

## Period Boundaries

```python
from frappe.utils import (
    get_first_day, get_last_day,
    get_first_day_of_week, get_last_day_of_week,
    get_quarter_start, get_quarter_ending,
    get_year_start, get_year_ending,
    is_last_day_of_the_month
)

get_first_day("2024-03-15")      # datetime.date(2024, 3, 1)
get_last_day("2024-03-15")       # datetime.date(2024, 3, 31)
get_first_day_of_week("2024-03-15")  # Monday of that week
get_quarter_start("2024-08-15")  # datetime.date(2024, 7, 1)
get_quarter_ending("2024-08-15") # datetime.date(2024, 9, 30)
get_year_start("2024-08-15")     # datetime.date(2024, 1, 1)
get_year_ending("2024-08-15")    # datetime.date(2024, 12, 31)
is_last_day_of_the_month("2024-03-31")  # True
```

## Timezone

```python
from frappe.utils import (
    get_system_timezone,
    convert_utc_to_system_timezone,
    convert_utc_to_timezone,
    get_datetime_in_timezone
)

get_system_timezone()                    # "Asia/Kolkata"
convert_utc_to_system_timezone(utc_dt)   # datetime in system TZ
convert_utc_to_timezone(utc_dt, "US/Eastern")  # datetime in specified TZ
get_datetime_in_timezone(dt, "Europe/Amsterdam") # convert to specified TZ
```

## Other Date Utilities

```python
from frappe.utils import (
    get_weekdays, get_weekday,
    get_timespan_date_range,  # v15+
    guess_date_format,        # v15+
    duration_to_seconds,      # v15+
    get_eta
)

get_weekdays()                    # ["Monday", "Tuesday", ...]
get_weekday("2024-03-15")        # "Friday"
get_timespan_date_range("Last Quarter")  # (start_date, end_date)
guess_date_format("15/03/2024")  # "dd/mm/yyyy"
duration_to_seconds("2h 30m")    # 9000.0
get_eta(start_dt, 0.75)          # estimated completion datetime
```
