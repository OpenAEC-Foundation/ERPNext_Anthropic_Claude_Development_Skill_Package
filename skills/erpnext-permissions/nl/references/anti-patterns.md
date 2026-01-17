# Permission Anti-Patterns

## ❌ Rol Checken in Plaats van Permission

```python
# ❌ FOUT - Bypass permission systeem
if "Sales Manager" in frappe.get_roles():
    doc.save()

# ✅ CORRECT - Gebruik permission systeem
if frappe.has_permission(doc.doctype, "write", doc):
    doc.save()
```

**Waarom fout**: Hardcoded rol checks negeren user permissions, sharing, en custom permission hooks.

---

## ❌ Hardcoded Administrator Bypass

```python
# ❌ FOUT - Security risico
if frappe.session.user == "Administrator":
    # doe alles

# ✅ CORRECT - Check daadwerkelijke permission
if frappe.has_permission("DocType", "write"):
    # proceed
```

**Waarom fout**: Administrator account moet alleen voor setup worden gebruikt. Code moet werken met normale gebruikers.

---

## ❌ Permissions Negeren Zonder Reden

```python
# ❌ FOUT - Geen documentatie waarom
doc.save(ignore_permissions=True)

# ✅ CORRECT - Gedocumenteerde reden
# Systeem-gegenereerde update die elevated privileges vereist
doc.flags.ignore_permissions = True
doc.db_set("system_field", value, update_modified=False)
```

**Waarom fout**: Maakt debugging onmogelijk en creëert security risico's.

---

## ❌ SQL Injection in Permission Query

```python
# ❌ FOUT - SQL injection kwetsbaarheid
def my_query(user):
    return f"owner = '{user}'"  # NOOIT doen

# ✅ CORRECT - Escaped input
def my_query(user):
    return f"owner = {frappe.db.escape(user)}"
```

**Waarom fout**: Kwaadwillende usernames kunnen SQL injecteren.

---

## ❌ get_all Gebruiken met Permission Verwachting

```python
# ❌ FOUT - get_all negeert user permissions
orders = frappe.get_all("Sales Order", filters={"status": "Draft"})
# ^ User ziet ALLE orders, niet alleen die van zijn territory

# ✅ CORRECT - get_list past user permissions toe
orders = frappe.get_list("Sales Order", filters={"status": "Draft"})
# ^ User ziet alleen orders in zijn territory
```

**Waarom fout**: `get_all` is bedoeld voor systeem operaties, niet user-facing queries.

---

## ❌ Permission Check na Actie

```python
# ❌ FOUT - Eerst doen, dan checken
doc.status = "Approved"
doc.save()
if not frappe.has_permission(doc.doctype, "write", doc):
    frappe.throw("Oops, not permitted")

# ✅ CORRECT - Check VOORDAT je handelt
if not frappe.has_permission(doc.doctype, "write", doc):
    frappe.throw(_("Not permitted"), frappe.PermissionError)
doc.status = "Approved"
doc.save()
```

**Waarom fout**: Actie is al uitgevoerd voordat permission wordt gecontroleerd.

---

## ❌ True Retourneren in has_permission Hook (v14)

```python
# ❌ FOUT in v14 - True heeft GEEN effect
def my_permission_hook(doc, ptype, user):
    if user == "special@user.com":
        return True  # Dit doet NIETS in v14!

# ✅ CORRECT - Hook kan alleen WEIGEREN
def my_permission_hook(doc, ptype, user):
    if some_condition:
        return False  # Weiger permission
    return None  # Ga door met standaard checks
```

**Waarom fout**: In v14 kan de hook alleen permission weigeren, niet toekennen.

---

## ❌ User Permissions Niet Testen

```python
# ❌ FOUT - Alleen testen als admin
# Development altijd met Administrator account

# ✅ CORRECT - Test met normale user accounts
# Maak test users met specifieke rollen
# Verifieer dat user permissions correct worden toegepast
```

**Waarom fout**: Permissions issues worden pas ontdekt in productie.

---

## ❌ Excessive Permission Ignoring

```python
# ❌ FOUT - Overal permissions negeren
@frappe.whitelist()
def my_api():
    doc = frappe.get_doc("Sales Order", "SO-001")
    doc.flags.ignore_permissions = True
    linked = frappe.get_doc("Customer", doc.customer)
    linked.flags.ignore_permissions = True
    # ... meer ignore_permissions

# ✅ CORRECT - Minimaal ignoren, liefst helemaal niet
@frappe.whitelist()
def my_api():
    # API is al gewhitelisted, normale user moet rechten hebben
    doc = frappe.get_doc("Sales Order", "SO-001")
    doc.check_permission("read")
    # Werk met normale permissions
```

**Waarom fout**: Als je overal permissions moet negeren, is je permission model verkeerd.

---

## ❌ Permission Logic in Client Script

```python
# ❌ FOUT - Client-side permission check
frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        if (frappe.user_roles.includes("Manager")) {
            frm.set_df_property("discount", "hidden", 0);
        }
    }
});
// ^ Kan worden omzeild via browser console

# ✅ CORRECT - Server-side via perm levels
// Zet discount veld op permlevel 1 in DocType
// Geef alleen Manager rol toegang tot level 1
```

**Waarom fout**: Client-side checks kunnen door eindgebruikers worden omzeild.

---

## ❌ Vergeten Cache te Clearen na Permission Wijzigingen

```python
# ❌ FOUT - Permission wijziging zonder cache clear
add_permission("Sales Order", "New Role", 0)
# Wijziging werkt niet direct!

# ✅ CORRECT - Clear cache na wijzigingen
add_permission("Sales Order", "New Role", 0)
frappe.clear_cache()
```

**Waarom fout**: Frappe cached permissions, wijzigingen worden pas actief na cache clear.
