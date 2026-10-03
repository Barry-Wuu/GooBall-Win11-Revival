# Unity 1.x SerializedFile (version 5) 格式定案

> 实测对象：GooBall (2005, Mac/PPC, Unity 1.x beta) —— 69 个关卡 + mainData + sharedassets.assets
> 验证方式：零依赖 Python 逐行解析 + 数据内容实证（对象头名字/结构打分），脚本 `scripts/unity1x.py`

## 1. 文件总体布局（与新版 Unity 相反：metadata 在文件末尾）

```
[0x00] header 16B 大端:
         metadataSize  u32
         fileSize      u32
         version       u32 = 5
         dataOffset    u32
[0x10]  objectData  = raw[16 .. fileSize-metadataSize)
[fs-ms] metadata    = raw[fileSize-metadataSize .. fileSize)
          int32 numBaseClasses          (小端)
          TypeTree[numBaseClasses]      (文本型, null 结尾字符串流, 如 "bool\0m_DrawSprings\0")
          int32 headField               (关卡=对象数; sharedassets=146, 语义待考)
          ObjectInfo[...]               (20B/条, 逐行解析至 classID 无效)
          int32 numExternals            (sharedassets=1)
          FileIdentifier[numExternals]
```

## 2. ObjectInfo（20 字节/条）—— 实测定案

| 偏移 | 宽度 | 字节序 | 含义 |
|---|---|---|---|
| +0 | u8 | — | pathID 低字节 |
| +1..+4 | u32 | **大端** | **offset**（数据区偏移，绝对自文件头） |
| +5..+6 | 2B | — | 未定（sharedassets 中呈 0/4，疑似流标志） |
| +7..+8 | u16 | **大端** | **size** |
| +9..+11 | 3B | — | MonoBehaviour 行呈 `FF FF FF xx` 形态 |
| +12..+13 | u16 | 小端 | typeID（类型树索引） |
| +14..+15 | u16 | 小端 | classID（Unity class ID；MonoBehaviour=114 时与 typeID 不等） |
| +16..+18 | 3B | — | 0 |
| +19 | u8 | — | pathID 高字节（对象数 >255 时进位） |

**pathID = b[0] | b[19]<<8**（sharedassets 2962 对象实证：b0 每 256 行回绕、b19 精确 +1）。

## 3. 验证结论（71/71 通过）

| 文件 | 对象数 | 数据区 | 特征 |
|---|---|---|---|
| level0..level68 | 199~822/关 | ≤40KB | **严格平铺**：offset == size 累加+8 对齐，逐行成立 |
| mainData | 60 | 14,790B | 平铺；全是 GameObject/Transform/MonoBehaviour |
| sharedassets.assets | 2962 | 91,307,673B | **不平铺**：对象 size 总和 15.9MB，149 个流洞共 75.4MB |

- sharedassets 末对象 offset(91,307,656)+size(17) = metaStart(91,307,673) 精确吻合。
- 2962 行 offset 处数据内容实证：1667 行有名字（`"montezuma"`、`"nmex1"`、`"leveldot selected"`、
  `" exit light"` 等——注意**名字长度是 int32 大端**，Mac/PPC 大端序列化的证据），
  1059 行无名合法结构，GameObject(cid=1) 开头是 component 引用而非 name。
- **75.4MB 流洞 = 贴图/音频本体**，由对象内部字段引用——现代 Unity `.resS` 流方案的前身。

## 4. 排错教训（供以后逆向复用）

1. **不要拿新版 Unity 的字段布局套 1.x**——新版 `pathID u32|offset u32|size u32` 全错。
2. 平铺自洽（offset == size 累加+对齐）是最强判据，但只适用于小文件；
   大文件有流洞，须改用「数据内容打分」（对象头 int32 大端长度 + ASCII 名）。
3. `classID 在 +12..+15 双写`，仅用 classID 做表定位签名会整体偏移 2 字节假阳性。
4. offset 高位字节排查法：**用累加值反查字节位置**（已知前 N 行 → 第 N+1 行 offset 完全已知
   → 在 20 字节里穷举哪个位置组合编码了它）。
5. UnityPy 1.25.3 对 version 5 误判为 2.5.0f5，全类型解析失败——1.x 必须自写解析器。

## 5. 下一步（资产解码）

- 对象数据内部也是**大端序列化**（PPC）——解码 Texture2D/Mesh/AudioClip 时字段全按大端读。
- 优先攻 Texture2D（cid=28）：内部含 width/height/格式/数据引用（指向流洞）。
- 流洞内数据定位：解析对象引用字段（洞起点 = 前对象结束对齐处）。
