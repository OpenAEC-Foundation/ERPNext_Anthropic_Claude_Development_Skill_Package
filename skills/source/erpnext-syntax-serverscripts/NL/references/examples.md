# Server Script Voorbeelden

## Inhoudsopgave

1. [Document Event Voorbeelden](#document-event-voorbeelden)
2. [API Voorbeelden](#api-voorbeelden)
3. [Scheduler Event Voorbeelden](#scheduler-event-voorbeelden)
4. [Permission Query Voorbeelden](#permission-query-voorbeelden)

---

## Document Event Voorbeelden

### 1. Validatie met foutmelding

**Script Type**: Document Event  
**DocType Event**: Before Save  
**Reference DocType**: Sales Invoice

```python
# Valideer minimum orderbedrag
if doc.grand_total < 100:
    frappe.throw("Minimum orderbedrag is €100")

# Valideer percentage
if doc.discount_percentage and doc.discount_percentage > 50:
    frappe.throw("Korting mag niet meer dan 50% zijn", title="Validatie Error")
```

### 2. Auto-berekening velden

**Script Type**: Document Event  
**DocType Event**: Before Save  
**Reference DocType**: Sales Order

```python
# Bereken totaal van child items
doc.total_qty = sum(item.qty or 0 for item in doc.items)
doc.total_weight = sum((item.qty or 0) * (item.weight_per_unit or 0) for item in doc.items)

# Zet status op basis van totaal
if doc.grand_total > 10000:
    doc.priority = "High"
    doc.requires_approval = 1
```

### 3. Auto-fill gerelateerde data

**Script Type**: Document Event  
**DocType Event**: Before Save  
**Reference DocType**: Sales Invoice

```python
# Haal customer data op als nog niet gezet
if doc.customer and not doc.customer_name:
    doc.customer_name = frappe.db.get_value("Customer", doc.customer, "customer_name")

# Haal territory van customer
if doc.customer and not doc.territory:
    doc.territory = frappe.db.get_value("Customer", doc.customer, "territory")
```

### 4. Gerelateerd document aanmaken

**Script Type**: Document Event  
**DocType Event**: After Insert  
**Reference DocType**: Sales Order

```python
# Maak ToDo voor sales team
frappe.get_doc({
    "doctype": "ToDo",
    "allocated_to": doc.owner,
    "reference_type": "Sales Order",
    "reference_name": doc.name,
    "description": f"Nieuwe order {doc.name} - Volg op met klant",
    "date": frappe.utils.add_days(frappe.utils.today(), 1)
}).insert(ignore_permissions=True)
```

### 5. Pre-submit validatie

**Script Type**: Document Event  
**DocType Event**: Before Submit  
**Reference DocType**: Purchase Order

```python
# Check budget approval voor grote orders
if doc.grand_total > 50000:
    if not doc.budget_approval:
        frappe.throw("Budget goedkeuring vereist voor orders boven €50.000")
    
    # Check of approver niet de aanmaker is
    if doc.approved_by == doc.owner:
        frappe.throw("Order kan niet door aanmaker worden goedgekeurd")
```

### 6. Post-submit acties

**Script Type**: Document Event  
**DocType Event**: After Submit  
**Reference DocType**: Sales Invoice

```python
# Update klant statistieken
customer_doc = frappe.get_doc("Customer", doc.customer)

# Tel totaal aantal facturen
total_invoices = frappe.db.count("Sales Invoice", 
    filters={"customer": doc.customer, "docstatus": 1})

# Update custom field
frappe.db.set_value("Customer", doc.customer, "total_invoices", total_invoices)

# Stuur notificatie bij high-value invoice
if doc.grand_total > 10000:
    frappe.msgprint(f"High-value factuur {doc.name} aangemaakt", alert=True)
```

### 7. Cancel validatie

**Script Type**: Document Event  
**DocType Event**: Before Cancel  
**Reference DocType**: Sales Invoice

```python
# Check of er betalingen zijn
payments = frappe.get_all("Payment Entry Reference",
    filters={
        "reference_doctype": "Sales Invoice",
        "reference_name": doc.name,
        "docstatus": 1
    },
    fields=["parent"]
)

if payments:
    frappe.throw(
        f"Kan niet annuleren: factuur heeft {len(payments)} gekoppelde betaling(en). "
        "Annuleer eerst de betalingen.",
        title="Annulering Geblokkeerd"
    )
```

### 8. Audit logging

**Script Type**: Document Event  
**DocType Event**: After Save  
**Reference DocType**: Sales Order

```python
# Log belangrijke wijzigingen
log_msg = f"Sales Order {doc.name} bijgewerkt\n"
log_msg += f"Status: {doc.status}\n"
log_msg += f"Totaal: {doc.grand_total}\n"
log_msg += f"Gewijzigd door: {frappe.session.user}"

frappe.log_error(log_msg, "Sales Order Audit")
```

---

## API Voorbeelden

### 9. Basis GET endpoint

**Script Type**: API  
**API Method**: get_customer_orders  
**Allow Guest**: No

```python
# Endpoint: /api/method/get_customer_orders?customer=CUST-001

customer = frappe.form_dict.get("customer")
if not customer:
    frappe.throw("Parameter 'customer' is verplicht")

# Check permissions
if not frappe.has_permission("Sales Order", "read"):
    frappe.throw("Geen toegang", frappe.PermissionError)

orders = frappe.get_all("Sales Order",
    filters={
        "customer": customer,
        "docstatus": 1
    },
    fields=["name", "transaction_date", "grand_total", "status"],
    order_by="transaction_date desc",
    limit=20
)

frappe.response["message"] = {
    "customer": customer,
    "orders": orders,
    "count": len(orders)
}
```

### 10. POST endpoint met data verwerking

**Script Type**: API  
**API Method**: update_order_status  
**Allow Guest**: No

```python
# Endpoint: POST /api/method/update_order_status
# Body: {"order": "SO-001", "status": "Completed"}

order_name = frappe.form_dict.get("order")
new_status = frappe.form_dict.get("status")

if not order_name or not new_status:
    frappe.throw("Parameters 'order' en 'status' zijn verplicht")

# Valideer status waarde
valid_statuses = ["Open", "Completed", "On Hold", "Cancelled"]
if new_status not in valid_statuses:
    frappe.throw(f"Ongeldige status. Kies uit: {', '.join(valid_statuses)}")

# Check permission voor specifiek document
if not frappe.has_permission("Sales Order", "write", order_name):
    frappe.throw("Geen wijzigingsrechten voor deze order", frappe.PermissionError)

# Update status
frappe.db.set_value("Sales Order", order_name, "status", new_status)

frappe.response["message"] = {
    "success": True,
    "order": order_name,
    "new_status": new_status
}
```

### 11. Dashboard data endpoint

**Script Type**: API  
**API Method**: get_sales_dashboard  
**Allow Guest**: No

```python
# Endpoint: /api/method/get_sales_dashboard

today = frappe.utils.today()
month_start = frappe.utils.get_first_day(today)

# Orders vandaag
orders_today = frappe.db.count("Sales Order",
    filters={"transaction_date": today, "docstatus": 1})

# Omzet deze maand
month_sales = frappe.db.sql("""
    SELECT COALESCE(SUM(grand_total), 0) as total
    FROM `tabSales Invoice`
    WHERE posting_date >= %(month_start)s
    AND docstatus = 1
""", {"month_start": month_start}, as_dict=True)

# Top 5 klanten
top_customers = frappe.get_all("Sales Invoice",
    filters={"posting_date": [">=", month_start], "docstatus": 1},
    fields=["customer", "sum(grand_total) as total"],
    group_by="customer",
    order_by="total desc",
    limit=5
)

frappe.response["message"] = {
    "orders_today": orders_today,
    "month_sales": month_sales[0].total if month_sales else 0,
    "top_customers": top_customers
}
```

### 12. Publiek endpoint (guest access)

**Script Type**: API  
**API Method**: check_product_availability  
**Allow Guest**: Yes

```python
# Endpoint: /api/method/check_product_availability?item=ITEM-001

item_code = frappe.form_dict.get("item")
if not item_code:
    frappe.throw("Parameter 'item' is verplicht")

# Alleen gepubliceerde items tonen
item = frappe.db.get_value("Item", item_code, 
    ["item_name", "stock_uom", "is_stock_item", "disabled"],
    as_dict=True)

if not item or item.disabled:
    frappe.response["message"] = {
        "available": False,
        "message": "Product niet gevonden"
    }
else:
    # Haal voorraad op (simplified)
    stock = frappe.db.get_value("Bin",
        {"item_code": item_code},
        "sum(actual_qty) as qty") or 0
    
    frappe.response["message"] = {
        "available": stock > 0,
        "item_name": item.item_name,
        "stock_qty": stock,
        "uom": item.stock_uom
    }
```

---

## Scheduler Event Voorbeelden

### 13. Dagelijkse reminder

**Script Type**: Scheduler Event  
**Event Frequency**: Cron  
**Cron Format**: `0 9 * * *` (dagelijks om 9:00)

```python
# Stuur reminders voor vervallen facturen
today = frappe.utils.today()

overdue_invoices = frappe.get_all("Sales Invoice",
    filters={
        "status": "Unpaid",
        "due_date": ["<", today],
        "docstatus": 1
    },
    fields=["name", "customer", "grand_total", "due_date", "owner"]
)

for inv in overdue_invoices:
    days_overdue = frappe.utils.date_diff(today, inv.due_date)
    
    # Maak ToDo voor sales rep
    if not frappe.db.exists("ToDo", {
        "reference_type": "Sales Invoice",
        "reference_name": inv.name,
        "status": "Open"
    }):
        frappe.get_doc({
            "doctype": "ToDo",
            "allocated_to": inv.owner,
            "reference_type": "Sales Invoice",
            "reference_name": inv.name,
            "description": f"Factuur {inv.name} is {days_overdue} dagen vervallen. Totaal: {inv.grand_total}"
        }).insert(ignore_permissions=True)

frappe.db.commit()
```

### 14. Wekelijkse cleanup

**Script Type**: Scheduler Event  
**Event Frequency**: Cron  
**Cron Format**: `0 2 * * 0` (zondag 02:00)

```python
# Verwijder oude draft documenten (ouder dan 30 dagen)
cutoff_date = frappe.utils.add_days(frappe.utils.today(), -30)

# Zoek oude drafts
old_drafts = frappe.get_all("Sales Order",
    filters={
        "docstatus": 0,
        "modified": ["<", cutoff_date]
    },
    fields=["name"],
    limit=100  # Batch limiet
)

deleted_count = 0
for draft in old_drafts:
    try:
        frappe.delete_doc("Sales Order", draft.name, force=True)
        deleted_count += 1
    except Exception:
        frappe.log_error(
            f"Kon draft {draft.name} niet verwijderen",
            "Cleanup Error"
        )

frappe.db.commit()

if deleted_count > 0:
    frappe.log_error(
        f"Cleanup: {deleted_count} oude drafts verwijderd",
        "Weekly Cleanup"
    )
```

### 15. Elk kwartier sync

**Script Type**: Scheduler Event  
**Event Frequency**: Cron  
**Cron Format**: `*/15 * * * *` (elke 15 minuten)

```python
# Sync externe data (voorbeeld: wisselkoersen)
# Dit is een placeholder - externe API calls werken niet in sandbox

last_sync = frappe.db.get_single_value("Sync Settings", "last_sync") or ""
now = frappe.utils.now()

# Check of sync nodig is
if last_sync:
    minutes_since = frappe.utils.time_diff_in_seconds(now, last_sync) / 60
    if minutes_since < 14:  # Skip als recent gesync'd
        return

# Log sync poging
frappe.log_error(f"Sync gestart om {now}", "External Sync")

# Update last sync time
frappe.db.set_single_value("Sync Settings", "last_sync", now)
frappe.db.commit()
```

### 16. Maandelijkse rapportage

**Script Type**: Scheduler Event  
**Event Frequency**: Cron  
**Cron Format**: `0 6 1 * *` (1e van de maand om 06:00)

```python
# Genereer maandelijkse sales summary
last_month_start = frappe.utils.add_months(
    frappe.utils.get_first_day(frappe.utils.today()), -1)
last_month_end = frappe.utils.get_last_day(last_month_start)

# Sales totalen
summary = frappe.db.sql("""
    SELECT 
        COUNT(*) as invoice_count,
        COALESCE(SUM(grand_total), 0) as total_revenue,
        COUNT(DISTINCT customer) as unique_customers
    FROM `tabSales Invoice`
    WHERE posting_date BETWEEN %(start)s AND %(end)s
    AND docstatus = 1
""", {"start": last_month_start, "end": last_month_end}, as_dict=True)[0]

# Maak rapport record
report_msg = f"""
Maandelijkse Sales Summary
Periode: {last_month_start} tot {last_month_end}

Facturen: {summary.invoice_count}
Omzet: €{summary.total_revenue:,.2f}
Unieke klanten: {summary.unique_customers}
"""

frappe.log_error(report_msg, "Monthly Sales Report")
frappe.db.commit()
```

---

## Permission Query Voorbeelden

### 17. Basis role-based filtering

**Script Type**: Permission Query  
**Reference DocType**: Sales Invoice

```python
# Filter documenten op basis van gebruikersrol
user_roles = frappe.get_roles(user)

if "System Manager" in user_roles or "Accounts Manager" in user_roles:
    # Volledige toegang
    conditions = ""
elif "Sales User" in user_roles:
    # Alleen eigen facturen
    conditions = f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
else:
    # Geen toegang
    conditions = "1=0"
```

### 18. Territory-based filtering

**Script Type**: Permission Query  
**Reference DocType**: Customer

```python
# Filter klanten op basis van user's territory
user_territory = frappe.db.get_value("User", user, "territory")

if not user_territory:
    # Als geen territory, toon niets (of alles voor managers)
    if "Sales Manager" in frappe.get_roles(user):
        conditions = ""
    else:
        conditions = "1=0"
else:
    # Alleen klanten in user's territory
    conditions = f"`tabCustomer`.territory = {frappe.db.escape(user_territory)}"
```

### 19. Company-based filtering

**Script Type**: Permission Query  
**Reference DocType**: Sales Order

```python
# Filter op basis van allowed companies
allowed_companies = frappe.get_all("User Permission",
    filters={"user": user, "allow": "Company"},
    pluck="for_value"
)

if not allowed_companies:
    # Als geen company permissions, gebruik default company
    default_company = frappe.db.get_single_value("Global Defaults", "default_company")
    if default_company:
        conditions = f"`tabSales Order`.company = {frappe.db.escape(default_company)}"
    else:
        conditions = ""
elif len(allowed_companies) == 1:
    conditions = f"`tabSales Order`.company = {frappe.db.escape(allowed_companies[0])}"
else:
    company_list = ", ".join(frappe.db.escape(c) for c in allowed_companies)
    conditions = f"`tabSales Order`.company IN ({company_list})"
```

### 20. Status-based filtering

**Script Type**: Permission Query  
**Reference DocType**: Task

```python
# Toon alleen open taken aan normale users
user_roles = frappe.get_roles(user)

if "Project Manager" in user_roles:
    # Managers zien alles
    conditions = ""
else:
    # Anderen zien alleen hun eigen open taken
    conditions = f"""
        (`tabTask`.owner = {frappe.db.escape(user)} 
         OR `tabTask`.assigned_to = {frappe.db.escape(user)})
        AND `tabTask`.status NOT IN ('Cancelled', 'Completed')
    """
```
