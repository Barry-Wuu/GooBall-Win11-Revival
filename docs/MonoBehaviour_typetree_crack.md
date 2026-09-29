# MonoBehaviour TypeTree 逆向全记录（GooBall / Unity 1.x beta）

> 本轮攻克目标：把 1447 个 MonoBehaviour 实例通过 TypeTree 绑定到 MonoScript 并**逐字段提取序列化值**。
> 结果：**1440/1447 完整提取（97.6%），字节级精确消耗，0 失步**；7 个为构建期悬空脚本（MissingScript）。

## 一、metadata TypeTree 格式（完全破解）

此前误判为「扁平描述符 + 独立层级区」，真相是**统一树列表 + classID 头 + DFS 隐式结构**：

```
[0:4]   int32 LE = 1            # enableTypeTree
[4]     1 字节                   # 树总数（脚本树+内置树，level0=93=70+23 ✓ sharedassets=163=121+42 ✓）
[5..]   连续树列表，每棵：
          int32 BE classID      # 脚本树=负数；内置树=Unity 类 ID
          type\0 name\0
          6×int32 BE            # byteSize, index, isArray, version, metaFlag, numChildren
          子节点按 DFS 紧随其后（numChildren 隐式编码，无独立子索引区）
末尾    7 字节                   # 00 00 00 + head_field(int32 LE, level0=146)
对象表  (20B/条)
```

### 关键规律（本轮实证坐实）

| 规律 | 证据 |
|---|---|
| **脚本树 classID = -实例 pathID** | level0 70 棵树 69 个直接命中（-641→pid 641→typeID 127→size 33 四重互证）；1 个例外（pid=511 的树标为 -255）用 byteSize 兜底配对 |
| **脚本树是每实例一棵** | 67 个 GradientMaterialColor 实例 = 67 棵结构相同、classID 各异的树 |
| **内置树 classID = 类 ID** | GameObject=1、Transform=4、Mesh=43、MonoScript=115；对象表 typeID==classID |
| **AudioClip 在此版本 = classID 83**（非现代 58） | MusicPlayer 的 9 个 PPtr 全部命中 class 83 且名字可读 |
| **序列化数据全大端、无对齐** | MB base 布局 17 字节 = m_GameObject(PPtr,8)+m_Enabled(bool,1)+m_Script(PPtr,8)，bool 后无填充 |
| **ColorRGBA 有两种编码** | LineRenderer 树中 = 打包 u32（单子节点 UInt32 rgba）；脚本树中 = 4×float。由树的子节点结构自然区分 |
| **string = int32 长度前缀**（非 \0 结尾） | MonoScript m_ClassName 解析修正后 121/121 绑定成功 |
| **PPtr.fileID: 0=本文件, ≥1=externals[fileID-1]** | 关卡 MB 的 m_Script=(1,8) → sharedassets |

### 本轮排除的错误假设（防再走弯路）

- ✗ 独立层级区（int32 nc + int16 子索引）——数学巧合 38234=4×3937+2×11243 误导
- ✗ 描述符内联子索引
- ✗ typeID 直接索引树根（typeID 是每实例唯一值，只对内置类等于 classID）
- ✗ typeID-1 索引 Base 根列表

## 二、提取统计

| 指标 | 数值 |
|---|---|
| MB 实例总数（71 文件） | 1447 |
| 成功绑定脚本名 + 字段提取 | **1440** |
| MissingScript（构建期悬空 m_Script=(0,0)） | 7 |
| 反序列化失步 / 无树 / 短数据 | 0 / 0 / 0 |
| 脚本类 | 83 种 |
| MonoScript（全部在 sharedassets） | 105 |

字段清单见 `assets/monobehaviour/mb_fields.json`（1447 条完整记录）；绑定明细 `mb_bind_all.json`。

## 三、出土数据精选

### 3.1 全游戏音乐路由表（MusicPlayer, mainData pid=50）

| 字段 | pathID | AudioClip 真名（class 83） |
|---|---|---|
| m_IntroMusic | 1653 | **Theme song, 09 on Morten F's demo**（主题曲） |
| m_DefaultMainMusic | 1488 | techno-jazz |
| m_GameOverMusic | 1531 | gameoverloop |
| m_UnderwaterMusic | 1574 | Underwater |
| m_NewMexicoMusic | 1521 | UFO WIP, for New Mexico |
| m_ScreamparkMusic | 1520 | Debil updated, for Screampark |
| m_TheMonsterMusic | 1735 | Monster |
| m_MontezumaMusic | 1734 | Warp (Multi Report - eardrop) |
| m_AncientMusic | 1550 | Montezuma |
| m_MusicVolume | — | 0.8 |

（开发者 WIP 原始命名原样保留，如 "UFO WIP"、"Debil updated"）

### 3.2 玩法物理参数（BallController, sharedassets pid=1906）

| 参数 | 值 | 参数 | 值 |
|---|---|---|---|
| maxSpeed | 16.0 | steerPower | 10.0 |
| jumpForceHard | 5.7 | jumpForceSticky | 7.2 |
| jumpUpAngle | 20.0° | stickyLoseGripAngle | 45.0° |
| stickyForceScale | 5.0 | stickyStartTime / StopTime | 0.6 / 1.8 |
| steerMaxFwdSpeed | 3.0 | steerMaxSideSpeed | 1.0 |
| bumpSpeed | 2.0 | gravityOnGround/InAir | （见 JSON） |
| latticeWidth Base/Mid/Top | 1.3 / 1.1 / 1.0 | surfaceSlideWhenHard | 0.7 |

### 3.3 全局状态与难度

- **PlayerState**（mainData）：初始 lives=**2**，score/stars/level 全 0（新建档状态）
- **TimeScaleManager**（sharedassets pid=2146）：kSlowDownScale=0.5，难度表 m_Difficulties=[**0.75, 0.875, 1.0**]（三档难度时间缩放）
- **LevelInfo**（示例）：completionTime=180.0s（3 分钟通关时限，与截图计时器吻合）、levelRadius=32.29、heightDiff=0.15

### 3.4 其他

- **BallCritterController**：goo 球 21 个语音/音效引用（m_Happy1/2、m_YeeHaa1/2、m_Hit1/2/3、m_Idle1-3、m_Ledge1-3、m_snore…）
- **BallSoundController**：硬/软滚地、撞墙音效的阈值+淡出参数全套（hardHit1Threshold、softRollFade…）
- **VariationHolder**：关卡变体对象名 player/camera/rollsparks/soundcontroller/textcontroller/gameovercamera/helpsystem/rollsparksAnim/rollsplats/levelhighscore
- **WorldDependantGlow**：六大世界（an/mo/mz/nm/sp/uw 前缀）各 6 个发光参数 ×6 世界
- 内置区还挖出 GooBall 专属引擎类完整布局：**GooLattice(150)、GooStickyness(151)、GooballCollider(77)、Script(109)、Pipeline(17)、Scene(29)**

## 四、工具

| 文件 | 用途 |
|---|---|
| `tools/unity1x.py` | SerializedFile v5 解析（对象表/数据） |
| `tools/typetree_lib.py` | TypeTree 解析库（DFS 树重建） |
| `tools/mb_fields.py` | **终版全量字段提取器**（树解析+绑定+反序列化一体） |
| `tools/bind_all_mb.py` | 全量 MB→脚本名绑定（含 externals 跨文件解析） |
| `assets/monobehaviour/mb_fields.json` | 1447 条完整字段数据 |
