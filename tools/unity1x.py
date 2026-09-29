#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""unity1x.py —— Unity 1.x (SerializedFile version 5) 解析器 · 终版（含 sharedassets）
目标：GooBall (2005, Unity 1.x beta, Mac/PPC)

文件布局
  header 16B 大端:  metadataSize(u32) fileSize(u32) version(u32)=5 dataOffset(u32)
  objectData     : [16, fileSize-metadataSize)
  metadata       : [fileSize-metadataSize, fileSize)
      int32 numBaseClasses
      TypeTree[numBaseClasses]   (文本型, null 结尾字符串流)
      int32 headField            (关卡=对象数; sharedassets=146, 语义待考)
      ObjectInfo[?]              ← 20B/条, 逐行解析至 classID 无效
      int32 numExternals
      FileIdentifier[numExternals]

ObjectInfo (20B) —— 实测定案（69 关全平铺自洽 + sharedassets 2962 行数据实证 92%）：
  +0      u8   pathID 低字节
  +1..+4  u32  大端 offset          ← 三文件统一（关卡数据区 <64KB 时高 2 字节恒 0）
  +5..+6  （未定，sharedassets 中呈 0/4 等值，疑似流标志）
  +7..+8  u16  大端 size
  +9..+11      （MonoBehaviour 行呈 0xFFFFFFxx 形态）
  +12..13 u16  小端 typeID  (类型树索引)
  +14..15 u16  小端 classID (Unity class ID; MonoBehaviour=114 时不等于 typeID)
  +16..18      0
  +19     u8   pathID 高字节        ← sharedassets 2962 对象 >255 实证：每 256 行进位

关键事实
  · 关卡文件（level0..68）+ mainData：数据区严格平铺（offset == size 累加+8 对齐）。
  · sharedassets.assets（91.5MB）：**不平铺**——对象 size 总和 15.9MB / 数据区 91.3MB，
    75MB 洞为流式大资产（贴图/音频本体，由对象内部字段引用），
    是现代 Unity .resS 流方案的前身。
  · 末对象 offset+size == metaStart（sharedassets 与关卡均吻合）。
"""
import struct, os

HEADER = 16
STRIDE = 20


def align8(x):
    return (x + 7) & ~7


class ObjectInfo:
    __slots__ = ("pathID", "offset", "size", "typeID", "classID", "pad56")

    def __init__(self, pathID, offset, size, typeID, classID, pad56):
        self.pathID, self.offset, self.size = pathID, offset, size
        self.typeID, self.classID, self.pad56 = typeID, classID, pad56

    def __repr__(self):
        return (f"<obj pid={self.pathID} @{self.offset:#x} size={self.size} "
                f"type={self.typeID} class={self.classID}>")


class Unity1x:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.raw = f.read()
        (self.metadata_size, self.file_size,
         self.version, self.data_offset) = struct.unpack(">IIII", self.raw[:HEADER])
        self.meta_start = self.file_size - self.metadata_size
        self.meta = self.raw[self.meta_start:]
        self.objects = []
        self.table_off = None
        self.head_field = None
        self._parse_table()

    # ---------- 对象表 ----------
    def _parse_table(self):
        """收集候选起点，各自解析取最优（优先末对象精确触底，其次行数多）。"""
        best, best_key = None, (-1, -1)
        for st in self._candidates():
            objs = self._parse_from(st)
            if not objs:
                continue
            last = objs[-1]
            key = (1 if last.offset + last.size == self.meta_start else 0, len(objs))
            if key > best_key:
                best, best_key = (st, objs), key
        if best:
            self.table_off, self.objects = best
            self.head_field = struct.unpack("<I", self.meta[self.table_off - 4:self.table_off])[0] \
                if self.table_off >= 4 else None

    def _candidates(self):
        buf, n = self.meta, len(self.meta)
        out = []
        for s in range(0, n - STRIDE * 4):
            ok1 = True   # 起始 pathID 低字节 1,2,3,4
            ok0 = True   # 起始 pathID 低字节 0,1,2,3（容错「表以 pathID 0 开头」）
            for k in range(4):
                p = s + k * STRIDE
                if buf[p] != k + 1 or buf[p + 1] or buf[p + 19] or \
                   buf[p + 16:p + 20] != b"\x00\x00\x00\x00":
                    ok1 = False
                if buf[p] != k or buf[p + 1] or buf[p + 19] or \
                   buf[p + 16:p + 20] != b"\x00\x00\x00\x00":
                    ok0 = False
            if ok1 or ok0:
                out.append(s)
        return out

    def _parse_from(self, st):
        objs, cur = [], HEADER
        flat = True                      # 是否保持平铺（关卡特征）
        while st + (len(objs) + 1) * STRIDE <= len(self.meta):
            p = st + len(objs) * STRIDE
            b = self.meta[p:p + STRIDE]
            off = int.from_bytes(b[1:5], "big")        # u32 大端
            sz = (b[7] << 8) | b[8]                    # u16 大端
            t1 = int.from_bytes(b[12:14], "little")
            t2 = int.from_bytes(b[14:16], "little")
            if t2 == 0 or t2 > 4096 or off < cur or off >= self.meta_start:
                break
            if off != cur:
                flat = False
            pid = b[0] | (b[19] << 8)
            objs.append(ObjectInfo(pid, off, sz, t1, t2, b[5:7].hex()))
            cur = align8(off + sz) if flat else off + sz
        # 平铺性差（大量跳跃）时仍接受（sharedassets 特征），由调用方按末位择优
        return objs

    # ---------- 取数据 ----------
    def obj_data(self, o):
        if isinstance(o, int):
            o = self.objects[o]
        return self.raw[o.offset:o.offset + o.size]

    def by_class(self, class_id):
        return [i for i, o in enumerate(self.objects) if o.classID == class_id]

    def stats(self):
        from collections import Counter
        return Counter(o.classID for o in self.objects)

    def check(self):
        """返回 (是否平铺自洽且首尾吻合, 末对象原始末位, meta_start)"""
        if not self.objects:
            return False, HEADER, self.meta_start
        cur = HEADER
        for o in self.objects:
            if o.offset != cur:
                # 非平铺：只要求单调 + 末位吻合
                last = self.objects[-1]
                tail_ok = last.offset + last.size == self.meta_start
                return tail_ok, last.offset + last.size, self.meta_start
            cur = align8(o.offset + o.size)
        last = self.objects[-1]
        return True, last.offset + last.size, self.meta_start

    def gap_report(self):
        """统计各对象间的空隙（>7 字节 = 流式洞）"""
        out = []
        for prev, o in zip(self.objects, self.objects[1:]):
            gap = o.offset - (prev.offset + prev.size)
            if gap > 7:
                out.append((prev, o, gap))
        return out


if __name__ == "__main__":
    D = r"D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents\Data"
    files = [f"level{i}" for i in range(69)] + ["mainData", "sharedassets.assets"]
    bad = []
    for fn in files:
        u = Unity1x(os.path.join(D, fn))
        ok, tail, ms = u.check()
        status = "OK " if ok else "FAIL"
        if not ok:
            bad.append(fn)
        extra = ""
        if fn == "sharedassets.assets":
            gaps = u.gap_report()
            extra = f" 流洞数={len(gaps)} 洞总量={sum(g[2] for g in gaps):,}B"
        print(f"{fn:<22}{status} rows={len(u.objects):>5} 末位={tail:,} metaStart={ms:,}{extra}")
    print(f"\n自检：{len(files)-len(bad)}/{len(files)} 通过" + (f"  失败: {bad}" if bad else ""))
