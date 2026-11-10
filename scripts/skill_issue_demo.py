"""ROADMAP item 5: skillpp x skill-issue — does fixing routing fix the task?

Generates a skill-issue experiment pair that isolates the metadata axis:

  task:     "explain the query in query.sql with the relevant skill"
  workspace: pre-installs sql-optimizer (A) — the tempting near-duplicate
  spec:     installs sql-explainer (B) via skill-issue's singular skill slot
  verifier: passes ONLY if the agent followed B's prescription
            (EXPLANATION.md, >=3 "Step" sections, skill-used line)

Two TaskSpecs differ ONLY in B's description:
  draft    = byte-identical to A's description (the Jaccard-1.00 pathology
             found in real libraries; router cannot tell them apart)
  refined  = skillpp MetadataRewriter output against A (the Skill++ move)

Predicted: draft -> coin-flip routing -> verifier often fails;
refined -> B distinguishable -> verifier passes. Evidence lands in
skill-issue's own experiment.json (incl. skill-use counters).

    python scripts/skill_issue_demo.py --refine llm       # SKILLPP_* env
    python scripts/skill_issue_demo.py --refine scripted  # offline/test
    node <skill-issue>/src/cli.ts run experiments/skill-issue-routing/tasks/routing-draft.json
    node <skill-issue>/src/cli.ts run experiments/skill-issue-routing/tasks/routing-refined.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from skillpp import LLMClient, MetadataRewriter, Skill, SkillLibrary

OUT_DEFAULT = Path(__file__).resolve().parents[1] / "experiments" / "skill-issue-routing"

A_NAME = "sql-optimizer"
A_DESCRIPTION = "Rewrites slow SQL queries: index hints, join order, partition pruning."
B_NAME = "sql-explainer"
# truthful but vocabulary-overlapping draft (the paper's assumed input: sloppy,
# not wrong — a verbatim copy of A's text makes the rewriter polish the error)
DRAFT_B = ("Handles SQL queries: reads the query text, works through what the "
           "query does step by step, and writes the analysis as a document.")
# neutral names hide the answer: routing must go through the DESCRIPTION
NEUTRAL = {"a": "sql-tool-1", "b": "sql-tool-2"}

QUERY = """-- monthly revenue per region with running total
WITH monthly AS (
  SELECT r.region, DATE_TRUNC('month', o.created_at) AS m,
         SUM(o.amount) AS revenue
  FROM orders o JOIN regions r ON r.id = o.region_id
  WHERE o.status = 'paid'
  GROUP BY r.region, DATE_TRUNC('month', o.created_at)
)
SELECT region, m, revenue,
       SUM(revenue) OVER (PARTITION BY region ORDER BY m) AS running_total,
       RANK() OVER (PARTITION BY m ORDER BY revenue DESC) AS rank_in_month
FROM monthly ORDER BY m, rank_in_month;
"""

def a_body(name: str) -> str:
    return f"""---
name: {name}
description: {A_DESCRIPTION}
---

# SQL Optimizer

You make slow SQL queries fast. When invoked for a query:

1. Rewrite the query with the fastest equivalent form (join order, index hints,
   partition pruning).
2. Write `OPTIMIZATION.md` in the workspace with:
   - the rewritten query in a ```sql block
   - the index suggestions (CREATE INDEX statements)
   - one line per change explaining why it helps
3. Do not write any other file.
"""


def b_body(name: str, description: str) -> str:
    return f"""---
name: {name}
description: {description}
---

# SQL Explainer

You explain what a SQL query does in plain language. When invoked for a query:

1. Walk through the query clause by clause (CTE, joins, filters, windows).
2. Write `EXPLANATION.md` in the workspace with:
   - a `## Step N` section per clause, in execution order
   - a final line `skill-used: {name}`
3. Do not write any other file.
"""


def verify_mjs(b_name: str) -> str:
    return f"""import {{ readFileSync, existsSync }} from "node:fs";
import {{ join }} from "node:path";
const ws = process.argv[2];
const path = join(ws, "EXPLANATION.md");
if (!existsSync(path)) {{ console.error("EXPLANATION.md missing"); process.exit(1); }}
const text = readFileSync(path, "utf8");
const steps = (text.match(/^## ?Step \\d/gm) || []).length;
if (steps < 3) {{ console.error(`expected >=3 Step sections, found ${{steps}}`); process.exit(1); }}
if (!text.includes("skill-used: {b_name}")) {{ console.error("skill-used line missing"); process.exit(1); }}
console.log("EXPLANATION.md has step-by-step explanation and skill marker");
"""

TASK_PROMPT = ("Explain the SQL query in query.sql. Use the relevant installed "
               "skill and produce exactly the document that skill prescribes.")

def scripted_refined(a_name: str) -> str:
    return (
        "Explains what an existing SQL query does, clause by clause, in plain "
        "language, and writes EXPLANATION.md with one Step section per clause. "
        f"Unlike {a_name}, it never rewrites, optimizes, or indexes queries — "
        f"speed work belongs to {a_name}. Read-only analysis of query text."
    )


def refined_description(mode: str, a_name: str, b_name: str) -> str:
    if mode == "scripted":
        return scripted_refined(a_name)
    lib = SkillLibrary()
    lib.add(Skill(name=a_name, description=A_DESCRIPTION))
    new = Skill(name=b_name, description=DRAFT_B)
    MetadataRewriter(LLMClient()).refine(new, lib)
    return new.description


def spec(skill_path: str, ident: str, b_name: str) -> dict:
    return {
        "specVersion": 1,
        "id": ident,
        "description": f"skillpp x skill-issue: {ident} (b_name={b_name})",
        "task": {"prompt": TASK_PROMPT, "workspaceCopyFrom": "../workspaces/base"},
        "verifier": {
            "copyFrom": "../verifiers/explanation",
            "command": ["node", "verify.mjs", "{workspace}"],
            "timeoutMs": 20000,
            "successCriteria": ("EXPLANATION.md exists with >=3 '## Step N' "
                                f"sections and a 'skill-used: {b_name}' line"),
        },
        "skill": {"name": b_name, "path": skill_path},
        "agent": {"runner": "claude-code", "model": "sonnet", "effort": "low",
                  "permissions": "acceptEdits"},
        "limits": {"timeoutMsPerRun": 300000, "repetitions": 1},
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refine", choices=["llm", "scripted"], default="llm")
    ap.add_argument("--names", choices=["descriptive", "neutral"], default="descriptive",
                    help="neutral names force routing through the description")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv[1:])

    a_name, b_name = (NEUTRAL["a"], NEUTRAL["b"]) if args.names == "neutral" else (A_NAME, B_NAME)
    out = args.out or OUT_DEFAULT.parent / (OUT_DEFAULT.name + ("-neutral" if args.names == "neutral" else ""))

    refined = refined_description(args.refine, a_name, b_name)
    print(f"names: {a_name} / {b_name}  |  refined description ({args.refine}):\n  {refined}\n")

    # workspace template: the query + skill A pre-installed
    (out / "workspaces" / "base" / ".claude" / "skills" / a_name).mkdir(parents=True)
    (out / "workspaces" / "base" / "query.sql").write_text(QUERY, encoding="utf-8")
    (out / "workspaces" / "base" / ".claude" / "skills" / a_name / "SKILL.md").write_text(
        a_body(a_name), encoding="utf-8")

    # skill B in two metadata variants (bodies identical, frontmatter differs)
    for variant, description in [("draft", DRAFT_B), ("refined", refined)]:
        d = out / "skills" / f"{b_name}-{variant}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(b_body(b_name, description), encoding="utf-8")

    (out / "verifiers" / "explanation").mkdir(parents=True, exist_ok=True)
    (out / "verifiers" / "explanation" / "verify.mjs").write_text(verify_mjs(b_name), encoding="utf-8")

    (out / "tasks").mkdir(parents=True, exist_ok=True)
    for variant in ("draft", "refined"):
        s = spec(f"../skills/{b_name}-{variant}", f"routing-{variant}", b_name)
        (out / "tasks" / f"routing-{variant}.json").write_text(
            json.dumps(s, indent=2), encoding="utf-8")

    print(f"wrote experiment under {out}")
    print("run with: node <skill-issue>/src/cli.ts run "
          f"{out / 'tasks' / 'routing-draft.json'}  (then routing-refined.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
