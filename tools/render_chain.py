# -*- coding: utf-8 -*-
"""GooBall 渲染链解析 —— GO → Mesh/Material/Shader/Texture 实体名
================================================================
scene_graph.json 里每个 GO 的 refs（mesh_pid/material_pids）目前只有 pid。
本脚本把它们跨文件解析成实体：
  mesh_pid     → sharedassets Mesh(43) 名（m_Name 为首部长度前缀串，直接读）
  material_pid → assets/materials/materials.json（含 shaderName/纹理/属性）
关卡本地材质（level47/48/55 各 1 个）用 sharedassets 的 Material 树布局兜底解析。
输出 assets/scene/render_chain.json。
"""
import struct, os, sys, json
from collections import Counter, defaultdict
sys.path.insert(0, ".")
from unity1x import Unity1x

D = r"D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data"
HERE = os.path.dirname(__file__)
REPO = os.path.join(HERE, "..", "repo_git")
SG = os.path.join(REPO, "assets", "scene", "scene_graph.json")
MAT = os.path.join(REPO, "assets", "materials", "materials.json")
OUT = os.path.join(REPO, "assets", "scene", "render_chain.json")

def read_len_str(d, p=0):
    if p + 4 > len(d):
        return None, p
    ln = struct.unpack_from(">i", d, p)[0]
    if ln < 0 or ln > 4096 or p + 4 + ln > len(d):
        return None, p
    return d[p+4:p+4+ln].decode("utf-8", "replace"), p + 4 + ln

def main():
    scene = json.load(open(SG, encoding="utf-8"))
    mats = {m["pathID"]: m for m in json.load(open(MAT, encoding="utf-8"))}

    # sharedassets Mesh 名（m_Name 在数据首部）
    u = Unity1x(os.path.join(D, "sharedassets.assets"))
    mesh_names = {}
    for i in u.by_class(43):
        o = u.objects[i]
        nm, _ = read_len_str(u.obj_data(o))
        if nm:
            mesh_names[o.pathID] = nm

    # 关卡本地材质兜底解析（Material 布局与 sharedassets 相同：name + shader PPtr + ...）
    local_mat = {}
    for fn in ("level47", "level48", "level55"):
        uu = Unity1x(os.path.join(D, fn))
        for i in uu.by_class(21):
            o = uu.objects[i]
            nm, p = read_len_str(uu.obj_data(o))
            local_mat[(fn, o.pathID)] = nm or f"mat#{o.pathID}"

    results = {}
    stats = Counter()
    usage_mesh = Counter(); usage_mat = Counter()

    for fn, r in scene.items():
        if "gameObjects" not in r:
            continue
        chain = []
        for gpid, go in r["gameObjects"].items():
            refs = go.get("refs")
            if not refs:
                continue
            entry = {"go": go.get("name"), "path": go.get("path")}
            if "meshfilter" in refs and refs["meshfilter"].get("mesh_pid"):
                mp = refs["meshfilter"]["mesh_pid"]
                entry["mesh"] = mesh_names.get(mp) or f"mesh#{mp}"
                stats["mesh_resolved" if mp in mesh_names else "mesh_miss"] += 1
                if mp in mesh_names: usage_mesh[mesh_names[mp]] += 1
            if "meshcollider" in refs and refs["meshcollider"].get("collider_mesh_pid"):
                mp = refs["meshcollider"]["collider_mesh_pid"]
                entry["collider_mesh"] = mesh_names.get(mp) or f"mesh#{mp}"
            if "renderer" in refs:
                mids = refs["renderer"].get("material_pids") or []
                ml = []
                for mid in mids:
                    m = mats.get(mid)
                    if m:
                        ml.append({"material": m["name"].strip(),
                                   "shader": m.get("shaderName"),
                                   "textures": [t.get("texName") for t in (m.get("textures") or [])]})
                        usage_mat[m["name"].strip()] += 1
                    else:
                        lm = local_mat.get((fn, mid))
                        ml.append({"material": lm or f"mat#{mid}", "shader": None, "textures": []})
                    stats["mat_resolved" if (mid in mats or (fn, mid) in local_mat) else "mat_miss"] += 1
                if ml:
                    entry["materials"] = ml
            if "light" in refs:
                entry["light"] = refs["light"]
            if "animation" in refs:
                entry["clip_count"] = len(refs["animation"].get("clip_pids") or [])
            if len(entry) > 2:
                chain.append(entry)
        if chain:
            results[fn] = chain

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    print("=== 渲染链统计 ===")
    print(f"  覆盖文件数={len(results)}  条目数={sum(len(v) for v in results.values())}")
    print(f"  mesh 解析={stats['mesh_resolved']} 未命中={stats['mesh_miss']}")
    print(f"  material 解析={stats['mat_resolved']} 未命中={stats['mat_miss']}")
    print("  最常用网格 top8:", usage_mesh.most_common(8))
    print("  最常用材质 top8:", usage_mat.most_common(8))
    # 样例：Ball
    for fn, ch in results.items():
        for e in ch:
            if e["go"] == "Ball":
                print(f"  样例 Ball@{fn}:", json.dumps(e, ensure_ascii=False)[:300])
                break
    print("已写出", OUT)

if __name__ == "__main__":
    main()
