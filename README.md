# 元素起源 · 宇宙元素生成示意图

一个开箱即用的交互式科普原型：把 118 种元素按**宇宙核合成来源**着色，并用一条
138 亿年的时间线动画展示每种元素的“诞生时代”。点击任意元素可查看它的来源构成、
宇宙丰度与简短的起源故事。

## 在线访问

正式站点（GitHub Pages，全球可访问）：
<https://yanxinwang-ml.github.io/element-origin/>

源码仓库：<https://github.com/yanxinwang-ml/element-origin>

> 提示：部分网络环境无法直连 `github.io` 域名，若打不开请开启代理/VPN 后访问，
> 或在网络不受限制的环境打开。本地始终可双击 `index.html` 离线使用。

### 本机代理（Clash Verge）说明

本机已安装并配置 Clash Verge（mihomo 内核，混合端口 `127.0.0.1:7897`）。
若你的网络无法访问 GitHub 系站点（`github.com` / `github.io` 连接重置），
按需开启系统代理即可：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\proxy-on.ps1    # 开启
powershell -ExecutionPolicy Bypass -File scripts\proxy-off.ps1   # 关闭
```

也可以在 Clash Verge 主界面点“系统代理”开关，或在代理组（如 `JMS`）里手动选择节点。

## 打开方式

直接双击 `index.html`（纯前端、无外部依赖，离线可用），或本地起一个静态服务：

```powershell
python -m http.server 8000
```

然后访问 `http://localhost:8000`。

## 功能

- **周期表**：118 个元素格子，颜色 = 主导来源；悬停显示提示，点击打开详情面板。
- **时间线动画**：播放/暂停/调速/拖动。元素在其主导来源的诞生时代被点亮
  （大爆炸 → 第一批恒星 → 中子星并合 → AGB 星 s-过程 → Ia 型超新星 → 太阳系形成
  → 实验室合成）。年代为科普示意值。
- **图例筛选**：点击某个来源分类，只高亮该来源的元素。
- **详情面板**：每条**生成路径**（生成场所 + 过程 + 具体反应式 + 占比，多来源
  会全部列出）、来源占比堆叠条、太阳系丰度（log ε，H = 12）、元素叙事、发现者/年份。
- **核反应动画模拟**：点击任意生成路径（或路径上的“▶ 动画模拟”按钮）弹出动画窗口，
  用 Canvas 模拟原子核的碰撞与变化——质子（红）、中子（灰）的聚变、中子俘获、
  β 衰变 / β⁺ 衰变（n↔p 转化 + 电子/中微子发射）、电子俘获、宇宙线散裂、
  超新星爆炸核合成、实验室重离子融合等，最后电子填充壳层形成中性原子。
  动画可播放/暂停/重播/调速（0.5×/1×/2×）；壳层阶段默认仅约 1 秒，且可随时
  点“跳过壳层”直接跳到结尾（播放结束后点“重播”可重新开始）。
- **粒子标注**：动画画面左上角常驻粒子图例（红=质子 p⁺、灰=中子 n、黄=电子 e⁻、
  靛蓝波浪=中微子 ν、金色=光子 γ、品红=α 粒子），每个核子上直接标注 p/n
  （可点“核子标注”开关切换；核子很多时自动抽样标注并保留精确计数），
  出射粒子带文字标签，步骤字幕显示完整粒子构成（如 ¹²C(6p+6n)）。

## 数据来源

| 数据 | 来源 |
| --- | --- |
| 元素来源分类与占比 | Jennifer Johnson（俄亥俄州立大学）《Origin of the Elements in the Solar System》，经 CMG Lee SVG 解析（[sitrucp/periodic_elements](https://github.com/sitrucp/periodic_elements)） |
| 太阳系丰度 | Lodders, Palme & Gail (2009)，取自 [NuGrid/iniabu](https://github.com/NuGrid/iniabu) |
| 元素中文名/发现信息 | 内置对照表 + [Periodic Table of Elements.csv](https://gist.github.com/c2dd862cd38f21b0ad36b8f96b4bf1ee) |

原始数据保存在 `data/` 目录（`periodic_elements.json`、`lodders09.dat`、
`element_metadata.csv`），生成脚本为 `src/generate_data.py`：

```powershell
python src/generate_data.py
```

## 已知限制

- 颜色只表示**主导**来源；多来源占比见详情面板。个别元素（锂、碳、铁等）的来源
  占比在不同文献中仍有讨论。
- 时间线上的年代是教学示意（例如“中子星并合约 130 亿年前开始”），并非精确值。
- 104–118 号元素（人工合成）在 Johnson 原始 SVG 中缺失或为图例单元格，本项目中
  统一按“人工合成”处理。
- 动画中的核素与反应式是**示意性主通道**（使用常见/代表同位素），粒子数严格守恒，
  但长链过程（s/r-过程）以压缩动画 + 计数器呈现，不代表真实每一步。

## 文件结构

```text
index.html            交互页面（HTML + CSS + JS，单文件）
elements_data.js      生成的元素数据集（勿手改，重新运行生成脚本）
simulator.js          Canvas 核反应动画引擎（无依赖）
src/generate_data.py  数据生成脚本
src/deploy_github.py  通过 GitHub REST API 部署到 Pages 的脚本
data/                 原始数据（来源见上表）
README.md
```
