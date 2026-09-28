import numpy as np, os, glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

base = r'D:\GooBall\extract\meshes'
picks = ['stonesShape3_120.obj','bigCHUNKShape_479.obj','bigjumpShape_649.obj',
         'polySurfaceShape6_1446.obj','cactusShape2_129.obj','Mesh_388.obj']
fig = plt.figure(figsize=(18, 12))
for idx, fn in enumerate(picks):
    p = os.path.join(base, fn)
    if not os.path.exists(p):
        continue
    V=[];F=[]
    for line in open(p):
        q=line.split()
        if q and q[0]=='v': V.append([float(x) for x in q[1:4]])
        elif q and q[0]=='f': F.append([int(x)-1 for x in q[1:4]])
    V=np.array(V);F=np.array(F)
    ax = fig.add_subplot(2,3,idx+1, projection='3d')
    if len(F):
        tris = V[F]
        pc = Poly3DCollection(tris, alpha=0.85, edgecolor='k', linewidths=0.15)
        ax.add_collection3d(pc)
    ax.scatter(V[:,0],V[:,1],V[:,2], s=1, c='r')
    c=(V.max(0)+V.min(0))/2; r=max((V.max(0)-V.min(0)).max()/2, 0.1)
    ax.set_xlim(c[0]-r,c[0]+r); ax.set_ylim(c[1]-r,c[1]+r); ax.set_zlim(c[2]-r,c[2]+r)
    ax.set_title(f'{fn}\nV={len(V)} F={len(F)}', fontsize=9)
    ax.set_box_aspect((1,1,1)); ax.axis('off')
plt.tight_layout()
out = r'D:\GooBall\proof\mesh_preview.png'
os.makedirs(os.path.dirname(out), exist_ok=True)
plt.savefig(out, dpi=90)
print('saved', out)
