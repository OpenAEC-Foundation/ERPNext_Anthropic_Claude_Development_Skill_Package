# Tree View Reference

Extended reference for Frappe tree views, tree DocType configuration, and tree node operations.
Parent skill: `frappe-impl-ui-components`

## Tree DocType Configuration

A Tree DocType uses the Nested Set Model (NSM) to store hierarchical data. Frappe automatically adds `lft`, `rgt`, `old_parent`, and `is_group` fields.

### Step 1: Enable Tree on DocType

In the DocType definition, check **Is Tree** (`is_tree = 1`). This:
- Adds `lft` (Int), `rgt` (Int) columns for nested set ordering
- Adds `parent_{scrubbed_doctype}` field (Link to self) as the parent pointer
- Adds `old_parent` field (Data) for change detection
- Adds `is_group` field (Check) to distinguish branches from leaves
- Enables the Tree View route: `/app/{doctype}/view/tree`

### Step 2: Parent Field Convention

The parent field follows the naming convention: `parent_` + scrubbed DocType name.

| DocType | Parent Field |
|---------|-------------|
| `Item Group` | `parent_item_group` |
| `Territory` | `parent_territory` |
| `Cost Center` | `parent_cost_center` |
| `Department` | `parent_department` |

To override, set `nsm_parent_field` on the controller:

```python
class MyTreeDocType(NestedSet):
    nsm_parent_field = "custom_parent"  # Override default naming
```

### Step 3: Controller Setup

```python
# myapp/doctype/my_category/my_category.py
from frappe.utils.nestedset import NestedSet

class MyCategory(NestedSet):
    # nsm_parent_field = "parent_my_category"  # auto-detected by default

    def on_update(self):
        super().on_update()  # CRITICAL: calls update_nsm() for tree rebalancing
        # Custom logic after tree update

    def validate(self):
        super().validate()
        # Custom validation
```

**Rule**: ALWAYS inherit from `frappe.utils.nestedset.NestedSet` for tree DocTypes. ALWAYS call `super().on_update()` — without it, `lft`/`rgt` values are never updated and the tree breaks.

### Key NestedSet Methods (Server-Side)

| Method | Purpose |
|--------|---------|
| `get_ancestors()` | List of all parent nodes up to root |
| `get_parent()` | Immediate parent document |
| `get_children()` | Direct child documents |
| `is_ancestor_of(node)` | Check if current node is ancestor of another |
| `is_group` | Check field — `1` = can have children, `0` = leaf |

### Server-Side Tree Queries

```python
# Get all ancestors of a node
ancestors = frappe.get_all("Territory",
    filters={"lft": ["<", node.lft], "rgt": [">", node.rgt]},
    order_by="lft desc"
)

# Get all descendants of a node
descendants = frappe.get_all("Territory",
    filters={"lft": [">", node.lft], "rgt": ["<", node.rgt]},
    order_by="lft"
)

# Get direct children only
children = frappe.get_all("Territory",
    filters={"parent_territory": node.name},
    order_by="name"
)

# Rebuild tree if lft/rgt values get corrupted
from frappe.utils.nestedset import rebuild_tree
rebuild_tree("Territory")  # Recalculates all lft/rgt values
```

**Rule**: NEVER manually edit `lft` or `rgt` fields. ALWAYS use `rebuild_tree()` if the nested set is corrupted.

## frappe.views.TreeView — Client-Side Tree View

### Automatic Tree View

Any DocType with `is_tree = 1` and an `is_group` field automatically gets a tree view at `/app/{doctype}/view/tree`. No JavaScript configuration required.

### Custom Tree View Configuration

Create `{doctype}_tree.js` in the DocType directory to customize behavior:

```javascript
// myapp/doctype/my_category/my_category_tree.js
frappe.treeview_settings["My Category"] = {
    // Breadcrumb module
    breadcrumb: "Setup",

    // Custom title
    title: "Category Hierarchy",

    // Root label (top of tree)
    root_label: "All Categories",

    // Show expand all / collapse all buttons
    show_expand_all: true,

    // Backend methods (override defaults)
    get_tree_nodes: "myapp.api.get_category_nodes",
    add_tree_node: "myapp.api.add_category_node",

    // Toolbar filter fields
    filters: [
        {
            fieldtype: "Select",
            fieldname: "status",
            label: __("Status"),
            options: ["", "Active", "Archived"],
            default: "Active",
            // Fires on change — triggers tree reload
        },
        {
            fieldtype: "Link",
            fieldname: "company",
            label: __("Company"),
            options: "Company",
            default: frappe.defaults.get_default("company"),
        },
    ],

    // Custom fields in "Add Child" dialog
    fields: [
        { fieldtype: "Check", fieldname: "is_group", label: __("Is Group") },
        { fieldtype: "Data", fieldname: "category_name", label: __("Name"), reqd: 1 },
        { fieldtype: "Select", fieldname: "type", label: __("Type"),
          options: "\nType A\nType B" },
    ],

    // Fields to exclude from the Add Child dialog
    ignore_fields: ["old_parent"],

    // Custom label renderer
    get_label(node) {
        if (node.data && node.data.color) {
            return `<span style="color:${node.data.color}">${node.label}</span>`;
        }
        return __(node.label);
    },

    // Lifecycle callbacks
    onload(treeview) {
        // Runs once when tree initializes
        // treeview.page is available here
    },

    post_render(treeview) {
        // Runs after tree is fully rendered
    },

    onrender(node) {
        // Runs for each individual node after it renders
        if (node.data && node.data.disabled) {
            node.$tree_link.addClass("text-muted");
        }
    },

    on_get_node(nodes) {
        // Process node data before display
    },

    // Click handler
    click(node) {
        // Custom action when a node is clicked
    },

    // Custom view template (split view)
    view_template: "my_category_node_detail",

    // Custom toolbar buttons
    toolbar: [
        {
            label: __("Move"),
            condition(node) { return !node.is_root; },
            click(node) {
                move_category(node.label);
            },
            btnClass: "hidden-xs",
        },
    ],

    // Set to true to EXTEND default toolbar (Edit, Add Child, Rename, Delete)
    // Set to false/omit to REPLACE default toolbar entirely
    extend_toolbar: true,

    // Custom menu items (added to page menu dropdown)
    menu_items: [
        {
            label: __("Import Categories"),
            action() { frappe.set_route("data-import", "My Category"); },
            condition: "frappe.user.has_role('System Manager')",
        },
    ],
};
```

### TreeView Properties and Methods

The `frappe.views.TreeView` instance (accessible via `cur_tree.view_name === "Tree"`) exposes:

| Property/Method | Purpose |
|----------------|---------|
| `treeview.tree` | The underlying `frappe.ui.Tree` instance |
| `treeview.page` | The `frappe.ui.Page` instance |
| `treeview.doctype` | The DocType name |
| `treeview.body` | jQuery wrapper for the tree container |
| `treeview.make_tree()` | Rebuild the tree (full refresh) |
| `treeview.new_node()` | Open the "Add Child" dialog |
| `treeview.rebuild_tree()` | Calls `frappe.utils.nestedset.rebuild_tree` |

### frappe.ui.Tree — Low-Level Tree API

The `frappe.ui.Tree` class handles rendering and node management:

```javascript
// Constructor options
let tree = new frappe.ui.Tree({
    parent: $container,          // jQuery container
    label: "Root",               // Root node label
    root_value: "Root",          // Root node value
    expandable: true,            // Allow expand/collapse
    with_skeleton: true,         // Show loading skeleton
    args: { doctype: "Territory" },  // Extra args for API calls
    method: "frappe.desk.treeview.get_children",  // Backend method
    toolbar: [...],              // Toolbar button definitions
    icon_set: {                  // Custom icons (optional)
        open: '<i class="fa fa-folder-open"></i>',
        closed: '<i class="fa fa-folder"></i>',
        leaf: '<i class="fa fa-file"></i>',
    },
    // Callbacks
    get_label(node) { return node.label; },
    on_render(node) { /* after node renders */ },
    on_click(node) { /* node clicked */ },
    on_get_node(data) { /* data received from server */ },
    on_node_render(node, deep) { /* after load_children completes */ },
});
```

| Method | Purpose |
|--------|---------|
| `tree.get_selected_node()` | Get currently selected TreeNode |
| `tree.set_selected_node(node)` | Set selection |
| `tree.load_children(node, deep)` | Load children; `deep=true` loads all descendants |
| `tree.reload_node(node)` | Reload a specific node's children |
| `tree.toggle()` | Toggle selected node expand/collapse |
| `tree.refresh()` | Refresh selected node's parent |
| `tree.add_node(parent_node, data)` | Add a child node to the DOM |
| `tree.nodes` | Object map: `{ label: TreeNode }` |
| `tree.root_node` | The root TreeNode instance |

### TreeNode Properties

Each node in the tree is a `TreeNode` instance:

| Property | Type | Description |
|----------|------|-------------|
| `node.label` | String | Node identifier |
| `node.data` | Object | Server data (`value`, `expandable`, etc.) |
| `node.parent_label` | String | Parent's label |
| `node.parent_node` | TreeNode | Parent TreeNode reference |
| `node.expandable` | Boolean | Can have children |
| `node.is_root` | Boolean | Is the root node |
| `node.loaded` | Boolean | Children have been fetched |
| `node.expanded` | Boolean | Currently expanded |
| `node.$tree_link` | jQuery | The clickable link element |
| `node.$ul` | jQuery | The children container |
| `node.$toolbar` | jQuery | The toolbar buttons (if any) |

## Tree Node Operations

### Add a Child Node

```javascript
// Via the built-in dialog (recommended)
cur_tree.view_name; // Access current tree view
// Click "New" button or use the "Add Child" toolbar button

// Programmatic: call the backend
frappe.call({
    method: "frappe.desk.treeview.add_node",
    args: {
        doctype: "Territory",
        parent: "India",  // parent node label
        is_group: 1,
        territory_name: "North India",
    },
    callback(r) {
        if (!r.exc) {
            // Reload the parent node to show the new child
            let parent_node = cur_tree.tree.nodes["India"];
            cur_tree.tree.load_children(parent_node);
        }
    }
});
```

### Move a Node (Re-parent)

Moving a node means changing its parent. The nested set is automatically rebalanced on `on_update`:

```python
# Server-side: move "North India" under "Asia"
doc = frappe.get_doc("Territory", "North India")
doc.parent_territory = "Asia"
doc.save()  # on_update → update_nsm() rebalances lft/rgt
```

```javascript
// Client-side
frappe.call({
    method: "frappe.client.set_value",
    args: {
        doctype: "Territory",
        name: "North India",
        fieldname: "parent_territory",
        value: "Asia",
    },
    callback() {
        // Refresh the tree view
        cur_tree && cur_tree.make_tree();
    }
});
```

**Rule**: NEVER move a node to one of its own descendants — this creates a circular reference. The NestedSet class validates this and raises `NestedSetRecursionError`.

### Delete a Node

```javascript
// Via toolbar "Delete" button (built-in)
// Or programmatically:
frappe.model.delete_doc("Territory", "North India", function() {
    // Refresh parent node
    let parent_node = cur_tree.tree.nodes["India"];
    if (parent_node) cur_tree.tree.load_children(parent_node);
});
```

**Rule**: NEVER delete a group node that has children — Frappe raises `NestedSetChildExistsError`. ALWAYS delete or move children first.

### Rebuild Corrupted Tree

If `lft`/`rgt` values become inconsistent (e.g., after direct SQL edits):

```python
# Server-side
from frappe.utils.nestedset import rebuild_tree
rebuild_tree("Territory")

# Or via API
frappe.call({
    method: "frappe.utils.nestedset.rebuild_tree",
    args: { doctype: "Territory" }
});
```

The "Rebuild Tree" option also appears in the tree view's menu dropdown for System Managers.

## Common Tree Patterns

### Pattern: Chart of Accounts Tree

ERPNext's Chart of Accounts is the canonical tree example:

```javascript
// erpnext/accounts/doctype/account/account_tree.js
frappe.treeview_settings["Account"] = {
    breadcrumb: "Accounts",
    title: __("Chart of Accounts"),
    get_tree_root: false,  // Uses company-based root
    root_label: "Accounts",
    filters: [
        {
            fieldtype: "Link",
            fieldname: "company",
            label: __("Company"),
            options: "Company",
            default: frappe.defaults.get_default("company"),
        },
    ],
    fields: [
        { fieldtype: "Data", fieldname: "account_name", label: __("Account Name"), reqd: 1 },
        { fieldtype: "Check", fieldname: "is_group", label: __("Is Group") },
        { fieldtype: "Link", fieldname: "account_type", label: __("Account Type"),
          options: "Account Type" },
    ],
    get_label(node) {
        // Show account number + name
        if (node.data && node.data.account_number) {
            return `${node.data.account_number} - ${node.label}`;
        }
        return node.label;
    },
};
```

### Pattern: Territory / Region Tree

```javascript
frappe.treeview_settings["Territory"] = {
    breadcrumb: "Selling",
    title: __("Territory"),
    // Uses default toolbar (Edit, Add Child, Rename, Delete)
    // No custom fields needed — territory_name is auto-detected as mandatory
};
```

### Pattern: Custom Tree with Split View

Display node details alongside the tree:

```javascript
frappe.treeview_settings["My Category"] = {
    // view_template renders in a side panel when a node is clicked
    view_template: "my_category_detail",

    // The template receives { data: node.data, doctype: "My Category" }
    // Create: myapp/doctype/my_category/my_category_detail.html
};
```

Template file (`my_category_detail.html`):

```html
<div class="category-detail">
    <h4>{{ data.value }}</h4>
    <p>{{ data.description || "No description" }}</p>
    <a href="/app/my-category/{{ data.value }}" class="btn btn-default btn-sm">
        {{ __("Open") }}
    </a>
</div>
```

## Anti-Patterns

| Anti-Pattern | Correct Approach |
|---|---|
| Not calling `super().on_update()` in tree controller | ALWAYS call `super().on_update()` — it triggers nested set rebalancing |
| Manually editing `lft`/`rgt` via SQL | Use `rebuild_tree()` after any direct database changes |
| Deleting a group with children | Move or delete children first, then delete the group |
| Moving a node under its own descendant | NestedSet validates this — but design your UI to prevent it |
| Missing `is_group` field on DocType | Tree DocTypes MUST have `is_group` (Check) — without it, `TreeFactory` rejects the view |
| Forgetting `is_tree = 1` on DocType | Without it, no tree view route is generated |
| Using `parent` as field name | `parent` is reserved by Frappe for child table links — tree uses `parent_{doctype}` |
