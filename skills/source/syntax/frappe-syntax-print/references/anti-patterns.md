# Print Format Anti-Patterns — Complete Reference

> Common mistakes when building print formats and generating PDFs in Frappe v14/v15/v16, with correct alternatives.

---

## AP-1: Mixing Jinja and JS Template Syntax

### The Mistake

Using `{{ }}` (Jinja) syntax in a Report Print Format, or `{%= %}` (JS microtemplate) in a Jinja Print Format.

```html
<!-- WRONG: Jinja syntax in a Report Print Format -->
<td>{{ row.item_name }}</td>
<td>{{ row.qty }}</td>
```

### Why It Fails

Report Print Formats use JavaScript microtemplate engine (`{%= %}`), NOT Jinja. The `{{ }}` syntax is silently ignored or causes rendering errors.

### The Fix

```html
<!-- CORRECT: JS microtemplate in Report Print Format -->
<td>{%= row.item_name %}</td>
<td>{%= row.qty %}</td>

{% if (row.qty > 10) { %}
  <strong>Bulk</strong>
{% } %}
```

**Rule:** ALWAYS check the `print_format_for` field. If it says `"Report"`, use `{%= %}`. For all other print formats, use Jinja `{{ }}`.

---

## AP-2: N+1 Queries in Jinja Templates

### The Mistake

```html
<!-- WRONG: frappe.get_doc() inside a loop -->
{% for row in doc.items %}
  {% set item = frappe.get_doc("Item", row.item_code) %}
  <td>{{ item.item_group }}</td>
  <td>{{ item.stock_uom }}</td>
{% endfor %}
```

### Why It Fails

If `doc.items` has 50 rows, this executes 50 separate database queries. For complex documents with hundreds of items, this causes severe performance degradation and can time out PDF generation.

### The Fix

```html
<!-- CORRECT: Batch fetch before the loop -->
{% set item_codes = doc.items | map(attribute='item_code') | list %}
{% set item_data = frappe.get_all("Item",
    filters={"name": ["in", item_codes]},
    fields=["name", "item_group", "stock_uom"]
) %}
{% set item_map = {} %}
{% for item in item_data %}
  {% set _ = item_map.update({item.name: item}) %}
{% endfor %}

{% for row in doc.items %}
  {% set item = item_map.get(row.item_code, {}) %}
  <td>{{ item.get("item_group", "") }}</td>
  <td>{{ item.get("stock_uom", "") }}</td>
{% endfor %}
```

**Rule:** NEVER call `frappe.get_doc()` or `frappe.db.get_value()` inside a `{% for %}` loop. ALWAYS batch-fetch data before the loop.

---

## AP-3: Heavy Business Logic in Jinja Templates

### The Mistake

```html
<!-- WRONG: Complex calculations in the template -->
{% set tax_rate = 0 %}
{% for tax in doc.taxes %}
  {% if tax.charge_type == "On Net Total" %}
    {% set tax_rate = tax_rate + tax.rate %}
  {% endif %}
{% endfor %}
{% set adjusted_total = doc.net_total * (1 + tax_rate / 100) %}
{% if adjusted_total > doc.grand_total %}
  {% set difference = adjusted_total - doc.grand_total %}
  <!-- ... 50 more lines of calculation logic ... -->
{% endif %}
```

### Why It Fails

- Jinja templates are hard to debug (no breakpoints, limited error messages)
- Business logic in templates cannot be unit tested
- Makes the template unmaintainable and unreadable
- Jinja's scoping rules make complex state management error-prone

### The Fix

Move logic to a Python method and call it from the template:

```python
# myapp/utils/print_helpers.py
def get_invoice_summary(doc_name):
    """Calculate invoice summary for print format."""
    doc = frappe.get_doc("Sales Invoice", doc_name)
    tax_rate = sum(
        tax.rate for tax in doc.taxes
        if tax.charge_type == "On Net Total"
    )
    adjusted_total = doc.net_total * (1 + tax_rate / 100)
    return {
        "tax_rate": tax_rate,
        "adjusted_total": adjusted_total,
        "difference": adjusted_total - doc.grand_total
    }
```

```python
# hooks.py
jinja = {
    "methods": ["myapp.utils.print_helpers.get_invoice_summary"]
}
```

```html
<!-- CORRECT: Simple template, logic in Python -->
{% set summary = get_invoice_summary(doc.name) %}
<p>Tax Rate: {{ summary.tax_rate }}%</p>
<p>Adjusted Total: {{ frappe.utils.fmt_money(summary.adjusted_total, currency=doc.currency) }}</p>
```

**Rule:** If your Jinja template has more than 5 lines of calculation or conditional logic, ALWAYS move it to a Python function registered via `jinja.methods` in hooks.py.

---

## AP-4: Hardcoding Page Dimensions in CSS

### The Mistake

```css
/* WRONG: Hardcoded pixel dimensions */
.my-print-format {
  width: 794px;
  height: 1123px;
  padding: 50px;
}

.my-table {
  width: 694px;
}
```

### Why It Fails

- Pixel dimensions break on different DPI settings
- Does not adapt to different paper sizes (Letter vs A4)
- PDF engine may interpret pixel sizes differently than browser
- Ignores user's Print Settings (margins, paper size)

### The Fix

```css
/* CORRECT: Use relative/print-friendly units */
.print-format {
  max-width: 100%;
  padding: 0;
}

.my-table {
  width: 100%;
}

@media print {
  @page {
    size: A4 portrait;
    margin: 15mm;
  }
}
```

**Rule:** ALWAYS use `%`, `mm`, `cm`, or `in` for print dimensions. NEVER use `px` for page-level layout in print formats. Use Frappe's `.print-format` class which handles A4/Letter sizing automatically.

---

## AP-5: Ignoring the `no_letterhead` Parameter

### The Mistake

```python
# WRONG: Hardcoded letterhead inclusion
def generate_pdf(doctype, name):
    html = frappe.get_print(doctype, name, "My Format")
    return get_pdf(html)
```

### Why It Fails

- Users may want PDFs without Letter Head (e.g., for embedding in other documents)
- Some workflows specifically require no Letter Head
- Ignores user preference from Print Settings

### The Fix

```python
# CORRECT: Respect no_letterhead parameter
def generate_pdf(doctype, name, no_letterhead=0):
    html = frappe.get_print(
        doctype, name, "My Format",
        no_letterhead=no_letterhead
    )
    return get_pdf(html)
```

**Rule:** ALWAYS accept and pass through the `no_letterhead` parameter in any PDF generation function. NEVER assume Letter Head should always be included.

---

## AP-6: Using Print Designer on v14

### The Mistake

Attempting to install or use Print Designer on Frappe v14.

```bash
# WRONG on v14:
bench get-app print_designer
```

### Why It Fails

Print Designer is a v15+ application. It requires WeasyPrint and Frappe v15's Print Format architecture changes. Installing it on v14 will fail or produce broken output.

### The Fix

- On v14: Use Jinja Print Formats with `custom_format=1` for full layout control
- On v15+: Print Designer is available as a separate app (`bench get-app print_designer`)

**Rule:** ALWAYS check the Frappe version before recommending Print Designer. On v14, use Jinja-based custom print formats instead.

---

## AP-7: Large Images Without Size Constraints

### The Mistake

```html
<!-- WRONG: No size constraints on images -->
<img src="{{ frappe.utils.get_url() }}/files/product_photo.jpg">

<!-- WRONG: Base64 inline image -->
<img src="data:image/jpeg;base64,{{ huge_base64_string }}">
```

### Why It Fails

- Unconstrained images overflow the page and break layout
- Large base64 images dramatically increase HTML size, causing wkhtmltopdf to run out of memory
- PDF generation time increases by 10-100x with inline images

### The Fix

```html
<!-- CORRECT: Constrained image with URL -->
<img src="{{ frappe.utils.get_url() }}/files/product_photo.jpg"
     style="max-width: 100%; height: auto; max-height: 200px;">

<!-- For logos/small images only — limit base64 to under 50KB -->
<img src="{{ doc.image }}" style="max-width: 150px; height: auto;">
```

**Rule:** ALWAYS set `max-width: 100%` and `height: auto` on images in print formats. NEVER embed large images as base64. Use absolute URLs for images and constrain dimensions with CSS.

---

## AP-8: Not Using `| safe` for HTML Content

### The Mistake

```html
<!-- WRONG: HTML-encoded output -->
<div>{{ doc.terms }}</div>
<!-- Renders as: &lt;p&gt;Payment due in 30 days&lt;/p&gt; -->
```

### Why It Fails

Jinja auto-escapes HTML by default. Fields containing HTML (like `terms`, `description`, `letter_head`) render as escaped text instead of formatted HTML.

### The Fix

```html
<!-- CORRECT: Mark as safe HTML -->
<div>{{ doc.terms | safe }}</div>
<!-- Renders as: <p>Payment due in 30 days</p> -->
```

**Rule:** ALWAYS use `| safe` filter when outputting fields that contain HTML content (Text Editor fields, terms, descriptions). NEVER use `| safe` on user-input fields that should not contain HTML.

---

## AP-9: Relative Image URLs in PDF

### The Mistake

```html
<!-- WRONG: Relative URL -->
<img src="/files/logo.png">
```

### Why It Fails

wkhtmltopdf runs as a separate process and cannot resolve relative URLs. The image will be missing in the generated PDF, even though it works in browser print preview.

### The Fix

```html
<!-- CORRECT: Absolute URL -->
<img src="{{ frappe.utils.get_url() }}/files/logo.png"
     style="max-width: 200px; height: auto;">
```

**Rule:** ALWAYS use `{{ frappe.utils.get_url() }}` prefix for image and asset URLs in print formats. Relative URLs work in browser preview but FAIL in PDF generation.

---

## AP-10: Forgetting Jinja Variable Scoping in Loops

### The Mistake

```html
<!-- WRONG: Variable set inside loop does not update outer scope -->
{% set total = 0 %}
{% for row in doc.items %}
  {% set total = total + row.amount %}
{% endfor %}
<p>Total: {{ total }}</p>
<!-- Always shows 0! -->
```

### Why It Fails

Jinja2's scoping rules mean that `{% set %}` inside a `{% for %}` block creates a new variable in the loop's scope. It does NOT update the outer variable.

### The Fix

```html
<!-- CORRECT: Use namespace for mutable state across scopes -->
{% set ns = namespace(total=0) %}
{% for row in doc.items %}
  {% set ns.total = ns.total + row.amount %}
{% endfor %}
<p>Total: {{ frappe.utils.fmt_money(ns.total, currency=doc.currency) }}</p>
```

**Rule:** ALWAYS use `namespace()` when you need to accumulate values across a `{% for %}` loop in Jinja2. Plain `{% set %}` inside loops does NOT update outer scope variables.

---

## Summary Table

| # | Anti-Pattern | Key Rule |
|---|-------------|----------|
| AP-1 | Mixing Jinja/JS syntax | Check `print_format_for` field |
| AP-2 | N+1 queries in loops | Batch-fetch before loops |
| AP-3 | Logic in templates | Move to Python, register via hooks |
| AP-4 | Hardcoded dimensions | Use relative units, `.print-format` class |
| AP-5 | Ignoring no_letterhead | ALWAYS pass through the parameter |
| AP-6 | Print Designer on v14 | Requires v15+ |
| AP-7 | Large unconstrained images | `max-width: 100%`, use URLs not base64 |
| AP-8 | Missing `\| safe` filter | Use for HTML content fields |
| AP-9 | Relative image URLs | Use `frappe.utils.get_url()` prefix |
| AP-10 | Variable scoping in loops | Use `namespace()` for loop accumulators |
