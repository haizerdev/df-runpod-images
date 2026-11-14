# Образ df-comfy: ComfyUI + Wan 2.2 I2V 14B (fp8 + lightx2v 4 кроки) + Illustrious XL — pod RunPod лише запускає.
# Збирається в GitHub Actions (haizerdev/df-runpod-images, .github/workflows/df-comfy.yml) → ghcr.io/<owner>/df-comfy.
# Великі моделі лежать шматками по 4 ГБ (шар ≤ 5 ГБ), агент збирає їх на старті pod-а (~1–2 хв, без мережі).
# офіційний PyTorch 2.8 + CUDA 12.6 (драйвери RunPod 12.6+), runtime — без зайвих ГБ
FROM pytorch/pytorch:2.8.0-cuda12.6-cudnn9-runtime

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates libgl1 libglib2.0-0  && rm -rf /var/lib/apt/lists/*

ARG COMFY_REF=master
RUN git clone https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI \
 && cd /opt/ComfyUI && git checkout "$COMFY_REF" && git rev-parse HEAD > /opt/comfy_ref \
 && python3 -m pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache

COPY models.json models.py /opt/df/
# шматок = окремий шар (python3 models.py plan — що в якому)
RUN python3 /opt/df/models.py part 0
RUN python3 /opt/df/models.py part 1
RUN python3 /opt/df/models.py part 2
RUN python3 /opt/df/models.py part 3
RUN python3 /opt/df/models.py part 4
RUN python3 /opt/df/models.py part 5
RUN python3 /opt/df/models.py part 6
RUN python3 /opt/df/models.py part 7
RUN python3 /opt/df/models.py part 8
RUN python3 /opt/df/models.py part 9
RUN python3 /opt/df/models.py part 10
RUN python3 /opt/df/models.py part 11
RUN python3 /opt/df/models.py part 12
RUN python3 /opt/df/models.py part 13
RUN python3 /opt/df/models.py part 14
RUN python3 /opt/df/models.py verify && du -sh /opt/df-parts /opt/ComfyUI/models \
 && python3 -c "import torch; print('torch', torch.__version__)"

ENV DF_PREBUILT=1 DF_COMFY=/opt/ComfyUI DF_PARTS=/opt/df-parts
LABEL org.opencontainers.image.description="Dragon Factory: ComfyUI + Wan 2.2 I2V 14B + Illustrious XL, предустановлено для RunPod"
# агент приходить зі змінною DF_AGENT (dockerStartCmd з factory/cloud_comfy.py) — образ не треба перезбирати при зміні агента
