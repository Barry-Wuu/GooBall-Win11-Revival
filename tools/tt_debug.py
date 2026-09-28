#!/usr/bin/env python3
import os, sys, struct, re
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x
D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
u = Unity1x(os.path.join(D, 'sharedassets.assets'))
meta = u.meta
# 找前 6 个 'Base\0'
cnt=0
for m in re.finditer(rb'Base\x00', meta):
    p = m.start()
    print(f"--- 'Base' @ {p:#x} ---")
    seg = meta[p-20:p+20]
    for off in range(0, len(seg), 4):
        v = struct.unpack('<i', seg[off:off+4])[0]
        h = seg[off:off+4].hex()
        a = ''.join(chr(x) if 32<=x<127 else '.' for x in seg[off:off+4])
        print(f"  rel{off:+03d}: {v:>12}  {h}  {a}")
    cid_be = struct.unpack('>i', meta[p+5:p+9])[0]
    print(f"  >> classID@p+5 BE = {cid_be}")
    cnt+=1
    if cnt>=6: break
