# Context Objects Reference

> Beschikbare objecten per Jinja template type in Frappe/ERPNext v14/v15.

---

## Print Formats

| Object | Type | Beschrijving |
|--------|------|--------------|
| `doc` | Document | Het document dat wordt geprint |
| `frappe` | Module | Frappe module met alle utility methods |
| `frappe.utils` | Module | Utility functies |
| `_()` | Function | Vertaalfunctie |

### Voorbeeld Print Format Context

```jinja
<h1>{{ doc.name }}</h1>
<p>{{ doc.customer_name }}</p>
<p>{{ doc.get_formatted("posting_date") }}</p>
<p>{{ doc.get_formatted("grand_total") }}</p>
<p>{{ _("Invoice") }}</p>
```

---

## Email Templates

| Object | Type | Beschrijving |
|--------|------|--------------|
| `doc` | Document | Het gekoppelde document (indien aanwezig) |
| Alle velden | Veldwaarden | Direct toegankelijk via veldnaam |
| `frappe` | Module | Frappe module (beperkt) |

### Voorbeeld Email Context

```jinja
<p>Dear {{ doc.customer_name }},</p>
<p>Invoice {{ doc.name }} is due.</p>
<p>Amount: {{ doc.get_formatted("grand_total") }}</p>
```

---

## Portal Pages (www/*.html)

| Object | Type | Beschrijving |
|--------|------|--------------|
| `frappe` | Module | Frappe module |
| `frappe.session` | Object | Sessie informatie |
| `frappe.session.user` | String | Huidige gebruiker |
| `frappe.form_dict` | Dict | Query parameters (bij web request) |
| `frappe.lang` | String | Huidige taal (twee-letter code) |
| Custom context | Varies | Via Python controller toegevoegd |

### Voorbeeld Portal Context

```jinja
{% extends "templates/web.html" %}

{% block page_content %}
{% if frappe.session.user != 'Guest' %}
    <p>Welcome, {{ frappe.get_fullname() }}</p>
{% endif %}

{% for project in projects %}
    <h3>{{ project.title }}</h3>
{% endfor %}
{% endblock %}
```

---

## Controller Context Keys

Speciale keys die je in Python controllers kunt zetten:

| Key | Type | Beschrijving |
|-----|------|--------------|
| `title` | String | Page title |
| `description` | String | Meta description |
| `image` | String | Meta image URL |
| `no_cache` | Boolean | Disable page caching |
| `sitemap` | Boolean | Include in sitemap |
| `add_breadcrumbs` | Boolean | Auto-generate breadcrumbs |
| `safe_render` | Boolean | Enable/disable safe render |

### Voorbeeld Controller

```python
# www/projects/index.py
import frappe

def get_context(context):
    context.title = "Our Projects"
    context.no_cache = True
    context.projects = frappe.get_all(
        "Project",
        filters={"is_public": 1},
        fields=["name", "title", "description", "status"]
    )
    return context
```

---

## Report Print Formats (NIET Jinja!)

**WAARSCHUWING**: Report Print Formats voor Query/Script Reports gebruiken JavaScript templating, NIET Jinja.

| Syntax | Jinja (Server) | JS Template (Client) |
|--------|----------------|---------------------|
| Code blocks | `{% %}` | `{% %}` |
| Output | `{{ }}` | `{%= %}` |
| Taal | Python | JavaScript |

```html
<!-- JS Template syntax -->
{% for(var i=0; i<data.length; i++) { %}
<tr>
    <td>{%= data[i].name %}</td>
</tr>
{% } %}
```
