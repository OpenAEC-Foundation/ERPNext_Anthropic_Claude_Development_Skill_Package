# Server Script Events - Complete Referentie

## Inhoudsopgave

1. [Event Name Mapping](#event-name-mapping)
2. [Document Lifecycle Volgorde](#document-lifecycle-volgorde)
3. [Event Details](#event-details)
4. [Speciale Events](#speciale-events)

---

## Event Name Mapping

### KRITIEK: UI Namen vs Interne Hooks

De Server Script UI toont andere event namen dan de interne Frappe hooks. Dit is essentieel om te begrijpen voor correcte werking:

| Server Script UI | Interne Hook | Controller Method |
|------------------|--------------|-------------------|
| Before Insert | `before_insert` | `before_insert()` |
| After Insert | `after_insert` | `after_insert()` |
| Before Validate | `before_validate` | `before_validate()` |
| **Before Save** | **`validate`** | `validate()` |
| After Save | `on_update` | `on_update()` |
| Before Submit | `before_submit` | `before_submit()` |
| After Submit | `on_submit` | `on_submit()` |
| Before Cancel | `before_cancel` | `before_cancel()` |
| After Cancel | `on_cancel` | `on_cancel()` |
| Before Delete | `on_trash` | `on_trash()` |
| After Delete | `after_delete` | `after_delete()` |

### Waarom "Before Save" = `validate`?

In Frappe's architectuur:
- `validate` is de primaire hook voor pre-save validatie en berekeningen
- `before_save` bestaat ook maar draait NA `validate`
- De UI koos "Before Save" als meer intuïtieve naam voor `validate`

---

## Document Lifecycle Volgorde

### Nieuw Document Insert

```
1. before_insert      ← "Before Insert"
2. before_naming
3. autoname
4. before_validate    ← "Before Validate"
5. validate           ← "Before Save" ⚠️
6. before_save
7. [DB INSERT]
8. after_insert       ← "After Insert"
9. on_update          ← "After Save"
10. on_change
```

### Bestaand Document Update

```
1. before_validate    ← "Before Validate"
2. validate           ← "Before Save" ⚠️
3. before_save
4. [DB UPDATE]
5. on_update          ← "After Save"
6. on_change
```

### Document Submit

```
1. before_validate    ← "Before Validate"
2. validate           ← "Before Save" ⚠️
3. before_submit      ← "Before Submit"
4. [DB UPDATE: docstatus=1]
5. on_update          ← "After Save"
6. on_submit          ← "After Submit"
7. on_change
```

### Document Cancel

```
1. before_cancel      ← "Before Cancel"
2. [DB UPDATE: docstatus=2]
3. on_cancel          ← "After Cancel"
4. on_change
```

### Document Delete

```
1. on_trash           ← "Before Delete"
2. [DB DELETE]
3. after_delete       ← "After Delete"
```

---

## Event Details

### Before Insert

**Wanneer**: Alleen bij NIEUWE documenten, voor DB insert
**Gebruik**: Initiële waarden zetten, pre-insert validatie
**doc.name**: Nog NIET beschikbaar (tenzij handmatig gezet)

```python
# Voorbeeld: Default waarden voor nieuw document
if not doc.priority:
    doc.priority = "Medium"

doc.created_by_script = 1
```

### After Insert

**Wanneer**: Direct na eerste DB insert
**Gebruik**: Gerelateerde records aanmaken, notificaties
**doc.name**: Nu beschikbaar

```python
# Voorbeeld: Maak gerelateerd ToDo
frappe.get_doc({
    "doctype": "ToDo",
    "reference_type": doc.doctype,
    "reference_name": doc.name,
    "description": f"Review {doc.name}"
}).insert(ignore_permissions=True)
```

### Before Validate / Before Save (validate)

**Wanneer**: Voor elke save (nieuw en update)
**Gebruik**: Validatie, berekeningen, auto-fill velden
**Throw errors hier**: Voorkomt save

```python
# Before Validate: voor framework validatie
# Before Save (validate): voor custom validatie

if doc.discount_percentage > 50:
    frappe.throw("Korting mag niet meer dan 50% zijn")

# Auto-berekening
doc.total = sum(item.amount for item in doc.items)
```

### After Save (on_update)

**Wanneer**: Na succesvolle save naar DB
**Gebruik**: Side effects, sync met externe systemen
**Let op**: Wijzigingen aan doc worden NIET automatisch opgeslagen

```python
# Voorbeeld: Update gerelateerd document
if doc.status == "Approved":
    linked = frappe.get_doc("Project", doc.project)
    linked.approval_date = frappe.utils.today()
    linked.save(ignore_permissions=True)
```

### Before Submit / After Submit

**Wanneer**: Alleen voor submittable documents (met docstatus)
**Before Submit**: Laatste kans om te valideren/aanpassen
**After Submit**: Document is nu immutable

```python
# Before Submit
if doc.grand_total > 100000 and not doc.manager_approval:
    frappe.throw("Manager goedkeuring vereist voor bedragen boven 100.000")

# After Submit
frappe.sendmail(
    recipients=[doc.owner],
    subject=f"{doc.name} ingediend",
    message=f"Document {doc.name} is succesvol ingediend."
)
```

### Before Cancel / After Cancel

**Wanneer**: Bij cancellation van submitted document
**Before Cancel**: Valideer of cancel toegestaan is
**After Cancel**: Cleanup, reverse effecten

```python
# Before Cancel
linked_docs = frappe.get_all("Payment Entry",
    filters={"reference_name": doc.name, "docstatus": 1})
if linked_docs:
    frappe.throw("Kan niet annuleren: er zijn gekoppelde betalingen")

# After Cancel
doc.add_comment("Info", "Document geannuleerd door systeem")
```

### Before Delete / After Delete

**Wanneer**: Bij permanent verwijderen
**Before Delete (on_trash)**: Laatste kans om te blokkeren
**After Delete**: Cleanup externe referenties

```python
# Before Delete
if doc.has_linked_documents:
    frappe.throw("Verwijder eerst gekoppelde documenten")

# After Delete
frappe.log_error(f"Document {doc.name} verwijderd", "Audit Log")
```

---

## Speciale Events

### on_change

Draait na ELKE wijziging (save, submit, cancel). Nuttig voor audit logging:

```python
# Wordt getriggerd door save, submit, EN cancel
frappe.log_error(
    f"Document {doc.name} gewijzigd naar status {doc.docstatus}",
    "Change Log"
)
```

### Niet beschikbaar in Server Scripts

De volgende events zijn alleen beschikbaar in Document Controllers, NIET in Server Scripts:

- `autoname` - Custom naming logic
- `before_naming` - Pre-naming hook
- `db_insert` / `db_update` - Direct na DB operatie
- `get_feed` - Activity feed customization

---

## Veelvoorkomende Patronen

### Alleen bij status wijziging

```python
# In After Save: check of status is gewijzigd
# Let op: get_doc_before_save() niet beschikbaar in Server Scripts
# Alternatief: gebruik flags of custom field

if doc.status == "Approved" and doc.previous_status != "Approved":
    # Actie bij goedkeuring
    pass
```

### Voorkom oneindige loops

```python
# Gebruik flags om recursieve saves te voorkomen
if doc.flags.get("skip_custom_logic"):
    # Skip om loop te voorkomen
    pass
else:
    # Normale logica
    doc.flags.skip_custom_logic = True
    # ... wijzigingen
```
