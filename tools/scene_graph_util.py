#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""场景读取小工具：反序列化 GameObject / Transform，合成世界变换。

给 level_diamond_support.py 等分析脚本复用。原 scene_graph.py 硬编码了 Mac 版
提取目录，这里改成接受任意 Data 目录（Windows 原版同样适用）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unity1x import Unity1x
from mb_fields import parse_all_trees, deserialize_tree


def pptr(p):
    if isinstance(p, dict):
        return (p.get("m_FileID", 0), p.get("m_PathID", 0))
    return (0, None)


def vec(v):
    if isinstance(v, dict):
        return (float(v.get("x", 0) or 0), float(v.get("y", 0) or 0), float(v.get("z", 0) or 0))
    if isinstance(v, (list, tuple)) and len(v) >= 3:
        return tuple(map(float, v[:3]))
    return (0.0, 0.0, 0.0)


def quat(v):
    if isinstance(v, dict):
        return (float(v.get("x", 0) or 0), float(v.get("y", 0) or 0),
                float(v.get("z", 0) or 0), float(v.get("w", 1) or 1))
    if isinstance(v, (list, tuple)) and len(v) >= 4:
        return tuple(map(float, v[:4]))
    return (0.0, 0.0, 0.0, 1.0)


def qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz)


def qrot(q, v):
    x, y, z, w = q
    vx, vy, vz = v
    tx = 2 * (y * vz - z * vy)
    ty = 2 * (z * vx - x * vz)
    tz = 2 * (x * vy - y * vx)
    return (vx + w * tx + (y * tz - z * ty),
            vy + w * ty + (z * tx - x * tz),
            vz + w * tz + (x * ty - y * tx))


def name_of(go, pid):
    """m_Name 可能是 char 数组或字符串，统一转可读串"""
    n = go.get(pid, {}).get("name")
    if isinstance(n, str):
        return n
    if isinstance(n, dict):
        arr = n.get("Array")
        if isinstance(arr, list) and arr and all(isinstance(x, int) and 0 <= x < 256 for x in arr):
            return bytes(arr).decode("ascii", "replace")
    return str(n)


def load(data_dir, fn):
    """返回 (u, gameObjects, transforms, transform_by_go)"""
    u = Unity1x(os.path.join(data_dir, fn))
    trees = parse_all_trees(u.meta, 5, u.table_off - 7)
    by_cid = {}
    for t in trees:
        by_cid.setdefault(t["classID"], t)

    go = {}
    if 1 in by_cid:
        for i in u.by_class(1):
            o = u.objects[i]
            try:
                val, _ = deserialize_tree(by_cid[1], u.obj_data(o))
            except Exception:
                go[o.pathID] = {"name": None, "comps": []}
                continue
            comps = []
            for c in (val.get("m_Component") or []):
                comps.append((c.get("first"), pptr(c.get("second"))[1]))
            go[o.pathID] = {"name": val.get("m_Name"), "comps": comps,
                            "active": val.get("m_IsActive")}

    tr = {}
    tr_by_go = {}
    if 4 in by_cid:
        for i in u.by_class(4):
            o = u.objects[i]
            try:
                val, _ = deserialize_tree(by_cid[4], u.obj_data(o))
            except Exception:
                continue
            _, gop = pptr(val.get("m_GameObject"))
            _, fat = pptr(val.get("m_Father"))
            tr[o.pathID] = {"go": gop, "father": fat,
                            "p": vec(val.get("m_LocalPosition")),
                            "q": quat(val.get("m_LocalRotation")),
                            "s": vec(val.get("m_LocalScale"))}
            if gop is not None:
                tr_by_go[gop] = o.pathID
    return u, go, tr, tr_by_go


def global_of(tr, tr_by_go, go_pid):
    """沿 father 链递归合成世界 (位置, 旋转, 链)；链首为根"""
    tp = tr_by_go.get(go_pid)
    if tp is None:
        return None, None, []
    chain = []
    cur = tp
    seen = set()
    while cur is not None and cur not in seen:
        seen.add(cur)
        t = tr.get(cur)
        if t is None:
            break
        chain.append(t)
        cur = t["father"] if t["father"] in tr else None
    pos = (0.0, 0.0, 0.0)
    rot = (0.0, 0.0, 0.0, 1.0)
    scl = (1.0, 1.0, 1.0)
    for t in reversed(chain):
        lp, lq, ls = t["p"], t["q"], t["s"]
        pos = tuple(pos[i] + qrot(rot, (lp[0] * scl[0], lp[1] * scl[1], lp[2] * scl[2]))[i]
                    for i in range(3))
        rot = qmul(rot, lq)
        scl = (scl[0] * ls[0], scl[1] * ls[1], scl[2] * ls[2])
    return pos, rot, chain
