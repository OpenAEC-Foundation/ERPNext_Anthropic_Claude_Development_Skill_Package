# Global & Website Search

## Global Search

### How It Works

1. Fields with `in_global_search=1` are indexed into `__global_search` table
2. Changes queued via Redis, synced every 15 minutes
3. Search uses DB-native fulltext: MariaDB `MATCH...AGAINST`, PostgreSQL `TSVECTOR`
4. Results are permission-filtered

### Indexing

```python
from frappe.utils.global_search import (
    rebuild_for_doctype,
    rebuild,
    update_global_search
)

# Rebuild index for one DocType
rebuild_for_doctype("Sales Order")

# Rebuild entire index
rebuild()

# Queue single document update (auto-called on doc save)
update_global_search(doc)
```

### hooks.py Configuration

```python
# Define which doctypes appear in global search results
global_search_doctypes = {
    "Default": [
        {"doctype": "Contact"},
        {"doctype": "Customer"},
        {"doctype": "Sales Order"},
        {"doctype": "Item"},
    ]
}
```

### API

```python
from frappe.utils.global_search import search, web_search

# Desk search (permission-filtered)
results = search("acme corp", start=0, limit=20, doctype="Customer")

# Website search (published docs only, guest-accessible)
results = web_search("product guide", scope="/products", start=0, limit=20)
```

### Important Limitations

- **15-minute sync delay** — Changes aren't immediately searchable
- **Redis dependency** — Queue fails gracefully to direct sync if Redis unavailable
- **Batch size** — 50,000 records per insert batch
- **HTML sanitized** — Script/style tags stripped from indexed content

---

## WebsiteSearch (Whoosh-based)

### Overview

File-based search using Whoosh library. Indexes website pages for visitor search.

### Schema

```python
# Default fields
name = ID(stored=True)      # Page path
title = TEXT(stored=True)    # Page title
content = TEXT(stored=True)  # Page content (HTML stripped)
```

### Index Location

```
sites/{site}/indexes/{index_name}/
```

### API

```python
from frappe.search.website_search import WebsiteSearch

ws = WebsiteSearch()
ws.build_index()                          # Full rebuild
ws.update_index(document)                 # Update single doc
results = ws.search("query", limit=20)    # Search
```

### Web API

```
/api/method/frappe.search.web_search?text=query&scope=/blog&limit=20
```

### What Gets Indexed

- Static pages in `www/` directory
- Published documents with `has_web_view=1` on their DocType
- Pages rendered as Guest user (respects publish status)

---

## SQLiteSearch (FTS5) — v15+

### Architecture

Uses SQLite FTS5 virtual tables for advanced full-text search.

### Creating a Custom Search Index

```python
# my_app/search.py
from frappe.search.sqlite_search import SQLiteSearch

class TaskSearch(SQLiteSearch):
    # Define metadata columns (filterable, not full-text)
    INDEX_SCHEMA = {
        "metadata_fields": ["project", "owner", "status", "priority"],
        "tokenizer": "unicode61 remove_diacritics 2 tokenchars '-_'",
    }

    # Define which DocTypes and fields to index
    INDEXABLE_DOCTYPES = {
        "Task": {
            "fields": [
                "name",                    # Indexed as-is
                {"title": "subject"},      # Map "subject" field → "title" column
                {"content": "description"},# Map "description" → "content"
                "modified",                # For recency scoring
                "project",                 # Metadata field
                "status",
                "priority",
            ],
            "filters": {"status": ("!=", "Cancelled")}  # Exclude cancelled
        },
        "Project": {
            "fields": [
                "name",
                {"title": "project_name"},
                {"content": "notes"},
                "modified",
                "status",
            ],
        }
    }

    def get_search_filters(self, query, scope=None):
        """Permission filtering — restrict results to user's projects."""
        user_projects = frappe.get_all("Project",
            filters={"owner": frappe.session.user},
            pluck="name"
        )
        if user_projects:
            return {"project": ("in", user_projects)}
        return {}

    @SQLiteSearch.scoring_function
    def boost_high_priority(self, doc, base_score):
        """Custom scoring — boost high priority tasks."""
        if doc.get("priority") == "High":
            return base_score * 1.5
        return base_score
```

### Register in hooks.py

```python
# hooks.py
sqlite_search = ['my_app.search.TaskSearch']
```

### Automatic Scheduling

Once registered, Frappe handles:
- **Build index**: Every 3 hours (`build_index_if_not_exists`)
- **Process queue**: Every 5 minutes (`index_docs_in_queue`)
- **Doc events**: `on_update` → update index, `on_trash` → delete from index

### Built-in Features

| Feature | Description |
|---------|-------------|
| Spelling correction | Trigram Jaccard (70%) + sequence similarity (30%) |
| Recency boosting | 1.8x (24h), 1.5x (7d), 1.2x (30d), 1.1x (90d) |
| Resumable indexing | Progress tracked in `search_index_progress` table |
| Atomic replacement | Builds in temp DB, swaps on completion |
| Snippet generation | 64-char context snippets around matches |
| Title exact match | 5x boost for exact title matches |

### Constants

```python
MAX_SEARCH_RESULTS = 100
SNIPPET_LENGTH = 64
MIN_WORD_LENGTH = 4
TITLE_EXACT_MATCH_BOOST = 5.0
```

---

## Search Hooks Summary

| Hook | Purpose | Example |
|------|---------|---------|
| `standard_queries` | Override link field search per DocType | `{"Customer": "app.queries.customer_query"}` |
| `global_search_doctypes` | Define global search DocTypes | `{"Default": [{"doctype": "Contact"}]}` |
| `sqlite_search` | Register FTS5 search classes [v15+] | `['my_app.search.TaskSearch']` |
| `permission_query_conditions` | Filter search results by permissions | `{"ToDo": "app.perms.todo_filter"}` |
