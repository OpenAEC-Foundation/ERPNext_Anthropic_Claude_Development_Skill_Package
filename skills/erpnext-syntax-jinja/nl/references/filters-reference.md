# Jinja Filters Reference

> Standaard Jinja2 filters beschikbaar in Frappe/ERPNext templates.

---

## String Filters

| Filter | Voorbeeld | Output |
|--------|-----------|--------|
| `lower` | `{{ "HELLO" \| lower }}` | `hello` |
| `upper` | `{{ "hello" \| upper }}` | `HELLO` |
| `title` | `{{ "hello world" \| title }}` | `Hello World` |
| `trim` | `{{ "  text  " \| trim }}` | `text` |
| `escape` | `{{ "<b>text</b>" \| escape }}` | `&lt;b&gt;text&lt;/b&gt;` |
| `safe` | `{{ html_content \| safe }}` | Renders als HTML |

### Voorbeelden

```jinja
{# Lowercase/uppercase #}
{{ doc.customer_name | upper }}
{{ doc.status | lower }}

{# Title case #}
{{ doc.description | title }}

{# Trim whitespace #}
{{ doc.notes | trim }}

{# HTML escape (standaard, veilig) #}
{{ user_input | escape }}

{# Render als HTML (alleen voor vertrouwde content!) #}
{{ doc.terms | safe }}
```

---

## List/Array Filters

| Filter | Voorbeeld | Output |
|--------|-----------|--------|
| `length` | `{{ items \| length }}` | Aantal items |
| `first` | `{{ items \| first }}` | Eerste item |
| `last` | `{{ items \| last }}` | Laatste item |
| `join` | `{{ items \| join(', ') }}` | Items als string |
| `sort` | `{{ items \| sort }}` | Gesorteerde list |
| `reverse` | `{{ items \| reverse }}` | Omgekeerde volgorde |

### Voorbeelden

```jinja
{# Aantal items #}
<p>Items: {{ doc.items | length }}</p>

{# Eerste/laatste item #}
<p>First: {{ doc.items | first }}</p>
<p>Last: {{ doc.items | last }}</p>

{# Join naar string #}
{% set names = doc.items | map(attribute='item_name') | list %}
<p>Items: {{ names | join(', ') }}</p>
```

---

## Number Filters

| Filter | Voorbeeld | Output |
|--------|-----------|--------|
| `round` | `{{ 3.14159 \| round(2) }}` | `3.14` |
| `int` | `{{ "42" \| int }}` | `42` |
| `float` | `{{ "3.14" \| float }}` | `3.14` |
| `abs` | `{{ -5 \| abs }}` | `5` |

### Voorbeelden

```jinja
{# Afronden #}
{{ doc.discount_percentage | round(2) }}

{# Convert types #}
{{ doc.qty | int }}
{{ doc.rate | float }}

{# Absolute waarde #}
{{ doc.balance | abs }}
```

---

## Default Values

| Filter | Voorbeeld | Output |
|--------|-----------|--------|
| `default` | `{{ value \| default('N/A') }}` | Waarde of 'N/A' |

### Voorbeelden

```jinja
{# Default waarde als None/empty #}
{{ doc.customer_group | default('Not Set') }}
{{ doc.notes | default('No notes available') }}

{# Met boolean check #}
{{ doc.discount_percentage | default(0) }}
```

---

## Custom Filters via jenv Hook

### hooks.py Configuratie

```python
# hooks.py
jenv = {
    "filters": [
        "app.jinja.filters"
    ]
}
```

### Filter Implementatie

```python
# app/jinja/filters.py

def format_currency_custom(value, currency="EUR"):
    """Custom currency formatting filter"""
    return f"{currency} {value:,.2f}"

def truncate_text(text, length=100):
    """Truncate text met ellipsis"""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'

def nl2br(text):
    """Convert newlines naar <br> tags"""
    if not text:
        return ""
    return text.replace('\n', '<br>')
```

### Gebruik Custom Filters

```jinja
{# Custom filters #}
<p>{{ doc.grand_total | format_currency_custom("USD") }}</p>
<p>{{ doc.description | truncate_text(50) }}</p>
<p>{{ doc.notes | nl2br | safe }}</p>
```

---

## Filter Chaining

Filters kunnen gecombineerd worden:

```jinja
{# Meerdere filters combineren #}
{{ doc.description | trim | truncate_text(100) | title }}

{# Met escape en safe #}
{{ doc.notes | nl2br | safe }}

{# Strings bewerken #}
{{ doc.customer_name | lower | title }}
```
