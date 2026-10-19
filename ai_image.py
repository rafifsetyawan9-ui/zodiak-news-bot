"""Ilustrasi AI untuk latar kartu berita. Gratis (Pollinations, model Flux), tanpa API key.
Kalau gagal/lambat, kembalikan None -> kartu tetap dibuat dengan latar abu-abu polos."""
from __future__ import annotations

import io
import os
import random
from urllib.parse import quote

import requests
from PIL import Image

STYLE = ("cinematic editorial photo illustration, financial news, dramatic lighting, "
         "high detail, no text, no letters, no logos, no watermark, no real people, no faces")


def generate(prompt: str, seed: int | None = None, timeout: int = 60) -> Image.Image | None:
    full = f"{prompt}. {STYLE}"
    url = (f"https://image.pollinations.ai/prompt/{quote(full)}"
           f"?width=1080&height=720&nologo=true&model=flux&seed={seed or random.randint(1, 10**6)}")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ZodiakNewsBot/1.0)"}
    token = os.environ.get("POLLINATIONS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        if not resp.headers.get("content-type", "").startswith("image/"):
            raise ValueError(f"bukan gambar: {resp.headers.get('content-type')}")
        return Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception as exc:
        print(f"[WARN] ilustrasi AI gagal: {str(exc)[:150]}", flush=True)
        return None
