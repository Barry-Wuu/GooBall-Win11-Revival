#!/usr/bin/env python3
"""权威 (classID -> 类型名) 映射：TypeTree 文本自带，文件自带不依赖 UnityPy 现代表。
格式: 'ClassName\\0Base\\0' + int32BE(classID) @ Base起点+5
"""
import os, sys, struct, re
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x
from collections import Counter

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
u = Unity1x(os.path.join(D, 'sharedassets.assets'))
meta = u.meta

def plausible(b):
    return 2 <= len(b) <= 50 and all(48<=c<58 or 65<=c<91 or 97<=c<123 or c==95 for c in b)

seen = {}
for m in re.finditer(rb'Base\x00', meta):
    b = m.start()              # 'B' 位置
    cid = struct.unpack('>i', meta[b+5:b+9])[0]
    # 类名 = Base 前最近 \0 之后、Base 终止\0 之前
    i = b - 2
    while i >= 0 and meta[i] != 0:
        i -= 1
    cls = meta[i+1:b-1]
    if not plausible(cls):
        continue
    nm = cls.decode('ascii')
    if cid not in seen:
        seen[cid] = nm

# 全文件计数
allc = Counter()
for fn in [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]:
    pp = os.path.join(D, fn)
    if not os.path.exists(pp): continue
    uu = Unity1x(pp)
    allc.update(o.classID for o in uu.objects)

print(f"{'classID':>6} {'TypeTree名':<24} {'count':>6}")
for cid in sorted(allc):
    nm = seen.get(cid, '?')
    print(f"{cid:>6} {nm:<24} {allc[cid]:>6}")

# 写出映射
import json
with open(r'D:\GooBall\scripts\_tt_names.json','w') as f:
    json.dump(seen, f, indent=2)
print(f"\n写 _tt_names.json ({len(seen)} 个已知类型)")
