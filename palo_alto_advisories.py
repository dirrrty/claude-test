#!/usr/bin/env python3
"""
Fetch and display Palo Alto Networks security advisories.
Output is printed to stdout and saved to palo_alto_advisories.txt.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

OUTPUT_FILE = "/home/user/claude-test/palo_alto_advisories.txt"
ADVISORIES_URL = "https://security.paloaltonetworks.com/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_advisories():
    print(f"Fetching advisories from {ADVISORIES_URL} ...")
    resp = requests.get(ADVISORIES_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text


def parse_advisories(html):
    soup = BeautifulSoup(html, "html.parser")
    advisories = []

    # Each advisory row on security.paloaltonetworks.com
    rows = soup.select("table tbody tr")
    if not rows:
        # Fallback: try card/list-item selectors
        rows = soup.select("li.advisory, div.advisory, div[class*='advisory']")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 3:
            link_tag = cells[0].find("a")
            advisory_id = link_tag.get_text(strip=True) if link_tag else cells[0].get_text(strip=True)
            url = link_tag["href"] if link_tag and link_tag.get("href") else ""
            if url and url.startswith("/"):
                url = "https://security.paloaltonetworks.com" + url

            title    = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            severity = cells[2].get_text(strip=True) if len(cells) > 2 else ""
            date     = cells[3].get_text(strip=True) if len(cells) > 3 else ""

            advisories.append({
                "id":       advisory_id,
                "title":    title,
                "severity": severity,
                "date":     date,
                "url":      url,
            })

    return advisories


def severity_order(s):
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4, "none": 5}
    return order.get(s.lower(), 99)


def build_report(advisories):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("=" * 70)
    lines.append(f"  PALO ALTO NETWORKS — SECURITY ADVISORIES")
    lines.append(f"  Retrieved: {now}")
    lines.append(f"  Source:    {ADVISORIES_URL}")
    lines.append("=" * 70)

    if not advisories:
        lines.append("\n  No advisories parsed — page structure may have changed.")
        return "\n".join(lines)

    # Sort by severity
    advisories.sort(key=lambda a: severity_order(a["severity"]))

    # Severity counts
    from collections import Counter
    counts = Counter(a["severity"].capitalize() for a in advisories)
    lines.append(f"\n  Total advisories found: {len(advisories)}")
    for sev, cnt in sorted(counts.items(), key=lambda x: severity_order(x[0])):
        lines.append(f"    {sev:<15} {cnt}")

    lines.append("\n" + "-" * 70)
    lines.append(f"  {'ID':<20} {'Severity':<12} {'Date':<12} {'Title'}")
    lines.append("-" * 70)

    for a in advisories:
        title_trunc = a["title"][:45] + "…" if len(a["title"]) > 45 else a["title"]
        lines.append(f"  {a['id']:<20} {a['severity']:<12} {a['date']:<12} {title_trunc}")
        if a["url"]:
            lines.append(f"  {'':20} {a['url']}")

    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    try:
        html = fetch_advisories()
    except requests.exceptions.ProxyError:
        print("ERROR: A proxy is blocking the connection.")
        print("       Run this script directly on a machine with internet access.")
        return
    except requests.exceptions.ConnectionError:
        print("ERROR: No internet connection or host unreachable.")
        print("       Run this script on a machine with access to security.paloaltonetworks.com")
        return
    except requests.RequestException as e:
        print(f"ERROR: Could not reach {ADVISORIES_URL}: {e}")
        return

    advisories = parse_advisories(html)
    report = build_report(advisories)

    print(report)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report + "\n")

    print(f"\nOutput saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
