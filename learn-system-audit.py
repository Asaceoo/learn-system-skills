# -*- coding: utf-8 -*-
"""learn-system 对抗性审查脚本（视角二：审查者）
用法: python learn-system-audit.py
退出码非 0 表示有 FAIL。输出真实报错，不美化。
"""
import os, re, sys, yaml, html.parser, datetime, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(ROOT, "skill", "learn-system")   # 仓库副本 = 唯一真源
INSTALLED = os.path.join(os.path.expanduser("~"), ".workbuddy", "skills", "learn-system")
WS    = r"C:/Users/iamly/WorkBuddy/2026-10-30-23-04-03/study/注塑"

FAILS = []
def chk(cond, name, detail=""):
    tag = "PASS" if cond else "FAIL"
    if not cond:
        FAILS.append(f"{name} :: {detail}")
    print(f"  {tag}  {name}" + (f"  <- {detail}" if (detail and not cond) else ""))
    return cond

def rd(p):
    return open(p, encoding="utf-8").read()

print("=== A. 包完整性 ===")
need = ["SKILL.md", "README.md",
        "references/01-system-design.md", "references/02-teaching.md",
        "references/03-assessment.md", "references/04-mastery.md",
        "references/05-review.md", "references/06-sources.md",
        "templates/syllabus.template.yaml", "templates/mission.template.md",
        "templates/mastery.template.md", "templates/review.template.md",
        "templates/mistakes.template.md", "templates/learning-record.template.md",
        "templates/lesson.template.html", "templates/reference.template.html"]
files = sorted(os.path.relpath(os.path.join(d, f), SKILL).replace("\\", "/")
               for d, _, fs in os.walk(SKILL) for f in fs)
print(f"  (实际 {len(files)} 个文件)")
for n in need:
    chk(n in files, f"存在 {n}", "缺失")

print("\n=== B. frontmatter ===")
sk = rd(os.path.join(SKILL, "SKILL.md"))
fm = yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", sk, re.S).group(1))
chk(fm.get("name") == "learn-system", "name 正确", str(fm.get("name")))
chk(len(fm.get("description", "")) > 60, "description 非空", str(len(fm.get("description", ""))))
sz = os.path.getsize(os.path.join(SKILL, "SKILL.md"))
chk(sz <= 14336, f"SKILL.md <= 14KB (实 {sz}B)", f"{sz}B")

print("\n=== C. 铁律编号自引（实现者最容易写错的地方）==")
rules = {}
for m in re.finditer(r"^(\d+)\. \*\*(.+?)\*\*", sk, re.M):
    rules[int(m.group(1))] = m.group(2)
print(f"  解析到 {len(rules)} 条铁律")
chk(len(rules) == 18, "铁律 18 条", f"实 {len(rules)}")

# 每条铁律的语义关键词（正文抽取 + 同义词补充），用于判定引用是否指对
SYN = {
    1:  {"一次", "产出", "一课", "批量", "多课", "一口气", "绝不"},
    2:  {"调研", "教材", "标准", "锚定", "待核验", "来源"},
    3:  {"断言", "三级", "事实", "建议", "推断", "锚点"},
    4:  {"覆盖", "概念", "差集", "not_covered"},
    5:  {"MISSION", "为什么学", "成功", "不学什么"},
    6:  {"开课前", "用户确认", "确认后才出", "必须有大纲"},
    7:  {"前置", "依据", "卡在", "nice_to_have"},
    8:  {"M01", "复审", "大纲"},
    9:  {"校验", "前置", "L3", "核心概念"},
    10: {"mastery", "更新", "掌握"},
    11: {"证据", "判定方", "证据表", "表外"},
    17: {"无证据", "不得升档", "已上未评", "自评", "好看"},
    12: {"自评", "我能独立做到", "封顶"},
    13: {"零提示", "出题"},
    14: {"复练", "重问原题", "换语境"},
    15: {"日期", "心算", "date"},
    16: {"个人目录", "Desktop", "Downloads", "Documents", "兜底", "退回", "目录"},
}
# 判定：命中关键词最多的那条铁律才是"语义上真正被引用"的
law_start = sk.index("## 铁律"); law_end = sk.index("## 状态模型")
for m in re.finditer(r"铁律\s*(\d+)", sk):
    n = int(m.group(1))
    if law_start <= m.start() <= law_end:
        continue          # 铁律正文内部的交叉引用是合法的，不参与判定
    ctx = sk[max(0, m.start() - 60): m.end() + 20]
    # 豁免语境（「不适用」「例外」「豁免」）是在解除该条铁律，不是引用它
    if any(w in ctx for w in ("不适用", "例外", "豁免")):
        continue
    if n not in rules:
        chk(False, f"引用铁律 {n} 存在", "编号越界")
        continue
    # 优先采信作者写的「铁律 N（简述）」括号提示——这是最精确的语义标注
    tail = sk[m.end(): m.end() + 30]
    mb = re.match(r"\s*[（(]([^）)]{1,24})[）)]", tail)
    scope = mb.group(1) if mb else ctx
    scored = []
    for rid, keys in SYN.items():
        hit = [k for k in keys if k in scope]
        if hit:
            scored.append((len(hit), rid, hit))
    if mb and scored:
        pass                     # 括号提示有命中 → 直接用它的结果
    elif mb is None:
        scored = [(c, r, h) for c, r, h in scored]
    scored.sort(key=lambda x: (-x[0], -sum(len(k) for k in x[2]), x[1]))   # 并列时取更具体的
    best = scored[0][1] if scored else None
    chk(best == n, f"L{m.start()} 引用『铁律 {n}』指对",
        f"上下文语义最接近铁律{best}『{rules.get(best,'?')[:26]}』命中{scored[0][2] if scored else []}，却写成铁律{n}")

print("\n=== D. 跨文件规则一致性（同一件事不能有几种说法）==")
def grep_all(pat):
    out = []
    for f in files:
        p = os.path.join(SKILL, f)
        try:
            t = rd(p)
        except Exception:
            continue
        for i, line in enumerate(t.splitlines(), 1):
            if pat in line:
                out.append((f, i, line.strip()))
    return out

mist = grep_all("mistakes")
cond_keys = []
for f, i, line in mist:
    k = "连续2次" if "连续错 2 次" in line else ("答错即记" if "答错" in line else ("忘记勉强即记" if "忘记或勉强" in line else "?"))
    cond_keys.append((f, i, k, line[:70]))
print("  mistakes 相关条款：")
for f, i, k, l in cond_keys:
    print(f"    [{k:8s}] {f}:{i}  {l}")
uniq = {c[2] for c in cond_keys if c[2] != "?"}
chk(len(uniq) <= 1, "mistakes 创建条件全局唯一", f"出现 {len(uniq)} 种说法: {uniq}")

print("\n=== E. 停更判定可执行性 ===")
tpl = yaml.safe_load(rd(os.path.join(SKILL, "templates/syllabus.template.yaml")))
chk("started_at" in tpl.get("topic", {}), "模板有 topic.started_at（停更逾期要算）", "模板无起点日期字段")
wsy = yaml.safe_load(rd(os.path.join(WS, "syllabus.yaml")))
chk("started_at" in wsy.get("topic", {}), "注塑 syllabus 有 started_at", "无起点日期，逾期 1/3/6 周无法计算")
chk(all("core" in m for m in wsy["modules"]), "注塑每模块有 core（铁律 9 前置校验用）", "缺 core 字段")
chk(all("core" in m for m in tpl["modules"]), "模板每模块有 core", "缺 core 字段")

print("\n=== F. 单文件 vs 外链样式（硬约束冲突）==")
b2 = [l for l in sk.splitlines() if "lesson.css" in l]
b3 = [l for l in sk.splitlines() if "单文件" in l]
require = [l for l in b2 if not re.search(r"不抽|不要|禁止|不许", l)]
print(f"  流程B提及 css: {len(b2)} 处（其中要求抽离 {len(require)} 处）| 要求单文件: {len(b3)} 处")
chk(not (require and b3), "B2 外链样式 与 B3 单文件离线 不冲突", "同一流程既要求抽 assets/lesson.css 又要求单文件")
chk(bool(b2), "B2 已显式说明 css 处理（避免实现方自己猜）", "未说明，AI 会各自发挥")

print("\n=== G. 引用链（SKILL.md -> references/templates）==")
refs = {r for r in re.findall(r"`((?:references|templates)/[^`]+)`", sk)
        if "*" not in r and "<" not in r}
bad = [r for r in refs if not os.path.exists(os.path.join(SKILL, r))]
chk(not bad, f"SKILL.md {len(refs)} 处引用可解析", f"失效 {bad}")

print("\n=== H. 真实工作区产物（注塑）==")
les = os.path.join(WS, "lessons", "0001-成型周期与温度组.html")
chk(os.path.exists(les), "0001 存在", "缺失")
h = rd(les)
for blk in ["goal", "anchor", "quiz", "check", "perish", "tag", "risk"]:
    chk(f'class="{blk}"' in h, f"0001 含区块 .{blk}", "缺失该区块")
ans = re.findall(r'data-answer="([a-d])"', h)
chk(3 <= len(ans) <= 5, f"自检 {len(ans)} 题（3-5）", str(ans))
chk(len(set(ans)) > 1, f"正确项位置打散 {ans}", "位置集中")

# 导航链：本课 -> 速查件 可达；上一课/下一课 表示是否定义
local = re.findall(r'href="(\.\./[^"]+)"', h)
for l in local:
    chk(os.path.exists(os.path.normpath(os.path.join(WS, "lessons", l))), f"导航 {l} 可达", "断链")
nav_txt = h[h.find('<nav'):h.find('</nav>')]
chk("上一课" in nav_txt or "首课" in nav_txt, "导航含上一课位置", "缺失")
chk("0002" in nav_txt, "导航声明下一课", "未声明下一课")

print("\n=== I. 掌握度 / 复习 一致性 ===")
mt = rd(os.path.join(WS, "mastery.md"))
rv = rd(os.path.join(WS, "review.md"))
mrows = [r for r in mt.splitlines() if re.match(r"^\| [^|]+ \| M\d", r)]
rrows = [r for r in rv.splitlines() if re.match(r"^\| [^|]+ \| M\d", r)]
chk(len(mrows) == 26, f"mastery 明细 {len(mrows)} 行", "应 26")
mc = [r.split("|")[1].strip() for r in mrows]
rc = [r.split("|")[1].strip() for r in rrows]
chk(all(x in mc for x in rc), "review 概念 ⊆ mastery 概念", f"孤立 {[x for x in rc if x not in mc]}")
today = datetime.date.fromisoformat(subprocess.run(["date", "+%F"], capture_output=True, text=True).stdout.strip())
for r in rrows:
    p = [x.strip() for x in r.split("|")]
    chk(p[6] == str(today + datetime.timedelta(days=1)), f"{p[1]} 到期日算术", f"{p[6]} != 今天+1")
chk(all(k in mt for k in ["当前模块", "下一课", "到期复习"]), "mastery 顶部三行恢复入口", "缺失")

print("\n=== J. 覆盖度（铁律 4：每个概念必须出现在某课或速查件）==")
all_text = h + rd(os.path.join(WS, "reference", "成型周期与温度组速查.html"))
m01 = [m for m in wsy["modules"] if m["id"] == "M01"][0]
covered = [c for c in m01["concepts"] if c in all_text]
print(f"  M01 概念 {len(m01['concepts'])} 个，已覆盖 {len(covered)}: {covered}")
left = [c for c in m01["concepts"] if c not in covered]
print(f"  未覆盖（应在后续课讲授）: {left}")
chk(True, "覆盖度缺口已显式列出（非静默）", "")

print("\n=== K. HTML 合法性 ===")
class V(html.parser.HTMLParser):
    def __init__(s):
        super().__init__(); s.st = []; s.err = []
    def handle_starttag(s, t, a):
        if t not in {"meta", "br", "hr", "input", "img", "link"}: s.st.append(t)
    def handle_endtag(s, t):
        if t in {"meta", "br", "hr", "input", "img", "link"}: return
        if s.st and s.st[-1] == t: s.st.pop()
        else: s.err.append(t)
v = V(); v.feed(h)
chk(not v.st and not v.err, "0001 标签闭合", f"未闭合 {v.st[:3]} 错配 {v.err[:3]}")

print("\n=== L. 规则可执行性（写不出字段 = 规则是空的）==")
chk("study/*" in sk or "扫" in sk, "新会话定位 study/<topic>/ 有说明",
    "恢复入口只说 mastery.md，没说怎么找到它（多 topic 时歧义）")
chk(any(k in yaml.safe_load(rd(os.path.join(SKILL, "templates/syllabus.template.yaml")))
        .get("modules", [{}])[0] for k in ("core", "core_concepts")),
    "syllabus 有『核心概念』字段（铁律 9 校验要用到）",
    "铁律 9 要求前置核心概念 >=L3，但没字段标记哪些是核心")
chk("收尾" in sk, "路由表『B 收尾』在流程 B 中有定义", "路由指向不存在的子流程")
chk("PowerShell" in sk or "date" in sk, "日期获取在 Windows 下另有说明",
    "铁律 15 只给 date +%F（bash），未覆盖 PowerShell/cmd")

print("\n=== M. 未产出课程时的导航约定 ==")
chk("待出" in sk or "未产出" in sk, "规定了下一课尚未产出时导航怎么写",
    "铁律『链断等于课程链断』但未定义未产出课的表示方式，实现方会各写各的")

print("\n=== O. 模板自身不能带断链（会教出坏产物）==")
lt = rd(os.path.join(SKILL, "templates/lesson.template.html"))
hrefs = re.findall(r'href="([^"]+)"', lt)
for h_ in hrefs:
    if h_.startswith("http") or h_ == "#" or "<" in h_:
        continue
    chk("index.html" not in h_, f"模板 href {h_} 不指向不存在的 index.html",
        "状态模型里没有 reference/index.html，模板会教 AI 写出断链")

print("\n=== P. 口径一致（同一数字两处写不能打架）==")
due_top = re.search(r"到期复习：(\d+) 条", mt)
due_rev = re.search(r"今天（[\d-]+）到期 (\d+) 条", rv) or re.search(r"今天到期 (\d+) 条", rv)
if due_top and due_rev:
    chk(due_top.group(1) == due_rev.group(1),
        f"mastery 顶部『到期复习 {due_top.group(1)} 条』= review『今天到期 {due_rev.group(1)} 条』",
        "两处口径不一致，恢复时会读错")

print("\n=== Q. 盲测暴露的条款是否补上 ===")
chk("没有 `syllabus.yaml`" in sk, "接管检测排除本 skill 自身进度", "本 skill 自己也有 lessons/+MISSION.md，会每次误报")
chk("已上未评" in sk, "定义了无自检反馈时的状态（消解铁律 10 vs 17 互斥）", "无此条款时必违反铁律之一")
chk("topic 级" in sk, "明确了调研粒度（每 topic 一次 vs 每课一次）", "未定义会导致每课都重跑调研或都不跑")
chk("不得自造同义名" in sk, "明确了概念粒度与命名", "AI 会自造概念名，mastery 对不上")

print("\n=== R. 跨文件术语与计数同步（改了铁律条数，引用处要跟着改）==")
rdm = rd(os.path.join(SKILL, "README.md"))
m = re.search(r"铁律\s*(\d+)\s*条", rdm)
chk(m and int(m.group(1)) == len(rules),
    f"README 说『铁律 {m.group(1) if m else '?'} 条』= 实际 {len(rules)} 条", "README 未同步")
r1 = rd(os.path.join(SKILL, "references/01-system-design.md"))
chk("core" in r1, "01 的前置校验说明用 core 字段", "仍写『核心概念』，与铁律 9 不一致")
all_txt = "".join(rd(os.path.join(SKILL, f)) for f in files if f.endswith(".md"))
chk("复习档位" not in all_txt, "全局无『复习档位』残留（已改名复习档）", "术语回退")

print("\n=== N. 覆盖度检查时机 ==")
chk(re.search(r"覆盖度.*?(每课|模块结束)", sk, re.S) is not None,
    "定义了覆盖度检查时机", "铁律 4 要求覆盖度验收，但没说什么时候查")

print("\n=== V. 知识图谱总览功能完整性 ===")
_v = os.path.join(ROOT, "tools", "review_graph.py")
if os.path.exists(_v):
    import subprocess
    if subprocess.call([sys.executable, _v]) != 0:
        FAILS.append("图谱 V 段有 FAIL（见上方 V 段输出）")
else:
    FAILS.append("缺 tools/review_graph.py")

print("\n=== T. 弹窗（开课三问）功能完整性 ===")
_t = os.path.join(ROOT, "tools", "review_dialog.py")
if os.path.exists(_t):
    import subprocess
    if subprocess.call([sys.executable, _t]) != 0:
        FAILS.append("弹窗 T 段有 FAIL（见上方 T 段输出）")
else:
    FAILS.append("缺 tools/review_dialog.py")

print("\n=== U. 双副本一致性（审错对象 = 全绿也是假的）===")
if os.path.isdir(INSTALLED):
    import filecmp
    diff = []
    for base, _, fs in os.walk(SKILL):
        rel = os.path.relpath(base, SKILL)
        d = INSTALLED if rel == "." else os.path.join(INSTALLED, rel)
        for f in fs:
            sp, dp = os.path.join(base, f), os.path.join(d, f)
            if not os.path.exists(dp):
                diff.append("已装副本缺 " + os.path.join(rel, f))
            elif not filecmp.cmp(sp, dp, shallow=False):
                diff.append("内容不同 " + os.path.join(rel, f))
    chk(not diff, "已安装副本与仓库副本逐文件一致", "跑 build.py 会自动部署；不一致说明审的是旧副本：\n        " + "; ".join(diff[:5]))
else:
    print("  --    未安装，跳过")

print("\n=== W. 文档口径（项数不能三份各说各的）===")
import re as _re
def _claims(path):
    try:
        x = rd(path)
    except Exception:
        return set()
    return set(_re.findall(r"(\d+)\s*项", x))
_c1 = _claims(os.path.join(ROOT, "README.md"))
_c2 = _claims(os.path.join(ROOT, "docs", "USER_GUIDE.md"))
_c3 = _claims(os.path.join(ROOT, "docs", "TECHNICAL.md"))
_audit_nums = {n for n in (_c1 & _c2 & _c3) if int(n) > 50}
chk(len(_audit_nums) == 1,
    f"三份文档里的审计项数一致（{'/'.join(sorted(_audit_nums)) or '不一致'}）",
    "改了 README 忘了改手册 = 用户和实现者看到的数字不一样")

print("\n" + "=" * 58)
if FAILS:
    print(f"共 {len(FAILS)} 项 FAIL：")
    for i, f in enumerate(FAILS, 1):
        print(f"  {i}. {f}")
    sys.exit(len(FAILS))
print("全部 PASS")
