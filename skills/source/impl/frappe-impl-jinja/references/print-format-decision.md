# Print Format: Jinja vs Print Designer vs JS Microtemplate

> Decision tree for choosing the right print format technology in Frappe/ERPNext.

---

## Master Decision: Which Print Technology?

```
Need a print format?
│
├─► Simple layout, standard fields
│   └── Standard Print Format (no code)
│       - Setup > Printing > Print Format Builder
│       - Drag-and-drop field placement
│       - Works on all versions (v14/v15/v16)
│       - No coding required
│
├─► Custom layout with logic/calculations
│   └── Jinja Print Format ✓ (THIS skill)
│       - Full template control with {{ }} and {% %}
│       - Server-side, Python-powered
│       - Works on v14+ (all versions)
│       - Conditional sections, computed values, child table loops
│       - CSS styling in <style> block
│       - PDF via wkhtmltopdf (v14/v15) or Chrome (v16)
│
├─► Visual drag-and-drop design [v15+]
│   └── Print Designer (separate Frappe app)
│       - Install: bench get-app print_designer
│       - No coding required — WYSIWYG editor
│       - Uses WeasyPrint for PDF rendering (not wkhtmltopdf)
│       - Dynamic fields via drag-and-drop binding
│       - v15+: stable; v14: NOT supported
│       - GitHub: https://github.com/frappe/print_designer
│
└─► Report print format (Query Report / Script Report)
    └── JS Microtemplate ({%= %} syntax)
        ⚠️ NOT Jinja — completely different engine
        - Client-side, JavaScript-powered
        - Uses {%= %} for expressions, {% %} for logic
        - Access: data[], filters, report_summary
        - See frappe-syntax-print skill for full coverage
```

---

## Key Differences: Three Template Engines

| Feature | Jinja | Print Designer | JS Microtemplate |
|---------|-------|----------------|------------------|
| **Syntax** | `{{ }}` / `{% %}` | No code (visual) | `{%= %}` / `{% %}` |
| **Execution** | Server-side (Python) | Server-side (WeasyPrint) | Client-side (JavaScript) |
| **Used for** | Print Formats, Emails, Portal | Print Formats only | Report Print Formats only |
| **Versions** | v14/v15/v16 | v15+ (separate app) | v14/v15/v16 |
| **PDF engine** | wkhtmltopdf / Chrome (v16) | WeasyPrint | wkhtmltopdf / Chrome (v16) |
| **Coding required** | Yes (HTML + Jinja) | No (drag-and-drop) | Yes (HTML + JS) |
| **Child tables** | `{% for row in doc.items %}` | Visual table binding | `{% for(var i=0; i<data.length; i++) %}` |
| **Formatting** | `doc.get_formatted("field")` | Automatic | `format_currency(value)` |

---

## Critical Rules

### NEVER Mix Template Engines

```
⚠️ FATAL MISTAKE: Using Jinja syntax in a Report Print Format

Report Print Format uses JS microtemplate:
  WRONG: {{ doc.grand_total }}         ← Jinja syntax, will NOT render
  RIGHT: {%= format_currency(row.grand_total) %}  ← JS microtemplate

Jinja Print Format uses Jinja:
  WRONG: {%= doc.grand_total %}        ← JS syntax, will NOT render
  RIGHT: {{ doc.get_formatted("grand_total") }}   ← Jinja syntax
```

### When to Choose What

| Scenario | Choose | Why |
|----------|--------|-----|
| Invoice/Quote/PO with custom layout | **Jinja** | Full control, version-independent |
| Non-technical user designs prints | **Print Designer** | No code needed, visual editor |
| Query/Script Report output | **JS Microtemplate** | Only option for reports |
| Simple field rearrangement | **Standard** | Fastest, no code |
| Complex multi-page with calculations | **Jinja** | Most powerful, full Python access |
| Label/barcode printing | **Print Designer** | Better for precise positioning |

---

## Print Designer Details (v15+)

### Installation

```bash
bench get-app print_designer
bench --site sitename install-app print_designer
```

### How It Works

1. Go to **Print Designer** in the sidebar
2. Create new format, select DocType
3. Drag fields onto the canvas
4. Bind dynamic data via field selector
5. Style visually (fonts, colors, borders, positioning)
6. Save — format appears in Print Format dropdown

### Print Designer vs Jinja Print Format

```
Choose Print Designer when:
├─ Users need to modify layouts without developer help
├─ Precise pixel positioning is required (labels, certificates)
├─ No conditional logic needed (or very simple show/hide)
└─ Running v15 or later

Choose Jinja Print Format when:
├─ Complex business logic in the template (calculations, conditionals)
├─ Need to aggregate or transform data before display
├─ Must work on v14 (Print Designer requires v15+)
├─ Need programmatic control (loops with counters, custom grouping)
└─ Integration with custom Jinja methods/filters
```

### Limitations of Print Designer

- **No arbitrary Python logic** — limited to field binding and simple expressions
- **Requires WeasyPrint** — different PDF output from wkhtmltopdf/Chrome
- **No Email/Portal support** — Print Designer is for print formats ONLY
- **v15+ only** — not available on v14 installations

---

## Cross-References

| Skill | Covers |
|-------|--------|
| `frappe-impl-jinja` (this skill) | Jinja Print Format creation workflow |
| `frappe-syntax-jinja` | Jinja syntax reference (filters, tags, context) |
| `frappe-syntax-print` | Full print system: all format types, JS microtemplate, PDF engines |

---

## Version Compatibility Matrix

| Technology | v14 | v15 | v16 |
|------------|:---:|:---:|:---:|
| Standard Print Format | Yes | Yes | Yes |
| Jinja Print Format | Yes | Yes | Yes |
| Print Designer | No | Yes | Yes |
| JS Microtemplate (Reports) | Yes | Yes | Yes |
| wkhtmltopdf | Yes | Yes | Deprecated |
| Chrome PDF | No | No | Yes |
| WeasyPrint (Print Designer) | No | Yes | Yes |
