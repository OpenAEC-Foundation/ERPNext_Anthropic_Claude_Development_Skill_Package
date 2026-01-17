# Database Examples

## Voorbeeld 1: Document CRUD

### Create
```python
# Nieuw document maken en opslaan
doc = frappe.get_doc({
    'doctype': 'Task',
    'subject': 'Review Sales Report',
    'status': 'Open',
    'priority': 'High',
    'description': 'Monthly sales review',
    'exp_start_date': frappe.utils.today(),
    'expected_time': 2
})
doc.insert()
frappe.db.commit()

print(f"Created: {doc.name}")
```

### Read
```python
# Document ophalen
doc = frappe.get_doc('Task', 'TASK-00001')
print(f"Subject: {doc.subject}")
print(f"Status: {doc.status}")

# Alleen specifieke velden
subject, status = frappe.db.get_value('Task', 'TASK-00001', ['subject', 'status'])
```

### Update
```python
# Via ORM (met validaties)
doc = frappe.get_doc('Task', 'TASK-00001')
doc.status = 'Working'
doc.save()

# Direct database update (zonder validaties)
frappe.db.set_value('Task', 'TASK-00001', 'status', 'Completed')
```

### Delete
```python
frappe.delete_doc('Task', 'TASK-00001')
```

---

## Voorbeeld 2: Lijst Queries

### Gefilterde Lijst
```python
# Open high-priority taken
tasks = frappe.get_all('Task',
    filters={
        'status': 'Open',
        'priority': 'High'
    },
    fields=['name', 'subject', 'assigned_to', 'exp_end_date'],
    order_by='exp_end_date asc',
    page_length=50
)

for task in tasks:
    print(f"{task.name}: {task.subject} (Due: {task.exp_end_date})")
```

### Met OR Filters
```python
# Taken die urgent zijn OF verlopen
urgent_tasks = frappe.get_all('Task',
    filters={'docstatus': 0},
    or_filters={
        'priority': 'Urgent',
        'exp_end_date': ['<', frappe.utils.today()]
    },
    fields=['name', 'subject', 'priority', 'exp_end_date']
)
```

### Paginering
```python
def get_all_invoices():
    """Haal alle facturen op met paginering."""
    page = 0
    page_size = 100
    all_invoices = []
    
    while True:
        batch = frappe.get_all('Sales Invoice',
            filters={'docstatus': 1},
            fields=['name', 'customer', 'grand_total'],
            start=page * page_size,
            page_length=page_size
        )
        
        if not batch:
            break
            
        all_invoices.extend(batch)
        page += 1
    
    return all_invoices
```

---

## Voorbeeld 3: Aggregaties

### Met get_list
```python
# v14/v15 syntax
stats = frappe.get_all('Task',
    filters={'docstatus': 0},
    fields=['status', 'count(name) as count'],
    group_by='status'
)

for stat in stats:
    print(f"{stat.status}: {stat.count} taken")
```

### Met Query Builder
```python
from frappe.query_builder.functions import Count, Sum

Task = frappe.qb.DocType('Task')

stats = (
    frappe.qb.from_(Task)
    .select(
        Task.status,
        Count(Task.name).as_('count'),
        Sum(Task.expected_time).as_('total_hours')
    )
    .where(Task.docstatus == 0)
    .groupby(Task.status)
).run(as_dict=True)

for stat in stats:
    print(f"{stat.status}: {stat.count} taken, {stat.total_hours}h totaal")
```

---

## Voorbeeld 4: JOIN Queries

### Sales Report
```python
from frappe.query_builder.functions import Sum

SI = frappe.qb.DocType('Sales Invoice')
Customer = frappe.qb.DocType('Customer')

report = (
    frappe.qb.from_(SI)
    .inner_join(Customer)
    .on(SI.customer == Customer.name)
    .select(
        Customer.customer_name,
        Customer.territory,
        Sum(SI.grand_total).as_('total_sales'),
        Count(SI.name).as_('invoice_count')
    )
    .where(SI.docstatus == 1)
    .where(SI.posting_date >= '2024-01-01')
    .groupby(Customer.name)
    .orderby(Sum(SI.grand_total), order='desc')
    .limit(10)
).run(as_dict=True)

for row in report:
    print(f"{row.customer_name}: {row.total_sales} ({row.invoice_count} facturen)")
```

### Met Raw SQL
```python
results = frappe.db.sql("""
    SELECT 
        c.customer_name,
        c.territory,
        SUM(si.grand_total) as total_sales,
        COUNT(si.name) as invoice_count
    FROM `tabSales Invoice` si
    INNER JOIN `tabCustomer` c ON si.customer = c.name
    WHERE si.docstatus = 1
    AND si.posting_date >= %(from_date)s
    GROUP BY c.name
    ORDER BY total_sales DESC
    LIMIT 10
""", {'from_date': '2024-01-01'}, as_dict=True)
```

---

## Voorbeeld 5: Batch Verwerking

### N+1 Vermijden
```python
def process_orders(orders):
    """Process orders met geoptimaliseerde database calls."""
    
    # ❌ FOUT - N+1 queries
    # for order in orders:
    #     customer = frappe.get_doc('Customer', order.customer)
    
    # ✅ CORRECT - Batch fetch
    customer_names = list(set(o.customer for o in orders))
    
    customers = {c.name: c for c in frappe.get_all(
        'Customer',
        filters={'name': ['in', customer_names]},
        fields=['name', 'customer_name', 'customer_group', 'territory']
    )}
    
    for order in orders:
        customer = customers.get(order.customer)
        if customer:
            print(f"Order {order.name} van {customer.customer_name}")
```

### Bulk Update
```python
# v15+ bulk_update
def close_old_tasks():
    """Sluit alle taken ouder dan 30 dagen."""
    
    old_tasks = frappe.get_all('Task',
        filters={
            'status': 'Open',
            'creation': ['<', frappe.utils.add_days(frappe.utils.today(), -30)]
        },
        pluck='name'
    )
    
    if old_tasks:
        updates = {name: {'status': 'Closed'} for name in old_tasks}
        frappe.db.bulk_update('Task', updates, chunk_size=100)
        frappe.db.commit()
        
        print(f"Closed {len(old_tasks)} old tasks")
```

---

## Voorbeeld 6: Caching Pattern

### Dashboard met Cache
```python
from frappe.utils.caching import redis_cache

@redis_cache(ttl=300)  # 5 minuten
def get_sales_dashboard(user):
    """Cached sales dashboard data."""
    
    # Basis stats
    today = frappe.utils.today()
    month_start = frappe.utils.get_first_day(today)
    
    # Dit jaar
    this_month = frappe.db.sql("""
        SELECT SUM(grand_total) as total
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND posting_date >= %(month_start)s
    """, {'month_start': month_start}, as_dict=True)[0].total or 0
    
    # Open orders
    open_orders = frappe.db.count('Sales Order', {
        'docstatus': 1,
        'status': ['in', ['To Deliver and Bill', 'To Bill', 'To Deliver']]
    })
    
    # Top klanten
    top_customers = frappe.db.sql("""
        SELECT customer_name, SUM(grand_total) as total
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        AND posting_date >= %(month_start)s
        GROUP BY customer
        ORDER BY total DESC
        LIMIT 5
    """, {'month_start': month_start}, as_dict=True)
    
    return {
        'this_month_sales': this_month,
        'open_orders': open_orders,
        'top_customers': top_customers
    }

# Invalideer bij nieuwe factuur
class SalesInvoice(Document):
    def on_submit(self):
        get_sales_dashboard.clear_cache()
```

---

## Voorbeeld 7: Transactie met Rollback

```python
def process_payment(invoice_name, amount):
    """Process betaling met transactie rollback bij fout."""
    
    frappe.db.savepoint('before_payment')
    
    try:
        # Get invoice
        invoice = frappe.get_doc('Sales Invoice', invoice_name)
        
        # Create payment entry
        pe = frappe.get_doc({
            'doctype': 'Payment Entry',
            'payment_type': 'Receive',
            'party_type': 'Customer',
            'party': invoice.customer,
            'paid_amount': amount,
            'received_amount': amount,
            'references': [{
                'reference_doctype': 'Sales Invoice',
                'reference_name': invoice_name,
                'allocated_amount': amount
            }]
        })
        pe.insert()
        pe.submit()
        
        # Update invoice
        invoice.db_set('status', 'Paid')
        
        frappe.db.commit()
        return {'success': True, 'payment': pe.name}
        
    except Exception as e:
        frappe.db.rollback(save_point='before_payment')
        frappe.log_error(frappe.get_traceback(), 'Payment Processing Error')
        return {'success': False, 'error': str(e)}
```

---

## Voorbeeld 8: Permission Check

```python
def get_user_documents(doctype, user=None):
    """Haal documenten op met permission check."""
    
    user = user or frappe.session.user
    
    # Check read permission
    if not frappe.has_permission(doctype, 'read', user=user):
        frappe.throw(f"Geen leesrechten voor {doctype}", frappe.PermissionError)
    
    # get_list past automatisch user permissions toe
    docs = frappe.db.get_list(doctype,
        fields=['name', 'owner', 'creation'],
        order_by='creation desc',
        page_length=100
    )
    
    return docs

def update_document_secure(doctype, name, values):
    """Update document met permission check."""
    
    # Check write permission
    if not frappe.has_permission(doctype, 'write', doc=name):
        frappe.throw("Geen schrijfrechten", frappe.PermissionError)
    
    doc = frappe.get_doc(doctype, name)
    doc.update(values)
    doc.save()
    
    return doc.name
```
