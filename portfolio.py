"""
Lorris-inspired portfolio, derived from:
https://outstanding-strengthening-284213.framer.app/

Run:  pip install flask && python portfolio.py
Open: http://127.0.0.1:5000

Blog compose password: set COMPOSE_PASSWORD env var (default: kia-compose-2026)
Messages saved to: messages.json
"""

from __future__ import annotations

import json
import logging
import os
import re
import secrets
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from flask import Flask, has_request_context, jsonify, redirect, request, session, url_for
from jinja2 import DictLoader, Environment, select_autoescape
from markupsafe import Markup, escape

BASE_DIR = Path(__file__).resolve().parent
STATIC_PROJECTS = "/static/projects"
PACKAGED_BLOGS = BASE_DIR / "blogs.json"
PACKAGED_MESSAGES = BASE_DIR / "messages.json"
COMPOSE_PASSWORD = os.environ.get("COMPOSE_PASSWORD", "kia-compose-2026")

log = logging.getLogger("portfolio")
if not log.handlers:
    logging.basicConfig(level=logging.INFO)

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
        {"label": "BRAINDUMP", "href": "/brain"},
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
            "Scouted by 1517 Fund, Danielle Strachman",
            "FCCLA Sustainability Challenge, State 3rd Place & National Qualifier",
            "FCSA Gold Medal, FCCLA State Leadership Conference",
            "FCCLA Regional Champion, State 3rd & National Qualifier, Sustainability",
            "FCCLA VP of Competitive Events, Power of One Leadership Awardee",
            "DECA Regional Competitor 2025-26",
            "S4CA Best Young Architect Award, 3x Contractor Award 2024-25",
            "SPOT VSSF Top 100 Young Scientists, India (x2)",
            "International 3D Design, SelfCAD Winner 2023-24",
            "Semi-Finalist Achievement in Distinction, Straight A's in all topics, SpellBee International",
            "Bronze Winner, Intl. Level (Zonal Rank 6, Intl. Rank 60) Science Olympiad",
        ],
        "experience": [
            {"role": "Founder", "company": "Adopurr", "detail": "making all nine lives of a cat matter :D", "year": "Jul 2025 to Present"},
            {"role": "Scouted Founder", "company": "1517 Fund", "detail": "Danielle Strachman", "year": "2025"},
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
                "A cat adoption can get decided in fifteen minutes. That always felt off to me, "
                "especially in a world that can already predict the next movie I will watch. If "
                "the algorithm is that good at entertainment, why are we still guessing when a "
                "cat needs a home?\n\n"
                "That question is why I built Adopurr, an AI-driven matching system I have been "
                "on for about two years. Freshman year I worked at Mini Cat Town: play with the "
                "cats, feed them, notice if they were sick. I could have stopped at cute. I "
                "did not. Same breed, completely different personalities, and I kept thinking "
                "that if we study human traits to make better decisions, we can study animals "
                "the same way. So I started reading the journals, then using things like Monte "
                "Carlo and random forest to match cats with the people who will actually keep "
                "them. Happy cat, happy home.\n\n"
                "I used to hate coding. Both of my parents do it for a living, and debugging "
                "never looked like a calling from where I was sitting. Research is what made "
                "it click. The work was not the problem. Sitting in someone else's workplace "
                "was. That is also when I decided I would rather build something that helps "
                "people and animals than work for someone else. Social entrepreneur is the "
                "flashy label. I just wanted the matching to be less random.\n\n"
                "Getting into the 1517 Fund community changed the pace. We have been in talks "
                "with Dallas Animal Shelter, Operation Kindness, and other local shelters, and "
                "the work has expanded into dogs: characteristics, emotional triggers, the "
                "same matching problem with a bigger animal. Over the summer we planned Paws "
                "for Cause, an NPO branch where high school chapters advocate for animal "
                "welfare and fundraise. We have already scouted more than 25 chapters, got "
                "$400 from national FCCLA to start, and we are raising the rest ourselves."
            ),
        },
        {
            "slug": "arkire",
            "title": "Arkire",
            "category": "co-founder / growth",
            "image": f"{STATIC_PROJECTS}/arkire.jpg",
            "href": "#",
            "story": (
                "Arkire was a smart marketing agency that taught students how marketing "
                "actually works. I came in as co-founder and head of growth: positioning, "
                "outreach, turning interest into real users instead of a nice deck.\n\n"
                "I left because it stopped lining up with the kind of work I want to be "
                "responsible for. Not a blowup. A filter. I would rather spend the hours on "
                "things I still believe in when nobody is watching."
            ),
        },
        {
            "slug": "lt-fccla",
            "title": "Lebanon Trail FCCLA",
            "category": "chapter website / VP of competitive events",
            "image": f"{STATIC_PROJECTS}/lt-fccla.png",
            "href": "https://lt-fccla.vercel.app/",
            "story": (
                "Lebanon Trail FCCLA is the chapter that gave me a family after I moved to "
                "Texas. I joined as a member sophomore year, right after the move, and they "
                "made me feel included before I had any titles. Then I competed, learned FCCLA "
                "inside out, and got elected VP of Competitive Events.\n\n"
                "This year we have five service projects planned and about $3500 projected in "
                "funding. I also built the chapter site so members are not hunting for "
                "deadlines in a group chat. As VP of comp, I care less about collecting "
                "officers and more about whether people actually get to show who they are and "
                "still grow. That is the whole point of a chapter for me."
            ),
        },
        {
            "slug": "launchpoint",
            "title": "LaunchPoint",
            "category": "branding / 22k+ IG",
            "image": f"{STATIC_PROJECTS}/launchpoint.png",
            "href": "#",
            "story": (
                "LaunchPoint is a UGC startup for star athletes, founded by Tristan Rhee "
                "(CEO), Adam Barr-Neuwirth (CTO), and Caleb Downs of the Dallas Cowboys. I "
                "spent the summer there as a branding intern: graphics, Instagram, making the "
                "page look like it knew what it was doing.\n\n"
                "By the time I left, the account was at 22K+ followers. The work was fast and "
                "public, which I liked. Visuals are how people decide to stay, so I treated "
                "the feed like that, not like leftover posters."
            ),
        },
        {
            "slug": "fccla-nats",
            "title": "FCCLA Nationals",
            "category": "national champion + silver medal",
            "image": f"{STATIC_PROJECTS}/fccla-nats.jpg",
            "image_alt": "Four Lebanon Trail FCCLA members in red blazers under the 2026 National Leadership Conference welcome arch",
            "href": "https://starlocalmedia.com/friscoenterprise/news/frisco-isd-students-earn-medals-at-fccla-nationals/article_54aa6c9e-50a1-47a8-b710-5dcd8dca20c9.html",
            "story": (
                "At the FCCLA National Leadership Conference I was named National Champion and "
                "gold medalist in School to Career Challenge Test Level 2, and silver medal "
                "finalist in Sustainability Challenge Level 2.\n\n"
                "Frisco Enterprise and Star Local Media covered it for Frisco ISD. The photo "
                "is us in the red blazers under the NLC arch, which is still the version of "
                "the week I remember most. Competitive events are a lot of studying in rooms "
                "that do not look like this. Then they do."
            ),
        },
        {
            "slug": "fccla-sustainability",
            "title": "AeraDomus",
            "category": "indoor air / sustainability",
            "image": f"{STATIC_PROJECTS}/fccla-sustainability.jpg",
            "href": "https://www.friscoisd.org/article/3004120",
            "story": (
                "The strange thing about fainting is that it does not warn you. One morning "
                "before school I was getting ready, and then I was on the floor trying to "
                "figure out what just happened. The most annoying part at the time was missing "
                "a test. It felt random.\n\n"
                "Afterward I could not stop thinking about how much the rooms we live in "
                "affect our health. Indoor air pollution is tied to millions of premature "
                "deaths every year, and it is worse in lower-income housing: poor ventilation, "
                "materials that off-gas, solutions that cost more than the people most "
                "affected can pay.\n\n"
                "That is how AeraDomus started. It is a housing design framework for indoor "
                "air quality that uses passive, low-cost architecture instead of expensive "
                "filters: airflow patterns, solar-powered ventilation chimneys, materials that "
                "hold fewer toxins. I built a small model and watched smoke move through "
                "different paths. Healthy air vs. unhealthy air was a design decision, not a "
                "gadget.\n\n"
                "A lot of problems we file under health are also design problems. I want to "
                "build systems people barely notice, because when they work, they just quietly "
                "shape how you feel every day."
            ),
        },
        {
            "slug": "selfcad-champ",
            "title": "SelfCAD Champ",
            "category": "3D modeling / international award at 13",
            "image": f"{STATIC_PROJECTS}/selfcad.png",
            "href": "#",
            "story": (
                "When I was 13, my friend and I built Candyland from scratch in SelfCAD and "
                "won an international 3D award for it. No kit. Just the two of us trying to "
                "make a world that looked like sugar and still held together as a model.\n\n"
                "That win turned into a couple of years as a SelfCAD ambassador: tutorials, "
                "community, teaching other people how to make weird little scenes on purpose. "
                "It is still the project that made 3D feel like mine, not like an assignment."
            ),
        },
        {
            "slug": "dreamyuni",
            "title": "DreamyUni",
            "category": "operations / HR",
            "image": f"{STATIC_PROJECTS}/dreamyuni.png",
            "href": "#",
            "story": (
                "At DreamyUni I worked with Danny W. Chen in the early stages, first in "
                "marketing and then as HR director, helping students actually get into their "
                "dream universities.\n\n"
                "Marketing was how the project looked from the outside. HR was how it felt "
                "from the inside: recruiting, coordination, keeping a young team from turning "
                "into a group chat with extra steps. Same org. Different muscle. I liked both, "
                "which is probably why I stayed long enough to do them back to back."
            ),
        },
        {
            "slug": "microbit-automizer",
            "title": "micro:bit AUTOMAZER",
            "category": "Ithaca TISA / Finch + micro:bit",
            "image": f"{STATIC_PROJECTS}/microbit-automazer.jpg",
            "image_alt": "MakeCode for micro:bit project lambjam: Finch robot blocks, radio group 125, and two simulators for AUTOMAZER",
            "href": "#",
            "story": (
                "AUTOMAZER is the robot I built at Ithaca TISA. A Finch plus a micro:bit "
                "reads the space in front of it, figures out how to get through a maze, and "
                "sends those moves over radio to a second robot so it takes the same path.\n\n"
                "I programmed it in Microsoft MakeCode (project name lambjam) with radio group "
                "125, distance thresholds, a 360 scan when the path is messy, then a pick for "
                "the next turn. If it is too close, it backs out. If it is clear, it goes. "
                "The point was never a pretty demo. It was whether two boards could agree on "
                "a route without me standing there steering."
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
        "school_hours": "weekdays, 9:00 AM to 4:30 PM",
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
  <link rel="preload" href="https://fonts.gstatic.com/s/ibmplexmono/v19/-F6qfjptAgt5VM-kVkqdyU8n3twJwlBFgg.woff2" as="font" type="font/woff2" crossorigin>
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
    @font-face {
      font-family: "IBM Plex Mono";
      src: url("https://fonts.gstatic.com/s/ibmplexmono/v19/-F6qfjptAgt5VM-kVkqdyU8n3twJwlBFgg.woff2") format("woff2");
      font-weight: 400; font-style: normal; font-display: swap;
    }
  </style>
  <link rel="stylesheet" href="/static/site.css">
</head>
<body{% if brain_page %} class="brain-page"{% endif %}>
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

    (function () {
      const who = document.querySelector(".whoami");
      if (!who) return;
      const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      function updateWho() {
        if (reduced) {
          who.style.setProperty("--who-p", "1");
          return;
        }
        const span = Math.max(1, who.offsetHeight - window.innerHeight * 0.7);
        const p = Math.min(1, Math.max(0, -who.getBoundingClientRect().top / span));
        who.style.setProperty("--who-p", String(p));
      }
      updateWho();
      window.addEventListener("scroll", updateWho, { passive: true });
      window.addEventListener("resize", updateWho);
    })();

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
<section class="whoami" id="who-am-i" aria-label="Who am I">
  <div class="whoami-sticky">
    <h1 class="whoami-title reveal visible">who am <em>i</em></h1>
    <img
      class="whoami-cutout"
      src="/static/whoami-cutout.png"
      width="320"
      height="553"
      alt="{{ meta.name }} in a pink striped sweater and pink sunglasses, crouched with her chin in her hand"
    >
    <p class="whoami-line whoami-idk">i don't know..</p>
    <p class="whoami-line whoami-sure">but one thing for sure is i'm full of love, hustle</p>
  </div>
</section>

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
      <img src="{{ hero.portrait }}" alt="{{ meta.name }} in a black blazer at a desk, looking up at the camera" width="800" height="1082" decoding="async">
      <span class="hero-badge">{{ meta.title }}</span>
    </div>
  </div>
</section>

<figure class="quote-banner reveal">
  <blockquote>“{{ quote.text }}”</blockquote>
  <figcaption>{{ quote.attr }}</figcaption>
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
        <img src="{{ p.image }}" alt="{{ p.get('image_alt') or p.title }}" loading="lazy">
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
        <img src="{{ p.image }}" alt="{{ p.get('image_alt') or p.title }}" loading="lazy">
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
    <img src="{{ project.image }}" alt="{{ project.get('image_alt') or project.title }}" loading="lazy">
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
    <img src="{{ about.portrait }}" alt="{{ meta.name }} in a black blazer at DFW Startup Week, Capital One backdrop with a disco-ball cowboy" width="380" height="1466" decoding="async">
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
  {% if flash_msg %}
  <p class="flash flash-{{ flash_type }}" role="status">{{ flash_msg }}</p>
  {% endif %}
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
      <p>Weekdays 9:00 to 4:30. Please CC my personal email so I don’t miss it.</p>
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
        <option value="school">School email, 9:00 to 4:30 · CC personal</option>
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
<p class="contact-body reveal" style="font-size:18px;max-width:640px;">{{ ism.program }}: what we do, what I’m researching, and why I’m here.</p>

<figure class="quote-banner reveal">
  <blockquote>“{{ quote.text }}”</blockquote>
  <figcaption>{{ quote.attr }}</figcaption>
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
<div class="brain-collage">
<section class="brain-band brain-grid-cream">
  <div class="brain-band-inner">
    <div class="brain-hero-top">
      <p class="brain-kicker reveal">{{ brain.kicker }}</p>
      <h1 class="brain-title reveal">welcome to my <em>brain</em><span class="brain-emoji" aria-hidden="true">🧠</span></h1>
    </div>
    <img class="sticker" src="/static/brain/shell.png" alt="" style="width:86px;top:6%;left:42%;transform:rotate(-14deg);">
    <img class="sticker" src="/static/brain/apple.png" alt="" style="width:68px;top:10%;right:8%;transform:rotate(10deg);">
    <img class="sticker" src="/static/brain/banana.png" alt="" style="width:100px;top:38%;left:2%;transform:rotate(-22deg);">
    <img class="sticker" src="/static/brain/keys.png" alt="" style="width:108px;top:48%;right:6%;transform:rotate(-16deg);">
    <img class="sticker" src="/static/brain/clip.png" alt="" style="width:58px;top:18%;left:28%;transform:rotate(12deg);">
    <img class="sticker" src="/static/brain/notebook.png" alt="" style="width:72px;bottom:8%;left:8%;transform:rotate(8deg);">
    <img class="sticker" src="/static/brain/star.png" alt="" style="width:48px;top:28%;right:28%;transform:rotate(18deg);">
    <figure class="polaroid sticker" style="top:22%;left:8%;width:148px;">
      <img src="/static/casual-gallery.jpg" alt="{{ meta.name }} in a black blazer, photographed from above at a desk">
    </figure>
    <div class="brain-about-row">
      <div>
        <h2 class="brain-title reveal" style="font-size:clamp(28px,5vw,52px);margin-bottom:0.85rem;">about <em>me</em> 😼</h2>
        <p class="brain-copy reveal">{{ brain.intro }}</p>
      </div>
      <div class="brain-photo-wrap reveal-scale">
        <img class="brain-photo" src="/static/whoami-cutout.png" alt="{{ meta.name }} in a pink striped sweater, pink sunglasses, and patchwork jeans, crouched with her chin in her hand">
        <img class="sticker fragile-tag" src="/static/brain/fragile.png" alt="">
      </div>
    </div>
  </div>
</section>

<section class="brain-band brain-grid-pink">
  <div class="brain-band-inner">
    <h2 class="brain-title reveal" style="font-size:clamp(32px,6vw,64px);">the <em>side hustles</em> 🔥</h2>
    <div class="brain-hustle-field">
      <article class="hustle-float reveal" style="top:8%;left:2%;">
        <img src="/static/brain/cat.png" alt="stretching black cat sticker">
        <p>Random projects that started as purely “for fun”</p>
      </article>
      <article class="hustle-float reveal" style="top:18%;left:38%;">
        <img src="/static/brain/cd.png" alt="holographic CD sticker">
        <p>Helping people make things look and feel better</p>
      </article>
      <article class="hustle-float reveal" style="top:6%;right:2%;">
        <img src="/static/brain/polaroid.jpg" alt="tiny polaroid of a quiet street">
        <p>Saying yes, then learning how to do the thing</p>
      </article>
      <img class="sticker" src="/static/brain/receipt.png" alt="" style="width:70px;bottom:12%;left:22%;transform:rotate(8deg);">
      <img class="sticker" src="/static/brain/star.png" alt="" style="width:52px;bottom:18%;right:28%;">
      <img class="sticker" src="/static/brain/coffee.png" alt="" style="width:88px;bottom:4%;right:8%;transform:rotate(-8deg);">
      <img class="sticker" src="/static/brain/dog.png" alt="" style="width:92px;top:52%;left:52%;transform:rotate(8deg);">
    </div>
    <p class="brain-note">{{ brain.hustles_note }}</p>
  </div>
</section>

<section class="brain-band brain-grid-dark">
  <div class="brain-band-inner brain-dark-layout">
    <div>
      <h2 class="brain-title reveal" style="font-size:clamp(32px,6vw,64px);">hyper-<em>fixations</em> 😜</h2>
      <ul class="brain-fix-list">
        {% for item in brain.fixations %}
        <li>{{ item }}</li>
        {% endfor %}
      </ul>
      <p class="brain-note">{{ brain.fixations_note }}</p>
      <h2 class="brain-title reveal" style="font-size:clamp(26px,4vw,44px);margin-top:2rem;">brain <em>dump</em></h2>
      <div class="brain-dumps">
        {% for d in brain.dumps %}
        <article class="dump-card reveal">
          <strong>{{ d.label }}</strong>
          <p>{{ d.text }}</p>
        </article>
        {% endfor %}
      </div>
    </div>
    <div style="position:relative;min-height:280px;">
      <img class="sticker" src="/static/brain/earbuds.png" alt="" style="width:150px;top:0;right:4%;transform:rotate(12deg);">
      <img class="sticker" src="/static/brain/dog.png" alt="" style="width:128px;top:38%;left:0;">
      <img class="sticker" src="/static/brain/apple.png" alt="" style="width:70px;bottom:22%;right:10%;transform:rotate(-18deg);">
      <img class="sticker" src="/static/brain/keys.png" alt="" style="width:92px;bottom:4%;left:18%;transform:rotate(14deg);">
      <aside class="sticky-note reveal" style="position:relative;margin-top:12rem;">
        <p>“{{ quote.text }}”</p>
        <cite>{{ quote.attr }}</cite>
      </aside>
    </div>
  </div>
</section>
</div>
{% endblock %}
"""


def _writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except OSError:
        return False


def data_dir() -> Path:
    env = os.environ.get("DATA_DIR") or os.environ.get("RENDER_DISK_PATH")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env).expanduser())
    candidates.extend([Path("/var/data"), Path("/data"), BASE_DIR])
    for candidate in candidates:
        if _writable_dir(candidate):
            return candidate
    return BASE_DIR


def blogs_path() -> Path:
    env = os.environ.get("BLOGS_FILE")
    if env:
        path = Path(env).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    return data_dir() / "blogs.json"


def messages_path() -> Path:
    env = os.environ.get("MESSAGES_FILE")
    if env:
        path = Path(env).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    return data_dir() / "messages.json"


def atomic_write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_json_list(path: Path) -> list:
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8-sig").strip() or "[]"
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError) as exc:
        log.error("Failed to read %s: %s", path, exc)
        return []


def _seed_if_needed(path: Path, packaged: Path) -> None:
    if path.exists() or not packaged.exists():
        return
    if path.resolve() == packaged.resolve():
        return
    try:
        atomic_write_json(path, _read_json_list(packaged))
        log.info("Seeded %s from %s", path, packaged)
    except OSError as exc:
        log.warning("Could not seed %s: %s", path, exc)


def load_blogs() -> list[dict]:
    path = blogs_path()
    _seed_if_needed(path, PACKAGED_BLOGS)
    return _read_json_list(path)


def save_blogs(blogs: list[dict]) -> bool:
    path = blogs_path()
    try:
        atomic_write_json(path, blogs)
        log.info("Saved %s blog post(s) to %s", len(blogs), path)
        return True
    except OSError as exc:
        log.exception("Failed to save blogs to %s: %s", path, exc)
        return False


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


def save_message(name: str, email: str, message: str, channel: str) -> bool:
    path = messages_path()
    _seed_if_needed(path, PACKAGED_MESSAGES)
    messages = _read_json_list(path)
    messages.append({
        "name": name,
        "email": email,
        "message": message,
        "channel": channel,
        "at": datetime.now(timezone.utc).isoformat(),
    })
    try:
        atomic_write_json(path, messages)
        return True
    except OSError as exc:
        log.exception("Failed to save message to %s: %s", path, exc)
        return False


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


def _ctx(*, active: str, page_title: str, show_contact: bool = True, wide_page: bool = False, brain_page: bool = False, **extra) -> dict:
    ctx = {
        "active": active,
        "page_title": page_title,
        "show_contact": show_contact,
        "wide_page": wide_page,
        "brain_page": brain_page,
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
    return render_page("brain.html", active="BRAINDUMP", page_title="my braindump", wide_page=True, brain_page=True)


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
        saved = save_message(name, email, message, channel)
    except OSError:
        saved = False
    if not saved and not wants_json:
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
            if not (title and excerpt and body):
                session["flash_msg"] = "Please fill in title, excerpt, and body."
                session["flash_type"] = "error"
                return redirect(url_for("compose"))
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
            if not save_blogs(blogs):
                session["flash_msg"] = (
                    "Could not save this post. The disk may be read-only after deploy. "
                    "Set DATA_DIR or BLOGS_FILE to a writable persistent folder and try again."
                )
                session["flash_type"] = "error"
                return redirect(url_for("compose"))
            session["flash_msg"] = "Published."
            session["flash_type"] = "success"
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
