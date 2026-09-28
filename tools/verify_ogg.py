import subprocess, glob, os, json

FF = r"D:\B++\WorkBuddy\tools\ffmpeg\bin\ffmpeg.exe"
audio_dir = r"D:\GooBall\extract\audio"
oggs = sorted(glob.glob(os.path.join(audio_dir, "*.ogg")))
res = {}
for f in oggs:
    p = subprocess.run([FF, "-v", "error", "-i", f, "-f", "null", "-"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = p.stderr.decode("utf-8", "replace")
    # also get duration/stream info
    pi = subprocess.run([FF, "-hide_banner", "-i", f],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    info = pi.stderr.decode("utf-8", "replace")
    # extract Duration and audio stream line
    dur = "?"
    for line in info.splitlines():
        if "Duration:" in line:
            dur = line.split("Duration:")[1].split(",")[0].strip()
        if "Audio:" in line:
            astr = line.strip()
    # classify errors
    bad = [l for l in err.splitlines() if ("End of file" in l or "invalid" in l.lower()
            or "Error" in l or "corrupt" in l.lower())]
    res[os.path.basename(f)] = {
        "exit": p.returncode, "dur": dur, "errlines": bad[:5],
        "bytes": os.path.getsize(f),
    }
    print(f"{os.path.basename(f):45} exit={p.returncode} dur={dur} errs={len(bad)}")
    for b in bad[:5]:
        print("    ", b[:120])

with open(os.path.join(audio_dir, "_ogg_verify.json"), "w") as fh:
    json.dump(res, fh, indent=2)
print("\nWROTE _ogg_verify.json")
