"""
scraper.py
Fetches company websites and extracts contact emails from the homepage
and relevant subpages (contact, about, careers).
"""

import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

RELEVANT_PAGE_KEYWORDS = ["contact", "career", "careers", "jobs", "about"]
EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'


def fetch_page(url, timeout=10):
    """Fetch a URL's HTML, with timeout + basic error handling."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; JobApplicationBot/1.0; personal use)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        print(f"Timeout fetching {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error for {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def extract_emails(html):
    """
    Extracts emails from HTML, checking mailto links first (High confidence),
    then footer text (Medium), then the rest of the page (Low).
    Returns a deduped list of (email, source, confidence).
    """
    soup = BeautifulSoup(html, "html.parser")
    found = []

    # 1. mailto: links — highest confidence
    for link in soup.select('a[href^="mailto:"]'):
        email = link["href"].replace("mailto:", "").split("?")[0].strip()
        if email:
            found.append((email, "mailto link", "High"))

    # 2. Footer text — medium confidence
    footer = soup.find("footer")
    if footer:
        for email in re.findall(EMAIL_PATTERN, footer.get_text()):
            found.append((email, "footer", "Medium"))

    # 3. Rest of page text — low confidence
    for email in re.findall(EMAIL_PATTERN, soup.get_text()):
        if email not in [f[0] for f in found]:
            found.append((email, "page text", "Low"))

    # Dedupe, keeping the first (highest-confidence) occurrence
    seen = set()
    deduped = []
    for email, source, confidence in found:
        if email.lower() not in seen:
            seen.add(email.lower())
            deduped.append((email, source, confidence))

    return deduped


def find_relevant_pages(html, base_url):
    """Finds contact/about/careers page links on the same domain."""
    soup = BeautifulSoup(html, "html.parser")
    found_links = set()
    base_domain = urlparse(base_url).netloc

    for link in soup.find_all("a", href=True):
        full_url = urljoin(base_url, link["href"])
        parsed = urlparse(full_url)
        clean_url = parsed._replace(fragment="").geturl()

        path = parsed.path.lower()
        if any(kw in path for kw in RELEVANT_PAGE_KEYWORDS) and parsed.netloc == base_domain:
            found_links.add(clean_url)

    return list(found_links)


def gather_all_emails(homepage_url, homepage_html):
    """
    Combines emails from the homepage + contact/about/careers pages
    into a single deduped list of (email, source, confidence).
    """
    all_found = extract_emails(homepage_html)
    subpages = find_relevant_pages(homepage_html, homepage_url)

    for url in subpages:
        time.sleep(1)  # courtesy delay between requests to the same site
        page_html = fetch_page(url)
        if page_html:
            page_name = urlparse(url).path.strip("/").replace("/", "-") or "homepage"
            for email, source, confidence in extract_emails(page_html):
                all_found.append((email, f"{page_name} page ({source})", confidence))

    seen = set()
    deduped = []
    for email, source, confidence in all_found:
        if email.lower() not in seen:
            seen.add(email.lower())
            deduped.append((email, source, confidence))

    return deduped
