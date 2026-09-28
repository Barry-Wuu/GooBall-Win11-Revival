# GooBall Win11 Revival

把 2005 年 Mac 独占游戏 **GooBall** 复活到现代 Windows（Win11）。

> GooBall 是 **史上第一款 Unity 引擎游戏**（Unity 1.x beta，2005，Over The Edge / Ambrosia Software）。
> 原始平台为 Mac / PowerPC，游戏本体已近乎失传。本仓库对它做二进制级逆向，还原全部资产与逻辑，
> 目标是在现代 Windows 上以 Godot 4 / Unity 2021 LTS 重建可玩版本。

---

## 原始文件

| 项 | 值 |
|---|---|
| 版本 | GooBall 1.0.2（2007-04-03 / 1.0.1 为 2007-02-02） |
| 平台 | Mac OS X / PowerPC（Fat binary：PPC + x86） |
| 引擎 | Unity 1.x beta，SerializedFile **version 5** |
| 内容 | 69 个关卡 + mainData + sharedassets.assets（91.5 MB，2962 对象） |

---

## 资产提取进度

| 资产 | 类 | 状态 | 产出 |
|---|---|---|---|
| 对象表 | — | ✅ | `tools/unity1x.py`，71/71 文件通过 |
| Texture2D | classID 28 | ✅ 218/218 | `assets/textures/` 229 张 PNG（35 MB） |
| AudioClip | classID 83 | ✅ 55/55 | `assets/audio/` 9 首 Ogg BGM + 46 个 PCM 音效（48 MB） |
| Mesh | classID 43 | ✅ 809/823 | `assets/meshes/` 809 个 OBJ，146,638 三角形（9 MB） |
| Shader | classID 48 | ✅ 50/50 | `assets/shaders/` 完整 shader 源码 |
| Material | classID 21 | ✅ 250/250 | `assets/materials/materials.json`（纹理/shader 绑定 + 属性） |
| AnimationClip | classID 74 | ✅ 157 | `assets/animations/`（原始 + JSON） |
| 场景层级 | GameObject/Transform | ✅ | `assets/scenes/`（69 关 + mainData + sharedassets） |
| 关卡数据 | — | ✅ | `assets/levels/` 65 个 level 名称列表 |
| 游戏逻辑 | MonoBehaviour | 🚧 | `docs/il_*.txt`（IL）、`docs/GooBall_logic_recovery.md` |

预览：`proof/mesh_preview.png`

---

## 逆向成果（格式文档）

| 文档 | 内容 |
|---|---|
| `docs/Unity1x_serializedfile_v5.md` | SerializedFile v5 对象表布局 |
| `docs/ASSET_FORMATS.md` | **Asset 二进制格式**：AudioClip / Mesh / Texture2D 精确字段布局（本仓库核心） |
| `docs/GooBall_logic_recovery.md` | Unity C# 层逻辑恢复 |

### 关键结论

- **流式存储**：大资产（纹理/音频/网格顶点）散落在 75 MB 流洞中。音频/网格的流式余量**紧跟内联对象、无间隙**，整段 = `raw[obj.offset + header : + dataSize]`；Ogg 按 stream serial 聚合重建。
- **字节序混合**：头部字段为**大端**（PPC）；但 **PCM 音频样本为小端**、**Mesh 顶点 float 为大端**。
- **AudioClip 压缩枚举**：`1`=8bit PCM(mono)、`2`=16bit PCM(mono)、`4`=16bit PCM(stereo)、`5`=OggVorbis。**无 MP3**。
- **Mesh**：`m_LODData → MeshData{faces[trio], strips[tri-strip]} → m_Vertices[big-endian float3] → m_UV`，几何在 faces **或** strips 中。

---

## 工具

```
tools/
├── unity1x.py              # SerializedFile v5 对象表解析（核心）
├── extract_audio_final.py  # 55 个 AudioClip → Ogg/WAV
├── ogg_rebuild.py          # 按 serial 重建流式 Ogg
├── mesh_extract4.py        # 823 个 Mesh → OBJ（faces/strips 双解）
├── extract_textures.py     # Texture2D → PNG
├── verify_ogg.py / verify_audio2.py  # ffmpeg 解码验证
├── manifest_audio.py       # 音频清单
├── census_classes.py       # classID 普查
└── dump_syms.py            # Mach-O 符号提取
```

依赖：Python 3.11+、ffmpeg（验证音频）、numpy + matplotlib（网格预览）。

---

## 复现

```bash
# 1. 解包原始 .dmg / .app，得到 Data/ 目录（含 sharedassets.assets）
# 2. 提取音频
python tools/extract_audio_final.py
python tools/ogg_rebuild.py
# 3. 提取网格
python tools/mesh_extract4.py
# 4. 提取纹理
python tools/extract_textures.py
```

---

## Roadmap

- [x] 对象表解析（SerializedFile v5）
- [x] Texture2D / AudioClip / Mesh / Shader / Material / AnimationClip 全量提取
- [x] 场景层级（69 关 + sharedassets）导出
- [ ] Material/Shader → Godot 材质转换
- [ ] Mesh 剩余 14 个退化网格
- [ ] 在 Godot 4 重建物理 / 输入 / 存档 / 消息契约
- [ ] Win11 可玩版本发布

---

## 声明

本项目为**技术研究与数字保存**用途。GooBall 及其全部资产版权归原作者与发行商
（Over The Edge / Ambrosia Software）所有。因原平台与发行渠道已消亡，本仓库对失传资产做保存性归档。
