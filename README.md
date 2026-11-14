# df-runpod-images

Docker-образы для RunPod: всё предустановлено, pod только запускается.

| Папка | Образ | Что внутри |
|---|---|---|
| `docker/acestep` | `ghcr.io/haizerdev/df-music` | ACE-Step 1.5 + модели XL SFT (4B), LM 4B и 1.7B, turbo, VAE |
| `docker/comfy` | `ghcr.io/haizerdev/df-comfy` | ComfyUI + Wan 2.2 I2V 14B fp8 + lightx2v 4 шага, umt5, VAE, Illustrious XL v2.0 (шарды по 4 ГБ, собираются на старте pod-а) |

Сборка: Actions → нужный workflow → Run workflow. Модели — MIT (ACE-Step), код моделей — с их GitHub.
