/* TML design-preview switcher: left-edge widget that toggles the same page
   between the classic (live-mirror) design and the new design at /new/. */
(function () {
  "use strict";
  if (window.__tmlSwitch) return;
  window.__tmlSwitch = true;

  var path = location.pathname.replace(/\/+$/, "") || "/";
  var isNew = path === "/new" || path.indexOf("/new/") === 0;
  var classicPath = isNew ? (path.replace(/^\/new/, "") || "/") : path;
  var newPath = classicPath === "/" ? "/new" : "/new" + classicPath;

  var css = [
    "#tml-switch{position:fixed;left:0;top:50%;transform:translateY(-50%);z-index:2147483000;",
    "font-family:'Barlow Condensed','Arial Narrow',Arial,sans-serif;display:flex;flex-direction:column;",
    "border-radius:0 10px 10px 0;overflow:hidden;box-shadow:0 8px 30px rgba(10,16,6,.35);",
    "border:1px solid rgba(255,255,255,.14);border-left:0}",
    "#tml-switch a{display:flex;align-items:center;justify-content:center;",
    "writing-mode:vertical-rl;transform:rotate(180deg);text-orientation:mixed;",
    "padding:14px 9px;min-height:86px;font-size:15px;font-weight:600;letter-spacing:.08em;",
    "text-transform:uppercase;text-decoration:none;transition:padding .18s ease}",
    "#tml-switch a.cur{background:#cfe84d;color:#141b0d;cursor:default}",
    "#tml-switch a.alt{background:#141b0d;color:#fff}",
    "#tml-switch a.alt:hover{background:#263617;color:#cfe84d;padding-right:14px}",
    "#tml-switch .tag{position:absolute;left:calc(100% + 8px);top:50%;transform:translateY(-50%);",
    "background:#141b0d;color:#fff;font-size:12px;letter-spacing:.05em;padding:6px 10px;border-radius:6px;",
    "white-space:nowrap;opacity:0;pointer-events:none;transition:opacity .2s ease}",
    "#tml-switch:hover .tag{opacity:1}",
    "@media (max-width:700px){#tml-switch a{padding:10px 6px;min-height:64px;font-size:12px}}",
    "@media print{#tml-switch{display:none}}"
  ].join("");

  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  var el = document.createElement("div");
  el.id = "tml-switch";
  el.setAttribute("role", "navigation");
  el.setAttribute("aria-label", "Design preview switcher");
  el.innerHTML =
    '<a class="' + (isNew ? "cur" : "alt") + '" href="' + (isNew ? "#" : newPath) + '"' +
    (isNew ? ' aria-current="true"' : "") + ">New design</a>" +
    '<a class="' + (isNew ? "alt" : "cur") + '" href="' + (isNew ? classicPath : "#") + '"' +
    (isNew ? "" : ' aria-current="true"') + ">Classic</a>" +
    '<span class="tag">Toggle design preview</span>';
  el.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (a && a.getAttribute("href") === "#") e.preventDefault();
  });

  if (document.body) document.body.appendChild(el);
  else document.addEventListener("DOMContentLoaded", function () { document.body.appendChild(el); });
})();
