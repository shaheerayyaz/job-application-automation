# Job Application Outreach Agent

A personal automation tool that finds software companies, extracts a relevant
contact email from each company's website, logs everything to Google Sheets
for manual review, and sends a personalized job application — with automatic
follow-ups for companies that don't reply.

> **Built to solve a real problem**: manually researching companies, hunting
> for contact emails, and sending applications one by one was slow and
> repetitive. This agent automates the research and outreach while keeping a
> manual review step before anything is actually sent.

**[Watch a 90-second demo](https://www.loom.com/share/cd9e4c3ad8fa4e1e9958d7c49bb65149)**

## Note on running this yourself

This project uses personal credentials (Gmail, Google Sheets, my own CV) and
isn't designed to be cloned and run out-of-the-box — see the demo video above
for a full walkthrough, or reach out if you'd like to discuss the
implementation in more detail.

## How it works

```
Company list (Google Sheet)
        │
        ▼
Fetch homepage + contact/about/careers pages  (requests + BeautifulSoup)
        │
        ▼
Extract emails: mailto links → footer → page text
  (each tagged with a confidence: High / Medium / Low)
        │
        ▼
Rank candidates: hiring-related > general company > never auto-pick
  (sales/support/legal/privacy addresses are skipped even if it's the
  only address found)
        │
        ▼
Log to Google Sheets  (deduped by domain, across every run — not just
  the current one)
        │
        ▼
Manual review  (I check the sheet before anything is sent)
        │
        ▼
Send personalized application via Gmail SMTP  (CV attached, company name
  in the greeting, randomized delay between sends)
        │
        ▼
Automatic follow-up after 7 days if no reply is logged
```

## Design decisions worth calling out

- **Manual company discovery, automated everything after.** Google Search and
  LinkedIn actively block scraping — fighting that wasn't worth it for a
  personal-scale tool. A short manually-curated list of target companies is
  the actual input.
- **Gmail SMTP over a transactional email service.** Third-party ESPs
  (SendGrid, Brevo, etc.) are built for businesses and increasingly require a
  verified domain — a real wall for an individual, no-domain use case. At
  20–30 emails/day, Gmail's own 500/day limit was never actually the
  constraint; a personal Gmail account with an App Password is the simpler,
  fully-supported option.
- **Confidence scoring, not blind automation.** Every extracted email is
  tagged High / Medium / Low based on *where* it was found (a `mailto:` link
  is far more reliable than a regex match buried in page text). This drives
  what gets a closer manual look before sending.
- **A 3-tier ranking system, not a long ordered list.** Most company sites
  only expose 1–3 relevant addresses, so the system collapses to: prefer
  hiring-related addresses, fall back to general company addresses, and
  never auto-pick sales/support/legal/privacy addresses even if nothing else
  exists.
- **One retry, then skip and log — no retry queues.** For a personal-scale
  tool, elaborate backoff/retry infrastructure solves a scale problem this
  project doesn't have. Every failure mode (timeout, 403, broken HTML,
  bounced email) is logged with a specific reason instead of retried
  indefinitely.

## Tech stack

| Component | Tool |
|---|---|
| Scraping | `requests`, `BeautifulSoup` |
| Data store | Google Sheets API (`gspread`) |
| Email sending | Gmail SMTP (`smtplib`) |
| Language | Python 3 |

## Project structure

```
src/
  scraper.py   — fetches pages, extracts and merges emails
  ranking.py   — 3-tier email selection logic
  sheets.py    — Google Sheets read/write + cross-run dedupe
  mailer.py    — email templates + sending + follow-up logic
  main.py      — scrape → rank → log pipeline
  send.py      — separate trigger for sending + follow-ups
```

Scraping/logging (`main.py`) and sending (`send.py`) are kept as separate
entry points on purpose — so a review step always sits between finding a
company and actually emailing them.

## What I'd build next

- Tech-stack detection for lighter personalization (skipped for now — an
  unreliable guess looks worse than a good generic line)
- A small web UI instead of running scripts directly, if this were to be
  used by more than one person
