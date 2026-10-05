# -*- coding: utf-8 -*-
"""全量绑定 MonoBehaviour -> 脚本名（覆盖全部 71 文件 / 约 5698 实例）
核心：
  · 序列化数据 int32 为大端；MB base 布局固定：
      m_GameObject (m_FileID@0, m_PathID@4) + m_Enabled@8 + m_Script(m_FileID@9, m_PathID@13)
  · PPtr.fileID: 0=本文件, >=1=externals[fileID-1]
  · 仅 sharedassets 含 MonoScript(105)；关卡/ mainData 均为 0 -> 跨文件脚本全部落在 sharedassets
  · externals 映射：扫描元数据尾部 null 结尾的文件名串，按出现序映射 fileID
"""
import struct, os, sys, json
from collections import Counter
sys.path.insert(0, ".")
from unity1x import Unity1x

D = r"D:\GooBall\win\Data"

FILES = [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]

def read_len_str(d, p):
    if p + 4 > len(d): return None, p
    ln = struct.unpack_from(">i", d, p)[0]
    if ln < 0 or ln > 4096 or p + 4 + ln > len(d): return None, p
    return d[p+4:p+4+ln].decode("ascii", "replace"), p + 4 + ln

def extract_externals(u):
    """扫描元数据尾部，抽取 null 结尾的「文件名串」按出现序映射 fileID=1,2,...。"""
    meta = u.meta
    ot_end = u.table_off + len(u.objects) * 20
    region = meta[ot_end:ot_end+512]
    exts = {}
    fid = 0
    i = 0
    while i < len(region) - 4:
        # 找 \0 结尾串
        e = region.find(b"\x00", i)
        if e == -1: break
        s = region[i:e]
        if 1 <= len(s) <= 120 and (b".assets" in s or b".resource" in s or b"/" in s or b"mainData" in s or b".res" in s):
            fid += 1
            exts[fid] = s.decode("ascii", "replace")
        i = e + 1
    return exts

# ---- 构建全局 MonoScript 注册表： (file, pathID) -> {class, ns, asm} ----
registry = {}          # (filename, pathID) -> info
registry_by_file = {}  # filename -> {pathID: info}
files_with_ms = []
for fn in FILES:
    try:
        u = Unity1x(os.path.join(D, fn))
    except Exception as e:
        print(f"跳过 {fn}: {e}"); continue
    ms = u.by_class(115)
    if ms:
        files_with_ms.append(fn)
    fmap = {}
    for i in ms:
        o = u.objects[i]
        d = u.obj_data(o)
        cls, p1 = read_len_str(d, 0)
        ns, p2 = read_len_str(d, p1) if cls is not None else (None, 0)
        asmb, _ = read_len_str(d, p2) if ns is not None else (None, 0)
        info = {"class": cls or "", "ns": ns or "", "asm": asmb or "", "size": len(d)}
        registry[(fn, o.pathID)] = info
        fmap[o.pathID] = info
    registry_by_file[fn] = fmap

print(f"含 MonoScript 的文件={files_with_ms}  (总 MonoScript={sum(len(v) for v in registry_by_file.values())})")

# ---- 跨文件解析所有 MB ----
all_bind = []
unresolved = 0
per_file_stats = {}
script_dist = Counter()
mb_total = 0

for fn in FILES:
    try:
        u = Unity1x(os.path.join(D, fn))
    except Exception:
        continue
    exts = extract_externals(u)
    fmap_self = registry_by_file.get(fn, {})
    mb = u.by_class(114)
    if not mb:
        per_file_stats[fn] = 0
        continue
    cnt = 0
    for mi in mb:
        o = u.objects[mi]
        d = u.obj_data(o)
        if len(d) < 17:
            unresolved += 1; continue
        go_pid = struct.unpack_from(">i", d, 4)[0]
        en = d[8]
        sc_file = struct.unpack_from(">i", d, 9)[0]
        sc_pid = struct.unpack_from(">i", d, 13)[0]
        mb_total += 1
        # 解析脚本
        info = None
        if sc_pid == 0 and sc_file == 0:
            # 构建时被剥离/悬空的脚本引用（如 prefab 丢失脚本），无法还原类名
            cls = "MissingScript"
        else:
            if sc_file == 0:
                info = fmap_self.get(sc_pid)
            else:
                tgt = exts.get(sc_file)
                if tgt and tgt in registry_by_file:
                    info = registry_by_file[tgt].get(sc_pid)
            # 兜底：全局按 pathID 搜（因仅 sharedassets 有 MS，等价于 fileID>=1 -> sharedassets）
            if info is None:
                for (f2, pid2), v in registry.items():
                    if pid2 == sc_pid:
                        info = v; break
            cls = info["class"] if info else None
            if cls is None:
                unresolved += 1
                cls = "UNRESOLVED"
        if cls not in ("MissingScript", "UNRESOLVED"):
            script_dist[cls] += 1
        all_bind.append({
            "file": fn, "mb_pid": o.pathID, "typeID": o.typeID,
            "script_file": sc_file, "script_pid": sc_pid,
            "script_class": cls, "go_pid": go_pid, "enabled": en,
        })
        cnt += 1
    per_file_stats[fn] = cnt

n_missing = sum(1 for r in all_bind if r["script_class"] == "MissingScript")
n_unres = sum(1 for r in all_bind if r["script_class"] == "UNRESOLVED")
print(f"\nMB 实例总数(扫描)={mb_total}  成功绑定={mb_total-n_missing-n_unres}  "
      f"MissingScript(悬空)={n_missing}  UNRESOLVED={n_unres}")
print(f"跨文件映射命中示例 exts(sharedassets)={extract_externals(Unity1x(os.path.join(D,'level0')))}")
print(f"\n脚本种类数={len(script_dist)}")
for k, v in script_dist.most_common(30):
    print(f"   {k}: {v}")
print(f"\n每文件 MB 数(前20):")
for fn in FILES[:20]:
    if per_file_stats.get(fn,0)>0:
        print(f"   {fn}: {per_file_stats[fn]}")

# 写出
out = os.path.join(os.path.dirname(__file__), "mb_bind_all.json")
with open(out, "w") as f:
    json.dump(all_bind, f, indent=1, ensure_ascii=False)
print(f"\n已写出 {out}  ({len(all_bind)} 条)")
