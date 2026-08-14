/* TML version switcher: left-edge widget toggling the same page between the
   ORIGINAL mirror and the FIXED working copy at /fixed/, plus a link to the
   owner-facing change log at /changes. */
(function () {
  "use strict";
  if (window.__tmlSwitch) return;
  window.__tmlSwitch = true;

  var path = location.pathname.replace(/\/+$/, "") || "/";
  var isFixed = path === "/fixed" || path.indexOf("/fixed/") === 0;
  var origPath = isFixed ? (path.replace(/^\/fixed/, "") || "/") : path;
  var fixedPath = origPath === "/" ? "/fixed" : "/fixed" + origPath;

  var css = [
    "#tml-switch{position:fixed;left:0;top:50%;transform:translateY(-50%);z-index:2147483000;",
    "font-family:Arial,Helvetica,sans-serif;display:flex;flex-direction:column;",
    "border-radius:0 10px 10px 0;overflow:hidden;box-shadow:0 8px 30px rgba(10,16,6,.35);",
    "border:1px solid rgba(255,255,255,.14);border-left:0}",
    "#tml-switch a{display:flex;align-items:center;justify-content:center;",
    "writing-mode:vertical-rl;transform:rotate(180deg);text-orientation:mixed;",
    "padding:12px 8px;min-height:74px;font-size:13px;font-weight:700;letter-spacing:.08em;",
    "text-transform:uppercase;text-decoration:none;transition:padding .18s ease}",
    "#tml-switch a.cur{background:#587735;color:#fff;cursor:default}",
    "#tml-switch a.alt{background:#141b0d;color:#fff}",
    "#tml-switch a.alt:hover{background:#263617;color:#cfe84d;padding-right:13px}",
    "#tml-switch a.log{background:#fff;color:#30302f;min-height:52px;font-size:11px;border-top:1px solid #d8d8d0}",
    "#tml-switch a.log:hover{color:#587735}",
    "@media (max-width:700px){#tml-switch a{padding:9px 6px;min-height:60px;font-size:11px}#tml-switch a.log{min-height:44px}}",
    "@media print{#tml-switch{display:none}}"
  ].join("");

  var style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  var el = document.createElement("div");
  el.id = "tml-switch";
  el.setAttribute("role", "navigation");
  el.setAttribute("aria-label", "Site version switcher");
  el.innerHTML =
    '<a class="' + (isFixed ? "cur" : "alt") + '" href="' + (isFixed ? "#" : fixedPath) + '"' +
    (isFixed ? ' aria-current="true"' : "") + ">Fixed</a>" +
    '<a class="' + (isFixed ? "alt" : "cur") + '" href="' + (isFixed ? origPath : "#") + '"' +
    (isFixed ? "" : ' aria-current="true"') + ">Original</a>" +
    '<a class="log" href="/changes" title="What changed and why">Log</a>';
  el.addEventListener("click", function (e) {
    var a = e.target.closest("a");
    if (a && a.getAttribute("href") === "#") e.preventDefault();
  });

  if (document.body) document.body.appendChild(el);
  else document.addEventListener("DOMContentLoaded", function () { document.body.appendChild(el); });
})();
