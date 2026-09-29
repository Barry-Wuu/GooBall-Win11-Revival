# -*- coding: utf-8 -*-
"""GooBall (Unity 1.x beta) MonoBehaviour 全量字段提取器 —— 终版
=====================================================================
metadata 格式（本轮逆向坐实）：
  [0:4]  int32 LE = 1 (enableTypeTree)
  [4]    1 字节 = 树总数 (脚本树+内置树)
  [5..]  连续树列表，每棵:
           int32 BE classID      (脚本树=负数且 == -MB实例pathID; 内置树=Unity类ID)
           type\\0 name\\0
           6×int32 BE (byteSize,index,isArray,version,metaFlag,numChildren)
           子节点按 DFS 紧随 (numChildren 隐式编码)
  末尾   7 字节 (00 00 00 + head_field int32 LE)
  对象表 (20B/条)

序列化数据：全大端，无对齐。MB base = m_GameObject(PPtr,8) + m_Enabled(bool,1)
           + m_Script(PPtr,8) = 17 字节，之后为脚本自定义字段。
"""
import struct, os, sys, json
from collections import defaultdict
sys.path.insert(0, ".")
from unity1x import Unity1x

D = r"D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data"
OUT = os.path.join(os.path.dirname(__file__), "mb_fields.json")
FILES = [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]

# ---------------- 树解析 ----------------
def read_str(meta, pos):
    e = meta.index(b"\x00", pos)
    return meta[pos:e], e + 1

def parse_all_trees(meta, start, end):
    """解析 [4B classID]+树 序列。返回树列表: {classID, nodes(扁平), root_i}"""
    trees = []
    p = start
    while p + 4 <= end:
        cid = struct.unpack_from(">i", meta, p)[0]
        p += 4
        nodes = []
        # 读根
        t, p = read_str(meta, p)
        nm, p = read_str(meta, p)
        vals = struct.unpack_from(">6I", meta, p); p += 24
        nodes.append({"type": t, "name": nm, "bs": vals[0], "idx": vals[1],
                      "isArr": vals[2], "ver": vals[3], "mf": vals[4], "nc": vals[5]})
        stack = [vals[5]] if vals[5] > 0 else []
        while stack:
            t, p = read_str(meta, p)
            nm, p = read_str(meta, p)
            vals = struct.unpack_from(">6I", meta, p); p += 24
            nodes.append({"type": t, "name": nm, "bs": vals[0], "idx": vals[1],
                          "isArr": vals[2], "ver": vals[3], "mf": vals[4], "nc": vals[5]})
            stack[-1] -= 1
            if stack[-1] <= 0:
                stack.pop()
            if vals[5] > 0:
                stack.append(vals[5])
            if p > end:
                break
        trees.append({"classID": cid, "nodes": nodes})
        if p > end:
            break
    return trees

def compute_spans(nodes):
    """每个节点的子树占用节点数"""
    n = len(nodes)
    spans = [0] * n
    # 逆序：叶 span=1；内部 = 1 + sum(children spans)；children 从 i+1 连续
    for i in range(n - 1, -1, -1):
        nc = nodes[i]["nc"]
        if nc == 0:
            spans[i] = 1
        else:
            s = 1
            j = i + 1
            for _ in range(nc):
                s += spans[j]
                j += spans[j]
            spans[i] = s
    return spans

# ---------------- 反序列化 ----------------
SCALARS = {
    b"float": (">f", 4), b"SInt32": (">i", 4), b"int": (">i", 4),
    b"UInt32": (">I", 4), b"unsigned int": (">I", 4),
    b"bool": (">B", 1), b"char": (">B", 1), b"UInt8": (">B", 1),
    b"UInt16": (">H", 2), b"SInt16": (">h", 2), b"double": (">d", 8),
}

class Desync(Exception):
    pass

def read_value(nodes, spans, i, data, off):
    """返回 (value, new_off)。value: 标量/list/dict"""
    nd = nodes[i]
    t = nd["type"]; nc = nd["nc"]
    if t in SCALARS and nc == 0:
        fmt, w = SCALARS[t]
        if off + w > len(data):
            raise Desync(f"EOF@{off} need {w}")
        return struct.unpack_from(fmt, data, off)[0], off + w
    if t == b"string" and nc == 0:
        if off + 4 > len(data):
            raise Desync("EOF str len")
        ln = struct.unpack_from(">i", data, off)[0]
        if ln < 0 or off + 4 + ln > len(data):
            raise Desync(f"bad str len {ln}")
        return data[off+4:off+4+ln].decode("utf-8", "replace"), off + 4 + ln
    if t in (b"TypelessData",) and nc == 0:
        if off + nd["bs"] > len(data):
            raise Desync("EOF typeless")
        return data[off:off+nd["bs"]].hex(), off + nd["bs"]
    # 容器/结构体：递归子节点
    if t in (b"Array",):
        # children: [size(int), data(elem)]
        ci = i + 1
        cnt, off2 = read_value(nodes, spans, ci, data, off)
        if not isinstance(cnt, int) or cnt < 0 or cnt > 100000:
            raise Desync(f"bad array count {cnt}")
        elem_i = ci + spans[ci]
        arr = []
        for _ in range(cnt):
            v, off2 = read_value(nodes, spans, elem_i, data, off2)
            arr.append(v)
        return arr, off2
    if t in (b"vector", b"map", b"set"):
        # 唯一子节点为 Array（或直接 size+elem 结构），整体委托
        ci = i + 1
        v, off2 = read_value(nodes, spans, ci, data, off)
        return v, off2
    # 普通结构体 / PPtr / pair / ColorRGBA 等：按子节点顺次
    out = {}
    off2 = off
    ci = i + 1
    for _ in range(nc):
        cname = nodes[ci]["name"].decode("utf-8", "replace")
        v, off2 = read_value(nodes, spans, ci, data, off2)
        out[cname] = v
        ci += spans[ci]
    return out, off2

def deserialize_tree(tree, data):
    nodes = tree["nodes"]
    spans = compute_spans(nodes)
    return read_value(nodes, spans, 0, data, 0)

# ---------------- 主流程 ----------------
def read_len_str(d, p):
    if p + 4 > len(d): return None, p
    ln = struct.unpack_from(">i", d, p)[0]
    if ln < 0 or ln > 4096 or p + 4 + ln > len(d): return None, p
    return d[p+4:p+4+ln].decode("utf-8", "replace"), p + 4 + ln

def extract_externals(u):
    meta = u.meta
    ot_end = u.table_off + len(u.objects) * 20
    region = meta[ot_end:ot_end+512]
    exts = {}; fid = 0; i = 0
    while i < len(region) - 4:
        e = region.find(b"\x00", i)
        if e == -1: break
        s = region[i:e]
        if 1 <= len(s) <= 120 and (b".assets" in s or b".resource" in s or b"/" in s or b"mainData" in s or b".res" in s):
            fid += 1
            exts[fid] = s.decode("utf-8", "replace")
        i = e + 1
    return exts

def main():
    # 全局 MonoScript 注册表
    registry = {}   # filename -> {pid: info}
    for fn in FILES:
        try:
            u = Unity1x(os.path.join(D, fn))
        except Exception:
            continue
        fmap = {}
        for i in u.by_class(115):
            o = u.objects[i]
            d = u.obj_data(o)
            cls, p1 = read_len_str(d, 0)
            ns, p2 = read_len_str(d, p1) if cls is not None else (None, 0)
            asmb, _ = read_len_str(d, p2) if ns is not None else (None, 0)
            fmap[o.pathID] = {"class": cls or "", "ns": ns or "", "asm": asmb or ""}
        registry[fn] = fmap

    results = []
    stats = {"ok": 0, "desync": 0, "noscript": 0, "notree": 0, "short": 0}
    desync_examples = []
    per_class_fields = defaultdict(set)

    for fn in FILES:
        try:
            u = Unity1x(os.path.join(D, fn))
        except Exception:
            continue
        meta = u.meta
        trees = parse_all_trees(meta, 5, u.table_off - 7)
        tree_by_pid = {}
        orphan_trees = []
        for tr in trees:
            if tr["classID"] < 0:
                pid = -tr["classID"]
                if pid in {u.objects[i].pathID for i in u.by_class(114)}:
                    tree_by_pid[pid] = tr
                else:
                    orphan_trees.append(tr)
        # 兜底：无树 MB ↔ 孤儿树 按 byteSize 配对
        mb_no_tree = [i for i in u.by_class(114)
                      if u.objects[i].pathID not in tree_by_pid]
        for mi in mb_no_tree:
            o = u.objects[mi]
            cand = [tr for tr in orphan_trees
                    if tr["nodes"][0]["bs"] == o.size or tr["nodes"][0]["bs"] == 0xFFFFFFFF]
            if len(cand) == 1:
                tree_by_pid[o.pathID] = cand[0]
                orphan_trees.remove(cand[0])
        exts = extract_externals(u)
        fmap_self = registry.get(fn, {})
        mb_idx = u.by_class(114)

        for mi in mb_idx:
            o = u.objects[mi]
            d = u.obj_data(o)
            rec = {"file": fn, "mb_pid": o.pathID, "typeID": o.typeID,
                   "size": o.size, "script_class": None, "fields": None}
            if len(d) < 17:
                stats["short"] += 1; results.append(rec); continue
            go_pid = struct.unpack_from(">i", d, 4)[0]
            en = d[8]
            sc_file = struct.unpack_from(">i", d, 9)[0]
            sc_pid = struct.unpack_from(">i", d, 13)[0]
            rec["go_pid"] = go_pid; rec["enabled"] = en
            rec["sc_file"] = sc_file; rec["sc_pid"] = sc_pid
            # 脚本名
            info = None
            if sc_pid == 0 and sc_file == 0:
                rec["script_class"] = "MissingScript"
            else:
                if sc_file == 0:
                    info = fmap_self.get(sc_pid)
                else:
                    tgt = exts.get(sc_file)
                    if tgt and tgt in registry:
                        info = registry[tgt].get(sc_pid)
                if info is None:
                    for f2 in registry.values():
                        if sc_pid in f2:
                            info = f2[sc_pid]; break
                rec["script_class"] = info["class"] if info else "UNRESOLVED"
            # 反序列化
            tr = tree_by_pid.get(o.pathID)
            if tr is None:
                stats["notree"] += 1; results.append(rec); continue
            try:
                val, consumed = deserialize_tree(tr, d)
            except Desync as ex:
                stats["desync"] += 1
                if len(desync_examples) < 10:
                    desync_examples.append((fn, o.pathID, rec["script_class"], o.size, str(ex)))
                results.append(rec); continue
            if consumed != len(d):
                stats["desync"] += 1
                if len(desync_examples) < 10:
                    desync_examples.append((fn, o.pathID, rec["script_class"], o.size, f"consumed={consumed}"))
                results.append(rec); continue
            if isinstance(val, dict):
                fields = {k: v for k, v in val.items()
                          if k not in ("m_GameObject", "m_Enabled", "m_Script")}
                rec["fields"] = fields
                if rec["script_class"] not in (None, "MissingScript", "UNRESOLVED"):
                    per_class_fields[rec["script_class"]].update(fields.keys())
                    stats["ok"] += 1
            results.append(rec)

    print("=== 提取统计 ===")
    print(f"  成功(字段+字节精确)={stats['ok']}  反序列化失步={stats['desync']}  "
          f"无树={stats['notree']}  短数据={stats['short']}")
    print(f"  总记录={len(results)}")
    if desync_examples:
        print("  失步示例:")
        for e in desync_examples: print("   ", e)
    print(f"\n=== 各脚本类字段清单 ({len(per_class_fields)} 类) ===")
    for cls in sorted(per_class_fields):
        print(f"  {cls}: {sorted(per_class_fields[cls])}")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"\n已写出 {OUT}")

if __name__ == "__main__":
    main()
