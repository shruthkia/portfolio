#!/usr/bin/env node
/**
 * Shockwaves FTC 38213 Engineering Portfolio — local preview server
 * Preview: http://localhost:3851
 * PDF: POST /api/export-pdf  or  npm run export:pdf
 */
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");
const express = require("express");

const PORT = Number(process.env.PORT || 3851);
const ROOT = __dirname;
const PDF_NAME = "Shockwaves-38213-Engineering-Portfolio-BIOBUZZ.pdf";

const app = express();
app.use("/assets", express.static(path.join(ROOT, "assets")));
app.use(express.static(path.join(ROOT, "public")));

app.get("/health", (_req, res) => {
  res.json({
    ok: true,
    team: "Shockwaves 38213",
    season: "2026-2027 BIOBUZZ",
    pages: 16,
  });
});

let exporting = false;

app.post("/api/export-pdf", async (_req, res) => {
  if (exporting) {
    res.status(429).send("Export already in progress");
    return;
  }
  exporting = true;
  const outPath = path.join(ROOT, PDF_NAME);
  try {
    await new Promise((resolve, reject) => {
      const child = spawn(
        process.execPath,
        [path.join(ROOT, "scripts", "export-pdf.mjs"), outPath],
        {
          cwd: ROOT,
          env: (() => { const e = { ...process.env, PORT: String(PORT) }; delete e.PORTFOLIO_URL; return e; })(),
          // Unset so export spins its own static server (avoids nesting on this request)
          stdio: ["ignore", "pipe", "pipe"],
        }
      );
      let err = "";
      child.stderr.on("data", (d) => {
        err += d.toString();
      });
      child.on("close", (code) => {
        if (code === 0) resolve();
        else reject(new Error(err || `export exited ${code}`));
      });
    });
    res.download(outPath, PDF_NAME);
  } catch (e) {
    console.error(e);
    res.status(500).send(String(e.message || e));
  } finally {
    exporting = false;
  }
});

app.get("/api/pdf", (_req, res) => {
  const outPath = path.join(ROOT, PDF_NAME);
  if (!fs.existsSync(outPath)) {
    res.status(404).send("PDF not generated yet. Use Export PDF or npm run export:pdf");
    return;
  }
  res.download(outPath, PDF_NAME);
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Shockwaves Engineering Portfolio → http://localhost:${PORT}`);
});
