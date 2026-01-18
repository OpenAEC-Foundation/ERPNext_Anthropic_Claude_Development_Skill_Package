# Code Interpreter Workflow - Detailed Steps

## Complete Interpretation Process

### Step 1: Extract Intent

**Goal**: Understand what the user actually wants to achieve.

#### 1.1 Identify the Action Verb

| User Says | Likely Intent |
|-----------|---------------|
| "auto-calculate", "automatically fill" | Field computation |
| "validate", "check", "ensure" | Data validation |
| "prevent", "block", "stop" | Operation blocking |
| "notify", "alert", "email" | Notification |
| "sync", "connect", "integrate" | External integration |
| "schedule", "daily", "every hour" | Scheduled task |
| "approve", "review", "authorize" | Workflow |
| "filter", "show only", "restrict view" | Permission/filtering |
| "add button", "add action" | UI customization |
| "format", "print", "PDF" | Print/report customization |

#### 1.2 Identify the Subject

What data/document is involved?
- Specific DocType mentioned?
- Field names mentioned?
- Related documents involved?

#### 1.3 Identify the Condition

When should this happen?
- Always?
- Only when specific field has value?
- Only for specific status?
- Only for specific user/role?

### Step 2: Identify Trigger Context

**Goal**: Determine WHEN the code should execute.

#### Decision Tree: Trigger Type

```
Is it triggered by...

USER ACTION ON FORM?
├─► Field value change
│   └── Client Script: on field change
├─► Form load
│   └── Client Script: refresh event
├─► Button click
│   └── Client Script: custom button with frappe.call
├─► Save button
│   └── Server Script: validate (before) or on_update (after)
├─► Submit button
│   └── Server Script: before_submit or on_submit
└─► Cancel button
    └── Server Script: before_cancel or on_cancel

TIME/SCHEDULE?
├─► Every X minutes/hours
│   └── Server Script Scheduler or hooks.py
├─► Daily at specific time
│   └── Server Script Scheduler (cron) or hooks.py
└─► Weekly/Monthly
    └── hooks.py scheduler_events

EXTERNAL EVENT?
├─► Webhook from external system
│   └── Server Script API or @frappe.whitelist
├─► API call
│   └── Server Script API or @frappe.whitelist
└─► Another app's action
    └── doc_events in hooks.py

PERMISSION CHECK?
└─► List view filtering
    └── Server Script Permission Query
```

### Step 3: Determine Mechanism

**Goal**: Select the right ERPNext mechanism.

#### Primary Decision: Server Script vs Controller

```
CAN YOU USE SERVER SCRIPT?

Check these disqualifiers:
[ ] Need to import external library (requests, pandas, etc.)
[ ] Need complex try/except/finally with rollback
[ ] Need to modify multiple documents in transaction
[ ] Need to access file system
[ ] Need to run shell commands

If ANY checked → Controller (custom app required)
If NONE checked → Server Script acceptable
```

#### Secondary Decision: Client Script Needed?

```
ADD CLIENT SCRIPT WHEN:

[ ] Real-time UI feedback needed (instant calculation)
[ ] Field visibility/read-only based on other fields
[ ] Custom buttons needed
[ ] Form-level warnings/alerts
[ ] Auto-fetch from linked documents
```

#### Mechanism Selection Summary

| Requirement | Mechanism |
|-------------|-----------|
| Quick validation on save | Server Script (validate) |
| Real-time UI calculation | Client Script + Server Script backup |
| Simple API endpoint | Server Script (API) |
| Complex API with external calls | @frappe.whitelist in custom app |
| Daily batch job (simple) | Server Script (Scheduler) |
| Complex scheduled job | hooks.py scheduler_events |
| List filtering per user | Server Script (Permission Query) |
| Multiple doc transaction | Controller in custom app |
| Document lifecycle hooks | Server Script or hooks.py doc_events |

### Step 4: Generate Specification

**Goal**: Create actionable technical spec.

#### Specification Components

1. **Summary** (1 sentence)
   - What will be built
   - What problem it solves

2. **Business Requirement** (clarified)
   - Original request with ambiguities resolved
   - Assumptions made (if any)

3. **Implementation Details**
   - DocType(s) involved
   - Trigger/event
   - Mechanism selected
   - Version compatibility

4. **Data Flow**
   - What data is read
   - What processing happens
   - What data is written/modified
   - What output is produced

5. **Error Handling**
   - What errors can occur
   - How each error is handled
   - User feedback approach

6. **Validation Criteria**
   - How to test it works
   - Edge cases to verify

### Step 5: Map to Skills

**Goal**: Identify which skills are needed for implementation.

#### Skill Mapping Process

1. Based on mechanism, identify PRIMARY skills:
   - Server Script → `erpnext-syntax-serverscripts`, `erpnext-impl-serverscripts`
   - Client Script → `erpnext-syntax-clientscripts`, `erpnext-impl-clientscripts`
   - etc.

2. Add ERROR HANDLING skills:
   - Every mechanism needs its error handling skill
   - `erpnext-errors-*` corresponding to mechanism

3. Add SUPPORTING skills if needed:
   - Database operations → `erpnext-database`
   - Permission checks → `erpnext-permissions`
   - API responses → `erpnext-api-patterns`

4. Check for CUSTOM APP requirement:
   - If needed → add `erpnext-syntax-customapp`, `erpnext-impl-customapp`
   - If hooks.py needed → add `erpnext-syntax-hooks`, `erpnext-impl-hooks`

## Example Interpretation Walkthrough

### Input Request
> "When a Sales Invoice is submitted, check if customer credit limit is exceeded and block if so"

### Step 1: Extract Intent
- **Action**: "check" and "block" → Validation that prevents action
- **Subject**: Sales Invoice, Customer credit limit
- **Condition**: On submit

### Step 2: Identify Trigger
- User action: Submit button
- Trigger: before_submit (must block BEFORE action completes)

### Step 3: Determine Mechanism
- No external libraries needed ✓
- No complex transactions needed ✓
- No file system access needed ✓
- → Server Script is acceptable

### Step 4: Generate Specification

```markdown
## Technical Specification

### Summary
Block Sales Invoice submission when customer's credit limit is exceeded.

### Business Requirement
When submitting a Sales Invoice, calculate the customer's total outstanding 
including this invoice. If it exceeds their credit limit, prevent submission 
with clear error message.

### Implementation

| Aspect | Value |
|--------|-------|
| **DocType(s)** | Sales Invoice, Customer |
| **Trigger** | before_submit |
| **Mechanism** | Server Script (Document Event) |
| **Version** | v14/v15/v16 |

### Data Flow
1. Get customer from Sales Invoice
2. Query customer's current outstanding amount
3. Add current invoice grand_total
4. Compare with customer's credit_limit
5. If exceeded: frappe.throw() with message
6. If OK: allow submission to proceed

### Error Handling
- frappe.throw() blocks submission with clear message
- Message includes: current outstanding, limit, and amount over

### Required Skills
- [x] erpnext-syntax-serverscripts - Server Script syntax
- [x] erpnext-impl-serverscripts - Document event implementation
- [x] erpnext-errors-serverscripts - Error handling patterns
- [x] erpnext-database - Query for outstanding calculation

### Validation Criteria
1. Submit invoice for customer under credit limit → succeeds
2. Submit invoice that would exceed limit → blocked with message
3. Message shows correct amounts
4. Cancelled/Draft invoices not counted in outstanding
```

### Step 5: Map to Skills
- Primary: `erpnext-syntax-serverscripts`, `erpnext-impl-serverscripts`
- Error: `erpnext-errors-serverscripts`
- Supporting: `erpnext-database` (for outstanding calculation query)
