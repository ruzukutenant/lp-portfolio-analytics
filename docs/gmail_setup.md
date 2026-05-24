# Gmail integration — setup and use

The pipeline can pull founder-update emails directly from Gmail and turn them into structured signals. Two scripts:

- `pipeline/pull_gmail.py` — auth + fetch emails from a Gmail label → JSON
- `pipeline/parse_emails_with_llm.py` — optional: enrich the raw emails with structured fields (ARR, growth, runway, etc.) via Claude

Why bother: founder quarterly updates are the single highest-value forward signal you get as an LP. The pipeline uses fields like `current_arr_usd`, `yoy_growth_pct`, and `runway_months` to calibrate scenario weights during the verification step. Manually retyping those numbers from email into JSON every quarter is the kind of task that quietly stops happening — automating it is what makes the methodology actually maintainable.

## At a glance

```
Gmail label "lp/<fund-name>"
   │
   │  pipeline/pull_gmail.py
   ▼
sample_inputs/founder_quarterly_email.json    (raw bodies in _raw_body, structured fields null)
   │
   │  pipeline/parse_emails_with_llm.py  (optional but recommended)
   ▼
sample_inputs/founder_quarterly_email.json    (structured fields filled in by Claude)
   │
   │  pipeline/emit_dashboard_json.py
   ▼
Dashboard renders updated signals
```

You can stop after step 1 and hand-fill the structured fields yourself. Step 2 is the one that makes the workflow stick.

---

## Part 1: Gmail OAuth setup (~10 minutes, one-time)

### 1. Create a Google Cloud project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown at the top → **New Project**
3. Name it something like "LP Portfolio Tools" (you only need this for the API access; it's not user-visible)
4. Click **Create**, wait ~10 seconds for it to provision, then make sure it's selected in the project dropdown

### 2. Enable the Gmail API

1. In the search bar at the top, search for "Gmail API"
2. Click the result → **Enable**
3. Wait for it to enable (a few seconds)

### 3. Configure the OAuth consent screen

1. Sidebar → **APIs & Services** → **OAuth consent screen**
2. Select **External** user type → **Create**
3. Fill in:
   - **App name**: "LP Portfolio Tools" (anything works)
   - **User support email**: your email
   - **Developer contact**: your email
4. Click **Save and Continue**
5. **Scopes**: click **Add or Remove Scopes**, search for "gmail.readonly", check `.../auth/gmail.readonly`, click **Update**
6. Click **Save and Continue**
7. **Test users**: click **Add Users**, add your own Gmail address (the account whose mail you want to read)
8. Click **Save and Continue** → **Back to Dashboard**

You don't need to publish the app — keeping it in "Testing" mode is fine for personal use.

### 4. Create OAuth credentials

1. Sidebar → **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. **Application type**: Desktop app
4. **Name**: anything (e.g., "lp-portfolio-cli")
5. Click **Create**
6. In the dialog that appears, click **Download JSON**
7. Move the downloaded file to the repo root and rename it to `credentials.json`:
   ```bash
   mv ~/Downloads/client_secret_*.json /path/to/lp-portfolio-analytics/credentials.json
   ```

The repo's `.gitignore` should already exclude `credentials.json` and `token.json`, but double-check before you commit anything.

### 5. Install Python dependencies

```bash
cd /path/to/lp-portfolio-analytics
pip install -r pipeline/requirements.txt
```

This installs the Google API client libraries plus the Anthropic SDK (for step 2).

---

## Part 2: Gmail label setup (~5 minutes, one-time per fund)

Create a label and a filter so founder emails land there automatically.

### 1. Create the label

In Gmail:
1. Left sidebar → scroll down → **More** → **Create new label**
2. Name it `lp/sahil-rolling` (or whatever fits your fund — slash makes it a nested label)
3. Click **Create**

### 2. Add a filter to auto-route founder emails

Two approaches:

**Approach A: filter by sender domain** (works if all founder emails come from `@<company>.com` style addresses you can list):

1. Gmail search bar → click the **Show search options** icon (sliders, far right)
2. **From**: `update@bus-right.com OR investors@hone.com OR ...` (list every founder email address)
3. Click **Create filter** at the bottom
4. Check **Apply the label**: `lp/sahil-rolling`
5. Optionally check **Skip the Inbox** if you want them filed away
6. **Create filter**

You'll need to update this filter each time a new portfolio company adds you to its investor list.

**Approach B: filter by subject pattern** (catches typical investor-update subjects):

1. Search options → **Subject contains**: `"investor update" OR "quarterly update" OR "Q1 2026" OR "Q2 2026"`
2. Apply the label as above

This is less precise but catches more by default. You can manually relabel anything that slips through.

**Approach C: hybrid** — start with whichever you prefer, then manually apply the label to anything that misses (Gmail has a one-click "always apply this label to messages from this sender" affordance once you start tagging manually).

### 3. Verify

After a few founder updates have landed, click the label in Gmail's sidebar and confirm it's catching what you expect. If too much noise is getting through, tighten the filter.

---

## Part 3: First run

### Pull emails

```bash
cd pipeline
python pull_gmail.py --label "lp/sahil-rolling"
```

The first run will:
1. Open a browser window asking you to grant access to the OAuth app
2. After you click "Allow", redirect back to localhost
3. Save the authentication token to `token.json` in the repo root
4. Fetch every message in the label, dump to `sample_inputs/founder_quarterly_email.json`

Subsequent runs reuse `token.json` and skip the browser flow until the token expires (Google's refresh handles most cases automatically).

**Filter to recent emails only:**

```bash
python pull_gmail.py --label "lp/sahil-rolling" --after 2026/01/01
```

Useful for quarterly refreshes — you only want the new emails, not the full history every time.

**Output to a different file:**

```bash
python pull_gmail.py --label "lp/sahil-rolling" --output ../scratch/raw_emails.json
```

### Parse with Claude (recommended)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python parse_emails_with_llm.py
```

This reads `founder_quarterly_email.json`, finds entries with raw bodies but null structured fields, and asks Claude to fill them in. Default model is `claude-sonnet-4-6`; the system prompt is cached so cost per email after the first is mostly the email body itself. ~30 emails per fund per year typically costs under $0.10 per refresh.

**Reparse everything** (e.g., if you tweaked the extraction prompt):

```bash
python parse_emails_with_llm.py --reparse
```

**Test on the first few emails before doing a full run:**

```bash
python parse_emails_with_llm.py --limit 3
```

### Regenerate dashboard data

After the structured fields are populated:

```bash
python emit_dashboard_json.py
```

The dashboard now reflects the new signals.

---

## Schedule it

For quarterly refreshes, this is fine to run manually. For continuous tracking, set up a cron job:

```cron
# Every Monday at 8am, pull last 7 days of founder updates and parse them
0 8 * * 1 cd /path/to/lp-portfolio-analytics && \
  python pipeline/pull_gmail.py --label "lp/sahil-rolling" --after "$(date -v -7d +%Y/%m/%d)" && \
  python pipeline/parse_emails_with_llm.py && \
  python pipeline/emit_dashboard_json.py
```

(macOS `date` syntax; Linux uses `date -d '7 days ago' +%Y/%m/%d`.)

For a real LP workflow, weekly is probably overkill — monthly is plenty.

---

## Troubleshooting

**"Token has been expired or revoked"**

Delete `token.json` and re-run `pull_gmail.py`. The browser flow will run again and write a fresh token.

**"Access blocked: This app's request is invalid"**

You skipped step 3.7 — your Gmail address isn't in the OAuth app's test users list. Go back to **OAuth consent screen** → **Test users** → **Add Users**.

**"Label 'lp/sahil-rolling' not found"**

Either:
- The label doesn't exist yet (create it in Gmail per Part 2)
- The label name doesn't match exactly (Gmail label names are case-sensitive — `LP/Sahil-Rolling` ≠ `lp/sahil-rolling`)

**Pull works but emails have empty bodies**

The script falls back to HTML if no plain text is available. If you're getting empty bodies, the email is probably image-only or has an unusual MIME structure. Open the email in Gmail and confirm it has text content.

**Claude returns weird parses (made-up numbers, wrong ARR)**

- Check the email body in `_raw_body` — if it's HTML cruft, the LLM might be confused by the markup. The HTML stripper in `pull_gmail.py` is crude; consider running the body through a cleaner step.
- Tighten the system prompt in `pipeline/parse_emails_with_llm.py` with specific instructions for the patterns you see — e.g., "If the email mentions 'bookings' separately from 'ARR', use ARR only".
- Use `--limit 3` to iterate on the prompt cheaply.

**Quota errors from Gmail API**

The free tier is 1 billion quota units per day, which is far more than you'll use for personal LP tracking. If you hit a quota error, you're probably looping the script accidentally — check `cron` schedules.

---

## Multiple Gmail accounts

If your founder emails are split across multiple Google accounts (e.g., a personal Gmail and a work-account Gmail), run separate OAuth flows for each:

```bash
GMAIL_CREDENTIALS=./credentials-personal.json GMAIL_TOKEN=./token-personal.json \
  python pipeline/pull_gmail.py --label "lp/sahil-rolling" --output ../sample_inputs/founder_personal.json

GMAIL_CREDENTIALS=./credentials-work.json GMAIL_TOKEN=./token-work.json \
  python pipeline/pull_gmail.py --label "lp/austen-access" --output ../sample_inputs/founder_work.json
```

Then concatenate the JSON outputs (or run the LLM parser on each separately and merge later).

---

## Security notes

- **Never commit `credentials.json` or `token.json`.** Both contain secrets that grant read access to your Gmail. The `.gitignore` excludes them by default, but if you've already committed them, rotate immediately: delete the OAuth client in Google Cloud Console and create a new one.
- **The OAuth scope is `gmail.readonly`** — the script cannot send, modify, or delete emails. Even if `token.json` leaks, the worst-case impact is someone reading your founder updates, not posing as you.
- **For multi-user deployments** (e.g., an LP workspace with several partners), don't share OAuth credentials. Each user should run their own pull against their own Gmail.
- **`ANTHROPIC_API_KEY`** has full account access on the Anthropic side. Store it in your shell profile or a secret manager, not in any file you commit.

---

## What this doesn't do

- **Doesn't pull attachments** — if a founder sends financials as a PDF attachment, you'll see references in the body but not the attachment contents. To handle attachments, extend `pull_gmail.py` with the Files API beta and pipe to Claude's PDF support.
- **Doesn't follow threads** — currently fetches each message individually. If a founder update has a long Q&A thread underneath, only the top message is captured. Use `_thread_id` to fetch the full thread if needed.
- **Doesn't handle inline images / screenshots** — typical for "here's our chart of ARR over time" updates. Same fix as attachments: pass image references to Claude's vision support.
- **No deduplication across pulls** — if you pull the same label twice with overlapping date ranges, you'll get duplicate entries. The pipeline downstream doesn't care (latest entry wins by company), but `founder_quarterly_email.json` will grow. Use `--output` to write to a fresh file and reconcile manually if you need precision.

These are all small extensions to the existing scripts if you need them.
