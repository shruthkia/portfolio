/* Non-critical site behavior. Loaded with defer so HTML can parse first. */
(function () {
  const themeSwitch = document.getElementById("themeSwitch");
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("theme", theme); } catch (e) {}
    if (!themeSwitch) return;
    themeSwitch.setAttribute("aria-checked", theme === "dark" ? "true" : "false");
    themeSwitch.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
    if (themeMeta) themeMeta.setAttribute("content", theme === "dark" ? "#131018" : "#f3efe8");
  }
  applyTheme(currentTheme());
  if (themeSwitch) {
    themeSwitch.addEventListener("click", () => {
      applyTheme(currentTheme() === "dark" ? "light" : "dark");
    });
  }

  (function () {
    const who = document.querySelector(".whoami");
    if (!who) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let ticking = false;
    function updateWho() {
      if (reduced) {
        who.style.setProperty("--who-p", "1");
        return;
      }
      const span = Math.max(1, who.offsetHeight - window.innerHeight * 0.7);
      const p = Math.min(1, Math.max(0, -who.getBoundingClientRect().top / span));
      who.style.setProperty("--who-p", String(p));
    }
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        updateWho();
        ticking = false;
      });
    }
    updateWho();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", updateWho);
  })();

  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("nav-links");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      navToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    navLinks.querySelectorAll(".has-dropdown > .nav-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        if (window.matchMedia("(max-width: 960px)").matches) {
          e.preventDefault();
          link.parentElement.classList.toggle("open");
        }
      });
    });
  }

  const reveals = document.querySelectorAll(".reveal, .reveal-scale");
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add("visible"); });
  }, { threshold: 0.08 });
  reveals.forEach((el, i) => {
    el.style.transitionDelay = (el.dataset.delay || (i * 0.05)) + "s";
    observer.observe(el);
    const r = el.getBoundingClientRect();
    if (r.top < window.innerHeight * 0.92) el.classList.add("visible");
  });

  const glow = document.getElementById("cursorGlow");
  if (glow) {
    document.addEventListener("mousemove", (e) => {
      glow.style.left = e.clientX + "px";
      glow.style.top = e.clientY + "px";
    });
  }

  document.querySelectorAll("[data-tilt]").forEach((el) => {
    el.addEventListener("mousemove", (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      el.style.transform = `perspective(800px) rotateX(${-y * 12}deg) rotateY(${x * 12}deg) scale3d(1.02,1.02,1.02)`;
    });
    el.addEventListener("mouseleave", () => { el.style.transform = ""; });
  });

  document.querySelectorAll(".project-card").forEach((card) => {
    const inner = card.querySelector(".project-card-inner");
    if (!inner) return;
    card.addEventListener("mousemove", (e) => {
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      inner.style.transform = `rotateX(${-y * 10}deg) rotateY(${x * 10}deg)`;
    });
    card.addEventListener("mouseleave", () => { inner.style.transform = ""; });
  });

  document.querySelectorAll(".magnetic, .btn-pill").forEach((btn) => {
    btn.addEventListener("mousemove", (e) => {
      const r = btn.getBoundingClientRect();
      const x = e.clientX - r.left - r.width / 2;
      const y = e.clientY - r.top - r.height / 2;
      btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
    });
    btn.addEventListener("mouseleave", () => { btn.style.transform = ""; });
  });

  const contactForm = document.getElementById("contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(contactForm);
      const btn = contactForm.querySelector(".form-submit");
      if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }
      try {
        const res = await fetch("/contact/send", {
          method: "POST",
          body: fd,
          headers: { "X-Requested-With": "fetch" },
        });
        const data = await res.json();
        if (data.ok) {
          if (data.mailto) {
            const mail = window.open(data.mailto, "_blank");
            if (!mail) {
              window.location.href = data.mailto;
            }
          }
          window.setTimeout(() => {
            window.location.href = "/contact?sent=1";
          }, 250);
          return;
        }
        window.location.href = "/contact?sent=0";
      } catch (err) {
        contactForm.submit();
      }
    });
  }
})();
