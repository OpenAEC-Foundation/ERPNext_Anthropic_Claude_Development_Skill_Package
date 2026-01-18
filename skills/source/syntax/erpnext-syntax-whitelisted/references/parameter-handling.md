# Parameter Handling Reference

Hoe request parameters worden verwerkt in whitelisted methods.

## Parameter Toegang

### Via Function Arguments (Aanbevolen)

```python
@frappe.whitelist()
def process_order(customer, items=None, include_tax=False):
    """
    Parameters worden automatisch doorgegeven als arguments.
    - customer: verplicht
    - items: optioneel, default None
    - include_tax: optioneel, default False
    """
    return {
        "customer": customer,
        "item_count": len(items or []),
        "include_tax": include_tax
    }
```

### Via frappe.form_dict

```python
@frappe.whitelist()
def process_data():
    """Direct toegang tot alle request parameters."""
    # Als dict
    all_params = frappe.form_dict
    
    # Specifieke waarde ophalen
    customer = frappe.form_dict.get('customer')
    items = frappe.form_dict.get('items', [])
    
    # Of via frappe.local
    customer = frappe.local.form_dict.get('customer')
    
    return {"customer": customer}
```

**Wanneer `frappe.form_dict` gebruiken:**
- Dynamische parameters (onbekend tijdens development)
- Alle parameters loggen
- Parameters doorsturen naar andere functies

## Type Conversion

Frappe converteert automatisch string parameters:

| Client Input | Python Type | Voorwaarde |
|-------------|-------------|------------|
| `"123"` | `int` | Als parameter type hint is int |
| `"true"`, `"1"` | `True` | Boolean conversie |
| `"false"`, `"0"` | `False` | Boolean conversie |
| `"[1, 2, 3]"` | `list` | JSON array |
| `"{\"key\": \"value\"}"` | `dict` | JSON object |

### Automatische Conversie

```python
@frappe.whitelist()
def calculate(amount, quantity, enabled):
    """
    JavaScript:
    frappe.call({
        method: '...',
        args: {
            amount: "100.50",    # wordt float/string
            quantity: "5",       # wordt string
            enabled: "true"     # wordt string "true"
        }
    })
    """
    # Type conversie vaak nog nodig
    amount = float(amount)
    quantity = int(quantity)
    enabled = enabled in ("true", "1", True)
    
    return amount * quantity if enabled else 0
```

## JSON Data Parsing

### Expliciet Parsen (Aanbevolen)

```python
@frappe.whitelist(methods=["POST"])
def create_items(data):
    """Data kan als JSON string binnenkomen."""
    # Veilig parsen
    if isinstance(data, str):
        data = frappe.parse_json(data)
    
    # Nu is data een dict/list
    for item in data.get('items', []):
        process_item(item)
    
    return {"processed": True}
```

### Alternatief met json.loads

```python
import json

@frappe.whitelist(methods=["POST"])
def process_json(payload):
    """Alternatieve JSON parsing."""
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            frappe.throw(_("Invalid JSON"))
    
    return payload
```

## Type Annotations (v15+)

Frappe v15 valideert type annotations automatisch:

```python
@frappe.whitelist()
def get_orders(customer: str, limit: int = 10, include_draft: bool = False) -> dict:
    """
    Type annotations worden gevalideerd bij request.
    
    - customer moet een string zijn
    - limit moet een integer zijn (of converteerbaar)
    - include_draft moet een boolean zijn
    
    Verkeerde types resulteren in ValidationError.
    """
    filters = {"customer": customer}
    if not include_draft:
        filters["docstatus"] = 1
    
    orders = frappe.get_all(
        "Sales Order",
        filters=filters,
        limit=limit
    )
    return {"orders": orders, "count": len(orders)}
```

**v14 Compatibiliteit**: Type annotations werken wel maar worden niet automatisch gevalideerd.

## Complexe Data Structuren

### List van Dicts

```python
@frappe.whitelist(methods=["POST"])
def bulk_update(items):
    """
    JavaScript:
    frappe.call({
        method: '...',
        args: {
            items: JSON.stringify([
                {name: 'ITEM-001', qty: 10},
                {name: 'ITEM-002', qty: 20}
            ])
        }
    })
    """
    if isinstance(items, str):
        items = frappe.parse_json(items)
    
    results = []
    for item in items:
        frappe.db.set_value("Item", item['name'], "qty", item['qty'])
        results.append(item['name'])
    
    return {"updated": results}
```

### Nested Objects

```python
@frappe.whitelist(methods=["POST"])
def create_order(order_data):
    """
    JavaScript:
    frappe.call({
        method: '...',
        args: {
            order_data: JSON.stringify({
                customer: 'CUST-001',
                items: [
                    {item_code: 'ITEM-001', qty: 1},
                    {item_code: 'ITEM-002', qty: 2}
                ],
                shipping: {
                    address: '...',
                    method: 'express'
                }
            })
        }
    })
    """
    if isinstance(order_data, str):
        order_data = frappe.parse_json(order_data)
    
    # Toegang tot nested data
    customer = order_data.get('customer')
    items = order_data.get('items', [])
    shipping = order_data.get('shipping', {})
    shipping_method = shipping.get('method', 'standard')
    
    return {"status": "received"}
```

## Validatie Patronen

### Verplichte Parameters

```python
@frappe.whitelist()
def required_params(customer, amount):
    """Verplichte parameters valideren."""
    if not customer:
        frappe.throw(_("Customer is required"))
    
    if amount is None:
        frappe.throw(_("Amount is required"))
    
    return {"valid": True}
```

### Type Validatie (Handmatig)

```python
@frappe.whitelist()
def validate_types(email, amount, items):
    """Handmatige type validatie (v14 compatible)."""
    # String validatie
    if not isinstance(email, str) or not email:
        frappe.throw(_("Valid email required"))
    
    # Numeriek valideren
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        frappe.throw(_("Amount must be a number"))
    
    # List valideren
    if isinstance(items, str):
        items = frappe.parse_json(items)
    if not isinstance(items, list):
        frappe.throw(_("Items must be a list"))
    
    return {"email": email, "amount": amount, "items": items}
```

## Veelvoorkomende Problemen

| Probleem | Oorzaak | Oplossing |
|----------|---------|-----------|
| `None` voor verwachte waarde | Parameter niet meegestuurd | Default value of validatie |
| String ipv dict/list | JSON niet geparsed | `frappe.parse_json()` gebruiken |
| Type mismatch | Geen conversie | Expliciet converteren |
| Unicode errors | Encoding issues | `frappe.safe_decode()` gebruiken |
