# Anti-Patterns: Mistakes to Avoid

> Common mistakes in Jinja templates and how to prevent them.

---

## ❌ Query in Loop (N+1 Problem)

### Wrong

```jinja
{% for item in doc.items %}
    {% set stock = frappe.db.get_value("Bin", {"item_code": item.item_code}, "actual_qty") %}
    <p>{{ item.item_name }}: {{ stock }} in stock</p>
{% endfor %}
```

**Problem**: With 100 items, 100+ database queries are executed.

### Correct

```python
# In Python controller/print format script
def get_context(context):
    item_codes = [item.item_code for item in doc.items]
    bins = frappe.get_all("Bin", 
        filters={"item_code": ["in", item_codes]},
        fields=["item_code", "actual_qty"]
    )
    context.stock_qty = {b.item_code: b.actual_qty for b in bins}
```

```jinja
{% for item in doc.items %}
    <p>{{ item.item_name }}: {{ stock_qty.get(item.item_code, 0) }} in stock</p>
{% endfor %}
```

---

## ❌ Heavy Calculations in Template

### Wrong

```jinja
{% set complex_total = 0 %}
{% for item in doc.items %}
    {% set item_discount = item.rate * (item.discount_percentage / 100) %}
    {% set item_tax = (item.rate - item_discount) * 0.21 %}
    {% set item_total = (item.rate - item_discount + item_tax) * item.qty %}
    {% set complex_total = complex_total + item_total %}
{% endfor %}
<p>Total: {{ complex_total }}</p>
```

### Correct

Do calculations in Python, not in Jinja:

```python
# In controller
def get_context(context):
    total = 0
    for item in doc.items:
        discount = item.rate * (item.discount_percentage / 100)
        tax = (item.rate - discount) * 0.21
        total += (item.rate - discount + tax) * item.qty
    context.calculated_total = total
```

```jinja
<p>Total: {{ calculated_total }}</p>
```

---

## ❌ Unescaped User Input (XSS Risk)

### Wrong

```jinja
{# DANGEROUS - XSS risk #}
{{ user_comment | safe }}
{{ frappe.form_dict.search | safe }}
```

### Correct

```jinja
{# Automatically escaped (safe) #}
{{ user_comment }}

{# Only use safe for trusted admin content #}
{{ doc.terms | safe }}  {# Only if terms is entered by admin #}

{# Explicitly escape when in doubt #}
{{ potentially_unsafe | escape }}
```

---

## ❌ Hardcoded Strings (Not Translatable)

### Wrong

```jinja
<th>Invoice Number</th>
<th>Amount</th>
<p>Thank you for your business!</p>
```

### Correct

```jinja
<th>{{ _("Invoice Number") }}</th>
<th>{{ _("Amount") }}</th>
<p>{{ _("Thank you for your business!") }}</p>

{# With variables #}
<p>{{ _("Total: {0}").format(doc.grand_total) }}</p>
```

---

## ❌ No Default Values

### Wrong

```jinja
{# Can fail if field is None #}
<p>{{ doc.customer_group }}</p>
<p>{{ doc.notes | truncate(100) }}</p>
```

### Correct

```jinja
<p>{{ doc.customer_group | default('Not Set') }}</p>
<p>{{ doc.notes | default('') | truncate(100) }}</p>

{# Or with condition #}
{% if doc.notes %}
    <p>{{ doc.notes | truncate(100) }}</p>
{% endif %}
```

---

## ❌ Wrong Currency Formatting

### Wrong

```jinja
{# No currency symbol, wrong format #}
<p>{{ doc.grand_total }}</p>
<p>{{ "%.2f" | format(doc.grand_total) }}</p>
```

### Correct

```jinja
{# Use get_formatted for currency fields #}
<p>{{ doc.get_formatted("grand_total") }}</p>

{# Or frappe.format with fieldtype #}
<p>{{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}</p>

{# For child table items - pass parent doc #}
{% for row in doc.items %}
    <td>{{ row.get_formatted("amount", doc) }}</td>
{% endfor %}
```

---

## ❌ Forgetting Loop Variables

### Wrong

```jinja
{% for item in doc.items %}
    <tr class="{% if loop.index == 1 %}first{% endif %}">
        <td>{{ item.idx }}</td>  {# idx can differ from loop position #}
    </tr>
{% endfor %}
```

### Correct

```jinja
{% for item in doc.items %}
    <tr class="{% if loop.first %}first{% endif %}{% if loop.last %} last{% endif %}">
        <td>{{ loop.index }}</td>  {# Consistent numbering #}
    </tr>
{% endfor %}
```

### Available Loop Variables

| Variable | Description |
|----------|-------------|
| `loop.index` | 1-indexed position |
| `loop.index0` | 0-indexed position |
| `loop.first` | True on first iteration |
| `loop.last` | True on last iteration |
| `loop.length` | Total number of items |

---

## ❌ Jinja Syntax in Report Print Formats

### Wrong

```html
<!-- This does NOT work in Report Print Formats -->
{% for item in data %}
    <tr><td>{{ item.name }}</td></tr>
{% endfor %}
```

### Correct

Report Print Formats use JavaScript templating:

```html
<!-- JS Template syntax for Reports -->
{% for(var i=0; i<data.length; i++) { %}
<tr>
    <td>{%= data[i].name %}</td>
</tr>
{% } %}
```

**Note**: Do NOT use single quotes `'` in JS templates.

---

## ❌ Inefficient Document Retrieval

### Wrong

```jinja
{# Fetching full document for one field #}
{% set customer = frappe.get_doc("Customer", doc.customer) %}
<p>{{ customer.customer_group }}</p>
```

### Correct

```jinja
{# Only fetch the needed field #}
{% set customer_group = frappe.db.get_value("Customer", doc.customer, "customer_group") %}
<p>{{ customer_group }}</p>

{# Or multiple fields at once #}
{% set name, group = frappe.db.get_value("Customer", doc.customer, ["customer_name", "customer_group"]) %}
```

---

## ❌ Disabling Safe Render Without Reason

### Wrong

```python
# Disabling safe_render without good reason
def get_context(context):
    context.safe_render = False  # DANGEROUS
```

### Correct

Safe render protects against code injection. Only disable if absolutely necessary and you're certain all input is safe:

```python
def get_context(context):
    # Only disable with good reason and after security review
    # context.safe_render = False
    pass
```

---

## Summary: Best Practices

1. **ALWAYS** use `_()` for user-facing strings
2. **ALWAYS** use `get_formatted()` for currency/date fields
3. **NEVER** execute queries in loops
4. **NEVER** use `| safe` for user input
5. **ALWAYS** use default values for optional fields
6. **ALWAYS** do calculations in Python, not in Jinja
7. **REMEMBER** that Report Print Formats use JS, not Jinja
