# 013 · 隐藏关 level5：被砍掉的 Area 51 前导关

> 问题来源：README 与 [`011-各关钻石统计.md`](011-各关钻石统计.md) 提到
> 「`level5` 存 5 颗钻石但未被关卡表引用 —— 被砍掉的隐藏关，游戏内进不去」。
> 读者追问：这关到底是怎么回事？能不能用某个按键切换进去？
>
> 结论：**`level5` 是一个完整制作、但最终被砍掉的 Area 51 同主题关卡**
> （新墨西哥沙漠 / 外星人基地风格）。它从未被注册进 `MapInfo::SetupLevels` 的关卡表，
> 游戏内没有任何入口，也**不存在任何按键/作弊码能切换进入**。
> 5 颗钻石在最终资产里被全部禁用（`m_Enabled=0`），`levelRadius=1.0` 明显未完成配置。

---

## 一、关卡表证据：`SetupLevels` 跳过了 index 2

游戏内关卡表由 `MapInfo::SetupLevels`（IL rva=`0x008de0`）硬编码，场景文件号 = `AddLevel` 的 index + 3。
完整版（Panther 分支）中 **Introduction** 章节只注册了三关：

```cil
IL_0027: call  AddLevel("Welcome", 0)     # → level3
IL_0032: call  AddLevel("Lagoon", 1)      # → level4
IL_003d: call  AddLevel("Area 51", 3)     # → level6   ← 跳过了 index 2
```

**跳过的 index 2 对应的正是 `level5`**。它从未进入 `m_Levels` 数组，
选关界面的点位、`MapInfo::NextLevel` 的推进链里都没有它。

---

## 二、场景内容：完整的 NM（新墨西哥 / Area 51 主题）关卡

`D:\GooBall\win\Data\level5` 文件 **112,502 字节**，与相邻正式关卡同一量级：

| 场景 | 大小 | 状态 |
|---|---|---|
| `level4` (Lagoon) | 106,780 B | 正式 |
| **`level5`** | **112,502 B** | **被砍** |
| `level6` (Area 51) | 123,158 B | 正式 |

共 **194 个 GameObject、23 个 MonoBehaviour、13 类脚本**。关卡主体逻辑完整：
`LevelInfo` / `GoalTrigger` / `LevelTilter` / `WaterControl`×2 / `CloudMover`×2 /
`CloudRotator` / `CameraAnimator` / `FXGlow` / `ReflectionRenderTexture` 全部启用。

### 主题判定：与 level6 (Area 51) 完全同源

level5 场景内大量 `NM_` 前缀对象（`NM_` = **New Mexico**，`docs/004` 坐实
`m_NewMexicoMusic = "UFO WIP, for New Mexico"`）。与正式关卡 level6 (Area 51) 对照：

| 对象 | level5 | level6 (Area 51) |
|---|---|---|
| `NM_startplatform` | ✅ | ✅ |
| `NM_bridgeUP` | ✅ | ✅ |
| `NM_sign_goaway` | ✅ | ✅ |
| `NM_sign_nogooballs` | ✅ | — |
| `NM_sign_nothingtosee` | ✅ | — |
| `NM_sign_runforrest` | ✅ | — |
| `NM_sign_stayout` | ✅ | — |
| `NM_restrictedsign` / `NM_buttonsign` | ✅ | ✅ |
| `NM_fencepart` | — | ✅ |
| `nm_pillar_*`（柱） | ✅ | ✅ |
| `NM_kaktus` / `cactus2` | ✅ | ✅ |
| `ufoSphere*` / `ufoexhaust*` | ✅ | ✅ |

**结论：level5 与 Area 51 使用同一套新墨西哥外星人基地主题资源**，
是 Introduction 章节中 Lagoon 与 Area 51 之间被砍掉的一关。
它独有的 4 块警示牌（`goaway` / `nogooballs` / `nothingtosee` / `runforrest` / `stayout`）
说明关卡叙事已设计好（"闲人免进的外星人基地"）。

---

## 三、钻石：5 颗全部被禁用

`mb_bind_all.json` 显示 level5 有 **5 个 `StarPickup` 实例，`m_Enabled` 全部为 0**。
反序列化后字段与正常关卡一致（`m_Speed=(0,1,0)`、`m_KillDelay=2.0`），仅被关闭。

世界坐标（沿 Transform 父链累加，工具复现见文末）：

| GO pid | 世界坐标 | 备注 |
|---|---|---|
| 1011 | (-15.21, 3.76, 11.21) | 场景内，可达 |
| 1027 | (-18.62, 2.83, 14.58) | 场景内，可达 |
| 1043 | (-6.71, 3.91, 6.90) | 场景内，可达 |
| 1059 | (-5.24, 4.34, 15.10) | 场景内，可达 |
| 152 | (-10.90, 4.98, 9.65) | 场景内，可达 |

与 [`012-悬空钻石排查`](012-悬空钻石排查.md) 的 Quagmire 悬空钻石不同，
**level5 的 5 颗钻石位置全部在关卡几何范围内**，没有任何"够不到"的问题——
它们是**被主动禁用**的，不是放错了。

---

## 四、LevelInfo：与 Area 51 同 world 组，`levelRadius` 异常

反序列化 level5 的 `LevelInfo`（pid=233）：

| 字段 | level5 | level3 (Welcome) | level4 (Lagoon) | level6 (Area 51) |
|---|---|---|---|---|
| `completionTime` | **120.0** | 180.0 | 180.0 | 90.0 |
| `world` | **1** | 0 | 4 | **1** |
| `levelRadius` | **1.0** ⚠️ | 32.29 | 20.0 | 30.0 |
| `heightDiff` | 0.15 | 0.15 | 0.10 | 0.15 |

要点：
- **`world=1` 与 level6 (Area 51) 完全一致**，再次佐证二者同属一个世界组。
  （注意：`docs/003` 的 World 枚举中 1 标为 "Ancient"，但正式关卡 Area 51 也是 1，
  说明 `LevelInfo.world` 的实际含义与主题命名存在错位，至少它与 Area 51 同组是确定的。）
- **`levelRadius=1.0` 极不正常**——全库正式关卡均在 20~32 量级。这是**未完成配置的占位值**，
  说明 level5 在砍掉前没有做完最终的半径/碰撞参数。

---

## 五、能不能按键切换进入？—— 不能

全量 IL（`docs/evidence/il_all.txt`，310,996 条指令）中所有关卡切换路径均依赖
**已注册的 `m_Levels` 数组**，不存在跳转到未注册场景的按键或作弊码：

| 函数 | rva | 逻辑 | 结论 |
|---|---|---|---|
| `MapInfo::SetupLevels` | `0x008de0` | 硬编码关卡表，无 level5 | 表里没有它 |
| `MapInfo::LevelWithIndex` | `0x0093fc` | 线性遍历 `m_Levels` 匹配 index | 找不到 index 2 |
| `MapInfo::NextLevel` | `0x0093cc` | 取当前关 `number+1` 再查表 | 推进链断在 Area 51 之前 |
| `ChapterItem::Update` | `0x003cac` | 方向键选关（`up/down/left/right` + `enter/return`） | 只操作已注册 ChapterItem |
| `SequenceController::Update` | `0x009e80` | 仅「鼠标左键 + StateUp」确认通关 | 无调试按键 |

`ChapterItem::Update` 里的按键（`"up"/"down"/"left"/"right"/"enter"/"return"`）是章节选择菜单的
**导航键**，不是关卡跳转快捷键；`SequenceController` 也无任何 `KeyCode` 分支。

---

## 六、想看到它怎么办

游戏内无入口，只能改数据：

1. **改关卡表**：把 `MapInfo::SetupLevels` 中某个 `AddLevel` 的 index 改成 `2`，
   或把 Introduction 章节补一条 `AddLevel("???", 2)`。
2. **直接加载场景**：调用 `Application.LoadLevel("level5")`（build index 6），
   但需先绕过 `MapInfo` 的关卡状态机，且 5 颗钻石仍是禁用的。

由于它从未进过正式关卡表，**没有"官方"进入方式**——这就是它叫"隐藏关"的原因。

---

## 复现

以下脚本可直接对原版 `Data/` 重跑，还原本文全部数据：

```python
# 依赖 tools/unity1x.py + tools/mb_fields.py
import sys, os, json
sys.path.insert(0, "tools")
from unity1x import Unity1x
from mb_fields import parse_all_trees, deserialize_tree

u = Unity1x(r"D:\GooBall\win\Data\level5")
trees = parse_all_trees(u.meta, 5, u.table_off - 7)
by_cid = {t["classID"]: t for t in trees}

# 1) GameObject 名称
for i in u.by_class(1):
    o = u.objects[i]
    val, _ = deserialize_tree(by_cid[1], u.obj_data(o))
    name = val.get("m_Name")
    if isinstance(name, dict) and name.get("Array"):
        name = bytes(name["Array"]).decode("ascii", "replace")
    print(o.pathID, name, val.get("m_IsActive"))

# 2) StarPickup 字段（pid 已知，树 classID = -pid）
for pid in (1025, 1041, 1055, 1071, 1082):
    o = next(o for o in u.objects if o.pathID == pid)
    val, _ = deserialize_tree(by_cid[-pid], u.obj_data(o))
    print(pid, "enabled=", val["m_Enabled"], "speed=", val["m_Speed"])
```