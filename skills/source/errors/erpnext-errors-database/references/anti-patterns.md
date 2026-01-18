# Anti-Patterns - Database Error Handling

Common mistakes to avoid when handling database errors in Frappe/ERPNext.

---

## 1. SQL Injection via String Formatting

### ❌ WRONG

```python
# CRITICAL SECURITY VULNERABILITY!
def get_customer(customer_name):
    query = f"SELECT * FROM `tabCustomer` WHERE name = '{customer_name}'"
    return frappe.db.sql(query)

# Also wrong with .format()
query = "SELECT * FROM `tabCustomer` WHERE name = '{}'".format(customer_name)
```

### ✅ CORRECT

```python
def get_customer(customer_name):
    # Parameterized query
    return frappe.db.sql(
        "SELECT * FROM `tabCustomer` WHERE name = %(name)s",
        {"name": customer_name},
        as_dict=True
    )

# Or use the ORM
customer = frappe.db.get_value("Customer", customer_name, "*", as_dict=True)
```

**Why**: String formatting allows SQL injection attacks. Always use parameterized queries.

---

## 2. Not Checking Existence Before get_doc

### ❌ WRONG

```python
def update_customer(customer_name, data):
    # Crashes with DoesNotExistError if customer doesn't exist!
    doc = frappe.get_doc("Customer", customer_name)
    doc.update(data)
    doc.save()
```

### ✅ CORRECT

```python
def update_customer(customer_name, data):
    if not frappe.db.exists("Customer", customer_name):
        frappe.throw(_("Customer '{0}' not found").format(customer_name))
    
    doc = frappe.get_doc("Customer", customer_name)
    doc.update(data)
    doc.save()
```

**Why**: get_doc throws DoesNotExistError. Check first or catch the exception.

---

## 3. Ignoring DuplicateEntryError on Insert

### ❌ WRONG

```python
def create_customer(data):
    # Crashes on duplicate!
    doc = frappe.get_doc({"doctype": "Customer", **data})
    doc.insert()
    return doc.name
```

### ✅ CORRECT

```python
def create_customer(data):
    try:
        doc = frappe.get_doc({"doctype": "Customer", **data})
        doc.insert()
        return {"success": True, "name": doc.name}
    except frappe.DuplicateEntryError:
        existing = frappe.db.get_value("Customer", {"customer_name": data.get("customer_name")})
        return {"success": True, "name": existing, "existing": True}
```

**Why**: Unique constraints cause DuplicateEntryError. Handle gracefully.

---

## 4. Assuming db.set_value Always Works

### ❌ WRONG

```python
def mark_as_synced(customer_name):
    # Silently does nothing if customer doesn't exist!
    frappe.db.set_value("Customer", customer_name, "synced", 1)
    return "Success"  # Lies!
```

### ✅ CORRECT

```python
def mark_as_synced(customer_name):
    if not frappe.db.exists("Customer", customer_name):
        frappe.throw(_("Customer '{0}' not found").format(customer_name))
    
    frappe.db.set_value("Customer", customer_name, "synced", 1)
    return "Success"
```

**Why**: db.set_value doesn't raise error if record doesn't exist. Verify first.

---

## 5. Committing in Controller Hooks

### ❌ WRONG

```python
class SalesOrder(Document):
    def validate(self):
        self.calculate_totals()
        frappe.db.commit()  # BREAKS TRANSACTION!
    
    def on_update(self):
        self.update_linked()
        frappe.db.commit()  # DON'T DO THIS!
```

### ✅ CORRECT

```python
class SalesOrder(Document):
    def validate(self):
        self.calculate_totals()
        # No commit - framework handles it
    
    def on_update(self):
        self.update_linked()
        # No commit - framework handles it
```

**Why**: Manual commits in controllers break transaction management and can cause partial saves.

---

## 6. Missing Commit in Background Jobs

### ❌ WRONG

```python
def background_sync():
    for item in frappe.get_all("Item", limit=100):
        frappe.db.set_value("Item", item.name, "synced", 1)
    
    # Missing commit - ALL CHANGES LOST!
```

### ✅ CORRECT

```python
def background_sync():
    for item in frappe.get_all("Item", limit=100):
        frappe.db.set_value("Item", item.name, "synced", 1)
    
    frappe.db.commit()  # REQUIRED!
```

**Why**: Background jobs don't auto-commit. Always commit explicitly.

---

## 7. Swallowing Database Errors

### ❌ WRONG

```python
def update_customer(name, data):
    try:
        doc = frappe.get_doc("Customer", name)
        doc.update(data)
        doc.save()
    except Exception:
        pass  # Silent failure - impossible to debug!
```

### ✅ CORRECT

```python
def update_customer(name, data):
    try:
        doc = frappe.get_doc("Customer", name)
        doc.update(data)
        doc.save()
    except frappe.DoesNotExistError:
        frappe.throw(_("Customer not found"))
    except frappe.ValidationError as e:
        frappe.throw(str(e))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Customer Update Error")
        frappe.throw(_("An error occurred. Please try again."))
```

**Why**: Silent failures make debugging impossible. Always log or re-raise.

---

## 8. Not Handling Empty Query Results

### ❌ WRONG

```python
def get_latest_invoice(customer):
    result = frappe.db.sql("""
        SELECT name FROM `tabSales Invoice`
        WHERE customer = %s
        ORDER BY posting_date DESC
        LIMIT 1
    """, customer)
    
    return result[0][0]  # IndexError if no results!
```

### ✅ CORRECT

```python
def get_latest_invoice(customer):
    result = frappe.db.sql("""
        SELECT name FROM `tabSales Invoice`
        WHERE customer = %s
        ORDER BY posting_date DESC
        LIMIT 1
    """, customer)
    
    return result[0][0] if result else None
```

**Why**: Empty result sets cause IndexError. Always check before accessing.

---

## 9. N+1 Query Pattern

### ❌ WRONG

```python
def get_customer_details(customer_names):
    details = []
    for name in customer_names:
        # N queries for N customers!
        doc = frappe.get_doc("Customer", name)
        details.append(doc.as_dict())
    return details
```

### ✅ CORRECT

```python
def get_customer_details(customer_names):
    # Single query for all customers
    return frappe.get_all(
        "Customer",
        filters={"name": ["in", customer_names]},
        fields=["name", "customer_name", "credit_limit", "territory"]
    )
```

**Why**: N+1 queries are extremely slow. Batch fetch instead.

---

## 10. No Limit on Queries

### ❌ WRONG

```python
def get_all_invoices():
    # Could return millions of rows!
    return frappe.get_all("Sales Invoice")
```

### ✅ CORRECT

```python
def get_all_invoices(page=1, page_size=100):
    return frappe.get_all(
        "Sales Invoice",
        limit_start=(page - 1) * page_size,
        limit_page_length=page_size
    )
```

**Why**: Unbounded queries can crash the system. Always paginate.

---

## 11. Catching Generic Exception for Specific Errors

### ❌ WRONG

```python
def delete_customer(name):
    try:
        frappe.delete_doc("Customer", name)
    except Exception as e:
        # Catches everything - hard to handle appropriately
        frappe.throw(str(e))
```

### ✅ CORRECT

```python
def delete_customer(name):
    try:
        frappe.delete_doc("Customer", name)
    except frappe.DoesNotExistError:
        frappe.throw(_("Customer not found"))
    except frappe.LinkExistsError:
        frappe.throw(_("Cannot delete - linked documents exist"))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Delete Error")
        frappe.throw(_("Delete failed. Please contact support."))
```

**Why**: Specific exceptions allow specific handling and better error messages.

---

## 12. Exposing Database Errors to Users

### ❌ WRONG

```python
def run_report(filters):
    try:
        return frappe.db.sql(query, filters)
    except Exception as e:
        frappe.throw(str(e))  # Exposes SQL error details!
```

### ✅ CORRECT

```python
def run_report(filters):
    try:
        return frappe.db.sql(query, filters)
    except frappe.db.InternalError as e:
        frappe.log_error(frappe.get_traceback(), "Report Query Error")
        frappe.throw(_("Error generating report. Please try again."))
```

**Why**: Database error messages can expose sensitive information.

---

## 13. Race Condition on Get-or-Create

### ❌ WRONG

```python
def get_or_create_customer(name):
    if not frappe.db.exists("Customer", name):
        # Race condition! Another process might create it here
        doc = frappe.get_doc({"doctype": "Customer", "customer_name": name})
        doc.insert()  # DuplicateEntryError!
        return doc
    return frappe.get_doc("Customer", name)
```

### ✅ CORRECT

```python
def get_or_create_customer(name):
    if not frappe.db.exists("Customer", name):
        try:
            doc = frappe.get_doc({"doctype": "Customer", "customer_name": name})
            doc.insert()
            return doc
        except frappe.DuplicateEntryError:
            # Race condition - someone else created it
            pass
    
    return frappe.get_doc("Customer", name)
```

**Why**: Between exists() check and insert(), another process might create the record.

---

## 14. Not Handling Concurrent Edits

### ❌ WRONG

```python
def update_customer(name, data):
    doc = frappe.get_doc("Customer", name)
    doc.update(data)
    doc.save()  # TimestampMismatchError if modified by another user!
```

### ✅ CORRECT

```python
def update_customer(name, data):
    try:
        doc = frappe.get_doc("Customer", name)
        doc.update(data)
        doc.save()
    except frappe.TimestampMismatchError:
        frappe.throw(
            _("This document was modified by another user. Please refresh and try again.")
        )
```

**Why**: Concurrent edits cause TimestampMismatchError. Handle gracefully.

---

## 15. Using get_doc When get_value Suffices

### ❌ WRONG

```python
def get_customer_credit_limit(name):
    # Loads entire document just for one field!
    doc = frappe.get_doc("Customer", name)
    return doc.credit_limit
```

### ✅ CORRECT

```python
def get_customer_credit_limit(name):
    # Only fetches the needed field
    return frappe.db.get_value("Customer", name, "credit_limit") or 0
```

**Why**: get_doc loads entire document. Use get_value for single fields.

---

## Quick Checklist: Database Code Review

Before deploying:

- [ ] All SQL queries use parameterized values (no string formatting)
- [ ] Existence checked before get_doc (or exception caught)
- [ ] DuplicateEntryError handled on insert
- [ ] db.set_value preceded by existence check
- [ ] No frappe.db.commit() in controller hooks
- [ ] frappe.db.commit() in background jobs
- [ ] Database errors logged, not swallowed
- [ ] Empty results handled (no blind array access)
- [ ] Queries have limits (pagination)
- [ ] Specific exceptions caught before generic Exception
- [ ] Database errors not exposed to users
- [ ] Race conditions handled on get-or-create
- [ ] TimestampMismatchError handled for saves
- [ ] get_value used instead of get_doc for single fields
