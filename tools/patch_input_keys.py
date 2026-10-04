#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""列出 / 修改 Unity 1.x 的 InputManager（classID 13）键位绑定。

背景
  GooBall 原为 Mac 独占，跳跃按钮 "StateUp" 绑的是 **left cmd**（Mac Command 键）。
  2007 年的 Windows 移植版（archive.org GooBall-Win.zip）发布时**没有重绑**这份配置
  —— Win/Mac 两版 mainData 里 InputManager 逐字节相同，于是 Windows 上跳跃永远触发不了
  （Windows 没有 Command 键），而游戏内提示仍写着「按 cmd 跳跃」。

用法
  python patch_input_keys.py <mainData路径>                     # 只列出
  python patch_input_keys.py <mainData路径> StateUp space       # 把 StateUp 的正键改成 space
  python patch_input_keys.py <mainData路径> StateDown "left shift"

二进制布局（Unity 1.x SerializedFile v5，全大端，classID 13）
  [u32 axisCount]
  每轴: [str m_Name][str descriptiveName][str descriptiveNegativeName]
        [str negativeButton][str positiveButton]
        [str altNegativeButton][str altPositiveButton]
        [f32 gravity][f32 dead][f32 sensitivity]
        [u8 snap][u8 invert]
        [u32 type][u32 axis][u32 joyNum]
  str = [u32 字节数][bytes]，**不做 4 字节对齐**（Unity 1.x 与后续版本不同）

改写的零重排技巧
  键名变短会缩短对象数据，若直接写入会错位后续所有对象。做法：
  中间紧凑替换 → 对象**末尾**补等量 0x00 → size 不变 → offset/header/对象表全不用动。
  （曾踩坑：把 padding 补在字符串后面会污染下一个字段的长度前缀。）
"""
import sys
import shutil
import struct

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from unity1x import Unity1x  # noqa: E402


def read_str(d, p):
    L = int.from_bytes(d[p:p + 4], "big")
    return d[p + 4:p + 4 + L].decode("ascii", "replace"), p + 4 + L


def parse(d):
    """返回 (轴列表, 每个轴的正/负键在数据内的字节偏移)"""
    p = 0
    n = int.from_bytes(d[0:4], "big")
    p = 4
    axes = []
    for _ in range(n):
        rec = {}
        for key in ("name", "desc", "descNeg"):
            rec[key], p = read_str(d, p)
        rec["neg_off"] = p + 4          # 指向 negativeButton 的字节区
        rec["neg"], p = read_str(d, p)
        rec["pos_off"] = p + 4          # 指向 positiveButton 的字节区
        rec["pos"], p = read_str(d, p)
        rec["altNeg"], p = read_str(d, p)
        rec["altPos"], p = read_str(d, p)
        p += 12 + 2                     # gravity/dead/sensitivity + snap/invert
        rec["type"] = int.from_bytes(d[p:p + 4], "big")
        p += 12                         # type/axis/joyNum
        axes.append(rec)
    return axes, n


def enc(s):
    b = s.encode("ascii")
    return len(b).to_bytes(4, "big") + b


def main():
    path = sys.argv[1]
    u = Unity1x(path)
    objs = [o for o in u.objects if o.classID == 13]
    if not objs:
        print("该文件没有 InputManager (classID 13)")
        return 1
    o = objs[0]
    d = bytearray(u.obj_data(o))
    axes, n = parse(d)

    if len(sys.argv) >= 4:
        axis_name, newkey = sys.argv[2], sys.argv[3]
        tgt = [a for a in axes if a["name"] == axis_name]
        if not tgt:
            print("找不到轴:", axis_name, "现有:", [a["name"] for a in axes])
            return 1
        a = tgt[0]
        # 优先替换非空的那一个（跳跃等动作只绑了 positiveButton）
        off = a["pos_off"] if a["pos"] else a["neg_off"]
        old = a["pos"] if a["pos"] else a["neg"]
        oldb = enc(old)
        newb = enc(newkey)
        assert d[off - 4:off - 4 + len(oldb)] == oldb, "偏移校验失败"
        d[off - 4:off - 4 + len(oldb)] = newb
        gap = len(oldb) - len(newb)
        d += b"\x00" * gap              # 末尾补零，保持对象 size 不变
        assert len(d) == o.size
        shutil.copy(path, path + ".bak")
        raw = bytearray(u.raw)
        raw[o.offset:o.offset + o.size] = bytes(d)
        open(path, "wb").write(bytes(raw))
        print("已改: %s  %r -> %r   (备份 %s.bak)" % (axis_name, old, newkey, path))
        return 0

    print("%s  轴数=%d  InputManager @%d size=%d" % (path, n, o.offset, o.size))
    print("%-16s %-12s %-12s %-10s %-10s %-5s" %
          ("Name", "negBtn", "posBtn", "altNeg", "altPos", "type"))
    for a in axes:
        print("%-16s %-12s %-12s %-10s %-10s %-5d" %
              (a["name"], a["neg"], a["pos"], a["altNeg"], a["altPos"], a["type"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
