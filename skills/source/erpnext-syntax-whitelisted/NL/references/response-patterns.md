# Response Patterns Reference

Hoe responses gestructureerd worden in whitelisted methods.

## Return Value (Aanbevolen)

De eenvoudigste aanpak - return value wordt automatisch JSON:

```python
@frappe.whitelist()
def get_summary(customer):
    """Return value wordt automatisch gewrapt in {"message": ...}"""
    return {
        "customer": customer,
        "total_orders": 5,
        "total_value": 15000
    }
```

**Response**:
```json
{
    "message": {
        "customer": "Customer ABC",
        "total_orders": 5,
        "total_value": 15000
    }
}
```

### Verschillende Return Types

```python
# Dict retourneren
@frappe.whitelist()
def return_dict():
    return {"key": "value"}
# â†’ {"message": {"key": "value"}}

# List retourneren
@frappe.whitelist()
def return_list():
    return [1, 2, 3]
# â†’ {"message": [1, 2, 3]}

# String retourneren
@frappe.whitelist()
def return_string():
    return "Hello"
# â†’ {"message": "Hello"}

# None retourneren (of geen return)
@frappe.whitelist()
def return_none():
    pass
# â†’ {"message": null}
```

## frappe.response Object

Voor meer controle over de response:

```python
@frappe.whitelist()
def custom_response(param):
    """Direct response manipulatie."""
    # Standaard message zetten
    frappe.response["message"] = {"data": "value"}
    
    # Extra velden toevoegen (buiten message)
    frappe.response["count"] = 10
    frappe.response["status"] = "success"
    
    # Geen return nodig
```

**Response**:
```json
{
    "message": {"data": "value"},
    "count": 10,
    "status": "success"
}
```

### Combinatie Return en frappe.response

```python
@frappe.whitelist()
def mixed_response():
    """Return overschrijft frappe.response["message"]."""
    frappe.response["extra_info"] = "additional"
    return {"main": "data"}
```

**Response**:
```json
{
    "message": {"main": "data"},
    "extra_info": "additional"
}
```

## Response Types

| Type | Gebruik | Instelling |
|------|---------|------------|
| `json` (default) | API responses | Automatisch |
| `download` | File downloads | `frappe.response.type = "download"` |
| `csv` | CSV export | `frappe.response.type = "csv"` |
| `pdf` | PDF download | `frappe.response.type = "pdf"` |
| `redirect` | HTTP redirect | `frappe.response.type = "redirect"` |
| `binary` | Binary data | `frappe.response.type = "binary"` |

### File Download

```python
@frappe.whitelist()
def download_file(name):
    """Download een bestand."""
    file = frappe.get_doc("File", name)
    
    frappe.response.filename = file.file_name
    frappe.response.filecontent = file.get_content()
    frappe.response.type = "download"
    frappe.response.display_content_as = "attachment"
```

### Inline Display (PDF/Image)

```python
@frappe.whitelist()
def view_pdf(name):
    """Toon PDF in browser."""
    content = generate_pdf(name)
    
    frappe.response.filename = f"{name}.pdf"
    frappe.response.filecontent = content
    frappe.response.type = "download"
    frappe.response.display_content_as = "inline"  # Toont in browser
```

### CSV Export

```python
@frappe.whitelist()
def export_csv(doctype, filters=None):
    """Export data als CSV."""
    import csv
    from io import StringIO
    
    data = frappe.get_all(doctype, filters=frappe.parse_json(filters) if filters else {})
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    writer.writerows(data)
    
    frappe.response.filename = f"{doctype}_export.csv"
    frappe.response.filecontent = output.getvalue()
    frappe.response.type = "download"
```

### HTTP Redirect

```python
@frappe.whitelist()
def redirect_to_doc(doctype, name):
    """Redirect naar document."""
    frappe.response.type = "redirect"
    frappe.response.location = f"/app/{frappe.scrub(doctype)}/{name}"
```

## HTTP Status Codes

### Custom Status Code Zetten

```python
@frappe.whitelist()
def custom_status(param):
    """Custom HTTP status code."""
    if not param:
        frappe.local.response["http_status_code"] = 400
        return {"error": "Parameter required"}
    
    # Success (default 200)
    return {"success": True}
```

### Veelgebruikte Status Codes

```python
# 400 Bad Request
frappe.local.response["http_status_code"] = 400
return {"error": "Invalid input"}

# 404 Not Found
frappe.local.response["http_status_code"] = 404
return {"error": "Resource not found"}

# 403 Forbidden
frappe.local.response["http_status_code"] = 403
return {"error": "Access denied"}

# 429 Too Many Requests
frappe.local.response["http_status_code"] = 429
return {"error": "Rate limit exceeded"}

# 201 Created
frappe.local.response["http_status_code"] = 201
return {"name": "NEW-0001", "created": True}
```

## Response Structuur bij Errors

### Success Response

```json
{
    "message": {
        "data": "value"
    }
}
```

### Error Response (na frappe.throw)

```json
{
    "exc_type": "ValidationError",
    "exc": "[Traceback string...]",
    "_server_messages": "[{\"message\": \"Error message\"}]"
}
```

### Handmatige Error Response

```python
@frappe.whitelist()
def api_with_error_handling(param):
    """Consistente error response structuur."""
    try:
        result = process(param)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        frappe.local.response["http_status_code"] = 400
        return {
            "success": False,
            "error": str(e)
        }
```

## Paginated Response

```python
@frappe.whitelist()
def get_paginated_data(page=1, page_size=20):
    """Paginated response met metadata."""
    page = int(page)
    page_size = int(page_size)
    
    start = (page - 1) * page_size
    
    data = frappe.get_all(
        "Sales Order",
        limit_start=start,
        limit_page_length=page_size
    )
    
    total = frappe.db.count("Sales Order")
    
    return {
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": (total + page_size - 1) // page_size
        }
    }
```

## Response Headers

```python
@frappe.whitelist()
def custom_headers():
    """Custom response headers toevoegen."""
    # Via frappe.local.response
    frappe.local.response.headers["X-Custom-Header"] = "value"
    frappe.local.response.headers["Cache-Control"] = "no-cache"
    
    return {"data": "value"}
```

## Best Practices

1. **Consistente structuur** - Gebruik altijd dezelfde response structuur
2. **Success indicator** - Voeg een `success` boolean toe bij complexe APIs
3. **Metadata** - Voeg pagination/count info toe bij lijsten
4. **Geen sensitive data** - Log errors server-side, geef generieke messages
5. **HTTP codes** - Gebruik juiste status codes voor de situatie
