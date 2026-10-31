#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""组合产出（借力其他 skill）专项审查 —— Y 段。

用法： python tools/review_compose.py
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
R7 = os.path.join(SKILL, "references", "07-routing.md")

sk = open(SK, encoding="utf-8").read()
r10 = open(REF10, encoding="utf-8").read() if os.path.exists(REF10) else ""
br = open(BRIEF, encoding="utf-8").read() if os.path.exists(BRIEF) else ""
syl = open(SYL, encoding="utf-8").read()
r7 = open(R7, encoding="utf-8").read()

FAIL = []


def chk(cond, name, fix):
    if cond:
        print("  PASS  " + name)
    else:
        print("  FAIL  " + name + "\n        -> " + fix)
        FAIL.append(name)


print("=== Y. 组合产出功能完整性 ===")

# --- Y01 细则文件 ---
chk(len(r10) >= 3000, "Y01 存在 references/10-composition.md 且 >= 3000 B（当前 %d）" % len(r10),
    "没有细则 = 组合只停在口头，各人各做")

# --- Y02 三条铁律锚点齐全（控制权/落盘输入/必须登记/不硬塞）---
# 只认「N. **铁律名**」这种编号标题形式——避免别处散落的同义词把检查撑绿
laws = {
    "控制权不转移": re.search(r"^\d\. \*\*[^*]*控制权不转移", r10, re.M) is not None,
    "派活给已落盘输入": re.search(r"^\d\. \*\*[^*]*(已落盘|落盘输入)", r10, re.M) is not None,
    "产物必须登记": re.search(r"^\d\. \*\*[^*]*必须登记", r10, re.M) is not None,
    "格式不归一不硬塞": re.search(r"^\d\. \*\*[^*]*(不硬塞|就不硬塞|不归一)", r10, re.M) is not None,
}
chk(all(laws.values()), "Y02 四条组合铁律都在（编号标题形式，%s）" % laws,
    "缺铁律 = 组合会把状态搞乱：" + str([k for k, v in laws.items() if not v]))

# --- Y03 产物矩阵八类齐全 ---
kinds = ["单点课", "知识图谱页", "速查件", "深讲卡", "交互课件", "模块手册", "抽认卡", "音频"]
miss = [k for k in kinds if k not in r10]
chk(not miss, "Y03 产物矩阵 8 类齐全（缺：%s）" % (miss or "无"),
    "少了类别 = 用户想要的时候不知道能不能要")

# --- Y04 每类要有触发条件，不是"想多做就多做" ---
chk("触发条件" in r10 and "为丰富而丰富" in r10,
    "Y04 明确「触发条件不满足就不产出」并点名反模式",
    "不写 = 组合会变成无脑堆文件")

# --- Y05 禁止外部改状态 ---
chk(re.search(r"(mastery|掌握)[\s\S]{0,40}只由本 skill 写", r10) is not None
    or "只由本 skill 写" in r10,
    "Y05 明确「掌握度/复习队列只由本 skill 写」",
    "外部 skill 顺手改状态 = 直接毁掉唯一恢复入口")

# --- Y06 简报模板六字段 ---
need = ["这是给谁看的", "要做什么产物", "已知信息", "格式约束", "不要做什么", "交回给我什么"]
missb = [n for n in need if n not in br]
chk(not missb, "Y06 简报模板 6 个字段齐全（缺：%s）" % (missb or "无"),
    "字段不全 = 借力时又要重新口述需求")

# --- Y07 简报必须带格式硬约束（离线/无外链）---
chk("断网可用" in br or "断网" in br, "Y07 简报写明「断网可用」硬要求",
    "不写 = 外部产出可能挂满 CDN，一断网就白图")
chk("不要新建" in br and "掌握度" in br, "Y08 简报写明禁止新建 study/ 与改状态",
    "不写 = 对方可能自建目录、自改掌握度")

# --- Y09 路由表两档区分 ---
chk("借力" in r7 and "切走" in r7, "Y09 07-routing 区分了「切走」与「借力」两档",
    "只有切走 = 组合无处安放，用户一提附加材料就被劝走")
chk("这门课还继续吗" in r7 or "还继续" in r7, "Y10 两档给了一句判据",
    "没判据 = 每次都要重新想该切走还是借力")

# --- Y11 SKILL.md 指路 ---
chk("10-composition.md" in sk, "Y11 SKILL.md 指向 references/10-composition.md",
    "不指路 = AI 看不到细则")

# --- Y12 大纲模板有 artifacts 登记位 ---
chk("artifacts:" in syl, "Y12 syllabus 模板含 artifacts 登记位",
    "产物没地方登记 = 下个会话等于不存在")

# --- Y13 降级：切不成就自己做并标 self-fallback ---
chk("self-fallback" in r10 and "不许因为切不过去就不做" in r10,
    "Y13 降级规则明确：切不成自己做、标 self-fallback、不许不做",
    "不写 = 借不到就干脆不产出，或者假装做过了")

# --- Y14 真实工作区：借力产物都登记了 ---
work = os.path.join(ROOT, "study", "注塑")
refdir = os.path.join(work, "reference")
syp = os.path.join(work, "syllabus.yaml")
if os.path.isdir(refdir) and os.path.exists(syp):
    try:
        import yaml
        d = yaml.safe_load(open(syp, encoding="utf-8").read()) or {}
        arts = d.get("artifacts") or []
        paths = {a.get("path", "") for a in arts if isinstance(a, dict)}
        # 借力产物：reference/ 下除「*速查.html」以外的文件
        loose = []
        for base, _, fs in os.walk(refdir):
            for f in fs:
                if "速查" in f:
                    continue
                full = os.path.relpath(os.path.join(base, f), work).replace("\\", "/")
                if full not in paths:
                    loose.append(full)
        chk(not loose, "Y14 真实工作区里借力产物都已登记（未登记：%s）" % (loose or "无"),
            "没登记的产物下个会话发现不了，等于白做")
    except Exception as e:
        chk(False, "Y14 读 syllabus.yaml 失败", str(e))
else:
    print("  --    Y14 跳过（无真实工作区）")

print("\n" + "=" * 58)
if FAIL:
    print("FAIL %d 项：" % len(FAIL))
    for f in FAIL:
        print("  - " + f)
    sys.exit(1)
print("Y 段全部 PASS")
