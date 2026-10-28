#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""扫描全关卡：每颗钻石（StarPickup）下方是否有真实关卡几何支撑。

用途
  GooBall 的钻石偶有「看得见、吃不到」的情况。本工具从二进制直接判断：
  对每颗钻石取世界坐标，检查该 XZ 位置是否落在某个 MeshFilter / MeshCollider
  网格的世界包围盒内（排除钻石自身子树），从而区分「设计上的悬空物」与「正常摆件」。

结论（2026-10-25 实测）
  61 关 262 颗钻石里，**只有 2 颗没有任何几何支撑**：
    level20（Montezuma #1 Quagmire）   pos=(19.12, 0.88, 5.99)
    level55（Aztec Spacerace #3 Faster, Faster）pos=(-79.11, -8.29, -53.01)
  详见 docs/012-悬空钻石排查.md。

用法
  python level_diamond_support.py                 # 全部 61 关
  python level_diamond_support.py level20         # 单关明细
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unity1x import Unity1x
from mb_fields import parse_all_trees, deserialize_tree
import scene_graph_util as SU
from level_diamonds import load_level_table

D = r"D:\GooBall\win\Data"
HERE = os.path.dirname(os.path.abspath(__file__))
MB_BIND = os.path.join(HERE, "mb_bind_all.json")

# 物理常量（sharedassets pid=1906 BallController 实测）
MAX_SPEED = 16.0        # 速度钳制（所以任何抛体初速上限都是 16）
GRAVITY_AIR = 15.0      # 空中重力，决定最大弹道射程


def be32(b, i):
    return int.from_bytes(b[i:i + 4], "big")


def bef(b, i):
    import struct
    return struct.unpack(">f", b[i:i + 4])[0]


def mesh_aabb(u, o):
    """Mesh(classID 43) 的顶点包围盒：跳过 LOD 索引段后读 [u32 V][V×Vector3f]"""
    d = u.obj_data(o)
    n = be32(d, 0)
    if not (0 < n < 200):
        return None
    R = d[4 + n:]
    L = be32(R, 0)
    if not (1 <= L <= 8):
        return None
    p = 4
    for _ in range(L):
        if p + 4 > len(R):
            return None
        cnt = be32(R, p); p += 4
        if not (0 <= cnt <= 64):
            return None
        for _ in range(cnt):
            if p + 4 > len(R):
                return None
            nf = be32(R, p); p += 4
            if not (0 <= nf <= 200000) or p + nf * 6 > len(R):
                return None
            p += nf * 6
            if p + 4 > len(R):
                return None
            ns = be32(R, p); p += 4
            if not (0 <= ns <= 200000) or p + ns * 2 > len(R):
                return None
            p += ns * 2
    if p + 4 > len(R):
        return None
    V = be32(R, p)
    if not (3 <= V <= 60000) or p + 4 + V * 12 > len(R):
        return None
    xs, ys, zs = [], [], []
    for k in range(V):
        xs.append(bef(R, p + 4 + k * 12))
        ys.append(bef(R, p + 8 + k * 12))
        zs.append(bef(R, p + 12 + k * 12))
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def qmat(q):
    """四元数 → 3×3 旋转矩阵"""
    x, y, z, w = q
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    return [[1 - 2 * (yy + zz), 2 * (xy - wz), 2 * (xz + wy)],
            [2 * (xy + wz), 1 - 2 * (xx + zz), 2 * (yz - wx)],
            [2 * (xz - wy), 2 * (yz + wx), 1 - 2 * (xx + yy)]]


def load_meshes():
    sa = Unity1x(os.path.join(D, "sharedassets.assets"))
    out = {}
    for o in sa.objects:
        if o.classID == 43:
            a = mesh_aabb(sa, o)
            if a:
                out[o.pathID] = a
    return out


def world_boxes(u, go, tr, tr_by_go, meshes):
    """返回 [(go_pid, wmin, wmax)] —— 所有带 MeshFilter/MeshCollider 的节点"""
    trees = parse_all_trees(u.meta, 5, u.table_off - 7)
    by_cid = {}
    for t in trees:
        by_cid.setdefault(t["classID"], t)

    def refs(cid):
        res = {}
        if cid not in by_cid:
            return res
        for i in u.by_class(cid):
            o = u.objects[i]
            try:
                val, _ = deserialize_tree(by_cid[cid], u.obj_data(o))
            except Exception:
                continue
            _, gop = SU.pptr(val.get("m_GameObject"))
            _, mp = SU.pptr(val.get("m_Mesh"))
            res.setdefault(gop, set()).add(mp)
        return res

    mf, mc = refs(33), refs(64)
    boxes = []
    for gop in set(mf) | set(mc):
        pids = set(mf.get(gop, ())) | set(mc.get(gop, ()))
        p, q, _ = SU.global_of(tr, tr_by_go, gop)
        if p is None:
            continue
        R = qmat(q)
        s = 1.0
        cur = tr_by_go.get(gop)
        seen = set()
        while cur in tr and cur not in seen:
            seen.add(cur)
            ls = tr[cur]["s"]
            s *= (abs(ls[0]) + abs(ls[1]) + abs(ls[2])) / 3.0 or 1.0
            cur = tr[cur]["father"]
        for mp in pids:
            if mp not in meshes:
                continue
            mn, mx = meshes[mp]
            pts = []
            for cx in (mn[0], mx[0]):
                for cy in (mn[1], mx[1]):
                    for cz in (mn[2], mx[2]):
                        v = (cx * s, cy * s, cz * s)
                        pts.append(tuple(p[i] + sum(R[i][j] * v[j] for j in range(3))
                                         for i in range(3)))
            boxes.append((gop,
                          tuple(min(x[i] for x in pts) for i in range(3)),
                          tuple(max(x[i] for x in pts) for i in range(3))))
    return boxes


def subtree(tr, tr_by_go, gop):
    """钻石自身子树（自身网格不能算作「地面」）"""
    out = {gop}
    stack = [gop]
    while stack:
        g = stack.pop()
        tp = tr_by_go.get(g)
        for t in tr.values():
            if t["father"] == tp and t["go"] is not None and t["go"] not in out:
                out.add(t["go"])
                stack.append(t["go"])
    return out


def scan(fn, meshes, mb_rows):
    u, go, tr, tr_by_go = SU.load(D, fn)
    boxes = world_boxes(u, go, tr, tr_by_go, meshes)
    res = []
    for r in mb_rows:
        if r["file"] != fn or r["script_class"] != "StarPickup":
            continue
        gop = r["go_pid"]
        p, _, _ = SU.global_of(tr, tr_by_go, gop)
        if p is None:
            continue
        skip = subtree(tr, tr_by_go, gop)
        best = None
        for bgop, mn, mx in boxes:
            if bgop in skip:
                continue
            if mn[0] - 0.8 <= p[0] <= mx[0] + 0.8 and mn[2] - 0.8 <= p[2] <= mx[2] + 0.8:
                if best is None or mx[1] > best:
                    best = mx[1]
        res.append({"pos": p, "support_y": best})
    return res


def main():
    meshes = load_meshes()
    mb_rows = json.load(open(MB_BIND, encoding="utf-8"))
    if len(sys.argv) > 1:
        for fn in sys.argv[1:]:
            print("=== %s ===" % fn)
            for d in scan(fn, meshes, mb_rows):
                p, s = d["pos"], d["support_y"]
                print("   pos=(%8.2f,%7.2f,%8.2f)  %s" %
                      (p[0], p[1], p[2],
                       "无几何支撑" if s is None else "支撑面 Y=%.2f (Δ%+.2f)" % (s, p[1] - s)))
        return 0

    table = load_level_table()
    bad = 0
    for ch, name, idx in table:
        fn = "level%d" % (idx + 3)
        try:
            res = scan(fn, meshes, mb_rows)
        except Exception as e:
            print("  %-8s ERR %r" % (fn, e))
            continue
        hits = [d for d in res if d["support_y"] is None]
        if hits:
            bad += len(hits)
            print("%-8s %-16s %-18s 钻石 %d，悬空 %d" %
                  (fn, ch[:16], name[:18], len(res), len(hits)))
            for d in hits:
                p = d["pos"]
                print("        pos=(%.2f, %.2f, %.2f)" % p)
    print("\n悬空钻石合计: %d" % bad)
    print("参考：最大弹道射程 = maxSpeed²/g = %.1f²/%.1f = %.1f 单位"
          % (MAX_SPEED, GRAVITY_AIR, MAX_SPEED ** 2 / GRAVITY_AIR))
    return 0


if __name__ == "__main__":
    sys.exit(main())
