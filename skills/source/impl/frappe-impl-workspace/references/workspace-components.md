# Workspace Components Reference

Complete reference for all component types that can be added to a Frappe Workspace.

---

## Shortcuts

Shortcuts provide quick-access buttons on the workspace. They are child-table entries on the Workspace DocType (`Workspace Shortcut`).

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `label` | Data | Display text on the shortcut button |
| `type` | Select | `DocType` / `Report` / `Page` / `URL` |
| `link_to` | Dynamic Link | Target document name (based on `type`) |
| `url` | Data | External URL (when `type` = URL) |
| `color` | Select | Button color: Grey, Blue, Orange, Green, Red, Yellow, Cyan, Pink |
| `format` | Data | Stats format string, e.g., `"{} Open"` |
| `stats_filter` | JSON | Filter for stats count display |
| `restrict_to_domain` | Link | Domain restriction |
| `icon` | Data | Icon name (optional) |

### Example: DocType Shortcut with Stats

```python
workspace.append("shortcuts", {
    "label": "Open Orders",
    "type": "DocType",
    "link_to": "Sales Order",
    "color": "Blue",
    "format": "{} Open",
    "stats_filter": json.dumps([
        ["Sales Order", "docstatus", "=", 1],
        ["Sales Order", "status", "=", "To Deliver and Bill"]
    ])
})
```

### Example: Report Shortcut

```python
workspace.append("shortcuts", {
    "label": "Sales Analytics",
    "type": "Report",
    "link_to": "Sales Analytics",
    "color": "Orange"
})
```

### Example: URL Shortcut

```python
workspace.append("shortcuts", {
    "label": "Documentation",
    "type": "URL",
    "url": "https://docs.erpnext.com",
    "color": "Grey"
})
```

### Rules

- ALWAYS set `color` — defaults to Grey but explicit is better
- ALWAYS match the `type` with the correct target field (`link_to` or `url`)
- Stats filters use the same format as frappe.get_list filters
- `format` string uses `{}` as placeholder for the count value

---

## Number Cards

Number Cards display single aggregate metrics. They are standalone documents (`Number Card` DocType) referenced from the workspace.

### Three Types

#### 1. Document Type (Aggregate)

Computes Count, Sum, Average, Min, or Max on a DocType field.

```python
card = frappe.new_doc("Number Card")
card.label = "Total Revenue"
card.document_type = "Sales Invoice"
card.function = "Sum"
card.aggregate_function_based_on = "grand_total"  # Required for Sum/Avg/Min/Max
card.filters_json = json.dumps([
    ["Sales Invoice", "docstatus", "=", 1],
    ["Sales Invoice", "posting_date", ">=", "2024-01-01"]
])
card.is_public = 1
card.show_percentage_stats = 1  # Show comparison with previous period
card.stats_time_interval = "Monthly"
card.insert()
```

| Field | Required | Description |
|-------|----------|-------------|
| `label` | Yes | Display name |
| `document_type` | Yes | Source DocType |
| `function` | Yes | `Count` / `Sum` / `Average` / `Min` / `Max` |
| `aggregate_function_based_on` | For Sum/Avg/Min/Max | Field to aggregate |
| `filters_json` | No | JSON filter array |
| `is_public` | Yes | Set to 1 for workspace use |
| `show_percentage_stats` | No | Show period-over-period comparison |
| `stats_time_interval` | No | `Daily` / `Weekly` / `Monthly` / `Yearly` |
| `color` | No | Card accent color |

#### 2. Report

Pulls a value from a Report's output.

```python
card = frappe.new_doc("Number Card")
card.label = "Monthly Profit"
card.type = "Report"
card.report_name = "Profit and Loss Statement"
card.report_field = "net_profit"
card.filters_json = json.dumps({"company": "My Company"})
card.is_public = 1
card.insert()
```

#### 3. Custom (Python Method)

Calls a whitelisted Python method that returns a numeric value.

```python
# In your app's Python code:
@frappe.whitelist()
def get_active_subscription_count():
    return frappe.db.count("Subscription", {"status": "Active"})

# Number Card document:
card = frappe.new_doc("Number Card")
card.label = "Active Subscriptions"
card.type = "Custom"
card.method = "myapp.api.get_active_subscription_count"
card.is_public = 1
card.insert()
```

### Rules

- ALWAYS set `is_public = 1` for cards used in public workspaces
- ALWAYS set `aggregate_function_based_on` when function is Sum/Average/Min/Max
- NEVER use `Count` with `aggregate_function_based_on` — Count ignores it
- Custom method MUST be decorated with `@frappe.whitelist()`

---

## Dashboard Charts

Dashboard Charts display visual data representations. They are standalone documents (`Dashboard Chart` DocType).

### Chart Types (data source)

| `chart_type` | Description |
|--------------|-------------|
| `Count` | Count documents over time |
| `Sum` | Sum a field over time |
| `Average` | Average a field over time |
| `Group By` | Group documents by a field |
| `Custom` | Whitelisted Python method |
| `Report` | Data from a Report |

### Visual Types

| `type` | Best for |
|--------|----------|
| `Line` | Time-series trends |
| `Bar` | Categorical comparison |
| `Percentage` | Part-of-whole (stacked bar) |
| `Pie` | Distribution (≤8 categories) |
| `Donut` | Distribution with center metric |
| `Heatmap` | Activity over calendar year |

### Example: Time-Series Count Chart

```python
chart = frappe.new_doc("Dashboard Chart")
chart.chart_name = "Monthly New Customers"
chart.chart_type = "Count"
chart.document_type = "Customer"
chart.based_on = "creation"  # Date field for time axis
chart.time_interval = "Monthly"
chart.timespan = "Last Year"
chart.type = "Line"  # Visual type
chart.color = "#4CAF50"
chart.is_public = 1
chart.insert()
```

### Example: Group By Chart

```python
chart = frappe.new_doc("Dashboard Chart")
chart.chart_name = "Orders by Status"
chart.chart_type = "Group By"
chart.document_type = "Sales Order"
chart.group_by_type = "Count"
chart.group_by_based_on = "status"
chart.type = "Donut"
chart.is_public = 1
chart.filters_json = json.dumps([["Sales Order", "docstatus", "=", 1]])
chart.insert()
```

### Example: Custom Chart (Python Method)

```python
# Python method must return:
# {"labels": [...], "datasets": [{"name": "...", "values": [...]}]}
@frappe.whitelist()
def get_pipeline_chart():
    stages = frappe.get_all("Opportunity",
        fields=["sales_stage", "count(name) as count"],
        group_by="sales_stage")
    return {
        "labels": [s.sales_stage for s in stages],
        "datasets": [{"name": "Opportunities", "values": [s.count for s in stages]}]
    }

# Chart document:
chart = frappe.new_doc("Dashboard Chart")
chart.chart_name = "Sales Pipeline"
chart.chart_type = "Custom"
chart.source = "myapp.api.get_pipeline_chart"
chart.type = "Bar"
chart.is_public = 1
chart.insert()
```

### Time Intervals

| `time_interval` | `timespan` options |
|------------------|--------------------|
| `Quarterly` | Last Quarter, Last Year |
| `Monthly` | Last Month, Last Quarter, Last Year, All Time |
| `Weekly` | Last Month, Last Quarter, Last Year |
| `Daily` | Last Week, Last Month, Last Quarter |

### Rules

- ALWAYS set `is_public = 1` for charts in public workspaces
- ALWAYS set `based_on` for time-series charts (Count/Sum/Average) — must be a Date/Datetime field
- NEVER use Pie/Donut for more than 8 categories — use Bar instead
- Custom chart methods MUST return `{"labels": [...], "datasets": [...]}`
- Group By charts do NOT need `based_on` — they group by the `group_by_based_on` field

---

## Custom HTML Blocks

Custom HTML Blocks allow embedding arbitrary HTML, JavaScript, and CSS into a workspace. They are standalone documents (`Custom HTML Block` DocType).

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Data | Unique identifier |
| `html` | Code (HTML) | HTML content |
| `script` | Code (JS) | JavaScript (runs in block context) |
| `style` | Code (CSS) | Scoped CSS |
| `private` | Check | If checked, only visible to creator |

### Example: Status Banner

```python
block = frappe.new_doc("Custom HTML Block")
block.name = "system-status-banner"
block.html = """
<div class="system-status-widget">
    <h4>System Status</h4>
    <div id="status-content">Loading...</div>
</div>
"""
block.script = """
frappe.call({
    method: "myapp.api.get_system_status",
    callback: function(r) {
        const el = document.getElementById("status-content");
        if (r.message) {
            el.innerHTML = `<span class="indicator-pill green">${r.message}</span>`;
        }
    }
});
"""
block.style = """
.system-status-widget {
    padding: 15px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    background: var(--card-bg);
}
"""
block.private = 0
block.insert()
```

### Adding to Workspace

```python
# Reference in workspace content JSON
content_block = {
    "id": frappe.generate_hash(length=10),
    "type": "custom_block",
    "data": {"custom_block_name": "system-status-banner", "col": 12}
}

# AND add child table entry
workspace.append("custom_blocks", {
    "custom_block_name": "system-status-banner"
})
```

### Rules

- ALWAYS use Frappe CSS variables (`var(--border-color)`, `var(--card-bg)`) for theme compatibility
- ALWAYS set `private = 0` for blocks used in public workspaces
- NEVER include `<script>` tags in the HTML field — use the `script` field instead
- NEVER load external scripts/stylesheets — use Frappe's built-in libraries or bundle via app assets
- Custom blocks ship as fixtures, NOT as part of the workspace JSON

---

## Quick Lists

Quick Lists show recent records for a DocType. They are child-table entries on the Workspace (`Workspace Quick List`).

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `label` | Data | Display heading |
| `document_type` | Link → DocType | Source DocType |
| `quick_list_filter` | JSON | Optional filter |

### Example

```python
workspace.append("quick_lists", {
    "label": "Recent Invoices",
    "document_type": "Sales Invoice",
    "quick_list_filter": json.dumps([
        ["Sales Invoice", "docstatus", "=", 1]
    ])
})
```

### Rules

- Quick Lists show the most recent 5 records by default
- Filters follow the standard frappe.get_list filter format
- Quick Lists respect the user's DocType permissions — no extra permission handling needed
