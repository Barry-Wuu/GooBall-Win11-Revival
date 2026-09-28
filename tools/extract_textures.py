# -*- coding: utf-8 -*-
"""extract_textures.py —— GooBall Texture2D 全量提取器（内联部分）
已确认格式（Unity 1.x, PPC 大端）：
  1  = Alpha8（含 mipmap 链，取顶层）        —— 灰度输出
  2  = ARGB4444 大端                         ✔ 实证 (ambrosia stencil)
  3  = RGB24（cisz 字段 = w*h*4-1 是显存分配尺寸，存储 3B/px）✔ 实证 (bubble)
  7  = RGB565 大端                           ✔ 实证 (monster1)
  10 = DXT1（统计 0.5B/px×4/3 mip，暂未解）
  11 = DXT5（统计 1B/px×4/3 mip，暂未解）
头布局：int32BE nameLen + name + 44B 头 + 图像数据
  头[0:4]=w  [4:8]=h  [8:12]=cisz  [12:16]=fmt  其余渲染设置
数据起点 = 名字后 45B；长度 = 存储尺寸（按格式算）
流式对象（数据不在对象内）单独列清单，指向流洞。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unity1x import Unity1x
from PIL import Image
import struct

D = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data'
OUT = r'D:\GooBall\extract\textures'
os.makedirs(OUT, exist_ok=True)


def mip_chain_bytes(w, h, bpp_bytes):
    """全 mipmap 链字节数（每级 4bpp 压缩格式按块算的简化版仅用于非压缩）"""
    total = 0
    while w >= 1 and h >= 1:
        total += w * h * bpp_bytes
        w, h = max(w // 2, 1), max(h // 2, 1)
        if w == 1 and h == 1:
            break
    return total


def decode_pixels(data, w, h, fmt):
    """返回 RGBA 像素列表（取最顶层 mip），或 None。"""
    if fmt == 7:                                    # RGB565 BE
        need = w * h * 2
        if len(data) < need:
            return None
        px = []
        for i in range(w * h):
            v = int.from_bytes(data[i*2:i*2+2], 'big')
            px.append((((v >> 11) & 31) * 255 // 31,
                       ((v >> 5) & 63) * 255 // 63,
                       (v & 31) * 255 // 31, 255))
        return px
    if fmt == 3:                                    # RGB24
        need = w * h * 3
        if len(data) < need:
            return None
        return [(data[i*3], data[i*3+1], data[i*3+2], 255) for i in range(w * h)]
    if fmt == 2:                                    # ARGB4444 BE
        need = w * h * 2
        if len(data) < need:
            return None
        px = []
        for i in range(w * h):
            v = int.from_bytes(data[i*2:i*2+2], 'big')
            px.append((((v >> 8) & 15) * 17, ((v >> 4) & 15) * 17,
                       (v & 15) * 17, ((v >> 12) & 15) * 17))
        return px
    if fmt == 1:                                    # Alpha8（+mip链，顶层在前）
        need = w * h
        if len(data) < need:
            return None
        return [(v, v, v, 255) for v in data[:w * h]]
    return None


def main():
    u = Unity1x(os.path.join(D, 'sharedassets.assets'))
    ok, skip_fmt, stream = 0, {}, []
    manifest = []
    for o in u.objects:
        if o.classID != 28:
            continue
        d = u.obj_data(o)
        n = int.from_bytes(d[0:4], 'big')
        if not (0 < n < 100):
            continue
        name = d[4:4 + n].decode('ascii', 'replace')
        p = 4 + n
        w = int.from_bytes(d[p:p+4], 'big')
        h = int.from_bytes(d[p+4:p+8], 'big')
        cisz = int.from_bytes(d[p+8:p+12], 'big')
        fmt = int.from_bytes(d[p+12:p+16], 'big')
        if not (0 < w <= 4096 and 0 < h <= 4096):
            continue
        off = p + 45
        # 该格式的真实存储字节数
        if fmt == 3:
            store = w * h * 3
        elif fmt in (2, 7):
            store = w * h * 2
        elif fmt == 1:
            store = mip_chain_bytes(w, h, 1)
        else:
            store = cisz
        data = d[off:off + store]
        px = decode_pixels(data, w, h, fmt)
        if px is None:
            if off + store > o.size:
                stream.append((name, w, h, fmt, store, o.size - off))
            else:
                skip_fmt[fmt] = skip_fmt.get(fmt, 0) + 1
            continue
        img = Image.new('RGBA', (w, h))
        img.putdata(px)
        safe = name.strip().replace(' ', '_').replace('-', '_') or f'tex_{o.pathID}'
        fp = os.path.join(OUT, f'{safe}_{o.pathID}.png')
        img.save(fp)
        ok += 1
        manifest.append((name, w, h, fmt, 'OK'))
    print(f'提取成功: {ok} 张 -> {OUT}')
    print(f'未支持格式: {skip_fmt}')
    print(f'流式(数据在流洞): {len(stream)}')
    for s in stream[:10]:
        print('  ', s)


if __name__ == '__main__':
    main()
