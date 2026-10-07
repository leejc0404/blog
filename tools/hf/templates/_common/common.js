/* blog/tools/hf 공통 도우미 — 모든 움직임은 GSAP 타임라인(window.__timelines.main) 위에서만 만든다.
   콜백(onUpdate·call)은 쓰지 않는다: HyperFrames 는 프레임마다 시각을 '찾아가며' 찍으므로
   속성 트윈과 tl.set 만이 어느 시각으로 이동해도 같은 그림을 보장한다. */
(function () {
  const V = window.HFV || {};
  const HF = (window.HF = {});
  HF.V = V;
  HF.W = V.W; HF.H = V.H; HF.DUR = V.DUR; HF.FPS = V.FPS || 30;

  // 0and1Life-Insta I-3-1 팔레트 + 블로그 설명컷 팔레트(ol·kp)
  HF.PAL = {
    ink: "#14161B", k: "#14161B", paper: "#FFF8EA", w: "#FFFFFF",
    r: "#E0483A", a: "#F5A524", y: "#FFD640", m: "#7CD678", s: "#78BEFF", p: "#F49AC1", t: "#D9774B"
  };
  HF.THEME = {
    ol: { bg: "#f7f8f6", fg: "#222222", sub: "#666666", gain: "#2e7d5b", loss: "#c0392b", neutral: "#555555", accent: "#c0392b", line: "#d9dcd6" },
    kp: { bg: "#f6f4ef", fg: "#1d232b", sub: "#6b7280", gain: "#2f7d5b", loss: "#c2410c", neutral: "#2b6cb0", accent: "#c2410c", line: "#dcd8cf" },
    dark: { bg: "#0f141c", fg: "#f5f7fa", sub: "#9aa4b2", gain: "#7CD678", loss: "#FF6B5A", neutral: "#78BEFF", accent: "#FFD640", line: "#2a3342" },
    aipick: { bg: "#FBF6EC", fg: "#1f2328", sub: "#5f6670", gain: "#2e7d5b", loss: "#c0392b", neutral: "#555555", accent: "#B5532B", line: "#e6dccb" }
  };
  HF.theme = (name) => Object.assign({}, HF.THEME[name] || HF.THEME.ol, V.palette || {});
  HF.color = (c, fallback) => (!c ? fallback : (HF.PAL[c] || c));

  HF.rng = (seed) => { let s = (seed >>> 0) || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); };

  // 글자 폭 추정(Pretendard 기준). 폰트 로딩 전에도 같은 결과가 나와야 하므로 측정 대신 추정한다.
  HF.cw = (ch) => {
    const c = ch.codePointAt(0);
    if (c >= 0xac00 && c <= 0xd7a3) return 0.96;
    if (c >= 0x3130 && c <= 0x318f) return 0.92;
    if (ch === " ") return 0.28;
    if (/[0-9]/.test(ch)) return 0.62;
    if (/[A-Z]/.test(ch)) return 0.7;
    if (/[a-z]/.test(ch)) return 0.57;
    if (/[.,:;'!|]/.test(ch)) return 0.3;
    if (/[-()\[\]\/·~+=]/.test(ch)) return 0.45;
    if (/[₩%$?&]/.test(ch)) return 0.74;
    return 0.95;
  };
  HF.textW = (t, size, weight) => { let w = 0; for (const ch of String(t)) w += HF.cw(ch); return w * size * ((weight || 700) >= 800 ? 1.05 : 1.0); };
  HF.fit = (t, size, maxW, weight, min) => { const w = HF.textW(t, size, weight); return w <= maxW ? size : Math.max(min || 12, Math.floor((size * maxW) / w)); };
  HF.esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // 시각: 숫자 그대로, 또는 beats 이름(vars.beats = {이름: 초})
  HF.t = (at, dflt) => {
    if (typeof at === "number") return at;
    const b = V.beats || {};
    if (at != null && typeof b[at] === "number") return b[at];
    if (at != null && Array.isArray(b[at])) return b[at][0];
    return dflt || 0;
  };

  HF.el = (tag, cls, css, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (css) Object.assign(e.style, css);
    if (html != null) e.innerHTML = html;
    return e;
  };
  HF.chars = (host, text) => {
    for (const ch of String(text)) {
      const s = document.createElement("span");
      s.className = "ch";
      s.textContent = ch === " " ? " " : ch;
      host.appendChild(s);
    }
    return host.querySelectorAll(".ch");
  };

  // 흰 글자 + 검은 테두리(밈 자막)
  HF.outline = (px, col) => {
    const c = col || "#000", a = [];
    for (let k = 0; k < 16; k++) { const r = (k / 16) * Math.PI * 2; a.push(`${(Math.cos(r) * px).toFixed(1)}px ${(Math.sin(r) * px).toFixed(1)}px 0 ${c}`); }
    return a.join(",");
  };

  // 숫자 올라가기 — 단계별 span 을 겹쳐 두고 tl.set 으로만 전환한다(시킹 안전)
  HF.countUp = (tl, host, finalText, t0, dur, steps) => {
    const m = String(finalText).match(/-?[\d,]*\d(\.\d+)?/);
    host.style.display = "inline-grid";
    const mk = (txt) => { const s = HF.el("span", "", { gridArea: "1 / 1", visibility: "hidden", whiteSpace: "nowrap" }); s.textContent = txt; host.appendChild(s); return s; };
    const fin = mk(finalText);
    if (!m || dur <= 0) { fin.style.visibility = "visible"; return; }
    const raw = m[0], dec = (m[1] || "").length ? m[1].length - 1 : 0;
    const num = parseFloat(raw.replace(/,/g, "")), comma = raw.includes(",");
    const pre = String(finalText).slice(0, m.index), post = String(finalText).slice(m.index + raw.length);
    const fmt = (x) => { let s = Math.abs(x).toFixed(dec); if (comma) { const [i, d] = s.split("."); s = i.replace(/\B(?=(\d{3})+(?!\d))/g, ",") + (d ? "." + d : ""); } return (x < 0 ? "-" : "") + s; };
    const n = steps || 10, spans = [];
    for (let k = 1; k < n; k++) { const e = 1 - Math.pow(1 - k / n, 3); spans.push(mk(pre + fmt(num * e) + post)); }
    const all = [...spans, fin];
    // 시작 상태는 DOM 에 직접 둔다(전부 숨김, t0=0 이면 첫 단계만 보임). 시각 이동은 tl.set 만으로.
    all.forEach((s, k) => {
      const on = t0 + (dur * k) / n;
      if (on <= 0.0001) s.style.visibility = "visible"; else tl.set(s, { visibility: "visible" }, on);
      if (k < all.length - 1) tl.set(s, { visibility: "hidden" }, t0 + (dur * (k + 1)) / n);
    });
  };

  // 프레임 0에서 완성 상태여야 하는 요소인지 (0초 beat)
  HF.atZero = (t) => t <= 0.0001;
})();
