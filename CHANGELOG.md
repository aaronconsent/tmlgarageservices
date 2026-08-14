# TML Garage Services — Website Fix Log

A running record of every repair made to the "Fixed" version of the site
(`/fixed/`), kept for the site owner. The "Original" version is an untouched
copy of the current live website; use the switcher on the left edge of any
page to compare the two, page by page.

Format: each entry says **what** was wrong, **where**, **what changed**, and
**why it matters**.

---

## 2026-08-14 — Real Google reviews, baked into the site

- **Your reviews were being hidden.** Seven "Clients Review" sections loaded
  third-party widgets (Trustmary, Elfsight) that were over their free
  limits — visitors saw "Site owner: upgrade your plan" instead of reviews.
  Meanwhile the business has a **5.0-star rating from 213 Google reviews**.
- **Now the reviews are part of the page itself.** All seven sections show
  "Rated 5.0 ★ from 213 Google reviews," six real recent reviews (with
  reviewer names and dates, naming your technicians), and a link to read
  all 213 on Google. Because they're written into the page — not loaded by
  a widget — Google and AI search engines (ChatGPT, AI Overviews,
  Perplexity) can actually read and quote them, they load instantly, and
  nothing can ever expire or nag again.
- **Added business schema on every page.** Structured data now tells search
  engines exactly who the business is: name, phone, address, service area,
  and the 5.0/213 rating. The old site had none of this.
- **Refreshing is one command** (re-pulls the latest reviews for about five
  cents) — we can put it on a monthly schedule.
- *Owner: the six featured reviews were auto-picked (recent, detailed,
  5-star). Happy to swap in any favorites.*

## 2026-08-14 — Dead links: removed the old ones, built the missing pages

- **Removed 140 links to deleted home-improvement pages.** The menus and
  footers on nearly every page linked to Bathroom Renovations, Flooring,
  Kitchen Remodeling, and Complete Home Renovation — pages that no longer
  exist. Every click landed on an error page. Those links are gone.
- **Built the three missing gate/overhead pages.** The services page linked
  to Residential Driveway Gate Services, Commercial Overhead Door Services,
  and Commercial Gate &amp; Opener Services — services TML offers, but the
  pages were never created. Each now exists as a simple page in the site's
  own style, written from TML's already-published claims (same-day service,
  insured technicians, service area). *Owner: please review the wording on
  these three pages and tell us anything you'd like changed.*

## 2026-08-14 — Phone, address, and email repairs

- **Every call button now dials the right number.** 121 of the site's 135
  phone links were dialing old or wrong numbers — most dialed (833) 537-6686
  (the old TML Home Improvement line), including the "Call Us" button in the
  header of every page, and the homepage hero button dialed (832) 303-7032 —
  even though the on-screen text said (832) 887-8747. All 135 phone links now
  dial **(832) 887-8747**. This was silently sending mobile callers to the
  wrong line on nearly every tap.
- **Wrong phone numbers shown on screen corrected.** 16 places displayed
  (832) 303-7032, (833) 537-6686, or (832) 371-2484 — including the homepage
  hero button. All now show (832) 887-8747. Also fixed 37 typo'd displays of
  the correct number, e.g. "(832] 887-8747" with a stray bracket and
  "832- 887-8747" with a stray space.
- **One address everywhere.** The site showed two different business
  addresses (the footer said 15232 Saddlewood Dr; the contact page said
  2330 FM 1488 #400). All 34 address mentions now read
  **2330 FM 1488 #400, Conroe, TX 77384**. Consistent address info also
  matters for Google local rankings.
- **Repaired the scrambled address on the contact page.** Promo text had been
  pasted into the middle of the address, so it rendered as
  "2330 FM 1488 #400, CHouston Homeowners: Get a Complete…onroe, TX…" — 
  unreadable for visitors and for Google. It now reads as a clean address.
- **Email links now go where they say they go.** Two "info@tmlgarageservices.com"
  links actually opened an email to info@tml-homeimprovement.com (the old
  business domain). Both now send to info@tmlgarageservices.com.

## 2026-08-14 — Baseline

- **Created the Fixed working copy.** `/fixed/` starts as an exact clone of
  the current site. No visual or content changes yet — every difference from
  here forward is a deliberate, logged repair.
