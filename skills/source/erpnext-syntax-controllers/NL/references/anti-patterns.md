# Anti-Patterns Reference

Veelgemaakte fouten bij Document Controllers en correcte alternatieven.

## Inhoudsopgave

1. [Lifecycle Hook Fouten](#lifecycle-hook-fouten)
2. [Database Operatie Fouten](#database-operatie-fouten)
3. [Permission en Validatie Fouten](#permission-en-validatie-fouten)
4. [Performance Anti-Patterns](#performance-anti-patterns)
5. [Override en Extensie Fouten](#override-en-extensie-fouten)
6. [Async en Queue Fouten](#async-en-queue-fouten)

---

## Lifecycle Hook Fouten

### âŒ Wijzigingen na on_update

**Probleem**: Wijzigingen aan `self` in `on_update` worden niet opgeslagen.

```python
# âŒ FOUT - wijziging verdwijnt
def on_update(self):
    self.status = "Completed"  # Wordt NIET opgeslagen in database
    self.modified_by = frappe.session.user  # Verloren!
```

**Waarom**: `on_update` draait NA de database operatie. Het document is al opgeslagen.

```python
# âœ… GOED - gebruik db_set voor post-save wijzigingen
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "status", "Completed")
    # Of meerdere velden:
    frappe.db.set_value(self.doctype, self.name, {
        "status": "Completed",
        "completed_at": frappe.utils.now()
    })
```

```python
# âœ… GOED - alternatief: doe berekeningen in validate
def validate(self):
    if self.all_items_delivered():
        self.status = "Completed"  # Dit wordt WEL opgeslagen
```

---

### âŒ Recursive Save

**Probleem**: `save()` aanroepen in `on_update` veroorzaakt infinite loop.

```python
# âŒ FOUT - infinite loop
def on_update(self):
    self.counter = (self.counter or 0) + 1
    self.save()  # Triggert on_update â†’ save() â†’ on_update â†’ ...
```

```python
# âœ… GOED - gebruik db_set (triggert GEEN hooks)
def on_update(self):
    new_count = (self.counter or 0) + 1
    frappe.db.set_value(
        self.doctype, self.name, 
        "counter", new_count, 
        update_modified=False  # Voorkom modified timestamp update
    )
```

```python
# âœ… GOED - gebruik flag om herhaalde save te voorkomen
def on_update(self):
    if self.flags.get('in_recursive_update'):
        return
    
    self.flags.in_recursive_update = True
    # ... andere operaties ...
```

---

### âŒ Verkeerde Hook voor Validatie

**Probleem**: Validatie in `on_update` kan geen fout meer gooien.

```python
# âŒ FOUT - te laat voor validatie
def on_update(self):
    if self.grand_total < 0:
        frappe.throw("Invalid total")  # Document is al opgeslagen!
```

**Waarom**: Als je in `on_update` een error gooit, is het document al opgeslagen. De fout wordt wel getoond, maar de data staat in de database.

```python
# âœ… GOED - valideer in validate hook
def validate(self):
    if self.grand_total < 0:
        frappe.throw("Invalid total")  # Blokkeert save
```

---

### âŒ after_insert vs on_update Verwarring

**Probleem**: `after_insert` wordt alleen bij INSERT aangeroepen, niet bij UPDATE.

```python
# âŒ FOUT - draait alleen bij creatie
def after_insert(self):
    self.send_notification()  # Nooit bij updates!
```

```python
# âœ… GOED - gebruik on_update voor alle saves
def on_update(self):
    if self.is_new():  # Check of het een nieuw document is
        self.send_welcome_notification()
    else:
        self.send_update_notification()
```

```python
# âœ… GOED - gebruik get_doc_before_save
def on_update(self):
    old = self.get_doc_before_save()
    if old is None:
        # Dit is een nieuw document
        self.send_welcome_notification()
```

---

## Database Operatie Fouten

### âŒ Commit in Controllers

**Probleem**: Handmatige commits verstoren Frappe's transaction management.

```python
# âŒ FOUT - verstoor transaction
def on_update(self):
    frappe.db.sql("UPDATE tabItem SET ...")
    frappe.db.commit()  # NIET DOEN
```

**Waarom**: Frappe handelt commits automatisch af aan het einde van een request. Tussentijdse commits kunnen partial updates veroorzaken bij errors.

```python
# âœ… GOED - laat Frappe commits afhandelen
def on_update(self):
    frappe.db.sql("UPDATE tabItem SET ...")
    # Geen commit nodig - Frappe doet dit automatisch
```

---

### âŒ db_insert/db_update Misbruik

**Probleem**: `db_insert()` en `db_update()` bypass alle validatie.

```python
# âŒ FOUT - bypass alle hooks en validatie
def create_related_doc(self):
    doc = frappe.get_doc({"doctype": "Task", "title": "New Task"})
    doc.db_insert()  # Geen validate, geen permissions check
```

```python
# âœ… GOED - gebruik insert() of save()
def create_related_doc(self):
    doc = frappe.get_doc({"doctype": "Task", "title": "New Task"})
    doc.insert()  # Alle hooks worden uitgevoerd
```

**Uitzondering**: `db_insert()`/`db_update()` alleen gebruiken voor bulk operaties met bewuste bypass:

```python
# âœ… ACCEPTABEL - bulk import met bewuste bypass
def bulk_import_items(items):
    for item_data in items:
        doc = frappe.get_doc({"doctype": "Item", **item_data})
        doc.flags.ignore_permissions = True
        doc.flags.ignore_validate = True
        doc.db_insert()  # Sneller voor bulk, maar wees bewust van risico's
```

---

### âŒ SQL Injection Risico

**Probleem**: User input direct in SQL queries.

```python
# âŒ FOUT - SQL injection mogelijk
def get_items(self):
    return frappe.db.sql(f"""
        SELECT * FROM tabItem WHERE name = '{self.item_code}'
    """)
```

```python
# âœ… GOED - gebruik parameterized queries
def get_items(self):
    return frappe.db.sql("""
        SELECT * FROM tabItem WHERE name = %s
    """, [self.item_code])
```

```python
# âœ… GOED - gebruik frappe.db.get_all
def get_items(self):
    return frappe.get_all("Item", filters={"name": self.item_code})
```

---

## Permission en Validatie Fouten

### âŒ Missende Permission Check

**Probleem**: Gevoelige operaties zonder permission check.

```python
# âŒ FOUT - iedereen kan salaris aanpassen
@frappe.whitelist()
def update_salary(employee, new_salary):
    frappe.db.set_value("Employee", employee, "salary", new_salary)
```

```python
# âœ… GOED - check permissions
@frappe.whitelist()
def update_salary(employee, new_salary):
    if not frappe.has_permission("Employee", "write"):
        frappe.throw("Not permitted")
    
    # Extra check voor gevoelige velden
    if not frappe.has_role("HR Manager"):
        frappe.throw("Only HR Manager can update salary")
    
    frappe.db.set_value("Employee", employee, "salary", new_salary)
```

---

### âŒ ignore_permissions Misbruik

**Probleem**: Overal `ignore_permissions=True` gebruiken.

```python
# âŒ FOUT - security bypass overal
def on_update(self):
    doc = frappe.get_doc("Sales Invoice", self.invoice)
    doc.flags.ignore_permissions = True
    doc.submit()  # Iedereen kan nu invoices submitten!
```

```python
# âœ… GOED - alleen waar nodig, met duidelijke reden
def on_update(self):
    # System operation - explicitly bypassing permissions
    # Reason: This is a background job running as Administrator
    if frappe.session.user == "Administrator":
        doc = frappe.get_doc("Sales Invoice", self.invoice)
        doc.flags.ignore_permissions = True
        doc.submit()
```

---

### âŒ Validatie Alleen aan Client-Side

**Probleem**: Alleen JavaScript validatie, geen server validatie.

```python
# âŒ FOUT - geen server validatie
class Order(Document):
    pass  # Vertrouwt volledig op client-side validation
```

```python
# âœ… GOED - altijd server-side validatie
class Order(Document):
    def validate(self):
        # Dupliceer kritieke validaties van client-side
        if not self.items:
            frappe.throw(_("Items required"))
        if self.discount_percent > 50:
            frappe.throw(_("Discount cannot exceed 50%"))
```

---

## Performance Anti-Patterns

### âŒ N+1 Query Problem

**Probleem**: Database query in loop.

```python
# âŒ FOUT - N+1 queries
def validate(self):
    for item in self.items:  # N items
        stock = frappe.db.get_value("Bin", 
            {"item_code": item.item_code, "warehouse": item.warehouse},
            "actual_qty"
        )  # N queries!
        if item.qty > stock:
            frappe.throw(f"Insufficient stock for {item.item_code}")
```

```python
# âœ… GOED - batch query
def validate(self):
    # Haal alle stock data in Ã©Ã©n query
    item_warehouse_pairs = [
        [item.item_code, item.warehouse] for item in self.items
    ]
    
    stock_data = frappe.get_all("Bin",
        filters=[
            ["item_code", "in", [p[0] for p in item_warehouse_pairs]],
            ["warehouse", "in", [p[1] for p in item_warehouse_pairs]]
        ],
        fields=["item_code", "warehouse", "actual_qty"]
    )
    
    # Maak lookup dict
    stock_map = {
        (d.item_code, d.warehouse): d.actual_qty 
        for d in stock_data
    }
    
    for item in self.items:
        stock = stock_map.get((item.item_code, item.warehouse), 0)
        if item.qty > stock:
            frappe.throw(f"Insufficient stock for {item.item_code}")
```

---

### âŒ Heavy Operations in validate

**Probleem**: Langlopende operaties blokkeren de gebruiker.

```python
# âŒ FOUT - blokkeert UI
def validate(self):
    self.generate_100_page_pdf()  # Duurt 30 seconden
    self.send_emails_to_all_customers()  # 1000 emails
```

```python
# âœ… GOED - enqueue zware taken
def validate(self):
    # Snelle validatie hier
    pass

def on_update(self):
    # Enqueue langlopende taken
    frappe.enqueue(
        'myapp.tasks.generate_large_pdf',
        queue='long',
        doc_name=self.name,
        enqueue_after_commit=True  # Wacht tot save compleet
    )
    
    frappe.enqueue(
        'myapp.tasks.send_bulk_emails',
        queue='long',
        doc_name=self.name
    )
```

---

### âŒ Ongebruikte Cache

**Probleem**: Herhaaldelijk dezelfde data ophalen.

```python
# âŒ FOUT - meerdere DB calls voor zelfde data
def validate(self):
    customer = frappe.get_doc("Customer", self.customer)
    # ... later in dezelfde method ...
    customer_email = frappe.get_value("Customer", self.customer, "email")
    customer_credit = frappe.get_value("Customer", self.customer, "credit_limit")
```

```python
# âœ… GOED - gebruik caching
def validate(self):
    customer = frappe.get_cached_doc("Customer", self.customer)
    email = customer.email
    credit = customer.credit_limit
```

---

## Override en Extensie Fouten

### âŒ Missende super() Aanroep

**Probleem**: Parent functionaliteit wordt overgeslagen.

```python
# âŒ FOUT - parent validate wordt overgeslagen
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        self.my_custom_validation()
        # Parent validate nooit aangeroepen!
```

**Gevolgen**: Alle standaard ERPNext validaties worden overgeslagen.

```python
# âœ… GOED - altijd super() aanroepen
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # Eerst parent
        self.my_custom_validation()
```

```python
# âœ… GOED - of parent na custom (afhankelijk van behoefte)
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        # Pre-processing die voor standard validatie moet
        self.prepare_data()
        
        super().validate()  # Standard validatie
        
        # Post-processing
        self.finalize_data()
```

---

### âŒ doc_events met Verkeerde Signature

**Probleem**: Handler functie met verkeerde parameters.

```python
# âŒ FOUT - verkeerde signature
def on_validate(document):  # Fout: moet 'doc' en optioneel 'method' zijn
    pass
```

```python
# âœ… GOED - correcte signature
def on_validate(doc, method=None):
    """
    Args:
        doc: Het document object
        method: Naam van de hook (bijv. 'validate')
    """
    pass
```

---

### âŒ Override voor Minor Changes

**Probleem**: Hele controller overriden voor kleine wijziging.

```python
# âŒ OVERKILL - hele controller override voor 1 check
# hooks.py
override_doctype_class = {"Sales Invoice": "myapp.override.CustomSI"}

# myapp/override.py (150 regels)
class CustomSI(SalesInvoice):
    def validate(self):
        super().validate()
        if self.total < 100:
            frappe.msgprint("Small order")
```

```python
# âœ… BETER - gebruik doc_events voor kleine toevoegingen
# hooks.py
doc_events = {
    "Sales Invoice": {
        "validate": "myapp.events.si_validate"
    }
}

# myapp/events.py (10 regels)
def si_validate(doc, method=None):
    if doc.total < 100:
        frappe.msgprint("Small order")
```

---

## Async en Queue Fouten

### âŒ Enqueue zonder Error Handling

**Probleem**: Background job failures worden niet afgehandeld.

```python
# âŒ FOUT - geen error handling
def on_submit(self):
    frappe.enqueue('myapp.tasks.process', doc_name=self.name)
```

```python
# âœ… GOED - met error handling en retry
def on_submit(self):
    frappe.enqueue(
        'myapp.tasks.process',
        doc_name=self.name,
        queue='short',
        timeout=300,
        retry=3,  # Automatische retry
        enqueue_after_commit=True
    )

# myapp/tasks.py
def process(doc_name):
    try:
        doc = frappe.get_doc("MyDocType", doc_name)
        doc.do_processing()
    except Exception as e:
        frappe.log_error(
            message=f"Processing failed for {doc_name}: {str(e)}",
            title="Process Error"
        )
        raise  # Re-raise voor retry mechanisme
```

---

### âŒ Synchrone Externe API Calls

**Probleem**: Externe API in validate blokkeert gebruiker.

```python
# âŒ FOUT - gebruiker wacht op externe API
def validate(self):
    response = requests.get("https://api.external.com/validate", 
                           timeout=30)  # Kan 30 sec duren!
    if not response.ok:
        frappe.throw("External validation failed")
```

```python
# âœ… GOED - async validatie met status tracking
def validate(self):
    # Snelle lokale validatie
    self.status = "Pending External Validation"

def on_update(self):
    # Async externe validatie
    frappe.enqueue(
        'myapp.integrations.validate_external',
        doc_name=self.name,
        queue='short'
    )

# myapp/integrations.py
def validate_external(doc_name):
    try:
        response = requests.get("https://api.external.com/validate")
        status = "Validated" if response.ok else "Validation Failed"
    except requests.Timeout:
        status = "Validation Timeout"
    
    frappe.db.set_value("MyDocType", doc_name, "status", status)
```

---

## Samenvatting Best Practices

| Anti-Pattern | Oplossing |
|--------------|-----------|
| self.x in on_update | Gebruik `frappe.db.set_value()` |
| save() in on_update | Gebruik `db_set()` of flags |
| Validatie in on_update | Verplaats naar `validate` |
| frappe.db.commit() | Verwijder - Frappe handelt af |
| Query in loop | Batch query met get_all |
| Heavy ops in validate | Gebruik `frappe.enqueue()` |
| Override zonder super() | Altijd `super().method()` aanroepen |
| ignore_permissions overal | Alleen waar nodig met documentatie |
| Sync externe API | Async met enqueue |
