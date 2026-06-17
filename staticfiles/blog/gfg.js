/* GFG-style enhancements: one-click Copy button on code blocks. */
(function () {
  "use strict";
  function addCopy() {
    var body = document.querySelector(".article-body");
    if (!body) return;
    body.querySelectorAll("pre").forEach(function (pre) {
      if (pre.dataset.copyReady) return;
      pre.dataset.copyReady = "1";
      pre.style.position = "relative";

      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "code-copy-btn";
      btn.setAttribute("aria-label", "Copy code");
      btn.innerHTML = "<span>Copy</span>";

      function done(ok) {
        btn.classList.toggle("copied", ok);
        btn.innerHTML = "<span>" + (ok ? "Copied!" : "Failed") + "</span>";
        setTimeout(function () {
          btn.classList.remove("copied");
          btn.innerHTML = "<span>Copy</span>";
        }, 1600);
      }
      function fallback(text) {
        var ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.focus(); ta.select();
        var ok = false;
        try { ok = document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta); done(ok);
      }
      btn.addEventListener("click", function () {
        var code = pre.querySelector("code");
        var text = (code || pre).innerText.replace(/\n?Copy(ed!|)\n?$/, "");
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text)
            .then(function () { done(true); })
            .catch(function () { fallback(text); });
        } else { fallback(text); }
      });
      pre.appendChild(btn);
    });
  }
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", addCopy);
  else addCopy();
})();
