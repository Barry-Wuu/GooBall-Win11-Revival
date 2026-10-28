# GooBall — Win11 Revival

<a href="README.md">简体中文</a> ｜ <b>English</b>

Reviving **GooBall** — the very first Unity-engine game (2005) — on modern Windows (Win11).

> GooBall is the **first-ever Unity engine game** (Unity 1.x, 2005, by Over The Edge / Ambrosia Software).

## ★ Latest: the original Windows player has been found (2026-10-05)

**`archive.org` holds the Windows original uploaded in 2007** (`GooBall-Win.zip`, 71.4 MB, CRC verified).
Unzip and play — original engine, original scripts, **all 69 levels completable**, native OpenGL rendering.

```
Double-click D:\GooBall\开始游戏.bat
```

> Key binding patched: the original jump key was Mac's Command key, which was never rebound for the
> Windows release. It is now remapped to **Space** (see [`docs/010`](docs/010-Windows原版播放器.md) and `tools/patch_input_keys.py`).

`sharedassets.assets` (91.5 MB) and all 69 levels are **byte-for-byte identical to the Mac version**;
only `UnityEngine.dll` / `Assembly - CSharp.dll` / `unity default resources` differ between platforms —
no stubbing, no recompilation, no emulator needed.

See [`docs/010-Windows原版播放器.md`](docs/010-Windows原版播放器.md).

## What this repository does

Now that the original data is in hand, this repo's value shifts to **complete reverse-engineering and preservation**:
`docs/` records every binary-format conclusion, and `tools/` provides a reproducible extraction toolchain.

> **2026-10-05 cleanup**: early extraction products (`assets/`, `extract/`, `proof/`) have been recycled — the original is in hand.
> The repo now keeps only `docs/` (conclusions) + `tools/` (tools) + `开始游戏.bat` (original launcher).
> To obtain assets again, just re-run the `tools/` scripts against the original `Data/` (a few minutes).
> The Mac original dmg (1.0.1 / 1.0.2, 256 MB) has also been recycled — this project standardizes on the Windows original.
> The asset layers are byte-identical between the two (`sharedassets.assets` and the 69 levels share the same md5); the Mac version merely adds
> one extra PowerPC Mach-O player. Grab logs are in `docs/evidence/macdmg_*.log`.

| Item | Value |
|---|---|
| Version | GooBall 1.0.2 (2007, Ambrosia Software) |
| Platform | Mac OS X / PowerPC (**a Windows original also exists, see above**) |
| Engine | Unity 1.x, SerializedFile **version 5** |
| Content | 69 levels + mainData + sharedassets.assets (91.5 MB) |

---

## Asset extraction progress

| Asset | Class | Status | Output |
|---|---|---|---|
| Object table | — | ✅ | `tools/unity1x.py`, 71/71 files pass |
| Texture2D | classID 28 | ✅ 218/218 | `assets/textures/` 229 PNG (35 MB) |
| AudioClip | classID 83 | ✅ 55/55 | `assets/audio/` 9 Ogg BGM + 46 PCM SFX (48 MB) |
| Mesh | classID 43 | ✅ 809/823 | `assets/meshes/` 809 OBJ, 146,638 triangles (9 MB) |
| Shader | classID 48 | ✅ 50/50 | `assets/shaders/` full shader source |
| Material | classID 21 | ✅ 250/250 | `assets/materials/materials.json` (texture/shader binding + props) |
| AnimationClip | classID 74 | ✅ 157 | `assets/animations/` (raw + JSON) |
| Scene hierarchy | GameObject/Transform | ✅ | `assets/scenes/` (69 levels + mainData + sharedassets) |
| Level data | — | ✅ | `assets/levels/` 65 level name list |
| TextMesh | classID 102 | ✅ 76/76 | `assets/textmeshes/` (72 with text, 54 unique strings) |
| MonoScript | classID 115 | ✅ 105 | `assets/data/monoscripts.json` (script list) |
| MonoBehaviour | classID 17 / 114 | 🚧 | `assets/data/monobehaviours.json` (5698 instances, script association TBD) |
| Game logic | MonoBehaviour | 🚧 | `docs/evidence/il_*.txt` (IL), `docs/003-游戏逻辑恢复.md` |

> The `Output` directories in the table above are **past extraction products, now recycled** (see above).
> To reproduce: run the corresponding `tools/` script against the original `Data/` (see the *Reproduce* section).

---

## Reverse-engineering results (format docs)

| Document | Content |
|---|---|
| `docs/001-Unity1x序列化文件v5格式.md` | SerializedFile v5 object-table layout |
| `docs/002-资产二进制格式总表.md` | **Asset binary format**: precise field layout for AudioClip / Mesh / Texture2D / TextMesh / MonoScript / MonoBehaviour (core of this repo) |
| `docs/003-游戏逻辑恢复.md` | Unity C# layer logic recovery |
| `docs/009-托管宿主可行性分析.md` | **Can we write our own emulator to run the original?** PE/CLI metadata proves game logic is 100% managed, with only 235 reachable icalls |
| `docs/010-Windows原版播放器.md` | **★ Original Windows player found** (preserved on archive.org since 2007): unzip and play, OpenGL + all 69 levels |
| `docs/011-各关钻石统计.md` | **11 chapters / 61 levels per-level diamond counts** (not tracked in-game): matrix table + per-level detail + unused scenes |
| `docs/012-悬空钻石排查.md` | **The unreachable diamond in Quagmire**: geometric/ballistic proof of unreachability; only 2 of 262 diamonds float in the whole library |
| `docs/013-隐藏关level5.md` | **The cut Area 51 intro level**: full scene restoration + level-table evidence + IL audit proving "no key can enter it" |

### Key conclusions

- **Streaming storage**: large assets (textures/audio/mesh vertices) are scattered through a 75 MB stream hole. Audio/mesh streaming remainders sit **flush against the inline object, no gap** — the whole is `raw[obj.offset + header : + dataSize]`; Ogg is rebuilt by aggregating stream serials.
- **Mixed endianness**: header fields are **big-endian** (PPC); but **PCM audio samples are little-endian**, and **Mesh vertex floats are big-endian**.
- **AudioClip compression enum**: `1`=8bit PCM(mono), `2`=16bit PCM(mono), `4`=16bit PCM(stereo), `5`=OggVorbis. **No MP3.**
- **Mesh**: `m_LODData → MeshData{faces[trio], strips[tri-strip]} → m_Vertices[big-endian float3] → m_UV`; geometry lives in faces **or** strips.
- **TextMesh** (classID 102): `[0:8] m_GameObject PPtr(big-endian) + [8:12] m_Text len(u32 BE) + [12:] text`. All in-game text recovered, including the `unity 1.6 conversion` marker (confirming conversion via the Unity 1.6 toolchain).
- **MonoScript** (classID 115): `[u32BE len + name]×3` (name / className / assembly). 105 scripts listed.
- **Authoritative classID mapping**: trust the TypeTree's own text (`Base\0` then +5 bytes big-endian int32 = classID), **do not blindly trust UnityPy's modern numbering** — early IDs in this title are off (e.g. 17=MonoBehaviour, not Pipeline).
- **⚠️ pathID 32-bit encoding trap**: the object table's pathID is 16-bit (`b0 | b19<<8`); but the PPtr references inside MonoBehaviour instance data use a **32-bit mixed encoding** — the same 32-bit value shows inconsistent byte order across types (TextMesh's `m_GameObject.pathID` must be big-endian, MB's `m_Script` must be little-endian to make sense). **MonoBehaviour instance field extraction is thus blocked, pending a full clarification of PPtr byte order.**

---

## Diamonds per level

The in-game HUD **does not provide a total diamond count for the whole game**; the table below is counted directly
from the binary assets by `tools/level_diamonds.py` (a diamond = a `StarPickup` MonoBehaviour instance).
Full per-level detail is in [`docs/011-各关钻石统计.md`](docs/011-各关钻石统计.md).

| Chapter | L1 | L2 | L3 | L4 | L5 | L6 | L7 | Subtotal |
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
| **Total** | **49** | **61** | **46** | **50** | **33** | **18** | **5** | **262** |

- **11 chapters, 61 levels** (scene file number = `AddLevel` index + 3); enabled-level diamonds total **262**.
- Most in a single level: **Freestyle** (Scream Park L2) **14**; `Welcome` 10.
- 7 levels with `0` are pure skill/race levels (no `StarPickup` instance in the scene).
- `level5` holds 5 diamonds but is **not referenced by the level table** — the cut Area 51 intro level, unreachable in-game (full restoration in [`docs/013`](docs/013-隐藏关level5.md)).

---

## Tools

```
tools/
├── unity1x.py              # SerializedFile v5 object-table parser (core)
├── extract_audio_final.py  # 55 AudioClip → Ogg/WAV
├── ogg_rebuild.py          # rebuild streaming Ogg by serial
├── mesh_extract4.py        # 823 Mesh → OBJ (faces/strips dual parse)
├── extract_textures.py     # Texture2D → PNG
├── extract_shaders.py      # 50 Shader → source text
├── extract_materials.py    # 250 Material → JSON
├── extract_anim_scene.py   # AnimationClip + scene hierarchy
├── textmesh_extract.py     # 76 TextMesh → in-game text
├── extract_mb.py           # MonoScript list + MonoBehaviour instances
├── tt_classmap3.py         # TypeTree → authoritative classID→name map
├── census_all.py           # full-file classID census (41231 objects)
├── unitypy_types.py        # UnityPy classID cross-check
├── verify_ogg.py / verify_audio2.py  # ffmpeg decode verification
├── manifest_audio.py       # audio manifest
├── census_classes.py       # classID census
└── dump_syms.py            # Mach-O symbol extraction
```

Dependencies: Python 3.11+, ffmpeg (audio verification), numpy + matplotlib (mesh preview).

---

## Reproduce

```bash
# 1. Unpack GooBall-Win.zip (or the Mac .dmg) to get the Data/ directory (incl. sharedassets.assets)
# 2. Extract audio
python tools/extract_audio_final.py
python tools/ogg_rebuild.py
# 3. Extract meshes
python tools/mesh_extract4.py
# 4. Extract textures
python tools/extract_textures.py
# 5. Extract text / scripts / behaviours
python tools/textmesh_extract.py
python tools/extract_mb.py
```

---

## Roadmap

- [x] Object-table parsing (SerializedFile v5)
- [x] Texture2D / AudioClip / Mesh / Shader / Material / AnimationClip full extraction
- [x] Scene hierarchy export (69 levels + sharedassets)
- [x] In-game text recovered (TextMesh 76, incl. `unity 1.6 conversion` evidence)
- [x] MonoScript list (105) recovered
- [x] MonoBehaviour instance field extraction (1440/1447, 83 script classes, byte-exact)
- [ ] Material/Shader → Godot material conversion
- [ ] Remaining 14 degenerate meshes
- [x] **Win11 playable release**: original Windows player (double-click `开始游戏.bat`)

---

## Disclaimer

This project is for **technical research and digital preservation** purposes only. GooBall and all its assets
are copyrighted by the original authors and publishers (Over The Edge / Ambrosia Software). Because the original
platform and distribution channels are defunct, this repository archives the lost assets for preservation.
