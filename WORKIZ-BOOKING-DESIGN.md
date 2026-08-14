# Native booking → Workiz API — design

**Question:** keep the "pick a time" experience on tmlgarageservices.com and push
the booking into Workiz via API, instead of embedding Workiz's iframe?

**Answer: yes — with one constraint that shapes the whole design.**

## The constraint

Workiz's Developer API (api.workiz.com/api/v1) exposes **Jobs** (create, update,
assign, payments), **Leads** (create, convert, mark lost), **Team**, and
**Time Off**. It does **not** expose real-time technician availability or open
appointment slots.

So a native picker cannot show *true* open slots. It can show **offerable
windows** (from business rules we control) and create the job in Workiz the
moment someone picks one. TML then confirms — which is exactly what their
current copy already promises ("our team will contact you shortly to confirm
your appointment").

That is the honest, higher-converting model anyway: fewer steps, our own fast
mobile UI, no third-party iframe, and the customer still gets a real
confirmation from a human.

| | Workiz iframe (built, ready) | Native picker + API (this design) |
|---|---|---|
| Real availability | Whatever Workiz shows | Offerable windows, confirmed after |
| Speed / mobile UX | Third-party, slower | Ours, instant, matches the site |
| Design control | None | Full |
| Attribution | `ad_group` param | Full UTM/gclid → job fields + our own DB |
| Lead safety | Workiz owns it | We store every lead ourselves too |
| Build cost | Done | ~1 day + testing |

## Architecture

```
Browser (booking page)
  └─ POST /api/book   (same origin, no token in the browser)
       │
Cloudflare Worker  (tmlgarageservices)
  ├─ 1. Validate + normalize (phone, address, window)
  ├─ 2. Turnstile verify (spam gate)
  ├─ 3. Idempotency check   (KV: hash of phone+window, 10 min)
  ├─ 4. Persist lead        (D1: every submission, before anything else)
  ├─ 5. POST Workiz  api/v1/{token}/job/create/   ──► job in Workiz
  ├─ 6. Notify TML          (Resend email + optional SMS)
  └─ 7. Return {ok, ref}    → thank-you state + dataLayer conversion event
```

**Rule: step 4 and step 6 never depend on step 5.** If Workiz is down, rejects
the payload, or the token expires, the lead is still saved and TML is still
emailed. A booking must never be lost because an API call failed. Failed
Workiz pushes land in a retry queue (Cloudflare Queues or a cron'd D1 sweep)
and are visible in a small admin view.

## Frontend (what the customer sees)

Three short steps on one screen — no page loads:

1. **What's wrong?** — chips: Broken spring · Won't open · Opener · Off track ·
   New door · Other (chips pre-fill the job type; one tap, no typing)
2. **When?** — next 7 days as day cards, then a window: Morning (8–12),
   Afternoon (12–4), Evening (4–7). Emergency/today gets a red "Call now"
   nudge, because a phone call beats a form for a stuck door.
3. **Where + who** — name, mobile, address (Google Places autocomplete),
   optional notes. Phone field first: it's the field that matters.

Then: instant on-page confirmation with a reference number, a "we'll text you
to confirm" line, and the phone number for anyone who wants to talk now.

Conversion details that matter: no account creation, no email required (phone
is enough), address autocomplete to kill typing, the whole thing above the
fold on a phone, and the sticky CALL/TEXT bar stays visible throughout.

## Data mapping (our form → Workiz job)

| Our field | Workiz field | Notes |
|---|---|---|
| first / last | `FirstName`, `LastName` | split on submit |
| phone | `Phone` | E.164 normalized |
| email (optional) | `Email` | |
| address | `Address`, `City`, `State`, `PostalCode`, `Country` | from Places result |
| chosen day + window | `JobDateTime` | ISO 8601, window start; end via `JobEndDateTime` if accepted |
| problem chip | job type / `JobType` | mapped to TML's Workiz job types |
| notes | job description | |
| utm_source / utm_campaign / gclid | job source / custom field | so booked revenue ties back to the ad that caused it |

TML confirms and adjusts the exact arrival time in Workiz — the API booking is
the *request*, their dispatcher owns the calendar.

## Security

- **API token lives only in Worker secrets** (`wrangler secret put WORKIZ_TOKEN`,
  `WORKIZ_SECRET`). Never in the page, never in the repo, never in git history.
- **Cloudflare Turnstile** on the form (the `turnstile-spin` skill automates the
  widget + siteverify Worker).
- **Rate limit** per IP and per phone number (KV counter), plus a honeypot field.
- Server-side validation of every field; the browser is never trusted.
- No PII in logs or query strings.

## Testing plan (before it touches the real account)

1. **Dry-run mode** — `DRY_RUN=1` env: everything runs, Workiz call is logged
   not sent. Confirms validation, storage, email, and the UI end to end.
2. **Sandbox booking** — first real call creates a test job in Workiz named
   `TEST — website booking`, then delete it in the Workiz UI.
3. **Field audit** — book one of each problem type; confirm in Workiz that
   name, phone, address, time window, job type, and source all landed right.
4. **Failure drill** — deliberately break the token; confirm the customer still
   sees success, the lead is still in D1, and TML still gets the email.
5. **Attribution check** — book through a `?utm_source=google&utm_campaign=x`
   link; confirm the campaign shows on the Workiz job.

## Rollout

- **Phase 1 (now):** the page already books via the existing calendar link and
  call/text, and the Workiz *iframe* slot is wired and tested — set
  `TML_WORKIZ.account` and it goes live in one line.
- **Phase 2 (when API access lands):** build the native picker behind a flag,
  run it in dry-run, then A/B it against the iframe on real traffic. Whichever
  books more jobs per 100 visitors wins.
- **Phase 3:** feed booked jobs back into the market dashboard so cost-per-lead
  becomes cost-per-*booked-job* with real numbers instead of assumptions.

## What's needed to start Phase 2

1. Workiz **Developer API** add-on enabled (Settings → Integrations → Developer),
   then the **API token + secret**.
2. The list of TML's **job types** in Workiz, so the problem chips map cleanly.
3. Confirmation of their real **service hours** and how far ahead they'll book.
4. A decision on the lead store: **D1** (queryable, feeds the dashboard) or
   plain email only.

---
*Companion to `build_booking_page.py`, which renders the live booking page and
already contains the Workiz iframe slot (`TML_WORKIZ`) and UTM→`ad_group`
attribution.*
