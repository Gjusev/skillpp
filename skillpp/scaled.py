"""Scaled benchmark fixtures: 12 domains, 24 sessions, 36-skill final library.

ROADMAP item 2. Structure per domain: one base skill plus two variants whose
DRAFT descriptions deliberately share the domain's vocabulary (no exclusions
stated — the interference condition). Sessions interleave domains, so the
first 12 add one sibling per domain and the last 12 add a second (three-way
crowding — accuracy should decay as the library grows).

Deterministic: no randomness, no timestamps — same fixtures every run.
Caveat for honest reporting: probes are authored next to their skills, which
favors the mechanism; they are generated, not human-elicited.
"""

from __future__ import annotations

from .bench import Session
from .types import Skill

# (name, draft description, domain_tags, [3 probe queries])
_DOMAINS: list[dict] = [
    {
        "base": ("sql-optimizer", "Rewrites slow SQL queries: index hints, join order, partition pruning.",
                 ("sql", "performance"),
                 ["make this slow join query faster",
                  "why is my report query taking minutes",
                  "add indexes to speed up my select"]),
        "variants": [
            ("sql-explainer", "Explains what a SQL query does, step by step, in plain language.",
             ("sql", "explainability"),
             ["explain what this query does in plain words",
              "walk me through this select statement",
              "what does this nested subquery return"]),
            ("sql-migrator", "Converts SQL queries between database dialects, rewriting syntax for the target engine.",
             ("sql", "migration"),
             ["convert this oracle query to postgres",
              "rewrite this mysql script for sql server",
              "translate this query to bigquery sql"]),
        ],
    },
    {
        "base": ("pdf-redactor", "Removes personal data from PDF files permanently, with verification.",
                 ("pdf", "privacy"),
                 ["remove the iban from this pdf",
                  "black out patient names in this scan",
                  "strip the addresses out of this contract"]),
        "variants": [
            ("pdf-signature-check", "Checks whether a PDF file has digital signatures and whether they are valid.",
             ("pdf", "signatures"),
             ["is this signed pdf valid",
              "check the signature on this contract",
              "does this document have valid signatures"]),
            ("pdf-watermarker", "Stamps text watermarks across PDF pages and reports which pages were changed.",
             ("pdf", "watermark"),
             ["add a draft watermark to every page",
              "stamp confidential on this pdf",
              "put a review watermark on the appendix pages"]),
        ],
    },
    {
        "base": ("email-triage", "Classifies inbound support email by intent, urgency and language.",
                 ("email", "triage"),
                 ["sort incoming customer emails by urgency",
                  "label these messages as complaint or renewal",
                  "which of these mails need immediate reply"]),
        "variants": [
            ("email-drafter", "Drafts replies to customer emails following the support tone guide.",
             ("email", "writing"),
             ["write a reply to this angry customer",
              "draft an apology email for the delay",
              "answer this billing question politely"]),
            ("email-digest", "Summarizes long email threads into short bullet digests with action items.",
             ("email", "summary"),
             ["summarize this 40-message thread",
              "what was decided in this email chain",
              "give me the action items from these mails"]),
        ],
    },
    {
        "base": ("csv-cleaner", "Cleans CSV files: fixes quoting, strips whitespace, normalizes column names.",
                 ("csv", "cleaning"),
                 ["fix the broken quoting in this csv",
                  "clean up messy column headers",
                  "strip whitespace from this export"]),
        "variants": [
            ("csv-merger", "Merges several CSV files into one, matching rows by a key column.",
             ("csv", "merge"),
             ["combine these three exports into one file",
              "join these csv files on customer id",
              "merge the january and february csvs"]),
            ("csv-deduper", "Finds duplicate rows in CSV files and reports which columns matched.",
             ("csv", "dedup"),
             ["find the duplicate rows in this sheet",
              "which of these records are the same customer",
              "remove double entries from this csv"]),
        ],
    },
    {
        "base": ("git-bisector", "Runs git bisect automatically to find the commit that introduced a bug.",
                 ("git", "debugging"),
                 ["find the commit that broke the build",
                  "bisect this regression",
                  "which commit introduced the crash"]),
        "variants": [
            ("git-conflict-resolver", "Explains merge conflicts in a branch and suggests resolution for each hunk.",
             ("git", "merge"),
             ["help me resolve these merge conflicts",
              "why is this hunk conflicting",
              "suggest a resolution for this rebase conflict"]),
            ("git-changelog", "Generates a changelog from commit history between two refs.",
             ("git", "release"),
             ["write release notes from these commits",
              "changelog since the last tag",
              "summarize commits between v1 and v2"]),
        ],
    },
    {
        "base": ("log-parser", "Parses raw server logs into structured records with timestamp and level.",
                 ("logs", "parsing"),
                 ["parse these nginx logs into json",
                  "structure this syslog dump",
                  "extract timestamp and level from this log"]),
        "variants": [
            ("log-anomaly", "Scans parsed logs for unusual patterns and spikes, flagging suspicious lines.",
             ("logs", "anomaly"),
             ["anything strange in last night's logs",
              "find the anomaly before the crash",
              "flag unusual error spikes in this log"]),
            ("log-tailer", "Watches a live log stream and prints lines matching a pattern as they arrive.",
             ("logs", "streaming"),
             ["follow this log and show timeouts",
              "tail the app log for stack traces",
              "stream only warning lines from this service log"]),
        ],
    },
    {
        "base": ("api-mocker", "Generates mock API servers from an OpenAPI spec with fake but realistic responses.",
                 ("api", "mocking"),
                 ["mock this openapi spec for testing",
                  "spin up a fake server for this api",
                  "stub these endpoints with sample data"]),
        "variants": [
            ("api-diff", "Compares two OpenAPI specs and reports breaking changes for clients.",
             ("api", "versioning"),
             ["is this api change breaking",
              "diff the old and new openapi specs",
              "what endpoints changed between versions"]),
            ("api-loadtest", "Sends configurable load against an API endpoint and reports latency percentiles.",
             ("api", "load"),
             ["load test this endpoint at 100 rps",
              "measure p99 latency of the checkout api",
              "stress the search endpoint briefly"]),
        ],
    },
    {
        "base": ("regex-builder", "Builds a regular expression from a plain-language description and test strings.",
                 ("regex", "generation"),
                 ["regex for german license plates",
                  "build a pattern matching these examples",
                  "write a regex for invoice numbers"]),
        "variants": [
            ("regex-explainer", "Explains a given regular expression token by token in plain language.",
             ("regex", "explainability"),
             ["explain this regex to me",
              "what does this pattern match",
              "decode this cryptic regular expression"]),
            ("regex-tester", "Runs a regex against a list of test strings and reports matches and capture groups.",
             ("regex", "testing"),
             ["test this pattern against my samples",
              "which of these strings match the regex",
              "show capture groups for each match"]),
        ],
    },
    {
        "base": ("cron-scheduler", "Writes and validates cron expressions from a plain-language schedule.",
                 ("cron", "scheduling"),
                 ["cron for every tuesday at 3am",
                  "validate this cron expression",
                  "schedule a job twice a day"]),
        "variants": [
            ("cron-explainer", "Explains what a cron expression does, in plain language, including quirks.",
             ("cron", "explainability"),
             ["what does this cron actually run",
              "explain this five-field cron",
              "when will this schedule next fire"]),
            ("cron-migrator", "Converts cron expressions between formats: standard five-field, quartz, and systemd timers.",
             ("cron", "migration"),
             ["convert this cron to quartz format",
              "turn this cron into a systemd timer",
              "rewrite this quartz trigger as standard cron"]),
        ],
    },
    {
        "base": ("doc-summarizer", "Summarizes long text documents into a short abstract with key points.",
                 ("docs", "summary"),
                 ["summarize this 50-page report",
                  "key points of this whitepaper",
                  "shorten this spec to one paragraph"]),
        "variants": [
            ("doc-translator", "Translates documents between languages, keeping formatting and terminology consistent.",
             ("docs", "translation"),
             ["translate this manual to german",
              "convert this doc to spanish",
              "translate the readme to japanese"]),
            ("doc-critiquer", "Reviews a draft document for clarity, structure, and missing sections, with line comments.",
             ("docs", "review"),
             ["review my draft design doc",
              "what sections are missing from this spec",
              "critique the structure of this proposal"]),
        ],
    },
    {
        "base": ("image-resizer", "Resizes and crops images in bulk to target dimensions and formats.",
                 ("images", "resize"),
                 ["resize these photos to 1024 wide",
                  "crop all images to square",
                  "convert this folder of pngs to webp at half size"]),
        "variants": [
            ("image-captioner", "Generates alt-text captions for images using a vision model.",
             ("images", "accessibility"),
             ["alt text for these product photos",
              "caption this screenshot for accessibility",
              "describe what is in this chart image"]),
            ("image-ocr", "Extracts text from images and scanned PDFs with position information.",
             ("images", "ocr"),
             ["read the text in this receipt photo",
              "ocr this scanned form",
              "extract the printed words from this screenshot"]),
        ],
    },
    {
        "base": ("slide-builder", "Creates presentation slides from an outline, applying the corporate template.",
                 ("slides", "generation"),
                 ["make slides from this outline",
                  "turn these bullets into a deck",
                  "build the quarterly review presentation"]),
        "variants": [
            ("slide-auditor", "Checks a slide deck for overflowing text, unreadable contrast, and missing speaker notes.",
             ("slides", "review"),
             ["check this deck for text overflow",
              "audit my slides for contrast issues",
              "which slides are missing notes"]),
            ("slide-exporter", "Exports slide decks to PDF, images, or HTML handouts with speaker notes included.",
             ("slides", "export"),
             ["export this deck to pdf with notes",
              "turn these slides into png images",
              "make an html handout of this deck"]),
        ],
    },
]


def _skill(entry: tuple) -> Skill:
    name, desc, tags, _queries = entry
    return Skill(name=name, description=desc, domain_tags=tags)


def scaled_base_skills() -> list[Skill]:
    return [_skill(d["base"]) for d in _DOMAINS]


def scaled_sessions() -> list[Session]:
    """24 sessions: sessions 1-12 add each domain's variant 1, 13-24 variant 2.

    Probes per session: the new variant's 3 queries + the domain base skill's
    3 (must the old skill survive its new sibling?) + up to 2 regression
    probes: the domain's other variant (once it exists) and the previous
    session's new skill (session 1 has neither). 179 probes in total.
    """
    sessions: list[Session] = []
    added: list[tuple[str, str]] = []  # (name, first query) of prior variants
    for i in range(24):
        domain = _DOMAINS[i % 12]
        variant = domain["variants"][0 if i < 12 else 1]
        base_name, _bd, _bt, base_queries = domain["base"]
        v_name, _vd, _vt, v_queries = variant
        regression: list[tuple[str, str]] = []
        # the domain's other variant, if already added
        other = domain["variants"][1 if i < 12 else 0]
        if other[0] in {a[0] for a in added}:
            regression.append((other[3][0], other[0]))
        if added:
            regression.append((added[(i - 1) % len(added)][1], added[(i - 1) % len(added)][0]))
        sessions.append(Session(
            new_skill=_skill(variant),
            probes=[(q, v_name) for q in v_queries] + [(q, base_name) for q in base_queries],
            regression_probes=regression,
        ))
        added.append((v_name, v_queries[0]))
    return sessions
