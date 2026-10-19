"""
Kartu berita ZODIAK (1080x1080 PNG) untuk tiap postingan bot.
Gaya mengikuti postingan IG ZODIAK: latar abu-abu, judul putih tebal bergaris gelap,
label merah "HIGH IMPACT NEWS", logo asli di kanan atas, @zodiakfxtrade di kiri bawah.
Dibuat dengan kode (Pillow), jadi gratis, cepat, dan selalu konsisten.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).with_name("assets")
W = H = 1080
BG = (187, 187, 187)
WHITE = (255, 255, 255)
INK = (20, 20, 20)
MUTED = (70, 70, 70)
RED = (170, 40, 40)
GREEN = (28, 120, 60)
DARK = (45, 45, 45)
GOLD = (176, 122, 20)
PANEL = (204, 204, 204)
PANEL_LINE = (150, 150, 150)
WIB = timezone(timedelta(hours=7))
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
         "September", "Oktober", "November", "Desember"]


def _font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(ASSETS / "fonts" / f"Poppins-{weight}.ttf"), size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _fit_title(draw, text: str, max_w: int, max_h: int, max_lines: int = 4):
    """Cari ukuran font terbesar yang muat di area judul (maks 4 baris)."""
    for size in (78, 70, 62, 56, 50, 45):
        font = _font("ExtraBold", size)
        lines = _wrap(draw, text, font, max_w)
        if len(lines) <= max_lines and len(lines) * int(size * 1.12) <= max_h:
            return font, lines
    font = _font("ExtraBold", 45)
    lines = _wrap(draw, text, font, max_w)[:max_lines]
    lines[-1] = lines[-1].rstrip(".,") + "…"
    return font, lines


def _id_num(x: float, dec: int = 2) -> str:
    return f"{x:,.{dec}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _tanggal(dt: datetime) -> str:
    d = dt.astimezone(WIB)
    return f"{HARI[d.weekday()]}, {d.day} {BULAN[d.month - 1]} {d.year} · {d:%H:%M} WIB"


def _apply_background(img: Image.Image, bg: Image.Image) -> None:
    """Ilustrasi AI di bagian atas (0-640px), digelapkan sedikit, lalu memudar ke abu-abu ZODIAK."""
    TOP_H, FADE = 640, 170
    bg = bg.convert("RGB")
    scale = max(W / bg.width, TOP_H / bg.height)
    bg = bg.resize((int(bg.width * scale) + 1, int(bg.height * scale) + 1), Image.LANCZOS)
    left, top = (bg.width - W) // 2, (bg.height - TOP_H) // 2
    bg = bg.crop((left, top, left + W, top + TOP_H))
    bg = Image.blend(bg, Image.new("RGB", bg.size, (25, 25, 25)), 0.42)  # gelapkan biar judul terbaca
    mask = Image.new("L", (W, TOP_H), 255)
    md = ImageDraw.Draw(mask)
    for i in range(FADE):
        md.line((0, TOP_H - FADE + i, W, TOP_H - FADE + i), fill=int(255 * (1 - i / FADE)))
    img.paste(bg, (0, 0), mask)


def make_card(judul: str, *, high_impact: bool, aset: list[str], move: dict | None,
              published: datetime | None, source: str, out_path: str | Path,
              background: Image.Image | None = None) -> Path:
    img = Image.new("RGB", (W, H), BG)
    if background is not None:
        _apply_background(img, background)
    d = ImageDraw.Draw(img)

    # Logo asli (tidak diubah) di kanan atas
    logo = Image.open(ASSETS / "logo.png").convert("RGBA")
    img.paste(logo, (W - 40 - logo.width, 36), logo)
    d.text((60, 92), "ZODIAK NEWS", font=_font("Bold", 28), fill=WHITE if background is not None else INK, anchor="lm",
           stroke_width=2 if background is not None else 0, stroke_fill=INK)
    if background is not None:
        d.text((60, 128), "Ilustrasi: AI", font=_font("Medium", 20), fill=(230, 230, 230), anchor="lm")

    # Label kategori
    label = "HIGH IMPACT NEWS" if high_impact else "MARKET NEWS"
    f_pill = _font("Bold", 30)
    tw = d.textlength(label, font=f_pill)
    pw, ph = int(tw + 64), 58
    px, py = (W - pw) // 2, 180
    d.rounded_rectangle((px, py, px + pw, py + ph), radius=ph // 2, fill=RED if high_impact else DARK)
    d.text((W // 2, py + ph // 2), label, font=f_pill, fill=WHITE, anchor="mm")

    # Tata letak tetap (atas ke bawah): label 180 | judul 268-590 | garis | chip 625 | panel 700-880 | info 935 | footer
    TITLE_TOP, TITLE_BOTTOM = py + ph + 30, 590
    f_title, lines = _fit_title(d, judul.upper(), W - 160, TITLE_BOTTOM - TITLE_TOP)
    lh = int(f_title.size * 1.12)
    y = TITLE_TOP + (TITLE_BOTTOM - TITLE_TOP - lh * len(lines)) // 2
    for line in lines:
        d.text((W // 2 + 4, y + 5), line, font=f_title, fill=(90, 90, 90), anchor="ma")  # bayangan
        d.text((W // 2, y), line, font=f_title, fill=WHITE, anchor="ma",
               stroke_width=4, stroke_fill=INK)
        y += lh
    d.line((160, 605, W - 160, 605), fill=WHITE, width=4)

    # Chip aset
    chips = [f"#{a}" for a in aset[:4]]
    if chips:
        f_chip = _font("SemiBold", 28)
        widths = [int(d.textlength(c, font=f_chip)) + 44 for c in chips]
        total = sum(widths) + 16 * (len(chips) - 1)
        x = (W - total) // 2
        for c, w in zip(chips, widths):
            d.rounded_rectangle((x, 628, x + w, 678), radius=25, fill=PANEL, outline=PANEL_LINE, width=2)
            d.text((x + w // 2, 653), c, font=f_chip, fill=INK, anchor="mm")
            x += w + 16

    # Panel gerak XAUUSD
    box_top = 705
    box = (150, box_top, W - 150, box_top + 180)
    d.rounded_rectangle(box, radius=28, fill=PANEL, outline=PANEL_LINE, width=2)
    cx = W // 2
    if move:
        up = move["pct"] > 0.005
        down = move["pct"] < -0.005
        color = GREEN if up else RED if down else MUTED
        d.text((cx, box_top + 34), "XAUUSD SEJAK BERITA TERBIT", font=_font("SemiBold", 26), fill=MUTED, anchor="mm")
        pct = f"{'+' if move['pct'] > 0 else ''}{_id_num(move['pct'])}%"
        f_pct = _font("ExtraBold", 68)
        tri = 36 if (up or down) else 0
        pw2 = d.textlength(pct, font=f_pct)
        start = cx - (pw2 + tri + (16 if tri else 0)) / 2
        ay = box_top + 92
        if up:
            d.polygon([(start, ay + 15), (start + tri, ay + 15), (start + tri / 2, ay - 18)], fill=color)
        elif down:
            d.polygon([(start, ay - 15), (start + tri, ay - 15), (start + tri / 2, ay + 18)], fill=color)
        d.text((start + tri + (16 if tri else 0), ay), pct, font=f_pct, fill=color, anchor="lm")
        d.text((cx, box_top + 150), f"dari {_id_num(move['from'])} ke {_id_num(move['to'])}",
               font=_font("Medium", 28), fill=INK, anchor="mm")
    else:
        d.text((cx, box_top + 65), "FOKUS: XAUUSD", font=_font("ExtraBold", 48), fill=GOLD, anchor="mm")
        d.text((cx, box_top + 125), "Baca dampaknya ke emas di caption", font=_font("Medium", 28),
               fill=INK, anchor="mm")

    # Tanggal + sumber
    info = []
    if published:
        info.append(_tanggal(published))
    info.append(f"Sumber: {source}")
    d.text((cx, 935), "  ·  ".join(info), font=_font("Medium", 25), fill=INK, anchor="mm")

    # Footer
    f_foot = _font("Medium", 26)
    d.text((60, H - 58), "@zodiakfxtrade", font=f_foot, fill=INK, anchor="lm")
    d.text((W - 60, H - 58), "Bukan ajakan jual/beli", font=f_foot, fill=INK, anchor="rm")

    out = Path(out_path)
    img.save(out, "PNG", optimize=True)
    return out
