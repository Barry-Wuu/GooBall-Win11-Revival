# GooBall Revival — 可玩重建（level3 / New Mexico）

用 2005 原版逆向出土的资产（OBJ 网格 / PNG 纹理 / 场景图 / 材质绑定 / 物理参数）
在 Three.js 上重建的可玩原型。

## 启动

**双击 `开始游戏.bat`**（游戏根目录下），自动起本地服务器并打开浏览器。

> 需要本机有 Python 3（bat 依次尝试 `py` / `python` / `D:\B++\Py313\python.exe`）。
> 不能直接双击 index.html——浏览器 file:// 下无法 fetch 资产，必须走 HTTP。

## 玩法

- WASD / 方向键：滚动小球（`maxSpeed=16`、`ACCEL=30` 来自原版 BallController 实测字段）
- 空格：跳跃 · R：回到出生点
- 收集 10 颗 ★ 后进入绿色光环过关；球半径 0.3 = 原版 SphereCollider.m_Radius
- BGM：`UFO WIP, for New Mexico`（原版 MusicPlayer 路由表出土的真名）

## 文件

| 文件 | 说明 |
|---|---|
| `开始游戏.bat` | 启动器（ASCII 内容，避免中文 bat 编码坑） |
| `index.html` / `main.js` | 游戏（内置极简 OBJ 解析器，无第三方 loader 依赖） |
| `lib/three.module.js` | three.js r160 本地副本（离线可玩） |
| `data/level.json` | 关卡数据：对象变换矩阵/网格/纹理 + 星星/目标/出生点 |
| `assets/` | 由 `tools/gen_gamedata.py` 从 `assets/` 复制（不入库） |

## 重建数据

`python tools/gen_gamedata.py level3` 从仓库资产重新生成
`game/data/level.json` 并复制所需网格/纹理/音频（约 1.3 MB）。
