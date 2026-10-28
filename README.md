# GooBall Win11 Revival

把 2005 年的 Unity 首款游戏 **GooBall** 复活到现代 Windows（Win11）。

> GooBall 是 **史上第一款 Unity 引擎游戏**（Unity 1.x，2005，Over The Edge / Ambrosia Software）。

## ★ 最新进展：Windows 原版播放器已找到（2026-10-05）

**`archive.org` 存有 2007 年上传的 Windows 原版**（`GooBall-Win.zip`，71.4 MB，CRC 通过）。
解压即玩 —— 原版引擎、原版脚本、**69 个关卡全通**、原生 OpenGL 渲染。

```
双击 D:\GooBall\开始游戏.bat
```

> 键位已打补丁：原版跳跃键是 Mac 的 Command 键，Windows 版发布时未重绑，
> 现已改为 **空格**（见 [`docs/010`](docs/010-Windows原版播放器.md) 与 `tools/patch_input_keys.py`）。

`sharedassets.assets`（91.5 MB）与全部 69 个关卡**与 Mac 版逐字节相同**，
只有 `UnityEngine.dll` / `Assembly - CSharp.dll` / `unity default resources`
三个平台相关文件不同 —— 无需打桩、无需重编译、无需模拟器。

详见 [`docs/010-Windows原版播放器.md`](docs/010-Windows原版播放器.md)。

## 本仓库做什么

原版数据已到手后，本仓库的价值转为**完整逆向与保存**：
以 `docs/` 记录全部二进制格式结论，以 `tools/` 提供可复现的提取工具链。

> **2026-10-05 清理**：Three.js 复刻版（`game/`、`开始游戏.bat`(Web 版)、`gen_gamedata.py`）
> 与提取产物（`assets/`、`extract/`、`proof/`）已回收 —— 原版已在手，不再需要复刻。
> 仓库只留 `docs/`（结论）+ `tools/`（工具）+ `开始游戏.bat`（原版启动器）。
> 需要资产时用 `tools/` 脚本对着原版 `Data/` 重跑即可（几分钟）。
> Mac 版原始 dmg（1.0.1 / 1.0.2，256 MB）亦已回收 —— 本项目以 Windows 原版为准。
> 两者资产层逐字节相同（`sharedassets.assets` 与 69 个关卡 md5 一致），Mac 版只多一份
> PowerPC Mach-O 播放器。抓取记录见 `docs/evidence/macdmg_*.log`。

| 项 | 值 |
|---|---|
| 版本 | GooBall 1.0.2（2007，Ambrosia Software） |
| 平台 | Mac OS X / PowerPC（**另有 Windows 原版，见上**） |
| 引擎 | Unity 1.x，SerializedFile **version 5** |
| 内容 | 69 个关卡 + mainData + sharedassets.assets（91.5 MB） |

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
| TextMesh | classID 102 | ✅ 76/76 | `assets/textmeshes/`（72 含文本，54 唯一字符串） |
| MonoScript | classID 115 | ✅ 105 | `assets/data/monoscripts.json`（脚本清单） |
| MonoBehaviour | classID 17 / 114 | 🚧 | `assets/data/monobehaviours.json`（5698 实例，脚本关联待解） |
| 游戏逻辑 | MonoBehaviour | 🚧 | `docs/evidence/il_*.txt`（IL）、`docs/003-游戏逻辑恢复.md` |

> 上表 `产出` 列的目录是**当年提取产物，现已回收**（见上）。
> 复现方式：对着原版 `Data/` 跑 `tools/` 下对应脚本（见「复现」一节）。

---

## 各关钻石统计

游戏内 HUD **不提供全游戏钻石总数**，以下由 `tools/level_diamonds.py` 从二进制资产直接统计
（钻石 = `StarPickup` MonoBehaviour 实例）。完整逐关明细见 [`docs/011-各关钻石统计.md`](docs/011-各关钻石统计.md)。

| 章节 | 第1关 | 第2关 | 第3关 | 第4关 | 第5关 | 第6关 | 第7关 | 小计 |
|---|---|---|---|---|---|---|---|---|
| **Introduction** | 10 | 6 | 6 | — | — | — | — | **22** |
| **Area 51** | 0 | 4 | 3 | 5 | 3 | — | — | **15** |
| **UFO Crash Site** | 6 | 5 | 5 | 4 | 7 | — | — | **27** |
| **Montezuma** | 4 | 5 | 5 | 5 | 4 | 5 | 5 | **33** |
| **Space** | 6 | 6 | 4 | 4 | 3 | — | — | **23** |
| **Scream Park** | 5 | **14** | 3 | 9 | 6 | 5 | — | **42** |
| **Underwater** | 0 | 4 | 7 | 8 | 2 | 0 | 0 | **21** |
| **Aztec Spacerace** | 3 | 6 | 2 | 2 | 3 | — | — | **16** |
| **Cruel World** | 4 | 3 | 5 | 8 | 2 | 4 | — | **26** |
| **Dementia** | 3 | 5 | 2 | 5 | 3 | 0 | — | **18** |
| **Evil Finale** | 8 | 3 | 4 | 0 | 0 | 4 | — | **19** |
| **合计** | **49** | **61** | **46** | **50** | **33** | **18** | **5** | **262** |

- **11 章 61 关**（场景文件号 = `AddLevel` index + 3），启用关卡钻石合计 **262 颗**
- 单关最多：**Freestyle**（Scream Park 第 2 关）**14 颗**；`Welcome` 10 颗
- `0` 的 7 关是纯技巧/竞速关（场景内无 `StarPickup` 实例）
- 另有 `level5` 存 5 颗钻石但**未被关卡表引用** —— 被砍掉的 Area 51 前导关，游戏内进不去（完整还原见 [`docs/013`](docs/013-隐藏关level5.md)）

---

## 逆向成果（格式文档）

| 文档 | 内容 |
|---|---|
| `docs/001-Unity1x序列化文件v5格式.md` | SerializedFile v5 对象表布局 |
| `docs/002-资产二进制格式总表.md` | **Asset 二进制格式**：AudioClip / Mesh / Texture2D / TextMesh / MonoScript / MonoBehaviour 精确字段布局（本仓库核心） |
| `docs/003-游戏逻辑恢复.md` | Unity C# 层逻辑恢复 |
| `docs/006-浏览器可玩重建.md` | **Web 复刻全部逆向结论**：坐标系手性、strips 三角带、m_UV 位置、DXT 端序、关卡映射、出生点 |
| `docs/009-托管宿主可行性分析.md` | **能否自己写模拟器跑原版**：PE/CLI 元数据实证游戏逻辑 100% 纯托管，可达 icall 仅 235 个 |
| `docs/010-Windows原版播放器.md` | **★ 原版 Windows 播放器已找到**（archive.org 2007 留存）：解压即玩，OpenGL + 69 关全通 |
| `docs/011-各关钻石统计.md` | **11 章 61 关逐关钻石数**（游戏内无此统计）：矩阵表 + 逐关明细 + 未启用场景 |
| `docs/012-悬空钻石排查.md` | **Quagmire 那颗吃不到的钻石**：几何/弹道双向证明不可达，全库 262 颗仅 2 颗悬空 |
| `docs/013-隐藏关level5.md` | **被砍掉的 Area 51 前导关**：完整场景还原 + 关卡表证据 + 「无按键可进」的 IL 排查 |

### 关键结论

- **流式存储**：大资产（纹理/音频/网格顶点）散落在 75 MB 流洞中。音频/网格的流式余量**紧跟内联对象、无间隙**，整段 = `raw[obj.offset + header : + dataSize]`；Ogg 按 stream serial 聚合重建。
- **字节序混合**：头部字段为**大端**（PPC）；但 **PCM 音频样本为小端**、**Mesh 顶点 float 为大端**。
- **AudioClip 压缩枚举**：`1`=8bit PCM(mono)、`2`=16bit PCM(mono)、`4`=16bit PCM(stereo)、`5`=OggVorbis。**无 MP3**。
- **Mesh**：`m_LODData → MeshData{faces[trio], strips[tri-strip]} → m_Vertices[big-endian float3] → m_UV`，几何在 faces **或** strips 中。
- **TextMesh**（classID 102）：`[0:8] m_GameObject PPtr(大端) + [8:12] m_Text len(u32 BE) + [12:] text`。已出土全部游戏内文本，含 `unity 1.6 conversion` 字样（坐实由 Unity 1.6 工具链转换）。
- **MonoScript**（classID 115）：`[u32BE len + name]×3`（name / className / assembly）。提取 105 个脚本清单。
- **classID 权威映射**：以 TypeTree 自带文本（`Base\0` 后 +5 字节大端 int32 = classID）为准，**不盲信 UnityPy 现代编号**——本作早期编号存在偏差（如 17=MonoBehaviour 而非 Pipeline）。
- **⚠️ pathID 32-bit 编码陷阱**：对象表 pathID 为 16-bit（`b0 | b19<<8`）；但 MonoBehaviour 实例数据里的 PPtr 引用是 **32-bit 混合编码**——同一 32-bit 值在不同类型上字节序表现不一致（TextMesh 的 `m_GameObject.pathID` 须大端，MB 的 `m_Script` 须小端才合理）。**MonoBehaviour 实例字段值提取因此被阻断，待彻底厘清 PPtr 字节序后攻克。**

---

## 工具

```
tools/
├── unity1x.py              # SerializedFile v5 对象表解析（核心）
├── extract_audio_final.py  # 55 个 AudioClip → Ogg/WAV
├── ogg_rebuild.py          # 按 serial 重建流式 Ogg
├── mesh_extract4.py        # 823 个 Mesh → OBJ（faces/strips 双解）
├── extract_textures.py     # Texture2D → PNG
├── extract_shaders.py      # 50 个 Shader → 源码文本
├── extract_materials.py    # 250 个 Material → JSON
├── extract_anim_scene.py   # AnimationClip + 场景层级
├── textmesh_extract.py     # 76 个 TextMesh → 游戏内文本
├── extract_mb.py           # MonoScript 清单 + MonoBehaviour 实例
├── tt_classmap3.py         # TypeTree → 权威 classID→类名映射
├── census_all.py           # 全文件 classID 普查（41231 对象）
├── unitypy_types.py        # UnityPy classID 对照（交叉验证）
├── verify_ogg.py / verify_audio2.py  # ffmpeg 解码验证
├── manifest_audio.py       # 音频清单
├── census_classes.py       # classID 普查
└── dump_syms.py            # Mach-O 符号提取
```

依赖：Python 3.11+、ffmpeg（验证音频）、numpy + matplotlib（网格预览）。

---

## 复现

```bash
# 1. 解包 GooBall-Win.zip（或 Mac 版 .dmg），得到 Data/ 目录（含 sharedassets.assets）
# 2. 提取音频
python tools/extract_audio_final.py
python tools/ogg_rebuild.py
# 3. 提取网格
python tools/mesh_extract4.py
# 4. 提取纹理
python tools/extract_textures.py
# 5. 提取文本 / 脚本 / 行为
python tools/textmesh_extract.py
python tools/extract_mb.py
```

---

## Roadmap

- [x] 对象表解析（SerializedFile v5）
- [x] Texture2D / AudioClip / Mesh / Shader / Material / AnimationClip 全量提取
- [x] 场景层级（69 关 + sharedassets）导出
- [x] 游戏内文本出土（TextMesh 76，含 `unity 1.6 conversion` 证据）
- [x] MonoScript 清单（105）出土
- [x] MonoBehaviour 实例字段值提取（1440/1447，83 脚本类，字节精确）
- [ ] Material/Shader → Godot 材质转换
- [ ] Mesh 剩余 14 个退化网格
- [x] **Win11 可玩版本发布**：原版 Windows 播放器（双击 `开始游戏.bat`）
- [x] ~~可玩 Web 重建原型（Three.js）~~ → **已回收**（原版到手，复刻不再需要；
      逆向结论保留在 `docs/006-浏览器可玩重建.md`）

---

## 声明

本项目为**技术研究与数字保存**用途。GooBall 及其全部资产版权归原作者与发行商
（Over The Edge / Ambrosia Software）所有。因原平台与发行渠道已消亡，本仓库对失传资产做保存性归档。
