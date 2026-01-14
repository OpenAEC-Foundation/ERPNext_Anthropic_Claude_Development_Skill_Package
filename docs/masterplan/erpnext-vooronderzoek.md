# ERPNext/Frappe Framework - Vooronderzoek

> Dit document bevat het initiële onderzoek uitgevoerd aan het begin van het project.
> Bron: Deep research sessie over alle triggerable code en scripting opties in ERPNext/Frappe.

---

## Overzicht

ERPNext en Frappe bieden **zeven distinct scripting mechanismen** voor customization:
1. Client Scripts
2. Server Scripts
3. Document Controllers
4. hooks.py configuratie
5. Jinja templates
6. Scheduled jobs
7. Whitelisted API methods

Elk dient specifieke use cases, en het beheersen ervan maakt krachtige customizations mogelijk zonder core code aan te passen.

---

## 1. Client Scripts (JavaScript)

Client Scripts draaien in de browser en controleren alle UI interacties. Ze worden aangemaakt via **Setup → Client Script** of in custom apps onder `public/js/`.

### Alle beschikbare trigger events

Form-level events ontvangen `frm` als eerste parameter:

| Event | Wanneer het triggert |
|-------|----------------------|
| `setup` | Eenmalig wanneer form voor het eerst wordt aangemaakt |
| `onload` | Wanneer form is geladen en gaat renderen |
| `refresh` | Na form load en render (meest gebruikt) |
| `onload_post_render` | Nadat form volledig is geladen en gerenderd |
| `validate` | Voor save, throw errors hier om save te voorkomen |
| `before_save` | Net voor save wordt aangeroepen |
| `after_save` | Nadat form succesvol is opgeslagen |
| `before_submit` | Voor document submission |
| `on_submit` | Nadat document is submitted |
| `before_cancel` | Voor cancellation |
| `after_cancel` | Nadat form is gecanceld |
| `timeline_refresh` | Nadat timeline is gerenderd |
| `before_workflow_action` | Voor workflow state change |
| `after_workflow_action` | Na workflow state change |
| `{fieldname}` | Wanneer dat veld's waarde verandert |

### Basis syntax

```javascript
frappe.ui.form.on('Sales Invoice', {
    setup(frm) {
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));
    },
    
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 0) {
            frm.add_custom_button(__('Generate Report'), () => {
                frappe.call({
                    method: 'myapp.api.generate_report',
                    args: { invoice: frm.doc.name },
                    callback: (r) => frappe.msgprint(r.message)
                });
            });
        }
    },
    
    validate(frm) {
        if (frm.doc.grand_total <= 0) {
            frappe.throw(__('Grand total must be positive'));
        }
    },
    
    customer(frm) {
        // Triggered wanneer customer veld verandert
        if (frm.doc.customer) {
            frappe.db.get_value('Customer', frm.doc.customer, 
                ['customer_group', 'territory'])
                .then(r => {
                    frm.set_value('customer_group', r.message.customer_group);
                    frm.set_value('territory', r.message.territory);
                });
        }
    }
});
```

### Field manipulation methods

**Waarden zetten en ophalen:**
```javascript
frm.set_value('status', 'Approved');              // Enkele waarde
frm.set_value({status: 'Approved', priority: 'High'});  // Meerdere
let value = frm.doc.fieldname;                    // Waarde direct ophalen
```

**Visibility en properties:**
```javascript
frm.toggle_display('priority', frm.doc.status === 'Open');     // Tonen/verbergen
frm.toggle_reqd('due_date', true);                              // Verplicht maken
frm.toggle_enable('amount', false);                             // Read-only maken

frm.set_df_property('status', 'options', ['New', 'Open', 'Closed']);
frm.set_df_property('amount', 'read_only', 1);
frm.set_df_property('description', 'hidden', 1);
```

**Link velden filteren:**
```javascript
// Simpele filter
frm.set_query('item_code', () => ({
    filters: { is_sales_item: 1, disabled: 0 }
}));

// Filter in child table
frm.set_query('warehouse', 'items', (doc, cdt, cdn) => ({
    filters: { company: doc.company }
}));

// Custom server-side query
frm.set_query('customer', () => ({
    query: 'myapp.queries.get_customers_by_territory',
    filters: { territory: frm.doc.territory }
}));
```

### Custom buttons met groepen

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            // Gegroepeerde buttons verschijnen in dropdown
            frm.add_custom_button(__('Sales Invoice'), () => {
                frappe.model.open_mapped_doc({
                    method: 'erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice',
                    frm: frm
                });
            }, __('Create'));
            
            frm.add_custom_button(__('Delivery Note'), () => {
                frappe.model.open_mapped_doc({
                    method: 'erpnext.selling.doctype.sales_order.sales_order.make_delivery_note',
                    frm: frm
                });
            }, __('Create'));
        }
        
        // Primary action button
        frm.page.set_primary_action(__('Process'), () => {
            frm.call('process_order').then(() => frm.reload_doc());
        });
    }
});
```

### Server methods aanroepen

```javascript
// frappe.call voor elke whitelisted method
frappe.call({
    method: 'myapp.api.process_data',
    args: {
        customer: frm.doc.customer,
        items: frm.doc.items
    },
    freeze: true,
    freeze_message: __('Processing...'),
    callback: (r) => {
        if (r.message) {
            frm.set_value('total', r.message.total);
            frappe.show_alert({message: __('Success'), indicator: 'green'});
        }
    }
});

// frm.call voor document controller methods
frm.call('calculate_taxes', { include_shipping: true })
    .then(r => frm.reload_doc());

// Async/await pattern
async function fetchData(frm) {
    let r = await frappe.call({
        method: 'frappe.client.get_value',
        args: { doctype: 'Customer', filters: {name: frm.doc.customer}, fieldname: 'credit_limit' }
    });
    return r.message.credit_limit;
}
```

### Child table manipulatie

```javascript
// Rijen toevoegen
let row = frm.add_child('items', {
    item_code: 'ITEM-001',
    qty: 5,
    rate: 100
});
frm.refresh_field('items');

// Rijen benaderen en aanpassen
frm.doc.items.forEach((row, idx) => {
    if (row.qty > 10) row.discount_percentage = 5;
});
frm.refresh_field('items');

// Tabel legen
frm.clear_table('items');
frm.refresh_field('items');

// Child table field events
frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);
        calculate_totals(frm);
    },
    
    item_code(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.call({
            method: 'frappe.client.get_value',
            args: { doctype: 'Item', filters: {name: row.item_code}, fieldname: ['item_name', 'standard_rate'] },
            callback: (r) => {
                frappe.model.set_value(cdt, cdn, 'item_name', r.message.item_name);
                frappe.model.set_value(cdt, cdn, 'rate', r.message.standard_rate);
            }
        });
    },
    
    items_remove(frm) {
        calculate_totals(frm);
    }
});
```

---

## 2. Server Scripts (Python)

Server Scripts voeren Python code uit getriggerd door document lifecycle events, scheduled tasks, of API calls. Activeer met `bench --site sitename set-config server_script_enabled true`. Aanmaken via **Setup → Server Script**.

### Document event types

| UI Event Naam | Interne Hook | Beschrijving |
|---------------|--------------|--------------|
| Before Insert | `before_insert` | Voor nieuw document naar database |
| After Insert | `after_insert` | Na nieuw document opgeslagen |
| Before Validate | `before_validate` | Voor validatie draait |
| Before Save | `validate` | Voor document opslaan (nieuw of update) |
| After Save | `on_update` | Na document succesvol opgeslagen |
| Before Submit | `before_submit` | Voor document submit |
| After Submit | `on_submit` | Na document submit |
| Before Cancel | `before_cancel` | Voor document cancel |
| After Cancel | `on_cancel` | Na document cancel |
| Before Delete | `on_trash` | Voor document delete |
| After Delete | `after_delete` | Na document delete |

### Voorbeeld: Before Save

```python
# Server Script: Before Save op Sales Invoice
# Valideert en auto-calculeert waarden

if doc.grand_total < 0:
    frappe.throw("Grand total cannot be negative")

# Auto-set approval requirement
if doc.grand_total > 10000:
    doc.requires_approval = 1

# Fetch linked data
if doc.customer and not doc.customer_name:
    doc.customer_name = frappe.db.get_value("Customer", doc.customer, "customer_name")
```

### Voorbeeld: After Submit

```python
# Server Script: After Submit op Sales Order
# Maakt follow-up ToDo

if doc.grand_total > 5000:
    frappe.get_doc({
        'doctype': 'ToDo',
        'allocated_to': doc.owner,
        'reference_type': 'Sales Order',
        'reference_name': doc.name,
        'description': f'Follow up on high-value order {doc.name}'
    }).insert(ignore_permissions=True)
```

### API endpoint scripts

REST endpoints toegankelijk op `/api/method/{method_name}`:

```python
# Server Script Type: API
# API Method: get_customer_orders
# Allow Guest: No

customer = frappe.form_dict.customer
if not customer:
    frappe.throw("Customer parameter required")

orders = frappe.get_all(
    "Sales Order",
    filters={"customer": customer, "docstatus": 1},
    fields=["name", "grand_total", "transaction_date", "status"],
    order_by="transaction_date desc",
    limit=20
)

frappe.response['orders'] = orders
frappe.response['count'] = len(orders)
```

### Scheduled cron scripts

```python
# Server Script Type: Scheduler Event
# Cron Format: 0 9 * * * (dagelijks om 9 uur)

# Stuur pending invoice reminders
pending = frappe.get_all(
    "Sales Invoice",
    filters={"status": "Unpaid", "due_date": ["<", frappe.utils.today()]},
    fields=["name", "customer", "grand_total", "customer_email"]
)

for inv in pending:
    frappe.sendmail(
        recipients=[inv.customer_email],
        subject=f"Payment Reminder: {inv.name}",
        message=f"Invoice {inv.name} for {inv.grand_total} is overdue."
    )

frappe.db.commit()
```

### Permission Query scripts

Filter document list views dynamisch:

```python
# Server Script Type: Permission Query
# Reference DocType: Sales Invoice

if "Sales Manager" in frappe.get_roles(user):
    conditions = ""  # Geen restricties
elif "Sales User" in frappe.get_roles(user):
    # Alleen eigen facturen tonen
    conditions = f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
else:
    conditions = "1=0"  # Niets tonen
```

---

## 3. Document Controllers (Python Classes)

Controllers zijn Python classes die alle document lifecycle events afhandelen. Gedefinieerd in `{app}/{module}/doctype/{doctype}/{doctype}.py`.

### Complete lifecycle method execution order

**Voor nieuwe document insert:**
`before_insert` → `before_naming` → `autoname` → `before_validate` → `validate` → `before_save` → `db_insert` → `after_insert` → `on_update` → `on_change`

**Voor bestaand document save:**
`before_validate` → `validate` → `before_save` → `db_update` → `on_update` → `on_change`

**Voor submit:**
`before_validate` → `validate` → `before_submit` → `db_update` → `on_update` → `on_submit` → `on_change`

**Voor cancel:**
`before_cancel` → `db_update` → `on_cancel` → `on_change`

### Controller voorbeeld

```python
import frappe
from frappe.model.document import Document

class SalesOrder(Document):
    def autoname(self):
        # Custom naming
        self.name = f"SO-{self.customer[:3]}-{frappe.utils.now_datetime().strftime('%Y%m%d%H%M%S')}"
    
    def before_validate(self):
        # Auto-calculate voor validatie
        self.total = sum(item.amount or 0 for item in self.items)
    
    def validate(self):
        # Validatie logica - throw errors hier
        if not self.items:
            frappe.throw("At least one item is required")
        
        if self.delivery_date and self.delivery_date < frappe.utils.today():
            frappe.throw("Delivery date cannot be in the past")
    
    def before_submit(self):
        # Pre-submission checks
        if self.total > 50000 and not self.manager_approval:
            frappe.throw("Manager approval required for orders over 50,000")
    
    def on_submit(self):
        # Post-submission actions
        self.update_customer_credit()
        self.create_delivery_schedule()
    
    def on_cancel(self):
        # Cleanup bij cancellation
        self.reverse_customer_credit()
    
    @frappe.whitelist()
    def calculate_taxes(self, include_shipping=False):
        # Aanroepbaar via frm.call('calculate_taxes')
        tax_amount = self.total * 0.1
        if include_shipping:
            tax_amount += 50
        return {"tax_amount": tax_amount}
```

---

## 4. hooks.py Configuratie

Het `hooks.py` bestand is de centrale configuratie voor custom apps, definieert hoe je app integreert met Frappe.

### Document events hook

```python
doc_events = {
    "*": {
        # Toepassen op ALLE doctypes
        "after_insert": "myapp.events.log_creation"
    },
    "Sales Invoice": {
        "before_insert": "myapp.si.before_insert",
        "validate": "myapp.si.validate",
        "on_submit": "myapp.si.on_submit",
        "on_cancel": "myapp.si.on_cancel",
        "before_rename": "myapp.si.before_rename",
        "after_rename": "myapp.si.after_rename"
    }
}

# Handler implementatie in myapp/si.py
def validate(doc, method=None):
    if doc.grand_total < 0:
        frappe.throw("Invalid total")
```

### Scheduler events hook

```python
scheduler_events = {
    "all": ["myapp.tasks.every_tick"],           # Elke scheduler tick (~4 min)
    "hourly": ["myapp.tasks.hourly_cleanup"],
    "daily": ["myapp.tasks.daily_report"],
    "daily_long": ["myapp.tasks.heavy_processing"],  # Long worker queue
    "weekly": ["myapp.tasks.weekly_summary"],
    "monthly": ["myapp.tasks.monthly_archive"],
    "cron": {
        "*/15 * * * *": ["myapp.tasks.every_15_min"],
        "0 9 * * 1-5": ["myapp.tasks.weekday_morning"],
        "0 0 1 * *": ["myapp.tasks.first_of_month"]
    }
}
```

### Override en extend bestaande doctypes

```python
# Override doctype class volledig
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice"
}

# Custom JavaScript toevoegen aan bestaande forms
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "Customer": "public/js/customer.js"
}

# Custom list view settings
doctype_list_js = {
    "Sales Invoice": "public/js/sales_invoice_list.js"
}

# Override whitelisted methods
override_whitelisted_methods = {
    "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice": 
        "myapp.overrides.custom_make_sales_invoice"
}
```

### Permission hooks

```python
# Custom permission query (filtert list views)
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_conditions"
}

# Custom document-level permission
has_permission = {
    "Sales Invoice": "myapp.permissions.si_permission"
}

# Implementatie
def si_conditions(user):
    if "Sales Manager" not in frappe.get_roles(user):
        return f"owner = {frappe.db.escape(user)}"
    return ""

def si_permission(doc, user=None, permission_type=None):
    if permission_type == "write" and doc.status == "Closed":
        return False
    return None  # Fall back naar default
```

### Andere essentiële hooks

```python
# Include assets in desk
app_include_js = "assets/myapp/js/myapp.min.js"
app_include_css = "assets/myapp/css/myapp.css"

# Toevoegen aan boot info (beschikbaar in frappe.boot)
extend_bootinfo = "myapp.boot.extend_bootinfo"

# Install/uninstall hooks
after_install = "myapp.setup.after_install"
before_uninstall = "myapp.setup.before_uninstall"

# Fixtures voor export/import
fixtures = [
    "Custom Field",
    "Property Setter",
    {"dt": "Role", "filters": [["name", "like", "MyApp%"]]}
]

# Jinja environment extensions
jenv = {
    "methods": ["myapp.jinja.custom_method"],
    "filters": ["myapp.jinja.custom_filter"]
}
```

---

## 5. Whitelisted Methods (@frappe.whitelist)

Gebruik `@frappe.whitelist()` om Python functies als REST endpoints te exposen.

```python
import frappe

@frappe.whitelist()
def get_customer_summary(customer):
    """Endpoint: /api/method/myapp.api.get_customer_summary"""
    if not frappe.has_permission("Customer", "read", customer):
        frappe.throw("No permission", frappe.PermissionError)
    
    orders = frappe.get_all(
        "Sales Order",
        filters={"customer": customer, "docstatus": 1},
        fields=["sum(grand_total) as total", "count(name) as count"]
    )[0]
    
    return {
        "customer": customer,
        "total_orders": orders.count,
        "total_value": orders.total or 0
    }

@frappe.whitelist(allow_guest=True)
def public_endpoint():
    """Toegankelijk zonder authenticatie"""
    return {"status": "ok"}

@frappe.whitelist(methods=["POST"])
def create_record(data):
    """POST-only endpoint"""
    if isinstance(data, str):
        data = frappe.parse_json(data)
    
    doc = frappe.get_doc(data)
    doc.insert()
    return doc.name
```

---

## 6. Jinja Templates

### Print format scripting

```jinja
<style>
    .invoice-header { background: #f5f5f5; padding: 15px; }
    .amount { text-align: right; }
</style>

<div class="invoice-header">
    <h1>{{ doc.name }}</h1>
    <p>Date: {{ frappe.format_date(doc.posting_date) }}</p>
    <p>Customer: {{ doc.customer_name }}</p>
</div>

{% set customer = frappe.get_doc("Customer", doc.customer) %}
<p>Credit Limit: {{ frappe.format(customer.credit_limit, {'fieldtype': 'Currency'}) }}</p>

<table>
    <thead>
        <tr><th>Item</th><th>Qty</th><th>Rate</th><th>Amount</th></tr>
    </thead>
    <tbody>
        {% for item in doc.items %}
        <tr>
            <td>{{ item.item_name }}</td>
            <td>{{ item.qty }}</td>
            <td class="amount">{{ frappe.format(item.rate, {'fieldtype': 'Currency'}) }}</td>
            <td class="amount">{{ frappe.format(item.amount, {'fieldtype': 'Currency'}) }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<p><strong>Total: {{ frappe.format(doc.grand_total, {'fieldtype': 'Currency'}) }}</strong></p>

{% if doc.status == "Paid" %}
    <span class="badge badge-success">{{ _("PAID") }}</span>
{% endif %}
```

### Beschikbare Jinja methods

- `frappe.format(value, df)` - Formatteer waarde per fieldtype
- `frappe.format_date(date)` - Human-readable date
- `frappe.get_doc(doctype, name)` - Fetch document
- `frappe.get_all(doctype, filters, fields)` - Query records
- `frappe.db.get_value(doctype, name, field)` - Get enkele waarde
- `frappe.get_url()` - Site URL
- `_('text')` - Vertaling functie

---

## 7. Background Jobs & Scheduler

### frappe.enqueue syntax

```python
frappe.enqueue(
    method='myapp.tasks.process_records',  # Functie of pad
    queue='long',                           # short, default, long
    timeout=3600,                           # Custom timeout (seconden)
    job_name='process_batch_123',          # Voor identificatie
    enqueue_after_commit=True,             # Wacht op DB commit
    at_front=True,                         # Priority execution
    # Arguments doorgegeven aan method:
    records=record_list,
    notify_user=True
)

# Queue timeouts: short=300s, default=300s, long=1500s

# Enqueue document method
frappe.enqueue_doc(
    "Sales Invoice",
    "SINV-00001", 
    "send_notification",
    queue="short"
)
```

### Task implementatie

```python
def process_records(records, notify_user=False):
    for record in records:
        try:
            process_single(record)
            frappe.db.commit()  # Commit elke success
        except Exception:
            frappe.db.rollback()
            frappe.log_error(frappe.get_traceback(), "Process Error")
    
    if notify_user:
        frappe.publish_realtime('show_alert', 
            {'message': 'Processing complete', 'indicator': 'green'},
            user=frappe.session.user)
```

---

## 8. Document Flags

### Built-in flags

```python
doc.flags.ignore_permissions = True     # Bypass permission checks
doc.flags.ignore_validate = True        # Skip validation
doc.flags.ignore_mandatory = True       # Skip required field checks
doc.flags.ignore_links = True           # Skip link validation
doc.flags.ignore_version = True         # Don't create version record
```

### Custom flags voor inter-event communicatie

```python
class SalesInvoice(Document):
    def validate(self):
        if self.grand_total > 10000:
            self.flags.high_value = True
    
    def on_submit(self):
        if self.flags.get('high_value'):
            self.notify_finance_team()
    
    def before_save(self):
        if self.get_doc_before_save():
            old_status = self.get_doc_before_save().status
            if old_status != self.status:
                self.flags.status_changed = True
```

---

## 9. Best Practices

### Error handling

```python
# Gebruik frappe.throw voor validation errors
if doc.amount < 0:
    frappe.throw("Amount cannot be negative", title="Validation Error")

# Gebruik try/except met proper logging
try:
    external_api_call()
except Exception as e:
    frappe.log_error(frappe.get_traceback(), "API Error")
    frappe.throw("External service unavailable. Please try later.")
```

### Database best practices

```python
# DON'T call commit in controller hooks - framework handles het
# DON'T gebruik string formatting met user input

# DO gebruik parameterized queries
results = frappe.db.sql("""
    SELECT name FROM `tabCustomer` WHERE territory = %(territory)s
""", {"territory": territory}, as_dict=True)

# DO gebruik get_all voor simpele queries (niet raw SQL)
customers = frappe.get_all("Customer", 
    filters={"territory": "USA"}, 
    fields=["name", "customer_name"])

# DO batch fetch om N+1 queries te vermijden
customer_names = [i.customer for i in items]
customers = {c.name: c for c in frappe.get_all(
    "Customer", filters={"name": ["in", customer_names]}, fields=["*"]
)}
```

### Performance optimization

```python
# Gebruik caching voor expensive operations
@frappe.whitelist()
def get_dashboard_data():
    cache_key = f"dashboard_{frappe.session.user}"
    data = frappe.cache().get_value(cache_key)
    if not data:
        data = compute_dashboard()
        frappe.cache().set_value(cache_key, data, expires_in_sec=300)
    return data

# Gebruik get_cached_value voor frequent accessed data
company = frappe.get_cached_value("Company", company_name, "country")

# Limiteer fields in queries
items = frappe.get_all("Item", 
    fields=["name", "item_name"],  # Niet "*"
    limit_page_length=50)
```

---

## 10. Wanneer Wat Gebruiken

| Use Case | Aanbevolen Aanpak |
|----------|-------------------|
| UI gedrag, velden tonen/verbergen | Client Script |
| Real-time validatie feedback | Client Script |
| Snelle custom validaties | Server Script |
| Core business logic | Document Controller |
| Extend standard doctypes | hooks.py doc_events |
| REST APIs maken | Whitelisted methods |
| Scheduled tasks | hooks.py scheduler_events |
| Long-running operations | frappe.enqueue |
| Print customization | Jinja templates |

---

## Bronnen

- Frappe Framework Documentatie: https://docs.frappe.io/framework
- ERPNext Documentatie: https://docs.erpnext.com
- Frappe GitHub: https://github.com/frappe/frappe
