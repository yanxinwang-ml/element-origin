# -*- coding: utf-8 -*-
"""
Generate elements_data.js for the interactive "Origin of the Elements" prototype.

Inputs (provenance):
  data/periodic_elements.json  - parsed from CMG Lee's SVG of Jennifer Johnson's
                                 "Origin of the Elements in the Solar System" table
                                 (https://github.com/sitrucp/periodic_elements)
  data/lodders09.dat           - Lodders et al. (2009) proto-solar abundances
                                 (https://github.com/NuGrid/iniabu)
  gist.json                    - element metadata CSV (English names, discoverers)
Output:
  elements_data.js             - window.ELEMENTS_DATA object for the web app
"""

import csv
import io
import json
import math

_raw_text = open("data/periodic_elements.json", encoding="utf-8").read()
_raw_text = _raw_text.replace("var periodic_elements =", "", 1).strip().rstrip(";")
RAW = json.loads(_raw_text)

# element metadata CSV (English names, discoverers, years)
csv_text = open("data/element_metadata.csv", encoding="utf-8").read()
meta = {}
for row in csv.DictReader(io.StringIO(csv_text)):
    try:
        z = int(row["AtomicNumber"])
    except (ValueError, KeyError):
        continue
    meta[z] = {
        "en": row.get("Element", ""),
        "discoverer": row.get("Discoverer", "").strip(),
        "year": row.get("Year", "").strip(),
    }

# ---- Lodders 2009 proto-solar abundances (atomic, relative to Si = 1e6) ----
abund = {}
for line in open("data/lodders09.dat", encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    parts = line.split()
    z, n = int(parts[0]), float(parts[4])
    abund[z] = abund.get(z, 0.0) + n
n_h = abund[1]
log_e = {z: 12.0 + math.log10(n / n_h) for z, n in abund.items()}

# ---- Chinese names for all 118 elements ----
CN_NAMES = {
    1: "氢", 2: "氦", 3: "锂", 4: "铍", 5: "硼", 6: "碳", 7: "氮", 8: "氧",
    9: "氟", 10: "氖", 11: "钠", 12: "镁", 13: "铝", 14: "硅", 15: "磷",
    16: "硫", 17: "氯", 18: "氩", 19: "钾", 20: "钙", 21: "钪", 22: "钛",
    23: "钒", 24: "铬", 25: "锰", 26: "铁", 27: "钴", 28: "镍", 29: "铜",
    30: "锌", 31: "镓", 32: "锗", 33: "砷", 34: "硒", 35: "溴", 36: "氪",
    37: "铷", 38: "锶", 39: "钇", 40: "锆", 41: "铌", 42: "钼", 43: "锝",
    44: "钌", 45: "铑", 46: "钯", 47: "银", 48: "镉", 49: "铟", 50: "锡",
    51: "锑", 52: "碲", 53: "碘", 54: "氙", 55: "铯", 56: "钡", 57: "镧",
    58: "铈", 59: "镨", 60: "钕", 61: "钷", 62: "钐", 63: "铕", 64: "钆",
    65: "铽", 66: "镝", 67: "钬", 68: "铒", 69: "铥", 70: "镱", 71: "镥",
    72: "铪", 73: "钽", 74: "钨", 75: "铼", 76: "锇", 77: "铱", 78: "铂",
    79: "金", 80: "汞", 81: "铊", 82: "铅", 83: "铋", 84: "钋", 85: "砹",
    86: "氡", 87: "钫", 88: "镭", 89: "锕", 90: "钍", 91: "镤", 92: "铀",
    93: "镎", 94: "钚", 95: "镅", 96: "锔", 97: "锫", 98: "锎", 99: "锿",
    100: "镄", 101: "钔", 102: "锘", 103: "铹", 104: "𬬻", 105: "𬭊",
    106: "𬭳", 107: "𬭛", 108: "𬭶", 109: "鿏", 110: "𫟼", 111: "𬬭",
    112: "鿔", 113: "鿭", 114: "𫓧", 115: "镆", 116: "𫟷", 117: "鿬",
    118: "鿫",
}

SYMBOLS = {
    104: "Rf", 105: "Db", 106: "Sg", 107: "Bh", 108: "Hs", 109: "Mt",
    110: "Ds", 111: "Rg", 112: "Cn", 113: "Nh", 114: "Fl", 115: "Mc",
    116: "Lv", 117: "Ts", 118: "Og",
}

EN_FALLBACK = {
    104: "Rutherfordium", 105: "Dubnium", 106: "Seaborgium", 107: "Bohrium",
    108: "Hassium", 109: "Meitnerium", 110: "Darmstadtium", 111: "Roentgenium",
    112: "Copernicium", 113: "Nihonium", 114: "Flerovium", 115: "Moscovium",
    116: "Livermorium", 117: "Tennessine", 118: "Oganesson",
}

# ---- category metadata (Johnson table legend) ----
CATS = {
    "b": {
        "name": "大爆炸核合成",
        "en": "Big Bang fusion",
        "desc": "宇宙诞生后最初约 3–20 分钟内，质子和中子结合成氢、氦及微量锂。",
        "epochGya": 13.8,
        "epochText": "诞生于大爆炸（约 138 亿年前）",
        "color": "#3b82f6",
    },
    "j": {
        "name": "宇宙线散裂",
        "en": "Cosmic ray spallation",
        "desc": "高能宇宙线撞击星际介质中较重的原子核，将其“打碎”成锂、铍、硼等轻元素。",
        "epochGya": 13.6,
        "epochText": "自第一批恒星出现后持续生成（约 136 亿年前至今）",
        "color": "#a855f7",
    },
    "g": {
        "name": "大质量恒星核燃烧/超新星",
        "en": "Exploding massive stars",
        "desc": "大质量恒星内部逐级燃烧氢、氦、碳、氖、氧、硅直到铁；坍缩超新星把产物抛回星际空间。",
        "epochGya": 13.6,
        "epochText": "自第一批大质量恒星起持续生成（约 136 亿年前至今）",
        "color": "#ef4444",
    },
    "o": {
        "name": "中子星并合（r-过程）",
        "en": "Merging neutron stars",
        "desc": "两颗中子星并合时极短时间内连续俘获中子（r-过程），生成金、铂、铀等重元素。2017 年 GW170817 千新星首次直接观测证实。",
        "epochGya": 13.0,
        "epochText": "自早期中子星并合起持续生成（约 130 亿年前至今；2017 年首次直接观测）",
        "color": "#22c55e",
    },
    "y": {
        "name": "低质量恒星死亡（AGB 星，s-过程）",
        "en": "Dying low-mass stars",
        "desc": "低质量恒星演化到渐近巨星分支（AGB）时，慢中子俘获（s-过程）把种子核逐步推向锶、钡、铅等重元素，星风将产物吹回星际空间。",
        "epochGya": 12.5,
        "epochText": "自第一批低质量恒星死亡起持续生成（约 125 亿年前至今）",
        "color": "#f59e0b",
    },
    "c": {
        "name": "白矮星爆发（Ia 型超新星）",
        "en": "Exploding white dwarfs",
        "desc": "白矮星吸积或并合触发碳氧热核爆炸（Ia 型超新星），主要生产铁族元素（Cr、Mn、Fe、Ni 等）。",
        "epochGya": 12.0,
        "epochText": "自第一批 Ia 型超新星起持续生成（约 120 亿年前至今）",
        "color": "#14b8a6",
    },
    "z": {
        "name": "人工合成",
        "en": "Human synthesis",
        "desc": "20 世纪以来在实验室通过核反应人工制造的放射性元素（含锝、钷及 93 号以后的大部分元素）。",
        "epochGya": 8.6e-8,
        "epochText": "20 世纪以来在实验室合成（约 1940 年至今）",
        "color": "#64748b",
    },
}

# ---- curated narratives for well-known elements ----
NARRATIVES = {
    1: "宇宙中质量占比约 75% 的氢几乎全部来自大爆炸。恒星至今仍在把氢聚变成氦，所以宇宙中的“原初氢”在不断被消耗。",
    2: "约 91% 的氦来自大爆炸；恒星聚变也持续生产新的氦（氦在宇宙中质量占比约 25%）。",
    3: "锂的来源很复杂：低质量恒星（AGB 星）、宇宙线散裂与大爆炸各占一部分，其“应该有多少”与观测不符，是天体物理中有名的“宇宙锂问题”。",
    4: "铍几乎全部由宇宙线散裂产生，宇宙中相当稀有。",
    5: "硼同铍一样，主要由宇宙线散裂产生，是罕见的轻元素。",
    6: "碳约 3/4 来自低质量恒星（AGB 星）死亡时抛出的星风，其余来自大质量恒星。它是生命和有机化学的骨架。",
    7: "氮主要来自 AGB 星的 CNO 循环产物抛射，加上大质量恒星的贡献。",
    8: "氧是宇宙中质量丰度第三的元素（仅次于氢、氦），几乎全部由大质量恒星核燃烧产生，主要路径是氦燃烧中碳-12 俘获 α 粒子生成氧-16。",
    26: "铁主要由 Ia 型白矮星爆发贡献（约 2/3），其余来自大质量恒星。铁是核聚变释放能量的“终点”，再往上聚变不再放出能量。",
    43: "地球上没有稳定同位素，通常标注为人工合成；但恒星光谱中确实观测到锝，证明恒星内部 s-过程正在实时发生。",
    61: "与锝类似，钷没有稳定同位素，通常为人工合成产物。",
    63: "铕是典型的 r-过程元素（约 95% 来自中子星并合），常被天文学家用来衡量 r-过程的贡献。",
    79: "金几乎全部由 r-过程产生，主要来自中子星并合。2017 年 GW170817 千新星的光谱中观测到金等重元素，为这一图景提供了直接证据。",
    92: "铀是 r-过程产物，由中子星并合产生。其长半衰期使铀成为测年的“时钟”（如地球年龄约 45.6 亿年）。",
    94: "绝大多数钚是人工合成的，但自然界存在痕量的钚-244——它是太阳系形成前 r-过程事件的残留证据。",
}

# ---------------------------------------------------------------------------
# Generation paths: for every element, one or more "path" entries
# (site + process + reaction). Curated reaction strings for the well-known
# elements; category-level templates cover the rest.
# ---------------------------------------------------------------------------
CATS_SITE = {
    "b": "宇宙大爆炸（t ≈ 3–20 分钟）",
    "j": "银河系星际介质",
    "g": "大质量恒星内部 / 坍缩超新星",
    "c": "白矮星爆发（Ia 型超新星）",
    "y": "AGB 星（低质量恒星晚期）",
    "o": "中子星并合（千新星）",
    "z": "实验室（粒子加速器 / 反应堆）",
}

CATS_PROCESS = {
    "b": "大爆炸核合成（BBN）",
    "j": "宇宙线散裂（spallation）",
    "g": "恒星核燃烧 / 爆炸核合成",
    "c": "热核爆炸核合成",
    "y": "s-过程（慢中子俘获）",
    "o": "r-过程（快中子俘获）",
    "z": "人工核反应",
}

# Common/representative mass number per element, used by the schematic
# s-/r-process animation chains (A = Z + N).
COMMON_A = {
    3: 7, 4: 9, 5: 11, 6: 12, 7: 14, 8: 16, 9: 19, 10: 20, 11: 23, 12: 24,
    13: 27, 14: 28, 15: 31, 16: 32, 17: 35, 18: 36, 19: 39, 20: 40, 21: 45,
    22: 48, 23: 51, 24: 52, 25: 55, 26: 56, 27: 59, 28: 60, 29: 65, 30: 66,
    31: 69, 32: 72, 33: 75, 34: 80, 35: 79, 36: 84, 37: 85, 38: 88, 39: 89,
    40: 90, 41: 93, 42: 98, 43: 99, 44: 102, 45: 103, 46: 106, 47: 107,
    48: 114, 49: 115, 50: 120, 51: 121, 52: 128, 53: 127, 54: 132, 55: 133,
    56: 138, 57: 139, 58: 140, 59: 141, 60: 142, 61: 147, 62: 150, 63: 153,
    64: 158, 65: 159, 66: 164, 67: 165, 68: 166, 69: 169, 70: 173, 71: 175,
    72: 178, 73: 181, 74: 184, 75: 187, 76: 192, 77: 193, 78: 195, 79: 197,
    80: 202, 81: 205, 82: 208, 83: 209, 84: 209, 85: 210, 86: 222, 87: 223,
    88: 226, 89: 227, 90: 232, 91: 231, 92: 238, 93: 237, 94: 244, 95: 241,
    96: 242, 97: 244, 98: 246, 99: 249, 100: 250, 101: 256, 102: 254,
    103: 256, 104: 257, 105: 260, 106: 261, 107: 262, 108: 265, 109: 266,
    110: 269, 111: 272, 112: 283, 113: 283, 114: 289, 115: 289, 116: 293,
    117: 294, 118: 294,
}

# Well-known laboratory synthesis reactions (mass balanced).
LAB_REACTIONS = {
    96: "He4+Pu239->Cm242+n",
    97: "He4+Am241->Bk244+n",
    98: "C12+U238->Cf246+4n",
    99: "N15+U238->Es249+4n",
    100: "O16+U238->Fm250+4n",
    101: "He4+Es253->Md256+n",
    102: "C12+Cm246->No254+4n",
    103: "B11+Cf249->Lr256+4n",
    104: "C12+Cf249->Rf257+4n",
    105: "N15+Cf249->Db260+4n",
    106: "Cr54+Pb208->Sg261+n",
    107: "Cr54+Bi209->Bh262+n",
    108: "Fe58+Pb208->Hs265+n",
    109: "Fe58+Bi209->Mt266+n",
    110: "Ni62+Pb208->Ds269+n",
    111: "Ni64+Bi209->Rg272+n",
    112: "Ca48+U238->Cn283+3n",
    113: "Ca48+Np237->Nh283+2n",
    114: "Ca48+Pu244->Fl289+3n",
    115: "Ca48+Am243->Mc289+2n",
    116: "Ca48+Cm248->Lv293+3n",
    117: "Ca48+Bk249->Ts294+3n",
    118: "Ca48+Cf249->Og294+3n",
}

# Machine-readable reaction recipe per (element, source) used by the animation.
def recipe_for(z, code, symbol):
    if code == "b":
        if z == 1:
            return "primordial:H1"
        if z == 2:
            return "fusion:p+n->D2;fusion:D2+D2->He4"
        if z == 3:
            return "ecap:Be7->Li7"
    if code == "j":
        return {
            3: "spall:p+C12->Li7",
            4: "spall:p+C12->Be9",
            5: "spall:p+C14->B11",
        }.get(z, "spall:p+C12->Li7")
    if code == "g":
        gmap = {
            2: "fusion:H1+H1->D2;fusion:H1+D2->He3;fusion:He3+He3->He4+2p",
            6: "fusion:He4+He4->Be8;fusion:He4+Be8->C12",
            7: "fusion:p+C12->N13;bplus:N13->C13;fusion:p+C13->N14",
            8: "fusion:He4+C12->O16",
            9: "nuproc:Ne20->F19",
            10: "fusion:C12+C12->Ne20+a",
            11: "fusion:C12+C12->Na23+p",
            12: "fusion:He4+Ne20->Mg24",
            13: "fusion:p+Mg26->Al27",
            14: "fusion:O16+O16->Si28",
            15: "fusion:O16+O16->P31+p",
            16: "fusion:O16+O16->S32",
            17: "fusion:He4+P31->Cl35",
            18: "fusion:He4+S32->Ar36",
            19: "fusion:p+Ar38->K39",
            20: "fusion:He4+Ar36->Ca40",
            21: "fusion:p+Ca44->Sc45",
            22: "fusion:He4+Ca44->Ti48",
            23: "fusion:p+Ti50->V51",
            24: "fusion:He4+Ti48->Cr52",
            25: "fusion:p+Cr54->Mn55",
            26: "fusion:He4+Cr52->Fe56",
            27: "fusion:p+Fe58->Co59",
            28: "fusion:He4+Fe56->Ni60",
            29: "fusion:p+Ni64->Cu65",
            30: "fusion:He4+Ni62->Zn66",
        }
        if z in gmap:
            return gmap[z]
        if 31 <= z <= 40:
            return "sproc:Fe56->%s%d" % (symbol, COMMON_A.get(z, 60))
    if code == "y":
        ymap = {
            2: "fusion:H1+H1->D2;fusion:H1+D2->He3;fusion:He3+He3->He4+2p",
            3: "fusion:He3+He4->Be7;ecap:Be7->Li7",
            6: "fusion:He4+He4->Be8;fusion:He4+Be8->C12",
            7: "fusion:p+C12->N13;bplus:N13->C13;fusion:p+C13->N14",
        }
        if z in ymap:
            return ymap[z]
        return "sproc:Fe56->%s%d" % (symbol, COMMON_A.get(z, 60))
    if code == "o":
        return "rproc:Fe56->%s%d" % (symbol, COMMON_A.get(z, 100))
    if code == "c":
        if z == 26:
            return "bplus:Ni56->Co56;bplus:Co56->Fe56"
        return "explosion:Si28->%s%d" % (symbol, COMMON_A.get(z, 40))
    if code == "z":
        if z == 43:
            return "capture:n+Mo98->Mo99;bdecay:Mo99->Tc99"
        if z == 61:
            return "capture:n+Nd146->Nd147;bdecay:Nd147->Pm147"
        if z in LAB_REACTIONS:
            return "lab:" + LAB_REACTIONS[z]
        return "lab:Ca48+Cf249->%s294+3n" % symbol
    return "fusion:He4+C12->O16"  # safe fallback

CURATED = {
    1: {"b": "原初质子：宇宙冷却后由夸克直接结合而成（无需聚变）"},
    2: {"b": "p + n → d；d + d → ⁴He（另有 ³He + n → ⁴He）"},
    3: {
        "b": "⁷Be（电子俘获）→ ⁷Li（BBN 痕量合成）",
        "j": "高能宇宙线撞击 C/N/O 核 → ⁷Li + 碎片",
        "y": "AGB 星：³He + ⁴He → ⁷Be →（电子俘获）⁷Li（Cameron–Fowler 机制）",
    },
    4: {"j": "高能 p + ¹²C / ¹⁶O → ⁹Be + 碎片"},
    5: {"j": "高能 p + ¹²C / ¹⁴N / ¹⁶O → ¹⁰B / ¹¹B + 碎片"},
    6: {
        "y": "AGB 星氦壳燃烧：3 ⁴He → ¹²C（三氦过程），随星风抛射",
        "g": "大质量恒星氦燃烧：3 ⁴He → ¹²C（三氦过程）",
    },
    7: {
        "y": "CNO 循环产物 ¹⁴N，经第三次 dredge-up 与星风抛射",
        "g": "氢燃烧 CNO 循环：¹²C(p,γ)¹³N… → ¹⁴N",
    },
    8: {"g": "氦燃烧：¹²C + ⁴He → ¹⁶O"},
    9: {"g": "超新星中微子过程（ν-过程）：²⁰Ne(ν,ν′p) → ¹⁹F 等"},
    10: {"g": "碳燃烧：¹²C + ¹²C → ²⁰Ne + ⁴He"},
    11: {"g": "碳燃烧：¹²C + ¹²C → ²³Na + p"},
    12: {"g": "碳/氖燃烧：¹²C+¹²C → ²⁴Mg + γ；²⁰Ne(α,γ) → ²⁴Mg"},
    13: {"g": "碳/氖/氧燃烧：²⁵Mg(p,γ)… → ²⁷Al"},
    14: {"g": "氧燃烧：¹⁶O + ¹⁶O → ²⁸Si + ⁴He"},
    15: {"g": "氧燃烧：¹⁶O + ¹⁶O → ³¹P + p"},
    16: {"g": "氧燃烧：¹⁶O + ¹⁶O → ³²S + γ（及硅燃烧）"},
    17: {"g": "氧/硅燃烧：³²S(p,γ)… → ³⁵Cl"},
    18: {"g": "氧/硅燃烧：³⁶Ar"},
    19: {"g": "爆炸硅燃烧：³⁹K（少量）"},
    20: {"g": "硅燃烧 / 爆炸核合成：⁴⁰Ca"},
    21: {"g": "硅燃烧 / 爆炸核合成：铁族附近核素"},
    22: {"g": "硅燃烧 / 爆炸核合成：⁴⁸Ti 等"},
    23: {"g": "爆炸核合成：⁵¹V"},
    24: {"g": "爆炸核合成：⁵²Cr / ⁵³Cr"},
    25: {"g": "爆炸核合成：⁵⁵Mn"},
    26: {
        "g": "大质量恒星硅燃烧 + 坍缩超新星爆发核合成",
        "c": "Ia 型超新星：⁵⁶Ni → ⁵⁶Co → ⁵⁶Fe（衰变链）",
    },
    27: {"g": "爆炸核合成：⁵⁹Co", "c": "Ia 型超新星：⁵⁶Ni 衰变链副产品"},
    28: {"g": "爆炸核合成：⁵⁸Ni / ⁶²Ni", "c": "Ia 型超新星：⁵⁶Ni → ⁵⁸Ni 等"},
    29: {"g": "爆炸核合成：⁶³Cu", "c": "Ia 型超新星核合成"},
    30: {"g": "爆炸核合成：⁶⁴Zn", "c": "Ia 型超新星核合成"},
    38: {"y": "s-过程：Fe 种子核 + 慢中子俘获 → ⁸⁶Sr/⁸⁸Sr"},
    43: {
        "z": "反应堆 / 加速器：⁹⁸Mo + n → ⁹⁹Mo →（β⁻）⁹⁹Tc；或铀裂变产物分离",
        "y": "AGB 星 s-过程实时产物（恒星光谱中观测到 Tc）",
    },
    47: {"o": "r-过程：种子核快中子俘获 → ¹⁰⁷Ag/¹⁰⁹Ag"},
    61: {"z": "核反应堆裂变产物 / 中子辐照：¹⁴⁶Nd + n → ¹⁴⁷Nd →（β⁻）¹⁴⁷Pm"},
    63: {"o": "r-过程：种子核快中子俘获 → ¹⁵¹Eu/¹⁵³Eu"},
    79: {
        "o": "r-过程：种子核（A ≈ 130 附近）快速俘获中子 → ¹⁹⁷Au",
        "y": "s-过程分支：¹⁹⁶Pt(n,γ) → ¹⁹⁷Pt →（β⁻）¹⁹⁷Au",
    },
    82: {
        "y": "s-过程终点：²⁰⁷Pb / ²⁰⁸Pb（中子俘获链末端）",
        "o": "r-过程：丰中子前体 β 衰变 → ²⁰⁸Pb 等",
    },
    83: {"o": "r-过程：²⁰⁹Bi（s-过程链的天然终点之一）"},
    90: {"o": "r-过程：丰中子前体 β 衰变 → ²³²Th"},
    92: {"o": "r-过程：丰中子前体 β 衰变 → ²³⁵U / ²³⁸U"},
    94: {"o": "r-过程：²⁴⁴Pu（太阳系形成前的 r-过程残留，现为痕量）"},
}

def _template_reaction(code, z, symbol):
    if code == "j":
        return "高能宇宙线撞击 C/N/O 较重核 → 轻元素 + 碎片"
    if code == "y":
        return "s-过程：种子核（Fe/Sr/Zr 等）逐次慢中子俘获，两次俘获间 β⁻ 衰变，沿 s-路径到达该元素"
    if code == "o":
        return "r-过程：种子核在 <1 s 内连续俘获数十个中子，生成丰中子核后 β⁻ 衰变为该元素"
    if code == "z":
        return "实验室重离子融合：靶核 + 加速器离子（⁴⁸Ca/⁵⁸Fe 等）→ " + symbol + " + 若干中子"
    if code == "b":
        return "大爆炸核合成（BBN）产物"
    if code == "c":
        return "白矮星热核爆炸：爆炸性硅燃烧 → 铁族（⁵⁶Ni → ⁵⁶Co → ⁵⁶Fe）"
    if code == "g":
        if 31 <= z <= 37:
            return "大质量恒星弱 s-过程：Fe 种子核慢中子俘获"
        if z <= 30:
            return "恒星逐级核燃烧 / 超新星爆炸核合成 → 铁族"
        return "大质量恒星核燃烧 / 坍缩超新星爆发核合成"
    return "（该来源的具体反应见叙事）"

def build_paths(el):
    paths = []
    for s in el["sources"]:
        code = s["code"]
        reaction = CURATED.get(el["z"], {}).get(code)
        if not reaction:
            reaction = _template_reaction(code, el["z"], el["symbol"])
        paths.append({
            "code": code,
            "site": CATS_SITE[code],
            "process": CATS_PROCESS[code],
            "reaction": reaction,
            "share": s["percent"],
            "recipe": recipe_for(el["z"], code, el["symbol"]),
        })
    return paths

# ---- aggregate per-element data ----
by_num = {}
for e in RAW:
    n = e["number"]
    if n not in by_num:
        by_num[n] = {
            "symbol": e["symbol"] or SYMBOLS.get(n, ""),
            "chart_col": e.get("chart_col", 1),
            "chart_row": e.get("chart_row", 1),
            "sources": [],
        }
    sources_agg = by_num[n]["sources"]
    seen_codes = {s["code"] for s in sources_agg}
    for code, pct in zip(e["source"], e["percent"]):
        p = float(pct)
        if p <= 0:
            continue
        if code in seen_codes:
            continue
        seen_codes.add(code)
        sources_agg.append({"code": code, "percent": p})

def layout(n, row, col):
    if 57 <= n <= 71:          # lanthanides
        return 9, 4 + (n - 57)
    if 89 <= n <= 103:         # actinides
        return 10, 4 + (n - 89)
    if n >= 104:               # superheavy elements on row 7
        return 7, n - 100
    return row, col

elements = []
for n in range(1, 119):
    if n >= 104:
        # The parsed SVG contains the *legend* cells at "element" slots 104-110
        # (empty symbols, bogus origins) and nothing at all for 111-118.
        # All of 104-118 are laboratory-synthesized elements.
        by_num[n] = {
            "symbol": SYMBOLS.get(n, f"E{n}"),
            "chart_col": n - 100,
            "chart_row": 7,
            "sources": [{"code": "z", "percent": 1.0}],
        }
    elif n not in by_num:
        by_num[n] = {
            "symbol": SYMBOLS.get(n, f"E{n}"),
            "chart_col": n - 100,
            "chart_row": 7,
            "sources": [{"code": "z", "percent": 1.0}],
        }
    rec = by_num[n]
    sources = sorted(rec["sources"], key=lambda s: -s["percent"])
    dominant = max(sources, key=lambda s: s["percent"])
    row, col = layout(n, rec["chart_row"], rec["chart_col"])
    meta_n = meta.get(n, {})
    elements.append({
        "z": n,
        "symbol": rec["symbol"],
        "cn": CN_NAMES[n],
        "en": meta_n.get("en") or EN_FALLBACK.get(n, rec["symbol"]),
        "row": row,
        "col": col,
        "sources": [{"code": s["code"], "percent": round(s["percent"], 3)} for s in sources],
        "dominant": dominant["code"],
        "epochGya": CATS[dominant["code"]]["epochGya"],
        "abundance": round(log_e[n], 2) if n in log_e else None,
        "discoverer": meta_n.get("discoverer") or "",
        "year": meta_n.get("year") or "",
        "narrative": NARRATIVES.get(n, ""),
        "paths": build_paths({
            "z": n,
            "symbol": rec["symbol"],
            "sources": sources,
        }),
    })

data = {
    "meta": {
        "title": "元素起源 · 宇宙元素生成示意图",
        "source": "Jennifer Johnson (Ohio State) “Origin of the Elements in the Solar System” 分类数据，经 CMG Lee SVG 解析（sitrucp/periodic_elements）；丰度数据 Lodders et al. 2009（iniabu/NuGrid）。",
    },
    "categories": CATS,
    "elements": elements,
}

with open("elements_data.js", "w", encoding="utf-8") as f:
    f.write("// Generated by src/generate_data.py — do not edit by hand.\n")
    f.write("window.ELEMENTS_DATA = ")
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")

print("elements:", len(elements))
print("categories:", list(CATS))
print("with abundance:", sum(1 for e in elements if e["abundance"] is not None))
print("sample:", elements[0], elements[7], elements[78])
