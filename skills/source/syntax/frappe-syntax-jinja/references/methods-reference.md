# Frappe Methods Reference for Jinja

> All available frappe.* methods in Jinja templates (v14/v15).

---

## Formatting Methods

### frappe.format(value, df)

Formats a raw database value to user-presentable format.

```jinja
{# Basic usage #}
{{ frappe.format(doc.posting_date, {'fieldtype': 'Date'}) }}
{# Output: "09-08-2019" #}

{# Currency formatting #}
{{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}
{# Output: "€ 2,399.00" #}

{# With options #}
{{ frappe.format(doc.amount, {'fieldtype': 'Currency', 'options': 'currency'}) }}
```

### frappe.format_date(date)

Formats date to human-readable long format.

```jinja
{{ frappe.format_date(doc.posting_date) }}
{# Output: "September 8, 2019" #}

{# v15+ with custom format #}
{{ frappe.utils.format_date(doc.posting_date, "d MMMM, YYYY") }}
{# Output: "8 September, 2019" #}
```

### doc.get_formatted(fieldname, doc=None)

**RECOMMENDED** for field formatting in print formats.

```jinja
{# Parent document fields #}
{{ doc.get_formatted("posting_date") }}
{{ doc.get_formatted("grand_total") }}

{# Child table rows - pass parent doc for currency context #}
{% for row in doc.items %}
    {{ row.get_formatted("rate", doc) }}
    {{ row.get_formatted("amount", doc) }}
{% endfor %}
```

---

## Document Methods

### frappe.get_doc(doctype, name)

Retrieves a complete document.

```jinja
{% set customer = frappe.get_doc("Customer", doc.customer) %}
<p>Credit Limit: {{ frappe.format(customer.credit_limit, {'fieldtype': 'Currency'}) }}</p>
<p>Territory: {{ customer.territory }}</p>
```

### frappe.get_all(doctype, filters, fields, order_by, limit_page_length)

Retrieves list of records (no permission check).

```jinja
{% set tasks = frappe.get_all('Task', 
    filters={'status': 'Open'}, 
    fields=['title', 'due_date'], 
    order_by='due_date asc',
    limit_page_length=10) %}

{% for task in tasks %}
<div>
    <h3>{{ task.title }}</h3>
    <p>Due: {{ frappe.format_date(task.due_date) }}</p>
</div>
{% endfor %}
```

### frappe.get_list(doctype, filters, fields, ...)

Similar to `get_all` but filters based on current user's permissions.

```jinja
{% set my_orders = frappe.get_list('Sales Order',
    filters={'customer': doc.customer},
    fields=['name', 'grand_total', 'transaction_date']) %}
```

---

## Database Methods

### frappe.db.get_value(doctype, name, fieldname)

Retrieves specific field value(s).

```jinja
{# Single value #}
{% set abbr = frappe.db.get_value('Company', doc.company, 'abbr') %}
<p>Company: {{ doc.company }} ({{ abbr }})</p>

{# Multiple values #}
{% set title, description = frappe.db.get_value('Task', 'TASK00002', ['title', 'description']) %}
```

### frappe.db.get_single_value(doctype, fieldname)

Retrieves value from a Single DocType.

```jinja
{% set timezone = frappe.db.get_single_value('System Settings', 'time_zone') %}
<p>Server timezone: {{ timezone }}</p>
```

---

## System Methods

### frappe.get_system_settings(fieldname)

Shortcut for System Settings values.

```jinja
{% if frappe.get_system_settings('country') == 'India' %}
    <p>GST: {{ doc.gst_amount }}</p>
{% endif %}
```

### frappe.get_meta(doctype)

Retrieves DocType metadata.

```jinja
{% set meta = frappe.get_meta('Task') %}
<p>Task has {{ meta.fields | length }} fields.</p>
{% if meta.get_field('status') %}
    <p>Status field exists</p>
{% endif %}
```

### frappe.get_fullname(user=None)

Returns the full name of a user.

```jinja
{# Current user #}
<p>Prepared by: {{ frappe.get_fullname() }}</p>

{# Specific user #}
<p>Owner: {{ frappe.get_fullname(doc.owner) }}</p>
```

---

## Session & Request Methods

### frappe.session.user

```jinja
{% if frappe.session.user != 'Guest' %}
    <p>Welcome, {{ frappe.get_fullname() }}</p>
{% endif %}
```

### frappe.session.csrf_token

```jinja
<input type="hidden" name="csrf_token" value="{{ frappe.session.csrf_token }}">
```

### frappe.form_dict

Query parameters for web requests.

```jinja
{# URL: /page?name=John&age=30 #}
{% if frappe.form_dict %}
    <p>Name: {{ frappe.form_dict.name }}</p>
    <p>Age: {{ frappe.form_dict.age }}</p>
{% endif %}
```

---

## Template Methods

### frappe.render_template(template, context)

Renders another Jinja template.

```jinja
{# Render template file #}
{{ frappe.render_template('templates/includes/footer/footer.html', {}) }}

{# Render string template #}
{{ frappe.render_template('{{ foo }}', {'foo': 'bar'}) }}
{# Output: bar #}
```

### _(string) - Translation Function

```jinja
<h1>{{ _("Invoice") }}</h1>
<p>{{ _("Thank you for your business!") }}</p>

{# With variables #}
<p>{{ _("Total: {0}").format(doc.grand_total) }}</p>
```
