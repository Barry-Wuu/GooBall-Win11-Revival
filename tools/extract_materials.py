#!/usr/bin/env python3
"""提取 Material（classID 21）→ JSON。
布局: u32 namelen | name | PPtr shader(8) | u32 texCount | {u32 namelen, name, PPtr tex(8), Vector4}× |
      后续 float/color 属性（u32 namelen, name, value）
扫描器：识别长度前缀的 '_' 名，按后续 8B 是否 PPtr→Texture 判定绑定，否则按 float/color。
"""
import sys, os, json, struct
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\materials'
os.makedirs(OUT, exist_ok=True)
u = Unity1x(os.path.join(D, 'sharedassets.assets'))

obj_by_pid = {o.pathID: o for o in u.objects}
tex_pids = {o.pathID for o in u.objects if o.classID == 28}
shader_by_pid = {o.pathID: o for o in u.objects if o.classID == 48}

def oname(o):
    if o is None: return '?'
    d = u.obj_data(o); n = int.from_bytes(d[0:4],'big')
    return d[4:4+n].decode('ascii','replace') if 0 < n < 200 else '?'

def be32(b,i): return int.from_bytes(b[i:i+4],'big')
def bf(b,i): return struct.unpack('>f', b[i:i+4])[0]

def parse_mat(o):
    d = u.obj_data(o)
    n = be32(d, 0)
    name = d[4:4+n].decode('ascii','replace') if 0 < n < 200 else '?'
    raw = d[4+n:]
    fid, pid = be32(raw,0), be32(raw,4)
    shader_pid = pid if (fid==0 and pid in shader_by_pid) else None
    # texCount
    texcount = be32(raw, 8)
    pos = 12
    textures = []
    # 先按 texCount 精确读纹理条目
    for _ in range(min(texcount, 64)):
        if pos+4 > len(raw): break
        L = be32(raw, pos)
        if not (1 <= L <= 60) or pos+4+L+24 > len(raw): break
        prop = raw[pos+4:pos+4+L].decode('ascii','replace')
        if not prop.startswith('_'): break
        tf, tp = be32(raw,pos+4+L), be32(raw,pos+8+L)
        pos += 4+L+8+16
        textures.append({'prop':prop, 'texPathID':tp,
                         'texName': oname(obj_by_pid.get(tp)) if (tf==0 and tp in tex_pids) else None})
    # 之后扫描 float/color 属性
    scalars = []
    i = pos
    while i < len(raw) - 8:
        L = be32(raw, i)
        if 2 <= L <= 40 and i+4+L <= len(raw):
            nm = raw[i+4:i+4+L]
            if nm[:1] == b'_' and all(32 <= c < 127 for c in nm):
                prop = nm.decode('ascii')
                after = i+4+L
                # 尝试 float（4B）后是否紧跟下一个 name 头或结束
                def next_is_name(q):
                    if q+4 > len(raw): return True
                    if q == len(raw): return True
                    L2 = be32(raw, q)
                    return 2 <= L2 <= 40 and raw[q+4:q+5] == b'_'
                if after+4 <= len(raw) and (after+4 == len(raw) or next_is_name(after+4)):
                    scalars.append({'prop':prop, 'type':'float', 'value':round(bf(raw,after),5)})
                    i = after+4; continue
                if after+16 <= len(raw) and (after+16 == len(raw) or next_is_name(after+16)):
                    scalars.append({'prop':prop, 'type':'color',
                                    'value':[round(bf(raw,after+4*k),4) for k in range(4)]})
                    i = after+16; continue
                i = after; continue
        i += 1
    return {'pathID':o.pathID, 'name':name,
            'shaderPathID':shader_pid, 'shaderName':oname(shader_by_pid.get(shader_pid)) if shader_pid else None,
            'textures':textures, 'properties':scalars}

mats = []
for o in u.objects:
    if o.classID != 21: continue
    try:
        mats.append(parse_mat(o))
    except Exception as e:
        mats.append({'pathID':o.pathID, 'error':str(e)})

with open(os.path.join(OUT, 'materials.json'), 'w', encoding='utf-8') as f:
    json.dump(mats, f, ensure_ascii=False, indent=1)

ntex = sum(1 for m in mats if m.get('textures'))
nsh  = sum(1 for m in mats if m.get('shaderPathID'))
print(f"Material: {len(mats)}  有纹理 {ntex}  有shader {nsh}")
for m in mats[:6]:
    print(f"  {m['name'][:28]:<30} shader={m.get('shaderName')} tex={[t['texName'] for t in m.get('textures',[])]}")
