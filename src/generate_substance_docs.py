# -*- coding: utf-8 -*-
"""Generate Markdown docs for common inorganic substances (docs/substances/).
Repo-only content: the interactive site does not reference these files.
"""

import json
import os
import re

OUT_DIR = "docs/substances"
SITE_URL = "https://yanxinwang-ml.github.io/element-origin/"

# ---- load element data for cross links ----
raw = open("elements_data.js", encoding="utf-8").read()
DATA = json.loads(raw[raw.index("=") + 1:].strip().rstrip(";"))
ELEMENTS = DATA["elements"]
BY_SYMBOL = {e["symbol"]: e for e in ELEMENTS}


def element_doc_link(symbol):
    el = BY_SYMBOL.get(symbol)
    if not el:
        return None
    en = re.sub(r"[^a-z0-9]+", "-", el["en"].strip().lower()).strip("-")
    return "../elements/%03d-%s.md" % (el["z"], en), "%s（%s）" % (el["cn"], symbol)


# name_en is used only for the file slug
SUBSTANCES = [
    {
        "cn": "水", "en": "water", "formula": "H₂O",
        "mass": "18.02", "state": "常温下为无色、无味液体",
        "elems": ["H", "O"],
        "structure": "V 形（弯曲形）分子，结构式 H–O–H，键角约 104.5°；O 原子带有 2 对孤对电子。",
        "bond": "极性共价键（O–H），分子间存在氢键",
        "polar": "极性分子",
        "principle": [
            "氧原子外层有 6 个电子，还需 2 个电子才能满足 8 电子（八隅体）稳定结构；两个氢原子各提供 1 个电子，与氧共用形成 2 个 O–H 共价键。",
            "氧的电负性（3.44）明显大于氢（2.20），共用电子对偏向氧，使 O–H 键成为极性键；分子呈 V 形、电荷分布不对称，故水是极性分子。",
            "一个水分子中带正电的氢与另一个水分子中带负电的氧之间形成氢键，使水的沸点、比热异常高，这也是冰能漂浮、水成为生命溶剂的原因。",
        ],
        "prep": [
            "化合：2H₂ + O₂ ——点燃→ 2H₂O（氢气在氧气中燃烧，也是火箭燃料的主要反应之一）。",
            "电解：2H₂O ——通电→ 2H₂↑ + O₂↑（同时制得氢气和氧气）。",
            "中和：H⁺ + OH⁻ → H₂O（酸与碱反应的实质）。",
        ],
        "uses": ["生命活动必需溶剂", "饮用、农业灌溉", "工业冷却剂与反应介质"],
    },
    {
        "cn": "氢气", "en": "hydrogen", "formula": "H₂",
        "mass": "2.016", "state": "常温下为无色、无味气体，密度最小",
        "elems": ["H"],
        "structure": "双原子分子，结构式 H–H，两个氢原子以单键相连。",
        "bond": "非极性共价键（H–H）",
        "polar": "非极性分子",
        "principle": [
            "每个氢原子只有 1 个电子，两个氢原子各贡献 1 个电子形成一对共用电子对，使每个氢都达到类似氦的 2 电子稳定结构。",
            "H₂ 分子比两个孤立的氢原子能量更低（键能约 436 kJ/mol），因此自然界中氢通常以 H₂ 而非单原子形式存在。",
        ],
        "prep": [
            "活泼金属与酸：Zn + 2HCl → ZnCl₂ + H₂↑（实验室常用）。",
            "电解水：2H₂O ——通电→ 2H₂↑ + O₂↑。",
            "工业水煤气：C + H₂O ——高温→ CO + H₂。",
        ],
        "uses": ["合成氨（Haber 法）原料", "加氢反应与还原剂", "燃料电池与清洁能源"],
    },
    {
        "cn": "氧气", "en": "oxygen", "formula": "O₂",
        "mass": "32.00", "state": "常温下为无色、无味气体，微溶于水",
        "elems": ["O"],
        "structure": "双原子分子，结构式 O=O，氧原子间以双键相连（实际为三线态，有两个未成对电子，具顺磁性）。",
        "bond": "非极性共价键（O=O 双键）",
        "polar": "非极性分子",
        "principle": [
            "每个氧原子外层有 6 个电子，两个氧原子各提供 2 个电子形成两对共用电子对（双键），使每个氧都满足八隅体，且各自保留 2 对孤对电子。",
            "分子轨道理论还表明 O₂ 有 2 个未成对电子，因此氧气具有顺磁性，可被液氧磁化这一性质证实。",
        ],
        "prep": [
            "实验室：2H₂O₂ ——MnO₂催化→ 2H₂O + O₂↑；2KMnO₄ ——加热→ K₂MnO₄ + MnO₂ + O₂↑；2KClO₃ ——MnO₂加热→ 2KCl + 3O₂↑。",
            "电解水：2H₂O ——通电→ 2H₂↑ + O₂↑。",
            "工业：空气液化后分馏（利用氮、氧沸点不同）或膜分离法。",
        ],
        "uses": ["呼吸与医疗供氧", "助燃（炼钢、焊接、火箭）", "废水处理与氧化工艺"],
    },
    {
        "cn": "氮气", "en": "nitrogen", "formula": "N₂",
        "mass": "28.01", "state": "常温下为无色、无味气体，约占空气体积的 78%",
        "elems": ["N"],
        "structure": "双原子分子，结构式 N≡N，氮原子间以三键相连。",
        "bond": "非极性共价键（N≡N 三键，键能约 946 kJ/mol）",
        "polar": "非极性分子",
        "principle": [
            "每个氮原子外层有 5 个电子，还需 3 个电子达到八隅体；两个氮原子各提供 3 个电子形成三对共用电子对（三键）。",
            "三键键能极高，使 N₂ 化学性质非常稳定，常温下很难反应，这也是合成氨必须使用高温高压和催化剂的原因。",
        ],
        "prep": [
            "工业：空气液化分馏（氮气先于氧气蒸出）。",
            "实验室：NaNO₂ + NH₄Cl ——加热→ NaCl + 2H₂O + N₂↑（亚硝酸铵分解）。",
        ],
        "uses": ["合成氨与氮肥原料", "食品与金属保护气", "液氮制冷"],
    },
    {
        "cn": "臭氧", "en": "ozone", "formula": "O₃",
        "mass": "48.00", "state": "常温下为淡蓝色气体，有特殊气味",
        "elems": ["O"],
        "structure": "V 形分子，键角约 116.8°；两个 O–O 键实际为单双键共振，键级约 1.5。",
        "bond": "极性共价键（O–O，存在共振结构）",
        "polar": "极性分子",
        "principle": [
            "3 个氧原子中，中心氧与两侧氧各形成一个 O–O 键，并保留 1 对孤对电子；两个 O–O 键之间发生单双键共振，使两个键完全相同。",
            "臭氧中氧的平均氧化态为 0，但分子不稳定，容易分解为普通氧气并放出能量。",
        ],
        "prep": [
            "放电或紫外线：3O₂ ——放电/紫外→ 2O₃（闪电后的清新气味、复印机附近气味即源于此）。",
        ],
        "uses": ["饮用水与空气消毒", "臭氧层吸收太阳紫外线", "氧化漂白"],
    },
    {
        "cn": "过氧化氢", "en": "hydrogen-peroxide", "formula": "H₂O₂",
        "mass": "34.01", "state": "纯品为无色粘稠液体，水溶液俗称双氧水",
        "elems": ["H", "O"],
        "structure": "开链结构 H–O–O–H，O–O 单键连接两个 O–H。",
        "bond": "极性共价键（O–H、O–O）",
        "polar": "极性分子",
        "principle": [
            "每个氧原子与一个氢和一个氧各成键，满足八隅体；分子中氧的氧化态为 −1（介于 O₂ 的 0 与 H₂O 的 −2 之间），因此不稳定，容易发生歧化分解。",
            "分解反应：2H₂O₂ → 2H₂O + O₂↑（放热，MnO₂ 等可催化）。",
        ],
        "prep": [
            "BaO₂ + H₂SO₄ → BaSO₄↓ + H₂O₂（实验室经典方法）。",
            "工业：硫酸氢铵电解后水解制得。",
        ],
        "uses": ["伤口消毒", "漂白与去污", "环保氧化剂"],
    },
    {
        "cn": "二氧化碳", "en": "carbon-dioxide", "formula": "CO₂",
        "mass": "44.01", "state": "常温下为无色无味气体，可溶于水；固态称干冰",
        "elems": ["C", "O"],
        "structure": "直线形分子，结构式 O=C=O，两个 C=O 双键对称排列。",
        "bond": "极性共价键（C=O），分子整体对称",
        "polar": "非极性分子",
        "principle": [
            "碳原子外层有 4 个电子，与两个氧原子各形成双键（共用两对电子），使碳和两个氧都满足八隅体。",
            "两个 C=O 键方向相反、偶极相互抵消，因此分子整体为非极性；CO₂ 可溶于水生成碳酸 H₂CO₃（弱酸）。",
        ],
        "prep": [
            "燃烧：C + O₂ ——点燃→ CO₂；含碳燃料充分燃烧的主要产物。",
            "实验室：CaCO₃ + 2HCl → CaCl₂ + H₂O + CO₂↑。",
            "工业/高温：CaCO₃ ——高温→ CaO + CO₂↑；发酵与呼吸作用也产生 CO₂。",
        ],
        "uses": ["灭火器", "碳酸饮料与干冰", "光合作用原料、温室气体"],
    },
    {
        "cn": "一氧化碳", "en": "carbon-monoxide", "formula": "CO",
        "mass": "28.01", "state": "常温下为无色无味气体，有毒（与血红蛋白结合）",
        "elems": ["C", "O"],
        "structure": "直线形分子，结构式 C≡O，碳氧之间为三键（含一个配位键），碳端保留 1 对孤对电子。",
        "bond": "极性共价键（C≡O）",
        "polar": "极性很弱的极性分子",
        "principle": [
            "碳与氧各提供部分电子形成三键，使两者都满足八隅体；碳端的孤对电子使 CO 可作配体（如与血红蛋白中的 Fe²⁺ 结合）。",
            "CO 是碳不完全燃烧的产物，具有较强的还原性，可将金属氧化物还原为金属。",
        ],
        "prep": [
            "不完全燃烧：2C + O₂ ——氧气不足→ 2CO。",
            "工业：C + H₂O ——高温→ CO + H₂（水煤气）；HCOOH ——浓硫酸加热→ CO↑ + H₂O。",
        ],
        "uses": ["冶炼金属的还原剂（高炉炼铁）", "合成气（与 H₂ 混合）原料", "燃料（需注意通风防中毒）"],
    },
    {
        "cn": "氨", "en": "ammonia", "formula": "NH₃",
        "mass": "17.03", "state": "常温下为无色、有刺激性气味气体，极易液化",
        "elems": ["N", "H"],
        "structure": "三角锥形分子，键角约 107°，N 原子顶端带 1 对孤对电子。",
        "bond": "极性共价键（N–H），分子间有氢键",
        "polar": "极性分子",
        "principle": [
            "氮原子有 5 个价电子，与 3 个氢各成 1 个共价键后仍剩 1 对孤对电子；4 对电子呈四面体取向，孤对电子斥力使键角压缩为约 107°，形成三角锥。",
            "电负性 N(3.04) > H(2.20)，电子云偏向氮，分子不对称 → 强极性；易溶于水（1 体积水约溶解 700 体积氨），水溶液呈碱性：NH₃ + H₂O ⇌ NH₄⁺ + OH⁻。",
        ],
        "prep": [
            "工业 Haber 法：N₂ + 3H₂ ——高温高压、Fe 催化→ 2NH₃。",
            "实验室：2NH₄Cl + Ca(OH)₂ ——加热→ CaCl₂ + 2NH₃↑ + 2H₂O。",
        ],
        "uses": ["氮肥（尿素、硝酸铵等）原料", "硝酸工业原料", "制冷剂与清洁剂"],
    },
    {
        "cn": "氯化氢（盐酸）", "en": "hydrogen-chloride", "formula": "HCl",
        "mass": "36.46", "state": "纯品为无色气体；其水溶液即盐酸（无色液体，强酸）",
        "elems": ["H", "Cl"],
        "structure": "双原子分子，结构式 H–Cl，单键相连。",
        "bond": "强极性共价键（H–Cl）",
        "polar": "极性分子",
        "principle": [
            "氢（1 个电子）与氯（7 个价电子）各提供一个电子形成共用电子对：氢达到 2 电子稳定结构，氯达到八隅体。",
            "氯电负性（3.16）远大于氢，共用电子对强烈偏向氯，H–Cl 键极性很强；溶于水后在水分子的作用下完全电离：HCl → H⁺ + Cl⁻，故盐酸是强酸。",
        ],
        "prep": [
            "化合：H₂ + Cl₂ ——点燃或光照→ 2HCl。",
            "实验室：NaCl + H₂SO₄（浓）——加热→ NaHSO₄ + HCl↑。",
        ],
        "uses": ["金属除锈与酸洗", "制药与化工原料", "实验室常用强酸"],
    },
    {
        "cn": "硫酸", "en": "sulfuric-acid", "formula": "H₂SO₄",
        "mass": "98.08", "state": "纯品为无色油状液体，难挥发，具强吸水性",
        "elems": ["H", "S", "O"],
        "structure": "硫原子为中心四面体：两个 S=O 双键 + 两个 S–OH 单键。",
        "bond": "极性共价键（S=O、S–O、O–H）",
        "polar": "极性分子",
        "principle": [
            "硫原子（6 个价电子）与 4 个氧原子成键：2 个双键、2 个单键（后者再连氢），形成稳定的四面体结构，硫可扩展八隅体（超价）。",
            "两个羟基氢在水中完全电离，第一步 H₂SO₄ → H⁺ + HSO₄⁻（强），第二步 HSO₄⁻ ⇌ H⁺ + SO₄²⁻；浓硫酸还有强吸水性和脱水性。",
        ],
        "prep": [
            "接触法：S（或 FeS₂ 焙烧）→ SO₂ →（V₂O₅ 催化、约 450°C）SO₃ → 溶于浓硫酸再稀释得 H₂SO₄。",
        ],
        "uses": ["化肥（磷肥）与化工原料", "铅蓄电池电解质", "干燥剂与脱水剂"],
    },
    {
        "cn": "硝酸", "en": "nitric-acid", "formula": "HNO₃",
        "mass": "63.01", "state": "纯品为无色液体，见光或受热分解，具强氧化性",
        "elems": ["H", "N", "O"],
        "structure": "平面三角形：氮为中心，两个 N=O 双键 + 一个 N–OH 单键。",
        "bond": "极性共价键（N=O、N–O、O–H）",
        "polar": "极性分子",
        "principle": [
            "氮原子以 sp² 杂化与 3 个氧成键（两个双键、一个单键），剩余 p 轨道参与形成大π键，结构为平面三角形。",
            "羟基氢完全电离，HNO₃ 是强酸；硝酸中氮为 +5 价（最高价态），因此硝酸具有强氧化性，稀硝酸与浓硝酸氧化能力表现不同。",
        ],
        "prep": [
            "奥斯特瓦尔德（Ostwald）法：NH₃ 催化氧化 → NO → NO₂ → 与水反应：3NO₂ + H₂O → 2HNO₃ + NO。",
        ],
        "uses": ["氮肥（硝酸铵）原料", "炸药（如 TNT 需用混酸硝化）", "金属酸洗与化工"],
    },
    {
        "cn": "氢氧化钠", "en": "sodium-hydroxide", "formula": "NaOH",
        "mass": "40.00", "state": "白色固体，易潮解，水溶液为强碱",
        "elems": ["Na", "H", "O"],
        "structure": "离子化合物：Na⁺ 与 OH⁻（O–H 共价键）通过离子键结合。",
        "bond": "离子键（Na⁺–OH⁻），OH⁻ 内部为共价键",
        "polar": "离子晶体",
        "principle": [
            "钠原子（1 个价电子）极易失去电子形成 Na⁺，氧原子倾向得电子或与氢共用电子形成 OH⁻（羟基）；正负离子靠静电引力（离子键）结合。",
            "NaOH 在水中完全电离：NaOH → Na⁺ + OH⁻，因此是强碱；浓溶液对皮肤、玻璃有强腐蚀性。",
        ],
        "prep": [
            "氯碱工业（电解饱和食盐水）：2NaCl + 2H₂O ——通电→ 2NaOH + H₂↑ + Cl₂↑。",
            "化学法：Na₂CO₃ + Ca(OH)₂ → CaCO₃↓ + 2NaOH。",
        ],
        "uses": ["制皂与造纸", "化工与石油加工", "实验室强碱"],
    },
    {
        "cn": "氢氧化钙", "en": "calcium-hydroxide", "formula": "Ca(OH)₂",
        "mass": "74.09", "state": "白色粉末，微溶于水（水溶液为澄清石灰水）",
        "elems": ["Ca", "H", "O"],
        "structure": "离子化合物：Ca²⁺ 与两个 OH⁻ 通过离子键结合。",
        "bond": "离子键（Ca²⁺–OH⁻）",
        "polar": "离子晶体",
        "principle": [
            "钙原子（2 个价电子）失去两个电子形成 Ca²⁺，与两个 OH⁻ 以离子键结合，满足电荷平衡。",
            "其水溶液呈碱性（中强碱）：Ca(OH)₂ → Ca²⁺ + 2OH⁻（部分电离）；澄清石灰水遇 CO₂ 变浑浊：Ca(OH)₂ + CO₂ → CaCO₃↓ + H₂O，可检验二氧化碳。",
        ],
        "prep": [
            "生石灰消化：CaO + H₂O → Ca(OH)₂（剧烈放热，生成熟石灰）。",
        ],
        "uses": ["建筑砂浆与涂料", "中和酸性土壤", "检验 CO₂ 的澄清石灰水"],
    },
    {
        "cn": "氯化钠", "en": "sodium-chloride", "formula": "NaCl",
        "mass": "58.44", "state": "白色晶体（食盐主要成分），易溶于水",
        "elems": ["Na", "Cl"],
        "structure": "离子晶体：Na⁺ 与 Cl⁻ 交替排列，形成面心立方晶格（每个 Na⁺ 周围 6 个 Cl⁻，反之亦然）。",
        "bond": "离子键",
        "polar": "离子晶体",
        "principle": [
            "钠失 1 个电子成为 Na⁺，氯得 1 个电子成为 Cl⁻，两者因库仑引力结合；正负离子在三维空间周期排列，晶格能很高，使 NaCl 熔点高、硬度较大。",
            "溶于水时离子被水分子包围而分离，溶液能导电；熔融态也能导电（工业电解熔融 NaCl 制钠：2NaCl ——电解熔融→ 2Na + Cl₂↑）。",
        ],
        "prep": [
            "海水晒盐（蒸发结晶）或盐矿开采提纯。",
            "工业以 NaCl 为原料进行氯碱电解、制钠等。",
        ],
        "uses": ["食盐与食品保鲜", "氯碱工业原料", "道路融雪"],
    },
    {
        "cn": "碳酸钠", "en": "sodium-carbonate", "formula": "Na₂CO₃",
        "mass": "105.99", "state": "白色粉末（纯碱/苏打），易溶于水，水溶液呈碱性",
        "elems": ["Na", "C", "O"],
        "structure": "离子化合物：2 个 Na⁺ 与 CO₃²⁻ 结合；CO₃²⁻ 为平面三角形共振离子。",
        "bond": "离子键（Na⁺–CO₃²⁻），CO₃²⁻ 内部为共价键（含共振）",
        "polar": "离子晶体",
        "principle": [
            "CO₃²⁻ 中碳与三个氧成键：一个 C=O 双键与两个 C–O 单键在三个氧之间共振，三个 C–O 键实际等同（键级约 1.33），呈平面三角形。",
            "CO₃²⁻ 水解使溶液呈碱性：CO₃²⁻ + H₂O ⇌ HCO₃⁻ + OH⁻，因此纯碱是重要的工业碱源。",
        ],
        "prep": [
            "侯氏制碱法（联合制碱）：先制 NaHCO₃：NaCl + NH₃ + CO₂ + H₂O → NaHCO₃↓ + NH₄Cl，再加热分解：2NaHCO₃ ——加热→ Na₂CO₃ + H₂O + CO₂↑。",
        ],
        "uses": ["玻璃制造", "洗涤剂与造纸", "面食加工（中和酸）"],
    },
    {
        "cn": "碳酸氢钠", "en": "sodium-bicarbonate", "formula": "NaHCO₃",
        "mass": "84.01", "state": "白色细小晶体（小苏打），可溶于水，水溶液呈弱碱性",
        "elems": ["Na", "H", "C", "O"],
        "structure": "离子化合物：Na⁺ 与 HCO₃⁻ 结合；HCO₃⁻ 含 C=O、C–O 与 O–H。",
        "bond": "离子键（Na⁺–HCO₃⁻），HCO₃⁻ 内部为共价键",
        "polar": "离子晶体",
        "principle": [
            "HCO₃⁻ 是碳酸的酸式根：碳酸 H₂CO₃ 失去一个 H⁺ 后得到 HCO₃⁻，再失去才得 CO₃²⁻，因此 NaHCO₃ 既能与酸反应放出 CO₂，也能与碱反应。",
            "受热分解：2NaHCO₃ ——加热→ Na₂CO₃ + H₂O + CO₂↑，这也是小苏打作膨松剂和灭火剂成分的原理。",
        ],
        "prep": [
            "侯氏/索尔维制碱法中间产物：NaCl + NH₃ + CO₂ + H₂O → NaHCO₃↓ + NH₄Cl（低温下溶解度小而析出）。",
        ],
        "uses": ["烘焙膨松剂", "中和胃酸（抗酸药）", "泡沫灭火器成分"],
    },
    {
        "cn": "氧化钙", "en": "calcium-oxide", "formula": "CaO",
        "mass": "56.08", "state": "白色块状固体（生石灰），遇水剧烈放热",
        "elems": ["Ca", "O"],
        "structure": "离子晶体：Ca²⁺ 与 O²⁻ 以离子键结合，岩盐型结构。",
        "bond": "离子键",
        "polar": "离子晶体",
        "principle": [
            "钙失去 2 个电子成 Ca²⁺，氧得到 2 个电子成 O²⁻，正负离子静电结合形成稳定晶格；O²⁻ 的强碱性使 CaO 为碱性氧化物。",
            "与水反应放热：CaO + H₂O → Ca(OH)₂（放热约 65 kJ/mol），是“生石灰消化”的原理。",
        ],
        "prep": [
            "高温煅烧石灰石：CaCO₃ ——高温→ CaO + CO₂↑。",
        ],
        "uses": ["建筑材料（水泥、石灰浆）", "干燥剂", "炼钢造渣"],
    },
    {
        "cn": "氧化铝", "en": "aluminium-oxide", "formula": "Al₂O₃",
        "mass": "101.96", "state": "白色固体，熔点极高（约 2072°C），两性氧化物",
        "elems": ["Al", "O"],
        "structure": "离子化合物（晶体中 Al³⁺ 与 O²⁻ 规则排列）；α-Al₂O₃（刚玉）硬度极大。",
        "bond": "离子键（Al³⁺–O²⁻），Al–O 有较强共价成分",
        "polar": "离子晶体",
        "principle": [
            "铝失 3 个电子成 Al³⁺，氧得 2 个电子成 O²⁻，按电荷比 2:3 结合为 Al₂O₃；Al³⁺ 电荷高、半径小，Al–O 键结合很强，故熔点极高。",
            "两性：既能与酸反应（Al₂O₃ + 6HCl → 2AlCl₃ + 3H₂O），也能与强碱反应（Al₂O₃ + 2NaOH + 3H₂O → 2Na[Al(OH)₄]）。",
        ],
        "prep": [
            "铝土矿拜耳（Bayer）法提纯：铝土矿用 NaOH 溶解、沉淀、煅烧得 Al₂O₃。",
            "燃烧：4Al + 3O₂ ——点燃→ 2Al₂O₃（铝热反应也会生成）。",
        ],
        "uses": ["电解炼铝原料", "耐火材料与刚玉磨料", "陶瓷与电子器件"],
    },
    {
        "cn": "二氧化硅", "en": "silicon-dioxide", "formula": "SiO₂",
        "mass": "60.08", "state": "常温下为固体（石英、砂子），熔点很高",
        "elems": ["Si", "O"],
        "structure": "共价晶体（原子晶体）：每个 Si 与 4 个 O 以共价键相连，每个 O 连接 2 个 Si，形成三维空间网络（无独立分子）。",
        "bond": "共价键（Si–O）",
        "polar": "原子晶体（不导电）",
        "principle": [
            "硅（4 个价电子）与氧（6 个价电子）通过共价键连接，Si 满足八隅体（与 4 个 O 成 4 个单键），O 与两个 Si 成键也满足八隅体。",
            "整个晶体是一个巨型分子，Si–O 键能高，因此 SiO₂ 硬度大、熔点高；它不与水反应，但能与强碱或氢氟酸反应。",
        ],
        "prep": [
            "硅燃烧：Si + O₂ ——高温→ SiO₂。",
            "自然界大量存在（沙、石英、水晶），工业上用于制玻璃与提纯单质硅（SiO₂ + 2C ——高温→ Si + 2CO↑）。",
        ],
        "uses": ["玻璃与光纤原料", "集成电路硅片原料", "石英钟与耐火材料"],
    },
    {
        "cn": "碳酸钙", "en": "calcium-carbonate", "formula": "CaCO₃",
        "mass": "100.09", "state": "白色固体（石灰石、大理石），难溶于水",
        "elems": ["Ca", "C", "O"],
        "structure": "离子化合物：Ca²⁺ 与 CO₃²⁻ 结合；CO₃²⁻ 为平面三角形共振离子。",
        "bond": "离子键（Ca²⁺–CO₃²⁻），CO₃²⁻ 内部为共价键",
        "polar": "离子晶体",
        "principle": [
            "钙以 Ca²⁺ 存在，碳酸根 CO₃²⁻ 由碳与三个氧共价结合（共振）形成；两者靠离子键构成晶体，难溶于水。",
            "遇酸放出 CO₂：CaCO₃ + 2HCl → CaCl₂ + H₂O + CO₂↑（实验室制 CO₂ 的原理）；高温分解：CaCO₃ ——高温→ CaO + CO₂↑。",
        ],
        "prep": [
            "天然矿藏（石灰石、大理石）开采；生物沉积（贝壳、珊瑚、蛋壳）。",
            "化学合成：CaO + CO₂ → CaCO₃（如石灰乳吸收 CO₂ 碳化）。",
        ],
        "uses": ["建筑材料与水泥", "制取 CaO 与 CO₂", "补钙剂与造纸填料"],
    },
]


def substance_md(s):
    L = []
    L.append("# %s（%s）" % (s["cn"], s["formula"]))
    L.append("")
    L.append("## 基本信息")
    L.append("")
    L.append("| 项目 | 内容 |")
    L.append("|---|---|")
    L.append("| 中文名 | %s |" % s["cn"])
    L.append("| 英文名 | %s |" % s["en"].replace("-", " ").title())
    L.append("| 化学式 | %s |" % s["formula"])
    L.append("| 相对分子质量 | %s g/mol |" % s["mass"])
    L.append("| 状态 | %s |" % s["state"])
    elems = []
    for sym in s["elems"]:
        link = element_doc_link(sym)
        elems.append("**%s**（%d 号元素）" % (sym, BY_SYMBOL[sym]["z"]))
    L.append("| 组成元素 | %s |" % "、".join(elems))
    L.append("| 化学键类型 | %s |" % s["bond"])
    L.append("| 分子极性 | %s |" % s["polar"])
    L.append("")
    L.append("## 组成方式（原子如何结合）")
    L.append("")
    L.append(s["structure"])
    L.append("")
    L.append("## 组成原理（为什么这样结合）")
    L.append("")
    for p in s["principle"]:
        L.append("- " + p)
    L.append("")
    L.append("## 组成元素的宇宙起源")
    L.append("")
    L.append("该物质由以下元素组成，各元素的核合成起源见对应文档：")
    L.append("")
    for sym in s["elems"]:
        link = element_doc_link(sym)
        if link:
            el = BY_SYMBOL[sym]
            dom = DATA["categories"][el["dominant"]]["name"]
            L.append("- [%s](%s)：原子序数 %d，太阳系中的主导来源为「%s」。" % (
                link[1], link[0], el["z"], dom))
    L.append("")
    L.append("## 常见制取")
    L.append("")
    for p in s["prep"]:
        L.append("- " + p)
    L.append("")
    L.append("## 主要用途")
    L.append("")
    for u in s["uses"]:
        L.append("- " + u)
    L.append("")
    L.append("## 参考资料")
    L.append("")
    L.append("- 元素起源数据：Jennifer Johnson, *Origin of the Elements in the Solar System*（Ohio State Univ.）。")
    L.append("- 丰度数据：Lodders, Palme & Gail (2009)。")
    L.append("- 本站交互页面：[元素起源](%s)；元素文档：[索引](../elements/README.md)。" % SITE_URL)
    L.append("")
    return "\n".join(L)


def index_md():
    L = []
    L.append("# 常见无机物 · 组成方式与组成原理")
    L.append("")
    L.append("本文档介绍常见无机物的**组成方式**（原子如何结合成分子/晶体）与**组成原理**")
    L.append("（为什么这样结合：八隅体规则、共价键/离子键、电负性与极性、共振、氢键等），")
    L.append("并关联组成元素的宇宙核合成起源。")
    L.append("")
    L.append("| 物质 | 化学式 | 组成元素 | 主要键型 | 文档 |")
    L.append("|---|---|---|---|---|")
    for i, s in enumerate(SUBSTANCES, 1):
        elems = "、".join("**%s**" % e for e in s["elems"])
        link = "%02d-%s.md" % (i, s["en"])
        L.append("| %s | %s | %s | %s | [查看](./%s) |" % (s["cn"], s["formula"], elems, s["bond"], link))
    L.append("")
    L.append("相关：[元素起源 · 逐元素文档](../elements/README.md) ｜ [在线交互页面](%s)" % SITE_URL)
    L.append("")
    return "\n".join(L)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for i, s in enumerate(SUBSTANCES, 1):
        fname = "%02d-%s.md" % (i, s["en"])
        with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
            f.write(substance_md(s))
    with open(os.path.join(OUT_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write(index_md())
    print("generated", len(SUBSTANCES), "substance docs + README index in", OUT_DIR)


if __name__ == "__main__":
    main()
