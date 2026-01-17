# Complete Jinja Voorbeelden

> Werkende voorbeelden voor Print Formats, Email Templates en Portal Pages.

---

## Print Format: Sales Invoice

```jinja
<style>
    .invoice-header { background: #f5f5f5; padding: 15px; margin-bottom: 20px; }
    .text-right { text-align: right; }
    .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    .table th, .table td { border: 1px solid #ddd; padding: 8px; }
    .table th { background: #f9f9f9; }
    .totals { margin-top: 20px; }
    .terms { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }
</style>

<div class="invoice-header">
    <div class="row">
        <div class="col-md-6">
            <h1>{{ doc.select_print_heading or _("Invoice") }}</h1>
            <p><strong>{{ doc.name }}</strong></p>
        </div>
        <div class="col-md-6 text-right">
            <p><strong>{{ _("Date") }}:</strong> {{ doc.get_formatted("posting_date") }}</p>
            <p><strong>{{ _("Due Date") }}:</strong> {{ doc.get_formatted("due_date") }}</p>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <h4>{{ _("Bill To") }}</h4>
        <p><strong>{{ doc.customer_name }}</strong></p>
        {% if doc.customer_address %}
            {{ doc.address_display or '' }}
        {% endif %}
    </div>
    <div class="col-md-6 text-right">
        {% set company_address = frappe.db.get_value("Company", doc.company, "company_name") %}
        <h4>{{ _("From") }}</h4>
        <p><strong>{{ company_address }}</strong></p>
    </div>
</div>

<table class="table">
    <thead>
        <tr>
            <th style="width: 5%">{{ _("Sr") }}</th>
            <th style="width: 35%">{{ _("Item") }}</th>
            <th style="width: 25%">{{ _("Description") }}</th>
            <th class="text-right" style="width: 10%">{{ _("Qty") }}</th>
            <th class="text-right" style="width: 12%">{{ _("Rate") }}</th>
            <th class="text-right" style="width: 13%">{{ _("Amount") }}</th>
        </tr>
    </thead>
    <tbody>
        {%- for row in doc.items -%}
        <tr>
            <td>{{ row.idx }}</td>
            <td>
                {{ row.item_name }}
                {% if row.item_code != row.item_name -%}
                    <br><small>{{ _("Item Code") }}: {{ row.item_code }}</small>
                {%- endif %}
            </td>
            <td>{{ row.description | truncate(100) if row.description else '' }}</td>
            <td class="text-right">{{ row.qty }} {{ row.uom or row.stock_uom }}</td>
            <td class="text-right">{{ row.get_formatted("rate", doc) }}</td>
            <td class="text-right">{{ row.get_formatted("amount", doc) }}</td>
        </tr>
        {%- endfor -%}
    </tbody>
</table>

<div class="row totals">
    <div class="col-md-6"></div>
    <div class="col-md-6">
        <table class="table">
            <tr>
                <td><strong>{{ _("Net Total") }}</strong></td>
                <td class="text-right">{{ doc.get_formatted("net_total") }}</td>
            </tr>
            {% if doc.total_taxes_and_charges %}
            <tr>
                <td><strong>{{ _("Taxes") }}</strong></td>
                <td class="text-right">{{ doc.get_formatted("total_taxes_and_charges") }}</td>
            </tr>
            {% endif %}
            {% if doc.discount_amount %}
            <tr>
                <td><strong>{{ _("Discount") }}</strong></td>
                <td class="text-right">-{{ doc.get_formatted("discount_amount") }}</td>
            </tr>
            {% endif %}
            <tr style="font-size: 1.2em;">
                <td><strong>{{ _("Grand Total") }}</strong></td>
                <td class="text-right"><strong>{{ doc.get_formatted("grand_total") }}</strong></td>
            </tr>
        </table>
    </div>
</div>

{% if doc.terms %}
<div class="terms">
    <h4>{{ _("Terms and Conditions") }}</h4>
    {{ doc.terms }}
</div>
{% endif %}

<div class="row" style="margin-top: 50px;">
    <div class="col-md-6">
        <p>{{ _("Prepared by") }}: {{ frappe.get_fullname(doc.owner) }}</p>
    </div>
    <div class="col-md-6 text-right">
        <p>{{ _("Printed on") }}: {{ frappe.format_date(frappe.utils.nowdate()) }}</p>
    </div>
</div>
```

---

## Email Template: Payment Reminder

```jinja
<p>{{ _("Dear") }} {{ doc.customer_name }},</p>

<p>{{ _("This is a friendly reminder that invoice") }} <strong>{{ doc.name }}</strong> 
{{ _("for") }} {{ doc.get_formatted("grand_total") }} {{ _("is now due for payment.") }}</p>

<table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
    <tr>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>{{ _("Invoice Number") }}</strong></td>
        <td style="padding: 8px; border: 1px solid #ddd;">{{ doc.name }}</td>
    </tr>
    <tr>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>{{ _("Invoice Date") }}</strong></td>
        <td style="padding: 8px; border: 1px solid #ddd;">{{ frappe.format_date(doc.posting_date) }}</td>
    </tr>
    <tr>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>{{ _("Due Date") }}</strong></td>
        <td style="padding: 8px; border: 1px solid #ddd;">{{ frappe.format_date(doc.due_date) }}</td>
    </tr>
    <tr>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>{{ _("Amount Due") }}</strong></td>
        <td style="padding: 8px; border: 1px solid #ddd;"><strong>{{ doc.get_formatted("outstanding_amount") }}</strong></td>
    </tr>
</table>

{% if doc.items %}
<p><strong>{{ _("Items") }}:</strong></p>
<ul>
{% for item in doc.items %}
    <li>{{ item.item_name }} - {{ item.qty }} x {{ item.get_formatted("rate", doc) }}</li>
{% endfor %}
</ul>
{% endif %}

<p>{{ _("Please make payment at your earliest convenience.") }}</p>

<p>{{ _("Best regards") }},<br>
{{ frappe.db.get_value("Company", doc.company, "company_name") }}</p>
```

---

## Portal Page: Project List

### www/projects/index.html

```jinja
{% extends "templates/web.html" %}

{% block title %}{{ _("Projects") }}{% endblock %}

{% block page_content %}
<div class="container">
    <h1>{{ _("Our Projects") }}</h1>
    
    {% if frappe.session.user != 'Guest' %}
        <p class="text-muted">{{ _("Welcome") }}, {{ frappe.get_fullname() }}</p>
    {% endif %}
    
    <div class="row">
        {% for project in projects %}
        <div class="col-md-4" style="margin-bottom: 20px;">
            <div class="card" style="padding: 15px; border: 1px solid #ddd; border-radius: 4px;">
                <h3><a href="/projects/{{ project.name }}">{{ project.title }}</a></h3>
                <p>{{ project.description | truncate(150) if project.description else '' }}</p>
                <p>
                    <span class="label label-{% if project.status == 'Open' %}primary{% elif project.status == 'Completed' %}success{% else %}default{% endif %}">
                        {{ project.status }}
                    </span>
                </p>
                <p class="text-muted">
                    <small>{{ _("Started") }}: {{ frappe.format_date(project.expected_start_date) }}</small>
                </p>
            </div>
        </div>
        {% else %}
        <div class="col-md-12">
            <p class="text-muted">{{ _("No projects found.") }}</p>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
```

### www/projects/index.py

```python
import frappe

def get_context(context):
    context.title = "Projects"
    context.no_cache = True
    
    context.projects = frappe.get_all(
        "Project",
        filters={"is_public": 1},
        fields=[
            "name", 
            "title", 
            "description", 
            "status",
            "expected_start_date"
        ],
        order_by="creation desc"
    )
    
    return context
```

---

## Custom jenv Methods

### hooks.py

```python
jenv = {
    "methods": [
        "myapp.jinja.methods"
    ],
    "filters": [
        "myapp.jinja.filters"
    ]
}
```

### myapp/jinja/methods.py

```python
import frappe

def get_company_logo(company):
    """Haal company logo URL op"""
    logo = frappe.db.get_value("Company", company, "company_logo")
    return logo or "/assets/myapp/images/default_logo.png"

def get_outstanding_invoices(customer, limit=5):
    """Haal openstaande facturen op voor een klant"""
    return frappe.get_all(
        "Sales Invoice",
        filters={
            "customer": customer,
            "docstatus": 1,
            "outstanding_amount": [">", 0]
        },
        fields=["name", "posting_date", "grand_total", "outstanding_amount"],
        order_by="posting_date desc",
        limit_page_length=limit
    )

def format_address(address_name):
    """Formatteer een Address document naar string"""
    if not address_name:
        return ""
    
    address = frappe.get_doc("Address", address_name)
    parts = []
    
    if address.address_line1:
        parts.append(address.address_line1)
    if address.address_line2:
        parts.append(address.address_line2)
    if address.city:
        parts.append(address.city)
    if address.pincode:
        parts.append(address.pincode)
    if address.country:
        parts.append(address.country)
    
    return ", ".join(parts)
```

### myapp/jinja/filters.py

```python
def currency_words(amount, currency="EUR"):
    """Convert bedrag naar woorden"""
    # Simplified implementation
    return f"{currency} {amount:,.2f}"

def phone_format(phone):
    """Formatteer telefoonnummer"""
    if not phone:
        return ""
    # Remove non-digits
    digits = ''.join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone
```

### Gebruik in Templates

```jinja
{# Custom methods #}
<img src="{{ get_company_logo(doc.company) }}" alt="Logo">

{% set invoices = get_outstanding_invoices(doc.customer) %}
{% for inv in invoices %}
    <p>{{ inv.name }}: {{ inv.outstanding_amount }}</p>
{% endfor %}

<p>{{ format_address(doc.customer_address) }}</p>

{# Custom filters #}
<p>{{ doc.grand_total | currency_words }}</p>
<p>{{ doc.phone | phone_format }}</p>
```
