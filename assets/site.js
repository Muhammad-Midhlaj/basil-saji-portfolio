// Basil Saji portfolio — interactions
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function fit(c) {
    const r = c.getBoundingClientRect(), d = window.devicePixelRatio || 1;
    c.width = Math.round(r.width * d); c.height = Math.round(r.height * d);
    const x = c.getContext('2d'); x.setTransform(d, 0, 0, d, 0, 0);
    return { x, w: r.width, h: r.height };
  }

  /* ---- Hero oscilloscope: sine reference vs SPWM inverter output ---- */
  const sc = document.getElementById('scope');
  if (sc) {
    let g = fit(sc), t0 = 0;
    window.addEventListener('resize', () => (g = fit(sc)));
    const draw = (ts) => {
      const { x, w, h } = g; t0 = reduce ? 0 : ts / 1000;
      x.clearRect(0, 0, w, h);
      const mid1 = h * 0.3, mid2 = h * 0.74, A = h * 0.18;
      // CH2: sinusoidal PWM (compare sine vs triangle carrier)
      x.beginPath(); x.lineWidth = 1.6; x.strokeStyle = '#f0913a'; x.shadowColor = '#f0913a'; x.shadowBlur = 6;
      let prev = null;
      for (let px = 0; px <= w; px += 0.5) {
        const ph = (px / w) * 4 * Math.PI + t0 * 2;
        const ref = Math.sin(ph) * 0.85;
        const car = (2 / Math.PI) * Math.asin(Math.sin(px * 0.16 + t0 * 6));
        const y = mid2 - (ref > car ? 1 : -1) * A * 0.75;
        if (prev === null) x.moveTo(px, y); else { if (y !== prev) x.lineTo(px, prev); x.lineTo(px, y); }
        prev = y;
      }
      x.stroke();
      // CH1: sine reference + 3rd harmonic hint
      x.beginPath(); x.strokeStyle = '#7cffb2'; x.shadowColor = '#7cffb2'; x.shadowBlur = 10; x.lineWidth = 2;
      for (let px = 0; px <= w; px += 1) {
        const ph = (px / w) * 4 * Math.PI + t0 * 2;
        const y = mid1 - Math.sin(ph) * A;
        px ? x.lineTo(px, y) : x.moveTo(px, y);
      }
      x.stroke(); x.shadowBlur = 0;
      x.fillStyle = 'rgba(124,255,178,.7)'; x.font = '10px JetBrains Mono, monospace';
      x.fillText('CH1  V_ref', 8, 14); x.fillStyle = 'rgba(240,145,58,.85)'; x.fillText('CH2  SPWM', 8, h * 0.5 + 14);
      if (!reduce) requestAnimationFrame(draw);
    };
    requestAnimationFrame(draw);
  }

  /* ---- Interleaved PWM lab ---- */
  const lab = document.getElementById('pwmlab');
  if (lab) {
    const slider = document.getElementById('duty'), out = document.getElementById('dutyv'), rip = document.getElementById('ripv');
    let g = fit(lab), phase = 0;
    window.addEventListener('resize', () => { g = fit(lab); });
    const N = 600, P = 3; // samples, periods shown
    function sim(D) {
      const g1 = [], g2 = [], i1 = [], i2 = [], s = [];
      let a = 0, b = 0;
      const st = (t, off) => (((t + off) % 1) + 1) % 1 < D;
      // integrate for one warm-up period then record
      for (let k = -N / P; k < N; k++) {
        const t = k / (N / P) + phase;
        const on1 = st(t, 0), on2 = st(t, 0.5);
        a += (on1 ? 1 - D : -D) / (N / P); b += (on2 ? 1 - D : -D) / (N / P);
        if (k >= 0) { g1.push(on1); g2.push(on2); i1.push(a); i2.push(b); s.push(a + b); }
      }
      const mean = (v) => v.reduce((p, c) => p + c, 0) / v.length;
      const m1 = mean(i1), m2 = mean(i2);
      for (let k = 0; k < N; k++) { i1[k] -= m1; i2[k] -= m2; s[k] -= m1 + m2; }
      const pp = (v) => Math.max(...v) - Math.min(...v);
      return { g1, g2, i1, i2, s, r1: pp(i1), rs: pp(s) };
    }
    function render() {
      const D = slider.value / 100; out.textContent = D.toFixed(2);
      const r = sim(D), { x, w, h } = g;
      x.clearRect(0, 0, w, h);
      // grid
      x.strokeStyle = 'rgba(124,255,178,.07)'; x.lineWidth = 1;
      for (let i = 1; i < 12; i++) { x.beginPath(); x.moveTo((w * i) / 12, 0); x.lineTo((w * i) / 12, h); x.stroke(); }
      const rows = [h * 0.12, h * 0.3, h * 0.56, h * 0.84];
      const sx = (k) => (k / (N - 1)) * w;
      const sq = (arr, y0, col) => {
        x.beginPath(); x.strokeStyle = col; x.lineWidth = 1.6;
        arr.forEach((v, k) => { const y = y0 - (v ? h * 0.07 : -h * 0.03); k ? x.lineTo(sx(k), y) : x.moveTo(0, y); });
        x.stroke();
      };
      const wave = (arr, y0, scale, col, lw) => {
        x.beginPath(); x.strokeStyle = col; x.lineWidth = lw;
        arr.forEach((v, k) => { const y = y0 - v * scale; k ? x.lineTo(sx(k), y) : x.moveTo(0, y); });
        x.stroke();
      };
      sq(r.g1, rows[0], '#f0913a'); sq(r.g2, rows[1], '#4fd6ff');
      const sc = h * 0.75;
      wave(r.i1, rows[2], sc, 'rgba(240,145,58,.9)', 1.6); wave(r.i2, rows[2], sc, 'rgba(79,214,255,.9)', 1.6);
      x.shadowColor = '#7cffb2'; x.shadowBlur = 8; wave(r.s, rows[3], sc, '#7cffb2', 2.2); x.shadowBlur = 0;
      x.font = '10px JetBrains Mono, monospace'; x.fillStyle = '#5fbf8a';
      x.fillText('S1 gate', 6, rows[0] - h * 0.085); x.fillText('S2 gate (180° shift)', 6, rows[1] - h * 0.085);
      x.fillText('iL1 / iL2 ripple', 6, rows[2] - h * 0.13); x.fillText('Σ input current ripple', 6, rows[3] - h * 0.1);
      const pct = r.r1 > 1e-9 ? Math.round((1 - r.rs / r.r1) * 100) : 0;
      rip.textContent = pct + '%';
    }
    slider.addEventListener('input', render);
    window.addEventListener('resize', render);
    render();
  }

  /* ---- reveal on scroll ---- */
  const io = 'IntersectionObserver' in window ? new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.12 }) : null;
  document.querySelectorAll('.rv').forEach((el) => (io ? io.observe(el) : el.classList.add('in')));

  /* ---- lightbox ---- */
  const lb = document.querySelector('.lb');
  if (lb) {
    const im = lb.querySelector('img');
    document.querySelectorAll('[data-zoom]').forEach((f) => f.addEventListener('click', () => { im.src = f.dataset.zoom; im.alt = f.querySelector('img')?.alt || ''; lb.classList.add('on'); }));
    lb.addEventListener('click', () => lb.classList.remove('on'));
    document.addEventListener('keydown', (e) => e.key === 'Escape' && lb.classList.remove('on'));
  }

  /* ---- copy link ---- */
  const toast = document.querySelector('.toast');
  document.querySelectorAll('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    const url = location.href.split('#')[0];
    try { await navigator.clipboard.writeText(url); } catch (e) { prompt('Copy this link:', url); return; }
    if (toast) { toast.classList.add('on'); setTimeout(() => toast.classList.remove('on'), 1800); }
  }));
})();
