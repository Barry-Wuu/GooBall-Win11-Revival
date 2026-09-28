# -*- coding: utf-8 -*-
"""extract_stream_tex.py —— 流式 DXT 贴图提取（自动洞扫描版）
洞定位：对每个流式对象，在其前方 gap 内按 8B 步进扫描起点，
判据 = 首 256 块 c0 序列相邻差和最小（真实图像块间颜色连续）。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unity1x import Unity1x
from extract_all_tex import dxt1_decode, dxt5_decode

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\textures'
os.makedirs(OUT, exist_ok=True)


def find_best_start(raw, lo, hi, need):
    """在 [lo, hi] 按 8 步进扫描，返回 (最优起点, 分数)。分数=首行块 c0 相邻差和。"""
    best, best_score = None, None
    seg_need = 256 * 8
    for s in range(lo, hi + 1, 8):
        if s + seg_need > len(raw):
            break
        seg = raw[s:s + seg_need]
        c0s = [int.from_bytes(seg[i*8:i*8+2], 'big') for i in range(256)]
        score = sum(abs(c0s[i] - c0s[i+1]) for i in range(255))
        if best_score is None or score < best_score:
            best, best_score = s, score
    return best, best_score


def main():
    u = Unity1x(os.path.join(D, 'sharedassets.assets'))
    objs = u.objects
    done, fail = 0, []
    for i, o in enumerate(objs):
        if o.classID != 28:
            continue
        d = u.obj_data(o)
        n = int.from_bytes(d[0:4], 'big')
        if not (0 < n < 100):
            continue
        name = d[4:4+n].decode('ascii', 'replace')
        p = 4 + n
        w = int.from_bytes(d[p:p+4], 'big')
        h = int.from_bytes(d[p+4:p+8], 'big')
        fmt = int.from_bytes(d[p+12:p+16], 'big')
        if fmt not in (10, 11):
            continue
        bs = 16 if fmt == 11 else 8
        need = ((w+3)//4) * ((h+3)//4) * bs
        off = p + 45
        if o.size - off >= need:
            continue                                  # 内联，主脚本已处理
        # 前方 gap = [prev 结束对齐, o.offset)
        prev_end = objs[i-1].offset + objs[i-1].size if i > 0 else 16
        gap_lo, gap_hi = prev_end, o.offset
        if gap_hi - gap_lo < need - 8:
            fail.append((name, w, h, fmt, f'gap 不足 {gap_hi-gap_lo}/{need}'))
            continue
        s, score = find_best_start(u.raw, gap_lo, gap_hi - need + 8, need)
        if s is None:
            fail.append((name, w, h, fmt, '无起点'))
            continue
        data = u.raw[s:s+need].ljust(need, b'\x00')
        img = dxt1_decode(data, w, h) if fmt == 10 else dxt5_decode(data, w, h)
        safe = name.strip().replace(' ', '_').replace('-', '_') or f'tex_{o.pathID}'
        fp = os.path.join(OUT, f'{safe}_{o.pathID}.png')
        img.save(fp)
        done += 1
        print(f'OK {name:<22} {w}x{h} fmt={fmt} 洞起点={s:#x} 分={score}')
    print(f'\n流式提取: {done} 张')
    if fail:
        print('失败:')
        for f in fail:
            print('  ', f)


if __name__ == '__main__':
    main()
