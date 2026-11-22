// Accessibility helpers for the theme markup, which comes from the al-folio gems:
// - a "Skip to main content" link as the first focusable element (WCAG 2.4.1)
// - the page header inside the main region is not exposed as a second banner landmark
(function () {
  function init() {
    var main = document.querySelector('[role="main"]') || document.querySelector("main");
    if (main) {
      if (!main.id) main.id = "main-content";
      if (!main.hasAttribute("tabindex")) main.setAttribute("tabindex", "-1");
      if (!document.querySelector(".skip-link")) {
        var skip = document.createElement("a");
        skip.className = "skip-link";
        skip.href = "#" + main.id;
        skip.textContent = "Skip to main content";
        document.body.insertBefore(skip, document.body.firstChild);
      }
      main.querySelectorAll("header").forEach(function (h) {
        h.setAttribute("role", "none");
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
