# Research Document: Document Controllers (Fase 2.1)

> **Doel**: Verifiëren, verdiepen en actualiseren van informatie uit erpnext-vooronderzoek.md sectie 3 (Document Controllers) voor Frappe v14/v15.

---

## Bronnen Geraadpleegd

| Bron | URL/Locatie | Type |
|------|-------------|------|
| Frappe Docs - Controllers | docs.frappe.io/framework/user/en/basics/doctypes/controllers | Primair |
| Frappe Docs - Document API | docs.frappe.io/framework/user/en/api/document | Primair |
| Frappe GitHub - document.py | github.com/frappe/frappe/blob/develop/frappe/model/document.py | Verificatie |
| Frappe GitHub - server_script_utils.py | github.com/frappe/frappe/blob/develop/.../server_script_utils.py | Verificatie |
| Frappe Docs - Naming | docs.frappe.io/framework/user/en/basics/doctypes/naming | Primair |
| Frappe Docs - Hooks | docs.frappe.io/framework/user/en/python-api/hooks | Primair |
| erpnext-vooronderzoek.md | Project bestand | Basis |

---

## 1. CLASS STRUCTUUR

### Basis Controller Structuur

Een controller is een Python class die `frappe.model.document.Document` uitbreidt. Locatie: `{app}/{module}/doctype/{doctype}/{doctype}.py`

```python
# Standaard imports
import frappe
from frappe.model.document import Document

# Class naam = DocType naam in PascalCase (spaties verwijderd)
class SalesOrder(Document):
    pass
```

**Versie v14/v15**: Identiek.

### Naming Convention

| DocType naam | Class naam | Bestandsnaam |
|--------------|------------|--------------|
| Sales Order | SalesOrder | sales_order.py |
| Custom DocType Name | CustomDoctypeName | custom_doctype_name.py |

### Inheritance Patronen

```python
# Standaard inheritance
from frappe.model.document import Document
class MyDocType(Document):
    pass

# Tree DocType inheritance (voor hiërarchische structuren)
from frappe.utils.nestedset import NestedSet
class MyTreeDocType(NestedSet):
    pass

# Extend bestaande controller
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
class CustomSalesOrder(SalesOrder):
    pass
```

### Type Annotations (v15+)

Frappe v15 ondersteunt automatisch gegenereerde type annotations:

```python
class Person(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from frappe.types import DF
        first_name: DF.Data
        last_name: DF.Data
        user: DF.Link
    # end: auto-generated types
    pass
```

**Activeren in hooks.py:**
```python
export_python_type_annotations = True
```

---

## 2. LIFECYCLE METHODS - Complete Lijst met Execution Order

### Complete EVENT_MAP (Geverifieerd uit Frappe GitHub source)

| Interne Hook | UI/Server Script Event | Beschrijving |
|--------------|------------------------|--------------|
| `before_insert` | Before Insert | Voor nieuw document naar database gaat |
| `after_insert` | After Insert | Na nieuw document is opgeslagen |
| `before_validate` | Before Validate | Voor validatie begint |
| `validate` | Before Save | Hoofdvalidatie hook (nieuw of update) |
| `on_update` | After Save | Na document succesvol opgeslagen |
| `before_rename` | Before Rename | Voor document wordt hernoemd |
| `after_rename` | After Rename | Na document is hernoemd |
| `before_submit` | Before Submit | Voor document submit (docstatus 0→1) |
| `on_submit` | After Submit | Na document submit |
| `before_cancel` | Before Cancel | Voor document cancel (docstatus 1→2) |
| `on_cancel` | After Cancel | Na document cancel |
| `before_discard` | Before Discard | Voor draft wordt verwijderd |
| `on_discard` | After Discard | Na draft is verwijderd |
| `on_trash` | Before Delete | Voor document wordt verwijderd |
| `after_delete` | After Delete | Na document is verwijderd |
| `before_update_after_submit` | Before Save (Submitted Document) | Voor update van submitted doc |
| `on_update_after_submit` | After Save (Submitted Document) | Na update van submitted doc |
| `before_print` | Before Print | Voor print format wordt gerenderd |
| `on_change` | (intern) | Na elke wijziging, inclusief db_set |

### Naming-Specifieke Hooks

| Hook | Wanneer |
|------|---------|
| `before_naming` | Voor name wordt gegenereerd |
| `autoname` | Genereer custom name programmatisch |

### Execution Order voor INSERT (Nieuw Document)

```
1. before_insert
2. before_naming
3. autoname
4. before_validate
5. validate
6. before_save
7. [db_insert - intern]
8. after_insert
9. on_update
10. on_change
```

### Execution Order voor SAVE (Bestaand Document)

```
1. before_validate
2. validate
3. before_save
4. [db_update - intern]
5. on_update
6. on_change
```

### Execution Order voor SUBMIT

```
1. before_validate
2. validate
3. before_submit
4. [db_update - docstatus=1]
5. on_update
6. on_submit
7. on_change
```

### Execution Order voor CANCEL

```
1. before_cancel
2. [db_update - docstatus=2]
3. on_cancel
4. [check_no_back_links_exist]
5. on_change
```

### Execution Order voor UPDATE AFTER SUBMIT

```
1. before_update_after_submit
2. [db_update]
3. on_update_after_submit
4. on_change
```

### Execution Order voor DELETE

```
1. on_trash
2. [delete from database]
3. after_delete
```

---

## 3. SPECIALE METHODS

### doc.get_doc_before_save()

Retourneert het document zoals het was vóór de huidige wijzigingen. Beschikbaar in `validate`, `on_update`, `on_change`, etc.

```python
def validate(self):
    old_doc = self.get_doc_before_save()
    if old_doc and old_doc.status != self.status:
        # Status is gewijzigd
        self.log_status_change()
```

### doc.db_insert() / doc.db_update()

**WAARSCHUWING**: Deze methodes bypassen alle validaties en controller hooks.

```python
# ALLEEN gebruiken als je weet wat je doet
doc = frappe.get_doc(doctype="MyDoc", data="")
doc.db_insert()  # Bypass alle hooks

# Normaal gebruik - gebruik insert() of save()
doc.insert()  # Triggert alle hooks
doc.save()    # Triggert alle hooks
```

### doc.run_method(method_name, *args, **kwargs)

Voert een controller method uit en triggert ook bijbehorende hooks.

```python
# Voert validate uit + hooks.py doc_events + server scripts
doc.run_method('validate')

# Met argumenten
doc.run_method('custom_method', value1='test')
```

### doc.reload()

Herlaadt document uit database met laatste waarden:

```python
def on_update(self):
    # Andere code heeft misschien velden geüpdatet
    self.reload()
    print(self.modified_by)  # Laatste waarde
```

### doc.as_dict()

Serialiseert document naar dictionary:

```python
>>> doc.as_dict()
{
    'name': '000001',
    'doctype': 'ToDo',
    'owner': 'Administrator',
    'creation': datetime.datetime(...),
    'modified': datetime.datetime(...),
    'status': 'Open',
    ...
}
```

### doc.get_valid_dict()

Retourneert dictionary met alleen geldige velden (gefilterd op permissions en docfield meta).

### doc.queue_action(action, **kwargs)

Voert een controller method uit in de achtergrond:

```python
def on_submit(self):
    # Zware operatie async uitvoeren
    self.queue_action('send_emails', emails=email_list, message='Howdy')
```

### doc.notify_update()

Publiceert realtime event dat document is gewijzigd (voor form refresh):

```python
# Handmatig triggeren na directe DB update
frappe.db.set_value('Sales Order', self.name, 'status', 'Closed')
self.notify_update()
```

### doc.add_comment(comment_type, text)

Voegt commentaar toe aan document timeline:

```python
def on_submit(self):
    self.add_comment('Edit', 'Document submitted for approval')
```

### Tree DocType Methodes (NestedSet)

Alleen beschikbaar voor DocTypes met "Is Tree" enabled:

```python
# Krijg kinderen
for child_doc in doc.get_children():
    print(child_doc.name)

# Krijg parent
parent_doc = doc.get_parent()
```

---

## 4. FLAGS SYSTEEM

### Standaard Flags

```python
# Permission bypass
doc.flags.ignore_permissions = True      # Bypass alle permission checks

# Validation bypass  
doc.flags.ignore_validate = True         # Skip validate() method
doc.flags.ignore_mandatory = True        # Skip verplichte veld checks
doc.flags.ignore_links = True            # Skip link validatie

# Versioning
doc.flags.ignore_version = True          # Maak geen version record

# Notifications
doc.flags.notify_update = False          # Stuur geen realtime update (v15)
```

### Systeem Flags (via frappe.flags)

```python
frappe.flags.in_import = True            # Import modus
frappe.flags.in_install = True           # Installatie modus
frappe.flags.in_patch = True             # Patch/migrate modus
frappe.flags.in_migrate = True           # Migratie modus
frappe.flags.mute_emails = True          # Onderdruk email versturen
```

### Custom Flags voor Inter-Event Communicatie

```python
class SalesInvoice(Document):
    def validate(self):
        if self.grand_total > 10000:
            self.flags.high_value = True
            
    def on_submit(self):
        if self.flags.get('high_value'):
            self.notify_finance_team()
            
    def before_save(self):
        old_doc = self.get_doc_before_save()
        if old_doc and old_doc.status != self.status:
            self.flags.status_changed = True
```

### Flags in insert() en save()

```python
# Insert met flags
doc.insert(
    ignore_permissions=True,      # Bypass write permissions
    ignore_links=True,            # Bypass link validatie
    ignore_if_duplicate=True,     # Geen error bij duplicate
    ignore_mandatory=True         # Bypass verplichte velden
)

# Save met flags
doc.save(
    ignore_permissions=True,      # Bypass write permissions
    ignore_version=True           # Geen version record maken
)
```

---

## 5. WHITELISTED METHODS IN CONTROLLER

### Basis Syntax

```python
class SalesOrder(Document):
    @frappe.whitelist()
    def calculate_taxes(self, include_shipping=False):
        """Aanroepbaar via frm.call('calculate_taxes')"""
        tax_amount = self.total * 0.1
        if include_shipping:
            tax_amount += 50
        return {"tax_amount": tax_amount}
```

### Aanroepen vanuit Client (JavaScript)

```javascript
// Methode 1: frm.call
frm.call('calculate_taxes', { include_shipping: true })
    .then(r => {
        if (r.message) {
            let tax = r.message.tax_amount;
            frm.set_value('tax_amount', tax);
        }
    });

// Methode 2: Directe call met volledig pad
frappe.call({
    method: 'erpnext.selling.doctype.sales_order.sales_order.SalesOrder.calculate_taxes',
    args: {
        self: frm.doc.name,  // Document name doorgeven
        include_shipping: true
    },
    callback: (r) => console.log(r.message)
});
```

### Decorator Opties

```python
# Standaard - alleen authenticated users
@frappe.whitelist()
def my_method(self):
    pass

# Toegankelijk voor gasten (niet-ingelogde gebruikers)
@frappe.whitelist(allow_guest=True)
def public_method(self):
    pass

# Alleen specifieke HTTP methods
@frappe.whitelist(methods=['POST'])
def post_only_method(self):
    pass

# XSS veilig (schakel HTML escaping uit)
@frappe.whitelist(xss_safe=True)
def html_method(self):
    return "<strong>HTML content</strong>"
```

---

## 6. AUTONAME PATTERNS

### Via DocType Configuratie (Auto Name veld)

| Pattern | Voorbeeld | Resultaat |
|---------|-----------|-----------|
| `field:fieldname` | `field:item_code` | Waarde van item_code veld |
| `naming_series:` | `naming_series:` | Naming series dropdown |
| `PREF.#####` | `SO-.#####` | SO-00001, SO-00002 |
| `PREF.YYYY.#####` | `INV-.YYYY.-.#####` | INV-2025-00001 |
| `hash` | `hash` | Random hash |
| `prompt` | `prompt` | Gebruiker wordt gevraagd |
| `autoincrement` | `autoincrement` | Integer auto-increment |

### Programmatisch via autoname()

```python
from frappe.model.naming import getseries

class Project(Document):
    def autoname(self):
        # Custom naming logic
        prefix = f"P-{self.customer[:3]}-"
        self.name = getseries(prefix, 3)  # P-CUS-001
```

### before_naming Hook

```python
def before_naming(self):
    # Wijzig naming parameters voor autoname draait
    if self.is_priority:
        self.naming_series = "PRIORITY-.#####"
```

---

## 7. CONTROLLER OVERRIDE (hooks.py)

### override_doctype_class

Volledig vervangen van een DocType controller:

```python
# In hooks.py
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice"
}
```

```python
# In myapp/overrides.py
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # Belangrijk: roep parent aan
        # Custom validatie
        self.custom_validation()
```

### doc_events Hook

Event handlers toevoegen zonder controller te overschrijven:

```python
# In hooks.py
doc_events = {
    "Sales Invoice": {
        "validate": "myapp.events.si_validate",
        "on_submit": "myapp.events.si_on_submit",
    },
    "*": {
        # Voor ALLE doctypes
        "after_insert": "myapp.events.log_creation"
    }
}
```

```python
# In myapp/events.py
def si_validate(doc, method=None):
    """Handler ontvangt doc en method naam"""
    if doc.grand_total < 0:
        frappe.throw("Invalid total")

def log_creation(doc, method=None):
    frappe.log_error(f"Created {doc.doctype}: {doc.name}")
```

---

## 8. SUBMITTABLE DOCUMENTS

### Docstatus Waarden

| Waarde | Status | Bewerkbaar |
|--------|--------|------------|
| 0 | Draft | Ja |
| 1 | Submitted | Nee (behalve "Allow on Submit" velden) |
| 2 | Cancelled | Nee |

### Lifecycle voor Submittable

```python
class PurchaseOrder(Document):
    def before_submit(self):
        # Pre-submission checks
        if self.total > 50000 and not self.manager_approval:
            frappe.throw("Manager approval required")
            
    def on_submit(self):
        # Post-submission actions
        self.update_ordered_qty()
        
    def before_cancel(self):
        # Pre-cancellation checks
        if self.has_linked_invoices():
            frappe.throw("Cannot cancel - linked invoices exist")
            
    def on_cancel(self):
        # Cleanup
        self.reverse_ordered_qty()
```

### Update After Submit

```python
# Velden met "Allow on Submit" kunnen worden geüpdatet
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.status = "Closed"  # Alleen als "Allow on Submit" aan staat
doc.save()  # Triggert on_update_after_submit

# Of direct:
frappe.db.set_value("Sales Order", "SO-00001", "status", "Closed")
```

---

## 9. VIRTUAL DOCTYPES

DocTypes zonder database tabel (v14+):

```python
class VirtualDoctype(Document):
    """Custom data source controller"""
    
    def db_insert(self, *args, **kwargs):
        """Implementeer custom insert"""
        data = self.get_valid_dict(convert_dates_to_str=True)
        # Save to external source
        
    def load_from_db(self):
        """Laad data van externe bron"""
        external_data = get_from_api(self.name)
        super(Document, self).__init__(external_data)
        
    def db_update(self, *args, **kwargs):
        """Implementeer custom update"""
        self.db_insert(*args, **kwargs)
        
    @staticmethod
    def get_list(args):
        """Return list van documenten"""
        return [frappe._dict(doc) for doc in get_all_from_api()]
        
    @staticmethod
    def get_count(args):
        """Return count"""
        return len(get_all_from_api())
```

---

## 10. BEST PRACTICES

### Validation Pattern

```python
def validate(self):
    # 1. Check required conditions
    if not self.items:
        frappe.throw(_("At least one item is required"))
        
    # 2. Cross-field validation
    if self.from_date > self.to_date:
        frappe.throw(_("From Date cannot be after To Date"))
        
    # 3. External validation (cached)
    customer = frappe.get_cached_doc("Customer", self.customer)
    if customer.disabled:
        frappe.throw(_("Customer is disabled"))
```

### Geen Commit in Controllers

```python
# ❌ FOUT - Frappe handelt commits automatisch af
def on_update(self):
    frappe.db.commit()  # NIET DOEN

# ✅ GOED - Laat framework commits afhandelen
def on_update(self):
    self.update_related_doc()  # Geen commit nodig
```

### Wijzigingen na on_update

**BELANGRIJK**: Wijzigingen aan `self` na `on_update` worden NIET opgeslagen!

```python
# ❌ FOUT - wijziging wordt niet opgeslagen
def on_update(self):
    self.status = "Completed"  # NIET OPGESLAGEN in DB

# ✅ GOED - gebruik db_set voor post-save wijzigingen
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "status", "Completed")
```

### Permission Check

```python
def on_submit(self):
    # Check permissions voor gevoelige acties
    if not frappe.has_permission("Salary Slip", "submit"):
        frappe.throw(_("Not permitted to submit"))
```

---

## 11. VERSIE VERSCHILLEN (v14 vs v15)

| Feature | v14 | v15 |
|---------|-----|-----|
| Type annotations | ❌ | ✅ Auto-generated |
| `flags.notify_update` | ❌ | ✅ Beschikbaar |
| before_discard/on_discard | ❌ | ✅ Nieuwe hooks |
| Event mapping | Basis | Uitgebreid met payments |

---

## 12. ANTI-PATTERNS

### ❌ Aannames over execution order

```python
# FOUT - aannemen dat validate altijd voor on_update draait bij andere docs
def on_update(self):
    other_doc = frappe.get_doc("Other", self.link)
    other_doc.some_field = "value"
    other_doc.save()  # Dit triggert andere doc's hooks
```

### ❌ Recursive saves

```python
# FOUT - kan infinite loop veroorzaken
def on_update(self):
    self.counter += 1
    self.save()  # Triggert on_update opnieuw!

# GOED - gebruik db_set
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "counter", 
                        self.counter + 1, update_modified=False)
```

### ❌ Heavy operations in validate

```python
# FOUT - blokkeert save voor gebruiker
def validate(self):
    self.process_large_dataset()  # Kan minuten duren

# GOED - queue voor background
def on_update(self):
    frappe.enqueue(
        'myapp.tasks.process_large_dataset',
        doc_name=self.name,
        queue='long'
    )
```

---

## Samenvatting voor Skill Creatie

### Key Learnings

1. **Controller class** = Python class die `Document` uitbreidt
2. **Lifecycle hooks** volgen strikte execution order
3. **EVENT_MAP** in source code definieert alle beschikbare hooks
4. **Flags** systeem voor behaviour override en inter-event communicatie
5. **@frappe.whitelist()** maakt controller methods aanroepbaar van client
6. **on_change** hook triggert na ELKE wijziging (ook db_set)
7. **Wijzigingen na on_update** worden NIET automatisch opgeslagen - gebruik db_set
8. **Type annotations** zijn nieuw in v15

### Skill References te Maken

1. `lifecycle-methods.md` - Alle hooks met execution order
2. `methods.md` - Alle doc.* methodes met signatures
3. `flags.md` - Flags systeem documentatie
4. `examples.md` - Complete werkende voorbeelden
5. `anti-patterns.md` - Wat te vermijden
