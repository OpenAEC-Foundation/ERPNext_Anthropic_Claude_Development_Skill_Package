# ERPNext/Frappe Client Scripts - Research Document

> **Fase**: 1.1  
> **Datum**: Januari 2026  
> **Versie scope**: Frappe v14/v15, ERPNext v14/v15  
> **Basis**: erpnext-vooronderzoek.md sectie 1  

---

## 1. FORM EVENTS - Volledige Lijst en Execution Order

### 1.1 Form-Level Events

Alle form-level events ontvangen `frm` als eerste parameter.

| Event | Execution Order | Beschrijving | v14 | v15 |
|-------|-----------------|--------------|-----|-----|
| `setup` | 1 | Eenmalig wanneer form voor het eerst wordt aangemaakt. Ideaal voor `set_query`. | âœ… | âœ… |
| `before_load` | 2 | Voor het form gaat laden | âœ… | âœ… |
| `onload` | 3 | Wanneer form is geladen en gaat renderen | âœ… | âœ… |
| `refresh` | 4 | Na form load en render (meest gebruikt) | âœ… | âœ… |
| `onload_post_render` | 5 | Nadat form volledig is geladen en gerenderd | âœ… | âœ… |
| `validate` | - | Voor save, throw errors hier om save te voorkomen | âœ… | âœ… |
| `before_save` | - | Net voor save wordt aangeroepen | âœ… | âœ… |
| `after_save` | - | Nadat form succesvol is opgeslagen | âœ… | âœ… |
| `before_submit` | - | Voor document submission | âœ… | âœ… |
| `on_submit` | - | Nadat document is submitted | âœ… | âœ… |
| `before_cancel` | - | Voor cancellation | âœ… | âœ… |
| `after_cancel` | - | Nadat form is gecanceld | âœ… | âœ… |
| `timeline_refresh` | - | Nadat timeline is gerenderd | âœ… | âœ… |
| `before_workflow_action` | - | Voor workflow state change | âœ… | âœ… |
| `after_workflow_action` | - | Na workflow state change | âœ… | âœ… |
| `{fieldname}` | - | Wanneer dat veld's waarde verandert | âœ… | âœ… |
| `{fieldname}_on_form_rendered` | - | Wanneer row als form geopend wordt in Table field | âœ… | âœ… |

**Bron**: https://docs.frappe.io/framework/v15/user/en/api/form

### 1.2 Execution Order - Load Sequence

```
setup â†’ before_load â†’ onload â†’ refresh â†’ onload_post_render
```

### 1.3 Execution Order - Save Sequence

```
validate â†’ before_save â†’ [server processing] â†’ after_save â†’ refresh
```

### 1.4 Execution Order - Submit Sequence

```
validate â†’ before_submit â†’ [server processing] â†’ on_submit â†’ refresh
```

---

## 2. CHILD TABLE EVENTS

Child table events ontvangen drie parameters: `frm`, `cdt` (Child DocType name), `cdn` (Child Docname/row name).

| Event | Beschrijving | v14 | v15 |
|-------|--------------|-----|-----|
| `{fieldname}_add` | Wanneer rij wordt toegevoegd aan Table field | âœ… | âœ… |
| `{fieldname}_remove` | Wanneer rij wordt verwijderd uit Table field | âœ… | âœ… |
| `before_{fieldname}_remove` | Net voor rij wordt verwijderd | âœ… | âœ… |
| `{fieldname}_move` | Wanneer rij wordt herschikt naar andere locatie | âœ… | âœ… |
| `form_render` | Wanneer rij als form geopend wordt in Table field | âœ… | âœ… |

**Bron**: https://docs.frappe.io/framework/v15/user/en/api/form

### 2.1 Child Table Script Syntax

```javascript
// Child table scripts in HETZELFDE bestand als parent
frappe.ui.form.on('Quotation', {
    // Parent events
    refresh(frm) { }
});

frappe.ui.form.on('Quotation Item', {
    // cdt = Child DocType name (bijv. "Quotation Item")
    // cdn = row name (bijv. "bbfcb8da6a")
    item_code(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        // row bevat alle velden van deze specifieke rij
    },
    
    items_add(frm, cdt, cdn) {
        // Triggered wanneer rij toegevoegd
    },
    
    items_remove(frm, cdt, cdn) {
        // Triggered wanneer rij verwijderd
    }
});
```

---

## 3. FRM METHODS - Complete Reference

### 3.1 Waarden Zetten en Ophalen

| Method | Signature | Return | Beschrijving |
|--------|-----------|--------|--------------|
| `frm.set_value` | `(fieldname, value)` of `({field: value})` | `Promise` | Zet waarde en triggert field change event |
| `frm.doc.{fieldname}` | - | `any` | Direct ophalen van veldwaarde |

```javascript
// Enkele waarde
frm.set_value('status', 'Approved');

// Meerdere waarden
frm.set_value({
    status: 'Approved',
    priority: 'High'
});

// Met promise
frm.set_value('status', 'Open').then(() => {
    // na waarde gezet
});
```

### 3.2 Field Properties Manipuleren

| Method | Signature | Beschrijving |
|--------|-----------|--------------|
| `frm.set_df_property` | `(fieldname, property, value)` | Wijzig docfield property |
| `frm.toggle_display` | `(fieldname(s), show)` | Toon/verberg veld(en) |
| `frm.toggle_reqd` | `(fieldname(s), required)` | Maak veld(en) verplicht/optioneel |
| `frm.toggle_enable` | `(fieldname(s), enabled)` | Enable/disable veld(en) |

```javascript
// Enkele property
frm.set_df_property('status', 'read_only', 1);
frm.set_df_property('status', 'options', ['New', 'Open', 'Closed']);
frm.set_df_property('description', 'hidden', 1);
frm.set_df_property('title', 'reqd', 1);

// Toggle methods (accepteren array of string)
frm.toggle_display('priority', frm.doc.status === 'Open');
frm.toggle_display(['priority', 'due_date'], true);
frm.toggle_reqd('due_date', true);
frm.toggle_enable('amount', false);
```

### 3.3 Link Field Filters

| Method | Signature | Beschrijving |
|--------|-----------|--------------|
| `frm.set_query` | `(fieldname, [tablename], filters_fn)` | Filter link field opties |

```javascript
// Simpele filter
frm.set_query('customer', () => ({
    filters: { 
        territory: 'India',
        disabled: 0 
    }
}));

// Filter in child table
frm.set_query('item_code', 'items', (doc, cdt, cdn) => ({
    filters: { 
        item_group: 'Products',
        is_sales_item: 1 
    }
}));

// Met custom server-side query
frm.set_query('customer', () => ({
    query: 'myapp.queries.get_customers_by_territory',
    filters: { territory: frm.doc.territory }
}));

// BELANGRIJK: set_query moet vroeg in lifecycle (setup of onload)
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));
    }
});
```

### 3.4 Custom Buttons

| Method | Signature | Beschrijving |
|--------|-----------|--------------|
| `frm.add_custom_button` | `(label, action, [group])` | Voeg custom button toe |
| `frm.remove_custom_button` | `(label, [group])` | Verwijder custom button |
| `frm.clear_custom_buttons` | `()` | Verwijder alle custom buttons |
| `frm.change_custom_button_type` | `(label, [group], type)` | Wijzig button type |
| `frm.page.set_primary_action` | `(label, action)` | Zet primary action button |

```javascript
// Simpele button
frm.add_custom_button(__('Click Me'), () => {
    frappe.msgprint('Clicked!');
});

// Gegroepeerde buttons (verschijnen in dropdown)
frm.add_custom_button(__('Sales Invoice'), () => {
    // action
}, __('Create'));

frm.add_custom_button(__('Delivery Note'), () => {
    // action
}, __('Create'));

// Primary action
frm.page.set_primary_action(__('Process'), () => {
    frm.call('process_order').then(() => frm.reload_doc());
});

// Button type wijzigen
frm.change_custom_button_type('Submit', null, 'primary');

// Verwijderen
frm.remove_custom_button('Click Me');
frm.remove_custom_button('Sales Invoice', 'Create'); // gegroepeerde
frm.clear_custom_buttons();
```

### 3.5 Form Status Methods

| Method | Signature | Return | Beschrijving |
|--------|-----------|--------|--------------|
| `frm.is_new()` | `()` | `boolean` | Check of form nieuw is |
| `frm.is_dirty()` | `()` | `boolean` | Check of form unsaved changes heeft |
| `frm.dirty()` | `()` | - | Markeer form als dirty |

```javascript
if (!frm.is_new()) {
    frm.add_custom_button('Process', () => {});
}

if (frm.is_dirty()) {
    frappe.show_alert('Please save first');
}

// Forceer dirty state
frm.doc.custom_data = JSON.stringify(data);
frm.dirty();
frm.save();
```

### 3.6 Save en Refresh Methods

| Method | Signature | Return | Beschrijving |
|--------|-----------|--------|--------------|
| `frm.save()` | `([action])` | `Promise` | Save form |
| `frm.refresh()` | `()` | - | Refresh form met server values |
| `frm.reload_doc()` | `()` | `Promise` | Herlaad document van server |
| `frm.refresh_field()` | `(fieldname)` | - | Refresh specifiek veld |
| `frm.enable_save()` | `()` | - | Enable save button |
| `frm.disable_save()` | `()` | - | Disable save button |

```javascript
frm.save();                    // Normal save
frm.save('Submit');            // Submit
frm.save('Cancel');            // Cancel
frm.save('Update');            // Update (after submit)

frm.refresh_field('items');    // Na child table wijziging
frm.reload_doc();              // Volledige refresh
```

### 3.7 Server Calls

| Method | Signature | Return | Beschrijving |
|--------|-----------|--------|--------------|
| `frm.call()` | `(method, args)` | `Promise` | Call controller method |
| `frm.trigger()` | `(event_name)` | - | Trigger form event |

```javascript
// Call whitelisted controller method
frm.call('calculate_taxes', { include_shipping: true })
    .then(r => {
        if (r.message) {
            console.log(r.message);
        }
    });

// Trigger custom event
frm.trigger('recalculate_totals');

frappe.ui.form.on('Invoice', {
    refresh(frm) {
        frm.trigger('recalculate_totals');
    },
    recalculate_totals(frm) {
        // custom logic
    }
});
```

### 3.8 Child Table Methods

| Method | Signature | Return | Beschrijving |
|--------|-----------|--------|--------------|
| `frm.add_child()` | `(tablename, values)` | `row object` | Voeg rij toe aan child table |
| `frm.clear_table()` | `(tablename)` | - | Verwijder alle rijen |
| `frm.get_selected()` | `()` | `object` | Get geselecteerde rijen |

```javascript
// Rij toevoegen
let row = frm.add_child('items', {
    item_code: 'ITEM-001',
    qty: 5,
    rate: 100
});
frm.refresh_field('items'); // VERPLICHT na add_child

// Tabel legen
frm.clear_table('items');
frm.refresh_field('items');

// Rijen itereren
frm.doc.items.forEach((row, idx) => {
    if (row.qty > 10) row.discount = 5;
});
frm.refresh_field('items');

// Get selected rows
let selected = frm.get_selected();
// { items: ["bbfcb8da6a", "b1f1a43233"], taxes: ["036ab9452a"] }
```

### 3.9 Overige Methods

| Method | Signature | Beschrijving |
|--------|-----------|--------------|
| `frm.set_intro()` | `(message, [color])` | Toon intro text bovenaan form |
| `frm.email_doc()` | `([message])` | Open email dialog |
| `frm.ignore_doctypes_on_cancel_all` | `array` | Skip cancel voor gelinkte doctypes |

```javascript
// Intro text (colors: 'blue', 'red', 'orange', 'green', 'yellow')
frm.set_intro('Please fill all required fields', 'blue');

// Email dialog
frm.email_doc();
frm.email_doc(`Hello ${frm.doc.customer_name}`);

// Cancel ignore
frm.ignore_doctypes_on_cancel_all = ['Payment Entry', 'Journal Entry'];
```

---

## 4. FRAPPE CLIENT-SIDE API

### 4.1 frappe.call - Server Method Aanroepen

```javascript
frappe.call({
    method: 'myapp.api.process_data',
    args: {
        customer: frm.doc.customer,
        items: frm.doc.items
    },
    freeze: true,                        // Toon loading indicator
    freeze_message: __('Processing...'), // Custom freeze message
    async: true,                         // Default true
    callback: (r) => {
        if (r.message) {
            console.log(r.message);
        }
    },
    error: (r) => {
        // Error handling
    }
});

// Async/await pattern
async function processData(frm) {
    let r = await frappe.call({
        method: 'myapp.api.get_data',
        args: { name: frm.doc.name }
    });
    return r.message;
}
```

### 4.2 frappe.db - Client-side Database API

| Method | Signature | Return | Beschrijving |
|--------|-----------|--------|--------------|
| `frappe.db.get_value` | `(doctype, name, fieldname)` | `Promise` | Get field value(s) |
| `frappe.db.get_single_value` | `(doctype, fieldname)` | `Promise` | Get Single DocType value |
| `frappe.db.set_value` | `(doctype, name, fieldname, value)` | `Promise` | Set field value |
| `frappe.db.get_doc` | `(doctype, name)` | `Promise` | Get full document |
| `frappe.db.get_list` | `(doctype, options)` | `Promise` | Get list of documents |
| `frappe.db.insert` | `(doc)` | `Promise` | Insert new document |
| `frappe.db.count` | `(doctype, [filters])` | `Promise` | Count documents |
| `frappe.db.exists` | `(doctype, name)` | `Promise` | Check if exists |
| `frappe.db.delete_doc` | `(doctype, name)` | `Promise` | Delete document |

```javascript
// Get single value
frappe.db.get_value('Customer', frm.doc.customer, 'credit_limit')
    .then(r => console.log(r.message.credit_limit));

// Get multiple values
frappe.db.get_value('Customer', frm.doc.customer, ['credit_limit', 'territory'])
    .then(r => {
        let values = r.message;
        console.log(values.credit_limit, values.territory);
    });

// Get with filters
frappe.db.get_value('Customer', { status: 'Active' }, 'name')
    .then(r => console.log(r.message.name));

// Get Single DocType value
frappe.db.get_single_value('System Settings', 'time_zone')
    .then(timezone => console.log(timezone));

// Set value
frappe.db.set_value('Task', 'TASK00001', 'status', 'Completed');

// Get full document
frappe.db.get_doc('Customer', 'CUST-001')
    .then(doc => console.log(doc));

// Get list
frappe.db.get_list('Task', {
    fields: ['name', 'subject', 'status'],
    filters: { status: 'Open' },
    order_by: 'creation desc',
    limit_page_length: 20
}).then(records => console.log(records));

// Insert
frappe.db.insert({
    doctype: 'Task',
    subject: 'New Task'
}).then(doc => console.log(doc.name));

// Count
frappe.db.count('Task', { status: 'Open' })
    .then(count => console.log(count));

// Exists
frappe.db.exists('Task', 'TASK00001')
    .then(exists => console.log(exists)); // true/false
```

### 4.3 frappe.model - Model Utilities

```javascript
// Get row from child table
let row = frappe.get_doc(cdt, cdn);

// Set value in child table row
frappe.model.set_value(cdt, cdn, 'qty', 10);
frappe.model.set_value(cdt, cdn, {qty: 10, rate: 100});

// Get list from child table
let items = frappe.model.get_list('Sales Invoice Item', {
    parent: frm.doc.name
});

// Open mapped document
frappe.model.open_mapped_doc({
    method: 'erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice',
    frm: frm
});

// Create new document with prefilled values
frappe.new_doc('Task', {
    subject: 'Follow up',
    reference_type: frm.doc.doctype,
    reference_name: frm.doc.name
});
```

### 4.4 UI Utilities

```javascript
// Messages
frappe.msgprint('This is a message');
frappe.msgprint({
    title: __('Success'),
    message: __('Operation completed'),
    indicator: 'green'
});

// Alerts
frappe.show_alert({
    message: __('Saved'),
    indicator: 'green'
}, 5); // 5 seconds

// Throw (stops execution)
frappe.throw(__('Validation failed'));

// Confirm dialog
frappe.confirm(
    'Are you sure?',
    () => { /* Yes */ },
    () => { /* No */ }
);

// Routing
frappe.set_route('Form', 'Customer', 'CUST-001');
frappe.set_route('List', 'Task', 'Gantt');
let route = frappe.get_route(); // ['Form', 'Customer', 'CUST-001']

// Formatting
frappe.format('2019-09-08', { fieldtype: 'Date' }); // "09-08-2019"
frappe.format(2399, { fieldtype: 'Currency' });     // "2,399.00"
```

### 4.5 Realtime Events

```javascript
// Listen to event
frappe.realtime.on('event_name', (data) => {
    console.log(data);
});

// Stop listening
frappe.realtime.off('event_name');
```

---

## 5. ANTI-PATTERNS EN VEELVOORKOMENDE FOUTEN

### 5.1 âŒ refresh_field Vergeten na Child Table Wijziging

```javascript
// FOUT
frm.add_child('items', { item_code: 'X' });
// UI toont geen nieuwe rij!

// CORRECT
frm.add_child('items', { item_code: 'X' });
frm.refresh_field('items');
```

### 5.2 âŒ set_query op Verkeerd Moment

```javascript
// FOUT - te laat, werkt mogelijk niet consistent
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        frm.set_query('customer', () => ({}));
    }
});

// CORRECT - vroeg in lifecycle
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));
    }
});
```

### 5.3 âŒ Synchrone Behandeling van Async Calls

```javascript
// FOUT
let value;
frappe.db.get_value('Item', frm.doc.item_code, 'rate')
    .then(r => value = r.message.rate);
frm.set_value('rate', value); // value is undefined!

// CORRECT
frappe.db.get_value('Item', frm.doc.item_code, 'rate')
    .then(r => {
        frm.set_value('rate', r.message.rate);
    });

// OF met async/await
async function setRate(frm) {
    let r = await frappe.db.get_value('Item', frm.doc.item_code, 'rate');
    frm.set_value('rate', r.message.rate);
}
```

### 5.4 âŒ Infinite Loop door Field Change

```javascript
// FOUT - infinite loop
frappe.ui.form.on('Sales Order', {
    amount(frm) {
        frm.set_value('total', frm.doc.amount * 1.1);
    },
    total(frm) {
        frm.set_value('amount', frm.doc.total / 1.1);
    }
});

// CORRECT - gebruik flag
frappe.ui.form.on('Sales Order', {
    amount(frm) {
        if (frm._setting_amount) return;
        frm._setting_total = true;
        frm.set_value('total', frm.doc.amount * 1.1);
        frm._setting_total = false;
    },
    total(frm) {
        if (frm._setting_total) return;
        frm._setting_amount = true;
        frm.set_value('amount', frm.doc.total / 1.1);
        frm._setting_amount = false;
    }
});
```

### 5.5 âŒ cur_frm Gebruiken (Deprecated Pattern)

```javascript
// VEROUDERD - werkt maar niet aanbevolen
cur_frm.set_value('status', 'Open');

// CORRECT - gebruik frm parameter
frappe.ui.form.on('Task', {
    refresh(frm) {
        frm.set_value('status', 'Open');
    }
});
```

### 5.6 âŒ Validatie met frappe.msgprint ipv frappe.throw

```javascript
// FOUT - save gaat door ondanks foutmelding
frappe.ui.form.on('Invoice', {
    validate(frm) {
        if (frm.doc.total < 0) {
            frappe.msgprint('Total cannot be negative');
        }
    }
});

// CORRECT - throw stopt de save
frappe.ui.form.on('Invoice', {
    validate(frm) {
        if (frm.doc.total < 0) {
            frappe.throw(__('Total cannot be negative'));
        }
    }
});
```

### 5.7 âŒ Child Table Row Direct Modificeren zonder frappe.model.set_value

```javascript
// FOUT - UI update niet altijd correct
frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        row.amount = row.qty * row.rate; // Direct assignment
    }
});

// CORRECT - gebruik frappe.model.set_value
frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);
    }
});
```

### 5.8 âŒ Buttons Toevoegen zonder is_new() Check

```javascript
// FOUT - button verschijnt ook op nieuw document
frappe.ui.form.on('Task', {
    refresh(frm) {
        frm.add_custom_button('Complete', () => {});
    }
});

// CORRECT
frappe.ui.form.on('Task', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button('Complete', () => {});
        }
    }
});
```

### 5.9 âŒ Hardcoded Strings (Niet Vertaalbaar)

```javascript
// FOUT
frappe.msgprint('Document saved successfully');
frm.add_custom_button('Create Invoice', () => {});

// CORRECT - gebruik __() voor vertalingen
frappe.msgprint(__('Document saved successfully'));
frm.add_custom_button(__('Create Invoice'), () => {});
```

### 5.10 âŒ Vergeten dat frm.call een @frappe.whitelist Nodig Heeft

```javascript
// CLIENT
frm.call('my_method'); // Werkt alleen als my_method whitelisted is

// SERVER - VEREIST
class MyDocType(Document):
    @frappe.whitelist()  # VERPLICHT!
    def my_method(self):
        pass
```

---

## 6. BEST PRACTICES

### 6.1 Event Keuze Guide

| Doel | Event |
|------|-------|
| Link filters zetten | `setup` |
| Custom buttons toevoegen | `refresh` |
| UI initialisatie | `onload` of `refresh` |
| Data validatie | `validate` |
| Post-save actions | `after_save` |
| Veld wijziging afhandelen | `{fieldname}` |

### 6.2 Performance Tips

```javascript
// Cache frappe.call resultaten waar mogelijk
let cached_data = null;

frappe.ui.form.on('Sales Order', {
    async refresh(frm) {
        if (!cached_data) {
            let r = await frappe.call({
                method: 'myapp.api.get_config'
            });
            cached_data = r.message;
        }
        // gebruik cached_data
    }
});

// Batch child table updates
frm.doc.items.forEach(row => {
    // Bereken eerst alles
});
frm.refresh_field('items'); // EÃ©n keer refresh aan het eind
```

### 6.3 Code Organisatie

```javascript
// Goede structuur voor complexe scripts
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        setup_queries(frm);
    },
    
    refresh(frm) {
        setup_buttons(frm);
        setup_indicators(frm);
    },
    
    validate(frm) {
        validate_items(frm);
        validate_dates(frm);
    }
});

// Helper functions
function setup_queries(frm) {
    frm.set_query('customer', () => ({
        filters: { disabled: 0 }
    }));
}

function setup_buttons(frm) {
    if (frm.is_new()) return;
    
    frm.add_custom_button(__('Create Invoice'), () => {
        create_invoice(frm);
    }, __('Create'));
}

function validate_items(frm) {
    if (!frm.doc.items || !frm.doc.items.length) {
        frappe.throw(__('Please add at least one item'));
    }
}
```

---

## 7. BRONNEN

| Bron | URL | Toegang |
|------|-----|---------|
| Frappe Form API (v15) | https://docs.frappe.io/framework/v15/user/en/api/form | Januari 2026 |
| Frappe Client Script | https://docs.frappe.io/framework/v15/user/en/desk/scripting/client-script | Januari 2026 |
| Frappe JS Utilities | https://docs.frappe.io/framework/user/en/api/js-utils | Januari 2026 |
| Frappe GitHub Wiki | https://github.com/frappe/frappe/wiki/Client-Side-Scripting-Index | Januari 2026 |
| Vooronderzoek | erpnext-vooronderzoek.md sectie 1 | Project document |

---

## 8. VERSIE NOTITIES

| Aspect | v14 | v15 | Notitie |
|--------|-----|-----|---------|
| Class-based scripts | âŒ | âœ… (CRM only) | Nieuwe syntax voor Vue apps |
| frappe.ui.form.on | âœ… | âœ… | Standaard pattern |
| cur_frm | âœ… (deprecated) | âœ… (deprecated) | Vermijd, gebruik frm |
| Promise-based API | âœ… | âœ… | Alle async methods retourneren Promises |

---

*Document gegenereerd als onderdeel van ERPNext Skills Package - Fase 1.1*
