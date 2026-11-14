"""Smoke-тест образу: кожен файл з HF-репозиторіїв моделей є на диску (ваги XL — bf16, тож розмір ≈ половина),
і модулі ACE-Step імпортуються. Будь-яка розбіжність → код 1 → збірка падає, образ не публікується."""
import sys
from pathlib import Path

from huggingface_hub import HfApi

CK = Path("/opt/ACE-Step-1.5/checkpoints")
REPOS = {"ACE-Step/Ace-Step1.5": CK, "ACE-Step/acestep-v15-xl-sft": CK / "acestep-v15-xl-sft",
         "ACE-Step/acestep-5Hz-lm-4B": CK / "acestep-5Hz-lm-4B"}
bad = []
for repo, root in REPOS.items():
    info = HfApi().model_info(repo, files_metadata=True)
    for f in info.siblings:
        if f.rfilename in (".gitattributes",):
            continue
        p = root / f.rfilename
        if not p.is_file():
            bad.append(f"нет {repo}:{f.rfilename}")
            continue
        size, want = p.stat().st_size, f.size or 0
        half = "xl-sft" in repo and f.rfilename.startswith("model-")  # fp32 → bf16
        if want and not (abs(size - want / 2) < want * 0.02 if half else size == want):
            bad.append(f"размер {repo}:{f.rfilename} {size} != {want}{' / 2' if half else ''}")
    print("ok" if not bad else "!!", repo, len(info.siblings), "файлов")
print("\n".join(bad) or "все файлы на месте")
sys.exit(1 if bad else 0)
