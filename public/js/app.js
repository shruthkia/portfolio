/* Preview toolbar + client-triggered PDF export via /api/export-pdf */
(function () {
  const statusEl = document.getElementById("export-status");
  const btn = document.getElementById("btn-export");

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg;
  }

  async function exportPdf() {
    setStatus("Exporting…");
    btn.disabled = true;
    try {
      const res = await fetch("/api/export-pdf", { method: "POST" });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || res.statusText);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Shockwaves-38213-Engineering-Portfolio-BIOBUZZ.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setStatus("PDF ready · US Letter");
    } catch (err) {
      console.error(err);
      setStatus("Export failed — try npm run export:pdf");
    } finally {
      btn.disabled = false;
    }
  }

  if (btn) btn.addEventListener("click", exportPdf);
})();
