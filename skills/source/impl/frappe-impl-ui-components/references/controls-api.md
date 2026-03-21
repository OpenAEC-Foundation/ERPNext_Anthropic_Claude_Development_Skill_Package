# Controls API Reference

Extended reference for standalone controls, control types, and advanced control patterns.
Parent skill: `frappe-impl-ui-components`

## frappe.ui.form.make_control() — Standalone Controls

Create Frappe controls outside of forms — in custom pages, dialogs, or arbitrary DOM containers.

### Signature

```javascript
frappe.ui.form.make_control({
    parent: HTMLElement | jQuery,  // Container element
    df: {                          // Field definition object
        fieldtype: "Data",
        fieldname: "my_field",
        label: "My Field",
        // ... any standard field properties
    },
    render_input: true,  // MUST be true to render the actual input element
});
```

### How It Works

The factory function maps `fieldtype` to a class name: `"Control" + fieldtype.replace(/ /g, "")`.
For example, `fieldtype: "Small Text"` resolves to `frappe.ui.form.ControlSmallText`.

**Rule**: ALWAYS set `render_input: true` when creating standalone controls. Without it, only the wrapper is created — no input element is rendered.

### Basic Example — Standalone Control on a Page

```javascript
frappe.pages["my-page"].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "My Page",
        single_column: true,
    });

    let $container = $('<div class="my-controls">').appendTo(page.body);

    // Create a standalone Link control
    let customer_control = frappe.ui.form.make_control({
        parent: $container,
        df: {
            fieldtype: "Link",
            fieldname: "customer",
            label: "Customer",
            options: "Customer",
            change() {
                let value = customer_control.get_value();
                if (value) load_customer_data(value);
            }
        },
        render_input: true,
    });

    // Create a standalone Date control
    let date_control = frappe.ui.form.make_control({
        parent: $container,
        df: {
            fieldtype: "Date",
            fieldname: "from_date",
            label: "From Date",
            default: frappe.datetime.month_start(),
        },
        render_input: true,
    });

    // Set a value programmatically
    customer_control.set_value("CUST-001");
};
```

### Control Methods (BaseControl / BaseInput)

All controls inherit from `frappe.ui.form.Control` (BaseControl):

| Method | Purpose |
|--------|---------|
| `control.get_value()` | Get current value |
| `control.set_value(value)` | Set value (returns Promise) |
| `control.refresh()` | Re-render the control based on current state |
| `control.toggle(show)` | Show/hide the control |
| `control.set_description(text)` | Set help text below the control |
| `control.set_mandatory(value)` | Set/unset required state |

Input controls (`BaseInput` subclasses) additionally have:

| Method | Purpose |
|--------|---------|
| `control.set_input(value)` | Set the DOM input value directly |
| `control.get_input_value()` | Read raw DOM input value |
| `control.validate(value)` | Run validation on a value |
| `control.set_invalid()` | Mark the control as invalid (red border) |
| `control.set_disp_area(value)` | Set the read-only display value |

### Control Events

Controls support these event hooks in the `df` (field definition):

```javascript
let control = frappe.ui.form.make_control({
    parent: $wrapper,
    df: {
        fieldtype: "Data",
        fieldname: "email",
        label: "Email",
        // Event hooks:
        change() {
            // Fires when value changes (user input or set_value)
            console.log("New value:", this.get_value());
        },
        onchange() {
            // Alternative to change — same behavior
        },
        onchange_modified: true,  // Only fire change if value actually differs
    },
    render_input: true,
});
```

**Rule**: Use `change` for standalone controls. Use `onchange` in form field definitions. Both work, but `change` is the convention for standalone use.

### before_render Event

The `before_render` hook is available on form-level controls via Client Script:

```javascript
// In a Client Script for a DocType
frappe.ui.form.on("Sales Invoice", {
    before_render(frm) {
        // Runs before the form renders — configure controls here
        // Useful for setting up dynamic field properties
        frm.fields_dict.customer.df.read_only = 1;
    }
});
```

For standalone controls, use the constructor to configure before rendering, or call methods after `make_control()` but before appending to the visible DOM.

## Complete Control Type Reference

### Text Input Controls

| Fieldtype | Options | Notes |
|-----------|---------|-------|
| `Data` | `"Email"`, `"Name"`, `"Phone"`, `"URL"`, `"Barcode"` | Options add validation |
| `Small Text` | — | Textarea, 3-4 rows |
| `Text` | — | Textarea, larger |
| `Long Text` | — | Textarea, even larger |
| `Password` | — | Masked input |
| `Read Only` | — | Display-only text |

### Number Controls

| Fieldtype | Options | Notes |
|-----------|---------|-------|
| `Int` | — | Integer only |
| `Float` | — | Decimal number |
| `Currency` | `"currency_field"` or `"USD"` | Formatted with currency symbol |
| `Percent` | — | 0-100 with % symbol |

### Date/Time Controls

| Fieldtype | Options | Notes |
|-----------|---------|-------|
| `Date` | — | Calendar picker |
| `Time` | — | Time picker |
| `Datetime` | — | Combined date + time |
| `Date Range` | — | Returns `[start, end]` array |
| `Duration` | `"hide_days"` | Duration in seconds |

### Selection Controls

| Fieldtype | Options | Notes |
|-----------|---------|-------|
| `Select` | `"Option1\nOption2\nOption3"` or `["A","B","C"]` | Dropdown |
| `Link` | `"DocType Name"` | Autocomplete linked record |
| `Dynamic Link` | `"field_holding_doctype"` | Link with dynamic DocType |
| `Autocomplete` | `["val1","val2"]` | Free-text with suggestions |
| `MultiSelect` | `["opt1","opt2"]` | Multiple selection pills |
| `MultiCheck` | `[{label,value,checked}]` | Checkbox grid, `columns: N` |
| `Table MultiSelect` | `"Child DocType"` | Table-based multiselect |

### Rich Content Controls

| Fieldtype | Options | Notes |
|-----------|---------|-------|
| `Text Editor` | — | Quill WYSIWYG editor |
| `Markdown Editor` | — | Markdown with preview |
| `HTML Editor` | — | Raw HTML editing |
| `Code` | `"JavaScript"`, `"Python"`, `"HTML"`, `"CSS"`, `"JSON"` | Syntax highlighting, `wrap: true`, `max_lines: N` |
| `Comment` | — | Comment input with mentions |

### Media Controls

| Fieldtype | Options | Notes |
|-----------|---------|-------|
| `Attach` | — | File upload (any type) |
| `Attach Image` | — | Image upload with preview |
| `Image` | `"image_field"` | Display-only image |
| `Barcode` | — | Barcode display/scan |
| `Signature` | — | Draw signature |

### Special Controls

| Fieldtype | Options | Notes |
|-----------|---------|-------|
| `Check` | — | Checkbox (0/1) |
| `Color` | — | Color picker |
| `Rating` | — | Star rating (0-1 float) |
| `Geolocation` | — | Map with coordinates |
| `Icon` | — | Icon selector |
| `Button` | — | Action button, `btn_size: "xs"/"sm"/"lg"` |
| `HTML` | — | Raw HTML block |
| `Heading` | — | Section heading |
| `JSON` | — | JSON editor |
| `Phone` | — | Phone input with country code |

### Layout Controls (no data)

| Fieldtype | Notes |
|-----------|-------|
| `Section Break` | Start new section, `collapsible: 1` |
| `Column Break` | Start new column within section |
| `Tab Break` | Start new tab (v14+) |

## Custom Form Layouts with Standalone Controls

### Pattern: Dashboard Widget with Controls

```javascript
class MyDashboard {
    constructor(parent) {
        this.$wrapper = $('<div class="my-dashboard">').appendTo(parent);
        this.make_filters();
        this.make_chart_area();
    }

    make_filters() {
        let $filters = $('<div class="filter-row d-flex gap-2">').appendTo(this.$wrapper);

        this.company = frappe.ui.form.make_control({
            parent: $('<div>').appendTo($filters),
            df: {
                fieldtype: "Link",
                fieldname: "company",
                label: "Company",
                options: "Company",
                default: frappe.defaults.get_default("company"),
                change: () => this.refresh(),
            },
            render_input: true,
        });

        this.period = frappe.ui.form.make_control({
            parent: $('<div>').appendTo($filters),
            df: {
                fieldtype: "Select",
                fieldname: "period",
                label: "Period",
                options: ["Monthly", "Quarterly", "Yearly"],
                default: "Monthly",
                change: () => this.refresh(),
            },
            render_input: true,
        });
    }

    refresh() {
        let company = this.company.get_value();
        let period = this.period.get_value();
        if (company) {
            this.load_data(company, period);
        }
    }
}
```

### Pattern: Standalone Dialog with Custom Control Layout

```javascript
function show_custom_dialog() {
    let d = new frappe.ui.Dialog({ title: "Advanced Search", size: "large" });

    // Use make_control inside dialog body for custom layouts
    let $row = $('<div class="row">').appendTo(d.body);
    let $left = $('<div class="col-6">').appendTo($row);
    let $right = $('<div class="col-6">').appendTo($row);

    let search = frappe.ui.form.make_control({
        parent: $left,
        df: { fieldtype: "Data", fieldname: "search", label: "Search Term" },
        render_input: true,
    });

    let doctype_filter = frappe.ui.form.make_control({
        parent: $right,
        df: {
            fieldtype: "Link",
            fieldname: "doctype",
            label: "DocType",
            options: "DocType",
        },
        render_input: true,
    });

    let $results = $('<div class="search-results mt-3">').appendTo(d.body);

    d.set_primary_action("Search", () => {
        let term = search.get_value();
        let dt = doctype_filter.get_value();
        run_search(term, dt, $results);
    });

    d.show();
}
```

## Anti-Patterns

| Anti-Pattern | Correct Approach |
|---|---|
| `make_control` without `render_input: true` | ALWAYS pass `render_input: true` for standalone controls |
| Reading value before `set_value` Promise resolves | ALWAYS `await control.set_value(x)` or use `.then()` |
| Using `control.value` directly | Use `control.get_value()` — it applies formatting/parsing |
| Forgetting `options` on Link fields | ALWAYS set `options: "DocType"` — without it, the Link control has no target |
| Creating controls on hidden elements | Create AFTER the parent is visible, or call `control.refresh()` after showing |
