# Jinja Print Formats — Complete Reference

> Detailed reference for Jinja-based print formats in Frappe v14/v15/v16.

---

## Template Context

Every Jinja Print Format receives these variables automatically:

| Variable | Type | Description |
|----------|------|-------------|
| `doc` | `Document` | The document being printed (fully loaded with child tables) |
| `meta` | `Meta` | DocType metadata (field definitions, permissions) |
| `layout` | `list` | Field layout sections from DocType definition |
| `letter_head` | `str` | Pre-rendered Letter Head HTML |
| `footer` | `str` | Pre-rendered footer HTML |
| `print_settings` | `dict` | Print Settings document values |
| `frappe` | `module` | Full `frappe` module — access to all utilities |
| `frappe.utils` | `module` | All utility functions (nowdate, flt, fmt_money, etc.) |
| `no_letterhead` | `int` | 1 if Letter Head should be suppressed |

---

## Jinja Syntax Quick Reference

### Output Expressions

```html
<!-- Simple field output -->
{{ doc.name }}
{{ doc.customer_name }}
{{ doc.posting_date }}

<!-- Nested child table access -->
{% for item in doc.items %}
  {{ item.item_name }} - {{ item.qty }}
{% endfor %}

<!-- Frappe utility functions -->
{{ frappe.utils.nowdate() }}
{{ frappe.utils.flt(doc.grand_total, 2) }}
{{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}
{{ frappe.format_value(doc.posting_date, {"fieldtype": "Date"}) }}
```

### Control Flow

```html
<!-- Conditionals -->
{% if doc.discount_amount > 0 %}
  <p>Discount: {{ frappe.utils.fmt_money(doc.discount_amount, currency=doc.currency) }}</p>
{% endif %}

{% if doc.status == "Paid" %}
  <span class="badge badge-success">PAID</span>
{% elif doc.status == "Overdue" %}
  <span class="badge badge-danger">OVERDUE</span>
{% else %}
  <span class="badge badge-warning">{{ doc.status }}</span>
{% endif %}

<!-- Loops -->
{% for row in doc.items %}
  <tr>
    <td>{{ loop.index }}</td>
    <td>{{ row.item_name }}</td>
    <td>{{ row.qty }}</td>
  </tr>
{% endfor %}

<!-- Loop utilities -->
{{ loop.index }}      {# 1-based counter #}
{{ loop.index0 }}     {# 0-based counter #}
{{ loop.first }}      {# True on first iteration #}
{{ loop.last }}       {# True on last iteration #}
{{ loop.length }}     {# Total number of items #}
```

### Setting Variables

```html
{% set total_qty = 0 %}
{% for row in doc.items %}
  {% set total_qty = total_qty + row.qty %}
{% endfor %}

{# NOTE: set inside a for loop does NOT update the outer variable in Jinja2. #}
{# Use namespace instead: #}
{% set ns = namespace(total_qty=0) %}
{% for row in doc.items %}
  {% set ns.total_qty = ns.total_qty + row.qty %}
{% endfor %}
<p>Total Qty: {{ ns.total_qty }}</p>
```

### Macros (Reusable Components)

```html
{% macro money(value, currency=doc.currency) %}
  {{ frappe.utils.fmt_money(value, currency=currency) }}
{% endmacro %}

{% macro address_block(address_name) %}
  {% set addr = frappe.get_doc("Address", address_name) %}
  <div class="address">
    {{ addr.address_line1 }}<br>
    {% if addr.address_line2 %}{{ addr.address_line2 }}<br>{% endif %}
    {{ addr.city }}, {{ addr.state }} {{ addr.pincode }}<br>
    {{ addr.country }}
  </div>
{% endmacro %}

<!-- Usage -->
<p>Total: {{ money(doc.grand_total) }}</p>
{{ address_block(doc.customer_address) }}
```

---

## Available Filters

### Built-in Jinja Filters

| Filter | Purpose | Example |
|--------|---------|---------|
| `default(value)` | Fallback for None/empty | `{{ doc.po_no \| default("N/A") }}` |
| `title` | Title case | `{{ doc.status \| title }}` |
| `lower` / `upper` | Case conversion | `{{ doc.name \| upper }}` |
| `replace(old, new)` | String replacement | `{{ doc.name \| replace("-", " ") }}` |
| `truncate(length)` | Truncate string | `{{ doc.description \| truncate(100) }}` |
| `round(precision)` | Round number | `{{ doc.rate \| round(2) }}` |
| `join(sep)` | Join list | `{{ tags \| join(", ") }}` |
| `safe` | Mark as safe HTML | `{{ doc.terms \| safe }}` |

### Frappe-Specific Filters

| Filter | Purpose | Example |
|--------|---------|---------|
| `global_date_format` | System date format | `{{ doc.posting_date \| global_date_format }}` |
| `json` | Serialize to JSON | `{{ doc.items \| json }}` |
| `len` | Get length | `{{ doc.items \| len }}` |
| `int` | Cast to int | `{{ value \| int }}` |
| `flt` | Cast to float | `{{ value \| flt }}` |
| `markdown` | Markdown to HTML | `{{ doc.description \| markdown }}` |
| `abs` | Absolute value | `{{ value \| abs }}` |

---

## Accessing Related Documents

### Fetching Related Data

```html
<!-- Get a linked document -->
{% set customer = frappe.get_doc("Customer", doc.customer) %}
<p>Customer Group: {{ customer.customer_group }}</p>

<!-- Get multiple records -->
{% set contacts = frappe.get_all("Contact",
    filters={"link_doctype": "Customer", "link_name": doc.customer},
    fields=["first_name", "last_name", "email_id"],
    limit=5
) %}
{% for contact in contacts %}
  <p>{{ contact.first_name }} {{ contact.last_name }} — {{ contact.email_id }}</p>
{% endfor %}

<!-- Get a single value (efficient) -->
{% set customer_group = frappe.db.get_value("Customer", doc.customer, "customer_group") %}
```

**IMPORTANT:** NEVER use `frappe.get_doc()` inside a `{% for %}` loop iterating over child table rows. This creates N+1 queries. Instead, fetch all needed data BEFORE the loop:

```html
{# CORRECT: Fetch once, use in loop #}
{% set item_groups = {} %}
{% for item_code in doc.items | map(attribute='item_code') | unique %}
  {% set _ = item_groups.update({item_code: frappe.db.get_value("Item", item_code, "item_group")}) %}
{% endfor %}

{% for row in doc.items %}
  <td>{{ item_groups.get(row.item_code, "") }}</td>
{% endfor %}
```

---

## Formatting Utilities

```html
<!-- Money formatting -->
{{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}

<!-- Number formatting -->
{{ frappe.utils.flt(value, 2) }}
{{ frappe.format_value(value, {"fieldtype": "Currency", "options": "currency"}) }}

<!-- Date formatting -->
{{ frappe.utils.formatdate(doc.posting_date) }}
{{ doc.posting_date | global_date_format }}
{{ frappe.utils.format_datetime(doc.creation) }}

<!-- Address formatting -->
{{ frappe.utils.get_formatted_address(frappe.get_doc("Address", doc.customer_address)) }}
```

---

## Including External Templates

```html
<!-- Include another template -->
{% include "templates/includes/my_component.html" %}

<!-- Include from app path -->
{% include "myapp/templates/print/invoice_header.html" %}

<!-- Conditional include -->
{% if doc.doctype == "Sales Invoice" %}
  {% include "myapp/templates/print/sales_header.html" %}
{% endif %}
```

---

## Complete Example: Sales Invoice Print Format

```html
<style>
  .print-format { font-family: Arial, sans-serif; font-size: 10pt; }
  .invoice-header { margin-bottom: 20px; }
  .items-table { width: 100%; border-collapse: collapse; }
  .items-table th, .items-table td { border: 1px solid #ddd; padding: 6px 8px; }
  .items-table th { background: #f5f5f5; text-align: left; }
  .text-right { text-align: right; }
  .totals { margin-top: 20px; float: right; width: 40%; }
  .totals td { padding: 4px 8px; }
</style>

{% macro money(val) %}
  {{ frappe.utils.fmt_money(val, currency=doc.currency) }}
{% endmacro %}

<div class="invoice-header">
  <h2>{{ doc.name }}</h2>
  <p>
    <strong>Customer:</strong> {{ doc.customer_name }}<br>
    <strong>Date:</strong> {{ doc.posting_date | global_date_format }}<br>
    {% if doc.po_no %}
      <strong>PO #:</strong> {{ doc.po_no }}<br>
    {% endif %}
  </p>
</div>

<table class="items-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Item</th>
      <th>Description</th>
      <th class="text-right">Qty</th>
      <th class="text-right">Rate</th>
      <th class="text-right">Amount</th>
    </tr>
  </thead>
  <tbody>
    {% for row in doc.items %}
    <tr>
      <td>{{ loop.index }}</td>
      <td>{{ row.item_name }}</td>
      <td>{{ row.description | truncate(80) | default("") }}</td>
      <td class="text-right">{{ row.qty }}</td>
      <td class="text-right">{{ money(row.rate) }}</td>
      <td class="text-right">{{ money(row.amount) }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<table class="totals">
  <tr>
    <td><strong>Net Total</strong></td>
    <td class="text-right">{{ money(doc.net_total) }}</td>
  </tr>
  {% if doc.discount_amount %}
  <tr>
    <td>Discount</td>
    <td class="text-right">-{{ money(doc.discount_amount) }}</td>
  </tr>
  {% endif %}
  {% for tax in doc.taxes %}
  <tr>
    <td>{{ tax.description }}</td>
    <td class="text-right">{{ money(tax.tax_amount) }}</td>
  </tr>
  {% endfor %}
  <tr style="border-top: 2px solid #333;">
    <td><strong>Grand Total</strong></td>
    <td class="text-right"><strong>{{ money(doc.grand_total) }}</strong></td>
  </tr>
</table>

<div style="clear: both;"></div>

{% if doc.terms %}
<div style="margin-top: 30px;">
  <h4>Terms & Conditions</h4>
  {{ doc.terms | safe }}
</div>
{% endif %}
```

---

## Registering Custom Jinja Methods & Filters

### Via hooks.py

```python
# hooks.py
jinja = {
    "methods": [
        "myapp.utils.jinja_helpers.get_barcode_svg",
        "myapp.utils.jinja_helpers.get_qr_code",
    ],
    "filters": [
        "myapp.utils.jinja_helpers.format_iban",
    ]
}
```

### Implementation

```python
# myapp/utils/jinja_helpers.py

def get_barcode_svg(value, barcode_type="Code128"):
    """Generate barcode SVG. Use in templates: {{ get_barcode_svg(doc.name) }}"""
    import barcode
    from io import BytesIO
    code = barcode.get(barcode_type, value, writer=barcode.writer.SVGWriter())
    buffer = BytesIO()
    code.write(buffer)
    return buffer.getvalue().decode()

def format_iban(value):
    """Format IBAN with spaces. Use as: {{ bank_account | format_iban }}"""
    if not value:
        return ""
    clean = value.replace(" ", "")
    return " ".join([clean[i:i+4] for i in range(0, len(clean), 4)])
```

### Usage in Print Format

```html
<!-- Method call -->
<div class="barcode">{{ get_barcode_svg(doc.name) | safe }}</div>

<!-- Filter -->
<p>Bank Account: {{ doc.bank_account | format_iban }}</p>
```
