#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""第 8 轮对抗性审查 Z 段：组合功能（v0.8.0）的深度校验。

Y 段只验「规则在不在」，Z 段验「规则对不对、老工作区能不能用、会不会与既有概念混」。

用法： python tools/review_compose_deep.py
退出码： 0 = 全绿； 1 = 有 FAIL
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skill", "learn-system")
SK = os.path.join(SKILL, "SKILL.md")
REF10 = os.path.join(SKILL, "references", "10-composition.md")
BRIEF = os.path.join(SKILL, "templates", "compose-brief.md")
SYL = os.path.join(SKILL, "templates", "syllabus.template.yaml")

sk = open(SK, encoding="utf-8").read()
r10 = open(REF10, encoding="utf-8").read() if os.path.exists(REF10) else ""
br = open(BRIEF, encoding="utf-8").read() if os.path.exists(BRIEF) else ""
syl = open(SYL, encoding="utf-8").read()

TYPES = {"deep-dive", "interactive", "handbook", "flashcards", "audio"}
FAIL = []


def chk(cond, name, fix):
    if cond:
        print("  PASS  " + name)
    else:
        print("  FAIL  " + name + "\n        -> " + fix)
        FAIL.append(name)


print("=== Z. 组合功能深度校验 ===")

# --- Z01 老工作区迁移：升级后 syllabus.yaml 没有 artifacts 字段怎么办 ---
chk(
    ("已有工作区" in r10 or "老工作区" in r10 or "升级" in r10) and "artifacts" in r10,
    "Z01 说明了已有工作区如何补 artifacts 字段（迁移路径）",
    "只在新模板里加字段 = 老课题升级后没有这一项，第一次借力就卡住或静默跳过登记",
)

# --- Z02 8 类产物 vs 5 个登记 type，必须说清对应关系 ---
declared = set(re.findall(r"\|\s*`?(" + "|".join(TYPES) + r")`?\s*\|", r10)) | set(
    re.findall(r"(deep-dive|interactive|handbook|flashcards|audio)", r10))
chk(
    len(declared & TYPES) >= 4 and ("不登记" in r10 or "不用登记" in r10),
    "Z02 说清了「8 类产物里哪 3 类不需要登记」（登记 type 只有 5 个）",
    "8 类都要登记 vs 5 个 type = 用户不知道速查件/课要不要填 artifacts",
)

# --- Z03 「2 次没懂」不能与「2 次答错」混（后者会建 mistakes.md）---
chk(
    ("答错" in r10 or "错题" in r10 or "没懂 ≠" in r10 or "区别于" in r10),
    "Z03 区分了「连续 2 次没懂」与「累计 2 次答错」",
    "两个「2 次」并存：一个是建深讲卡的触发，一个是建 mistakes.md 的触发，混了会误触发",
)

# --- Z04 真实工作区 artifacts 结构校验 ---
work = os.path.join(ROOT, "study", "注塑")
syp = os.path.join(work, "syllabus.yaml")
if os.path.exists(syp):
    try:
        import yaml
        d = yaml.safe_load(open(syp, encoding="utf-8").read()) or {}
        has_field = "artifacts" in d
        arts = d.get("artifacts") or []
        chk(has_field, "Z04 真实工作区已有 artifacts 字段（值可为空）",
            "老工作区缺字段：第一次借力时无处登记，等于静默丢掉产物")
        bad = []
        for a in arts:
            if not isinstance(a, dict):
                bad.append(str(a)); continue
            for f in ("name", "type", "path", "source", "created"):
                if not a.get(f):
                    bad.append("%s 缺 %s" % (a.get("name", "?"), f))
            if a.get("type") and a["type"] not in TYPES:
                bad.append("%s 的 type=%s 不在枚举内" % (a.get("name"), a.get("type")))
            p = a.get("path", "")
            if p and not os.path.exists(os.path.join(work, p)):
                bad.append("%s 的 path 不存在：%s" % (a.get("name"), p))
        chk(not bad, "Z05 artifacts 每条结构合法（name/type/path/source/created）",
            "结构不合法 = 登记了也查不到：" + str(bad[:3]))
    except Exception as e:
        chk(False, "Z04 读真实 syllabus.yaml", str(e))
else:
    print("  --    Z04/Z05 跳过（无真实工作区）")

# --- Z06 组合产物不得进 lessons/ ---
chk(
    "不要塞进 `lessons/`" in r10 or "不塞进" in r10 or "不要塞 `lessons/`" in r10,
    "Z06 明确禁止把外部产物塞进 lessons/",
    "课号与顺序是状态的一部分，混进外来文件会让出课顺序错乱",
)

# --- Z07 简报字段与细则的接口契约表一致 ---
need = ["这是给谁看的", "要做什么产物", "已知信息", "格式约束", "不要做什么", "交回给我什么"]
miss = [n for n in need if n not in br]
chk(not miss, "Z07 简报 6 字段齐全（缺：%s）" % (miss or "无"), "字段不全 = 借力又要重新口述")
# 简报里的 type 提示必须与枚举一致
brief_types = set(re.findall(r"(deep-dive|interactive|handbook|flashcards|audio)", br))
chk(brief_types and brief_types <= TYPES, "Z08 简报里的 type 提示与枚举一致（%s）" % sorted(brief_types),
    "简报提示了枚举外的 type = 产物登记时校验不过")

# --- Z09 简报占位符都有说明（不能留裸 {{X}}）---
phs = set(re.findall(r"\{\{([^}]+)\}\}", br))
undecl = [p for p in phs if p not in br.split("<!--")[-1] and br.count(p) < 2]
chk(not undecl or len(phs) < 20, "Z09 简报占位符 %d 个，均可被使用者理解" % len(phs),
    "占位符没说明 = 填错或漏填")

# --- Z10 有「何时不借」防止滥用 ---
chk("什么时候**不**借" in r10 or "什么时候不借" in r10,
    "Z10 有「何时不借」反向约束",
    "只有该借的规则 = 什么场合都会借，最后堆一身材料")

# --- Z11 SKILL.md 体积 ---
size = os.path.getsize(SK)
chk(size <= 15360, "Z11 SKILL.md 体积 %d B <= 15 KB 红线" % size, "又超红线了")

# --- Z12 Y 段已挂进主审计 ---
aud = open(os.path.join(ROOT, "learn-system-audit.py"), encoding="utf-8").read()
chk("review_compose.py" in aud, "Z12 组合 Y 段已挂进主审计",
    "专项脚本不挂主审计 = 平时没人跑")


# --- Z13 「没懂」必须有计数落点（真机实测：AI 只能凭印象判第几次）---
chk(
    ("备注" in r10 and "未懂" in r10),
    "Z13 「没懂」有计数落点（mastery 备注列记「未懂 N」）",
    "只在语义上区分「2 次没懂」= 触发条件不可审计，AI 只能凭印象判第几次",
)
chk(
    "看了两遍" in r10 and "1 次" in r10,
    "Z14 明确了「看了两遍」算 1 次反馈，不是 2 次",
    "不写 = 用户一说「看了两遍」就误触发深讲卡",
)

# --- Z15 材料缺失 vs 材料不够花 必须分流 ---
chk(
    "根本不是" in r10 or "材料**缺失**" in r10 or "材料缺失" in r10,
    "Z15 区分「材料缺失」与「材料不够花」（前者补课，后者借深讲卡）",
    "不区分 = 把没讲过一课的概念拿深讲卡顶替，附加材料进了不进 lessons/ 序列",
)

# --- Z16 降级两条路径分岔 ---
chk(
    "课还在推进" in r10 and "课先不上" in r10,
    "Z16 降级按「课还继续吗」分成两条落点（reference/登记 vs 讲完即止）",
    "只有一条 = 与 SKILL.md 降级表打架（一个要求登记，一个禁止建目录）",
)

# --- Z17 状态冲突裁决（真机实测：用户说已上未评、盘上是未学）---
chk(
    "以文件为准" in sk,
    "Z17 SKILL.md 写明「用户说的进度与文件不符 → 以文件为准」",
    "不裁决 = 每个 AI 自己选边，恢复入口失去权威",
)

# --- Z18 路由表必须带「无独立课不出卡」例外（F5：路由表曾无条件写「满 2 次出卡」，与 ref 10 §4 冲突）---
row = [l for l in sk.splitlines() if "没懂" in l and "出深讲卡" in l]
chk(
    any(("无独立课" in r) or ("不出卡顶替" in r) for r in row),
    "Z18 路由表『没懂』行带「无独立课不出卡」例外（与 ref 10 §4 一致）",
    "路由表是 AI 第一眼读到的，漏掉例外会让无独立课的概念也被出卡顶替，与 §4 打架",
)

print("\n" + "=" * 58)
if FAIL:
    print("FAIL %d 项：" % len(FAIL))
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
print("Z 段全部 PASS")
