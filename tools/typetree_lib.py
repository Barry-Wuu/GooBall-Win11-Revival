# -*- coding: utf-8 -*-
"""Unity 1.x (SerializedFile v5) TypeTree 终版解析库 v5  [DFS 扁平树坐实版]
布局坐实（sharedassets 实测，推翻旧「独立层级区」假设）：
  meta[0:4]   int32 LE = 1   (enableTypeTree)
  meta[4:9]   5 字节未知头
  meta[9:]    扁平描述符列表(DFS 顺序平铺)：每条 = type\\0name\\0 + 6×int32 大端
              6 int = (byteSize, index, isArray, version, metaFlag, numChildren)
              ★ 树结构由「顺序 + numChildren」隐式编码（深度优先平铺）：
                节点 i 的 numChildren[i] 个子节点 = 列表中紧随其后的 numChildren[i] 个节点。
              无需独立子索引区——描述符列表 [9, 194129) 即整棵树，之后仅 3 字节尾部 + head_field。
  meta[table_off-4] int32 LE = head_field (146)
  meta[table_off:]   ObjectInfo 对象表
重建：用栈做 DFS 还原 parent/child；以「栈恰好清空」反搜真实节点数 N（最大合法 N）。
"""
import struct

def read_str(meta, pos):
    end = meta.index(b"\x00", pos)
    return meta[pos:end], end + 1

def parse_descriptors_greedy(meta, start):
    pos = start; n = len(meta); nodes = []
    while pos + 24 <= n:
        t, p1 = read_str(meta, pos)
        if p1 >= n: break
        nm, p2 = read_str(meta, p1)
        if p2 + 24 > n: break
        bsz, idx, isArr, ver, mf, nc = struct.unpack_from(">6I", meta, p2)
        nodes.append({"type": t.decode("ascii", "replace"),
                      "name": nm.decode("ascii", "replace"),
                      "type_off": start, "name_off": p1,
                      "byteSize": bsz, "index": idx, "isArray": isArr,
                      "version": ver, "metaFlag": mf, "numChildren": nc,
                      "end": p2 + 24})
        pos = p2 + 24
    return nodes

def dfs_rebuild(nodes):
    """用栈把 DFS 扁平节点列表还原成树，返回 (parents, roots, ok)。
    ok=True 当且仅当处理完所有节点后栈恰好清空（完整闭合的森林）。"""
    parents = {}; roots = []; stack = []   # stack: [(node_idx, remaining_children)]
    for i, nd in enumerate(nodes):
        if stack:
            p, rem = stack[-1]
            parents[i] = p
            rem -= 1
            if rem <= 0:
                stack.pop()
            else:
                stack[-1] = (p, rem)
        else:
            roots.append(i)
        stack.append((i, nd["numChildren"]))
        # 若当前节点无剩余子节点，立即弹出（它不占用栈位等待子节点）
        while stack and stack[-1][1] <= 0:
            stack.pop()
    ok = (len(stack) == 0)
    return parents, roots, ok

def build_tree(meta, anchor, table_off):
    nodes = parse_descriptors_greedy(meta, anchor)
    # 反搜最大合法 N：处理 nodes[:N] 后栈恰好清空
    best_N = None
    for N in range(len(nodes), 0, -1):
        _, _, ok = dfs_rebuild(nodes[:N])
        if ok:
            best_N = N
            break
    if best_N is None:
        raise RuntimeError("DFS 未能重建闭合树")
    nodes = nodes[:best_N]
    parents, roots, _ = dfs_rebuild(nodes)
    for i, nd in enumerate(nodes):
        nd["parent"] = parents.get(i)
        nd["is_root"] = (i not in parents)
    return nodes, parents, roots

def root_children(nodes, roots):
    ch = {r: [] for r in roots}
    for i, nd in enumerate(nodes):
        p = nd["parent"]
        if p is not None:
            ch.setdefault(p, []).append(i)
    # 按 DFS 出现序排序
    for r in ch:
        ch[r].sort()
    return ch

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, ".")
    from unity1x import Unity1x
    D = r"D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data"
    u = Unity1x(os.path.join(D, "sharedassets.assets"))
    meta = u.meta
    nodes, parents, roots = build_tree(meta, 9, u.table_off)
    print(f"节点数 N={len(nodes)}  根节点={len(roots)}")
    print(f"  其中 name=='Base' 根={sum(1 for r in roots if nodes[r]['name']=='Base')}")
    print(f"  叶子节点={sum(1 for nd in nodes if nd['numChildren']==0)}")
    print("\n前 60 个根: #idx  type / name")
    for r in roots[:60]:
        print(f"  #{r:<5} {nodes[r]['type']} / {nodes[r]['name']}")
    # typeID -> 根 映射验证
    STD = {1:"GameObject",4:"Transform",20:"Camera",21:"Material",23:"Renderer",25:"Texture2D",
           43:"Mesh",48:"Shader",58:"AudioClip",64:"MeshCollider",95:"AnimationClip",102:"TextMesh",
           108:"Light",111:"Animation",114:"MonoBehaviour",115:"MonoScript",137:"SkinnedMeshRenderer"}
    tid2cls = {}
    for o in u.objects:
        tid2cls.setdefault(o.typeID, set()).add(o.classID)
    for label, fn in [("typeID-1 -> roots[idx]", lambda tid: tid-1)]:
        mism = 0; samp = []
        for tid, clss in sorted(tid2cls.items()):
            ri = fn(tid)
            if 0 <= ri < len(roots):
                tname = nodes[roots[ri]]["type"]
                if not any(STD.get(c) == tname for c in clss):
                    mism += 1
                    if len(samp) < 30: samp.append((tid, sorted(clss), tname))
        print(f"\n[{label}]  不匹配={mism}/{len(tid2cls)}")
        for s in samp: print("   ", s)
