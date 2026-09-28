#!/usr/bin/env python3
"""GooBall 全部非Ogg音频提取 -> WAV（全部为 PCM，无真MP3）。
fmt=1 -> 8-bit unsigned PCM
fmt=2 -> 16-bit signed LE PCM (mono)
fmt=4 -> 16-bit signed LE PCM (stereo)
声道以 duration 反推校验。流式余量紧跟内联、无间隙：
整段 = raw[o.offset+header : o.offset+header+s1], header=4+namelen+20。
删除此前误生成的全部 .mp3。
"""
import sys, os, struct, wave, glob
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\audio'
os.makedirs(OUT, exist_ok=True)

def safe(name):
    return ''.join(c if c.isalnum() or c in ' -_' else '_' for c in name)

u = Unity1x(os.path.join(D, 'sharedassets.assets'))
raw = u.raw
aus = [o for o in u.objects if o.classID == 83]
aus.sort(key=lambda o: o.pathID)

# 清理误生成的 .mp3
for mp in glob.glob(os.path.join(OUT, '*.mp3')):
    os.remove(mp)
print("已删除残留 .mp3")

def pick_channels(s1, bps, freq, dur):
    mono = s1 / (bps * 1 * freq)
    stereo = s1 / (bps * 2 * freq)
    return 1 if abs(mono - dur) <= abs(stereo - dur) else 2

ok = 0; report = []
for o in aus:
    d = u.obj_data(o)
    n = int.from_bytes(d[0:4], 'big')
    if not (0 < n < 200): continue
    name = d[4:4+n].decode('ascii', 'replace')
    p = 4 + n
    fmt = int.from_bytes(d[p:p+4], 'big')
    if fmt == 5:
        continue
    dur = struct.unpack('>f', d[p+4:p+8])[0]
    freq = int.from_bytes(d[p+8:p+12], 'big')
    s1 = int.from_bytes(d[p+12:p+16], 'big')
    header = 4 + n + 20
    audio = raw[o.offset + header : o.offset + header + s1]
    if len(audio) != s1:
        report.append(f"[!] {name}: 读取 {len(audio)} != s1 {s1}"); continue
    bps = 1 if fmt == 1 else 2
    ch = pick_channels(s1, bps, freq, dur)
    fp = os.path.join(OUT, safe(name) + '.wav')
    with wave.open(fp, 'wb') as w:
        w.setnchannels(ch); w.setsampwidth(bps); w.setframerate(freq)
        w.writeframes(audio)
    report.append(f"[PCM{'8' if bps==1 else '16'}] {name:<28} ch={ch} freq={freq} dur={dur:.2f}")
    ok += 1

print('\n'.join(report))
print(f"\n非Ogg提取: {ok} 个 WAV -> {OUT}")
