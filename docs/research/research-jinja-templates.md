# Research Document: Jinja Templates (Fase 2.4)

> **Doel**: VerifiÃ«ren, verdiepen en actualiseren van informatie uit erpnext-vooronderzoek.md sectie 6 (Jinja Templates) voor Frappe v14/v15.

---

## Bronnen Geraadpleegd

| Bron | URL/Locatie | Type |
|------|-------------|------|
| Frappe Docs - Jinja API | docs.frappe.io/framework/user/en/api/jinja | Primair |
| Frappe Docs - Printing | docs.frappe.io/framework/v15/user/en/desk/printing | Primair |
| Frappe Docs - Portal Pages | docs.frappe.io/framework/v15/user/en/portal-pages | Primair |
| Frappe Docs - Hooks (jenv) | docs.frappe.io/framework/user/en/python-api/hooks | Primair |
| Frappe Docs - Utility Functions | docs.frappe.io/framework/v15/user/en/api/utils | Primair |
| ERPNext Docs - Email Template | docs.frappe.io/erpnext/user/manual/en/email-template | Secundair |
| ERPNext Docs - Print Format | docs.frappe.io/erpnext/user/manual/en/records-print-format | Secundair |
| ERPNext Docs - Child Table Jinja | docs.frappe.io/erpnext/user/manual/en/fetch-child-table-values-using-jinja-tags | Secundair |
| erpnext-vooronderzoek.md | Project bestand | Basis |

---

## 1. BESCHIKBARE OBJECTEN IN JINJA CONTEXT

### Print Formats Context

In Print Formats zijn de volgende objecten automatisch beschikbaar:

| Object | Type | Beschrijving |
|--------|------|--------------|
| `doc` | Document | Het document dat wordt geprint |
| `frappe` | Module | Frappe module met alle utility methods |
| `frappe.utils` | Module | Utility functies |
| `_()` | Function | Vertaalfunctie |

### Portal Pages Context

In Portal Pages (www/*.html) zijn beschikbaar:

| Object | Type | Beschrijving |
|--------|------|--------------|
| `frappe` | Module | Frappe module |
| `frappe.session` | Object | Sessie informatie |
| `frappe.session.user` | String | Huidige gebruiker |
| `frappe.form_dict` | Dict | Query parameters (bij web request) |
| `frappe.lang` | String | Huidige taal (twee-letter code) |

### Email Templates Context

In Email Templates zijn beschikbaar:

| Object | Type | Beschrijving |
|--------|------|--------------|
| `doc` | Document | Het gekoppelde document (indien aanwezig) |
| Alle velden van DocType | Veldwaarden | Direct toegankelijk via veldnaam |
| `frappe` | Module | Frappe module (beperkt) |

---

## 2. FRAPPE METHODS IN JINJA

### Formatting Methods

#### frappe.format(value, df)

Formatteert een ruwe databasewaarde naar user-presentable formaat.

```jinja
{# Basis gebruik #}
{{ frappe.format(doc.posting_date, {'fieldtype': 'Date'}) }}
{# Output: "09-08-2019" (afhankelijk van user date format) #}

{# Currency formatting #}
{{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}
{# Output: "â‚¹ 2,399.00" #}

{# Met fieldtype opties #}
{{ frappe.format(doc.amount, {'fieldtype': 'Currency', 'options': 'currency'}) }}
```

**Versie v14/v15**: Identiek.

#### frappe.format_date(date)

Formatteert datum naar human-readable long format.

```jinja
{{ frappe.format_date(doc.posting_date) }}
{# Output: "September 8, 2019" #}

{# Met custom format (v15+) #}
{{ frappe.utils.format_date(doc.posting_date, "d MMMM, YYYY") }}
{# Output: "8 September, 2019" #}
```

#### doc.get_formatted(fieldname, doc=None)

De aanbevolen manier om veldwaarden geformatteerd op te halen in print formats.

```jinja
{# Voor parent document #}
{{ doc.get_formatted("posting_date") }}
{{ doc.get_formatted("grand_total") }}

{# Voor child table rows - parent doc meegeven voor currency context #}
{% for row in doc.items %}
    {{ row.get_formatted("rate", doc) }}
    {{ row.get_formatted("amount", doc) }}
{% endfor %}
```

**BELANGRIJK**: `get_formatted()` is de beste manier voor currency en date formatting in print formats omdat het automatisch de juiste formattering en currency symbolen toepast.

### Document Methods

#### frappe.get_doc(doctype, name)

Haalt een volledig document op.

```jinja
{% set customer = frappe.get_doc("Customer", doc.customer) %}
<p>Credit Limit: {{ frappe.format(customer.credit_limit, {'fieldtype': 'Currency'}) }}</p>
<p>Territory: {{ customer.territory }}</p>
```

#### frappe.get_all(doctype, filters, fields, order_by, start, page_length, pluck)

Haalt lijst van records op.

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

#### frappe.get_list(doctype, filters, fields, ...)

Vergelijkbaar met `get_all` maar filtert records op basis van permissions van huidige gebruiker.

```jinja
{% set my_orders = frappe.get_list('Sales Order',
    filters={'customer': doc.customer},
    fields=['name', 'grand_total', 'transaction_date']) %}
```

### Database Methods

#### frappe.db.get_value(doctype, name, fieldname)

Haalt specifieke veldwaarde(n) op.

```jinja
{# Enkele waarde #}
{% set abbr = frappe.db.get_value('Company', doc.company, 'abbr') %}
<p>Company: {{ doc.company }} ({{ abbr }})</p>

{# Meerdere waarden #}
{% set title, description = frappe.db.get_value('Task', 'TASK00002', ['title', 'description']) %}
```

#### frappe.db.get_single_value(doctype, fieldname)

Haalt waarde op uit een Single DocType.

```jinja
{% set timezone = frappe.db.get_single_value('System Settings', 'time_zone') %}
<p>Server timezone: {{ timezone }}</p>
```

### System Methods

#### frappe.get_system_settings(fieldname)

Shortcut voor System Settings waarden.

```jinja
{% if frappe.get_system_settings('country') == 'India' %}
    <p>GST: {{ doc.gst_amount }}</p>
{% endif %}
```

#### frappe.get_meta(doctype)

Haalt DocType metadata op.

```jinja
{% set meta = frappe.get_meta('Task') %}
<p>Task has {{ meta.fields | length }} fields.</p>
{% if meta.get_field('status') %}
    <p>Status field exists</p>
{% endif %}
```

#### frappe.get_fullname(user=None)

Retourneert de volledige naam van een gebruiker.

```jinja
{# Huidige gebruiker #}
<p>Prepared by: {{ frappe.get_fullname() }}</p>

{# Specifieke gebruiker #}
<p>Owner: {{ frappe.get_fullname(doc.owner) }}</p>
```

### Session & Request Methods

#### frappe.session.user

Huidige ingelogde gebruiker.

```jinja
{% if frappe.session.user != 'Guest' %}
    <p>Welcome, {{ frappe.get_fullname() }}</p>
{% endif %}
```

#### frappe.session.csrf_token

CSRF token voor forms.

```jinja
<input type="hidden" name="csrf_token" value="{{ frappe.session.csrf_token }}">
```

#### frappe.form_dict

Query parameters bij web requests.

```jinja
{# URL: /page?name=John&age=30 #}
{% if frappe.form_dict %}
    <p>Name: {{ frappe.form_dict.name }}</p>
    <p>Age: {{ frappe.form_dict.age }}</p>
{% endif %}
```

### Template Methods

#### frappe.render_template(template, context)

Rendert een andere Jinja template.

```jinja
{# Render template file #}
{{ frappe.render_template('templates/includes/footer/footer.html', {}) }}

{# Render string template #}
{{ frappe.render_template('{{ foo }}', {'foo': 'bar'}) }}
{# Output: bar #}
```

#### _(string) - Vertaalfunctie

```jinja
<h1>{{ _("Invoice") }}</h1>
<p>{{ _("Thank you for your business!") }}</p>

{# Met variabelen (gebruik format na vertaling) #}
<p>{{ _("Total: {0}").format(doc.grand_total) }}</p>
```

---

## 3. PRINT FORMATS

### Types Print Formats

| Type | Beschrijving | Technologie |
|------|--------------|-------------|
| Standard | Automatisch gegenereerd | Jinja server-side |
| Print Format Builder | Drag-and-drop editor | Jinja server-side |
| Custom HTML | Volledig custom | Jinja server-side |
| Report Print Formats | Voor Query/Script Reports | JS Templating client-side |

### Print Format Structuur

**Basis HTML Print Format:**

```jinja
<style>
    .invoice-header { background: #f5f5f5; padding: 15px; }
    .text-right { text-align: right; }
    .table { width: 100%; border-collapse: collapse; }
    .table th, .table td { border: 1px solid #ddd; padding: 8px; }
</style>

<div class="invoice-header">
    <h1>{{ doc.select_print_heading or _("Invoice") }}</h1>
    <p>{{ doc.name }}</p>
</div>

<div class="row">
    <div class="col-md-6">
        <strong>{{ _("Customer") }}:</strong> {{ doc.customer_name }}
    </div>
    <div class="col-md-6 text-right">
        <strong>{{ _("Date") }}:</strong> {{ doc.get_formatted("posting_date") }}
    </div>
</div>

<table class="table">
    <thead>
        <tr>
            <th>{{ _("Sr") }}</th>
            <th>{{ _("Item") }}</th>
            <th>{{ _("Description") }}</th>
            <th class="text-right">{{ _("Qty") }}</th>
            <th class="text-right">{{ _("Rate") }}</th>
            <th class="text-right">{{ _("Amount") }}</th>
        </tr>
    </thead>
    <tbody>
        {%- for row in doc.items -%}
        <tr>
            <td>{{ row.idx }}</td>
            <td>
                {{ row.item_name }}
                {% if row.item_code != row.item_name -%}
                    <br><small>Item Code: {{ row.item_code }}</small>
                {%- endif %}
            </td>
            <td>{{ row.description }}</td>
            <td class="text-right">{{ row.qty }} {{ row.uom or row.stock_uom }}</td>
            <td class="text-right">{{ row.get_formatted("rate", doc) }}</td>
            <td class="text-right">{{ row.get_formatted("amount", doc) }}</td>
        </tr>
        {%- endfor -%}
    </tbody>
</table>

<div class="row">
    <div class="col-md-6"></div>
    <div class="col-md-6 text-right">
        <p><strong>{{ _("Net Total") }}:</strong> {{ doc.get_formatted("net_total") }}</p>
        <p><strong>{{ _("Tax") }}:</strong> {{ doc.get_formatted("total_taxes_and_charges") }}</p>
        <p><strong>{{ _("Grand Total") }}:</strong> {{ doc.get_formatted("grand_total") }}</p>
    </div>
</div>

{% if doc.terms %}
<div class="terms">
    <h4>{{ _("Terms and Conditions") }}</h4>
    {{ doc.terms }}
</div>
{% endif %}
```

### Child Table Iteratie

```jinja
{# Methode 1: Direct itereren #}
{% for item in doc.items %}
    <p>{{ item.item_name }}: {{ item.qty }}</p>
{% endfor %}

{# Methode 2: Met index #}
{% for item in doc.items %}
    <p>{{ loop.index }}. {{ item.item_name }}</p>
{% endfor %}

{# Methode 3: Als HTML tabel #}
<table>
    {% for item in doc.items %}
    <tr>
        <td>{{ item.idx }}</td>
        <td>{{ item.item_name }}</td>
        <td>{{ item.get_formatted("amount", doc) }}</td>
    </tr>
    {% endfor %}
</table>

{# Methode 4: Als ongeordende lijst #}
<ul>
    {% for item in doc.items %}
    <li>{{ item.item_name }} - Qty: {{ item.qty }}</li>
    {% endfor %}
</ul>
```

### Data Ophalen uit Ander Document

```jinja
{# Verkrijg linked document #}
{% set sales_order_doc = frappe.get_doc("Sales Order", doc.sales_order) %}
<p>Original SO Customer: {{ sales_order_doc.customer_name }}</p>
<p>SO Date: {{ frappe.format_date(sales_order_doc.transaction_date) }}</p>

{# Verkrijg specifieke velden zonder volledig document #}
{% set customer_group = frappe.db.get_value("Customer", doc.customer, "customer_group") %}
<p>Customer Group: {{ customer_group }}</p>
```

### Styling met Bootstrap

Print Formats ondersteunen Bootstrap 3 classes:

```jinja
<div class="row">
    <div class="col-md-6">Left column</div>
    <div class="col-md-6">Right column</div>
</div>

<table class="table table-bordered table-condensed">
    {# table content #}
</table>

<span class="label label-success">{{ _("Paid") }}</span>
<span class="badge">{{ doc.items | length }}</span>
```

---

## 4. EMAIL TEMPLATES

### Structuur

Email Templates gebruiken Jinja met beperkte context:

```jinja
{# Basis email template #}
<p>Dear {{ doc.customer_name }},</p>

<p>Your invoice <strong>{{ doc.name }}</strong> for {{ doc.get_formatted("grand_total") }} 
is now due for payment.</p>

<p>Invoice Date: {{ frappe.format_date(doc.posting_date) }}</p>
<p>Due Date: {{ frappe.format_date(doc.due_date) }}</p>

{% if doc.items %}
<h4>Items:</h4>
<ul>
{% for item in doc.items %}
    <li>{{ item.item_name }} - {{ item.qty }} x {{ item.get_formatted("rate", doc) }}</li>
{% endfor %}
</ul>
{% endif %}

<p>Please make payment at your earliest convenience.</p>

<p>Best regards,<br>
{{ frappe.db.get_value("Company", doc.company, "company_name") }}</p>
```

### Beschikbare Variabelen

In Email Templates (gekoppeld aan DocType):

| Variabele | Beschrijving |
|-----------|--------------|
| `doc` | Het gekoppelde document |
| `doc.fieldname` | Elk veld van het document |
| `frappe` | Frappe module (beperkt) |

### HTML vs Text

Email Templates kunnen in HTML of plain text:

```jinja
{# HTML mode (Use HTML checkbox enabled) #}
<table>
    <tr><td>Invoice:</td><td>{{ doc.name }}</td></tr>
    <tr><td>Amount:</td><td>{{ doc.get_formatted("grand_total") }}</td></tr>
</table>

{# Text mode #}
Invoice: {{ doc.name }}
Amount: {{ doc.grand_total }}
```

---

## 5. WEB TEMPLATES (Portal Pages)

### Structuur

Portal pages bevinden zich in `app/www/` folder:

```
app/
â”œâ”€â”€ www/
â”‚   â”œâ”€â”€ about.html
â”‚   â”œâ”€â”€ about.py
â”‚   â”œâ”€â”€ projects/
â”‚   â”‚   â”œâ”€â”€ index.html
â”‚   â”‚   â”œâ”€â”€ index.py
â”‚   â”‚   â””â”€â”€ project.html
â”‚   â””â”€â”€ project.py
```

### Template met Controller

**www/projects/index.html**
```jinja
{% extends "templates/web.html" %}

{% block title %}{{ _("Projects") }}{% endblock %}

{% block page_content %}
<h1>{{ _("Our Projects") }}</h1>

{% for project in projects %}
<div class="project-card">
    <h3><a href="/projects/{{ project.name }}">{{ project.title }}</a></h3>
    <p>{{ project.description }}</p>
    <span class="badge">{{ project.status }}</span>
</div>
{% endfor %}

{% if not projects %}
<p class="text-muted">{{ _("No projects found.") }}</p>
{% endif %}
{% endblock %}
```

**www/projects/index.py**
```python
import frappe

def get_context(context):
    context.projects = frappe.get_all(
        "Project",
        filters={"is_public": 1},
        fields=["name", "title", "description", "status"],
        order_by="creation desc"
    )
    return context
```

### Base Templates

Alle portal pages extenden standaard van:
- `frappe/templates/web.html` (portal base)
- `frappe/templates/base.html` (ultimate base)

```jinja
{# Expliciet extenden #}
{% extends "templates/web.html" %}

{% block title %}{{ _("My Page") }}{% endblock %}

{% block page_content %}
    {# Page content here #}
{% endblock %}

{# Of zonder extend (gebruikt default base) #}
<h1>{{ _("Simple Page") }}</h1>
<p>Content goes here</p>
```

### Beschikbare Blocks

| Block | Beschrijving |
|-------|--------------|
| `title` | Page title |
| `head_include` | Extra items in `<head>` |
| `page_content` | Hoofdcontent van pagina |
| `footer` | Footer sectie |

### Dynamic Routes

```python
# hooks.py
website_route_rules = [
    {"from_route": "/project/<name>", "to_route": "app/templates/project"},
]
```

```python
# app/templates/project.py
def get_context(context):
    project_name = frappe.form_dict.name
    context.project = frappe.get_doc("Project", project_name)
    return context
```

### Context Keys

Speciale context keys die je kunt zetten:

| Key | Type | Beschrijving |
|-----|------|--------------|
| `title` | String | Page title |
| `description` | String | Meta description |
| `image` | String | Meta image URL |
| `no_cache` | Boolean | Disable page caching |
| `sitemap` | Boolean | Include in sitemap |
| `add_breadcrumbs` | Boolean | Auto-generate breadcrumbs |
| `safe_render` | Boolean | Enable/disable safe render |

### Frontmatter

```jinja
---
title: Introduction
metatags:
  description: This is the introduction page
add_breadcrumbs: true
---

# Introduction

Content here...
```

---

## 6. CUSTOM FILTERS/METHODS (jenv Hook)

### Configuratie in hooks.py

```python
# hooks.py
jenv = {
    "methods": [
        "app.jinja.methods",           # Module path - alle functies
        "app.utils.get_fullname"       # Specifieke functie
    ],
    "filters": [
        "app.jinja.filters",
        "app.utils.format_currency"
    ]
}
```

### Methods Implementatie

```python
# app/jinja/methods.py

def sum_values(a, b):
    """Som van twee waarden"""
    return a + b

def get_company_logo(company):
    """Haal company logo URL op"""
    import frappe
    logo = frappe.db.get_value("Company", company, "company_logo")
    return logo or "/assets/app/images/default_logo.png"

def format_address(address_dict):
    """Formatteer address naar string"""
    parts = []
    if address_dict.get("address_line1"):
        parts.append(address_dict.address_line1)
    if address_dict.get("city"):
        parts.append(address_dict.city)
    if address_dict.get("country"):
        parts.append(address_dict.country)
    return ", ".join(parts)
```

### Filters Implementatie

```python
# app/jinja/filters.py

def format_currency_custom(value, currency="EUR"):
    """Custom currency formatting filter"""
    return f"{currency} {value:,.2f}"

def truncate_text(text, length=100):
    """Truncate text met ellipsis"""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'

def nl2br(text):
    """Convert newlines naar <br> tags"""
    if not text:
        return ""
    return text.replace('\n', '<br>')
```

### Gebruik in Templates

```jinja
{# Methods #}
<p>Sum: {{ sum_values(10, 20) }}</p>
<img src="{{ get_company_logo(doc.company) }}">
<p>{{ format_address(address) }}</p>

{# Filters #}
<p>{{ doc.grand_total | format_currency_custom("USD") }}</p>
<p>{{ doc.description | truncate_text(50) }}</p>
<p>{{ doc.notes | nl2br }}</p>
```

---

## 7. STANDARD JINJA FILTERS & FUNCTIONS

### Ingebouwde Jinja2 Filters

Deze standaard Jinja2 filters zijn beschikbaar:

| Filter | Voorbeeld | Beschrijving |
|--------|-----------|--------------|
| `length` / `len` | `{{ items \| length }}` | Aantal items |
| `default` | `{{ value \| default('N/A') }}` | Default waarde |
| `first` | `{{ items \| first }}` | Eerste item |
| `last` | `{{ items \| last }}` | Laatste item |
| `join` | `{{ items \| join(', ') }}` | Join list naar string |
| `lower` | `{{ text \| lower }}` | Lowercase |
| `upper` | `{{ text \| upper }}` | Uppercase |
| `title` | `{{ text \| title }}` | Title Case |
| `trim` | `{{ text \| trim }}` | Strip whitespace |
| `round` | `{{ number \| round(2) }}` | Afronden |
| `int` | `{{ value \| int }}` | Convert naar integer |
| `float` | `{{ value \| float }}` | Convert naar float |
| `safe` | `{{ html \| safe }}` | Render als HTML |
| `escape` | `{{ text \| escape }}` | HTML escape |

### Jinja Control Structures

```jinja
{# If/Elif/Else #}
{% if doc.status == "Paid" %}
    <span class="label label-success">Paid</span>
{% elif doc.status == "Overdue" %}
    <span class="label label-danger">Overdue</span>
{% else %}
    <span class="label label-default">{{ doc.status }}</span>
{% endif %}

{# For Loop #}
{% for item in doc.items %}
    <p>{{ loop.index }}. {{ item.item_name }}</p>
{% else %}
    <p>No items found</p>
{% endfor %}

{# Loop Variables #}
{% for item in doc.items %}
    {{ loop.index }}      {# 1-indexed #}
    {{ loop.index0 }}     {# 0-indexed #}
    {{ loop.first }}      {# True if first iteration #}
    {{ loop.last }}       {# True if last iteration #}
    {{ loop.length }}     {# Total items #}
{% endfor %}

{# Set Variables #}
{% set total = 0 %}
{% for item in doc.items %}
    {% set total = total + item.amount %}
{% endfor %}
<p>Total: {{ total }}</p>

{# With Statement (scoped variables) #}
{% with subtotal = doc.net_total, tax = doc.total_taxes_and_charges %}
    <p>Subtotal: {{ subtotal }}</p>
    <p>Tax: {{ tax }}</p>
    <p>Total: {{ subtotal + tax }}</p>
{% endwith %}
```

---

## 8. SECURITY & BEST PRACTICES

### Safe Render

Frappe blokkeert standaard templates met `.__` om code injection te voorkomen:

```python
# In controller
def get_context(context):
    context.safe_render = False  # Uitschakelen (alleen indien zeker veilig)
```

### Input Escaping

```jinja
{# Automatisch escaped (veilig) #}
{{ user_input }}

{# Als HTML renderen (alleen voor vertrouwde content) #}
{{ trusted_html | safe }}

{# Expliciet escapen #}
{{ potentially_unsafe | escape }}
```

### Performance

```jinja
{# âŒ VERMIJD - Query in loop #}
{% for item in doc.items %}
    {% set item_doc = frappe.get_doc("Item", item.item_code) %}
    {{ item_doc.item_group }}
{% endfor %}

{# âœ… BETER - Batch ophalen in controller #}
{# In Python: context.item_groups = get_item_groups(doc.items) #}
{% for item in doc.items %}
    {{ item_groups.get(item.item_code, '') }}
{% endfor %}
```

### Caching

```python
# In controller voor portal pages
def get_context(context):
    context.no_cache = True  # Disable caching voor dynamische content
```

---

## 9. REPORT PRINT FORMATS (Client-Side)

**BELANGRIJK**: Report Print Formats voor Query en Script Reports gebruiken GEEN Jinja, maar JavaScript templating (John Resig's Microtemplate).

### Syntax Verschillen

| Aspect | Jinja (Server) | JS Template (Client) |
|--------|----------------|---------------------|
| Code blocks | `{% %}` | `{% %}` |
| Output | `{{ }}` | `{%= %}` |
| Taal | Python | JavaScript |
| Beschikbaar | Print Formats, Portal | Report Print Formats |

### JS Template Voorbeeld

```html
{% for(var i=0, l=data.length; i<l; i++) { %}
<tr>
    {% if(data[i].posting_date) { %}
        <td>{%= frappe.datetime.str_to_user(data[i].posting_date) %}</td>
        <td>{%= data[i].remarks %}</td>
    {% } %}
</tr>
{% } %}
```

**WAARSCHUWING**: Gebruik GEEN single quotes `'` in JS templates.

---

## 10. VERSIE VERSCHILLEN (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| Basis Jinja API | âœ… | âœ… |
| frappe.utils.format_date | âœ… | âœ… Met extra format opties |
| get_formatted() | âœ… | âœ… |
| jenv hook | âœ… | âœ… |
| Safe render | âœ… | âœ… |
| Portal pages | âœ… | âœ… |

---

## 11. ANTI-PATTERNS

### âŒ Query in Loop

```jinja
{# FOUT - N+1 queries #}
{% for item in doc.items %}
    {% set stock = frappe.db.get_value("Bin", {"item_code": item.item_code}, "actual_qty") %}
{% endfor %}
```

### âŒ Zware Berekeningen in Template

```jinja
{# FOUT - Doe berekeningen in controller #}
{% set complex_total = 0 %}
{% for item in doc.items %}
    {% set item_total = item.qty * item.rate * (1 - item.discount/100) %}
    {% set complex_total = complex_total + item_total %}
{% endfor %}
```

### âŒ OngeÃ«scapete User Input

```jinja
{# FOUT - XSS risico #}
{{ user_comment | safe }}

{# GOED - Alleen voor vertrouwde content #}
{{ doc.terms | safe }}  {# Alleen als terms van admin komt #}
```

### âŒ Hardcoded Strings (niet vertaalbaar)

```jinja
{# FOUT #}
<th>Invoice Number</th>

{# GOED #}
<th>{{ _("Invoice Number") }}</th>
```

---

## Samenvatting voor Skill Creatie

### Key Learnings

1. **doc.get_formatted()** is de aanbevolen methode voor veld formatting in print formats
2. **frappe.format()** voor algemene value formatting met fieldtype specificatie  
3. **jenv hook** voor custom methods en filters toevoegen
4. **Portal Pages** gebruiken Python controllers voor context
5. **Report Print Formats** gebruiken JS templating, NIET Jinja
6. **Safe render** beschermt tegen code injection
7. **Vertaling** via `_()` functie voor alle user-facing strings

### Skill References te Maken

1. `available-objects.md` - Alle beschikbare objecten per context
2. `methods.md` - Alle frappe.* methods met signatures  
3. `print-formats.md` - Print format patterns en voorbeelden
4. `email-templates.md` - Email template patterns
5. `portal-pages.md` - Web template patterns met controllers
6. `custom-jenv.md` - Custom methods/filters via hooks
7. `examples.md` - Complete werkende voorbeelden
8. `anti-patterns.md` - Wat te vermijden
