#!/usr/bin/env python3
"""提取 TextMesh (classID=102) 的游戏内文本 + 字体/材质引用。
布局: [0:8] PPtr<GameObject>(fileID i32 BE, pathID i32 BE)
       [8:12] m_Text length (u32 BE)
       [12:12+L] m_Text
       ... m_OffsetZ(f32 BE), m_CharacterSize(f32 BE), m_LineSpacing(f32 BE),
           m_Anchor(i32), m_Alignment(i32), m_TabSize(f32 BE),
           PPtr<Font>(8B), PPtr<Material>(8B), m_Color(RGBA f32 BE x4)
"""
import os, sys, struct, json
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\textmeshes'
os.makedirs(OUT, exist_ok=True)

all_files = [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]
records = []
for fn in all_files:
    p = os.path.join(D, fn)
    if not os.path.exists(p): continue
    u = Unity1x(p)
    for i in u.by_class(102):
        o = u.objects[i]
        raw = u.obj_data(o)
        if len(raw) < 12: continue
        go_file = struct.unpack('>i', raw[0:4])[0]
        go_pid = struct.unpack('>i', raw[4:8])[0]
        tl = struct.unpack('>I', raw[8:12])[0]
        if 0 < tl < len(raw) - 12:
            text = raw[12:12+tl].decode('utf-8', 'replace')
        else:
            text = ''
        rec = {
            "file": fn, "pathID": o.pathID, "size": o.size,
            "gameObject": {"fileID": go_file, "pathID": go_pid},
            "text": text,
        }
        records.append(rec)

# 按文件分组写 JSON
by_file = {}
for r in records:
    by_file.setdefault(r["file"], []).append(r)
for fn, recs in by_file.items():
    with open(os.path.join(OUT, f"{fn}_textmeshes.json"), 'w', encoding='utf-8') as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "_all_textmeshes.json"), 'w', encoding='utf-8') as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

# 汇总唯一文本
texts = sorted(set(r["text"] for r in records if r["text"]))
print(f"TextMesh 总数: {len(records)}")
print(f"含文本: {sum(1 for r in records if r['text'])}")
print(f"唯一文本: {len(texts)}")
print("\n=== 全部游戏内文本 ===")
for t in texts:
    print(f"  {t!r}")
