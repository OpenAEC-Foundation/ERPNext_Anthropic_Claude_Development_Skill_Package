# Client Calls Reference

Hoe whitelisted methods aanroepen vanuit JavaScript.

## frappe.call() - Algemeen Gebruik

### Basis Syntax

```javascript
frappe.call({
    method: 'myapp.api.get_customer_summary',
    args: {
        customer: 'CUST-00001',
        include_orders: true
    },
    callback: function(r) {
        if (r.message) {
            console.log(r.message);
        }
    }
});
```

### Met Loading Indicator

```javascript
frappe.call({
    method: 'myapp.api.process_data',
    args: { data: myData },
    freeze: true,
    freeze_message: __('Processing...'),
    callback: function(r) {
        frappe.show_alert({
            message: __('Done!'),
            indicator: 'green'
        });
    }
});
```

### Promise-Based (Modern)

```javascript
frappe.call({
    method: 'myapp.api.get_data',
    args: { id: 123 }
}).then(r => {
    console.log(r.message);
}).catch(err => {
    console.error(err);
});
```

### Async/Await

```javascript
async function getData() {
    let r = await frappe.call({
        method: 'myapp.api.get_data',
        args: { id: 123 }
    });
    return r.message;
}

// Gebruik
getData().then(data => console.log(data));
```

## frappe.call() Parameters

| Parameter | Type | Default | Beschrijving |
|-----------|------|---------|--------------|
| `method` | string | - | Dotted path naar whitelisted method |
| `args` | object | `{}` | Arguments voor de method |
| `type` | string | `"POST"` | HTTP method: GET, POST, PUT, DELETE |
| `callback` | function | - | Success callback |
| `error` | function | - | Error callback |
| `always` | function | - | Always callback (success of error) |
| `freeze` | boolean | `false` | Toon loading indicator |
| `freeze_message` | string | - | Custom loading message |
| `async` | boolean | `true` | Async request |
| `btn` | jQuery | - | Button om te disablen tijdens call |

### Alle Parameters Voorbeeld

```javascript
frappe.call({
    method: 'myapp.api.complex_operation',
    type: 'POST',
    args: {
        customer: 'CUST-001',
        items: JSON.stringify([{item: 'ITEM-001', qty: 10}])
    },
    freeze: true,
    freeze_message: __('Processing your request...'),
    btn: $(this),  // Disable button tijdens call
    callback: function(r) {
        if (r.message.success) {
            frappe.msgprint(__('Operation completed!'));
        }
    },
    error: function(r) {
        frappe.msgprint({
            title: __('Error'),
            indicator: 'red',
            message: __('Operation failed')
        });
    },
    always: function() {
        // Cleanup, altijd uitgevoerd
        console.log('Request completed');
    }
});
```

## frm.call() - Controller Methods

Voor methods op een DocType controller:

### Basis Syntax

```javascript
// In Form Script
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        frm.add_custom_button(__('Calculate Tax'), () => {
            frm.call('calculate_taxes', {
                include_shipping: true
            }).then(r => {
                if (r.message) {
                    frm.set_value('tax_amount', r.message.tax_amount);
                }
            });
        });
    }
});
```

### Server-Side Vereiste

```python
# In controller (myapp/doctype/sales_order/sales_order.py)
class SalesOrder(Document):
    @frappe.whitelist()
    def calculate_taxes(self, include_shipping=False):
        """Controller method MOET @frappe.whitelist() hebben."""
        tax = self.total * 0.21
        if include_shipping:
            tax += 50
        return {"tax_amount": tax}
```

### Met Refresh na Call

```javascript
frm.call('update_status', {
    new_status: 'Approved'
}).then(r => {
    if (r.message) {
        frm.reload_doc();  // Herlaad document
    }
});
```

### Met Loading Indicator

```javascript
frm.call({
    method: 'send_email',
    args: { template: 'order_confirmation' },
    freeze: true,
    freeze_message: __('Sending email...')
}).then(r => {
    frappe.show_alert({
        message: __('Email sent'),
        indicator: 'green'
    });
});
```

## Direct REST API Calls

### Met Fetch API

```javascript
fetch('/api/method/myapp.api.get_data', {
    method: 'POST',
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': frappe.csrf_token
    },
    body: JSON.stringify({
        param1: 'value1',
        param2: 'value2'
    })
})
.then(r => r.json())
.then(data => console.log(data.message))
.catch(err => console.error(err));
```

### GET Request

```javascript
fetch('/api/method/myapp.api.get_status?order_id=SO-00001', {
    headers: {
        'Accept': 'application/json',
        'X-Frappe-CSRF-Token': frappe.csrf_token
    }
})
.then(r => r.json())
.then(data => console.log(data.message));
```

## API Endpoints

| Type | Endpoint Pattern |
|------|-----------------|
| Method call | `/api/method/dotted.path.to.function` |
| v15+ Method | `/api/v1/method/dotted.path.to.function` |
| v15 API v2 | `/api/v2/method/dotted.path.to.function` |
| Document method | `/api/v2/document/{doctype}/{name}/method/{method}` |

### Endpoint Voorbeelden

```javascript
// Standalone API
// Server: myapp/api.py â†’ def get_customers()
frappe.call({ method: 'myapp.api.get_customers' });
// Endpoint: /api/method/myapp.api.get_customers

// Utils module
// Server: myapp/utils/helpers.py â†’ def calculate()
frappe.call({ method: 'myapp.utils.helpers.calculate' });
// Endpoint: /api/method/myapp.utils.helpers.calculate

// Controller method (via frm.call)
// Server: myapp/doctype/sales_order/sales_order.py â†’ class SalesOrder: def send_email()
frm.call('send_email');
// Endpoint: /api/method/run_doc_method (intern)
```

## Error Handling

### Callback-Based

```javascript
frappe.call({
    method: 'myapp.api.risky_operation',
    args: { data: myData },
    callback: function(r) {
        if (r.message && r.message.success) {
            frappe.msgprint(__('Success!'));
        }
    },
    error: function(r) {
        // Server error (500, etc.)
        frappe.msgprint({
            title: __('Error'),
            indicator: 'red',
            message: __('Operation failed. Please try again.')
        });
    }
});
```

### Promise-Based

```javascript
frappe.call({
    method: 'myapp.api.get_data',
    args: { id: 123 }
})
.then(r => {
    if (!r.message) {
        throw new Error('No data returned');
    }
    return r.message;
})
.catch(err => {
    frappe.show_alert({
        message: err.message || __('An error occurred'),
        indicator: 'red'
    });
});
```

### Async/Await met Try/Catch

```javascript
async function processData() {
    try {
        let r = await frappe.call({
            method: 'myapp.api.process',
            args: { data: myData }
        });
        
        if (r.message.success) {
            frappe.show_alert({
                message: __('Done!'),
                indicator: 'green'
            });
        }
    } catch (err) {
        frappe.show_alert({
            message: __('Failed'),
            indicator: 'red'
        });
    }
}
```

## Veelvoorkomende Patronen

### Batch Requests

```javascript
async function batchProcess(items) {
    const results = [];
    
    for (const item of items) {
        const r = await frappe.call({
            method: 'myapp.api.process_item',
            args: { item: item }
        });
        results.push(r.message);
    }
    
    return results;
}
```

### Parallel Requests

```javascript
async function parallelFetch(ids) {
    const promises = ids.map(id => 
        frappe.call({
            method: 'myapp.api.get_item',
            args: { id: id }
        })
    );
    
    const results = await Promise.all(promises);
    return results.map(r => r.message);
}
```

### Debounced Call (Search)

```javascript
let searchTimeout;

function searchCustomers(query) {
    clearTimeout(searchTimeout);
    
    searchTimeout = setTimeout(() => {
        frappe.call({
            method: 'myapp.api.search_customers',
            args: { query: query }
        }).then(r => {
            updateResults(r.message);
        });
    }, 300);  // Wacht 300ms na laatste keystroke
}
```

## Tips

1. **Altijd `r.message` checken** - Response kan leeg zijn
2. **JSON.stringify voor complexe args** - Arrays en objects als string
3. **CSRF token** - Vereist voor directe fetch calls
4. **freeze gebruiken** - Voor lange operaties
5. **Error callbacks** - Altijd afhandelen voor betere UX
