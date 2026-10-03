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
LEVELNUM = LEVEL[5:] if LEVEL.startswith("level") else LEVEL

def quat_to_mat4(q, t, s):
    w, x, y, z = q
    return [s[0]*(1-2*y*y-2*z*z), s[0]*(2*x*y-2*w*z),   s[0]*(2*x*z+2*w*y),   t[0],
            s[1]*(2*x*y+2*w*z),   s[1]*(1-2*x*x-2*z*z), s[1]*(2*y*z-2*w*x),   t[1],
            s[2]*(2*x*z-2*w*y),   s[2]*(2*y*z+2*w*x),   s[2]*(1-2*x*x-2*y*y), t[2],
            0, 0, 0, 1]

def mat_mul4(a, b):
    """行主序 4x4 矩阵乘"""
    out = [0.0] * 16
    for i in range(4):
        for j in range(4):
            s = 0.0
            for k in range(4):
                s += a[i * 4 + k] * b[k * 4 + j]
            out[i * 4 + j] = s
    return out


def local_mat(t):
    """单个 Transform 的局部 TRS（row-major）"""
    pos = t.get("pos") or {}; rot = t.get("rot") or {}; scl = t.get("scale") or {}
    q = (rot.get("w", 1), rot.get("x", 0), rot.get("y", 0), rot.get("z", 0))
    tr = (pos.get("x", 0), pos.get("y", 0), pos.get("z", 0))
    sc = (scl.get("x", 1), scl.get("y", 1), scl.get("z", 1))
    return quat_to_mat4(q, tr, sc)


IDENT4 = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

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
    tr_by_pid = {}
    for t in trs.values():
        tr_by_go[t["go_pid"]] = t
        tr_by_pid[t["pid"]] = t

    def world_mat(go_pid):
        """沿 father_tp 链从根到叶累乘，得到真正的世界矩阵。

        Unity Transform 的 pos/rot/scale 是相对父节点的局部值；直接用会把
        层级打散（level3 里 174/177 个节点有父，最深 5 层）——必须累乘父链。
        """
        t = tr_by_go.get(go_pid)
        if not t:
            return None
        chain = []
        cur, seen, guard = t, set(), 0
        while cur is not None and guard < 64:
            chain.append(local_mat(cur))
            seen.add(cur.get("pid"))
            fp = cur.get("father_tp")
            if not fp or fp in seen:
                break
            cur = tr_by_pid.get(fp)
            guard += 1
        m = list(IDENT4)
        for lm in reversed(chain):
            m = mat_mul4(m, lm)
        return m

    def pos_of(go_pid):
        m = world_mat(go_pid)
        if m is None:
            return None
        return [round(m[3], 3), round(m[7], 3), round(m[11], 3)]

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
                      "matrix": world_mat(gpid),
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
    # 出生点：Level Pivot 是关卡原点（球在这里出生）；Respawn 是死亡重生点，兜底。
    spawn = None
    for gpid, go in gos.items():
        nm = (go.get("name") or "").strip().lower()
        if nm in ("level pivot", "levelpivot"):
            p = pos_of(int(gpid))
            if p:
                spawn = [p[0], p[1] + 5, p[2]]
                break
    if spawn is None:
        for gpid, go in gos.items():
            nm = (go.get("name") or "").strip().lower()
            if "respawn" in nm or nm in ("start", "spawn", "ballstart"):
                p = pos_of(int(gpid))
                if p:
                    spawn = [p[0], p[1] + 2, p[2]]
                    break
    if not spawn:
        ys = [p[1] for p in ([pos_of(int(g)) for g in gos] if False else [])]
        spawn = [0, 10, 0]

    out = {"level": LEVEL, "objects": items, "stars": stars, "goals": goals,
           "spawn": spawn, "ballRadius": 0.3}
    with open(os.path.join(GAME, "data", f"level{LEVELNUM}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)

    # 维护选关清单：把本关标记为已生成
    mpath = os.path.join(GAME, "data", "levels.json")
    try:
        meta = json.load(open(mpath, encoding="utf-8"))
    except Exception:
        meta = {}
    gen = set(meta.get("generated") or [])
    try:
        gen.add(int(LEVELNUM))
    except ValueError:
        pass
    meta["generated"] = sorted(gen)
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)

    print(f"渲染条目={len(items)} 网格复制={len(mesh_map)} 纹理复制={len(tex_map)} "
          f"网格未命中={miss_mesh} 纹理未命中={miss_tex}")
    print(f"星星={len(stars)} 目标={len(goals)} 出生点={spawn}")
    print(f"已写出 game/data/level{LEVELNUM}.json")

if __name__ == "__main__":
    main()
