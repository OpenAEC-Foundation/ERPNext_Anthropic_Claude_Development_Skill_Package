# Permission Anti-Patterns

## ❌ Checking Role Instead of Permission

```python
# ❌ WRONG - Bypasses permission system
if "Sales Manager" in frappe.get_roles():
    doc.save()

# ✅ CORRECT - Uses permission system
if frappe.has_permission(doc.doctype, "write", doc):
    doc.save()
```

**Why wrong**: Hardcoded role checks ignore user permissions, sharing, and custom permission hooks.

---

## ❌ Hardcoded Administrator Bypass

```python
# ❌ WRONG - Security risk
if frappe.session.user == "Administrator":
    # do anything

# ✅ CORRECT - Check actual permission
if frappe.has_permission("DocType", "write"):
    # proceed
```

**Why wrong**: Administrator account should only be used for setup. Code must work with normal users.

---

## ❌ Ignoring Permissions Without Reason

```python
# ❌ WRONG - No documentation why
doc.save(ignore_permissions=True)

# ✅ CORRECT - Documented reason
# System-generated update that requires elevated privileges
doc.flags.ignore_permissions = True
doc.db_set("system_field", value, update_modified=False)
```

**Why wrong**: Makes debugging impossible and creates security risks.

---

## ❌ SQL Injection in Permission Query

```python
# ❌ WRONG - SQL injection vulnerability
def my_query(user):
    return f"owner = '{user}'"  # NEVER do this

# ✅ CORRECT - Escaped input
def my_query(user):
    return f"owner = {frappe.db.escape(user)}"
```

**Why wrong**: Malicious usernames can inject SQL.

---

## ❌ Using get_all with Permission Expectation

```python
# ❌ WRONG - get_all ignores user permissions
orders = frappe.get_all("Sales Order", filters={"status": "Draft"})
# ^ User sees ALL orders, not just those in their territory

# ✅ CORRECT - get_list applies user permissions
orders = frappe.get_list("Sales Order", filters={"status": "Draft"})
# ^ User sees only orders in their territory
```

**Why wrong**: `get_all` is intended for system operations, not user-facing queries.

---

## ❌ Permission Check After Action

```python
# ❌ WRONG - Act first, check later
doc.status = "Approved"
doc.save()
if not frappe.has_permission(doc.doctype, "write", doc):
    frappe.throw("Oops, not permitted")

# ✅ CORRECT - Check BEFORE acting
if not frappe.has_permission(doc.doctype, "write", doc):
    frappe.throw(_("Not permitted"), frappe.PermissionError)
doc.status = "Approved"
doc.save()
```

**Why wrong**: Action is already performed before permission is checked.

---

## ❌ Returning True in has_permission Hook (v14)

```python
# ❌ WRONG in v14 - True has NO effect
def my_permission_hook(doc, ptype, user):
    if user == "special@user.com":
        return True  # This does NOTHING in v14!

# ✅ CORRECT - Hook can only DENY
def my_permission_hook(doc, ptype, user):
    if some_condition:
        return False  # Deny permission
    return None  # Continue with standard checks
```

**Why wrong**: In v14, the hook can only deny permission, not grant it.

---

## ❌ Not Testing User Permissions

```python
# ❌ WRONG - Only testing as admin
# Development always with Administrator account

# ✅ CORRECT - Test with normal user accounts
# Create test users with specific roles
# Verify that user permissions are correctly applied
```

**Why wrong**: Permission issues are only discovered in production.

---

## ❌ Excessive Permission Ignoring

```python
# ❌ WRONG - Ignoring permissions everywhere
@frappe.whitelist()
def my_api():
    doc = frappe.get_doc("Sales Order", "SO-001")
    doc.flags.ignore_permissions = True
    linked = frappe.get_doc("Customer", doc.customer)
    linked.flags.ignore_permissions = True
    # ... more ignore_permissions

# ✅ CORRECT - Minimal ignoring, preferably none
@frappe.whitelist()
def my_api():
    # API is already whitelisted, normal user should have rights
    doc = frappe.get_doc("Sales Order", "SO-001")
    doc.check_permission("read")
    # Work with normal permissions
```

**Why wrong**: If you need to ignore permissions everywhere, your permission model is wrong.

---

## ❌ Permission Logic in Client Script

```python
# ❌ WRONG - Client-side permission check
frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        if (frappe.user_roles.includes("Manager")) {
            frm.set_df_property("discount", "hidden", 0);
        }
    }
});
// ^ Can be bypassed via browser console

# ✅ CORRECT - Server-side via perm levels
// Set discount field to permlevel 1 in DocType
// Grant only Manager role access to level 1
```

**Why wrong**: Client-side checks can be bypassed by end users.

---

## ❌ Forgetting to Clear Cache After Permission Changes

```python
# ❌ WRONG - Permission change without cache clear
add_permission("Sales Order", "New Role", 0)
# Change doesn't work immediately!

# ✅ CORRECT - Clear cache after changes
add_permission("Sales Order", "New Role", 0)
frappe.clear_cache()
```

**Why wrong**: Frappe caches permissions, changes only become active after cache clear.
