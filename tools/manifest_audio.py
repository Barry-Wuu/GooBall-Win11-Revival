#!/usr/bin/env python3
"""汇总 GooBall 55 个音频资产清单（含格式/声道/采样率/时长/产物）。"""
import sys, os, struct, json, wave, glob
sys.path.insert(0, os.path.dirname(__file__))
from unity1x import Unity1x

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\audio'
u = Unity1x(os.path.join(D, 'sharedassets.assets'))
raw = u.raw

def safe(name):
    return ''.join(c if c.isalnum() or c in ' -_' else '_' for c in name)

# Ogg 时长（来自前次 verify）
ogg_dur = {
 'techno-jazz':825.53,'Debil updated, for Screampark':172.0,'UFO WIP, for New Mexico':117.0,
 'gameoverloop':20.29,'Montezuma':213.79,'Underwater':300.72,
 'Theme song, 09 on Morten F\'s demo':326.89,'Warp (Multi Report - eardrop)':377.89,
 'Monster':213.82}

FMTNAME={1:'PCM8',2:'PCM16',4:'PCM16',5:'OggVorbis'}
rows=[]
for o in u.objects:
    if o.classID!=83: continue
    d=u.obj_data(o); n=int.from_bytes(d[0:4],'big')
    if not (0<n<200): continue
    name=d[4:4+n].decode('ascii','replace'); p=4+n
    fmt=int.from_bytes(d[p:p+4],'big')
    freq=int.from_bytes(d[p+8:p+12],'big')
    s1=int.from_bytes(d[p+12:p+16],'big')
    header=4+n+20
    if fmt==5:
        fn=safe(name)+'.ogg'; ch='?'; dur=ogg_dur.get(name)
    else:
        fn=safe(name)+'.wav'
        bps=1 if fmt==1 else 2
        with wave.open(os.path.join(OUT,fn),'rb') as w:
            ch=w.getnchannels(); fr=w.getframerate(); nf=w.getnframes()
            dur=nf/fr
    fp=os.path.join(OUT,fn)
    rows.append({'name':name,'fmt':FMTNAME[fmt],'channels':ch,'freq':freq,
                 'decl_bytes':s1,'duration':round(dur,2) if dur else None,
                 'file':fn,'exists':os.path.exists(fp),
                 'bytes':os.path.getsize(fp) if os.path.exists(fp) else 0})

rows.sort(key=lambda r:r['name'].lower())
with open(os.path.join(OUT,'_manifest.json'),'w',encoding='utf-8') as f:
    json.dump(rows,f,ensure_ascii=False,indent=2)

print(f"总计 {len(rows)} 个音频资产:")
from collections import Counter
c=Counter(r['fmt'] for r in rows)
for k,v in c.items(): print(f"  {k}: {v}")
ogg_b=sum(r['bytes'] for r in rows if r['fmt']=='OggVorbis')
wav_b=sum(r['bytes'] for r in rows if r['fmt']!='OggVorbis')
print(f"  产物总大小: Ogg {ogg_b/1024/1024:.1f}MB + WAV {wav_b/1024/1024:.1f}MB")
missing=[r['name'] for r in rows if not r['exists']]
print(f"  缺失产物: {missing if missing else '无'}")
print(f"\n清单已写: {os.path.join(OUT,'_manifest.json')}")
