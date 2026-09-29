# -*- coding: utf-8 -*-
"""生成 GooBall Three.js 重建版的关卡数据
=========================================
输入 repo_git/assets/{scene/scene_graph.json, scene/render_chain.json, scene/mb_locations.json}
输出 game/data/level.json：渲染列表 + 星星 + 出生点 + 目标点
并复制所需 OBJ/PNG/音频 到 game/assets/。
"""
import os, sys, json, glob, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..", "repo_git")
GAME = os.path.join(HERE, "..", "game")
LEVEL = sys.argv[1] if len(sys.argv) > 1 else "level3"

def quat_to_mat4(q, t, s):
    w, x, y, z = q
    return [s[0]*(1-2*y*y-2*z*z), s[0]*(2*x*y-2*w*z),   s[0]*(2*x*z+2*w*y),   t[0],
            s[1]*(2*x*y+2*w*z),   s[1]*(1-2*x*x-2*z*z), s[1]*(2*y*z-2*w*x),   t[1],
            s[2]*(2*x*z-2*w*y),   s[2]*(2*y*z+2*w*x),   s[2]*(1-2*x*x-2*y*y), t[2],
            0, 0, 0, 1]

def find_obj(pid):
    if pid is None:
        return None
    hits = glob.glob(os.path.join(REPO, "assets", "meshes", f"*_{pid}.obj"))
    return hits[0] if hits else None

TEX_INDEX = None
def find_tex(name):
    """大小写不敏感 + 空格/横线归一化的纹理查找"""
    global TEX_INDEX
    if not name:
        return None
    if TEX_INDEX is None:
        TEX_INDEX = {}
        d = os.path.join(REPO, "assets", "textures")
        for f in os.listdir(d):
            if f.lower().endswith(".png"):
                key = f[:-4].lower().replace(" ", "_").replace("-", "_")
                TEX_INDEX.setdefault(key, f)
    key = name.lower().replace(" ", "_").replace("-", "_")
    f = TEX_INDEX.get(key)
    if f:
        return f
    # 前缀匹配（带 _pid 后缀的副本）
    for k, v in TEX_INDEX.items():
        if k.startswith(key + "_") or k == key:
            return v
    return None

def main():
    sg = json.load(open(os.path.join(REPO, "assets", "scene", "scene_graph.json"), encoding="utf-8"))
    loc = json.load(open(os.path.join(REPO, "assets", "scene", "mb_locations.json"), encoding="utf-8"))
    mats_by_pid = {m["pathID"]: m for m in json.load(
        open(os.path.join(REPO, "assets", "materials", "materials.json"), encoding="utf-8"))}
    r = sg[LEVEL]
    gos = r["gameObjects"]
    trs = r["transforms"]

    tr_by_go = {}
    for t in trs.values():
        tr_by_go[t["go_pid"]] = t

    def matrix_of(go_pid):
        t = tr_by_go.get(go_pid)
        if not t:
            return None
        pos = t.get("pos") or {}; rot = t.get("rot") or {}; scl = t.get("scale") or {}
        q = (rot.get("w", 1), rot.get("x", 0), rot.get("y", 0), rot.get("z", 0))
        tr = (pos.get("x", 0), pos.get("y", 0), pos.get("z", 0))
        sc = (scl.get("x", 1), scl.get("y", 1), scl.get("z", 1))
        return quat_to_mat4(q, tr, sc)

    def pos_of(go_pid):
        t = tr_by_go.get(go_pid)
        if not t:
            return None
        p = t.get("pos") or {}
        return [round(p.get("x", 0), 3), round(p.get("y", 0), 3), round(p.get("z", 0), 3)]

    for sub in ("data", "assets/meshes", "assets/textures", "assets/audio"):
        os.makedirs(os.path.join(GAME, sub), exist_ok=True)

    items, mesh_map, tex_map = [], {}, {}
    miss_mesh = miss_tex = 0
    for gpid_s, go in gos.items():
        gpid = int(gpid_s)
        refs = go.get("refs") or {}
        mf = refs.get("meshfilter")
        rd = refs.get("renderer")
        if not (mf and rd):
            continue
        objf = find_obj(mf.get("mesh_pid"))
        if not objf:
            miss_mesh += 1
            continue
        dst = os.path.basename(objf)
        if dst not in mesh_map:
            shutil.copy(objf, os.path.join(GAME, "assets", "meshes", dst))
            mesh_map[dst] = True
        e_mats = []
        texs = []
        for mpid in (rd.get("material_pids") or []):
            m = mats_by_pid.get(mpid)
            if not m:
                continue
            tlist = [t for t in [find_tex(t.get("texName") if isinstance(t, dict) else t)
                                 for t in (m.get("textures") or [])] if t]
            color = None
            for prop in (m.get("properties") or []):
                if prop.get("prop") == "_Color" and isinstance(prop.get("value"), list):
                    color = [round(c, 3) for c in prop["value"]]
                    break
            for tname in (m.get("textures") or []):
                tn = tname.get("texName") if isinstance(tname, dict) else tname
                tf = find_tex(tn)
                if tf:
                    if tf not in tex_map:
                        shutil.copy(os.path.join(REPO, "assets", "textures", tf),
                                    os.path.join(GAME, "assets", "textures", tf))
                        tex_map[tf] = True
                    if "assets/textures/" + tf not in texs:
                        texs.append("assets/textures/" + tf)
                elif tn:
                    miss_tex += 1
            e_mats.append({"color": color})
        # 材质信息附到条目（首个材质色作兜底）
        items.append({"name": go.get("name"), "path": go.get("path"),
                      "mesh": "assets/meshes/" + dst,
                      "matrix": matrix_of(gpid),
                      "textures": texs,
                      "color": (e_mats[0]["color"] if e_mats and e_mats[0]["color"] else None),
                      "collider_mesh": ("assets/meshes/" + os.path.basename(find_obj(
                          refs["meshcollider"]["collider_mesh_pid"]))
                          if refs.get("meshcollider") and find_obj(refs["meshcollider"].get("collider_mesh_pid")) else None)})

    # 星星 / 目标 / 出生点
    stars, goals = [], []
    for m in loc:
        if m["file"] != LEVEL:
            continue
        p = pos_of(m.get("go_pid")) if m.get("go_pid") is not None else None
        if p is None:
            continue
        if m["script"] == "StarPickup":
            stars.append(p)
        elif m["script"] == "GoalTrigger":
            goals.append(p)
    # 出生点：Level Pivot 位置 + 上方 5；否则场景中心
    spawn = None
    for gpid, go in gos.items():
        if (go.get("name") or "").lower() in ("level pivot", "levelpivot") :
            p = pos_of(int(gpid))
            if p:
                spawn = [p[0], p[1] + 5, p[2]]
            break
    if not spawn:
        ys = [p[1] for p in ([pos_of(int(g)) for g in gos] if False else [])]
        spawn = [0, 10, 0]

    out = {"level": LEVEL, "objects": items, "stars": stars, "goals": goals,
           "spawn": spawn, "ballRadius": 0.3}
    with open(os.path.join(GAME, "data", "level.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

    print(f"渲染条目={len(items)} 网格复制={len(mesh_map)} 纹理复制={len(tex_map)} "
          f"网格未命中={miss_mesh} 纹理未命中={miss_tex}")
    print(f"星星={len(stars)} 目标={len(goals)} 出生点={spawn}")
    print("已写出 game/data/level.json")

if __name__ == "__main__":
    main()
