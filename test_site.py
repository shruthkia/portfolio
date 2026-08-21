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
    assert "please don't quiz me" in home
    assert "full of love, hustle" not in home
    brain = client.get("/brain").get_data(as_text=True)
    assert "BRAINDUMP" in brain
    assert "welcome to my" in brain
    assert "my braindump" in brain.lower()
    assert "/static/brain/center.jpg" in brain
    assert "/static/brain/polaroid-me.jpg" in brain
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
    test_compose_and_restart_persistence()
    print("all checks passed")
    print("blogs_path default:", blogs_path())
