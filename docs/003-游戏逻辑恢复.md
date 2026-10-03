# GooBall 逻辑还原报告

> 对象：`Assembly - CSharp.dll`（148 KB，Mono 编译，i386 PE32）
> 方法：dnfile 元数据解析 + 自研 CIL 反汇编器（`scripts/dn_il.py`）逐方法还原
> 日期：2026-09-27

---

## 一、程序集概况

| 项 | 值 |
|---|---|
| 文件 | `Contents/Data/Assembly - CSharp.dll` |
| 大小 / 机器 | 147,968 B / `0x014c`（i386） |
| 格式 | PE32 + CLI Header（标准 .NET 程序集） |
| Module 名 | `82b080d3fff604c09bd0eff126270ec3.dll`（Mono 哈希名） |
| Assembly | 同名，版本 0.0.0.0 |
| 引用 | **UnityEngine 0.0.0.0**、**mscorlib 1.0.5000.0**（.NET 1.1 世代） |
| TypeDef / MethodDef / Field | **143 / 759 / 1089** |
| 引用类型 / 成员 | TypeRef 85 / MemberRef 410 |
| 常量表 | 126 条（枚举 + 数值常量） |

**结论**：游戏逻辑 100% 在托管代码里，**没有 native 代码**。整份逻辑可用标准 .NET 工具链处理，无需逆向机器码。

---

## 二、类全谱（143 类，按职责分组）

### 球体核心（最重）
| 类 | 方法/字段 | 职责 |
|---|---|---|
| `BallController` | **58 / 106** | 自研球体物理总控（重力/阻力/转向/黏着/跳跃/碰撞） |
| `BallCritterController` | 13 / 33 | 球表面"小生物"（Critter）表现 |
| `BallSoundController` | 13 / 57 | 滚动/撞击音效（14 个音效槽） |
| `Grabber` / `Shadow` | 3 / 5、3 / 4 | 抓取与投影 |
| `AutoHeightRespawn` | 2 / 0 | 自动高度重生 |

### 流程与进度
| 类 | 方法/字段 | 职责 |
|---|---|---|
| `SequenceController` | **46 / 23** | 全局状态机 + 模式入口 + 关卡加载 |
| `GameManager` | 26 / 23 | 局内管理：命/星/计时/重生/通关 |
| `MapScreen` | 20 / **171** | 选关地图（点位/连线/高亮） |
| `MapInfo` | 23 / 9 | 地图数据（章节/世界/关卡表） |
| `ChapterSelector` / `ChapterWelcome` / `ChapterItem` | — | 章节选择与欢迎页 |
| `LevelTilter` | 4 / 1 | 关卡整体倾斜（Monkey Ball 式） |

### 相机
| 类 | 方法/字段 | 职责 |
|---|---|---|
| `CameraManager` | 10 / 16 | 相机模式管理 |
| `CameraAnimator` | 13 / 18 | 关卡开场/坠落/重生/超时运镜 |
| `BackgroundLevelCamera` | 14 / 17 | 背景关卡循环展示 |
| `GameOverCamera` / `FixCamera` / `LooseCameraRotator` / `ConstrainToPlane` / `EnterExitTrigger` | — | 约束与触发 |

### 菜单 / UI
| 类 | 方法/字段 | 职责 |
|---|---|---|
| `MenuController` | 19 / 22 | 菜单中枢（增删项/选中/切换） |
| `MainMenu` / `GamePlayMenu` | 4 / 0、5 / 0 | 主菜单 / 局内菜单 |
| `MenuItem` / `MenuToggle` / `MenuCommand` / `MenuGoto` / `MenuInactiveItem` | — | 菜单项类型 |
| `MouseGUI` / `MouseClickable` / `MouseForwarder` | 12 / 5、4 / 6、4 / 1 | 鼠标交互 |
| `KeyboardNavigation` | 3 / 6 | 键盘导航 |
| `HUD*`（12 类） | — | 倒计时/黏液槽/圈速/命/星/跳跃/状态文字 |

### 拾取与机关
| 类 | 方法/字段 | 职责 |
|---|---|---|
| `PickupController` / `GooPickup` / `StarPickup` / `SlowmoPickup` / `TriggerPickup` | — | 黏液/星星/慢动作/触发拾取 |
| `CatapultAction` / `CoolMoveBegin` / `CoolMoveEnd` / `DelayedTrigger` / `ActivateTrigger` | — | 弹射 / 特殊移动 / 触发 |
| `PlatformMover` / `ObjectMover` / `WaterPlatformHit` | — | 平台运动 |
| `FalloutCollider` / `GoalTrigger` / `AreaAction` | — | 坠落区/终点/区域事件 |

### 音频
| 类 | 方法/字段 | 职责 |
|---|---|---|
| `MusicPlayer` / `MusicPlayerForwarder` | 10 / 12、4 / 0 | BGM 播放 |
| `EventSoundController` / `SoundTrigger` / `VolumeFader` | — | 事件音效/淡入淡出 |

### 表现特效
| 类 | 方法/字段 | 职责 |
|---|---|---|
| `FXGlow` / `WorldDependantGlow` / `GradientMaterialColor` | 9 / 25、5 / 42、7 / 10 | 辉光/渐变 |
| `ReflectionRenderTexture` / `TestRenderTex` | 10 / 6、5 / 2 | 反射 |
| `CloudRotator` / `CloudMover` / `Rotator` / `FaceForward` | — | 环境动效 |
| `GodrayGenerator` / `WaterControl` / `FoamController` / `WaterPlacer` / `VerticalLine` | — | 神光/水面/泡沫 |

### 存档与状态
| 类 | 方法/字段 | 职责 |
|---|---|---|
| `PlayerState` | 15 / 10 | 玩家状态单例（命/星/分/名） |
| `StatsFile` / `FloatStat` | 15 / 9、3 / 4 | 统计文件 |
| `HighScoreTable` / `LevelHighScore` / `Entry` / `CompareEntry` | — | 高分榜 |
| `TimeScaleManager` | 14 / 10 | 时间缩放（慢动作） |
| `VariationHolder` | 5 / 24 | 变体持有（难度/画质变体） |

### 设置与其他
`ApplySettings`（7 / 1）、`QualityDisabler`、`QualityMaterialSwitcher`、`ShaderReload`、`MyApplication`、`MoviePlayer`、`IntroLogos`、`DemoLoop` / `DemoLoopText` / `DemoFinishedLoop`、`Help` / `HelpRenderer`、`EulerHelper` / `PositionEuler`、`WindArea`、`WorldDependantInstancer`、`TriggerPickup`、`SoundTrigger`、`VariationHolder`

### 数据类（纯字段，0 方法）
`Level`{title, chapter, world, state, number, index, linePtr}、`World`（枚举）、`Layout`、`MapScreenState`、`BumpInfo`{speed, state}、`ContactPoint`、`AvgPenetration`、`SoundState`、`Plane`、`Gradient`

---

## 三、球体物理还原（BallController）

> **注意：GooBall 不使用 Unity 内置 CharacterController，而是基于 Rigidbody 自研**。
> 这些方法在 `FixedUpdate` 中按**固定顺序**调用，顺序本身是手感的一部分。

### 3.1 主循环 `FixedUpdate`

```csharp
void FixedUpdate() {
    if ((isActive || stopPlayFalling) && !stillWait)
        FixedDoGravity();

    if (stillWait) stillWait--;              // 整数计数器，非时间

    FixedDoConstantDrag();
    UpdateFwd();                             // 刷新朝向 fwd

    float m = rb.velocity.magnitude;
    if (m > maxSpeed) rb.velocity *= (maxSpeed / m);      // 全局速度钳制

    if (!isActive) return;

    UpdateTiltLevel();                       // 关卡倾斜
    FixedUpdateState();                      // 状态机（Hard/Sticky/InAir/LyingStill）
    FixedColliderSetup();
    FixedInJump();
    FixedCalculateContactNormal();           // 求接触法线 contactNormal

    if (contactNormalDefined && isSticky && HasGroundContact())
        stickTimer += Time.deltaTime;        // 黏着计时
    else
        stickTimer = 0f;

    if (isSticky)                            // 滚动角速度：切向速度 / 半径
        rb.angularVelocity = Vector3.Cross(
            contactNormal,
            Vector3.Exclude(contactNormal, rb.velocity)) / GetRadius();

    FixedSteerBall();                        // 输入 → 速度
    FixedStick();                            // 黏着吸附

    if (contactNormalDefined) GenericCollisionEvent();

    bool up = Input.GetButton("StateUp");    // 跳跃键（named "StateUp"）
    if (up && !jumpButtonSavedState) FixedDoJump();   // 边沿触发，防连跳
    jumpButtonSavedState = up;
    // …后续：音效状态、粒子、调试
}
```

### 3.2 重力 `FixedDoGravity`

```csharp
const float kGravityRamp = 0.15f;
float t = Mathf.Clamp(inAirTimer / kGravityRamp, 0f, 1f);
if (inJump) t = 1f;                                     // 跳跃中按空中重力
float g = Mathf.Lerp(gravityOnGround, gravityInAir, t);

float scale;
if (inAirTimer < groundContactBias && stickTimer > 0f)
    scale = onNonstickySurface ? gravityStickyFactor * 5f : 0f;   // 黏着态：非黏面 5 倍重力，否则 0
else {
    scale = 1f;
    if (HasGroundContact())
        scale -= Mathf.Gamma(rb.velocity.y, 3f, 2f) / 30f;         // 落速越大重力越小（缓冲）
}
rb.AddForce(new Vector3(0f, -g * scale * rb.mass, 0f));
```

### 3.3 阻力 `FixedDoConstantDrag`

```csharp
float maxDrag = -currentConstantDrag * rb.mass;
Vector3 cap = rb.velocity * (-rb.mass) / Time.fixedDeltaTime;
Vector3 f = maxDrag * rb.velocity.normalized;
if (f.sqrMagnitude > cap.sqrMagnitude) f = cap;   // 不超调（防抖动/反向）
rb.AddForce(f);
```

### 3.4 转向 `FixedSteerBall`（操控核心）

```csharp
float v = Mathf.Clamp(Input.GetAxis("Vertical"),   -1f, 1f);
float h = Mathf.Clamp(Input.GetAxis("Horizontal"), -1f, 1f);
steerAcceleration = Vector3.zero;

float len = Mathf.Sqrt(h * h + v * v);
if (len > 1f) { v /= len; h /= len; }              // 斜向归一化（不加速）

if (stickTimer > 0f && jumpTimer == 0f) {          // 黏着且未跳跃
    // 以接触法线 + 相机右向构造切平面基底
    Vector3 right = Vector3.Normalize(Vector3.Cross(crawlNormal,
                        cameraTransform.TransformDirection(Vector3.right)));
    Vector3 fwd = Vector3.Normalize(Vector3.Cross(right, crawlNormal));

    Vector3 target = Mathf.Gamma(h, 0.5f, 2f) * fwd
                   + (-Mathf.Gamma(v, 0.5f, 2f)) * right;    // 手感响应曲线
    target *= travelMode ? steerMaxSpeedStickyTravelmode : steerMaxSpeedSticky;

    if (rb.velocity.sqrMagnitude < target.sqrMagnitude)
        rb.velocity = target;                       // 未达上限：直接设速
    else {
        Vector3 delta = target - rb.velocity;
        rb.velocity += delta * (Time.deltaTime * 3f * stickyness);   // 平滑趋近
    }
    if (onNonstickySurface && rb.velocity.y > -0.5f) { /* …贴面修正… */ }
} else {
    /* 非黏着：空中/硬球转向，走 steerAcceleration → AddForce */
}
```

**要点**
1. `Vertical` 实际驱动**切向 fwd**，`Horizontal` 驱动**切向 right**（相对相机）。
2. `Mathf.Gamma(x, a, b)` 是**响应曲线**，现代 Unity 已删除该 API —— 需自实现（见缺口清单）。
3. 黏着态直接写 `rb.velocity`（瞬时），非黏着态用 `AddForce`（渐进）。**两套手感模型**。

### 3.5 黏着吸附 `FixedStick`（GooBall 招牌机制）

```csharp
if (!contactNormalDefined || !isSticky || jumpTimer != 0) return;

if (inAirTimer > groundContactBias) {
    // 长期离地：剥离法向分量并强减速
    rb.velocity = Vector3.Exclude(contactNormal, rb.velocity);
    float m = rb.velocity.magnitude;
    if (m > 4f) rb.velocity = rb.velocity / (m * 4f);      // ⚠ 语义存疑，待实测校准
    return;
}

// 正常黏着：把速度投影到切平面（保留大小）
Vector3 proj = Vector3.Exclude(contactNormal, rb.velocity);
float mag = rb.velocity.magnitude;
Vector3 v2 = proj.normalized * mag;
float m2 = v2.magnitude;
if (mag < float.Epsilon) v2 = Vector3.zero;
else if (m2 > mag) v2 = v2 * (mag / m2);
rb.velocity = v2;

// 非 travel 模式下，接触法线偏离"下"过多 → 失去抓地
if (!travelMode && Vector3.Angle(minContactNormalUntilted, Vector3.down) >= stickyLoseGripAngle) {
    UnStick(); return;
}

// ★ 8 方向 × 子采样射线，探测球体周围是否存在支撑面
var list = new ArrayList();
for (int i = 0; i < 8; i++) {
    int steps = (i == 0 || i == 7) ? 1 : 10;         // 首尾方向只 1 次
    for (int j = 0; j < steps; j++) {
        Quaternion q = Quaternion.Euler(-90f + i * 45f, j * 90f, 0f);
        RaycastHit hit;
        if (Physics.Raycast(transform.position, q * Vector3.forward, out hit,
                            Mathf.Lerp(GetRadius(), baseRadius, 0.5f)))
            list.Add(hit.collider);
    }
}
var cols = (Collider[])list.ToArray(typeof(Collider));
if (cols.Length == 0)
    rb.position += -contactNormal * 0.005f;          // 完全悬空 → 贴回表面
```

### 3.6 跳跃 `FixedDoJump` / `UnStick`

```csharp
void FixedDoJump() {
    if (inAirTimer >= groundContactBias) return;            // 空中不可跳
    inJump = true;
    Vector3 force;
    if (isSticky) {
        rb.velocity = new Vector3(rb.velocity.x, 0f, rb.velocity.z);   // 清垂直分量
        force = jumpDirection * jumpForceSticky;
        fwd = Vector3.Slerp(fwd, jumpDirection, 0.8f);                 // 朝向跟随跳跃方向
    } else {
        force = Vector3.up * jumpForceHard;                 // 硬球（非黏）纯上跳
    }
    UnStick();
    if (standingOn != null) {
        if (isSticky) rb.velocity += surfaceVelocity;       // 继承移动平台速度
        surfaceVelocity = Vector3.zero;
        standingOn = null;
    }
    rb.AddForce(force * rb.mass / Time.deltaTime);          // 除以 dt = 瞬时速度效果
    BroadcastMessage("BallJumped", isSticky);               // 通知音效/特效
}

void UnStick() {
    inAirTimer      = groundContactBias + 0.001f;
    stickTimer      = 0f;
    currentConstantDrag = 0f;
    noSteerTimer    = 0f;
    jumpTimer       = 0.15f;                                // 跳跃冷却 0.15 s
}
```

### 3.7 碰撞 `FixedDidBump`

```csharp
float sq = (lastVelFixed - rb.velocity).sqrMagnitude;       // 本帧速度突变
if (sq > sqrBumpSpeed && HasGroundContact())
    BroadcastMessage("BallBumped", new BumpInfo { speed = sq, state = GetState() });
```

---

## 四、关卡流程状态机（SequenceController）

### 4.1 状态枚举

```
kGameLoaderLevel             = 0     // 加载器场景
kMapscreenLevel              = 1     // 选关地图
kAdventureChapterScreenLevel = 2     // 章节选择
kChapterWelcomeScreen        = 3     // 章节欢迎页
kFirstPlayLevel              = 4     // ★ 游戏关卡起始 build index
kDisplayBackgroundLevelCycle = 15.0f // 背景关卡轮换周期(秒)
```

**关卡加载公式**：`Application.LoadLevel(levelIndex + 4)`
即 `level0~3` 是四个功能场景，`level4+` 才是真正的游戏房间。

### 4.2 六大世界（`World` 枚举，已用 Constant 表坐实）

| 值 | 世界 | 入口方法 |
|---|---|---|
| 0 | **NewMexico**（新墨西哥） | `StartPracticeNewMexico` |
| 1 | **Ancient**（远古） | `StartPracticeAncient` |
| 2 | **Montezuma**（蒙特祖玛） | `StartPracticeMontezuma` |
| 3 | **Underwater**（水下） | `StartPracticeUnderwater` |
| 4 | **Screampark**（尖叫公园） | `StartPracticeScreampark` |
| 5 | **TheMonster**（怪物） | `StartPracticeTheMonster` |

### 4.3 四种玩法模式（`PlayMode`）

| 值 | 模式 | 说明 |
|---|---|---|
| 0 | `none` | |
| 1 | **`adventure`** | 冒险主线，**唯一存进度**（`playmode==1` 才写 `PlayerPrefs`） |
| 2 | `practice` | 练习（单关），不存进度 |
| 3 | `travel` | 旅行模式（**需 `Application.isPanther`**） |
| 4 | `hardcore` | 硬核模式（**需 `Application.isPanther` + 解锁 10 章**） |

### 4.4 SequenceController 内部状态（`State`）

`AdventureChapterScreen` / `MapScreen` / `HiScore` / `ChapterWelcome` / `PlayingGame` / `DemoLoop` / `DemoFinishedRegisterGameLoop` / `PublisherLogos` / `MainMenu` / `SetupMenu`

（`StartPractice` 设 `m_State=2`、`StartLevel` 设 `m_State=6`，实测两处指向 MapScreen / PlayingGame —— 以运行期为准）

### 4.5 流程入口一览

```
启动 → PublisherLogos → MainMenu
  ├─ ADVENTURE  → StartAdventureGame → 章节选择 → ChapterWelcome → MapScreen
  ├─ PRACTICE   → 6 世界选择 → StartPractice(world)
  ├─ TRAVEL     → StartTravelmodeGame（isPanther 门禁）
  ├─ HARDCORE   → StartHardcoreGame（isPanther 门禁）
  ├─ HIGHSCORE  → SelectHiScore
  └─ Settings   → GamePlayMenu
MapScreen → MapScreenDidSelectLevel → StartLevel(idx) → LoadLevel(idx+4)
局内结束 → ReachedGoal / GameOver / FallOut / TimeOut → 结算/HiScore
```

---

## 五、局内规则（GameManager）

```csharp
const float kDefaultCompletionTime = 60f;    // 每关限时
const float kRespawnInAirTime      = 2f;     // 重生空中判定
const float kHurryUpTime           = 5f;     // 剩 5 秒 → Hurry Up
const int   kStarsForOneLive       = 10;     // 10 星换 1 命

void Initialize(PlayerState ps) {
    m_Respawnable = GameObject.FindGameObjectsWithTag("Respawnable");
    foreach (var g in m_Respawnable) g.SetActiveRecursively(false);
    m_BonusScore = 0;
    m_Lives      = ps.lives;
    m_StarCount  = ps.stars;
    var fo = GameObject.FindGameObjectWithTag("FalloutHeight");
    m_FalloutHeight = fo != null ? fo.transform : null;
    kVariation.InstantiateGameObject("textcontroller");
}

void PickedupStar() {
    m_StarCount++; m_StarsCollected++;
    int bonus = m_StarCount / 10;
    if (bonus > 0) m_Lives += bonus;          // 每 10 星累加命
}

void ReachedGoal() {
    if (!m_IsGameRunning) return;
    BroadcastMessage("StopPlay", false);
    BroadcastMessage("LevelComplete");
    LevelInfo li = new LevelInfo {
        stars       = m_StarsCollected,
        timeLeft    = Mathf.Max(m_Time, 0f),
        bonusPoints = m_BonusScore,
    };
    li.completionTime = LevelInfo.singleton.completionTime - li.timeLeft;
    int difficulty = PlayerPrefs.GetInt("DIFFICULTY", 1);
    // …写高分表 / 解锁下一关
}
```

`LevelInfo` 字段：`completionTime, skybox, levelRadius, flyinAnimation, world, flyinGamma, flyinRotation, heightDiff, singleton`

---

## 六、玩家状态与存档（PlayerState）

```csharp
class PlayerState : MonoBehaviour {
    const int kRestartLives = 5;
    const int kMinimumPracticePlayPoints = 10;

    static PlayerState singleton;
    int    lives = 5;  int stars;  int score;  string playerName = "";
    int    currentLevel;  int playmode;  World world;

    void Awake() { DontDestroyOnLoad(gameObject); }        // 跨场景常驻 singleton
    void ResetPlayerState() { lives = 5; stars = 0; score = 0; playerName = ""; }

    bool HasPracticeMode() => LastUnlockedChapter() >= 1;
    bool HasTravelMode()   => LastUnlockedChapter() >= 5  && Application.isPanther;
    bool HasHardcore()     => LastUnlockedChapter() >= 10 && Application.isPanther;
}
```

### PlayerPrefs 存档键（完整）

| 键 | 类型 | 说明 |
|---|---|---|
| `PlayPoints` | int | 练习点（仅 `playmode==1` 写） |
| `PlayedLevels <n>` | int | 关卡已玩标记 |
| `LapRecords <level>` | float | 圈速记录（默认 10000.0f） |
| `LapRecords Name <level>` | string | 圈速记录保持者 |
| `DIFFICULTY` | int | 难度（默认 1） |
| `UnityGraphicsQuality` | int | 画质档位 |
| `LastUnlockedChapter` | int | 已解锁章节数（进度核心） |

---

## 七、输入契约（移植必做）

### 7.1 轴（`Input.GetAxis`）

| 轴名 | 用途 |
|---|---|
| `Vertical` / `Horizontal` | **主操控**（球体移动） |
| `VerticalTilt` / `HorizontalTilt` | 关卡倾斜（`LevelTilter` / `UpdateTiltLevel`） |

### 7.2 按钮 / 键（`GetButton` / `GetKey`）

| 名称 | 用途 |
|---|---|
| **`StateUp`** | **跳跃**（球体主按钮，易误读为"状态上"） |
| `StateDown` | 状态切换（黏着开/关） |
| `space` / `enter` / `return` / `escape` | 菜单确认 / 取消 |
| `down` / `up` / `left` / `right` | 菜单导航 |
| `r` / `o` / `t` / `e` | 调试键 |
| `flyin gameover` | 特殊运镜触发 |

### 7.3 鼠标

`Input.GetMouseButton*` 用于 `MouseGUI` / `MouseClickable` / `MouseForwarder`（3 处）。菜单支持鼠标与键盘双导航（`MenuController.SetUseMouse`）。

---

## 八、消息图（BroadcastMessage / SendMessage）

GooBall 大量使用**广播消息**解耦，移植时需还原同一套消息名与接收方。

| 消息 | 发送方 | 语义 |
|---|---|---|
| `BallJumped` (bool isSticky) | BallController | 跳跃发生 |
| `BallBumped` (BumpInfo) | BallController | 碰撞发生 |
| `StopPlay` (bool) | GameManager | 停止操控 |
| `StartPlay` | CameraAnimator | 开始操控 |
| `LevelComplete` | GameManager | 通关 |
| `Respawn` / `RespawnBall` | GameManager | 重生 |
| `SetLifeCounter` / `SetStars` | GameManager | HUD 刷新 |
| `StateUp` / `StateDown` | BallController | 状态切换广播 |
| `CoroutineUpdate` | GameEndedHighScore | 协程驱动 |
| `EnterDemoLoop` / `DemoLoopFinished` | SequenceController / DemoLoop | 演示循环 |
| `ActivateDelayed` / `DoActivateTrigger` | ActivateTrigger | 延迟激活 |
| `StartChapter` / `ContinueAfterChapterWelcome` | ChapterSelector / ChapterWelcome | 章节流程 |
| `Clicked` | MouseClickable | 点击事件 |
| `Spawn` | GodrayGenerator | 生成 |
| `ActualCamera` / `BackgroundCamera` / `RenderTex` / `SmallRenderTex` | 渲染链 | 相机/RT 切换 |
| `GooLevelPivot` | BallController | 关卡枢轴 |
| `ExpensiveWater` / `ParticleFX` | ApplySettings | 画质开关 |

**注意**：现代 Unity 仍支持 `BroadcastMessage`，但已被标记为性能不友好；重建时可替换为事件/接口，**但必须保证消息名语义等价**（尤其 `BallJumped`/`BallBumped` 这类驱动音效与特效的）。

---

## 九、菜单结构

### MainMenu.SetupMenu（主菜单项）
```
ADVENTURE    → StartAdventureGame
PRACTICE     → StartPractice
TRAVEL       → StartTravelmodeGame      (isPanther)
HARDCORE     → StartHardcoreGame        (isPanther)
HIGHSCORE    → SelectHiScore
Settings     → GamePlayMenu
```
### GamePlayMenu.SetupMenu（局内菜单项）
```
Continue / ContinuePlaying
BackToMapScreen / FromPracticeToMapScreen
BackToDemoLoop
BACK
```
### 难度档（`DIFFICULTY`）
`Simple` / `Good` / `Beautiful` / `Fantastic`（画质）；`Casual` / `Cool` / `Tough` / `Fast` / `Fastest`（速度）；`OFF` / `QUIET` / `MELLOW` / `LOUD`（音量）
### 布局（`Layout`）
`horizontal` / `vertical` / `splitvertical`

---

## 十、音效槽（BallSoundController，14 个）

```
kHardRoll1/2/3   kSoftRoll   kSoftSteady   kFalling
kSoftHit1/2/3    kHardHit1/2/3   kSleepy        kSoundsEnd
```

---

## 十一、现代 Windows 移植缺口清单（★ 关键）

| # | 缺口 | 影响 | 处置 |
|---|---|---|---|
| 1 | **`Application.isPanther`** | Windows 恒 false → **Travel / Hardcore 模式永久锁死** | 移植时改为恒 true（或在 UI 隐藏这两个入口）。**这是缝合壳无法解决的平台硬耦合** |
| 2 | **`Mathf.Gamma(x, a, b)`** | 现代 Unity 已删除该 API，而它是**操控手感曲线** | 必须自实现。调用点：`FixedDoGravity(3,2)`、`FixedSteerBall(0.5,2)`。需按实测拟合 |
| 3 | **`Vector3.Exclude`** | 现代 Unity 已删除 | 等价于 `v - Vector3.Project(v, normal)`，直接替换 |
| 4 | **`GameObject.SetActiveRecursively`** | 已废弃 | 换 `SetActive(true)`（现代版递归语义已内置） |
| 5 | **`Application.LoadLevel`** | 已废弃 | 换 `SceneManager.LoadScene`；需重建 **build index → 场景** 映射（`idx+4`） |
| 6 | **`Input.GetAxis("Vertical"/"Horizontal")`** | 需 Input Manager 轴定义 | 重建 ProjectSettings/InputManager.asset，或改用新 Input System |
| 7 | **`Input.GetButton("StateUp")` 等自定义按钮** | 同上 | 在 Input Manager 里定义同名按钮 |
| 8 | **`BroadcastMessage` 消息链** | 需还原全部消息名与接收方 | 逐条对照第八节实现 |
| 9 | **Unity 1.x 资产（格式 v5）** | UnityPy 读不出对象数据（无 TypeTree） | **贴图/网格/音频需自写解码器**（另开工） |
| 10 | **`Application.isPanther` 之外的 Mac 专属** | `Screen.showCursor` 等行为差异 | 逐项实测 |
| 11 | **Unity 1.x QualitySettings 预设名** | `UnityGraphicsQuality` 档位语义 | 重建画质档位映射 |
| 12 | **PlayerPrefs 键名带空格与后缀** | 如 `"LapRecords " + level`（**注意尾随空格**） | 原样保留，否则存档不兼容 |

---

## 十二、复刻可行性结论

| 维度 | 评价 |
|---|---|
| **游戏逻辑** | ✅ **100% 可还原**。759 个方法全部已反汇编程可读 IL，无 native 依赖 |
| **数值/常量** | ✅ 全部解出（含 float 按位译码），手感参数可直接照搬 |
| **关卡结构** | ✅ 六大世界 + `LoadLevel(idx+4)` 映射清晰 |
| **输入契约** | ✅ 轴名/按钮名/鼠标用法全清单 |
| **存档格式** | ✅ PlayerPrefs 键名全清单（注意尾随空格） |
| **资产（贴图/网格/音频）** | ⚠️ **UnityPy 对 Unity 1.x 导出失败**，需自写解码器（唯一硬缺口） |
| **平台耦合点** | ⚠️ 12 项（见第十一节），其中 `isPanther` 与 `Mathf.Gamma` 是硬骨头 |

**下一步优先级**：
1. 攻 **Unity 1.x 资产解码器**（贴图 → PNG、Mesh → OBJ、AudioClip → WAV）—— 决定"能不能重建"的前提
2. 按本报告在 Godot 4 或 Unity 2021 LTS 上重建 `BallController` 物理（数值照搬）
3. 重建输入/存档/消息契约
4. 指令级对照验证（对比原版 IL 与重建代码的常量、公式）

---

*本报告基于静态反汇编。所有 IL 原文见 `extract/il_all.txt`（25,545 行）；分类清单见 `extract/types_methods.txt`、`extract/fields.txt`。*
