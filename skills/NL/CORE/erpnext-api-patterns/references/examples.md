# API Examples

> Complete werkende voorbeelden voor veelvoorkomende integratie scenarios.

---

## 1. Python API Client

```python
"""
Frappe API Client - Complete implementatie
"""
import requests
import os
from typing import Optional, Dict, List, Any

class FrappeClient:
    def __init__(self, url: str, api_key: str, api_secret: str):
        self.url = url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {api_key}:{api_secret}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        response = self.session.request(
            method,
            f'{self.url}{endpoint}',
            **kwargs
        )
        
        if not response.ok:
            error = response.json()
            raise Exception(
                error.get('_server_messages') or 
                error.get('message') or 
                response.text
            )
        
        return response.json()
    
    # Resource API Methods
    def get_list(
        self,
        doctype: str,
        fields: Optional[List[str]] = None,
        filters: Optional[List] = None,
        order_by: Optional[str] = None,
        limit_start: int = 0,
        limit_page_length: int = 20
    ) -> List[Dict]:
        params = {
            'limit_start': limit_start,
            'limit_page_length': limit_page_length
        }
        if fields:
            params['fields'] = str(fields)
        if filters:
            params['filters'] = str(filters)
        if order_by:
            params['order_by'] = order_by
        
        result = self._request('GET', f'/api/resource/{doctype}', params=params)
        return result.get('data', [])
    
    def get_doc(self, doctype: str, name: str) -> Dict:
        result = self._request('GET', f'/api/resource/{doctype}/{name}')
        return result.get('data', {})
    
    def create_doc(self, doctype: str, data: Dict) -> Dict:
        result = self._request('POST', f'/api/resource/{doctype}', json=data)
        return result.get('data', {})
    
    def update_doc(self, doctype: str, name: str, data: Dict) -> Dict:
        result = self._request('PUT', f'/api/resource/{doctype}/{name}', json=data)
        return result.get('data', {})
    
    def delete_doc(self, doctype: str, name: str) -> bool:
        self._request('DELETE', f'/api/resource/{doctype}/{name}')
        return True
    
    # Method API
    def call_method(self, method: str, **kwargs) -> Any:
        result = self._request('POST', f'/api/method/{method}', json=kwargs)
        return result.get('message')
    
    # Convenience methods
    def get_value(
        self,
        doctype: str,
        name: str,
        fieldname: str
    ) -> Any:
        return self.call_method(
            'frappe.client.get_value',
            doctype=doctype,
            filters={'name': name},
            fieldname=fieldname
        )
    
    def submit_doc(self, doctype: str, name: str) -> Dict:
        return self.call_method(
            'frappe.client.submit',
            doc={'doctype': doctype, 'name': name}
        )

# Gebruik
if __name__ == '__main__':
    client = FrappeClient(
        url='https://site.local',
        api_key=os.environ['FRAPPE_API_KEY'],
        api_secret=os.environ['FRAPPE_API_SECRET']
    )
    
    # List customers
    customers = client.get_list(
        'Customer',
        fields=['name', 'customer_name', 'outstanding_amount'],
        filters=[['outstanding_amount', '>', 0]],
        order_by='outstanding_amount desc',
        limit_page_length=10
    )
    
    # Create order
    order = client.create_doc('Sales Order', {
        'customer': 'CUST-00001',
        'delivery_date': '2024-02-01',
        'items': [
            {'item_code': 'ITEM-001', 'qty': 5, 'rate': 100}
        ]
    })
    
    # Submit order
    client.submit_doc('Sales Order', order['name'])
```

---

## 2. JavaScript/Node.js Client

```javascript
/**
 * Frappe API Client - Node.js implementatie
 */
class FrappeClient {
    constructor(url, apiKey, apiSecret) {
        this.url = url.replace(/\/$/, '');
        this.auth = `token ${apiKey}:${apiSecret}`;
    }
    
    async _request(method, endpoint, options = {}) {
        const response = await fetch(`${this.url}${endpoint}`, {
            method,
            headers: {
                'Authorization': this.auth,
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                ...options.headers
            },
            body: options.body ? JSON.stringify(options.body) : undefined
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            const error = data._server_messages || data.message || response.statusText;
            throw new Error(typeof error === 'string' ? error : JSON.stringify(error));
        }
        
        return data;
    }
    
    // Resource API
    async getList(doctype, options = {}) {
        const params = new URLSearchParams();
        
        if (options.fields) {
            params.set('fields', JSON.stringify(options.fields));
        }
        if (options.filters) {
            params.set('filters', JSON.stringify(options.filters));
        }
        if (options.orderBy) {
            params.set('order_by', options.orderBy);
        }
        params.set('limit_start', options.limitStart || 0);
        params.set('limit_page_length', options.limitPageLength || 20);
        
        const result = await this._request('GET', `/api/resource/${doctype}?${params}`);
        return result.data || [];
    }
    
    async getDoc(doctype, name) {
        const result = await this._request('GET', `/api/resource/${doctype}/${name}`);
        return result.data || {};
    }
    
    async createDoc(doctype, data) {
        const result = await this._request('POST', `/api/resource/${doctype}`, { body: data });
        return result.data || {};
    }
    
    async updateDoc(doctype, name, data) {
        const result = await this._request('PUT', `/api/resource/${doctype}/${name}`, { body: data });
        return result.data || {};
    }
    
    async deleteDoc(doctype, name) {
        await this._request('DELETE', `/api/resource/${doctype}/${name}`);
        return true;
    }
    
    // Method API
    async callMethod(method, args = {}) {
        const result = await this._request('POST', `/api/method/${method}`, { body: args });
        return result.message;
    }
}

// Gebruik
const client = new FrappeClient(
    'https://site.local',
    process.env.FRAPPE_API_KEY,
    process.env.FRAPPE_API_SECRET
);

// Async/await
async function main() {
    // Get customers with outstanding balance
    const customers = await client.getList('Customer', {
        fields: ['name', 'customer_name', 'outstanding_amount'],
        filters: [['outstanding_amount', '>', 0]],
        orderBy: 'outstanding_amount desc',
        limitPageLength: 10
    });
    
    console.log('Customers:', customers);
    
    // Create sales order
    const order = await client.createDoc('Sales Order', {
        customer: 'CUST-00001',
        delivery_date: '2024-02-01',
        items: [
            { item_code: 'ITEM-001', qty: 5, rate: 100 }
        ]
    });
    
    console.log('Created order:', order.name);
}

main().catch(console.error);
```

---

## 3. cURL Scripts

### Basis CRUD

```bash
#!/bin/bash
# frappe_api.sh - cURL wrapper voor Frappe API

BASE_URL="https://site.local"
API_KEY="your_api_key"
API_SECRET="your_api_secret"

# Auth header
AUTH="Authorization: token ${API_KEY}:${API_SECRET}"

# List customers
curl -s -X GET "${BASE_URL}/api/resource/Customer" \
  -H "${AUTH}" \
  -H "Accept: application/json" \
  -G \
  --data-urlencode 'fields=["name","customer_name"]' \
  --data-urlencode 'filters=[["customer_type","=","Company"]]' \
  --data-urlencode 'limit_page_length=10' | jq .

# Get single document
curl -s -X GET "${BASE_URL}/api/resource/Customer/CUST-00001" \
  -H "${AUTH}" \
  -H "Accept: application/json" | jq .

# Create document
curl -s -X POST "${BASE_URL}/api/resource/Customer" \
  -H "${AUTH}" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "New Customer",
    "customer_type": "Company"
  }' | jq .

# Update document
curl -s -X PUT "${BASE_URL}/api/resource/Customer/CUST-00001" \
  -H "${AUTH}" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Updated Name"
  }' | jq .

# Delete document
curl -s -X DELETE "${BASE_URL}/api/resource/Customer/CUST-00001" \
  -H "${AUTH}" \
  -H "Accept: application/json" | jq .

# Call method
curl -s -X POST "${BASE_URL}/api/method/frappe.client.get_count" \
  -H "${AUTH}" \
  -H "Content-Type: application/json" \
  -d '{
    "doctype": "Sales Order",
    "filters": {"status": "Draft"}
  }' | jq .
```

---

## 4. Webhook Ontvanger (Flask)

```python
"""
Flask webhook receiver met signature verificatie
"""
from flask import Flask, request, jsonify
import hmac
import hashlib
import json
import os

app = Flask(__name__)
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'your-secret')

def verify_signature(payload: bytes, signature: str) -> bool:
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.route('/webhook/order', methods=['POST'])
def handle_order_webhook():
    # Verify signature
    signature = request.headers.get('X-Webhook-Secret', '')
    if not verify_signature(request.get_data(), signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Parse data
    data = request.get_json()
    event = data.get('event')
    doctype = data.get('doctype')
    doc_data = data.get('data', {})
    
    # Handle events
    if event == 'on_submit' and doctype == 'Sales Order':
        process_submitted_order(doc_data)
    elif event == 'on_cancel' and doctype == 'Sales Order':
        handle_cancelled_order(doc_data)
    
    return jsonify({'status': 'ok'}), 200

def process_submitted_order(order: dict):
    """Process submitted sales order"""
    order_id = order.get('name')
    customer = order.get('customer')
    total = order.get('grand_total')
    
    print(f"New order {order_id} from {customer}: ${total}")
    
    # Sync to external system, send notification, etc.

def handle_cancelled_order(order: dict):
    """Handle cancelled order"""
    order_id = order.get('name')
    print(f"Order {order_id} was cancelled")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 5. Paginatie Helper

```python
def fetch_all_documents(client, doctype, filters=None, fields=None, batch_size=100):
    """
    Haal alle documents op met automatische paginatie
    """
    all_docs = []
    offset = 0
    
    while True:
        batch = client.get_list(
            doctype,
            filters=filters,
            fields=fields,
            limit_start=offset,
            limit_page_length=batch_size
        )
        
        if not batch:
            break
        
        all_docs.extend(batch)
        offset += batch_size
        
        # Safety check
        if len(batch) < batch_size:
            break
    
    return all_docs

# Gebruik
all_orders = fetch_all_documents(
    client,
    'Sales Order',
    filters=[['status', '=', 'Completed']],
    fields=['name', 'customer', 'grand_total'],
    batch_size=100
)
```

---

## 6. Batch Operations

```python
def batch_create_documents(client, doctype, documents, batch_size=50):
    """
    Maak meerdere documents in batches
    """
    results = []
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        for doc in batch:
            try:
                result = client.create_doc(doctype, doc)
                results.append({'success': True, 'doc': result})
            except Exception as e:
                results.append({'success': False, 'error': str(e), 'data': doc})
    
    return results

# Gebruik
customers_to_create = [
    {'customer_name': 'Customer 1', 'customer_type': 'Company'},
    {'customer_name': 'Customer 2', 'customer_type': 'Individual'},
    # ... meer customers
]

results = batch_create_documents(client, 'Customer', customers_to_create)

# Check results
successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]
print(f"Created: {len(successful)}, Failed: {len(failed)}")
```

---

## 7. Error Handling Pattern

```python
from enum import Enum

class FrappeAPIError(Exception):
    pass

class ValidationError(FrappeAPIError):
    pass

class PermissionError(FrappeAPIError):
    pass

class NotFoundError(FrappeAPIError):
    pass

def handle_api_response(response):
    """Parse API response en raise appropriate errors"""
    if response.status_code == 200:
        return response.json()
    
    try:
        error_data = response.json()
    except:
        raise FrappeAPIError(f"HTTP {response.status_code}: {response.text}")
    
    exc_type = error_data.get('exc_type', '')
    messages = error_data.get('_server_messages', '')
    
    if 'ValidationError' in exc_type:
        raise ValidationError(messages)
    elif 'PermissionError' in exc_type or response.status_code == 403:
        raise PermissionError(messages)
    elif 'DoesNotExistError' in exc_type or response.status_code == 404:
        raise NotFoundError(messages)
    else:
        raise FrappeAPIError(messages or error_data.get('message'))

# Gebruik
try:
    result = client.get_doc('Customer', 'NONEXISTENT')
except NotFoundError:
    print("Customer not found")
except PermissionError:
    print("No permission to access customer")
except ValidationError as e:
    print(f"Validation failed: {e}")
```
