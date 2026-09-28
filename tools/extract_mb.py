#!/usr/bin/env python3
"""提取 MonoScript 清单 + MonoBehaviour(17/114) 的 m_Script 关联。
MonoScript(115) 布局: [0:4] m_Name(len BE) [4:] name\0 [..] className\0 [..] assembly\0
MonoBehaviour: [0:8] PPtr<GameObject> [8:16] PPtr<MonoScript> [16] m_Enabled
"""
import os, sys, struct, json
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract'
all_files = [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]

# 1) 收集 MonoScript 清单
monoscripts = {}  # pathID -> dict
for fn in all_files:
    p = os.path.join(D, fn)
    if not os.path.exists(p): continue
    u = Unity1x(p)
    for i in u.by_class(115):
        o = u.objects[i]
        raw = u.obj_data(o)
        # 解析 [name][className][assembly]，每个 = u32BE len + bytes
        pos = 0
        def rd_str(r, p0):
            if p0+4 > len(r): return None, p0
            L = struct.unpack('>I', r[p0:p0+4])[0]
            if p0+4+L > len(r): return None, p0
            return r[p0+4:p0+4+L].decode('ascii','replace'), p0+4+L
        name, pos = rd_str(raw, 0)
        cls, pos = rd_str(raw, pos)
        asm, pos = rd_str(raw, pos)
        monoscripts[o.pathID] = {"name": name, "className": cls, "assembly": asm, "file": fn}

print(f"MonoScript 清单: {len(monoscripts)}")
names = sorted(set(v["name"] for v in monoscripts.values() if v["name"]))
print(f"唯一脚本类名: {len(names)}")
for n in names:
    print(f"  {n}")

# 2) MonoBehaviour -> MonoScript 关联
mb_records = []
for fn in all_files:
    p = os.path.join(D, fn)
    if not os.path.exists(p): continue
    u = Unity1x(p)
    for cid in (17, 114):
        for i in u.by_class(cid):
            o = u.objects[i]
            raw = u.obj_data(o)
            if len(raw) < 16: continue
            go_file = struct.unpack('>i', raw[0:4])[0]
            go_pid = struct.unpack('>i', raw[4:8])[0]
            s_file = struct.unpack('>i', raw[8:12])[0]
            s_pid = struct.unpack('>i', raw[12:16])[0]
            enabled = raw[16] if len(raw) > 16 else None
            rec = {"file": fn, "classID": cid, "pathID": o.pathID,
                   "gameObject": {"fileID": go_file, "pathID": go_pid},
                   "script": {"fileID": s_file, "pathID": s_pid,
                              "name": monoscripts.get(s_pid, {}).get("name")},
                   "enabled": enabled}
            mb_records.append(rec)

with open(os.path.join(OUT, "monobehaviours.json"), 'w', encoding='utf-8') as f:
    json.dump(mb_records, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT, "monoscripts.json"), 'w', encoding='utf-8') as f:
    json.dump(monoscripts, f, ensure_ascii=False, indent=2)

print(f"\nMonoBehaviour 实例: {len(mb_records)} (classID17 + classID114)")
# 统计每个脚本类关联了多少 MB
from collections import Counter
c = Counter(r["script"]["name"] for r in mb_records if r["script"]["name"])
print("Top 脚本关联数:")
for nm, n in c.most_common(15):
    print(f"  {n:>5}  {nm}")
