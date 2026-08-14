# TML Garage Services — Website Fix Log

A running record of every repair made to the "Fixed" version of the site
(`/fixed/`), kept for the site owner. The "Original" version is an untouched
copy of the current live website; use the switcher on the left edge of any
page to compare the two, page by page.

Format: each entry says **what** was wrong, **where**, **what changed**, and
**why it matters**.

---

## 2026-08-14 — Broken links, search visibility, and page-structure repairs

- **Removed 128 links to pages that don't exist.** The menus and footers
  linked to seven pages that were deleted long ago (Bathroom Renovations,
  Flooring, Kitchen Remodeling, Complete Home Renovation, and three
  gate/overhead-door pages) — clicking any of them landed visitors on an
  error page. The four home-improvement links were removed; the three
  gate/overhead links now point to the closest real service page.
- **Replaced the broken reviews widgets with your actual awards.** The
  "Clients Review" section on six pages loaded a third-party widget that
  publicly displayed "Site owner: upgrade your plan" instead of reviews.
  It now shows your Angi Super Service Award and HomeAdvisor badges with
  links to your real review profiles.
- **Repaired the contact page headline.** The main heading was an entire
  paragraph that cut off mid-word ("…or a routine maintena"). It now reads
  "TML Garage Door Services is here to help." with the rest of the message
  as normal text below it.
- **Gave the four brand pages real search listings.** LiftMaster, Genie,
  Chamberlain, and Craftsman pages all shared the generic title
  "TML Garage Door Services" with no description — these are the pages that
  should rank for "LiftMaster repair near me" searches. Each now has a
  unique title and description; nine other pages got missing descriptions.
- **Fixed the image that appears when the site is shared.** Sharing any page
  on Facebook/text messages showed a stock template avatar (or nothing).
  It now shows a real garage door photo.
- **Fixed page structure for Google.** Service pages had 4–5 "main
  headlines" competing with each other and all eight blog posts had none —
  17 extra headings demoted, 8 blog titles promoted, so every page now has
  exactly one main heading.
- **Made the financing message readable.** "Renovate Now. Pay Later." was
  light gray on a green background — nearly invisible. Now white.
- **Moved the red emergency button** from the bottom-left (where it covered
  text and form fields) to the bottom-right corner.
- **Described 244 images for accessibility and image search.** Photos had
  no alt descriptions; screen readers and Google Images now know what's in
  them. Also removed image variants that pointed at files that don't exist
  (a silent error on every page load).

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
