# -*- coding: utf-8 -*-
"""GooBall 场景重建 —— 组件挂接的场景树 + MonoBehaviour 定位
=============================================================
利用 metadata 内置类型树（classID>0）精确反序列化 GameObject(1) 与 Transform(4)，
再沿 Transform.m_Father 重建父子层级、算出每个 GameObject 的场景路径；
把 1447 个 MonoBehaviour 经 go_pid 锚定到场景节点，输出「脚本在游戏场景中的物理位置」。

组件清单直接取自 GameObject.m_Component（元素含 first=classID, second=pid），
无需逐组件反序列化。可选富化：Renderer/MeshFilter/Light/Animation/MeshCollider
在「本文件有对应类型树」时反序列化，抽取 mesh/material/clip/light 引用。
"""
import struct, os, sys, json
from collections import defaultdict
sys.path.insert(0, ".")
from unity1x import Unity1x
from mb_fields import parse_all_trees, deserialize_tree

D = r"D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data"
OUT = os.path.join(os.path.dirname(__file__), "..", "repo_git", "assets", "scene")
os.makedirs(OUT, exist_ok=True)
FILES = [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]

MB_JSON = os.path.join(os.path.dirname(__file__), "mb_fields.json")

# 需要富化反序列化的组件类（仅当本文件有对应树时）
ENRICH = {23: "renderer", 33: "meshfilter", 64: "meshcollider",
          108: "light", 111: "animation"}

def decode_name(v):
    """把类型树反序列化出的 m_Name（char 数组/字符串）转成可读串"""
    if v is None:
        return None
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        if "Array" in v and isinstance(v["Array"], list):
            arr = v["Array"]
            if arr and isinstance(arr[0], int) and all(0 <= x < 256 for x in arr):
                try:
                    s = bytes(arr).decode("ascii")
                    return s if s.isprintable() else None
                except Exception:
                    return None
        if "string" in v:
            return decode_name(v["string"])
    return None

def pptr_pid(p):
    if isinstance(p, dict):
        return (p.get("m_FileID", 0), p.get("m_PathID", 0))
    return (0, 0)

def build_file(fn, mb_by_file):
    path = os.path.join(D, fn)
    if not os.path.exists(path):
        return None
    try:
        u = Unity1x(path)
    except Exception as e:
        return {"file": fn, "error": str(e)}
    meta = u.meta
    try:
        trees = parse_all_trees(meta, 5, u.table_off - 7)
    except Exception:
        trees = []
    by_cid = {}
    for t in trees:
        by_cid.setdefault(t["classID"], t)

    # pathID -> 对象索引（用于跨引用解析）
    pid2idx = {o.pathID: i for i, o in enumerate(u.objects)}

    # 1) GameObject
    gameObjects = {}
    for i in u.by_class(1):
        o = u.objects[i]
        try:
            val, cons = deserialize_tree(by_cid[1], u.obj_data(o))
        except Exception:
            gameObjects[o.pathID] = {"pid": o.pathID, "name": None, "components": [],
                                     "layer": None, "active": None}
            continue
        comps = []
        for c in (val.get("m_Component") or []):
            cls = c.get("first")
            fid, pid = pptr_pid(c.get("second"))
            comps.append({"classID": cls, "pid": pid, "fileID": fid})
        gameObjects[o.pathID] = {
            "pid": o.pathID,
            "name": decode_name(val.get("m_Name")),
            "components": comps,
            "layer": val.get("m_Layer"),
            "active": val.get("m_IsActive"),
            "tag": val.get("m_Tag"),
        }

    # 2) Transform
    transforms = {}
    transform_by_go = {}
    for i in u.by_class(4):
        o = u.objects[i]
        try:
            val, cons = deserialize_tree(by_cid[4], u.obj_data(o))
        except Exception:
            continue
        fid, go_pid = pptr_pid(val.get("m_GameObject"))
        f_fid, f_tp = pptr_pid(val.get("m_Father"))
        children = [pptr_pid(c)[1] for c in (val.get("m_Children") or [])]
        pos = val.get("m_LocalPosition")
        rot = val.get("m_LocalRotation")
        scl = val.get("m_LocalScale")
        transforms[o.pathID] = {
            "pid": o.pathID, "go_pid": go_pid, "father_tp": f_tp,
            "children_tp": children, "pos": pos, "rot": rot, "scale": scl,
        }
        if go_pid is not None:
            transform_by_go[go_pid] = o.pathID

    # 3) 富化：组件关键引用
    enrich_data = defaultdict(dict)  # go_pid -> {key: value}
    for cls, label in ENRICH.items():
        if cls not in by_cid:
            continue
        for i in u.by_class(cls):
            o = u.objects[i]
            try:
                val, cons = deserialize_tree(by_cid[cls], u.obj_data(o))
            except Exception:
                continue
            fid, go_pid = pptr_pid(val.get("m_GameObject"))
            if go_pid is None:
                continue
            rec = {}
            if label == "meshfilter":
                fid2, mesh = pptr_pid(val.get("m_Mesh"))
                rec["mesh_pid"] = mesh
            elif label == "renderer":
                mats = [pptr_pid(m)[1] for m in (val.get("m_Materials") or [])]
                rec["material_pids"] = mats
            elif label == "meshcollider":
                fid2, mesh = pptr_pid(val.get("m_Mesh"))
                rec["collider_mesh_pid"] = mesh
            elif label == "light":
                rec["light_type"] = val.get("m_LightType")
                col = val.get("m_Color")
                rec["color"] = col
                rec["intensity"] = val.get("m_Intensity")
            elif label == "animation":
                anims = [pptr_pid(a)[1] for a in (val.get("m_Animations") or [])]
                rec["clip_pids"] = anims
            if rec:
                enrich_data[go_pid][label] = rec

    # 4) 计算场景路径（沿 father_tp 上溯）
    def scene_path(go_pid):
        tp = transform_by_go.get(go_pid)
        if tp is None:
            return None
        names = []
        seen = set()
        cur = tp
        while cur is not None and cur not in seen:
            seen.add(cur)
            t = transforms.get(cur)
            if t is None:
                break
            g = gameObjects.get(t["go_pid"])
            names.append((g["name"] if g and g["name"] else f"GO#{t['go_pid']}"))
            nxt = t["father_tp"]
            cur = nxt if (nxt and nxt in transforms) else None
        return "/".join(reversed(names))

    for gpid, g in gameObjects.items():
        g["path"] = scene_path(gpid)
        if gpid in enrich_data:
            g["refs"] = enrich_data[gpid]

    # 5) 关联 MB
    mb_list = []
    for rec in mb_by_file.get(fn, []):
        gpid = rec.get("go_pid")
        g = gameObjects.get(gpid) if gpid is not None else None
        entry = {
            "file": fn,
            "mb_pid": rec.get("mb_pid"),
            "script": rec.get("script_class"),
            "go_pid": gpid,
            "go_name": g["name"] if g else None,
            "scene_path": (g["path"] if g else None),
            "size": rec.get("size"),
            "enabled": rec.get("enabled"),
        }
        # 关键字段（取前若干标量，便于审阅）
        flds = rec.get("fields") or {}
        keys = [k for k, v in flds.items()
                if isinstance(v, (int, float, str)) and not isinstance(v, bool)]
        entry["key_fields"] = {k: flds[k] for k in keys[:12]}
        mb_list.append(entry)

    # 组件类分布
    comp_dist = defaultdict(int)
    for g in gameObjects.values():
        for c in g["components"]:
            if c["classID"] is not None:
                comp_dist[c["classID"]] += 1

    return {
        "file": fn,
        "gameObject_count": len(gameObjects),
        "transform_count": len(transforms),
        "mb_count": len(mb_list),
        "component_distribution": dict(comp_dist),
        "gameObjects": gameObjects,
        "transforms": transforms,
        "mb": mb_list,
    }

def main():
    # 载入 MB 记录，按 file 索引
    mb_all = json.load(open(MB_JSON, encoding="utf-8"))
    mb_by_file = defaultdict(list)
    for r in mb_all:
        mb_by_file[r["file"]].append(r)

    results = {}
    summary = {}
    for fn in FILES:
        r = build_file(fn, mb_by_file)
        if r is None:
            continue
        results[fn] = r
        summary[fn] = {
            "GO": r["gameObject_count"], "TR": r["transform_count"],
            "MB": r["mb_count"],
            "components": r["component_distribution"],
        }
        print(f"  {fn:<18} GO={r['gameObject_count']:<5} TR={r['transform_count']:<5} "
              f"MB={r['mb_count']:<5}", flush=True)

    # 输出：完整场景图
    with open(os.path.join(OUT, "scene_graph.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    # 输出：聚焦的 MB 定位表
    mb_locations = []
    for fn, r in results.items():
        for m in r["mb"]:
            mb_locations.append(m)
    mb_locations.sort(key=lambda x: (x["file"], x["go_pid"] or 0))
    with open(os.path.join(OUT, "mb_locations.json"), "w", encoding="utf-8") as f:
        json.dump(mb_locations, f, ensure_ascii=False, indent=1)

    # 输出：摘要
    with open(os.path.join(OUT, "scene_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)

    print(f"\n总 MB 定位条目: {len(mb_locations)}")
    # 统计有场景路径的比例
    with_path = sum(1 for m in mb_locations if m["scene_path"])
    print(f"  有场景路径: {with_path}/{len(mb_locations)}")
    print("已写出 assets/scene/{scene_graph.json, mb_locations.json, scene_summary.json}")

if __name__ == "__main__":
    main()
