# ZODIAK News Bot

Bot yang tiap 15 menit cek berita forex/komoditi, pilih yang berdampak besar (Fed, CPI, NFP, emas, USD, minyak, dll),
ringkas ke Bahasa Indonesia pakai Gemini (Google, tier gratis), lalu kirim ke channel Telegram. Semuanya Rp0: GitHub Actions + Gemini gratis.

Bot ini **hanya kirim berita + ringkasan netral + link sumber**. Tidak ada rekomendasi buy/sell (diatur di prompt).

## Setup (sekali saja, ±15 menit)

### 1. Bikin bot Telegram
1. Chat **@BotFather** → `/newbot` → isi nama & username (akhiran `bot`).
2. Simpan **token** yang dikasih. Jangan kirim ke siapa pun, jangan taruh di kode.
   Kalau bocor: `/revoke` di BotFather.

### 2. Jadikan bot admin channel
Buka channel **ZODIAK FX TRADE** → Administrators → Add Admin → pilih bot lu →
aktifkan izin **Post Messages** (sisanya boleh mati).

### 3. Siapkan 3 secret
| Nama | Isi |
|---|---|
| `TELEGRAM_BOT_TOKEN` | token dari BotFather |
| `TELEGRAM_CHAT_ID` | `@username_channel` (contoh: `@zodiakfxtrade`; lihat "share link" di info channel) |
| `GEMINI_API_KEY` | API key gratis dari aistudio.google.com → Get API key |

### 4. Taruh di GitHub
1. Bikin repo baru di GitHub. **Disarankan Public** (lihat catatan menit di bawah). Secret tetap aman, tidak ikut terlihat.
2. Upload semua isi folder ini (termasuk folder `.github`).
3. Repo → **Settings → Secrets and variables → Actions → New repository secret** → masukkan 3 secret di atas.
4. Repo → **Settings → Actions → General → Workflow permissions** → pilih **Read and write permissions** → Save.

### 5. Tes bertahap (urutan penting)
Repo → tab **Actions** → **ZODIAK News Bot** → **Run workflow**:
1. `check`: tes semua feed RSS. Lihat log, pastikan minimal beberapa `[OK]`. Feed yang `[GAGAL]` hapus/ganti di `FEEDS` (atas `news_bot.py`).
2. `dry`: bot menampilkan berita yang akan dikirim di log, **belum kirim**. Cek hasil ringkasannya.
3. `run`: kirim sungguhan. Cek channel.

Setelah itu jalan otomatis tiap 15 menit.

## Pengaturan
Di `news.yml` (bagian `env`, hapus `#` untuk mengaktifkan):
- `MIN_SCORE` (default 4): naikkan ke 5-6 kalau terlalu banyak berita, turunkan ke 3 kalau terlalu sepi.
- `MAX_PER_RUN` (3) dan `MAX_PER_DAY` (15): batas biar channel tidak spam.
- `MAX_AGE_HOURS` (3): berita lebih tua dari ini diabaikan.

Kata kunci filter dan sumber berita ada di bagian atas `news_bot.py`.

## Catatan penting
- **Menit GitHub Actions:** repo **private** di akun gratis dapat 2.000 menit/bulan, sedangkan jadwal tiap 15 menit butuh ±2.900 menit.
  Pilih: repo public (gratis tanpa batas), atau ganti cron jadi `*/30 * * * *` kalau mau private.
- **Cron GitHub bisa telat** beberapa menit, kadang lebih saat jam sibuk. Jadi ini "hampir real-time", bukan detik.
- **Workflow terjadwal bisa dimatikan otomatis** GitHub kalau repo tidak ada aktivitas ±60 hari. Kalau bot tiba-tiba diam, cek tab Actions dan klik Enable.
- **Gemini gratis:** batas pemakaian gratis ditentukan Google dan bisa berubah. Kalau log menunjukkan `429`, berarti batas tercapai; turunkan `MAX_PER_DAY` atau tunggu besok. Model dipilih otomatis; kalau Google ganti nama model, isi `GEMINI_MODEL` di `news.yml`.
- **Kalau bot gagal** (token salah, bot bukan admin, API key ditolak), workflow ditandai merah dan GitHub mengirim email notifikasi.
- **Hak cipta:** bot hanya memakai judul + cuplikan RSS, meringkas dengan kata sendiri, dan selalu menautkan sumber. Jangan ubah jadi menyalin artikel penuh.
- Feed RSS pihak ketiga bisa berubah/mati sewaktu-waktu. Jalankan mode `check` sesekali.
