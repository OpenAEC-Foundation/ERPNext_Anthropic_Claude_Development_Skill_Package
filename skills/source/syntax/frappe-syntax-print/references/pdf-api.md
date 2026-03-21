# PDF Generation API — Complete Reference

> All PDF generation methods, download endpoints, and rendering configuration in Frappe v14/v15/v16.

---

## Core API: `get_pdf()`

```python
from frappe.utils.pdf import get_pdf

# Basic usage — returns PDF bytes
pdf_bytes = get_pdf(html_string)

# With wkhtmltopdf options
pdf_bytes = get_pdf(html_string, options={
    "page-size": "A4",
    "margin-top": "15mm",
    "margin-right": "10mm",
    "margin-bottom": "15mm",
    "margin-left": "10mm",
    "orientation": "Portrait",
    "encoding": "UTF-8",
})
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `html` | `str` | Required | HTML content to convert to PDF |
| `options` | `dict` | `None` | wkhtmltopdf options (page-size, margins, orientation) |

### Return Value

Returns `bytes` — the raw PDF binary content. ALWAYS handle as binary, never decode to string.

### Common wkhtmltopdf Options

| Option | Values | Default |
|--------|--------|---------|
| `page-size` | `A4`, `Letter`, `A3`, `Legal` | `A4` |
| `orientation` | `Portrait`, `Landscape` | `Portrait` |
| `margin-top` | e.g. `15mm`, `0.5in` | `15mm` |
| `margin-right` | e.g. `10mm` | `15mm` |
| `margin-bottom` | e.g. `15mm` | `15mm` |
| `margin-left` | e.g. `10mm` | `15mm` |
| `encoding` | `UTF-8` | `UTF-8` |
| `quiet` | (flag, no value) | Set by Frappe |

---

## Download Endpoints

### Single Document PDF

```
GET /api/method/frappe.utils.print_format.download_pdf
    ?doctype=Sales Invoice
    &name=SINV-00001
    &format=My Print Format       # optional, uses default if omitted
    &no_letterhead=0               # optional, 0=with letterhead, 1=without
    &letterhead=My Letter Head     # optional, specific Letter Head name
```

### Python: `download_pdf()`

```python
from frappe.utils.print_format import download_pdf

# This sets frappe.response for file download — use in whitelisted methods
download_pdf(
    doctype="Sales Invoice",
    name="SINV-00001",
    format="My Print Format",   # optional
    doc=None,                   # optional, pass pre-loaded doc
    no_letterhead=0             # optional
)
```

### Multiple Documents in One PDF

```
GET /api/method/frappe.utils.print_format.download_multi_pdf
    ?doctype=Sales Invoice
    &name=["SINV-00001","SINV-00002","SINV-00003"]
    &format=My Print Format
    &no_letterhead=0
```

```python
from frappe.utils.print_format import download_multi_pdf

# Downloads concatenated PDF of multiple documents
download_multi_pdf(
    doctype="Sales Invoice",
    name='["SINV-00001","SINV-00002"]',  # JSON string of names
    format="My Print Format",
    no_letterhead=0
)
```

---

## Generating PDF Programmatically

### In a Whitelisted API

```python
@frappe.whitelist()
def get_invoice_pdf(invoice_name):
    """Return PDF as base64 for API consumption."""
    import base64
    from frappe.utils.print_format import download_pdf

    html = frappe.get_print(
        doctype="Sales Invoice",
        name=invoice_name,
        print_format="My Print Format",
        no_letterhead=0
    )

    from frappe.utils.pdf import get_pdf
    pdf_bytes = get_pdf(html)

    return base64.b64encode(pdf_bytes).decode()
```

### Attach PDF to Document

```python
def attach_pdf_to_doc(doctype, name, print_format=None):
    """Generate PDF and attach to document as a file."""
    html = frappe.get_print(
        doctype=doctype,
        name=name,
        print_format=print_format
    )

    from frappe.utils.pdf import get_pdf
    pdf_bytes = get_pdf(html)

    file_name = f"{name}.pdf"
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "content": pdf_bytes,
        "attached_to_doctype": doctype,
        "attached_to_name": name,
        "is_private": 1
    })
    file_doc.save(ignore_permissions=True)
    return file_doc.file_url
```

### Send PDF via Email

```python
def email_with_pdf(doctype, name, recipients, print_format=None):
    """Send document PDF as email attachment."""
    html = frappe.get_print(
        doctype=doctype,
        name=name,
        print_format=print_format
    )

    from frappe.utils.pdf import get_pdf
    pdf_bytes = get_pdf(html)

    frappe.sendmail(
        recipients=recipients,
        subject=f"{doctype}: {name}",
        message=f"Please find attached {doctype} {name}.",
        attachments=[{
            "fname": f"{name}.pdf",
            "fcontent": pdf_bytes
        }]
    )
```

---

## `frappe.get_print()`

The primary function to render a document's print format to HTML.

```python
html = frappe.get_print(
    doctype="Sales Invoice",
    name="SINV-00001",
    print_format="My Print Format",  # optional
    doc=None,                        # optional, pass pre-loaded doc
    no_letterhead=0,                 # optional
    letterhead=None,                 # optional, Letter Head name
    as_pdf=False                     # if True, returns PDF bytes directly
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `doctype` | `str` | Required | DocType name |
| `name` | `str` | Required | Document name |
| `print_format` | `str` | `None` | Print Format name (uses default if None) |
| `doc` | `Document` | `None` | Pre-loaded document (skips DB fetch) |
| `no_letterhead` | `int` | `0` | 1 to suppress Letter Head |
| `letterhead` | `str` | `None` | Specific Letter Head name |
| `as_pdf` | `bool` | `False` | Return PDF bytes instead of HTML |

---

## PDF Hooks

### Inject HTML into PDF Header/Footer/Body

```python
# hooks.py
pdf_header_html = "myapp.utils.pdf.get_pdf_header"
pdf_body_html = "myapp.utils.pdf.get_pdf_body"
pdf_footer_html = "myapp.utils.pdf.get_pdf_footer"
```

```python
# myapp/utils/pdf.py
def get_pdf_header(soup, head, content, styles):
    """Called during PDF generation. Return HTML string for header."""
    return '<div style="text-align:center; font-size:8pt;">Company Name</div>'

def get_pdf_footer(soup, head, content, styles):
    """Called during PDF generation. Return HTML string for footer."""
    return '''
    <div style="text-align:center; font-size:8pt;">
        Page <span class="page"></span> of <span class="topage"></span>
    </div>
    '''
```

### Hook Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `soup` | `BeautifulSoup` | Parsed HTML of the print format |
| `head` | `str` | HTML `<head>` content |
| `content` | `str` | HTML body content |
| `styles` | `str` | CSS styles |

---

## PDF Engine Configuration (v15+)

### Per Print Format

Set `pdf_generator` field on the Print Format document:

| Value | Engine | Notes |
|-------|--------|-------|
| (empty) | wkhtmltopdf | Default, compatible with v14 |
| `chrome` | Chromium headless | Better CSS3/flexbox support |

### Print Designer (v15+ Only)

Print Designer formats ALWAYS use WeasyPrint. No configuration needed — it is automatic.

### Global Configuration

In `site_config.json`:

```json
{
  "pdf_generator": "chrome"
}
```

This sets the default PDF engine for ALL print formats on the site. Individual Print Format settings override the global default.

---

## Page Break Control

### In HTML

```html
<!-- Page break between sections -->
<div class="page-break"></div>

<!-- Page break before a specific section -->
<div style="page-break-before: always;">
  <h2>Section 2</h2>
</div>

<!-- Prevent break inside an element -->
<div style="page-break-inside: avoid;">
  <table>...</table>
</div>
```

### In Jinja Loops (e.g., Multi-Section Invoices)

```html
{% for group in doc.item_groups %}
  {% if not loop.first %}
    <div class="page-break"></div>
  {% endif %}

  <h3>{{ group.name }}</h3>
  <table>
    {% for item in group.items %}
      <tr><td>{{ item.item_name }}</td></tr>
    {% endfor %}
  </table>
{% endfor %}
```

### wkhtmltopdf Header/Footer with Page Numbers

```html
<!-- Elements with these IDs are extracted by wkhtmltopdf -->
<div id="header-html">
  <div style="font-size: 8pt; text-align: right; padding: 5mm;">
    {{ doc.company }}
  </div>
</div>

<div id="footer-html">
  <div style="font-size: 8pt; text-align: center; padding: 5mm;">
    Page <span class="page"></span> of <span class="topage"></span>
  </div>
</div>
```

**IMPORTANT:** `<span class="page">` and `<span class="topage">` are wkhtmltopdf-specific replacements. They ONLY work in PDF output, not in browser print preview.

---

## Troubleshooting PDF Generation

### Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| Blank PDF | HTML has syntax errors | Validate HTML, check Frappe error log |
| Missing images | Relative URLs | Use absolute URLs: `{{ frappe.utils.get_url() }}/files/logo.png` |
| CSS not applied | External stylesheets blocked | Inline CSS or use `<style>` tags |
| Page breaks ignored | `page-break-inside: avoid` on parent | Check parent element CSS |
| Fonts not rendering | Custom fonts not available to wkhtmltopdf | Use system fonts or embed as base64 |
| Landscape not working | Option not passed | Set `orientation: Landscape` in options |
| Letter Head missing | `no_letterhead=1` or no default | Check Letter Head configuration |

### Debug PDF Rendering

```python
# Get the HTML that would be sent to PDF engine
html = frappe.get_print("Sales Invoice", "SINV-00001", "My Format")
frappe.log_error(html, "PDF Debug HTML")

# Check wkhtmltopdf version
import subprocess
result = subprocess.run(["wkhtmltopdf", "--version"], capture_output=True, text=True)
print(result.stdout)
```
