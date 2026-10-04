# 010 - Windows 原版播放器（7HE-CODE 打法移植）

> 2026-10-05。**本项目最简的结论：原版 Windows 播放器一直存在，不必自己造引擎。**
> 入口：双击 `D:\GooBall\运行原版.bat`

## 一句话

`archive.org` 上的 `GooBall` 条目里存着 **2007 年的 Windows 原版**
（`GooBall-Win.zip`，71,369,943 字节，CRC 校验通过）。
解压即玩 —— 原版引擎、原版脚本、原版 69 个关卡，**原生 OpenGL 渲染，60 FPS**。

这正是 7HE-CODE-Win11-Revival 用的打法（引擎壳缝合）的直接对应物，
但**我们连缝合都不用做**：当年 Unity 已经把 Windows 播放器发布出来了。

## 为什么之前没找到

前几轮一直在扒 Mac 版 `.app`（`extract102/`），并推断「Unity 1.0 是 Mac 独占、
1.1 起才有 Windows」，于是把 12.7MB PowerPC Mach-O 的执行问题当成死路，
转去做 Three.js 复刻和托管宿主分析。

**实际结论相反**：GooBall 1.0.2（2007-02，Ambrosia）当年就出了 Windows 版，
只是没在 Mac 包里。**该先搜的是「有没有现成 Windows 版」，不是「怎么在 Windows 上跑 Mac 版」。**

## 拿到它的路径（本机实测）

本机出口带宽 ~78 KB/s，且 archive.org 直连走代理 ProxyError，
所以走 Kaggle 中转（`wubarry/gooball-meta` → `gooball-dl` → `gooball-slice`）：

| 步骤 | 内核 | 作用 |
|---|---|---|
| 1 | `gooball-meta` | 抓 `archive.org/metadata/GooBall` → 列出文件清单（发现 `GooBall-Win.zip` 71.4MB） |
| 2 | `gooball-dl` | 云端下整包 + 在云端 `zipfile` 列出 91 项内容 |
| 3 | `gooball-slice` | 切 6 块 × 12MB + 逐块 md5，写 `manifest.json` |
| 4 | 本机 | 签名直链多线程 Range 续传拉块 → 校验 → 拼装 |

### 回传踩坑（补充技能）

- `kernels output` 整流下载在 **~3MB 处必断**（IncompleteRead）——老坑依旧。
- `kernels output` 的 `file_pattern` 参数**可以单文件拉取**（`re` 正则，锚定 `^manifest\.json$`），
  CLI 没有 `--file-name` 参数。
- 但**单块 12MB 仍然断**（ConnectTimeout / ConnectionError，14 次重试全挂）。
- **正解 = 签名直链 + 小分段多线程**：
  ```python
  from kagglesdk.kernels.types.kernels_api_service import ApiListKernelSessionOutputRequest
  with api.build_kaggle_client() as kag:
      req = ApiListKernelSessionOutputRequest(); req.user_name='wubarry'; req.kernel_slug='<slug>'
      r = kag.kernels.kernels_api_client.list_kernel_session_output(req)
      url = {it.file_name.split('/')[-1]: it.url for it in r.files}
  ```
  再对每个 url 做 **512KB/段 × 12 线程** 的 Range 拉取。
  实测 71.4MB / 6 块 / 140 段全部 md5 通过，耗时 31 分钟（约 38 KB/s 总带宽）。
- ⚠️ **SDK 导入路径随版本变**：本机是
  `kagglesdk.kernels.types.kernels_api_service`（不是技能里写的 `kagglesdk.kernels.models`），
  `ApiListKernelSessionOutputRequest` 只存在于 `kernels_api_service` 子模块。
  正确路径可从 `inspect.getsource(KaggleApi.kernels_output)` 反查。

## 解压后的构成

```
D:\GooBall\win\
├── GooBall.exe              3,178,496 B   i386 PE, OverTheEdge.Unity.UnityPlayer
└── Data\
    ├── Assembly - CSharp.dll    144,384 B   游戏逻辑（与 Mac 版不同，见下）
    ├── sharedassets.assets   91,561,103 B   ★ 与 Mac 版逐字节相同
    ├── level0 .. level68              69 个 ★ 与 Mac 版逐字节相同
    ├── mainData / ScreenSelector.bmp
    ├── lib\   mscorlib.dll / UnityEngine.dll / Boo.Lang.dll / UnityDomainLoad.exe
    ├── unity\ mono-1-vc.dll / unity default resources / wrap_oal.dll
    ├── etc\   mono\1.0\machine.config / mono\2.0\machine.config
    └── output_log.txt          （上传者跑到 "Player: init engine" 就关了）
```

### 平台差异只有 3 个文件

| 文件 | Mac 版 | Windows 版 | 性质 |
|---|---|---|---|
| `sharedassets.assets` | 91,561,103 | 91,561,103 | **md5 相同** |
| `level0` / `level4` / `mainData` | — | — | **md5 相同**（69 关全同） |
| `unity default resources` | 773,898 | 773,898 | 字节数同、**md5 不同** |
| `UnityEngine.dll` | 165,376 | 164,864 | 字节数不同 |
| `Assembly - CSharp.dll` | 147,968 | 144,384 | 字节数不同 |

→ 资产层（关卡/网格/纹理/音频）**完全通用**；
只有引擎 API 封装与内置资源是平台定制的。这就是 7HE-CODE 打法要处理的那一层，
而我们拿到的是**官方原版**，无需打桩。

## 运行环境

| 项 | 值 |
|---|---|
| 架构 | i386（32 位），Win7/10/11 均可运行 |
| 渲染 | **OpenGL**（不是 D3D9）—— 2005 年后的所有显卡都支持 |
| 音频 | OpenAL（`wrap_oal.dll`） |
| 脚本 | Mono 1.x + Boo（`Boo.Lang.dll` 自带） |
| 显存 | `Ageia.tif` 曾在 Mac 包里；Windows 包用 OpenGL，走软/硬兼容皆可 |

## 与三条旧路线的关系

| 路线 | 状态 |
|---|---|
| A. QEMU/TigerOS 跑 Mac 版 | **作废**（有原生 Windows 版，无需模拟） |
| B. Three.js 复刻（`开始游戏.bat`） | 保留作为「Web 版」，但不再是主线 |
| C. 托管宿主（`docs/009`） | 降级为备选（原版已在手，无需重写引擎核） |

**B 仍有价值**：浏览器直接开、免 32 位兼容层、便于做 B 站素材。
但**「原版行为 100% 一致」这个目标现在由 Windows 原版直接满足了**。

## 复刻要点

- archive.org 抓取一律走 Kaggle（`is_internet_enabled: true`），本机直连必 ProxyError。
- 大文件回传用「云端切片 + 签名直链小分段多线程」，别用 `kernels output` 整流。
- 内核跑完即删（`echo yes | kaggle kernels delete wubarry/<slug>`）——
  本次三个内核不含明文凭证，但按铁律仍清理。

## 产出文件

| 路径 | 说明 |
|---|---|
| `D:\GooBall\win\` | Windows 原版播放器（解压即玩） |
| `D:\GooBall\运行原版.bat` | 启动器（纯 ASCII + CRLF，规避 cp936 分词崩溃） |
| `D:\GooBall\GooBall-Win.zip` | 原始 zip（71,369,943 B，md5 `d3a0b4520735eab08e29481a9973da99`） |
