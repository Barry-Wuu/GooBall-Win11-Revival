#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GooBall 托管宿主：游戏逻辑可达的 icall 传递闭包

从游戏逻辑（docs/evidence/il_all.txt）引用的 UnityEngine 成员出发，
沿 UnityEngine.dll 的托管包装逐层向下 BFS，直到触达 icall 叶子。
闭包内的 icall = 宿主必须逐个重写的引擎核规模；闭包外的 icall 游戏不碰，可后置。

依赖 tools/host_feasibility.py 里的 CLI 元数据解析器（Asm 类）。
输出写入 docs/evidence/spike_icall_closure.txt。
"""
import os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from host_feasibility import Asm          # noqa: E402

BASE = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents'
UE   = os.path.join(BASE, 'Resources', 'UnityEngine.dll')
IL   = r'D:\GooBall\repo_git\docs\evidence\il_all.txt'
OUT  = r'D:\GooBall\repo_git\docs\evidence\spike_icall_closure.txt'
LIST = r'D:\GooBall\repo_git\docs\evidence\spike_icall_closure_list.txt'

NORM = lambda s: re.sub(r'<.*>$', '', s)   # 去掉泛型/签名后缀，重载归一

# 会跟随 4 字节元数据 token 的 IL 操作码
TOKEN_OPS = (set(range(0x28, 0x2B)) | {0x6F,0x73,0x7B,0x7E,0x7C,0x80,0x74,0x75,0x8C,0x8D,
              0xA5,0x71,0x81,0x8F,0x72,0x7A,0x79,0xC2,0xC6,0xD0,0x76,0x77,0x78,0x8A,0xFE})


def load_methods(a):
    """(TypeName, MethodBaseName) -> (isIcall, rva)；同时返回 MethodDef 行号映射"""
    mdef, methods = {}, {}
    for i in range(a.n(2)):
        m0 = a.cell(2, i, 12)
        m1 = a.cell(2, i + 1, 12) if i + 1 < a.n(2) else a.n(6) + 1
        tn = a.s(2, i, 4)
        for k in range(m0, min(m1, a.n(6) + 1)):
            nm = NORM(a.s(6, k, 8))
            ic = bool(a.cell(6, k, 4) & 0x1000)     # MethodImplAttributes.InternalCall
            rva = a.cell(6, k, 0)
            mdef[k + 1] = (tn, nm, ic, rva)
            methods.setdefault((tn, nm), (ic, rva))
    return methods, mdef


def make_body_refs(a, mdef):
    def mr_target(i):
        cls = a.cell(10, i, 0)
        tag, idx = cls & 7, cls >> 3
        nm = NORM(a.s(10, i, 2))
        return (a.s(1, idx - 1, 2), nm) if tag == 1 else None   # tag=1 -> TypeRef

    def body_refs(rva):
        """扫描一个方法体，返回它调用的 (TypeName, MemberName) 集合"""
        if not rva:
            return set()
        try:
            off = a.r2o(rva)
        except ValueError:
            return set()
        b0 = a.d[off]
        if (b0 & 3) == 0x2:                       # tiny 头
            size, p = b0 >> 2, off + 1
        elif (b0 & 3) == 0x3:                     # fat 头
            fl = int.from_bytes(a.d[off:off+2], 'little')
            p = off + ((fl >> 12) * 4)
            size = int.from_bytes(a.d[off+4:off+8], 'little')
        else:
            return set()
        out, q, end = set(), p, p + size
        while q < end and q < len(a.d) - 5:
            if a.d[q] in TOKEN_OPS:
                tok = int.from_bytes(a.d[q+1:q+5], 'little')
                top = tok >> 24
                if top == 0x0A:                   # MemberRef
                    mi = tok & 0xFFFFFF
                    if 1 <= mi <= a.n(10):
                        t = mr_target(mi - 1)
                        if t:
                            out.add(t)
                elif top == 0x06:                 # MethodDef = 同类型内调用
                    mi = tok & 0xFFFFFF
                    if mi in mdef:
                        out.add((mdef[mi][0], mdef[mi][1]))
            q += 1
        return out
    return body_refs


def main():
    ue = Asm(UE)
    methods, mdef = load_methods(ue)
    body_refs = make_body_refs(ue, mdef)

    il = open(IL, encoding='utf-8', errors='ignore').read()
    game = {(t, NORM(m)) for t, m in re.findall(
        r'(?:call|callvirt|newobj|ldsfld|ldfld|stsfld)\s+'
        r'UnityEngine\.([A-Za-z0-9_]+)::([A-Za-z0-9_<>.$]+)', il)}

    hit = [k for k in game if k in methods]
    total_icall = sum(1 for i in range(ue.n(6)) if ue.cell(6, i, 4) & 0x1000)

    seen, icalls, queue = set(hit), set(), list(hit)
    depth = {k: 0 for k in hit}
    while queue:
        nxt = []
        for k in queue:
            is_icall, rva = methods[k]
            if is_icall:
                icalls.add(k)
                continue
            for t in body_refs(rva):
                if t in methods and t not in seen:
                    seen.add(t)
                    depth[t] = depth[k] + 1
                    nxt.append(t)
        queue = nxt

    by = defaultdict(list)
    for t, m in sorted(icalls):
        by[t].append(m)

    lines = []
    P = lines.append
    P('=' * 78)
    P(' GooBall 托管宿主：游戏逻辑可达的 icall 传递闭包')
    P('=' * 78)
    P('')
    P('游戏逻辑引用的 UnityEngine 成员(去重归一) : %d' % len(game))
    P('  在 UnityEngine.dll 找到定义            : %d' % len(hit))
    P('')
    P('传递闭包触达 UnityEngine 方法             : %d  (最大调用深度 %d)'
      % (len(seen), max(depth.values()) if depth else 0))
    P('  其中 icall —— 宿主必须逐个重写          : %d' % len(icalls))
    P('  游戏不可达的 icall —— 可后置            : %d / %d' % (total_icall - len(icalls), total_icall))
    P('')
    P('== icall 工作面分布 ==')
    for t in sorted(by, key=lambda x: -len(by[x])):
        names = sorted(by[t])
        P('  %-26s %3d   %s' % (t, len(names), ', '.join(names[:6]) + (' ...' if len(names) > 6 else '')))
    P('')
    P('== 完整 icall 清单（%d 个）==' % len(icalls))
    for t in sorted(by):
        for m in sorted(by[t]):
            P('  %s::%s' % (t, m))

    text = '\n'.join(lines) + '\n'
    print(text)
    open(OUT, 'w', encoding='utf-8').write(text)
    open(LIST, 'w', encoding='utf-8').write(
        '\n'.join('%s\t%s' % (t, ', '.join(sorted(by[t]))) for t in sorted(by)))
    print('写出 %s 与 %s' % (OUT, LIST))


if __name__ == '__main__':
    main()
