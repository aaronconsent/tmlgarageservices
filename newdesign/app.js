/* TML redesign v2 interactions: door choreography, menu, reveals, tracking. */
(function () {
  "use strict";

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* THE DOOR: roll up on load, then reveal the hero lines. Runs once per
     session so back/forward navigation doesn't replay it. */
  var door = document.getElementById("door");
  var hero = document.querySelector(".hero");
  var seen = false;
  try { seen = sessionStorage.getItem("tml-door") === "1"; } catch (e) {}
  if (door && (reduce || seen)) {
    document.documentElement.classList.add("no-door");
    if (hero) hero.classList.add("on");
  } else if (door && hero) {
    var opened = false;
    var open = function () {
      if (opened) return;
      opened = true;
      requestAnimationFrame(function () { door.classList.add("open"); });
      setTimeout(function () { hero.classList.add("on"); }, 900);
      setTimeout(function () { door.remove(); }, 2000);
      try { sessionStorage.setItem("tml-door", "1"); } catch (e) {}
    };
    if (document.readyState === "complete") setTimeout(open, 150);
    else window.addEventListener("load", function () { setTimeout(open, 150); });
    setTimeout(open, 1800); /* never hold the page hostage */
  } else if (hero) {
    hero.classList.add("on");
  }

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

  /* scroll reveals: enhance-only; content is fully visible without JS */
  if (!reduce && "IntersectionObserver" in window) {
    document.documentElement.classList.add("js-motion");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    document.querySelectorAll(".rise, .clipy").forEach(function (el) { io.observe(el); });
    setTimeout(function () {
      document.querySelectorAll(".rise:not(.in), .clipy:not(.in)").forEach(function (el) { el.classList.add("in"); });
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
