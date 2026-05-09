---
name: database-guardian
description: Guard database-sensitive work with read-only defaults, environment proof, visible action reports, and explicit approval gates. Use when working with databases, SQL, migrations, Supabase, Postgres, Prisma, Drizzle, seed data, RLS policies, schema changes, data backfills, production or staging database access, or any command that may inspect or mutate database state.
---

# Database Guardian

## Purpose

Prevent accidental database damage while still allowing useful read-only investigation. Keep the user's trust boundary clear: read safely, explain risky work, and never mutate, delete, null out, reset, migrate, or weaken database security without explicit approval.

## First Response

When database-sensitive work is detected, state:

```text
Database-sensitive work detected. I will use read-only investigation by default. I will not mutate data, run migrations, reset databases, delete records, set values to NULL, or change database security without explicit approval.
```

Maintain a visible `DB Safety Log` in the conversation whenever database commands, migration edits, seed edits, RLS changes, or ORM schema changes are involved.

## Operating Modes

Use the safest mode that fits the task:

- `READ_ONLY`: Inspect schema/data safely. Default for local/dev when environment proof exists.
- `PRODUCTION_SAFE`: Read-only only. Default for production, staging, shared, remote, or unknown environments.
- `GUARDED_WRITE`: Writes or migrations allowed only after exact preview, row count or impact estimate, rollback plan, and user approval.
- `LOCKDOWN`: No database commands. Use when the user says to freeze database access or when environment risk cannot be resolved.

If no mode is stated, use `READ_ONLY` for proven local/dev and `PRODUCTION_SAFE` for anything else.

## Decision Workflow

1. Classify the work:
   - Read-only inspection
   - Migration/schema edit
   - Seed/data fixture edit
   - Data mutation/backfill
   - Security/RLS/policy change
   - Database command or deployment command
2. Prove the environment:
   - `local`, `dev`, `preview`, `staging`, `production`, `shared`, or `unknown`
   - Cite the proof, such as localhost URL, local Supabase config, env var name, CLI target, branch, connection string host, or Supabase project ref.
3. Choose the mode.
4. For read-only work, use safe query rules.
5. For risky work, present the action preview and wait for approval.
6. After each database-sensitive action, update the `DB Safety Log`.

If the environment cannot be proven local/dev, treat it as production-safe and ask before running any query that may expose sensitive data, create load, or touch shared systems.

## Database Detection

Before deciding that a project has no database, inspect safe local signals:

- Database folders: `supabase/`, `prisma/`, `drizzle/`, `migrations/`, `db/`, `database/`.
- Database files: `schema.sql`, `schema.prisma`, `drizzle.config.*`, migration files, seed files.
- Package scripts and dependencies mentioning Supabase, Postgres, Prisma, Drizzle, TypeORM, Sequelize, Knex, Rails migrations, Django migrations, or similar database tools.
- Environment files such as `.env`, `.env.local`, `.env.development`, `.env.production`, and `.env.example`.

When inspecting environment files:

- Read only enough to detect database presence and environment target.
- Prefer key names and non-secret identifiers over values.
- Treat keys like `SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `SUPABASE_PROJECT_ID`, `SUPABASE_DB_URL`, `DATABASE_URL`, `POSTGRES_URL`, `PRISMA_DATABASE_URL`, and `DIRECT_URL` as database signals.
- For Supabase URLs, the project ref in `https://<project-ref>.supabase.co` proves a Supabase project exists, but does not prove whether it is production or staging.
- Never print secret values, service-role keys, passwords, tokens, full connection strings, or private `.env` contents into chat.
- If a `.env` file contains a remote Supabase/Postgres URL and the environment cannot be proven local/dev, use `PRODUCTION_SAFE`.

If no database signals are found, say that Database Guardian is available but no database-sensitive work is detected, then continue normally.

## Read-Only Mode

Read-only investigation is allowed when the environment is known and the query is limited.

Allowed examples:

```sql
SELECT COUNT(*) FROM table_name;
SELECT id, status, created_at FROM table_name ORDER BY created_at DESC LIMIT 20;
EXPLAIN SELECT ...;
SHOW ...;
```

Read-only rules:

- Prefer counts, metadata, and limited samples.
- Use `LIMIT` for sample queries.
- Select explicit non-sensitive columns. Avoid `SELECT *` on user, customer, payment, auth, or operationally sensitive tables.
- Avoid dumping PII, secrets, tokens, addresses, phone numbers, emails, payment data, and private customer notes.
- Ask before large exports, production-sized joins, `EXPLAIN ANALYZE`, long-running queries, or any read that may create load.
- Never use read-only investigation as a reason to mutate data.

## Risk Levels

- `LOW`: Local read-only schema inspection, counts, limited non-sensitive samples.
- `MEDIUM`: Read-only staging/production queries, larger joins, sensitive table inspection with limited columns, migration file edits that only add safe objects.
- `HIGH`: Any write, migration run, seed change, backfill, RLS/policy change, ORM push, shared database command, or broad read against sensitive data.
- `CRITICAL`: `DELETE`, `DROP`, `TRUNCATE`, database reset, setting existing values to `NULL`, disabling/weakening RLS, production/staging mutation, irreversible migration.

If unsure, classify one level higher.

## Approval Gates

Do not proceed without explicit approval for:

- `INSERT`, `UPDATE`, `UPSERT`, `DELETE`, `MERGE`, or backfills.
- `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `REINDEX`, or schema changes on a live database.
- Running migrations or ORM push/deploy commands.
- Changing seed data that may be applied to shared environments.
- Creating, altering, dropping, disabling, or weakening RLS policies.
- Setting existing database values to `NULL`.
- Resetting, restoring, cloning, importing, or exporting databases.
- Any command where the target environment is unclear.

Vague approval is not enough for high or critical actions. Require exact approval such as:

```text
YES, run this migration on local.
YES, update kitchen_brand_schedules rows where kitchen_id = ...
YES, delete rows from checklist_runs where id in (...)
YES, drop column old_status from table_name.
```

## Risky Action Preview

Before any high or critical action, show:

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

Stop after the preview and wait for the user's explicit approval.

## Mutation Rules

- Never mutate data when the user only asked to inspect, review, debug, or explain.
- Never invent seed values for real records.
- Never set existing values to `NULL` unless the user explicitly names the table, column, and reason.
- Never run `UPDATE` or `DELETE` without a specific `WHERE` clause.
- Treat broad predicates like `WHERE true`, `WHERE id IS NOT NULL`, and missing tenant/workspace filters as dangerous.
- Before mutations, estimate rows affected with a read-only query whenever possible.
- Prefer transaction dry-runs for manual SQL:

```sql
BEGIN;
-- proposed write
-- inspect result
ROLLBACK;
```

Only `COMMIT` after explicit approval.

## Migration Review

Before creating or running migrations, summarize:

```text
Migration safety summary:
- Tables changed:
- Columns added:
- Columns removed:
- Indexes changed:
- Constraints changed:
- Policies/RLS changed:
- Existing data touched:
- Backfill behavior:
- Reversibility:
- Risk level:
```

For non-null columns on existing tables, verify defaults/backfills and lock risk. For foreign keys, indexes, unique constraints, and triggers, explain likely runtime impact.

## RLS And Security Guard

RLS and policy changes are high risk by default.

- Never disable RLS without explicit critical approval.
- Never loosen access without explaining who gains access and to what rows.
- Never drop policies silently.
- Test or describe expected behavior for representative roles such as anonymous, authenticated, admin, owner, and service role when relevant.
- If the policy's business meaning is unclear, ask the user rather than guessing from table or column names.

## Dangerous Commands

Ask before running commands like:

```bash
supabase db reset
supabase db push
supabase migration up
supabase migration repair
supabase db dump
prisma migrate deploy
prisma db push
drizzle-kit push
psql -c "UPDATE ..."
psql -c "DELETE ..."
```

If a command can target a remote project, prove the target first.

## Scanner

For SQL files, migrations, seeds, or command snippets, run or mentally apply `scripts/scan_sql_risk.py` when practical:

```bash
python scripts/scan_sql_risk.py path/to/file.sql
```

Use scanner output as a warning system, not as permission. If the scanner finds nothing but the change still appears risky, follow the approval gates.

See `references/risk-patterns.md` for dangerous SQL and command patterns.

## Adapter Guidance

For cross-agent installation, see `references/agent-adapters.md`. Use this skill as the source of truth, then point Codex, Claude, Cursor, Kimi, and repo-level `AGENTS.md` files at it.

## DB Safety Log

Keep this log visible during database-sensitive work:

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

If no SQL or database command was run, say so plainly.
