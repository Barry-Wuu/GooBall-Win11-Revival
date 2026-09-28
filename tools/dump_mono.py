#!/usr/bin/env python3
import os, sys, struct
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x
D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'

def dump_one(cid, label, maxlen=300):
    for fn in [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]:
        p = os.path.join(D, fn)
        if not os.path.exists(p): continue
        u = Unity1x(p)
        for i in u.by_class(cid):
            o = u.objects[i]
            raw = u.obj_data(o)
            print(f"=== {label} classID={cid} 来自 {fn} idx={i} size={o.size} ===")
            # 可读字符串
            cur=bytearray(); strs=[]
            for b in raw:
                if 32<=b<127: cur.append(b)
                else:
                    if len(cur)>=3: strs.append(bytes(cur).decode('ascii'))
                    cur=bytearray()
            if cur: strs.append(bytes(cur).decode('ascii'))
            print("  字符串:", strs[:15])
            for off in range(0, min(len(raw), maxlen), 16):
                seg=raw[off:off+16]
                h=' '.join(f'{x:02x}' for x in seg)
                a=''.join(chr(x) if 32<=x<127 else '.' for x in seg)
                print(f"  +{off:03x}: {h:<48} {a}")
            return
    print(f"{label} classID={cid} 未找到")

dump_one(115, "MonoScript")
