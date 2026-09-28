# -*- coding: utf-8 -*-
"""decode_dxt1.py —— 解流洞中的 DXT1 大贴图（六大世界主图 1024x512）。
机制：大贴图占 2^18=262144B 预算 = 对象头(58B) + DXT1 数据；洞紧邻对象头。
试验：montezuma 对象@302,984，洞 = 40,898..302,984 (262,086B)。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unity1x import Unity1x
from PIL import Image

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\textures'
os.makedirs(OUT, exist_ok=True)
ENDIAN = 'big'        # DXT 块内 color0/color1 按小端试（硬件惯例），失败再换


def dxt1_decode(data, w, h, endian='little'):
    """BC1/DXT1: 每 4x4 像素块 8 字节 = c0,c1 (u16) + 32bit 索引。"""
    bw, bh = (w + 3) // 4, (h + 3) // 4
    img = Image.new('RGBA', (w, h))
    pix = img.load()
    for by in range(bh):
        for bx in range(bw):
            o = (by * bw + bx) * 8
            blk = data[o:o+8].ljust(8, b'\x00')
            c0 = int.from_bytes(blk[0:2], endian)
            c1 = int.from_bytes(blk[2:4], endian)
            idx = int.from_bytes(blk[4:8], 'little')
            r0 = ((c0 >> 11) & 31) * 255 // 31
            g0 = ((c0 >> 5) & 63) * 255 // 63
            b0 = (c0 & 31) * 255 // 31
            r1 = ((c1 >> 11) & 31) * 255 // 31
            g1 = ((c1 >> 5) & 63) * 255 // 63
            b1 = (c1 & 31) * 255 // 31
            pal = [(r0, g0, b0, 255), (r1, g1, b1, 255)]
            if c0 > c1:      # 不透明模式：第 3/4 色插值
                pal.append(((2*r0 + r1) // 3, (2*g0 + g1) // 3, (2*b0 + b1) // 3, 255))
                pal.append(((r0 + 2*r1) // 3, (g0 + 2*g1) // 3, (b0 + 2*b1) // 3, 255))
            else:            # 1-bit alpha 模式
                pal.append(((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2, 255))
                pal.append((0, 0, 0, 0))
            for py in range(4):
                for px in range(4):
                    x, y = bx*4 + px, by*4 + py
                    if x >= w or y >= h:
                        continue
                    k = (py*4 + px) * 2
                    pix[x, y] = pal[(idx >> k) & 3]
    return img


def main():
    u = Unity1x(os.path.join(D, 'sharedassets.assets'))
    target = None
    for o in u.objects:
        if o.classID != 28:
            continue
        d = u.obj_data(o)
        n = int.from_bytes(d[0:4], 'big')
        if not (0 < n < 100):
            continue
        if d[4:4+n] == b'montezuma' and o.size < 200:
            target = (o, d)
            break
    o, d = target
    n = int.from_bytes(d[0:4], 'big')
    p = 4 + n
    w = int.from_bytes(d[p:p+4], 'big')
    h = int.from_bytes(d[p+4:p+8], 'big')
    fmt = int.from_bytes(d[p+12:p+16], 'big')
    print(f'montezuma: {w}x{h} fmt={fmt} 对象@{o.offset:#x} sz={o.size}')
    # 洞 = 对象前一段：从上一对象结束对齐处到本对象起点
    # row22 前一行（row21）结束于 40,898
    hole_start = 40840
    data = u.raw[hole_start:o.offset]
    print(f'洞数据: {hole_start:#x}..{o.offset:#x} = {len(data):,}B (满块需 {w//4*(h//4)*8:,}B)')
    img = dxt1_decode(data, w, h, ENDIAN)
    fp = os.path.join(OUT, 'montezuma_dxt1.png')
    img.save(fp)
    print('->', fp)


if __name__ == '__main__':
    main()
