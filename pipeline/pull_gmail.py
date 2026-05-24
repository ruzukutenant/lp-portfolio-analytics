"""
Pull founder-update emails from a Gmail label into JSON.

This script handles the Google OAuth flow on first run (browser opens, you
grant gmail.readonly, token is cached to token.json) and on subsequent runs
just queries the label and writes JSON.

Output schema matches sample_inputs/founder_quarterly_email.json with raw
email body in `_raw_body` and structured fields (current_arr_usd, etc.) left
null. Run pipeline/parse_emails_with_llm.py afterward to fill those.

Setup: see docs/gmail_setup.md

Usage:
    python pull_gmail.py --label "lp/sahil-rolling"
    python pull_gmail.py --label "lp/sahil-rolling" --after 2026/01/01
    python pull_gmail.py --label "lp/sahil-rolling" --output ../sample_inputs/founder_quarterly_email.json
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime
from email import message_from_bytes
from email.policy import default as default_policy
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = REPO_ROOT / "sample_inputs" / "founder_quarterly_email.json"
CREDENTIALS_PATH = Path(os.environ.get("GMAIL_CREDENTIALS", REPO_ROOT / "credentials.json"))
TOKEN_PATH = Path(os.environ.get("GMAIL_TOKEN", REPO_ROOT / "token.json"))

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_service():
    """Authenticate and return a Gmail API service."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        sys.exit(
            "Missing Google API deps. Install:\n"
            "    pip install -r pipeline/requirements.txt\n"
            "See docs/gmail_setup.md for full setup."
        )

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                sys.exit(
                    f"No credentials.json found at {CREDENTIALS_PATH}.\n"
                    "See docs/gmail_setup.md for how to create OAuth credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())
        print(f"Saved auth token to {TOKEN_PATH}")

    return build("gmail", "v1", credentials=creds)


def get_label_id(service, label_name: str) -> str:
    """Look up a label's ID by name (e.g., 'lp/sahil-rolling')."""
    resp = service.users().labels().list(userId="me").execute()
    for label in resp.get("labels", []):
        if label["name"] == label_name:
            return label["id"]
    sys.exit(
        f"Label '{label_name}' not found.\n"
        "Create it in Gmail (Settings → Labels → Create new label) and add a "
        "filter that routes founder emails to it. See docs/gmail_setup.md."
    )


def list_messages(service, label_id: str, after: str | None = None) -> list[dict]:
    """List all message metadata for the given label."""
    query_parts = []
    if after:
        query_parts.append(f"after:{after}")
    query = " ".join(query_parts) if query_parts else None

    messages = []
    page_token = None
    while True:
        resp = (
            service.users()
            .messages()
            .list(
                userId="me",
                labelIds=[label_id],
                q=query,
                pageToken=page_token,
                maxResults=100,
            )
            .execute()
        )
        messages.extend(resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return messages


def extract_body(payload: dict) -> str:
    """Walk the MIME tree and return the best plain-text body we can find."""
    if not payload:
        return ""
    mime_type = payload.get("mimeType", "")
    body_data = payload.get("body", {}).get("data")
    if mime_type == "text/plain" and body_data:
        return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
    if mime_type.startswith("multipart/"):
        for part in payload.get("parts", []):
            text = extract_body(part)
            if text:
                return text
    if mime_type == "text/html" and body_data:
        html = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="replace")
        # Strip tags crudely; the LLM parser will handle real cleanup
        return re.sub(r"<[^>]+>", " ", html)
    return ""


def fetch_message(service, msg_id: str) -> dict:
    """Fetch one message in full and return a normalized dict."""
    msg = (
        service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    )
    headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
    body = extract_body(msg["payload"])

    return {
        "_gmail_id": msg_id,
        "_thread_id": msg.get("threadId"),
        "_raw_body": body.strip(),
        "company": None,
        "email_date": headers.get("date", ""),
        "quarter": None,
        "subject": headers.get("subject", ""),
        "from": headers.get("from", ""),
        "current_arr_usd": None,
        "yoy_growth_pct": None,
        "runway_months": None,
        "raise_planned": None,
        "headcount": None,
        "customer_metrics": None,
        "highlights": None,
        "risk_flags": None,
        "ask": None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", required=True, help="Gmail label name, e.g. 'lp/sahil-rolling'")
    parser.add_argument("--after", help="Only fetch messages after this date (YYYY/MM/DD)")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output JSON path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    service = get_service()
    label_id = get_label_id(service, args.label)
    metadata = list_messages(service, label_id, args.after)
    print(f"Found {len(metadata)} messages in label '{args.label}'", end="", flush=True)
    if args.after:
        print(f" after {args.after}", end="")
    print()

    results = []
    for i, m in enumerate(metadata, 1):
        msg = fetch_message(service, m["id"])
        results.append(msg)
        if i % 10 == 0 or i == len(metadata):
            print(f"  fetched {i}/{len(metadata)}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {len(results)} emails to {output_path}")
    print("Next: run `python pipeline/parse_emails_with_llm.py` to extract structured fields.")


if __name__ == "__main__":
    main()
