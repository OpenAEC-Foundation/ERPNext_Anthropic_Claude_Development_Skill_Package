# Data Masking (Frappe v16+)

Field-level data masking in Frappe hides sensitive values from users who lack the appropriate permission level. This is a server-enforced privacy feature -- masked values are replaced before they reach the client.

## Core Concept

A DocField with `mask=1` requires explicit `mask` permission at the field's `permlevel` for a user to see the real value. Users without that permission see obfuscated placeholders (e.g. `XXXXXXXX`).

**Key principle**: The Administrator role ALWAYS sees unmasked values. Masking NEVER applies to Administrator.

## Enabling Masking on a Field

Set the `mask` property on a DocField in the DocType JSON:

```json
{
  "fieldname": "phone",
  "fieldtype": "Data",
  "options": "Phone",
  "label": "Phone",
  "mask": 1,
  "permlevel": 1
}
```

Then grant `mask` permission at that `permlevel` to roles that need to see the real value:

| Role | permlevel | mask permission |
|------|-----------|-----------------|
| HR Manager | 1 | Yes (sees real value) |
| Employee | 1 | No (sees `042XXXXXX`) |

## How Masking Is Resolved

The `Meta.get_masked_fields()` method determines which fields are masked for the current user:

```python
# frappe/model/meta.py -- simplified logic
def get_masked_fields(self):
    if frappe.session.user == "Administrator":
        return []  # Administrator NEVER sees masked values

    masked_fields = []
    for df in self.fields:
        if df.get("mask") and not self.has_permlevel_access_to(
            fieldname=df.fieldname, df=df, permission_type="mask"
        ):
            df_copy = copy.deepcopy(df)
            df_copy.mask_readonly = 1
            masked_fields.append(df_copy)
    return masked_fields
```

Results are cached per user + DocType combination: `masked_fields::{doctype}::{user}`.

## Masking Patterns by Fieldtype

The `frappe.model.utils.mask` module applies type-aware obfuscation:

| Fieldtype + Options | Input | Masked Output |
|---------------------|-------|---------------|
| Data (Phone) | `+31612345678` | `+31XXXXXX` (first 3 chars + `XXXXXX`) |
| Data (Email) | `user@example.com` | `XXXXXX@example.com` (domain preserved) |
| Date | `2024-03-15` | `XX-XX-XXXX` |
| Time | `14:30:00` | `XX:XX` |
| All others | any value | `XXXXXXXX` |
| Empty/None | `None` or `""` | Returned as-is |

## Where Masking Is Applied

Masking is enforced at multiple layers:

| Layer | Module | How |
|-------|--------|-----|
| Document load | `frappe.model.document` | `get_masked_fields()` check on `load_from_db` and `as_dict` |
| Report Builder | `frappe.model.db_query` | `get_masked_fields()` applied to query results |
| Query Builder | `frappe.query_builder.utils` | Masked fields replaced after query execution |
| Script Reports | `frappe.desk.query_report` | Column-level masking using `ref_doctype_meta.get_masked_fields()` |
| Form view (JS) | `frappe/form/form.js` | Masked fields rendered read-only with placeholder |
| List view (JS) | `frappe/list/list_view.js` | Masked fields are non-filterable, non-clickable |
| Form meta (JS) | `frappe/desk/form/meta.py` | `masked_fields` list sent with meta for client-side rendering |

## Utility Functions

```python
from frappe.model.utils.mask import mask_field_value, mask_dict_results, mask_list_results

# Mask a single value
masked = mask_field_value(field_df, "user@example.com")
# → "XXXXXX@example.com"

# Mask all sensitive fields in dict-based query results
results = [{"name": "EMP-001", "phone": "+31612345678"}]
masked_results = mask_dict_results(results, masked_fields)

# Mask tuple-based results (with field index map)
results = [("EMP-001", "+31612345678")]
field_map = {"phone": 1}
masked_results = mask_list_results(results, masked_fields, field_map)
```

## GDPR / Privacy Use Cases

| Scenario | Implementation |
|----------|---------------|
| Employee personal data | Set `mask=1` on phone, email, address fields at `permlevel=1`; grant `mask` to HR Manager only |
| Customer PII | Mask contact details; grant `mask` permission to Account Manager role |
| Financial data | Mask salary, bank details at elevated permlevel |
| Audit compliance | Masked fields are read-only in the UI (`mask_readonly=1`), preventing accidental edits |

## Critical Rules

1. ALWAYS set `permlevel` > 0 on masked fields -- masking at `permlevel=0` has no practical effect since most roles have level-0 access.
2. NEVER rely on client-side masking alone -- the server masks values before sending them.
3. ALWAYS grant `mask` permission explicitly via Role Permission for DocType at the correct permlevel.
4. NEVER assume masked values are encrypted -- they are obfuscated for display only. The real values remain in the database.
5. ALWAYS clear cache after changing mask permissions: `frappe.cache.delete_value(f"masked_fields::{doctype}::{user}")`.

## Source Files

| File | Purpose |
|------|---------|
| `frappe/model/utils/mask.py` | `mask_field_value`, `mask_dict_results`, `mask_list_results` |
| `frappe/model/meta.py` | `Meta.get_masked_fields()` -- permission-aware field resolution |
| `frappe/model/db_query.py` | Report Builder masking integration |
| `frappe/query_builder/utils.py` | Query Builder masking integration |
| `frappe/desk/form/meta.py` | Sends `masked_fields` list to client |
| `frappe/model/document.py` | Document-level masking on load and serialize |
