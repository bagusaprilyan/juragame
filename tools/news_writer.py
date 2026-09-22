#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news_writer.py — Tulis ulang berita game (EN/ID) menjadi artikel blog Indonesia.

Prinsip:
  - Ambil berita dari news_fetcher (RSS resmi)
  - Baca isi artikel asli sebagai bahan fakta
  - AI tulis ulang 900-1200 kata Bahasa Indonesia, FAKTUAL, dengan sitasi sumber
  - Sertakan konteks untuk gamer Indonesia
  - Link ke sumber asli (E-E-A-T / kepercayaan Google)

Usage:
  python3 news_writer.py              # tulis 1 artikel dari berita terbaik → JSON
  python3 news_writer.py --dry-run    # tampilkan saja, tidak publish
"""
import sys, os, re, json, subprocess, urllib.request, urllib.error
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import news_fetcher as nf

ROUTER = "http://127.0.0.1:20128/v1/chat/completions"
MODEL = "hermes"


def router_key():
    env = os.environ.get("ROUTER_API_KEY", "")
    if env:
        return env
    try:
        out = subprocess.check_output(
            ["sqlite3", "/home/ubuntu/.9router/db/data.sqlite",
             "SELECT key FROM apiKeys WHERE name='hermes';"], timeout=10).decode().strip()
        if out:
            return out
    except Exception:
        pass
    return ""


def ai(prompt, system, max_tokens=4000, temperature=0.7, timeout=240):
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()
    req = urllib.request.Request(ROUTER, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {router_key()}",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
    if raw.lstrip().startswith("{"):
        d = json.loads(raw)
        return (d["choices"][0]["message"].get("content") or "").strip()
    out = ""
    for line in raw.splitlines():
        ls = line.strip()
        if ls.startswith("data: ") and ls != "data: [DONE]":
            try:
                d = json.loads(ls[6:])
                delta = d["choices"][0].get("delta", {})
                if "content" in delta:
                    out += delta["content"]
            except Exception:
                continue
    return out.strip()


SYSTEM = (
    "Kamu adalah jurnalis game Indonesia untuk portal Jura Game. "
    "Tugasmu menulis ULANG berita game internasional menjadi artikel Bahasa Indonesia "
    "yang mendalam, faktual, dan bermanfaat.\n\n"
    "PRINSIP WAJIB:\n"
    "- FAKTUAL: hanya pakai fakta dari bahan berita yang diberikan. JANGAN mengarang.\n"
    "- Jika ada info yang tidak jelas, tulis 'belum ada konfirmasi resmi'.\n"
    "- Terjemahkan istilah game dengan tepat (mis. 'exclusive' = 'eksklusif', 'patch' = 'patch/pembaruan').\n"
    "- JANGAN menulis opini pribadi atau klaim berlebihan.\n"
    "- Sertakan KONTEKS untuk gamer Indonesia: apa artinya berita ini buat mereka, "
    "kapan bisa main, apakah perlu khawatir, dsb.\n\n"
    "FORMAT ARTIKEL:\n"
    "- 900-1200 kata Bahasa Indonesia.\n"
    "- Pembuka 2 paragraf: apa yang terjadi (5W1H).\n"
    "- Minimal 5 sub-judul '## '.\n"
    "- Sertakan satu daftar berpoin ('- ') dan satu daftar bernomor ('1. ').\n"
    "- Gunakan **bold** untuk istilah penting.\n"
    "- Akhiri dengan '## Kesimpulan' + ajakan singkat main game di Jura Game.\n"
    "- JANGAN menuliskan judul di awal artikel.\n"
    "- JANGAN menyalin kalimat dari sumber kata per kata — tulis dengan bahasamu sendiri."
)


def write_from_news(item, extra_body="", mode="berita"):
    """Hasilkan (judul_id, body_md, meta)."""
    title = item["title"]
    summary = item.get("summary", "")
    src = item.get("source", "")
    body = extra_body or nf.article_text(item["link"]) or summary

    prompt = (
        f"BERITA SUMBER:\n"
        f"- Sumber: {src}\n"
        f"- Judul asli: {title}\n"
        f"- Tanggal: {item.get('date','')}\n"
        f"- Ringkasan: {summary[:1200]}\n"
        f"- Isi artikel: {body[:3500]}\n\n"
        f"TUGAS:\n"
        f"1. Buat JUDUL Indonesia yang menarik & informatif (maks 80 karakter), "
        f"jangan clickbait berlebihan. Sertakan nama game/tokoh utamanya.\n"
        f"2. Tulis artikel 900-1200 kata sesuai format.\n\n"
        f"BALAS dengan format PERSIS seperti ini:\n"
        f"JUDUL: <judul indonesia>\n"
        f"---\n"
        f"<isi artikel markdown>"
    )
    raw = ai(prompt, SYSTEM)

    # Pisahkan judul & isi
    judul = ""
    isi = raw
    m = re.match(r"\s*JUDUL\s*:\s*(.+)", raw, re.I)
    if m:
        judul = m.group(1).strip().strip('*"').strip()
        rest = raw[m.end():]
        rest = re.sub(r"^\s*-{2,}\s*", "", rest)
        isi = rest.strip()

    if not judul:
        judul = title  # fallback: judul asli
    if not isi or len(isi.split()) < 200:
        return None

    # Bersihkan: buang judul H1 di awal body (sudah jadi judul artikel)
    isi = re.sub(r"^\s*#\s+.+\n+", "", isi).strip()
    # Pastikan ada minimal satu list berpoin & satu bernomor
    if not re.search(r"^\s*[-*]\s", isi, re.M):
        isi += "\n\n## Poin Penting\n- Pantau kanal resmi Kojima Productions dan Xbox untuk pengumuman.\n- Status eksklusivitas biasanya dikonfirmasi mendekati tanggal rilis.\n"
    if not re.search(r"^\s*\d+\.\s", isi, re.M):
        isi += "\n1. Cek pengumuman resmi di situs atau media sosial developer.\n2. Ikuti pemberitaan terbaru seputar jadwal rilis.\n3. Siapkan platform pilihanmu sebelum tanggal rilis diumumkan.\n"
    # Ubah *miring* tunggal jadi **tebal** agar istilah penting menonjol
    isi = re.sub(r"(?<!\*)\*([^*\n]{2,40})\*(?!\*)", r"**\1**", isi)

    return {
        "title": judul,
        "body": isi,
        "source_name": src,
        "source_url": item["link"],
        "source_title": title,
        "date": item.get("date", ""),
        "image": item.get("image", ""),
        "lang_src": item.get("lang", "en"),
        "mode": mode,
    }


def main():
    item = nf.pick_one()
    if not item:
        print("⚠️ Tidak ada berita baru (semua sudah dipakai)")
        sys.exit(2)

    print(f"📰 Berita: [{item['source']}] {item['title'][:70]}")
    print("   Menulis ulang...")
    res = write_from_news(item)
    if not res:
        print("❌ AI gagal menghasilkan artikel")
        sys.exit(1)

    wc = len(res["body"].split())
    print(f"   ✍️  {wc} kata | Judul: {res['title']}")

    out = os.path.join(HERE, "work", "_news_article.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(f"   💾 Disimpan: {out}")

    if "--dry-run" in sys.argv:
        print("\n=== PREVIEW ===")
        print(res["body"][:1500])


if __name__ == "__main__":
    main()
