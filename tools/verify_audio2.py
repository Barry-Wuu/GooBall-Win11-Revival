#!/usr/bin/env python3
"""验证所有 WAV/MP3 可解码，时长与存储 dur 对比。"""
import subprocess, glob, os, re, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\audio'
FF = r'D:\B++\WorkBuddy\tools\ffmpeg\bin\ffmpeg.exe'

# 重建存储 dur 表
u = Unity1x(os.path.join(D, 'sharedassets.assets'))
dur_map = {}
for o in u.objects:
    if o.classID != 83: continue
    d = u.obj_data(o)
    n = int.from_bytes(d[0:4],'big')
    if not (0<n<200): continue
    name = d[4:4+n].decode('ascii','replace')
    p = 4+n; fmt = int.from_bytes(d[p:p+4],'big')
    if fmt==5: continue
    dur = struct.unpack('>f', d[p+4:p+8])[0]
    dur_map[name] = dur

def safe(name):
    return ''.join(c if c.isalnum() or c in ' -_' else '_' for c in name)

def ff_probe(f):
    r = subprocess.run([FF,'-hide_banner','-i',f],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    s = r.stderr.decode('utf-8','replace')
    dur=None
    for line in s.splitlines():
        if 'Duration:' in line:
            m=re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)',line)
            if m: dur=int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))
    return dur

def ff_check(f):
    r = subprocess.run([FF,'-v','error','-i',f,'-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    err=[l for l in r.stderr.decode('utf-8','replace').splitlines() if l.strip()]
    return r.returncode, err

files = sorted(glob.glob(os.path.join(OUT,'*.wav'))+glob.glob(os.path.join(OUT,'*.mp3')))
bad=0
for f in files:
    rc, err = ff_check(f)
    dur = ff_probe(f)
    base = os.path.splitext(os.path.basename(f))[0]
    # 还原原始名（safe 反向不精确，用文件名前缀匹配）
    orig = None
    for k in dur_map:
        if safe(k) == base: orig=k;break
    sd = dur_map.get(orig)
    flag=''
    if rc!=0: flag+=' [DECODE_ERR]'; bad+=1
    if sd and dur:
        if abs(sd-dur)>0.3: flag+=f' [DUR_MISMATCH {sd:.2f}vs{dur:.2f}]'; bad+=1
    print(f"{os.path.basename(f):<36} rc={rc} dur={dur!s:>8} {flag}")
print(f"\n问题文件: {bad}")
