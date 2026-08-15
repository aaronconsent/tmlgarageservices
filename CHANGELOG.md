# TML Garage Services — Website Fix Log

A running record of every repair made to the "Fixed" version of the site
(`/fixed/`), kept for the site owner. The "Original" version is an untouched
copy of the current live website; use the switcher on the left edge of any
page to compare the two, page by page.

Format: each entry says **what** was wrong, **where**, **what changed**, and
**why it matters**.

---

## 2026-08-14 — A working contact form, feeding straight into Workiz

The home page, contact page and the four opener brand pages now carry your
Workiz service-request form: name, phone, email, and what the problem is.
**Submissions go into the same Workiz account as your online bookings**, so
enquiries and booked jobs arrive in one place rather than two.

This replaces the prototype form that was standing in on those pages. The
booking page keeps the full booking widget, where a customer picks a service, a
day and a time — a short enquiry form suits the other pages better than asking
someone to schedule before they have even described the problem.

The form now stands on its own, with no heading or explanatory line above it and
no alternative-contact row beneath it. With that copy gone the surrounding panel
would only have been a box inside a box, so it collapsed to a single card — which
also gave the form more room: 570px wide on a desktop and 273px on a phone, up
from 516px and 239px.

Worth restating plainly: **before today, the form on these pages went nowhere.**
Anything sent through it was lost without the sender knowing. That is now fixed.

---

## 2026-08-14 — Booking widget framed to fit the page

The Workiz booking widget now sits in a proper frame rather than floating on the
page.

- **On a phone it was getting 309px of a 375px screen**, because the panel and
  the frame each added their own margin. It now runs edge to edge, and is sized
  to the height of the screen — before, the first step was a small card adrift in
  about 500px of empty grey, with a scrollbar inside a scrollbar underneath.
- **On a desktop** it is a little wider, in a clean white card with a rounded
  border, and the "Need it today?" panel beside it now travels down with you
  instead of leaving a tall gap.

**One honest limit.** The widget itself belongs to Workiz and is loaded from
their servers. Its fonts, colours, buttons and wording cannot be changed from
this site — browsers do not allow one site to restyle another's, and Workiz does
not offer a hook for it. Anything inside that box is changed in your Workiz
account settings, where they offer branding options. Everything around it is
ours, and that is what has been tidied.

---

## 2026-08-14 — Real Workiz booking live on the booking page

The booking page now shows **your actual Workiz online booking widget** instead
of the prototype. A booking made here goes straight into Workiz.

It is switched on for that one page only. The six other pages carrying the
booking form still show the prototype, so the live widget can be tried properly
before it goes everywhere. Turning on the rest is a one-line change once you are
happy with it.

One useful detail: where a visitor came from is passed to Workiz with the
booking, so bookings arriving from Google Ads, Facebook, or a direct visit are
distinguishable in your Workiz records.

---

## 2026-08-14 — The booking form now sits on the pages themselves

The six pages that used to carry the broken contact form were given a panel
linking through to the booking page. They now carry **the booking form itself** —
choose the problem, pick a day, pick an arrival window, leave your details —
so nobody has to click through to another page to book.

It appears on the home page, the contact page, and all four opener brand pages.
The form is taken from the booking page when the site is built, so there is one
version to maintain: change it there and every page follows.

Two things fixed to make it fit: the two-column layouts on these pages never
stacked on a phone, which squeezed the form into about 205px of a 375px screen;
and the three arrival windows were being crushed side by side with their times
wrapping mid-line. Both now behave on a phone.

As before, this is still the prototype flow — it collects everything and shows a
confirmation, and will push to Workiz once the account is connected.

---

## 2026-08-14 — Last of the Webflow leftovers cleared out

Nothing visible changed here. This was the final sweep for traces of the old
platform in the page code:

- Removed the "Last Published" stamp, the site and page identifiers, and the
  animation hooks Webflow attached to elements — none of which did anything once
  its code was gone.
- Deleted the hidden "No project gallery found." placeholders Webflow leaves
  behind for unfilled content, rather than keeping its styling around just to
  hide them.
- Removed the leftover styling rules that pointed at those hooks.

**There are now no references to Webflow anywhere in the site's code** — no
scripts, no identifiers, no links to its servers.

One group was deliberately left in place: about a thousand `w-` prefixed style
names still used by the site's stylesheet for layout. They are only names, they
cost nothing, and renaming them would mean rewriting the stylesheet with a real
risk of shifting the layout. That is a job worth doing on its own terms, not as
a footnote to this clean-up.

---

## 2026-08-14 — The site no longer runs on Webflow's code

Every page was loading jQuery and Webflow's framework — about 417 KB of
JavaScript on every visit — to power five things. All five have been replaced
with code the browser already has built in, and the framework is gone.

Along the way this fixed two things that were quietly broken:

- **The contact form never worked on this copy of the site.** It had no
  destination: it relied on Webflow's servers, which this exported version
  cannot reach. Every "Request Appointment" went nowhere — no email, no record,
  and the visitor saw no error, so they believed they had reached you. It is
  replaced by a panel that sends people to the online booking page, with call
  and text alongside it. **Anyone who filled in that form was never heard.**
- **Four FAQ answers on the home page and About page could not be opened.**
  Clicking a question did nothing at all. They now open and close properly, and
  can be found by the browser's search-in-page.

Also replaced: the photo pop-ups, the photo carousel, the tabbed panels, and the
home page video's play button — all now using the browser's own features, all
working from the keyboard, and all lighter than what they replaced.

Nothing on the site looks different. It is simply much lighter and no longer
depends on a platform the site was exported away from.

---

## 2026-08-14 — More of the old Webflow machinery removed

Continuing the clean-up, each step checked before it was made:

- **The photo pop-ups on the four project pages** now use the browser's own
  pop-up instead of Webflow's. Clicking a photo still opens it large over a
  dimmed background; pressing Escape or clicking outside closes it, which the
  old one did not do.
- **The play/pause button on the home page video** no longer needs Webflow's
  code. The video itself never did. One small addition: if a visitor has asked
  their phone or computer to reduce motion, the video now waits rather than
  playing automatically — the button still starts it.
- **Removed hidden copies of page markup** that Webflow leaves behind on the
  project pages. They were never displayed, and every one of them still pointed
  at Webflow's own servers for the photographs. **There are now no references to
  Webflow's servers anywhere on the site.**

---

## 2026-08-14 — "Why Choose TML" is now its own section, and the photo gallery no longer needs Webflow

**Why Choose TML Garage Door Services.** On the home page and the About page this
was the left-hand column of a two-column block, sharing the row with the FAQ
list. Seven reasons to hire you were squeezed into a narrow column of small text
running down the side of the page, reading like a caption to the FAQ rather than
an argument of its own. It is now a **full-width section of its own, sitting
above the FAQ**, with each reason as a headed point with a check against it,
three across on a desktop and stacking on a phone. Same words, same black
section, same phone and Explore Services buttons.

**The "Some of our work" photo gallery** on five pages was a Webflow slider.
It has been rebuilt using the browser's own scrolling, which means swiping on a
phone now feels like every other gallery on your phone rather than a website
imitation of one. Clicking a photo still opens it full-size. Arrows, position
dots and the photos themselves are unchanged. This removes one of the four
things still tying the site to the old Webflow code.

Also fixed along the way: on phones, the collapsed menu was being rendered
off-screen to the right, which let the page slide sideways slightly. It no
longer does.

---

## 2026-08-14 — Fonts now served from your own site

Every page was loading a script from Google that then went and fetched six
typeface families at every available weight — around 36 font files' worth — when
the site only ever displays four of them. Worse, it was a blocking request: text
could not appear until Google answered.

The four typefaces the site actually uses are now served from your own site, in
only the weights that appear on screen. **The fonts look exactly the same** —
this is purely about where they come from and how many are fetched. Two side
effects worth having: pages start showing text sooner, and visitors are no longer
being pinged to a third-party server just to read your site.

---

## 2026-08-14 — Removed a broken script request from every page

Every page was asking the server for a Webflow tracking file that was never
included in the export. The file does not exist, so all 36 pages made one
request that failed on every single visit. It has been removed — nothing on the
page looked at it or needed it.

This is the first of a series of clean-up steps, each one reviewed and approved
before it is made.

---

## 2026-08-14 — Header menu reworked, and hidden sections brought into view

**The menu.** The four items now sit to the left beside the logo instead of
floating in the middle of the bar, each with a small icon. The Brands menu was
the real problem: it opened on hover only, which means it could not be used on a
phone at all, and on a desktop it snapped shut if the mouse strayed while
travelling down to the list. It now opens on a click, on every device, and stays
open until you pick something, click elsewhere, or press Escape. It also works
from the keyboard now, which it did not before.

**Sections that were hiding half their content.** Three pages used a tab widget
where only one panel showed at a time and the tab labels looked like ordinary
paragraphs, so nothing indicated there was more to see:

- On the **home page**, "Why Choose TML Garage Door Services?" was visible and
  "What You Can Expect From TML" — your eight promises, the strongest trust
  content on the page — was hidden behind a tab most visitors would never click.
  Both are now full sections, one after the other, with the eight promises shown
  as a checked list.
- The **About** page and **The Woodlands** page had the same widget hiding
  "Trend Watch", "Quality Assurance" and "Client Focus". All now show in full.

No wording changed anywhere — content that was hidden is simply on the page now.

---

## 2026-08-14 — Driveway gate and commercial overhead door pages built out

Two service pages existed in name only. Each was about a paragraph long: two
sentences, the standard expectations list, a phone number, and nothing else — no
banner, no reviews, no questions answered, and nothing for Google to index. Both
now match the other service pages.

- **Residential Driveway Gate Services** and **Commercial Overhead Door
  Services** each have a photo banner, the twelve most common faults for that
  equipment, the upfront-pricing promise, a numbered walk-through of what a
  service visit covers, the 5.0 rating from 213 Google reviews, four answered
  questions, the service area, and a clear way to get in touch.
- **The three missing photos on the services page are fixed.** Four of the seven
  service cards had a picture and three did not, so the grid looked
  half-finished. TML's own photo library already contained pictures named for
  exactly those three services — they shipped with the site and had simply never
  been connected. All seven cards now have a photo.

**Please read these two pages before showing them to customers.** Unlike every
other change in this log, most of the wording here is new rather than yours —
the originals had almost nothing to work from. Everything TML already says about
these services is used word for word; the rest describes common symptoms and
what a service call involves. It deliberately claims nothing about gate brands,
gate types, materials, or anything else that isn't already stated somewhere on
your site, because guessing at those would put words in your mouth.

---

## 2026-08-14 — The remaining three service pages rebuilt to match

Spring replacement, new door installation and commercial doors now follow the
same structure as the opener page you reviewed. **All existing copy is intact** —
only the order and presentation changed.

Each page now answers questions in the order a customer asks them: what's wrong
(or what you gain), what it costs, what the job involves step by step, proof from
213 Google reviews, the detail for people still researching, then why TML, the
FAQ, service area and one clear way to get in touch.

A few pages needed their own treatment rather than a copy of the opener layout:

- **Spring replacement** leads with the eight warning signs, and the safety
  warning about not attempting spring work yourself now sits directly under that
  list where it will actually be read.
- **New door installation** opens with the eight *benefits* of a new door rather
  than a fault list — the same layout, but marked in green because these are
  reasons to buy, not symptoms. The door styles you install are shown as
  photographs where photos exist, with the remaining styles listed beneath, and
  the manufacturers you carry follow after — style first, then brand, the order
  a customer decides in.
- **Commercial** keeps its two services side by side (repair and installation),
  and the preventive maintenance programme has its own section rather than being
  buried in a list.
- Where a page has one service rather than two, its lead photograph now sits
  beside the opening paragraphs instead of in a half-width panel.

Section backgrounds alternate automatically so two shaded sections can never
end up against each other and read as one long block.

---

## 2026-08-14 — Opener page rebuilt around how people actually shop

The garage door opener page has been rebuilt from the ground up between the
banner and the footer. **Every word of the existing copy is still on the page** —
what changed is the order it appears in and how it is presented.

The old page opened with a general description of the company and worked its way
toward the useful parts. The new one answers questions in the order a homeowner
with a broken door actually asks them:

1. **"Is this what mine is doing?"** — the list of twelve opener symptoms now
   sits near the top, in three scannable columns, so a visitor finds their exact
   problem in seconds instead of scrolling past sales copy. Call, text and
   booking buttons sit directly underneath it.
2. **"What is this going to cost me?"** — the pricing promise comes next, before
   any selling. Being upfront about pricing early is what separates you from the
   companies people are afraid of hiring.
3. **"What does the job involve?"** — repair and replacement side by side, each
   with a real photograph of your own technicians at work.
4. **Proof** — the 5.0 rating from 213 Google reviews.
5. **The detail** — opener types, features and brands, lower down where the
   person doing research will find them without slowing down the person whose
   door is stuck.
6. **Why customers choose TML**, the FAQ, service area, and one clear closing
   call to action.

The eleven-step installation list now has a section of its own below the two
services, numbered in the order the work actually happens, three columns wide on
a desktop and one on a phone. Previously it sat inside one of the two side-by-side
columns and made that column roughly three times taller than the one next to it.

Presentation notes: the content column is centred with generous line spacing,
section backgrounds alternate so each part reads as a distinct answer, and the
symptom list uses simple ruled rows rather than boxes so twelve items stay
readable. On a phone everything stacks to one column with nothing cut off, and
the call/text bar stays fixed at the bottom.

This is the first of the four service pages, built for review before the same
treatment is applied to the others.

---

## 2026-08-14 — Service pages no longer sit against the left edge

The service pages were built as two columns: the article on the left and a
sidebar on the right. The sidebar holds three links and is about 150px tall,
but the pages are now several thousand pixels long — so past the first screen
the text was jammed against the left edge with a permanent empty band roughly a
third of the page wide running all the way down the right.

- **The article is now a single centred column** with equal margins on both
  sides, so the page reads as balanced at every point on the way down instead of
  pushed to one side.
- **The "Our Services" links moved to the end of the article** as a row of
  cards. They still link to the other services, which helps both visitors and
  search engines, but no longer cost a third of the page width for the entire
  length of the page to do it.
- Checked at desktop and phone widths: nothing overflows and the link row drops
  to a single column on a phone.

---

## 2026-08-14 — Duplicate "Need this fixed today?" blocks removed

Each service page was ending with the same green call-to-action band printed
**three times in a row**, directly below a fourth green band saying much the
same thing. Four near-identical panels stacked at the bottom of the page.

- **The three copies are now one.** A build step was adding the band each time
  it ran without clearing the previous one, so the copies accumulated. The step
  has been corrected and a check now removes stragglers automatically.
- **The two remaining bands are now a single block.** They were the same green,
  28px apart, and both carried the same "Call (832) 887-8747" button. The one
  that names the actual service was kept, and the text-message button moved into
  it, so every way of reaching TML is still one click away: **Call, Text, or
  Book online, together in one panel.**

---

## 2026-08-14 — Google reviews section repaired

The Google reviews block on the service pages was rendering as a column of
very narrow, extremely tall cards — unreadable, and the opposite of the
credibility boost it is there to provide.

- **Two leftover styles from the old site were squeezing the cards.** The old
  theme caps quote boxes at 60% width and adds a thick inner border and 39px of
  padding on every side. Applied to a review card sitting in the article
  column, that left about 180px for the text, so each card stretched to over
  1,500px tall. Both are now overridden inside the reviews block: **cards went
  from 143px wide and 1,559px tall to 260px wide and 414px tall**, and the whole
  section shrank from roughly 3,000px to 1,250px.
- **The card grid now adapts to the space it has.** It was fixed at three
  columns, which only works across the full page width. It now fits as many
  columns as will comfortably hold a readable card, so the section works in the
  narrower article column as well as full width.

---

## 2026-08-14 — Page content no longer sits shifted to the left

On the service pages the whole body of the page was pinned to the left with a
wide empty band down the right-hand side. The cause was a single missing
closing tag in the page's HTML.

- **The "Our Services" sidebar had been swallowed by the main column.** These
  pages are built as two columns — the article on the left, the service list on
  the right. One tag left unclosed by an earlier edit put the sidebar *inside*
  the article column instead of beside it. Browsers do not report this; they
  quietly repair it and carry on, which is why the page still looked
  reasonable — just narrow, left-aligned, with the service list stranded at the
  bottom.
- **Fixed on all nine affected pages** — the seven service pages, the services
  hub and the booking page. The sidebar is back alongside the content and the
  page fills the width again.
- The tool that made the original edit has been corrected, and a check now runs
  at the end of every build so a page can no longer be published with an
  unclosed tag.

---

## 2026-08-14 — Images fixed and the whole site made 9x lighter

A polish pass over the service pages turned up one broken image and one much
bigger problem underneath it.

- **A photo that never loaded.** The technician-and-customer photo on the
  opener page pointed at the wrong asset folder, so visitors saw an empty grey
  box where the picture should be. Fixed.
- **The site was shipping 20 MB of images per page.** The original Webflow
  export uses 2 MB photographs everywhere, including as small thumbnails, and
  even Webflow's own smaller fallbacks stayed in the same heavy format. A
  single service page pulled about 20 MB of images. Every content photo is now
  also published in a modern compressed format at four sizes, and the browser
  picks the smallest one that suits the visitor's screen. **The same page now
  loads about 2 MB — roughly a ninth of what it was.** On a phone on cell
  service that is the difference between a page that appears and a page
  someone abandons. The original files are untouched and still serve as a
  fallback.
- **The photo banner under each page title** was locked to a fixed box that
  cropped the photograph awkwardly, sat with square corners while everything
  around it is rounded, and overhung the text column by about 60 px. It now
  matches the section photos below it and lines up with the text.
- **Section styling brought in line with the rest of the page.** Corner radii,
  spacing, text sizes and chip shapes in the new sections were each a pixel or
  two off from the same elements elsewhere on the page; they now use identical
  values. Paragraph width is capped for readability instead of running the full
  page width.
- **Door-style gallery fixed.** Leftover styling from the old site was making
  the cards half-width with large gaps between them on phones. They now fill
  the column and sit in an even grid.
- **Two ordering bugs.** An intro line ending in a colon was printing after the
  list it introduces, and one heading was claiming a photo layout it had no
  content for, leaving an empty column beside it.

---

## 2026-08-14 — Service-page copy broken into designed sections with photos

The service pages carried long unbroken walls of text — a heading followed by
a plain bulleted list, several times over. On a phone that reads as a scroll
with nothing to hold on to. The words are unchanged; the layout around them
is not:

- **Real TML job photos placed beside the copy.** Each major section now sits
  next to a photograph from TML's own library — a technician on a torsion
  spring, a completed door install, a commercial bay, an operator being wired.
  No stock photography and no AI-generated images: for a trade where customers
  are afraid of being scammed, real crews on real jobs are the proof.
- **Symptom lists now read as warning cards.** "Signs you need…" and "Common
  problems…" bullets became two-column cards with a red alert badge, so a
  visitor scanning for their own symptom finds it in a glance instead of
  reading a paragraph-shaped list.
- **"What's included" lists became green checklists**, two columns on desktop
  and one on a phone, which reads as a promise of work delivered rather than
  an inventory.
- **Door and opener types became tiles**, and the residential page's door
  styles now show photographs for the styles TML has pictures of, with the
  remaining styles listed as tiles underneath — previously photos and
  text-only entries were mixed in one grid, leaving ragged holes.
- **Removed two duplicated blocks per page.** Each page repeated a "Why choose
  us" section and a second, longer service-area list that the page already
  covers in its own panels. Saying it twice does not make it truer, and the
  duplicate city list was the kind of block search engines discount.
- **Fixed text that displayed as code.** Apostrophes and ampersands in the
  original copy were rendering as `won&#x27;t` and `&amp;` in some headings.

---

## 2026-08-14 — The four main service pages rebuilt

Spring repair, opener repair/installation, new door installation, and
commercial doors now follow one proven layout. **Every word of the original
service content was kept** — the symptom lists, what's-included lists, and
door/opener types are all still there. What's new around them:

- **A banner that matches what people searched for**, with the phone number,
  the 5.0/213 Google rating and same-day promise visible before any
  scrolling — on a phone as well as a computer.
- **Straight answers up top.** Each page opens with the three questions
  customers actually ask ("What causes a garage door spring to break?",
  "Should I repair or replace my opener?") answered in a short paragraph
  each. This is also the format Google and AI assistants quote.
- **A "what will it cost?" block** explaining that the technician gives the
  full price before any work starts. *When the owner gives us his
  starting prices, they drop straight into this block.*
- **A plain-spoken "how we keep this straightforward" panel** — you approve
  the price first, a real person answers, our own technicians, weekends
  cost the same.
- **Reviews, opener brands, service areas, a fuller FAQ, and a closing
  call band** on every page.
- **Fixed unfinished text in the original site:** two pages still said
  "[Your Company Name]" where the business name belonged — visible to
  customers on the live site today.

## 2026-08-14 — Search-engine address problems fixed sitewide

- **Every page now tells Google its correct address.** None of the 36 pages
  had a "canonical" tag — the line that tells search engines which web
  address is the official one for a page. All 36 have one now.
- **Removed the last references to the old misspelled domain.** The About
  page was telling Facebook, LinkedIn and search engines that it lived at
  "tmlhomeimprovment.com/about-us" (an address that doesn't exist), and the
  Services page did the same. Both now point at tmlgarageservices.com.

> **Action needed on the live website (we cannot change it from here):**
> the current Services page at tmlgarageservices.com contains a setting
> that tells Google **not to list it at all** ("noindex"), left over from
> when the site was built. That page cannot appear in search results until
> someone removes that setting in Webflow. The same page also points to the
> misspelled old domain. These are switches inside the Webflow editor —
> whoever manages that account needs to flip them.

## 2026-08-14 — Services page rebuilt around garage doors

- **The Services page was still selling home remodeling.** Its description
  read "Our home renovation services are the perfect fit for homeowners who
  want to improve their home comfort," and the page closed with "bring your
  vision to life… discuss your renovation ideas" — leftovers from the old
  TML Home Improvement website. All of it is now garage-door copy.
- **Two invisible problems, both fixed.** The page was telling Google *not
  to list it* (a "noindex" tag left over from the old site build), and its
  share/link address pointed at a misspelled old domain
  ("tmlhomeimprovment.com"). Left alone, that page could never appear in
  search results. *(See the note below about the live site.)*
- **Rebuilt as a real services hub:** phone-first banner with the 5.0/213
  Google rating, all seven services as cards with photos and plain-English
  one-liners, a "what you can expect" panel (price before the work, a real
  person answers, our own technicians, weekends cost the same), opener
  brands, service areas, the review wall, six common questions answered,
  and a closing "Garage door won't open?" call band.
- **Added the structured data search engines and AI assistants read**:
  service listings, breadcrumbs, and the FAQ — on top of the business and
  review data already sitewide.

## 2026-08-14 — Service pages: FAQs and the booking call-out separated

- **On all four service pages, the "Schedule … Today" call-out was buried
  inside the FAQ list** — it ran on straight after the last answer, so it
  read like one more question instead of the invitation to book. It's now
  its own green panel with a Call button and a Book online button.
- **The questions themselves are now a proper FAQ block** — tap-to-open
  cards under a clear heading, instead of a wall of headings and
  paragraphs.
- **Added FAQ structured data to those pages**, so Google and AI assistants
  can pull the answers directly into results.

## 2026-08-14 — Cleaner homepage banner

- **Removed the "☎ CALL NOW / 832-887-8747" box** from the top-left of the
  homepage banner — the phone number is now in the header button, the
  banner button, and (on phones) the bottom Call bar, so the floating box
  was a fourth copy competing with them.
- **The banner text now sits in the same semi-transparent black panel**
  used elsewhere on the site, at every screen size — previously it was
  white-on-white over the video on larger screens and only readable on
  phones.
- **Moved the red Emergency Service button to the right side** so it no
  longer sits on top of the banner text and buttons.

## 2026-08-14 — Simpler header, stronger calls to action

- **The menu is now four items:** Home · Services · Brands · About. Service
  Areas moved down to the footer (where location lists belong, and where
  they still help local search), and the separate "Schedule Service" menu
  item is gone — booking is now the button.
- **The header ends with two buttons instead of a phone label:** a
  tap-to-call button showing (832) 887-8747, and a green **Book Now**
  button that goes straight to the booking page. Both are full-width and
  side-by-side on phones.
- **Rebuilt the mobile menu so it opens reliably** — it now opens and
  closes on its own logic instead of depending on the old site's
  interaction script, closes when you pick a link, tap outside, or press
  Escape, and lists everything left-aligned with the call and Book Now
  buttons at the bottom.

## 2026-08-14 — Schedule page rebuilt as a real booking page

- **The scheduling page is now built to book jobs, not just describe them.**
  It opens with what matters to someone with a broken door (same-day, no
  weekend surcharge, upfront pricing, 5.0 from 213 Google reviews), then
  puts booking front and center with the phone number and a $69 tune-up
  offer alongside it.
- **Ready for Workiz Online Booking.** The booking panel is wired to drop in
  TML's Workiz scheduler the moment the account is connected — including
  automatic tracking of which ad or campaign each booking came from. Until
  then, the page books through the existing online calendar and call/text,
  so it's converting today.
- **Kept the page focused on one action.** Booking and the phone number are
  the only things competing for attention, followed by answers to the five
  questions people ask before scheduling — cost, speed, weekends, what
  happens next, financing. Those answers are marked up so Google and AI
  assistants can quote them.

## 2026-08-14 — Reviews restyled as a credibility showcase

- **The review sections are now a proper selling moment.** A large "5.0"
  score with gold stars, the Google logo, "213 five-star Google reviews,"
  and a green "Read them all on Google" button sit alongside the reviews
  themselves — presented as clean white cards with the reviewer's initial,
  name, and date.
- **On phones the reviews are a swipeable carousel** that advances on its
  own every 2 seconds, with progress dots underneath. Swiping pauses the
  auto-advance for a few seconds so no one loses their place mid-read, and
  visitors who prefer reduced motion get a static, swipeable version.
- **On desktop** the score sits in a column on the left with all six
  reviews in a card grid beside it.

## 2026-08-14 — Homepage: texting button clarified and centered

- The blue button below the contact form said "CHAT WITH US NOW" but
  actually opens a text message. It now says **"💬 Send Us a Text"**, is
  centered on the page, and the texting link was normalized so it works
  reliably on both iPhone and Android.

## 2026-08-14 — Homepage: Contact Us upgraded to a button

- In the green "Garage Door Repair &amp; Installation Services" section,
  the "Contact Us" text link is now a white button (desktop and mobile) —
  much more visible against the green background.

## 2026-08-14 — Every image described for Google and accessibility

- **253 photos had no description (alt text)** — invisible to screen
  readers and to Google Images. All now have descriptions: we hand-wrote
  accurate ones for the key photos (looking at each image — e.g. "TML
  technician adjusting a garage door torsion spring," "TML-branded garage
  door torsion springs"), and derived the rest from their filenames.
- **Removed image references that pointed at files that don't exist** — a
  silent error on every page load, inherited from the original site.

## 2026-08-14 — Mobile rework: one clean way to reach you

- **A Call / Text bar now sits at the bottom of every page on phones** — two
  big thumb-friendly buttons: CALL dials (832) 887-8747, TEXT starts a text
  message to the same number. Always visible, never covers the content.
- **Removed the three competing phone buttons from the mobile view** — the
  "CALL NOW" box and phone button in the homepage banner, and the floating
  red emergency button that used to sit on top of text and form fields.
  One clear path beats three overlapping ones.
- **The homepage banner text is finally readable on phones** — it now sits
  in a semi-transparent dark panel over the video instead of white text on
  a white garage door.
- **"Explore Services" is now an actual button** on mobile instead of a
  small text link.

## 2026-08-14 — Financing message made readable

- **"Renovate Now. Pay Later." was light gray on a green background** on the
  contact and schedule pages — nearly invisible. Financing is a real selling
  point on bigger jobs; the line is now white and clearly readable.

## 2026-08-14 — A share card that sells

- **Sharing the site used to show a stock template avatar** (or no image at
  all — the picture link was broken in a way sharing platforms ignore).
  Every page now shares with a purpose-built card: the garage photo,
  "Same-Day Garage Door Repair," the phone number front and center, a
  "Call Now — We Answer" button, and the real 5.0★ / 213-review rating
  with a customer quote. Texting or posting any page of the site is now a
  little advertisement.

## 2026-08-14 — Page structure for search engines

- **Every page now has exactly one main headline.** Service pages had 4–5
  competing "main headlines" (H1s), the homepage had 3, and all eight blog
  posts had none at all (their titles were plain styled boxes). 17 extra
  headings were demoted to sub-headings and the 8 blog titles were promoted
  to real headlines. Nothing changed visually — this is how Google and
  screen readers read the page's outline.

## 2026-08-14 — Search listings for the brand pages

- **The four opener-brand pages (LiftMaster, Genie, Chamberlain, Craftsman)
  all had the same generic title** — "TML Garage Door Services" — and no
  description. These are the pages that should win searches like
  "LiftMaster garage door opener repair Houston." Each now has a unique
  title ("LiftMaster Garage Door Opener Repair &amp; Installation | TML
  Garage Services | Conroe, TX") and a description with the service area
  and phone number.
- **Nine more pages were missing descriptions** (contact, The Woodlands
  page, legal pages) — all filled in. Title and description are what
  searchers read in a Google listing; every page now has its own.

## 2026-08-14 — Contact page headline repaired

- **The contact page's main headline was a full paragraph that cut off
  mid-word** — it ended "…or a routine maintena" (the text was truncated in
  the original site's content, not a display glitch). The headline is now
  the first sentence — "TML Garage Door Services is here to help." — with
  the rest as normal text below, and the cut-off sentence completed:
  "Whether it's an emergency repair or routine maintenance, we're ready to
  help." *Owner: we finished that sentence for you — happy to change the
  wording if you had something else in mind.*

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
