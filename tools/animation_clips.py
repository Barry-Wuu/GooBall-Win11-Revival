# -*- coding: utf-8 -*-
"""GooBall AnimationClip(74) 关键帧曲线解包
============================================
用内置类型树反序列化全部 AnimationClip，产出结构化动画数据：
  m_Name / m_SampleRate / m_ChildTracks / m_ClassIDToTrack
  m_RotationCurves(QuaternionCurve) / m_PositionCurves / m_ScaleCurves(Vector3Curve)
  m_FloatCurves(FloatCurve)
每条曲线含 path + keyframes[{t, v[, inSlope, outSlope]}]。
输出 assets/animations/clips_index.json + assets/animations/clips/<name>_<pid>.json
"""
import struct, os, sys, json, re
sys.path.insert(0, ".")
from unity1x import Unity1x
from mb_fields import parse_all_trees, deserialize_tree, Desync

D = r"D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data"
HERE = os.path.dirname(__file__)
REPO = os.path.join(HERE, "..", "repo_git")
OUT = os.path.join(REPO, "assets", "animations")
os.makedirs(os.path.join(OUT, "clips"), exist_ok=True)
FILES = [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]

def decode_text(v):
    if v is None:
        return None
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        if "Array" in v and isinstance(v["Array"], list):
            arr = v["Array"]
            if arr and all(isinstance(x, int) and 0 <= x < 256 for x in arr):
                return bytes(arr).decode("utf-8", "replace")
        if "string" in v:
            return decode_text(v["string"])
    return None

def v3(x):
    if isinstance(x, dict) and "x" in x:
        return [round(float(x.get("x", 0)), 5), round(float(x.get("y", 0)), 5), round(float(x.get("z", 0)), 5)]
    return x

def v4(x):
    if isinstance(x, dict) and "x" in x:
        return [round(float(x.get("x", 0)), 5), round(float(x.get("y", 0)), 5),
                round(float(x.get("z", 0)), 5), round(float(x.get("w", 0)), 5)]
    return x

def curve_kfs(curve_obj, dim):
    """从 QuaternionCurve/Vector3Curve/FloatCurve 抽取 keyframes"""
    if not isinstance(curve_obj, dict):
        return []
    ac = curve_obj.get("curve")
    if not isinstance(ac, dict):
        return []
    kfs = ac.get("m_Curve")
    if isinstance(kfs, dict) and "Array" in kfs:
        kfs = kfs["Array"]
    if not isinstance(kfs, list):
        return []
    out = []
    for k in kfs:
        if not isinstance(k, dict):
            continue
        t = k.get("time")
        val = k.get("value")
        if dim == "q":
            out.append([round(float(t), 5), v4(val)])
        elif dim == "v3":
            out.append([round(float(t), 5), v3(val)])
        else:  # float
            out.append([round(float(t), 5), round(float(val), 5) if val is not None else None])
    return out

def safe(s):
    return re.sub(r"[^0-9A-Za-z_\-]+", "_", (s or "x")).strip("_")[:60] or "x"

def main():
    index = []
    total_kf = 0
    max_size = 0
    for fn in FILES:
        path = os.path.join(D, fn)
        if not os.path.exists(path):
            continue
        try:
            u = Unity1x(path)
        except Exception:
            continue
        try:
            trees = parse_all_trees(u.meta, 5, u.table_off - 7)
        except Exception:
            continue
        by_cid = {}
        for t in trees:
            by_cid.setdefault(t["classID"], t)
        if 74 not in by_cid:
            continue
        for i in u.by_class(74):
            o = u.objects[i]
            d = u.obj_data(o)
            try:
                v, cons = deserialize_tree(by_cid[74], d)
            except Desync as e:
                index.append({"file": fn, "pathID": o.pathID, "size": o.size, "error": str(e),
                              "raw": f"clips/{safe(f'anim{o.pathID}')}_{o.pathID}.raw.bin"})
                with open(os.path.join(OUT, "clips", f"{safe(f'anim{o.pathID}')}_{o.pathID}.raw.bin"), "wb") as rf:
                    rf.write(d)
                continue
            if cons != len(d):
                index.append({"file": fn, "pathID": o.pathID, "size": o.size, "error": f"consumed={cons}",
                              "raw": f"clips/{safe(f'anim{o.pathID}')}_{o.pathID}.raw.bin"})
                with open(os.path.join(OUT, "clips", f"{safe(f'anim{o.pathID}')}_{o.pathID}.raw.bin"), "wb") as rf:
                    rf.write(d)
                continue
            name = decode_text(v.get("m_Name")) or f"anim{o.pathID}"
            rec = {"file": fn, "pathID": o.pathID, "name": name,
                   "sampleRate": v.get("m_SampleRate"), "size": o.size,
                   "rotationCurves": [], "positionCurves": [], "scaleCurves": [],
                   "floatCurves": [], "childTracks": []}
            dur = 0.0
            for c in (v.get("m_RotationCurves") or []):
                kfs = curve_kfs(c, "q")
                p = decode_text(c.get("path"))
                rec["rotationCurves"].append({"path": p, "keyframes": kfs})
                if kfs: dur = max(dur, kfs[-1][0])
            for key, dim in (("m_PositionCurves", "v3"), ("m_ScaleCurves", "v3")):
                for c in (v.get(key) or []):
                    kfs = curve_kfs(c, dim)
                    p = decode_text(c.get("path"))
                    rec["positionCurves" if key == "m_PositionCurves" else "scaleCurves"].append(
                        {"path": p, "keyframes": kfs})
                    if kfs: dur = max(dur, kfs[-1][0])
            for c in (v.get("m_FloatCurves") or []):
                kfs = curve_kfs(c, "f")
                rec["floatCurves"].append({
                    "path": decode_text(c.get("path")),
                    "attribute": decode_text(c.get("attribute")),
                    "classID": c.get("classID"),
                    "keyframes": kfs})
                if kfs: dur = max(dur, kfs[-1][0])
            for ct in (v.get("m_ChildTracks") or []):
                if isinstance(ct, dict):
                    rec["childTracks"].append({"path": decode_text(ct.get("path")),
                                               "classID": ct.get("classID")})
            rec["duration"] = round(dur, 4)
            nk = sum(len(c["keyframes"]) for c in
                     rec["rotationCurves"] + rec["positionCurves"] + rec["scaleCurves"] + rec["floatCurves"])
            rec["keyframe_count"] = nk
            total_kf += nk
            max_size = max(max_size, o.size)
            # 写单 clip 结构化文件
            with open(os.path.join(OUT, "clips", f"{safe(name)}_{o.pathID}.json"), "w", encoding="utf-8") as f:
                json.dump(rec, f, ensure_ascii=False, indent=1)
            # 索引摘要（去掉 keyframes 明细，只留计数）
            index.append({
                "file": fn, "pathID": o.pathID, "name": name,
                "sampleRate": rec["sampleRate"], "duration": rec["duration"],
                "keyframe_count": nk, "size": o.size,
                "rotation": len(rec["rotationCurves"]), "position": len(rec["positionCurves"]),
                "scale": len(rec["scaleCurves"]), "float": len(rec["floatCurves"]),
                "childTracks": len(rec["childTracks"]),
                "paths": sorted({c["path"] for c in
                                 rec["rotationCurves"] + rec["positionCurves"] + rec["scaleCurves"]
                                 if c["path"]})[:6],
                "attributes": sorted({c["attribute"] for c in rec["floatCurves"] if c["attribute"]})[:6],
            })

    index.sort(key=lambda r: (r["file"], r.get("pathID", 0)))
    with open(os.path.join(OUT, "clips_index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)

    errs = [r for r in index if r.get("error")]
    print(f"=== AnimationClip 解包 ===")
    print(f"  clip 总数={len(index)}  失败={len(errs)}  总关键帧={total_kf}  最大clip字节={max_size}")
    if errs[:6]:
        print("  失败样例:", errs[:6])
    # 最长动画 top8
    ok = [r for r in index if not r.get("error")]
    print("  时长 top8:", [(r["name"], r["duration"], r["keyframe_count"]) for r in
                          sorted(ok, key=lambda r: -r["duration"])[:8]])
    print("已写出 assets/animations/clips_index.json + clips/*.json")

if __name__ == "__main__":
    main()
