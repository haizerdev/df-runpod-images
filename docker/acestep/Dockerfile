# Образ df-music: ACE-Step 1.5 + моделі XL уже всередині — pod RunPod лише запускає (нічого не ставить і не качає).
# Збирається в GitHub Actions (.github/workflows/acestep.yml) → ghcr.io/<owner>/df-music.
# База — та сама, що й у pod-ів голосу: на хостах RunPod вона часто вже в кеші.
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

ENV PYTHONUNBUFFERED=1 UV_LINK_MODE=copy UV_PYTHON_PREFERENCE=only-system HF_HUB_DISABLE_TELEMETRY=1
RUN python3 -m pip install --no-cache-dir uv huggingface_hub

# код ACE-Step (закріплений коміт) + venv
ARG ACE_REF=main
RUN git clone https://github.com/ACE-Step/ACE-Step-1.5 /opt/ACE-Step-1.5 \
 && cd /opt/ACE-Step-1.5 && git checkout "$ACE_REF" && git rev-parse HEAD > /opt/ace_ref \
 && (uv sync --frozen || uv sync) \
 && uv cache clean && rm -rf /root/.cache

COPY fetch.py /opt/fetch.py
WORKDIR /opt/ACE-Step-1.5
# основний репозиторій (VAE, текстовий енкодер, turbo, LM 1.7B — на 24 ГБ картах)
RUN python3 /opt/fetch.py ACE-Step/Ace-Step1.5 checkpoints "*.json" "*.md" "*.txt" "*.py" "*.jinja" "vae/*" "Qwen3-Embedding-0.6B/*"
RUN python3 /opt/fetch.py ACE-Step/Ace-Step1.5 checkpoints "acestep-5Hz-lm-1.7B/*"
RUN python3 /opt/fetch.py ACE-Step/Ace-Step1.5 checkpoints "acestep-v15-turbo/*"
# XL SFT (4 шматки по 5 ГБ — по шару на кожен)
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "*.json" "*.md" "*.py" "*.txt"
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "model-00001-*"
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "model-00002-*"
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "model-00003-*"
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "model-00004-*"
# LM 4B (48 ГБ карти)
RUN python3 /opt/fetch.py ACE-Step/acestep-5Hz-lm-4B checkpoints/acestep-5Hz-lm-4B "*.json" "*.md" "*.txt" "*.jinja"
RUN python3 /opt/fetch.py ACE-Step/acestep-5Hz-lm-4B checkpoints/acestep-5Hz-lm-4B "model-00001-*"
RUN python3 /opt/fetch.py ACE-Step/acestep-5Hz-lm-4B checkpoints/acestep-5Hz-lm-4B "model-00002-*"
RUN rm -rf /root/.cache checkpoints/.cache */.cache 2>/dev/null; du -sh checkpoints/* && .venv/bin/python -c "import acestep, torch; print('acestep ok, torch', torch.__version__)"

LABEL org.opencontainers.image.description="Dragon Factory: ACE-Step 1.5 XL SFT + LM 4B, предустановлено для RunPod"
# агент приходить зі змінною DF_AGENT (dockerStartCmd з factory/cloud_music.py) — образ не треба перезбирати при зміні агента
