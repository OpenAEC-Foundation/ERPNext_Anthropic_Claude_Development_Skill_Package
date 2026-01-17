---
name: erpnext-syntax-jinja
version: 1.0.0
description: Deterministische Jinja template syntax voor ERPNext/Frappe Print Formats, Email Templates en Portal Pages
author: OpenAEC Foundation
tags: [erpnext, frappe, jinja, templates, print-formats, email-templates, portal-pages]
languages: [nl]
frappe_versions: [v14, v15]
---

# ERPNext Jinja Templates Syntax Skill

> Correcte Jinja syntax voor Print Formats, Email Templates en Portal Pages in ERPNext/Frappe v14/v15.

---

## Wanneer Deze Skill Gebruiken

GEBRUIK deze skill wanneer je:
- Print Formats maakt of aanpast
- Email Templates ontwikkelt
- Portal Pages (www/*.html) bouwt
- Custom Jinja filters/methods toevoegt via hooks

GEBRUIK NIET voor:
- Report Print Formats (die gebruiken JavaScript templating, niet Jinja)
- Client Scripts (gebruik erpnext-syntax-clientscripts)
- Server Scripts (gebruik erpnext-syntax-serverscripts)

---

## Context Objecten per Template Type

### Print Formats

| Object | Beschrijving |
|--------|--------------|
| `doc` | Het document dat wordt geprint |
| `frappe` | Frappe module met utility methods |
| `_()` | Vertaalfunctie |

### Email Templates

| Object | Beschrijving |
|--------|--------------|
| `doc` | Het gekoppelde document |
| `frappe` | Frappe module (beperkt) |

### Portal Pages

| Object | Beschrijving |
|--------|--------------|
| `frappe.session.user` | Huidige gebruiker |
| `frappe.form_dict` | Query parameters |
| `frappe.lang` | Huidige taal |
| Custom context | Via Python controller |

> **Zie**: `references/context-objects.md` voor complete details.

---

## Essentiële Methods

### Formatting (ALTIJD gebruiken)

```jinja
{# AANBEVOLEN voor velden in print formats #}
{{ doc.get_formatted("posting_date") }}
{{ doc.get_formatted("grand_total") }}

{# Voor child table rows - parent doc meegeven #}
{% for row in doc.items %}
    {{ row.get_formatted("rate", doc) }}
    {{ row.get_formatted("amount", doc) }}
{% endfor %}

{# Algemene formatting #}
{{ frappe.format(value, {'fieldtype': 'Currency'}) }}
{{ frappe.format_date(doc.posting_date) }}
```

### Document Ophalen

```jinja
{# Volledig document #}
{% set customer = frappe.get_doc("Customer", doc.customer) %}

{# Specifieke veldwaarde (efficiënter) #}
{% set abbr = frappe.db.get_value("Company", doc.company, "abbr") %}

{# Lijst van records #}
{% set tasks = frappe.get_all('Task', 
    filters={'status': 'Open'}, 
    fields=['title', 'due_date']) %}
```

### Vertaling (VERPLICHT voor user-facing strings)

```jinja
<h1>{{ _("Invoice") }}</h1>
<p>{{ _("Total: {0}").format(doc.grand_total) }}</p>
```

> **Zie**: `references/methods-reference.md` voor alle methods.

---

## Control Structures

### Conditionals

```jinja
{% if doc.status == "Paid" %}
    <span class="label-success">{{ _("Paid") }}</span>
{% elif doc.status == "Overdue" %}
    <span class="label-danger">{{ _("Overdue") }}</span>
{% else %}
    <span>{{ doc.status }}</span>
{% endif %}
```

### Loops

```jinja
{% for item in doc.items %}
    <tr>
        <td>{{ loop.index }}</td>
        <td>{{ item.item_name }}</td>
        <td>{{ item.get_formatted("amount", doc) }}</td>
    </tr>
{% else %}
    <tr><td colspan="3">{{ _("No items") }}</td></tr>
{% endfor %}
```

### Loop Variables

| Variable | Beschrijving |
|----------|--------------|
| `loop.index` | 1-indexed positie |
| `loop.first` | True bij eerste |
| `loop.last` | True bij laatste |
| `loop.length` | Totaal items |

### Variables

```jinja
{% set total = 0 %}
{% set customer_name = doc.customer_name | default('Unknown') %}
```

---

## Filters

### Veelgebruikt

| Filter | Voorbeeld |
|--------|-----------|
| `default` | `{{ value \| default('N/A') }}` |
| `length` | `{{ items \| length }}` |
| `join` | `{{ names \| join(', ') }}` |
| `truncate` | `{{ text \| truncate(100) }}` |
| `safe` | `{{ html \| safe }}` (alleen vertrouwde content!) |

> **Zie**: `references/filters-reference.md` voor alle filters.

---

## Print Format Template

```jinja
<style>
    .header { background: #f5f5f5; padding: 15px; }
    .table { width: 100%; border-collapse: collapse; }
    .table th, .table td { border: 1px solid #ddd; padding: 8px; }
    .text-right { text-align: right; }
</style>

<div class="header">
    <h1>{{ doc.select_print_heading or _("Invoice") }}</h1>
    <p>{{ doc.name }}</p>
    <p>{{ _("Date") }}: {{ doc.get_formatted("posting_date") }}</p>
</div>

<table class="table">
    <thead>
        <tr>
            <th>{{ _("Item") }}</th>
            <th class="text-right">{{ _("Qty") }}</th>
            <th class="text-right">{{ _("Amount") }}</th>
        </tr>
    </thead>
    <tbody>
        {% for row in doc.items %}
        <tr>
            <td>{{ row.item_name }}</td>
            <td class="text-right">{{ row.qty }}</td>
            <td class="text-right">{{ row.get_formatted("amount", doc) }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<p><strong>{{ _("Grand Total") }}:</strong> {{ doc.get_formatted("grand_total") }}</p>
```

---

## Email Template

```jinja
<p>{{ _("Dear") }} {{ doc.customer_name }},</p>

<p>{{ _("Invoice") }} <strong>{{ doc.name }}</strong> {{ _("for") }} 
{{ doc.get_formatted("grand_total") }} {{ _("is due.") }}</p>

<p>{{ _("Due Date") }}: {{ frappe.format_date(doc.due_date) }}</p>

{% if doc.items %}
<ul>
{% for item in doc.items %}
    <li>{{ item.item_name }} - {{ item.qty }} x {{ item.get_formatted("rate", doc) }}</li>
{% endfor %}
</ul>
{% endif %}

<p>{{ _("Best regards") }},<br>
{{ frappe.db.get_value("Company", doc.company, "company_name") }}</p>
```

---

## Portal Page met Controller

### www/projects/index.html

```jinja
{% extends "templates/web.html" %}

{% block title %}{{ _("Projects") }}{% endblock %}

{% block page_content %}
<h1>{{ _("Projects") }}</h1>

{% if frappe.session.user != 'Guest' %}
    <p>{{ _("Welcome") }}, {{ frappe.get_fullname() }}</p>
{% endif %}

{% for project in projects %}
    <div class="project">
        <h3>{{ project.title }}</h3>
        <p>{{ project.description | truncate(150) }}</p>
    </div>
{% else %}
    <p>{{ _("No projects found.") }}</p>
{% endfor %}
{% endblock %}
```

### www/projects/index.py

```python
import frappe

def get_context(context):
    context.title = "Projects"
    context.projects = frappe.get_all(
        "Project",
        filters={"is_public": 1},
        fields=["name", "title", "description"],
        order_by="creation desc"
    )
    return context
```

---

## Custom Filters/Methods via jenv Hook

### hooks.py

```python
jenv = {
    "methods": ["myapp.jinja.methods"],
    "filters": ["myapp.jinja.filters"]
}
```

### myapp/jinja/methods.py

```python
import frappe

def get_company_logo(company):
    """Haal company logo URL op"""
    return frappe.db.get_value("Company", company, "company_logo") or ""
```

### Gebruik

```jinja
<img src="{{ get_company_logo(doc.company) }}">
```

---

## Kritieke Regels

### ✅ ALTIJD

1. `_()` gebruiken voor alle user-facing strings
2. `get_formatted()` gebruiken voor currency/date velden
3. Default values gebruiken: `{{ value | default('') }}`
4. Child table rows: `row.get_formatted("field", doc)`

### ❌ NOOIT

1. Queries in loops uitvoeren (N+1 probleem)
2. `| safe` gebruiken voor user input (XSS risico)
3. Zware berekeningen in templates (doe in Python)
4. Jinja syntax in Report Print Formats (die gebruiken JS)

---

## Report Print Formats (NIET Jinja!)

**WAARSCHUWING**: Report Print Formats voor Query/Script Reports gebruiken JavaScript templating.

| Aspect | Jinja (Print Formats) | JS (Report Print Formats) |
|--------|----------------------|---------------------------|
| Output | `{{ }}` | `{%= %}` |
| Code | `{% %}` | `{% %}` |
| Taal | Python | JavaScript |

```html
<!-- JS Template voor Reports -->
{% for(var i=0; i<data.length; i++) { %}
<tr><td>{%= data[i].name %}</td></tr>
{% } %}
```

---

## Versie Compatibiliteit

| Feature | v14 | v15 |
|---------|:---:|:---:|
| Basis Jinja API | ✅ | ✅ |
| get_formatted() | ✅ | ✅ |
| jenv hook | ✅ | ✅ |
| Portal pages | ✅ | ✅ |
| frappe.utils.format_date met format | ✅ | ✅+ |

---

## Reference Files

| Bestand | Inhoud |
|---------|--------|
| `references/context-objects.md` | Beschikbare objecten per template type |
| `references/methods-reference.md` | Alle frappe.* methods |
| `references/filters-reference.md` | Standaard en custom filters |
| `references/examples.md` | Complete werkende voorbeelden |
| `references/anti-patterns.md` | Fouten te vermijden |

---

## Zie Ook

- `erpnext-syntax-hooks` - Voor jenv configuratie in hooks.py
- `erpnext-impl-jinja` - Voor implementatie patronen
- `erpnext-errors-jinja` - Voor foutafhandeling
