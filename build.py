#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""learn-system 打包脚本：自动递增版本号 → 同步三份文档 → 打技能 zip。

用法:
    python build.py              # 默认递增 patch
    python build.py --bump minor # 递增 minor
    python build.py --bump major # 递增 major
    python build.py --no-bump    # 只打包，不动版本号

产物:
    VERSION                      版本号（唯一真源）
    dist/learn-system-vX.Y.Z.zip 技能包（解压即用）
"""
import argparse, os, re, sys, zipfile, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(ROOT, "skill", "learn-system")
DOCS = [
    os.path.join(ROOT, "README.md"),
    os.path.join(ROOT, "docs", "USER_GUIDE.md"),
    os.path.join(ROOT, "docs", "TECHNICAL.md"),
]
VERSION_FILE = os.path.join(ROOT, "VERSION")
INSTALLED = os.path.join(os.path.expanduser("~"), ".workbuddy", "skills", "learn-system")
DIST = os.path.join(ROOT, "dist")

# 文档里所有需要同步的版本号写法
PATTERNS = [
    re.compile(r"(版本[：:] *v?)(\d+\.\d+\.\d+)"),
    re.compile(r"(Version:? *v?)(\d+\.\d+\.\d+)", re.I),
    re.compile(r"(learn-system[ -]v)(\d+\.\d+\.\d+)"),
    re.compile(r"(\| *版本 *\| *v?)(\d+\.\d+\.\d+)"),
]


def read_version():
    if os.path.exists(VERSION_FILE):
        return open(VERSION_FILE, encoding="utf-8").read().strip()
    return "0.0.0"


def bump(v, part):
    a, b, c = (int(x) for x in v.split("."))
    if part == "major":
        return f"{a+1}.0.0"
    if part == "minor":
        return f"{a}.{b+1}.0"
    return f"{a}.{b}.{c+1}"


def sync_docs(old, new):
    """把三份文档里的旧版本号替换成新版本号，返回改动统计。"""
    changed = []
    for p in DOCS:
        if not os.path.exists(p):
            print(f"  [skip] 文档不存在: {os.path.relpath(p, ROOT)}")
            continue
        t = open(p, encoding="utf-8").read()
        orig = t
        for pat in PATTERNS:
            t = pat.sub(lambda m: m.group(1) + new, t)
        if t != orig:
            open(p, "w", encoding="utf-8", newline="\n").write(t)
            n = sum(1 for a, b in zip(orig.splitlines(), t.splitlines()) if a != b)
            changed.append((os.path.relpath(p, ROOT), n))
        else:
            changed.append((os.path.relpath(p, ROOT), 0))
    return changed


def make_zip(version):
    os.makedirs(DIST, exist_ok=True)
    name = f"learn-system-v{version}.zip"
    path = os.path.join(DIST, name)
    if os.path.exists(path):
        os.remove(path)
    n = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for base, label in [(SKILL, "learn-system"), (os.path.join(ROOT, "docs"), "docs")]:
            if not os.path.isdir(base):
                continue
            for d, _, fs in os.walk(base):
                for f in sorted(fs):
                    full = os.path.join(d, f)
                    rel = os.path.relpath(full, base).replace("\\", "/")
                    z.write(full, f"{label}/{rel}")
                    n += 1
        z.write(VERSION_FILE, "VERSION")
        n += 1
    return path, n


def deploy():
    """仓库副本 -> 已安装副本。不部署 = 改了仓库但跑的还是旧副本（本轮实测踩过）。"""
    if not os.path.isdir(INSTALLED):
        print("部署: 跳过（未找到已安装目录 %s）" % INSTALLED)
        return 0
    import shutil, filecmp
    n = 0
    for base, _, fs in os.walk(SKILL):
        rel = os.path.relpath(base, SKILL)
        dst_dir = INSTALLED if rel == "." else os.path.join(INSTALLED, rel)
        os.makedirs(dst_dir, exist_ok=True)
        for f in fs:
            src, dst = os.path.join(base, f), os.path.join(dst_dir, f)
            if not os.path.exists(dst) or not filecmp.cmp(src, dst, shallow=False):
                shutil.copy2(src, dst)
                n += 1
    print(f"部署: {n} 个文件已同步到已安装副本")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bump", choices=["patch", "minor", "major"], default="patch")
    ap.add_argument("--no-bump", action="store_true")
    args = ap.parse_args()

    old = read_version()
    new = old if args.no_bump else bump(old, args.bump)
    print(f"版本号: v{old} -> v{new}" + ("（--no-bump）" if args.no_bump else f"（bump {args.bump}）"))

    open(VERSION_FILE, "w", encoding="utf-8", newline="\n").write(new + "\n")

    print("同步文档:")
    for rel, n in sync_docs(old, new):
        flag = "OK  " if n else "--  "
        print(f"  {flag}{rel}: {n} 处版本号已更新")

    deploy()

    # 项数兜底：文档说的审计项数必须等于实际。不一致就拒绝打包（v0.7.3 漏过一次）
    cc = os.path.join(ROOT, "tools", "count_checks.py")
    if os.path.exists(cc):
        import subprocess
        print("校验文档项数:")
        if subprocess.call([sys.executable, cc], cwd=ROOT) != 0:
            print("!! 文档项数与实际不符，已拒绝打包。改完再跑 build.py")
            return 1

    path, n = make_zip(new)
    print(f"打包: {os.path.relpath(path, ROOT)}  ({n} 个文件, {os.path.getsize(path)//1024} KB)")
    print(f"完成: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
