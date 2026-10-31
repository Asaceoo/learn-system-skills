#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第 9 轮对抗性审查 AA 段：v0.8.1 四处修复的副作用检查。

上一轮修了「未懂计数 / 材料缺失分流 / 降级双落点 / 状态冲突裁决」，
这四项都会与既有规则**交界**，交界处最容易出新矛盾。

用法： python tools/review_side_effects.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skill", "learn-system")
SK = os.path.join(SKILL, "SKILL.md")
R10 = os.path.join(SKILL, "references", "10-composition.md")
R05 = os.path.join(SKILL, "references", "05-review.md")
MT = os.path.join(SKILL, "templates", "mastery.template.md")
MTP = os.path.join(ROOT, "study", "注塑", "mastery.md")

sk = open(SK, encoding="utf-8").read()
r10 = open(R10, encoding="utf-8").read()
r05 = open(R05, encoding="utf-8").read()
mt = open(MT, encoding="utf-8").read()
mtp = open(MTP, encoding="utf-8").read() if os.path.exists(MTP) else ""

FAIL = []


def chk(cond, name, fix):
    if cond:
        print("  PASS  " + name)
    else:
        print("  FAIL  " + name + "\n        -> " + fix)
        FAIL.append(name)


print("=== AA. v0.8.1 四处修复的副作用 ===")

# --- AA01 备注列已有用途，写「未懂 N」不能覆盖它 ---
chk(
    ("；" in r10 and "未懂" in r10) or "分隔" in r10,
    "AA01 说明「未懂 N」怎么与备注列已有内容共存（分隔而非覆盖）",
    "备注列已用于「待自检评级后定档」等，直接写会覆盖旧备注，信息丢失",
)

# --- AA02 状态冲突裁决要给出「用户坚持时怎么办」 ---
chk(
    ("以文件为准" in sk),
    "AA02 SKILL.md 有「以文件为准」的裁决",
    "不裁决 = 每个 AI 自己选边",
)
has_followup = ("learning-record" in sk[sk.index("以文件为准") - 80: sk.index("以文件为准") + 200]
                if "以文件为准" in sk else False)
chk(
    has_followup or "用户坚持" in r10 or "坚持" in sk,
    "AA03 裁决之后给了后续动作（用户坚持时怎么改）",
    "只说「以文件为准」不说「用户坚持怎么办」= 用户会被告知差异然后卡住",
)

# --- AA04 降级两条落点：两处表述必须能对上 ---
# 注意：「单概念讲解」在 SKILL.md 出现多次（目标章节的不做清单、降级表），
# 只取第一处会假阴性——必须检查是否**有任一**处指向细则
sk_deg_hits = re.findall(r"单概念讲解[^\n]*", sk)
r10_deg = ("课还在推进" in r10) and ("课先不上" in r10)
chk(
    any("见 10" in h for h in sk_deg_hits) and r10_deg,
    "AA04 降级两条落点在 SKILL.md 与 10 之间互相指得通（%d 处「单概念讲解」）" % len(sk_deg_hits),
    "SKILL.md 说「见 10」但 10 里没有对应分支 = 指了个空",

)

# --- AA05 「材料缺失先补课」不与流程 B「一次一课」冲突 ---
chk(
    "补课" in r10 and ("流程 B" in r10 or "先补" in r10),
    "AA05 「材料缺失」导向补课，路径明确到流程 B",
    "只说「先补课」不指路径 = 下次还是直接出深讲卡",

)

# --- AA06 两个「2 次」的计数规则不能互相污染 ---
m_err = re.search(r"累计\s*2\s*次错", sk)
m_nd = re.search(r"未懂\s*2|未懂 N", r10)
chk(
    m_err is not None and m_nd is not None,
    "AA06 「2 次错」（mistakes）与「2 次没懂」（深讲卡）各自有落点且不共用计数",
    "共用计数 = 答错一次 + 没懂一次会凑成「两次」，两边都误触发",
)
chk(
    "答错" in r10 and "没懂" in r10,
    "AA07 细则里两个概念都用明确词（答错 / 没懂），不用模糊词",
    "用「不懂/不会/错」混着写 = 无法区分触发哪条",
)

# --- AA08 体积红线：四处脚本 + 文档必须同一个数 ---
thresholds = {}
for f, label in [(os.path.join(ROOT, "learn-system-audit.py"), "主审计")] + [
    (os.path.join(ROOT, "tools", g), g) for g in
    ("review_dialog.py", "review_graph.py", "review_compose_deep.py", "review_regress.py", "review_compose.py")
]:
    if os.path.exists(f):
        t = open(f, encoding="utf-8").read()
        found = set(re.findall(r"(1[0-9]{4})", t))
        if found:
            thresholds[label] = found
uniq = set().union(*thresholds.values()) if thresholds else set()
chk(
    len(uniq) == 1,
    "AA08 所有脚本的体积阈值同一个数（%s）" % (uniq or "无"),
    "只改一个脚本 = 换个段跑就判不一致，比不调还糟：" + str(thresholds),
)
n = int(list(uniq)[0]) if uniq else 0
doc_ok = True
for p in ["docs/TECHNICAL.md", "README.md", "docs/USER_GUIDE.md"]:
    fp = os.path.join(ROOT, p)
    if not os.path.exists(fp):
        continue
    txt = open(fp, encoding="utf-8").read()
    kb = n // 1024
    if ("14 KB" in txt or "14KB" in txt) and f"{kb} KB" not in txt:
        doc_ok = False
chk(doc_ok, "AA09 文档里的红线表述与脚本阈值一致（%d B ≈ %d KB）" % (n, n // 1024),
    "文档写 14 KB、脚本判 15 KB = 用户和实现者看到的不是一回事")

# --- AA10 v0.8.1 的四条断言真的在脚本里 ---
zd = open(os.path.join(ROOT, "tools", "review_compose_deep.py"), encoding="utf-8").read()
need = ["未懂", "看了两遍", "材料", "课还在推进", "以文件为准"]
miss = [k for k in need if k not in zd]
chk(not miss, "AA10 v0.8.1 修复对应的断言都在 Z 段（缺：%s）" % (miss or "无"),
    "修了规则不补断言 = 下次改回去没人发现")


# --- AA11 关键约束不能只写在表格之后（真机实测：只看表会误判）---
tbl_row = [ln for ln in r10.splitlines() if "深讲卡" in ln and ln.strip().startswith("|")]
chk(
    any("看了两遍" in ln for ln in tbl_row),
    "AA11 产物矩阵那一行**内部**就注明「看了两遍算 1 次」",
    "澄清只在表格之后 = 只读表格的执行者会把 1 次误判成 2 次，立刻出卡",
)

# --- AA12 §4（材料缺失）与 §6（降级产出）的优先级必须写死 ---
chk(
    "优先级" in r10 and ("§4 胜" in r10 or "1. **材料缺失" in r10 or "材料缺失判断" in r10),
    "AA12 §4 与 §6 打架时给了优先级（材料缺失优先）",
    "两条规则对同一场景给出相反指令（别出卡 / 自己做出来），不写优先级只能靠 AI 猜",
)

# --- AA13 主流程/路由表要有「没懂」的入口 ---
route_hit = [ln for ln in sk.splitlines() if ln.startswith("|") and "没懂" in ln]
chk(
    bool(route_hit),
    "AA13 路由表有「这个概念我没懂」的入口行（%d 行）" % len(route_hit),
    "流程 A-E 都不提深讲卡，用户说没懂时 AI 无处可去，只能靠两处细则拼路径",
)
chk(
    route_hit and "备注" in route_hit[0] and "变更日志" in route_hit[0],
    "AA14 入口行写明了「记备注、不记变更日志」",
    "铁律 10 要求变更日志，但一次没懂反馈不是一课，不写清就两头不是",
)

print("\n" + "=" * 58)
if FAIL:
    print("FAIL %d 项：" % len(FAIL))
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
print("AA 段全部 PASS")
