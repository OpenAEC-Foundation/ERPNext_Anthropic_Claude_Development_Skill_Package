# Frappe Methods Reference voor Jinja

> Alle beschikbare frappe.* methods in Jinja templates (v14/v15).

---

## Formatting Methods

### frappe.format(value, df)

Formatteert een ruwe databasewaarde naar user-presentable formaat.

```jinja
{# Basis gebruik #}
{{ frappe.format(doc.posting_date, {'fieldtype': 'Date'}) }}
{# Output: "09-08-2019" #}

{# Currency formatting #}
{{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}
{# Output: "€ 2,399.00" #}

{# Met options #}
{{ frappe.format(doc.amount, {'fieldtype': 'Currency', 'options': 'currency'}) }}
```

### frappe.format_date(date)

Formatteert datum naar human-readable long format.

```jinja
{{ frappe.format_date(doc.posting_date) }}
{# Output: "September 8, 2019" #}

{# v15+ met custom format #}
{{ frappe.utils.format_date(doc.posting_date, "d MMMM, YYYY") }}
{# Output: "8 September, 2019" #}
```

### doc.get_formatted(fieldname, doc=None)

**AANBEVOLEN** voor veld formatting in print formats.

```jinja
{# Parent document velden #}
{{ doc.get_formatted("posting_date") }}
{{ doc.get_formatted("grand_total") }}

{# Child table rows - parent doc meegeven voor currency context #}
{% for row in doc.items %}
    {{ row.get_formatted("rate", doc) }}
    {{ row.get_formatted("amount", doc) }}
{% endfor %}
```

---

## Document Methods

### frappe.get_doc(doctype, name)

Haalt een volledig document op.

```jinja
{% set customer = frappe.get_doc("Customer", doc.customer) %}
<p>Credit Limit: {{ frappe.format(customer.credit_limit, {'fieldtype': 'Currency'}) }}</p>
<p>Territory: {{ customer.territory }}</p>
```

### frappe.get_all(doctype, filters, fields, order_by, limit_page_length)

Haalt lijst van records op (geen permission check).

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

Vergelijkbaar met `get_all` maar filtert op permissions van huidige gebruiker.

```jinja
{% set my_orders = frappe.get_list('Sales Order',
    filters={'customer': doc.customer},
    fields=['name', 'grand_total', 'transaction_date']) %}
```

---

## Database Methods

### frappe.db.get_value(doctype, name, fieldname)

Haalt specifieke veldwaarde(n) op.

```jinja
{# Enkele waarde #}
{% set abbr = frappe.db.get_value('Company', doc.company, 'abbr') %}
<p>Company: {{ doc.company }} ({{ abbr }})</p>

{# Meerdere waarden #}
{% set title, description = frappe.db.get_value('Task', 'TASK00002', ['title', 'description']) %}
```

### frappe.db.get_single_value(doctype, fieldname)

Haalt waarde op uit een Single DocType.

```jinja
{% set timezone = frappe.db.get_single_value('System Settings', 'time_zone') %}
<p>Server timezone: {{ timezone }}</p>
```

---

## System Methods

### frappe.get_system_settings(fieldname)

Shortcut voor System Settings waarden.

```jinja
{% if frappe.get_system_settings('country') == 'India' %}
    <p>GST: {{ doc.gst_amount }}</p>
{% endif %}
```

### frappe.get_meta(doctype)

Haalt DocType metadata op.

```jinja
{% set meta = frappe.get_meta('Task') %}
<p>Task has {{ meta.fields | length }} fields.</p>
{% if meta.get_field('status') %}
    <p>Status field exists</p>
{% endif %}
```

### frappe.get_fullname(user=None)

Retourneert de volledige naam van een gebruiker.

```jinja
{# Huidige gebruiker #}
<p>Prepared by: {{ frappe.get_fullname() }}</p>

{# Specifieke gebruiker #}
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

Query parameters bij web requests.

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

Rendert een andere Jinja template.

```jinja
{# Render template file #}
{{ frappe.render_template('templates/includes/footer/footer.html', {}) }}

{# Render string template #}
{{ frappe.render_template('{{ foo }}', {'foo': 'bar'}) }}
{# Output: bar #}
```

### _(string) - Vertaalfunctie

```jinja
<h1>{{ _("Invoice") }}</h1>
<p>{{ _("Thank you for your business!") }}</p>

{# Met variabelen #}
<p>{{ _("Total: {0}").format(doc.grand_total) }}</p>
```
