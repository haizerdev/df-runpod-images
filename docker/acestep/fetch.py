"""Скачати частину репозиторію HF у образ (окремий RUN = окремий шар ≤ 5 ГБ: ghcr не любить шари > 10 ГБ).
python3 fetch.py <repo> <куди> <шаблон> [шаблон…]"""
import sys

from huggingface_hub import snapshot_download

repo, dst, *patterns = sys.argv[1:]
snapshot_download(repo, local_dir=dst, allow_patterns=patterns or None)
print("ok", repo, patterns)
