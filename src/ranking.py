"""
ranking.py
Picks the single best contact email from a list of candidates using a
3-tier priority system: hiring-related > general company > never auto-pick.
"""

TIER1_KEYWORDS = ["career", "job", "hr@", "talent", "recruit", "hiring"]
TIER2_KEYWORDS = ["info", "hello", "contact", "team"]
TIER3_KEYWORDS = ["sales", "support", "legal", "privacy"]  # never auto-pick


def _matches(email, keywords):
    local_part = email.split("@")[0].lower()
    return any(kw in local_part for kw in keywords)


def rank_email(emails):
    """
    emails: list of (email, source, confidence) tuples from scraper.gather_all_emails()
    Returns the best pick as a tuple, or None if nothing usable is found.
    """
    tier1_matches = [e for e in emails if _matches(e[0], TIER1_KEYWORDS)]
    tier2_matches = [e for e in emails if _matches(e[0], TIER2_KEYWORDS)]
    tier3_matches = [e for e in emails if _matches(e[0], TIER3_KEYWORDS)]

    if tier1_matches:
        return tier1_matches[0]
    if tier2_matches:
        return tier2_matches[0]

    # Nothing in tier 1 or 2 — only skip if EVERY email found is tier 3
    if tier3_matches and len(tier3_matches) == len(emails):
        return None
    if emails:
        return emails[0]  # fallback: unclassified email
    return None
