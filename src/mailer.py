"""
mailer.py
Sends application and follow-up emails via Gmail SMTP, and updates
the tracker sheet's Status / Date Sent / Follow-up Sent columns.
"""

import random
import smtplib
import time
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

YOUR_NAME = "Shaheer Ayyaz"
YOUR_EMAIL = "shaheerayaz163@gmail.com"
YOUR_PHONE = "+00-309-0000000"


def build_application_body(company_name):
    return f"""Hi {company_name} team,

Hope you're doing well!

I'll keep this short.

I'm {YOUR_NAME}, a Software Engineer who enjoys building things more than just
talking about them. I've attached my CV — if you're hiring for Web, AI, Backend,
Full-Stack, QA, or Automation roles, I'd really appreciate your consideration.

I'm open to discussing any role where I can contribute, learn quickly, and grow
with the team.

Thanks for your time, and I hope to hear from you.

Best regards,
{Shaheer Ayyaz}
{shaheerayaz163@gmail.com}
{+92-309-0000000}"""


def build_followup_body(company_name):
    return f"""Hi {company_name} team,

Just wanted to follow up on my previous email in case it got buried.

I'm still very interested in any Software Engineering opportunities you might
have, and I'd love the chance to chat if my background looks like a fit.

My CV is attached again for convenience. Thanks again for your time.

Best regards,
{Shaheer Ayyaz}
{shaheerayaz163}
{+92-309-0000000}"""


def _send_email(gmail_address, app_password, recipient, subject, body, cv_path):
    msg = MIMEMultipart()
    msg["From"] = gmail_address
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with open(cv_path, "rb") as f:
        part = MIMEApplication(f.read(), Name="CV.pdf")
    part["Content-Disposition"] = 'attachment; filename="CV.pdf"'
    msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(gmail_address, app_password)
    server.sendmail(gmail_address, recipient, msg.as_string())
    server.quit()


def send_pending_applications(main_sheet, gmail_address, app_password, cv_path):
    """Sends the initial application to every row marked 'Pending' with an email."""
    all_data = main_sheet.get_all_values()
    header = all_data[0]

    email_col = header.index("Email")
    status_col = header.index("Status")
    company_col = header.index("Company")
    date_sent_col = header.index("Date Sent")

    sent_count = 0
    for i, row in enumerate(all_data[1:], start=2):
        if len(row) <= status_col:
            continue
        status = row[status_col]
        email = row[email_col] if len(row) > email_col else ""
        company_name = row[company_col]

        if status == "Pending" and email:
            try:
                subject = "Application — Software Engineer"
                body = build_application_body(company_name)
                _send_email(gmail_address, app_password, email, subject, body, cv_path)

                main_sheet.update_cell(i, status_col + 1, "Sent")
                main_sheet.update_cell(i, date_sent_col + 1,
                                        datetime.now().strftime("%Y-%m-%d %H:%M"))
                print(f"Sent to {company_name} ({email})")
                sent_count += 1
                time.sleep(random.uniform(15, 45))
            except Exception as e:
                main_sheet.update_cell(i, status_col + 1, "Failed")
                print(f"Failed to send to {company_name}: {e}")

    print(f"\nDone. Sent {sent_count} application(s).")


def send_followups(main_sheet, gmail_address, app_password, cv_path, wait_days=7):
    """Sends one follow-up to rows sent >= wait_days ago with no reply."""
    all_data = main_sheet.get_all_values()
    header = all_data[0]

    email_col = header.index("Email")
    company_col = header.index("Company")
    status_col = header.index("Status")
    date_sent_col = header.index("Date Sent")
    replied_col = header.index("Replied")
    followup_col = header.index("Follow-up Sent")

    followup_count = 0
    for i, row in enumerate(all_data[1:], start=2):
        if len(row) <= followup_col:
            continue

        status = row[status_col]
        date_sent_str = row[date_sent_col]
        replied = row[replied_col].strip().upper()
        followup_sent = row[followup_col].strip().upper()
        email = row[email_col]
        company_name = row[company_col]

        if status != "Sent" or not date_sent_str or replied == "Y" or followup_sent == "Y":
            continue

        try:
            date_sent = datetime.strptime(date_sent_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        days_since_sent = (datetime.now() - date_sent).days
        if days_since_sent >= wait_days:
            try:
                subject = "Following up — Software Engineer Application"
                body = build_followup_body(company_name)
                _send_email(gmail_address, app_password, email, subject, body, cv_path)

                main_sheet.update_cell(i, followup_col + 1, "Y")
                print(f"Follow-up sent to {company_name} ({email}) "
                      f"— {days_since_sent} days since initial email")
                followup_count += 1
                time.sleep(random.uniform(15, 45))
            except Exception as e:
                print(f"Failed to send follow-up to {company_name}: {e}")

    print(f"\nDone. Sent {followup_count} follow-up(s).")
