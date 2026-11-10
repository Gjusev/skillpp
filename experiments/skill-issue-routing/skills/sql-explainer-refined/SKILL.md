---
name: sql-explainer
description: Explains SQL queries: breaks down a given query's logic, table relationships, filters, and execution-plan steps into plain language, flagging sections that look expensive. Read-only analysis: unlike sql-optimizer, it makes no changes to the query and produces no optimized version; route rewrite and tuning requests to sql-optimizer. Excludes: query rewriting, index hints, join reordering, partition pruning, query generation, and query execution.
---

# SQL Explainer

You explain what a SQL query does in plain language. When invoked for a query:

1. Walk through the query clause by clause (CTE, joins, filters, windows).
2. Write `EXPLANATION.md` in the workspace with:
   - a `## Step N` section per clause, in execution order
   - a final line `skill-used: sql-explainer`
3. Do not write any other file.
