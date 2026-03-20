# Examples - Client Script Error Handling

Complete working examples of error handling in Frappe/ERPNext Client Scripts.

---

## Example 1: Sales Order with Full Validation

Complete client script with comprehensive error handling.

```javascript
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        // Set up link filters with error handling
        try {
            frm.set_query('customer', () => ({
                filters: { disabled: 0 }
            }));
            
            frm.set_query('item_code', 'items', () => ({
                filters: { is_sales_item: 1, disabled: 0 }
            }));
        } catch (error) {
            console.error('Setup error:', error);
            // Don't throw - allow form to load
        }
    },
    
    refresh(frm) {
        // Add buttons with error boundaries
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Check Credit'), async () => {
                await safeAction(frm, checkCustomerCredit);
            });
        }
    },
    
    async customer(frm) {
        if (!frm.doc.customer) {
            // Clear related fields
            frm.set_value({
                customer_name: '',
                territory: '',
                credit_limit: 0
            });
            return;
        }
        
        try {
            frm.toggle_enable('customer', false);  // Disable while loading
            
            const r = await frappe.db.get_value('Customer', frm.doc.customer, [
                'customer_name', 'territory', 'credit_limit', 'disabled'
            ]);
            
            if (r.message) {
                if (r.message.disabled) {
                    frappe.msgprint({
                        title: __('Warning'),
                        message: __('Selected customer is disabled'),
                        indicator: 'orange'
                    });
                }
                
                frm.set_value({
                    customer_name: r.message.customer_name,
                    territory: r.message.territory,
                    credit_limit: r.message.credit_limit
                });
            }
        } catch (error) {
            console.error('Customer fetch error:', error);
            frappe.show_alert({
                message: __('Could not load customer details'),
                indicator: 'orange'
            }, 3);
        } finally {
            frm.toggle_enable('customer', true);
        }
    },
    
    validate(frm) {
        let errors = [];
        
        // Required field validation
        if (!frm.doc.customer) {
            errors.push(__('Customer is required'));
        }
        
        if (!frm.doc.delivery_date) {
            errors.push(__('Delivery Date is required'));
        } else if (frm.doc.delivery_date < frappe.datetime.get_today()) {
            errors.push(__('Delivery Date cannot be in the past'));
        }
        
        // Items validation
        if (!frm.doc.items || frm.doc.items.length === 0) {
            errors.push(__('At least one item is required'));
        } else {
            frm.doc.items.forEach((row, idx) => {
                if (!row.item_code) {
                    errors.push(__('Row {0}: Item Code is required', [idx + 1]));
                }
                if (!row.qty || row.qty <= 0) {
                    errors.push(__('Row {0}: Quantity must be positive', [idx + 1]));
                }
                if (row.rate < 0) {
                    errors.push(__('Row {0}: Rate cannot be negative', [idx + 1]));
                }
            });
        }
        
        // Amount validation
        if (frm.doc.grand_total <= 0 && frm.doc.items?.length > 0) {
            errors.push(__('Total amount must be greater than zero'));
        }
        
        // Credit limit warning (non-blocking)
        if (frm.doc.credit_limit && frm.doc.grand_total > frm.doc.credit_limit) {
            frappe.msgprint({
                title: __('Credit Warning'),
                message: __('Order total ({0}) exceeds customer credit limit ({1})', 
                    [format_currency(frm.doc.grand_total), format_currency(frm.doc.credit_limit)]),
                indicator: 'orange'
            });
        }
        
        // Throw all errors at once
        if (errors.length > 0) {
            frappe.throw({
                title: __('Please correct the following errors'),
                message: errors.join('<br>')
            });
        }
    },
    
    after_save(frm) {
        frappe.show_alert({
            message: __('Sales Order saved successfully'),
            indicator: 'green'
        }, 3);
    }
});

// Child table events
frappe.ui.form.on('Sales Order Item', {
    item_code(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (!row.item_code) {
            frappe.model.set_value(cdt, cdn, {
                item_name: '',
                rate: 0,
                amount: 0
            });
            return;
        }
        
        // Fetch item details with error handling
        frappe.call({
            method: 'frappe.client.get',
            args: {
                doctype: 'Item',
                name: row.item_code
            },
            callback(r) {
                if (r.message) {
                    frappe.model.set_value(cdt, cdn, {
                        item_name: r.message.item_name,
                        rate: r.message.standard_rate || 0
                    });
                }
            },
            error(r) {
                console.error('Item fetch error:', r);
                frappe.show_alert({
                    message: __('Could not load item details for {0}', [row.item_code]),
                    indicator: 'orange'
                }, 3);
            }
        });
    },
    
    qty(frm, cdt, cdn) {
        calculateRowAmount(frm, cdt, cdn);
    },
    
    rate(frm, cdt, cdn) {
        calculateRowAmount(frm, cdt, cdn);
    }
});

function calculateRowAmount(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    let amount = (row.qty || 0) * (row.rate || 0);
    frappe.model.set_value(cdt, cdn, 'amount', amount);
}

async function safeAction(frm, actionFn) {
    try {
        await actionFn(frm);
    } catch (error) {
        console.error('Action error:', error);
        frappe.msgprint({
            title: __('Error'),
            message: error.message || __('An error occurred. Please try again.'),
            indicator: 'red'
        });
    }
}

async function checkCustomerCredit(frm) {
    const r = await frappe.call({
        method: 'erpnext.selling.doctype.customer.customer.get_credit_limit',
        args: { customer: frm.doc.customer }
    });
    
    if (r.message) {
        const available = r.message.credit_limit - r.message.outstanding;
        frappe.msgprint({
            title: __('Credit Status'),
            message: `
                <p><strong>${__('Credit Limit')}:</strong> ${format_currency(r.message.credit_limit)}</p>
                <p><strong>${__('Outstanding')}:</strong> ${format_currency(r.message.outstanding)}</p>
                <p><strong>${__('Available')}:</strong> ${format_currency(available)}</p>
            `,
            indicator: available > 0 ? 'green' : 'red'
        });
    }
}
```

---

## Example 2: Form with Async Validation

```javascript
frappe.ui.form.on('Purchase Order', {
    async validate(frm) {
        // Collect async validation results
        const validationResults = {
            errors: [],
            warnings: []
        };
        
        // Check supplier status
        try {
            const supplier = await frappe.db.get_value('Supplier', frm.doc.supplier, [
                'disabled', 'on_hold', 'hold_type'
            ]);
            
            if (supplier.message?.disabled) {
                validationResults.errors.push(__('Supplier is disabled'));
            }
            
            if (supplier.message?.on_hold) {
                if (supplier.message.hold_type === 'All') {
                    validationResults.errors.push(__('Supplier is on hold for all transactions'));
                } else {
                    validationResults.warnings.push(__('Supplier is on hold for {0}', 
                        [supplier.message.hold_type]));
                }
            }
        } catch (error) {
            console.error('Supplier validation error:', error);
            validationResults.warnings.push(__('Could not verify supplier status'));
        }
        
        // Check item availability
        try {
            for (const row of frm.doc.items || []) {
                const item = await frappe.db.get_value('Item', row.item_code, [
                    'disabled', 'is_purchase_item'
                ]);
                
                if (item.message?.disabled) {
                    validationResults.errors.push(__('Item {0} is disabled', [row.item_code]));
                }
                
                if (item.message && !item.message.is_purchase_item) {
                    validationResults.errors.push(__('Item {0} is not a purchase item', [row.item_code]));
                }
            }
        } catch (error) {
            console.error('Item validation error:', error);
            validationResults.warnings.push(__('Could not verify all items'));
        }
        
        // Show warnings (non-blocking)
        if (validationResults.warnings.length > 0) {
            frappe.msgprint({
                title: __('Warnings'),
                message: validationResults.warnings.join('<br>'),
                indicator: 'orange'
            });
        }
        
        // Throw errors (blocking)
        if (validationResults.errors.length > 0) {
            frappe.throw({
                title: __('Cannot Save'),
                message: validationResults.errors.join('<br>')
            });
        }
    }
});
```

---

## Example 3: Wizard-Style Form with Step Validation

```javascript
frappe.ui.form.on('Project Setup', {
    refresh(frm) {
        // Show current step
        updateStepIndicator(frm);
        
        // Add navigation buttons
        frm.add_custom_button(__('Next Step'), async () => {
            await validateAndAdvance(frm);
        }).addClass('btn-primary');
        
        if (frm.doc.current_step > 1) {
            frm.add_custom_button(__('Previous'), () => {
                frm.set_value('current_step', frm.doc.current_step - 1);
            });
        }
    }
});

async function validateAndAdvance(frm) {
    const currentStep = frm.doc.current_step || 1;
    
    try {
        // Validate current step
        switch (currentStep) {
            case 1:
                validateBasicInfo(frm);
                break;
            case 2:
                await validateTeamSetup(frm);
                break;
            case 3:
                validateBudget(frm);
                break;
            case 4:
                await validateAndComplete(frm);
                return;  // Final step, don't advance
        }
        
        // Advance to next step
        await frm.set_value('current_step', currentStep + 1);
        await frm.save();
        
        frappe.show_alert({
            message: __('Step {0} completed', [currentStep]),
            indicator: 'green'
        }, 2);
        
    } catch (error) {
        if (error.message) {
            // Validation error - show to user
            frappe.msgprint({
                title: __('Step {0} Incomplete', [currentStep]),
                message: error.message,
                indicator: 'red'
            });
        } else {
            // Unexpected error
            console.error('Step validation error:', error);
            frappe.msgprint({
                title: __('Error'),
                message: __('Could not complete this step. Please try again.'),
                indicator: 'red'
            });
        }
    }
}

function validateBasicInfo(frm) {
    const errors = [];
    
    if (!frm.doc.project_name) errors.push(__('Project Name is required'));
    if (!frm.doc.customer) errors.push(__('Customer is required'));
    if (!frm.doc.start_date) errors.push(__('Start Date is required'));
    
    if (errors.length > 0) {
        throw new Error(errors.join('<br>'));
    }
}

async function validateTeamSetup(frm) {
    if (!frm.doc.project_manager) {
        throw new Error(__('Project Manager is required'));
    }
    
    // Verify project manager exists and is active
    const user = await frappe.db.get_value('User', frm.doc.project_manager, 'enabled');
    if (!user.message?.enabled) {
        throw new Error(__('Selected Project Manager is not an active user'));
    }
}

function validateBudget(frm) {
    if (!frm.doc.budget_amount || frm.doc.budget_amount <= 0) {
        throw new Error(__('Budget amount must be greater than zero'));
    }
}

async function validateAndComplete(frm) {
    // Final validation
    const r = await frappe.call({
        method: 'myapp.api.validate_project_setup',
        args: { project: frm.doc.name },
        freeze: true,
        freeze_message: __('Validating setup...')
    });
    
    if (r.message?.valid) {
        await frm.set_value('status', 'Active');
        await frm.save();
        
        frappe.msgprint({
            title: __('Success'),
            message: __('Project setup completed successfully!'),
            indicator: 'green',
            primary_action: {
                label: __('Go to Project'),
                action: () => {
                    frappe.set_route('Form', 'Project', frm.doc.project);
                }
            }
        });
    } else {
        throw new Error(r.message?.error || __('Setup validation failed'));
    }
}

function updateStepIndicator(frm) {
    const steps = ['Basic Info', 'Team', 'Budget', 'Complete'];
    const current = frm.doc.current_step || 1;
    
    let html = '<div class="step-indicator">';
    steps.forEach((step, idx) => {
        const stepNum = idx + 1;
        const status = stepNum < current ? 'complete' : (stepNum === current ? 'active' : 'pending');
        html += `<span class="step ${status}">${stepNum}. ${__(step)}</span>`;
    });
    html += '</div>';
    
    frm.set_intro(html);
}
```

---

## Example 4: Real-time Stock Check with Debouncing

```javascript
let stockCheckTimeout = null;

frappe.ui.form.on('Sales Order Item', {
    item_code(frm, cdt, cdn) {
        checkStockWithDebounce(frm, cdt, cdn);
    },
    
    qty(frm, cdt, cdn) {
        checkStockWithDebounce(frm, cdt, cdn);
    },
    
    warehouse(frm, cdt, cdn) {
        checkStockWithDebounce(frm, cdt, cdn);
    }
});

function checkStockWithDebounce(frm, cdt, cdn) {
    // Clear previous timeout
    if (stockCheckTimeout) {
        clearTimeout(stockCheckTimeout);
    }
    
    // Debounce: wait 500ms before checking
    stockCheckTimeout = setTimeout(() => {
        checkStock(frm, cdt, cdn);
    }, 500);
}

async function checkStock(frm, cdt, cdn) {
    const row = frappe.get_doc(cdt, cdn);
    
    if (!row.item_code || !row.qty || !row.warehouse) {
        // Clear stock indicator
        frappe.model.set_value(cdt, cdn, 'stock_status', '');
        return;
    }
    
    try {
        const r = await frappe.call({
            method: 'erpnext.stock.utils.get_stock_balance',
            args: {
                item_code: row.item_code,
                warehouse: row.warehouse
            }
        });
        
        const available = r.message || 0;
        const status = available >= row.qty ? 'green' : (available > 0 ? 'orange' : 'red');
        const message = available >= row.qty 
            ? __('In Stock ({0})', [available])
            : __('Low Stock ({0} available)', [available]);
        
        frappe.model.set_value(cdt, cdn, 'stock_status', 
            `<span class="indicator ${status}">${message}</span>`);
        
        // Show alert for out of stock
        if (available < row.qty) {
            frappe.show_alert({
                message: __('Item {0}: Only {1} available in {2}', 
                    [row.item_code, available, row.warehouse]),
                indicator: 'orange'
            }, 5);
        }
        
    } catch (error) {
        console.error('Stock check error:', error);
        frappe.model.set_value(cdt, cdn, 'stock_status', 
            `<span class="indicator gray">${__('Could not check stock')}</span>`);
    }
}
```

---

## Example 5: Form with External API Integration

```javascript
frappe.ui.form.on('Address Verification', {
    async verify_address(frm) {
        if (!frm.doc.address_line1 || !frm.doc.city || !frm.doc.country) {
            frappe.msgprint({
                title: __('Missing Information'),
                message: __('Please enter address, city, and country'),
                indicator: 'orange'
            });
            return;
        }
        
        try {
            // Show loading state
            frm.disable_save();
            frm.set_intro(__('Verifying address...'), 'blue');
            
            const r = await frappe.call({
                method: 'myapp.integrations.address.verify_address',
                args: {
                    address_line1: frm.doc.address_line1,
                    address_line2: frm.doc.address_line2,
                    city: frm.doc.city,
                    state: frm.doc.state,
                    postal_code: frm.doc.postal_code,
                    country: frm.doc.country
                }
            });
            
            if (r.message?.verified) {
                // Address verified - update with standardized values
                frm.set_value({
                    address_line1: r.message.standardized.address_line1,
                    city: r.message.standardized.city,
                    state: r.message.standardized.state,
                    postal_code: r.message.standardized.postal_code,
                    verification_status: 'Verified',
                    verified_on: frappe.datetime.now_datetime()
                });
                
                frm.set_intro(__('Address verified successfully'), 'green');
                
                frappe.show_alert({
                    message: __('Address verified'),
                    indicator: 'green'
                }, 3);
                
            } else if (r.message?.suggestions) {
                // Show suggestions
                showAddressSuggestions(frm, r.message.suggestions);
                
            } else {
                // Could not verify
                frm.set_value('verification_status', 'Unverified');
                frm.set_intro(__('Address could not be verified'), 'orange');
                
                frappe.msgprint({
                    title: __('Verification Failed'),
                    message: r.message?.error || __('The address could not be verified. Please check and try again.'),
                    indicator: 'orange'
                });
            }
            
        } catch (error) {
            console.error('Address verification error:', error);
            
            frm.set_intro(__('Verification service unavailable'), 'red');
            
            // Determine error type
            let userMessage = __('Could not connect to verification service. Please try again later.');
            
            if (error.status === 429) {
                userMessage = __('Too many verification requests. Please wait a moment and try again.');
            } else if (error.status >= 500) {
                userMessage = __('Verification service is temporarily unavailable.');
            }
            
            frappe.msgprint({
                title: __('Verification Error'),
                message: userMessage,
                indicator: 'red'
            });
            
        } finally {
            frm.enable_save();
        }
    }
});

function showAddressSuggestions(frm, suggestions) {
    const options = suggestions.map((s, idx) => ({
        label: `${s.address_line1}, ${s.city}, ${s.state} ${s.postal_code}`,
        value: idx
    }));
    
    frappe.prompt({
        label: __('Did you mean one of these?'),
        fieldname: 'selection',
        fieldtype: 'Select',
        options: options.map(o => o.label).join('\n'),
        default: options[0].label
    }, (values) => {
        const idx = options.findIndex(o => o.label === values.selection);
        if (idx >= 0) {
            const selected = suggestions[idx];
            frm.set_value({
                address_line1: selected.address_line1,
                city: selected.city,
                state: selected.state,
                postal_code: selected.postal_code,
                verification_status: 'Verified',
                verified_on: frappe.datetime.now_datetime()
            });
            frm.set_intro(__('Address verified'), 'green');
        }
    }, __('Address Suggestions'));
}
```

---

## Quick Reference: Error Response Codes

```javascript
// Common HTTP status codes and handling
switch (error.status) {
    case 400:
        // Bad Request - validation error from server
        message = __('Invalid data. Please check your input.');
        break;
    case 401:
        // Unauthorized - session expired
        message = __('Session expired. Please refresh the page.');
        break;
    case 403:
        // Forbidden - no permission
        message = __('You do not have permission for this action.');
        break;
    case 404:
        // Not Found - record deleted
        message = __('Record not found. It may have been deleted.');
        break;
    case 417:
        // Expectation Failed - frappe.throw() from server
        // Parse _server_messages for actual error
        break;
    case 429:
        // Too Many Requests - rate limited
        message = __('Too many requests. Please wait and try again.');
        break;
    case 500:
        // Internal Server Error
        message = __('Server error. Please try again later.');
        break;
    case 502:
    case 503:
    case 504:
        // Gateway errors - server overloaded
        message = __('Service temporarily unavailable.');
        break;
    default:
        message = __('An error occurred. Please try again.');
}
```
