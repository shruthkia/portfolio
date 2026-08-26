#!/usr/bin/env python3
"""Route and blog-persistence checks for the portfolio app."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("PORTFOLIO_SECRET", "test-secret")

from portfolio import (  # noqa: E402
    COMPOSE_PASSWORD,
    app,
    blogs_path,
    load_blogs,
    save_blogs,
)


ROUTES = [
    "/",
    "/about",
    "/work",
    "/work/adopurr",
    "/work/arkire",
    "/work/lt-fccla",
    "/work/launchpoint",
    "/work/fccla-nationals",
    "/work/fccla-sustainability",
    "/work/selfcad-champ",
    "/work/dreamyuni",
    "/work/microbit-automizer",
    "/ism",
    "/research/1",
    "/mentor",
    "/brain",
    "/blog",
    "/writing",
    "/contact",
    "/compose",
]


def assert_ok(resp, path: str) -> None:
    assert resp.status_code == 200, f"{path} -> {resp.status_code}"
    body = resp.get_data(as_text=True)
    assert "Shruthika" in body
    assert "\u2014" not in body, f"em dash leaked on {path}"
    assert "Automizer" not in body
    assert "NATS" not in body


def test_routes() -> None:
    client = app.test_client()
    for path in ROUTES:
        assert_ok(client.get(path), path)
    home = client.get("/").get_data(as_text=True)
    assert "who am" in home
    assert "i don't know" in home
    assert "i love animals" in home
    assert "please don't quiz me" not in home
    assert "/static/ghibli-me-cat.png" in home
    assert "hero-cta-only" in home
    assert "hero-portrait-wrap" not in home
    assert home.count("/static/ghibli-me-cat.png") == 1
    assert "hero-intro" not in home or "I do a little bit of everything, designing" not in home
    assert "love a leaf" in home.lower()
    assert "beautiful to love the ordinary" in home.lower()
    assert "S.C. Lourie" in home
    assert "John A. Shedd" not in home
    assert "beautiful to love the common" not in home.lower()
    assert "RESEARCH" in home
    assert "Research 1" in home
    assert "MENTOR" in home
    css = (ROOT / "static" / "site.css").read_text(encoding="utf-8")
    assert "paw-cursor" not in css
    # Classic tall sticky who-am-i scroll theater (pre-blank-cleanup curves)
    assert "min-height: 220vh" in css
    assert "top: 16vh" in css
    assert "min-height: 68vh" in css
    assert "--who-p" in css
    assert "position: sticky" in css
    assert "(var(--who-p) - 0.18)" in css
    assert "(var(--who-p) - 0.42)" in css
    assert "(var(--who-p) - 0.68)" in css
    whoami_block = css[css.find(".whoami-cutout") : css.find(".whoami-line")]
    assert "opacity: clamp(0, calc((var(--who-p) - 0.18) * 4.5), 1)" in whoami_block
    base = (ROOT / "portfolio.py").read_text(encoding="utf-8")
    assert 'setProperty("--who-p"' in base
    assert "prefers-reduced-motion" in base
    assert not (ROOT / "static" / "paw-cursor.png").exists()
    assert not (ROOT / "static" / "paw-cursor-32.png").exists()
    assert (ROOT / "static" / "ghibli-me-cat.png").exists()
    # Transparent cutout (near-white backdrop removed)
    from PIL import Image
    whoami_img = Image.open(ROOT / "static" / "ghibli-me-cat.png")
    assert whoami_img.mode == "RGBA"
    assert whoami_img.getpixel((0, 0))[3] == 0
    assert whoami_img.getpixel((whoami_img.size[0] // 2, whoami_img.size[1] // 2))[3] > 0
    assert (ROOT / "static" / "mentor-unknown.png").exists()
    ism = client.get("/ism").get_data(as_text=True)
    assert "S.C. Lourie" in ism
    assert "love a leaf" in ism.lower()
    brain = client.get("/brain").get_data(as_text=True)
    assert "S.C. Lourie" in brain
    assert "love a leaf" in brain.lower()
    assert "BRAINDUMP" in brain
    assert "welcome to my" in brain
    assert "my braindump" in brain.lower()
    assert "/static/brain/center.jpg" in brain
    assert "/static/brain/polaroid-me.jpg" in brain
    assert "fragile" not in brain.lower()
    assert "fragile.png" not in brain
    assert "brain-scatter" in brain
    assert "brain-deco-row" not in brain
    assert "brain-photo-decos" not in brain
    assert "/static/brain/shell.png" in brain
    assert "/static/brain/earbuds.png" in brain
    assert "/static/brain/coffee.png" in brain
    research = client.get("/research/1").get_data(as_text=True)
    assert "re-sheltering" in research.lower() or "resheltering" in research.lower() or "re-sheltering" in research
    assert "A Cat" in research
    assert "Paul Koudounaris" in research
    assert "Rethinking Rescue" in research
    assert "Carol Mithers" in research
    assert "Dogs Demystified" in research
    assert "Total Cat Mojo" in research
    assert "Jackson Galaxy" in research
    assert "Year of the Puppy" in research
    assert "Alexandra Horowitz" in research
    mentor = client.get("/mentor").get_data(as_text=True)
    assert "mentor" in mentor.lower()
    assert "/static/mentor-unknown.png" in mentor
    assert "/contact" in mentor
    assert "looking" in mentor.lower() or "wanted" in mentor.lower()
    contact = client.get("/contact").get_data(as_text=True)
    assert 'action="/contact/send"' in contact
    assert "id=\"contact-form\"" in contact
    work = client.get("/work/microbit-automizer").get_data(as_text=True)
    assert "AUTOMAZER" in work
    assert "lambjam" in client.get("/work").get_data(as_text=True) or "Finch" in work
    nationals = client.get("/work/fccla-nationals").get_data(as_text=True)
    assert "fccla-nationals.jpg" in nationals
    assert "NATS" not in nationals
    old = client.get("/work/fccla-nats", follow_redirects=False)
    assert old.status_code in (301, 302)
    about = client.get("/about").get_data(as_text=True)
    assert "Mahatma" not in about
    assert "DFW Startup Week" in about
    assert "/static/about.jpg" in about


def test_contact_saves_message() -> None:
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        store = Path(tmp) / "messages.json"
        os.environ["MESSAGES_FILE"] = str(store)
        client = app.test_client()
        resp = client.post(
            "/contact/send",
            data={
                "name": "Test Friend",
                "email": "friend@example.com",
                "channel": "personal",
                "message": "hello from the test suite",
            },
            headers={"X-Requested-With": "fetch"},
        )
        assert resp.status_code == 200
        payload = resp.get_json()
        assert payload["ok"] is True
        assert store.exists()
        saved = json.loads(store.read_text(encoding="utf-8"))
        assert saved[-1]["name"] == "Test Friend"
        assert "mailto:" in payload["mailto"]
        os.environ.pop("MESSAGES_FILE", None)


def test_compose_and_restart_persistence() -> None:
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        store = Path(tmp) / "blogs.json"
        os.environ["BLOGS_FILE"] = str(store)
        save_blogs([])
        client = app.test_client()
        unlock = client.post("/compose", data={"password": COMPOSE_PASSWORD}, follow_redirects=True)
        assert unlock.status_code == 200
        published = client.post(
            "/compose",
            data={
                "action": "publish",
                "title": "persistence check",
                "excerpt": "does this stay",
                "body": "if you can read this after restart, persistence works.",
            },
            follow_redirects=False,
        )
        assert published.status_code in {302, 303}
        assert store.exists(), "compose did not write blogs.json"
        payload = json.loads(store.read_text(encoding="utf-8"))
        assert len(payload) == 1, payload
        assert payload[0]["slug"] == "persistence-check"
        assert "persistence check" in client.get("/blog").get_data(as_text=True)

        env = os.environ.copy()
        env["BLOGS_FILE"] = str(store)
        env["PORTFOLIO_SECRET"] = "test-secret"
        script = (
            "import os,sys; sys.path.insert(0, os.environ['ROOT']); "
            "from portfolio import app; "
            "c=app.test_client(); "
            "html=c.get('/blog').get_data(as_text=True); "
            "assert 'persistence check' in html, html[:500]; "
            "print('restart-ok')"
        )
        proc = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(ROOT),
            env={**env, "ROOT": str(ROOT)},
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "restart-ok" in proc.stdout

        # default next-to-app file still loads independently
        os.environ.pop("BLOGS_FILE", None)
        assert any(p.get("slug") == "hello-world" for p in load_blogs())


if __name__ == "__main__":
    test_routes()
    test_contact_saves_message()
    test_compose_and_restart_persistence()
    print("all checks passed")
    print("blogs_path default:", blogs_path())
