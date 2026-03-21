# Workspace Anti-Patterns

Common mistakes when creating and shipping Frappe Workspaces, and how to avoid them.

---

## Anti-Pattern 1: Content/Child-Table Desync

### The Mistake

Manually editing the `content` JSON field without updating the corresponding child tables (or vice versa).

```python
# WRONG: Adding a chart to content but not to the charts child table
workspace.content = json.dumps([
    {"id": "abc", "type": "chart", "data": {"chart_name": "My Chart", "col": 12}}
])
workspace.save()  # Chart block appears but may not render correctly
```

### Why It Breaks

Frappe's Workspace Builder reads BOTH the `content` JSON (for layout) and the child tables (for component metadata). When they disagree:
- Blocks appear in the layout but show as empty/broken
- The Builder UI may remove orphaned entries on next save
- Export to JSON captures the inconsistent state

### The Fix

ALWAYS update both simultaneously:

```python
# CORRECT: Update content AND child table together
workspace.content = json.dumps([
    {"id": "abc", "type": "chart", "data": {"chart_name": "My Chart", "col": 12}}
])
workspace.append("charts", {"chart_name": "My Chart"})
workspace.save()
```

Or better: use the Workspace Builder UI, which keeps them in sync automatically.

---

## Anti-Pattern 2: Missing Fixture Dependencies

### The Mistake

Shipping a workspace JSON that references Number Cards, Dashboard Charts, or Custom HTML Blocks without including those documents as fixtures.

### Why It Breaks

On the target site, the workspace installs but the referenced components don't exist. Result:
- Number Card blocks show "Number Card 'X' not found"
- Chart blocks render as empty frames
- Custom blocks silently fail

### The Fix

ALWAYS declare dependencies in `hooks.py` fixtures:

```python
fixtures = [
    {"dt": "Number Card", "filters": [["module", "=", "My Module"]]},
    {"dt": "Dashboard Chart", "filters": [["module", "=", "My Module"]]},
    {"dt": "Custom HTML Block", "filters": [["name", "in", ["Block A", "Block B"]]]},
]
```

ALWAYS run `bench export-fixtures` after creating or modifying these documents.

---

## Anti-Pattern 3: Editing via DocType Form

### The Mistake

Navigating to `/app/workspace/My Workspace` (the DocType form view) and directly editing fields like `content`, `charts`, or `shortcuts`.

### Why It Breaks

- The DocType form does not validate content/child-table consistency
- The JSON editor in the form does not enforce the block schema
- Easy to create malformed JSON that crashes the Workspace Builder

### The Fix

ALWAYS use the Workspace Builder UI:
1. Navigate to Desk
2. Click the workspace in the sidebar
3. Click the **Edit** (pencil) icon
4. Use the visual builder to add/remove/reorder blocks

Exception: programmatic creation in install scripts or fixtures is fine — but use the documented API pattern with both content and child tables.

---

## Anti-Pattern 4: No Module Association

### The Mistake

Creating a workspace without setting the `module` field.

```python
workspace = frappe.new_doc("Workspace")
workspace.label = "Secret HR Dashboard"
# module not set!
workspace.insert()
```

### Why It Breaks

Without a module, the workspace is visible to ALL Desk users. There is no module-level access control. Even adding role restrictions provides only a secondary layer — the workspace still appears in API responses.

### The Fix

ALWAYS set the `module` field:

```python
workspace.module = "HR"  # Only users with HR module access see this
```

For sensitive workspaces, add role restrictions as a second layer:

```python
workspace.append("roles", {"role": "HR Manager"})
```

---

## Anti-Pattern 5: Workspace Name Collides with DocType

### The Mistake

Naming a workspace the same as an existing DocType (e.g., creating a workspace named "Sales Order").

### Why It Breaks

- URL routing conflicts: `/app/sales-order` could mean the workspace OR the DocType list
- Frappe v14/v15 may silently prefer one over the other
- v16 has auto-deduplication but the behavior can be confusing

### The Fix

ALWAYS use descriptive, unique names for workspaces:

```python
# WRONG
workspace.label = "Sales Order"

# CORRECT
workspace.label = "Sales Dashboard"
workspace.label = "Sales Overview"
workspace.label = "Order Management"
```

---

## Anti-Pattern 6: Shipping with for_user Set

### The Mistake

Exporting a workspace that has `for_user` set (e.g., it was created as a private workspace during development).

```json
{
    "name": "my_dashboard",
    "for_user": "admin@example.com",
    "label": "My Dashboard"
}
```

### Why It Breaks

On the target site, the workspace installs as a private workspace owned by a user that may not exist. No other users can see it.

### The Fix

ALWAYS verify the exported JSON does NOT contain `for_user`:

```bash
# Check before committing
grep -l "for_user" myapp/mymodule/workspace/*//*.json
```

If found, remove the field from the JSON or re-export from a public workspace.

---

## Anti-Pattern 7: Hardcoded sequence_id

### The Mistake

Setting `sequence_id` to a low fixed value (like 0, 1, or 2) which conflicts with core ERPNext workspaces.

### Why It Breaks

- Sidebar ordering becomes unpredictable
- Multiple apps competing for `sequence_id = 1` cause random ordering
- Users cannot reliably find workspaces in the expected position

### The Fix

Use a higher `sequence_id` for custom app workspaces:

```python
# WRONG
workspace.sequence_id = 1  # Conflicts with core workspaces

# CORRECT
workspace.sequence_id = 20  # Leaves room for core and other apps
```

Convention: core ERPNext uses 0-15; custom apps should use 20+.

---

## Anti-Pattern 8: Oversized Workspaces

### The Mistake

Putting too many components on a single workspace — 10+ charts, 20+ number cards, dozens of shortcuts.

### Why It Breaks

- Page load time increases dramatically (each chart/card is a separate API call)
- Mobile rendering becomes unusable
- Users cannot find relevant information in the noise

### The Fix

Follow the "one purpose per workspace" principle:

- **Overview workspace**: 3-4 KPI cards + 1-2 charts + key shortcuts
- **Detail workspace**: Focused on one area with relevant charts and lists
- Use sidebar hierarchy (`parent_page`) to organize related workspaces

Rule of thumb: if a workspace takes more than 3 seconds to load, split it.

---

## Anti-Pattern 9: Ignoring Permission on Components

### The Mistake

Creating Number Cards or Dashboard Charts that query DocTypes the workspace user may not have access to.

### Why It Breaks

- Frappe enforces permissions at the data layer — the component returns empty/error
- Users see "Insufficient Permission" errors on their dashboard
- The workspace appears broken even though it's a permission issue

### The Fix

ALWAYS ensure component permissions align with workspace roles:

```python
# If workspace is restricted to Sales User role,
# all Number Cards and Charts must query DocTypes
# that Sales User has read access to.

# Verify:
frappe.has_permission("Sales Order", "read", user="sales@example.com")
```

For mixed-permission dashboards, use separate workspaces per role (see Pattern 2 in SKILL.md).

---

## Quick Checklist: Avoid All Anti-Patterns

- [ ] Content JSON and child tables are in sync
- [ ] All referenced Number Cards, Charts, and Custom Blocks are in fixtures
- [ ] Workspace was edited via Builder UI (not DocType form)
- [ ] `module` field is set
- [ ] Workspace name does not collide with any DocType name
- [ ] `for_user` is NOT set in shipped JSON
- [ ] `sequence_id` is 20+ for custom app workspaces
- [ ] Workspace has ≤ 6 charts and ≤ 8 number cards
- [ ] All component queries respect the target user's permissions
