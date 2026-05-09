#!/usr/bin/env python3
"""Scan SQL or command text for database safety risk patterns."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PATTERNS = [
    ("CRITICAL", r"\bdrop\s+database\b", "Drops an entire database."),
    ("CRITICAL", r"\bdrop\s+schema\b", "Drops a schema."),
    ("CRITICAL", r"\bdrop\s+table\b", "Drops a table."),
    ("CRITICAL", r"\balter\s+table\b[\s\S]*?\bdrop\s+column\b", "Drops a column."),
    ("CRITICAL", r"\btruncate\b", "Deletes all rows from a table."),
    ("CRITICAL", r"\bdelete\s+from\b", "Deletes rows."),
    ("CRITICAL", r"\bdisable\s+row\s+level\s+security\b", "Disables RLS."),
    ("CRITICAL", r"\bdrop\s+policy\b", "Drops an RLS policy."),
    ("CRITICAL", r"\bupdate\b[\s\S]*?\bset\b[\s\S]*?=\s*null\b", "Sets values to NULL."),
    ("HIGH", r"\bupdate\b", "Updates existing rows."),
    ("HIGH", r"\binsert\s+into\b", "Inserts rows."),
    ("HIGH", r"\bupsert\b", "Upserts rows."),
    ("HIGH", r"\bmerge\b", "Merges row changes."),
    ("HIGH", r"\balter\s+table\b", "Alters table structure."),
    ("HIGH", r"\bcreate\s+policy\b", "Creates an RLS policy."),
    ("HIGH", r"\balter\s+policy\b", "Alters an RLS policy."),
    ("HIGH", r"\bcreate\s+trigger\b", "Creates a trigger."),
    ("HIGH", r"\bset\s+not\s+null\b", "Adds a NOT NULL requirement."),
    ("HIGH", r"\bcreate\s+unique\s+index\b", "Adds uniqueness enforcement."),
    ("MEDIUM", r"\bselect\s+\*\s+from\b", "Reads all columns."),
    ("MEDIUM", r"\bexplain\s+analyze\b", "May execute an expensive query."),
    ("COMMAND", r"\bsupabase\s+db\s+reset\b", "Resets a Supabase database."),
    ("COMMAND", r"\bsupabase\s+db\s+push\b", "Pushes local schema to database."),
    ("COMMAND", r"\bsupabase\s+migration\s+up\b", "Runs Supabase migrations."),
    ("COMMAND", r"\bprisma\s+migrate\s+deploy\b", "Deploys Prisma migrations."),
    ("COMMAND", r"\bprisma\s+db\s+push\b", "Pushes Prisma schema."),
    ("COMMAND", r"\bdrizzle-kit\s+push\b", "Pushes Drizzle schema."),
]

WHERE_PATTERNS = [
    (r"\bwhere\s+true\b", "Broad predicate: WHERE true."),
    (r"\bwhere\s+1\s*=\s*1\b", "Broad predicate: WHERE 1 = 1."),
    (r"\bwhere\s+id\s+is\s+not\s+null\b", "Broad predicate: id IS NOT NULL."),
]


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def scan_text(label: str, text: str) -> list[tuple[str, int, str, str]]:
    findings: list[tuple[str, int, str, str]] = []
    for severity, pattern, message in PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            findings.append((severity, line_number(text, match.start()), message, match.group(0).strip()))
    for pattern, message in WHERE_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            findings.append(("HIGH", line_number(text, match.start()), message, match.group(0).strip()))
    findings.sort(key=lambda item: (item[1], item[0]))
    return findings


def read_inputs(paths: list[str]) -> list[tuple[str, str]]:
    if not paths:
        return [("<stdin>", sys.stdin.read())]
    inputs = []
    for raw_path in paths:
        path = Path(raw_path)
        inputs.append((str(path), path.read_text(encoding="utf-8")))
    return inputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan SQL or command text for database risk patterns.")
    parser.add_argument("paths", nargs="*", help="Files to scan. Reads stdin when omitted.")
    args = parser.parse_args()

    total = 0
    highest = "OK"
    rank = {"OK": 0, "MEDIUM": 1, "HIGH": 2, "COMMAND": 2, "CRITICAL": 3}

    for label, text in read_inputs(args.paths):
        findings = scan_text(label, text)
        if not findings:
            print(f"{label}: OK - no configured risk patterns found")
            continue
        print(f"{label}: {len(findings)} finding(s)")
        for severity, line, message, snippet in findings:
            total += 1
            if rank[severity] > rank[highest]:
                highest = severity
            print(f"  [{severity}] line {line}: {message} Matched: {snippet}")

    if total:
        print(f"\nRisk scan complete: {total} finding(s), highest severity: {highest}")
        return 2 if highest == "CRITICAL" else 1
    print("\nRisk scan complete: no findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
