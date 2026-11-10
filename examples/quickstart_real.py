"""Real-LLM run of InterferenceBench over the shipped sessions.

Unlike examples/quickstart.py this sets NO defaults: it uses whatever
SKILLPP_BASE_URL / SKILLPP_MODEL / SKILLPP_API_KEY say (per CONTINUE.md the
Z.ai Coding Plan endpoint). Writes results/first_run.json and prints the
before/after table plus the refined descriptions.

    export SKILLPP_BASE_URL="https://api.z.ai/api/coding/paas/v4"
    export SKILLPP_MODEL="glm-5.3-flash"
    export SKILLPP_API_KEY="<Z.ai key>"
    python examples/quickstart_real.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without pip install

from skillpp import (
    InterferenceBench,
    LLMClient,
    MetadataRewriter,
    OpenAICompatRouter,
)
from skillpp.fixtures import base_skills, sessions

llm = LLMClient()  # raises with instructions if the env vars are unset
print(f"router+rewriter model: {llm.model} @ {llm.base_url}")

bench = InterferenceBench(base_skills(), OpenAICompatRouter(llm), MetadataRewriter(llm))
report = bench.run(sessions())

print(report.summary())
for s in report.sessions:
    print(f"\n[{s['new_skill']}] refined description:\n  {s['refined_description']}")

out = Path(__file__).resolve().parents[1] / "results" / "first_run.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({
    "model": llm.model,
    "base_url": llm.base_url,
    "accuracy_before": report.accuracy_before,
    "accuracy_after": report.accuracy_after,
    "sessions": report.sessions,
}, indent=2))
print(f"\nwrote {out}")
