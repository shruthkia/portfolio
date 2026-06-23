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

from flask import Flask, has_request_context, redirect, request, session, url_for
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

# ─────────────────────────────────────────────────────────────────────────────
# CONTENT — swap in your details
# ─────────────────────────────────────────────────────────────────────────────

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
        "copyright": "©2026 | Shruthika Omkumar",
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
            "BS-ing (Native or Bilingual)",
        ],
        "awards": [
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
            "Semi-Finalist Achievement in Distinction, Straight A's in all topics",
            "Bronze Winner, Intl. Level (Zonal Rank 6, Intl. Rank 60)",
        ],
        "experience": [
            {"role": "Founder", "company": "Adopurr, making all nine lives of a cat matter :D", "year": "Jul 2025 to Present"},
            {"role": "Scouted Founder", "company": "1507 Funds, Danielle Strachman", "year": "2025"},
            {"role": "Co-Founder & Head of Growth", "company": "Arkire, Ontario, Canada", "year": "Feb 2025 to Sep 2025"},
            {"role": "Human Resources Director", "company": "DreamyUni, Brooklyn, NY", "year": "Jul 2025 to Present"},
            {"role": "Marketing Intern", "company": "DreamyUni, Brooklyn, NY", "year": "Oct 2024 to Jun 2025"},
            {"role": "UNA USA Ambassador", "company": "United Nations Association USA", "year": "2025-26", "link": "https://innerview.org/shruthikaomkumar2"},
            {"role": "Graphic Lead", "company": "LaunchPoint, 22k+ IG followers, visual strategy & growth", "year": "Jun 2026 to Present"},
            {"role": "Director of Fundraising", "company": "Horizon Labs", "year": "Mar 2025 to Present"},
            {"role": "Director of Fundraising", "company": "The Metastatic Cancer Initiative, Texas", "year": "Dec 2024 to Present"},
            {"role": "Regional Rep & Chapter President", "company": "Girls in Research Global, Washington", "year": "Oct 2024 to Present"},
            {"role": "Head of Operations", "company": "Visionary", "year": "Jan 2025 to Present"},
            {"role": "Operations Manager", "company": "Badavas, NYC Metro", "year": "Jan 2025 to Aug 2025"},
            {"role": "Ambassador, Intl. Competition Winner", "company": "SelfCAD, 3D modeling tutorials & community", "year": "Feb 2023 to Jun 2025"},
            {"role": "Intern", "company": "RoundPier, NYC Metro", "year": "Nov 2024 to Aug 2025"},
            {"role": "Internship Trainee", "company": "U R Rao Satellite Centre (URSC), ISRO, Bengaluru", "year": "Jun 2024"},
            {"role": "Internship Trainee", "company": "VSSC, ISRO, Thiruvananthapuram", "year": "Mar 2023"},
            {"role": "School Internship Programme Lead", "company": "Scholastic India, book fair lead, team of 10", "year": "Nov 2023 to Jan 2024"},
        ],
        "education": [
            {"degree": "High School Diploma", "school": "Lebanon Trail High School", "year": "Aug 2025 to May 2028"},
            {"degree": "High School", "school": "Milpitas High School", "year": "Jan 2025 to Jun 2025"},
            {"degree": "K-12", "school": "Mahatma Global Gateway", "year": "Jun 2016 to Jan 2025"},
            {"degree": "JuniorMBA, Entrepreneurship", "school": "Clever Harvey, Certified by IIT Roorkee", "year": "May 2024"},
            {"degree": "JuniorMBA, Advertising", "school": "Clever Harvey", "year": ""},
            {"degree": "JuniorMBA, Design and Branding", "school": "Clever Harvey", "year": ""},
        ],
        "certifications": [
            {"name": "Canva Essentials", "issuer": "Canva", "date": "Oct 2024", "credential_id": "0e2c89"},
            {"name": "Graphic Design Essentials", "issuer": "Canva", "date": "Oct 2024", "credential_id": "8415e2"},
            {"name": "Fundamentals of Digital Marketing", "issuer": "Google", "date": "Oct 2024", "credential_id": "331005004"},
        ],
    },
    "more_of_me": {
        "title": "a lil bit more of",
        "title_em": "me",
        "intro": "the random bits that don't really fit anywhere else but still very me",
        "bits": [
            {"ascii": "(ノ◕ヮ◕)ノ*:･ﾟ✧", "label": "hiphop aerobics", "detail": "certified, Mar 2017"},
            {"ascii": "✧･ﾟ: *✧･ﾟ:*", "label": "vocabulary & language dev", "detail": "SpellBee International, Jun 2023"},
            {"ascii": "¯\\_(ツ)_/¯", "label": "BS-ing", "detail": "native or bilingual"},
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
            "story": "",
        },
        {
            "slug": "arkire",
            "title": "Arkire",
            "category": "co-founder / growth",
            "image": f"{STATIC_PROJECTS}/arkire.jpg",
            "href": "#",
            "story": "",
        },
        {
            "slug": "launchpoint",
            "title": "LaunchPoint",
            "category": "graphic design / 22k+ IG",
            "image": f"{STATIC_PROJECTS}/launchpoint.png",
            "href": "#",
            "story": "",
        },
        {
            "slug": "fccla-sustainability",
            "title": "Sustainability Challenge",
            "category": "FCCLA / state 3rd, national qualifier",
            "image": f"{STATIC_PROJECTS}/fccla-sustainability.jpg",
            "href": "https://www.friscoisd.org/article/3004120",
            "story": "",
        },
        {
            "slug": "selfcad-champ",
            "title": "SelfCAD Champ",
            "category": "3D modeling / 1st prize · Candyland w/ Sachin (7B)",
            "image": f"{STATIC_PROJECTS}/selfcad.png",
            "href": "#",
            "story": "",
        },
        {
            "slug": "dreamyuni",
            "title": "DreamyUni",
            "category": "marketing / HR",
            "image": f"{STATIC_PROJECTS}/dreamyuni.png",
            "href": "#",
            "story": "",
        },
    ],
    "writing": [
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
        "cta_href": "mailto:shruthikaomkumar@gmail.com",
    },
}

THEME = {
    "bg": "#131018",
    "accent": "#f0b8c8",
    "accent_dark": "#b86b8a",
    "accent_40": "rgba(240, 184, 200, 0.4)",
    "accent_10": "rgba(240, 184, 200, 0.1)",
    "accent_glow": "#f0b8c880",
    "white": "#ffffff",
    "muted": "rgba(245, 210, 220, 0.82)",
    "text": "#f4f4f5",
    "text-soft": "rgba(255, 255, 255, 0.92)",
    "font_display": "'Syncopate', sans-serif",
    "font_body": "'Jost', sans-serif",
    "font_ui": "'Manrope', sans-serif",
    "ease": "cubic-bezier(0.44, 0, 0.56, 1)",
    "transition": "0.4s cubic-bezier(0.44, 0, 0.56, 1)",
}

BASE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="dark">
  <title>{{ page_title }} | {{ meta.name }}</title>
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
    :root {
      --bg: {{ theme.bg }};
      --accent: {{ theme.accent }};
      --accent-dark: {{ theme.accent_dark }};
      --accent-40: {{ theme.accent_40 }};
      --accent-10: {{ theme.accent_10 }};
      --accent-glow: {{ theme.accent_glow }};
      --white: {{ theme.white }};
      --text: {{ theme.text }};
      --text-soft: {{ theme["text-soft"] }};
      --muted: {{ theme.muted }};
      --font-display: Syncopate, "Segoe UI", sans-serif;
      --font-body: Jost, "Segoe UI", system-ui, sans-serif;
      --ease: {{ theme.ease }};
      --transition: {{ theme.transition }};
    }

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { -webkit-font-smoothing: antialiased; scroll-behavior: smooth; }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
    }
    body {
      background: var(--bg); color: var(--text);
      font-family: var(--font-body); font-size: 17px; line-height: 1.6;
      min-height: 100vh; overflow-x: hidden; cursor: default;
    }
    a { color: inherit; text-decoration: none; }
    a:focus-visible, button:focus-visible, input:focus-visible, textarea:focus-visible, .btn-pill:focus-visible {
      outline: 2px solid var(--accent); outline-offset: 3px;
    }
    .skip-link {
      position: absolute; left: -9999px; top: 0; z-index: 10000;
      background: var(--accent); color: var(--bg); padding: 0.75rem 1rem;
      font-weight: 600; border-radius: 0 0 8px 0;
    }
    .skip-link:focus { left: 0; }
    em, .italic { font-style: italic; color: var(--accent); font-weight: 400; }

    /* ── Ambient floating layer ── */
    .ambient { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }

    .moving-light {
      position: absolute; top: -340px; left: 50%;
      transform: translateX(-50%);
      width: 600px; height: 600px; border-radius: 50%;
      background: var(--accent-glow); filter: blur(100px);
      animation: drift 14s var(--ease) infinite alternate;
    }
    .moving-light-2 {
      position: absolute; bottom: -200px; right: -100px;
      width: 400px; height: 400px; border-radius: 50%;
      background: rgba(184, 107, 138, 0.35); filter: blur(80px);
      animation: drift2 18s var(--ease) infinite alternate;
    }

    .float-shape {
      position: absolute; border-radius: 50%;
      border: 1px solid var(--accent-10);
      animation: float 8s var(--ease) infinite;
    }
    .float-shape-1 { width: 80px; height: 80px; top: 18%; left: 8%; animation-delay: 0s; }
    .float-shape-2 { width: 24px; height: 24px; top: 60%; right: 12%; background: var(--accent-10); animation-delay: -2s; }
    .float-shape-3 { width: 120px; height: 120px; bottom: 25%; left: 5%; animation-delay: -4s; border-color: var(--accent-40); }
    .float-cross {
      position: absolute; width: 40px; height: 40px; top: 30%; right: 18%;
      animation: spin 20s linear infinite;
    }
    .float-cross::before, .float-cross::after {
      content: ""; position: absolute; background: var(--accent-40);
    }
    .float-cross::before { width: 1px; height: 100%; left: 50%; }
    .float-cross::after  { width: 100%; height: 1px; top: 50%; }

    @keyframes drift {
      from { transform: translateX(-50%) translateY(0); opacity: 0.6; }
      to   { transform: translateX(-42%) translateY(40px); opacity: 1; }
    }
    @keyframes drift2 {
      from { transform: translate(0, 0); }
      to   { transform: translate(-60px, -40px); }
    }
    @keyframes float {
      0%, 100% { transform: translateY(0) rotate(0deg); }
      50%      { transform: translateY(-24px) rotate(6deg); }
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Ticker ── */
    .ticker-wrap {
      border-bottom: 1px solid var(--accent-10);
      overflow: hidden; position: relative; z-index: 2;
    }
    .ticker { display: inline-flex; animation: marquee 28s linear infinite; }
    .ticker-item {
      display: inline-flex; align-items: center; gap: 1.25rem;
      padding: 0.65rem 0; font-size: 13px; letter-spacing: 0.08em;
      text-transform: lowercase; color: var(--muted);
    }
    .ticker-item .sep { color: var(--accent-40); }
    @keyframes marquee {
      from { transform: translateX(0); }
      to   { transform: translateX(-50%); }
    }

    /* ── Nav ── */
    .site-header {
      position: sticky; top: 0; z-index: 100;
      backdrop-filter: blur(16px);
      background: rgba(19, 16, 24, 0.8);
      border-bottom: 1px solid var(--accent-10);
    }
    .nav-inner {
      max-width: 1200px; margin: 0 auto; padding: 1.25rem 2rem;
      display: flex; align-items: center; justify-content: space-between;
    }
    .logo {
      font-family: var(--font-display); font-size: 14px;
      letter-spacing: 0.16em; text-transform: uppercase; color: var(--accent);
      transition: letter-spacing var(--transition);
    }
    .logo:hover { letter-spacing: 0.22em; }
    .nav-links { display: flex; gap: 2.5rem; list-style: none; }
    .nav-link {
      position: relative; font-size: 13px; letter-spacing: 0.08em;
      text-transform: uppercase; transition: color var(--transition);
    }
    .nav-link::after {
      content: ""; position: absolute; left: 0; bottom: -4px;
      width: 100%; height: 1px; background: var(--accent);
      transform: scaleX(0); transform-origin: left;
      transition: transform var(--transition);
    }
    .nav-link:hover, .nav-link.active { color: var(--accent); }
    .nav-link:hover::after, .nav-link.active::after { transform: scaleX(1); }

    /* ── Page shell ── */
    .page {
      position: relative; z-index: 1;
      max-width: 1200px; margin: 0 auto; padding: 0 2rem 6rem;
    }

    /* ── Reveal animations ── */
    .reveal {
      opacity: 0; transform: translateY(48px);
      transition: opacity 0.9s var(--ease), transform 0.9s var(--ease);
    }
    .reveal.visible { opacity: 1; transform: translateY(0); }
    .reveal-scale {
      opacity: 0; transform: scale(0.92);
      transition: opacity 1s var(--ease), transform 1s var(--ease);
    }
    .reveal-scale.visible { opacity: 1; transform: scale(1); }

    /* ── HERO ── */
    .hero {
      min-height: 92vh; display: grid;
      grid-template-columns: 1fr 1fr; gap: 3rem;
      align-items: center; padding: 4rem 0 2rem;
      position: relative;
    }
    @media (max-width: 809px) {
      .hero { grid-template-columns: 1fr; min-height: auto; padding-top: 2rem; }
      .nav-links { display: none; }
    }

    .hero-visual { position: relative; display: flex; justify-content: center; align-items: center; }

    .hero-circle {
      position: absolute; width: 340px; height: 340px;
      border-radius: 50%; background: var(--accent-dark);
      z-index: 0; animation: pulse-ring 4s var(--ease) infinite;
    }
    .hero-circle::before {
      content: ""; position: absolute; inset: -20px;
      border-radius: 50%; border: 1px solid var(--accent-40);
      animation: spin 12s linear infinite;
    }
    .hero-circle::after {
      content: ""; position: absolute; inset: -45px;
      border-radius: 50%; border: 1px dashed var(--accent-10);
      animation: spin 25s linear infinite reverse;
    }
    @keyframes pulse-ring {
      0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(240,184,200,0.15); }
      50%      { transform: scale(1.03); box-shadow: 0 0 60px 10px rgba(240,184,200,0.08); }
    }

    .hero-portrait-wrap {
      position: relative; z-index: 2;
      width: 280px; height: 380px;
      border-radius: 11px; overflow: hidden;
      box-shadow: 0 30px 80px rgba(0,0,0,0.5), inset 0 0 0 1px var(--accent-10);
      transform-style: preserve-3d;
      transition: transform 0.1s linear;
    }
    .hero-portrait-wrap img {
      width: 100%; height: 100%; object-fit: cover;
      transition: transform 0.6s var(--ease);
    }
    .hero-portrait-wrap:hover img { transform: scale(1.06); }

    .hero-portrait-wrap::after {
      content: ""; position: absolute; inset: 0;
      background: linear-gradient(180deg, transparent 55%, rgba(16,19,17,0.85) 100%);
      pointer-events: none;
    }

    .hero-badge {
      position: absolute; bottom: 1rem; left: 1rem; z-index: 3;
      font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase;
      font-style: italic; color: var(--accent);
      background: rgba(16,19,17,0.7); backdrop-filter: blur(8px);
      padding: 0.4rem 0.75rem; border-radius: 100px;
      border: 1px solid var(--accent-10);
    }

    .hero-copy { position: relative; z-index: 2; }

    .hero-eyebrow {
      font-size: 13px; letter-spacing: 0.16em; text-transform: uppercase;
      color: var(--muted); margin-bottom: 1.5rem;
    }

    .hero-intro {
      font-size: clamp(18px, 2.5vw, 24px); line-height: 1.6;
      color: var(--text-soft); max-width: 480px; margin-bottom: 2.5rem;
    }
    .hero-intro em { font-style: italic; font-weight: 400; }

    .hero-ctas { display: flex; gap: 1rem; flex-wrap: wrap; }

    .btn-pill {
      display: inline-flex; align-items: center; gap: 0.75rem;
      padding: 0.85rem 1.5rem; border-radius: 100px;
      font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase;
      border: 1px solid var(--accent-10); background: var(--accent-10);
      transition: all var(--transition); position: relative; overflow: hidden;
    }
    .btn-pill::before {
      content: ""; position: absolute; inset: 0;
      background: var(--accent); transform: scaleX(0); transform-origin: left;
      transition: transform var(--transition); z-index: 0;
    }
    .btn-pill span { position: relative; z-index: 1; transition: color var(--transition); }
    .btn-pill:hover::before { transform: scaleX(1); }
    .btn-pill:hover span { color: var(--bg); }
    .btn-pill.primary { background: var(--accent); border-color: var(--accent); }
    .btn-pill.primary span { color: var(--bg); font-weight: 600; }
    .btn-pill.primary::before { background: var(--white); }
    .btn-pill.primary:hover span { color: var(--bg); }

    /* Big scrolling name strip */
    .big-scroll-wrap {
      overflow: hidden; width: 100%; padding: 3rem 0 1rem;
      mask-image: linear-gradient(90deg, transparent, black 10%, black 90%, transparent);
    }
    .big-scroll {
      display: flex; gap: 4rem; width: max-content;
      animation: big-marquee 16s linear infinite;
    }
    .big-scroll h1 {
      font-family: var(--font-display);
      font-size: clamp(60px, 12vw, 160px);
      letter-spacing: -0.03em; text-transform: uppercase;
      white-space: nowrap; line-height: 0.9;
      color: transparent;
      -webkit-text-stroke: 1px var(--accent-40);
      transition: -webkit-text-stroke var(--transition), color var(--transition);
    }
    .big-scroll h1:nth-child(even) {
      font-family: var(--font-body); font-style: italic; font-weight: 700;
      -webkit-text-stroke: 0; color: var(--accent-10);
    }
    .big-scroll-wrap:hover .big-scroll h1 { -webkit-text-stroke-color: var(--accent); }
    .big-scroll-wrap:hover .big-scroll h1:nth-child(even) { color: var(--accent-40); }
    @keyframes big-marquee {
      from { transform: translateX(0); }
      to   { transform: translateX(-50%); }
    }

    /* ── Section titles ── */
    .section-head {
      display: flex; align-items: baseline; justify-content: space-between;
      margin-bottom: 3rem; padding-top: 4rem;
      border-top: 1px solid var(--accent-10);
    }
    .page-title {
      font-family: var(--font-display);
      font-size: clamp(36px, 7vw, 64px);
      letter-spacing: -0.02em; text-transform: lowercase; line-height: 1;
    }
    .page-title em {
      font-family: var(--font-body); font-style: italic; font-weight: 700;
      text-transform: lowercase; color: var(--accent);
    }
    .section-link {
      font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase;
      color: var(--muted); transition: color var(--transition);
      display: flex; align-items: center; gap: 0.5rem;
    }
    .section-link:hover { color: var(--accent); }
    .section-link .arrow {
      width: 32px; height: 32px; border-radius: 50%;
      background: var(--accent-10); display: grid; place-items: center;
      transition: transform var(--transition), background var(--transition);
    }
    .section-link:hover .arrow { transform: translate(3px,-3px); background: var(--accent); }

    /* ── Work grid ── */
    .work-grid {
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 2rem;
    }
    @media (max-width: 809px) { .work-grid { grid-template-columns: 1fr; } }

    .project-card { perspective: 1200px; display: block; }
    .project-card-inner {
      border-radius: 11px; overflow: hidden;
      background: var(--accent-10);
      box-shadow: inset 0 0 0 1px var(--accent-10);
      transform-style: preserve-3d;
      transition: box-shadow var(--transition);
    }
    .project-card:hover .project-card-inner {
      box-shadow: inset 0 0 0 1px var(--accent), 0 20px 60px rgba(0,0,0,0.4);
    }
    .project-image-wrap { position: relative; aspect-ratio: 4/3; overflow: hidden; }
    .project-image-wrap img {
      width: 100%; height: 100%; object-fit: cover;
      transition: transform 0.7s var(--ease), filter 0.5s;
    }
    .project-card:hover .project-image-wrap img {
      transform: scale(1.08); filter: brightness(1.1);
    }
    .project-image-wrap::after {
      content: ""; position: absolute; inset: 0;
      background: linear-gradient(180deg, transparent 55%, rgba(16,19,17,0.95) 100%);
    }
    .project-meta {
      position: absolute; bottom: 0; left: 0; right: 0;
      padding: 1.5rem; display: flex; justify-content: space-between;
      align-items: flex-end; z-index: 1;
    }
    .project-title {
      font-size: clamp(20px, 3vw, 30px); font-weight: 600;
      letter-spacing: -0.02em; transition: transform var(--transition);
    }
    .project-card:hover .project-title { transform: translateY(-4px); }
    .project-category {
      font-size: 13px; font-style: italic; letter-spacing: 0.04em;
      color: var(--accent); text-align: right;
    }
    .project-arrow {
      position: absolute; top: 1rem; right: 1rem; z-index: 2;
      width: 44px; height: 44px; border-radius: 50%;
      background: var(--accent); display: grid; place-items: center;
      opacity: 0; transform: translate(8px, -8px) scale(0.8);
      transition: all var(--transition);
    }
    .project-card:hover .project-arrow { opacity: 1; transform: none; }
    .project-arrow svg { width: 16px; fill: var(--bg); }

    /* ── About ── */
    .about-hero {
      display: grid; grid-template-columns: 380px 1fr; gap: 4rem;
      align-items: start; padding-top: 3rem;
    }
    @media (max-width: 809px) { .about-hero { grid-template-columns: 1fr; } }

    .about-photo {
      position: relative; border-radius: 11px; overflow: hidden;
      aspect-ratio: 3/4; box-shadow: 0 40px 80px rgba(0,0,0,0.45);
      transform-style: preserve-3d;
    }
    .about-photo img { width: 100%; height: 100%; object-fit: cover; }
    .about-photo::before {
      content: ""; position: absolute; inset: 0; z-index: 1;
      background: linear-gradient(135deg, rgba(240,184,200,0.12) 0%, transparent 60%);
    }
    .about-photo-label {
      position: absolute; bottom: 1.25rem; left: 1.25rem; z-index: 2;
      font-family: var(--font-display); font-size: 11px;
      letter-spacing: 0.2em; text-transform: uppercase; color: var(--accent);
    }

    .about-intro {
      font-size: clamp(22px, 3vw, 32px); line-height: 1.5;
      color: var(--text-soft); margin-bottom: 3rem;
    }
    .about-intro em { font-style: italic; color: var(--accent); }

    .timeline { display: flex; flex-direction: column; gap: 0; margin-bottom: 3rem; }
    .timeline-label {
      font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
      color: var(--muted); margin-bottom: 1rem;
    }
    .timeline-item {
      display: grid; grid-template-columns: 1fr auto; gap: 1rem;
      padding: 1.25rem 0; border-bottom: 1px solid var(--accent-10);
      transition: all var(--transition); cursor: default;
    }
    .timeline-item:hover { padding-left: 0.75rem; color: var(--accent); }
    .timeline-item .role { font-weight: 600; font-size: 16px; }
    .timeline-item .company { font-style: italic; color: var(--muted); font-size: 14px; }
    .timeline-item:hover .company { color: var(--accent-40); }
    .timeline-item .year {
      font-size: 12px; letter-spacing: 0.08em; color: var(--muted);
      align-self: center;
    }

    .skills-cloud { display: flex; flex-wrap: wrap; gap: 0.75rem; }
    .skill-tag {
      padding: 0.5rem 1rem; border-radius: 100px;
      font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;
      border: 1px solid var(--accent-10); color: var(--muted);
      transition: all var(--transition); cursor: default;
    }
    .skill-tag:hover {
      border-color: var(--accent); color: var(--accent);
      background: var(--accent-10); transform: translateY(-3px);
      box-shadow: 0 8px 24px rgba(240,184,200,0.12);
    }

    /* ── Writing ── */
    .writing-item {
      display: grid; grid-template-columns: 1fr auto; gap: 1rem;
      padding: 2.5rem 0; border-bottom: 1px solid var(--accent-10);
      position: relative; transition: color var(--transition);
    }
    .writing-item::before {
      content: ""; position: absolute; bottom: 0; left: 0;
      width: 0; height: 1px; background: var(--accent);
      transition: width 0.6s var(--ease);
    }
    .writing-item:hover::before { width: 100%; }
    .writing-item:hover { color: var(--accent); }
    .writing-item h3 { font-size: 22px; font-weight: 600; margin-bottom: 0.5rem; }
    .writing-item p { color: var(--muted); font-size: 16px; grid-column: 1; }
    .writing-publisher { font-size: 12px; color: var(--accent); letter-spacing: 0.06em; text-transform: uppercase; margin-top: 0.35rem; }

    /* ── Contact form ── */
    .contact-form { max-width: 520px; display: flex; flex-direction: column; gap: 1.25rem; margin-top: 2rem; }
    .form-field { display: flex; flex-direction: column; gap: 0.45rem; }
    .form-field label { font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-soft); font-weight: 600; }
    .form-field input, .form-field textarea {
      background: rgba(255,255,255,0.06); border: 1px solid var(--accent-40);
      border-radius: 8px; padding: 0.85rem 1rem; color: var(--text);
      font-family: var(--font-body); font-size: 16px; line-height: 1.5;
    }
    .form-field textarea { min-height: 140px; resize: vertical; }
    .form-field input::placeholder, .form-field textarea::placeholder { color: var(--muted); opacity: 1; }
    .form-submit {
      align-self: flex-start; padding: 0.9rem 1.75rem; border-radius: 100px;
      border: none; background: var(--accent); color: var(--bg);
      font-family: var(--font-body); font-size: 13px; font-weight: 600;
      letter-spacing: 0.1em; text-transform: uppercase; cursor: pointer;
      transition: transform var(--transition), box-shadow var(--transition);
    }
    .form-submit:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(240,184,200,0.25); }
    .flash { padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1.5rem; font-size: 15px; }
    .flash-success { background: var(--accent-10); border: 1px solid var(--accent-40); color: var(--text-soft); }
    .flash-error { background: rgba(255,100,100,0.12); border: 1px solid rgba(255,120,120,0.4); color: #ffd4d4; }

    /* ── Blog ── */
    .blog-body { max-width: 680px; color: var(--text-soft); font-size: 18px; line-height: 1.75; }
    .blog-body p { margin-bottom: 1.25rem; }
    .project-story-hero {
      max-width: 900px; margin-bottom: 2.5rem; border-radius: 11px; overflow: hidden;
      box-shadow: 0 30px 80px rgba(0,0,0,0.35);
    }
    .project-story-hero img { width: 100%; display: block; aspect-ratio: 16/10; object-fit: cover; }
    .compose-form { max-width: 640px; margin-top: 2rem; }

    /* ── Whimsy / more of me ── */
    .whimsy-section {
      margin-top: 5rem; padding-top: 4rem;
      border-top: 1px solid var(--accent-10);
    }
    .whimsy-intro {
      color: var(--muted); font-size: 16px; font-style: italic;
      max-width: 480px; margin-bottom: 2.5rem;
    }
    .whimsy-grid {
      display: flex; flex-wrap: wrap; gap: 1rem;
    }
    .whimsy-card {
      flex: 1 1 200px; max-width: 280px;
      padding: 1.25rem 1.35rem; border-radius: 11px;
      background: var(--accent-10); border: 1px solid var(--accent-10);
      transition: transform 0.45s var(--ease), border-color var(--transition), box-shadow var(--transition);
      cursor: default;
    }
    .whimsy-card:nth-child(3n+1) { transform: rotate(-1.2deg); }
    .whimsy-card:nth-child(3n+2) { transform: rotate(0.8deg); }
    .whimsy-card:nth-child(3n)   { transform: rotate(-0.5deg); }
    .whimsy-card:hover {
      transform: rotate(0deg) translateY(-6px) scale(1.02);
      border-color: var(--accent-40);
      box-shadow: 0 16px 40px rgba(240,184,200,0.12);
    }
    .whimsy-ascii {
      font-family: "Cascadia Code", "Consolas", "Segoe UI Emoji", monospace;
      font-size: 14px; line-height: 1.2; color: var(--accent);
      margin-bottom: 0.65rem; white-space: pre; user-select: none;
    }
    .whimsy-label {
      font-size: 15px; font-weight: 600; letter-spacing: -0.01em;
      color: var(--text-soft); margin-bottom: 0.35rem;
      text-transform: lowercase;
    }
    .whimsy-detail {
      font-size: 13px; color: var(--muted); font-style: italic; line-height: 1.45;
    }
    .ascii-gallery {
      display: flex; flex-wrap: wrap; gap: 2.5rem; justify-content: center;
      align-items: flex-end; margin-top: 3.5rem; padding: 2rem 1rem;
      border-top: 1px dashed var(--accent-10);
    }
    .ascii-art {
      font-family: "Cascadia Code", "Consolas", "Segoe UI Emoji", monospace;
      font-size: clamp(9px, 1.1vw, 12px); line-height: 1.15;
      color: var(--accent-40); white-space: pre; margin: 0;
      transition: color 0.5s var(--ease), transform 0.5s var(--ease);
      user-select: none;
    }
    .ascii-art:hover { color: var(--accent); transform: translateY(-4px); }
    .ascii-art:nth-child(1) { animation: float 7s var(--ease) infinite; }
    .ascii-art:nth-child(2) { animation: float 5s var(--ease) infinite -1s; font-size: clamp(12px, 1.4vw, 16px); }
    .ascii-art:nth-child(3) { animation: float 6s var(--ease) infinite -2s; }
    .writing-item .date {
      font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase;
      color: var(--muted); font-style: italic;
    }

    /* ── Contact block ── */
    .contact-block {
      margin-top: 6rem; padding: 4rem 0 0;
      border-top: 1px solid var(--accent-10); position: relative;
    }
    .contact-label {
      font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase;
      color: var(--accent); margin-bottom: 1.5rem;
    }
    .contact-headline-row {
      display: flex; align-items: flex-end; justify-content: space-between;
      flex-wrap: wrap; gap: 1rem; margin-bottom: 2rem;
    }
    .contact-headline {
      font-family: var(--font-display); font-size: clamp(28px, 5vw, 40px);
      text-transform: lowercase;
    }
    .contact-headline em { font-family: var(--font-body); font-style: italic; color: var(--accent); }
    .contact-num {
      font-family: var(--font-display);
      font-size: clamp(80px, 18vw, 200px); line-height: 0.85;
      color: var(--accent-10); user-select: none;
      animation: float 6s var(--ease) infinite;
    }
    .contact-num.cute {
      font-family: var(--font-body); font-size: clamp(36px, 8vw, 72px);
      color: var(--accent-40); letter-spacing: 0.02em;
    }
    .about-location {
      font-size: 13px; letter-spacing: 0.1em; text-transform: uppercase;
      color: var(--muted); margin-bottom: 1.5rem; font-style: italic;
    }
    .award-item {
      font-size: 14px; line-height: 1.5; color: var(--muted);
      padding: 0.65rem 0; border-bottom: 1px solid var(--accent-10);
      transition: color var(--transition), padding-left var(--transition);
    }
    .award-item:hover { color: var(--accent); padding-left: 0.5rem; }
    .contact-body { max-width: 420px; color: var(--muted); margin-bottom: 2.5rem; }

    .btn-cta {
      display: inline-flex; align-items: center; gap: 1rem;
      font-size: 12px; letter-spacing: 0.1em; text-transform: uppercase;
      transition: color var(--transition);
    }
    .btn-cta:hover { color: var(--accent); }
    .btn-arrow {
      width: 52px; height: 52px; border-radius: 50%;
      background: var(--accent); display: grid; place-items: center;
      transition: transform 0.5s var(--ease), box-shadow var(--transition);
    }
    .btn-cta:hover .btn-arrow {
      transform: translate(6px, -6px) rotate(-45deg);
      box-shadow: -4px 4px 0 var(--accent-40);
    }
    .btn-arrow svg { width: 18px; stroke: var(--bg); stroke-width: 2; fill: none; }

    /* ── Footer ── */
    .site-footer {
      border-top: 1px solid var(--accent-10); padding: 2rem 0;
      position: relative; z-index: 2;
    }
    .footer-inner { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
    .social-ticker { display: flex; gap: 2rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
    .social-link {
      font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase;
      transition: color var(--transition), letter-spacing var(--transition);
    }
    .social-link:hover { color: var(--accent); letter-spacing: 0.14em; }
    .copyright { font-size: 13px; color: var(--accent-40); }

    /* ── Custom cursor glow ── */
    .cursor-glow {
      position: fixed; width: 300px; height: 300px;
      border-radius: 50%; pointer-events: none; z-index: 9999;
      background: radial-gradient(circle, rgba(240,184,200,0.06) 0%, transparent 70%);
      transform: translate(-50%, -50%);
      transition: opacity 0.3s; opacity: 0;
    }
    body:hover .cursor-glow { opacity: 1; }
  </style>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
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
      <ul class="nav-links" aria-label="Main navigation">
        {% for link in nav %}
          <li><a href="{{ link.href }}" class="nav-link{% if active == link.label %} active{% endif %}">{{ link.label }}</a></li>
        {% endfor %}
      </ul>
    </div>
  </header>

  <main class="page" id="main-content">
    {% block content %}{% endblock %}
    {% if show_contact %}
    <section class="contact-block reveal">
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
          {% if not loop.last %}<span style="color:var(--accent-40)"> / </span>{% endif %}
        {% endfor %}
      </div>
      <p class="copyright">{{ meta.copyright }}</p>
    </div>
  </footer>

  <script>
    // Scroll reveal with stagger
    const reveals = document.querySelectorAll('.reveal, .reveal-scale');
    const observer = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
    }, { threshold: 0.1 });
    reveals.forEach((el, i) => {
      el.style.transitionDelay = (el.dataset.delay || (i * 0.07)) + 's';
      observer.observe(el);
      // Show elements already on screen (fixes invisible sections on load)
      const r = el.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.92) el.classList.add('visible');
    });

    // Cursor glow follow
    const glow = document.getElementById('cursorGlow');
    document.addEventListener('mousemove', e => {
      glow.style.left = e.clientX + 'px';
      glow.style.top  = e.clientY + 'px';
    });

    // 3D tilt — hero portrait
    document.querySelectorAll('[data-tilt]').forEach(el => {
      el.addEventListener('mousemove', e => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width  - 0.5;
        const y = (e.clientY - r.top)  / r.height - 0.5;
        el.style.transform = `perspective(800px) rotateX(${-y*12}deg) rotateY(${x*12}deg) scale3d(1.02,1.02,1.02)`;
      });
      el.addEventListener('mouseleave', () => { el.style.transform = ''; });
    });

    // 3D tilt — project cards
    document.querySelectorAll('.project-card').forEach(card => {
      const inner = card.querySelector('.project-card-inner');
      card.addEventListener('mousemove', e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width  - 0.5;
        const y = (e.clientY - r.top)  / r.height - 0.5;
        inner.style.transform = `rotateX(${-y*10}deg) rotateY(${x*10}deg)`;
      });
      card.addEventListener('mouseleave', () => { inner.style.transform = ''; });
    });

    // Magnetic buttons
    document.querySelectorAll('.magnetic, .btn-pill').forEach(btn => {
      btn.addEventListener('mousemove', e => {
        const r = btn.getBoundingClientRect();
        const x = e.clientX - r.left - r.width/2;
        const y = e.clientY - r.top  - r.height/2;
        btn.style.transform = `translate(${x*0.15}px, ${y*0.15}px)`;
      });
      btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
    });

    // Parallax floating shapes on scroll
    const shapes = document.querySelectorAll('.float-shape, .float-cross');
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      shapes.forEach((s, i) => {
        s.style.transform = `translateY(${y * (0.04 + i * 0.02)}px)`;
      });
    }, { passive: true });
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
  <div class="hero-visual reveal-scale" data-delay="0.15">
    <div class="hero-circle" aria-hidden="true"></div>
    <div class="hero-portrait-wrap" data-tilt>
      <img src="{{ hero.portrait }}" alt="{{ meta.name }}">
      <span class="hero-badge">{{ meta.title }}</span>
    </div>
  </div>
</section>

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
  {% if p.card_href %}
  <a href="{{ p.card_href }}" class="project-card reveal" data-delay="{{ loop.index0 * 0.1 }}"{% if p.card_external %} target="_blank" rel="noopener noreferrer"{% endif %}>
  {% else %}
  <div class="project-card reveal" data-delay="{{ loop.index0 * 0.1 }}">
  {% endif %}
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
  {% if p.card_href %}</a>{% else %}</div>{% endif %}
  {% endfor %}
</div>

<section class="whimsy-section" id="more-of-me">
  <div class="section-head reveal visible" style="border-top:none;padding-top:0;margin-bottom:2rem;">
    <h2 class="page-title">a lil bit more of <em>me</em></h2>
  </div>
  <p class="whimsy-intro reveal visible">{{ more_of_me.intro }}</p>
  <div class="whimsy-grid">
    {% for item in more_of_me.bits %}
    <div class="whimsy-card reveal" data-delay="{{ loop.index0 * 0.06 }}">
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
<h1 class="page-title reveal" style="padding-top:3rem;margin-bottom:3rem;">my <em>work</em></h1>
<div class="work-grid">
  {% for p in projects %}
  {% if p.card_href %}
  <a href="{{ p.card_href }}" class="project-card reveal" data-delay="{{ loop.index0 * 0.08 }}"{% if p.card_external %} target="_blank" rel="noopener noreferrer"{% endif %}>
  {% else %}
  <div class="project-card reveal" data-delay="{{ loop.index0 * 0.08 }}">
  {% endif %}
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
  {% if p.card_href %}</a>{% else %}</div>{% endif %}
  {% endfor %}
</div>
{% endblock %}
"""

PROJECT_PAGE = r"""{% extends "base.html" %}
{% block content %}
<article class="reveal visible" style="padding-top:3rem;">
  <p class="about-location">{{ project.category }}</p>
  <h1 class="page-title" style="margin-bottom:2rem;">{{ project.title }}</h1>
  <div class="project-story-hero reveal visible">
    <img src="{{ project.image }}" alt="{{ project.title }}" loading="lazy">
  </div>
  <div class="blog-body">
    {% for para in project.story_paragraphs %}
    <p>{{ para }}</p>
    {% endfor %}
  </div>
  {% if project.href and project.href != '#' %}
  <p style="margin-top:2rem;">
    <a href="{{ project.href }}" class="btn-pill magnetic" target="_blank" rel="noopener noreferrer"><span>view project link</span></a>
  </p>
  {% endif %}
  <p style="margin-top:3rem;"><a href="/work" class="section-link">back to work</a></p>
</article>
{% endblock %}
"""

ABOUT_PAGE = r"""{% extends "base.html" %}
{% block content %}
<div class="about-hero">
  <div class="about-photo reveal-scale" data-tilt>
    <img src="{{ about.portrait }}" alt="{{ meta.name }}">
    <span class="about-photo-label">{{ meta.title }}</span>
  </div>
  <div>
    <h1 class="page-title reveal" style="margin-bottom:1rem;">about <em>me</em></h1>
    <p class="about-location reveal">{{ about.location }}</p>
    <p class="about-intro reveal">{{ about.intro | safe_em }}</p>

    <p class="timeline-label reveal">skills</p>
    <div class="skills-cloud reveal" style="margin-bottom:3rem;">
      {% for skill in about.skills %}
        <span class="skill-tag">{{ skill }}</span>
      {% endfor %}
    </div>

    <p class="timeline-label reveal">honors & awards</p>
    <div class="reveal" style="margin-bottom:3rem;">
      {% for award in about.awards %}
        <div class="award-item">{{ award }}</div>
      {% endfor %}
    </div>

    <p class="timeline-label reveal">languages</p>
    <div class="skills-cloud reveal" style="margin-bottom:3rem;">
      {% for lang in about.languages %}
        <span class="skill-tag">{{ lang }}</span>
      {% endfor %}
    </div>

    <p class="timeline-label reveal">certifications</p>
    <div class="timeline reveal" style="margin-bottom:3rem;">
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
    <div class="timeline reveal">
      {% for job in about.experience %}
      <div class="timeline-item">
        <div>
          <div class="role">{{ job.role }}</div>
          <div class="company">
            {% if job.get('link') %}
              <a href="{{ job.link }}" target="_blank" rel="noopener noreferrer">{{ job.company }}</a>
            {% else %}
              {{ job.company }}
            {% endif %}
          </div>
        </div>
        <span class="year">{{ job.year }}</span>
      </div>
      {% endfor %}
    </div>

    <p class="timeline-label reveal">education</p>
    <div class="timeline reveal">
      {% for edu in about.education %}
      <div class="timeline-item">
        <div>
          <div class="role">{{ edu.degree }}</div>
          <div class="company">{{ edu.school }}</div>
        </div>
        {% if edu.year %}<span class="year">{{ edu.year }}</span>{% endif %}
      </div>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
"""

WRITING_PAGE = r"""{% extends "base.html" %}
{% block content %}
<h1 class="page-title reveal" style="padding-top:3rem;margin-bottom:2rem;">my <em>writing</em></h1>
<div>
  {% for post in writing %}
  {% if post.href %}
  <a href="{{ post.href }}" class="writing-item reveal" data-delay="{{ loop.index0 * 0.1 }}" target="_blank" rel="noopener noreferrer">
  {% else %}
  <article class="writing-item reveal" data-delay="{{ loop.index0 * 0.1 }}" style="cursor:default;">
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
<h1 class="page-title reveal" style="padding-top:3rem;margin-bottom:2rem;">life <em>blog</em></h1>
<p class="about-location reveal" style="margin-bottom:2.5rem;">thoughts, experiments, and whatever I'm up to</p>
<div>
  {% for post in blogs %}
  <a href="/blog/{{ post.slug }}" class="writing-item reveal" data-delay="{{ loop.index0 * 0.1 }}">
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
<p class="reveal" style="margin-top:3rem;">
  <a href="/compose" class="btn-pill"><span>write a new post</span></a>
</p>
{% endblock %}
"""

BLOG_POST_PAGE = r"""{% extends "base.html" %}
{% block content %}
<article class="reveal visible" style="padding-top:3rem;">
  <p class="about-location">{{ post.date }}</p>
  <h1 class="page-title" style="margin-bottom:2rem;">{{ post.title }}</h1>
  <div class="blog-body">
    {% for para in post.body_paragraphs %}
    <p>{{ para }}</p>
    {% endfor %}
  </div>
  <p style="margin-top:3rem;"><a href="/blog" class="section-link">back to blog</a></p>
</article>
{% endblock %}
"""

COMPOSE_PAGE = r"""{% extends "base.html" %}
{% block content %}
<h1 class="page-title reveal" style="padding-top:3rem;margin-bottom:1rem;">write a <em>post</em></h1>
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
<h1 class="page-title reveal" style="padding-top:3rem;margin-bottom:1rem;">say <em>hi</em> ♡</h1>
<p class="about-location reveal" style="margin-bottom:2rem;">plano, texas / ryu_kiara on discord</p>

{% if flash_msg %}
<p class="flash flash-{{ flash_type }}" role="status">{{ flash_msg }}</p>
{% endif %}

<section class="reveal visible">
  <p class="contact-body" style="font-size:20px;max-width:560px;margin-bottom:1rem;">{{ contact.body }}</p>

  <form method="post" action="/contact/send" class="contact-form" aria-label="Send a message">
    <div class="form-field">
      <label for="name">Your name</label>
      <input type="text" id="name" name="name" required maxlength="120" autocomplete="name" placeholder="Who are you?">
    </div>
    <div class="form-field">
      <label for="email">Your email</label>
      <input type="email" id="email" name="email" required maxlength="200" autocomplete="email" placeholder="you@example.com">
    </div>
    <div class="form-field">
      <label for="message">Message</label>
      <textarea id="message" name="message" required maxlength="5000" placeholder="Say hello, pitch an idea, or just vibe..."></textarea>
    </div>
    <button type="submit" class="form-submit">Send message</button>
  </form>

  <p style="margin-top:2.5rem;color:var(--muted);font-style:italic;">or email me directly: {{ meta.email }}</p>
  <div class="ascii-gallery" style="margin-top:2rem;border-top:none;padding-top:0;" aria-hidden="true">
    <pre class="ascii-art">  ∧,,,∧
(  ̳• · • ̳)
/    づ♡</pre>
    <pre class="ascii-art">                へ  ♡
         ૮  >  <)
          /  ⁻  ៸|
     乀(ˍ, ل ل</pre>
  </div>
</section>
{% endblock %}
"""


def load_blogs() -> list[dict]:
    if not BLOGS_FILE.exists():
        return []
    return json.loads(BLOGS_FILE.read_text(encoding="utf-8"))


def save_blogs(blogs: list[dict]) -> None:
    BLOGS_FILE.write_text(
        json.dumps(blogs, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "post"


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


def save_message(name: str, email: str, message: str) -> None:
    messages = []
    if MESSAGES_FILE.exists():
        messages = json.loads(MESSAGES_FILE.read_text(encoding="utf-8"))
    messages.append({
        "name": name,
        "email": email,
        "message": message,
        "at": datetime.now(timezone.utc).isoformat(),
    })
    MESSAGES_FILE.write_text(
        json.dumps(messages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def safe_em_filter(text: str) -> Markup:
    """Render trusted <em> tags in content; escape everything else."""
    import re

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
    }),
    autoescape=select_autoescape(["html"]),
)
_jinja.filters["safe_em"] = safe_em_filter


def _ctx(*, active: str, page_title: str, show_contact: bool = True, **extra) -> dict:
    ctx = {
        "active": active,
        "page_title": page_title,
        "show_contact": show_contact,
        "meta": CONTENT["meta"],
        "hero": CONTENT["hero"],
        "nav": CONTENT["nav"],
        "ticker": CONTENT["ticker"],
        "social": CONTENT["social"],
        "contact": CONTENT["contact"],
        "about": CONTENT["about"],
        "projects": enrich_projects(CONTENT["projects"]),
        "writing": CONTENT["writing"],
        "more_of_me": CONTENT["more_of_me"],
        "blogs": load_blogs(),
        "theme": THEME,
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


@app.route("/contact")
def contact():
    return render_page("contact.html", active="CONTACT", page_title="Contact", show_contact=False)


@app.route("/contact/send", methods=["POST"])
def contact_send():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    message = (request.form.get("message") or "").strip()
    if not name or not email or not message:
        session["flash_msg"] = "Please fill in all fields."
        session["flash_type"] = "error"
        return redirect(url_for("contact"))
    try:
        save_message(name, email, message)
        session["flash_msg"] = "Message sent! I'll get back to you soon."
        session["flash_type"] = "success"
    except OSError:
        session["flash_msg"] = "Could not save your message. Try emailing me directly."
        session["flash_type"] = "error"
    return redirect(url_for("contact"))


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
    app.run(debug=True, port=5000)
