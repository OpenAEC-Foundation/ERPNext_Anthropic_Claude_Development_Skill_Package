# Code Interpreter Examples

## Example 1: Auto-Calculate Request

### User Input
> "I want the total weight to automatically calculate based on item weights in the Sales Order"

### Interpretation Process

**Extract Intent:**
- Action: Auto-calculate (field computation)
- Subject: Total weight field, item weights in Sales Order
- Condition: When items change

**Identify Trigger:**
- Field change (item added/removed/modified) → Client Script
- Before save (validation backup) → Server Script

**Determine Mechanism:**
- Real-time UI update needed → Client Script
- Save validation needed → Server Script
- No external libraries → Server Script OK

### Generated Specification

```markdown
## Technical Specification

### Summary
Auto-calculate total weight in Sales Order based on sum of item weights.

### Business Requirement
The total_weight field in Sales Order should automatically update whenever 
items are added, removed, or quantities change. The calculation should 
happen in real-time on the form and be validated on save.

### Implementation

| Aspect | Value |
|--------|-------|
| **DocType(s)** | Sales Order, Sales Order Item |
| **Trigger** | Item table change + before save |
| **Mechanism** | Client Script + Server Script |
| **Version** | v14/v15/v16 |

### Data Flow
1. User modifies items table (add/remove/change qty)
2. Client Script triggers calculation
3. Sum: qty × weight_per_unit for each item
4. Update total_weight field
5. On save: Server Script recalculates and validates

### Error Handling
- Missing weight_per_unit: treat as 0, no error
- Negative result: frappe.throw() on save

### Required Skills
- [x] erpnext-syntax-clientscripts
- [x] erpnext-impl-clientscripts
- [x] erpnext-syntax-serverscripts
- [x] erpnext-impl-serverscripts

### Validation Criteria
1. Add item → total updates immediately
2. Change qty → total updates immediately
3. Remove item → total updates immediately
4. Save with correct total → succeeds
```

---

## Example 2: Notification Request

### User Input
> "Send email to manager when purchase order exceeds $10,000"

### Interpretation Process

**Extract Intent:**
- Action: Send email (notification)
- Subject: Purchase Order, amount threshold
- Condition: Amount > $10,000

**Identify Trigger:**
- When is "exceeds" determined? → On submit (finalized amount)
- Email after the action → on_submit event

**Determine Mechanism:**
- No external libraries needed
- Simple notification → Server Script
- Could also use Notification DocType (no-code)

### Generated Specification

```markdown
## Technical Specification

### Summary
Email notification to manager when Purchase Order is submitted with 
grand_total exceeding $10,000.

### Business Requirement
When a Purchase Order is submitted and the grand_total is greater than 
$10,000, send an email to the purchasing manager with order details.

### Implementation

| Aspect | Value |
|--------|-------|
| **DocType(s)** | Purchase Order |
| **Trigger** | on_submit |
| **Mechanism** | Server Script (Document Event) |
| **Version** | v14/v15/v16 |

### Data Flow
1. User submits Purchase Order
2. Server Script checks if grand_total > 10000
3. If yes: frappe.sendmail() to manager
4. Email includes: PO number, supplier, amount, items summary

### Error Handling
- Email failure: log error but don't block submission
- No manager configured: log warning

### Required Skills
- [x] erpnext-syntax-serverscripts
- [x] erpnext-impl-serverscripts
- [x] erpnext-errors-serverscripts

### Alternative: No-Code Solution
Could use Notification DocType instead of Server Script:
- Document Type: Purchase Order
- Event: Submit
- Condition: doc.grand_total > 10000
```

---

## Example 3: External Integration Request

### User Input
> "Sync inventory to our warehouse system via API when stock moves"

### Interpretation Process

**Extract Intent:**
- Action: Sync to external system (integration)
- Subject: Inventory/stock data
- Condition: When stock moves

**Identify Trigger:**
- Stock movement → Stock Entry submission
- Real-time sync → on_submit

**Determine Mechanism:**
- External API = needs `requests` library
- Server Script CANNOT import requests
- → MUST use Controller in custom app

### Generated Specification

```markdown
## Technical Specification

### Summary
Sync stock movements to external warehouse system via REST API when 
Stock Entries are submitted.

### Business Requirement
When a Stock Entry is submitted, send the stock movement data to the 
external warehouse management system via their REST API. Handle failures 
gracefully without blocking the stock entry.

### Implementation

| Aspect | Value |
|--------|-------|
| **DocType(s)** | Stock Entry |
| **Trigger** | on_submit |
| **Mechanism** | Controller (custom app) |
| **Version** | v14/v15/v16 |

### ⚠️ CRITICAL: Custom App Required
Server Scripts CANNOT import the `requests` library. This integration 
MUST be implemented in a custom app using either:
- Controller class override
- hooks.py doc_events

### Data Flow
1. Stock Entry submitted
2. Controller's on_submit hook triggers
3. Transform data to external API format
4. POST to external warehouse API
5. Log response
6. If failure: log error, optionally queue for retry

### Error Handling
- API timeout: log and continue (don't block stock entry)
- API error response: log with details
- Consider: background job for retry queue

### Required Skills
- [x] erpnext-syntax-customapp - Custom app structure
- [x] erpnext-impl-customapp - App setup
- [x] erpnext-syntax-controllers - Controller class
- [x] erpnext-impl-controllers - on_submit implementation
- [x] erpnext-errors-controllers - Error handling
- [x] erpnext-syntax-hooks - doc_events configuration

### Validation Criteria
1. Submit Stock Entry → data sent to API
2. API success → logged
3. API failure → logged, Stock Entry still saved
4. Test with API unavailable → Stock Entry succeeds, error logged
```

---

## Example 4: Permission Filtering Request

### User Input
> "Sales reps should only see their own customers"

### Interpretation Process

**Extract Intent:**
- Action: Filter/restrict view (permission)
- Subject: Customer list
- Condition: Based on sales rep assignment

**Identify Trigger:**
- List view access → Permission Query

**Determine Mechanism:**
- Dynamic list filtering → Server Script Permission Query
- No external libraries needed

### Generated Specification

```markdown
## Technical Specification

### Summary
Filter Customer list view to show only customers assigned to the 
current sales representative.

### Business Requirement
When a user with Sales User role views the Customer list, they should 
only see customers where they are assigned as the account_manager 
(or similar field). Administrators should see all customers.

### Implementation

| Aspect | Value |
|--------|-------|
| **DocType(s)** | Customer |
| **Trigger** | List view access |
| **Mechanism** | Server Script (Permission Query) |
| **Version** | v14/v15/v16 |

### Data Flow
1. User opens Customer list
2. Permission Query script executes
3. Check if user has System Manager role → return None (no filter)
4. Otherwise: return condition filtering by account_manager field

### Error Handling
- Script error: Frappe shows all (fail-open is dangerous!)
- Better: fail-closed with restrictive default

### Required Skills
- [x] erpnext-syntax-serverscripts - Permission Query syntax
- [x] erpnext-impl-serverscripts - Permission Query implementation
- [x] erpnext-permissions - Permission patterns
- [x] erpnext-errors-permissions - Permission error handling

### Validation Criteria
1. Sales User A sees only their customers
2. Sales User B sees only their customers
3. System Manager sees all customers
4. New customer without account_manager: not visible to sales users
```

---

## Example 5: Workflow Request

### User Input
> "Purchase orders over $5000 need manager approval before submission"

### Interpretation Process

**Extract Intent:**
- Action: Approval workflow
- Subject: Purchase Order
- Condition: Amount > $5000

**Identify Trigger:**
- Before submission → Workflow states
- Workflow is built-in feature

**Determine Mechanism:**
- ERPNext has built-in Workflow feature
- Custom states and transitions
- May need Server Script for complex conditions

### Generated Specification

```markdown
## Technical Specification

### Summary
Implement approval workflow for Purchase Orders exceeding $5,000 
requiring manager approval before submission.

### Business Requirement
Purchase Orders with grand_total > $5,000 must go through manager 
approval before they can be submitted. Orders under $5,000 can be 
submitted directly.

### Implementation

| Aspect | Value |
|--------|-------|
| **DocType(s)** | Purchase Order |
| **Trigger** | Document state changes |
| **Mechanism** | Built-in Workflow + optional Server Script |
| **Version** | v14/v15/v16 |

### Solution: Workflow Configuration

**States:**
1. Draft (default)
2. Pending Approval (for high-value)
3. Approved
4. Submitted (final)
5. Rejected

**Transitions:**
- Draft → Pending Approval: for grand_total > 5000
- Draft → Submitted: for grand_total <= 5000
- Pending Approval → Approved: by Purchase Manager
- Pending Approval → Rejected: by Purchase Manager
- Approved → Submitted: automatic or by creator

### Optional Server Script
For complex routing logic (e.g., different approvers by amount tier):
- before_submit: verify workflow completion
- on_update: auto-transition based on conditions

### Required Skills
- [ ] ERPNext Workflow documentation
- [x] erpnext-syntax-serverscripts - Optional custom logic
- [x] erpnext-impl-serverscripts - Optional validation

### Validation Criteria
1. PO < $5000 → can submit directly
2. PO > $5000 → goes to Pending Approval
3. Manager approves → state changes to Approved
4. Manager rejects → state changes to Rejected
5. Cannot submit without approval for high-value POs
```

---

## Example 6: Scheduled Task Request

### User Input
> "Every night, check for overdue invoices and send reminders"

### Interpretation Process

**Extract Intent:**
- Action: Check and send (scheduled task)
- Subject: Overdue invoices
- Condition: Daily schedule, due_date < today, unpaid

**Identify Trigger:**
- Time-based → Scheduler

**Determine Mechanism:**
- Simple query and email → Server Script Scheduler OK
- Complex processing → hooks.py scheduler_events

### Generated Specification

```markdown
## Technical Specification

### Summary
Daily scheduled task to identify overdue Sales Invoices and send 
payment reminder emails to customers.

### Business Requirement
Every night at 2 AM, check for unpaid Sales Invoices where due_date 
has passed. Send a reminder email to each customer with overdue invoices.

### Implementation

| Aspect | Value |
|--------|-------|
| **DocType(s)** | Sales Invoice |
| **Trigger** | Cron: 0 2 * * * (daily at 2 AM) |
| **Mechanism** | Server Script (Scheduler Event) |
| **Version** | v14/v15/v16 |

### Data Flow
1. Scheduler triggers at 2 AM
2. Query: outstanding > 0 AND due_date < today
3. Group invoices by customer
4. For each customer with overdue invoices:
   - Compile invoice list
   - Send reminder email
   - Log sent reminder

### Error Handling
- Email failure: log error, continue with next customer
- Query error: log and abort (notify admin)
- Long running: consider chunking if many invoices

### Required Skills
- [x] erpnext-syntax-serverscripts
- [x] erpnext-impl-serverscripts
- [x] erpnext-syntax-scheduler
- [x] erpnext-impl-scheduler
- [x] erpnext-database - Query patterns

### Validation Criteria
1. Runs at 2 AM daily
2. Only unpaid, overdue invoices selected
3. Each customer gets one email with all their overdue invoices
4. Paid or not-yet-due invoices ignored
5. Email failures don't stop other emails
```

---

## Pattern Recognition Summary

| User Phrase | Likely Mechanism |
|-------------|-----------------|
| "auto-calculate", "automatically fill" | Client Script + Server Script |
| "validate", "check before save" | Server Script (validate) |
| "prevent", "block", "don't allow" | Server Script with frappe.throw() |
| "send email", "notify" | Server Script (on_* event) or Notification |
| "sync", "integrate", "API" | Controller (custom app) |
| "every day", "schedule" | Server Script Scheduler or hooks.py |
| "only see their own" | Server Script Permission Query |
| "approval", "authorize" | Built-in Workflow |
| "add button", "custom action" | Client Script |
| "print format", "PDF" | Jinja Template |
