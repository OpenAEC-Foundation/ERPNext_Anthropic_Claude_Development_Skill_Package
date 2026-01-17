# Database Anti-Patterns

## 1. SQL Injection

### ❌ FOUT - String Formatting
```python
# KRITIEK BEVEILIGINGSRISICO!
user_input = "admin'; DROP TABLE tabUser; --"

# Nooit doen:
frappe.db.sql(f"SELECT * FROM `tabUser` WHERE name = '{user_input}'")
frappe.db.sql("SELECT * FROM `tabUser` WHERE name = '%s'" % user_input)
frappe.db.sql("SELECT * FROM `tabUser` WHERE name = " + user_input)
```

### ✅ CORRECT - Parameterized Query
```python
frappe.db.sql(
    "SELECT * FROM `tabUser` WHERE name = %(name)s",
    {'name': user_input}
)

# Of via ORM
frappe.get_all('User', filters={'name': user_input})
```

---

## 2. N+1 Query Problem

### ❌ FOUT - Query in Loop
```python
def get_order_details(order_names):
    results = []
    for name in order_names:
        order = frappe.get_doc('Sales Order', name)  # N queries!
        customer = frappe.get_doc('Customer', order.customer)  # Nog N queries!
        results.append({
            'order': order.name,
            'customer': customer.customer_name
        })
    return results
```

### ✅ CORRECT - Batch Fetch
```python
def get_order_details(order_names):
    # Één query voor alle orders
    orders = frappe.get_all('Sales Order',
        filters={'name': ['in', order_names]},
        fields=['name', 'customer', 'grand_total']
    )
    
    # Één query voor alle customers
    customer_names = list(set(o.customer for o in orders))
    customers = {c.name: c for c in frappe.get_all('Customer',
        filters={'name': ['in', customer_names]},
        fields=['name', 'customer_name']
    )}
    
    return [{
        'order': o.name,
        'customer': customers[o.customer].customer_name
    } for o in orders]
```

---

## 3. Commit in Controller Hooks

### ❌ FOUT - Handmatige Commit
```python
class SalesInvoice(Document):
    def validate(self):
        self.calculate_totals()
        frappe.db.commit()  # NOOIT DOEN!
    
    def on_submit(self):
        self.create_gl_entries()
        frappe.db.commit()  # NOOIT DOEN!
```

### ✅ CORRECT - Laat Framework het Doen
```python
class SalesInvoice(Document):
    def validate(self):
        self.calculate_totals()
        # Geen commit - framework handelt dit af
    
    def on_submit(self):
        self.create_gl_entries()
        # Geen commit - framework handelt dit af
```

**Uitzondering**: Alleen in background jobs of scripts waar je weet wat je doet.

---

## 4. Selecteer Alle Velden

### ❌ FOUT - SELECT *
```python
# Haalt ALLE velden op, ook grote TEXT velden
docs = frappe.get_all('Sales Invoice', fields=['*'])

frappe.db.sql("SELECT * FROM `tabSales Invoice`")
```

### ✅ CORRECT - Specificeer Velden
```python
docs = frappe.get_all('Sales Invoice',
    fields=['name', 'customer', 'grand_total', 'status']
)

frappe.db.sql("""
    SELECT name, customer, grand_total, status
    FROM `tabSales Invoice`
""")
```

---

## 5. Geen Paginering

### ❌ FOUT - Alle Records Ophalen
```python
# Kan miljoenen records returnen!
all_logs = frappe.get_all('Error Log')

frappe.db.sql("SELECT * FROM `tabError Log`")
```

### ✅ CORRECT - Altijd Limiteren
```python
# Met page_length
logs = frappe.get_all('Error Log',
    fields=['name', 'error', 'creation'],
    order_by='creation desc',
    page_length=100
)

# Met LIMIT in SQL
frappe.db.sql("""
    SELECT name, error, creation
    FROM `tabError Log`
    ORDER BY creation DESC
    LIMIT 100
""")
```

---

## 6. Ignore Flags Misbruik

### ❌ FOUT - Alles Negeren
```python
doc.insert(
    ignore_permissions=True,
    ignore_mandatory=True,
    ignore_links=True,
    ignore_validate=True
)
```

### ✅ CORRECT - Alleen Wat Nodig Is
```python
# Specifiek en gedocumenteerd
doc.flags.ignore_permissions = True  # Reden: System background job
doc.insert()
```

---

## 7. db_set zonder Begrip

### ❌ FOUT - db_set voor Alles
```python
def update_status(name, status):
    # Bypassed alle validaties!
    frappe.db.set_value('Task', name, 'status', status)
```

### ✅ CORRECT - ORM voor Business Logic
```python
def update_status(name, status):
    doc = frappe.get_doc('Task', name)
    doc.status = status
    doc.save()  # Triggert validate, on_update, etc.
```

**db_set alleen gebruiken voor**:
- Hidden fields
- Counters
- Timestamps
- Background jobs waar performance kritiek is

---

## 8. Geen Error Handling

### ❌ FOUT - Geen Try/Except
```python
def process_data(data):
    for item in data:
        doc = frappe.get_doc('Item', item)
        doc.status = 'Processed'
        doc.save()
    frappe.db.commit()
```

### ✅ CORRECT - Proper Error Handling
```python
def process_data(data):
    processed = []
    errors = []
    
    for item in data:
        try:
            doc = frappe.get_doc('Item', item)
            doc.status = 'Processed'
            doc.save()
            processed.append(item)
        except frappe.DoesNotExistError:
            errors.append({'item': item, 'error': 'Not found'})
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f'Process Error: {item}')
            errors.append({'item': item, 'error': str(e)})
    
    if processed:
        frappe.db.commit()
    
    return {'processed': processed, 'errors': errors}
```

---

## 9. Cache Zonder Invalidatie

### ❌ FOUT - Cache Nooit Geleegd
```python
@redis_cache
def get_settings():
    return frappe.get_doc('My Settings')

# Settings worden gewijzigd maar cache wordt niet geleegd
```

### ✅ CORRECT - Cache Invalidatie
```python
@redis_cache(ttl=3600)
def get_settings():
    return frappe.get_doc('My Settings')

class MySettings(Document):
    def on_update(self):
        get_settings.clear_cache()
```

---

## 10. Blocking Operations in Request

### ❌ FOUT - Lange Operatie in Request
```python
@frappe.whitelist()
def process_all_invoices():
    # Dit kan minuten duren!
    invoices = frappe.get_all('Sales Invoice', filters={'status': 'Unpaid'})
    for inv in invoices:
        send_reminder_email(inv.name)
    return "Done"
```

### ✅ CORRECT - Background Job
```python
@frappe.whitelist()
def process_all_invoices():
    frappe.enqueue(
        'myapp.tasks.process_invoices_bg',
        queue='long',
        timeout=3600
    )
    return "Processing started"

def process_invoices_bg():
    invoices = frappe.get_all('Sales Invoice', filters={'status': 'Unpaid'})
    for inv in invoices:
        send_reminder_email(inv.name)
        frappe.db.commit()  # Commit per iteratie in background job
```

---

## 11. get_doc voor Existence Check

### ❌ FOUT - get_doc om te Checken
```python
try:
    doc = frappe.get_doc('User', email)
    exists = True
except:
    exists = False
```

### ✅ CORRECT - exists Method
```python
exists = frappe.db.exists('User', email)
# Of
exists = frappe.db.exists('User', {'email': email})
```

---

## 12. Hardcoded Table Names

### ❌ FOUT - Zonder Prefix
```python
frappe.db.sql("SELECT * FROM Task")
frappe.db.sql("SELECT * FROM sales_invoice")
```

### ✅ CORRECT - Met `tab` Prefix
```python
frappe.db.sql("SELECT * FROM `tabTask`")
frappe.db.sql("SELECT * FROM `tabSales Invoice`")
```

**Tabelnaam format**: `tab{DocType Name}` met exacte spelling en spaties.
