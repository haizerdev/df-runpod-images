"""Ваги fp32 → bf16 на місці (той самий файл і ті самі імена тензорів): ACE-Step однаково вантажить у bf16,
а образ стає вдвічі меншим (XL SFT 19 → 9.5 ГБ) — pod тягне його вдвічі швидше.
.venv/bin/python bf16.py <файл.safetensors> [...]"""
import sys

import torch
from safetensors.torch import load_file, save_file

for f in sys.argv[1:]:
    t = load_file(f)
    t = {k: (v.to(torch.bfloat16) if v.dtype == torch.float32 else v).contiguous() for k, v in t.items()}
    save_file(t, f + ".tmp", metadata={"format": "pt"})
    del t
    import os
    os.replace(f + ".tmp", f)
    print("bf16", f, os.path.getsize(f) >> 20, "MB")
