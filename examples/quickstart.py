"""Quickstart: run the interference benchmark with a real LLM (rewriter + router).

Defaults to the Z.ai Coding Plan endpoint (flat subscription — no per-call
billing). Or point SKILLPP_BASE_URL anywhere OpenAI-compatible (e.g. Ollama:
SKILLPP_BASE_URL=http://localhost:11434/v1 SKILLPP_MODEL=qwen2.5:7b).
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # run without pip install

os.environ.setdefault("SKILLPP_BASE_URL", "https://api.z.ai/api/coding/paas/v4")
os.environ.setdefault("SKILLPP_MODEL", "glm-5.3-flash")

from skillpp import (
    InterferenceBench,
    LLMClient,
    MetadataRewriter,
    OpenAICompatRouter,
)
from skillpp.fixtures import base_skills, sessions

bench = InterferenceBench(base_skills(), OpenAICompatRouter(), MetadataRewriter(LLMClient()))
report = bench.run(sessions())
print(report.summary())
for s in report.sessions:
    print(f"\n[{s['new_skill']}] refined description:\n  {s['refined_description']}")
