// Standard / wide width toggle, modelled on Wikimedia's Vector 2022 limited-width setting:
// standard keeps content at 960px; wide lets it grow to 1440px. The button shows only on
// screens wider than 1400px (CSS), and the choice persists across pages in this browser.
(function () {
  var KEY = "site-width";
  var root = document.documentElement;

  function read() {
    try {
      return window.localStorage.getItem(KEY);
    } catch (e) {
      return null;
    }
  }

  function write(value) {
    try {
      window.localStorage.setItem(KEY, value);
    } catch (e) {
      /* storage unavailable: the choice lasts for this page only */
    }
  }

  function apply(mode, button) {
    var wide = mode === "wide";
    root.classList.toggle("site-wide", wide);
    if (button) {
      button.setAttribute("aria-pressed", wide ? "true" : "false");
      button.title = wide ? "Switch to standard width" : "Switch to wide width";
      button.querySelector(".width-toggle-label").textContent = wide ? "Standard" : "Wide";
    }
  }

  apply(read());

  function init() {
    var nav = document.querySelector("#navbarNav .navbar-nav");
    if (!nav || document.getElementById("width-toggle")) return;
    var item = document.createElement("li");
    item.className = "nav-item width-toggle-item";
    var button = document.createElement("button");
    button.id = "width-toggle";
    button.type = "button";
    button.className = "width-toggle";
    button.innerHTML = '<span class="nav-link"><i class="fa-solid fa-left-right"></i> <span class="width-toggle-label">Wide</span></span>';
    button.addEventListener("click", function () {
      var next = root.classList.contains("site-wide") ? "standard" : "wide";
      write(next);
      apply(next, button);
    });
    item.appendChild(button);
    nav.appendChild(item);
    apply(read(), button);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
