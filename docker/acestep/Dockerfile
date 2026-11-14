# Образ df-music: ACE-Step 1.5 + моделі XL уже всередині — pod RunPod лише запускає (нічого не ставить і не качає).
# Збирається в GitHub Actions (.github/workflows/df-music.yml) → ghcr.io/<owner>/df-music.
# База — тонка (python:3.11-slim): CUDA-бібліотеки приходять з колесами torch cu128 у venv,
# драйвер і nvidia-smi дає RunPod. Образ ~30 ГБ замість 61 — pod тягне його вдвічі швидше.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 UV_LINK_MODE=copy UV_PYTHON_PREFERENCE=only-system HF_HUB_DISABLE_TELEMETRY=1
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential ca-certificates curl \
      ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/* \
 && python3 -m pip install --no-cache-dir uv huggingface_hub

# код ACE-Step (закріплений коміт) + venv
ARG ACE_REF=main
RUN git clone https://github.com/ACE-Step/ACE-Step-1.5 /opt/ACE-Step-1.5 \
 && cd /opt/ACE-Step-1.5 && git checkout "$ACE_REF" && git rev-parse HEAD > /opt/ace_ref \
 && (uv sync --frozen || uv sync) \
 && uv cache clean && rm -rf /root/.cache

COPY fetch.py bf16.py verify.py /opt/
WORKDIR /opt/ACE-Step-1.5
# основний репозиторій (VAE, текстовий енкодер, turbo, LM 1.7B) — ACE-Step перевіряє його наявність
RUN python3 /opt/fetch.py ACE-Step/Ace-Step1.5 checkpoints "-acestep-5Hz-lm-1.7B/*" "-acestep-v15-turbo/*"
RUN python3 /opt/fetch.py ACE-Step/Ace-Step1.5 checkpoints "acestep-5Hz-lm-1.7B/*"
RUN python3 /opt/fetch.py ACE-Step/Ace-Step1.5 checkpoints "acestep-v15-turbo/*"
# XL SFT: 4 шматки по 5 ГБ fp32 → bf16 по 2.5 ГБ (ACE-Step однаково працює в bf16), по шару на кожен
# усе, крім ваг: silence_latent.pt, конфіги, код моделі (без silence_latent.pt XL не ініціалізується)
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "-model-*.safetensors"
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "model-00001-*" \
 && .venv/bin/python /opt/bf16.py checkpoints/acestep-v15-xl-sft/model-00001-*.safetensors
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "model-00002-*" \
 && .venv/bin/python /opt/bf16.py checkpoints/acestep-v15-xl-sft/model-00002-*.safetensors
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "model-00003-*" \
 && .venv/bin/python /opt/bf16.py checkpoints/acestep-v15-xl-sft/model-00003-*.safetensors
RUN python3 /opt/fetch.py ACE-Step/acestep-v15-xl-sft checkpoints/acestep-v15-xl-sft "model-00004-*" \
 && .venv/bin/python /opt/bf16.py checkpoints/acestep-v15-xl-sft/model-00004-*.safetensors
# LM 4B (уже bf16)
RUN python3 /opt/fetch.py ACE-Step/acestep-5Hz-lm-4B checkpoints/acestep-5Hz-lm-4B "-model-*.safetensors"
RUN python3 /opt/fetch.py ACE-Step/acestep-5Hz-lm-4B checkpoints/acestep-5Hz-lm-4B "model-00001-*"
RUN python3 /opt/fetch.py ACE-Step/acestep-5Hz-lm-4B checkpoints/acestep-5Hz-lm-4B "model-00002-*"
RUN rm -rf /root/.cache checkpoints/.cache */.cache 2>/dev/null; du -sh checkpoints/* /opt/ACE-Step-1.5/.venv && ls checkpoints/acestep-v15-xl-sft checkpoints/acestep-v15-turbo \
 && test -f checkpoints/acestep-v15-xl-sft/silence_latent.pt \
 && python3 /opt/verify.py  && .venv/bin/python -c "import torch, acestep, acestep.api_server, acestep.llm_inference, safetensors.torch as st; from acestep.core.generation.handler import init_service_loader; h = st.load_file('checkpoints/acestep-v15-xl-sft/model-00001-of-00004.safetensors'); assert all(v.dtype == torch.bfloat16 for v in h.values() if v.is_floating_point()); print('acestep ok, torch', torch.__version__, 'xl bf16 ok')"

LABEL org.opencontainers.image.description="Dragon Factory: ACE-Step 1.5 XL SFT (bf16) + LM 4B, предустановлено для RunPod"
# агент приходить зі змінною DF_AGENT (dockerStartCmd з factory/cloud_music.py) — образ не треба перезбирати при зміні агента
