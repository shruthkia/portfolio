# Shockwaves FTC 38213 — Engineering Portfolio

Print-ready **16-page** (1 cover + 15 content) FTC Engineering Portfolio template for **Shockwaves Robotics FTC 38213**, season **2026–2027 BIOBUZZ™**.

## Quick start

```bash
npm install
npx playwright install chromium
npm start
```

Open **http://localhost:3851**

- **Export PDF** button in the toolbar, or:
- `npm run export:pdf` → writes `Shockwaves-38213-Engineering-Portfolio-BIOBUZZ.pdf`

PDF settings: **US Letter 8.5in × 11in**, portrait, `printBackground: true`.

## Swap your assets

Every placeholder image lives in [`/assets/`](./assets/). See **[`assets/README.md`](./assets/README.md)** for the full filename → page swap list.

Regenerate technical placeholders (optional):

```bash
npm run assets
```

## Page map

| # | Title |
|---|---|
| 00 | Cover |
| 01 | Meet the Team |
| 02 | Sustainability |
| 03 | Goals & Reflections |
| 04 | Outreach |
| 05 | Engineering Process & Trade-Offs |
| 06 | Robot Overview / CoM / Wiring |
| 07 | Chassis |
| 08 | Intake |
| 09 | Lift / Transfer |
| 10 | Scoring / Turret |
| 11 | Autonomous |
| 12 | TeleOp & Vision |
| 13 | Testing & Telemetry |
| 14 | Season Progression |
| 15 | Season Summary |

## Stack

- Static HTML/CSS/JS preview (`public/`)
- Express on port **3851** (`server.js`)
- Playwright PDF export (`scripts/export-pdf.mjs`)

Edit copy in `public/index.html`. Visual tokens live in `public/css/portfolio.css`.
