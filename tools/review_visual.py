# -*- coding: utf-8 -*-
"""AC 段：图面语法（融合 diagram-design 后的可机检部分）。

跑法：python tools/review_visual.py
退出码非 0 即有问题。主审计会自动调用本文件。
"""
import io
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skill", "learn-system")
WS = os.path.join(ROOT, "study", "注塑")

fails = []


def chk(ok, name, why=""):
    if ok:
        print("  PASS  " + name)
    else:
        print("  FAIL  " + name + ("  ← " + why if why else ""))
        fails.append(name)


def rd(p):
    return io.open(p, encoding="utf-8").read()


R11 = os.path.join(SKILL, "references", "11-visual-grammar.md")
R9 = os.path.join(SKILL, "references", "09-knowledge-graph.md")
TPL = os.path.join(SKILL, "templates", "graph.template.html")
KBF = os.path.join(SKILL, "scripts", "kbfig.py")
SK = os.path.join(SKILL, "SKILL.md")

v11 = rd(R11) if os.path.exists(R11) else ""
r9 = rd(R9) if os.path.exists(R9) else ""
tpl = rd(TPL) if os.path.exists(TPL) else ""
kbf = rd(KBF) if os.path.exists(KBF) else ""
sk = rd(SK) if os.path.exists(SK) else ""

print("\n=== AC. 图面语法（融合 diagram-design）===")

# --- AC01 文件存在且有实质内容 ---
chk(len(v11.encode("utf-8")) > 3000, "AC01 11-visual-grammar.md 存在且有实质内容（%d B）" % len(v11.encode("utf-8")),
    "少于 3000 B 说明只写了个壳")

# --- AC02 §0 三问 ---
chk(all(k in v11 for k in ["什么时候**不**该画", "读一遍就懂", "表格能说清", "只是把正文重画"]),
    "AC02 §0 有三问闸门（不画比画好）",
    "缺闸门 = 每课机械凑图，违背「一张图只回答一个问题」")

# --- AC03 两步选型 ---
chk("第一步 · 定语义" in v11 and "第二步 · 定图型" in v11,
    "AC03 §1 是「先语义、再图型」两步",
    "跳过第一步会拿流程图讲连续量关系，答不了「为什么」")

# --- AC04 八种结构图/数据图，每种有预算 ---
rows8 = re.findall(r"^\| S[1-8] \|", v11, re.M)
chk(len(rows8) == 8, "AC04 §2 结构图/数据图八种齐全（实 %d）" % len(rows8),
    "eight types 少一个就会去硬套机制图")

# --- AC05 复杂度预算四个上限 ---
nums_ok = all(k in v11 for k in ["**9**", "**12**", "**2**"])
chk(nums_ok and "超过 9 个节点的图，通常是两张图" in v11,
    "AC05 §3 复杂度预算写明 9 节点 / 12 连线 / 2 焦点",
    "没有上限 = 26 个概念也敢塞一张图")

# --- AC06 remove test 四问 ---
chk(v11.count("能删掉") + v11.count("能合并") >= 3 and "Remove test" in v11,
    "AC06 §4 remove test 四问齐全",
    "缺这四问 = 只会加不会删")

# --- AC07 出图前先声明 ---
chk("出图前先声明" in v11 and "会砍掉" in v11,
    "AC07 §5 要求出图前声明「图型 / 问题 / 砍掉什么」",
    "不声明 = 用户只能看到成品，改不动方向")

# --- AC08 反模式 ≥10 条 ---
apx = v11[v11.index("## 6. 通用反模式"):v11.index("## 7.")] if "## 6. 通用反模式" in v11 else ""
n_ap = len(re.findall(r"^\| [^|]+ \| [^|]+ \|$", apx, re.M))
chk(n_ap >= 10, "AC08 §6 通用反模式 ≥10 条（实 %d）" % n_ap,
    "少于 10 条挡不住 AI 味的图")

# --- AC09 无障碍四条 ---
chk('aria-labelledby' in v11 and "第一个子元素" in v11 and "不许用裸" in v11,
    "AC09 §7 无障碍是四条唯一写法（role+labelledby / title 首子 / 前缀 id / desc 写内容）",
    "口径一松，两类图各写各的，谁也机检不了")

# --- AC10 手机宽两条 ---
chk("min-width" in v11 and "overflow-x" in v11,
    "AC10 §8 手机宽两条（min-width=viewBox 宽 + overflow-x 容器）",
    "缺一条 = 手机上整页横滚，或被 hidden 裁掉没滚动条")

# --- AC11 交卷清单 ---
chk("## 9. 交卷清单" in v11 and v11.count("- [ ]") >= 8,
    "AC11 §9 交卷清单 ≥8 项",
    "没有清单 = 规则看完就忘")

# --- AC12 明确不并的部分（防未来又去并 45 种） ---
chk("## 10. 明确不并的部分" in v11 and "45 种图型全库" in v11,
    "AC12 §10 写明「不并」的清单与理由",
    "不写 = 下次有人（包括我）又把 45 种搬进来")

# --- AC13 kbfig 的 svg() 满足契约 ---
chk('aria-labelledby="{slug}-title {slug}-desc"' in kbf and "min-width:{self.w}px" in kbf,
    "AC13 kbfig.svg() 输出 role+aria-labelledby+min-width",
    "库不遵守自己的规范 = 生成的每张图都违规")

# --- AC14 figure() 拒绝非问句 ---
chk("def figure(" in kbf and 'endswith(("？", "?"))' in kbf,
    "AC14 kbfig.figure() 拒绝非问句 data-q",
    "允许名词短语 = data-q 退化成标题")

# --- AC15 09 指向 11 ---
chk("11-visual-grammar.md" in r9,
    "AC15 09 抬头指向 11",
    "不指路 = 画课时永远读不到语法")

# --- AC16 09 无障碍口径已收敛（不再有「或 aria-label」） ---
chk("aria-label` **或**" not in r9 and "按 `11` §7" in r9,
    "AC16 09 的无障碍口径收敛为 11 §7 唯一写法",
    "两套口径并存 = 上一轮审查抓到的「规则写了不执行」重演")

# --- AC17 模板有路径与热力图两节 ---
chk("学习路径" in tpl and "掌握度热力图" in tpl,
    "AC17 graph 模板含「学习路径」与「掌握度热力图」两节",
    "只有依赖图 = 看不出进度，图谱页仍是静态资料")

# --- AC18 模板无阴影/渐变/大圆角 ---
bad_style = []
for m in re.finditer(r"border-radius:(\d+)px", tpl):
    if int(m.group(1)) > 12:
        bad_style.append("radius " + m.group(1))
if "box-shadow" in tpl:
    bad_style.append("box-shadow")
if "gradient" in tpl:
    bad_style.append("gradient")
chk(not bad_style, "AC18 模板无阴影/渐变/超 12px 圆角",
    "命中 11 §6 反模式：" + str(bad_style[:3]))

# --- AC19 模板图必须带 overflow 容器 ---
chk("overflow-x:auto" in tpl or "overflow-x: auto" in tpl,
    "AC19 模板里的宽内容有 overflow-x 容器",
    "缺了 = 手机上整页横滚")

# --- AC20 每课图数 ≤5（真实工作区） ---
if os.path.isdir(os.path.join(WS, "lessons")):
    over = []
    for fn in sorted(glob.glob(os.path.join(WS, "lessons", "*.html"))):
        n = rd(fn).count("<figure")
        if n > 5:
            over.append(os.path.basename(fn) + "=" + str(n))
    chk(not over, "AC20 每课图数 ≤5（11 §3）",
        "超了说明这一课塞了不止一个能力点：" + str(over))

# --- AC21/22 图谱页每一张结构图都在预算内 ---
# 教训：第一版按固定标题「一、图谱」定位，真实产物标题是「依赖总览」，正则没命中 →
# 统计到 0 个节点 → 假绿放行；第二版标题又改成「模块级总览」，再次定位失败。
# 结论：**不要按标题找，按图找**——凡是结构图（class 含 fig-map），逐张过预算。
gp = os.path.join(WS, "graph.html")
if os.path.exists(gp):
    g = rd(gp)
    blocks = re.findall(r'<svg class="[^"]*fig-map[^"]*"[\s\S]*?</svg>', g)
    if not blocks:
        chk(False, "AC21 图谱页有结构图可校验", "一张都没有 = 要么没画，要么 class 丢了，都无法验证预算")
    else:
        over_n, over_l = [], []
        for b in blocks:
            t = re.search(r"<title[^>]*>([^<]*)</title>", b)
            name = (t.group(1) if t else "?")[:26]
            # 节点 = 带 rx 的矩形；连线 = path 里排除 <defs> 内的 marker 定义
            body = re.sub(r"<defs>[\s\S]*?</defs>", "", b)
            n = len(re.findall(r"<rect[^>]*rx=", body))
            lk = len(re.findall(r"<path", body))
            if n > 9:
                over_n.append("%s(%d)" % (name, n))
            if lk > 12:
                over_l.append("%s(%d)" % (name, lk))
        chk(not over_n, "AC21 全部 %d 张结构图节点 ≤9" % len(blocks),
            "超预算（11 §3，超了要拆图）：" + "；".join(over_n[:4]))
        chk(not over_l, "AC22 全部 %d 张结构图连线 ≤12" % len(blocks),
            "连线超预算：" + "；".join(over_l[:4]))

# --- AC23 图谱页的图必须带无障碍契约 ---
if os.path.exists(gp):
    g = rd(gp)
    svgs = re.findall(r"<svg[\s\S]*?</svg>", g)
    bad = []
    for b in svgs:
        if 'role="img"' not in b:
            bad.append("no role")
        elif "aria-labelledby=" not in b:
            bad.append("no labelledby")
        elif not re.search(r'<svg[^>]*>\s*<title id="[a-z0-9-]+-title"', b):
            bad.append("title 不是首子元素或缺前缀 id")
    chk(not bad, "AC23 图谱页 %d 张图全部满足 11 §7 无障碍契约" % len(svgs),
        "违规 %d 张：%s" % (len(bad), sorted(set(bad))[:3]))

# --- AC25 八种结构图型必须有可复制样例，不能只躺在表格里 ---
# 这条是防我自己：diagram-design 声称 45 种却只给 4 个样例，批评完别重犯。
GAL = os.path.join(SKILL, "assets", "diagram-gallery.html")
GENS = os.path.join(SKILL, "scripts", "diagram_gallery.py")
chk(os.path.exists(GENS), "AC25a 样例生成脚本存在（diagram_gallery.py）",
    "没有生成器 = 样例不可复现，改一处要手改 HTML")
if os.path.exists(GAL):
    gal = rd(GAL)
    types = re.findall(r"<h2>(S[1-8])[^<]*</h2>", gal)
    chk(len(set(types)) == 8, "AC25b 样例库含 8 种图型（实 %d）" % len(set(types)),
        "缺的图型 = 文档里很合理，真要画时没得抄")
    gs = re.findall(r"<svg[\s\S]*?</svg>", gal)
    bad = []
    for b in gs:
        if 'role="img"' not in b or "aria-labelledby=" not in b:
            bad.append("缺 role/labelledby")
        elif not re.search(r'<svg[^>]*>\s*<title id="[a-z0-9-]+-title"', b):
            bad.append("title 不是首子元素")
        elif not re.search(r"min-width:\d+px", b):
            bad.append("缺 min-width")
    chk(not bad, "AC25c 样例库 %d 张图全部满足 11 §7/§8" % len(gs),
        "样例自己不合规 = 抄的人一定跟着错：" + str(sorted(set(bad))[:3]))
    over = []
    for b in gs:
        n = len(re.findall(r"<rect[^>]*rx=", re.sub(r"<defs>[\s\S]*?</defs>", "", b)))
        if n > 9:
            over.append(n)
    chk(not over, "AC25d 样例节点数都在 ≤9 预算内（超的：%s）" % (over or "无"),
        "样例自己超预算 = 教人超预算")
    chk("diagram_gallery.py" in v11, "AC25e 11 §2 指向样例库",
        "不指路 = 样例生成完没人知道")

# --- AC26 §1 选型表必须给「多因一果」指到 S6（真机盲测实测：第一次选型会犹豫）---
chk(
    "多因一果" in v11 and "S6" in v11,
    "AC26 §1 语义表给「多因一果」显式指向 S6",
    "§1 说因果去 09、§2 又有因果鱼骨 = 第一次选型只能猜（盲测实测踩到）",
)

# --- AC24/25 图内 <a> 必须配平且不许嵌套 ---
# 实测踩过：模块细节图里 <a> 少写一个 </a>，于是每个 <a> 层层嵌套，
# 浏览器直接不渲染内部元素 —— 结果「6 个方框只画出 1 个、文字全不见」，
# 而 grep 数 rect / text 一切正常。数量对 ≠ 结构对。
for fp, label in ((gp, "图谱页"), (os.path.join(WS, "lessons"), "课内")):
    if not os.path.exists(fp):
        continue
    targets = ([fp] if os.path.isfile(fp)
               else sorted(glob.glob(os.path.join(fp, "*.html"))))
    opens, closes, nested = 0, 0, []
    for fn in targets:
        t = rd(fn)
        o = len(re.findall(r"<a\s", t))
        c = len(re.findall(r"</a>", t))
        opens += o
        closes += c
        if o != c:
            nested.append(os.path.basename(fn) + " 开%d闭%d" % (o, c))
        elif re.search(r"<a\s[^>]*>(?:(?!</a>)[\s\S]){0,120}<a\s", t):
            nested.append(os.path.basename(fn) + " 有嵌套")
    if opens or closes:
        chk(not nested, "AC24 %s %d 个 <a> 全部配平且无嵌套" % (label, opens),
            "不配平/嵌套 = 浏览器不渲染内部元素，而 grep 数数量一切正常：" + "；".join(nested[:3]))

print("\n" + "=" * 58)
if fails:
    print("AC 段 FAIL %d 项：%s" % (len(fails), "；".join(fails[:6])))
    sys.exit(1)
print("AC 段全部 PASS")
