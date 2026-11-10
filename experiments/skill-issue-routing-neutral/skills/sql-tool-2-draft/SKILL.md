---
name: sql-tool-2
description: Handles SQL queries: reads the query text, works through what the query does step by step, and writes the analysis as a document.
---

# SQL Explainer

You explain what a SQL query does in plain language. When invoked for a query:

1. Walk through the query clause by clause (CTE, joins, filters, windows).
2. Write `EXPLANATION.md` in the workspace with:
   - a `## Step N` section per clause, in execution order
   - a final line `skill-used: sql-tool-2`
3. Do not write any other file.
