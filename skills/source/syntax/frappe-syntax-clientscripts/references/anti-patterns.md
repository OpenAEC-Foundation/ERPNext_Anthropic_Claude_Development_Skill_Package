# Client Script Anti-Patterns (EN)

## ❌ Direct Field Value Assignment

**WRONG:**
```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        frm.doc.customer_name = 'Test';  // WRONG!
    }
});
```

**CORRECT:**
```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        frm.set_value('customer_name', 'Test');  // GOOD
    }
});
```

**Why:** `frm.set_value()` triggers dirty flag, validation, and UI refresh. Direct assignment does not.

---

## ❌ Child Table Modification Without Refresh

**WRONG:**
```javascript
let row = frm.add_child('items', { item_code: 'TEST' });
// UI doesn't show new row!
```

**CORRECT:**
```javascript
let row = frm.add_child('items', { item_code: 'TEST' });
frm.refresh_field('items');  // REQUIRED
```

**Why:** The UI is not automatically updated after child table manipulation.

---

## ❌ set_query in refresh Event

**WRONG:**
```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));
    }
});
```

**CORRECT:**
```javascript
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));
    }
});
```

**Why:** `setup` runs once; `refresh` is triggered repeatedly. Query in refresh is inefficient.

---

## ❌ Synchronous Server Calls

**WRONG:**
```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        frappe.call({
            method: 'myapp.api.get_data',
            async: false,  // WRONG! Blocks UI
            callback: (r) => { }
        });
    }
});
```

**CORRECT:**
```javascript
frappe.ui.form.on('Sales Order', {
    async customer(frm) {
        let r = await frappe.call({
            method: 'myapp.api.get_data'
        });
        // Process result
    }
});
```

**Why:** Synchronous calls freeze the browser. Always use async patterns.

---

## ❌ Hardcoded Strings Without Translation

**WRONG:**
```javascript
frappe.msgprint('Operation completed successfully');
frm.add_custom_button('Generate Report', () => {});
```

**CORRECT:**
```javascript
frappe.msgprint(__('Operation completed successfully'));
frm.add_custom_button(__('Generate Report'), () => {});
```

**Why:** Without `__()` translation won't work for multilingual installations.

---

## ❌ Callback Hell

**WRONG:**
```javascript
frappe.call({
    method: 'method1',
    callback: (r1) => {
        frappe.call({
            method: 'method2',
            callback: (r2) => {
                frappe.call({
                    method: 'method3',
                    callback: (r3) => {
                        // Unreadable!
                    }
                });
            }
        });
    }
});
```

**CORRECT:**
```javascript
async function processData() {
    let r1 = await frappe.call({ method: 'method1' });
    let r2 = await frappe.call({ method: 'method2' });
    let r3 = await frappe.call({ method: 'method3' });
    // Readable and maintainable
}
```

---

## ❌ No Error Handling on Server Calls

**WRONG:**
```javascript
frappe.call({
    method: 'myapp.api.risky_operation',
    callback: (r) => {
        frm.set_value('result', r.message);  // Crashes if r.message undefined
    }
});
```

**CORRECT:**
```javascript
frappe.call({
    method: 'myapp.api.risky_operation',
    callback: (r) => {
        if (r.message) {
            frm.set_value('result', r.message);
        }
    },
    error: (r) => {
        frappe.msgprint(__('Operation failed'));
    }
});
```

---

## ❌ frappe.throw in Async Callbacks

**WRONG:**
```javascript
frappe.ui.form.on('Sales Order', {
    validate(frm) {
        frappe.call({
            method: 'myapp.api.check_credit',
            async: true,
            callback: (r) => {
                if (!r.message.ok) {
                    frappe.throw(__('Credit exceeded'));  // Too late! Save already started
                }
            }
        });
    }
});
```

**CORRECT:**
```javascript
frappe.ui.form.on('Sales Order', {
    async validate(frm) {
        let r = await frappe.call({
            method: 'myapp.api.check_credit',
            args: { customer: frm.doc.customer }
        });
        
        if (!r.message.ok) {
            frappe.throw(__('Credit exceeded'));  // Works correctly
        }
    }
});
```

**Why:** Non-blocking callbacks execute after validate has already returned.

---

## ❌ Excessive refresh_field Usage

**WRONG:**
```javascript
frm.doc.items.forEach(item => {
    item.amount = item.qty * item.rate;
    frm.refresh_field('items');  // WRONG! In every iteration
});
```

**CORRECT:**
```javascript
frm.doc.items.forEach(item => {
    item.amount = item.qty * item.rate;
});
frm.refresh_field('items');  // Once after all modifications
```

---

## ❌ Global Variables for State

**WRONG:**
```javascript
var current_customer = null;  // Global state

frappe.ui.form.on('Sales Order', {
    customer(frm) {
        current_customer = frm.doc.customer;
    }
});
```

**CORRECT:**
```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        frm.customer_data = {};  // State on frm object
    }
});
```

**Why:** Global variables conflict between multiple open forms.

---

## ❌ DOM Manipulation Outside Frappe API

**WRONG:**
```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        $('[data-fieldname="customer"]').hide();  // Direct jQuery
    }
});
```

**CORRECT:**
```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        frm.toggle_display('customer', false);  // Frappe API
    }
});
```

**Why:** Direct DOM manipulation can conflict with Frappe's form rendering.

---

## ❌ Blocking Loops for Server Calls

**WRONG:**
```javascript
frm.doc.items.forEach(item => {
    frappe.call({
        method: 'myapp.api.process_item',
        args: { item: item.name },
        async: false  // Blocks for EVERY item!
    });
});
```

**CORRECT:**
```javascript
// Option 1: Batch call
frappe.call({
    method: 'myapp.api.process_items',
    args: { items: frm.doc.items.map(i => i.name) }
});

// Option 2: Promise.all for parallel execution
async function processItems(frm) {
    await Promise.all(frm.doc.items.map(item =>
        frappe.call({
            method: 'myapp.api.process_item',
            args: { item: item.name }
        })
    ));
}
```

---

## ❌ No Check on frm.is_new()

**WRONG:**
```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // Button appears even on new documents where it won't work
        frm.add_custom_button(__('Process'), () => {
            frm.call('process');
        });
    }
});
```

**CORRECT:**
```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Process'), () => {
                frm.call('process');
            });
        }
    }
});
```

---

## ❌ frappe.model.set_value Outside Child Events

**WRONG:**
```javascript
// In parent form context
frappe.model.set_value(cdt, cdn, 'qty', 10);  // cdt/cdn not available
```

**CORRECT:**
```javascript
// In child table event
frappe.ui.form.on('Sales Order Item', {
    item_code(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'qty', 10);  // Correct context
    }
});

// Or directly via frm.doc
frm.doc.items[0].qty = 10;
frm.refresh_field('items');
```

---

## Pre-Deployment Checklist

- [ ] All strings wrapped in `__()`
- [ ] No `async: false` calls
- [ ] `refresh_field()` after child table modifications
- [ ] Error handling on all server calls
- [ ] `frm.is_new()` check where needed
- [ ] `set_query` in `setup`, not `refresh`
- [ ] No global state variables
- [ ] No direct DOM manipulation
