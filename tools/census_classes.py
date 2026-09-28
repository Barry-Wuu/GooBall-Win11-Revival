#!/usr/bin/env python3
"""普查 sharedassets.assets 所有 classID 出现次数（规划资产挖掘）。"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
u = Unity1x(os.path.join(D, 'sharedassets.assets'))
from collections import Counter
c = Counter(o.classID for o in u.objects)
# Unity 常见 classID 名
NAMES={
 1:'GameObject',4:'Transform',20:'Camera',21:'Material',23:'MeshRenderer',
 28:'Texture2D',33:'MeshFilter',43:'Mesh',48:'Shader',58:'Cubemap',
 65:'Light',74:'Animation',83:'AudioClip',95:'Animator',102:'SkinnedMeshRenderer',
 128:'Font',134:'MonoBehaviour',137:'Texture3D',150:'GameManager'}
for cid,cnt in sorted(c.items(), key=lambda x:-x[1]):
    print(f"  classID={cid:<5} {NAMES.get(cid,'?'):<18} x{cnt}")
print(f"\n总对象数: {len(u.objects)}")
# 单独确认 Mesh 规模
meshes=[o for o in u.objects if o.classID==43]
print(f"Mesh(43) 数量: {len(meshes)}  size总和={sum(o.size for o in meshes):,}B")
