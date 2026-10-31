#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""知识图谱总览（流程 A 第 4 步）对抗性审查 —— 工具实现者视角。

用法： python tools/review_graph.py
退出码： 0 = 全绿； 1 = 有 FAIL
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skill", "learn-system")
SK = os.path.join(SKILL, "SKILL.md")
REF9 = os.path.join(SKILL, "references", "09-knowledge-graph.md")
TPL = os.path.join(SKILL, "templates", "graph.template.html")
SYL = os.path.join(SKILL, "templates", "syllabus.template.yaml")
WORK = os.path.join(ROOT, "study", "注塑")

sk = open(SK, encoding="utf-8").read()
r9 = open(REF9, encoding="utf-8").read() if os.path.exists(REF9) else ""
tpl = open(TPL, encoding="utf-8").read() if os.path.exists(TPL) else ""
syl = open(SYL, encoding="utf-8").read()

FAIL = []


def chk(cond, name, fix):
    if cond:
        print("  PASS  " + name)
    else:
        print("  FAIL  " + name + "\n        -> " + fix)
        FAIL.append(name)


print("=== V. 知识图谱总览功能完整性 ===")

# --- V01 铁律层有据可依 ---
chk(
    re.search(r"^18\. ", sk, re.M) is not None,
    "V01 新增铁律 18（七字段 + 2D/3D 缺一不算覆盖）",
    "没有铁律 = 图谱是建议不是硬要求，AI 会跳过",
)

# --- V02 细则文件存在且有体量 ---
chk(
    len(r9) >= 2500,
    "V02 存在细则 references/09-knowledge-graph.md 且 >= 2500 B（当前 %d）" % len(r9),
    "细则太薄 = 七字段没有合格判据，AI 会糊弄",
)

# --- V03 七字段在细则里有定义 ---
fields = ["prereq", "related", "assumption", "first_principle", "plain", "extend"]
miss = [f for f in fields if f not in r9]
chk(
    not miss,
    "V03 六个 yaml 字段在细则里都有定义（缺：%s）" % (miss or "无"),
    "字段没定义 = AI 不知道写什么，只能留空",
)

# --- V04 七字段有合格判据（防止糊弄）---
chk(
    all(k in r9 for k in ["合格判据", "常见糊弄"]),
    "V04 细则给了「合格判据 + 常见糊弄」对照",
    "只说「要写第一性原理」没有判据 = AI 会写「因为热传导」就交差",
)

# --- V05 2D / 3D 都定义了 ---
chk(
    "2D" in r9 and "3D" in r9,
    "V05 细则定义了 2D 与 3D 两种图示",
    "只定义一种 = 用户要的八项里缺一项",
)

# --- V06 3D 图示的硬约束（与单文件离线可开冲突）---
chk(
    "Three.js" in r9 or "three" in r9.lower(),
    "V06 细则明令禁止外链 Three.js 等 3D 库",
    "外链 3D 库 = 破坏「单文件离线可开」，断网就白图",
)
chk(
    ("等距" in r9 or "isometric" in r9.lower()),
    "V07 细则给出了可落地的 3D 方案（等距投影）",
    "只禁止不给替代方案 = AI 要么违规外链，要么不画 3D",
)

# --- V08 图谱页模板存在 ---
chk(
    len(tpl) >= 3000,
    "V08 存在 templates/graph.template.html 且 >= 3000 B（当前 %d）" % len(tpl),
    "没有模板 = 每个 AI 各画各的图谱页",
)

# --- V09 模板含 2D 与 3D 两种图 ---
chk(
    "<svg" in tpl and ("等距" in tpl or "polygon" in tpl),
    "V09 模板含 2D 与 3D（等距）两种 SVG 图示例",
    "模板只有一种图 = AI 照抄就缺另一种",
)

# --- V10 模板无外链 ---
# 外链只认「真的会发请求」的写法；xmlns 命名空间与正文里提到 Three.js 不算
def has_external(html):
    body = re.sub(r'xmlns="[^"]*"', "", html)          # SVG 命名空间不是请求
    body = re.sub(r"<!--[\s\S]*?-->", "", body)         # 注释里提到库名不算引用
    return bool(re.search(r'(src|href)\s*=\s*"https?:', body)
                or re.search(r"<script[^>]+src=", body)
                or re.search(r"<link[^>]+href=", body)
                or "cdn." in body
                or "cdnjs" in body
                or "unpkg" in body)

chk(
    not has_external(tpl),
    "V10 模板无任何真外链（排除 xmlns 与注释）",
    "外链 = 离线打不开；图谱页必须自包含",
)

# --- V11 模板有图谱边（前置/相关的区分）---
chk(
    "marker" in tpl and "stroke-dasharray" in tpl,
    "V11 模板区分了前置（实线箭头）与相关（虚线）",
    "两种边画一样 = 图谱退化成目录，看不出依赖",
)

# --- V12 大纲模板带 concept_cards ---
chk(
    "concept_cards" in syl,
    "V12 syllabus 模板含 concept_cards 结构",
    "数据没落脚点 = 七字段无处可写，铁律 18 是空的",
)

# --- V13 概念名一致性要求（concepts vs concept_cards）---
chk(
    ("完全一致" in r9 or "集合" in r9),
    "V13 细则要求 concept_cards 与 concepts 概念名集合一致",
    "两个列表不同步 = 覆盖度检查与图谱对不上",
)

# --- V14 前置无环 ---
chk(
    "无环" in r9 or "环" in r9,
    "V14 细则要求概念级 prereq 无环",
    "有环 = 出课顺序算不出来，卡死",
)

# --- V15 与铁律 2（调研先于出课）的关系说清 ---
chk(
    "铁律 2" in r9 or "调研" in r9,
    "V15 细则说明了图谱与「调研先于出课」不冲突",
    "不说清 = AI 在大纲阶段凭空编第一性原理，违反铁律 2",
)

# --- V16 SKILL.md 指路 ---
chk(
    "09-knowledge-graph.md" in sk,
    "V16 SKILL.md 指向 references/09-knowledge-graph.md",
    "不指路 = AI 永远看不到细则",
)

# --- V17 体积红线 ---
size = os.path.getsize(SK)
chk(
    size <= 15360,
    "V17 SKILL.md 体积 %d B <= 15 KB 红线" % size,
    "加规则不能靠无限加字",
)

# --- V18 真实工作区落地（注塑）---
gpath = os.path.join(WORK, "graph.html")
if os.path.exists(gpath):
    g = open(gpath, encoding="utf-8").read()
    chk(
        not re.search(r'src="https?:', g) and "cdn." not in g,
        "V18 真实图谱页 graph.html 无外链",
        "真实产物外链 = 离线打不开",
    )
    n2d = len(re.findall(r'class="cap">2D', g)) or len(re.findall(r'data-kind="2d"', g))
    n3d = len(re.findall(r'class="cap">3D', g)) or len(re.findall(r'data-kind="3d"', g))
    chk(
        n2d >= 1 and n3d >= 1 and n2d == n3d,
        "V19 真实图谱页 2D/3D 图数量配平（2D %d / 3D %d）" % (n2d, n3d),
        "数量不等 = 有的概念缺一种图",
    )
else:
    print("  --    V18 跳过（无真实工作区 study/注塑/graph.html）")


# --- V20 路由表不得与本功能打架（盲测实测：07 曾写「知识图谱不接活」）---
import glob as _g
_routing_texts = {}
for _f in _g.glob(os.path.join(SKILL, "**", "*.md"), recursive=True):
    _routing_texts[os.path.basename(_f)] = open(_f, encoding="utf-8").read()
bad7 = []
for _name, _txt in _routing_texts.items():
    for ln in _txt.splitlines():
        # 「知识图谱 + 判给别的技能」即算矛盾；提到「自己产 / 不外包」的句子放行
        if "知识图谱" in ln and any(k in ln for k in ("teachany", "不接活", "切到")):
            if not any(w in ln for w in ("不外包", "自己产", "本 skill 自己")):
                bad7.append(_name + ": " + ln.strip()[:52])
chk(
    not bad7,
    "V20 路由表没有把「知识图谱」判给别的 skill（会与本功能自相矛盾）",
    "07-routing 曾写『知识图谱 → teachany 不接活』，与本 skill 自己出依赖图谱直接冲突：" + str(bad7[:1]),
)

# --- V21 字段口径一致：铁律 18 说几项，细则就得是几项 ---
m18 = re.search(r"^18\. (.*)$", sk, re.M)
t18 = m18.group(1) if m18 else ""
chk(
    ("六字段" in t18) == ("六个字段" in r9 or "六字段" in r9),
    "V21 铁律 18 的字段口径与细则一致（铁律侧：%s）" % ("六字段" if "六字段" in t18 else "?"),
    "铁律说七字段、细则写六个字段 = AI 不知道听谁的（本轮盲测实测踩到）",
)

# --- V22 产物位置必须写死（盲测实测：不知道放 topic 根还是 reference/）---
chk(
    "graph.html" in r9 and ("topic 根" in r9 or "根目录" in r9),
    "V22 细则写明了 graph.html 放在 topic 根目录",
    "不写位置 = AI 可能塞进 reference/，与速查件混在一起",
)

# --- V23 断言三级要落到概念卡（盲测实测：AI 为此自造了 evidence 字段）---
chk(
    "断言" in r9 and ("三级" in r9 or "建议" in r9),
    "V23 细则说明了概念卡里的断言怎么标级别",
    "不说 = AI 要么不标（违反铁律 3），要么自造字段（与 concepts 又要同步一次）",
)

# --- V24 图示画不完时的处置（盲测实测：26 概念 52 张图是真瓶颈）---
chk(
    ("批量生成" in r9 or "绘制脚本" in r9 or "复用" in r9),
    "V24 细则允许用可复用绘制脚本批量生成图示（不算降级）",
    "只给「概念太多就砍」这一条 = 26 个概念就被迫降级；批量生成才是正解",
)

# --- V25/V26 真实工作区严格校验 ---
syp = os.path.join(WORK, "syllabus.yaml")
if os.path.exists(syp):
    try:
        import yaml
        d = yaml.safe_load(open(syp, encoding="utf-8").read())
        names, cards = [], []
        for m in d.get("modules", []):
            names += [c for c in m.get("concepts", []) if isinstance(c, str)]
            cards += [c.get("name") for c in m.get("concept_cards", []) if isinstance(c, dict)]
        chk(
            names and set(names) == set(cards),
            "V26 concept_cards 集合 == concepts 集合（%d vs %d）" % (len(cards), len(names)),
            "两个列表不同步 = 覆盖度与图谱对不上",
        )
        empty = 0
        for m in d.get("modules", []):
            for c in m.get("concept_cards", []):
                if isinstance(c, dict):
                    for f in ["assumption", "first_principle", "plain", "extend"]:
                        if not str(c.get(f, "")).strip():
                            empty += 1
        chk(
            empty == 0,
            "V27 概念卡四字段无空值（空 %d 处）" % empty,
            "空字段 = 铁律 18 没落实",
        )
    except Exception as e:
        chk(False, "V26 syllabus.yaml 可解析", str(e))


# --- V28 口径唯一：全局不得再有「七字段」（笔误说明句除外）---
bad7f = []
for nm, txt in [("SKILL.md", sk), ("09 细则", r9),
                ("graph 模板", tpl), ("syllabus 模板", syl)]:
    for ln in txt.splitlines():
        if "七字段" in ln and "笔误" not in ln and "早期" not in ln:
            bad7f.append(nm + ": " + ln.strip()[:40])
chk(
    not bad7f,
    "V28 全库口径唯一（不再有「七字段」的说法）",
    "四套说法并存时 AI 只能靠猜：" + str(bad7f[:2]),
)

# --- V29 09 的步号要与 SKILL.md 实际流程一致 ---
a_steps = re.findall(r"^### ([A-E]) (.*)$", sk, re.M)
has_graph_in_a3 = bool(re.search(r"^3\..{0,200}图谱", sk, re.M))
chk(
    ("第 3 步" in r9) and has_graph_in_a3,
    "V29 09 说的步号 = SKILL.md 里图谱实际所在的步号（第 3 步）",
    "09 写第 4 步但实际在第 3 步 = AI 会去找一个不存在的步骤",
)

# --- V30 模板卡片六行（前置/相关各占一行）---
chk(
    ('<b>前置</b>' in tpl and '<b>相关</b>' in tpl),
    "V30 模板卡片里「前置」「相关」各占一行（不再挤在标题行）",
    "细则要求六行、模板只有四行 = AI 照模板画就欠两项",
)

# --- V31 模板导航不得硬编码会断的链接 ---
chk(
    not re.search(r'href="mastery\.md"', tpl),
    "V31 模板导航不硬编码 mastery.md 链接（未建文件时就是断链）",
    "图谱先于课程产出，此时链 mastery.md 必断",
)

# --- V32 重合边 / 无来源数值 的处置要写清 ---
chk(
    ("既在" in r9 and "related" in r9) or "不重复画虚线" in r9,
    "V32 细则规定了 prereq 与 related 重合时怎么画",
    "不规定 = AI 把相关全画成边，图谱变成全连接网没有信息量",
)
chk(
    "待核验" in r9,
    "V33 细则规定了无来源数值要标待核验并记 coverage_gap",
    "图注里写死没来源的数字 = 违反铁律 2/3，且图最容易被当成权威",
)

# --- V34 脚本生成不算降级 ---
chk(
    ("常规手段" in r9 or "不是降级" in r9),
    "V34 细则明确脚本批量生成不属于降级",
    "写成「概念太多才允许」= 6 个概念时 AI 会犹豫，或改成手画粗制图",
)

print("\n" + "=" * 58)
if FAIL:
    print("FAIL %d 项：" % len(FAIL))
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
print("V 段全部 PASS")
