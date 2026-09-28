#!/usr/bin/env python3
"""用 UnityPy 拿 (classID -> type 名) 权威映射，并导出可读对象 JSON。"""
import json, os, sys
try:
    import UnityPy
except Exception as e:
    print("UnityPy 导入失败:", e); sys.exit(1)

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
SA = os.path.join(D, 'sharedassets.assets')

env = UnityPy.load(SA)
cid2name = {}
read_ok = 0
read_fail = 0
for obj in env.objects:
    cid2name.setdefault(obj.class_id, obj.type.name)
    # 尝试读取（收集可读资产）
    try:
        d = obj.read()
        read_ok += 1
    except Exception as e:
        read_fail += 1

print("=== classID -> UnityPy 类型名 ===")
for cid in sorted(cid2name):
    print(f"  {cid:>4}  {cid2name[cid]}")
print(f"\nread_ok={read_ok} read_fail={read_fail}")

with open(r'D:\GooBall\scripts\_cid2name.json', 'w') as f:
    json.dump(cid2name, f, indent=2)
print("已写 _cid2name.json")
