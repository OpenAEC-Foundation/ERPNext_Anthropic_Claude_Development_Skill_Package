# Link Search API — frappe.desk.search

## search_link() — Main Entry Point

```python
@frappe.whitelist()
@http_cache(max_age=60, stale_while_revalidate=300)  # v15+ only
def search_link(
    doctype,                    # DocType to search
    txt,                        # Search text
    query=None,                 # Custom query function path
    filters=None,               # Additional filters (JSON)
    page_length=10,             # Results per page (v14: 20)
    searchfield=None,           # Override search field
    reference_doctype=None,     # Calling DocType (for context)
    ignore_user_permissions=False,
    *,
    link_fieldname=None         # v15+ only: calling field name
)
```

**Result format**: `LinkSearchResults` list of dicts:
```python
[{"value": "CUST-001", "description": "Acme Corp", "label": "Acme Corp"}]
```

## search_widget() — Internal Implementation

Called by `search_link()`. Builds the actual SQL query.

### Search Order

1. Check `standard_queries` hook for custom function
2. Build field list: `name` + `title_field` + `search_fields`
3. Filter by text across all searchable fields (OR conditions)
4. Apply `enabled`/`disabled` field filtering
5. Rank by relevance (prefix matches first)

### Allowed Search Field Types

Only these fieldtypes are searchable in link queries:
- Autocomplete, Data, Text, Small Text, Long Text
- Link, Select, Read Only, Text Editor

### Relevance Ranking

```sql
-- Prefix matches rank higher (value 0) than substring matches (value 1)
ORDER BY
  CASE WHEN name LIKE 'search%' THEN 0 ELSE 1 END,
  CASE WHEN title LIKE 'search%' THEN 0 ELSE 1 END,
  name ASC
```

## Configuring Search Fields

### DocType Properties

```json
{
    "search_fields": "customer_name, customer_group, territory",
    "title_field": "customer_name",
    "show_title_field_in_link": 1
}
```

- `search_fields` — Comma-separated list; `name` always included
- `title_field` — Displayed as description; auto-detects `title` field
- `show_title_field_in_link` — Shows title alongside name in link displays

### Via Customize Form

1. Open Customize Form for target DocType
2. Set "Search Fields" (comma-separated field names)
3. Set "Title Field" for display
4. Check "Show Title Field in Link"

## Custom Link Queries

### Method 1: standard_queries Hook (Global Override)

```python
# hooks.py
standard_queries = {
    "Customer": "my_app.queries.customer_query",
    "Item": "my_app.queries.item_query",
}
```

```python
# my_app/queries.py
@frappe.whitelist()
def customer_query(doctype, txt, searchfield, start, page_length, filters,
                   as_dict=False, reference_doctype=None,
                   ignore_user_permissions=False):
    """Custom customer search with active-only filtering."""
    conditions = []
    if txt:
        conditions.append(
            "(c.name LIKE %(txt)s OR c.customer_name LIKE %(txt)s)"
        )

    return frappe.db.sql("""
        SELECT c.name, c.customer_name AS description
        FROM `tabCustomer` c
        WHERE c.status = 'Active'
        {conditions}
        ORDER BY
            CASE WHEN c.name LIKE %(prefix)s THEN 0 ELSE 1 END,
            c.customer_name ASC
        LIMIT %(page_length)s OFFSET %(start)s
    """.format(conditions="AND " + " AND ".join(conditions) if conditions else ""),
    {
        "txt": f"%{txt}%",
        "prefix": f"{txt}%",
        "start": start,
        "page_length": page_length
    }, as_dict=True)
```

### Method 2: Per-Field Query (Client Script)

```javascript
// In setup() of form script
frappe.ui.form.on("Sales Order", {
    setup(frm) {
        // Simple filter
        frm.set_query("customer", () => ({
            filters: { status: "Active" }
        }));

        // Dynamic filter based on form data
        frm.set_query("item_code", "items", () => ({
            filters: {
                item_group: frm.doc.item_group,
                disabled: 0
            }
        }));

        // Custom query function
        frm.set_query("warehouse", () => ({
            query: "my_app.queries.warehouse_query",
            filters: { company: frm.doc.company }
        }));
    }
});
```

### Method 3: query Parameter on Link Field

```json
{
    "fieldname": "custom_field",
    "fieldtype": "Link",
    "options": "Item",
    "link_filters": "[[\"Item\", \"disabled\", \"=\", 0]]"
}
```

## Awesomebar

The Awesomebar (`awesome_bar.js`) is the global search bar in Desk.

### What It Searches

- DocType names and reports → navigation
- Recent pages → history
- Calculator expressions (numbers, `=` prefix)
- Tags (prefix `#`)
- Current list filter (when on list view)
- Global search dialog (fallback for text queries)

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+K` / `Cmd+K` | Focus Awesomebar |
| Arrow keys | Navigate results |
| Enter | Select result |
| Ctrl+Enter | Open in new tab |
| Escape | Close |
