#!/usr/bin/env python3
"""提取 Shader（classID 48）—— 对象内即源码文本。
布局: u32BE namelen | name | u32BE srclen | src
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\shaders'
os.makedirs(OUT, exist_ok=True)
u = Unity1x(os.path.join(D, 'sharedassets.assets'))

def safe(s):
    return ''.join(c if c.isalnum() or c in ' -_.' else '_' for c in s).strip() or 'shader'

ok = 0; bad = []
for o in u.objects:
    if o.classID != 48:
        continue
    d = u.obj_data(o)
    n = int.from_bytes(d[0:4], 'big')
    if not (0 < n < 200):
        bad.append(o.pathID); continue
    name = d[4:4+n].decode('ascii', 'replace')
    p = 4 + n
    src_len = int.from_bytes(d[p:p+4], 'big')
    src = d[p+4:p+4+src_len]
    txt = src.decode('utf-8', 'replace')
    fn = os.path.join(OUT, f"{safe(name)}_{o.pathID}.shader")
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(txt)
    ok += 1

print(f"Shader 提取: {ok}  -> {OUT}")
print("失败:", bad[:5])
# 打印几个 shader 头行
for f in sorted(os.listdir(OUT))[:6]:
    first = open(os.path.join(OUT, f), encoding='utf-8', errors='replace').readline().strip()
    print(f"  {f[:40]:<42} | {first[:60]}")
