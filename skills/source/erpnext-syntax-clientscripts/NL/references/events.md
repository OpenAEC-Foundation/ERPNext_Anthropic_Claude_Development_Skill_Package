# Client Script Events (NL)

## Form-Level Events

Alle form-level events ontvangen `frm` als eerste parameter.

### Event Execution Order

**Bij form laden:**
```
setup → onload → refresh → onload_post_render
```

**Bij opslaan (nieuw document):**
```
validate → before_save → [server save] → after_save
```

**Bij opslaan (bestaand document):**
```
validate → before_save → [server save] → after_save
```

**Bij submit:**
```
validate → before_submit → [server submit] → on_submit
```

**Bij cancel:**
```
before_cancel → [server cancel] → after_cancel
```

## Complete Event Referentie

| Event | Trigger Moment | Typisch Gebruik |
|-------|----------------|-----------------|
| `setup` | Eenmalig bij eerste form creatie | `set_query`, default waarden |
| `onload` | Form is geladen, gaat renderen | Data pre-processing |
| `refresh` | Na form load en render | Buttons, UI, visibility |
| `onload_post_render` | Volledig geladen en gerenderd | DOM manipulatie |
| `validate` | Voor save | Validatie, `frappe.throw()` |
| `before_save` | Net voor save call | Last-minute wijzigingen |
| `after_save` | Na succesvolle save | Notificaties, cleanup |
| `before_submit` | Voor document submit | Pre-submit checks |
| `on_submit` | Na document submit | Post-submit acties |
| `before_cancel` | Voor cancellation | Pre-cancel checks |
| `after_cancel` | Na cancellation | Post-cancel cleanup |
| `timeline_refresh` | Na timeline render | Timeline customization |
| `before_workflow_action` | Voor workflow state change | Workflow interceptie |
| `after_workflow_action` | Na workflow state change | Workflow post-processing |

## Field Change Events

Reageren op waarde wijziging van specifiek veld:

```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        // Triggered wanneer 'customer' veld verandert
        if (frm.doc.customer) {
            // Fetch gerelateerde data
        }
    },
    
    posting_date(frm) {
        // Triggered wanneer 'posting_date' verandert
    }
});
```

## Event Parameters

### Form Events

```javascript
frappe.ui.form.on('DocType', {
    event_name(frm) {
        // frm = form object
        // frm.doc = document data
        // frm.doctype = doctype naam
        // frm.is_new() = true als nieuw document
    }
});
```

### Child Table Events

```javascript
frappe.ui.form.on('Child DocType', {
    fieldname(frm, cdt, cdn) {
        // frm = parent form object
        // cdt = child doctype naam
        // cdn = child row name (ID)
        let row = frappe.get_doc(cdt, cdn);
    },
    
    items_add(frm, cdt, cdn) {
        // Nieuwe rij toegevoegd
    },
    
    items_remove(frm) {
        // Rij verwijderd (geen cdt/cdn)
    },
    
    items_move(frm) {
        // Rij verplaatst (drag & drop)
    }
});
```

## Event Naming Conventies

### Child Table Events

Format: `{tablename}_{action}`

| Event | Beschrijving |
|-------|--------------|
| `{table}_add` | Rij toegevoegd |
| `{table}_remove` | Rij verwijderd |
| `{table}_move` | Rij verplaatst |
| `{table}_before_remove` | Voor rij verwijdering |

### Field Events

Gebruik exact de fieldname als event naam:

```javascript
frappe.ui.form.on('Sales Invoice', {
    // Field 'grand_total' change event
    grand_total(frm) { },
    
    // Field 'customer' change event
    customer(frm) { }
});
```

## Belangrijk: setup vs refresh

| Aspect | setup | refresh |
|--------|-------|---------|
| Frequentie | Eenmaal per form instantie | Bij elke refresh/reload |
| Gebruik | Filters, queries | Buttons, visibility |
| Timing | Vóór data laden | Ná data laden |

```javascript
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        // GOED: set_query hier
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));
    },
    
    refresh(frm) {
        // GOED: buttons hier
        frm.add_custom_button(__('Action'), () => {});
        
        // FOUT: set_query hier (werkt, maar inefficiënt)
    }
});
```

## Event Chaining en Return Values

### validate Event

```javascript
frappe.ui.form.on('Sales Order', {
    validate(frm) {
        // Return false of throw om save te voorkomen
        if (frm.doc.grand_total <= 0) {
            frappe.throw(__('Total must be positive'));
            // Of: return false;
        }
    }
});
```

### Promise Support

Moderne events ondersteunen async/await:

```javascript
frappe.ui.form.on('Sales Order', {
    async refresh(frm) {
        let data = await frappe.call({
            method: 'myapp.api.get_data',
            args: { name: frm.doc.name }
        });
        // Process data
    }
});
```
