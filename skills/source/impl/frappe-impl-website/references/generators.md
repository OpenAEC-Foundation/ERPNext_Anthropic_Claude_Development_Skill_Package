# Website Generators — Portal Generators, Blog System & Custom Routing

Reference for `frappe-impl-website`. Covers how DocTypes auto-generate web pages, the blog system, and advanced routing patterns.

**Source**: [Frappe Portal Pages](https://docs.frappe.io/framework/user/en/portal-pages), [Frappe Hooks API](https://docs.frappe.io/framework/user/en/python-api/hooks)

---

## 1. Portal Generators — DocType Web Views

### Enabling has_web_view on a DocType

When a DocType has `has_web_view = 1`, each document becomes a publicly accessible web page. The DocType controller MUST extend `WebsiteGenerator` instead of `Document`.

**Required DocType fields:**

| Field | Type | Purpose |
|-------|------|---------|
| `route` | Data (hidden) | Auto-generated URL slug |
| `published` | Check | Controls public visibility |

**Controller setup:**

```python
from frappe.website.website_generator import WebsiteGenerator

class Article(WebsiteGenerator):
    website = frappe._dict(
        template="templates/generators/article.html",
        condition_field="published",
        page_title_field="title",
    )

    def get_context(self, context):
        # Add custom context for the web page
        context.related_articles = frappe.get_all(
            "Article",
            filters={"published": 1, "name": ("!=", self.name)},
            fields=["title", "route", "image"],
            order_by="creation desc",
            limit=5,
        )
```

**Rule**: ALWAYS include both `route` and `published` fields. NEVER expose documents without a condition_field check.

### The `website` Dict Properties

| Property | Type | Description |
|----------|------|-------------|
| `template` | str | Path to the Jinja template for rendering |
| `condition_field` | str | Field name that must be truthy for the page to be visible (typically `"published"`) |
| `page_title_field` | str | Field used as the HTML `<title>` |
| `no_cache` | bool | Disable caching for this generator |
| `no_sitemap` | bool | Exclude from sitemap.xml |
| `parent_website_route` | str | Parent route prefix for breadcrumbs |

### The `website_generators` Hook

Register DocTypes as website generators in `hooks.py`:

```python
# hooks.py
website_generators = ["Article", "Product", "FAQ"]
```

This tells Frappe to include these DocTypes in route resolution and sitemap generation.

**What happens when registered:**
1. Frappe creates routes for each document where `condition_field` is truthy
2. Documents appear in `/sitemap.xml`
3. Route conflicts are resolved by app installation order (last installed wins)

### Route Generation

Routes are auto-generated from the document name (slugified). You can customize:

```python
class Article(WebsiteGenerator):
    def before_save(self):
        # Custom route pattern: /articles/2024/my-article-title
        if not self.route:
            from frappe.utils import slugify
            year = self.creation.year if self.creation else frappe.utils.now_datetime().year
            self.route = f"articles/{year}/{slugify(self.title)}"
```

**Rule**: ALWAYS validate route uniqueness. Frappe raises `frappe.DuplicateEntryError` on duplicate routes.

### Template Structure

Templates for generators live in the app's `templates/generators/` directory:

```
myapp/
├── templates/
│   └── generators/
│       ├── article.html          # Single article page
│       └── article_row.html      # List item template (optional)
```

**Single item template (`article.html`):**

```html
{% extends "templates/web.html" %}

{% block page_content %}
<div class="article-page">
    <h1>{{ doc.title }}</h1>
    <p class="text-muted">{{ frappe.utils.format_date(doc.creation) }}</p>
    <div class="article-content">
        {{ doc.content }}
    </div>

    {% if related_articles %}
    <h3>Related Articles</h3>
    <ul>
        {% for article in related_articles %}
        <li><a href="/{{ article.route }}">{{ article.title }}</a></li>
        {% endfor %}
    </ul>
    {% endif %}
</div>
{% endblock %}
```

**List row template (`article_row.html`):**

```html
<div class="web-list-item">
    <a href="/{{ doc.route }}">
        <h4>{{ doc.title }}</h4>
        <p>{{ doc.description | truncate(150) }}</p>
    </a>
</div>
```

### The `get_context()` Method Pattern

`get_context` is the standard hook for injecting data into web page templates.

**For portal pages (www/ files):**

```python
# myapp/www/dashboard.py
import frappe

def get_context(context):
    context.title = "Dashboard"
    context.no_cache = 1
    context.show_sidebar = True

    # Fetch data for the template
    context.orders = frappe.get_all(
        "Sales Order",
        filters={"customer": frappe.session.user},
        fields=["name", "grand_total", "status"],
        order_by="creation desc",
        limit=20,
    )
```

**For WebsiteGenerator DocTypes:**

```python
class Product(WebsiteGenerator):
    def get_context(self, context):
        # 'self' is the document, also available as 'doc' in template
        context.variants = frappe.get_all(
            "Product Variant",
            filters={"parent_product": self.name, "published": 1},
            fields=["name", "title", "price", "route"],
        )
        context.metatags = {
            "title": self.title,
            "description": self.meta_description or self.title,
            "image": self.image,
        }
        # Parents for breadcrumb trail
        context.parents = [
            {"name": "Products", "route": "/products"},
        ]
```

**Rule**: ALWAYS set `context.no_cache = 1` for pages with user-specific data. NEVER serve cached pages with personal information.

---

## 2. Blog System

### Core DocTypes

| DocType | Purpose |
|---------|---------|
| **Blog Post** | Individual blog article |
| **Blog Category** | Grouping/taxonomy for posts |
| **Blog Settings** | Global blog configuration |
| **Blogger** | Author profile |

### Blog Post Structure

Blog Post has these key fields:

| Field | Type | Notes |
|-------|------|-------|
| `title` | Data | Post title |
| `blog_category` | Link | Required — links to Blog Category |
| `blogger` | Link | Author (Blogger DocType) |
| `published` | Check | Controls visibility |
| `published_on` | Date | REQUIRED for RSS and sorting |
| `content_type` | Select | "Markdown" or "Rich Text" |
| `content` | Text Editor | The post body (Rich Text) |
| `content_md` | Code | The post body (Markdown) |
| `meta_title` | Data | SEO title override |
| `meta_description` | Small Text | SEO description |
| `meta_image` | Attach Image | Social sharing image |
| `featured` | Check | Mark as featured (v15+) |

### Route Pattern

Blog routes follow this auto-generated pattern:

```
/blog/{blog-category-slug}/{post-slug}
```

Example: A post titled "Getting Started" in category "Tutorials" generates `/blog/tutorials/getting-started`.

The blog listing page is at `/blog`.

### Blog Settings

Configure via **Blog Settings** DocType:

| Setting | Effect |
|---------|--------|
| `blog_title` | Displayed on the blog listing page |
| `blog_introduction` | Introductory text on listing page |
| `browse_by_category` | Show category filter in sidebar |
| `comment_limit` | Max comments per post (0 = unlimited) |
| `allow_guest_to_comment` | Let unauthenticated users comment |

### RSS Feeds

Frappe auto-generates RSS feeds:

- **Blog RSS**: `/blog/feed` — includes all published Blog Posts
- RSS includes: title, description, published_on, link, author

**Rule**: ALWAYS set `published_on` date on Blog Posts. Posts without this date are excluded from RSS feeds and may sort incorrectly.

**Custom RSS**: For custom DocType RSS, implement in your controller:

```python
class Article(WebsiteGenerator):
    def get_feed(self):
        return self.title
```

### Custom Blog Templates

Override the default blog templates by placing files in your app:

```
myapp/templates/
├── includes/
│   └── blog/               # Override blog components
│       ├── blog.html        # Main blog listing page
│       └── blog_post.html   # Individual post page
```

Or use `base_template_map` in hooks.py for route-specific templates:

```python
base_template_map = {
    r"blog.*": "myapp/templates/custom_blog_base.html"
}
```

---

## 3. Custom Web Templates for DocTypes

### Web Template DocType (v13+)

Web Templates are reusable, configurable components for building web pages:

```python
# Creating a Web Template programmatically
web_template = frappe.get_doc({
    "doctype": "Web Template",
    "name": "Product Card",
    "template": """
        <div class="product-card">
            <img src="{{ image }}" alt="{{ title }}">
            <h3>{{ title }}</h3>
            <p>{{ description }}</p>
            <span class="price">{{ price }}</span>
        </div>
    """,
    "fields": [
        {"fieldname": "title", "fieldtype": "Data", "label": "Title"},
        {"fieldname": "description", "fieldtype": "Text", "label": "Description"},
        {"fieldname": "image", "fieldtype": "Attach Image", "label": "Image"},
        {"fieldname": "price", "fieldtype": "Data", "label": "Price"},
    ]
})
```

Web Templates are used inside Web Pages via the page builder interface, not directly in generators. For generator DocTypes, use standard Jinja templates (see Section 1).

---

## 4. website_route_rules — Custom Routing

### Basic Syntax

```python
# hooks.py
website_route_rules = [
    # Simple parameterized route
    {"from_route": "/projects/<name>", "to_route": "projects/project"},

    # Path parameter (captures slashes)
    {"from_route": "/kb/<path:name>", "to_route": "knowledge-base"},

    # Multiple parameters
    {"from_route": "/shop/<category>/<product>", "to_route": "shop/product"},
]
```

### How Route Rules Work

1. `from_route` — the public URL pattern (what users see)
2. `to_route` — the internal page that handles the request (www/ page or Web Page name)
3. Parameters from `from_route` become `frappe.form_dict` values in the handler

**Handler example:**

```python
# myapp/www/projects/project.py
import frappe

def get_context(context):
    project_name = frappe.form_dict.name
    project = frappe.get_doc("Project", project_name)

    if not project.published:
        raise frappe.DoesNotExistError

    context.project = project
    context.title = project.project_name
    context.no_cache = 1
```

### Related Routing Hooks

```python
# hooks.py

# Simple redirects (use INSTEAD of route_rules for redirects)
website_redirects = [
    {"source": "/old-page", "target": "/new-page"},
    {"source": r"/docs(/.*)?", "target": r"https://docs.example.com\1"},
]

# Dynamic route resolver
website_path_resolver = "myapp.routing.resolve_path"

# Dynamic routes beyond standard pages
get_web_pages_with_dynamic_routes = "myapp.routing.get_dynamic_routes"

# Custom 404 handler
website_catch_all = "not_found"
```

**Rule**: Use `website_route_rules` for parameterized routes. Use `website_redirects` for simple URL redirects. NEVER use route_rules when a redirect suffices.

---

## 5. Common Patterns

### Pattern A: Product Catalog

```python
# hooks.py
website_generators = ["Product"]

# product.py (DocType controller)
class Product(WebsiteGenerator):
    website = frappe._dict(
        template="templates/generators/product.html",
        condition_field="published",
        page_title_field="product_name",
    )

    def get_context(self, context):
        context.variants = frappe.get_all(
            "Product Variant",
            filters={"product": self.name, "published": 1},
            fields=["name", "variant_name", "price", "image"],
        )
        context.parents = [{"name": "Products", "route": "/products"}]

# hooks.py — listing page route
website_route_rules = [
    {"from_route": "/products", "to_route": "products"},
    {"from_route": "/products/<category>", "to_route": "products"},
]
```

### Pattern B: Knowledge Base

```python
# hooks.py
website_generators = ["KB Article"]
website_route_rules = [
    {"from_route": "/kb/<path:name>", "to_route": "knowledge-base"},
]

# kb_article.py
class KBArticle(WebsiteGenerator):
    website = frappe._dict(
        template="templates/generators/kb_article.html",
        condition_field="published",
        page_title_field="title",
    )

    def get_context(self, context):
        context.siblings = frappe.get_all(
            "KB Article",
            filters={"category": self.category, "published": 1},
            fields=["title", "route"],
        )
        context.parents = [
            {"name": "Knowledge Base", "route": "/kb"},
            {"name": self.category, "route": f"/kb/{frappe.scrub(self.category)}"},
        ]
```

### Pattern C: Customer Portal

```python
# hooks.py
role_home_page = {
    "Customer": "portal/dashboard",
}

portal_menu_items = [
    {"title": "Dashboard", "route": "/portal/dashboard", "role": "Customer"},
    {"title": "Orders", "route": "/portal/orders", "role": "Customer"},
    {"title": "Invoices", "route": "/portal/invoices", "role": "Customer"},
    {"title": "Support", "route": "/portal/tickets", "role": "Customer"},
]

# myapp/www/portal/dashboard.py
import frappe

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)

    context.title = "My Dashboard"
    context.no_cache = 1
    context.show_sidebar = True

    customer = frappe.db.get_value("Customer", {"user": frappe.session.user})
    context.orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer, "docstatus": 1},
        fields=["name", "grand_total", "status", "transaction_date"],
        order_by="transaction_date desc",
        limit=10,
    )
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|---|---|---|
| WebsiteGenerator without `condition_field` | All documents exposed publicly | ALWAYS set `condition_field="published"` |
| Missing `route` field on has_web_view DocType | Routes not generated, pages 404 | ALWAYS add hidden `route` Data field |
| Forgetting `website_generators` hook entry | DocType pages unreachable | ALWAYS register in hooks.py |
| Blog Post without `published_on` date | Missing from RSS, wrong sort order | ALWAYS set published_on |
| Using `website_route_rules` for simple redirects | Unnecessary complexity | Use `website_redirects` instead |
| Hardcoded routes in templates | Breaks when route changes | Use `{{ doc.route }}` or `frappe.utils.get_url()` |
| Cached pages with user-specific data | Data leaks between users | ALWAYS set `no_cache = 1` for personalized pages |
