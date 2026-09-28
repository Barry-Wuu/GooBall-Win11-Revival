#!/usr/bin/env python3
"""按 Ogg stream serial 分组重建完整 Ogg 文件。
Unity 1.x 把 Ogg 完整页（含 OggS）散落在流区，对象内仅存头两页。
通过 serial 聚合所有同 serial 页，按文件偏移排序拼接 -> 完整 Ogg。
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\audio'
os.makedirs(OUT, exist_ok=True)

u = Unity1x(os.path.join(D, 'sharedassets.assets'))
raw = u.raw

# 1) 扫描所有 OggS 页
pages = []  # (serial, file_offset, page_bytes, eos)
i = 0
while i < len(raw) - 27:
    if raw[i:i+4] != b'OggS':
        i += 1
        continue
    segn = raw[i+26]
    tbl = raw[i+27:i+27+segn]
    decl = sum(tbl)
    eos = bool(raw[i+5] & 0x04)
    serial = struct.unpack_from('<I', raw, i+14)[0]
    pages.append((serial, i, 27+segn+decl, eos))
    i += 27 + segn + decl
print(f'扫描到 Ogg 页: {len(pages)}')

# 2) 按 serial 分组
from collections import defaultdict
groups = defaultdict(list)
for serial, off, size, eos in pages:
    groups[serial].append((off, size, eos))
print(f'不同 serial 数: {len(groups)}')

# 3) 对每个 AudioClip Ogg 对象，取头页 serial，重建
def safe(name):
    return ''.join(c if c.isalnum() or c in ' -_' else '_' for c in name)

aus = [o for o in u.objects if o.classID == 83]
aus.sort(key=lambda o: o.pathID)
ok = 0
for o in aus:
    d = u.obj_data(o)
    n = int.from_bytes(d[0:4], 'big')
    if not (0 < n < 200):
        continue
    name = d[4:4+n].decode('ascii', 'replace')
    p = 4 + n
    fmt = int.from_bytes(d[p:p+4], 'big')
    if fmt != 5:
        continue
    idx = d.find(b'OggS')
    serial = struct.unpack_from('<I', d, idx+14)[0]
    if serial not in groups:
        print(f'  [!] {name}: serial {serial:#x} 无流区页')
        continue
    grp = sorted(groups[serial])
    blob = b''.join(raw[off:off+size] for off, size, eos in grp)
    last_eos = grp[-1][2]
    fp = os.path.join(OUT, safe(name) + '.ogg')
    with open(fp, 'wb') as f:
        f.write(blob)
    ok += 1
    n_pages = len(grp)
    print(f'  [Ogg] {name[:30]:<32} serial={serial:#010x} 页={n_pages} 末页EOS={last_eos} -> {len(blob):,}B')
print(f'\n重建完成: {ok} 个 Ogg -> {OUT}')
