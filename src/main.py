"""
main.py
Entry point that ties everything together: scrape -> rank -> log.
Sending and follow-ups are triggered separately (see README) so you can
review the sheet before anything actually goes out.
"""

import os
import time

from scraper import fetch_page, gather_all_emails
from ranking import rank_email
from sheets import connect, log_result, get_already_logged_domains, get_domain

SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON", "service-account.json")
SHEET_ID = os.environ.get("SHEET_ID", "your-sheet-id-here")
COMPANY_LIST_TAB = "Company List"


def run_pipeline():
    spreadsheet = connect(SERVICE_ACCOUNT_JSON, SHEET_ID)
    company_list_sheet = spreadsheet.worksheet(COMPANY_LIST_TAB)
    main_sheet = spreadsheet.sheet1

    rows = company_list_sheet.get_all_values()[1:]  # skip header
    seen_domains = get_already_logged_domains(main_sheet)

    processed, skipped = 0, 0

    for row in rows:
        if len(row) < 2 or not row[0].strip() or not row[1].strip():
            continue

        company_name, website = row[0].strip(), row[1].strip()
        domain = get_domain(website)

        if domain in seen_domains:
            print(f"Skipping already-logged company: {company_name} ({domain})")
            skipped += 1
            continue
        seen_domains.add(domain)

        print(f"\nProcessing: {company_name} ({website})")
        homepage_html = fetch_page(website)

        if not homepage_html:
            log_result(main_sheet, company_name, website, None, status="Failed - unreachable")
            continue

        all_emails = gather_all_emails(website, homepage_html)
        best = rank_email(all_emails)
        log_result(main_sheet, company_name, website, best, status="Pending")
        processed += 1

        time.sleep(2)  # courtesy delay between different companies' sites

    print(f"\nDone. Processed: {processed}, Skipped (already logged): {skipped}")


if __name__ == "__main__":
    run_pipeline()
