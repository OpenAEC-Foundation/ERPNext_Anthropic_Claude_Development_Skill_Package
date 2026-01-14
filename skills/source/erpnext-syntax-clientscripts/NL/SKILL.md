---
name: erpnext-syntax-clientscripts
description: "Exacte JavaScript syntax voor ERPNext/Frappe Client Scripts. Gebruik wanneer je client-side code moet schrijven voor form events, veld manipulatie, server calls, of child table handling in ERPNext v14/v15. Triggers: client script, form event, frm methods, frappe.call, frappe.ui.form.on, JavaScript in ERPNext, browser-side code, UI interactie, veld validatie client-side."
---

# ERPNext Client Scripts Syntax (NL)

Client Scripts draaien in de browser en controleren alle UI interacties in ERPNext/Frappe. Ze worden gecreëerd via **Setup → Client Script** of in custom apps onder `public/js/`.

**Versie**: v14/v15 compatible (tenzij anders aangegeven)

## Quick Reference

### Basis Structuur

```javascript
frappe.ui.form.on('DocType Name', {
    // Form-level events
    setup(frm) { },
    refresh(frm) { },
    validate(frm) { },
    
    // Field change events
    fieldname(frm) { }
});
```

### Meest Gebruikte Patterns

| Actie | Code |
|-------|------|
| Waarde zetten | `frm.set_value('field', value)` |
| Veld verbergen | `frm.toggle_display('field', false)` |
| Veld verplicht maken | `frm.toggle_reqd('field', true)` |
| Server aanroepen | `frappe.call({method: 'path.to.method', args: {}})` |
| Save voorkomen | `frappe.throw('Error message')` |

## Event Selectie

Welk event moet ik gebruiken?

```
Eenmalige setup (queries, defaults)?
└── setup

UI tonen/verbergen, buttons toevoegen?
└── refresh

Validatie voor opslaan?
└── validate

Direct na opslaan iets doen?
└── after_save

Reageren op veld wijziging?
└── {fieldname}
```

→ Zie [references/events.md](references/events.md) voor complete event lijst en execution order.

## Essentiële Methods

### Waarden Manipuleren

```javascript
// Enkele waarde zetten (async, retourneert Promise)
frm.set_value('status', 'Approved');

// Meerdere waarden tegelijk
frm.set_value({
    status: 'Approved',
    priority: 'High'
});

// Waarde ophalen
let value = frm.doc.fieldname;
```

### Veld Properties

```javascript
// Tonen/verbergen
frm.toggle_display('priority', condition);

// Verplicht maken
frm.toggle_reqd('due_date', true);

// Read-only maken
frm.toggle_enable('amount', false);

// Geavanceerde property wijziging
frm.set_df_property('status', 'options', ['New', 'Open', 'Closed']);
frm.set_df_property('amount', 'read_only', 1);
```

### Link Field Filters

```javascript
// Simpele filter
frm.set_query('customer', () => ({
    filters: { disabled: 0 }
}));

// Filter in child table
frm.set_query('item_code', 'items', (doc, cdt, cdn) => ({
    filters: { is_sales_item: 1 }
}));
```

→ Zie [references/methods.md](references/methods.md) voor complete method signatures.

## Server Communicatie

### frappe.call (Whitelisted Methods)

```javascript
frappe.call({
    method: 'myapp.api.process_data',
    args: { customer: frm.doc.customer },
    freeze: true,
    freeze_message: __('Processing...'),
    callback: (r) => {
        if (r.message) {
            frm.set_value('result', r.message);
        }
    }
});
```

### frm.call (Document Methods)

```javascript
// Roept method op document controller aan
frm.call('calculate_taxes', { include_shipping: true })
    .then(r => frm.reload_doc());
```

### Async/Await Pattern

```javascript
async function fetchData(frm) {
    let r = await frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Customer',
            filters: { name: frm.doc.customer },
            fieldname: 'credit_limit'
        }
    });
    return r.message.credit_limit;
}
```

## Child Table Handling

### Rijen Toevoegen

```javascript
let row = frm.add_child('items', {
    item_code: 'ITEM-001',
    qty: 5,
    rate: 100
});
frm.refresh_field('items');  // VERPLICHT na wijziging
```

### Rijen Bewerken

```javascript
frm.doc.items.forEach((row) => {
    if (row.qty > 10) {
        row.discount_percentage = 5;
    }
});
frm.refresh_field('items');
```

### Child Table Events

```javascript
frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);
    },
    
    items_add(frm, cdt, cdn) {
        // Nieuwe rij toegevoegd
    },
    
    items_remove(frm) {
        // Rij verwijderd
    }
});
```

→ Zie [references/examples.md](references/examples.md) voor complete child table voorbeelden.

## Custom Buttons

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            // Gegroepeerde buttons
            frm.add_custom_button(__('Invoice'), () => {
                // action
            }, __('Create'));
            
            // Primary action
            frm.page.set_primary_action(__('Process'), () => {
                frm.call('process').then(() => frm.reload_doc());
            });
        }
    }
});
```

## Kritieke Regels

1. **ALTIJD** `frm.refresh_field('table')` aanroepen na child table wijzigingen
2. **NOOIT** `frm.doc.field = value` gebruiken — gebruik `frm.set_value()`
3. **ALTIJD** `__('text')` gebruiken voor vertaalbare strings
4. **validate** event: gebruik `frappe.throw()` om save te voorkomen
5. **setup** event: alleen voor eenmalige configuratie (wordt niet herhaald)

→ Zie [references/anti-patterns.md](references/anti-patterns.md) voor veelgemaakte fouten.

## Gerelateerde Skills

- `erpnext-impl-clientscripts` — Implementatie workflows en decision trees
- `erpnext-errors-clientscripts` — Error handling patterns
- `erpnext-syntax-whitelisted` — Server-side methods om aan te roepen
