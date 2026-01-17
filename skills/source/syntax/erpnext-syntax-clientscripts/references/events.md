# Client Script Events (EN)

## Form-Level Events

All form-level events receive `frm` as the first parameter.

### Event Execution Order

**On form load:**
```
setup → onload → refresh → onload_post_render
```

**On save (new document):**
```
validate → before_save → [server save] → after_save
```

**On save (existing document):**
```
validate → before_save → [server save] → after_save
```

**On submit:**
```
validate → before_submit → [server submit] → on_submit
```

**On cancel:**
```
before_cancel → [server cancel] → after_cancel
```

## Complete Event Reference

| Event | Trigger Moment | Typical Usage |
|-------|----------------|---------------|
| `setup` | Once per form instance creation | `set_query`, default values |
| `onload` | Form is loaded, about to render | Data pre-processing |
| `refresh` | After form load and render | Buttons, UI, visibility |
| `onload_post_render` | Fully loaded and rendered | DOM manipulation |
| `validate` | Before save | Validation, `frappe.throw()` |
| `before_save` | Just before save call | Last-minute changes |
| `after_save` | After successful save | Notifications, cleanup |
| `before_submit` | Before document submit | Pre-submit checks |
| `on_submit` | After document submit | Post-submit actions |
| `before_cancel` | Before cancellation | Pre-cancel checks |
| `after_cancel` | After cancellation | Post-cancel cleanup |
| `timeline_refresh` | After timeline render | Timeline customization |
| `before_workflow_action` | Before workflow state change | Workflow interception |
| `after_workflow_action` | After workflow state change | Workflow post-processing |

## Field Change Events

React to value change of a specific field:

```javascript
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        // Triggered when 'customer' field changes
        if (frm.doc.customer) {
            // Fetch related data
        }
    },
    
    posting_date(frm) {
        // Triggered when 'posting_date' changes
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
        // frm.doctype = doctype name
        // frm.is_new() = true if new document
    }
});
```

### Child Table Events

```javascript
frappe.ui.form.on('Child DocType', {
    fieldname(frm, cdt, cdn) {
        // frm = parent form object
        // cdt = child doctype name
        // cdn = child row name (ID)
        let row = frappe.get_doc(cdt, cdn);
    },
    
    items_add(frm, cdt, cdn) {
        // New row added
    },
    
    items_remove(frm) {
        // Row removed (no cdt/cdn)
    },
    
    items_move(frm) {
        // Row moved (drag & drop)
    }
});
```

## Event Naming Conventions

### Child Table Events

Format: `{tablename}_{action}`

| Event | Description |
|-------|-------------|
| `{table}_add` | Row added |
| `{table}_remove` | Row removed |
| `{table}_move` | Row moved |
| `{table}_before_remove` | Before row removal |

### Field Events

Use the exact fieldname as event name:

```javascript
frappe.ui.form.on('Sales Invoice', {
    // Field 'grand_total' change event
    grand_total(frm) { },
    
    // Field 'customer' change event
    customer(frm) { }
});
```

## Important: setup vs refresh

| Aspect | setup | refresh |
|--------|-------|---------|
| Frequency | Once per form instance | On every refresh/reload |
| Usage | Filters, queries | Buttons, visibility |
| Timing | Before data load | After data load |

```javascript
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        // GOOD: set_query here
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));
    },
    
    refresh(frm) {
        // GOOD: buttons here
        frm.add_custom_button(__('Action'), () => {});
        
        // BAD: set_query here (works, but inefficient)
    }
});
```

## Event Chaining and Return Values

### validate Event

```javascript
frappe.ui.form.on('Sales Order', {
    validate(frm) {
        // Return false or throw to prevent save
        if (frm.doc.grand_total <= 0) {
            frappe.throw(__('Total must be positive'));
            // Or: return false;
        }
    }
});
```

### Promise Support

Modern events support async/await:

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
