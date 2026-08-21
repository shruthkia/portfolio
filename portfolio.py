"""
Lorris-inspired portfolio — derived from:
https://outstanding-strengthening-284213.framer.app/

Run:  pip install flask && python portfolio.py
Open: http://127.0.0.1:5000

Blog compose password: set COMPOSE_PASSWORD env var (default: kia-compose-2026)
Messages saved to: messages.json
"""

from __future__ import annotations

import json
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from flask import Flask, has_request_context, jsonify, redirect, request, session, url_for
from jinja2 import DictLoader, Environment, select_autoescape
from markupsafe import Markup, escape

BASE_DIR = Path(__file__).resolve().parent
STATIC_PROJECTS = "/static/projects"
BLOGS_FILE = BASE_DIR / "blogs.json"
MESSAGES_FILE = BASE_DIR / "messages.json"
COMPOSE_PASSWORD = os.environ.get("COMPOSE_PASSWORD", "kia-compose-2026")

app = Flask(
    __name__,
    static_folder=str(BASE_DIR / "static"),
    static_url_path="/static",
)
app.secret_key = os.environ.get("PORTFOLIO_SECRET", secrets.token_hex(32))

CONTENT = {
    "meta": {
        "name": "Shruthika Omkumar",
        "first_name": "Shruthika",
        "last_name": "Omkumar",
        "title": "entrepreneur & builder",
        "title_italic": "experimenter",
        "tagline": "build cuz u care",
        "version": "v.01",
        "year": "2026",
        "email": "shruthikaomkumar@gmail.com",
        "school_email": "shruthika.omkumar.246@k12.friscoisd.org",
        "copyright": "©2026 | Shruthika Omkumar",
    },
    "quote": {
        "text": "A ship in harbor is safe, but that is not what ships are built for.",
        "attr": "John A. Shedd",
    },
    "hero": {
        "portrait": "/static/hero.jpg",
        "scrolling_words": ["KIA", "BUILDER"],
        "intro": (
            "I do a little bit of everything, designing, writing, organizing chaos, "
            "maybe oversharing on LinkedIn. Currently figuring out the crossroads between "
            "<em>creative stuff and nerdy stuff</em> (think: 3D modeling + poetry + tech + "
            "med + design + business + research??). I've flopped, learned, and somehow "
            "ended up here, still curious, still experimenting."
        ),
        "cta_work": "MORE WORK",
        "cta_about": "MORE ABOUT ME",
    },
    "ticker": [
        "welcome",
        "portfolio",
        "build cuz u care",
        "entrepreneur & builder",
    ],
    "nav": [
        {"label": "ABOUT", "href": "/about"},
        {"label": "WORK", "href": "/work"},
        {"label": "ISM", "href": "/ism"},
        {"label": "BRAIN", "href": "/brain"},
        {"label": "BLOG", "href": "/blog"},
        {"label": "WRITING", "href": "/writing"},
        {"label": "CONTACT", "href": "/contact"},
    ],
    "social": [
        {"label": "LINKEDIN", "href": "https://www.linkedin.com/in/shruthika-o/"},
        {"label": "GITHUB", "href": "https://github.com/shruthkia"},
        {"label": "DISCORD ryu_kiara", "href": "https://discord.com/channels/users/1233690977105870861"},
    ],
    "about": {
        "portrait": "/static/about.jpg",
        "location": "Plano, Texas",
        "intro": (
            "Founder @ <em>Adopurr</em> ฅ^>⩊<^ ฅ. I do a little bit of everything: designing, "
            "writing, organizing chaos, maybe oversharing on LinkedIn. Currently at the "
            "crossroads of <em>creative stuff and nerdy stuff</em> (3D modeling + poetry + "
            "digital ops??). I've interned, led, flopped, learned, and somehow ended up here, "
            "still curious, still experimenting."
        ),
        "skills": [
            "Entrepreneurship",
            "Team Coordination",
            "Presentation Skills",
            "Graphic Design",
            "3D Modeling",
            "Marketing & Branding",
            "Fundraising",
            "Research",
            "Digital Ops",
            "HR & Recruiting",
        ],
        "languages": [
            "English (Full Professional)",
            "Tamil (Native)",
            "French (Elementary)",
        ],
        "awards": [
            "FCCLA National Champion & Gold Medalist, School to Career Challenge Test Level 2 (NATS, Washington D.C.)",
            "FCCLA Silver Medal Finalist, Sustainability Challenge Level 2 (NATS)",
            "Featured in Frisco Enterprise / Star Local Media for FCCLA nationals medals",
            "UNA USA Ambassador 2025-26, United Nations Association USA",
            "Scouted by 1507 Funds, Danielle Strachman",
            "FCCLA Sustainability Challenge, State 3rd Place & National Qualifier",
            "FCSA Gold Medal, FCCLA State Leadership Conference",
            "FCCLA Regional Champion, State 3rd & National Qualifier, Sustainability",
            "FCCLA VP of Competitive Events, Power of One Leadership Awardee",
            "DECA Regional Competitor 2025-26",
            "S4CA Best Young Architect Award, 3x Contractor Award 2024-25",
            "SPOT VSSF Top 100 Young Scientists, India (x2)",
            "International 3D Design, SelfCAD Winner 2023-24",
            "Semi-Finalist Achievement in Distinction, Straight A's in all topics — SpellBee International",
            "Bronze Winner, Intl. Level (Zonal Rank 6, Intl. Rank 60) Science Olympiad",
        ],
        "experience": [
            {"role": "Founder", "company": "Adopurr", "detail": "making all nine lives of a cat matter :D", "year": "Jul 2025 to Present"},
            {"role": "Scouted Founder", "company": "1507 Funds", "detail": "Danielle Strachman", "year": "2025"},
            {"role": "Co-Founder & Head of Growth", "company": "Arkire", "detail": "Ontario, Canada", "year": "Feb 2025 to Sep 2025"},
            {"role": "Human Resources Director", "company": "DreamyUni", "detail": "Brooklyn, NY", "year": "Jul 2025 to Present", "group": "DreamyUni"},
            {"role": "Marketing Intern", "company": "DreamyUni", "detail": "Brooklyn, NY", "year": "Oct 2024 to Jun 2025", "group": "DreamyUni"},
            {"role": "UNA USA Ambassador", "company": "United Nations Association USA", "detail": "Innerview profile", "year": "2025-26", "link": "https://innerview.org/shruthikaomkumar2"},
            {"role": "VP of Competitive Events & Chapter Web Builder", "company": "Lebanon Trail FCCLA", "detail": "built lt-fccla.vercel.app", "year": "2025-26", "link": "https://lt-fccla.vercel.app/"},
            {"role": "Graphic Lead", "company": "LaunchPoint", "detail": "22k+ IG followers, visual strategy & growth", "year": "Jun 2026 to Present"},
            {"role": "Director of Fundraising", "company": "Horizon Labs", "year": "Mar 2025 to Present"},
            {"role": "Director of Fundraising", "company": "The Metastatic Cancer Initiative", "detail": "Texas", "year": "Dec 2024 to Present"},
            {"role": "Regional Rep & Chapter President", "company": "Girls in Research Global", "detail": "Washington", "year": "Oct 2024 to Present"},
            {"role": "Head of Operations", "company": "Visionary", "year": "Jan 2025 to Present"},
            {"role": "Operations Manager", "company": "Badavas", "detail": "NYC Metro", "year": "Jan 2025 to Aug 2025"},
            {"role": "Ambassador, Intl. Competition Winner", "company": "SelfCAD", "detail": "3D modeling tutorials & community", "year": "Feb 2023 to Jun 2025"},
            {"role": "Intern", "company": "RoundPier", "detail": "NYC Metro", "year": "Nov 2024 to Aug 2025"},
            {"role": "Internship Trainee", "company": "ISRO", "detail": "U R Rao Satellite Centre (URSC), Bengaluru", "year": "Jun 2024", "group": "ISRO"},
            {"role": "Internship Trainee", "company": "ISRO", "detail": "Vikram Sarabhai Space Centre (VSSC), Thiruvananthapuram", "year": "Mar 2023", "group": "ISRO"},
            {"role": "School Internship Programme Lead", "company": "Scholastic India", "detail": "book fair lead, team of 10", "year": "Nov 2023 to Jan 2024"},
        ],
        "education": [
            {"degree": "High School Diploma", "school": "Lebanon Trail High School", "year": "Aug 2025 to May 2028"},
            {"degree": "High School", "school": "Milpitas High School", "year": "Jan 2025 to Jun 2025"},
            {"degree": "", "school": "Mahatma Global Gateway", "year": "Jun 2016 to Jan 2025"},
            {"degree": "JuniorMBA, Entrepreneurship", "school": "Clever Harvey", "detail": "Certified by IIT Roorkee", "year": "May 2024", "group": "Clever Harvey"},
            {"degree": "JuniorMBA, Advertising", "school": "Clever Harvey", "year": "", "group": "Clever Harvey"},
            {"degree": "JuniorMBA, Design and Branding", "school": "Clever Harvey", "year": "", "group": "Clever Harvey"},
        ],
        "certifications": [
            {"name": "Canva Essentials", "issuer": "Canva", "date": "Oct 2024", "credential_id": "0e2c89"},
            {"name": "Graphic Design Essentials", "issuer": "Canva", "date": "Oct 2024", "credential_id": "8415e2"},
            {"name": "Fundamentals of Digital Marketing", "issuer": "Google", "date": "Oct 2024", "credential_id": "331005004"},
        ],
    },
    "ism": {
        "program": "Frisco ISD Independent Study & Mentorship",
        "mission": (
            "The mission of Frisco ISD’s Independent Study and Mentorship (ISM) program is to "
            "give advanced academic students a self-directed, in-depth study of a topic they "
            "choose, with real-world experience under a community mentor. The program is built "
            "so students can explore future career interests, develop a professional product, "
            "and serve their community."
        ),
        "what_we_do": [
            "Juniors and seniors apply and are selected for a rigorous, weighted elective.",
            "We pick a topic, interview professionals, and choose a mentor to work with.",
            "Fall is research-heavy: secondary sources, interviews, a mission statement, and a portfolio.",
            "Later we build an original product with our mentor and present the work.",
            "Along the way: professionalism, networking, public speaking, and actually showing up for people.",
        ],
        "topic_title": "My research topic",
        "topic": (
            "Examining how domesticated animals’ behaviour or characteristics change based on "
            "re-sheltering, and how that affects their future adoption processes."
        ),
        "personal_title": "Personal mission",
        "personal": "To be able to serve and advocate for those who cannot for themselves.",
    },
    "brain": {
        "kicker": "A digitized collection of things and core memories that live rent-free in my mind.",
        "intro": (
            "Hey! I do things. A lot of them. Usually on purpose, sometimes by accident. "
            "I like trying new stuff, meeting people, and pretending I’m chill about it. "
            "This site is a soft archive and a hard launch (depending on the day)."
        ),
        "hustles_note": "Technically not “side hustles” but they do take up side-hustle amounts of brain space.",
        "hustles": [
            {"img": "/static/brain/cat.png", "alt": "stretching black cat sticker", "text": "Random projects that started as purely “for fun”"},
            {"img": "/static/brain/cd.png", "alt": "holographic CD sticker", "text": "Helping people make things look and feel better"},
            {"img": "/static/brain/polaroid.jpg", "alt": "polaroid of a quiet street", "text": "Saying yes, then learning how to do the thing"},
        ],
        "fixations_note": "Current obsessions that overstimulate me in a good way",
        "fixations": [
            "Curating my life like it’s a playlist",
            "Internet trends I notice before they’re annoying",
            "Being “low-maintenance” but highly organized",
            "Activities that make me forget to check my phone",
        ],
        "dumps": [
            {"label": "right now", "text": "ISM research, Adopurr, FCCLA chapter stuff, and trying not to treat my notes app like a landfill."},
            {"label": "on loop", "text": "cats, 3D models, poetry lines I refuse to finish, and whatever song has me in a chokehold this week."},
            {"label": "working theory", "text": "showing up for animals (and people) is the whole point. the rest is just formatting."},
        ],
    },
    "more_of_me": {
        "title": "a lil bit more of",
        "title_em": "me",
        "intro": "the random bits that don't really fit anywhere else but still very me",
        "bits": [
            {"ascii": "(ノ◕ヮ◕)ノ*:･ﾟ✧", "label": "hiphop aerobics", "detail": "certified, Mar 2017"},
            {"ascii": "✧･ﾟ: *✧･ﾟ:*", "label": "vocabulary & language dev", "detail": "SpellBee International, Jun 2023"},
            {"ascii": "(˶ᵔ ᵕ ᵔ˶)", "label": "tamil", "detail": "native speaker"},
            {"ascii": "bon·jour~", "label": "french", "detail": "elementary, work in progress"},
            {"ascii": "~ * ❀ * ~", "label": "3D models + poetry", "detail": "yes, in the same brain"},
            {"ascii": "@_@/", "label": "linkedin oversharer", "detail": "maybe too much, no regrets"},
            {"ascii": "ฅ^>⩊<^ ฅ", "label": "cat person", "detail": "founder @ Adopurr"},
            {"ascii": "hehe ←", "label": "self proclaimed funny", "detail": "certified by me, disputed by no one"},
            {"ascii": "? ➜ !", "label": "still experimenting", "detail": "flopped, learned, repeat"},
        ],
        "ascii_cats": [
            r"""                            ╱|、
                          (˚ˎ 。7
                           |、˜〵
                          じしˍ,)ノ              /| _ ╱|、
             ( •̀ㅅ •́  )
       ＿ノ ヽ ノ＼＿
    /　`/ ⌒Ｙ⌒ Ｙ　 \
 ( 　(三ヽ人　 /　 　|
   |　ﾉ⌒＼ ￣￣ヽ　 ノ
ヽ＿＿＿＞､＿＿／
          ｜( 王 ﾉ〈
           /ﾐ`ー―彡\
          |╰          ╯|
          |       /\       |
          |      /  \      |
          |    /     \     |""",
            r"""  ∧,,,∧
(  ̳• · • ̳)
   /    づ♡""",
            r"""                へ  ♡
         ૮  >  <)
          /  ⁻  ៸|
     乀(ˍ, ل ل""",
        ],
    },
    "projects": [
        {
            "slug": "adopurr",
            "title": "Adopurr",
            "category": "founder / social impact",
            "image": f"{STATIC_PROJECTS}/adopurr.png",
            "href": "#",
            "story": (
                "Adopurr is my baby: a project about making all nine lives of a cat matter. "
                "I started it because shelter animals don’t get a second chance unless someone "
                "actually builds the systems, stories, and stubbornness around them.\n\n"
                "I’m the founder, which in practice means design, ops, storytelling, and "
                "reminding people that “cute” is not a care plan. The through-line is the same "
                "as my ISM work — advocate for those who cannot advocate for themselves, and "
                "make adoption feel possible instead of like a maze."
            ),
        },
        {
            "slug": "arkire",
            "title": "Arkire",
            "category": "co-founder / growth",
            "image": f"{STATIC_PROJECTS}/arkire.jpg",
            "href": "#",
            "story": (
                "Arkire was a co-founder chapter: Ontario-based, growth-shaped, and very "
                "much a “say yes then figure out the funnel” era. I led growth — positioning, "
                "outreach, and the unglamorous work of turning interest into actual users.\n\n"
                "It taught me how fast a product story can fall apart if you don’t talk to "
                "people, and how much of “head of growth” is just listening, iterating, and "
                "refusing to make the brand sound like a press release."
            ),
        },
        {
            "slug": "lt-fccla",
            "title": "Lebanon Trail FCCLA",
            "category": "chapter website / design + build",
            "image": f"{STATIC_PROJECTS}/lt-fccla.png",
            "href": "https://lt-fccla.vercel.app/",
            "story": (
                "As VP of Competitive Events and chapter web builder, I designed and shipped "
                "the Lebanon Trail FCCLA site so members could actually find competitions, "
                "deadlines, and chapter life without digging through a group chat archaeology dig.\n\n"
                "It’s live at lt-fccla.vercel.app — part brand, part utility. I wanted it to "
                "feel like us: organized enough to be useful, still a little extra."
            ),
        },
        {
            "slug": "launchpoint",
            "title": "LaunchPoint",
            "category": "graphic design / 22k+ IG",
            "image": f"{STATIC_PROJECTS}/launchpoint.png",
            "href": "#",
            "story": (
                "At LaunchPoint I came in as graphic lead for a page sitting at 22k+ on "
                "Instagram. The job was visual strategy: make the feed look like it knows "
                "what it’s doing, then keep it growing without turning into beige startup soup.\n\n"
                "I handled graphics, visual direction, and the “does this still feel like us?” "
                "gut check. Design here is not decoration — it’s how people decide to stay."
            ),
        },
        {
            "slug": "fccla-nats",
            "title": "FCCLA Nationals",
            "category": "national champion + silver medal",
            "image": f"{STATIC_PROJECTS}/fccla-sustainability.jpg",
            "href": "https://starlocalmedia.com/friscoenterprise/news/frisco-isd-students-earn-medals-at-fccla-nationals/article_54aa6c9e-50a1-47a8-b710-5dcd8dca20c9.html",
            "story": (
                "At the FCCLA National Leadership Conference (NATS) in Washington, D.C., "
                "I was named National Champion and Gold Medalist in the School to Career "
                "Challenge Test Level 2, and earned a Silver Medal Finalist honor in the "
                "Sustainability Challenge Level 2.\n\n"
                "Frisco Enterprise / Star Local Media covered the medals for Frisco ISD. "
                "The short version: I studied like it mattered, showed up, and it did."
            ),
        },
        {
            "slug": "fccla-sustainability",
            "title": "Sustainability Challenge",
            "category": "FCCLA / state 3rd → NATS silver",
            "image": f"{STATIC_PROJECTS}/fccla-sustainability.jpg",
            "href": "https://www.friscoisd.org/article/3004120",
            "story": (
                "The Sustainability Challenge was the long haul: regional champion, state 3rd "
                "and national qualifier, then a silver medal finalist finish at NATS. It’s the "
                "project that taught me research is not a vibe — it’s receipts, systems, and "
                "being able to defend your recommendations out loud.\n\n"
                "I still care about the unsexy version of sustainability: what actually changes "
                "when a school, a family, or a shelter has to live with the plan."
            ),
        },
        {
            "slug": "selfcad-champ",
            "title": "SelfCAD Champ",
            "category": "3D modeling / 1st prize · Candyland w/ Sachin (7B)",
            "image": f"{STATIC_PROJECTS}/selfcad.png",
            "href": "#",
            "story": (
                "Candyland, but make it 3D. I teamed up with Sachin (7B) for an international "
                "SelfCAD competition, took 1st, and later spent a couple of years as a SelfCAD "
                "ambassador — tutorials, community, and teaching other people how to make "
                "weird little worlds on purpose.\n\n"
                "This is still one of my favorite proofs that “nerdy stuff” and “pretty stuff” "
                "are the same hobby if you let them be."
            ),
        },
        {
            "slug": "dreamyuni",
            "title": "DreamyUni",
            "category": "marketing / HR",
            "image": f"{STATIC_PROJECTS}/dreamyuni.png",
            "href": "#",
            "story": (
                "DreamyUni is a two-act story in one company. I started as a marketing intern "
                "(Oct 2024–Jun 2025): campaigns, visuals, the “please make this make sense on "
                "the internet” brief. Then I moved into Human Resources Director, still Brooklyn-based, "
                "still remote-brained, now on people ops.\n\n"
                "Same org, different muscle. Marketing taught me how a project looks from the "
                "outside. HR taught me how it feels from the inside — recruiting, coordination, "
                "and not letting the team become a group chat with extra steps."
            ),
        },
        {
            "slug": "microbit-automizer",
            "title": "micro:bit Automizer",
            "category": "hardware / automation",
            "image": f"{STATIC_PROJECTS}/microbit.svg",
            "href": "#",
            "story": (
                "The micro:bit Automizer is a hardware experiment: take the BBC micro:bit — "
                "that little yellow board with the 5×5 LED face — and turn it into a pocket "
                "automizer. Sensors in, routines out. Buttons, light, temperature, motion, "
                "whatever I can wire without setting a desk on fire.\n\n"
                "It’s the opposite of a 40-page plan. I wanted something that actually does "
                "the thing: trigger a reminder, log a reading, flash a pattern, kick off a "
                "tiny chain of actions. Builder energy, classroom hardware, slightly feral "
                "curiosity. Ships are not built for the harbor; yellow boards are not built "
                "to sit in a drawer."
            ),
        },
    ],
    "writing": [
        {
            "title": "Frisco ISD students earn medals at FCCLA nationals",
            "date": "Press",
            "publisher": "Frisco Enterprise / Star Local Media",
            "excerpt": (
                "Coverage of my FCCLA NATS results: National Champion & Gold Medalist "
                "(School to Career Challenge Test Level 2) and Silver Medal Finalist "
                "(Sustainability Challenge Level 2)."
            ),
            "href": "https://starlocalmedia.com/friscoenterprise/news/frisco-isd-students-earn-medals-at-fccla-nationals/article_54aa6c9e-50a1-47a8-b710-5dcd8dca20c9.html",
        },
        {
            "title": "Unveiling True Self: Defying Society's Gaze",
            "date": "Paper publication",
            "publisher": "CCMT Education Cell",
            "excerpt": "A poem on identity, perception, and pushing back against how society sees us.",
            "href": "",
        },
        {
            "title": "Comparative Analysis of Top U.S. Universities",
            "date": "RoundPier",
            "publisher": "RoundPier",
            "excerpt": "Research comparing top U.S. universities and what makes each one stand out.",
            "href": "https://gumroad.com/d/6c7b4829d113e72db088f2dd385b263f",
        },
    ],
    "contact": {
        "section_label": "SAY HI ♡",
        "headline": "let's",
        "headline_em": "chat?",
        "decorative_num": "ฅ^>⩊<^ ฅ",
        "body": (
            "Got an idea, a collab, or just wanna vibe about 3D models and poetry? "
            "I'd love to hear from you. No formal pitch required, just say hello."
        ),
        "cta_label": "SEND A HELLO",
        "cta_href": "/contact",
        "school_hours": "weekdays, 9:00 AM – 4:30 PM",
    },
}

BASE_HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#f3efe8">
  <title>{{ page_title }} | {{ meta.name }}</title>
  <script>
    (function () {
      try {
        var t = localStorage.getItem("theme");
        document.documentElement.setAttribute("data-theme", t === "dark" ? "dark" : "light");
      } catch (e) {
        document.documentElement.setAttribute("data-theme", "light");
      }
    })();
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" href="https://fonts.gstatic.com/s/jost/v18/92zPtBhPNqw79Ij1E865zBUv7myjJQVDPokMmuHL.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="https://fonts.gstatic.com/s/jost/v18/92zPtBhPNqw79Ij1E865zBUv7mx9IgVDPokMmuHL.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="https://fonts.gstatic.com/s/syncopate/v22/pe0pMIuPIYBCpEV5eFdKvtKaBvRue1UwVg.woff2" as="font" type="font/woff2" crossorigin>
  <style>
    @font-face {
      font-family: "Jost";
      src: url("https://fonts.gstatic.com/s/jost/v18/92zPtBhPNqw79Ij1E865zBUv7myjJQVDPokMmuHL.woff2") format("woff2");
      font-weight: 400; font-style: normal; font-display: swap;
    }
    @font-face {
      font-family: "Jost";
      src: url("https://fonts.gstatic.com/s/jost/v18/92zPtBhPNqw79Ij1E865zBUv7mx9IgVDPokMmuHL.woff2") format("woff2");
      font-weight: 600; font-style: normal; font-display: swap;
    }
    @font-face {
      font-family: "Jost";
      src: url("https://fonts.gstatic.com/s/jost/v18/92zJtBhPNqw73oHH7BbQp4-B6XlrZu0FNIgun_HLMEo.woff2") format("woff2");
      font-weight: 400; font-style: italic; font-display: swap;
    }
    @font-face {
      font-family: "Syncopate";
      src: url("https://fonts.gstatic.com/s/syncopate/v22/pe0pMIuPIYBCpEV5eFdKvtKaBvRue1UwVg.woff2") format("woff2");
      font-weight: 700; font-style: normal; font-display: swap;
    }
  </style>
  <link rel="stylesheet" href="/static/site.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <div class="grid-bg" aria-hidden="true">
    <div class="grid-paper"></div>
    <div class="grid-lines"></div>
  </div>
  <div class="ambient" aria-hidden="true">
    <div class="moving-light"></div>
    <div class="moving-light-2"></div>
    <div class="float-shape float-shape-1"></div>
    <div class="float-shape float-shape-2"></div>
    <div class="float-shape float-shape-3"></div>
    <div class="float-cross"></div>
  </div>
  <div class="cursor-glow" id="cursorGlow" aria-hidden="true"></div>

  <div class="ticker-wrap">
    <div class="ticker">
      {% for _ in range(2) %}
        {% for item in ticker %}
          <span class="ticker-item">{{ item }}<span class="sep"> / </span></span>
        {% endfor %}
        <span class="ticker-item">{{ meta.version }}<span class="sep"> / </span></span>
        <span class="ticker-item">©{{ meta.year }}<span class="sep"> / </span></span>
      {% endfor %}
    </div>
  </div>

  <header class="site-header">
    <div class="nav-inner">
      <a href="/" class="logo">{{ meta.name }}</a>
      <ul class="nav-links" id="nav-links" aria-label="Main navigation">
        {% for link in nav %}
          <li><a href="{{ link.href }}" class="nav-link{% if active == link.label %} active{% endif %}">{{ link.label }}</a></li>
        {% endfor %}
      </ul>
      <div class="nav-tools">
        <button type="button" class="theme-switch" id="themeSwitch" role="switch" aria-checked="false" aria-label="Switch to dark mode">
          <span class="theme-switch-label">Dark mode</span>
          <span class="theme-switch-knob" aria-hidden="true"></span>
        </button>
        <button type="button" class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="nav-links" aria-label="Open menu">
          <span class="nav-toggle-bars" aria-hidden="true"></span>
        </button>
      </div>
    </div>
  </header>

  <main class="page{% if wide_page %} page-wide{% endif %}" id="main-content">
    {% block content %}{% endblock %}
    {% if show_contact %}
    <section class="contact-block reveal{% if wide_page %} page-inner{% endif %}">
      <p class="contact-label">{{ contact.section_label }}</p>
      <div class="contact-headline-row">
        <h2 class="contact-headline">{{ contact.headline }} <em>{{ contact.headline_em }}</em></h2>
        <span class="contact-num cute">{{ contact.decorative_num }}</span>
      </div>
      <p class="contact-body">{{ contact.body }}</p>
      <a href="{{ contact.cta_href }}" class="btn-cta magnetic">
        {{ contact.cta_label }}
        <span class="btn-arrow"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H9M17 7V15"/></svg></span>
      </a>
    </section>
    {% endif %}
  </main>

  <footer class="site-footer">
    <div class="footer-inner">
      <div class="social-ticker">
        {% for s in social %}
          <a href="{{ s.href }}" class="social-link"{% if s.href != '#' %} target="_blank" rel="noopener noreferrer"{% endif %}>{{ s.label }}</a>
          {% if not loop.last %}<span style="color:var(--muted)"> / </span>{% endif %}
        {% endfor %}
      </div>
      <p class="copyright">{{ meta.copyright }}</p>
    </div>
  </footer>

  <script>
    const themeSwitch = document.getElementById("themeSwitch");
    const themeMeta = document.querySelector('meta[name="theme-color"]');
    function currentTheme() {
      return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    }
    function applyTheme(theme) {
      document.documentElement.setAttribute("data-theme", theme);
      try { localStorage.setItem("theme", theme); } catch (e) {}
        themeSwitch.setAttribute("aria-checked", theme === "dark" ? "true" : "false");
      themeSwitch.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
      if (themeMeta) themeMeta.setAttribute("content", theme === "dark" ? "#131018" : "#f3efe8");
    }
    applyTheme(currentTheme());
    themeSwitch.addEventListener("click", () => {
      applyTheme(currentTheme() === "dark" ? "light" : "dark");
    });

    const navToggle = document.getElementById("navToggle");
    const navLinks = document.getElementById("nav-links");
    navToggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      navToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });

    const reveals = document.querySelectorAll(".reveal, .reveal-scale");
    const observer = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("visible"); });
    }, { threshold: 0.08 });
    reveals.forEach((el, i) => {
      el.style.transitionDelay = (el.dataset.delay || (i * 0.05)) + "s";
      observer.observe(el);
      const r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.92) el.classList.add("visible");
    });

    const glow = document.getElementById("cursorGlow");
    document.addEventListener("mousemove", e => {
      glow.style.left = e.clientX + "px";
      glow.style.top  = e.clientY + "px";
    });

    document.querySelectorAll("[data-tilt]").forEach(el => {
      el.addEventListener("mousemove", e => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width  - 0.5;
        const y = (e.clientY - r.top)  / r.height - 0.5;
        el.style.transform = `perspective(800px) rotateX(${-y*12}deg) rotateY(${x*12}deg) scale3d(1.02,1.02,1.02)`;
      });
      el.addEventListener("mouseleave", () => { el.style.transform = ""; });
    });

    document.querySelectorAll(".project-card").forEach(card => {
      const inner = card.querySelector(".project-card-inner");
      card.addEventListener("mousemove", e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width  - 0.5;
        const y = (e.clientY - r.top)  / r.height - 0.5;
        inner.style.transform = `rotateX(${-y*10}deg) rotateY(${x*10}deg)`;
      });
      card.addEventListener("mouseleave", () => { inner.style.transform = ""; });
    });

    document.querySelectorAll(".magnetic, .btn-pill").forEach(btn => {
      btn.addEventListener("mousemove", e => {
        const r = btn.getBoundingClientRect();
        const x = e.clientX - r.left - r.width/2;
        const y = e.clientY - r.top  - r.height/2;
        btn.style.transform = `translate(${x*0.15}px, ${y*0.15}px)`;
      });
      btn.addEventListener("mouseleave", () => { btn.style.transform = ""; });
    });

    const contactForm = document.getElementById("contact-form");
    if (contactForm) {
      contactForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(contactForm);
        const btn = contactForm.querySelector(".form-submit");
        if (btn) { btn.disabled = true; btn.textContent = "Opening email…"; }
        try {
          const res = await fetch("/contact/send", {
            method: "POST",
            body: fd,
            headers: { "X-Requested-With": "fetch" },
          });
          const data = await res.json();
          if (data.ok && data.mailto) {
            window.location.href = data.mailto;
            return;
          }
          window.location.href = "/contact?sent=0";
        } catch (err) {
          const name = fd.get("name") || "";
          const email = fd.get("email") || "";
          const message = fd.get("message") || "";
          const channel = fd.get("channel") || "personal";
          const to = channel === "school" ? {{ meta.school_email|tojson }} : {{ meta.email|tojson }};
          const cc = channel === "school" ? {{ meta.email|tojson }} : "";
          const subject = encodeURIComponent("Portfolio hello from " + name);
          const body = encodeURIComponent("From: " + name + "\nReply-to: " + email + "\n\n" + message + "\n");
          let mailto = "mailto:" + to + "?subject=" + subject + "&body=" + body;
          if (cc) mailto += "&cc=" + encodeURIComponent(cc);
          window.location.href = mailto;
        }
      });
    }
  </script>
</body>
</html>
"""

HOME_PAGE = r"""{% extends "base.html" %}
{% block content %}
<section class="hero">
  <div class="hero-copy">
    <p class="hero-eyebrow reveal">{{ meta.tagline }} <em class="italic">{{ meta.title_italic }}</em></p>
    <p class="hero-intro reveal" data-delay="0.1">{{ hero.intro | safe_em }}</p>
    <div class="hero-ctas reveal" data-delay="0.2">
      <a href="/work" class="btn-pill primary magnetic"><span>{{ hero.cta_work }}</span></a>
      <a href="/about" class="btn-pill magnetic"><span>{{ hero.cta_about }}</span></a>
    </div>
  </div>
  <div class="hero-visual reveal-scale visible" data-delay="0.15">
    <div class="hero-circle" aria-hidden="true"></div>
    <div class="hero-portrait-wrap" data-tilt>
      <img src="{{ hero.portrait }}" alt="{{ meta.name }}" width="800" height="1082" decoding="async">
      <span class="hero-badge">{{ meta.title }}</span>
    </div>
  </div>
</section>

<figure class="quote-banner reveal">
  <blockquote>“{{ quote.text }}”</blockquote>
  <figcaption>— {{ quote.attr }}</figcaption>
</figure>

<div class="big-scroll-wrap" aria-hidden="true">
  <div class="big-scroll">
    {% for _ in range(4) %}
      {% for word in hero.scrolling_words %}
        <h1>{{ word }}</h1>
      {% endfor %}
    {% endfor %}
  </div>
</div>

<div class="section-head reveal">
  <h2 class="page-title">selected <em>work</em></h2>
  <a href="/work" class="section-link">view all <span class="arrow">→</span></a>
</div>
<div class="work-grid">
  {% for p in projects[:4] %}
  <a href="{{ p.card_href }}" class="project-card reveal" data-delay="{{ loop.index0 * 0.08 }}"{% if p.card_external %} target="_blank" rel="noopener noreferrer"{% endif %}>
    <div class="project-card-inner">
      <div class="project-image-wrap">
        <img src="{{ p.image }}" alt="{{ p.title }}" loading="lazy">
        <span class="project-arrow"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H9M17 7V15"/></svg></span>
        <div class="project-meta">
          <h3 class="project-title">{{ p.title }}</h3>
          <span class="project-category">{{ p.category }}</span>
        </div>
      </div>
    </div>
  </a>
  {% endfor %}
</div>

<section class="whimsy-section" id="more-of-me">
  <div class="section-head reveal visible" style="border-top:none;padding-top:0;margin-bottom:1rem;">
    <h2 class="page-title">a lil bit more of <em>me</em></h2>
  </div>
  <p class="whimsy-intro reveal visible">{{ more_of_me.intro }}</p>
  <div class="whimsy-grid">
    {% for item in more_of_me.bits %}
    <div class="whimsy-card reveal" data-delay="{{ loop.index0 * 0.04 }}">
      <pre class="whimsy-ascii" aria-hidden="true">{{ item.ascii }}</pre>
      <p class="whimsy-label">{{ item.label }}</p>
      <p class="whimsy-detail">{{ item.detail }}</p>
    </div>
    {% endfor %}
  </div>
  <div class="ascii-gallery" aria-hidden="true">
    {% for art in more_of_me.ascii_cats %}
    <pre class="ascii-art">{{ art }}</pre>
    {% endfor %}
  </div>
</section>
{% endblock %}
"""

WORK_PAGE = r"""{% extends "base.html" %}
{% block content %}
<h1 class="page-title reveal">my <em>work</em></h1>
<div class="work-grid">
  {% for p in projects %}
  <a href="{{ p.card_href }}" class="project-card reveal" data-delay="{{ loop.index0 * 0.06 }}"{% if p.card_external %} target="_blank" rel="noopener noreferrer"{% endif %}>
    <div class="project-card-inner">
      <div class="project-image-wrap">
        <img src="{{ p.image }}" alt="{{ p.title }}" loading="lazy">
        <span class="project-arrow"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M17 7H9M17 7V15"/></svg></span>
        <div class="project-meta">
          <h3 class="project-title">{{ p.title }}</h3>
          <span class="project-category">{{ p.category }}</span>
        </div>
      </div>
    </div>
  </a>
  {% endfor %}
</div>
{% endblock %}
"""

PROJECT_PAGE = r"""{% extends "base.html" %}
{% block content %}
<article class="reveal visible">
  <p class="about-location">{{ project.category }}</p>
  <h1 class="page-title">{{ project.title }}</h1>
  <div class="project-story-hero reveal visible">
    <img src="{{ project.image }}" alt="{{ project.title }}" loading="lazy">
  </div>
  <div class="blog-body">
    {% for para in project.story_paragraphs %}
    <p>{{ para }}</p>
    {% endfor %}
  </div>
  {% if project.href and project.href != '#' %}
  <p style="margin-top:1.25rem;">
    <a href="{{ project.href }}" class="btn-pill magnetic" target="_blank" rel="noopener noreferrer"><span>view project link</span></a>
  </p>
  {% endif %}
  <p style="margin-top:1.5rem;"><a href="/work" class="section-link">back to work</a></p>
</article>
{% endblock %}
"""

ABOUT_PAGE = r"""{% extends "base.html" %}
{% block content %}
<div class="about-hero">
  <div class="about-photo reveal-scale visible" data-tilt>
    <img src="{{ about.portrait }}" alt="{{ meta.name }}" width="800" height="1082" decoding="async">
    <span class="about-photo-label">{{ meta.title }}</span>
  </div>
  <div>
    <h1 class="page-title reveal">about <em>me</em></h1>
    <p class="about-location reveal">{{ about.location }}</p>
    <p class="about-intro reveal">{{ about.intro | safe_em }}</p>

    <p class="timeline-label reveal">skills</p>
    <div class="skills-cloud reveal">
      {% for skill in about.skills %}
        <span class="skill-tag">{{ skill }}</span>
      {% endfor %}
    </div>

    <p class="timeline-label reveal">honors & awards</p>
    <div class="reveal" style="margin-bottom:1.5rem;">
      {% for award in about.awards %}
        <div class="award-item">{{ award }}</div>
      {% endfor %}
    </div>

    <p class="timeline-label reveal">languages</p>
    <div class="skills-cloud reveal">
      {% for lang in about.languages %}
        <span class="skill-tag">{{ lang }}</span>
      {% endfor %}
    </div>

    <p class="timeline-label reveal">certifications</p>
    <div class="timeline reveal">
      {% for cert in about.certifications %}
      <div class="timeline-item">
        <div>
          <div class="role">{{ cert.name }}</div>
          <div class="company">{{ cert.issuer }}{% if cert.credential_id %}, ID {{ cert.credential_id }}{% endif %}</div>
        </div>
        <span class="year">{{ cert.date }}</span>
      </div>
      {% endfor %}
    </div>

    <p class="timeline-label reveal">experience</p>
    <div class="exp-list reveal">
      {% for group in experience_groups %}
      <article class="exp-card">
        <h2 class="exp-card-head">{{ group.label }}</h2>
        {% for job in group.entries %}
        <div class="timeline-item">
          <div>
            <div class="role">{{ job.role }}</div>
            {% if job.detail %}
            <div class="company">
              {% if job.get('link') %}
                <a href="{{ job.link }}" target="_blank" rel="noopener noreferrer">{{ job.detail }}</a>
              {% else %}
                {{ job.detail }}
              {% endif %}
            </div>
            {% elif job.get('link') %}
            <div class="company"><a href="{{ job.link }}" target="_blank" rel="noopener noreferrer">open link</a></div>
            {% endif %}
          </div>
          <span class="year">{{ job.year }}</span>
        </div>
        {% endfor %}
      </article>
      {% endfor %}
    </div>

    <p class="timeline-label reveal">education</p>
    <div class="exp-list reveal">
      {% for group in education_groups %}
      <article class="exp-card">
        <h2 class="exp-card-head">{{ group.label }}</h2>
        {% for edu in group.entries %}
        <div class="timeline-item">
          <div>
            <div class="role">{{ edu.degree or edu.year }}</div>
            {% if edu.detail %}<div class="company">{{ edu.detail }}</div>{% endif %}
          </div>
          {% if edu.degree and edu.year %}<span class="year">{{ edu.year }}</span>{% endif %}
        </div>
        {% endfor %}
      </article>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
"""

WRITING_PAGE = r"""{% extends "base.html" %}
{% block content %}
<h1 class="page-title reveal">my <em>writing</em></h1>
<div>
  {% for post in writing %}
  {% if post.href %}
  <a href="{{ post.href }}" class="writing-item reveal" data-delay="{{ loop.index0 * 0.08 }}" target="_blank" rel="noopener noreferrer">
  {% else %}
  <article class="writing-item reveal" data-delay="{{ loop.index0 * 0.08 }}" style="cursor:default;">
  {% endif %}
    <div>
      <h3>{{ post.title }}</h3>
      <p>{{ post.excerpt }}</p>
      {% if post.publisher %}<p class="writing-publisher">Published by {{ post.publisher }}</p>{% endif %}
    </div>
    <span class="date">{{ post.date }}</span>
  {% if post.href %}</a>{% else %}</article>{% endif %}
  {% endfor %}
</div>
{% endblock %}
"""

BLOG_PAGE = r"""{% extends "base.html" %}
{% block content %}
<h1 class="page-title reveal">life <em>blog</em></h1>
<p class="about-location reveal">thoughts, experiments, and whatever I'm up to</p>
<div>
  {% for post in blogs %}
  <a href="/blog/{{ post.slug }}" class="writing-item reveal" data-delay="{{ loop.index0 * 0.08 }}">
    <div>
      <h3>{{ post.title }}</h3>
      <p>{{ post.excerpt }}</p>
    </div>
    <span class="date">{{ post.date }}</span>
  </a>
  {% else %}
  <p class="contact-body reveal">No posts yet. Check back soon.</p>
  {% endfor %}
</div>
<p class="reveal" style="margin-top:1.5rem;">
  <a href="/compose" class="btn-pill"><span>write a new post</span></a>
</p>
{% endblock %}
"""

BLOG_POST_PAGE = r"""{% extends "base.html" %}
{% block content %}
<article class="reveal visible">
  <p class="about-location">{{ post.date }}</p>
  <h1 class="page-title">{{ post.title }}</h1>
  <div class="blog-body">
    {% for para in post.body_paragraphs %}
    <p>{{ para }}</p>
    {% endfor %}
  </div>
  <p style="margin-top:1.5rem;"><a href="/blog" class="section-link">back to blog</a></p>
</article>
{% endblock %}
"""

COMPOSE_PAGE = r"""{% extends "base.html" %}
{% block content %}
<h1 class="page-title reveal">write a <em>post</em></h1>
{% if flash_msg %}
<p class="flash flash-{{ flash_type }}" role="status">{{ flash_msg }}</p>
{% endif %}
{% if not compose_authed %}
<form method="post" class="contact-form compose-form reveal" aria-label="Compose login">
  <div class="form-field">
    <label for="password">Compose password</label>
    <input type="password" id="password" name="password" required autocomplete="current-password">
  </div>
  <button type="submit" class="form-submit">Unlock</button>
</form>
{% else %}
<form method="post" class="contact-form compose-form reveal" aria-label="New blog post">
  <input type="hidden" name="action" value="publish">
  <div class="form-field">
    <label for="title">Title</label>
    <input type="text" id="title" name="title" required maxlength="200">
  </div>
  <div class="form-field">
    <label for="excerpt">Short excerpt</label>
    <input type="text" id="excerpt" name="excerpt" required maxlength="300">
  </div>
  <div class="form-field">
    <label for="body">Post body</label>
    <textarea id="body" name="body" required placeholder="Write your post. New paragraphs on blank lines."></textarea>
  </div>
  <button type="submit" class="form-submit">Publish</button>
</form>
{% endif %}
{% endblock %}
"""

CONTACT_PAGE = r"""{% extends "base.html" %}
{% block content %}
<h1 class="page-title reveal">say <em>hi</em> ♡</h1>
<p class="about-location reveal">plano, texas / ryu_kiara on discord</p>

{% if flash_msg %}
<p class="flash flash-{{ flash_type }}" role="status">{{ flash_msg }}</p>
{% endif %}

<section class="reveal visible">
  <p class="contact-body" style="font-size:18px;max-width:560px;">{{ contact.body }}</p>

  <div class="email-cards">
    <div class="email-card">
      <h3>Personal</h3>
      <a href="mailto:{{ meta.email }}">{{ meta.email }}</a>
      <p>Anytime. Best if you just want to talk.</p>
    </div>
    <div class="email-card">
      <h3>School · {{ contact.school_hours }}</h3>
      <a href="mailto:{{ meta.school_email }}?cc={{ meta.email }}">{{ meta.school_email }}</a>
      <p>Weekdays 9:00–4:30. Please CC my personal email so I don’t miss it.</p>
    </div>
  </div>

  <form method="post" action="/contact/send" class="contact-form" id="contact-form" aria-label="Send a message">
    <div class="form-field">
      <label for="name">Your name</label>
      <input type="text" id="name" name="name" required maxlength="120" autocomplete="name" placeholder="Who are you?">
    </div>
    <div class="form-field">
      <label for="email">Your email</label>
      <input type="email" id="email" name="email" required maxlength="200" autocomplete="email" placeholder="you@example.com">
    </div>
    <div class="form-field">
      <label for="channel">Send to</label>
      <select id="channel" name="channel">
        <option value="personal">Personal email (anytime)</option>
        <option value="school">School email, 9:00–4:30 · CC personal</option>
      </select>
      <span class="form-help">This opens your email app with the message filled in, so it actually reaches me.</span>
    </div>
    <div class="form-field">
      <label for="message">Message</label>
      <textarea id="message" name="message" required maxlength="5000" placeholder="Say hello, pitch an idea, or just vibe..."></textarea>
    </div>
    <button type="submit" class="form-submit">Send message</button>
  </form>
</section>
{% endblock %}
"""

ISM_PAGE = r"""{% extends "base.html" %}
{% block content %}
<p class="about-location reveal">Frisco ISD · Lebanon Trail</p>
<h1 class="page-title reveal">independent study &amp; <em>mentorship</em></h1>
<p class="contact-body reveal" style="font-size:18px;max-width:640px;">{{ ism.program }} — what we do, what I’m researching, and why I’m here.</p>

<figure class="quote-banner reveal">
  <blockquote>“{{ quote.text }}”</blockquote>
  <figcaption>— {{ quote.attr }}</figcaption>
</figure>

<div class="ism-grid">
  <article class="ism-card reveal">
    <h2>Program mission</h2>
    <p>{{ ism.mission }}</p>
    <h2 style="margin-top:1rem;">What we do</h2>
    <ul class="ism-list">
      {% for item in ism.what_we_do %}
      <li>{{ item }}</li>
      {% endfor %}
    </ul>
  </article>
  <div>
    <article class="ism-card reveal" data-delay="0.08">
      <h2>{{ ism.topic_title }}</h2>
      <p>{{ ism.topic }}</p>
    </article>
    <article class="ism-card reveal" data-delay="0.12" style="margin-top:0.85rem;">
      <h2>{{ ism.personal_title }}</h2>
      <p>{{ ism.personal }}</p>
    </article>
  </div>
</div>
{% endblock %}
"""

BRAIN_PAGE = r"""{% extends "base.html" %}
{% block content %}
<section class="brain-hero">
  <div class="brain-stickers" aria-hidden="true">
    <img class="sticker" src="/static/brain/shell.png" alt="" style="width:88px;top:8%;left:4%;transform:rotate(-12deg);">
    <img class="sticker" src="/static/brain/apple.png" alt="" style="width:70px;top:12%;right:8%;transform:rotate(8deg);">
    <img class="sticker" src="/static/brain/banana.png" alt="" style="width:96px;top:58%;left:2%;transform:rotate(-20deg);">
    <img class="sticker" src="/static/brain/keys.png" alt="" style="width:110px;top:42%;right:3%;transform:rotate(-18deg);">
    <img class="sticker" src="/static/brain/receipt.png" alt="" style="width:64px;bottom:6%;right:18%;transform:rotate(6deg);">
    <img class="sticker" src="/static/brain/star.png" alt="" style="width:56px;bottom:12%;left:12%;">
  </div>
  <p class="brain-kicker reveal">{{ brain.kicker }}</p>
  <h1 class="brain-title reveal">welcome to my <em>brain</em></h1>
</section>

<section class="brain-band brain-band-pink">
  <div class="brain-band-inner brain-split">
    <img class="brain-photo reveal-scale" src="/static/brain/portrait.jpg" alt="{{ meta.name }} in a pink striped sweater">
    <div>
      <h2 class="brain-title reveal" style="font-size:clamp(28px,5vw,48px);margin-bottom:0.75rem;">about <em>me</em></h2>
      <p class="brain-copy reveal">{{ brain.intro }}</p>
    </div>
  </div>
</section>

<section class="brain-band">
  <div class="brain-band-inner">
    <h2 class="brain-title reveal" style="font-size:clamp(28px,5vw,48px);">the <em>side hustles</em></h2>
    <div class="brain-hustles">
      {% for h in brain.hustles %}
      <article class="hustle reveal">
        <img src="{{ h.img }}" alt="{{ h.alt }}">
        <p>{{ h.text }}</p>
      </article>
      {% endfor %}
    </div>
    <p class="brain-note">{{ brain.hustles_note }}</p>
  </div>
</section>

<section class="brain-band brain-band-dark">
  <div class="brain-band-inner brain-dark-layout">
    <div>
      <h2 class="brain-title reveal" style="font-size:clamp(28px,5vw,48px);">hyper-<em>fixations</em></h2>
      <ul class="brain-fix-list">
        {% for item in brain.fixations %}
        <li>{{ item }}</li>
        {% endfor %}
      </ul>
      <p class="brain-note">{{ brain.fixations_note }}</p>
    </div>
    <div aria-hidden="true" style="position:relative;min-height:220px;">
      <img class="sticker" src="/static/brain/earbuds.png" alt="" style="width:140px;top:0;right:8%;">
      <img class="sticker" src="/static/brain/dog.png" alt="" style="width:120px;bottom:0;left:0;">
      <img class="sticker" src="/static/brain/coffee.png" alt="" style="width:90px;bottom:10%;right:0;">
    </div>
  </div>
</section>

<section class="brain-band">
  <div class="brain-band-inner">
    <h2 class="brain-title reveal" style="font-size:clamp(28px,5vw,48px);">brain <em>dump</em></h2>
    <div class="brain-hustles" style="margin-top:1rem;">
      {% for d in brain.dumps %}
      <article class="hustle reveal">
        <p style="color:var(--accent);font-size:11px;margin-bottom:0.4rem;">{{ d.label }}</p>
        <p>{{ d.text }}</p>
      </article>
      {% endfor %}
      <aside class="sticky-note reveal">
        <p>“{{ quote.text }}”</p>
        <cite>— {{ quote.attr }}</cite>
      </aside>
    </div>
  </div>
</section>
{% endblock %}
"""


def load_blogs() -> list[dict]:
    if not BLOGS_FILE.exists():
        return []
    raw = BLOGS_FILE.read_text(encoding="utf-8-sig").strip() or "[]"
    return json.loads(raw)


def save_blogs(blogs: list[dict]) -> None:
    BLOGS_FILE.write_text(
        json.dumps(blogs, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "post"


def group_items(items: list[dict], label_keys: tuple[str, ...]) -> list[dict]:
    groups: list[dict] = []
    index: dict[str, dict] = {}
    for item in items:
        key = item.get("group") or next((item.get(k) for k in label_keys if item.get(k)), "item")
        if key not in index:
            label = item.get("group") or next((item.get(k) for k in label_keys if item.get(k)), key)
            rec = {"label": label, "entries": []}
            index[key] = rec
            groups.append(rec)
        index[key]["entries"].append(item)
    return groups


def enrich_projects(projects: list[dict]) -> list[dict]:
    enriched = []
    for project in projects:
        item = dict(project)
        if project.get("story"):
            item["card_href"] = f"/work/{project['slug']}"
            item["card_external"] = False
        elif project.get("href") and project["href"] != "#":
            item["card_href"] = project["href"]
            item["card_external"] = True
        else:
            item["card_href"] = ""
            item["card_external"] = False
        enriched.append(item)
    return enriched


def get_project(slug: str) -> dict | None:
    for project in CONTENT["projects"]:
        if project.get("slug") == slug:
            return project
    return None


def story_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def save_message(name: str, email: str, message: str, channel: str) -> None:
    messages = []
    if MESSAGES_FILE.exists():
        raw = MESSAGES_FILE.read_text(encoding="utf-8-sig").strip() or "[]"
        messages = json.loads(raw)
    messages.append({
        "name": name,
        "email": email,
        "message": message,
        "channel": channel,
        "at": datetime.now(timezone.utc).isoformat(),
    })
    MESSAGES_FILE.write_text(
        json.dumps(messages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_mailto(name: str, reply_email: str, message: str, channel: str) -> str:
    personal = CONTENT["meta"]["email"]
    school = CONTENT["meta"]["school_email"]
    to_addr = school if channel == "school" else personal
    cc = personal if channel == "school" else ""
    subject = quote(f"Portfolio hello from {name}")
    body = quote(f"From: {name}\nReply-to: {reply_email}\n\n{message}\n")
    url = f"mailto:{to_addr}?subject={subject}&body={body}"
    if cc:
        url += f"&cc={quote(cc)}"
    return url


def safe_em_filter(text: str) -> Markup:
    if not text:
        return Markup("")
    escaped = str(escape(text))
    html = re.sub(
        r"&lt;em&gt;(.*?)&lt;/em&gt;",
        lambda m: f"<em>{m.group(1)}</em>",
        escaped,
    )
    return Markup(html)


_jinja = Environment(
    loader=DictLoader({
        "base.html": BASE_HTML,
        "home.html": HOME_PAGE,
        "work.html": WORK_PAGE,
        "project.html": PROJECT_PAGE,
        "about.html": ABOUT_PAGE,
        "writing.html": WRITING_PAGE,
        "contact.html": CONTACT_PAGE,
        "blog.html": BLOG_PAGE,
        "blog_post.html": BLOG_POST_PAGE,
        "compose.html": COMPOSE_PAGE,
        "ism.html": ISM_PAGE,
        "brain.html": BRAIN_PAGE,
    }),
    autoescape=select_autoescape(["html"]),
)
_jinja.filters["safe_em"] = safe_em_filter


def _ctx(*, active: str, page_title: str, show_contact: bool = True, wide_page: bool = False, **extra) -> dict:
    ctx = {
        "active": active,
        "page_title": page_title,
        "show_contact": show_contact,
        "wide_page": wide_page,
        "meta": CONTENT["meta"],
        "hero": CONTENT["hero"],
        "nav": CONTENT["nav"],
        "ticker": CONTENT["ticker"],
        "social": CONTENT["social"],
        "contact": CONTENT["contact"],
        "about": CONTENT["about"],
        "quote": CONTENT["quote"],
        "ism": CONTENT["ism"],
        "brain": CONTENT["brain"],
        "experience_groups": group_items(CONTENT["about"]["experience"], ("company",)),
        "education_groups": group_items(CONTENT["about"]["education"], ("school", "degree")),
        "projects": enrich_projects(CONTENT["projects"]),
        "writing": CONTENT["writing"],
        "more_of_me": CONTENT["more_of_me"],
        "blogs": load_blogs(),
        "flash_msg": session.pop("flash_msg", None) if has_request_context() else None,
        "flash_type": session.pop("flash_type", "success") if has_request_context() else "success",
        "compose_authed": session.get("compose_authed", False) if has_request_context() else False,
    }
    ctx.update(extra)
    return ctx


def render_page(template_name: str, **kwargs):
    return _jinja.get_template(template_name).render(**_ctx(**kwargs))


@app.route("/")
def home():
    return render_page("home.html", active="", page_title="Home")


@app.route("/work")
def work():
    return render_page("work.html", active="WORK", page_title="Work")


@app.route("/work/<slug>")
def project_detail(slug: str):
    project = get_project(slug)
    if not project or not project.get("story"):
        return redirect(url_for("work"))
    detail = dict(project)
    detail["story_paragraphs"] = story_paragraphs(project["story"])
    return render_page(
        "project.html",
        active="WORK",
        page_title=project["title"],
        project=detail,
    )


@app.route("/about")
def about():
    return render_page("about.html", active="ABOUT", page_title="About")


@app.route("/ism")
def ism():
    return render_page("ism.html", active="ISM", page_title="ISM")


@app.route("/brain")
def brain():
    return render_page("brain.html", active="BRAIN", page_title="Brain dump", wide_page=True)


@app.route("/contact")
def contact():
    return render_page("contact.html", active="CONTACT", page_title="Contact", show_contact=False)


@app.route("/contact/send", methods=["POST"])
def contact_send():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    message = (request.form.get("message") or "").strip()
    channel = (request.form.get("channel") or "personal").strip()
    wants_json = request.headers.get("X-Requested-With") == "fetch"
    if not name or not email or not message:
        if wants_json:
            return jsonify({"ok": False, "error": "missing"}), 400
        session["flash_msg"] = "Please fill in all fields."
        session["flash_type"] = "error"
        return redirect(url_for("contact"))
    try:
        save_message(name, email, message, channel)
    except OSError:
        if not wants_json:
            session["flash_msg"] = "Could not save your message. Opening email instead."
            session["flash_type"] = "error"
    mailto = build_mailto(name, email, message, channel)
    if wants_json:
        return jsonify({"ok": True, "mailto": mailto})
    return redirect(mailto)


@app.route("/writing")
def writing():
    return render_page("writing.html", active="WRITING", page_title="Writing")


@app.route("/blog")
def blog():
    return render_page("blog.html", active="BLOG", page_title="Blog")


@app.route("/blog/<slug>")
def blog_post(slug: str):
    blogs = load_blogs()
    post = next((b for b in blogs if b.get("slug") == slug), None)
    if not post:
        return redirect(url_for("blog"))
    post = dict(post)
    post["body_paragraphs"] = [p.strip() for p in post.get("body", "").split("\n\n") if p.strip()]
    return render_page(
        "blog_post.html",
        active="BLOG",
        page_title=post["title"],
        post=post,
    )


@app.route("/compose", methods=["GET", "POST"])
def compose():
    if request.method == "POST":
        if request.form.get("action") == "publish" and session.get("compose_authed"):
            title = (request.form.get("title") or "").strip()
            excerpt = (request.form.get("excerpt") or "").strip()
            body = (request.form.get("body") or "").strip()
            if title and excerpt and body:
                blogs = load_blogs()
                slug = slugify(title)
                if any(b.get("slug") == slug for b in blogs):
                    slug = f"{slug}-{len(blogs) + 1}"
                blogs.insert(0, {
                    "slug": slug,
                    "title": title,
                    "date": datetime.now().strftime("%b %Y"),
                    "excerpt": excerpt,
                    "body": body,
                })
                save_blogs(blogs)
                return redirect(url_for("blog_post", slug=slug))
        password = request.form.get("password", "")
        if password == COMPOSE_PASSWORD:
            session["compose_authed"] = True
            return redirect(url_for("compose"))
        session["flash_msg"] = "Wrong password."
        session["flash_type"] = "error"
        return redirect(url_for("compose"))
    return render_page("compose.html", active="BLOG", page_title="Compose", show_contact=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
