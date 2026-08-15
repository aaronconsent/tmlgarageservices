#!/usr/bin/env python3
"""Replace the template blog with articles about garage doors.

What was there: eight posts on concrete, fencing, sustainable construction,
windows, historic restoration, foundations and HVAC — the Webflow template's
own demo content, headlines over lorem ipsum. Nothing to do with TML, and
nothing a person searching for a garage door would ever want.

What replaces it: five articles on the questions people actually type before
they call a garage door company — what a spring replacement costs, why the door
will not close, whether to repair or replace, what Gulf Coast heat and humidity
do to the hardware, and which opener drive to buy. Each one answers the question
first and links to the relevant service page second.

Topic selection note: this was researched from published cost guides and the
"most asked" lists that garage door companies and Angi maintain, not from
measured keyword volume — there is no DataForSEO login on this machine. The
five are safe picks either way; if volume data turns up, the ranking of what to
write next is worth revisiting.

Two content rules held throughout:
  * No price is attributed to TML. Cost ranges are published national figures,
    labelled as such. TML's own pricing is not documented anywhere I can verify,
    and a blog post is a bad place to invent it.
  * No claim about TML's history, staffing or credentials beyond what the rest
    of the site already says.

Idempotent: it rebuilds the same five posts and the index from scratch each run,
and removes the template posts if they are still present.
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
F = ROOT / "site" / "fixed"
B = F / "blogs"
LIVE = "https://www.tmlgarageservices.com"

PHONE = "(832) 887-8747"
TEL = "tel:+18328878747"
BOOK = "/fixed/schedule-consult"

OLD_POSTS = [
    "concrete-jungle-exploring-the-versatility-and-strength-of-concrete-in-construction",
    "enhancing-security-and-privacy-with-quality-fencing-solutions",
    "how-sustainable-construction-practices-are-shaping-the-future",
    "innovations-in-sustainable-infrastructure-building-for-the-future",
    "selecting-the-right-windows-for-energy-efficiency-and-style",
    "the-art-of-historic-restoration-and-adaptive-reuse-in-construction",
    "the-science-behind-foundation-construction-why-it-matters",
    "understanding-heating-ventilation-and-air-conditioning-in-construction",
]

IMG = {
    "repair": ("/assets/66b2dae9e779df43d0d269c9/66b2ec2555069ca418a48646_"
               "garage-door-repair-and-installer.png",
               "TML technician servicing a residential garage door"),
    "work": ("/assets/66b2dae9e779df43d0d269c9/6a54211784c18aea72a3603c_IMG_2909.jpg",
             "Garage door track and rollers during a service call"),
    "install": ("/assets/66b2dae9e779df43d0d269c9/66b2ec2561b760fe6fee299b_"
                "549fbd18a3bc84b4e30fc12d9d7d4ccb_new-garage-door-service-install-conroe.png",
                "Newly installed garage door on a Conroe home"),
    "dusk": ("/assets/66b2dae9e779df43d0d269c9/6a6638dbf310548aa6535691_"
             "copy_AE586C56-1DE3-4700-978C-82BBC75C202F_poster.0000000.jpg",
             "Modern home with a dark sectional garage door at dusk"),
    "opener": ("/assets/66b2dae9e779df43d0d269c9/6a542e2ec6b8791b21582f07_"
               "Photo%20Jul%2012%202026%2C%207%2009%2027%20PM%20(2)%20(1).png",
               "TML technician installing a LiftMaster garage door opener"),
}

CTA = (
    '<h3>Get it looked at</h3>'
    f'<p>TML Garage Door Services covers Conroe, The Woodlands, Spring and the greater '
    f'Houston area, with same-day appointments and the full price quoted before any work '
    f'starts. <a href="{BOOK}">Book online</a> or call '
    f'<a href="{TEL}">{PHONE}</a>.</p>')

POSTS = [
    {
        "slug": "garage-door-spring-replacement-cost",
        "title": "What Garage Door Spring Replacement Costs — and Why",
        "meta": "What garage door spring replacement typically costs, why springs are "
                "replaced in pairs, and why torsion springs are not a DIY job.",
        "date": "Jul 8, 2026",
        "img": "repair",
        "excerpt": "Published cost guides put a single spring in the low hundreds and a "
                   "pair higher still. Here is what you are actually paying for.",
        "body": """
<p>A broken spring is the most common reason a garage door stops working, and
it is usually the first time a homeowner has any reason to think about what a
spring costs. The number that comes back on the phone can feel high for a part
that looks like a piece of coiled steel. It helps to know what the spring is
doing.</p>

<h2>The spring, not the opener, lifts the door</h2>
<p>A double garage door weighs somewhere between 200 and 400 pounds. The opener
motor is not strong enough to lift that and was never designed to. What lifts
the door is the spring, which stores energy as the door comes down and gives it
back as the door goes up. The opener only nudges a load the spring has already
balanced.</p>
<p>That is why a door with a broken spring will not open even though the motor
runs, and why a door that is out of balance burns out openers. The spring is the
part doing the work.</p>

<h2>What the price range looks like</h2>
<p>National cost guides published in 2026 — This Old House, Angi and HomeAdvisor
among them — put a single spring replacement roughly in the $300 to $750 range
installed, and a pair somewhere between $500 and $1,500, depending on the door,
the spring type and the region. Those are national figures, quoted here so you
have a reference point; they are not TML's prices. Ask any company you call for
the full number before work begins.</p>
<p>What moves the price within that range:</p>
<ul>
<li><strong>Torsion or extension.</strong> Torsion springs mount on a bar above
the door and cost more; extension springs run along the tracks either side.</li>
<li><strong>Door weight and size.</strong> A heavy insulated double door needs a
higher-cycle spring than a light single.</li>
<li><strong>Spring life rating.</strong> A standard spring is rated around
10,000 cycles — roughly seven years at four openings a day. High-cycle springs
cost more up front and last considerably longer.</li>
<li><strong>Timing.</strong> Same-day and after-hours calls carry a premium at
most companies.</li>
</ul>

<h2>Why both springs get replaced</h2>
<p>If your door has two springs, they were installed together and have taken the
same number of cycles. When one goes, the other is at the end of its life too.
Replacing only the broken one usually means paying for a second call within a
year, and it leaves the door running unbalanced in the meantime. Most companies
will recommend the pair. That is not an upsell; it is the arithmetic of matched
components.</p>

<h2>This is the one repair not to do yourself</h2>
<p>A wound torsion spring holds a serious amount of stored energy, and it
releases all of it if the winding bars slip. Injuries from this are severe and
well documented. The tooling matters, and so does knowing the correct number of
turns for your door's height and weight. Cables, drums and the shaft all have to
be set correctly afterwards or the door runs crooked.</p>
<p>Nearly everything else on a garage door is reasonable to inspect yourself.
Springs are the exception.</p>

<h2>What to ask before you agree</h2>
<ul>
<li>Is the quote for one spring or both?</li>
<li>What cycle rating are the springs, and what does the higher rating cost?</li>
<li>Does the price include labour, the trip and any hardware that has to come
off to reach the spring?</li>
<li>Is there a warranty on the part and on the labour, and how long?</li>
</ul>
<p>A company that answers those four plainly is generally a company worth
booking. If you want the detail on how the job runs, our
<a href="/fixed/our-services/garage-door-spring-replacement">garage door spring
replacement page</a> walks through it.</p>
""",
    },
    {
        "slug": "garage-door-wont-close",
        "title": "Garage Door Won't Close? Seven Things to Check First",
        "meta": "The seven usual causes when a garage door refuses to close, in the order "
                "worth checking, and the point at which to stop and call someone.",
        "date": "Jul 15, 2026",
        "img": "work",
        "excerpt": "Most of the time it is the safety sensors, and most of the time you "
                   "can fix that yourself in five minutes.",
        "body": """
<p>A door that opens fine but will not close is one of the most common calls we
get, and it is also the one most likely to have a fix you can do standing in
your own garage. Work down this list in order — it runs from the most common
cause to the least, and from safest to check to least safe.</p>

<h2>1. The safety sensors</h2>
<p>Two small photo-eye units sit near the floor on either side of the opening,
about six inches up, pointed at each other. If the invisible beam between them
is broken, federal safety rules require the opener to refuse to close. Every
opener sold since 1993 has them.</p>
<p>Look for the indicator light on each sensor. One steady light and one
flickering or dark light means they are out of alignment or something is in the
way. Check for:</p>
<ul>
<li>A bin, bike, bag of soil or coiled hose sitting in the beam</li>
<li>Cobwebs or dust on the lens — wipe both with a dry cloth</li>
<li>A sensor knocked out of aim, which happens easily. Loosen the wing nut,
sight it at its partner, retighten when both lights are steady</li>
<li>Low afternoon sun straight into a lens, which genuinely does blind them</li>
</ul>
<p>This is the cause perhaps half the time.</p>

<h2>2. The wall button versus the remote</h2>
<p>Try closing from the wall button. If the wall button works and the remote
does not, the problem is the remote — usually a flat battery, occasionally lost
programming. If neither works, the problem is at the opener.</p>

<h2>3. The manual lock</h2>
<p>Many doors have a slide lock or a lock button on the wall console that
disables the remote. It gets pressed by accident more often than you would
think, particularly by children and houseguests.</p>

<h2>4. Something in the track</h2>
<p>Run your eye down both vertical tracks. A stone, a hardened lump of debris or
a bent section will stop the door and, on a well-adjusted opener, trigger the
reverse. Look also for a roller that has jumped out of the track.</p>

<h2>5. The close-limit setting</h2>
<p>The opener needs to know where the floor is. If the limit is set too low it
drives the door into the ground, senses resistance and reverses on the
assumption it hit something. If your door closes fully and then immediately
opens again, this is the likely cause. There is an adjustment screw on the
opener housing, and the manual for your model will tell you which way to turn
it — small movements.</p>

<h2>6. A broken spring</h2>
<p>Pull the emergency release cord and try to lift the door by hand. A balanced
door moves with modest effort and stays where you leave it at waist height. If
it is extremely heavy, slams down, or you can see a visible gap in the coil of
the spring above the door, stop there. Do not use the opener and do not stand
under the door. That is a
<a href="/fixed/our-services/garage-door-spring-replacement">spring replacement</a>,
and it is not a DIY repair.</p>

<h2>7. A frayed or slack cable</h2>
<p>Look at the steel cables running down each side. They should be taut and
evenly wound on the drums. A cable that has gone slack, frayed or jumped its
drum will make the door hang crooked and bind. Like springs, this is a
tensioned-component repair and belongs with a technician.</p>

<h2>Where to stop</h2>
<p>Items 1 through 5 are all reasonable to check and often to fix. Items 6 and 7
involve parts under load, and a door that comes down uncontrolled is dangerous.
If you get that far down the list, leave the door where it is.</p>
""" + CTA,
    },
    {
        "slug": "repair-or-replace-garage-door",
        "title": "Repair or Replace? Deciding on an Aging Garage Door",
        "meta": "How long garage doors and openers last, the signs that point to "
                "replacement rather than another repair, and how to weigh the two.",
        "date": "Jul 22, 2026",
        "img": "install",
        "excerpt": "Doors last decades; openers do not. Here is how to tell which one "
                   "you are actually dealing with.",
        "body": """
<p>There is a point where paying for another repair stops making sense, and it
is not always obvious from inside the garage. The useful first step is to
separate the door from the opener, because they age on completely different
schedules.</p>

<h2>Two systems, two lifespans</h2>
<p>A well-made steel door, kept lubricated and balanced, commonly lasts 20 to 30
years. The opener that drives it typically lasts 10 to 15. Springs are shorter
still — a standard spring is rated around 10,000 cycles, which is roughly seven
years of ordinary use.</p>
<p>So a 20-year-old door on its third opener is entirely normal, and replacing
the opener alone is often the right answer. A 20-year-old door with cracked
panels is a different conversation.</p>

<h2>Signs that point to replacing the door</h2>
<ul>
<li><strong>Damage across more than one panel.</strong> A single dented panel
can often be swapped. Once several are damaged, or the matching panel is
discontinued, replacement usually wins.</li>
<li><strong>Rot or delamination on a wood door.</strong> Gulf Coast humidity is
hard on wood. Once water has got into the core, patching buys a season.</li>
<li><strong>Sagging.</strong> If the door is no longer square in the opening, or
the top section flexes when it lifts, the structure is going.</li>
<li><strong>Repeat visits.</strong> Three service calls in two years on the same
door is a spending pattern, not a run of bad luck.</li>
<li><strong>No safety reverse at all.</strong> If the door predates 1993 and has
no photo-eye sensors, it does not meet current safety requirements. With
children or pets in the house that alone is reason enough.</li>
<li><strong>Selling soon.</strong> A garage door is often a third of the front
elevation. It is one of the more reliable exterior improvements for how a house
presents.</li>
</ul>

<h2>Signs that point to repairing</h2>
<ul>
<li>The door is straight, solid and closes evenly</li>
<li>The fault is a spring, a cable, rollers, a hinge or the opener — all
replaceable parts on a sound door</li>
<li>The door is noisy rather than failing. Noise is usually worn rollers, dry
hinges or a loose opener rail, and all three are cheap to put right</li>
<li>It is under ten years old and this is the first real fault</li>
</ul>

<h2>A rough way to weigh it</h2>
<p>If a repair costs more than about half what a new door would, and the door is
already past two thirds of its expected life, replacement is usually the better
buy. Below that, repair. It is a rule of thumb rather than a law, but it stops
the decision drifting.</p>
<p>Worth adding to the sum: a new insulated door does something the old one did
not. In a Conroe summer an uninsulated attached garage bakes, and that heat
comes through the wall into the house.</p>

<h2>If you are replacing</h2>
<p>Get the measurements, the headroom and the backroom checked in person before
ordering. Our
<a href="/fixed/our-services/residential-garage-door-services">new garage door
installation page</a> covers what the visit involves.</p>
""" + CTA,
    },
    {
        "slug": "texas-heat-garage-door-maintenance",
        "title": "What Texas Heat and Humidity Do to a Garage Door",
        "meta": "How Gulf Coast heat, humidity and storms wear garage door hardware, and "
                "a short seasonal maintenance routine for Conroe-area homes.",
        "date": "Jul 29, 2026",
        "img": "dusk",
        "excerpt": "Steel expands, grease thins, wood swells and springs rust. Twenty "
                   "minutes twice a year covers most of it.",
        "body": """
<p>Garage doors in Montgomery County live a harder life than the manufacturer's
average. A south-facing door can run well above ambient temperature on a July
afternoon, the humidity sits high most of the year, and the hardware is steel
under constant tension. None of that is a crisis, but it does mean the
maintenance interval that suits a mild climate is too long here.</p>

<h2>Heat</h2>
<p>Steel expands. Over a day the tracks, hinges and rollers grow and shrink
slightly, and over years that cycling works fasteners loose. The other heat
effect is on lubricant: a light oil that behaved fine in spring thins out in
August, runs off the pivot points and leaves the metal dry.</p>
<p>Dry hinges and rollers are the usual reason a door that was quiet in March is
loud by September.</p>

<h2>Humidity</h2>
<p>Wood doors take on moisture, swell and bind in the opening, then dry and
shrink. Painted surfaces that have hairline cracks let water into the core.
Steel doors do not care, but their hardware does — springs, cables and the
torsion bar all rust in humid air, and a rusted spring fails earlier than a
clean one.</p>

<h2>Storms</h2>
<p>The garage door is usually the largest opening in the house and the weakest
point in a wind event. If wind gets in through a failed door, the pressure has
to go somewhere, and it goes into the roof. If you are replacing a door in this
region, ask what wind rating it carries — it is worth knowing what you are
buying.</p>

<h2>A twice-yearly routine</h2>
<p>Do this in spring and again in autumn. It takes about twenty minutes.</p>
<ul>
<li><strong>Watch and listen.</strong> Run the door through one full cycle from
outside. Grinding, scraping or a jerky section tells you where to look.</li>
<li><strong>Test the balance.</strong> Pull the emergency release, lift the door
by hand to waist height and let go. It should stay put. If it drops or flies up,
the spring tension is off — book that one.</li>
<li><strong>Test the safety reverse.</strong> With the opener engaged, put a
roll of paper towel flat on the floor in the door's path and close it. The door
must reverse on contact. Then wave a broom handle through the photo-eye beam
while it closes; it must reverse then too.</li>
<li><strong>Lubricate.</strong> A garage-door-specific lithium or silicone spray
on hinges, rollers, the springs and the torsion bar. Not on the tracks — those
stay clean and dry. Skip WD-40 as a lubricant; it is a solvent and it strips
what is already there.</li>
<li><strong>Tighten.</strong> Check the hinge and bracket bolts. Snug, not
forced.</li>
<li><strong>Clean the tracks.</strong> Wipe out grit with a dry cloth.</li>
<li><strong>Check the bottom seal.</strong> A cracked or flattened seal lets in
water, heat and insects. It is an inexpensive part.</li>
</ul>

<h2>What to leave alone</h2>
<p>Do not adjust, loosen or attempt to tension the springs or the cables. Those
are the parts holding the door's weight. Everything above is safe with the door
down and the opener unplugged.</p>
""" + CTA,
    },
    {
        "slug": "belt-vs-chain-drive-garage-door-openers",
        "title": "Belt Drive vs Chain Drive Openers: Which Suits Your Home",
        "meta": "Belt, chain, screw and wall-mount garage door openers compared on noise, "
                "cost and lifespan, plus the features worth paying for.",
        "date": "Aug 5, 2026",
        "img": "opener",
        "excerpt": "The right answer depends mostly on one thing: whether anyone sleeps "
                   "above or beside the garage.",
        "body": """
<p>Opener choice comes down to a small number of real differences. Most of the
marketing is about features; the mechanical decision is simpler than it looks.</p>

<h2>Chain drive</h2>
<p>A metal chain, much like a bicycle chain, pulls the trolley along the rail.
It is the oldest design, the cheapest, and the most tolerant of heavy doors. It
is also the loudest — a metallic rattle you will hear through a shared wall.</p>
<p><strong>Good for:</strong> detached garages, workshops, heavy or oversized
doors, and anyone who would rather spend the money on the door itself.</p>

<h2>Belt drive</h2>
<p>Same mechanism, but a reinforced rubber belt replaces the chain. It runs
close to silent — a hum rather than a clatter — and has fewer moving parts to
wear. It costs more, typically by a hundred dollars or so at the same feature
level.</p>
<p><strong>Good for:</strong> attached garages, and any house with a bedroom or
living room over or next to the garage. If someone is asleep on the other side
of that wall, this is the one.</p>

<h2>Screw drive</h2>
<p>A threaded steel rod turns to move the trolley. Fewer parts again, decent
speed, moderate noise. Older screw drives disliked temperature swings, though
modern ones handle it better. Less common now than it was.</p>

<h2>Wall mount (jackshaft)</h2>
<p>Rather than hanging from the ceiling, this mounts on the wall beside the door
and turns the torsion bar directly. No rail overhead, which frees the ceiling
for storage or a car lift, and it suits rooms with high or awkward ceilings. It
is the most expensive option and needs the right door hardware, so it wants
checking in person.</p>

<h2>Features that are worth it</h2>
<ul>
<li><strong>Battery backup.</strong> Our grid goes down in summer storms, and a
garage door you cannot open is a car you cannot move. This is the feature most
worth the money in this region.</li>
<li><strong>Rolling-code security.</strong> The remote's code changes every use,
so a captured signal is useless. Standard on current models; worth confirming on
anything older.</li>
<li><strong>A DC motor with soft start and stop.</strong> Quieter, gentler on
the door, usually paired with battery backup.</li>
<li><strong>Phone control.</strong> Genuinely useful for checking whether you
left it open, and for letting a delivery or a family member in.</li>
</ul>
<h2>Features that are not</h2>
<p>Built-in speakers, cameras of middling quality and colour-changing lights add
to the price and to the number of things that can fail. A separate camera you
choose yourself will be better and cheaper.</p>

<h2>Horsepower</h2>
<p>Half-horsepower handles most single doors; three-quarters is the usual choice
for a double or an insulated door; one horsepower suits heavy carriage-style and
oversized doors. Going up a size does not make the door last longer — remember
the spring does the lifting, not the motor.</p>

<h2>Brands we service</h2>
<p>We repair and install
<a href="/fixed/brands/liftmaster-garage-door-opener-repair-and-installation">LiftMaster</a>,
<a href="/fixed/brands/chamberlain-garage-door-opener-repair-and-installation">Chamberlain</a>,
<a href="/fixed/brands/genie-garage-door-opener-repair-and-installation">Genie</a> and
<a href="/fixed/brands/craftsman-garage-door-opener-repair-and-installation">Craftsman</a>
openers. If you are weighing a replacement, our
<a href="/fixed/our-services/garage-door-opener-installation">opener service page</a>
covers what the fitting involves.</p>
""" + CTA,
    },
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def set_meta(html, key, value, attr="name"):
    def repl(m):
        tag = m.group(0)
        if not re.search(rf'{attr}="{re.escape(key)}"', tag):
            return tag
        return re.sub(r'content="[^"]*"', f'content="{value}"', tag, count=1)
    return re.sub(r"<meta\b[^>]*>", repl, html)


def shell():
    """Head + header + footer from a page that already has the blog styling."""
    src = B / OLD_POSTS[0] / "index.html"
    if not src.exists():                       # already rebuilt once
        src = next((p for p in B.glob("*/index.html")), None)
    html = src.read_text("utf-8", errors="replace")
    a = html.find('<section class="title-section"')
    b = html.find('<section class="footer"')
    return html[:a], html[b:]


CARD_CSS = """<style id="tmlblog-css">
.tmlblog-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
 gap:26px;margin:0;padding:0;list-style:none;}
.tmlblog-card{margin:0;background:#fff;border:1px solid #e2e6d8;border-radius:14px;
 overflow:hidden;display:flex;flex-direction:column;transition:transform .15s ease,
 box-shadow .15s ease;}
.tmlblog-card:hover{transform:translateY(-3px);box-shadow:0 10px 28px rgba(0,0,0,.09);}
.tmlblog-card a{display:flex;flex-direction:column;height:100%;text-decoration:none;
 color:inherit;}
.tmlblog-card img{display:block;width:100%;height:190px;object-fit:cover;}
.tmlblog-body{padding:20px 22px 24px;display:flex;flex-direction:column;gap:9px;flex:1;}
.tmlblog-date{font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:#6d7563;}
.tmlblog-card h2{font-size:20px;line-height:1.3;margin:0;}
.tmlblog-card p{margin:0;font-size:15px;line-height:1.55;color:#4c5348;}
.tmlblog-more{margin-top:auto;padding-top:10px;font-weight:600;color:#587735;}
.tmlblog-card a:focus-visible{outline:2px solid #587735;outline-offset:3px;}
@media(prefers-reduced-motion:reduce){.tmlblog-card{transition:none;}}
.tmlblog-related{margin-top:44px;padding-top:30px;border-top:1px solid #e2e6d8;}
.tmlblog-related h2{font-size:20px;margin:0 0 18px;}
.tmlblog-related ul{margin:0;padding:0;list-style:none;display:grid;gap:12px;}
.tmlblog-related a{font-weight:600;}
</style>"""


def head_for(html, title, desc, url):
    t, d = esc(title), esc(desc)
    html = re.sub(r"<title>.*?</title>", f"<title>{t}</title>", html, count=1, flags=re.S)
    for k, v, a in (("description", d, "name"), ("og:title", t, "property"),
                    ("og:description", d, "property"), ("twitter:title", t, "name"),
                    ("twitter:description", d, "name"), ("og:url", url, "property")):
        html = set_meta(html, k, v, a)
    html = re.sub(r'(<link[^>]*rel="canonical"[^>]*href=")[^"]*(")', rf"\1{url}\2", html)
    html = re.sub(r'<style id="tmlblog-css">.*?</style>', "", html, flags=re.S)
    return html.replace("</head>", CARD_CSS + "</head>", 1)


def post_html(prefix, suffix, post, others):
    url = f"{LIVE}/blogs/{post['slug']}"
    head = head_for(prefix, post["title"], post["meta"], url)
    src, alt = IMG[post["img"]]
    related = "".join(
        f'<li><a href="/fixed/blogs/{o["slug"]}">{esc(o["title"])}</a></li>' for o in others)
    return (
        head
        + '<section class="title-section"><div class="w-layout-blockcontainer container '
          'w-container"><div class="blog-detail"><div class="blog-title">'
          f'<h1 class="blog-name">{esc(post["title"])}</h1>'
          '<div class="news-data"><div class="body-x-small">'
          f'{post["date"]}</div></div></div>'
          f'<div class="blog-main-img"><img src="{src}" alt="{esc(alt)}" loading="eager" '
          'decoding="async" class="blog-image"/></div></div></div></section>'
        + '<section class="rich-section"><div class="w-layout-blockcontainer container '
          'w-container"><div class="rich-wrap"><div class="rich-text w-richtext">'
        + post["body"].strip()
        + '</div><div class="tmlblog-related"><h2>More garage door advice</h2><ul>'
        + related
        + "</ul></div></div></div></section>"
        + suffix)


def index_html(prefix, suffix):
    url = f"{LIVE}/blogs"
    head = head_for(prefix, "Garage Door Advice | TML Garage Door Services",
                    "Straight answers on spring costs, doors that will not close, "
                    "repair versus replacement, Texas heat and opener choice.", url)
    cards = []
    for p in POSTS:
        src, alt = IMG[p["img"]]
        cards.append(
            f'<li class="tmlblog-card"><a href="/fixed/blogs/{p["slug"]}">'
            f'<img src="{src}" alt="{esc(alt)}" loading="lazy" decoding="async"/>'
            f'<div class="tmlblog-body"><div class="tmlblog-date">{p["date"]}</div>'
            f'<h2>{esc(p["title"])}</h2><p>{esc(p["excerpt"])}</p>'
            f'<div class="tmlblog-more">Read this &rarr;</div></div></a></li>')
    return (
        head
        + '<section class="title-section"><div class="w-layout-blockcontainer container '
          'w-container"><div class="blog-detail"><div class="blog-title">'
          '<h1 class="blog-name">Garage door advice</h1>'
          '<div class="news-data"><div class="body-x-small">'
          'The questions we get asked most, answered properly.</div></div>'
          "</div></div></div></section>"
        + '<section class="rich-section"><div class="w-layout-blockcontainer container '
          'w-container"><ul class="tmlblog-grid">'
        + "".join(cards)
        + "</ul></div></section>"
        + suffix)


FOOTER_LINK = '<a href="/fixed/blogs" class="bottom-link">Garage Door Advice</a>'


def link_from_footer():
    """Give the blog a route in from every page: without one it is orphaned, which
    is exactly the state the template posts were in."""
    n = 0
    for f in sorted(F.rglob("index.html")):
        html = orig = f.read_text("utf-8", errors="replace")
        html = html.replace(FOOTER_LINK, "")
        m = re.search(r'<a[^>]*class="bottom-link"[^>]*>', html)
        if m:
            html = html[:m.start()] + FOOTER_LINK + html[m.start():]
        if html != orig:
            f.write_text(html, "utf-8")
            n += 1
    return n


def main():
    prefix, suffix = shell()

    removed = 0
    for slug in OLD_POSTS:
        d = B / slug
        if d.exists():
            shutil.rmtree(d)
            removed += 1

    for post in POSTS:
        others = [p for p in POSTS if p["slug"] != post["slug"]][:3]
        d = B / post["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(post_html(prefix, suffix, post, others), "utf-8")

    (B / "index.html").write_text(index_html(prefix, suffix), "utf-8")

    print(f"template posts removed: {removed}")
    print(f"articles published: {len(POSTS)}")
    print("index page: /blogs/")
    print(f"footer link added on: {link_from_footer()} page(s)")


if __name__ == "__main__":
    main()
