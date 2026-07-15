"""
send.py
Separate trigger for sending applications and follow-ups, run manually
after you've reviewed the tracker sheet. Kept separate from main.py so
scraping and sending are always deliberate, distinct steps.
"""

import os

from sheets import connect
from mailer import send_pending_applications, send_followups

SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON", "service-account.json")
SHEET_ID = os.environ.get("SHEET_ID", "your-sheet-id-here")
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "you@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
CV_PATH = os.environ.get("CV_PATH", "cv.pdf")

if __name__ == "__main__":
    spreadsheet = connect(SERVICE_ACCOUNT_JSON, SHEET_ID)
    main_sheet = spreadsheet.sheet1

    # Send new applications to any row marked "Pending"
    send_pending_applications(main_sheet, GMAIL_ADDRESS, GMAIL_APP_PASSWORD, CV_PATH)

    # Send follow-ups to anything sent 7+ days ago with no reply
    send_followups(main_sheet, GMAIL_ADDRESS, GMAIL_APP_PASSWORD, CV_PATH, wait_days=7)
