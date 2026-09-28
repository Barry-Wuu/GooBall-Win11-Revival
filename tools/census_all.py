#!/usr/bin/env python3
"""全文件 classID 普查（含 level0..68 + mainData + sharedassets）"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x
from collections import defaultdict, Counter

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
files = [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]

tot = Counter()
per_file = {}
for fn in files:
    p = os.path.join(D, fn)
    if not os.path.exists(p):
        print("MISSING", fn); continue
    u = Unity1x(p)
    c = Counter(o.classID for o in u.objects)
    per_file[fn] = c
    tot.update(c)

print("=== 全局 classID 计数 ===")
for cid, n in sorted(tot.items()):
    print(f"  classID={cid:>4}  x{n}")
print(f"\n总对象数: {sum(tot.values())}")
print(f"文件数: {len(files)}")

# 找出 Font(14)/TextMesh(13)/MonoBehaviour(17)/MonoScript 等
for target in (13, 14, 17, 107, 21, 115, 111, 114):
    files_with = [fn for fn,c in per_file.items() if c.get(target)]
    if files_with:
        print(f"\nclassID={target} 出现于 {len(files_with)} 文件: {files_with[:8]}")
