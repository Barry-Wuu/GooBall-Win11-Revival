#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析 .NET CLI 元数据（PE -> CLI header -> #~ 流 -> 表），按 ECMA-335 列模式计算行宽。
用于判断「原版 Unity 1.x 托管代码能否搬到现代 .NET 上跑」。

关键问题：
  1) UnityEngine.dll 的方法是 InternalCall（原生实现，藏在 13MB Mach-O 里）还是纯托管？
  2) Assembly - CSharp.dll 是纯 IL 吗？引用哪些程序集？
  3) 游戏逻辑实际调用 UnityEngine 的哪些类型/成员（= 需要重写的引擎 API 面）
"""
import struct, os
from collections import Counter, defaultdict

def u8(b,o):  return b[o]
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]

# (表号, 列定义)；列定义: (名字, 宽度类型)
# 宽度类型: 'u16' 'u32' 'u8' | ('str',) | ('blob',) | ('guid',) | ('idx', 表号) | ('ci', tagbits, [表...])
SCHEMA = {
 0 : [('Generation','u16'),('Name','str'),('Mvid','guid'),('EncId','guid'),('EncBaseId','guid')],
 1 : [('ResolutionScope','ci',2,[0,26,35,1]),('Name','str'),('Namespace','str')],
 2 : [('Flags','u32'),('Name','str'),('Namespace','str'),('Extends','ci',2,[2,1,28]),
      ('FieldList','idx',4),('MethodList','idx',6)],
 4 : [('Flags','u16'),('Name','str'),('Signature','blob')],
 6 : [('RVA','u32'),('ImplFlags','u16'),('Flags','u16'),('Name','str'),('Signature','blob'),('ParamList','idx',8)],
 8 : [('Flags','u16'),('Sequence','u16'),('Name','str')],
 9 : [('Class','idx',2),('Interface','ci',2,[2,1,28])],
 10: [('Class','ci',3,[2,1,27,6,28]),('Name','str'),('Signature','blob')],
 11: [('Type','u8'),('Padding','u8'),('Parent','ci',2,[4,8,24]),('Value','blob')],
 12: [('Parent','ci',5,[6,4,1,2,8,9,10,0,14,17,26,27,32,35,38,23,21,20,42]),
      ('Type','ci',3,[None,None,6,10]),('Value','blob')],
 14: [('Action','u16'),('Parent','ci',2,[2,6,32]),('PermissionSet','blob')],
 15: [('PackingSize','u16'),('ClassSize','u32'),('Parent','idx',2)],
 16: [('Offset','u32'),('Field','idx',4)],
 17: [('Signature','blob')],
 20: [('Parent','idx',2),('EventList','idx',21)],
 21: [('EventFlags','u16'),('Name','str'),('EventType','ci',2,[2,1,28])],
 23: [('Parent','idx',2),('PropertyList','idx',24)],
 24: [('Flags','u16'),('Name','str'),('Type','blob')],
 25: [('Semantics','u16'),('Method','idx',6),('Association','ci',1,[21,24])],
 26: [('Class','idx',2),('MethodBody','ci',1,[6,10]),('MethodDeclaration','ci',1,[6,10])],
 27: [('Name','str')],
 28: [('Signature','blob')],
 32: [('HashAlgId','u32'),('Major','u16'),('Minor','u16'),('Build','u16'),('Rev','u16'),
      ('Flags','u32'),('PublicKey','blob'),('Name','str'),('Culture','str')],
 35: [('Major','u16'),('Minor','u16'),('Build','u16'),('Rev','u16'),('Flags','u32'),
      ('PublicKeyOrToken','blob'),('Name','str'),('Culture','str'),('HashValue','blob')],
 36: [('Flags','u32'),('Name','str'),('HashValue','blob')],
 38: [('Offset','u32'),('Flags','u32'),('Name','str'),('Implementation','ci',2,[38,35])],
 40: [('NestedClass','idx',2),('EnclosingClass','idx',2)],
 41: [('Number','u16'),('Flags','u16'),('Owner','ci',1,[2,6]),('Name','str')],
 42: [('Method','ci',1,[6,10]),('Instantiation','blob')],
 43: [('Owner','idx',41),('Constraint','ci',2,[2,1,28])],
}
TNAME = {0:'Module',1:'TypeRef',2:'TypeDef',4:'Field',6:'MethodDef',8:'Param',9:'InterfaceImpl',
 10:'MemberRef',11:'Constant',12:'CustomAttribute',14:'DeclSecurity',15:'ClassLayout',
 16:'FieldLayout',17:'StandAloneSig',20:'EventMap',21:'Event',23:'PropertyMap',24:'Property',
 25:'MethodSemantics',26:'MethodImpl',27:'ModuleRef',28:'TypeSpec',32:'Assembly',35:'AssemblyRef',
 36:'File',38:'ManifestResource',40:'NestedClass',41:'GenericParam',42:'MethodSpec',
 43:'GenericParamConstraint'}


class CLI:
    def __init__(self, path):
        self.d = d = open(path,'rb').read()
        self.path = path
        pe = u32(d,0x3C)
        nsec = u16(d,pe+6); optsz = u16(d,pe+20); opt = pe+24
        ddir = opt + (96 if u16(d,opt)==0x10B else 112)
        self.clr_rva = u32(d,ddir+14*8)
        secs = []
        so = opt+optsz
        for i in range(nsec):
            b0 = so+i*40
            secs.append((u32(d,b0+12), u32(d,b0+8), u32(d,b0+20), u32(d,b0+16)))
        self.secs = secs
        self.w = {}

    def rva2off(self, rva):
        for va,vsz,ra,rsz in self.secs:
            if va <= rva < va+max(vsz,rsz): return ra+(rva-va)
        raise ValueError('bad rva 0x%x'%rva)

    def W(self, col):
        # col = (name, kind, *extra)
        kind = col[1]
        if kind == 'str':  return 4 if self.str_wide else 2
        if kind == 'blob': return 4 if self.blob_wide else 2
        if kind == 'guid': return 4 if self.guid_wide else 2
        if kind == 'idx':  return 4 if self.rows.get(col[2],0) >= 0x10000 else 2
        if kind == 'ci':
            maxrows = max((self.rows.get(t,0) for t in col[3] if t), default=0)
            return 4 if (maxrows << col[2]) >= 0x10000 else 2
        return {'u8':1,'u16':2,'u32':4}[kind]

    def parse(self):
        d = self.d
        co = self.rva2off(self.clr_rva)
        mo = self.rva2off(u32(d,co+8))
        assert d[mo:mo+4]==b'BSJB', 'no BSJB'
        vlen = u32(d,mo+12)
        p = mo+16+vlen+2
        ns = u16(d,p); p += 2
        self.streams = {}
        for _ in range(ns):
            off,size = u32(d,p),u32(d,p+4); p += 8
            nm=b''
            while d[p]!=0: nm+=bytes([d[p]]); p+=1
            p+=1
            while (p-mo)%4: p+=1
            self.streams[nm.decode('ascii')] = (mo+off, size)
        self.strings = self.streams.get('#Strings',(0,0))[0]
        self.blob    = self.streams.get('#Blob',(0,0))[0]
        self.guid    = self.streams.get('#GUID',(0,0))[0]
        q = self.streams['#~'][0]
        self.str_wide = bool(d[q+6]&1); self.guid_wide = bool(d[q+6]&2); self.blob_wide = bool(d[q+6]&4)
        valid = struct.unpack_from('<Q',d,q+8)[0]
        p = q+24
        self.rows = {}
        for i in range(64):
            if valid>>i&1: self.rows[i]=u32(d,p); p+=4
        self.offsets = {}
        self.roww = {}
        for t in range(64):
            n = self.rows.get(t,0)
            if not n: continue
            cols = SCHEMA.get(t)
            if cols is None: break
            self.offsets[t]=p
            self.roww[t]=sum(self.W(c) for c in cols)
            p += n*self.roww[t]
        self.colw = {t:[self.W(c) for c in SCHEMA[t]] for t in self.offsets}

    def s(self, idx):
        e = self.d.index(b'\0', self.strings+idx)
        return self.d[self.strings+idx:e].decode('utf-8','replace')

    def nrows(self,t): return self.rows.get(t,0)

    def cell(self, t, i, colname):
        cols = SCHEMA[t]
        o = self.offsets[t] + i*self.roww[t]
        x = o
        for cn, k in cols:
            wdt = self.W((cn,k)+tuple(cols[[c[0] for c in cols].index(cn)][2:]))
            v = int.from_bytes(self.d[x:x+wdt],'little')
            x += wdt
            if cn == colname: return v
        raise KeyError(colname)

    def field(self, t, i, colname):
        k = dict((c[0],c[1]) for c in SCHEMA[t])[colname]
        v = self.cell(t,i,colname)
        if k == 'str': return self.s(v)
        if k == 'ci':
            tag = v & ((1<<k[1])-1); idx = v >> k[1]
            return tag, idx
        return v

def analyze(path, label):
    print('='*74)
    print('%s   %s   (%d 字节)' % (label, os.path.basename(path), os.path.getsize(path)))
    print('='*74)
    c = CLI(path); c.parse()
    print('程序集引用:')
    for i in range(c.nrows(35)):
        print('   %-18s %s.%s.%s.%s' % (c.field(35,i,'Name'), c.field(35,i,'Major'),
              c.field(35,i,'Minor'), c.field(35,i,'Build'), c.field(35,i,'Rev')))
    print('表: TypeDef=%d TypeRef=%d MethodDef=%d MemberRef=%d Field=%d' %
          (c.nrows(2),c.nrows(1),c.nrows(6),c.nrows(10),c.nrows(4)))
    ic=pi=0; n=c.nrows(6)
    for i in range(n):
        f = c.field(6,i,'ImplFlags')
        if f & 0x0001: ic+=1
        if f & 0x2000: pi+=1
    print('MethodDef %d 个: InternalCall=%d  PinvokeImpl=%d  纯托管/运行时=%d'
          % (n, ic, pi, n-ic-pi))
    tds=[c.field(2,i,'Name') for i in range(c.nrows(2)) if c.field(2,i,'Name')!='<Module>']
    print('类型 %d 个: %s%s' % (len(tds), ', '.join(tds[:20]), ' ...' if len(tds)>20 else ''))
    return c

def main():
    base = r'D:\GooBall\extract102\raw\GooBall\GooBall\GooBall.app\Contents'
    cs = analyze(os.path.join(base,'Data','Assembly - CSharp.dll'), '游戏逻辑')
    print()
    ue = analyze(os.path.join(base,'Resources','UnityEngine.dll'), '引擎 API')
    print()
    print('='*74)
    print('游戏逻辑 -> UnityEngine 精确调用面（MemberRef 解引用 coded index）')
    print('='*74)
    memb = defaultdict(set)
    other = 0
    for i in range(cs.nrows(10)):
        tag, idx = cs.field(10,i,'Class')
        name = cs.field(10,i,'Name')
        if tag == 1:   # TypeRef
            full = (cs.field(1,idx-1,'Namespace') + '.' + cs.field(1,idx-1,'Name')).strip('.')
            if full.startswith('UnityEngine'):
                memb[full].add(name)
        elif tag == 0: # TypeDef (本程序集)
            other += 1
        else:
            other += 1
    print('TypeRef 指向 UnityEngine 的类型: %d   非 TypeRef 成员: %d' % (len(memb), other))
    tot = 0
    for t in sorted(memb, key=lambda x:-len(memb[x])):
        print('  %-34s %3d 成员' % (t, len(memb[t])))
        tot += len(memb[t])
    print('*** 需在宿主里实现的 UnityEngine 成员总数: %d ***' % tot)
    with open(r'D:\B++\WorkBuddy\spike_gooball\unity_api_surface.txt','w',encoding='utf-8') as f:
        for t in sorted(memb):
            f.write('%s\t%s\n' % (t, ', '.join(sorted(memb[t]))))

if __name__ == '__main__':
    main()
