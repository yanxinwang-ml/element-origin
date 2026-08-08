/* Nuclear-reaction animation engine for the "Origin of the Elements" page.
 * Pure Canvas 2D, no dependencies. Recipe language example:
 *   "fusion:He4+C12->O16"            two nuclei fuse (gamma flash)
 *   "fusion:C12+C12->Ne20+a"         fusion with alpha ejection
 *   "capture:n+Mo98->Mo99"           neutron capture
 *   "bdecay:Mo99->Tc99"              beta-minus: n -> p + e- + nu
 *   "bplus:N13->C13"                 beta-plus:  p -> n + e+ + nu
 *   "ecap:Be7->Li7"                  electron capture: p + e- -> n + nu
 *   "spall:p+C12->Li7"               spallation (projectile shatters target)
 *   "nuproc:Ne20->F19"               neutrino knocks a proton out
 *   "rproc:Fe56->Au197"              rapid neutron captures + beta cascade
 *   "sproc:Fe56->Ga69"               slow neutron captures + beta decays
 *   "explosion:Si28->Fe56"           explosive nucleosynthesis (schematic)
 *   "lab:Ca48+Cf249->Og294+3n"       accelerator fusion-evaporation
 *   "primordial:H1"                  direct formation (no reaction)
 */
(function (global) {
  "use strict";

  const SUP = { 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
  function sup(n) { return String(n).split("").map(function (c) { return SUP[c]; }).join(""); }
  function fmtNuc(n) {
    if (n.kind === "gamma") return "γ";
    if (n.kind === "electron") return "e⁻";
    if (n.kind === "positron") return "e⁺";
    if (n.kind === "neutrino") return "ν";
    if (n.symbol === "n") return "n";
    if (n.symbol === "p") return "p";
    return sup(n.A) + n.symbol;
  }
  function fmtNucC(n) {
    if (n.kind !== "nuc") return fmtNuc(n);
    return fmtNuc(n) + "(" + n.Z + "p+" + n.N + "n)";
  }

  const SPECIAL = {
    n: { Z: 0, A: 1, symbol: "n" },
    p: { Z: 1, A: 1, symbol: "p" },
    D: { Z: 1, A: 2, symbol: "H" },
    d: { Z: 1, A: 2, symbol: "H" },
  };

  const Sim = {
    _zmap: {},
    _cnmap: {},
    init: function (elements) {
      elements.forEach(function (el) {
        Sim._zmap[el.symbol] = el.z;
        Sim._cnmap[el.symbol] = el.cn;
      });
    },

    parseNuclide: function (tok) {
      tok = tok.trim();
      if (SPECIAL[tok]) return { kind: "nuc", ...SPECIAL[tok] };
      if (tok === "g" || tok === "γ") return { kind: "gamma", symbol: "γ" };
      if (tok === "e" || tok === "e-") return { kind: "electron", symbol: "e" };
      if (tok === "e+") return { kind: "positron", symbol: "e" };
      if (tok === "v" || tok === "nu") return { kind: "neutrino", symbol: "ν" };
      const m = /^([A-Za-z]{1,2})(\d+)$/.exec(tok);
      if (!m) return { kind: "generic", label: tok, Z: 0, A: 0, symbol: tok };
      const sym = m[1][0].toUpperCase() + m[1].slice(1).toLowerCase();
      const A = parseInt(m[2], 10);
      const Z = Sim._zmap[sym];
      return { kind: "nuc", symbol: sym, Z: Z, A: A, N: A - Z };
    },

    parseRecipe: function (recipe) {
      return recipe.split(";").map(function (part) {
        const ci = part.indexOf(":");
        const type = part.slice(0, ci).trim();
        const body = part.slice(ci + 1);
        const arrow = body.indexOf("->");
        let lhs = "";
        let rhs = body;
        if (arrow >= 0) {
          lhs = body.slice(0, arrow);
          rhs = body.slice(arrow + 2);
        }
        const reactants = lhs ? lhs.split("+").map(Sim.parseNuclide) : [];
        const parts = rhs.split("+");
        const products = [Sim.parseNuclide(parts[0].trim())];
        const ejectiles = [];
        if (parts.length > 1) {
          const e = parts.slice(1).join("+").trim();
          const mm = /^(\d+)?(n|p|a|g|e|v)$/.exec(e);
          const n = (mm && mm[1]) ? parseInt(mm[1], 10) : 1;
          for (let i = 0; i < n; i++) {
            ejectiles.push(Sim.parseNuclide(mm[2] === "a" ? "He4" : mm[2]));
          }
        }
        return { type: type, reactants: reactants, products: products, ejectiles: ejectiles, raw: part };
      });
    },

    /* Normalise parsed stages into the player's internal representation. */
    buildScene: function (recipe) {
      const stages = Sim.parseRecipe(recipe);
      const out = [];
      stages.forEach(function (st) {
        if (st.type === "fusion" || st.type === "capture" || st.type === "lab") {
          out.push({
            type: st.type,
            proj: st.reactants[0],
            target: st.reactants[1],
            product: st.products[0],
            ejectiles: st.ejectiles,
          });
        } else if (st.type === "bdecay" || st.type === "bplus") {
          out.push({ type: st.type, parent: st.reactants[0], product: st.products[0] });
        } else if (st.type === "ecap") {
          out.push({ type: st.type, parent: st.reactants[0], product: st.products[0] });
        } else if (st.type === "spall" || st.type === "nuproc") {
          out.push({
            type: st.type,
            proj: st.reactants[0],
            target: st.reactants[1],
            product: st.products[0],
          });
        } else if (st.type === "primordial") {
          out.push({ type: st.type, product: st.products[0] });
        } else if (st.type === "rproc" || st.type === "sproc") {
          out.push({ type: st.type, from: st.reactants[0], to: st.products[0], product: st.products[0] });
        } else if (st.type === "explosion") {
          out.push({ type: st.type, from: st.reactants[0], to: st.products[0], product: st.products[0] });
        }
      });
      out.push({ type: "atom", product: out.length ? out[out.length - 1].product : { Z: 1, N: 0, symbol: "H", A: 1 } });
      return { stages: out, total: out.length };
    },

    DUR: {
      fusion: 2.4, capture: 1.9, lab: 3.2, bdecay: 2.0, bplus: 2.0, ecap: 2.0,
      spall: 2.2, nuproc: 2.2, primordial: 1.6, rproc: 4.2, sproc: 4.2,
      explosion: 3.0, atom: 1.2,
    },

    createPlayer: function (canvas, scene, callbacks) {
      const ctx = canvas.getContext("2d");
      const W = 760, H = 440;
      const dpr = (typeof window !== "undefined" && window.devicePixelRatio) || 1;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const state = { nucleus: null, flash: 0, flash2: 0, proj: null, ejectiles: [], p: 0, extra: {} };
      let stageIdx = 0;
      let t = 0;
      let playing = true;
      let speed = 1;
      let rafId = null;
      let finished = false;
      let annotate = true;

      function setupStage(st) {
        state.ejectiles = [];
        state.flash = 0;
        state.flash2 = 0;
        state.proj = null;
        state.extra = {};
        if (st.type === "fusion" || st.type === "capture") {
          state.nucleus = { Z: st.target.Z, N: st.target.N, symbol: st.target.symbol, A: st.target.A };
          state.proj = st.proj;
        } else if (st.type === "lab") {
          state.nucleus = { Z: st.target.Z, N: st.target.N, symbol: st.target.symbol, A: st.target.A };
          state.proj = st.proj;
        } else if (st.type === "bdecay" || st.type === "bplus" || st.type === "ecap") {
          state.nucleus = { Z: st.parent.Z, N: st.parent.N, symbol: st.parent.symbol, A: st.parent.A };
        } else if (st.type === "spall" || st.type === "nuproc") {
          state.nucleus = { Z: st.target.Z, N: st.target.N, symbol: st.target.symbol, A: st.target.A };
          state.proj = st.proj;
        } else if (st.type === "primordial") {
          state.nucleus = { Z: st.product.Z, N: st.product.N, symbol: st.product.symbol, A: st.product.A };
        } else if (st.type === "rproc" || st.type === "sproc") {
          state.nucleus = { Z: st.from.Z, N: st.from.N, symbol: st.from.symbol, A: st.from.A };
          state.extra.dA = st.to.A - st.from.A;
          state.extra.dZ = st.to.Z - st.from.Z;
        } else if (st.type === "explosion") {
          state.nucleus = { Z: st.from.Z, N: st.from.N, symbol: st.from.symbol, A: st.from.A };
          state.extra.to = st.to;
        } else if (st.type === "atom") {
          const last = scene.stages[stageIdx - 1];
          const prod = last ? last.product : { Z: 1, N: 0, symbol: "H", A: 1 };
          state.nucleus = { Z: prod.Z, N: prod.N, symbol: prod.symbol, A: prod.A };
        }
      }

      function captionFor(st) {
        if (st.type === "fusion" || st.type === "capture") {
          const ej = st.ejectiles.length ? " + " + st.ejectiles.map(fmtNucC).join(" + ") : "";
          return fmtNucC(st.proj) + " + " + fmtNucC(st.target) + " → " + fmtNucC(st.product) + ej;
        }
        if (st.type === "lab") {
          return fmtNucC(st.proj) + " + " + fmtNucC(st.target) + " → 复合核* → " +
            fmtNucC(st.product) + " + " + st.ejectiles.length + "n";
        }
        if (st.type === "bdecay") return fmtNucC(st.parent) + " → " + fmtNucC(st.product) + " + e⁻ + ν̄";
        if (st.type === "bplus") return fmtNucC(st.parent) + " → " + fmtNucC(st.product) + " + e⁺ + ν";
        if (st.type === "ecap") return fmtNucC(st.parent) + " + e⁻ → " + fmtNucC(st.product) + " + ν";
        if (st.type === "spall") return fmtNucC(st.proj) + " + " + fmtNucC(st.target) + " → " + fmtNucC(st.product) + " + 碎片";
        if (st.type === "nuproc") return "ν + " + fmtNucC(st.target) + " → " + fmtNucC(st.product) + " + p";
        if (st.type === "primordial") return fmtNuc(st.product) + "：原初质子直接形成（无需反应）";
        if (st.type === "rproc") return "r-过程：快中子俘获 ×" + (st.to.A - st.from.A) +
          " → β⁻ 衰变 ×" + (st.to.Z - st.from.Z) + "（示意链）";
        if (st.type === "sproc") return "s-过程：慢中子俘获 ×" + (st.to.A - st.from.A) +
          " → β⁻ 衰变 ×" + (st.to.Z - st.from.Z) + "（示意链）";
        if (st.type === "explosion") return "爆炸性核合成：" + fmtNuc(st.from) + " → " + fmtNuc(st.to) + "（示意）";
        if (st.type === "atom") return fmtNuc(st.product) + " 原子形成：电子填入壳层";
        return st.raw || "";
      }

      function stageCaption(st) {
        if (st.type === "atom") return "电子填充壳层 → " + fmtNuc(st.product) + " 中性原子";
        return captionFor(st);
      }

      function update(dt) {
        t += dt * speed;
        let acc = 0;
        let idx = 0;
        for (let i = 0; i < scene.stages.length; i++) {
          const dur = Sim.DUR[scene.stages[i].type] || 2;
          if (t < acc + dur) { idx = i; break; }
          acc += dur;
          idx = i;
        }
        if (idx !== stageIdx) {
          stageIdx = idx;
          setupStage(scene.stages[idx]);
          if (callbacks.onStage) callbacks.onStage(idx, scene.stages.length, stageCaption(scene.stages[idx]));
        }
        let acc2 = 0;
        for (let i = 0; i < stageIdx; i++) acc2 += Sim.DUR[scene.stages[i].type] || 2;
        const dur = Sim.DUR[scene.stages[idx].type] || 2;
        state.p = Math.min(1, Math.max(0, (t - acc2) / dur));
        if (stageIdx === scene.stages.length - 1 && state.p >= 1 && playing && !finished) {
          finished = true;
          playing = false;
          if (callbacks.onFinish) callbacks.onFinish();
        }
      }

      /* ---------- drawing helpers ---------- */
      function nucleusGeometry(n) {
        const A = n.N + n.Z;
        let R0 = 5.4;
        if (A > 45) R0 = 4.6;
        if (A > 90) R0 = 3.8;
        if (A > 150) R0 = 3.2;
        return { R0: R0, dot: Math.max(2.2, R0 * 0.52) };
      }

      function drawNucleus(n, x, y, scale, glow, label, compact) {
        const g = nucleusGeometry(n);
        const R0 = g.R0 * (scale || 1) * (annotate ? 1.12 : 1);
        const dot = g.dot * (scale || 1) * (annotate ? 1.12 : 1);
        const A = n.N + n.Z;
        const labelStep = A > 70 ? Math.ceil(A / 36) : 1;
        for (let i = 0; i < A; i++) {
          const r = R0 * Math.sqrt(i + 1) * 0.92;
          const a = i * 2.39996;
          const px = x + Math.cos(a) * r;
          const py = y + Math.sin(a) * r;
          ctx.beginPath();
          ctx.arc(px, py, dot, 0, Math.PI * 2);
          ctx.fillStyle = i < n.Z ? "#f87171" : "#94a3b8";
          ctx.fill();
          ctx.strokeStyle = "rgba(255,255,255,0.35)";
          ctx.lineWidth = 0.7;
          ctx.stroke();
          if (annotate && (labelStep === 1 || i % labelStep === 0)) {
            ctx.fillStyle = "#0f172a";
            ctx.font = "600 " + Math.max(4, dot * 0.95) + "px 'Segoe UI', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText(i < n.Z ? "p" : "n", px, py + Math.max(1.4, dot * 0.36));
          }
        }
        if (glow > 0.02) {
          const grd = ctx.createRadialGradient(x, y, 4, x, y, 64);
          grd.addColorStop(0, "rgba(255,220,130," + (0.65 * glow) + ")");
          grd.addColorStop(1, "rgba(255,220,130,0)");
          ctx.fillStyle = grd;
          ctx.beginPath();
          ctx.arc(x, y, 64, 0, Math.PI * 2);
          ctx.fill();
        }
        if (!compact) {
          const cn = Sim._cnmap[n.symbol] || "";
          ctx.fillStyle = "#f8fafc";
          ctx.font = "600 16px 'Segoe UI', 'Microsoft YaHei', sans-serif";
          ctx.textAlign = "center";
          ctx.fillText(label || (fmtNuc(n) + (cn ? " " + cn : "")), x, y - 46);
          ctx.font = "12px 'Segoe UI', 'Microsoft YaHei', sans-serif";
          ctx.fillStyle = "#fca5a5";
          ctx.fillText(n.Z + "p", x - 56, y + 52);
          ctx.fillStyle = "#cbd5e1";
          ctx.fillText(n.N + "n", x - 14, y + 52);
          ctx.fillStyle = "rgba(226,232,240,0.75)";
          ctx.fillText("A = " + (n.Z + n.N), x + 34, y + 52);
        }
      }

      function drawSingle(n, x, y, color, label, scale) {
        const s = scale || 1;
        if (n.kind === "gamma") {
          ctx.strokeStyle = "rgba(253,224,71,0.9)";
          ctx.lineWidth = 2.4;
          for (let i = -1; i <= 1; i++) {
            ctx.beginPath();
            ctx.moveTo(x - 14, y + i * 8);
            ctx.quadraticCurveTo(x, y + i * 8 + 4, x + 14, y + i * 8);
            ctx.stroke();
          }
          ctx.fillStyle = "#fde047";
          ctx.font = "600 11px 'Segoe UI', 'Microsoft YaHei', sans-serif";
          ctx.textAlign = "left";
          ctx.fillText("γ 光子", x + 18, y + 4);
          return;
        }
        if (n.kind === "neutrino") {
          ctx.strokeStyle = "rgba(129,140,248,0.9)";
          ctx.lineWidth = 2;
          ctx.setLineDash([6, 5]);
          ctx.beginPath();
          ctx.moveTo(x - 16, y);
          ctx.lineTo(x + 16, y);
          ctx.stroke();
          ctx.setLineDash([]);
          ctx.fillStyle = "#a5b4fc";
          ctx.font = "600 11px 'Segoe UI', 'Microsoft YaHei', sans-serif";
          ctx.textAlign = "left";
          ctx.fillText("ν 中微子", x + 18, y + 4);
          return;
        }
        const DEFAULT_LABEL = {
          p: "p⁺", n: "n", electron: "e⁻", positron: "e⁺", neutrino: "ν", gamma: "γ",
        };
        const L = label || DEFAULT_LABEL[n.symbol] || fmtNuc(n);
        ctx.beginPath();
        ctx.arc(x, y, 5 * s, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = "rgba(255,255,255,0.5)";
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.fillStyle = "#0b1220";
        ctx.font = "700 9px 'Segoe UI', sans-serif";
        ctx.textAlign = "center";
        ctx.strokeStyle = "rgba(2,6,17,0.75)";
        ctx.lineWidth = 2.5;
        ctx.strokeText(L, x, y + 3);
        ctx.fillText(L, x, y + 3);
      }

      function drawShells(n, p) {
        const caps = [2, 8, 18, 32, 32, 18, 8];
        const elec = n.Z;
        let shells = 0, used = 0;
        for (let i = 0; i < caps.length; i++) {
          if (used >= elec) break;
          shells++;
          used += caps[i];
        }
        if (shells === 0) shells = 1;
        const spacing = Math.min(32, Math.max(24, 150 / shells));
        const shellR = [];
        for (let i = 0; i < shells; i++) shellR.push((i + 1) * spacing);
        const maxR = shellR[shells - 1];
        for (let i = 0; i < shells; i++) {
          ctx.beginPath();
          ctx.arc(0, 0, shellR[i], 0, Math.PI * 2);
          ctx.strokeStyle = "rgba(148,163,184,0.35)";
          ctx.lineWidth = 1;
          ctx.stroke();
        }
        let placed = 0;
        for (let s = 0; s < shells && placed < elec; s++) {
          const cap = caps[s];
          const count = Math.min(cap, elec - placed);
          for (let i = 0; i < count; i++) {
            const ang = (i / count) * Math.PI * 2 + s * 0.7;
            const r = shellR[s] + (1 - p) * 40;
            const ex = Math.cos(ang) * r;
            const ey = Math.sin(ang) * r;
            ctx.beginPath();
            ctx.arc(ex, ey, 2.6, 0, Math.PI * 2);
            ctx.fillStyle = "#fde047";
            ctx.fill();
            if (count <= 18) {
              ctx.fillStyle = "#0f172a";
              ctx.font = "500 5px 'Segoe UI', sans-serif";
              ctx.textAlign = "center";
              ctx.fillText("e⁻", ex, ey + 2);
            }
          }
          placed += count;
        }
        ctx.fillStyle = "#f8fafc";
        ctx.font = "600 17px 'Segoe UI', 'Microsoft YaHei', sans-serif";
        ctx.textAlign = "center";
        ctx.fillText(fmtNuc(n) + " 原子", 0, -maxR - 28);
        ctx.font = "12px 'Segoe UI', 'Microsoft YaHei', sans-serif";
        ctx.fillStyle = "rgba(226,232,240,0.9)";
        ctx.fillText("质子 ×" + n.Z + "　中子 ×" + n.N + "　电子 ×" + n.Z + "（填充 " + shells + " 层壳层）", 0, -maxR - 10);
      }

      /* ---------- stage renderers ---------- */
      function renderFusion(st, p) {
        const cx = 0, cy = 0;
        if (p < 0.45) {
          const f = p / 0.45;
          const x = -250 + (250 + cx) * (f * f * (3 - 2 * f));
          drawNucleus(state.nucleus, cx, cy, 1, 0);
          drawSingle(st.proj, x, cy - 26,
            st.proj.symbol === "n" ? "#94a3b8" : "#f87171",
            "", 1.6);
        } else if (p < 0.58) {
          const f = (p - 0.45) / 0.13;
          state.flash = Math.sin(f * Math.PI);
          drawNucleus(state.nucleus, cx, cy, 1, state.flash);
        } else {
          const f = (p - 0.58) / 0.42;
          state.nucleus = { Z: st.product.Z, N: st.product.N, symbol: st.product.symbol, A: st.product.A };
          drawNucleus(state.nucleus, cx, cy, 1, 1 - f);
          st.ejectiles.forEach(function (ej, i) {
            const ef = Math.max(0, Math.min(1, (p - 0.58 - i * 0.08) / 0.18));
            const ex = cx + 90 + ef * 170;
            const ey = cy - 60 + i * 30;
            if (ej.kind === "nuc") {
              drawNucleus(ej, ex, ey, 0.45, 0, "", true);
              if (ej.symbol === "He" && ej.A === 4) {
                ctx.fillStyle = "#f0abfc";
                ctx.font = "600 11px 'Segoe UI', 'Microsoft YaHei', sans-serif";
                ctx.textAlign = "center";
                ctx.fillText("α 粒子", ex, ey + 22);
              }
            } else drawSingle(ej, ex, ey, "#fde047", fmtNuc(ej));
          });
        }
      }

      function renderLab(st, p) {
        const cx = 0, cy = 0;
        if (p < 0.32) {
          const f = p / 0.32;
          const x = -250 + (250 + cx) * (f * f * (3 - 2 * f));
          drawNucleus(state.nucleus, cx, cy, 1, 0);
          drawNucleus(st.proj, x, cy - 70, 0.55, 0, "", true);
        } else if (p < 0.44) {
          const f = (p - 0.32) / 0.12;
          state.flash = Math.sin(f * Math.PI);
          drawNucleus({ Z: st.proj.Z + st.target.Z, N: st.proj.N + st.target.N, symbol: "*", A: st.proj.A + st.target.A },
            cx, cy, 1.08, state.flash, "复合核 *");
        } else {
          const k = Math.max(1, st.ejectiles.length);
          let emitted = 0;
          st.ejectiles.forEach(function (ej, i) {
            const start = 0.44 + i * 0.1;
            if (p >= start) emitted++;
            const ef = Math.max(0, Math.min(1, (p - start) / 0.12));
            const ex = cx + 70 + ef * 200;
            const ey = cy - 40 + i * 26;
            if (ej.kind === "nuc") drawSingle(ej, ex, ey, "#cbd5e1", "n", 1.4);
            else drawSingle(ej, ex, ey, "#fde047", fmtNuc(ej));
          });
          if (emitted >= k) {
            state.nucleus = { Z: st.product.Z, N: st.product.N, symbol: st.product.symbol, A: st.product.A };
            drawNucleus(state.nucleus, cx, cy, 1, 0.15);
          } else {
            drawNucleus({ Z: st.proj.Z + st.target.Z, N: st.proj.N + st.target.N, symbol: "*", A: st.proj.A + st.target.A },
              cx, cy, 1.05, 0.2, "复合核 *");
          }
        }
      }

      function renderDecay(st, p, kind) {
        const cx = 0, cy = 0;
        if (p < 0.3) {
          drawNucleus(state.nucleus, cx, cy, 1, 0);
        } else if (p < 0.45) {
          const f = (p - 0.3) / 0.15;
          state.flash = Math.sin(f * Math.PI);
          drawNucleus(state.nucleus, cx, cy, 1, state.flash);
        } else {
          const f = (p - 0.45) / 0.55;
          state.nucleus = { Z: st.product.Z, N: st.product.N, symbol: st.product.symbol, A: st.product.A };
          drawNucleus(state.nucleus, cx, cy, 1, 1 - f);
          const ex = cx + 100 + f * 150;
          const ey = cy - 70;
          if (kind === "bdecay") {
            drawSingle({ kind: "electron" }, ex, ey, "#fde047", "e⁻");
            drawSingle({ kind: "neutrino" }, ex, ey + 34, "#818cf8", "ν̄");
          } else if (kind === "bplus") {
            drawSingle({ kind: "positron" }, ex, ey, "#fde047", "e⁺");
            drawSingle({ kind: "neutrino" }, ex, ey + 34, "#818cf8", "ν");
          } else {
            drawSingle({ kind: "neutrino" }, ex, ey, "#818cf8", "ν");
          }
        }
      }

      function renderEcap(st, p) {
        const cx = 0, cy = 0;
        if (p < 0.42) {
          const f = p / 0.42;
          const x = 250 - (250 - cx) * (f * f * (3 - 2 * f));
          drawNucleus(state.nucleus, cx, cy, 1, 0);
          drawSingle({ kind: "electron" }, x, cy - 55, "#fde047", "e⁻", 1.5);
        } else if (p < 0.55) {
          const f = (p - 0.42) / 0.13;
          state.flash = Math.sin(f * Math.PI);
          drawNucleus(state.nucleus, cx, cy, 1, state.flash);
        } else {
          const f = (p - 0.55) / 0.45;
          state.nucleus = { Z: st.product.Z, N: st.product.N, symbol: st.product.symbol, A: st.product.A };
          drawNucleus(state.nucleus, cx, cy, 1, 1 - f);
          drawSingle({ kind: "neutrino" }, cx - 100 - f * 120, cy - 40, "#818cf8", "ν");
        }
      }

      function renderSpall(st, p) {
        const cx = 0, cy = 0;
        if (p < 0.45) {
          const f = p / 0.45;
          const x = -250 + (250 + cx) * (f * f * (3 - 2 * f));
          drawNucleus(state.nucleus, cx, cy, 1, 0);
          drawSingle(st.proj, x, cy - 30, "#f87171", "", 1.5);
        } else if (p < 0.58) {
          const f = (p - 0.45) / 0.13;
          state.flash = Math.sin(f * Math.PI);
          drawNucleus(state.nucleus, cx, cy, 1, state.flash);
        } else {
          const f = (p - 0.58) / 0.42;
          state.nucleus = { Z: st.product.Z, N: st.product.N, symbol: st.product.symbol, A: st.product.A };
          drawNucleus(state.nucleus, cx, cy, 1, 1 - f);
          const debris = [
            { dx: 120, dy: -70, color: "#94a3b8" },
            { dx: 150, dy: 50, color: "#94a3b8" },
            { dx: 90, dy: 90, color: "#cbd5e1" },
          ];
          debris.forEach(function (d, i) {
            const start = 0.58 + i * 0.06;
            const ef = Math.max(0, Math.min(1, (p - start) / 0.25));
            ctx.beginPath();
            ctx.arc(cx + d.dx * ef, cy + d.dy * ef, 3.4 - 1.2 * ef, 0, Math.PI * 2);
            ctx.fillStyle = d.color;
            ctx.fill();
          });
          if (p > 0.62) {
            ctx.fillStyle = "rgba(203,213,225,0.8)";
            ctx.font = "11px 'Segoe UI', 'Microsoft YaHei', sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("碎片", cx + 150, cy + 95);
          }
        }
      }

      function renderNuproc(st, p) {
        const cx = 0, cy = 0;
        if (p < 0.4) {
          const f = p / 0.4;
          const x = -250 + (250 + cx) * (f * f * (3 - 2 * f));
          drawNucleus(state.nucleus, cx, cy, 1, 0);
          drawSingle({ kind: "neutrino" }, x, cy - 55, "#818cf8", "ν", 1.5);
        } else if (p < 0.52) {
          const f = (p - 0.4) / 0.12;
          state.flash = Math.sin(f * Math.PI);
          drawNucleus(state.nucleus, cx, cy, 1, state.flash);
        } else {
          const f = (p - 0.52) / 0.48;
          state.nucleus = { Z: st.product.Z, N: st.product.N, symbol: st.product.symbol, A: st.product.A };
          drawNucleus(state.nucleus, cx, cy, 1, 1 - f);
          drawSingle({ Z: 1, A: 1, symbol: "p" }, cx + 110 + f * 130, cy - 60, "#f87171", "", 1.6);
        }
      }

      function renderChain(st, p, kind) {
        const cx = 0, cy = 0;
        const dA = state.extra.dA;
        const dZ = state.extra.dZ;
        const total = dA + dZ;
        const prog = Math.max(0, Math.min(1, p));
        const done = Math.floor(prog * total);
        const capturesDone = Math.min(dA, done);
        const decaysDone = Math.max(0, done - dA);
        state.nucleus = {
          Z: st.from.Z + decaysDone,
          N: st.from.N + capturesDone - decaysDone,
          symbol: st.from.symbol,
          A: st.from.A + capturesDone,
        };
        const flashPulse = Math.sin((prog * total - done) * Math.PI);
        const flash = (prog < 1 && flashPulse > 0.5 && (done < dA || (done - dA) < dZ)) ? flashPulse : 0;
        drawNucleus(state.nucleus, cx, cy, 1, flash * 0.8,
          p < 1 ? (kind === "rproc" ? "r-过程链" : "s-过程链") : fmtNuc(st.to));
        ctx.fillStyle = "rgba(96,165,250,0.95)";
        ctx.font = "600 13px 'Segoe UI', 'Microsoft YaHei', sans-serif";
        ctx.textAlign = "center";
        if (p < 1) {
          ctx.fillText(kind === "rproc"
            ? "中子快速接连被俘获…（已 ×" + capturesDone + " / " + dA + "，β⁻ 衰变 ×" + decaysDone + " / " + dZ + "）"
            : "中子逐个被俘获…（已 ×" + capturesDone + " / " + dA + "，β⁻ 衰变 ×" + decaysDone + " / " + dZ + "）",
            cx, cy + 92);
        } else {
          state.nucleus = { Z: st.to.Z, N: st.to.N, symbol: st.to.symbol, A: st.to.A };
          drawNucleus(state.nucleus, cx, cy, 1, 0.1);
          ctx.fillText("（链式示意，中子俘获与 β⁻ 衰变交替进行）", cx, cy + 92);
        }
      }

      function renderExplosion(st, p) {
        const cx = 0, cy = 0;
        const to = state.extra.to;
        const bursts = [0.1, 0.3, 0.5, 0.68, 0.84];
        let flash = 0;
        let burstDone = 0;
        bursts.forEach(function (b, i) {
          if (p >= b) {
            burstDone++;
            const f = Math.max(0, 1 - (p - b) / 0.18);
            flash = Math.max(flash, f);
          }
        });
        if (p < 0.92) {
          const frac = Math.min(1, p / 0.92);
          state.nucleus = {
            Z: st.from.Z + Math.round((to.Z - st.from.Z) * frac),
            N: st.from.N + Math.round((to.N - st.from.N) * frac),
            symbol: to.symbol,
            A: st.from.A + Math.round((to.A - st.from.A) * frac),
          };
          drawNucleus(state.nucleus, cx, cy, 1, flash * 0.9, "爆发核合成中…");
        } else {
          state.nucleus = { Z: to.Z, N: to.N, symbol: to.symbol, A: to.A };
          drawNucleus(state.nucleus, cx, cy, 1, flash * 0.15);
        }
        if (flash > 0.02) {
          ctx.strokeStyle = "rgba(253,224,71," + (0.55 * flash) + ")";
          ctx.lineWidth = 2;
          for (let i = 0; i < 6; i++) {
            const a = (i / 6) * Math.PI * 2;
            ctx.beginPath();
            ctx.moveTo(cx + Math.cos(a) * 46, cy + Math.sin(a) * 46);
            ctx.lineTo(cx + Math.cos(a) * (70 + 26 * flash), cy + Math.sin(a) * (70 + 26 * flash));
            ctx.stroke();
          }
        }
      }

      function renderPrimordial(st, p) {
        const f = Math.min(1, p / 0.35);
        drawNucleus(state.nucleus, 0, 0, f, 0);
        if (p > 0.4) {
          ctx.fillStyle = "rgba(226,232,240,0.8)";
          ctx.font = "13px 'Segoe UI', 'Microsoft YaHei', sans-serif";
          ctx.textAlign = "center";
          ctx.fillText("大爆炸后冷却，夸克结合成质子", 0, 110);
        }
      }

      function renderScene() {
        ctx.clearRect(0, 0, W, H);
        const legendItems = [
          ["#f87171", "p⁺ 质子"], ["#94a3b8", "n 中子"], ["#fde047", "e⁻ 电子"],
          ["#818cf8", "ν 中微子"], ["#fbbf24", "γ 光子"], ["#e879f9", "α 粒子"],
        ];
        ctx.font = "10px 'Segoe UI', 'Microsoft YaHei', sans-serif";
        legendItems.forEach(function (it, i) {
          const lx = 14 + i * 96;
          ctx.beginPath();
          ctx.arc(lx, H - 16, 4.5, 0, Math.PI * 2);
          ctx.fillStyle = it[0];
          ctx.fill();
          ctx.fillStyle = "rgba(226,232,240,0.85)";
          ctx.textAlign = "left";
          ctx.fillText(it[1], lx + 9, H - 12.5);
        });
        ctx.save();
        ctx.translate(W / 2, H / 2 - 8);
        ctx.fillStyle = "rgba(148,163,184,0.14)";
        ctx.font = "11px sans-serif";
        ctx.textAlign = "left";
        ctx.fillText("◦", -330, -170);
        ctx.fillText("◦", 280, -120);
        ctx.fillText("◦", -300, 160);
        ctx.fillText("◦", 310, 150);
        const st = scene.stages[stageIdx];
        if (!st) return;
        if (st.type === "fusion" || st.type === "capture") renderFusion(st, state.p);
        else if (st.type === "lab") renderLab(st, state.p);
        else if (st.type === "bdecay") renderDecay(st, state.p, "bdecay");
        else if (st.type === "bplus") renderDecay(st, state.p, "bplus");
        else if (st.type === "ecap") renderEcap(st, state.p);
        else if (st.type === "spall") renderSpall(st, state.p);
        else if (st.type === "nuproc") renderNuproc(st, state.p);
        else if (st.type === "rproc" || st.type === "sproc") renderChain(st, state.p, st.type);
        else if (st.type === "explosion") renderExplosion(st, state.p);
        else if (st.type === "primordial") renderPrimordial(st, state.p);
        else if (st.type === "atom") drawShells(state.nucleus, state.p);
        ctx.restore();
      }

      let lastTs = null;
      function frame(ts) {
        if (lastTs === null) lastTs = ts;
        const dt = Math.min(0.05, (ts - lastTs) / 1000);
        lastTs = ts;
        if (playing) update(dt);
        renderScene();
        if (callbacks.onUpdate) callbacks.onUpdate(state.p, stageIdx, playing);
        if (!finished) {
          rafId = requestAnimationFrame(frame);
        }
      }

      const player = {
        play: function () {
          if (finished) { this.restart(); return; }
          if (!playing) {
            playing = true;
            lastTs = null;
            rafId = requestAnimationFrame(frame);
          }
        },
        pause: function () { playing = false; },
        isPlaying: function () { return playing; },
        restart: function () {
          t = 0; stageIdx = 0; setupStage(scene.stages[0]); playing = true; finished = false; lastTs = null;
          if (callbacks.onStage) callbacks.onStage(0, scene.stages.length, stageCaption(scene.stages[0]));
          if (rafId) cancelAnimationFrame(rafId);
          rafId = requestAnimationFrame(frame);
        },
        setSpeed: function (s) { speed = s; },
        setAnnotate: function (v) { annotate = !!v; },
        skipAtom: function () {
          let total = 0;
          scene.stages.forEach(function (s) { total += (Sim.DUR[s.type] || 2); });
          t = total;
          stageIdx = scene.stages.length - 1;
          setupStage(scene.stages[stageIdx]);
          state.p = 1;
          playing = false;
          finished = true;
          if (rafId) cancelAnimationFrame(rafId);
          if (callbacks.onStage) callbacks.onStage(stageIdx, scene.stages.length, stageCaption(scene.stages[stageIdx]));
          renderScene();
          if (callbacks.onFinish) callbacks.onFinish();
        },
        destroy: function () {
          if (rafId) cancelAnimationFrame(rafId);
          playing = false;
        },
      };

      setupStage(scene.stages[0]);
      if (callbacks.onStage) callbacks.onStage(0, scene.stages.length, stageCaption(scene.stages[0]));
      rafId = requestAnimationFrame(frame);
      return player;
    },
  };

  global.Sim = Sim;
})(typeof window !== "undefined" ? window : globalThis);
