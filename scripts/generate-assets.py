#!/usr/bin/env python3
"""Generate realistic placeholder assets for the Shockwaves FTC portfolio."""

from __future__ import annotations

import math
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
REFS = Path("/cursor/stores/self/internal/refs")
OUT = ASSETS


def font(size: int, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]
        if mono
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def panel(w: int, h: int, title: str, subtitle: str = "", accent=(59, 130, 246)) -> Image.Image:
    img = Image.new("RGB", (w, h), (15, 20, 32))
    d = ImageDraw.Draw(img)
    # grid
    for x in range(0, w, 24):
        d.line([(x, 0), (x, h)], fill=(20, 28, 42), width=1)
    for y in range(0, h, 24):
        d.line([(0, y), (w, y)], fill=(20, 28, 42), width=1)
    # frame
    d.rectangle([1, 1, w - 2, h - 2], outline=accent, width=2)
    # corner brackets
    b = 18
    for x0, y0, dx, dy in ((4, 4, 1, 1), (w - 5, 4, -1, 1), (4, h - 5, 1, -1), (w - 5, h - 5, -1, -1)):
        d.line([(x0, y0), (x0 + dx * b, y0)], fill=accent, width=2)
        d.line([(x0, y0), (x0, y0 + dy * b)], fill=accent, width=2)
    # center label
    f1 = font(max(16, w // 28), mono=True)
    f2 = font(max(12, w // 40), mono=True)
    tw = d.textlength(title, font=f1)
    d.text(((w - tw) / 2, h / 2 - 18), title, fill=(248, 250, 252), font=f1)
    if subtitle:
        sw = d.textlength(subtitle, font=f2)
        d.text(((w - sw) / 2, h / 2 + 10), subtitle, fill=(56, 189, 248), font=f2)
    # deco isometric box
    cx, cy = w // 2, h // 2 + 70
    pts = [(cx, cy - 28), (cx + 48, cy - 10), (cx, cy + 8), (cx - 48, cy - 10)]
    d.polygon(pts, outline=(56, 189, 248))
    return img


def chart(w: int, h: int, title: str, values: list[float], labels: list[str]) -> Image.Image:
    img = Image.new("RGB", (w, h), (15, 20, 32))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(59, 130, 246), width=1)
    d.text((16, 12), title, fill=(248, 250, 252), font=font(18, True))
    pad_l, pad_r, pad_t, pad_b = 48, 20, 48, 36
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b
    mx = max(values) * 1.15 or 1
    # axes
    d.line([(pad_l, pad_t), (pad_l, pad_t + plot_h), (pad_l + plot_w, pad_t + plot_h)], fill=(100, 116, 139), width=1)
    bw = plot_w / max(len(values), 1) * 0.62
    gap = plot_w / max(len(values), 1)
    for i, (v, lab) in enumerate(zip(values, labels)):
        x = pad_l + gap * i + (gap - bw) / 2
        bh = (v / mx) * plot_h
        y = pad_t + plot_h - bh
        color = (52, 211, 153) if i == len(values) - 1 else (59, 130, 246)
        d.rectangle([x, y, x + bw, pad_t + plot_h], fill=color)
        lw = d.textlength(lab, font=font(11, True))
        d.text((x + bw / 2 - lw / 2, pad_t + plot_h + 8), lab, fill=(148, 163, 184), font=font(11, True))
        vw = d.textlength(str(int(v)), font=font(11, True))
        d.text((x + bw / 2 - vw / 2, y - 16), str(int(v)), fill=(248, 250, 252), font=font(11, True))
    return img


def timeline(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), (15, 20, 32))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(59, 130, 246), width=1)
    milestones = [
        ("KICKOFF", "V0 frame"),
        ("MEET 1", "intake V1"),
        ("MEET 2", "lift + transfer"),
        ("LEAGUE", "turret lock"),
        ("REGION", "cycle 4.8s"),
    ]
    y = h // 2
    d.line([(40, y), (w - 40, y)], fill=(56, 189, 248), width=2)
    for i, (m, sub) in enumerate(milestones):
        x = 40 + i * ((w - 80) / (len(milestones) - 1))
        d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=(59, 130, 246), outline=(248, 250, 252))
        tw = d.textlength(m, font=font(12, True))
        d.text((x - tw / 2, y - 36), m, fill=(248, 250, 252), font=font(12, True))
        sw = d.textlength(sub, font=font(11, True))
        d.text((x - sw / 2, y + 16), sub, fill=(52, 211, 153), font=font(11, True))
    return img


def wiring(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), (15, 20, 32))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(56, 189, 248), width=1)
    d.text((16, 12), "WIRING TOPOLOGY", fill=(248, 250, 252), font=font(16, True))
    boxes = [
        (40, 70, "CONTROL\nHUB"),
        (220, 70, "EXPANSION\nHUB"),
        (400, 70, "12V\nBATTERY"),
        (100, 200, "DRIVE\nx4"),
        (280, 200, "INTAKE\n+ LIFT"),
        (460, 200, "TURRET\n+ VISION"),
    ]
    for x, y, label in boxes:
        d.rectangle([x, y, x + 110, y + 56], outline=(59, 130, 246), width=1, fill=(22, 30, 48))
        for i, line in enumerate(label.split("\n")):
            tw = d.textlength(line, font=font(12, True))
            d.text((x + 55 - tw / 2, y + 12 + i * 16), line, fill=(248, 250, 252), font=font(12, True))
    for a, b in [((150, 126), (220, 98)), ((330, 98), (400, 98)), ((95, 126), (155, 200)), ((275, 126), (335, 200)), ((455, 126), (515, 200))]:
        d.line([a, b], fill=(245, 158, 11), width=2)
    return img


def field_paths(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), (15, 20, 32))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 1, w - 2, h - 2], outline=(59, 130, 246), width=1)
    # field square
    m = 36
    d.rectangle([m, m, w - m, h - m], outline=(71, 85, 105), width=2)
    # hive center
    cx, cy = w // 2, h // 2
    d.rectangle([cx - 40, cy - 18, cx + 40, cy + 18], outline=(245, 158, 11), width=2)
    d.text((cx - 18, cy - 8), "HIVE", fill=(245, 158, 11), font=font(12, True))
    # flowers
    for fx, fy in [(m + 30, m + 30), (w - m - 50, m + 30), (m + 30, h - m - 50), (w - m - 50, h - m - 50)]:
        d.ellipse([fx, fy, fx + 28, fy + 28], outline=(52, 211, 153), width=2)
        d.text((fx + 2, fy + 8), "FL", fill=(52, 211, 153), font=font(10, True))
    # path
    pts = [(m + 70, h - m - 40), (m + 120, h // 2), (cx - 50, cy), (w - m - 80, m + 80)]
    d.line(pts, fill=(56, 189, 248), width=3)
    d.text((16, 10), "AUTO PATHS · Pedro", fill=(248, 250, 252), font=font(14, True))
    return img


def save(img: Image.Image, name: str) -> None:
    path = OUT / name
    img.save(path)
    print("wrote", path, img.size)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # Cover CAD from portfolio-2 page 1 (exploded isometric)
    doc = fitz.open(str(REFS / "portfolio-2.pdf"))
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.2, 2.2))
    cover = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    # crop margins slightly for cleaner hero
    cover = cover.crop((40, 40, cover.width - 40, cover.height - 40))
    cover.save(OUT / "cover-cad.png")
    print("wrote cover-cad.png", cover.size)

    # Also keep purple CAD alt as robot-iso-alt
    purple = Image.open(REFS / "shockwaves-brand-banner.jpg").convert("RGB")
    purple.save(OUT / "cover-cad-alt.png")

    # Brand banner / logo (file named cover-cad-ref is actually brand banner)
    banner = Image.open(REFS / "cover-cad-ref.jpg").convert("RGB")
    banner.save(OUT / "brand-banner.png")
    # logo mark crop (left portion)
    mark = banner.crop((0, 0, 420, banner.height)).resize((256, 200), Image.Resampling.LANCZOS)
    mark.save(OUT / "logo-mark.png")
    # wide logo strip
    banner.resize((900, 152), Image.Resampling.LANCZOS).save(OUT / "logo-wide.png")

    specs = [
        ("team-photo.jpg", 1400, 780, "TEAM PHOTO", "Shockwaves 38213 · 2026–27"),
        ("org-structure.png", 1100, 320, "ORG STRUCTURE", "Build · Code · Outreach · Business"),
        ("budget-chart.png", 900, 420, "BUDGET SNAPSHOT", "Income · Cost · Rollover"),
        ("sponsor-wall.png", 1100, 280, "SPONSOR WALL", "Replace with logos"),
        ("goals-board.png", 1000, 480, "GOALS BOARD", "Season KPIs · Reflections"),
        ("outreach-tedx.jpg", 900, 520, "OUTREACH · TEDx", "Demo + talk"),
        ("outreach-stemcon.jpg", 900, 520, "OUTREACH · STEMCon", "Scrimmage host"),
        ("outreach-camp.jpg", 900, 520, "OUTREACH · CAMP", "Hands-on workshop"),
        ("outreach-map.png", 700, 420, "REACH MAP", "US · India · UAE · MY"),
        ("edp-diagram.png", 1100, 360, "EDP SEQUENCE", "Identify → Improve"),
        ("tradeoff-matrix.png", 900, 480, "TRADE-OFF MATRIX", "Mass · Cycle · Complexity"),
        ("robot-cad.png", 1000, 900, "ROBOT CAD ISO", "Onshape transparent PNG"),
        ("robot-iso.jpg", 900, 560, "ROBOT ISO PHOTO", "Field pose"),
        ("robot-top.jpg", 900, 560, "TOP VIEW", "CoM + packaging"),
        ("robot-side.jpg", 900, 560, "SIDE / LIFT", "Transfer stack"),
        ("com-diagram.png", 700, 420, "CENTER OF MASS", "Projected CoM mark"),
        ("wiring-diagram.png", 700, 420, "WIRING", "Hubs · runs · fuses"),
        ("chassis-cad.png", 900, 700, "CHASSIS CAD", "Parallel-plate 6061"),
        ("chassis-v1.jpg", 640, 400, "CHASSIS V1", "Kit channel"),
        ("chassis-v2.jpg", 640, 400, "CHASSIS V2", "First plates"),
        ("chassis-v3.jpg", 640, 400, "CHASSIS V3", "Current"),
        ("intake-cad.png", 900, 700, "INTAKE CAD", "POLLEN / NECTAR collector"),
        ("intake-v1.jpg", 640, 400, "INTAKE V1", "Stock wheels"),
        ("intake-v2.jpg", 640, 400, "INTAKE V2", "Silicone 30A"),
        ("intake-v3.jpg", 640, 400, "INTAKE V3", "Narrow throat"),
        ("lift-cad.png", 900, 700, "LIFT / TRANSFER CAD", "Vertical stage"),
        ("lift-v1.jpg", 640, 400, "LIFT V1", "Single stage"),
        ("lift-v2.jpg", 640, 400, "LIFT V2", "Cascading"),
        ("lift-v3.jpg", 640, 400, "LIFT V3", "Damped transfer"),
        ("turret-cad.png", 900, 700, "SCORING / TURRET CAD", "HIVE launch axis"),
        ("turret-v1.jpg", 640, 400, "TURRET V1", "Fixed hood"),
        ("turret-v2.jpg", 640, 400, "TURRET V2", "Belt drive"),
        ("turret-v3.jpg", 640, 400, "TURRET V3", "Vision lock"),
        ("auto-paths.png", 1000, 700, "AUTO PATHS", "Pedro · 3 routines"),
        ("auto-field.png", 900, 560, "FIELD OVERLAY", "HIVE · FLOWER tags"),
        ("teleop-hud.png", 1000, 560, "TELEOP HUD", "Cycle state machine"),
        ("vision-pipeline.png", 900, 560, "VISION PIPELINE", "AprilTag → turret"),
        ("telemetry-graph.png", 1000, 480, "TELEMETRY", "Cycle · pickup · tip"),
        ("cycle-sheet.png", 900, 420, "CYCLE SHEET", "Bench + field log"),
        ("test-bench.jpg", 900, 520, "TEST BENCH", "Instrumented runs"),
        ("season-timeline.png", 1100, 360, "SEASON TIMELINE", "Kickoff → Region"),
        ("score-arc.png", 900, 420, "SCORE ARC", "Meet averages"),
        ("season-summary.jpg", 1200, 640, "SEASON SUMMARY", "Team + robot"),
        ("next-year.png", 900, 360, "NEXT YEAR", "Commitments board"),
    ]

    accents = [
        (59, 130, 246),
        (56, 189, 248),
        (245, 158, 11),
        (52, 211, 153),
        (248, 113, 113),
    ]
    for i, (name, w, h, title, sub) in enumerate(specs):
        img = panel(w, h, title, sub, accents[i % len(accents)])
        if name.endswith(".jpg"):
            img.save(OUT / name, quality=88)
        else:
            img.save(OUT / name)
        print("wrote", name)

    # Overwrite a few with specialized graphics
    save(chart(1000, 480, "SCORE ARC · MEET AVERAGES", [62, 128, 186, 241, 268], ["M1", "M2", "M3", "LG", "RG"]), "score-arc.png")
    save(chart(1000, 480, "TELEMETRY · CYCLE TIME (s)", [7.4, 6.1, 5.4, 4.9, 4.8], ["V1", "V2", "V3", "V4", "NOW"]), "telemetry-graph.png")
    save(chart(900, 420, "BUDGET · CATEGORIES ($k)", [4.2, 3.1, 1.8, 0.9, 1.2], ["Parts", "Tools", "Travel", "Outreach", "Reserve"]), "budget-chart.png")
    save(timeline(1100, 360), "season-timeline.png")
    save(wiring(700, 420), "wiring-diagram.png")
    save(field_paths(1000, 700), "auto-paths.png")
    save(field_paths(900, 560), "auto-field.png")

    # CoM diagram
    com = panel(700, 420, "CENTER OF MASS", "Chassis footprint · CoM mark", (52, 211, 153))
    d = ImageDraw.Draw(com)
    d.rectangle([180, 140, 520, 340], outline=(148, 163, 184), width=2)
    d.ellipse([330, 220, 370, 260], outline=(248, 113, 113), width=3)
    d.line([(350, 180), (350, 300)], fill=(248, 113, 113), width=1)
    d.line([(280, 240), (420, 240)], fill=(248, 113, 113), width=1)
    save(com, "com-diagram.png")

    print("done", len(list(OUT.iterdir())), "files")


if __name__ == "__main__":
    main()
