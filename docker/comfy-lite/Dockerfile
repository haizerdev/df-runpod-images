# Образ df-comfy-lite: лише ComfyUI + PyTorch 2.8 (CUDA 12.8: Ampere/Ada/Blackwell), БЕЗ моделей (~4–5 ГБ замість 45).
# Моделі лежать на RunPod Network Volume df-models (/workspace/df-models), агент підключає їх через extra_model_paths.
# Збирається в GitHub Actions (haizerdev/df-runpod-images, .github/workflows/df-comfy-lite.yml).
FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates libgl1 libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

ARG COMFY_REF=master
RUN git clone https://github.com/comfyanonymous/ComfyUI /opt/ComfyUI \
 && cd /opt/ComfyUI && git checkout "$COMFY_REF" && git rev-parse HEAD > /opt/comfy_ref \
 && python3 -m pip install --no-cache-dir -r requirements.txt && rm -rf /root/.cache \
 && python3 -c "import torch; print('torch', torch.__version__, torch.version.cuda)"

ENV DF_PREBUILT=1 DF_COMFY=/opt/ComfyUI DF_LITE=1
LABEL org.opencontainers.image.description="Dragon Factory: ComfyUI без моделей (модели с RunPod Network Volume)"
# агент приходить зі змінною DF_AGENT (dockerStartCmd з factory/cloud_comfy.py)
