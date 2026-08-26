(function () {
  "use strict";

  function wireSearchBox(wrap) {
    var input = wrap.querySelector(".sb-input");
    var clear = wrap.querySelector(".sb-clear");
    if (!input || !clear) return;

    function sync() {
      wrap.classList.toggle("is-empty", input.value === "");
    }
    input.addEventListener("input", sync);
    clear.addEventListener("click", function () {
      input.value = "";
      sync();
      input.focus();
    });
    sync();
  }

  document.querySelectorAll(".sb-input-wrap").forEach(wireSearchBox);

  document.querySelectorAll("[data-toggle]").forEach(function (button) {
    button.addEventListener("click", function () {
      var target = document.getElementById(button.getAttribute("data-toggle"));
      if (target) target.hidden = !target.hidden;
    });
  });

  document.querySelectorAll("[data-reveal]").forEach(function (button) {
    button.addEventListener("click", function () {
      var input = document.getElementById(button.getAttribute("data-reveal"));
      if (!input) return;
      var hidden = input.type === "password";
      input.type = hidden ? "text" : "password";
      button.textContent = hidden ? "Hide" : "Show";
    });
  });

  // Only one result menu open at a time, and clicking anywhere else closes it.
  document.addEventListener("click", function (event) {
    document.querySelectorAll("details.result-menu[open]").forEach(function (menu) {
      if (!menu.contains(event.target)) menu.open = false;
    });
  });
})();
