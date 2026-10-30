#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""弹窗（开课三问）功能对抗性审查脚本 —— 工具实现者视角。

用法： python tools/review_dialog.py
退出码： 0 = 全绿； 1 = 有 FAIL

只做一件事：把「弹窗这个功能到底有没有被真正定义清楚」拆成可机检的断言，
先跑一遍拿到真实报错，再用报错驱动修 SKILL.md / 模板，最后跑到全绿。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skill", "learn-system", "SKILL.md")
TPL = os.path.join(ROOT, "skill", "learn-system", "templates")
REF = os.path.join(ROOT, "skill", "learn-system", "references")
DLG = os.path.join(TPL, "intake-dialog.template.html")

sk = open(SK, encoding="utf-8").read()
dlg = open(DLG, encoding="utf-8").read() if os.path.exists(DLG) else ""

FAIL = []


def chk(cond, name, fix):
    if cond:
        print("  PASS  " + name)
    else:
        print("  FAIL  " + name + "\n        -> " + fix)
        FAIL.append(name)


print("=== T. 弹窗（开课三问）功能完整性 ===")

# --- T1 声明实现工具 ---
chk(
    "show_widget" in sk and "widget_guidelines" in sk,
    "T01 SKILL.md 声明了弹窗的实现工具（show_widget + widget_guidelines）",
    "不声明工具 = 各平台各写各的；在流程 A 写明用 show_widget（先 widget_guidelines 取规范）",
)

# --- T2 存在弹窗模板 ---
chk(
    os.path.exists(DLG),
    "T02 存在弹窗模板 templates/intake-dialog.template.html",
    "没有模板 = 每个 AI 各画各的弹窗，形态不可复现；新建该模板",
)

# --- T3 模板体量 ---
chk(
    len(dlg) >= 3000,
    "T03 弹窗模板体量 >= 3000 B（当前 %d B）" % len(dlg),
    "太小说明只有骨架，没画完；补齐三问卡片 + 汇总行 + 确认按钮",
)

# --- T4 三问齐全 ---
chk(
    all(k in dlg for k in ["为什么学", "什么算成功", "小时"]),
    "T04 模板里三个问题都在（为什么学 / 什么算成功 / 每周几小时）",
    "漏问 = MISSION.md 缺字段，后面停更判定算不出来",
)

# --- T5 每问给可点选项 ---
n_opt = len(re.findall(r'class="opt"', dlg))
chk(
    6 <= n_opt <= 12,
    "T05 每问 2-4 个可点选项（当前 %d 个）" % n_opt,
    "0 个 = 弹窗退化成填空；>12 = 选项泛滥，卡片装不下",
)

# --- T6 汇总行 ---
chk(
    "汇总" in sk,
    "T06 SKILL.md 规定弹窗要有汇总行",
    "没有汇总行 = 用户不知道自己选了什么就点了确认",
)
chk(
    re.search(r'id="summary"', dlg) is not None,
    "T07 模板有 id=summary 的汇总行元素",
    "SKILL.md 说了要汇总，模板没这个元素 = 规则落不了地",
)

# --- T8 确认按钮 ---
chk(
    "确认" in sk,
    "T08 SKILL.md 规定弹窗要有确认按钮",
    "没有确认按钮 = 无提交动作，AI 无法判断用户是否答完",
)
chk(
    re.search(r'id="(confirm|ok|submit)"', dlg) is not None,
    "T09 模板有 id=confirm 的确认按钮",
    "SKILL.md 说了要确认，模板没按钮 = 规则落不了地",
)

# --- T10 主题占位 ---
chk(
    "{{" in dlg and "TOPIC" in dlg,
    "T10 模板用 {{TOPIC}} 之类占位符（领域可替换）",
    "写死领域 = 换个领域弹窗就错；改成占位符",
)

# --- T11 回写 MISSION.md ---
REF8 = os.path.join(REF, "08-intake-dialog.md")
ref8 = open(REF8, encoding="utf-8").read() if os.path.exists(REF8) else ""
chk(
    "08-intake-dialog.md" in sk,
    "T11a SKILL.md 指向弹窗细则 references/08-intake-dialog.md",
    "不指路 = AI 永远看不到细则，弹窗规则是死的",
)
chk(
    re.search(r"(回写|写入|落到|写进)\s*[`\"]?MISSION", ref8) is not None,
    "T11b 细则规定了弹窗答案如何回写 MISSION.md",
    "不规定回写 = 用户点完弹窗，答案只活在对话里，下次开课要重问一遍",
)

# --- T12 未确认 / 只选部分 ---
chk(
    any(k in ref8 for k in ["未确认", "没确认", "不点确认", "未点确认", "只选了一部分", "只选了部分", "没选全"]),
    "T12 细则规定了用户没确认 / 只选部分时怎么办",
    "不规定 = AI 要么卡死等确认，要么拿半份答案硬开课，两种都是 bug",
)

# --- T13 第 3 题双选 ---
chk(
    "模式" in sk and "小时" in sk,
    "T13 第 3 题双选（模式 + 每周小时）有说明",
    "第 3 问塞了两件事，不说清 = AI 只收一个、漏另一个",
)

# --- T14 降级：无弹窗能力 ---
# T14 必须精确命中「弹窗 / widget」，不能让「可视化」这类近义词蒙混过关
m14 = re.search(r"## 降级([\s\S]{0,900})", sk)
block14 = m14.group(1) if m14 else ""
chk(
    ("弹窗" in block14 or "widget" in block14 or "Widget" in block14),
    "T14 降级表含「无弹窗能力」的降级方案（精确匹配，不接受『可视化』蒙混）",
    "没有降级 = 不支持 widget 的平台直接卡住，整个流程 A 走不下去",
)

# --- T15 体积红线 ---
size = os.path.getsize(SK)
chk(
    size <= 14336,
    "T15 SKILL.md 体积 %d B <= 14 KB 红线" % size,
    "加规则不能靠无限加字；改流程顺序，或把细则外移到 references/",
)

# --- T16 文档同步 ---
rd = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
chk(
    "弹窗" in rd,
    "T16 README 提到弹窗（用户得知道首屏会弹）",
    "README 不写 = 用户不知道会弹窗，以为是卡住了",
)
ug = os.path.join(ROOT, "docs", "USER_GUIDE.md")
if os.path.exists(ug):
    chk(
        "弹窗" in open(ug, encoding="utf-8").read(),
        "T17 用户手册提到弹窗",
        "手册不写 = 用户不知道弹窗里怎么选、不选会怎样",
    )


# --- T18 字号不得违反平台规范（盲测实测：规范要求 >= 11px）---
sizes = [int(x) for x in re.findall(r"font-size:(\d+)px", dlg)]
bad = [n for n in sizes if n < 11]
chk(
    not bad,
    "T18 模板字号全部 >= 11px（当前最小 %s）" % (min(sizes) if sizes else "无"),
    "平台规范要求 >= 11px；小于 11 会被判违规，且小屏看不清",
)

# --- T19 小时数 -> 预期完成时间换算表（盲测实测：AI 只能拿示例值自曝）---
chk(
    "horizon_weeks" in ref8 and all(k in ref8 for k in ["D1", "D2", "D3"]),
    "T19 细则给了『每周小时 -> horizon_weeks』换算表",
    "没有换算表 = 预期完成时间算不出，停更三档（逾期 1/3/6 周）失去基准",
)

# --- T20 「不学什么」不阻塞开课（盲测实测：AI 卡在铁律 5 等用户补）---
chk(
    ("不学什么" in sk and "留待" in sk) or "不学什么" in ref8,
    "T20 明确了『不学什么』留到大纲阶段补、不阻塞开课第一步",
    "铁律 5 要它、弹窗不问它 = AI 卡死在流程 A 第 1 步",
)


# --- T21 平台规范：禁止阴影 / 渐变 ---
chk(
    "box-shadow" not in dlg and "gradient" not in dlg,
    "T21 模板无 box-shadow / gradient（平台规范禁止）",
    "阴影渐变会让流式渲染闪；改用实色 + 0.5px 描边",
)

# --- T22 主题适配：必须用 CSS 变量，不能硬编码浅色 ---
chk(
    "var(--color-background-primary)" in dlg and "var(--color-text-primary)" in dlg,
    "T22 模板用 CSS 变量做明暗主题适配",
    "硬编码浅色 = 暗色主题下突兀；全部换成 --color-* 变量",
)

# --- T23 确认按钮要把答案发回 AI ---
chk(
    "sendPrompt" in dlg,
    "T23 确认按钮调用 sendPrompt（点了就能把代号发回对话）",
    "不接 sendPrompt = 用户点完还要手抄代号，弹窗白做一半",
)

# --- T24 字重只用 400/500 ---
weights = set(re.findall(r"font-weight:(\d+)", dlg))
chk(
    weights <= {"400", "500"},
    "T24 字重只用 400/500（当前 %s）" % (sorted(weights) or "无"),
    "平台规范只允许两种字重；600/700 要降下来",
)

print("\n" + "=" * 58)
if FAIL:
    print("FAIL %d 项：" % len(FAIL))
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
print("T 段全部 PASS")
