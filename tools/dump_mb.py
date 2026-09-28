#!/usr/bin/env python3
"""dump 一个 MonoBehaviour 对象的原始字节 + 其 TypeTree 字段定义。"""
import os, sys, struct
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'

# 在 level0 找第一个 MonoBehaviour
for fn in [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]:
    p = os.path.join(D, fn)
    u = Unity1x(p)
    idxs = u.by_class(17)
    if not idxs:
        continue
    print(f"=== {fn}: 找到 {len(idxs)} 个 MonoBehaviour, 取 idx={idxs[0]} ===")
    o = u.objects[idxs[0]]
    print("object:", o)
    raw = u.obj_data(o)
    print(f"raw 长度 {len(raw)}")
    # 解析 name: u32 BE len + bytes
    nl = struct.unpack('>I', raw[0:4])[0]
    name = raw[4:4+nl].decode('ascii', 'replace')
    print(f"name(len={nl}) = {name!r}")
    # 接下来 PPtr<MonoScript> = fileID(i32 LE) + pathID(i32 LE)
    base = 4 + nl
    fid = struct.unpack('<i', raw[base:base+4])[0]
    pid = struct.unpack('<i', raw[base+4:base+8])[0]
    print(f"PPtr<MonoScript>: fileID={fid} pathID={pid}")
    # dump 之后字节
    rest = raw[base+8:]
    print(f"之后 {len(rest)} 字节 (hex ascii):")
    for off in range(0, min(len(rest), 200), 16):
        seg = rest[off:off+16]
        h = ' '.join(f'{x:02x}' for x in seg)
        a = ''.join(chr(x) if 32<=x<127 else '.' for x in seg)
        print(f"  +{off:03x}: {h:<48} {a}")
    break
