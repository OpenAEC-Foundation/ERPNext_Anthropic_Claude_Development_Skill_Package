# Error Handling Patterns - Database Operations

Complete error handling patterns for Frappe/ERPNext database operations.

---

## Pattern 1: Document CRUD with Full Error Handling

```python
import frappe
from frappe import _

class DocumentManager:
    """Reusable document manager with error handling."""
    
    @staticmethod
    def get(doctype, name, fields=None):
        """Get document with error handling."""
        if not name:
            return None
        
        if not frappe.db.exists(doctype, name):
            return None
        
        if fields:
            return frappe.db.get_value(doctype, name, fields, as_dict=True)
        
        return frappe.get_doc(doctype, name)
    
    @staticmethod
    def get_or_throw(doctype, name):
        """Get document or throw user-friendly error."""
        if not name:
            frappe.throw(_("{0} name is required").format(doctype))
        
        try:
            return frappe.get_doc(doctype, name)
        except frappe.DoesNotExistError:
            frappe.throw(
                _("{0} '{1}' not found").format(doctype, name),
                title=_("Not Found")
            )
    
    @staticmethod
    def create(doctype, data, ignore_duplicates=False):
        """Create document with duplicate handling."""
        try:
            doc = frappe.get_doc({"doctype": doctype, **data})
            doc.insert()
            return {"success": True, "name": doc.name, "doc": doc}
            
        except frappe.DuplicateEntryError:
            if ignore_duplicates:
                # Find and return existing
                existing = frappe.db.get_value(doctype, data, "name")
                if existing:
                    return {"success": True, "name": existing, "existing": True}
            frappe.throw(_("A {0} with these details already exists").format(doctype))
            
        except frappe.ValidationError as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def update(doctype, name, updates, ignore_missing=False):
        """Update document with concurrent edit handling."""
        if not frappe.db.exists(doctype, name):
            if ignore_missing:
                return {"success": False, "error": "Not found"}
            frappe.throw(_("{0} '{1}' not found").format(doctype, name))
        
        try:
            doc = frappe.get_doc(doctype, name)
            doc.update(updates)
            doc.save()
            return {"success": True, "doc": doc}
            
        except frappe.TimestampMismatchError:
            frappe.throw(
                _("This {0} was modified by another user. Please refresh and try again.").format(doctype),
                title=_("Concurrent Edit")
            )
        except frappe.ValidationError as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def delete(doctype, name, force=False, ignore_missing=False):
        """Delete document with link handling."""
        if not frappe.db.exists(doctype, name):
            if ignore_missing:
                return {"success": True, "message": "Already deleted"}
            frappe.throw(_("{0} '{1}' not found").format(doctype, name))
        
        try:
            frappe.delete_doc(doctype, name, force=force)
            return {"success": True}
            
        except frappe.LinkExistsError:
            linked = frappe.get_all(
                "DocField",
                filters={"fieldtype": "Link", "options": doctype},
                fields=["parent"]
            )
            frappe.throw(
                _("Cannot delete {0} '{1}'. It is linked to other documents.").format(doctype, name),
                title=_("Delete Error")
            )
```

---

## Pattern 2: Batch Database Operations

```python
import frappe
from frappe import _

def batch_create_documents(doctype, records, batch_size=100):
    """
    Create documents in batches with error isolation.
    Returns summary of successes and failures.
    """
    results = {
        "total": len(records),
        "created": 0,
        "failed": 0,
        "duplicates": 0,
        "errors": []
    }
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        for idx, record in enumerate(batch, i + 1):
            try:
                doc = frappe.get_doc({"doctype": doctype, **record})
                doc.insert()
                results["created"] += 1
                
            except frappe.DuplicateEntryError:
                results["duplicates"] += 1
                results["errors"].append({
                    "row": idx,
                    "error": "Duplicate entry",
                    "data": record.get("name", str(record)[:50])
                })
                
            except frappe.ValidationError as e:
                results["failed"] += 1
                results["errors"].append({
                    "row": idx,
                    "error": str(e)[:200],
                    "data": record.get("name", str(record)[:50])
                })
                
            except Exception as e:
                results["failed"] += 1
                frappe.log_error(
                    frappe.get_traceback(),
                    f"Batch create error row {idx}"
                )
                results["errors"].append({
                    "row": idx,
                    "error": "Unexpected error",
                    "data": record.get("name", str(record)[:50])
                })
        
        # Commit each batch
        frappe.db.commit()
    
    return results


def batch_update_documents(doctype, updates, batch_size=100):
    """
    Update documents in batches.
    updates = [{"name": "DOC001", "field": "value"}, ...]
    """
    results = {
        "total": len(updates),
        "updated": 0,
        "not_found": 0,
        "failed": 0,
        "errors": []
    }
    
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i + batch_size]
        
        for update in batch:
            name = update.pop("name", None)
            if not name:
                results["failed"] += 1
                continue
            
            if not frappe.db.exists(doctype, name):
                results["not_found"] += 1
                results["errors"].append({
                    "name": name,
                    "error": "Not found"
                })
                continue
            
            try:
                doc = frappe.get_doc(doctype, name)
                doc.update(update)
                doc.save()
                results["updated"] += 1
                
            except frappe.ValidationError as e:
                results["failed"] += 1
                results["errors"].append({
                    "name": name,
                    "error": str(e)[:200]
                })
            except Exception as e:
                results["failed"] += 1
                frappe.log_error(frappe.get_traceback(), f"Batch update error: {name}")
                results["errors"].append({
                    "name": name,
                    "error": "Unexpected error"
                })
        
        frappe.db.commit()
    
    return results
```

---

## Pattern 3: Safe Query Execution

```python
import frappe
from frappe import _

def execute_safe_query(query, values=None, as_dict=True):
    """
    Execute SQL query with comprehensive error handling.
    Always use parameterized queries!
    """
    try:
        result = frappe.db.sql(query, values or {}, as_dict=as_dict)
        return {"success": True, "data": result}
        
    except frappe.db.InternalError as e:
        error_msg = str(e).lower()
        
        # Deadlock detection
        if "deadlock" in error_msg:
            frappe.log_error(frappe.get_traceback(), "Query Deadlock")
            return {
                "success": False,
                "error": "Database busy. Please try again.",
                "retry": True
            }
        
        # Lock timeout
        if "lock wait timeout" in error_msg:
            frappe.log_error(frappe.get_traceback(), "Lock Timeout")
            return {
                "success": False,
                "error": "Database busy. Please try again.",
                "retry": True
            }
        
        # Connection lost
        if "lost connection" in error_msg or "gone away" in error_msg:
            frappe.log_error(frappe.get_traceback(), "Database Connection Lost")
            return {
                "success": False,
                "error": "Database connection error. Please refresh the page.",
                "retry": True
            }
        
        # Syntax error (shouldn't happen with proper queries)
        if "syntax" in error_msg:
            frappe.log_error(f"Query: {query}\nValues: {values}\n{frappe.get_traceback()}", "SQL Syntax Error")
            return {
                "success": False,
                "error": "Database query error. Please contact support."
            }
        
        # Unknown database error
        frappe.log_error(frappe.get_traceback(), "Database Error")
        return {
            "success": False,
            "error": "Database error occurred. Please try again."
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Unexpected Query Error")
        return {
            "success": False,
            "error": "An error occurred. Please try again."
        }


def execute_with_retry(query, values=None, max_retries=3, retry_delay=0.5):
    """Execute query with automatic retry on transient errors."""
    import time
    
    for attempt in range(max_retries):
        result = execute_safe_query(query, values)
        
        if result.get("success"):
            return result
        
        if not result.get("retry"):
            return result
        
        if attempt < max_retries - 1:
            time.sleep(retry_delay * (attempt + 1))
    
    return result
```

---

## Pattern 4: Query Builder with Error Handling

```python
import frappe
from frappe import _

def get_filtered_documents(doctype, filters=None, fields=None, limit=100):
    """
    Query with frappe.qb and error handling.
    """
    try:
        DocType = frappe.qb.DocType(doctype)
        
        # Build query
        query = frappe.qb.from_(DocType)
        
        # Select fields
        if fields:
            for field in fields:
                query = query.select(getattr(DocType, field))
        else:
            query = query.select(DocType.name)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if isinstance(value, list):
                    operator, operand = value[0], value[1]
                    if operator == "in":
                        query = query.where(getattr(DocType, field).isin(operand))
                    elif operator == "not in":
                        query = query.where(getattr(DocType, field).notin(operand))
                    elif operator == ">":
                        query = query.where(getattr(DocType, field) > operand)
                    elif operator == "<":
                        query = query.where(getattr(DocType, field) < operand)
                    elif operator == "like":
                        query = query.where(getattr(DocType, field).like(operand))
                else:
                    query = query.where(getattr(DocType, field) == value)
        
        # Limit
        query = query.limit(limit)
        
        return {"success": True, "data": query.run(as_dict=True)}
        
    except AttributeError as e:
        # Invalid field name
        frappe.throw(
            _("Invalid field in query: {0}").format(str(e)),
            title=_("Query Error")
        )
    except frappe.db.InternalError as e:
        frappe.log_error(frappe.get_traceback(), "Query Builder Error")
        frappe.throw(_("Database error. Please try again."))
```

---

## Pattern 5: Transaction with Savepoints

```python
import frappe
from frappe import _

def complex_multi_document_operation(data):
    """
    Complex operation with partial rollback capability.
    """
    created_docs = []
    
    try:
        # Phase 1: Create parent document
        frappe.db.savepoint("parent_created")
        
        parent = frappe.get_doc({
            "doctype": "Sales Order",
            **data.get("parent", {})
        })
        parent.insert()
        created_docs.append(("Sales Order", parent.name))
        
        # Phase 2: Create child documents
        frappe.db.savepoint("children_created")
        
        for child_data in data.get("children", []):
            try:
                child = frappe.get_doc({
                    "doctype": "Task",
                    "sales_order": parent.name,
                    **child_data
                })
                child.insert()
                created_docs.append(("Task", child.name))
            except frappe.ValidationError as e:
                # Roll back only children, keep parent
                frappe.db.rollback(save_point="children_created")
                frappe.log_error(str(e), "Child creation failed")
                return {
                    "success": True,
                    "partial": True,
                    "parent": parent.name,
                    "message": "Parent created, but some children failed"
                }
        
        # Phase 3: Update external systems
        frappe.db.savepoint("external_sync")
        
        try:
            sync_to_external(parent)
        except Exception:
            # External sync failed - log but don't rollback
            frappe.db.rollback(save_point="external_sync")
            frappe.log_error(frappe.get_traceback(), "External sync failed")
        
        return {
            "success": True,
            "parent": parent.name,
            "children": [d[1] for d in created_docs if d[0] == "Task"]
        }
        
    except frappe.DuplicateEntryError:
        frappe.throw(_("A document with these details already exists"))
        
    except frappe.ValidationError as e:
        frappe.throw(str(e))
        
    except Exception as e:
        # Full rollback
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Complex operation failed")
        frappe.throw(_("Operation failed. Please try again."))


def sync_to_external(doc):
    """Sync to external system."""
    pass
```

---

## Pattern 6: Existence Check Patterns

```python
import frappe
from frappe import _

def check_existence_patterns():
    """Various existence check patterns."""
    
    # Simple existence check
    if frappe.db.exists("Customer", "CUST-001"):
        # Customer exists
        pass
    
    # Check with filters
    if frappe.db.exists("Sales Invoice", {"customer": "CUST-001", "docstatus": 1}):
        # Submitted invoice exists for customer
        pass
    
    # Get value if exists (returns None if not found)
    status = frappe.db.get_value("Task", "TASK-001", "status")
    if status:
        # Task exists and has status
        pass
    
    # Batch existence check (efficient)
    names = ["CUST-001", "CUST-002", "CUST-003"]
    existing = frappe.get_all(
        "Customer",
        filters={"name": ["in", names]},
        pluck="name"
    )
    missing = set(names) - set(existing)
    
    # Check and get in one call
    customer_data = frappe.db.get_value(
        "Customer", "CUST-001",
        ["customer_name", "credit_limit", "disabled"],
        as_dict=True
    )
    if customer_data:
        # Customer exists, use data
        if customer_data.disabled:
            frappe.throw(_("Customer is disabled"))
    else:
        frappe.throw(_("Customer not found"))


def safe_get_or_create(doctype, filters, defaults=None):
    """Get existing document or create new one."""
    # Check if exists
    existing = frappe.db.get_value(doctype, filters, "name")
    
    if existing:
        return frappe.get_doc(doctype, existing)
    
    # Create new
    doc_data = {"doctype": doctype}
    doc_data.update(filters)
    if defaults:
        doc_data.update(defaults)
    
    try:
        doc = frappe.get_doc(doc_data)
        doc.insert()
        return doc
    except frappe.DuplicateEntryError:
        # Race condition - someone else created it
        existing = frappe.db.get_value(doctype, filters, "name")
        return frappe.get_doc(doctype, existing)
```

---

## Pattern 7: Connection Error Recovery

```python
import frappe
from frappe import _
import time

def with_connection_retry(func):
    """Decorator to retry on connection errors."""
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except frappe.db.InternalError as e:
                error_msg = str(e).lower()
                
                is_connection_error = any(x in error_msg for x in [
                    "lost connection",
                    "gone away",
                    "can't connect",
                    "connection refused"
                ])
                
                if not is_connection_error:
                    raise
                
                if attempt < max_retries - 1:
                    frappe.log_error(
                        f"Connection error, attempt {attempt + 1}/{max_retries}",
                        "Database Connection Retry"
                    )
                    time.sleep(retry_delay * (attempt + 1))
                    # Reconnect
                    frappe.db.connect()
                else:
                    frappe.log_error(frappe.get_traceback(), "Database Connection Failed")
                    frappe.throw(_("Database connection error. Please try again later."))
        
    return wrapper


@with_connection_retry
def reliable_database_operation():
    """Operation with automatic connection retry."""
    return frappe.get_all("Sales Invoice", limit=10)
```

---

## Quick Reference: Database Error Patterns

| Error | Check | Handle |
|-------|-------|--------|
| Document not found | `frappe.db.exists()` | Throw user-friendly message |
| Duplicate entry | Catch `DuplicateEntryError` | Return existing or inform user |
| Linked documents | Catch `LinkExistsError` | Show linked docs to user |
| Concurrent edit | Catch `TimestampMismatchError` | Ask user to refresh |
| Database error | Catch `InternalError` | Log and show generic message |
| Query timeout | Catch `QueryTimeoutError` | Optimize query or paginate |
