"""
Extract structured fields from raw founder-update emails using Claude.

Reads the JSON produced by pull_gmail.py (one entry per email, with the raw
body in `_raw_body` and structured fields like current_arr_usd left null) and
fills the structured fields by calling Claude on each email body.

Why an LLM for this: founder updates don't follow a fixed template. ARR might
be "crossed $16M ARR" in one email and "ended Q1 at $1.3M MRR ($15.6M
annualized)" in another. A regex won't catch both; an LLM will.

Requires ANTHROPIC_API_KEY. Setup:

    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Usage:

    python parse_emails_with_llm.py
    python parse_emails_with_llm.py --input ../sample_inputs/founder_quarterly_email.json
    python parse_emails_with_llm.py --reparse  # re-parse even already-filled entries

Cost note: the extraction system prompt is cached (~1500 tokens) so cost per
email after the first is mostly the email body itself. At ~30 emails per fund
per year, total cost per refresh is typically under $0.10.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "sample_inputs" / "founder_quarterly_email.json"

MODEL = "claude-sonnet-4-6"

EXTRACTION_TOOL = {
    "name": "record_founder_update",
    "description": (
        "Record the structured fields parsed from a founder quarterly update email. "
        "Use null for any field the email doesn't mention or doesn't have enough info to fill."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "company": {
                "type": ["string", "null"],
                "description": "Company name as referenced in the email. Null if unclear.",
            },
            "quarter": {
                "type": ["string", "null"],
                "description": "Reporting period like '2026 Q1' or 'Final notice'. Null if not stated.",
            },
            "current_arr_usd": {
                "type": ["integer", "null"],
                "description": (
                    "Current annual recurring revenue in USD. Convert MRR to ARR (×12) if needed. "
                    "Use the most recent figure. Null if the email doesn't state revenue."
                ),
            },
            "yoy_growth_pct": {
                "type": ["number", "null"],
                "description": (
                    "Year-over-year growth rate as a percentage. E.g. 78 means 78% YoY. "
                    "Negative for shrinking. Null if not stated."
                ),
            },
            "runway_months": {
                "type": ["integer", "null"],
                "description": "Stated runway in months. Null if not mentioned. 0 if shutdown.",
            },
            "raise_planned": {
                "type": ["string", "null"],
                "description": (
                    "Short description of any planned or completed raise — round name, target size, "
                    "expected timing or close date. Null if no raise mentioned."
                ),
            },
            "headcount": {
                "type": ["integer", "null"],
                "description": "Current full-time headcount. Null if not stated.",
            },
            "highlights": {
                "type": ["array", "null"],
                "items": {"type": "string"},
                "description": "Bullet points of positive signals (revenue milestones, customer wins, launches). Null if none.",
            },
            "risk_flags": {
                "type": ["array", "null"],
                "items": {"type": "string"},
                "description": "Concrete risk signals (founder departure, churn, lost customer, lawsuit, etc.). Null if none.",
            },
            "ask": {
                "type": ["string", "null"],
                "description": "The ask at the end of the email (intros, hiring, capital, advice). Null if no specific ask.",
            },
        },
        "required": [
            "company",
            "quarter",
            "current_arr_usd",
            "yoy_growth_pct",
            "runway_months",
            "raise_planned",
            "headcount",
            "highlights",
            "risk_flags",
            "ask",
        ],
    },
}

SYSTEM_PROMPT = """You are an LP-portfolio analytics assistant. Your job is to parse founder quarterly update emails into structured signals that feed downstream portfolio modeling.

Rules:
- Pull what's actually stated in the email. Do NOT infer numbers not mentioned.
- If a metric is given as a range, use the midpoint.
- If MRR is stated instead of ARR, multiply by 12 to get ARR.
- If the email mentions multiple revenue points (e.g., "started the year at $5M, now at $9M"), use the most recent.
- For yoy_growth_pct: 78 means 78% YoY growth. Negative for contraction. If only "doubled YoY" stated, use 100. If only stated as multiplier ("3× YoY"), convert to percent (200%).
- If runway is stated as "more than 24 months" or "~2 years", use 24.
- Always call the record_founder_update tool exactly once with all 10 fields populated (using null when the email doesn't provide enough info).
- Be concise in highlights and risk_flags — one short sentence each. No more than 5 of each.

You are processing emails one at a time. Do not editorialize, do not speculate about what's missing — just record what's there."""


def get_client():
    try:
        import anthropic
    except ImportError:
        sys.exit(
            "Missing anthropic package. Install:\n"
            "    pip install -r pipeline/requirements.txt"
        )

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "ANTHROPIC_API_KEY not set. Get one at https://console.anthropic.com/\n"
            "Then: export ANTHROPIC_API_KEY=sk-ant-..."
        )

    return anthropic.Anthropic(api_key=api_key)


def is_already_parsed(entry: dict) -> bool:
    """An entry is considered parsed if any structured field is non-null."""
    structured_fields = [
        "current_arr_usd",
        "yoy_growth_pct",
        "runway_months",
        "raise_planned",
        "headcount",
        "highlights",
        "risk_flags",
    ]
    return any(entry.get(f) is not None for f in structured_fields)


def extract_fields(client, email_body: str, subject: str | None) -> dict:
    """Call Claude and return the parsed structured fields."""
    user_content = f"Subject: {subject or '(no subject)'}\n\n---\n\n{email_body}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "record_founder_update"},
        messages=[{"role": "user", "content": user_content}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "record_founder_update":
            return block.input

    raise RuntimeError(
        f"Claude did not call the extraction tool. stop_reason={response.stop_reason}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Path to raw emails JSON (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        help="Output path. Defaults to overwriting --input.",
    )
    parser.add_argument(
        "--reparse",
        action="store_true",
        help="Re-parse even entries that already have structured fields filled.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Only process the first N unparsed entries (useful for testing).",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    entries = json.loads(input_path.read_text())
    client = get_client()

    processed = 0
    cache_reads = 0
    cache_writes = 0
    for i, entry in enumerate(entries):
        if not args.reparse and is_already_parsed(entry):
            continue
        if args.limit is not None and processed >= args.limit:
            break

        raw_body = entry.get("_raw_body")
        if not raw_body:
            print(f"  [{i+1}] no _raw_body — skipping")
            continue

        subject = entry.get("subject")
        print(f"  [{i+1}] parsing: {subject or '(no subject)'}", flush=True)

        try:
            fields = extract_fields(client, raw_body, subject)
        except Exception as exc:
            print(f"    ERROR: {exc}")
            continue

        for k, v in fields.items():
            entry[k] = v
        processed += 1

    output_path.write_text(json.dumps(entries, indent=2))
    print(f"\nProcessed {processed} email{'s' if processed != 1 else ''} → {output_path}")


if __name__ == "__main__":
    main()
