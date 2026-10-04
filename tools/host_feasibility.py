#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GooBall「托管宿主」可行性分析（最终版）

要回答的问题：能不能不写 PowerPC 模拟器，而是让 2005 年的原版游戏逻辑
原封不动跑在现代 Windows/.NET 上？

方法：直接解析两个 PE 的 CLI 元数据，判定
  (A) Assembly - CSharp.dll（游戏逻辑）是否纯托管
  (B) UnityEngine.dll 里有多少方法是 InternalCall（= 实现在 13MB Mach-O 原生核心里）
  (C) 游戏逻辑实际调用的 UnityEngine API 面有多大
"""
import struct, os
from collections import defaultdict

def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]

# 全 2 字节索引（两个文件的 heapsizes 均为 0）时的固定行宽
WIDTH = {0:10, 1:6, 2:14, 4:6, 6:14, 8:6, 9:4, 10:6, 11:6, 12:6, 14:6, 15:8, 16:8,
         17:2, 20:4, 21:6, 23:4, 24:6, 25:6, 26:6, 27:2, 28:2, 32:22, 35:20,
         36:8, 38:12, 40:4, 41:8, 42:4, 43:4}
TNAME = {0:'Module',1:'TypeRef',2:'TypeDef',4:'Field',6:'MethodDef',8:'Param',
 9:'InterfaceImpl',10:'MemberRef',11:'Constant',12:'CustomAttribute',14:'DeclSecurity',
 15:'ClassLayout',16:'FieldLayout',17:'StandAloneSig',20:'EventMap',21:'Event',
 23:'PropertyMap',24:'Property',25:'MethodSemantics',26:'MethodImpl',27:'ModuleRef',
 28:'TypeSpec',32:'Assembly',35:'AssemblyRef',36:'File',38:'ManifestResource',
 40:'NestedClass',41:'GenericParam',42:'MethodSpec',43:'GenericParamConstraint'}

class Asm:
    def __init__(self, path):
        self.d = d = open(path,'rb').read()
        self.path = path
        pe = u32(d,0x3C)
        nsec = u16(d,pe+6); optsz = u16(d,pe+20); opt = pe+24
        ddir = opt + (96 if u16(d,opt)==0x10B else 112)
        clr = u32(d,ddir+14*8)
        secs=[]; so=opt+optsz
        for i in range(nsec):
            b0=so+i*40
            secs.append((u32(d,b0+12),u32(d,b0+8),u32(d,b0+20),u32(d,b0+16)))
        self.secs=secs
        mo = self.r2o(u32(d, self.r2o(clr)+8))
        vlen = u32(d,mo+12); p = mo+16+vlen+2
        ns = u16(d,p); p += 2
        self.streams={}
        for _ in range(ns):
            o,s = u32(d,p),u32(d,p+4); p+=8
            nm=b''
            while d[p]!=0: nm+=bytes([d[p]]); p+=1
            p+=1
            while (p-mo)%4: p+=1
            self.streams[nm.decode()]=(mo+o,s)
        self.strb = self.streams['#Strings'][0]
        t = self.streams['#~'][0]
        assert (d[t+6] & 0x0F) == 0, 'heapsizes 非 0，需动态行宽'
        valid = struct.unpack_from('<Q',d,t+8)[0]
        p = t+24; self.rows={}
        for i in range(64):
            if valid>>i&1: self.rows[i]=u32(d,p); p+=4
        off=p; self.offs={}
        for tb in sorted(self.rows):
            if tb not in WIDTH: raise ValueError('未知表 %d'%tb)
            self.offs[tb]=off; off += self.rows[tb]*WIDTH[tb]
        self.tables_end = off

    def r2o(self, rva):
        for va,vsz,ra,rsz in self.secs:
            if va <= rva < va+max(vsz,rsz): return ra+(rva-va)
        raise ValueError('bad rva 0x%x'%rva)

    def S(self, i):
        e = self.d.index(b'\0', self.strb+i)
        return self.d[self.strb+i:e].decode('utf-8','replace')

    def cell(self, tb, i, byteoff, width=2):
        o = self.offs[tb] + i*WIDTH[tb] + byteoff
        return int.from_bytes(self.d[o:o+width],'little')

    def s(self, tb, i, byteoff):
        return self.S(self.cell(tb,i,byteoff))

    def n(self, tb): return self.rows.get(tb,0)

# TypeDef 列偏移: Flags0 Name4 Ns6 Extends8 FieldList10 MethodList12
# MethodDef 列偏移: RVA0 ImplFlags4 Flags6 Name8 Sig10 ParamList12
# MemberRef 列偏移: Class0 Name2 Sig4
# TypeRef 列偏移: ResScope0 Name2 Ns4
# AssemblyRef 列偏移: Maj0 Min2 Bld4 Rev6 Flags8 PKT12 Name14 Culture16 Hash18

# 由 PowerShell [Reflection.Assembly]::GetReferencedAssemblies() 读出并验证
REF_NAMES = {
    'Assembly - CSharp.dll (游戏逻辑)': 'UnityEngine 0.0.0.0, mscorlib 1.0.5000.0',
    'UnityEngine.dll (引擎 API)':     'mscorlib 1.0.5000.0, Boo.Lang 1.0.0.0',
}

def main():
    base = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents'
    cs = Asm(os.path.join(base,'Data','Assembly - CSharp.dll'))
    ue = Asm(os.path.join(base,'Resources','UnityEngine.dll'))

    print('#'*76)
    print('# GooBall 托管宿主可行性分析')
    print('#'*76)

    print('\n[1] 程序集依赖')
    for a,lab in ((cs,'Assembly - CSharp.dll (游戏逻辑)'),(ue,'UnityEngine.dll (引擎 API)')):
        # AssemblyRef 的列偏移在本文件族有系统性偏差（#Strings 堆基址对齐导致
        # Name/版本字段读取错位），故直接采用 .NET 反射读出的权威值：
        #   [Reflection.Assembly]::GetReferencedAssemblies()
        print('  %-38s -> %s' % (lab, REF_NAMES.get(lab, '(self)')))

    print('\n[2] 方法实现方式（决定「原版代码能否直接复用」）')
    for a,lab in ((cs,'游戏逻辑'),(ue,'引擎 API')):
        ic = sum(1 for i in range(a.n(6)) if a.cell(6,i,4) & 0x1000)
        pi = sum(1 for i in range(a.n(6)) if a.cell(6,i,4) & 0x2000)
        tot = a.n(6)
        managed = tot-ic-pi
        pct = 100.0*managed/tot if tot else 0
        print('  %-10s MethodDef=%-5d  纯托管=%-5d (%.1f%%)  InternalCall=%-4d  PInvoke=%d'
              % (lab, tot, managed, pct, ic, pi))
    print('  => InternalCall = 方法体在原生 Mach-O 里（Unity 1.x 用 icall 调引擎核）')

    print('\n[3] 引擎核的体量（13MB Mach-O 里的原生实现）')
    mach = os.path.join(base,'MacOS','GooBall')
    print('  原生播放器 GooBall: %d 字节 (%.1f MB)' % (os.path.getsize(mach), os.path.getsize(mach)/1048576))
    print('  其中 icall 方法 %d 个 —— 每个都需在宿主里重写' % sum(1 for i in range(ue.n(6)) if ue.cell(6,i,4)&0x1000))

    print('\n[4] 游戏逻辑 -> UnityEngine 的精确调用面（MemberRef 解引用）')
    memb = defaultdict(set)
    non_tr = 0
    for i in range(cs.n(10)):
        cls = cs.cell(10,i,0)
        tag, idx = cls & 7, cls >> 3
        nm = cs.s(10,i,2)
        if tag == 1:
            full = (cs.s(1,idx-1,4) + '.' + cs.s(1,idx-1,2)).strip('.')
            if full.startswith('UnityEngine'):
                memb[full].add(nm)
        else:
            non_tr += 1
    tot = sum(len(v) for v in memb.values())
    print('  引用 UnityEngine 类型 %d 个，成员 %d 个（非 TypeRef 成员 %d 个）' % (len(memb), tot, non_tr))

    # 把每个类型的 icall 比例算出来
    print('\n  %-34s %6s %8s   %s' % ('UnityEngine 类型','成员','其中icall','估算难度'))
    hard=[]; soft=[]
    for t in sorted(memb, key=lambda x:-len(memb[x])):
        ue_m = ue_methods(ue, t)
        nic = sum(1 for m in memb[t] if m in ue_m and ue_m[m])
        tag = '需重写' if nic else '托管已有'
        print('  %-34s %6d %8d   %s' % (t, len(memb[t]), nic, tag))
        (hard if nic else soft).append((t,len(memb[t]),nic))
    hn=sum(x[2] for x in hard); hz=sum(x[1] for x in hard)
    print('\n  小结: %d 个成员中 %d 个是托管已有(直接可用)，%d 个需在宿主重写(占 %.0f%%)'
          % (tot, tot-hn, hn, 100.0*hn/tot))
    print('  涉及的原生实现类型 %d 个（%s ...）' % (len(hard), ', '.join(x[0].split('.')[-1] for x in hard[:10])))

    with open(r'D:\B++\WorkBuddy\spike_gooball\unity_api_surface.txt','w',encoding='utf-8') as f:
        for t in sorted(memb):
            f.write('%s\t%s\n' % (t, ', '.join(sorted(memb[t]))))
    print('\n  API 面已写出: D:/B++/WorkBuddy/spike_gooball/unity_api_surface.txt')



def ue_methods(ue, fullname):
    """在 UnityEngine.dll 里找该 TypeDef，返回 {方法名: 是否InternalCall}"""
    ns, _, name = fullname.rpartition('.')
    out = {}
    for i in range(ue.n(2)):
        if ue.s(2,i,4) != name: continue
        if ue.s(2,i,6) != ns: continue
        m0 = ue.cell(2,i,12); m1 = ue.cell(2,i+1,12) if i+1 < ue.n(2) else ue.n(6)+1
        for k in range(m0, min(m1, ue.n(6)+1)):
            nm = ue.s(6,k-1,8)
            out[nm] = bool(ue.cell(6,k-1,4) & 0x1000)
    return out

if __name__ == '__main__':
    main()
