# Jinja Filters Reference

> Standard Jinja2 filters available in Frappe/ERPNext templates.

---

## String Filters

| Filter | Example | Output |
|--------|---------|--------|
| `lower` | `{{ "HELLO" \| lower }}` | `hello` |
| `upper` | `{{ "hello" \| upper }}` | `HELLO` |
| `title` | `{{ "hello world" \| title }}` | `Hello World` |
| `trim` | `{{ "  text  " \| trim }}` | `text` |
| `escape` | `{{ "<b>text</b>" \| escape }}` | `&lt;b&gt;text&lt;/b&gt;` |
| `safe` | `{{ html_content \| safe }}` | Renders as HTML |

### Examples

```jinja
{# Lowercase/uppercase #}
{{ doc.customer_name | upper }}
{{ doc.status | lower }}

{# Title case #}
{{ doc.description | title }}

{# Trim whitespace #}
{{ doc.notes | trim }}

{# HTML escape (default, safe) #}
{{ user_input | escape }}

{# Render as HTML (only for trusted content!) #}
{{ doc.terms | safe }}
```

---

## List/Array Filters

| Filter | Example | Output |
|--------|---------|--------|
| `length` | `{{ items \| length }}` | Number of items |
| `first` | `{{ items \| first }}` | First item |
| `last` | `{{ items \| last }}` | Last item |
| `join` | `{{ items \| join(', ') }}` | Items as string |
| `sort` | `{{ items \| sort }}` | Sorted list |
| `reverse` | `{{ items \| reverse }}` | Reversed order |

### Examples

```jinja
{# Number of items #}
<p>Items: {{ doc.items | length }}</p>

{# First/last item #}
<p>First: {{ doc.items | first }}</p>
<p>Last: {{ doc.items | last }}</p>

{# Join to string #}
{% set names = doc.items | map(attribute='item_name') | list %}
<p>Items: {{ names | join(', ') }}</p>
```

---

## Number Filters

| Filter | Example | Output |
|--------|---------|--------|
| `round` | `{{ 3.14159 \| round(2) }}` | `3.14` |
| `int` | `{{ "42" \| int }}` | `42` |
| `float` | `{{ "3.14" \| float }}` | `3.14` |
| `abs` | `{{ -5 \| abs }}` | `5` |

### Examples

```jinja
{# Rounding #}
{{ doc.discount_percentage | round(2) }}

{# Type conversion #}
{{ doc.qty | int }}
{{ doc.rate | float }}

{# Absolute value #}
{{ doc.balance | abs }}
```

---

## Default Values

| Filter | Example | Output |
|--------|---------|--------|
| `default` | `{{ value \| default('N/A') }}` | Value or 'N/A' |

### Examples

```jinja
{# Default value if None/empty #}
{{ doc.customer_group | default('Not Set') }}
{{ doc.notes | default('No notes available') }}

{# With boolean check #}
{{ doc.discount_percentage | default(0) }}
```

---

## Custom Filters via jenv Hook

### hooks.py Configuration

```python
# hooks.py
jenv = {
    "filters": [
        "app.jinja.filters"
    ]
}
```

### Filter Implementation

```python
# app/jinja/filters.py

def format_currency_custom(value, currency="EUR"):
    """Custom currency formatting filter"""
    return f"{currency} {value:,.2f}"

def truncate_text(text, length=100):
    """Truncate text with ellipsis"""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'

def nl2br(text):
    """Convert newlines to <br> tags"""
    if not text:
        return ""
    return text.replace('\n', '<br>')
```

### Using Custom Filters

```jinja
{# Custom filters #}
<p>{{ doc.grand_total | format_currency_custom("USD") }}</p>
<p>{{ doc.description | truncate_text(50) }}</p>
<p>{{ doc.notes | nl2br | safe }}</p>
```

---

## Filter Chaining

Filters can be combined:

```jinja
{# Combining multiple filters #}
{{ doc.description | trim | truncate_text(100) | title }}

{# With escape and safe #}
{{ doc.notes | nl2br | safe }}

{# String processing #}
{{ doc.customer_name | lower | title }}
```
