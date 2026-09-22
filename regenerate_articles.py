#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate artikel blog juragame yang terlalu tipis (<500 kata) menjadi panjang (900-1200 kata).

Strategi:
  1. Baca articles.json dari GitHub.
  2. Untuk tiap artikel < 500 kata, minta AI menulis ulang versi panjang (judul sama).
  3. Update file blog/<slug>.html + articles.json + blog/index.html + sitemap.xml.

Usage:
  python3 regenerate_articles.py            # semua artikel tipis
  python3 regenerate_articles.py --limit 5  # hanya 5 pertama
  python3 regenerate_articles.py --slug xxx # satu artikel tertentu
"""
import json, base64, sys, os, re, time, urllib.request, urllib.error, yaml, random
from datetime import datetime

CONFIG_PATH = "/home/ubuntu/.hermes/profiles/saham/config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "bagusaprilyan/juragame"
BASE_URL = "https://juragame.com"
API = f"https://api.github.com/repos/{REPO}/contents"
def _load_router_key():
    """Ambil API key 9Router dari DB lokal (paling andal)."""
    env_key = os.environ.get("ROUTER_API_KEY", "")
    if env_key:
        return env_key
    keyfile = "/tmp/jgwork/hermes.key"
    if os.path.exists(keyfile):
        with open(keyfile) as f:
            k = f.read().strip()
        if k:
            return k
    try:
        import subprocess
        out = subprocess.check_output(
            ["sqlite3", "/home/ubuntu/.9router/db/data.sqlite",
             "SELECT key FROM apiKeys WHERE name='hermes';"],
            timeout=10).decode().strip()
        if out:
            return out
    except Exception:
        pass
    return ""

AI_API_URL = "http://127.0.0.1:20128/v1/chat/completions"
AI_API_KEY = _load_router_key()
AI_MODEL = "hermes"
GH = {"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "HermesAgent", "Content-Type": "application/json"}

MIN_WORDS = 850          # target minimal kata setelah regenerate
THRESHOLD = 500          # artikel di bawah ini dianggap tipis


def gh_get(path):
    url = f"{API}/{path}"
    req = urllib.request.Request(url, headers=GH)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.load(r)
        return base64.b64decode(d['content']).decode('utf-8'), d['sha']
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        raise


def gh_put(path, content, message):
    _, sha = gh_get(path)
    payload = {"message": message, "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
    if sha:
        payload["sha"] = sha
    req = urllib.request.Request(f"{API}/{path}", data=json.dumps(payload).encode(), method="PUT", headers=GH)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def slugify(title):
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug[:60].strip('-')


def md_to_html(md_text):
    lines = md_text.strip().split('\n')
    out, in_list, in_ol = [], False, False
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                out.append('</ul>'); in_list = False
            if in_ol:
                out.append('</ol>'); in_ol = False
            continue
        # Lewati baris "Judul: ..." (judul sudah ada di header artikel)
        if re.match(r'^(Judul|Title)\s*:', line, re.I):
            continue
        if line.startswith('### '):
            out.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('#### '):
            out.append(f'<h3>{line[5:]}</h3>')
        elif line.startswith('## '):
            out.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('# '):
            out.append(f'<h2>{line[2:]}</h2>')
        elif re.match(r'^\*\*.+\*\*:?\s*$', line):
            # Baris yang seluruhnya bold dianggap sub-judul (mis. "**Bagian 1**")
            out.append('<h2>' + re.sub(r'^\*\*|\*\*:?\s*$', '', line).strip() + '</h2>')
        elif line.startswith('- ') or line.startswith('* '):
            if in_ol:
                out.append('</ol>'); in_ol = False
            if not in_list:
                out.append('<ul>'); in_list = True
            out.append(f'<li>{line[2:]}</li>')
        elif re.match(r'^\d+\.\s', line):
            # "1. Judul" atau "1. **Judul**" → sub-judul; "1. teks" panjang → item daftar
            item = re.sub(r'^\d+\.\s', '', line)
            is_bold_head = bool(re.match(r'^\*\*.+\*\*:?\s*$', item))
            is_short_head = len(item.split()) <= 7 and not item.endswith(('.', ',', '!', '?'))
            if is_bold_head or is_short_head:
                if in_list:
                    out.append('</ul>'); in_list = False
                if in_ol:
                    out.append('</ol>'); in_ol = False
                head = re.sub(r'^\*\*|\*\*:?\s*$', '', item).strip()
                out.append(f'<h2>{head}</h2>')
            else:
                if in_list:
                    out.append('</ul>'); in_list = False
                if not in_ol:
                    out.append('<ol>'); in_ol = True
                out.append(f'<li>{item}</li>')
        else:
            if in_list:
                out.append('</ul>'); in_list = False
            if in_ol:
                out.append('</ol>'); in_ol = False
            out.append(f'<p>{line}</p>')
    if in_list:
        out.append('</ul>')
    if in_ol:
        out.append('</ol>')
    html = '\n'.join(out)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', html)
    return html


def ai_write(topic, title_hint=""):
    system_prompt = (
        "Kamu adalah penulis konten senior untuk portal game Indonesia bernama Jura Game. "
        "Tulis artikel ORISINAL, mendalam, dan benar-benar bermanfaat (bukan konten tipis). "
        "Gaya bahasa: ramah, santai tapi informatif, memakai 'kamu'. "
        "WAJIB dalam Bahasa Indonesia yang baik dan benar.\n\n"
        "ATURAN FORMAT (patuhi ketat):\n"
        "- Panjang 900-1200 kata. Jangan kurang dari 900 kata.\n"
        "- Mulai dengan paragraf pembuka yang mengaitkan pembaca (tanpa heading 'Pendahuluan').\n"
        "- Gunakan minimal 5 sub-judul dengan format '## Judul Sub' (dua tanda pagar + spasi).\n"
        "- JANGAN pakai format '1. Judul' atau '**Judul**' sebagai sub-judul — WAJIB '## '.\n"
        "- Setiap sub-judul diikuti 2-3 paragraf penjelasan.\n"
        "- Sertakan minimal satu daftar berpoin ('- ') dan satu daftar bernomor ('1. ').\n"
        "- Gunakan **bold** untuk istilah penting.\n"
        "- Sebut nama game nyata yang relevan sebagai contoh.\n"
        "- Akhiri dengan '## Kesimpulan' + ajakan mencoba game di Jura Game.\n"
        "- JANGAN menulis judul artikel di awal.\n"
        "- JANGAN menulis catatan meta/disclaimer AI. Langsung isi."
    )
    user_prompt = (
        f"Tulis ulang artikel ini menjadi versi yang jauh lebih lengkap dan mendalam (900-1200 kata).\n"
        f"Judul harus tetap sama: \"{title_hint or topic}\"\n"
        f"Topik: {topic}\n\n"
        "Pertahankan temanya, tetapi tambahkan penjelasan, alasan, contoh game nyata, tips praktis, "
        "dan kesimpulan. Hindari kalimat klise dan pengulangan."
    )
    payload = json.dumps({
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 4000,
        "temperature": 0.75,
    }).encode('utf-8')
    req = urllib.request.Request(AI_API_URL, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}",
    })
    with urllib.request.urlopen(req, timeout=200) as r:
        raw = r.read().decode('utf-8', 'replace')

    # 9Router bisa balas SSE streaming ATAU JSON biasa — tangani keduanya.
    if raw.lstrip().startswith("{"):
        try:
            d = json.loads(raw)
            return (d['choices'][0]['message'].get('content') or '').strip()
        except Exception:
            return ""

    full = ""
    for line in raw.splitlines():
        ls = line.strip()
        if ls.startswith("data: ") and ls != "data: [DONE]":
            try:
                d = json.loads(ls[6:])
                delta = d['choices'][0].get('delta', {})
                if 'content' in delta:
                    full += delta['content']
            except Exception:
                continue
    return full.strip()


def word_count(text):
    return len(re.sub(r'<[^>]+>', ' ', str(text)).split())


def main():
    limit = None
    only_slug = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    if "--slug" in sys.argv:
        only_slug = sys.argv[sys.argv.index("--slug") + 1]

    arts_raw, _ = gh_get("articles.json")
    articles = json.loads(arts_raw) if arts_raw else []
    print(f"Total artikel: {len(articles)}")

    # Pilih yang tipis
    targets = []
    for a in articles:
        slug = a.get('slug') or slugify(a['title'])
        wc = word_count(a.get('body', ''))
        if only_slug and slug != only_slug:
            continue
        if wc < THRESHOLD:
            targets.append((a, slug, wc))
    targets.sort(key=lambda x: x[2])  # paling tipis dulu
    if limit:
        targets = targets[:limit]

    print(f"Akan regenerate: {len(targets)} artikel (di bawah {THRESHOLD} kata)\n")
    if not targets:
        print("Tidak ada artikel tipis. Selesai.")
        return

    ok, fail = 0, 0
    for i, (a, slug, wc) in enumerate(targets, 1):
        title = a['title']
        print(f"[{i}/{len(targets)}] {title}  (sekarang {wc} kata)")

        # Potongan isi lama sebagai konteks topik
        old_txt = re.sub(r'<[^>]+>', ' ', str(a.get('body', '')))
        old_txt = re.sub(r'\s+', ' ', old_txt).strip()[:600]

        try:
            body = ai_write(f"{title}. Konteks lama: {old_txt}", title_hint=title)
        except Exception as e:
            print(f"   ❌ AI gagal: {str(e)[:100]}")
            fail += 1
            continue

        nw = len(body.split())
        # 🔒 GUARD: kalau AI gagal / hasil lebih pendek dari aslinya → JANGAN timpa
        if nw < 200:
            print(f"   ❌ AI gagal (hanya {nw} kata) — artikel DILEWATI, tidak ditimpa")
            fail += 1
            continue
        if nw < wc:
            print(f"   ⚠️ Hasil ({nw}) lebih pendek dari asli ({wc}) — DILEWATI")
            fail += 1
            continue
        print(f"   ✍️  {nw} kata (dari {wc})")

        # Perbarui objek artikel
        a['body'] = body
        a['excerpt'] = re.sub(r'[*#_]', '', body)[:180].strip()
        a['date'] = datetime.now().strftime("%d %B %Y")
        a['date_iso'] = datetime.now().strftime("%Y-%m-%d")
        a['_regenerated'] = True   # tandai agar hanya artikel ini yang ditulis ulang HTML-nya

        ok += 1
        time.sleep(1)

    if ok == 0:
        print("\n⚠️ Tidak ada artikel yang berhasil diregenerate. Tidak ada yang diubah.")
        return

    # Simpan articles.json SEBELUM generate HTML (agar template bisa baca)
    gh_put("articles.json", json.dumps(articles, ensure_ascii=False, indent=2), "Regenerate: artikel diperpanjang")
    print(f"\n📦 articles.json diperbarui ({ok} artikel diperpanjang)")

    # Generate HTML artikel dari template blog_post.py
    import importlib.util
    spec = importlib.util.spec_from_file_location('bp', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blog_post.py'))
    bp = importlib.util.module_from_spec(spec)
    _argv, sys.argv = sys.argv, ['x']
    spec.loader.exec_module(bp)
    sys.argv = _argv

    for a in articles:
        if not a.get('_regenerated'):
            continue   # hanya artikel yang baru diregenerate
        slug = a.get('slug') or slugify(a['title'])
        content_html = md_to_html(a['body'])
        date_str = a.get('date', datetime.now().strftime("%d %B %Y"))
        date_iso = a.get('date_iso', datetime.now().strftime("%Y-%m-%d"))
        read_time = max(3, len(a['body'].split()) // 200)
        url = f"{BASE_URL}/blog/{slug}.html"
        cover = a.get('cover_image', '')
        html = bp.ARTICLE_TEMPLATE.format(
            title=a['title'],
            title_short=a['title'][:40] + "..." if len(a['title']) > 40 else a['title'],
            description=a.get('excerpt', '')[:160],
            keywords=slug.replace('-', ', '),
            url=url, cover_image=cover, category=a.get('category', 'Tips Gaming'),
            date=date_str, date_iso=date_iso, read_time=read_time, content=content_html,
        )
        gh_put(f"blog/{slug}.html", html, f"Regenerate: {a['title'][:45]}")
        print(f"   ✅ blog/{slug}.html")
        time.sleep(0.4)

    # Update sitemap
    slugs = [a.get('slug') or slugify(a['title']) for a in articles]
    urls = [f"  <url><loc>{BASE_URL}/</loc><priority>1.0</priority></url>",
            f"  <url><loc>{BASE_URL}/blog/</loc><priority>0.8</priority></url>"]
    for s in slugs:
        urls.append(f"  <url><loc>{BASE_URL}/blog/{s}.html</loc><priority>0.7</priority></url>")
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + '\n'.join(urls) + '\n</urlset>')
    gh_put("sitemap.xml", sm, "Regenerate: sitemap")
    print("   📄 sitemap.xml")

    print(f"\n🎉 SELESAI: {ok} berhasil, {fail} gagal")


if __name__ == "__main__":
    main()
