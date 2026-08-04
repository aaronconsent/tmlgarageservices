/* TML redesign v3 interactions: menu, quiet reveals, tracking. */
(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* mobile menu */
  var menu = document.getElementById("menu");
  var openBtn = document.getElementById("menu-open");
  var closeBtn = document.getElementById("menu-close");
  if (menu && openBtn && closeBtn) {
    var setMenu = function (on) {
      menu.classList.toggle("open", on);
      openBtn.setAttribute("aria-expanded", on ? "true" : "false");
      document.documentElement.style.overflow = on ? "hidden" : "";
      (on ? closeBtn : openBtn).focus();
    };
    openBtn.addEventListener("click", function () { setMenu(true); });
    closeBtn.addEventListener("click", function () { setMenu(false); });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("open")) setMenu(false);
    });
  }

  /* close nav dropdowns on outside click */
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".top-nav details[open]").forEach(function (d) {
      if (!d.contains(e.target)) d.removeAttribute("open");
    });
  });

  /* scroll reveals: enhance-only; content fully visible without JS */
  if (!reduce && "IntersectionObserver" in window) {
    document.documentElement.classList.add("js-motion");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    document.querySelectorAll(".rise").forEach(function (el) { io.observe(el); });
    setTimeout(function () {
      document.querySelectorAll(".rise:not(.in)").forEach(function (el) { el.classList.add("in"); });
    }, 3000);
  }

  /* call + booking clicks -> dataLayer for GTM */
  document.addEventListener("click", function (e) {
    var a = e.target.closest("a[href^='tel:'], a[data-track]");
    if (!a || !window.dataLayer) return;
    window.dataLayer.push({
      event: a.href.indexOf("tel:") === 0 ? "call_click" : a.getAttribute("data-track"),
      link_url: a.href,
      page_path: location.pathname
    });
  });
})();
