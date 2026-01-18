# Flags Systeem Reference

> Complete documentatie van het Frappe flags systeem voor behaviour override en inter-event communicatie.

---

## Overzicht

Frappe heeft twee niveaus van flags:
1. **Document flags** (`doc.flags`) - Per document instance
2. **Request flags** (`frappe.flags`) - Globaal voor huidige request

---

## Document Flags (doc.flags)

### Permission Bypass Flags

```python
# Bypass alle permission checks
doc.flags.ignore_permissions = True
doc.save()  # Geen permission check

# Voorbeeld: Systeem update zonder user permissions
doc = frappe.get_doc("Sales Order", "SO-00001")
doc.flags.ignore_permissions = True
doc.status = "Closed"
doc.save()
```

### Validation Bypass Flags

```python
# Skip validate() method
doc.flags.ignore_validate = True

# Skip verplichte veld checks
doc.flags.ignore_mandatory = True

# Skip link validatie (linked docs bestaan check)
doc.flags.ignore_links = True

# Combinatie voor bulk import
doc.flags.ignore_validate = True
doc.flags.ignore_mandatory = True
doc.flags.ignore_links = True
doc.insert()
```

### Versioning Flags

```python
# Maak geen version record aan
doc.flags.ignore_version = True
doc.save()  # Geen audit trail voor deze save
```

### Notification Flags (v15)

```python
# Stuur geen realtime update naar browser
doc.flags.notify_update = False
doc.save()  # Browser refresht niet automatisch
```

---

## Flags via insert() en save()

```python
# Insert met flags als parameters
doc.insert(
    ignore_permissions=True,      # Bypass write permissions
    ignore_links=True,            # Bypass link validatie
    ignore_if_duplicate=True,     # Geen error bij duplicate
    ignore_mandatory=True         # Bypass verplichte velden
)

# Save met flags
doc.save(
    ignore_permissions=True,      # Bypass write permissions
    ignore_version=True           # Geen version record
)
```

---

## Request Flags (frappe.flags)

### Systeem Status Flags

```python
# Check of we in import modus zijn
if frappe.flags.in_import:
    # Skip heavy validaties tijdens import
    return

# Check of we in installatie modus zijn
if frappe.flags.in_install:
    # Skip validaties tijdens app installatie
    return

# Check of we in patch/migrate modus zijn
if frappe.flags.in_patch:
    # Skip bepaalde checks tijdens migratie
    return

if frappe.flags.in_migrate:
    # Skip bepaalde checks tijdens migratie
    return
```

### Email Control

```python
# Onderdruk alle email versturen
frappe.flags.mute_emails = True
# Alle emails in deze request worden NIET verstuurd

# Voorbeeld: Bulk operatie zonder email spam
frappe.flags.mute_emails = True
for order_name in order_names:
    doc = frappe.get_doc("Sales Order", order_name)
    doc.submit()  # Geen notification emails
frappe.flags.mute_emails = False
```

### Scheduler Flag

```python
# Check of code draait in scheduler job
if frappe.flags.in_scheduler:
    # Pas gedrag aan voor background execution
    pass
```

---

## Custom Flags voor Inter-Event Communicatie

Gebruik `doc.flags` om informatie door te geven tussen hooks.

### Patroon: Status Change Tracking

```python
class SalesInvoice(Document):
    def validate(self):
        old_doc = self.get_doc_before_save()
        if old_doc and old_doc.status != self.status:
            self.flags.status_changed = True
            self.flags.old_status = old_doc.status
    
    def on_update(self):
        if self.flags.get('status_changed'):
            self.log_status_change(
                from_status=self.flags.old_status,
                to_status=self.status
            )
```

### Patroon: High Value Detection

```python
class SalesOrder(Document):
    def validate(self):
        if self.grand_total > 10000:
            self.flags.high_value = True
    
    def on_submit(self):
        if self.flags.get('high_value'):
            self.notify_finance_team()
            self.request_manager_approval()
```

### Patroon: Skip Recursive Calls

```python
class Task(Document):
    def on_update(self):
        # Voorkom infinite loop bij linked updates
        if self.flags.get('updating_from_project'):
            return
        
        project = frappe.get_doc("Project", self.project)
        project.flags.updating_from_task = True
        project.update_percent_complete()
        project.save()
```

### Patroon: Trigger Source Tracking

```python
class StockEntry(Document):
    def on_submit(self):
        if self.flags.get('from_purchase_receipt'):
            # Dit is getriggerd door Purchase Receipt
            self.add_comment('Info', 'Auto-created from Purchase Receipt')
        elif self.flags.get('from_sales_order'):
            # Dit is getriggerd door Sales Order
            pass

# Aanroep van buiten:
stock_entry.flags.from_purchase_receipt = True
stock_entry.submit()
```

---

## Flags Best Practices

### âœ… DO: Gebruik flags voor tijdelijke state

```python
def validate(self):
    # Goed: flag wordt automatisch opgeruimd na request
    self.flags.needs_notification = self.should_notify()

def on_update(self):
    if self.flags.get('needs_notification'):
        self.send_notification()
```

### âœ… DO: Check flags veilig met get()

```python
# Goed: retourneert None als flag niet bestaat
if self.flags.get('high_value'):
    pass

# Ook goed: met default
if self.flags.get('retry_count', 0) > 3:
    pass
```

### âŒ DON'T: Persisteer flags in database

```python
# Fout: flags zijn tijdelijk, niet voor opslag
def validate(self):
    self.custom_flag_field = self.flags.get('some_flag')  # Slaat verkeerde data op
```

### âŒ DON'T: Afhankelijk van flags tussen requests

```python
# Fout: flags bestaan alleen tijdens huidige request
# Deze flag bestaat niet meer bij volgende request
doc.flags.process_later = True
doc.save()  # Flag is weg na deze request
```

---

## Flags Reference Tabel

### doc.flags (Document Level)

| Flag | Type | Effect |
|------|------|--------|
| `ignore_permissions` | bool | Bypass permission checks |
| `ignore_validate` | bool | Skip validate() method |
| `ignore_mandatory` | bool | Skip verplichte veld checks |
| `ignore_links` | bool | Skip link validatie |
| `ignore_version` | bool | Geen version record |
| `notify_update` | bool | (v15) Realtime update aan/uit |

### frappe.flags (Request Level)

| Flag | Type | Effect |
|------|------|--------|
| `in_import` | bool | Import modus actief |
| `in_install` | bool | App installatie actief |
| `in_patch` | bool | Patch execution actief |
| `in_migrate` | bool | Migratie actief |
| `in_scheduler` | bool | Background job actief |
| `mute_emails` | bool | Onderdruk email versturen |

---

## Code Voorbeelden

### Bulk Update met Flags

```python
def bulk_update_status(doc_names, new_status):
    """Update meerdere documenten zonder validatie en emails."""
    frappe.flags.mute_emails = True
    
    for name in doc_names:
        doc = frappe.get_doc("Sales Order", name)
        doc.flags.ignore_permissions = True
        doc.flags.ignore_validate = True
        doc.status = new_status
        doc.save()
    
    frappe.flags.mute_emails = False
    frappe.db.commit()
```

### Import met Volledige Bypass

```python
def import_legacy_data(records):
    """Import legacy data met alle checks uitgeschakeld."""
    frappe.flags.in_import = True
    
    for record in records:
        doc = frappe.get_doc({
            "doctype": "Customer",
            **record
        })
        doc.flags.ignore_permissions = True
        doc.flags.ignore_mandatory = True
        doc.flags.ignore_links = True
        doc.flags.ignore_validate = True
        doc.insert()
    
    frappe.flags.in_import = False
```

### Controller met Custom Flags

```python
class Project(Document):
    def validate(self):
        # Bereken progress
        self.calculate_progress()
        
        # Track of progress significant is gewijzigd
        old = self.get_doc_before_save()
        if old and abs(old.percent_complete - self.percent_complete) > 10:
            self.flags.significant_progress = True
    
    def on_update(self):
        # Notificeer alleen bij significante progress
        if self.flags.get('significant_progress'):
            self.notify_stakeholders()
        
        # Update tasks als dit niet van task komt
        if not self.flags.get('from_task'):
            self.update_task_dates()
    
    def update_task_dates(self):
        for task in frappe.get_all("Task", filters={"project": self.name}):
            task_doc = frappe.get_doc("Task", task.name)
            task_doc.flags.from_project = True  # Voorkom recursive
            task_doc.expected_end_date = self.expected_end_date
            task_doc.save()
```
