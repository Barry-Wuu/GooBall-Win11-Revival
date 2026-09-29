# GooBall 场景重建：组件挂接的场景树 + MonoBehaviour 定位

> 第四轮资产之后的收口工作（2026-09-29）。把已出土的 1447 个 MonoBehaviour 实例
> 通过 `go_pid` 锚定到真实 GameObject，并沿 `Transform.m_Father` 父子链算出每个对象
> 在游戏场景中的**物理路径**，从而让全部脚本资产「可定位」。

---

## 1. 做法（为什么用类型树，而不是手写布局）

早期 `extract_anim_scene.py` 用手写布局解析 Transform，但实测发现 GooBall 的序列化
布局与假设不符（**GameObject 的 `m_Name` 以 char 数组存在尾部**，`m_Component` 在前）。
逐一猜测布局既脆弱又易错。

改用更可靠的路线：**直接用语义化 metadata 内置类型树（classID>0）反序列化**。这些树是
Unity 自己写进文件的权威布局，与序列化数据 100% 对应（实测 GameObject 96/96、Transform
124/124 字节精确消耗）。脚本 `scene_graph.py` 复用 `mb_fields.py` 的 `parse_all_trees` +
`deserialize_tree` 基础设施。

关键结构（实测确认）：

- `GameObject.m_Component`：元素为 `{first: 组件classID, second: {m_FileID, m_PathID}}`
  —— 直接拿到「组件类型 + pid」，无需查对象表。
- `Transform.m_Father` / `m_Children`：`PPtr<Transform>`，父子链用 **Transform 的 pid** 串。
- `Transform.m_GameObject`：`PPtr<GameObject>`，把 Transform 绑回 GO。

---

## 2. 成果数据

| 指标 | 数值 |
|---|---|
| GameObject 总数 | **6821**（全 71 文件） |
| Transform 总数 | 6816 |
| MB 定位条目 | 1447 |
| **有场景路径的 MB** | **1443（99.7%）** |
| 去重场景路径 | 263 条 |
| 最深层级 | 10 层 |
| 富化引用：Renderer | 3846 |
| 富化引用：MeshFilter | 3826 |
| 富化引用：MeshCollider | 2970 |
| 富化引用：Light | 689 |
| 富化引用：Animation | 4292 |

### 脚本定位样例（GO 名 → 场景路径）

| 脚本 | GameObject | 场景路径 |
|---|---|---|
| BallController | `Ball` | `_player/Ball`（玩家球本体） |
| StarPickup | `star pickup` | `Level Pivot/Holder/star pickup` |
| GameManager | `gamemanager` | `gamemanager`（根节点） |
| MusicPlayer | `Musicplayer` | `Musicplayer` |
| MainMenu | `menucontroller` | `menucontroller` |

### 全局脚本实例 Top（玩法逻辑分布）

```
StarPickup          268     ActivateTrigger     222     GradientMaterialColor 218
GoalTrigger          74     LevelTilter          62     LevelInfo             62
CloudMover           58     CatapultAction       56     ...（共 83 类）
```

### 关卡脚本丰富度 Top

`sharedassets`(46 类/121 实例，全局预制) 之外，玩法最密的关卡是 `level13 / level3 /
level4 / level51 / level8 / level9`（各 15 种脚本）。

---

## 3. 富化：组件关键引用

对每个 GameObject，在本文件有对应类型树时反序列化下列组件，抽取关键引用：

- **MeshFilter**(33) → `mesh_pid`（该 GO 用的网格）
- **MeshRenderer**(23) → `material_pids`（材质列表）
- **MeshCollider**(64) → `collider_mesh_pid`（碰撞网格）
- **Light**(108) → `color` / `intensity` / `light_type`（光照参数）
- **Animation**(111) → `clip_pids`（绑定的 AnimationClip 列表）

样例：

- Light `light` → 路径 `mapscreen/light`，颜色 `(0.135, 0.157, 0.206)` 深蓝环境光
- MeshCollider `NM_kaktus` → 路径 `Level Pivot/Holder/NM_kaktus`，碰撞网格 pid=129
- Animation `00 - NM Intro1` → 路径 `mapscreen/leveldots/new mexico/00 - NM Intro1`，clip=[127,19]

---

## 4. 边缘情况（已记录，不影响主线）

1. **4 个 MB 无场景路径（占 0.3%）**：其 `go_pid` 指向的 GameObject 反序列化或 Transform
   链缺失（`level0` 的孤儿树 MB、`mainData` 中 2 个缺 Transform 的 GO、`sharedassets` 中 1 个
   未解析 GO）。数据本身已提取，仅定位信息缺。
2. **4 个空关卡（level14 / 15 / 16 / 52）**：每文件恰 8 个对象，**全为引擎管理器占位类**
   （classID 127/104/31/63/35/46/7/29，nc=0、byteSize=0、数据为空）——是预留/未启用的
   关卡槽位，GO=0 完全合理，非解析失败。

---

## 5. 交付物

- `scripts/scene_graph.py` —— 终版场景重建器（类型树驱动，可重跑）
- `assets/scene/scene_graph.json` —— 完整场景图（每文件 GO/Transform/MB，8.3 MB）
- `assets/scene/mb_locations.json` —— **聚焦的 MB 定位表**（file/mb_pid/script/go_name/
  scene_path/key_fields，422 KB）
- `assets/scene/scene_summary.json` —— 每文件 GO/TR/MB 计数与组件分布

---

## 6. 渲染链打通（GO → 网格/材质/纹理）

`render_chain.py` 把场景图里的 pid 引用跨文件解析成实体名：

- `mesh_pid` → sharedassets Mesh(43) 实体名（m_Name 为数据首部长度前缀串）
- `material_pids` → `assets/materials/materials.json`（250 条，含 shader 名/纹理/属性）
- 关卡本地材质（level47/48/55 各 1 个）按 sharedassets 的 Material 布局兜底解析

| 指标 | 数值 |
|---|---|
| 覆盖文件 | 67 |
| 渲染链条目 | **5294** |
| mesh 解析 | 3750/3785（99.1%） |
| material 解析 | 3830/3846（99.6%） |

最常用材质：`wood2`(372)、`-star red`(183)、`sky`(152)、`monster_pattern2a`(104)；
最常用网格多为 Maya 导出名：`polySurface23|polySurfaceShape24`(267)、`skyShape4`(152)。

样例：

- `ChapterSelector/Chapter item` → mesh `Plane`，材质 `nmex1`（shader `Self-illumination`，纹理 `nmex1`）
- `ChapterSelector/camera/aspect pivot/Chapter: ` → 材质 `intro text`（shader `outlined text`，纹理 `gootxt_body`）

注：玩家球本体 GO（`_player/Ball`）无 MeshFilter——其组件为 Transform + Rigidbody(54)
+ 2×MonoBehaviour + AudioListener(82) + SphereCollider(135, radius=0.3)；
球体视觉由子对象渲染。

## 6.5 GooBall 私有物理类出土（黏球形变核心）

三者各 1 个实例（sharedassets 模板），全部挂在与 Ball 联动的 **`_player/BallSurface`** 上：

```
_player/Ball          Transform + Rigidbody(54) + BallController 等 MB + SphereCollider(135)
  └─ BallSurface      Transform + MeshFilter/Renderer + GooLattice(150)
                      + GooStickyness(151) + GooballCollider(77) + 2×MB
```

| 类 | 关键字段（反序列化实测） |
|---|---|
| **GooStickyness(151)** | m_BaseRadius=0.3, m_ContactNormalSmoothing=0.5, m_MaxStretch=1.0, m_StickynessStrength≈0.0001, m_ClampStrength=0, m_Drag=0, m_RotationalDrag=0, m_Ball→Ball(1592), m_DrawSprings=0 |
| **GooLattice(150)** | 1765B/53 节点：m_Verts = Array<Array<[5×Vector3f]>> + Matrix4x4f（可形变点阵，模板全 0，运行时填充） |
| **GooballCollider(77)** | m_Layers=1, m_Skip=3 |

注：metadata 类型树区的最后一个节点 `bool m_DrawSprings` 正是 GooStickyness 的末字段，
与此互证。classID 135 确认为标准 SphereCollider（非专属类）。

## 7. 下一步

- **AnimationClip**(74) 关键帧解包：4292 个 Animation 已指向 clip，下一步解曲线数据。
- **Light intensity 字段名补齐**：部分树字段名与预期不同。
- **物理重建**：GooLattice 点阵 + GooStickyness 参数已齐，可复现 goo 球黏附/形变物理。
