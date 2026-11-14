"""Моделі образу df-comfy: скачати шматок (окремий RUN = шар ≤ 4 ГБ) / зібрати / перевірити.

  python3 models.py part <i>        скачати шматок i (по всіх моделях — сквозна нумерація, див. plan)
  python3 models.py plan            список шматків (для генерації Dockerfile)
  python3 models.py verify          sha256 кожної моделі по шматках (на збірці, нічого не пише)
  python3 models.py assemble        зібрати великі моделі зі шматків у ComfyUI/models (на старті pod-а, ~1 хв)

Маленькі моделі (≤ PART) кладуться одразу в /opt/ComfyUI/models/<dir>/, великі — шматками в /opt/df-parts/.
"""
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODELS = json.loads((HERE / "models.json").read_text(encoding="utf-8"))
PART = 4 << 30
COMFY = Path(os.environ.get("DF_COMFY", "/opt/ComfyUI"))
PARTS = Path(os.environ.get("DF_PARTS", "/opt/df-parts"))


def plan():
    out = []
    for m in MODELS:
        n = (m["size"] + PART - 1) // PART
        for k in range(n):
            out.append((m, k, n))
    return out


def _dst(m, k, n):
    return COMFY / "models" / m["dir"] / m["name"] if n == 1 else PARTS / f"{m['name']}.part{k:02d}"


def part(i):
    m, k, n = plan()[i]
    a, b = k * PART, min((k + 1) * PART, m["size"]) - 1
    dst = _dst(m, k, n)
    dst.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(6):
        try:
            req = urllib.request.Request(m["url"], headers={"User-Agent": "dragon-factory", "Range": f"bytes={a}-{b}"})
            with urllib.request.urlopen(req, timeout=120) as r, open(dst, "wb") as f:
                while True:
                    c = r.read(16 << 20)
                    if not c:
                        break
                    f.write(c)
            if dst.stat().st_size == b - a + 1:
                print("ok", dst, dst.stat().st_size)
                return
            raise RuntimeError(f"размер {dst.stat().st_size} != {b - a + 1}")
        except Exception as e:
            print("retry", m["name"], k, e, flush=True)
    sys.exit(f"не скачался {m['name']} part {k}")


def _files(m):
    n = (m["size"] + PART - 1) // PART
    return [_dst(m, k, n) for k in range(n)]


def verify():
    bad = []
    for m in MODELS:
        h = hashlib.sha256()
        for p in _files(m):
            with open(p, "rb") as f:
                for c in iter(lambda: f.read(16 << 20), b""):
                    h.update(c)
        ok = h.hexdigest() == m["sha256"]
        print("✓" if ok else "✗", m["name"])
        if not ok:
            bad.append(m["name"])
    if bad:
        sys.exit("битые: " + ", ".join(bad))


def assemble(log=print):
    for m in MODELS:
        files = _files(m)
        if len(files) == 1:
            continue
        dst = COMFY / "models" / m["dir"] / m["name"]
        if dst.exists() and dst.stat().st_size == m["size"]:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_suffix(".tmp")
        with open(tmp, "wb") as out:
            for p in files:
                with open(p, "rb") as f:
                    for c in iter(lambda: f.read(64 << 20), b""):
                        out.write(c)
        if tmp.stat().st_size != m["size"]:
            raise RuntimeError(f"сборка {m['name']}: размер не совпал")
        tmp.replace(dst)
        log(f"собрана модель {m['name']} ({m['size'] >> 20} МБ)")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "part":
        part(int(sys.argv[2]))
    elif cmd == "plan":
        for i, (m, k, n) in enumerate(plan()):
            print(i, m["name"], k, n)
    elif cmd == "verify":
        verify()
    elif cmd == "assemble":
        assemble()
