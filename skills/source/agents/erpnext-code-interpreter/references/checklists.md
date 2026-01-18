# Code Interpreter Checklists

## Pre-Interpretation Checklist

Before starting interpretation, verify:

- [ ] User request is captured completely
- [ ] No obvious typos or misunderstandings
- [ ] Context is sufficient (which DocTypes, which ERPNext version)
- [ ] If unclear: clarifying questions prepared

---

## Step 1 Checklist: Extract Intent

### Action Identification
- [ ] Primary action verb identified
- [ ] Action mapped to category:
  - [ ] Computation/calculation
  - [ ] Validation/prevention
  - [ ] Notification/communication
  - [ ] Integration/sync
  - [ ] Filtering/permission
  - [ ] Workflow/approval
  - [ ] UI customization
  - [ ] Scheduling/automation

### Subject Identification
- [ ] Primary DocType(s) identified
- [ ] Related DocType(s) identified (if any)
- [ ] Specific field(s) mentioned (if any)
- [ ] Data transformation described (if any)

### Condition Identification
- [ ] Trigger condition clear (when should this happen?)
- [ ] Filter conditions clear (for which records?)
- [ ] User/role conditions clear (for whom?)

---

## Step 2 Checklist: Identify Trigger

### Trigger Type Confirmed
- [ ] User action on form
  - [ ] Field change
  - [ ] Form load
  - [ ] Button click
  - [ ] Save
  - [ ] Submit
  - [ ] Cancel
- [ ] Time/schedule
  - [ ] Frequency identified
  - [ ] Cron pattern determined
- [ ] External event
  - [ ] Webhook
  - [ ] API call
  - [ ] Other app trigger
- [ ] Permission check
  - [ ] List filtering
  - [ ] Document access

### Timing Confirmed
- [ ] Before action (can block)
- [ ] After action (cannot block, only react)

---

## Step 3 Checklist: Determine Mechanism

### Server Script Eligibility
- [ ] No external library imports needed
- [ ] No complex transaction management needed
- [ ] No file system access needed
- [ ] No shell commands needed
- [ ] → Server Script is eligible (all checked)
- [ ] → Controller required (any unchecked)

### Mechanism Selection
- [ ] Primary mechanism selected:
  - [ ] Client Script
  - [ ] Server Script (Document Event)
  - [ ] Server Script (API)
  - [ ] Server Script (Scheduler)
  - [ ] Server Script (Permission Query)
  - [ ] Controller
  - [ ] hooks.py configuration
  - [ ] Built-in feature (Workflow, Notification, etc.)
- [ ] Selection justified with reasoning
- [ ] Custom app requirement identified (yes/no)

### Additional Mechanisms Needed
- [ ] Client Script for UI feedback (if applicable)
- [ ] hooks.py configuration needed (if applicable)
- [ ] Multiple mechanisms coordinated (if applicable)

---

## Step 4 Checklist: Generate Specification

### Specification Completeness
- [ ] Summary (1 sentence)
- [ ] Business requirement (clarified)
- [ ] Implementation table:
  - [ ] DocType(s) listed
  - [ ] Trigger specified
  - [ ] Mechanism named
  - [ ] Version compatibility noted
- [ ] Data flow documented (numbered steps)
- [ ] Error handling defined

### Data Flow Quality
- [ ] Input data sources identified
- [ ] Processing steps clear
- [ ] Output/side effects documented
- [ ] No missing steps in flow

### Error Handling Quality
- [ ] Possible errors identified
- [ ] Each error has handling strategy
- [ ] User feedback approach defined
- [ ] Logging requirements noted

---

## Step 5 Checklist: Map to Skills

### Primary Skills
- [ ] Syntax skill for mechanism
- [ ] Implementation skill for mechanism
- [ ] Error handling skill for mechanism

### Supporting Skills
- [ ] Database operations (if needed)
- [ ] Permission handling (if needed)
- [ ] API patterns (if needed)
- [ ] Custom app structure (if needed)

### Skill Dependencies
- [ ] Dependencies between skills noted
- [ ] Order of skill usage clear

---

## Output Quality Checklist

### Clarity
- [ ] Non-technical user can understand the summary
- [ ] Technical implementer can follow the specification
- [ ] No ambiguous terms or undefined acronyms

### Completeness
- [ ] All aspects of request addressed
- [ ] Edge cases considered
- [ ] Version compatibility explicit

### Actionability
- [ ] Clear next steps for implementation
- [ ] Required skills listed
- [ ] Validation criteria defined

---

## Validation Criteria Checklist

For each specification, define tests for:

### Happy Path
- [ ] Normal use case works correctly
- [ ] Expected output/behavior occurs

### Edge Cases
- [ ] Empty/null values handled
- [ ] Boundary values handled
- [ ] Large volumes handled (if applicable)

### Error Cases
- [ ] Invalid input handled gracefully
- [ ] External failures handled (if applicable)
- [ ] User sees appropriate feedback

### Permission Cases
- [ ] Correct users can perform action
- [ ] Incorrect users are blocked
- [ ] Admin override works (if applicable)

---

## Common Pitfalls Checklist

Verify the specification avoids these:

### Mechanism Selection Pitfalls
- [ ] NOT using Server Script when imports are needed
- [ ] NOT using validate when before_submit is needed
- [ ] NOT confusing UI event names with hook names
- [ ] NOT forgetting Client Script for real-time UI

### Data Flow Pitfalls
- [ ] NOT modifying self after on_update (won't save)
- [ ] NOT assuming field values are set before validate
- [ ] NOT forgetting to handle child table changes

### Error Handling Pitfalls
- [ ] NOT swallowing errors silently
- [ ] NOT blocking operations unnecessarily
- [ ] NOT showing technical errors to users
- [ ] NOT forgetting to log errors

### Version Compatibility Pitfalls
- [ ] NOT using v16-only features without noting
- [ ] NOT forgetting scheduler tick differences
- [ ] NOT using deprecated patterns

---

## Quick Reference: Mechanism → Skills

| If Mechanism Is... | Then Skills Are... |
|--------------------|-------------------|
| Client Script | syntax-clientscripts, impl-clientscripts, errors-clientscripts |
| Server Script (Doc Event) | syntax-serverscripts, impl-serverscripts, errors-serverscripts |
| Server Script (API) | syntax-serverscripts, api-patterns, errors-api |
| Server Script (Scheduler) | syntax-serverscripts, syntax-scheduler, impl-scheduler |
| Server Script (Permission) | syntax-serverscripts, permissions, errors-permissions |
| Controller | syntax-controllers, impl-controllers, errors-controllers |
| Hooks | syntax-hooks, impl-hooks, errors-hooks |
| Custom App | syntax-customapp, impl-customapp |
| Jinja Template | syntax-jinja, impl-jinja |
| Database heavy | + database, errors-database |
| Whitelisted API | + syntax-whitelisted, impl-whitelisted |
