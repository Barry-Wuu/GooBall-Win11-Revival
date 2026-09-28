#!/usr/bin/env python3
"""提取 AnimationClip（74）+ 场景绑定（MeshRenderer/MeshFilter → Mesh/Material, Transform 层级）。"""
import sys, os, json, struct
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract'
os.makedirs(os.path.join(OUT, 'animations'), exist_ok=True)
u = Unity1x(os.path.join(D, 'sharedassets.assets'))

def be32(b,i): return int.from_bytes(b[i:i+4],'big')
def bf(b,i): return struct.unpack('>f', b[i:i+4])[0]
def safe(s): return ''.join(c if c.isalnum() or c in ' -_.' else '_' for c in s).strip() or 'x'

def rd_name(d):
    n = be32(d,0)
    return (d[4:4+n].decode('ascii','replace') if 0 < n < 300 else '?'), 4+n

# ---- AnimationClip ----
anims = []
for o in u.objects:
    if o.classID != 74: continue
    d = u.obj_data(o)
    name, p = rd_name(d)
    raw = d[p:]
    # 收集浮点（前 64 个）
    fl = [round(bf(raw, i), 4) for i in range(0, len(raw)-3, 4)]
    # 收集属性名（ascii 串）
    import re
    props = re.findall(rb'[A-Za-z][A-Za-z0-9_]{2,30}', raw)
    props = [x.decode('ascii') for x in props if not x.startswith(b'\x00')][:12]
    with open(os.path.join(OUT,'animations', f"{safe(name)}_{o.pathID}.bin"),'wb') as f:
        f.write(d)
    anims.append({'pathID':o.pathID,'name':name,'size':len(d),
                  'propertyNames':props,'floats':fl[:48]})
with open(os.path.join(OUT,'animations','animations.json'),'w',encoding='utf-8') as f:
    json.dump(anims, f, ensure_ascii=False, indent=1)

# ---- 场景绑定 ----
# MeshRenderer(23): name, m_Enabled(u8), PPtr GameObject(8), u32 matCount, PPtr[] 
# MeshFilter(33):   name, PPtr GameObject(8), PPtr Mesh(8)
# Transform(4):     name, PPtr GameObject, PPtr parent, pos(3f), rot(4f quat), scale(3f)
def rd_pptr(b,i): return (be32(b,i), be32(b,i+4))

renderers = []
for o in u.objects:
    if o.classID != 23: continue
    d = u.obj_data(o); name, p = rd_name(d)
    b = d[p:]
    go = rd_pptr(b, 1)     # 1: 1 字节 enabled
    mc = be32(b, 9)
    mats = [rd_pptr(b, 13+8*k)[1] for k in range(min(mc,32)) if 13+8*k+8 <= len(b)]
    renderers.append({'pathID':o.pathID,'name':name,'gameObject':go[1],'materials':mats})

filters = []
for o in u.objects:
    if o.classID != 33: continue
    d = u.obj_data(o); name, p = rd_name(d)
    b = d[p:]
    go = rd_pptr(b,0); mesh = rd_pptr(b,8)
    filters.append({'pathID':o.pathID,'name':name,'gameObject':go[1],'mesh':mesh[1]})

transforms = []
for o in u.objects:
    if o.classID != 4: continue
    d = u.obj_data(o); name, p = rd_name(d)
    b = d[p:]
    go = rd_pptr(b,0); parent = rd_pptr(b,8)
    pos = [round(bf(b,16+4*k),4) for k in range(3)]
    rot = [round(bf(b,28+4*k),4) for k in range(4)]
    scl = [round(bf(b,44+4*k),4) for k in range(3)]
    transforms.append({'pathID':o.pathID,'prefabName':name,'gameObject':go[1],
                       'parent':parent[1],'pos':pos,'rot':rot,'scale':scl})

with open(os.path.join(OUT,'scene_bindings.json'),'w',encoding='utf-8') as f:
    json.dump({'renderers':renderers,'filters':filters,'transforms':transforms},
              f, ensure_ascii=False, indent=1)

print(f"AnimationClip: {len(anims)} -> animations/")
print(f"MeshRenderer: {len(renderers)}  MeshFilter: {len(filters)}  Transform: {len(transforms)}")
for r in renderers[:4]:
    print("  R", r['name'][:24], "GO", r['gameObject'], "mats", r['materials'])
for t in transforms[:4]:
    print("  T", t['prefabName'][:20], "pos", t['pos'], "parent", t['parent'])
