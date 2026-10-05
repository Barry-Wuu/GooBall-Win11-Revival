#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""统计各关钻石（StarPickup）数量，输出「章节 × 关序号」矩阵。

游戏内 HUD 只显示「已收集 / 当前关总数」中的已收集数，**没有全游戏钻石总数统计**，
本工具把 61 关的逐关数据一次性算出来。

数据来源
  · 关卡表：`docs/evidence/il_all.txt` 里 `MapInfo::SetupLevels` 的 IL。
    注意该方法有 `Application.isPanther` 分支（Mac OS X 10.3 Panther 检测）：
      - Panther 分支（IL_0016~IL_0367）= **完整表，11 章 61 关**（发布版实际使用）
      - 正式版分支（IL_0368~IL_03cd）= 6 关 3 章的演示子集
    场景文件号 = AddLevel 的 index 参数 + 3（level0/1/2 = 标题/章节选择/地图）。
  · 钻石数：`tools/mb_bind_all.json`（由 `bind_all_mb.py` 生成）中
    `script_class == "StarPickup"` 的实例逐关计数。

用法
  python level_diamonds.py            # 打印 Markdown 表格
  python level_diamonds.py --md out.md # 写文件
"""
import os
import re
import sys
import json
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
IL = os.path.join(HERE, "..", "docs", "evidence", "il_all.txt")
MB = os.path.join(HERE, "mb_bind_all.json")


def load_level_table():
    """从 IL 提取 Panther 分支的 (章节, 关卡名, index) 列表"""
    t = open(IL, encoding="utf-8", errors="ignore").read()
    i = t.find("MapInfo::SetupLevels")
    m = re.search(r"\n//// ", t[i + 10:])
    seg = t[i:i + 10 + m.start()] if m else t[i:]

    rows = []
    for ln in seg.splitlines():
        s = ln.strip()
        mm = re.match(r"(IL_[0-9a-f]{4}):\s+(.*)", s)
        if not mm:
            continue
        lab, op = mm.group(1), mm.group(2)
        if op.startswith("ldstr"):
            v = re.match(r'ldstr\s+"(.*)"', op)
            if v:
                rows.append((lab, "str", v.group(1)))
        elif op.startswith("ldc.i4"):
            v = re.match(r"ldc\.i4(?:\.s)?\s+(-?\d+)", op) or re.match(r"ldc\.i4\.(\d+)", op)
            if v:
                rows.append((lab, "int", int(v.group(1))))
        elif "AddLevel" in op or "AddChapter" in op:
            rows.append((lab, "call", "AddChapter" if "AddChapter" in op else "AddLevel"))

    def parse(lo, hi):
        ch = None
        out = []
        pend = pn = None
        for lab, k, v in rows:
            if lab > hi:
                break
            if lab < lo:
                continue
            if k == "str":
                pend = v
            elif k == "int":
                pn = v
            elif k == "call" and pend is not None and pn is not None:
                if v == "AddChapter":
                    ch = pend
                else:
                    out.append((ch, pend, pn))
                pend = pn = None
        return out

    return parse("IL_0016", "IL_0367")


def main():
    table = load_level_table()
    if not os.path.exists(MB):
        print("缺少 %s，请先运行 bind_all_mb.py" % MB)
        return 1
    rows = json.load(open(MB, encoding="utf-8"))
    dia = Counter(r["file"] for r in rows if r["script_class"] == "StarPickup")

    # 按章节分组
    chapters = []
    for ch, name, idx in table:
        if not chapters or chapters[-1][0] != ch:
            chapters.append((ch, []))
        chapters[-1][1].append((name, idx, dia.get("level%d" % (idx + 3), 0)))

    total = sum(n for _, _, n in
                [(c, l, d) for c, lst in chapters for l, _, d in lst])
    out = []
    A = out.append

    A("### 章节 × 关卡 钻石矩阵\n")
    width = max(len(lst) for _, lst in chapters)
    A("| 章节 | " + " | ".join("第%d关" % (i + 1) for i in range(width)) +
      " | 小计 |")
    A("|" + "---|" * (width + 2))
    for ch, lst in chapters:
        cells = [str(n) for _, _, n in lst] + ["—"] * (width - len(lst))
        A("| **%s** | %s | **%d** |" % (ch, " | ".join(cells), sum(n for _, _, n in lst)))
    A("| **合计** | " +
      " | ".join("**%d**" % sum(lst[i][2] for _, lst in chapters if i < len(lst))
                    for i in range(width)) + " | **%d** |" % total)
    A("\n> 共 %d 章 %d 关，钻石合计 **%d** 颗。空白表示该章关卡数不足。\n"
      % (len(chapters), len(table), total))

    A("### 逐关明细\n")
    A("| 章节 | # | 关卡名 | 场景文件 | 钻石 |")
    A("|---|---|---|---|---|")
    n = 0
    for ch, lst in chapters:
        for name, idx, d in lst:
            n += 1
            A("| %s | %d | %s | `level%d` | %d |" % (ch, n, name, idx + 3, d))
    A("")

    text = "\n".join(out)
    if len(sys.argv) == 3 and sys.argv[1] == "--md":
        open(sys.argv[2], "w", encoding="utf-8").write(text)
        print("已写出 %s" % sys.argv[2])
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
