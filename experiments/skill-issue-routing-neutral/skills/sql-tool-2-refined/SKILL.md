---
name: sql-tool-2
description: Reads SQL query text and produces a step-by-step written explanation of what the query does, output as an analysis document. Unlike sql-tool-1, which rewrites slow queries to improve performance, this skill only explains existing queries and never modifies them. It does not cover query rewriting, optimization, index hints, join-order changes, partition pruning, query execution, or SQL generation.
---

# SQL Explainer

You explain what a SQL query does in plain language. When invoked for a query:

1. Walk through the query clause by clause (CTE, joins, filters, windows).
2. Write `EXPLANATION.md` in the workspace with:
   - a `## Step N` section per clause, in execution order
   - a final line `skill-used: sql-tool-2`
3. Do not write any other file.
