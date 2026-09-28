# -*- coding: utf-8 -*-
"""extract_all_tex.py —— GooBall Texture2D 全量提取（内联 + 流式 DXT）
机制定案：
  对象头(45B, 名字后) 之后可能直接跟图像数据（内联）；
  大贴图（1024x512 等）数据不在对象内，而是紧贴对象头之前的流洞：
      data = raw[obj.offset - need : obj.offset]   need = 块数×块大小
  DXT1(10): 8B/块   c0,c1 u16 大端 + u32 索引小端；c0<=c1 时第4色=透明(1bit alpha)
  DXT5(11): 16B/块  alpha 8B(2参考+16×3bit) + DXT1 色 8B
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unity1x import Unity1x
from PIL import Image
from collections import Counter

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\textures'
os.makedirs(OUT, exist_ok=True)


def rgb565(v):
    return (((v >> 11) & 31) * 255 // 31,
            ((v >> 5) & 63) * 255 // 63,
            (v & 31) * 255 // 31)


def dxt1_decode(data, w, h):
    bw, bh = (w + 3) // 4, (h + 3) // 4
    img = Image.new('RGBA', (w, h))
    pix = img.load()
    for by in range(bh):
        for bx in range(bw):
            o = (by * bw + bx) * 8
            blk = data[o:o+8].ljust(8, b'\x00')
            c0 = int.from_bytes(blk[0:2], 'big')
            c1 = int.from_bytes(blk[2:4], 'big')
            idx = int.from_bytes(blk[4:8], 'little')
            cols = [rgb565(c0), rgb565(c1)]
            if c0 > c1:
                cols.append(tuple((2*cols[0][i]+cols[1][i])//3 for i in range(3)))
                cols.append(tuple((cols[0][i]+2*cols[1][i])//3 for i in range(3)))
                a = (255, 255, 255, 255)
            else:
                cols.append(tuple((cols[0][i]+cols[1][i])//2 for i in range(3)))
                cols.append((255, 0, 255))
                a = (255, 255, 255, 0)
            for py in range(4):
                for px in range(4):
                    x, y = bx*4+px, by*4+py
                    if x < w and y < h:
                        ci = (idx >> ((py*4+px)*2)) & 3
                        c = cols[ci]
                        pix[x, y] = (c[0], c[1], c[2], a[ci])
    return img


def dxt5_decode(data, w, h):
    bw, bh = (w + 3) // 4, (h + 3) // 4
    img = Image.new('RGBA', (w, h))
    pix = img.load()
    for by in range(bh):
        for bx in range(bw):
            o = (by * bw + bx) * 16
            blk = data[o:o+16].ljust(16, b'\x00')
            a0, a1 = blk[0], blk[1]
            aidx = int.from_bytes(blk[2:8], 'little')
            if a0 > a1:
                apal = [a0, a1, (6*a0+a1)//7, (5*a0+2*a1)//7, (4*a0+3*a1)//7,
                        (3*a0+4*a1)//7, (2*a0+5*a1)//7, (a0+6*a1)//7]
            else:
                apal = [a0, a1, (4*a0+a1)//5, (3*a0+2*a1)//5, (2*a0+3*a1)//5,
                        (a0+4*a1)//5, 0, 255]
            c0 = int.from_bytes(blk[8:10], 'big')
            c1 = int.from_bytes(blk[10:12], 'big')
            idx = int.from_bytes(blk[12:16], 'little')
            cols = [rgb565(c0), rgb565(c1)]
            if c0 > c1:
                cols.append(tuple((2*cols[0][i]+cols[1][i])//3 for i in range(3)))
                cols.append(tuple((cols[0][i]+2*cols[1][i])//3 for i in range(3)))
            else:
                cols.append(tuple((cols[0][i]+cols[1][i])//2 for i in range(3)))
                cols.append((0, 0, 0))
            for py in range(4):
                for px in range(4):
                    x, y = bx*4+px, by*4+py
                    if x < w and y < h:
                        k = py*4+px
                        ai = (aidx >> (k*3)) & 7
                        ci = (idx >> (k*2)) & 3
                        c = cols[ci]
                        pix[x, y] = (c[0], c[1], c[2], apal[ai])
    return img


def mip_chain_bytes(w, h, bpp_bytes):
    total = 0
    while True:
        total += w * h * bpp_bytes
        if w == 1 and h == 1:
            break
        w, h = max(w // 2, 1), max(h // 2, 1)
    return total


def main():
    u = Unity1x(os.path.join(D, 'sharedassets.assets'))
    ok = 0
    skip = Counter()
    fail = []
    names = Counter()
    for o in u.objects:
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
        if not (0 < w <= 4096 and 0 < h <= 4096):
            continue
        off = p + 45

        if fmt in (1, 2, 3, 7):                          # 非压缩：内联
            store = (w*h*3 if fmt == 3 else
                     w*h*2 if fmt in (2, 7) else
                     mip_chain_bytes(w, h, 1))
            data = d[off:off + store]
            px = None
            if fmt == 7 and len(data) >= w*h*2:
                px = [(*rgb565(int.from_bytes(data[i*2:i*2+2], 'big')), 255)
                      for i in range(w*h)]
            elif fmt == 3 and len(data) >= w*h*3:
                px = [(data[i*3], data[i*3+1], data[i*3+2], 255) for i in range(w*h)]
            elif fmt == 2 and len(data) >= w*h*2:
                px = []
                for i in range(w*h):
                    v = int.from_bytes(data[i*2:i*2+2], 'big')
                    px.append((((v >> 8) & 15)*17, ((v >> 4) & 15)*17,
                               (v & 15)*17, ((v >> 12) & 15)*17))
            elif fmt == 1 and len(data) >= w*h:
                px = [(v, v, v, 255) for v in data[:w*h]]
            if px is None:
                fail.append((name, w, h, fmt, '数据不足'))
                continue
            img = Image.new('RGBA', (w, h))
            img.putdata(px)
        elif fmt == 10:                                   # DXT1（内联或流洞）
            need = ((w+3)//4) * ((h+3)//4) * 8
            data = d[off:off+need]
            if len(data) < need:
                # 流洞规则（montezuma 实证）：头挤占 2^18 预算，
                # 数据 = [obj.offset - need + o.size, obj.offset)，尾部可能截断
                data = u.raw[max(16, o.offset - need + o.size):o.offset]
            if len(data) < need:
                data = data.ljust(need, b'\x00')
            img = dxt1_decode(data, w, h)
        elif fmt == 11:                                   # DXT5
            need = ((w+3)//4) * ((h+3)//4) * 16
            data = d[off:off+need]
            if len(data) < need:
                data = u.raw[max(16, o.offset - need + o.size):o.offset]
            if len(data) < need:
                data = data.ljust(need, b'\x00')
            img = dxt5_decode(data, w, h)
        else:
            skip[fmt] += 1
            continue

        names[name] += 1
        safe = name.strip().replace(' ', '_').replace('-', '_') or f'tex_{o.pathID}'
        if names[name] > 1:
            safe = f'{safe}_{names[name]}'
        fp = os.path.join(OUT, f'{safe}.png')
        img.save(fp)
        ok += 1

    print(f'提取成功: {ok} 张 -> {OUT}')
    print(f'未支持格式: {dict(skip)}')
    if fail:
        print(f'失败 {len(fail)}:')
        for f in fail[:12]:
            print('  ', f)


if __name__ == '__main__':
    main()
