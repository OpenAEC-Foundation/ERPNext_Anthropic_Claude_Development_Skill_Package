# REST API Reference

## Base URL

```
https://{your-instance}/api/resource/{doctype}
```

## Standard Headers

**ALWAYS** include for JSON responses:

```python
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'token api_key:api_secret'
}
```

---

## List Documents (GET)

```
GET /api/resource/{doctype}
```

### Default Behavior
- Returns 20 records
- Only `name` field

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `fields` | JSON array | Fields to retrieve |
| `filters` | JSON array | Filter conditions |
| `or_filters` | JSON array | OR filter conditions |
| `order_by` | string | Sorting (e.g., "modified desc") |
| `limit_start` | int | Offset for pagination |
| `limit_page_length` | int | Number of results |
| `limit` | int | Alias for limit_page_length (v15+) |
| `as_dict` | bool | Response as dict (default) |
| `debug` | bool | Show SQL query |
| `expand_links` | bool | Expand linked documents (v15+) |

### Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equal to | `["status", "=", "Open"]` |
| `!=` | Not equal | `["status", "!=", "Cancelled"]` |
| `>` | Greater than | `["amount", ">", 1000]` |
| `<` | Less than | `["amount", "<", 500]` |
| `>=` | Greater or equal | `["date", ">=", "2024-01-01"]` |
| `<=` | Less or equal | `["date", "<=", "2024-12-31"]` |
| `like` | SQL LIKE | `["name", "like", "%INV%"]` |
| `not like` | SQL NOT LIKE | `["name", "not like", "%TEST%"]` |
| `in` | In list | `["status", "in", ["Open", "Pending"]]` |
| `not in` | Not in list | `["status", "not in", ["Cancelled"]]` |
| `is` | NULL check | `["ref", "is", "set"]` or `["ref", "is", "not set"]` |
| `between` | Between values | `["amount", "between", [100, 500]]` |

### Example: Filtered List

```bash
GET /api/resource/Sales Invoice
    ?fields=["name","customer","grand_total","status"]
    &filters=[["status","=","Paid"],["grand_total",">",1000]]
    &order_by=posting_date desc
    &limit_page_length=50
```

**Response:**
```json
{
    "data": [
        {
            "name": "SINV-00001",
            "customer": "Customer A",
            "grand_total": 1500.00,
            "status": "Paid"
        }
    ]
}
```

### Python Example

```python
import requests
import json

params = {
    'fields': json.dumps(["name", "customer", "grand_total"]),
    'filters': json.dumps([["status", "=", "Paid"]]),
    'limit_page_length': 100,
    'order_by': 'modified desc'
}

response = requests.get(
    'https://erp.example.com/api/resource/Sales Invoice',
    params=params,
    headers=headers
)
data = response.json()['data']
```

---

## Read Document (GET)

```
GET /api/resource/{doctype}/{name}
```

```bash
GET /api/resource/Customer/CUST-00001
```

**Response:**
```json
{
    "data": {
        "name": "CUST-00001",
        "customer_name": "Test Customer",
        "customer_group": "Commercial",
        "items": [...]  // Child table data included
    }
}
```

---

## Create Document (POST)

```
POST /api/resource/{doctype}
```

**Body:** JSON object with fields

```python
data = {
    "customer_name": "New Customer",
    "customer_type": "Company",
    "customer_group": "Commercial"
}

response = requests.post(
    'https://erp.example.com/api/resource/Customer',
    json=data,
    headers=headers
)
```

**Response:**
```json
{
    "data": {
        "name": "New Customer",
        "owner": "Administrator",
        "creation": "2024-01-15 10:30:00",
        "customer_name": "New Customer"
    }
}
```

### Create with Child Table

```python
data = {
    "customer": "CUST-00001",
    "items": [
        {
            "item_code": "ITEM-001",
            "qty": 5,
            "rate": 100
        },
        {
            "item_code": "ITEM-002",
            "qty": 2,
            "rate": 250
        }
    ]
}

response = requests.post(
    'https://erp.example.com/api/resource/Sales Order',
    json=data,
    headers=headers
)
```

---

## Update Document (PUT)

```
PUT /api/resource/{doctype}/{name}
```

**Body:** Only fields that need to be changed

```python
data = {"customer_group": "Premium"}

response = requests.put(
    'https://erp.example.com/api/resource/Customer/CUST-00001',
    json=data,
    headers=headers
)
```

### Update Child Table Items

```python
# Replace entire child table
data = {
    "items": [
        {"item_code": "ITEM-001", "qty": 10}  # All other items are removed
    ]
}

# Update specific child item (via name)
data = {
    "items": [
        {"name": "abc123", "qty": 10}  # Update existing item
    ]
}
```

---

## Delete Document (DELETE)

```
DELETE /api/resource/{doctype}/{name}
```

```bash
DELETE /api/resource/Customer/CUST-00001
```

**Response:**
```json
{"message": "ok"}
```

---

## Pagination Pattern

```python
def get_all_records(doctype, filters=None, page_size=100):
    """Retrieve all records with pagination."""
    all_data = []
    offset = 0
    
    while True:
        params = {
            'filters': json.dumps(filters or []),
            'limit_start': offset,
            'limit_page_length': page_size
        }
        
        response = requests.get(
            f'https://erp.example.com/api/resource/{doctype}',
            params=params,
            headers=headers
        )
        
        data = response.json().get('data', [])
        if not data:
            break
            
        all_data.extend(data)
        offset += page_size
    
    return all_data
```

---

## Expand Links (v15+)

Automatically retrieve related documents.

```bash
# Single document
GET /api/resource/Sales Invoice/SINV-00001?expand_links=True

# Listing with specific links
GET /api/resource/Sales Invoice?expand=["customer"]
```

---

## File Upload

```bash
POST /api/method/upload_file
Content-Type: multipart/form-data
```

```python
files = {
    'file': ('document.pdf', open('/path/to/doc.pdf', 'rb'), 'application/pdf')
}
data = {
    'doctype': 'Customer',
    'docname': 'CUST-00001',
    'is_private': 1
}

response = requests.post(
    'https://erp.example.com/api/method/upload_file',
    files=files,
    data=data,
    headers={'Authorization': 'token api_key:api_secret'}
)
```

**Response:**
```json
{
    "message": {
        "name": "file_hash.pdf",
        "file_url": "/private/files/file_hash.pdf",
        "is_private": 1
    }
}
```
