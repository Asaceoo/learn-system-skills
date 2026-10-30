#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""兜底校验：文档里宣称的审计项数，必须等于审计脚本实际跑出的 PASS 数。

为什么需要它：审计脚本内部的 W 段只能比较「三份文档之间是否一致」，
无法知道自己一共跑了多少项（T/V 段是子进程跑的）。所以「文档说 127、实际 128」
这类偏差它能一致地漏过去——v0.7.3 就漏过一次。

用法： python tools/count_checks.py
退出码： 0 = 一致；1 = 不一致（build.py 会据此拒绝打包）
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "learn-system-audit.py")
DOCS = ["README.md", os.path.join("docs", "USER_GUIDE.md"), os.path.join("docs", "TECHNICAL.md")]

r = subprocess.run([sys.executable, AUDIT], capture_output=True, text=True, cwd=ROOT)
actual = len([ln for ln in r.stdout.splitlines() if ln.strip().startswith("PASS")])
ok_run = r.returncode == 0

print("审计实际 PASS 项数：%d（退出码 %d）" % (actual, r.returncode))
if not ok_run:
    print("!! 审计本身有 FAIL，先修审计")
    tail = [ln for ln in r.stdout.splitlines() if "FAIL" in ln][:8]
    for t in tail:
        print("   " + t.strip())
    sys.exit(1)

bad = []
for d in DOCS:
    p = os.path.join(ROOT, d)
    if not os.path.exists(p):
        continue
    t = open(p, encoding="utf-8").read()
    nums = {int(x) for x in re.findall(r"(\d{2,3})\s*项", t) if int(x) >= 50}
    if not nums:
        bad.append("%s 未写审计项数" % d)
        continue
    for n in nums:
        mark = "OK " if n == actual else "MISMATCH"
        print("  %-9s %s 说 %d 项" % (mark, d, n))
        if n != actual:
            bad.append("%s 说 %d 项，实际 %d 项" % (d, n, actual))

print("-" * 50)
if bad:
    print("不一致 %d 处：" % len(bad))
    for b in bad:
        print("  - " + b)
    print("\n修法：把三份文档里的数字改成 %d，然后重跑。" % actual)
    sys.exit(1)
print("文档写明的项数与实际一致（%d）" % actual)
