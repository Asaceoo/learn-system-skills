# -*- coding: utf-8 -*-
"""AB 段：图型语法 + 坐标库 + 0003 的完整性与自洽性

覆盖本轮（v0.8.5/v0.8.6）新增的三块：
  1. 九种图型规范（09 §3.2）是否自洽、是否与库的能力相符
  2. kbfig.py 是否可运行、是否只用标准库、三条配方是否真被用过
  3. 课内图是否满足自己定的硬规范（含无障碍属性）

设计原则：每条断言都要能抓到一个具体的、已真实发生过的错误。
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skill", "learn-system")
WS = os.path.join(ROOT, "study", "注塑")
KB = os.path.join(SKILL, "scripts", "kbfig.py")
R9 = os.path.join(SKILL, "references", "09-knowledge-graph.md")

FAILS = []


def rd(p):
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def chk(ok, name, why=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + ("" if ok else "  <- " + why))
    if not ok:
        FAILS.append(name)


_lessons_dir = os.path.join(WS, "lessons")
def _lesson_htmls():
    """真实工作区 study/注塑 下的课内 HTML；目录缺失时返回空，避免审计崩溃。"""
    if not os.path.isdir(_lessons_dir):
        return []
    return sorted(f for f in os.listdir(_lessons_dir) if f.endswith(".html"))
if not _lesson_htmls():
    print("  --    study/注塑 缺失，跳过课内图回归（AB07-09, AB12-13）")


sk = rd(os.path.join(SKILL, "SKILL.md"))
r9 = rd(R9)
kb = rd(KB)

# ── AB01 库可导入 ────────────────────────────────
try:
    out = subprocess.run(
        [sys.executable, "-c",
         "import sys;sys.path.insert(0,%r);import kbfig;print(kbfig.Fig().h)" % os.path.dirname(KB)],
        capture_output=True, text=True, timeout=30)
    ok = out.returncode == 0
    detail = (out.stderr or "").strip().splitlines()[-1:] or [""]
except Exception as e:                                    # noqa: BLE001
    ok, detail = False, [str(e)]
chk(ok, "AB01 kbfig.py 可被导入且能构造 Fig", str(detail))

# ── AB02 demo 实际图数必须等于文档声称 ────────────
# 真实发生过的错：09 写「生成九种图型的对照样例」，实际只生成 4 张
claim = re.search(r"--demo out\.html\s*#\s*(.+)", r9)
claim_txt = claim.group(1) if claim else ""
m_num = re.search(r"([一二三四五六七八九十\d]+)\s*[种张]", claim_txt)
cn = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
want = None
if m_num:
    s_num = m_num.group(1)
    want = cn.get(s_num) or (int(s_num) if s_num.isdigit() else None)
try:
    sys.path.insert(0, os.path.dirname(KB))
    import kbfig                                            # noqa: E402
    got = len(re.findall(r"\b(plateau|window|slices)\(", rd(KB).split("def demo")[1].split("def ")[0]))
except Exception:                                            # noqa: BLE001
    got = -1
chk(want is not None and got == want,
    f"AB02 demo 的实际图数({got})与 09 声称({want})一致",
    "文档说『九种图型样例』实际只有 4 张 = 虚假声称，违反铁律 2")

# ── AB03 九种图型里哪些有配方，必须写明 ───────────
rec = ["plateau", "window", "slices"]
n_types = len(re.findall(r"^\| \d \| ", r9, re.M))
chk(n_types == 9, f"AB03 09 §3.2 列了 9 种图型（实 {n_types}）", "图型表条数不对")
chk(("配方覆盖到哪" in r9 or "配方只覆盖一半" in r9) and len(rec) == 3,
    "AB04 09 写明了哪些图型有现成配方、哪些需手写",
    "只给 3 个配方却列 9 种图型，执行者会去找不存在的函数")

# ── AB05 kbfig 只用标准库 ────────────────────────
imports = re.findall(r"^(?:import|from)\s+([a-zA-Z_][\w.]*)", kb, re.M)
stdlib = {"math", "sys", "os", "io", "re"}
third = [m for m in imports if m.split(".")[0] not in stdlib]
chk(not third, f"AB05 kbfig 无第三方依赖（{imports}）", f"引入了第三方：{third}")

# ── AB06 三条配方都真被调用过（防死代码）────────
demo_body = kb.split("def demo")[1] if "def demo" in kb else ""
used = [f for f in rec if (f + "(") in demo_body]
chk(len(used) == 3, f"AB06 三条配方都在 --demo 里被真实调用（{used}）",
    f"未被调用的配方等于没验证过：{[f for f in rec if f not in used]}")

# ── AB07 课内图的无障碍属性 ──────────────────────
# 真实发生过的错：硬规范写 aria-label，但库生成的图只有 title/desc，且审计没查
for fn in _lesson_htmls():
    if not fn.endswith(".html"):
        continue
    h = rd(os.path.join(WS, "lessons", fn))
    svgs = re.findall(r"<svg[\s\S]*?</svg>", h)
    bad = []
    for i, s in enumerate(svgs, 1):
        head = s[:s.find(">") + 1]
        if 'role="img"' not in head:
            bad.append(f"图{i} 缺 role")
        elif "aria-label" not in head and "<title>" not in s:
            bad.append(f"图{i} 无 aria-label 也无 title")
    chk(not bad, f"AB07 {fn} 每张图都有 role=img 且可读标签", str(bad[:3]))

# ── AB08 每课图数不超过 5（09 的拆课门槛）────────
for fn in _lesson_htmls():
    if not fn.endswith(".html"):
        continue
    h = rd(os.path.join(WS, "lessons", fn))
    n = len(re.findall(r"<figure[^>]*>", h))
    chk(n <= 5, f"AB08 {fn} 图数 {n} ≤ 5（超了该拆课）", "09 定的门槛是 5")

# ── AB09 data-q 必须是问句形态 ───────────────────
for fn in _lesson_htmls():
    if not fn.endswith(".html"):
        continue
    h = rd(os.path.join(WS, "lessons", fn))
    qs = re.findall(r'data-q="([^"]*)"', h)
    bad = [q for q in qs if not (q.endswith("？") or q.endswith("?"))]
    chk(not bad, f"AB09 {fn} data-q 都是问句（{len(qs)} 个）", f"不像问题：{bad[:2]}")

# ── AB10 SKILL.md 指向 09 §3.2 且该节真实存在 ────
chk("§3.2" in sk and "3.2 九种图型" in r9,
    "AB10 SKILL.md 指向 09 §3.2，且该节标题真实存在",
    "指路指向不存在的章节 = 执行者找不到")
chk(re.findall(r"^### 3\.2 ", r9, re.M) != [],
    "AB11 09 §3.2 标题层级正确（### 而非 ##）", "层级错会导致目录解析失败")

# ── AB12 0003 图型与内容匹配（不能为了凑 2D/3D 硬套）──
_h3_path = os.path.join(WS, "lessons", "0003-冷却时间.html")
if os.path.isfile(_h3_path):
    h3 = rd(_h3_path)
    caps = re.findall(r"<figcaption>([\s\S]*?)</figcaption>", h3)
    chk(len(caps) == 3, f"AB12 0003 有 3 条 figcaption（实 {len(caps)}）", "图与说明数量不符")
    chk(all(len(re.sub(r"<[^>]+>", "", c)) >= 40 for c in caps),
        "AB13 每条 figcaption 都能独立说明（≥40 字）", "太短的说明图读不懂")

# ── 汇总 ────────────────────────────────────────
print()
if FAILS:
    print(f"AB 段 {len(FAILS)} 项 FAIL：")
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("AB 段全部 PASS")
