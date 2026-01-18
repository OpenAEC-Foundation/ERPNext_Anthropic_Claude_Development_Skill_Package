# Error Handling Patterns - Client Scripts

Complete error handling patterns for Frappe/ERPNext Client Scripts.

---

## Pattern 1: Comprehensive Form Validation

```javascript
frappe.ui.form.on('Sales Order', {
    validate(frm) {
        const validator = new FormValidator(frm);
        
        // Header validations
        validator.require('customer', __('Customer'));
        validator.require('delivery_date', __('Delivery Date'));
        validator.dateNotPast('delivery_date', __('Delivery Date'));
        
        // Amount validations
        validator.positive('grand_total', __('Total'));
        validator.max('discount_percentage', 50, __('Discount'));
        
        // Child table validations
        validator.requireChildTable('items', __('Items'));
        validator.validateChildRows('items', (row, idx) => {
            if (!row.item_code) {
                return __('Row {0}: Item is required', [idx]);
            }
            if (row.qty <= 0) {
                return __('Row {0}: Quantity must be positive', [idx]);
            }
            return null;
        });
        
        // Throw all errors
        validator.throwIfErrors();
    }
});

/**
 * Reusable Form Validator Class
 */
class FormValidator {
    constructor(frm) {
        this.frm = frm;
        this.errors = [];
    }
    
    require(field, label) {
        if (!this.frm.doc[field]) {
            this.errors.push(__(`${label} is required`));
        }
    }
    
    positive(field, label) {
        if (this.frm.doc[field] <= 0) {
            this.errors.push(__(`${label} must be greater than zero`));
        }
    }
    
    max(field, maxVal, label) {
        if (this.frm.doc[field] > maxVal) {
            this.errors.push(__(`${label} cannot exceed ${maxVal}`));
        }
    }
    
    dateNotPast(field, label) {
        if (this.frm.doc[field] && this.frm.doc[field] < frappe.datetime.get_today()) {
            this.errors.push(__(`${label} cannot be in the past`));
        }
    }
    
    requireChildTable(table, label) {
        if (!this.frm.doc[table] || this.frm.doc[table].length === 0) {
            this.errors.push(__(`At least one ${label} row is required`));
        }
    }
    
    validateChildRows(table, validateFn) {
        (this.frm.doc[table] || []).forEach((row, idx) => {
            const error = validateFn(row, idx + 1);
            if (error) this.errors.push(error);
        });
    }
    
    throwIfErrors() {
        if (this.errors.length > 0) {
            frappe.throw({
                title: __('Please fix the following errors'),
                message: this.errors.join('<br>')
            });
        }
    }
}
```

---

## Pattern 2: Async Operation with Retry

```javascript
/**
 * Fetch data with automatic retry on failure
 */
async function fetchWithRetry(method, args, maxRetries = 3) {
    let lastError;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const r = await frappe.call({ method, args });
            return r.message;
        } catch (error) {
            lastError = error;
            console.warn(`Attempt ${attempt} failed:`, error);
            
            if (attempt < maxRetries) {
                // Wait before retry (exponential backoff)
                await new Promise(resolve => 
                    setTimeout(resolve, Math.pow(2, attempt) * 1000)
                );
            }
        }
    }
    
    throw lastError;
}

// Usage in form event
frappe.ui.form.on('Sales Order', {
    async customer(frm) {
        if (!frm.doc.customer) return;
        
        try {
            frm.dashboard.set_headline(__('Loading customer data...'), 'blue');
            
            const data = await fetchWithRetry(
                'myapp.api.get_customer_details',
                { customer: frm.doc.customer }
            );
            
            frm.set_value('credit_limit', data.credit_limit);
            frm.dashboard.set_headline('');
            
        } catch (error) {
            console.error('Failed after retries:', error);
            frm.dashboard.set_headline(
                __('Could not load customer data'),
                'orange'
            );
            frappe.show_alert({
                message: __('Customer data unavailable. You can still proceed.'),
                indicator: 'orange'
            }, 5);
        }
    }
});
```

---

## Pattern 3: Batch Operation Error Handling

```javascript
frappe.ui.form.on('Bulk Processor', {
    async process_items(frm) {
        const items = frm.doc.items || [];
        const results = { success: 0, failed: 0, errors: [] };
        
        // Show progress
        frappe.show_progress(
            __('Processing Items'),
            0,
            items.length,
            __('Starting...')
        );
        
        for (let i = 0; i < items.length; i++) {
            const item = items[i];
            
            try {
                await frappe.call({
                    method: 'myapp.api.process_item',
                    args: { item_code: item.item_code }
                });
                results.success++;
                
            } catch (error) {
                results.failed++;
                results.errors.push({
                    row: i + 1,
                    item: item.item_code,
                    error: error.message || __('Unknown error')
                });
            }
            
            // Update progress
            frappe.show_progress(
                __('Processing Items'),
                i + 1,
                items.length,
                __('Processing {0}', [item.item_code])
            );
        }
        
        frappe.hide_progress();
        
        // Show results
        if (results.failed === 0) {
            frappe.msgprint({
                title: __('Success'),
                message: __('All {0} items processed successfully', [results.success]),
                indicator: 'green'
            });
        } else {
            let errorDetails = results.errors.map(e => 
                __('Row {0} ({1}): {2}', [e.row, e.item, e.error])
            ).join('<br>');
            
            frappe.msgprint({
                title: __('Completed with Errors'),
                message: `
                    <p>${__('Processed: {0} success, {1} failed', [results.success, results.failed])}</p>
                    <hr>
                    <p><strong>${__('Errors')}:</strong></p>
                    <p>${errorDetails}</p>
                `,
                indicator: 'orange'
            });
        }
    }
});
```

---

## Pattern 4: Confirmation Before Destructive Action

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Cancel Order'), () => {
                confirmAndCancel(frm);
            }, __('Actions'));
        }
    }
});

async function confirmAndCancel(frm) {
    // First confirmation
    const confirmed = await new Promise(resolve => {
        frappe.confirm(
            __('Are you sure you want to cancel this order?'),
            () => resolve(true),
            () => resolve(false)
        );
    });
    
    if (!confirmed) return;
    
    // Check for dependencies
    try {
        const deps = await frappe.call({
            method: 'myapp.api.check_cancel_dependencies',
            args: { order: frm.doc.name }
        });
        
        if (deps.message && deps.message.has_dependencies) {
            // Second confirmation with warning
            const forceConfirmed = await new Promise(resolve => {
                frappe.confirm(
                    __('This order has linked documents ({0}). Cancel anyway?', 
                        [deps.message.count]),
                    () => resolve(true),
                    () => resolve(false)
                );
            });
            
            if (!forceConfirmed) return;
        }
        
        // Proceed with cancellation
        await frappe.call({
            method: 'frappe.client.cancel',
            args: { doctype: frm.doctype, name: frm.doc.name },
            freeze: true,
            freeze_message: __('Cancelling...')
        });
        
        frappe.show_alert({
            message: __('Order cancelled'),
            indicator: 'green'
        });
        frm.reload_doc();
        
    } catch (error) {
        console.error('Cancel failed:', error);
        frappe.msgprint({
            title: __('Cannot Cancel'),
            message: error.message || __('Cancellation failed. Please try again.'),
            indicator: 'red'
        });
    }
}
```

---

## Pattern 5: Network Error Detection

```javascript
/**
 * Detect and handle network errors
 */
async function safeServerCall(options) {
    try {
        return await frappe.call(options);
    } catch (error) {
        // Check for network error
        if (!navigator.onLine) {
            frappe.msgprint({
                title: __('No Internet Connection'),
                message: __('Please check your internet connection and try again.'),
                indicator: 'red'
            });
            throw new Error('NETWORK_OFFLINE');
        }
        
        // Check for timeout
        if (error.message && error.message.includes('timeout')) {
            frappe.msgprint({
                title: __('Request Timeout'),
                message: __('The server is taking too long to respond. Please try again.'),
                indicator: 'orange'
            });
            throw new Error('NETWORK_TIMEOUT');
        }
        
        // Check for server error (5xx)
        if (error.status >= 500) {
            frappe.msgprint({
                title: __('Server Error'),
                message: __('The server encountered an error. Please try again later.'),
                indicator: 'red'
            });
            throw new Error('SERVER_ERROR');
        }
        
        // Re-throw for other errors
        throw error;
    }
}

// Usage
frappe.ui.form.on('Sales Order', {
    async validate(frm) {
        try {
            await safeServerCall({
                method: 'myapp.api.validate_order',
                args: { name: frm.doc.name }
            });
        } catch (error) {
            if (error.message === 'NETWORK_OFFLINE') {
                frappe.throw(__('Cannot validate: No internet connection'));
            } else if (error.message === 'SERVER_ERROR') {
                frappe.throw(__('Cannot validate: Server error'));
            }
            throw error;
        }
    }
});
```

---

## Pattern 6: Dependent Field Validation

```javascript
frappe.ui.form.on('Purchase Order', {
    validate(frm) {
        // Validate shipping address only if requires_shipping is checked
        if (frm.doc.requires_shipping) {
            if (!frm.doc.shipping_address) {
                frappe.throw(__('Shipping Address is required when shipping is enabled'));
            }
        }
        
        // Validate payment terms only if not prepaid
        if (frm.doc.payment_type !== 'Prepaid') {
            if (!frm.doc.payment_terms_template) {
                frappe.throw(__('Payment Terms are required for non-prepaid orders'));
            }
            if (frm.doc.credit_days <= 0) {
                frappe.throw(__('Credit Days must be set for credit purchases'));
            }
        }
        
        // Cross-field validation
        if (frm.doc.delivery_date && frm.doc.expected_arrival_date) {
            if (frm.doc.expected_arrival_date < frm.doc.delivery_date) {
                frappe.throw(__('Expected Arrival cannot be before Delivery Date'));
            }
        }
    }
});
```

---

## Pattern 7: Async Field Change with Loading State

```javascript
frappe.ui.form.on('Quotation', {
    async item_code(frm) {
        if (!frm.doc.item_code) return;
        
        // Show loading state
        frm.set_df_property('rate', 'read_only', 1);
        frm.set_df_property('rate', 'description', __('Loading price...'));
        
        try {
            const r = await frappe.call({
                method: 'myapp.api.get_item_price',
                args: { 
                    item_code: frm.doc.item_code,
                    customer: frm.doc.customer
                }
            });
            
            if (r.message) {
                await frm.set_value('rate', r.message.rate);
                frm.set_df_property('rate', 'description', 
                    __('Price as of {0}', [r.message.price_date]));
            } else {
                frm.set_df_property('rate', 'description', 
                    __('No price found - please enter manually'));
            }
            
        } catch (error) {
            console.error('Price lookup failed:', error);
            frm.set_df_property('rate', 'description', 
                __('Could not load price - please enter manually'));
            frappe.show_alert({
                message: __('Price lookup failed'),
                indicator: 'orange'
            }, 3);
            
        } finally {
            // Always restore editable state
            frm.set_df_property('rate', 'read_only', 0);
        }
    }
});
```

---

## Pattern 8: Global Error Handler

```javascript
/**
 * Install global error handler for uncaught errors
 * Put this in your app's main JS file
 */
(function() {
    // Handle uncaught Promise rejections
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled Promise rejection:', event.reason);
        
        // Don't show alert for every Promise rejection
        // Only log for debugging
        if (frappe.boot.developer_mode) {
            frappe.show_alert({
                message: __('Async Error: ') + (event.reason?.message || 'Unknown'),
                indicator: 'red'
            }, 5);
        }
    });
    
    // Handle general JS errors
    window.addEventListener('error', (event) => {
        console.error('JavaScript Error:', event.error);
        
        if (frappe.boot.developer_mode) {
            frappe.show_alert({
                message: __('JS Error: ') + event.message,
                indicator: 'red'
            }, 5);
        }
    });
})();
```

---

## Pattern 9: Validation with Dependencies Check

```javascript
frappe.ui.form.on('Project', {
    async validate(frm) {
        // Run all validations in parallel
        const validations = await Promise.allSettled([
            validateBudget(frm),
            validateTeam(frm),
            validateSchedule(frm)
        ]);
        
        // Collect errors from failed validations
        const errors = validations
            .filter(v => v.status === 'rejected')
            .map(v => v.reason);
        
        if (errors.length > 0) {
            frappe.throw({
                title: __('Validation Errors'),
                message: errors.join('<br>')
            });
        }
    }
});

async function validateBudget(frm) {
    if (frm.doc.budget_allocated) {
        const spent = await frappe.db.get_value('Project Expense', 
            { project: frm.doc.name }, 
            'sum(amount) as total'
        );
        
        if (spent.message?.total > frm.doc.budget_allocated) {
            throw __('Expenses ({0}) exceed budget ({1})', 
                [spent.message.total, frm.doc.budget_allocated]);
        }
    }
}

async function validateTeam(frm) {
    if (!frm.doc.project_manager) {
        throw __('Project Manager is required');
    }
}

async function validateSchedule(frm) {
    if (frm.doc.end_date && frm.doc.start_date) {
        if (frm.doc.end_date <= frm.doc.start_date) {
            throw __('End Date must be after Start Date');
        }
    }
}
```

---

## Pattern 10: Error Boundary for Custom Buttons

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // Wrap button actions in error boundary
        frm.add_custom_button(__('Generate Invoice'), () => {
            withErrorBoundary(frm, 'generate_invoice', async () => {
                await frm.call('create_invoice');
                frappe.show_alert({
                    message: __('Invoice created'),
                    indicator: 'green'
                });
                frm.reload_doc();
            });
        });
    }
});

/**
 * Wrap async action with consistent error handling
 */
async function withErrorBoundary(frm, actionName, asyncFn) {
    try {
        frappe.show_progress(__('Processing'), 0, 100);
        await asyncFn();
        frappe.hide_progress();
        
    } catch (error) {
        frappe.hide_progress();
        console.error(`Action '${actionName}' failed:`, error);
        
        // Parse server error message if available
        let userMessage = __('Operation failed. Please try again.');
        if (error._server_messages) {
            try {
                const msgs = JSON.parse(error._server_messages);
                userMessage = msgs.map(m => JSON.parse(m).message).join('<br>');
            } catch (e) {
                // Use default message
            }
        } else if (error.message) {
            userMessage = error.message;
        }
        
        frappe.msgprint({
            title: __('Error'),
            message: userMessage,
            indicator: 'red'
        });
    }
}
```
