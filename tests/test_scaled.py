"""Offline tests: scaled fixtures (ROADMAP item 2) + the naive routers.

What is pinned here (all deterministic, no network):
- the scaled fixtures have a valid, stable shape;
- the paper's qualitative setup holds BEFORE refinement: routing accuracy
  decays as the library grows (MockRouter on draft metadata).
What is deliberately NOT asserted: that refinement helps. That depends on
the rewriter's text (template rewrites degrade lexical routers — they swap
draft vocabulary for boilerplate); the benefit claim is measured by the
real-LLM matrix runs in results/, not asserted offline.
"""

from skillpp import (
    InterferenceBench,
    MockRouter,
    TfidfRouter,
    scaled_base_skills,
    scaled_sessions,
)


def test_scaled_fixture_shape():
    base, sess = scaled_base_skills(), scaled_sessions()
    assert len(base) == 12
    assert len(sess) == 24
    names = {s.name for s in base} | {s.new_skill.name for s in sess}
    for s in sess:
        for _q, expected in s.probes + s.regression_probes:
            assert expected in names, f"probe targets unknown skill {expected}"
    # deterministic regeneration
    again = scaled_sessions()
    assert [s.new_skill.name for s in again] == [s.new_skill.name for s in sess]


def test_library_growth_induces_interference():
    """Routing accuracy on DRAFT metadata decays as sessions crowd the library."""
    report = InterferenceBench(scaled_base_skills(), MockRouter(), None).run(scaled_sessions())
    b = report.accuracy_before
    assert len(b) == 24
    half = len(b) // 2
    early = sum(b[:half]) / half
    late = sum(b[half:]) / (len(b) - half)
    assert late < early, f"expected decay: late {late:.2%} should be < early {early:.2%}"


def test_tfidf_router_deterministic_and_valid():
    router = TfidfRouter()
    skills = scaled_base_skills()
    r1 = router.route("translate this manual to german", skills)
    r2 = router.route("translate this manual to german", skills)
    assert r1.chosen == r2.chosen
    assert r1.chosen in {s.name for s in skills}
