# Database Guardian

Database Guardian is a portable AI-agent skill for safer database work.

It lets agents inspect databases in read-only mode, but requires explicit user approval before writes, migrations, deletes, resets, `NULL` backfills, RLS/security changes, or other risky database actions.

Use it with Codex, Claude, Cursor, Kimi, or any agent that can read a `SKILL.md` or project instruction file.

## What It Protects

The skill tells agents to:

- Use read-only investigation by default.
- Detect database presence from safe local signals such as `supabase/`, migrations, ORM config, and `.env` keys.
- Prove whether the target database is local, staging, production, shared, or unknown.
- Ask before any database mutation.
- Ask with double confirmation before destructive actions.
- Never silently delete data, drop schema, reset databases, or set existing values to `NULL`.
- Show the exact SQL or command before risky work.
- Estimate affected rows before writes when possible.
- Require a rollback or recovery plan for risky changes.
- Treat RLS and policy changes as high-risk.
- Keep a visible `DB Safety Log` in the chat.

## Repository Layout

```text
database-guardian/
  SKILL.md                         # Main skill instructions for agents
  agents/openai.yaml               # Codex/OpenAI skill metadata
  references/
    agent-adapters.md              # Setup notes for Codex, Claude, Cursor, Kimi
    approval-templates.md          # Reusable approval prompts
    risk-patterns.md               # Dangerous SQL and command patterns
  scripts/
    scan_sql_risk.py               # Simple SQL/command risk scanner
```

## Install To A Shared Skill Directory

Recommended shared install path:

```bash
mkdir -p ~/.config/agents/skills
git clone <repo-url> ~/.config/agents/skills/database-guardian
```

On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.config\agents\skills"
git clone <repo-url> "$HOME\.config\agents\skills\database-guardian"
```

Replace `<repo-url>` with the public GitHub URL after you publish the repo.

## Use With Codex

Option 1, copy or clone into Codex skills:

```bash
mkdir -p ~/.codex/skills
git clone <repo-url> ~/.codex/skills/database-guardian
```

Option 2, reference the shared skill from a project `AGENTS.md`:

```markdown
## Database Safety

For database-sensitive work, follow Database Guardian:
`~/.config/agents/skills/database-guardian/SKILL.md`

Use read-only investigation by default. Do not mutate, delete, null out, reset, migrate, or weaken database security without explicit user approval.
```

Then ask Codex:

```text
Use $database-guardian for this database task.
```

## Use With Claude

Clone or copy the repo into Claude's skills directory:

```bash
mkdir -p ~/.claude/skills
git clone <repo-url> ~/.claude/skills/database-guardian
```

Then ask Claude:

```text
Use the database-guardian skill for this SQL migration.
```

## Use With Cursor

Create this file in your project:

```text
.cursor/rules/database-guardian.mdc
```

Add:

```markdown
---
description: Use Database Guardian for database-sensitive work.
globs:
alwaysApply: false
---

For SQL, migrations, Supabase, Prisma, Drizzle, seed data, RLS policies, schema changes, or database commands, follow the portable skill at:

`~/.config/agents/skills/database-guardian/SKILL.md`

Use read-only investigation by default. Require explicit approval before writes, migrations, deletes, nulling values, resets, or RLS/security changes.
```

You can also add the same instruction as a Cursor User Rule for global use.

## Use With Kimi

Install to the shared skill directory:

```bash
git clone <repo-url> ~/.config/agents/skills/database-guardian
```

If your Kimi setup supports custom skill directories, point it at:

```text
~/.config/agents/skills
```

Then ask:

```text
Use database-guardian for this database task.
```

## Use With Any Agent

If your agent does not have native skills, add this to its global rules or project instructions:

```text
For database-sensitive work, follow Database Guardian from:
~/.config/agents/skills/database-guardian/SKILL.md

Use read-only investigation by default. Do not mutate data, run migrations, reset databases, delete records, set values to NULL, or change RLS/security without explicit user approval.
```

## Recommended Activation Prompt

At the start of any database-sensitive session, say:

```text
Activate database-guardian strict mode for this session.
Use read-only investigation by default.
Before any write, migration, seed change, RLS change, delete, reset, or NULL backfill, show me the exact SQL/command, environment, affected rows, risk level, and rollback plan, then wait for my explicit approval.
```

## Read-Only Mode

The skill allows safe read-only work.

Allowed examples:

```sql
SELECT COUNT(*) FROM table_name;
SELECT id, status, created_at FROM table_name ORDER BY created_at DESC LIMIT 20;
EXPLAIN SELECT ...;
SHOW ...;
```

The agent should avoid:

```sql
SELECT * FROM users;
SELECT * FROM customers;
```

Especially on production or sensitive tables.

## Database Detection

If a project might have a database, the agent should check safe local signals before deciding:

```text
supabase/
prisma/
drizzle/
migrations/
schema.sql
schema.prisma
drizzle.config.*
.env
.env.local
.env.example
```

Environment files are allowed for detection, but secrets must not be printed.

Database signal examples:

```text
SUPABASE_URL
NEXT_PUBLIC_SUPABASE_URL
SUPABASE_PROJECT_ID
SUPABASE_DB_URL
DATABASE_URL
POSTGRES_URL
PRISMA_DATABASE_URL
DIRECT_URL
```

For Supabase, a URL like this proves a Supabase project exists:

```text
https://<project-ref>.supabase.co
```

But it does not prove whether the project is production, staging, or dev. If the agent cannot prove the environment is local/dev, Database Guardian should use `PRODUCTION_SAFE`.

Important:

```text
Agents should never print service-role keys, passwords, tokens, full connection strings, or private .env contents into chat.
```

## Approval Examples

Vague approval should not be enough for risky work:

```text
ok
go ahead
yes
```

For high-risk actions, approve with exact wording:

```text
YES, run this migration on local.
YES, update 37 rows in kitchen_brand_schedules on local.
YES, delete rows from checklist_runs where id in (...).
YES, drop column old_status from table_name.
```

For critical destructive actions, require stronger confirmation:

```text
YES, I understand this may be irreversible. Delete rows from checklist_runs where id in (...) on local.
```

## SQL Risk Scanner

Run the included scanner against migrations, seed files, or SQL snippets:

```bash
python scripts/scan_sql_risk.py path/to/migration.sql
```

Scan stdin:

```bash
echo "DELETE FROM users;" | python scripts/scan_sql_risk.py
```

Example output:

```text
[CRITICAL] Deletes rows. Matched: DELETE FROM
```

The scanner is a warning tool. It does not replace human review or explicit approval.

## Keep The Skill Updated

Pull updates occasionally:

```bash
cd ~/.config/agents/skills/database-guardian
git pull
```

If you copied the skill into multiple agent directories, update each copy or replace copies with pointers in agent/project instructions.

## License

MIT
