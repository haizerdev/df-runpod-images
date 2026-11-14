"""Скачати частину репозиторію HF у образ (окремий RUN = окремий шар ≤ 5 ГБ: ghcr не любить шари > 10 ГБ).
python3 fetch.py <repo> <куди> <шаблон> [шаблон…]; шаблон з «-» на початку — виключити (напр. -model-*.safetensors)."""
import sys

from huggingface_hub import snapshot_download

repo, dst, *patterns = sys.argv[1:]
allow = [p for p in patterns if not p.startswith("-")] or None
ignore = [p[1:] for p in patterns if p.startswith("-")] or None
snapshot_download(repo, local_dir=dst, allow_patterns=allow, ignore_patterns=ignore)
print("ok", repo, patterns)
