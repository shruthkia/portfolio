#!/usr/bin/env node
/**
 * Playwright PDF export — US Letter 8.5×11, printBackground: true
 * Usage:
 *   node scripts/export-pdf.mjs [outputPath]
 *   PORTFOLIO_URL=http://127.0.0.1:3851/ node scripts/export-pdf.mjs
 *
 * If PORTFOLIO_URL is unset, spins up a temporary static server on an ephemeral port.
 */
import { chromium } from "playwright";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import http from "http";
import { createRequire } from "module";

const require = createRequire(import.meta.url);
const express = require("express");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const OUT =
  process.argv[2] ||
  path.join(ROOT, "Shockwaves-38213-Engineering-Portfolio-BIOBUZZ.pdf");

async function startTempServer() {
  const app = express();
  app.use("/assets", express.static(path.join(ROOT, "assets")));
  app.use(express.static(path.join(ROOT, "public")));
  const server = http.createServer(app);
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();
  return { server, url: `http://127.0.0.1:${port}/` };
}

async function main() {
  let server = null;
  let url = process.env.PORTFOLIO_URL;

  if (!url) {
    const tmp = await startTempServer();
    server = tmp.server;
    url = tmp.url;
  }

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "networkidle", timeout: 120000 });
  await page.emulateMedia({ media: "print" });
  await page.addStyleTag({
    content: `
      .toolbar { display: none !important; }
      body.preview-mode { padding: 0 !important; background: #000 !important; }
      .deck { gap: 0 !important; }
      .page { box-shadow: none !important; margin: 0 !important; }
    `,
  });
  await page.evaluate(async () => {
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
  });
  await page.waitForTimeout(500);

  await page.pdf({
    path: OUT,
    width: "8.5in",
    height: "11in",
    printBackground: true,
    preferCSSPageSize: true,
    margin: { top: "0", right: "0", bottom: "0", left: "0" },
  });

  await browser.close();
  if (server) server.close();

  const stat = fs.statSync(OUT);
  console.log(`Wrote ${OUT} (${stat.size} bytes)`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
