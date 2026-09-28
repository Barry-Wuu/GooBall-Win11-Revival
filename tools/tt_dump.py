#!/usr/bin/env python3
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
u = Unity1x(os.path.join(D, 'sharedassets.assets'))
meta = u.meta

# dump 开头 0x100 字节，8 列
print("=== meta 开头 (hex) ===")
line = meta[:0x200]
for off in range(0, len(line), 16):
    h = ' '.join(f'{x:02x}' for x in line[off:off+16])
    a = ''.join(chr(x) if 32<=x<127 else '.' for x in line[off:off+16])
    print(f"{off:04x}: {h:<48} {a}")

# 探测：第一个可读 ASCII 出现在哪（TypeTree 文本起点）
print("\n=== 找第一个 TypeTree 类名 ===")
# 文本名通常在 classID 列表之后。先看 meta[4:8] 等
for b in range(0, 0x40, 4):
    vbe = struct.unpack('>I', meta[b:b+4])[0]
    vle = struct.unpack('<I', meta[b:b+4])[0]
    print(f"off {b:#x}: BE={vbe:>10} LE={vle:>10} hex={meta[b:b+4].hex()}")
