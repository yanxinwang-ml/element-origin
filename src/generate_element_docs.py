# -*- coding: utf-8 -*-
"""Generate one Markdown document per element (docs/elements/) plus an index."""

import json
import os
import re

OUT_DIR = "docs/elements"
SITE_URL = "https://yanxinwang-ml.github.io/element-origin/"

SUP = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}


def sup(n):
    return "".join(SUP[c] for c in str(n))


def load_data():
    raw = open("elements_data.js", encoding="utf-8").read()
    raw = raw[raw.index("=") + 1:].strip().rstrip(";")
    return json.loads(raw)


DATA = load_data()
CATS = DATA["categories"]
ELEMENTS = DATA["elements"]
ZMAP = {e["symbol"]: e["z"] for e in ELEMENTS}


def parse_nuclide(tok):
    tok = tok.strip()
    special = {"n": ("n", 0, 1), "p": ("p", 1, 1), "D": ("H", 1, 2), "d": ("H", 1, 2)}
    if tok in special:
        sym, z, a = special[tok]
        return {"sym": sym, "z": z, "a": a, "label": sym if sym in ("n", "p") else "²H"}
    if tok in ("g", "γ"):
        return {"sym": "γ", "z": None, "a": None, "label": "γ"}
    if tok in ("e", "e-"):
        return {"sym": "e⁻", "z": None, "a": None, "label": "e⁻"}
    if tok == "e+":
        return {"sym": "e⁺", "z": None, "a": None, "label": "e⁺"}
    if tok in ("v", "nu"):
        return {"sym": "ν", "z": None, "a": None, "label": "ν"}
    m = re.match(r"^([A-Za-z]{1,2})(\d+)$", tok)
    if not m:
        return {"sym": tok, "z": None, "a": None, "label": tok}
    sym = m.group(1)[0].upper() + m.group(1)[1:].lower()
    a = int(m.group(2))
    z = ZMAP.get(sym)
    return {"sym": sym, "z": z, "a": a, "label": sup(a) + sym}


def fmt_nuc(n):
    if n["z"] is None:
        return n["label"]
    return "%s(%dp+%dn)" % (n["label"], n["z"], n["a"] - n["z"])


def build_chain(recipe):
    """Human-readable step list with proton/neutron counts from a recipe."""
    steps = []
    for stage in recipe.split(";"):
        typ, body = stage.split(":", 1)
        if typ in ("fusion", "capture", "lab"):
            lhs, rhs = body.split("->")
            lefts = [fmt_nuc(parse_nuclide(x)) for x in lhs.split("+")]
            parts = rhs.split("+")
            prod = fmt_nuc(parse_nuclide(parts[0]))
            ej = []
            for e in parts[1:]:
                mm = re.match(r"^(\d+)?(n|p|a|g|e|v)$", e.strip())
                if not mm:
                    continue
                cnt = int(mm.group(1)) if mm.group(1) else 1
                name = {"n": "n", "p": "p", "a": "α", "g": "γ", "e": "e⁻", "v": "ν"}[mm.group(2)]
                ej.append(("%d×" % cnt if cnt > 1 else "") + name)
            if typ == "lab":
                steps.append(" + ".join(lefts) + " → 复合核* → " + prod + (" + " + " ".join(ej) if ej else ""))
            else:
                steps.append(" + ".join(lefts) + " → " + prod + (" + " + " ".join(ej) if ej else ""))
        elif typ in ("bdecay", "bplus", "ecap"):
            lhs, rhs = body.split("->")
            src = fmt_nuc(parse_nuclide(lhs))
            dst = fmt_nuc(parse_nuclide(rhs))
            if typ == "bdecay":
                steps.append(src + " → " + dst + " + e⁻ + ν̄")
            elif typ == "bplus":
                steps.append(src + " → " + dst + " + e⁺ + ν")
            else:
                steps.append(src + " + e⁻ → " + dst + " + ν")
        elif typ in ("rproc", "sproc"):
            lhs, rhs = body.split("->")
            frm = parse_nuclide(lhs)
            to = parse_nuclide(rhs)
            dA = to["a"] - frm["a"]
            dZ = to["z"] - frm["z"]
            kind = "快中子俘获" if typ == "rproc" else "慢中子俘获"
            steps.append(
                "%s(种子) → %s ×%d → β⁻ 衰变 ×%d → %s（示意链）"
                % (fmt_nuc(frm), kind, dA, dZ, fmt_nuc(to))
            )
        elif typ == "explosion":
            lhs, rhs = body.split("->")
            steps.append("%s →（爆炸性核合成，示意）→ %s" % (fmt_nuc(parse_nuclide(lhs)), fmt_nuc(parse_nuclide(rhs))))
        elif typ == "spall":
            lhs, rhs = body.split("->")
            lefts = [fmt_nuc(parse_nuclide(x)) for x in lhs.split("+")]
            prod = fmt_nuc(parse_nuclide(rhs))
            steps.append(" + ".join(lefts) + " → " + prod + " + 碎片")
        elif typ == "nuproc":
            lhs, rhs = body.split("->")
            tgt = fmt_nuc(parse_nuclide(lhs))
            prod = fmt_nuc(parse_nuclide(rhs))
            steps.append("ν + " + tgt + " → " + prod + " + p")
        elif typ == "primordial":
            steps.append(fmt_nuc(parse_nuclide(body)) + "（原初质子直接形成，无需反应）")
    return steps


def auto_narrative(el):
    dom = CATS[el["dominant"]]
    dom_pct = next(s["percent"] for s in el["sources"] if s["code"] == el["dominant"])
    others = [s for s in el["sources"] if s["code"] != el["dominant"]]
    txt = "该元素在太阳系中主要由「%s」产生（约 %.0f%%）。%s" % (dom["name"], dom_pct * 100, dom["desc"])
    if others:
        txt += " 其余来自：" + "、".join(
            "「%s」（约 %.0f%%）" % (CATS[s["code"]]["name"], s["percent"] * 100) for s in others
        ) + "。"
    return txt


def slug(en):
    s = en.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def element_md(el):
    lines = []
    lines.append("# %s %s（%s）— 原子序数 %d" % (el["cn"], el["en"].strip(), el["symbol"], el["z"]))
    lines.append("")
    lines.append("## 基本信息")
    lines.append("")
    lines.append("| 项目 | 内容 |")
    lines.append("|---|---|")
    lines.append("| 原子序数 | %d |" % el["z"])
    lines.append("| 符号 | %s |" % el["symbol"])
    lines.append("| 中文名 | %s |" % el["cn"])
    lines.append("| 英文名 | %s |" % el["en"].strip())
    if el["discoverer"]:
        lines.append("| 发现 | %s%s |" % (el["discoverer"].replace("Prehistoric", "古代已知（史前）"), "（" + el["year"] + "）" if el["year"] else ""))
    if el["abundance"] is not None:
        lines.append("| 太阳系丰度 | log ε ≈ %.2f（以氢 = 12 为基准） |" % el["abundance"])
    else:
        synthetic = el["z"] in (43, 61) or el["z"] >= 93
        lines.append("| 太阳系丰度 | %s |" % ("无稳定同位素，天然丰度 ≈ 0（实验室合成）" if synthetic else "放射性元素，天然存在但丰度极低（衰变链产物）"))
    lines.append("")
    lines.append("## 起源概述")
    lines.append("")
    lines.append(el["narrative"] if el["narrative"] else auto_narrative(el))
    lines.append("")
    lines.append("## 生成路径（%d 条）" % len(el["paths"]))
    lines.append("")
    for i, p in enumerate(el["paths"], 1):
        cat = CATS[p["code"]]
        lines.append("### 路径 %d：%s（占比 %.0f%%）" % (i, cat["name"], p["share"] * 100))
        lines.append("")
        lines.append("| 项目 | 内容 |")
        lines.append("|---|---|")
        lines.append("| 生成场所 | %s |" % p["site"])
        lines.append("| 过程 | %s |" % p["process"])
        lines.append("| 占太阳系来源 | %.0f%% |" % (p["share"] * 100))
        lines.append("| 主要反应 | %s |" % p["reaction"])
        lines.append("| 动画配方 | `%s` |" % p["recipe"])
        lines.append("")
        lines.append("**核素变化链：**")
        lines.append("")
        for j, step in enumerate(build_chain(p["recipe"]), 1):
            lines.append("%d. %s" % (j, step))
        lines.append("")
        lines.append(cat["desc"])
        lines.append("")
    lines.append("## 参考资料")
    lines.append("")
    lines.append("- Jennifer Johnson, *Origin of the Elements in the Solar System*, Ohio State University（来源占比数据）。")
    lines.append("- Lodders, Palme & Gail (2009), *Abundances of the Elements in the Solar System*（丰度数据）。")
    lines.append("- 本站交互页面：[元素起源 · 宇宙元素生成示意图](%s)（周期表、时间线动画与核反应模拟）。" % SITE_URL)
    lines.append("- 相关文档：[元素起源文档索引](./README.md)。")
    lines.append("")
    return "\n".join(lines)


def index_md():
    lines = []
    lines.append("# 元素起源 · 逐元素文档")
    lines.append("")
    lines.append("本站为 118 种化学元素各生成一份起源说明文档，内容包括：基本信息、")
    lines.append("太阳系来源构成、每条核合成生成路径（生成场所 / 过程 / 主要反应 / 核素变化链）")
    lines.append("与参考资料。来源分类基于 Jennifer Johnson 的《Origin of the Elements in the Solar System》，")
    lines.append("丰度数据来自 Lodders et al. (2009)。")
    lines.append("")
    lines.append("| 原子序数 | 符号 | 中文名 | 英文名 | 主导来源 | 文档 |")
    lines.append("|---|---|---|---|---|---|")
    for el in ELEMENTS:
        dom = CATS[el["dominant"]]["name"]
        link = "%03d-%s.md" % (el["z"], slug(el["en"]))
        lines.append("| %d | %s | %s | %s | %s | [查看](./%s) |" % (
            el["z"], el["symbol"], el["cn"], el["en"].strip(), dom, link))
    lines.append("")
    lines.append("在线交互页面：[元素起源](%s)" % SITE_URL)
    lines.append("")
    return "\n".join(lines)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    count = 0
    for el in ELEMENTS:
        fname = "%03d-%s.md" % (el["z"], slug(el["en"]))
        with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
            f.write(element_md(el))
        count += 1
    with open(os.path.join(OUT_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(index_md())
    print("generated", count, "element docs + README index in", OUT_DIR)


if __name__ == "__main__":
    main()
