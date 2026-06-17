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

/* ── Member features: Follow buttons + comment delete ─────────── */
(function () {
  function getCookieSafe(n){var v='; '+document.cookie;var p=v.split('; '+n+'=');return p.length===2?p.pop().split(';').shift():'';}
  function token(){ return (typeof ensureCsrfToken==='function') ? ensureCsrfToken() : Promise.resolve(getCookieSafe('csrftoken')); }
  function post(url){ return token().then(function(tok){ var fd=new FormData(); fd.append('csrfmiddlewaretoken',tok); return fetch(url,{method:'POST',body:fd,headers:{'X-CSRFToken':tok},credentials:'same-origin'}); }).then(function(r){return r.json();}); }

  document.addEventListener('click', function (e) {
    var fb = e.target.closest && e.target.closest('.follow-btn');
    if (fb && fb.dataset.ftype) {
      e.preventDefault();
      var url = (fb.dataset.ftype === 'tag' ? '/follow/tag/' : '/follow/pub/') + fb.dataset.fid + '/';
      fb.disabled = true;
      post(url).then(function (d) {
        var txt = fb.querySelector('.fb-text');
        if (d.following) { fb.classList.add('following'); if (txt) txt.textContent = '✓ Following'; }
        else { fb.classList.remove('following'); if (txt) txt.textContent = '+ Follow'; }
      }).catch(function(){}).finally(function(){ fb.disabled = false; });
      return;
    }
    var del = e.target.closest && e.target.closest('.comment-del');
    if (del) {
      e.preventDefault();
      if (!confirm('Delete this comment?')) return;
      var id = del.dataset.id;
      post('/comment/' + id + '/delete/').then(function (d) {
        if (d.success) { var item = document.querySelector('.comment-item[data-comment-id="' + id + '"]'); if (item) item.remove(); }
      }).catch(function(){});
      return;
    }
  });
})();
