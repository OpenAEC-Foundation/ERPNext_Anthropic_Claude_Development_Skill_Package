# Document Methods Reference

> Complete documentatie van alle `doc.*` methodes beschikbaar in Frappe Document Controllers.

---

## Data Access Methodes

### doc.get(fieldname, default=None)

Veilig ophalen van veldwaarde met optionele default.

```python
# Basis gebruik
customer = self.get("customer")

# Met default waarde
status = self.get("status", "Draft")

# Voor child table velden
items = self.get("items", [])
```

### doc.as_dict(no_nulls=False, no_default_fields=False)

Serialiseert document naar dictionary.

```python
>>> doc.as_dict()
{
    'name': 'SO-00001',
    'doctype': 'Sales Order',
    'owner': 'Administrator',
    'creation': datetime.datetime(2025, 1, 13, 10, 30, 0),
    'modified': datetime.datetime(2025, 1, 13, 11, 0, 0),
    'customer': 'Customer A',
    'items': [{'item_code': 'ITEM-001', 'qty': 10}],
    ...
}

# Zonder null velden
>>> doc.as_dict(no_nulls=True)
# Alleen velden met waarden

# Zonder standaard velden (name, owner, creation, etc.)
>>> doc.as_dict(no_default_fields=True)
```

### doc.get_valid_dict(sanitize=True, convert_dates_to_str=False)

Retourneert dictionary met alleen geldige velden (gefilterd op permissions en docfield meta).

```python
# Voor API responses - alleen toegestane velden
valid_data = self.get_valid_dict()

# Voor export - dates als strings
export_data = self.get_valid_dict(convert_dates_to_str=True)
```

---

## Database Operaties

### doc.insert(ignore_permissions=False, ignore_links=False, ignore_if_duplicate=False, ignore_mandatory=False)

Insert nieuw document in database met alle hooks.

```python
# Standaard insert
doc = frappe.get_doc({
    "doctype": "Task",
    "subject": "New Task"
})
doc.insert()

# Met flags
doc.insert(
    ignore_permissions=True,     # Bypass write permissions
    ignore_links=True,           # Bypass link validatie
    ignore_if_duplicate=True,    # Geen error bij duplicate
    ignore_mandatory=True        # Bypass verplichte velden
)
```

### doc.save(ignore_permissions=False, ignore_version=True)

Save bestaand document met alle hooks.

```python
# Standaard save
doc.customer = "New Customer"
doc.save()

# Met flags
doc.save(
    ignore_permissions=True,     # Bypass write permissions
    ignore_version=True          # Geen version record maken
)
```

### doc.submit()

Submit document (docstatus 0 â†’ 1). Alleen voor submittable DocTypes.

```python
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.submit()  # Triggert before_submit, on_submit hooks
```

### doc.cancel()

Cancel document (docstatus 1 â†’ 2).

```python
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.cancel()  # Triggert before_cancel, on_cancel hooks
```

### doc.delete()

Verwijder document uit database.

```python
doc.delete()  # Triggert on_trash, after_delete hooks
```

### doc.reload()

Herlaad document uit database met laatste waarden.

```python
def on_update(self):
    # Andere code heeft misschien velden geÃ¼pdatet
    self.reload()
    print(self.modified_by)  # Meest recente waarde uit DB
```

---

## Low-Level Database Methodes

### doc.db_insert(*args, **kwargs)

**âš ï¸ WAARSCHUWING**: Directe database insert, bypast ALLE hooks.

```python
# ALLEEN gebruiken als je EXACT weet wat je doet
doc = frappe.get_doc({"doctype": "Log", "message": "test"})
doc.db_insert()  # Geen hooks, geen validatie

# âœ… Gebruik normaal insert() in plaats hiervan
doc.insert()
```

### doc.db_update()

**âš ï¸ WAARSCHUWING**: Directe database update, bypast ALLE hooks.

```python
# Bypass alle hooks - VERMIJD DIT
doc.some_field = "new value"
doc.db_update()

# âœ… Gebruik save() of db_set() in plaats hiervan
doc.save()
# of voor enkele velden:
frappe.db.set_value(doc.doctype, doc.name, "field", "value")
```

---

## Vergelijking met Vorige Versie

### doc.get_doc_before_save()

Retourneert document zoals het was vÃ³Ã³r huidige wijzigingen. Beschikbaar in `validate`, `on_update`, `on_change`, etc.

```python
def validate(self):
    old_doc = self.get_doc_before_save()
    
    if old_doc is None:
        # Dit is een NIEUW document
        self.created_by_validate = True
    else:
        # Dit is een UPDATE
        if old_doc.status != self.status:
            self.log_status_change(old_doc.status, self.status)
        
        if old_doc.customer != self.customer:
            frappe.throw(_("Cannot change customer after creation"))
```

**Let op**: Retourneert `None` voor nieuwe documenten (insert).

---

## Method Execution

### doc.run_method(method_name, *args, **kwargs)

Voert controller method uit en triggert ook bijbehorende hooks (doc_events, server scripts).

```python
# Voert validate uit + hooks.py doc_events + server scripts
doc.run_method('validate')

# Met argumenten
doc.run_method('custom_method', value1='test', notify=True)
```

### doc.queue_action(action, **kwargs)

Voert controller method uit in achtergrond (async).

```python
def on_submit(self):
    # Zware operatie async uitvoeren
    self.queue_action('send_emails', 
        emails=email_list, 
        message='Order submitted'
    )

def send_emails(self, emails, message):
    """Deze methode draait in background job."""
    for email in emails:
        frappe.sendmail(recipients=email, message=message)
```

---

## Realtime Updates

### doc.notify_update()

Publiceert realtime event dat document is gewijzigd (triggert form refresh in browser).

```python
# Na directe DB update - vertel frontend dat doc is gewijzigd
frappe.db.set_value('Sales Order', self.name, 'status', 'Closed')
self.notify_update()  # Browser refresht automatisch
```

---

## Comments & Communication

### doc.add_comment(comment_type, text, comment_email=None, comment_by=None)

Voegt commentaar toe aan document timeline.

```python
def on_submit(self):
    self.add_comment('Edit', 'Document submitted for processing')

def on_cancel(self):
    self.add_comment('Cancelled', f'Cancelled by {frappe.session.user}')
```

**Comment Types**: `Comment`, `Edit`, `Created`, `Submitted`, `Cancelled`, `Updated`, `Deleted`, `Assigned`, `Attachment`, `Info`, `Label`, `Shared`

---

## Child Table Methodes

### doc.append(fieldname, value=None)

Voeg rij toe aan child table.

```python
# Nieuwe rij met data
self.append("items", {
    "item_code": "ITEM-001",
    "qty": 10,
    "rate": 100
})

# Lege rij ophalen
row = self.append("items")
row.item_code = "ITEM-001"
row.qty = 10
```

### doc.extend(fieldname, values)

Voeg meerdere rijen toe aan child table.

```python
self.extend("items", [
    {"item_code": "ITEM-001", "qty": 10},
    {"item_code": "ITEM-002", "qty": 5},
])
```

### doc.set(fieldname, value)

Set veldwaarde (werkt voor alle veldtypes).

```python
# Enkele waarde
self.set("status", "Completed")

# Child table vervangen
self.set("items", [
    {"item_code": "ITEM-001", "qty": 10}
])
```

### doc.get(fieldname) voor child tables

```python
# Krijg alle items
for item in self.get("items"):
    print(item.item_code, item.qty)

# Filter items
high_value_items = [i for i in self.get("items") if i.amount > 1000]
```

---

## Tree DocType Methodes (NestedSet)

Alleen beschikbaar voor DocTypes met "Is Tree" enabled.

### doc.get_children()

```python
# Krijg directe kinderen
for child in self.get_children():
    print(child.name)
```

### doc.get_parent()

```python
# Krijg parent document
parent = self.get_parent()
if parent:
    print(f"Parent: {parent.name}")
```

### doc.get_ancestors()

```python
# Krijg alle ancestors (parents tot root)
for ancestor in self.get_ancestors():
    print(ancestor)
```

---

## Utility Methodes

### doc.is_new()

Check of document nieuw is (nog niet opgeslagen).

```python
def validate(self):
    if self.is_new():
        self.status = "Draft"
```

### doc.has_permission(permtype='read', user=None)

Check of gebruiker permission heeft.

```python
if not self.has_permission('write'):
    frappe.throw(_("You don't have permission to modify this document"))
```

### doc.get_title()

Krijg document title (gebruikt title_field configuratie).

```python
title = doc.get_title()  # Bijv. customer name voor Sales Order
```

### doc.get_url()

Krijg URL naar document in desk.

```python
url = doc.get_url()  # /app/sales-order/SO-00001
```

---

## Methode Signatures Samenvatting

| Methode | Parameters | Return | Beschrijving |
|---------|------------|--------|--------------|
| `get(fieldname, default)` | str, any | any | Veilig veld ophalen |
| `set(fieldname, value)` | str, any | None | Veld waarde zetten |
| `as_dict(no_nulls, no_default_fields)` | bool, bool | dict | Serialiseren |
| `get_valid_dict(sanitize, convert_dates)` | bool, bool | dict | Gefilterd serialiseren |
| `insert(**flags)` | kwargs | self | Nieuw doc opslaan |
| `save(**flags)` | kwargs | self | Doc updaten |
| `submit()` | - | self | Submit (0â†’1) |
| `cancel()` | - | self | Cancel (1â†’2) |
| `delete()` | - | None | Verwijderen |
| `reload()` | - | None | Herladen uit DB |
| `get_doc_before_save()` | - | Document/None | Vorige versie |
| `run_method(method, *args)` | str, args | any | Method + hooks uitvoeren |
| `queue_action(action, **kwargs)` | str, kwargs | None | Async uitvoeren |
| `notify_update()` | - | None | Realtime update |
| `add_comment(type, text)` | str, str | Comment | Commentaar toevoegen |
| `append(fieldname, value)` | str, dict | row | Child table rij |
| `is_new()` | - | bool | Check nieuw doc |
| `has_permission(permtype)` | str | bool | Permission check |
