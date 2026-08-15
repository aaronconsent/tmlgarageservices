#!/usr/bin/env python3
"""Page titles, descriptions and the social share image.

Three problems, all in <head>:

  * Titles ran 69-116 characters. Google shows roughly the first 600px, about
    60-65 characters, so nineteen pages were being cut off mid-phrase — and the
    part that got cut was usually the city, which is the part a local searcher
    is scanning for. Rewritten keyword-first, city second, business name last,
    every one under 65.
  * Eight descriptions sat outside the useful range: three legal pages too
    short to say anything, five long enough to be truncated.
  * og:image pointed at the staging host. Every link shared to Facebook,
    LinkedIn or iMessage would have shown a broken preview the moment staging
    went away.

The <title>, og:title and twitter:title are written together, and likewise the
three descriptions, so the page and its share card never disagree.

Idempotent.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"

LIVE = "https://www.tmlgarageservices.com"
STAGING = "https://tmlgarageservices.aironz.workers.dev"

# keyword first, city second, business name last: the leading words are what a
# searcher matches against, and the name is what they recognise once they have
TITLES = {
    "": "Garage Door Repair in Conroe, TX | TML Garage Door Services",
    "about": "About TML Garage Door Services | Conroe, TX Garage Doors",
    "contact": "Contact TML Garage Door Services | Conroe, TX",
    "services": "Garage Door Services in Conroe, TX | TML Garage Door Services",
    "schedule-consult": "Book Garage Door Service Online | TML Garage Door Services",
    "our-services/garage-door-spring-replacement":
        "Garage Door Spring Repair, Conroe TX | TML Garage Door Services",
    "our-services/garage-door-opener-installation":
        "Garage Door Opener Repair, Conroe TX | TML Garage Door Services",
    "our-services/residential-garage-door-services":
        "New Garage Door Installation | TML Garage Door Services",
    "our-services/residential-driveway-gate-services":
        "Driveway Gate Repair, Conroe TX | TML Garage Door Services",
    "our-services/commercial-garage-door-installation":
        "Commercial Garage Doors, Houston | TML Garage Door Services",
    "our-services/commercial-overhead-door-services":
        "Commercial Overhead Doors, Houston | TML Garage Door Services",
    "our-services/commercial-gate-opener-services":
        "Commercial Gate & Opener Service | TML Garage Door Services",
    "brands/chamberlain-garage-door-opener-repair-and-installation":
        "Chamberlain Opener Repair, Conroe TX | TML Garage Door Services",
    "brands/craftsman-garage-door-opener-repair-and-installation":
        "Craftsman Opener Repair, Conroe TX | TML Garage Door Services",
    "brands/genie-garage-door-opener-repair-and-installation":
        "Genie Opener Repair, Conroe TX | TML Garage Door Services",
    "brands/liftmaster-garage-door-opener-repair-and-installation":
        "LiftMaster Opener Repair, Conroe TX | TML Garage Door Services",
    "privacy-policy": "Privacy Policy | TML Garage Door Services",
    "terms-conditions": "Terms & Conditions | TML Garage Door Services",
    "cookie-policy": "Cookie Policy | TML Garage Door Services",
}

# only the eight that were too short to inform or long enough to be cut off
DESCRIPTIONS = {
    "": "Garage door repair, spring replacement and new installation in Conroe, "
        "The Woodlands and greater Houston. Same-day appointments. Call (832) 887-8747.",
    "services": "Garage door repair, springs, openers and new installation across Conroe, "
        "The Woodlands and Spring TX. Same-day appointments, upfront pricing.",
    "schedule-consult": "Book garage door repair, opener service or a tune-up online in under a "
        "minute. Same-day appointments across Conroe and The Woodlands, TX.",
    "our-services/garage-door-spring-replacement":
        "Broken garage door spring in Conroe or The Woodlands? Same-day replacement "
        "by trained technicians. Upfront pricing. Call (832) 887-8747.",
    "our-services/residential-driveway-gate-services":
        "Driveway gate and gate opener repair, service and installation for homes in "
        "Conroe, The Woodlands and Spring TX. Call (832) 887-8747.",
    "privacy-policy": "How TML Garage Door Services collects, uses and protects the personal "
        "information you share with us.",
    "terms-conditions": "The terms that apply when you use the TML Garage Door Services "
        "website or book garage door work with us.",
    "cookie-policy": "What cookies the TML Garage Door Services website uses, what they do, "
        "and how to turn them off.",
}


def set_meta(html, key, value, attr="name"):
    """Rewrite a <meta> tag's content, whatever order its attributes are in."""
    def repl(m):
        tag = m.group(0)
        if not re.search(rf'{attr}="{re.escape(key)}"', tag):
            return tag
        return re.sub(r'content="[^"]*"', f'content="{value}"', tag, count=1)
    return re.sub(r"<meta\b[^>]*>", repl, html)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    titles = descs = ogs = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        rel = str(f.parent.relative_to(F))
        key = "" if rel == "." else rel

        if key in TITLES:
            t = esc(TITLES[key])
            html = re.sub(r"<title>.*?</title>", f"<title>{t}</title>", html, count=1, flags=re.S)
            html = set_meta(html, "og:title", t, "property")
            html = set_meta(html, "twitter:title", t)

        if key in DESCRIPTIONS:
            d = esc(DESCRIPTIONS[key])
            html = set_meta(html, "description", d)
            html = set_meta(html, "og:description", d, "property")
            html = set_meta(html, "twitter:description", d)

        # the share card must live on the domain that will still exist next month
        if STAGING in html:
            html = html.replace(STAGING, LIVE)
            ogs += 1

        if html != orig:
            if key in TITLES:
                titles += 1
            if key in DESCRIPTIONS:
                descs += 1
            f.write_text(html, "utf-8")
    print(f"titles rewritten: {titles}")
    print(f"descriptions rewritten: {descs}")
    print(f"pages moved off the staging host: {ogs}")


if __name__ == "__main__":
    main()
