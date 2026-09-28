#!/usr/bin/env python3
import os, sys, struct
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x
D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'

def dump_one(cid, label):
    for fn in [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]:
        p = os.path.join(D, fn)
        if not os.path.exists(p): continue
        u = Unity1x(p)
        for i in u.by_class(cid):
            o = u.objects[i]
            raw = u.obj_data(o)
            print(f"=== {label} classID={cid} 来自 {fn} idx={i} size={o.size} ===")
            # 扫描所有可见 ascii 字符串
            s = raw
            # 找所有 \x00 分隔的 ascii 串
            strings = []
            cur = bytearray()
            for b in s:
                if 32 <= b < 127:
                    cur.append(b)
                else:
                    if len(cur) >= 2:
                        strings.append(bytes(cur).decode('ascii'))
                    cur = bytearray()
            if cur: strings.append(bytes(cur).decode('ascii'))
            print("  可读字符串:", strings[:12])
            # hex 头
            for off in range(0, min(len(raw), 120), 16):
                seg = raw[off:off+16]
                h = ' '.join(f'{x:02x}' for x in seg)
                a = ''.join(chr(x) if 32<=x<127 else '.' for x in seg)
                print(f"  +{off:03x}: {h:<48} {a}")
            return
    print(f"{label} classID={cid} 未找到")

dump_one(102, "TextMesh")
