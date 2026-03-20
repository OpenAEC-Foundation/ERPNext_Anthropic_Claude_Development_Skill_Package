# Client Script Methods (EN)

## frm.* Methods

### Value Manipulation

#### frm.set_value(fieldname, value)
Sets the value of a field. Async, returns Promise.

```javascript
// Signature
frm.set_value(fieldname: string, value: any): Promise

// Single value
frm.set_value('status', 'Approved');

// Multiple values
frm.set_value({
    status: 'Approved',
    priority: 'High',
    due_date: frappe.datetime.add_days(frappe.datetime.now_date(), 7)
});

// With Promise handling
frm.set_value('status', 'Approved').then(() => {
    console.log('Value set successfully');
});
```

#### frm.doc.fieldname
Direct access to field value (read-only pattern).

```javascript
let customer = frm.doc.customer;
let items = frm.doc.items;  // Array for child tables
```

### Field Display Properties

#### frm.toggle_display(fieldname, show)
Shows or hides a field.

```javascript
// Signature
frm.toggle_display(fieldname: string | string[], show: boolean): void

// Single field
frm.toggle_display('priority', frm.doc.status === 'Open');

// Multiple fields
frm.toggle_display(['priority', 'due_date'], frm.doc.status === 'Open');
```

#### frm.toggle_reqd(fieldname, required)
Makes field mandatory or optional.

```javascript
// Signature
frm.toggle_reqd(fieldname: string | string[], required: boolean): void

frm.toggle_reqd('due_date', true);
frm.toggle_reqd(['email', 'phone'], frm.doc.customer_type === 'Company');
```

#### frm.toggle_enable(fieldname, enable)
Makes field editable or read-only.

```javascript
// Signature
frm.toggle_enable(fieldname: string | string[], enable: boolean): void

frm.toggle_enable('amount', false);  // Read-only
frm.toggle_enable('amount', true);   // Editable
```

#### frm.set_df_property(fieldname, property, value)
Sets arbitrary field property.

```javascript
// Signature
frm.set_df_property(fieldname: string, property: string, value: any): void

// Available properties
frm.set_df_property('status', 'options', ['New', 'Open', 'Closed']);
frm.set_df_property('amount', 'read_only', 1);
frm.set_df_property('description', 'hidden', 1);
frm.set_df_property('priority', 'reqd', 1);
frm.set_df_property('rate', 'precision', 4);
frm.set_df_property('notes', 'label', 'Internal Notes');
```

### Link Field Queries

#### frm.set_query(fieldname, [tablename], query_function)
Filters options in Link fields.

```javascript
// Signature (form level)
frm.set_query(fieldname: string, query_function: Function): void

// Signature (child table)
frm.set_query(fieldname: string, tablename: string, query_function: Function): void

// Simple filter
frm.set_query('customer', () => ({
    filters: { disabled: 0, customer_type: 'Company' }
}));

// With document context
frm.set_query('customer', () => ({
    filters: { territory: frm.doc.territory }
}));

// In child table
frm.set_query('item_code', 'items', (doc, cdt, cdn) => {
    let row = locals[cdt][cdn];
    return {
        filters: { 
            is_sales_item: 1,
            item_group: row.item_group || undefined
        }
    };
});

// Server-side query
frm.set_query('customer', () => ({
    query: 'myapp.queries.get_customers_by_region',
    filters: { region: frm.doc.region }
}));
```

### Child Table Methods

#### frm.add_child(tablename, values)
Adds row to child table.

```javascript
// Signature
frm.add_child(tablename: string, values?: object): object

let row = frm.add_child('items', {
    item_code: 'ITEM-001',
    qty: 5,
    rate: 100
});
frm.refresh_field('items');  // REQUIRED
```

#### frm.clear_table(tablename)
Removes all rows from child table.

```javascript
// Signature
frm.clear_table(tablename: string): void

frm.clear_table('items');
frm.refresh_field('items');  // REQUIRED
```

#### frm.refresh_field(fieldname)
Redraws field in UI. **Required after child table modifications.**

```javascript
// Signature
frm.refresh_field(fieldname: string): void

frm.refresh_field('items');
frm.refresh_field('grand_total');
```

### Custom Buttons

#### frm.add_custom_button(label, action, [group])
Adds custom button.

```javascript
// Signature
frm.add_custom_button(label: string, action: Function, group?: string): jQuery

// Standalone button
frm.add_custom_button(__('Generate Report'), () => {
    frappe.call({
        method: 'myapp.api.generate_report',
        args: { name: frm.doc.name }
    });
});

// Grouped button (dropdown)
frm.add_custom_button(__('Sales Invoice'), () => {
    // Create invoice
}, __('Create'));

frm.add_custom_button(__('Delivery Note'), () => {
    // Create delivery note
}, __('Create'));
```

#### frm.remove_custom_button(label, [group])
Removes custom button.

```javascript
// Signature
frm.remove_custom_button(label: string, group?: string): void

frm.remove_custom_button(__('Generate Report'));
frm.remove_custom_button(__('Sales Invoice'), __('Create'));
```

#### frm.page.set_primary_action(label, action)
Sets primary action button.

```javascript
// Signature
frm.page.set_primary_action(label: string, action: Function): void

frm.page.set_primary_action(__('Submit'), () => {
    frm.call('custom_submit').then(() => frm.reload_doc());
});
```

### Utility Methods

#### frm.is_new()
Checks if document is new (not yet saved).

```javascript
// Signature
frm.is_new(): boolean

if (frm.is_new()) {
    frm.set_value('status', 'Draft');
}
```

#### frm.reload_doc()
Reloads document from server.

```javascript
// Signature
frm.reload_doc(): Promise

await frm.reload_doc();
```

#### frm.call(method, args)
Calls method on document controller.

```javascript
// Signature
frm.call(method: string, args?: object): Promise

frm.call('calculate_taxes', { include_shipping: true })
    .then(r => {
        console.log(r.message);
    });
```

#### frm.save()
Saves document.

```javascript
// Signature
frm.save(callback?: Function): Promise

frm.save().then(() => {
    frappe.show_alert('Saved!');
});
```

#### frm.enable_save() / frm.disable_save()
Enables/disables save button.

```javascript
frm.disable_save();  // Prevents saving
frm.enable_save();   // Allows saving
```

---

## frappe.* Client Methods

### Server Communication

#### frappe.call(options)
Calls whitelisted Python method.

```javascript
// Signature
frappe.call({
    method: string,           // Full method path
    args?: object,            // Arguments
    callback?: Function,      // Success callback
    error?: Function,         // Error callback
    async?: boolean,          // Default: true
    freeze?: boolean,         // Show loading indicator
    freeze_message?: string,  // Custom loading message
    btn?: jQuery              // Button to disable
}): Promise

// Example
frappe.call({
    method: 'myapp.api.get_customer_data',
    args: {
        customer: frm.doc.customer,
        include_orders: true
    },
    freeze: true,
    freeze_message: __('Loading customer data...'),
    callback: (r) => {
        if (r.message) {
            console.log(r.message);
        }
    },
    error: (r) => {
        frappe.msgprint(__('Error loading data'));
    }
});
```

#### frappe.db.get_value(doctype, name, fieldname)
Gets field value from server.

```javascript
// Signature
frappe.db.get_value(
    doctype: string,
    name: string | object,  // Name or filters
    fieldname: string | string[]
): Promise

// Single field
frappe.db.get_value('Customer', frm.doc.customer, 'credit_limit')
    .then(r => {
        console.log(r.message.credit_limit);
    });

// Multiple fields
frappe.db.get_value('Customer', frm.doc.customer, ['credit_limit', 'territory'])
    .then(r => {
        console.log(r.message.credit_limit);
        console.log(r.message.territory);
    });

// With filters
frappe.db.get_value('Customer', {customer_name: 'Test'}, 'name')
    .then(r => {
        console.log(r.message.name);
    });
```

#### frappe.db.get_list(doctype, args)
Gets list of documents.

```javascript
// Signature
frappe.db.get_list(doctype: string, args: object): Promise

frappe.db.get_list('Sales Order', {
    filters: { customer: frm.doc.customer },
    fields: ['name', 'grand_total', 'status'],
    order_by: 'creation desc',
    limit: 10
}).then(orders => {
    console.log(orders);
});
```

### User Interface

#### frappe.msgprint(message, [title])
Shows message dialog.

```javascript
// Signature
frappe.msgprint(message: string | object, title?: string): void

frappe.msgprint(__('Operation completed'));
frappe.msgprint({
    title: __('Success'),
    message: __('Invoice created'),
    indicator: 'green'
});
```

#### frappe.throw(message)
Shows error and stops execution.

```javascript
// Signature
frappe.throw(message: string): never

if (frm.doc.amount < 0) {
    frappe.throw(__('Amount cannot be negative'));
}
```

#### frappe.show_alert(message, [seconds])
Shows temporary notification.

```javascript
// Signature
frappe.show_alert(message: string | object, seconds?: number): void

frappe.show_alert(__('Saved!'), 3);
frappe.show_alert({
    message: __('Order processed'),
    indicator: 'green'
}, 5);
```

#### frappe.confirm(message, if_yes, if_no)
Shows confirmation dialog.

```javascript
// Signature
frappe.confirm(message: string, if_yes: Function, if_no?: Function): void

frappe.confirm(
    __('Are you sure you want to delete?'),
    () => {
        // User clicked Yes
        frm.call('delete_items');
    },
    () => {
        // User clicked No
    }
);
```

### Child Table Utilities

#### frappe.get_doc(cdt, cdn)
Gets child row data.

```javascript
// Signature
frappe.get_doc(cdt: string, cdn: string): object

frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        console.log(row.qty, row.rate);
    }
});
```

#### frappe.model.set_value(cdt, cdn, fieldname, value)
Sets value in child row.

```javascript
// Signature
frappe.model.set_value(cdt: string, cdn: string, fieldname: string, value: any): Promise

frappe.ui.form.on('Sales Invoice Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);
    }
});
```

### Translation

#### __(message)
Translates string.

```javascript
// Signature
__(message: string, replace?: object | string[], context?: string): string

frappe.msgprint(__('Hello World'));
frappe.msgprint(__('Hello {0}', [user_name]));
frappe.msgprint(__('Total: {0}', [frm.doc.grand_total]));
```

### Date/Time Utilities

```javascript
// Current date (YYYY-MM-DD)
frappe.datetime.now_date()

// Current datetime
frappe.datetime.now_datetime()

// Add days
frappe.datetime.add_days('2024-01-01', 7)  // '2024-01-08'

// Add months
frappe.datetime.add_months('2024-01-01', 1)  // '2024-02-01'

// Format date
frappe.datetime.str_to_user('2024-01-15')  // To user format

// Compare
frappe.datetime.get_diff(date1, date2)  // Difference in days
```
