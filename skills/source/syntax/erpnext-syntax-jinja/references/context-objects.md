# Context Objects Reference

> Available objects per Jinja template type in Frappe/ERPNext v14/v15.

---

## Print Formats

| Object | Type | Description |
|--------|------|-------------|
| `doc` | Document | The document being printed |
| `frappe` | Module | Frappe module with all utility methods |
| `frappe.utils` | Module | Utility functions |
| `_()` | Function | Translation function |

### Example Print Format Context

```jinja
<h1>{{ doc.name }}</h1>
<p>{{ doc.customer_name }}</p>
<p>{{ doc.get_formatted("posting_date") }}</p>
<p>{{ doc.get_formatted("grand_total") }}</p>
<p>{{ _("Invoice") }}</p>
```

---

## Email Templates

| Object | Type | Description |
|--------|------|-------------|
| `doc` | Document | The linked document (if available) |
| All fields | Field values | Directly accessible via field name |
| `frappe` | Module | Frappe module (limited) |

### Example Email Context

```jinja
<p>Dear {{ doc.customer_name }},</p>
<p>Invoice {{ doc.name }} is due.</p>
<p>Amount: {{ doc.get_formatted("grand_total") }}</p>
```

---

## Portal Pages (www/*.html)

| Object | Type | Description |
|--------|------|-------------|
| `frappe` | Module | Frappe module |
| `frappe.session` | Object | Session information |
| `frappe.session.user` | String | Current user |
| `frappe.form_dict` | Dict | Query parameters (for web requests) |
| `frappe.lang` | String | Current language (two-letter code) |
| Custom context | Varies | Added via Python controller |

### Example Portal Context

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

Special keys you can set in Python controllers:

| Key | Type | Description |
|-----|------|-------------|
| `title` | String | Page title |
| `description` | String | Meta description |
| `image` | String | Meta image URL |
| `no_cache` | Boolean | Disable page caching |
| `sitemap` | Boolean | Include in sitemap |
| `add_breadcrumbs` | Boolean | Auto-generate breadcrumbs |
| `safe_render` | Boolean | Enable/disable safe render |

### Example Controller

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

## Report Print Formats (NOT Jinja!)

**WARNING**: Report Print Formats for Query/Script Reports use JavaScript templating, NOT Jinja.

| Syntax | Jinja (Server) | JS Template (Client) |
|--------|----------------|---------------------|
| Code blocks | `{% %}` | `{% %}` |
| Output | `{{ }}` | `{%= %}` |
| Language | Python | JavaScript |

```html
<!-- JS Template syntax -->
{% for(var i=0; i<data.length; i++) { %}
<tr>
    <td>{%= data[i].name %}</td>
</tr>
{% } %}
```
