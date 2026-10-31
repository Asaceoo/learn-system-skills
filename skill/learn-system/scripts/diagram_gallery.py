# -*- coding: utf-8 -*-
"""把 11-visual-grammar.md §2 的八种结构/数据图型，各生成一个可复制的骨架样例。

为什么要有这个文件：光在表格里写「有八种图型」等于没写。
真正需要的时刻是「我要画一张鱼骨图」，那时手上得有现成坐标可改，
不是从零算像素（手算坐标必然压线，前面已经踩过五轮）。

用法：
    python diagram_gallery.py                 # 生成 assets/diagram-gallery.html
    python diagram_gallery.py out.html        # 指定输出

每张图都满足 11 §7 无障碍契约（role=img + aria-labelledby + 前缀化 title/desc，
title 是首子元素）与 §8 手机宽（min-width = viewBox 宽）。
只依赖标准库。
"""
import io
import os
import sys

INK, INK3 = "#1a1a1a", "#767676"
MAIN, LIGHT = "#8a5a2b", "#e7ddd0"
FOCUS, OK, BAND = "#b3403a", "#2f7a4d", "#f2ede4"
PAPER = "#fdfcfa"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def wrap(slug, title, desc, w, h, body):
    """统一的图壳：无障碍四条 + min-width。"""
    return (
        '<svg class="fig" viewBox="0 0 %d %d" role="img" '
        'aria-labelledby="%s-title %s-desc" style="min-width:%dpx" '
        'xmlns="http://www.w3.org/2000/svg">'
        '<title id="%s-title">%s</title><desc id="%s-desc">%s</desc>'
        '<rect width="100%%" height="100%%" fill="%s"/>%s</svg>'
        % (w, h, slug, slug, w, slug, esc(title), slug, esc(desc), PAPER, body))


def txt(x, y, s, size=11, fill=INK, anchor="start", weight="400"):
    return ('<text x="%.0f" y="%.0f" font-size="%d" fill="%s" text-anchor="%s" '
            'font-weight="%s" font-family="-apple-system,Segoe UI,Microsoft YaHei,sans-serif">%s</text>'
            % (x, y, size, fill, anchor, weight, esc(s)))


def box(x, y, w, h, label, fill="#fff", stroke="#c9c9c9", sw=1, sub="", rx=6):
    out = ['<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="%d" fill="%s" '
           'stroke="%s" stroke-width="%s"/>' % (x, y, w, h, rx, fill, stroke, sw)]
    if sub:
        out.append(txt(x + w / 2, y + h / 2 - 2, label, 12, INK, "middle", "500"))
        out.append(txt(x + w / 2, y + h / 2 + 14, sub, 11, INK3, "middle"))
    else:
        out.append(txt(x + w / 2, y + h / 2 + 4, label, 12, INK, "middle", "500"))
    return "".join(out)


def arrow_def(mid="ar"):
    return ('<defs><marker id="%s" markerWidth="7" markerHeight="7" refX="6" refY="3" '
            'orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#b9afa2"/></marker></defs>' % mid)


# ---------------------------------------------------------------- S1 层叠
def s1_stack():
    W, H = 620, 210
    layers = [("应用层 · 能判断该调哪个参数", BAND),
              ("工艺层 · 五组参数各管什么", "#fff"),
              ("材料层 · 收缩 / 流动从哪来", "#fff"),
              ("设备层 · 机器能给你多大压力", "#fff"),
              ("基础层 · 热量怎么传、压力怎么衰减", BAND)]
    b = [arrow_def()]
    y = 14
    for name, fill in layers:
        b.append('<rect x="24" y="%.0f" width="572" height="34" rx="5" fill="%s" '
                 'stroke="#cfc7bb" stroke-width="1"/>' % (y, fill))
        b.append(txt(40, y + 22, name, 12))
        y += 38
    b.append(txt(604, 200, "上层依赖下层 →", 11, INK3, "end"))
    return wrap("s1", "层叠图样例", "五层技能由下往上支撑，上层问题要回到下层找原因", W, H, "".join(b))


# ---------------------------------------------------------------- S2 树
def s2_tree():
    # 1 根 + 3 类 + 5 叶 = 9 个节点，正好在 11 §3 预算内。
    # 原版 4 类 10 节点超预算——样例自己都不能超。
    W, H = 620, 230
    b = [arrow_def("ar2")]
    b.append(box(230, 12, 160, 40, "缺陷", "#fff", MAIN, 1.6))
    cats = [("尺寸类", 40, ["偏大", "偏小"]),
            ("外观类", 240, ["飞边", "缩痕"]),
            ("结构类", 450, ["翘曲"])]
    for name, x, kids in cats:
        b.append('<path d="M310,52 L%.0f,84" stroke="#b9afa2" stroke-width="1" marker-end="url(#ar2)"/>'
                 % (x + 55))
        b.append(box(x, 88, 110, 32, name, BAND))
        yy = 132
        for k in kids:
            b.append('<path d="M%.0f,120 L%.0f,%.0f" stroke="#b9afa2" stroke-width="1"/>'
                     % (x + 55, x + 55, yy - 2))
            b.append(box(x + 8, yy, 94, 26, k, "#fff", "#d8d2c7", 1, rx=4))
            yy += 32
    return wrap("s2", "树图样例", "缺陷按类别逐层细分，每个叶子是一个可单独排查的对象", W, H, "".join(b))


# ---------------------------------------------------------------- S3 包含
def s3_nested():
    W, H = 620, 230
    rings = [("工艺窗口（能稳定生产的范围）", 20, 20, 580, 190, BAND, MAIN),
             ("可加工范围（不烧料、不欠注）", 60, 56, 500, 118, "#fff", "#b9afa2"),
             ("推荐区间（首件一次过）", 110, 96, 400, 46, "#fff", OK)]
    b = []
    for name, x, y, w, h, fill, stroke in rings:
        b.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" '
                 'stroke="%s" stroke-width="1.2"/>' % (x, y, w, h, fill, stroke))
        b.append(txt(x + 12, y + 18, name, 11, INK3))
    b.append(txt(310, 122, "实际取值落在这里", 12, OK, "middle", "500"))
    return wrap("s3", "包含图样例", "范围套范围：越往内越安全，但可用余地也越小", W, H, "".join(b))


# ---------------------------------------------------------------- S4 时间轴
def s4_timeline():
    W, H = 620, 230
    b = ['<path d="M40,150 L566,150" stroke="#b9afa2" stroke-width="1.5"/>',
         '<path d="M566,150 l-8,-4 l0,8 z" fill="#b9afa2"/>']
    # 相位条画在上方：两段各自标注，交接点单独一条红线——标签不可能撞
    b.append('<rect x="60" y="34" width="230" height="26" rx="4" fill="%s"/>' % BAND)
    b.append('<rect x="290" y="34" width="230" height="26" rx="4" fill="#f0ece4"/>')
    b.append(txt(175, 52, "速度控制：把料填满", 11, MAIN, "middle", "500"))
    b.append(txt(405, 52, "压力控制：把收缩补上", 11, MAIN, "middle", "500"))
    b.append('<path d="M290,26 L290,164" stroke="%s" stroke-width="1.2" stroke-dasharray="4 3"/>' % FOCUS)
    b.append(txt(298, 22, "切换点（V/P）", 11, FOCUS))
    stages = [("合模", 60), ("充模", 175), ("保压", 290), ("冷却", 405), ("开模", 520)]
    for name, x in stages:
        b.append('<circle cx="%d" cy="150" r="5" fill="%s"/>' % (x, MAIN))
        b.append(txt(x, 178, name, 12, INK, "middle", "500"))
    b.append(txt(405, 198, "周期的大头在这段", 11, INK3, "middle"))
    return wrap("s4", "时间轴样例", "成型周期五个阶段，以及速度控制与压力控制在何时交接", W, H, "".join(b))


# ---------------------------------------------------------------- S5 象限
def s5_quadrant():
    W, H = 620, 250
    b = ['<path d="M60,200 L580,200" stroke="#b9afa2" stroke-width="1"/>',
         '<path d="M60,200 L60,24" stroke="#b9afa2" stroke-width="1"/>',
         txt(560, 220, "调机难度 →", 11, INK3, "end"),
         txt(52, 40, "收益 ↑", 11, INK3, "end")]
    pts = [("保压时间", 150, 70, MAIN), ("模温", 300, 96, MAIN), ("注射速度", 470, 150, FOCUS)]
    b.append('<rect x="60" y="24" width="260" height="88" fill="%s" opacity=".55"/>' % BAND)
    b.append(txt(76, 42, "先做这一格", 11, MAIN))
    for name, x, y, c in pts:
        b.append('<circle cx="%d" cy="%d" r="5" fill="%s"/>' % (x, y, c))
        b.append(txt(x + 10, y + 4, name, 11, INK))
    return wrap("s5", "象限图样例", "按调机难度与收益两个维度摆放参数，左上角优先动", W, H, "".join(b))


# ---------------------------------------------------------------- S6 因果鱼骨
def s6_fishbone():
    # 620px 宽的画布放不下「4 骨 × 3 刺」——必然叠字。
    # 所以这里只画 4 骨 × 1 条主因：1 结果 + 4 类 + 4 成因 = 9 个节点，正好在 11 §3 预算内。
    # 要更多成因，就拆成两张图（一张一类的细分），不要往这张里塞。
    W, H = 620, 300
    b = [arrow_def("ar6")]
    b.append('<path d="M36,150 L500,150" stroke="#b9afa2" stroke-width="1.6" marker-end="url(#ar6)"/>')
    b.append(box(506, 130, 84, 40, "飞边", "#fff", FOCUS, 1.8))
    bones = [("料", 150, -1, "流动性过高"), ("机", 268, 1, "锁模力不足"),
             ("模", 386, -1, "分型面磨损"), ("法", 470, 1, "V/P 切换太晚")]
    for name, x, side, cause in bones:
        tip_y = 150 - side * 88
        tip_x = x - 26
        b.append('<path d="M%d,150 L%d,%.0f" stroke="#b9afa2" stroke-width="1.2"/>'
                 % (x, tip_x, tip_y))
        # 类别名在骨端外侧
        b.append(txt(tip_x, tip_y + (-10 if side < 0 else 20), name, 13, MAIN, "middle", "500"))
        # 成因贴着骨的中段，朝远离脊椎的一侧排，右对齐到骨的左边
        my = (150 + tip_y) / 2
        mx = (x + tip_x) / 2
        b.append('<path d="M%.0f,%.0f L%.0f,%.0f" stroke="#d8d2c7" stroke-width="1"/>'
                 % (mx, my, mx - 16, my))
        b.append(txt(mx - 20, my + 4, cause, 11, INK3, "end"))
    return wrap("s6", "因果鱼骨图样例",
                "一个结果（飞边）的四类主因：料、机、模、法，每类只放最可能的一条",
                W, H, "".join(b))


# ---------------------------------------------------------------- S7 热力图
def s7_heat():
    W, H = 620, 210
    rows = ["材料", "壁厚", "模温", "注射速度", "保压"]
    cols = ["飞边", "缩痕", "翘曲", "熔接痕"]
    data = [[3, 1, 2, 1], [0, 3, 2, 0], [0, 1, 3, 1], [3, 0, 1, 3], [3, 3, 1, 1]]
    x0, y0, cw, ch = 110, 40, 110, 30
    b = []
    for j, c in enumerate(cols):
        b.append(txt(x0 + j * cw + cw / 2, y0 - 10, c, 11, INK3, "middle"))
    for i, r in enumerate(rows):
        b.append(txt(x0 - 12, y0 + i * ch + 20, r, 11, INK3, "end"))
        for j, v in enumerate(data[i]):
            op = 0.08 if v <= 1 else (0.20 if v == 2 else 0.34)
            b.append('<rect x="%d" y="%d" width="%d" height="%d" fill="rgba(138,90,43,%.2f)" '
                     'stroke="#e7e2d8" stroke-width="1"/>'
                     % (x0 + j * cw, y0 + i * ch, cw, ch, op))
            b.append(txt(x0 + j * cw + cw / 2, y0 + i * ch + 20, v, 11,
                         INK if v >= 2 else INK3, "middle"))
    return wrap("s7", "热力图样例", "参数与缺陷的关系强弱，格子越深表示影响越大", W, H, "".join(b))


# ---------------------------------------------------------------- S8 条形
def s8_bar():
    W, H = 620, 210
    items = [("冷却", 46), ("保压", 22), ("充模", 15), ("开合模", 10), ("顶出", 7)]
    b = [txt(24, 22, "各阶段占成型周期的时间比例（示意）", 11, INK3)]
    y = 40
    for name, v in items:
        b.append(txt(24, y + 15, name, 11, INK3))
        b.append('<rect x="90" y="%.0f" width="%.0f" height="20" rx="3" fill="%s"/>'
                 % (y, v * 9.4, MAIN if v > 30 else LIGHT))
        b.append(txt(96 + v * 9.4, y + 15, "%d%%" % v, 11, INK))
        y += 32
    return wrap("s8", "条形图样例", "各阶段占比，长度正比于数值", W, H, "".join(b))


CARDS = [
    ("S1 层叠", "这件事分几层？上下层是支撑还是并列？", s1_stack),
    ("S2 树", "谁包含谁、谁属于谁？", s2_tree),
    ("S3 包含", "范围套范围，我在哪一圈里？", s3_nested),
    ("S4 时间轴", "什么时候发生什么？顺序能换吗？", s4_timeline),
    ("S5 象限", "两个维度上各在哪？取舍在哪一格？", s5_quadrant),
    ("S6 因果鱼骨", "一个结果的多类成因分别是什么？", s6_fishbone),
    ("S7 热力图", "多个对象 × 多个维度，哪格最烫？", s7_heat),
    ("S8 条形", "谁高谁低？差多少？", s8_bar),
]

HTML = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>结构图型样例库 · 八种</title>
<style>
  :root{--ink:#1a1a1a;--ink3:#767676;--line:#e2ded4;--accent:#8a5a2b;--bg:#fffdf8}
  body{margin:0;padding:28px 20px 60px;background:var(--bg);color:var(--ink);
    font-family:"PingFang SC","Microsoft YaHei",system-ui,sans-serif;line-height:1.7;
    max-width:760px;margin:0 auto}
  h1{font-size:20px;margin:0 0 4px}
  .meta{color:var(--ink3);font-size:13px;margin-bottom:22px}
  .item{margin:0 0 26px;border:1px solid var(--line);border-radius:10px;background:#fff;
    padding:14px 14px 10px}
  .item h2{font-size:15px;margin:0 0 2px;color:var(--accent)}
  .item .q{font-size:13px;color:var(--ink3);margin:0 0 10px}
  .item .wrap{overflow-x:auto}
  .item svg{display:block;height:auto}
  .item .how{font-size:12px;color:var(--ink3);margin-top:8px;border-top:1px dashed var(--line);
    padding-top:8px}
  code{background:#f4f1ea;padding:1px 4px;border-radius:3px;font-size:12px}
</style></head><body>
<h1>结构图型样例库 · 八种</h1>
<div class="meta">对应 <code>references/11-visual-grammar.md</code> §2。每张都满足 §7 无障碍契约与 §8 手机宽。</div>
%s
<div class="muted" style="font-size:12px;color:#767676;margin-top:10px">
用法：找一张与你要讲的关系最接近的，<b>照抄结构、换标签、按数据改坐标</b>，不要从零算像素。<br>
与 <code>09</code> §3.2 的九种机制图（坐标曲线类）互补：那些讲「为什么」，这八种讲「有什么 / 在哪层 / 多少」。
</div>
</body></html>
"""


def build(out_path):
    cards = []
    for name, q, fn in CARDS:
        svg = fn()
        cards.append(
            '<div class="item"><h2>%s</h2><p class="q">%s</p>'
            '<div class="wrap">%s</div>'
            '<div class="how">复制时保留 <code>role</code> / <code>aria-labelledby</code> / '
            '<code>&lt;title&gt;</code> 三个属性，改 <code>slug</code> 前缀避免同页撞 id。</div></div>'
            % (esc(name), esc(q), svg))
    html = HTML % "\n".join(cards)
    os.makedirs(os.path.dirname(out_path), exist_ok=True) if os.path.dirname(out_path) else None
    io.open(out_path, "w", encoding="utf-8", newline="\n").write(html)
    return len(CARDS)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "assets", "diagram-gallery.html")
    n = build(out)
    print("已生成 %s（%d 种图型，%.1f KB）" % (out, n, os.path.getsize(out) / 1024.0))
