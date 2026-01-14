# Client Script Anti-Patterns (NL)

## ❌ Direct Veldwaarden Toewijzen

**FOUT:**
```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        frm.doc.customer_name = 'Test';  // FOUT!
    }
});
```

**CORRECT:**
```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        frm.set_value('customer_name', 'Test');  // GOED
    }
});
```

**Waarom:** `frm.set_value()` triggert dirty flag, validation, en UI refresh. Direct toewijzen doet dit niet.

---

## ❌ Child Table Wijzigen Zonder Refresh

**FOUT:**
```javascript
let row = frm.add_child('items', { item_code: 'TEST' });
// UI toont nieuwe rij niet!
```

**CORRECT:**
```javascript
let row = frm.add_child('items', { item_code: 'TEST' });
frm.refresh_field('items');  // VERPLICHT
```

**Waarom:** De UI wordt niet automatisch bijgewerkt na child table manipulatie.

---

## ❌ set_query in refresh Event

**FOUT:**
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

**Waarom:** `setup` wordt eenmaal uitgevoerd; `refresh` wordt herhaaldelijk getriggerd. Query in refresh is inefficiënt.

---

## ❌ Synchrone Server Calls

**FOUT:**
```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        frappe.call({
            method: 'myapp.api.get_data',
            async: false,  // FOUT! Blokkert UI
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

**Waarom:** Synchrone calls bevriezen de browser. Gebruik altijd async patterns.

---

## ❌ Hardcoded Strings Zonder Vertaling

**FOUT:**
```javascript
frappe.msgprint('Operation completed successfully');
frm.add_custom_button('Generate Report', () => {});
```

**CORRECT:**
```javascript
frappe.msgprint(__('Operation completed successfully'));
frm.add_custom_button(__('Generate Report'), () => {});
```

**Waarom:** Zonder `__()` werkt vertaling niet voor meertalige installaties.

---

## ❌ Callback Hell

**FOUT:**
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
                        // Onleesbaar!
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
    // Leesbaar en onderhoudbaar
}
```

---

## ❌ Geen Error Handling bij Server Calls

**FOUT:**
```javascript
frappe.call({
    method: 'myapp.api.risky_operation',
    callback: (r) => {
        frm.set_value('result', r.message);  // Crasht als r.message undefined
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

**FOUT:**
```javascript
frappe.ui.form.on('Sales Order', {
    validate(frm) {
        frappe.call({
            method: 'myapp.api.check_credit',
            async: true,
            callback: (r) => {
                if (!r.message.ok) {
                    frappe.throw(__('Credit exceeded'));  // Te laat! Save is al gestart
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
            frappe.throw(__('Credit exceeded'));  // Werkt correct
        }
    }
});
```

**Waarom:** Non-blocking callbacks worden uitgevoerd nadat validate al is teruggekeerd.

---

## ❌ Overmatig refresh_field Gebruik

**FOUT:**
```javascript
frm.doc.items.forEach(item => {
    item.amount = item.qty * item.rate;
    frm.refresh_field('items');  // FOUT! In elke iteratie
});
```

**CORRECT:**
```javascript
frm.doc.items.forEach(item => {
    item.amount = item.qty * item.rate;
});
frm.refresh_field('items');  // Eenmaal na alle wijzigingen
```

---

## ❌ Global Variables voor State

**FOUT:**
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
        frm.customer_data = {};  // State op frm object
    }
});
```

**Waarom:** Global variables conflicteren tussen meerdere open forms.

---

## ❌ DOM Manipulatie Buiten Frappe API

**FOUT:**
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

**Waarom:** Direct DOM manipuleren kan conflicteren met Frappe's form rendering.

---

## ❌ Blocking Loops voor Server Calls

**FOUT:**
```javascript
frm.doc.items.forEach(item => {
    frappe.call({
        method: 'myapp.api.process_item',
        args: { item: item.name },
        async: false  // Blokkert voor ELKE item!
    });
});
```

**CORRECT:**
```javascript
// Optie 1: Batch call
frappe.call({
    method: 'myapp.api.process_items',
    args: { items: frm.doc.items.map(i => i.name) }
});

// Optie 2: Promise.all voor parallelle uitvoering
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

## ❌ Geen Check op frm.is_new()

**FOUT:**
```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // Button verschijnt ook op nieuwe documenten waar het niet werkt
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

## ❌ frappe.model.set_value Buiten Child Events

**FOUT:**
```javascript
// In parent form context
frappe.model.set_value(cdt, cdn, 'qty', 10);  // cdt/cdn niet beschikbaar
```

**CORRECT:**
```javascript
// In child table event
frappe.ui.form.on('Sales Order Item', {
    item_code(frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'qty', 10);  // Correct context
    }
});

// Of direct via frm.doc
frm.doc.items[0].qty = 10;
frm.refresh_field('items');
```

---

## Checklist Vóór Deployment

- [ ] Alle strings gewrapped in `__()`
- [ ] Geen `async: false` calls
- [ ] `refresh_field()` na child table wijzigingen
- [ ] Error handling op alle server calls
- [ ] `frm.is_new()` check waar nodig
- [ ] `set_query` in `setup`, niet `refresh`
- [ ] Geen global state variables
- [ ] Geen directe DOM manipulatie
