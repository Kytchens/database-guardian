# Approval Templates

Use these templates before risky database work.

## Database Work Detected

```text
Database-sensitive work detected.
Mode: READ_ONLY unless you approve a change.
I will inspect safely first and will not mutate data, run migrations, reset databases, delete records, set values to NULL, or change RLS/security without explicit approval.
```

## Risky Action Preview

```text
Proposed database action:
- Mode:
- Environment:
- Environment proof:
- Target:
- Action type:
- Exact SQL/command:
- Expected effect:
- Rows affected or impact estimate:
- Risk level:
- Rollback/recovery plan:
- Approval required:
```

## Exact Approval Prompt

```text
Please approve with exact wording if you want me to proceed:
"YES, <action> on <environment>."

Examples:
- YES, run this migration on local.
- YES, update 37 rows in kitchen_brand_schedules on local.
- YES, delete rows from checklist_runs where id in (...).
```

## Destructive Double Confirmation

```text
This is a CRITICAL database action because it can permanently remove or overwrite data.

To proceed, reply with:
"YES, I understand this may be irreversible. <exact action> on <environment>."
```

## DB Safety Log

```text
DB Safety Log:
- Mode:
- Environment:
- Read-only queries run:
- Files reviewed/edited:
- Risky actions proposed:
- Risky actions approved:
- Risky actions refused or deferred:
```
