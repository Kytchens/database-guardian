# Risk Patterns

Use this reference when reviewing SQL, migrations, seeds, ORM schema changes, or database commands.

## Critical SQL Patterns

Require exact user approval:

```sql
DROP DATABASE
DROP SCHEMA
DROP TABLE
DROP COLUMN
TRUNCATE
DELETE FROM table_name
ALTER TABLE table_name DROP ...
ALTER TABLE table_name DISABLE ROW LEVEL SECURITY
DROP POLICY
UPDATE table_name SET column = NULL
```

## High-Risk SQL Patterns

Require preview, impact estimate, rollback plan, and approval:

```sql
INSERT INTO
UPDATE
UPSERT
MERGE
ALTER TABLE
CREATE POLICY
ALTER POLICY
CREATE TRIGGER
ALTER TYPE
CREATE UNIQUE INDEX
SET NOT NULL
```

## Suspicious WHERE Clauses

Treat as dangerous until reviewed:

```sql
WHERE true
WHERE 1 = 1
WHERE id IS NOT NULL
WHERE created_at IS NOT NULL
-- missing tenant/workspace/kitchen/org filter in multi-tenant systems
```

## Read-Only Risks

Read-only queries can still be risky when they:

- Dump sensitive data.
- Use `SELECT *` on user/customer/payment/auth tables.
- Export large datasets.
- Run against production without limits.
- Use heavy joins on large tables.
- Use `EXPLAIN ANALYZE` on expensive queries.

## Dangerous Commands

Require target proof and approval:

```bash
supabase db reset
supabase db push
supabase migration up
supabase migration repair
supabase db dump
prisma migrate deploy
prisma db push
drizzle-kit push
rails db:migrate
rails db:reset
sequelize db:migrate
psql -c "UPDATE ..."
psql -c "DELETE ..."
```

## Safe Read Examples

Prefer these first:

```sql
SELECT COUNT(*) FROM table_name;
SELECT id, status, created_at FROM table_name LIMIT 20;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'table_name';
```
