#!/usr/bin/env python3
"""用 UnityPy 导出场景层级（GameObject 名 + Transform 位置/父子 + Renderer 绑定）。
覆盖：69 个 level 文件 + mainData + sharedassets.assets。
"""
import os, json, sys
import UnityPy

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\scenes'
os.makedirs(OUT, exist_ok=True)

FILES = [f'level{i}' for i in range(69)] + ['mainData', 'sharedassets.assets']

def dump_file(fn):
    path = os.path.join(D, fn)
    if not os.path.exists(path):
        return None
    try:
        env = UnityPy.load(path)
    except Exception as e:
        return {'file': fn, 'error': str(e)}
    gos, trs, rends, filt = {}, {}, [], []
    for o in env.objects:
        tn = o.type.name
        try:
            ob = o.read()
        except Exception:
            continue
        if tn == 'GameObject':
            nm = getattr(ob, 'm_Name', None)
            comps = []
            mc = getattr(ob, 'm_Component', None)
            if mc:
                for c in mc:
                    cp = getattr(c, 'component', c)
                    pid = getattr(cp, 'm_PathID', None) or getattr(cp, 'path_id', None)
                    comps.append(pid)
            gos[o.path_id] = {'name': nm, 'components': comps}
        elif tn == 'Transform':
            lp = getattr(ob,'m_LocalPosition',None); lr=getattr(ob,'m_LocalRotation',None); ls=getattr(ob,'m_LocalScale',None)
            fa = getattr(ob,'m_Father',None); ch = getattr(ob,'m_Children',None); go=getattr(ob,'m_GameObject',None)
            def v3(v): return [round(float(v.x),4),round(float(v.y),4),round(float(v.z),4)] if v else None
            def q4(v): return [round(float(v.x),4),round(float(v.y),4),round(float(v.z),4),round(float(v.w),4)] if v else None
            trs[o.path_id] = {
                'go': getattr(go,'m_PathID',None),
                'father': getattr(fa,'m_PathID',None),
                'children': [getattr(c,'m_PathID',None) for c in (ch or [])],
                'pos': v3(lp), 'rot': q4(lr), 'scale': v3(ls)}
        elif tn in ('MeshRenderer','SkinnedMeshRenderer'):
            mats = getattr(ob,'m_Materials',None) or []
            go = getattr(ob,'m_GameObject',None)
            rends.append({'type':tn,'pathID':o.path_id,'go':getattr(go,'m_PathID',None),
                          'materials':[getattr(m,'m_PathID',None) for m in mats]})
        elif tn == 'MeshFilter':
            go = getattr(ob,'m_GameObject',None); me = getattr(ob,'m_Mesh',None)
            filt.append({'pathID':o.path_id,'go':getattr(go,'m_PathID',None),
                         'mesh':getattr(me,'m_PathID',None)})
    # 解析 GO 名到 transform
    for tid, t in trs.items():
        g = gos.get(t['go'])
        t['name'] = g['name'] if g else None
    out = {'file': fn, 'gameObjects': gos, 'transforms': trs,
           'renderers': rends, 'filters': filt}
    return out

# 先跑关卡（快）
results = {}
for fn in [f'level{i}' for i in range(69)] + ['mainData']:
    r = dump_file(fn)
    if r:
        results[fn] = r
        ng = len(r.get('gameObjects',{}))
        print(f"  {fn:<18} GO={ng} TR={len(r.get('transforms',{}))} RD={len(r.get('renderers',[]))} MF={len(r.get('filters',[]))}", flush=True)
with open(os.path.join(OUT,'levels_scene.json'),'w',encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("levels_scene.json written", flush=True)

# 再跑 sharedassets（慢）
r = dump_file('sharedassets.assets')
if r:
    with open(os.path.join(OUT,'sharedassets_scene.json'),'w',encoding='utf-8') as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    print(f"sharedassets: GO={len(r.get('gameObjects',{}))} TR={len(r.get('transforms',{}))} RD={len(r.get('renderers',[]))}")
print("DONE")
