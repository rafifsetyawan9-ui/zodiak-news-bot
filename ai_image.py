"""Ilustrasi AI untuk latar kartu berita. Gratis (Pollinations, model Flux), tanpa API key.
Kalau gagal/lambat, kembalikan None -> kartu tetap dibuat dengan latar abu-abu polos."""
from __future__ import annotations

import io
import os
import random
import time
from urllib.parse import quote

import requests
from PIL import Image

STYLE = ("hyper-realistic 3D render, cinematic product shot, dark moody background, dramatic rim lighting, "
         "glowing light particles and sparks, shallow depth of field, octane render, 8k, sharp focus, "
         "no text, no letters, no watermark, no real people, no faces")


def generate(prompt: str, seed: int | None = None, timeout: int = 60) -> Image.Image | None:
    full = f"{prompt}. {STYLE}"
    url = (f"https://image.pollinations.ai/prompt/{quote(full)}"
           f"?width=1280&height=720&enhance=true&nologo=true&model=flux&seed={seed or random.randint(1, 10**6)}")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ZodiakNewsBot/1.0)"}
    token = os.environ.get("POLLINATIONS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    last = None
    for attempt in range(3):  # layanan gratis membatasi permintaan beruntun: tunggu lalu coba lagi
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 429:
                raise ValueError("429 terlalu cepat")
            resp.raise_for_status()
            if not resp.headers.get("content-type", "").startswith("image/"):
                raise ValueError(f"bukan gambar: {resp.headers.get('content-type')} {resp.text[:120]}")
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            print(f"[INFO] ilustrasi AI {img.width}x{img.height}", flush=True)
            return img
        except Exception as exc:
            last = exc
            time.sleep(15 * (attempt + 1))
    print(f"[WARN] ilustrasi AI gagal: {str(last)[:200]}", flush=True)
    return None
