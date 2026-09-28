# GooBall 资产二进制格式（Unity 1.x / SerializedFile v5 / PPC）

全部结论来自对 `sharedassets.assets`（91,561,103 B）与 69 个 level 文件的实测逆向，
经 ffmpeg 解码 / 三维渲染双重验证。

---

## 0. 对象表（ObjectInfo，20 B/条）

| 偏移 | 类型 | 含义 |
|---|---|---|
| +0 | u8 | pathID 低字节 |
| +1..+4 | u32 **BE** | offset（数据区偏移） |
| +5..+6 | u16 | 流标志（0 / 4） |
| +7..+8 | u16 **BE** | size（内联部分长度） |
| +9..+11 | — | — |
| +12..13 | u16 **LE** | typeID（类型树索引） |
| +14..15 | u16 **LE** | classID |
| +16..18 | — | 0 |
| +19 | u8 | pathID 高字节（每 256 行 +1） |

`pathID = b0 | b19<<8`。数据区 = `[16, metaStart)`，`metaStart = fileSize - metadataSize`。

---

## 1. 流式存储模型

数据区 = **对象内联部分**（sum 15.9 MB）+ **流洞**（75.4 MB）。
大资产的头部与前缀内联在对象里，**余量线性紧邻其后**（无间隙）：

```
整段资产 = raw[obj.offset + header_len : obj.offset + header_len + declaredSize]
```

- **音频 / 网格**：余量紧跟内联对象，直接切片即可。
- **Ogg**：页散落流区，需按 Ogg page 的 `bitstream_serial`（小端 @+14）分组、
  按文件偏移排序拼接重建（`tools/ogg_rebuild.py`，9561 页 → 9 组）。

---

## 2. AudioClip（classID 83）—— 55 个

```
u32 BE   name_len
u8[]     name
u32 BE   format          # 压缩格式枚举
f32 BE   duration        # 秒
u32 BE   frequency       # 采样率 (44100/22050/11025)
u32 BE   dataSize        # 音频字节数
u32 BE   dataSize        # 冗余双写（同值）
u8[]     音频数据（紧跟其后）
```

`format` 枚举：

| 值 | 含义 |
|---|---|
| 1 | 8-bit PCM，**mono** |
| 2 | 16-bit PCM，**mono** |
| 4 | 16-bit PCM，**stereo** |
| 5 | Ogg Vorbis（BGM） |

**关键**：
- PCM 样本字节序为**小端**（与文件整体大端相反）。
- 声道数可由 `dataSize / (bytesPerSample × channels × freq) ≈ duration` 反推。
- **本作无 MP3**：此前误判的 `0xFF` 同步字均为 PCM 波形中的偶然字节
  （如 `ff f1` 的 layer 位为 `00`=reserved，非法帧）。

产物：9 首 Ogg（38.6 MB）+ 46 个 WAV（8.7 MB），ffmpeg 全部解码通过、时长吻合。

---

## 3. Mesh（classID 43）—— 823 个

```
u32 BE   name_len
u8[]     name
# ---- m_LODData ----
u32 BE   LOD_count
  LOD:  u32 BE meshData_count
    MeshData:
      u32 BE faceCount          # 三角形数
      Face[faceCount]           # 每个 3 × u16 BE（v1,v2,v3）
      u32 BE stripCount         # 三角带 uint16 数
      u16[stripCount]           # 三角带（0xFFFF 为段重启）
# ---- 顶点等 ----
u32 BE   V                      # 顶点数
Vector3f[V]                     # 每顶点 3 × f32 BE
u32 BE   U
Vector2f[U]                     # UV，每顶点 2 × f32 BE
... m_UV1 / m_Colors / m_Skin / m_TangentSpace ...
AABB                            # m_LocalAABB：center(3f) + extent(3f)
u32 BE   nCol
u16[nCol]                       # m_CollisionTriangles
u32 BE                          # m_CollisionVertexCount
```

**关键**：
- 顶点 float 为**大端**（PPC）。
- 几何在 `faces`（三角形列表，计数=三角形数）**或** `strips`（三角带，计数=uint16 数）之一：
  实测 191 个用 faces、618 个用 strips。
- 三角带按标准 `i=even: (s[i],s[i+1],s[i+2]) / i=odd: (s[i+1],s[i],s[i+2])` 解码，
  缝合产生的退化三角形（重复索引 / 零面积）需剔除。
- 定位 `m_Vertices`：`faceCount` 个 Face（6 B/个）与 `stripCount` 个 u16（2 B/个）之后的
  第一个 `[u32 V][V×float3]` 区块（faces 的 u16 解释为 float 时是次正规数，天然排除）。

验证：渲染出连续三维形状（`proof/mesh_preview.png`），809/823 成功，146,638 三角形。

---

## 4. Texture2D（classID 28）—— 218 个

格式含 DXT1/DXT5 压缩与未压缩 RGB(A)，解码为 PNG。详见 `tools/extract_textures.py`。
