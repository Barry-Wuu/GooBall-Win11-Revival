#!/usr/bin/env python3
"""dump PPC Mach-O 符号表，找 Mesh/序列化相关符号。"""
import struct, re, sys

p = r'D:\GooBall\bin\GooBall_ppc'
s = open(p, 'rb').read()
magic, ct, cs, ft, ncmds, szcmds, flags = struct.unpack('>IIIIIII', s[:28])

symoff = nsyms = stroff = strsize = None
off = 28
for i in range(ncmds):
    cmd, cmdsize = struct.unpack('>II', s[off:off+8])
    if cmd == 0x2:
        symoff, nsyms, stroff, strsize = struct.unpack('>IIII', s[off+8:off+24])
    off += cmdsize

strtab = s[stroff:stroff+strsize]
syms = []
for i in range(nsyms):
    b = symoff + i*12
    strx, n_type, n_sect, n_desc, n_value = struct.unpack('>IBBhI', s[b:b+12])
    e = strtab.find(b'\x00', strx)
    nm = strtab[strx:e].decode('ascii', 'replace')
    syms.append((n_value, nm))
print(f"总符号 {len(syms)}")

# 分类
def show(pat, label):
    xs = [(v,n) for v,n in syms if re.search(pat, n, re.I)]
    print(f"\n=== {label} ({len(xs)}) ===")
    for v,n in xs[:60]:
        print(f"  {v:#010x} {n}")

show(r'mesh', 'mesh')
show(r'vertex|vertice|index|triangle|face', 'vertex/index')
show(r'serial', 'serialize')
show(r'audio|sound|clip', 'audio')
