# -*- coding: utf-8 -*-
"""kbfig —— 课内机制图的坐标换算与 SVG 生成。

纯标准库，无第三方依赖。设计原则：**坐标换算交给机器，标注位置留给人**。

为什么要有它：实测 6 张手写 SVG 抓出 5 处缺陷（文字压曲线、纵深轴与曲线交叉、
箭头贴边被裁、高亮区没对齐拐点），全部源于手工算像素。这个库把这些算术吃掉。

用法（数据坐标一律 0..1，不出现真实数值）：

    from kbfig import Fig, plateau
    f = Fig(xlab="保压时间 t →", ylab="制品重量 / 关键尺寸")
    plateau(f, [(0,.05),(.18,.55),(.36,.9),(.62,.93),(1,.93)],
            knee=.36, knee_label="浇口冻结 t_f",
            band_from=.36, band_label="越过拐点：再加时间也不变")
    print(f.svg(title="保压时间与制品重量"))

命令行自检（写出 4 张样例，覆盖图型 2/3/4/5）：

    python kbfig.py --demo gallery.html
"""

import math
import os
import sys

# ── 配色（与课内页面同一套）────────────────────────────
INK2, INK3 = "#4a4a4a", "#767676"
AXIS, SOFT = "#c9c4bb", "#a8a29a"
MAIN, ALT, LIGHT = "#8a5a2b", "#b07d4d", "#c9ab8c"
FOCUS, OK, BAND = "#b3403a", "#2f7a4d", "#fdf6e9"


class Fig:
    """一张 620 宽的坐标图。数据坐标 0..1 映射到绘图区。"""

    W = 620

    def __init__(self, h=250, pad=(70, 26, 34, 42), xlab="", ylab="",
                 note="示意图，不按比例，不含数值", w=None):
        self.h = h
        self.w = w or self.W
        self.pl, self.pr, self.pt, self.pb = pad
        self.xlab, self.ylab, self.note = xlab, ylab, note
        self.items = []

    # ── 坐标换算 ──────────────────────────────────────
    def X(self, t):
        return self.pl + t * (self.w - self.pl - self.pr)

    def Y(self, v):
        return self.h - self.pb - v * (self.h - self.pb - self.pt)

    # ── 图元 ─────────────────────────────────────────
    def band(self, t0, t1, color=BAND, opacity=.8, off=(0, 0)):
        x0, x1 = sorted((self.X(t0), self.X(t1)))
        y0, y1 = self.pt - 4, self.h - self.pb
        self.items.append(
            f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{x1 - x0:.0f}" '
            f'height="{y1 - y0:.0f}" fill="{color}" opacity="{opacity}" '
            f'transform="translate({off[0]},{off[1]})"/>')

    def line(self, pts, color=MAIN, width=2.5, smooth=True, off=(0, 0), dash=None):
        d = self._path(pts, smooth, off)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da}/>')

    def vline(self, t, color=FOCUS, off=(0, 0), dash="4 3", v0=0, v1=1):
        x = self.X(t) + off[0]
        self.items.append(
            f'<line x1="{x:.0f}" y1="{self.Y(v1) + off[1]:.0f}" '
            f'x2="{x:.0f}" y2="{self.Y(v0) + off[1]:.0f}" '
            f'stroke="{color}" stroke-width="1" stroke-dasharray="{dash}"/>')

    def dot(self, t, v, color=FOCUS, r=4, off=(0, 0)):
        self.items.append(
            f'<circle cx="{self.X(t) + off[0]:.0f}" cy="{self.Y(v) + off[1]:.0f}" '
            f'r="{r}" fill="{color}"/>')

    def text(self, t, v, s, color=INK3, anchor="start", off=(0, 0), size=11):
        self.items.append(
            f'<text x="{self.X(t) + off[0]:.0f}" y="{self.Y(v) + off[1]:.0f}" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}">{_esc(s)}</text>')

    def ptext(self, x, y, s, color=INK3, anchor="start", size=11):
        self.items.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}">{_esc(s)}</text>')

    def arrow(self, t1, v1, t2, v2, color=OK, dash="3 3", head=True):
        x1, y1 = self.X(t1), self.Y(v1)
        x2, y2 = self.X(t2), self.Y(v2)
        self.items.append(
            f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="{color}" stroke-width="1.2" stroke-dasharray="{dash}"/>')
        if head:
            ang = math.atan2(y2 - y1, x2 - x1)
            L, Wd = 7, 4
            px, py = x2 - L * math.cos(ang), y2 - L * math.sin(ang)
            self.items.append(
                f'<polygon points="{x2:.0f},{y2:.0f} '
                f'{px - Wd * math.sin(ang):.0f},{py + Wd * math.cos(ang):.0f} '
                f'{px + Wd * math.sin(ang):.0f},{py - Wd * math.cos(ang):.0f}" fill="{color}"/>')

    # ── 组装 ─────────────────────────────────────────
    def _axes(self):
        out = [
            f'<line x1="{self.pl}" y1="{self.h - self.pb}" x2="{self.W - self.pr}" '
            f'y2="{self.h - self.pb}" stroke="{AXIS}" stroke-width="1"/>',
            f'<line x1="{self.pl}" y1="{self.h - self.pb}" x2="{self.pl}" '
            f'y2="{self.pt}" stroke="{AXIS}" stroke-width="1"/>',
            f'<polygon points="{self.W - self.pr},{self.h - self.pb} '
            f'{self.W - self.pr - 9},{self.h - self.pb - 4} '
            f'{self.W - self.pr - 9},{self.h - self.pb + 4}" fill="{AXIS}"/>',
            f'<polygon points="{self.pl},{self.pt} {self.pl - 4},{self.pt + 8} '
            f'{self.pl + 4},{self.pt + 8}" fill="{AXIS}"/>',
        ]
        if self.xlab:
            out.append(f'<text x="{(self.pl + self.W - self.pr) / 2:.0f}" '
                       f'y="{self.h - 12}" font-size="11" fill="{INK3}" '
                       f'text-anchor="middle">{_esc(self.xlab)}</text>')
        if self.ylab:
            cy = (self.pt + self.h - self.pb) / 2
            out.append(f'<g transform="translate(20,{cy:.0f}) rotate(-90)">'
                       f'<text text-anchor="middle" font-size="11" fill="{INK3}">'
                       f'{_esc(self.ylab)}</text></g>')
        if self.note:
            out.append(f'<text x="{self.pl}" y="16" font-size="11" fill="{SOFT}">'
                       f'{_esc(self.note)}</text>')
        return out

    def svg(self, title="机制图", desc="", slug="fig"):
        """按 11 §7 的无障碍契约输出：role=img + aria-labelledby，title 首子元素，id 带前缀。

        slug 必须是**本页唯一**的短标识（通常就是文件名 slug）。同页多图共用 `title` / `desc`
        这种裸 id 会撞车，读屏会把最后一张图的描述念给第一张听。

        宽度：min-width 等于 viewBox 宽（11 §8），外面必须套 overflow-x 容器——用 figure() 一次做全。
        """
        desc = desc or title
        body = "\n  ".join(self._axes() + self.items)
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img" '
                f'aria-labelledby="{slug}-title {slug}-desc" '
                f'style="min-width:{self.w}px" '
                f'xmlns="http://www.w3.org/2000/svg">\n'
                f'<title id="{slug}-title">{_esc(title)}</title>\n'
                f'<desc id="{slug}-desc">{_esc(desc)}</desc>\n  '
                f'{body}\n</svg>')

    def _path(self, pts, smooth, off):
        xy = [(self.X(t) + off[0], self.Y(v) + off[1]) for t, v in pts]
        if not smooth or len(xy) < 3:
            return "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in xy)
        d = [f"M{xy[0][0]:.0f} {xy[0][1]:.0f}"]
        for i in range(len(xy) - 1):
            p0 = xy[i - 1] if i > 0 else xy[0]
            p1, p2 = xy[i], xy[i + 1]
            p3 = xy[i + 2] if i + 2 < len(xy) else xy[-1]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            d.append(f"C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} "
                     f"{p2[0]:.0f} {p2[1]:.0f}")
        return " ".join(d)


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ── 图型 2：平台/饱和曲线 ────────────────────────────────
def plateau(f, pts, knee, knee_label="拐点", band_from=None,
            band_text="越过拐点：再加也不变", band_sub=None, off=(0, 0)):
    """先升后平。knee 是曲线转平的位置，也是「加投入不再有用」的起点。"""
    f.band(band_from if band_from is not None else knee, 1.0, BAND, .8, off)
    f.line(pts, MAIN, 2.5, True, off)
    f.vline(knee, FOCUS, off)
    kv = _interp(pts, knee)
    f.dot(knee, kv, FOCUS, 4, off)
    f.text(knee, 1.0, knee_label, FOCUS, "end", (off[0] - 8, off[1] + 4))
    f.text(knee + .04, .74, band_text, "#8a6a1f", "start", off)
    if band_sub:
        f.text(knee + .04, .14, band_sub, "#8a6a1f", "start", off)
    return f


# ── 图型 3：交叉窗口 ────────────────────────────────────
def window(f, rise, fall, lo, hi, names=("随参数增大而下降的代价",
                                        "随参数增大而上升的代价"),
           rise_at=(.02, .94), fall_at=(.60, .94),
           band_text="窗口", off=(0, 0)):
    """两条方向相反的代价曲线，中间那条窄带就是可用窗口。

    rise_at / fall_at 是两条曲线标注的位置（数据坐标）。**必须分开摆**：
    两条曲线一降一升，放在同一高度必然交叉。
    """
    f.band(lo, hi, "#eaf3ec", 1.0, off)
    f.line(rise, MAIN, 2.5, True, off)
    f.line(fall, FOCUS, 2.5, True, off)
    f.text(rise_at[0], rise_at[1], names[0], MAIN,
           "end" if rise_at[0] > .5 else "start", off)
    f.text(fall_at[0], fall_at[1], names[1], FOCUS,
           "end" if fall_at[0] > .5 else "start", off)
    # 高亮带本身就是焦点，不另外画中线——中线会穿过带内标签
    f.text((lo + hi) / 2, .62, band_text, OK, "middle", off)
    return f


# ── 图型 4/5：切片族（3D 的等距近似）────────────────────
def slices(f, curves, depth=(52, -28), colors=(LIGHT, ALT, MAIN),
           labels=(), label_off=(8, 18), paxis_label="纵深轴 ↗",
           paxis_len=2, paxis_at=None):
    """同一族曲线沿纵深方向错开，构成 3D 观感。curves 是若干组 (t,v)。"""
    dx, dy = depth
    # 越界即报错：静默画到画布外是手算坐标时代最常见的坑
    for i, pts in enumerate(curves):
        for t, v in pts:
            y = f.Y(v) + dy * i
            if y < 8 or y > f.h - 8:
                raise ValueError(
                    f"slices: 第 {i + 1} 条曲线越界（y={y:.0f}，画布 0..{f.h}）。"
                    f"把 depth 的 dy 调小，或把数据幅度压低。")
    for i, pts in enumerate(curves):
        off = (dx * i, dy * i)
        f.line(pts, colors[min(i, len(colors) - 1)], 2.5 if i == len(curves) - 1 else 2,
               True, off)
        if i < len(labels) and labels[i]:
            px = f.X(pts[-1][0]) + off[0] + label_off[0]
            py = f.Y(pts[-1][1]) + off[1] + label_off[1]
            anchor = "start"
            if px > f.w - 46:                 # 贴边就改右对齐并回退
                anchor, px = "end", min(px, f.w - 8)
            f.items.append(
                f'<text x="{px:.0f}" y="{py:.0f}" font-size="11" fill="{SOFT}" '
                f'text-anchor="{anchor}">{_esc(labels[i])}</text>')
    # 纵深轴（浅色，避免与数据线混淆）
    x0, y0 = f.pl, f.h - f.pb
    x1, y1 = x0 + dx * paxis_len, y0 + dy * paxis_len
    f.items.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" '
                   f'stroke="#ded9d0" stroke-width="1"/>')
    f.items.append(f'<polygon points="{x1},{y1} {x1 - 7},{y1 - 2} {x1 - 3},{y1 + 6}" '
                   f'fill="#ded9d0"/>')
    # 标签默认贴在纵深轴末端的外侧。写死在绘图区角落会压住最低那条曲线起点（真机实测踩到）
    if paxis_label:
        # 默认放在轴的外侧（垂直外推），不落在数据区里。
        # 即便这样也可能与某条曲线相撞——传 paxis_at 显式指定，这是唯一可靠的兜底。
        if paxis_at:
            ax, ay = paxis_at
        else:
            # 落在「纵深轴与横轴之间的夹角空档」：轴末端下方，数据曲线都在它上面
            ax, ay = x1 - 10, y1 + 26
        f.items.append(f'<text x="{ax:.0f}" y="{ay:.0f}" font-size="11" '
                       f'fill="{INK3}" text-anchor="start">{_esc(paxis_label)}</text>')
    return f


def _interp(pts, t):
    # 越界即取端点（与 slices() 的「越界即报错」互补：插值函数要能安全返回端点，
    # 而不是把下界外的点误返回最后一点 y —— 那会让拐点圆点/标签掉到曲线顶端）。
    if t <= pts[0][0]:
        return pts[0][1]
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        if x0 <= t <= x1:
            k = (t - x0) / (x1 - x0) if x1 > x0 else 0
            return y0 + k * (y1 - y0)
    return pts[-1][1]


# ── 自检样例 ────────────────────────────────────────────
def demo(path="gallery.html"):
    figs = []

    f = Fig(xlab="保压时间 t →", ylab="制品重量 / 关键尺寸")
    plateau(f, [(0, .05), (.18, .55), (.36, .9), (.62, .93), (1, .93)],
            knee=.36, knee_label="浇口冻结 t_f",
            band_sub="补料通道已断 → 只增加周期，不增加料")
    figs.append(("2 平台/饱和曲线", "保压时间加长，为什么到某点后不再有用？", f))

    f = Fig(xlab="切换点：提前 ←　　　　→ 推后", ylab="缺陷程度")
    window(f, [(0, .93), (.3, .78), (.55, .34), (.72, .12), (1, .05)],
           [(0, .05), (.3, .08), (.55, .3), (.72, .7), (1, .93)],
           lo=.66, hi=.78, rise_at=(.98, .07), fall_at=(.56, .99),
           names=("欠注 · 末端不足 · 熔接痕明显", "飞边 · 内应力 · 脱模难"))
    figs.append(("3 交叉窗口", "切换点为什么没有唯一正确值？", f))

    f = Fig(xlab="保压时间 t →", ylab="重量 W")
    base = [(.05, .10), (.3, .36), (.55, .52), (.85, .54), (1, .54)]
    slices(f, [base, base, base],
           labels=("低压力", "中压力", "高压力"), paxis_label="保压压力 P ↗")
    figs.append(("4 切片族（曲面近似）", "压力与时间各管什么？", f))

    f = Fig(xlab="沿流长方向的距离 L →（浇口 → 末端）", ylab="压力 P")
    slices(f, [[(.05, .62), (.35, .45), (.65, .22), (.88, .06)],
               [(.05, .70), (.35, .55), (.65, .36), (.88, .20)]],
           labels=("", "晚期"), depth=(46, -26), paxis_label="时间 t ↗")
    f.dot(.88, .20, FOCUS, 3.5, (46, -26))
    f.text(.60, .62, "末端：压力趋近 0", FOCUS, "start")
    figs.append(("5 梯度/衰减曲面", "切换过早过晚各坏在哪？", f))

    rows = []
    for name, q, f in figs:
        rows.append(f'<section><h2>{_esc(name)}</h2>'
                    f'<p class="q">【这张图回答】{_esc(q)}</p>{f.svg(name, q)}</section>')
    html = ('<!DOCTYPE html><html><head><meta charset="utf-8">'
            '<style>body{margin:0;background:#fff;font-family:sans-serif}'
            'section{padding:10px 14px;border-bottom:2px solid #ddd}'
            'h2{font:500 14px sans-serif;color:#333;margin:4px 0}'
            '.q{font:12px sans-serif;color:#666;margin:2px 0 8px}'
            'svg{display:block;width:620px}</style></head><body>'
            + "".join(rows) + '</body></html>')
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return len(figs)


def selftest():
    """行为自检：插值边界 + 无障碍契约 + figure 拒绝非问句 + demo 产量。"""
    pts = [(0.2, 0.1), (0.5, 0.6), (1.0, 0.95)]
    assert abs(_interp(pts, 0.05) - 0.1) < 1e-9, "_interp 下界外应返回第一点 y"
    assert abs(_interp(pts, 0.5) - 0.6) < 1e-9, "_interp 区间内应线性插值"
    assert abs(_interp(pts, 0.99) - 0.943) < 1e-6, "_interp 上界附近插值"
    assert abs(_interp(pts, 2.0) - 0.95) < 1e-9, "_interp 上界外应返回最后一点 y"

    f = Fig(xlab="t", ylab="v")
    plateau(f, pts, knee=0.5, knee_label="k")
    svg = f.svg("自检图", "desc", "selftest")
    assert 'role="img"' in svg and "aria-labelledby=" in svg and "min-width:" in svg
    assert '<title id="selftest-title">' in svg, "title 必须是首子元素且带前缀 id"

    try:
        figure(svg, "不是问句", "x")
        raise AssertionError("figure() 应拒绝非问句 data-q")
    except ValueError:
        pass

    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_selftest_gallery.html")
    n = demo(tmp)
    assert n == 4, "demo 应产出 4 张图，实 %d" % n
    os.remove(tmp)
    return n


def figure(svg_text, q, caption, kind="2d"):
    """包成完整的 <figure data-fig data-q> + overflow-x 容器。

    q 必须是**问句**（这张图回答什么问题）；caption 要能独立读懂，不写「见图」。
    无障碍契约（role=img / aria-labelledby / title 首子元素带前缀 id / min-width）
    由 f.svg(...) 的 slug 参数保证，本函数只负责外层 <figure> 与 overflow-x 容器。

    用法：
        figure(f.svg("平台曲线", "到拐点后补料通道断开", "pf"),
               "为什么保压时间到某点后不再有用？",
               "平台曲线：越过拐点只增周期不增料。")
    """
    if not q.rstrip().endswith(("？", "?")):
        raise ValueError("data-q 必须是问句（11 §1）：" + q)
    return (f'<figure data-fig="{kind}" data-q="{_esc(q)}">\n'
            f'  <div style="overflow-x:auto">\n    {svg_text}\n  </div>\n'
            f'  <figcaption><b>【这张图回答】{_esc(q)}</b> {_esc(caption)}</figcaption>\n'
            f'</figure>')


if __name__ == "__main__":
    if "--demo" in sys.argv:
        i = sys.argv.index("--demo")
        out = sys.argv[i + 1] if i + 1 < len(sys.argv) else "gallery.html"
        n = demo(out)
        print(f"已生成 {n} 张样例 -> {out}")
    elif "--selftest" in sys.argv:
        n = selftest()
        print(f"kbfig 自检通过（{n} 张样例 + 边界/契约校验）")
    else:
        print(__doc__)
