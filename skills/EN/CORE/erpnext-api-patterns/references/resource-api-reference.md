# Resource API Reference

> REST CRUD operations for all DocTypes.

---

## 1. Endpoint Structuur

```
/api/resource/:doctype              # List, Create
/api/resource/:doctype/:name        # Read, Update, Delete
```

---

## 2. Verplichte Headers

```json
{
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "token api_key:api_secret"
}
```

---

## 3. List Documents (GET)

### Basis

```
GET /api/resource/Customer
```

**Response:**
```json
{
    "data": [
        {"name": "CUST-00001"},
        {"name": "CUST-00002"}
    ]
}
```

### Parameters

| Parameter | Type | Beschrijving | Voorbeeld |
|-----------|------|--------------|-----------|
| `fields` | JSON array | Velden om op te halen | `["name","status"]` |
| `filters` | JSON array | Filter condities | `[["status","=","Open"]]` |
| `or_filters` | JSON array | OR condities | `[["status","=","Open"],["status","=","Draft"]]` |
| `order_by` | string | Sortering | `"modified desc"` |
| `limit_start` | int | Offset | `0` |
| `limit_page_length` | int | Aantal records | `20` |
| `limit` | int | Alias voor limit_page_length | `20` |
| `as_dict` | boolean | Response format | `true` |
| `debug` | boolean | Toon SQL query | `false` |
| `expand` | JSON array | Expand link fields (v15+) | `["customer"]` |

### Fields Parameter

```
GET /api/resource/Sales Order?fields=["name","customer","grand_total","status"]
```

**Response:**
```json
{
    "data": [
        {
            "name": "SO-00001",
            "customer": "CUST-00001",
            "grand_total": 15000.00,
            "status": "Draft"
        }
    ]
}
```

### Filters

**Syntax:**
```
filters=[[<field>, <operator>, <value>], ...]
```

**Operators:**

| Operator | Gebruik | Voorbeeld |
|----------|---------|-----------|
| `=` | Gelijk | `["status","=","Open"]` |
| `!=` | Niet gelijk | `["status","!=","Cancelled"]` |
| `<` | Kleiner | `["grand_total","<","1000"]` |
| `>` | Groter | `["grand_total",">","1000"]` |
| `<=` | Kleiner of gelijk | `["qty","<=","100"]` |
| `>=` | Groter of gelijk | `["qty",">=","10"]` |
| `like` | Pattern match | `["customer_name","like","%Corp%"]` |
| `not like` | Inverse pattern | `["name","not like","TEST%"]` |
| `in` | In lijst | `["status","in",["Draft","Open"]]` |
| `not in` | Niet in lijst | `["status","not in",["Cancelled"]]` |
| `is` | NULL check | `["reference","is","not set"]` |
| `between` | Range | `["date","between",["2024-01-01","2024-12-31"]]` |

**Complexe filter:**
```
GET /api/resource/Sales Order?filters=[
    ["status","in",["Draft","To Deliver and Bill"]],
    ["grand_total",">","5000"],
    ["transaction_date",">=","2024-01-01"]
]&fields=["name","customer","grand_total","status"]
```

### OR Filters

```
GET /api/resource/Customer?or_filters=[
    ["customer_group","=","Commercial"],
    ["customer_group","=","Individual"]
]
```

### Paginatie

```
# Pagina 1 (eerste 20)
GET /api/resource/Customer?limit_start=0&limit_page_length=20

# Pagina 2 (21-40)
GET /api/resource/Customer?limit_start=20&limit_page_length=20

# Pagina 3 (41-60)
GET /api/resource/Customer?limit_start=40&limit_page_length=20
```

### Sortering

```
# Nieuwste eerst
GET /api/resource/Customer?order_by=creation desc

# Alfabetisch
GET /api/resource/Customer?order_by=customer_name asc

# Meerdere velden
GET /api/resource/Customer?order_by=customer_group asc, customer_name asc
```

### Link Expansion (v15+)

```
GET /api/resource/Sales Order?expand=["customer"]
```

**Response:**
```json
{
    "data": [
        {
            "name": "SO-00001",
            "customer": {
                "name": "CUST-00001",
                "customer_name": "Example Corp",
                "customer_group": "Commercial"
            }
        }
    ]
}
```

---

## 4. Create Document (POST)

```bash
POST /api/resource/Customer
Content-Type: application/json

{
    "customer_name": "Nieuwe Klant BV",
    "customer_type": "Company",
    "customer_group": "Commercial",
    "territory": "Netherlands"
}
```

**Response:**
```json
{
    "data": {
        "name": "Nieuwe Klant BV",
        "owner": "Administrator",
        "creation": "2024-01-15 10:30:00",
        "modified": "2024-01-15 10:30:00",
        "docstatus": 0,
        "customer_name": "Nieuwe Klant BV",
        "customer_type": "Company",
        "customer_group": "Commercial",
        "territory": "Netherlands",
        "doctype": "Customer"
    }
}
```

### Met Child Table

```bash
POST /api/resource/Sales Order
{
    "customer": "CUST-00001",
    "delivery_date": "2024-02-01",
    "items": [
        {
            "item_code": "ITEM-001",
            "qty": 10,
            "rate": 100
        },
        {
            "item_code": "ITEM-002",
            "qty": 5,
            "rate": 200
        }
    ]
}
```

---

## 5. Read Document (GET)

```
GET /api/resource/Customer/CUST-00001
```

**Response:**
```json
{
    "data": {
        "name": "CUST-00001",
        "customer_name": "Example Corp",
        "customer_type": "Company",
        "customer_group": "Commercial",
        "territory": "All Territories",
        "creation": "2024-01-10 09:00:00",
        "modified": "2024-01-15 14:30:00",
        "docstatus": 0,
        "doctype": "Customer"
    }
}
```

### Met Link Expansion

```
GET /api/resource/Sales Order/SO-00001?expand_links=True
```

---

## 6. Update Document (PUT)

```bash
PUT /api/resource/Customer/CUST-00001
Content-Type: application/json

{
    "customer_name": "Example Corporation",
    "territory": "Europe"
}
```

**Response:** Volledige document met updates.

### Partial Update

Alleen gespecificeerde velden worden gewijzigd:
```bash
PUT /api/resource/Sales Order/SO-00001
{
    "status": "On Hold"
}
```

### Child Table Update

```bash
PUT /api/resource/Sales Order/SO-00001
{
    "items": [
        {
            "name": "bestaande_row_name",
            "qty": 15
        },
        {
            "item_code": "ITEM-NEW",
            "qty": 3,
            "rate": 50
        }
    ]
}
```

---

## 7. Delete Document (DELETE)

```bash
DELETE /api/resource/Customer/CUST-00001
```

**Response:**
```json
{
    "message": "ok"
}
```

---

## 8. Speciale Response Velden

| Veld | Beschrijving |
|------|--------------|
| `name` | Document identifier |
| `doctype` | Document type |
| `docstatus` | 0=Draft, 1=Submitted, 2=Cancelled |
| `owner` | Aangemaakt door |
| `creation` | Aanmaakdatum |
| `modified` | Laatst gewijzigd |
| `modified_by` | Gewijzigd door |

---

## 9. Debug Mode

```
GET /api/resource/Customer?debug=True&limit=5
```

**Response bevat:**
```json
{
    "data": [...],
    "exc": "[\"SELECT ... LIMIT 5\", \"Execution time: 0.002 sec\"]"
}
```
