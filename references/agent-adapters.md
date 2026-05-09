# Agent Adapters

Use this skill as the source of truth, then point each agent at the same folder.

## Shared Location

Recommended shared install path:

```text
~/.config/agents/skills/database-guardian/
```

On Windows:

```text
C:\Users\<you>\.config\agents\skills\database-guardian\
```

## Codex

Copy or mirror the skill to:

```text
~/.codex/skills/database-guardian/
```

Or add a repo-level `AGENTS.md` pointer:

```markdown
## Database Safety

For database-sensitive work, use:
`~/.config/agents/skills/database-guardian/SKILL.md`
```

## Claude

Copy or mirror the skill to:

```text
~/.claude/skills/database-guardian/
```

## Kimi

Kimi can discover shared skills from:

```text
~/.config/agents/skills/database-guardian/
```

It can also load additional directories with `--skills-dir`.

## Cursor

Create `.cursor/rules/database-guardian.mdc`:

```markdown
---
description: Use Database Guardian for database-sensitive work.
globs:
alwaysApply: false
---

For SQL, migrations, Supabase, Prisma, Drizzle, seed data, RLS policies, schema changes, or database commands, follow the portable skill at:

`~/.config/agents/skills/database-guardian/SKILL.md`
```

For global use, add a Cursor User Rule:

```text
For database-sensitive work, follow Database Guardian from ~/.config/agents/skills/database-guardian/SKILL.md. Use read-only mode by default and require explicit approval before writes, migrations, deletes, nulling values, resets, or RLS/security changes.
```

## Repo-Level AGENTS.md

Add this to projects that need protection:

```markdown
## Database Safety

For database-sensitive work, follow Database Guardian:
`~/.config/agents/skills/database-guardian/SKILL.md`

Use read-only investigation by default. Do not mutate, delete, null out, reset, migrate, or weaken database security without explicit user approval.
```
