#!/usr/bin/env python3
"""Rebuild the body of a service page: everything between the hero and the
shared footer blocks.

Architecture follows the order a homeowner with a broken door actually asks
things in:

  1. triage      - "is this what mine is doing?"  their symptom, within a screen
  2. price       - "what will this cost me?"      answered before we sell
  3. the work    - repair vs replace, side by side, with real photos
  4. proof       - 5.0 from 213 Google reviews
  5. specs       - types / features / brands, for the researcher not the panicked
  6. why us      - the client's own reasons, on a dark panel
  7. FAQ         - accordion
  8. area + CTA  - where we work, then one clear way to act

Every word of the client's copy is preserved; only sequence and presentation
change. Header, hero and the shared trailing blocks are not touched.

Idempotent. Currently scoped to one page for review.
"""
import html as H
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE = ROOT / "site"
PHONE, PHONE_HREF, SMS_HREF = "(832) 887-8747", "tel:+18328878747", "sms:+18328878747"
BOOK = "/fixed/schedule-consult"
A1 = "/assets/66b2dae9e779df43d0d269c9"
A2 = "/assets/66b2dae9e779df43d0d269e7"

OPENER = {
    "slug": "garage-door-opener-installation",
    "intro_h": "Professional Garage Door Opener Services in Houston &amp; Surrounding Areas",
    "intro_p": [
        "A dependable garage door opener makes daily life more convenient and keeps your garage "
        "secure. Whether your opener has stopped working, is making unusual noises, or you're ready "
        "to upgrade to a smart opener, TML Garage Door Services provides expert garage door opener "
        "installation, repair, and replacement throughout Houston and the surrounding areas.",
        "Our experienced technicians service all major garage door opener brands and can quickly "
        "diagnose the problem to get your garage door operating safely and reliably.",
    ],
    "triage_h": "Common Garage Door Opener Problems",
    "triage_lede": "If your garage door opener isn't working properly, we'll identify the issue and "
                   "recommend the most cost-effective solution.",
    "triage": ["Garage door opener won't work", "Remote control not responding",
               "Wall button not working", "Door won't open or close completely",
               "Garage door reverses unexpectedly", "Flashing opener lights",
               "Loud or unusual noises", "Motor runs but the door doesn't move",
               "Intermittent operation", "Safety sensors not working",
               "Keypad won't open the door", "Wi-Fi or smart opener connectivity issues"],
    "triage_close": "Our technicians arrive with the tools and common replacement parts needed to "
                    "complete many repairs during the first visit.",
    "jobs": [
        {"h": "Garage Door Opener Repair",
         "p": "If your garage door opener isn't working properly, we'll identify the issue and "
              "recommend the most cost-effective solution.",
         "img": f"{A2}/6a6fa5ef7c6dd0cbdbbc4d52_F18562D0-6DF1-4CBC-A9C4-1513524B9391.PNG",
         "alt": "TML technician showing a homeowner what failed on their garage door opener",
         "list_h": "", "list": []},
        {"h": "Garage Door Opener Installation &amp; Replacement",
         "p": "If your opener is outdated, damaged, or beyond repair, we can install a new system "
              "that delivers smooth, quiet, and dependable performance.",
         "img": f"{A1}/6a542e2ec6b8791b21582f07_Photo%20Jul%2012%202026%2C%207%2009%2027%20PM%20(2)%20(1).png",
         "alt": "TML technician installing a new LiftMaster garage door opener",
         "list_h": "", "list": []},
    ],
    "jobs_close": "",
    # the install list is the job in order, start to finish — its own section, not a
    # column that dwarfs the one beside it
    "blocks": [
        {"kind": "steps", "tint": True, "h": "Our installation service includes:",
         "items": ["Removal of your old garage door opener", "Professional installation of a new opener",
                   "Rail and drive system installation", "Motor mounting and setup",
                   "Safety sensor installation", "Wall control installation", "Remote programming",
                   "Wireless keypad setup", "Smart phone app configuration (when available)",
                   "Complete safety testing", "Final adjustments and operation check"],
         "close": "We'll make sure your new opener is properly adjusted and ready for reliable "
                  "everyday use."},
    ],
    "specs_after_proof": [
        ("Types of Garage Door Openers We Install", "We install and replace:",
         ["Belt Drive Garage Door Openers", "Chain Drive Garage Door Openers",
          "Wall Mount (Jackshaft) Openers", "Smart Wi-Fi Garage Door Openers",
          "Battery Backup Garage Door Openers", "Quiet Garage Door Openers",
          "Heavy-Duty Garage Door Openers"],
         "Our team can help you choose the best opener based on your garage door, budget, and "
         "desired features."),
        ("Features of Modern Garage Door Openers", "Available features include:",
         ["Smartphone control from anywhere", "Wi-Fi connectivity", "Battery backup operation",
          "LED lighting", "Rolling code security technology", "Quiet belt-drive systems",
          "Motion-detecting control panels", "Automatic locking features", "Multiple remote controls",
          "Wireless keypads"],
         "We'll explain your options and help you choose the right opener for your home."),
        ("Brands We Service", "Our technicians work on most major garage door opener brands, including:",
         ["LiftMaster", "Chamberlain", "Genie", "Craftsman", "Linear", "Marantec", "Guardian", "Sommer"],
         "Not sure what brand you have? We'll identify it during the inspection."),
    ],
    "why_h": "Why Choose TML Garage Door Services?",
    "why_lede": "Homeowners trust us because we provide:",
    "why": ["Experienced local technicians", "Fast scheduling and same-day service",
            "Honest, upfront pricing", "Quality replacement parts", "Professional installation",
            "Reliable repairs", "Friendly customer service", "Satisfaction-focused workmanship"],
    "why_close": "Our goal is to keep your garage door opener operating safely, quietly, and reliably.",
    "areas_h": "Serving Houston &amp; Nearby Communities",
    "areas_lede": "We proudly provide garage door opener services throughout:",
    "areas": ["Houston", "Katy", "Cypress", "Sugar Land", "Pearland", "Tomball", "Spring",
              "Missouri City", "Richmond", "Fulshear", "The Woodlands", "Humble", "Pasadena",
              "Friendswood", "League City", "Bellaire", "Jersey Village"],
    "areas_close": "If you're in the area, contact us to schedule your service.",
    "price_tail": "for your opener",
    "cta_h": "Schedule Your Garage Door Opener Service Today",
    "cta_p": "Same-day appointments across Conroe, The Woodlands, Spring and greater Houston — "
             "and a real person answers the phone.",
}


SPRING = {
    "slug": "garage-door-spring-replacement",
    "intro_h": "Fast, Safe &amp; Professional Garage Door Spring Replacement",
    "intro_p": [
        "A broken garage door spring can leave your garage door stuck, heavy, or unsafe to operate. "
        "At TML GARAGE DOOR SERVICES, we provide fast and reliable garage door spring replacement for "
        "homeowners throughout Houston and the surrounding areas.",
        "Our experienced technicians replace broken torsion and extension springs using high-quality, "
        "long-lasting parts to restore your garage door's safe and smooth operation.",
    ],
    "triage_h": "Signs You Need Garage Door Spring Replacement",
    "triage_lede": "If you notice any of these problems, your garage door spring may need to be replaced:",
    "triage": ["Garage door won't open or only opens a few inches", "Loud bang coming from the garage",
               "Broken or separated spring", "Garage door feels unusually heavy",
               "Opener struggles or stops working", "Crooked or uneven garage door",
               "Door closes too quickly", "Visible gaps in the spring"],
    "triage_close": "Do not attempt to replace garage door springs yourself. Springs are under extreme "
                    "tension and can cause serious injury if handled improperly!",
    "price_tail": "for your door",
    "intro_img": (f"{A1}/6a543368b89f6b6fe88b1284_1F1EB104-997F-40F2-AAC8-9630A0DF66CC.PNG",
                  "TML technician adjusting a garage door torsion spring"),
    "jobs": [],
    "jobs_close": "",
    "blocks": [
        {"kind": "steps", "tint": True, "h": "Our Spring Replacement Service Includes",
         "items": ["Complete inspection of the garage door system", "Safe removal of broken springs",
                   "Installation of new high-cycle springs", "Spring balancing and tension adjustment",
                   "Cable inspection", "Roller inspection", "Track inspection", "Hinge inspection",
                   "Lubrication of moving parts", "Garage door safety test", "Opener performance check"],
         "close": "Before we leave, we make sure your garage door operates safely, quietly, and smoothly."},
    ],
    "specs_after_proof": [
        ("We Replace All Types of Garage Door Springs",
         "Our technicians service all residential garage door spring systems, including:",
         ["Torsion Springs", "Extension Springs", "Single Spring Systems", "Dual Spring Systems",
          "High-Cycle Springs"],
         "We work with all major garage door brands and models."),
    ],
    "why_h": "Why Choose Us?",
    "why_lede": "We take pride in providing dependable service and quality repairs that help extend "
                "the life of your garage door.",
    "why": ["Experienced local technicians", "Same-day service available",
            "High-quality replacement springs", "Honest, upfront pricing",
            "Fully equipped service vehicles", "Fast response times", "Professional workmanship",
            "Customer satisfaction focused"],
    "why_close": "",
    "areas_h": "Serving Houston &amp; Surrounding Areas",
    "areas_lede": "We proudly provide garage door spring replacement throughout:",
    "areas": ["Houston", "Katy", "Cypress", "Sugar Land", "Pearland", "Tomball", "Spring",
              "Missouri City", "Richmond", "Fulshear", "The Woodlands", "Humble", "Pasadena",
              "Friendswood", "League City", "Bellaire", "Jersey Village"],
    "areas_close": "If you're nearby, contact us to check service availability.",
    "cta_h": "Schedule Your Garage Door Spring Replacement Today",
    "cta_p": "If your garage door spring is broken or showing signs of wear, don't wait for the "
             "problem to get worse — a real person answers the phone.",
}

RESIDENTIAL = {
    "slug": "residential-garage-door-services",
    "intro_h": "Professional Garage Door Installation in Houston &amp; Surrounding Areas",
    "intro_p": [
        "Upgrade your home's appearance, security, and value with a professionally installed garage "
        "door. At TML GARAGE DOOR SERVICES, we provide expert garage door installation for homeowners "
        "throughout Houston and the surrounding communities.",
        "Whether you're replacing an old, damaged door or installing a brand-new garage door, our "
        "experienced technicians will help you choose the right style and ensure a safe, precise "
        "installation that lasts for years.",
    ],
    "triage_h": "Why Install a New Garage Door?",
    "triage_tone": "benefit",
    "triage_lede": "A new garage door offers more than just curb appeal. It can also provide:",
    "triage": ["Improved home security", "Increased property value",
               "Better energy efficiency with insulated doors", "Quieter, smoother operation",
               "Reduced maintenance", "Enhanced curb appeal", "Improved safety features",
               "Long-lasting durability"],
    "triage_close": "A professionally installed garage door is one of the best investments you can "
                    "make for your home.",
    "price_tail": "for your door",
    "intro_img": (f"{A1}/66b2ec2561b760fe6fee299b_549fbd18a3bc84b4e30fc12d9d7d4ccb_new-garage-door-service-install-conroe.png",
                  "Newly installed garage door on a Conroe home"),
    "jobs": [],
    "jobs_close": "",
    "blocks": [
        {"kind": "steps", "tint": True, "h": "Our Garage Door Installation Service Includes",
         "lede": "Every installation includes:",
         "items": ["Free consultation and measurements",
                   "Removal of your existing garage door (if needed)",
                   "Professional installation of your new garage door",
                   "Installation of new tracks and hardware",
                   "Spring system installation and balancing", "Roller and hinge installation",
                   "Garage door opener connection (if applicable)", "Safety sensor testing",
                   "Complete system inspection", "Final adjustments for smooth operation",
                   "Cleanup and haul-away of old materials"],
         "close": "Before we leave, we make sure your new garage door operates safely, quietly, "
                  "and reliably."},
    ],
    "blocks_after_proof": [
        {"kind": "gallery", "h": "Garage Door Styles We Install",
         "lede": "We install a wide variety of residential garage doors, including:",
         "photos": [
             ("Traditional Raised Panel Doors",
              f"{A1}/66b2ec2555069ca418a48646_garage-door-repair-and-installer.png",
              "traditional raised panel garage door installed by TML in the Conroe, TX area"),
             ("Modern Garage Doors",
              f"{A1}/66b2f63fedd0e3b2f83a04ae_555249ec745308b19d24469f04c99071_modern%20doors.png",
              "modern glass-panel garage door installed by TML in the Conroe, TX area"),
             ("Carriage House Garage Doors",
              f"{A1}/6a5d16d6089f1016a7e8321a_reserve-le-chevron-822.webp",
              "carriage house style garage doors installed by TML in the Conroe, TX area"),
         ],
         "rest": ["Contemporary Glass Garage Doors", "Flush Panel Garage Doors",
                  "Short Panel Garage Doors", "Long Panel Garage Doors", "Insulated Garage Doors",
                  "Non-Insulated Garage Doors", "Steel Garage Doors", "Aluminum Garage Doors",
                  "Wood-Look Garage Doors", "Custom Garage Doors"],
         "close": "Our team can help you choose the best option to match your home's style and your budget."},
    ],
    "specs_after_proof": [
        ("Garage Door Brands We Install",
         "We install garage doors from many leading manufacturers, including:",
         ["Amarr", "Clopay", "CHI Overhead Doors", "Wayne Dalton", "Haas Door", "Martin Door",
          "Midland Garage Door", "Northwest Door", "Windsor Door"],
         "If you already have a preferred brand, we'll help you find the right model for your home."),
    ],
    "why_h": "Why Choose TML GARAGE DOOR SERVICES?",
    "why_lede": "Homeowners trust us because we provide:",
    "why": ["Experienced installation technicians", "High-quality garage doors",
            "Honest, upfront pricing", "Professional workmanship", "Fast scheduling",
            "Reliable customer service", "Attention to detail", "Satisfaction-focused service"],
    "why_close": "We take pride in delivering garage door installations that look great and perform "
                 "reliably for years.",
    "areas_h": "Serving Houston &amp; Nearby Communities",
    "areas_lede": "We proudly install garage doors throughout:",
    "areas": ["Houston", "Katy", "Cypress", "Sugar Land", "Pearland", "Tomball", "Spring",
              "Missouri City", "Richmond", "Fulshear", "The Woodlands", "Humble", "Pasadena",
              "Friendswood", "League City", "Bellaire", "Jersey Village"],
    "areas_close": "Contact us to see if we service your area.",
    "cta_h": "Schedule Your New Garage Door Installation",
    "cta_p": "Ready to upgrade your home with a beautiful new garage door? Our team is here to help "
             "you choose the perfect door and provide expert installation from start to finish.",
}

COMMERCIAL = {
    "slug": "commercial-garage-door-installation",
    "intro_h": "Professional Commercial Garage Door Services in Houston &amp; Surrounding Areas",
    "intro_p": [
        "Your business depends on reliable access, security, and smooth daily operations. When a "
        "commercial garage door stops working properly, it can disrupt productivity, delay "
        "deliveries, and create safety concerns.",
        "At TML GARAGE DOOR SERVICES, we provide professional commercial garage door repair, "
        "installation, maintenance, and replacement services for warehouses, loading docks, "
        "distribution centers, automotive facilities, retail buildings, storage facilities, and "
        "industrial properties throughout Houston and the surrounding areas.",
        "Our experienced technicians deliver fast, dependable service to minimize downtime and keep "
        "your business running efficiently.",
    ],
    "triage_h": "Common Commercial Garage Door Problems",
    "triage_lede": "A malfunctioning commercial garage door can affect your operations and security. "
                   "Our team is equipped to diagnose and repair a wide range of commercial door "
                   "issues quickly and safely.",
    "triage": ["Broken torsion springs", "Damaged cables", "Bent or misaligned tracks", "Worn rollers",
               "Faulty door operators", "Damaged hinges", "Door off track",
               "Slow or uneven door movement", "Noisy operation", "Safety sensor issues",
               "Remote and keypad failures", "Loading dock door problems"],
    "triage_close": "We service all major commercial garage door systems and operators.",
    "price_tail": "for your facility",
    "jobs": [
        {"h": "Commercial Garage Door Repair",
         "p": "A malfunctioning commercial garage door can affect your operations and security. Our "
              "team is equipped to diagnose and repair a wide range of commercial door issues "
              "quickly and safely.",
         "img": f"{A2}/6a5433d6f361bf9f86682598_C2BB1CBF-4898-4C21-96DA-1E25A82EBDF2.PNG",
         "alt": "Commercial overhead doors at a loading dock serviced by TML",
         "list_h": "", "list": []},
        {"h": "Commercial Garage Door Installation",
         "p": "Whether you're building a new facility or replacing an aging door, we offer "
              "professional commercial garage door installation tailored to your business needs.",
         "img": f"{A1}/6a543355c034cb7d551b686f_E796B398-C84E-4B4B-8948-E05CBCB1864E.PNG",
         "alt": "TML technician at a commercial garage door installation",
         "list_h": "", "list": []},
    ],
    "jobs_close": "",
    "blocks": [
        {"kind": "steps", "tint": True, "h": "Our installation services include:",
         "items": ["Site evaluation and measurements", "Commercial door selection assistance",
                   "Professional installation", "Commercial operator installation",
                   "Safety system setup", "Track and hardware installation",
                   "Spring system installation", "Final adjustments and testing", "Safety inspection"],
         "close": "We ensure every commercial door is installed to manufacturer specifications for "
                  "long-term performance and reliability."},
    ],
    "blocks_after_proof": [
        {"kind": "checks", "tint": True, "h": "Preventive Maintenance Programs",
         "lede": "Routine maintenance helps reduce unexpected breakdowns and costly repairs. Our "
                 "commercial maintenance services include:",
         "items": ["Spring inspection", "Cable inspection", "Roller inspection", "Track inspection",
                   "Hardware tightening", "Door balancing", "Lubrication of moving parts",
                   "Safety testing", "Operator inspection", "Performance adjustments"],
         "close": "Regular maintenance can extend the life of your commercial garage door system and "
                  "improve workplace safety."},
    ],
    "specs_after_proof": [
        ("Types of Commercial Doors We Service", "We repair, replace, and install:",
         ["Sectional Commercial Garage Doors", "Rolling Steel Doors", "Roll-Up Doors",
          "Warehouse Doors", "Industrial Doors", "Loading Dock Doors", "Overhead Commercial Doors",
          "Service Doors", "Insulated Commercial Doors", "High-Speed Doors", "Fire-Rated Doors",
          "Security Grilles"],
         "Our technicians can help determine the best solution for your facility and operational "
         "requirements."),
        ("Commercial Door Operator Services", "Services include:",
         ["Commercial opener repair", "Operator replacement", "Remote programming",
          "Keypad installation", "Safety sensor repair", "Control system upgrades",
          "Preventive maintenance", "Emergency troubleshooting"],
         "We work with most major commercial operator brands and systems."),
        ("Industries We Serve", "We provide commercial garage door services for:",
         ["Warehouses", "Distribution Centers", "Manufacturing Facilities", "Auto Repair Shops",
          "Car Dealerships", "Storage Facilities", "Retail Buildings", "Office Complexes",
          "Municipal Buildings", "Restaurants", "Shopping Centers", "Property Management Companies"],
         "No matter the size of your facility, we have the expertise to keep your doors operating "
         "properly."),
    ],
    "why_h": "Why Choose TML GARAGE DOOR SERVICES?",
    "why_lede": "Businesses choose us because we provide:",
    "why": ["Experienced commercial technicians", "Fast response times", "Emergency repair service",
            "Quality replacement parts", "Professional installations", "Honest pricing",
            "Dependable workmanship", "Safety-focused service"],
    "why_close": "We understand the importance of minimizing downtime and delivering reliable "
                 "commercial door solutions.",
    "areas_h": "Serving Houston &amp; Nearby Areas",
    "areas_lede": "We proudly serve commercial customers throughout:",
    "areas": ["Houston", "Katy", "Cypress", "Sugar Land", "Pearland", "Tomball", "Spring",
              "Missouri City", "Richmond", "Fulshear", "The Woodlands", "Humble", "Pasadena",
              "Friendswood", "League City", "Bellaire", "Jersey Village"],
    "areas_close": "Contact us to discuss your commercial garage door needs.",
    "cta_h": "Schedule Commercial Garage Door Service Today",
    "cta_p": "Whether you need emergency repairs, preventive maintenance, a new installation, or a "
             "complete door replacement, TML Garage Door Services is ready to help.",
}

PAGES = [OPENER, SPRING, RESIDENTIAL, COMMERCIAL]

CSS = """<style id="tmlsv2-css">
.sv2{--g:#587735;--gd:#3f5a22;--ink:#1f2418;--mut:#535c48;--line:#dfe3d5;--cream:#f5f7ef;
 --shell:#fff;color:var(--ink);}
.sv2 *{box-sizing:border-box;}
.sv2 .sv2-wrap{width:min(100% - 40px,1060px);margin:0 auto;}
.sv2 .sv2-band{padding:clamp(40px,6vw,76px) 0;background:var(--shell);}
.sv2 .sv2-band.sv2-tint{background:var(--cream);}
.sv2 .sv2-band.sv2-tight{padding:clamp(28px,4vw,44px) 0;}
.sv2 h2{font-size:clamp(24px,3.6vw,36px);line-height:1.08;margin:0 0 14px;color:var(--ink);text-wrap:balance;}
.sv2 h3{font-size:clamp(19px,2.2vw,23px);line-height:1.15;margin:0 0 10px;color:var(--ink);}
.sv2 p{font-size:17px;line-height:1.62;color:var(--mut);margin:0 0 16px;max-width:64ch;text-wrap:pretty;}
.sv2 p:last-child{margin-bottom:0;}
.sv2 .sv2-kicker{font-size:17px;font-weight:700;color:var(--ink);margin:0 0 14px;}

/* trust strip under the hero */
.sv2 .sv2-trust{display:grid;gap:1px;background:var(--line);border-top:1px solid var(--line);
 border-bottom:1px solid var(--line);grid-template-columns:1fr;}
.sv2 .sv2-trust div{background:var(--shell);padding:16px 20px;}
.sv2 .sv2-trust b{display:block;font-size:15.5px;color:var(--ink);margin-bottom:2px;}
.sv2 .sv2-trust span{font-size:14.5px;color:var(--mut);line-height:1.45;}
@media(min-width:640px){.sv2 .sv2-trust{grid-template-columns:1fr 1fr;}}
@media(min-width:980px){.sv2 .sv2-trust{grid-template-columns:repeat(4,1fr);}}

/* symptom triage: ruled rows, not a field of boxes */
.sv2 .sv2-sym{list-style:none;margin:22px 0 24px;padding:0;display:grid;grid-template-columns:1fr;
 column-gap:36px;border-top:1px solid var(--line);}
.sv2 .sv2-sym li{display:flex;gap:12px;align-items:flex-start;padding:13px 2px;
 border-bottom:1px solid var(--line);font-size:16px;line-height:1.4;color:var(--ink);}
.sv2 .sv2-sym li::before{content:"";flex:0 0 auto;width:7px;height:7px;border-radius:50%;
 background:#b3352b;margin-top:8px;}
@media(min-width:620px){.sv2 .sv2-sym{grid-template-columns:1fr 1fr;}}
@media(min-width:940px){.sv2 .sv2-sym{grid-template-columns:repeat(3,1fr);}}

/* price: deliberately unlike anything else on the page */
.sv2 .sv2-price{border:2px dashed #9fb277;border-radius:14px;padding:clamp(20px,3vw,28px);background:var(--shell);}
.sv2 .sv2-price h2{font-size:clamp(21px,2.6vw,26px);margin-bottom:10px;}
.sv2 .sv2-price p{max-width:70ch;}

/* the two jobs */
.sv2 .sv2-jobs{display:grid;gap:clamp(26px,4vw,46px);grid-template-columns:1fr;}
@media(min-width:880px){.sv2 .sv2-jobs{grid-template-columns:1fr 1fr;}}
.sv2 .sv2-job figure{margin:0 0 18px;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#eef0e7;}
.sv2 .sv2-job picture{display:block;}
.sv2 .sv2-job img{width:100%;display:block;aspect-ratio:16/11;object-fit:cover;}
.sv2 .sv2-check{list-style:none;margin:0;padding:0;display:grid;gap:10px;}
.sv2 .sv2-check li{display:flex;gap:11px;align-items:flex-start;font-size:15.5px;line-height:1.5;color:var(--mut);}
.sv2 .sv2-check li::before{content:"✓";flex:0 0 auto;width:21px;height:21px;border-radius:50%;
 background:var(--g);color:#fff;font-size:12px;font-weight:800;display:grid;place-items:center;}

/* the install sequence: numbered, ruled, three columns of readable width */
.sv2 .sv2-steps{list-style:none;margin:26px 0 0;padding:0;display:grid;grid-template-columns:1fr;
 column-gap:38px;counter-reset:step;border-bottom:1px solid var(--line);}
.sv2 .sv2-steps li{counter-increment:step;display:flex;gap:14px;align-items:baseline;
 padding:14px 2px;border-top:1px solid var(--line);font-size:15.5px;line-height:1.45;color:var(--ink);}
.sv2 .sv2-steps li::before{content:counter(step);flex:0 0 auto;min-width:20px;
 font-size:13px;font-weight:800;color:var(--g);font-variant-numeric:tabular-nums;}
@media(min-width:620px){.sv2 .sv2-steps{grid-template-columns:1fr 1fr;}}
@media(min-width:940px){.sv2 .sv2-steps{grid-template-columns:repeat(3,1fr);}}

/* intro with its lead photo alongside */
.sv2 .sv2-intro{display:grid;gap:clamp(22px,3.5vw,40px);grid-template-columns:1fr;align-items:center;}
.sv2 .sv2-intro figure{margin:0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#eef0e7;}
.sv2 .sv2-intro picture{display:block;}
.sv2 .sv2-intro img{width:100%;display:block;aspect-ratio:16/11;object-fit:cover;}
@media(min-width:880px){.sv2 .sv2-intro{grid-template-columns:1.05fr .95fr;}}

/* benefit variant of the triage grid: same rhythm, positive marker */
.sv2 .sv2-sym-good li::before{background:var(--g);width:8px;height:8px;}
/* a wide check list that is its own section rather than a column */
.sv2 .sv2-check-wide{margin-top:24px;grid-template-columns:1fr;}
@media(min-width:620px){.sv2 .sv2-check-wide{grid-template-columns:1fr 1fr;column-gap:34px;}}
@media(min-width:940px){.sv2 .sv2-check-wide{grid-template-columns:repeat(3,1fr);}}
/* a single spec group reads better across the full column */
.sv2 .sv2-specs-one{grid-template-columns:1fr!important;}
.sv2 .sv2-specs-one p{max-width:64ch;}
/* one service instead of two: photo beside the text, not a half-width card */
@media(min-width:880px){
 .sv2 .sv2-jobs-solo{grid-template-columns:1fr 1fr;align-items:center;}
 .sv2 .sv2-jobs-solo .sv2-job{display:contents;}
 .sv2 .sv2-jobs-solo .sv2-job figure{margin:0;}
}
/* door-style gallery */
.sv2 .sv2-gal{display:grid;gap:14px;margin-top:22px;
 grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));}
.sv2 .sv2-shot{margin:0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#fff;}
.sv2 .sv2-shot picture{display:block;}
.sv2 .sv2-shot img{width:100%;display:block;aspect-ratio:4/3;object-fit:cover;}
.sv2 .sv2-shot figcaption{padding:12px 15px;font-weight:600;color:var(--ink);font-size:14.5px;line-height:1.35;}

/* specs: three plain groups, chips not cards */
.sv2 .sv2-specs{display:grid;gap:clamp(26px,4vw,40px);grid-template-columns:1fr;}
@media(min-width:820px){.sv2 .sv2-specs{grid-template-columns:repeat(3,1fr);align-items:start;}}
.sv2 .sv2-chips{list-style:none;margin:0 0 14px;padding:0;display:flex;flex-wrap:wrap;gap:8px;}
.sv2 .sv2-chips li{padding:8px 14px;border:1px solid var(--line);border-radius:999px;background:var(--shell);
 font-size:14.5px;font-weight:600;color:var(--ink);}
.sv2 .sv2-band.sv2-tint .sv2-chips li{background:var(--shell);}

/* why us */
.sv2 .sv2-dark{background:var(--ink);color:#fff;border-radius:18px;padding:clamp(24px,4.2vw,44px);}
.sv2 .sv2-dark h2{color:#fff;}
.sv2 .sv2-dark p{color:#c9d0bd;}
.sv2 .sv2-dark .sv2-kicker{color:#fff;}
.sv2 .sv2-dark .sv2-check{grid-template-columns:1fr;}
.sv2 .sv2-dark .sv2-check li{color:#dfe4d6;}
.sv2 .sv2-dark .sv2-check li::before{background:#cfe84d;color:#1f2418;}
@media(min-width:760px){.sv2 .sv2-dark .sv2-check{grid-template-columns:1fr 1fr;column-gap:30px;}}

/* areas */
.sv2 .sv2-areas{list-style:none;margin:0 0 16px;padding:0;display:flex;flex-wrap:wrap;gap:8px;}
.sv2 .sv2-areas li{padding:9px 15px;border:1px solid var(--line);border-radius:999px;background:var(--shell);
 font-size:14.5px;font-weight:600;color:var(--ink);}

/* closing CTA */
.sv2 .sv2-cta{background:var(--g);border-radius:18px;color:#fff;padding:clamp(24px,4.2vw,44px);}
.sv2 .sv2-cta h2{color:#fff;margin-bottom:8px;}
.sv2 .sv2-cta p{color:#eaf1de;max-width:56ch;margin-bottom:20px;}
.sv2 .sv2-acts{display:flex;flex-wrap:wrap;gap:11px;}
.sv2 .sv2-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:54px;
 padding:0 22px;border-radius:11px;font-weight:800;font-size:16.5px;text-decoration:none;
 white-space:nowrap;flex:0 0 auto;
 transition:background .14s ease,color .14s ease,border-color .14s ease;}
.sv2 .sv2-btn.sv2-p{background:#fff;color:var(--ink);}
.sv2 .sv2-btn.sv2-p:hover{background:var(--ink);color:#fff;}
.sv2 .sv2-btn.sv2-s{background:transparent;color:#fff;border:2px solid rgba(255,255,255,.62);}
.sv2 .sv2-btn.sv2-s:hover{background:#fff;color:var(--ink);border-color:#fff;}
.sv2 .sv2-btn.sv2-ink{background:var(--ink);color:#fff;}
.sv2 .sv2-btn.sv2-ink:hover{background:var(--gd);}
.sv2 .sv2-btn.sv2-outline{background:var(--shell);color:var(--ink);border:2px solid var(--ink);}
.sv2 .sv2-btn.sv2-outline:hover{background:var(--ink);color:#fff;}

/* related services */
.sv2 .sv2-rel{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));}
.sv2 .sv2-rel a{display:block;padding:15px 17px;border:1px solid var(--line);border-radius:12px;
 background:var(--shell);color:var(--ink);text-decoration:none;font-weight:600;font-size:15.5px;
 transition:border-color .14s ease,color .14s ease;}
.sv2 .sv2-rel a:hover{border-color:var(--g);color:var(--gd);}

.sv2 .sv2-rule{border:0;border-top:1px solid var(--line);margin:0;}
</style>"""

RELATED = [
    ("residential-garage-door-services", "New Garage Door Installation"),
    ("garage-door-spring-replacement", "Garage Door Spring Replacement"),
    ("garage-door-opener-installation", "Garage Door Opener Repair &amp; Installation"),
    ("commercial-garage-door-installation", "Commercial Garage Doors"),
]

WIDTHS = (500, 800, 1080)


def picture(url, alt, sizes, eager=False):
    cands = []
    for w in WIDTHS:
        d = url.rsplit(".", 1)[0] + f"-w{w}.webp"
        import urllib.parse
        if (SITE / urllib.parse.unquote(d).lstrip("/")).exists():
            cands.append(f"{d} {w}w")
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    img = f'<img src="{url}" alt="{alt}" {load} decoding="async">'
    if not cands:
        return img
    return ('<picture><source type="image/webp" srcset="' + ", ".join(cands)
            + f'" sizes="{sizes}">' + img + "</picture>")


def band(inner, tint=False, tight=False):
    """Recorded, not rendered — emit() decides the final tint so two tinted
    bands never sit against each other and read as one long block."""
    return {"inner": inner, "tint": tint, "tight": tight}


def emit(bands):
    html, prev = [], False
    for b in bands:
        tint = b["tint"] and not prev
        prev = tint
        cls = "sv2-band" + (" sv2-tint" if tint else "") + (" sv2-tight" if b["tight"] else "")
        html.append(f'<div class="{cls}"><div class="sv2-wrap">{b["inner"]}</div></div>')
    return "".join(html)


def acts(dark=True):
    a, b = ("sv2-btn sv2-p", "sv2-btn sv2-s") if dark else ("sv2-btn sv2-ink", "sv2-btn sv2-outline")
    return ('<div class="sv2-acts">'
            f'<a class="{a}" href="{PHONE_HREF}" data-book="call">&#9742; Call {PHONE}</a>'
            f'<a class="{b}" href="{SMS_HREF}" data-book="text">&#128172; Text us</a>'
            f'<a class="{b}" href="{BOOK}" data-book="service-cta">Book online</a>'
            "</div>")


def keep(html, cls):
    """Pull an already-rendered component (reviews, FAQ) out of the old body."""
    m = re.search(r'<div class="%s"[^>]*>' % re.escape(cls), html)
    if not m:
        return ""
    depth = 1
    for t in re.finditer(r"<div\b|</div>", html[m.end():]):
        depth += 1 if t.group(0) == "<div" else -1
        if depth == 0:
            return html[m.start():m.end() + t.end()]
    return ""


def steps_block(b):
    return (f'<h2>{H.escape(b["h"])}</h2>'
            + (f'<p>{H.escape(b["lede"])}</p>' if b.get("lede") else "")
            + '<ol class="sv2-steps">' + "".join(f"<li>{H.escape(x)}</li>" for x in b["items"]) + "</ol>"
            + (f'<p style="margin-top:24px">{H.escape(b["close"])}</p>' if b.get("close") else ""))


def checks_block(b):
    return (f'<h2>{H.escape(b["h"])}</h2>'
            + (f'<p>{H.escape(b["lede"])}</p>' if b.get("lede") else "")
            + '<ul class="sv2-check sv2-check-wide">'
            + "".join(f"<li>{H.escape(x)}</li>" for x in b["items"]) + "</ul>"
            + (f'<p style="margin-top:22px">{H.escape(b["close"])}</p>' if b.get("close") else ""))


def specs_block(b):
    groups = b["groups"]
    inner = "".join(
        f'<div><h3>{H.escape(h)}</h3>'
        + (f'<p>{H.escape(lede)}</p>' if lede else "")
        + '<ul class="sv2-chips">' + "".join(f"<li>{H.escape(x)}</li>" for x in items) + "</ul>"
        + (f'<p>{H.escape(close)}</p>' if close else "") + "</div>"
        for h, lede, items, close in groups)
    # one group reads better full width than stranded in a third of the row
    cls = "sv2-specs" if len(groups) > 1 else "sv2-specs sv2-specs-one"
    return f'<div class="{cls}">{inner}</div>'


def gallery_block(b):
    shots = "".join(
        '<figure class="sv2-shot">'
        + picture(img, H.escape(alt), "(min-width:820px) 32vw, 92vw")
        + f'<figcaption>{H.escape(label)}</figcaption></figure>'
        for label, img, alt in b["photos"])
    rest = ('<ul class="sv2-chips" style="margin-top:16px">'
            + "".join(f"<li>{H.escape(x)}</li>" for x in b["rest"]) + "</ul>") if b.get("rest") else ""
    return (f'<h2>{H.escape(b["h"])}</h2>'
            + (f'<p>{H.escape(b["lede"])}</p>' if b.get("lede") else "")
            + f'<div class="sv2-gal">{shots}</div>{rest}'
            + (f'<p style="margin-top:18px">{H.escape(b["close"])}</p>' if b.get("close") else ""))


RENDER = {"steps": steps_block, "checks": checks_block, "specs": specs_block, "gallery": gallery_block}


def build(p, reviews, faq):
    out = []

    # 1. trust strip + intro
    out.append(band(
        '<div class="sv2-trust">'
        "<div><b>The price before the work</b><span>Upfront pricing with no hidden fees.</span></div>"
        "<div><b>Same-day &amp; emergency</b><span>No extra charge for weekends.</span></div>"
        "<div><b>Insured technicians</b><span>Well-trained, and they work for TML.</span></div>"
        "<div><b>100% satisfaction guaranteed</b><span>We're not done until the door works right.</span></div>"
        "</div>", tight=True))

    intro_txt = (f'<h2>{p["intro_h"]}</h2>'
                 + "".join(f"<p>{H.escape(x)}</p>" for x in p["intro_p"]))
    if p.get("intro_img"):
        out.append(band(
            '<div class="sv2-intro"><div>' + intro_txt + '</div><figure>'
            + picture(p["intro_img"][0], H.escape(p["intro_img"][1]),
                      "(min-width:880px) 46vw, 92vw", eager=True)
            + "</figure></div>"))
    else:
        out.append(band(intro_txt))

    # 2. triage — their symptom, first
    tone = p.get("triage_tone", "problem")
    ul = "sv2-sym" if tone == "problem" else "sv2-sym sv2-sym-good"
    out.append(band(
        f'<h2>{H.escape(p["triage_h"])}</h2>'
        + (f'<p>{H.escape(p["triage_lede"])}</p>' if p.get("triage_lede") else "")
        + f'<ul class="{ul}">' + "".join(f"<li>{H.escape(x)}</li>" for x in p["triage"]) + "</ul>"
        + (f'<p>{H.escape(p["triage_close"])}</p>' if p.get("triage_close") else "")
        + acts(dark=False), tint=True))

    # 3. price, before any selling
    out.append(band(
        '<div class="sv2-price"><h2>What will it cost?</h2>'
        "<p>Your technician diagnoses the problem on site and gives you the full price before any "
        f'work begins — fair, upfront pricing with no hidden fees. Call <a href="{PHONE_HREF}">{PHONE}</a> '
        "and we can talk through the likely range " + p.get("price_tail", "for the job") + " before we come out.</p></div>",
        tight=True))

    # 4. the two jobs
    jobs = []
    for i, j in enumerate(p["jobs"]):
        lst = ('<p class="sv2-kicker">' + H.escape(j["list_h"]) + "</p>"
               '<ul class="sv2-check">' + "".join(f"<li>{H.escape(x)}</li>" for x in j["list"]) + "</ul>"
               ) if j["list"] else ""
        jobs.append('<div class="sv2-job"><figure>'
                    + picture(j["img"], H.escape(j["alt"]),
                              "(min-width:880px) 46vw, 92vw", eager=(i == 0))
                    + f'</figure><h3>{j["h"]}</h3><p>{H.escape(j["p"])}</p>{lst}</div>')
    close = (f'<p style="margin-top:26px">{H.escape(p["jobs_close"])}</p>'
             if p.get("jobs_close") else "")
    if jobs:
        jobs_cls = "sv2-jobs" if len(jobs) > 1 else "sv2-jobs sv2-jobs-solo"
        out.append(band(f'<div class="{jobs_cls}">' + "".join(jobs) + "</div>" + close))

    for b in p.get("blocks", []):
        out.append(band(RENDER[b["kind"]](b), tint=b.get("tint", False)))

    # 5. proof
    if reviews:
        out.append(band(reviews, tint=True))

    # 6. specs for the researcher, below the proof
    # narrative order: what it looks like, then who makes it
    for b in p.get("blocks_after_proof", []):
        out.append(band(RENDER[b["kind"]](b), tint=b.get("tint", False)))
    if p.get("specs_after_proof"):
        out.append(band(specs_block({"groups": p["specs_after_proof"]})))

    # 7. why us, in the client's own words
    out.append(band(
        f'<div class="sv2-dark"><h2>{H.escape(p["why_h"])}</h2>'
        f'<p class="sv2-kicker">{H.escape(p["why_lede"])}</p>'
        '<ul class="sv2-check">' + "".join(f"<li>{H.escape(x)}</li>" for x in p["why"]) + "</ul>"
        f'<p style="margin-top:18px">{H.escape(p["why_close"])}</p></div>', tight=True))

    # 8. FAQ
    if faq:
        out.append(band(faq, tint=True))

    # 9. where we work
    out.append(band(
        f'<h2>{p["areas_h"]}</h2><p>{H.escape(p["areas_lede"])}</p>'
        '<ul class="sv2-areas">' + "".join(f"<li>{H.escape(x)}</li>" for x in p["areas"]) + "</ul>"
        f'<p>{H.escape(p["areas_close"])}</p>', tight=True))

    # 10. one clear way to act
    out.append(band(f'<div class="sv2-cta"><h2>{H.escape(p["cta_h"])}</h2>'
                    f'<p>{H.escape(p["cta_p"])}</p>' + acts(dark=True) + "</div>", tight=True))

    # 11. related services
    others = [(sl, nm) for sl, nm in RELATED if sl != p["slug"]]
    out.append(band(
        '<h3 style="margin-bottom:14px">Other services</h3><div class="sv2-rel">'
        + "".join(f'<a href="/fixed/our-services/{sl}">{nm}</a>' for sl, nm in others)
        + "</div>", tight=True))

    return '<div class="sv2">' + emit(out) + "</div>"


def rebuild(spec):
    page = SITE / "fixed" / "our-services" / spec["slug"] / "index.html"
    html = page.read_text("utf-8", errors="replace")

    # strip the previous run's stylesheet FIRST: it lives in <head>, so removing it
    # after computing offsets would shift every index below it
    html = re.sub(r'<style id="tmlsv2-css">.*?</style>', "", html, flags=re.S)

    reviews = keep(html, "tmlrev")
    faq = keep(html, "tmlfaq")

    m = re.search(r'<section class="section-3"[^>]*>', html)
    if not m:
        print(f"  {spec['slug']}: section-3 not found — skipped")
        return
    depth, end = 1, None
    for t in re.finditer(r"<section\b|</section>", html[m.end():]):
        depth += 1 if t.group(0) == "<section" else -1
        if depth == 0:
            end = m.end() + t.start()
            break
    if end is None:
        print(f"  {spec['slug']}: could not find the end of section-3 — skipped")
        return

    body = build(spec, reviews, faq)
    html = html[:m.end()] + body + html[end:]
    html = html.replace("</head>", CSS + "</head>", 1)
    page.write_text(html, "utf-8")
    print(f"  {spec['slug']}: rebuilt (reviews {'kept' if reviews else 'MISSING'}, "
          f"faq {'kept' if faq else 'MISSING'})")


def main():
    for spec in PAGES:
        rebuild(spec)


if __name__ == "__main__":
    main()
