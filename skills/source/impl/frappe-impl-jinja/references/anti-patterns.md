# Jinja Templates - Anti-Patterns

> Common mistakes and how to avoid them.

---

## Anti-Pattern 1: Using Jinja Syntax in Report Print Formats

### ❌ Wrong

```jinja
{# In a Query Report or Script Report Print Format #}
{% for row in data %}
    <tr><td>{{ row.name }}</td></tr>
{% endfor %}
```

**Error**: Blank output or template not rendering

### ✅ Correct

```html
<!-- Report Print Formats use JAVASCRIPT templating -->
{% for (var i=0; i<data.length; i++) { %}
    <tr><td>{%= data[i].name %}</td></tr>
{% } %}
```

### Rule

**Report Print Formats (Query Reports, Script Reports) use JavaScript templating, NOT Jinja.**

| Context | Syntax | Variables |
|---------|--------|-----------|
| Print Format (DocType) | `{{ }}` / `{% %}` | `doc` |
| Report Print Format | `{%= %}` / `{% %}` | `data[]`, `filters` |

---

## Anti-Pattern 2: Raw Value Display Without Formatting

### ❌ Wrong

```jinja
<p>Total: {{ doc.grand_total }}</p>
<p>Date: {{ doc.posting_date }}</p>
```

**Result**: `Total: 12500.5` instead of `Total: € 12,500.50`

### ✅ Correct

```jinja
<p>Total: {{ doc.get_formatted("grand_total") }}</p>
<p>Date: {{ doc.get_formatted("posting_date") }}</p>

{# Or for general formatting #}
<p>Total: {{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}</p>
<p>Date: {{ frappe.format_date(doc.posting_date) }}</p>
```

### Rule

**ALWAYS use `get_formatted()` or `frappe.format()` for user-facing values.**

---

## Anti-Pattern 3: Missing Parent Doc for Child Table Formatting

### ❌ Wrong

```jinja
{% for item in doc.items %}
    <td>{{ item.get_formatted("rate") }}</td>
    <td>{{ item.get_formatted("amount") }}</td>
{% endfor %}
```

**Result**: Currency symbol/format may be wrong or missing

### ✅ Correct

```jinja
{% for item in doc.items %}
    <td>{{ item.get_formatted("rate", doc) }}</td>
    <td>{{ item.get_formatted("amount", doc) }}</td>
{% endfor %}
```

### Rule

**Child table rows need the parent doc for currency context.** Pass `doc` as second argument to `get_formatted()`.

---

## Anti-Pattern 4: N+1 Query Problem in Templates

### ❌ Wrong

```jinja
{% for item in doc.items %}
    {% set stock = frappe.db.get_value("Bin", 
        {"item_code": item.item_code, "warehouse": doc.warehouse}, 
        "actual_qty") %}
    <td>{{ stock }}</td>
{% endfor %}
```

**Result**: 1 query per item = slow rendering for large tables

### ✅ Correct

**Option A: Prefetch in Controller**

```python
# In controller or get_context
def before_print(self, settings=None):
    items = [i.item_code for i in self.items]
    self.stock_data = get_stock_for_items(items, self.warehouse)
```

```jinja
{% for item in doc.items %}
    <td>{{ doc.stock_data.get(item.item_code, 0) }}</td>
{% endfor %}
```

**Option B: Custom Jinja Method with Caching**

```python
# In jinja methods
def get_stock_batch(item_codes, warehouse):
    # Single query for all items
    result = frappe.db.sql("""...""")
    return {r.item_code: r.qty for r in result}
```

### Rule

**Never execute database queries inside loops.** Prefetch data before template rendering.

---

## Anti-Pattern 5: Using `| safe` for User Input

### ❌ Wrong

```jinja
<div>{{ doc.custom_notes | safe }}</div>
<p>{{ user_comment | safe }}</p>
```

**Result**: XSS vulnerability - users can inject malicious scripts

### ✅ Correct

```jinja
{# For trusted system content only #}
<div>{{ doc.terms | safe }}</div>

{# For user input - let Jinja auto-escape #}
<p>{{ user_comment }}</p>

{# Or explicit escape #}
<p>{{ user_comment | e }}</p>
```

### Rule

**Only use `| safe` for trusted HTML content** (like system-generated Terms & Conditions). User input should be auto-escaped.

---

## Anti-Pattern 6: Hardcoded Strings Without Translation

### ❌ Wrong

```jinja
<h1>Invoice</h1>
<th>Amount</th>
<td>Total:</td>
<p>Thank you for your business!</p>
```

**Result**: Cannot be translated for multi-language sites

### ✅ Correct

```jinja
<h1>{{ _("Invoice") }}</h1>
<th>{{ _("Amount") }}</th>
<td>{{ _("Total") }}:</td>
<p>{{ _("Thank you for your business!") }}</p>
```

### Rule

**Wrap ALL user-facing strings with `_()`** for translation support.

---

## Anti-Pattern 7: Missing Default Values

### ❌ Wrong

```jinja
<p>Contact: {{ doc.contact_name }}</p>
<p>Phone: {{ doc.contact_phone }}</p>
```

**Result**: Displays "None" or empty when field is null

### ✅ Correct

```jinja
<p>Contact: {{ doc.contact_name | default('-') }}</p>
<p>Phone: {{ doc.contact_phone | default('N/A') }}</p>

{# Or with conditional #}
{% if doc.contact_name %}
<p>Contact: {{ doc.contact_name }}</p>
{% endif %}
```

### Rule

**Always handle null/empty values** with `| default()` or conditionals.

---

## Anti-Pattern 8: Inline Styles in Email Templates (Wrong Way)

### ❌ Wrong

```jinja
<style>
    .email-header { background: #333; color: white; }
    .button { background: blue; padding: 10px; }
</style>
<div class="email-header">...</div>
```

**Result**: Most email clients ignore `<style>` blocks

### ✅ Correct

```jinja
<div style="background: #333; color: white; padding: 20px;">
    ...
</div>
<a href="..." style="background: blue; color: white; padding: 10px 20px; text-decoration: none; display: inline-block;">
    Button
</a>
```

### Rule

**Email templates must use inline styles.** CSS classes and `<style>` blocks are stripped by most email clients.

---

## Anti-Pattern 9: Heavy Computations in Templates

### ❌ Wrong

```jinja
{% set total = 0 %}
{% for order in frappe.get_all("Sales Order", filters={"customer": doc.customer}, fields=["grand_total"]) %}
    {% set total = total + order.grand_total %}
{% endfor %}
{% for invoice in frappe.get_all("Sales Invoice", filters={"customer": doc.customer}, fields=["outstanding_amount"]) %}
    {# More complex calculations #}
{% endfor %}
<p>Customer Lifetime Value: {{ total }}</p>
```

**Result**: Slow template rendering, complex logic hard to maintain

### ✅ Correct

```python
# In controller or context
def get_context(context):
    context.customer_stats = calculate_customer_stats(customer)
```

```jinja
<p>Customer Lifetime Value: {{ customer_stats.lifetime_value }}</p>
```

### Rule

**Templates are for presentation, not computation.** Move complex logic to Python.

---

## Anti-Pattern 10: Assuming Variable Existence

### ❌ Wrong

```jinja
<p>{{ doc.custom_field.nested_value }}</p>
<img src="{{ company.company_logo }}">
```

**Result**: AttributeError or UndefinedError if variable is None

### ✅ Correct

```jinja
<p>{{ doc.custom_field.nested_value if doc.custom_field else '' }}</p>

{% if company and company.company_logo %}
<img src="{{ company.company_logo }}">
{% endif %}
```

### Rule

**Always check variable existence** before accessing nested properties.

---

## Anti-Pattern 11: Breaking Page Layout in Print Formats

### ❌ Wrong

```jinja
<table>
    {% for item in doc.items %}
    <tr>
        <td>{{ item.item_name }}</td>
    </tr>
    {% endfor %}
</table>
{# Long description that might cause page break mid-row #}
```

**Result**: Table rows split across pages, broken layout

### ✅ Correct

```jinja
<style>
    .avoid-break { page-break-inside: avoid; }
    thead { display: table-header-group; }
</style>

<table>
    <thead>
        <tr><th>Item</th></tr>
    </thead>
    <tbody>
        {% for item in doc.items %}
        <tr class="avoid-break">
            <td>{{ item.item_name }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### Rule

**Use CSS page-break properties** to control print layout.

---

## Anti-Pattern 12: Not Testing PDF Output

### ❌ Wrong

Developing print format only checking in browser view.

**Result**: PDF renders differently (wkhtmltopdf has CSS limitations)

### ✅ Correct

Development workflow:

1. Design in browser
2. **Test PDF download** after each significant change
3. Check on actual printer if critical

### Rule

**Always test PDF output** - wkhtmltopdf (v14/v15) has limited CSS support (no flexbox, limited grid). V16 Chrome PDF is better.

---

## Anti-Pattern 13: Committing in Custom Jinja Methods

### ❌ Wrong

```python
# In jinja method
def update_counter(doc_name):
    frappe.db.set_value("Counter", doc_name, "count", count + 1)
    frappe.db.commit()  # ❌ NEVER DO THIS
    return count + 1
```

**Result**: Can break transaction integrity, data corruption

### ✅ Correct

```python
# Jinja methods should be READ-ONLY
def get_counter(doc_name):
    return frappe.db.get_value("Counter", doc_name, "count") or 0
```

### Rule

**Jinja methods should only READ data, never write.** Side effects in templates are dangerous.

---

## Anti-Pattern 14: Large Images Without Optimization

### ❌ Wrong

```jinja
<img src="{{ doc.image }}">
{# Where doc.image is a 5MB full-resolution photo #}
```

**Result**: Huge PDF files, slow loading

### ✅ Correct

```jinja
{# Use thumbnail if available #}
{% set image_url = doc.image %}
{% if image_url and not image_url.startswith('http') %}
    {% set image_url = "/api/method/frappe.utils.image.resize_image?image=" + image_url + "&height=200" %}
{% endif %}
<img src="{{ image_url }}" style="max-width: 200px;">
```

### Rule

**Optimize images for templates** - use thumbnails or resize on the fly.

---

## Anti-Pattern 15: Ignoring Template Errors

### ❌ Wrong

Template shows blank or partial output, developer assumes "it's working".

### ✅ Correct

**Debug steps:**

```jinja
{# 1. Add debug output #}
<!-- DEBUG: doc = {{ doc }} -->
<!-- DEBUG: doc.items length = {{ doc.items | length if doc.items else 'NONE' }} -->

{# 2. Check Error Log #}
{# Setup > Error Log #}

{# 3. Use try-except in custom methods #}
```

```python
def safe_method(arg):
    try:
        return do_something(arg)
    except Exception as e:
        frappe.log_error(f"Jinja method error: {e}")
        return ""
```

### Rule

**Check Error Log for template errors.** Add debug output when troubleshooting.

---

## Quick Reference: Anti-Pattern Summary

| Anti-Pattern | Fix |
|--------------|-----|
| Jinja in Report Print | Use JS templating `{%= %}` |
| Raw values | Use `get_formatted()` |
| Missing parent doc | Pass `doc` to child `get_formatted()` |
| Queries in loops | Prefetch data |
| `\| safe` on user input | Let Jinja auto-escape |
| Hardcoded strings | Use `_("string")` |
| Missing defaults | Use `\| default()` |
| `<style>` in email | Use inline styles |
| Heavy computation | Move to Python |
| Assuming variables exist | Check with `if` first |
| Bad page breaks | Use CSS page-break |
| No PDF testing | Always test PDF download |
| Commits in methods | Methods should be read-only |
| Large images | Optimize/resize |
| Ignoring errors | Check Error Log |
