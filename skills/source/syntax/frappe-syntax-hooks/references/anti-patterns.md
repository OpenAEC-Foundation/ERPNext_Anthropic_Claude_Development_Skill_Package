# Anti-Patterns en Best Practices

Veelgemaakte fouten in hooks.py en hoe ze te vermijden.

---

## Doc Events Anti-Patterns

### ❌ Commit in Event Handlers

```python
# FOUT - Frappe handelt commits automatisch af
def on_update(doc, method=None):
    update_related_doc(doc)
    frappe.db.commit()  # NIET DOEN - kan transactie breken

# ✅ GOED - geen commit nodig
def on_update(doc, method=None):
    update_related_doc(doc)
    # Frappe commit automatisch aan het einde van de request
```

**Waarom fout?** Manual commits kunnen:
- Deels uitgevoerde transacties achterlaten bij errors
- Race conditions veroorzaken
- Database inconsistentie veroorzaken

---

### ❌ Wijzigingen na on_update

```python
# FOUT - wijziging wordt NIET opgeslagen
def on_update(doc, method=None):
    doc.status = "Processed"  # Verloren! Document is al opgeslagen

# ✅ GOED - gebruik db_set
def on_update(doc, method=None):
    frappe.db.set_value(doc.doctype, doc.name, "status", "Processed")
    # OF
    doc.db_set("status", "Processed")
```

**Waarom?** `on_update` draait NA de database save, dus wijzigingen aan `doc` worden niet meer gepersisteerd.

---

### ❌ Heavy Operations in Sync Hooks

```python
# FOUT - blokkeert de gebruiker
def validate(doc, method=None):
    # Dit kan minuten duren!
    for customer in frappe.get_all("Customer"):
        recalculate_balance(customer.name)

# ✅ GOED - gebruik enqueue voor zware taken
def on_update(doc, method=None):
    frappe.enqueue(
        "myapp.tasks.recalculate_all_balances",
        queue="long",
        timeout=1500
    )
```

**Vuistregel**: Als het langer dan 5 seconden kan duren, gebruik enqueue.

---

### ❌ Oneindige Loops

```python
# FOUT - triggert zichzelf
def on_update(doc, method=None):
    doc.modified_by = "System"
    doc.save()  # Triggert on_update opnieuw! → Oneindige loop

# ✅ GOED - gebruik flags om loops te voorkomen
def on_update(doc, method=None):
    if doc.flags.get("in_custom_update"):
        return
    
    doc.flags.in_custom_update = True
    doc.db_set("modified_by", "System")

# ✅ OF gebruik db_set (triggert geen events)
def on_update(doc, method=None):
    frappe.db.set_value(doc.doctype, doc.name, "modified_by", "System")
```

---

## Override Anti-Patterns

### ❌ Vergeten super() Aan te Roepen

```python
# FOUT - parent validate niet aangeroepen
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        self.custom_validation()  # Parent logica overgeslagen!

# ✅ GOED - altijd super() eerst
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # Parent logica uitvoeren
        self.custom_validation()  # Dan custom logica
```

**Gevolg van vergeten super()**: Core validatie, berekeningen en side effects worden overgeslagen.

---

### ❌ Verkeerde Method Signature bij Override

```python
# FOUT - signature komt niet overeen
# Origineel: def get_count(doctype, filters=None, debug=False, cache=False)
override_whitelisted_methods = {
    "frappe.client.get_count": "myapp.overrides.my_get_count"
}

def my_get_count(doctype):  # Mist parameters!
    return frappe.db.count(doctype)

# ✅ GOED - exacte signature
def my_get_count(doctype, filters=None, debug=False, cache=False):
    # Custom logica
    count = frappe.db.count(doctype, filters)
    log_count_query(doctype)
    return count
```

---

## Scheduler Anti-Patterns

### ❌ Zware Taken in Default Queue

```python
# FOUT - timeout na 5 minuten
scheduler_events = {
    "daily": ["myapp.tasks.sync_all_records"]  # Duurt 20 min!
}

# ✅ GOED - gebruik _long variant
scheduler_events = {
    "daily_long": ["myapp.tasks.sync_all_records"]  # 25 min timeout
}
```

| Queue | Timeout |
|-------|---------|
| default (hourly, daily, etc.) | 300 sec (5 min) |
| long (hourly_long, daily_long, etc.) | 1500 sec (25 min) |

---

### ❌ Wijzigen Zonder Migrate

```python
# Na het wijzigen van scheduler_events:
# FOUT - wijzigingen worden niet opgepikt
# (scheduler config is gecached)

# ✅ GOED - altijd migrate na wijzigingen
# $ bench --site sitename migrate
```

---

### ❌ Tasks met Argumenten

```python
# FOUT - scheduler tasks krijgen geen argumenten
def my_task(company_name):
    process_company(company_name)

# ✅ GOED - haal data op binnen de functie
def my_task():
    companies = frappe.get_all("Company")
    for company in companies:
        process_company(company.name)
```

---

## Permission Anti-Patterns

### ❌ Geen User None Check

```python
# FOUT - user kan None zijn!
def my_query_conditions(user):
    return f"owner = {frappe.db.escape(user)}"  # Error als user None

# ✅ GOED - altijd None checken
def my_query_conditions(user):
    if not user:
        user = frappe.session.user
    return f"owner = {frappe.db.escape(user)}"
```

---

### ❌ SQL Injection Kwetsbaar

```python
# FOUT - SQL injection mogelijk
def my_query_conditions(user):
    return f"owner = '{user}'"  # Kwetsbaar!

# ✅ GOED - gebruik frappe.db.escape
def my_query_conditions(user):
    if not user:
        user = frappe.session.user
    return f"owner = {frappe.db.escape(user)}"
```

---

### ❌ Verwarren get_list en get_all

```python
# permission_query_conditions werkt ALLEEN met get_list
# FOUT verwachting:
frappe.db.get_all("Sales Invoice")  # NEGEERT permissions!

# ✅ GOED - gebruik get_list voor permission filtering
frappe.db.get_list("Sales Invoice")  # Respecteert permissions
```

---

## Fixtures Anti-Patterns

### ❌ Fixtures Zonder Filters

```python
# FOUT - exporteert ALLES, mogelijk honderden records
fixtures = ["Custom Field"]

# ✅ GOED - filter op relevante records
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]}
]
```

**Risico**: Zonder filters exporteer je mogelijk custom fields van andere apps, wat conflicten veroorzaakt.

---

### ❌ Transactionele Data als Fixture

```python
# FOUT - nooit transacties exporteren
fixtures = [
    "Sales Invoice",
    "Stock Entry"
]

# ✅ GOED - alleen configuratie
fixtures = [
    "Custom Field",
    "Property Setter",
    "Role"
]
```

---

## Boot Info Anti-Patterns

### ❌ Gevoelige Data in Bootinfo

```python
# FOUT - API keys/secrets in client-side JavaScript
def extend_boot(bootinfo):
    bootinfo.api_key = frappe.get_single("Settings").secret_key  # NOOIT!
    bootinfo.db_password = get_db_password()  # ABSOLUUT NIET!

# ✅ GOED - alleen publieke config
def extend_boot(bootinfo):
    bootinfo.app_version = "1.0.0"
    bootinfo.feature_flags = {"new_ui": True}
```

---

### ❌ Zware Queries in Bootinfo

```python
# FOUT - draait bij ELKE page load
def extend_boot(bootinfo):
    bootinfo.all_customers = frappe.get_all("Customer")  # Duizenden records!
    bootinfo.full_report = generate_complex_report()  # Seconden processing!

# ✅ GOED - minimale, gecachede data
def extend_boot(bootinfo):
    bootinfo.customer_count = frappe.cache().get_value("customer_count")
    if not bootinfo.customer_count:
        bootinfo.customer_count = frappe.db.count("Customer")
        frappe.cache().set_value("customer_count", bootinfo.customer_count)
```

---

## Best Practices Samenvatting

### ✅ DO

| Practice | Reden |
|----------|-------|
| Altijd `super()` bij overrides | Behoud core functionaliteit |
| `bench migrate` na scheduler wijzigingen | Config is gecached |
| `frappe.db.escape()` voor SQL | Voorkom injection |
| `_long` voor zware taken | Voorkom timeouts |
| Filters bij fixtures | Voorkom conflicten |
| None check voor user | Voorkom errors |

### ❌ DON'T

| Anti-Pattern | Probleem |
|--------------|----------|
| `frappe.db.commit()` in handlers | Breekt transacties |
| `doc.field = x` in on_update | Wordt niet opgeslagen |
| Zware operaties in sync hooks | Blokkeert gebruiker |
| `get_all` verwachten met permissions | Negeert permission hooks |
| Secrets in bootinfo | Security risico |
| Fixtures zonder filters | Exporteert te veel |

---

## Debug Checklist

Wanneer hooks niet werken:

1. **Scheduler niet actief?**
   ```bash
   bench --site sitename scheduler status
   bench --site sitename scheduler enable
   ```

2. **Migrate vergeten?**
   ```bash
   bench --site sitename migrate
   ```

3. **Cache issue?**
   ```bash
   bench --site sitename clear-cache
   ```

4. **Syntax error?**
   ```bash
   python -c "import myapp.hooks"
   ```

5. **Logs checken**
   ```bash
   tail -f ~/frappe-bench/logs/scheduler.log
   tail -f ~/frappe-bench/logs/worker.log
   ```
