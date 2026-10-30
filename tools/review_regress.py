#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第 7 轮对抗性审查 X 段：鲁班优化（v0.7.3）引入的回归风险。

用法： python tools/review_regress.py
退出码： 0 = 全绿； 1 = 有 FAIL

为什么单独一段：v0.7.3 动了 SKILL.md 的骨架（删章节、改清单、加目标），
这类改动最容易留下"指向已删内容的引用"和"文档与实际不符"。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skill", "learn-system")
SK = os.path.join(SKILL, "SKILL.md")

sk = open(SK, encoding="utf-8").read()


def rd(*p):
    f = os.path.join(SKILL, *p)
    return open(f, encoding="utf-8").read() if os.path.exists(f) else ""


FAIL = []


def chk(cond, name, fix):
    if cond:
        print("  PASS  " + name)
    else:
        print("  FAIL  " + name + "\n        -> " + fix)
        FAIL.append(name)


all_files = {}
for base, _, fs in os.walk(SKILL):
    for f in fs:
        p = os.path.join(base, f)
        rel = os.path.relpath(p, SKILL)
        all_files[rel] = open(p, encoding="utf-8").read()

print("=== X. 鲁班改动（v0.7.3）回归检查 ===")

# --- X01 删除的章节不得仍被引用 ---
refs_cn = [k for k, v in all_files.items() if "中文备注" in v and k != "SKILL.md"]
chk(
    "中文备注" not in sk and not refs_cn,
    "X01 已删除的「中文备注」没有任何悬空引用",
    "删了章节却留着引用 = 读者按名字去找，找不到：" + str(refs_cn),
)

# --- X02 清单项数：实际数 vs 文中自称 ---
n_box = len(re.findall(r"^   - \[ \]", sk, re.M))
claim = re.search(r"这\s*(\d+)\s*项", sk)
chk(
    (claim is None) or int(claim.group(1)) == n_box,
    "X02 交卷清单实际 %d 项，文中自称 %s 项" % (n_box, claim.group(1) if claim else "未写（可接受）"),
    "自称与实际不符 = AI 会按错的数目打勾",
)

# --- X03 交叉引用的文件都必须存在 ---
cited = {c for c in re.findall(r"`((?:references|templates)/[^`]+?\.(?:md|yaml|html))`", sk) if "*" not in c}
missing = [c for c in cited if not os.path.exists(os.path.join(SKILL, c))]
chk(
    not missing,
    "X03 SKILL.md 里 %d 个被引用的文件全部存在" % len(cited),
    "引用不存在的文件：" + str(missing),
)

# --- X04 降级表与路由表必须对上（新增的豁免不能被路由表漏掉）---
has_deg = "单概念讲解" in sk
route = [ln for ln in sk.splitlines() if "visual-knowledge-tutor" in ln and ln.startswith("|")]
chk(
    has_deg and route and any("降级" in ln for ln in route),
    "X04 路由表的单概念行指向降级表里的豁免条目",
    "豁免只写在降级节，按路由表决策时会看不到 → 直接拒答",
)

# --- X05 双目录扫描规则两处一致（鲁班修的那个 bug）---
m1 = re.search(r"`study/\*/mastery\.md`(.{0,110})", sk)
m2 = re.search(r"默认 `study/<topic>/`(.{0,120})", sk)
chk(
    m1 and "Documents/learn-system" in m1.group(1),
    "X05 恢复入口写明要扫兜底目录（防 topic 失联）",
    "只扫 study/ → 兜底过的 topic 会被当新课题重开",
)
chk(
    m2 and "Documents/learn-system" in m2.group(1),
    "X06 状态模型写明兜底路径与 study/ 等价",
    "一处写了另一处没写 = 仍然会只扫一处",
)

# --- X07 02 的例外必须指到真实存在的细则 ---
t02 = rd("references", "02-teaching.md")
if "例外" in t02:
    m = re.search(r"例外[^\n]{0,120}`([^`]+\.md)`", t02)
    target = m.group(1) if m else ""
    ok = target and os.path.exists(os.path.join(SKILL, "references", os.path.basename(target)))
    chk(ok, "X07 02 的「三问例外」指向的细则文件存在（%s）" % (target or "未指名"),
        "指了个不存在的文件，例外等于没有")
else:
    chk(False, "X07 02 里应有「三问例外」条款", "例外丢了 → 与开课弹窗三问冲突")

# --- X08 模板占位符必须在文档里有说明 ---
tpls = {k: v for k, v in all_files.items() if k.startswith("templates/") and k.endswith(".html")}
undoc = []
for k, v in tpls.items():
    for ph in set(re.findall(r"\{\{([A-Z_]+)\}\}", v)):
        # 占位符要么在同文件注释里解释，要么在对应 references 里出现
        if ("{{%s}}" % ph) in v.split("<!--")[-1] or ph in v.split("<!--")[-1]:
            continue
        undoc.append("%s:%s" % (k, ph))
chk(
    not undoc,
    "X08 模板占位符都有注释说明（未说明：%s）" % (undoc or "无"),
    "占位符没说明 = 填错或漏填，产物出现 {{X}} 残留",
)

# --- X09 结构：h1 必须是文档第一个标题，且四章齐备 ---
heads = re.findall(r"^(#{1,3}) (.+)$", sk, re.M)
first = heads[0] if heads else ("", "")
chk(
    first[0] == "#",
    "X09 第一个标题是 h1（当前：%s %s）" % first,
    "首标题不是 h1 = 层级从 h2 开始，结构不合规",
)
need = {"目标": False, "主流程": False, "降级": False, "铁律": False}
for lv, t in heads:
    for k in need:
        if k in t:
            need[k] = True
chk(
    all(need.values()),
    "X10 必含章节齐备（目标/铁律/主流程/降级）：%s" % need,
    "缺章节：" + str([k for k, v in need.items() if not v]),
)

# --- X11 文档与 SKILL.md 的铁律条数一致 ---
_ls = sk.index("## 铁律"); _le = sk.index("## 状态模型")
n_law = len(re.findall(r"^\d+\. \*\*", sk[_ls:_le], re.M))
bad = []
for doc in ["README.md", "docs/USER_GUIDE.md", "docs/TECHNICAL.md"]:
    p = os.path.join(ROOT, doc)
    if not os.path.exists(p):
        continue
    t = open(p, encoding="utf-8").read()
    for m in re.finditer(r"(\d+)\s*条铁律", t):
        if int(m.group(1)) != n_law:
            bad.append("%s 说 %s 条" % (doc, m.group(1)))
chk(
    not bad,
    "X11 三份文档的铁律条数 = 实际 %d 条" % n_law,
    "文档说的是旧条数：" + str(bad),
)


# --- X12 扫描基准必须写死（真机实测：向上找会误命中别人的课题）---
chk(
    "不向上级目录找" in sk or "不向上" in sk,
    "X12 定位规则写明「不向上级目录找」",
    "不写 = 在仓库/多项目下会扫到父级别人的 study/，误判当前课题",
)
# --- X13 多个命中时不许靠启发式自己猜 ---
m_multi = re.search(r"多个 → ([^；。]{0,40})", sk)
chk(
    m_multi and "让用户选" in m_multi.group(1),
    "X13 多个命中时要求让用户选（当前：%s）" % (m_multi.group(1) if m_multi else "未定义"),
    "真机实测：AI 靠文件时间戳自己猜了课题，虽然猜对但不是手册教的",
)

print("\n" + "=" * 58)
if FAIL:
    print("FAIL %d 项：" % len(FAIL))
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
print("X 段全部 PASS")
