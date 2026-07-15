"""
sheets.py
Handles reading the company list and logging scrape results to Google Sheets.

Expected tracker sheet (Sheet1) columns:
Company | Website | Email | Email Confidence | Source | Status |
Date Scraped | Date Sent | Replied | Follow-up Sent | Notes

Expected "Company List" tab columns:
Company | Website
"""

from datetime import datetime
from urllib.parse import urlparse

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def connect(service_account_json_path, sheet_id):
    """Authenticates and returns the gspread Spreadsheet object."""
    creds = Credentials.from_service_account_file(service_account_json_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)


def get_domain(url):
    """Normalizes a URL to just its domain, for dedupe purposes."""
    netloc = urlparse(url).netloc.lower()
    return netloc.replace("www.", "")


def log_result(main_sheet, company_name, website, best_email_result, status="Pending"):
    """Writes one row to the tracker sheet."""
    date_scraped = datetime.now().strftime("%Y-%m-%d %H:%M")

    if best_email_result:
        email, source, confidence = best_email_result
        row = [company_name, website, email, confidence, source, status,
               date_scraped, "", "", "", ""]
    else:
        row = [company_name, website, "", "", "", "No email found",
               date_scraped, "", "", "", ""]

    main_sheet.append_row(row)
    print(f"Logged: {company_name} — {row[2] or 'no email'}")


def get_already_logged_domains(main_sheet):
    """Returns a set of domains already present in the tracker, for dedupe across runs."""
    existing_data = main_sheet.get_all_values()
    header = existing_data[0]
    website_col = header.index("Website")

    domains = set()
    for row in existing_data[1:]:
        if len(row) > website_col and row[website_col].strip():
            domains.add(get_domain(row[website_col]))
    return domains
