#!/usr/bin/env python3
"""GooBall Mesh 提取器 v4 —— 结构遍历 + faces/strips 双解。
布局:
  m_LODData:[u32 L]{ LOD:[u32 n]{ MeshData: faces([u32 nf][nf×6B]), strips([u32 ns][ns×2B]) }*n }*L
  m_Vertices:[u32 V][V×Vector3f 大端]
  m_UV:[u32 U][U×Vector2f]
判定 faces vs strips: 取三角数更多且非退化更多的方案。
"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\meshes'
os.makedirs(OUT, exist_ok=True)
u = Unity1x(os.path.join(D, 'sharedassets.assets'))

def safe(s):
    return ''.join(c if c.isalnum() or c in ' -_' else '_' for c in s)
def be32(b, i): return int.from_bytes(b[i:i+4], 'big')
def bef(b, i):  return struct.unpack('>f', b[i:i+4])[0]

def walk(R):
    """返回 (lods, p_after) —— lods: 每个 MeshData 一项 (faces, strips)，不跨 LOD 混合。"""
    L = be32(R, 0)
    if not (1 <= L <= 8):
        return None
    p = 4
    lods = []
    for _ in range(L):
        if p + 4 > len(R): return None
        n = be32(R, p); p += 4
        if not (0 <= n <= 64): return None
        for _ in range(n):
            if p + 4 > len(R): return None
            nf = be32(R, p); p += 4
            if not (0 <= nf <= 200000) or p + nf*6 > len(R): return None
            faces = []
            for k in range(nf):
                a = int.from_bytes(R[p:p+2],'big'); b = int.from_bytes(R[p+2:p+4],'big'); c = int.from_bytes(R[p+4:p+6],'big')
                faces.append((a,b,c)); p += 6
            if p + 4 > len(R): return None
            ns = be32(R, p); p += 4
            if not (0 <= ns <= 500000) or p + ns*2 > len(R): return None
            strips = [int.from_bytes(R[p+2*k:p+2*k+2],'big') for k in range(ns)]
            p += ns*2
            lods.append((faces, strips))
    return lods, p

def strip_to_tris(s):
    tris = []
    # 分段：0xFFFF 为重启
    segs, cur = [], []
    for v in s:
        if v == 0xFFFF:
            if len(cur) >= 3: segs.append(cur)
            cur = []
        else:
            cur.append(v)
    if len(cur) >= 3: segs.append(cur)
    for sg in segs:
        for i in range(len(sg)-2):
            if i & 1:
                tris.append((sg[i+1], sg[i], sg[i+2]))
            else:
                tris.append((sg[i], sg[i+1], sg[i+2]))
    return tris

def tris_ok(tris, V):
    return all(a < V and b < V and c < V and not (a==b or b==c or a==c) for a,b,c in tris)

ok=0; novert=[]; face_used=0; strip_used=0; both=0
for o in u.objects:
    if o.classID != 43: continue
    d = u.obj_data(o)
    n = int.from_bytes(d[0:4],'big')
    if not (0 < n < 200): continue
    name = d[4:4+n].decode('ascii','replace'); R = d[4+n:]
    w = walk(R)
    if w is None:
        novert.append(name); continue
    lods, p = w
    if p + 4 > len(R): novert.append(name); continue
    V = be32(R, p)
    if not (3 <= V <= 60000) or p+4+V*12 > len(R):
        novert.append(name); continue
    # 校验顶点全 real
    if not all(isinstance(bef(R,p+4+j),float) for j in range(0, min(V*12, 4))):
        pass
    verts = [(bef(R,p+4+k*12), bef(R,p+8+k*12), bef(R,p+12+k*12)) for k in range(V)]
    # 每个 MeshData 的 faces/strips 是同一几何的两种索引表示；LOD0 精度最高。
    # faces 非空用 faces；否则 strips 按 Unity 三角带语义展开（相邻共享边 + 绕序交替）。
    # 旧版按退化率在「三角带 / 三元组」两种解读间二选一，三元组胜出时把大地形
    # （水面/峡谷/平面）拆成互不相连的棋盘碎片——strips 只有三角带一种正确读法。
    tris = None
    for f0, s0 in lods:
        ftris = [t for t in f0 if all(i < V for i in t)]
        if ftris:
            tris = ftris; face_used += 1
            break
        if s0:
            st = [s for s in s0 if s < V or s == 0xFFFF]
            t2 = [t for t in strip_to_tris(st) if all(i < V for i in t)]
            if t2:
                tris = t2; strip_used += 1
                break
    if tris is None:
        novert.append(name); continue

    # 剔除退化三角形（重复索引 / 零面积）—— 三角带缝合产生的垃圾
    def keep(t):
        a,b,c = t
        if a==b or b==c or a==c: return False
        va,vb,vc = verts[a],verts[b],verts[c]
        ax,ay,az=vb[0]-va[0],vb[1]-va[1],vb[2]-va[2]
        bx,by,bz=vc[0]-va[0],vc[1]-va[1],vc[2]-va[2]
        cx,cy,cz=ay*bz-az*by, az*bx-ax*bz, ax*by-ay*bx
        return cx*cx+cy*cy+cz*cz >= 1e-12
    tris = [t for t in tris if keep(t)]
    # UV
    uv = []
    uoff = p + 4 + V*12
    if uoff + 4 <= len(R):
        U = be32(R, uoff)
        if 0 < U <= V+1 and uoff+4+U*8 <= len(R):
            uv = [(bef(R,uoff+4+k*8), bef(R,uoff+8+k*8)) for k in range(U)]
    fn = os.path.join(OUT, f"{safe(name)}_{o.pathID}.obj")
    with open(fn, 'w') as f:
        f.write(f"# GooBall mesh {name} pathID={o.pathID} V={V} tris={len(tris)} uv={len(uv)}\n")
        for x,y,z in verts:
            f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")
        for x,y in uv:
            f.write(f"vt {x:.6f} {y:.6f}\n")
        for a,b,c in tris:
            f.write(f"f {a+1} {b+1} {c+1}\n")
    ok += 1

print(f"Mesh: {ok}  无顶点 {len(novert)}  faces方案 {face_used}  strips方案 {strip_used}  两者都有 {both}")
print("无顶点:", novert[:12])
