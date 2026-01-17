# Decision Tree: Client Script Events (EN)

## Complete Decision Tree

### Level 1: Client or Server?

```
WHERE SHOULD THE LOGIC RUN?
│
├─► Only when user opens/edits the form?
│   └── CLIENT SCRIPT
│
├─► Also on API calls, imports, Data Import Tool?
│   └── SERVER SCRIPT or CONTROLLER
│
├─► Critical business rule that must NEVER be skipped?
│   └── SERVER (controller validate/before_save)
│
└─► UX improvement (speed, feedback)?
    └── CLIENT SCRIPT (+ optional server backup)
```

### Level 2: Which Client Event?

```
WHAT IS THE GOAL?

INITIALIZATION
├─► One-time setup (link filters)?
│   └── setup
├─► UI initialization on form load?
│   └── onload
└─► Actions needed after complete render?
    └── onload_post_render

UI MANIPULATION  
├─► Add custom buttons?
│   └── refresh
├─► Show/hide fields?
│   └── refresh + {fieldname}
├─► Set indicator/intro text?
│   └── refresh
└─► Adjust form layout?
    └── refresh

DATA VALIDATION
├─► Sync validation (directly available data)?
│   └── validate
├─► Async validation (server check needed)?
│   └── validate (with await)
└─► Pre-submit check (before docstatus = 1)?
    └── before_submit

POST-SAVE ACTIONS
├─► UI update after save?
│   └── after_save
├─► Redirect to another document?
│   └── after_save
└─► Create next document?
    └── after_save or on_submit

FIELD CHANGES
├─► Respond to field change?
│   └── {fieldname}
├─► Cascading changes (A → B → C)?
│   └── {fieldname} (each link)
└─► Trigger calculation?
    └── {fieldname} (all input fields)

CHILD TABLE
├─► Row added?
│   └── {tablename}_add
├─► Row removed?
│   └── {tablename}_remove
├─► Field in row changed?
│   └── ChildDocType: {fieldname}
└─► Row reordered?
    └── {tablename}_move
```

## Event Combinations

### Pattern: Visibility Toggle

When: Field X determines whether field Y is visible.

```
REQUIRED EVENTS:
1. refresh      → Initial state on form load
2. {fieldname}  → Respond to change

IMPLEMENTATION:
refresh(frm) {
    frm.trigger('controlling_field');
}

controlling_field(frm) {
    frm.toggle_display('dependent_field', frm.doc.controlling_field);
}
```

### Pattern: Cascading Filters

When: Link B filtered based on selection in Link A.

```
REQUIRED EVENTS:
1. setup     → Set filter with dynamic value
2. {field_a} → Clear field_b on change

IMPLEMENTATION:
setup(frm) {
    frm.set_query('field_b', () => ({
        filters: { parent_field: frm.doc.field_a }
    }));
}

field_a(frm) {
    frm.set_value('field_b', '');
}
```

### Pattern: Calculated Fields

When: Field C = function of fields A and B.

```
REQUIRED EVENTS:
1. {field_a} → Recalculate on A change
2. {field_b} → Recalculate on B change

IMPLEMENTATION:
field_a(frm) { calculate(frm); }
field_b(frm) { calculate(frm); }

function calculate(frm) {
    frm.set_value('field_c', frm.doc.field_a + frm.doc.field_b);
}
```

### Pattern: Child Table Totals

When: Document total = sum of child row amounts.

```
REQUIRED EVENTS:
1. ChildDocType.qty      → Calculate row amount
2. ChildDocType.rate     → Calculate row amount  
3. ChildDocType.amount   → Calculate document total
4. ParentDocType.items_remove → Recalculate after removal

IMPLEMENTATION:
// Child events
frappe.ui.form.on('Invoice Item', {
    qty: calculate_row,
    rate: calculate_row,
    amount(frm) { calculate_totals(frm); }
});

// Parent event
frappe.ui.form.on('Invoice', {
    items_remove(frm) { calculate_totals(frm); }
});
```

## Event Timing Matrix

| Event | Timing | Can Stop Save? | Access to |
|-------|--------|----------------|-----------|
| setup | Once on first load | No | frm, doc (may be empty) |
| before_load | Before data load | No | frm |
| onload | After data load | No | frm, doc |
| refresh | After each render | No | frm, doc, full UI |
| onload_post_render | After complete render | No | frm, doc, DOM |
| validate | Before save | YES (throw) | frm, doc |
| before_save | Just before save | YES (throw) | frm, doc |
| after_save | After successful save | No | frm, doc (saved) |
| before_submit | Before submit | YES (throw) | frm, doc (docstatus=0) |
| on_submit | After submit | No | frm, doc (docstatus=1) |
| {fieldname} | On field change | No | frm, doc |

## Quick Reference: Common Scenarios

| I want to... | Event(s) |
|--------------|----------|
| Filter link field | `setup` |
| Add button | `refresh` |
| Hide field on condition | `refresh` + `{fieldname}` |
| Calculate value | `{input_fields}` |
| Validate before save | `validate` |
| Server check before save | `validate` (async) |
| Redirect after save | `after_save` |
| Calculate child table total | Child `{fieldname}` events |
| Set default value | `onload` (check is_new) |
