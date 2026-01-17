# Decision Tree: Client Script Events (NL)

## Complete Beslisboom

### Niveau 1: Client of Server?

```
WAAR MOET DE LOGICA DRAAIEN?
│
├─► Alleen wanneer gebruiker het form opent/bewerkt?
│   └── CLIENT SCRIPT
│
├─► Ook bij API calls, imports, Data Import Tool?
│   └── SERVER SCRIPT of CONTROLLER
│
├─► Kritieke business rule die NOOIT overgeslagen mag worden?
│   └── SERVER (controller validate/before_save)
│
└─► UX verbetering (snelheid, feedback)?
    └── CLIENT SCRIPT (+ optioneel server backup)
```

### Niveau 2: Welk Client Event?

```
WAT IS HET DOEL?

INITIALISATIE
├─► Eenmalige setup (link filters)?
│   └── setup
├─► UI initialisatie bij form load?
│   └── onload
└─► Na volledige render acties nodig?
    └── onload_post_render

UI MANIPULATIE  
├─► Custom buttons toevoegen?
│   └── refresh
├─► Velden tonen/verbergen?
│   └── refresh + {fieldname}
├─► Indicator/intro tekst zetten?
│   └── refresh
└─► Form layout aanpassen?
    └── refresh

DATA VALIDATIE
├─► Sync validatie (direct beschikbare data)?
│   └── validate
├─► Async validatie (server check nodig)?
│   └── validate (met await)
└─► Pre-submit check (voor docstatus = 1)?
    └── before_submit

POST-SAVE ACTIES
├─► UI update na save?
│   └── after_save
├─► Redirect naar ander document?
│   └── after_save
└─► Volgend document aanmaken?
    └── after_save of on_submit

VELD WIJZIGINGEN
├─► Reageren op veld change?
│   └── {fieldname}
├─► Cascading wijzigingen (A → B → C)?
│   └── {fieldname} (elke schakel)
└─► Berekening triggeren?
    └── {fieldname} (alle input velden)

CHILD TABLE
├─► Rij toegevoegd?
│   └── {tablename}_add
├─► Rij verwijderd?
│   └── {tablename}_remove
├─► Veld in rij gewijzigd?
│   └── ChildDocType: {fieldname}
└─► Rij herschikt?
    └── {tablename}_move
```

## Event Combinaties

### Pattern: Visibility Toggle

Wanneer: Veld X bepaalt of veld Y zichtbaar is.

```
VEREISTE EVENTS:
1. refresh      → Initiële staat bij form load
2. {fieldname}  → Reageer op wijziging

IMPLEMENTATIE:
refresh(frm) {
    frm.trigger('controlling_field');
}

controlling_field(frm) {
    frm.toggle_display('dependent_field', frm.doc.controlling_field);
}
```

### Pattern: Cascading Filters

Wanneer: Link B gefilterd op selectie in Link A.

```
VEREISTE EVENTS:
1. setup     → Zet filter met dynamische waarde
2. {field_a} → Clear field_b bij wijziging

IMPLEMENTATIE:
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

Wanneer: Veld C = functie van velden A en B.

```
VEREISTE EVENTS:
1. {field_a} → Herbereken bij A wijziging
2. {field_b} → Herbereken bij B wijziging

IMPLEMENTATIE:
field_a(frm) { calculate(frm); }
field_b(frm) { calculate(frm); }

function calculate(frm) {
    frm.set_value('field_c', frm.doc.field_a + frm.doc.field_b);
}
```

### Pattern: Child Table Totalen

Wanneer: Document totaal = som van child rij bedragen.

```
VEREISTE EVENTS:
1. ChildDocType.qty      → Bereken rij amount
2. ChildDocType.rate     → Bereken rij amount  
3. ChildDocType.amount   → Bereken document totaal
4. ParentDocType.items_remove → Herbereken na verwijdering

IMPLEMENTATIE:
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

| Event | Timing | Kan Save Stoppen? | Toegang tot |
|-------|--------|-------------------|-------------|
| setup | Eenmalig bij eerste load | Nee | frm, doc (kan leeg zijn) |
| before_load | Voor data load | Nee | frm |
| onload | Na data load | Nee | frm, doc |
| refresh | Na elke render | Nee | frm, doc, volledige UI |
| onload_post_render | Na complete render | Nee | frm, doc, DOM |
| validate | Voor save | JA (throw) | frm, doc |
| before_save | Net voor save | JA (throw) | frm, doc |
| after_save | Na succesvolle save | Nee | frm, doc (opgeslagen) |
| before_submit | Voor submit | JA (throw) | frm, doc (docstatus=0) |
| on_submit | Na submit | Nee | frm, doc (docstatus=1) |
| {fieldname} | Bij veld wijziging | Nee | frm, doc |

## Quick Reference: Veelvoorkomende Scenarios

| Ik wil... | Event(s) |
|-----------|----------|
| Link field filteren | `setup` |
| Button toevoegen | `refresh` |
| Veld verbergen op conditie | `refresh` + `{fieldname}` |
| Waarde berekenen | `{input_fields}` |
| Valideren voor save | `validate` |
| Server check voor save | `validate` (async) |
| Redirect na save | `after_save` |
| Child table totaal berekenen | Child `{fieldname}` events |
| Standaard waarde zetten | `onload` (check is_new) |
