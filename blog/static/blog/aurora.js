/* ============================================================
   AURORA GLASS — interaction + WebGL background layer
   Dependency-free. Raw WebGL fragment-shader aurora with a
   CSS-gradient fallback, plus 3D tilt, scroll reveal, parallax.
   ============================================================ */
(function () {
  "use strict";

  var REDUCED = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var LIGHT = document.documentElement.getAttribute("data-theme") === "light";

  /* ---------- 1. WebGL aurora background ---------------------- */
  function initAurora() {
    var canvas = document.getElementById("aurora-bg");
    if (!canvas || LIGHT) return;
    var gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
    if (!gl) return; // CSS fallback stays

    var vsrc =
      "attribute vec2 p;void main(){gl_Position=vec4(p,0.0,1.0);}";
    /* flowing aurora via layered fbm noise */
    var fsrc = [
      "precision highp float;",
      "uniform vec2 r;uniform float t;",
      "float h(vec2 n){return fract(sin(dot(n,vec2(12.9898,78.233)))*43758.5453);}",
      "float noise(vec2 p){vec2 i=floor(p);vec2 f=fract(p);vec2 u=f*f*(3.0-2.0*f);",
      "return mix(mix(h(i),h(i+vec2(1,0)),u.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),u.x),u.y);}",
      "float fbm(vec2 p){float v=0.0;float a=0.5;mat2 m=mat2(1.6,1.2,-1.2,1.6);",
      "for(int i=0;i<6;i++){v+=a*noise(p);p=m*p;a*=0.5;}return v;}",
      "void main(){",
      " vec2 uv=gl_FragCoord.xy/r.xy;",
      " vec2 q=uv;q.x*=r.x/r.y;",
      " float tt=t*0.06;",
      " float f=fbm(q*2.2+vec2(tt,tt*0.4));",
      " float bands=fbm(q*vec2(3.0,5.0)+vec2(-tt*1.4,f*1.6));",
      " float aurora=smoothstep(0.35,0.95,bands+ (1.0-uv.y)*0.5);",
      " vec3 cyan=vec3(0.13,0.83,0.93);",
      " vec3 violet=vec3(0.55,0.49,0.98);",
      " vec3 pink=vec3(0.96,0.45,0.71);",
      " vec3 col=mix(cyan,violet,smoothstep(0.0,1.0,uv.x+0.2*sin(tt)));",
      " col=mix(col,pink,smoothstep(0.6,1.0,f));",
      " vec3 bg=mix(vec3(0.02,0.024,0.06),vec3(0.04,0.055,0.13),uv.y);",
      " vec3 final=bg+col*aurora*0.9;",
      /* glow blobs */
      " float g1=exp(-8.0*length(uv-vec2(0.2,0.85)));",
      " float g2=exp(-8.0*length(uv-vec2(0.82,0.78)));",
      " final+=cyan*g1*0.5+violet*g2*0.5;",
      " float grain=h(uv*r.xy+t)*0.035;",
      " gl_FragColor=vec4(final+grain,1.0);",
      "}"
    ].join("\n");

    function sh(type, src) {
      var s = gl.createShader(type);
      gl.shaderSource(s, src); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { return null; }
      return s;
    }
    var vs = sh(gl.VERTEX_SHADER, vsrc), fs = sh(gl.FRAGMENT_SHADER, fsrc);
    if (!vs || !fs) return;
    var prog = gl.createProgram();
    gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
    gl.useProgram(prog);

    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, "p");
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    var uR = gl.getUniformLocation(prog, "r");
    var uT = gl.getUniformLocation(prog, "t");

    canvas.classList.add("webgl-on");

    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.uniform2f(uR, canvas.width, canvas.height);
    }
    window.addEventListener("resize", resize, { passive: true });
    resize();

    var start = null, raf = null, running = true;
    function frame(ts) {
      if (start === null) start = ts;
      gl.uniform1f(uT, (ts - start) / 1000);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      if (running && !REDUCED) raf = requestAnimationFrame(frame);
    }
    if (REDUCED) { gl.uniform1f(uT, 12.0); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); }
    else raf = requestAnimationFrame(frame);

    document.addEventListener("visibilitychange", function () {
      running = !document.hidden;
      if (running && !REDUCED) { start = null; raf = requestAnimationFrame(frame); }
      else if (raf) cancelAnimationFrame(raf);
    });
  }

  /* ---------- 2. 3D tilt -------------------------------------- */
  function initTilt() {
    if (REDUCED || window.matchMedia("(pointer: coarse)").matches) return;
    document.querySelectorAll(".tilt").forEach(function (el) {
      if (!el.querySelector(".tilt-glare")) {
        var g = document.createElement("span");
        g.className = "tilt-glare";
        el.appendChild(g);
      }
      var glare = el.querySelector(".tilt-glare");
      el.addEventListener("pointermove", function (e) {
        var rct = el.getBoundingClientRect();
        var px = (e.clientX - rct.left) / rct.width;
        var py = (e.clientY - rct.top) / rct.height;
        var rx = (0.5 - py) * 12, ry = (px - 0.5) * 14;
        el.style.transform =
          "perspective(900px) rotateX(" + rx.toFixed(2) + "deg) rotateY(" +
          ry.toFixed(2) + "deg) translateY(-8px)";
        if (glare) { glare.style.setProperty("--gx", (px*100).toFixed(1)+"%");
          glare.style.setProperty("--gy", (py*100).toFixed(1)+"%"); }
      });
      el.addEventListener("pointerleave", function () { el.style.transform = ""; });
    });
  }

  /* ---------- 3. Scroll reveal -------------------------------- */
  function initReveal() {
    var els = document.querySelectorAll(".reveal");
    if (!els.length) return;
    if (REDUCED || !("IntersectionObserver" in window)) {
      els.forEach(function (e) { e.classList.add("in"); }); return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.style.transitionDelay = (en.target.dataset.delay || "0ms");
          en.target.classList.add("in");
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    els.forEach(function (e) { io.observe(e); });
  }

  /* ---------- 4. Hero parallax -------------------------------- */
  function initParallax() {
    if (REDUCED) return;
    var hero = document.querySelector(".aurora-hero");
    if (!hero) return;
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (!ticking) requestAnimationFrame(function () {
        var y = window.scrollY;
        if (y < window.innerHeight) {
          hero.style.transform = "translateY(" + (y * 0.18).toFixed(1) + "px)";
          hero.style.opacity = Math.max(0, 1 - y / (window.innerHeight * 0.9));
        }
        ticking = false;
      });
      ticking = true;
    }, { passive: true });
  }

  /* ---------- 5. Auto-apply effect classes ------------------- */
  function decorate() {
    var tiltSel = ".article-card, .featured-card";
    document.querySelectorAll(tiltSel).forEach(function (el) { el.classList.add("tilt"); });

    var revSel = ".article-card, .featured-card, .sidebar-section, .cat-chip, .aurora-stat";
    var n = 0;
    document.querySelectorAll(revSel).forEach(function (el) {
      el.classList.add("reveal");
      el.dataset.delay = (Math.min(n, 6) * 60) + "ms";
      n++;
    });
  }

  function boot() {
    decorate();
    initAurora();
    initTilt();
    initReveal();
    initParallax();
  }
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
