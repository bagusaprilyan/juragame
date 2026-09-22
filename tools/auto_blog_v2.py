#!/usr/bin/env python3
"""
auto_blog_v2.py — Auto-posting blog Jura Game
- Cek token GitHub dulu sebelum posting
- Kirim notifikasi Telegram sukses/gagal
- Update report setiap posting
"""
import sys, os, re, json, random, base64, urllib.request, urllib.error, yaml
from datetime import datetime

# Load config
with open("/home/ubuntu/.hermes/profiles/saham/config.yaml") as f:
    cfg = yaml.safe_load(f)

# Load GitHub token
TOKEN = os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    try:
        TOKEN = re.search(r'ghp_[A-Za-z0-9]+', open('/home/ubuntu/.github_token').read()).group(0)
    except: TOKEN = ""

# Telegram notification settings
TG_BOT_TOKEN = cfg.get('telegram', {}).get('bot_token', '')
TG_CHAT_ID = "711882700"  # Home channel

REPO = "bagusaprilyan/juragame"
BASE = "https://juragame.com"
API = f"https://api.github.com/repos/{REPO}/contents"
GH = {"Authorization": f"token {TOKEN}", "User-Agent": "HermesAgent", "Content-Type": "application/json"}

AI_URL = cfg['model']['base_url'] + "/chat/completions"
AI_KEY = cfg['model']['api_key']

TOPICS = {
    "game": [
        "5 Game Balap Ringan Paling Seru untuk HP Kentang",
        "Rekomendasi Game Puzzle Santai untuk Mengisi Waktu Luang",
        "Game RPG Browser Terbaik yang Bisa Dimainkan Tanpa Download",
        "Game Multiplayer Online Ringan untuk Dimain Bareng Teman",
        "Game Survival Ringan dengan Grafis Cantik di Browser",
        "7 Game Sederhana Tapi Bikin Ketagihan untuk Sore Hari",
        "Game Platformer Gratis Terbaik untuk Anak dan Dewasa",
        "Game Kartu dan Strategi Ringan untuk Waktu Istirahat",
        "Game Simulasi Kehidupan Ringan Paling Realistis",
        "Game Horor Santai untuk Pemula yang Baru Mulai Main",
        "Game Battle Royale Ringan untuk HP Kentang",
        "Game Lari Tak Terbatas Paling Populer Tahun Ini",
        "Game Petualangan Ringan dengan Cerita Menarik",
        "Game IO Sederhana tapi Kompetitif",
    ],
    "review": [
        "Review Lengkap Subway Surfers: Game Endless Runner yang Tak Lekang Waktu",
        "Review Among Us: Game Sosial yang Masih Relevan di Tahun Ini",
        "Review Minecraft Versi Browser: Worth It atau Tidak",
        "Review 2048: Puzzle Angka yang Bikin Pikiran Jernih",
        "Review Stumble Guys: Alternatif Fall Guys yang Gratis",
        "Review Cookie Clicker: Game Idle Paling Adiktif",
        "Review Krunker.io: FPS Browser dengan Komunitas Aktif",
        "Review Slither.io: Game Ular Sederhana Tapi Kompetitif",
        "Review Tank Trouble: Tank Multiplayer Ringan untuk Santai",
        "Review Zombs Royale: Battle Royale Browser Paling Seru",
    ],
    "film": [
        "Review Film Dune Part Two: Mahakarya Sinema Modern",
        "Rekomendasi Film Sci-Fi Terbaik untuk Pecinta Game",
        "10 Film Action Terbaik yang Wajib Ditonton",
        "Review Film The Batman: Gelap dan Penuh Misteri",
        "Film Animasi Terbaik untuk Ditonton Bareng Keluarga",
        "Rekomendasi Film Thriller Plot Twist Mengejutkan",
        "Review Film Oppenheimer: Perjalanan Epik Penuh Makna",
        "Film Horor Asia Terseram yang Wajib Ditonton",
        "Rekomendasi Film Komedi Ringan untuk Mengusir Penat",
        "Review Film John Wick: Aksi Tanpa Henti",
    ]
}

KEYWORDS = {
    "game": ["game html5", "game gratis", "game online", "jura game", "game tanpa download"],
    "review": ["review game", "ulasan game", "jura game review", "game terbaik"],
    "film": ["review film", "rekomendasi film", "film terbaik", "ulasan film"],
    "berita": ["berita game", "kabar game", "update game", "game terbaru", "jura game news"],
    "panduan": ["panduan game", "tips game", "cara main", "tutorial game", "jura game"],
}
CATEGORIES = {"game": "Game Online", "review": "Review Game", "film": "Review Film",
              "berita": "Berita Game", "panduan": "Panduan"}

# ── Telegram notification ────────────────────────────────────────

def tg_notify(text):
    if not TG_BOT_TOKEN:
        return
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        payload = json.dumps({"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        print(f"Telegram notify error: {e}")

# ── GitHub API helpers ────────────────────────────────────────────

def check_token():
    """Cek apakah token GitHub masih valid."""
    if not TOKEN:
        return False, "Token GitHub kosong di /home/ubuntu/.github_token"
    try:
        req = urllib.request.Request('https://api.github.com/user', headers=GH)
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status == 200:
                return True, "Token OK"
        return False, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code} (token expired/revoked)"
    except Exception as e:
        return False, str(e)

def gh_get(p):
    try:
        req = urllib.request.Request(f"{API}/{p}", headers=GH)
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
        return base64.b64decode(d['content']).decode('utf-8'), d['sha']
    except urllib.error.HTTPError as e:
        if e.code == 404: return None, None
        raise

def gh_put(p, content, msg):
    _, sha = gh_get(p)
    payload = {"message": msg, "content": base64.b64encode(content.encode()).decode()}
    if sha: payload["sha"] = sha
    req = urllib.request.Request(f"{API}/{p}", data=json.dumps(payload).encode(), method="PUT", headers=GH)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

# ── AI ────────────────────────────────────────────────────────────

def router_key():
    """Ambil API key 9Router (env → DB lokal)."""
    env = os.environ.get("ROUTER_API_KEY", "")
    if env:
        return env
    try:
        import subprocess
        out = subprocess.check_output(
            ["sqlite3", "/home/ubuntu/.9router/db/data.sqlite",
             "SELECT key FROM apiKeys WHERE name='hermes';"], timeout=10).decode().strip()
        if out:
            return out
    except Exception:
        pass
    return AI_KEY  # fallback ke config


def ai_call(prompt):
    payload = json.dumps({
        "model": "hermes",
        "messages": [
            {"role": "system", "content": "Kamu penulis blog Jura Game Indonesia. Gaya santai tapi INFORMATIF dan FAKTUAL. Tulis dalam Bahasa Indonesia. PENTING: JANGAN menulis opini pribadi atau klaim yang dibuat-buat. Semua informasi harus realistis dan berdasarkan fakta (game/film yang benar-benar ada, fitur nyata, gameplay aktual). Hindari kata berlebihan seperti 'terbaik sepanjang masa', 'wajib', 'luar biasa' tanpa dasar. Fokus pada informasi berguna: apa gamenya, bagaimana cara mainnya, kelebihan/kekurangan yang nyata. Gunakan heading (##), list (- atau 1.), bold (**). Minimal 4 paragraf. Akhiri dengan 1 paragraf ajakan singkat ke Jura Game."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000
    }).encode()

    for attempt in range(3):
        try:
            req = urllib.request.Request(AI_URL, data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {router_key()}"
            })
            with urllib.request.urlopen(req, timeout=240) as r:
                raw = r.read().decode("utf-8", "replace")

            # Format A: JSON biasa (9Router balas non-stream)
            if raw.lstrip().startswith("{"):
                try:
                    d = json.loads(raw)
                    c = d["choices"][0]["message"].get("content") or ""
                    if c.strip():
                        return c.strip()
                except Exception:
                    pass

            # Format B: SSE (data: {...})
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
            if out.strip():
                return out.strip()
        except Exception as e:
            print(f"   AI retry {attempt+1}: {e}")
    return ""

def ai_with_topic(mode, topic):
    extra = {
        "game": "Sebutkan minimal 5 game yang BENAR-BENAR ADA dan bisa dimainkan di browser/HP saat ini. Jelaskan gameplay nyatanya secara singkat. Jangan mengarang game atau fitur yang tidak ada.",
        "review": "Bahas game berdasarkan fakta yang diketahui umum: gameplay, kontrol, grafik, kelebihan dan kekurangan nyata. Jika tidak yakin soal detail spesifik, jangan sebutkan angka pasti. Jangan mengarang statistik atau rating palsu.",
        "film": "Bahas film berdasarkan fakta: judul, genre, sutradara, pemeran utama yang benar-benar ada. Hindari spoiler. Jika tidak yakin detailnya, bahas secara umum tanpa mengarang fakta."
    }[mode]
    prompt = (
        f"Tulis artikel blog 900-1200 kata Bahasa Indonesia dengan topik: \"{topic}\".\n"
        f"Mode: {mode}.\nPanduan konten: {extra}\n\n"
        f"ATURAN WAJIB:\n"
        f"- Tulis berdasarkan FAKTA dan kondisi nyata saat ini, bukan opini pribadi\n"
        f"- Jangan melebih-lebihkan atau membuat klaim tanpa dasar\n"
        f"- Gaya netral-informatif seperti panduan, bukan promosi\n"
        f"- Panjang 900-1200 kata (JANGAN kurang dari 900 kata)\n\n"
        f"FORMAT:\n"
        f"- Pembuka langsung ke topik (tanpa basa-basi berlebihan)\n"
        f"- Minimal 6 sub-heading dengan format '## Judul Sub' (dua pagar + spasi)\n"
        f"- Wajib ada satu daftar berpoin ('- ') dan satu daftar bernomor ('1. ')\n"
        f"- Gunakan **bold** untuk istilah penting\n"
        f"- Akhiri dengan '## Kesimpulan' + ajakan singkat ke Jura Game\n"
    )
    return ai_call(prompt)

# ── HTML builder ──────────────────────────────────────────────────

STOPWORDS = {"yang", "untuk", "dengan", "dari", "pada", "akan", "tidak", "bisa",
             "tapi", "resmi", "juga", "ini", "itu", "dan", "atau", "ada", "ke",
             "di", "the", "and", "for", "with", "from", "that", "this", "will",
             "its", "has", "have", "was", "were", "are", "not", "but", "you",
             "game", "games", "berita", "news", "update", "baru", "terbaru"}


def make_tags(title, extra=""):
    """Buat tag bersih dari judul (buang stopword & kata umum)."""
    words = re.findall(r"[A-Za-z0-9]+", (title + " " + extra).lower())
    out = []
    for w in words:
        if len(w) > 3 and w not in STOPWORDS and w not in out:
            out.append(w)
    return out[:5] or ["berita-game"]


def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s[:60].strip('-')

def md_to_html(md):
    parts = []
    in_list = False
    for line in md.strip().split('\n'):
        line = line.strip()
        if not line:
            if in_list: parts.append('</ul>'); in_list = False
            continue
        if line.startswith('### '): parts.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('## '): parts.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('# '): parts.append(f'<h2>{line[2:]}</h2>')
        elif line.startswith(('- ', '* ')):
            if not in_list: parts.append('<ul>'); in_list = True
            parts.append(f'<li>{line[2:]}</li>')
        elif re.match(r'^\d+\.\s', line):
            if not in_list: parts.append('<ol>'); in_list = True
            item = re.sub(r'^\d+\.\s', '', line)
            parts.append(f'<li>{item}</li>')
        else:
            if in_list: parts.append('</ul>'); in_list = False
            parts.append(f'<p>{line}</p>')
    if in_list: parts.append('</ul>')
    html = '\n'.join(parts)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    return html

def build_article(mode, title, body_md, cover, slug, category, tags, description, date_str,
                  source_name=None, source_url=None):
    read_time = max(2, len(body_md.split()) // 150)
    url = f"{BASE}/blog/{slug}.html"
    keywords = ", ".join(KEYWORDS[mode] + tags)
    content_html = md_to_html(body_md)
    tags_html = " ".join([f'<a href="{BASE}/blog/?tag={t}" class="px-2 py-1 rounded-md bg-slate-800 text-indigo-300 text-xs">#{t}</a>' for t in tags])
    # Kotak sumber (untuk berita) — sinyal kepercayaan E-E-A-T
    source_html = ""
    if source_name and source_url:
        source_html = (
            f'<div class="rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-xs text-amber-200/90 space-y-1">'
            f'<p class="font-bold text-amber-300">📰 Sumber Berita</p>'
            f'<p>Artikel ini disusun ulang dalam Bahasa Indonesia berdasarkan laporan '
            f'<a href="{source_url}" target="_blank" rel="nofollow noopener" class="underline font-semibold">{source_name}</a>. '
            f'Semua fakta mengacu pada sumber asli. Kami menulis ulang dengan konteks untuk gamer Indonesia.</p>'
            f'</div>'
        )
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": description,
        "image": cover,
        "datePublished": date_str,
        "author": {"@type": "Organization", "name": "Jura Game"},
        "publisher": {"@type": "Organization", "name": "Jura Game"},
        "mainEntityOfPage": url,
        "keywords": keywords,
        "articleSection": category
    }, ensure_ascii=False)

    cta_title = {"game": "Main", "berita": "Main", "panduan": "Main"}.get(mode, "Nonton")
    cta_btn = {"game": "Mainkan Sekarang", "berita": "Main Game Sekarang", "panduan": "Mainkan Sekarang"}.get(mode, "Lihat Review Lengkap")

    return f'''<!DOCTYPE html>
<html lang="id" class="dark">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Jura Game Blog</title>
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<meta name="author" content="Admin Jura Game">
<meta name="robots" content="index, follow">
<meta name="article:published_time" content="{date_str}">
<meta name="article:section" content="{category}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{cover}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:image" content="{cover}">
<link rel="canonical" href="{url}">
<script type="application/ld+json">{jsonld}</script>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/lucide@latest"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
body{{font-family:'Inter',sans-serif;background:#020617;color:#f8fafc}}
.glass{{background:rgba(15,23,42,.85);backdrop-filter:blur(16px);border-bottom:1px solid rgba(255,255,255,.08)}}
.article-content h2{{color:#f8fafc;font-size:1.5rem;font-weight:800;margin:2rem 0 1rem}}
.article-content h3{{color:#f8fafc;font-size:1.25rem;font-weight:700;margin:1.5rem 0 .75rem}}
.article-content p{{color:#cbd5e1;line-height:1.8;margin-bottom:1.25rem}}
.article-content ul,.article-content ol{{color:#cbd5e1;padding-left:1.5rem;margin-bottom:1.25rem}}
.article-content ul{{list-style:disc}}.article-content ol{{list-style:decimal}}
.article-content li{{margin-bottom:.5rem;line-height:1.7}}
.article-content strong{{color:#f8fafc;font-weight:700}}
.article-content a{{color:#818cf8;text-decoration:underline}}
</style></head>
<body class="min-h-screen flex flex-col">
<header class="glass sticky top-0 z-40">
<div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
<a href="../index.html" class="flex items-center gap-2"><div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center text-white font-bold">J</div>
<span class="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-pink-400">Jura game</span></a>
<a href="../index.html" class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5"><i data-lucide="gamepad-2" class="w-4 h-4"></i> Main Game</a>
</div></header>
<main class="max-w-3xl mx-auto px-4 py-8 flex-grow space-y-6">
<nav class="flex items-center gap-2 text-xs text-slate-400">
<a href="../index.html" class="hover:text-white">Beranda</a><i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
<a href="index.html" class="hover:text-white">Blog</a><i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
<span class="text-indigo-400 truncate">{title[:40]}</span></nav>
<header class="space-y-3">
<div class="flex items-center gap-2 flex-wrap">
<span class="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-bold border border-indigo-500/30">{category}</span>
<span class="text-xs text-slate-400">{date_str}</span></div>
<h1 class="text-2xl sm:text-4xl font-black text-white leading-tight">{title}</h1>
<div class="flex items-center gap-2 text-xs text-slate-400 pt-1"><span>Oleh: <strong class="text-slate-200">Admin Jura</strong></span><span>•</span><span>{read_time} Min Baca</span></div>
<div class="flex flex-wrap gap-2 pt-2">{tags_html}</div>
</header>
<div class="rounded-2xl overflow-hidden border border-slate-800 shadow-2xl aspect-[16/9] bg-slate-900">
<img src="{cover}" alt="{title}" class="w-full h-full object-cover"></div>
{source_html}
<article class="article-content max-w-none text-slate-300 text-sm sm:text-base leading-relaxed space-y-4">
{content_html}
<div class="my-6 p-6 rounded-2xl bg-gradient-to-r from-indigo-950/80 to-purple-950/80 border border-indigo-500/30 text-center space-y-3">
<h3 class="text-lg font-bold text-white">Mau {cta_title} Sekarang?</h3>
<p class="text-xs text-slate-300">Jelajahi koleksi review & game terbaik di Jura Game.</p>
<a href="../index.html" class="inline-block px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-indigo-600/40">{cta_btn}</a>
</div>
</article>
<div class="border-t border-slate-800 pt-6"><a href="index.html" class="inline-flex items-center gap-2 text-xs font-bold text-indigo-400 hover:text-indigo-300"><i data-lucide="arrow-left" class="w-4 h-4"></i> Kembali ke Katalog</a></div>
</main>
<footer class="border-t border-slate-800 bg-slate-900/50 py-8 mt-12">
<div class="max-w-4xl mx-auto px-4 text-xs text-slate-500 space-y-3">
<div class="flex flex-wrap gap-x-4 gap-y-2 justify-center">
<a href="../index.html" class="hover:text-white transition">Beranda</a>
<a href="index.html" class="hover:text-white transition">Blog &amp; Tips</a>
<a href="../about.html" class="hover:text-white transition">Tentang Kami</a>
<a href="../contact.html" class="hover:text-white transition">Kontak</a>
<a href="../privacy.html" class="hover:text-white transition">Kebijakan Privasi</a>
<a href="../disclaimer.html" class="hover:text-white transition">Disclaimer</a>
<a href="../terms.html" class="hover:text-white transition">Syarat &amp; Ketentuan</a>
</div>
<p class="text-center">&copy; 2026 Jura Game. Portal game HTML5 gratis &amp; blog berita game.</p>
</div></footer>
<script>if(window.lucide)lucide.createIcons();</script></body></html>'''

# ── Main ─────────────────────────────────────────────────────────

def post(mode, custom_topic=None):
    category = CATEGORIES[mode]
    topic = custom_topic or random.choice(TOPICS[mode])
    slug = slugify(topic)
    print(f"Mode: {mode} | Topik: {topic}")

    # CEK TOKEN DULU sebelum posting
    ok, status = check_token()
    if not ok:
        msg = f"❌ BLOG GAGAL - Token GitHub rusak!\nMode: {mode}\nError: {status}\n\nSegera regenerate token & simpan ke `/home/ubuntu/.github_token`"
        print(msg)
        tg_notify(msg)
        return False

    body = ai_with_topic(mode, topic)
    if not body:
        msg = f"❌ BLOG GAGAL - AI tidak menghasilkan konten\nMode: {mode} | Topik: {topic}"
        print(msg)
        tg_notify(msg)
        return False

    cover = random.choice([
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800",
        "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800",
        "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800",
        "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=800",
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800",
        "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=800",
    ])
    date_str = datetime.now().strftime("%d %B %Y")
    excerpt = re.sub(r'[*#_]', '', body)[:160].strip()
    description = excerpt[:160]
    tags = make_tags(topic, category)

    try:
        article_html = build_article(mode, topic, body, cover, slug, category, tags, description, date_str)
        gh_put(f"blog/{slug}.html", article_html, f"Auto-post {mode}: {topic[:50]}")

        data, _ = gh_get("articles.json")
        arr = json.loads(data) if data else []
        arr = [a for a in arr if a.get('slug') != slug]
        arr.insert(0, {"slug": slug, "title": topic, "body": body, "excerpt": excerpt,
                        "date": date_str, "category": category, "cover_image": cover,
                        "tags": tags, "mode": mode})
        gh_put("articles.json", json.dumps(arr, ensure_ascii=False, indent=2), "Update articles.json")

        urls = [f'  <url><loc>{BASE}/</loc><priority>1.0</priority></url>',
                f'  <url><loc>{BASE}/blog/</loc><priority>0.8</priority></url>']
        urls += [f'  <url><loc>{BASE}/blog/{a.get("slug", slugify(a["title"]))}.html</loc><priority>0.7</priority></url>' for a in arr]
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>'
        gh_put("sitemap.xml", sitemap, "Update sitemap")

        url = f"{BASE}/blog/{slug}.html"
        msg = f"✅ BLOG POSTED\n\n📝 {topic}\n📂 {category}\n🔗 {url}\n\n_(Vercel deploy ~1-2 menit)_"
        print(f"Live: {url}")
        tg_notify(msg)
        return True
    except Exception as e:
        msg = f"❌ BLOG GAGAL - GitHub API error\nMode: {mode} | Topik: {topic}\nError: {e}"
        print(msg)
        tg_notify(msg)
        return False

def post_berita():
    """Ambil berita nyata dari RSS → tulis ulang jadi artikel panjang → publish."""
    import news_fetcher as nf
    import news_writer as nw

    print("Mode: berita (dari RSS eksternal)")
    ok, status = check_token()
    if not ok:
        msg = f"❌ BLOG GAGAL - Token GitHub rusak!\nMode: berita\nError: {status}"
        print(msg); tg_notify(msg)
        return False

    item = nf.pick_one()
    if not item:
        print("⚠️ Tidak ada berita baru (semua sudah dipakai) — lewati")
        return False
    print(f"   📰 [{item['source']}] {item['title'][:70]}")

    res = nw.write_from_news(item)
    if not res:
        msg = f"❌ BLOG GAGAL - AI gagal menulis berita\n{item['link']}"
        print(msg); tg_notify(msg)
        return False

    title = res["title"]
    body = res["body"]
    slug = slugify(title)
    category = CATEGORIES["berita"]
    date_str = datetime.now().strftime("%d %B %Y")
    excerpt = re.sub(r'[*#_]', '', body)[:160].strip()
    description = excerpt[:160]
    tags = make_tags(title, item['title'])

    # Cover: pakai gambar berita asli kalau ada, kalau tidak fallback
    cover = item.get("image") or random.choice([
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800",
        "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800",
        "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800",
    ])

    try:
        article_html = build_article("berita", title, body, cover, slug, category, tags,
                                     description, date_str,
                                     source_name=item["source"], source_url=item["link"])
        gh_put(f"blog/{slug}.html", article_html, f"Auto-berita: {title[:50]}")

        data, _ = gh_get("articles.json")
        arr = json.loads(data) if data else []
        arr = [a for a in arr if a.get('slug') != slug]
        arr.insert(0, {"slug": slug, "title": title, "body": body, "excerpt": excerpt,
                       "date": date_str, "category": category, "cover_image": cover,
                       "tags": tags, "mode": "berita",
                       "source_name": item["source"], "source_url": item["link"]})
        gh_put("articles.json", json.dumps(arr, ensure_ascii=False, indent=2), "Update articles.json")

        _rebuild_sitemap(arr)
        nf.mark_used(item["link"], item["title"])

        url = f"{BASE}/blog/{slug}.html"
        msg = (f"✅ BERITA POSTED\n\n📝 {title}\n📰 Sumber: {item['source']}\n"
               f"📂 {category}\n🔗 {url}\n\n_(Vercel deploy ~1-2 menit)_")
        print(f"Live: {url}")
        tg_notify(msg)
        return True
    except Exception as e:
        msg = f"❌ BERITA GAGAL - GitHub API error\n{item['link']}\nError: {e}"
        print(msg); tg_notify(msg)
        return False


def _rebuild_sitemap(articles):
    urls = [f'  <url><loc>{BASE}/</loc><priority>1.0</priority></url>',
            f'  <url><loc>{BASE}/blog/</loc><priority>0.8</priority></url>']
    for p in ["about", "contact", "privacy", "disclaimer", "terms"]:
        urls.append(f'  <url><loc>{BASE}/{p}.html</loc><priority>0.5</priority></url>')
    urls += [f'  <url><loc>{BASE}/blog/{a.get("slug", slugify(a["title"]))}.html</loc><priority>0.7</priority></url>' for a in articles]
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + '\n'.join(urls) + '\n</urlset>')
    gh_put("sitemap.xml", sitemap, "Update sitemap")


def post_mixed():
    """Campuran 70% berita + 30% panduan/review (anti-konten-tipis)."""
    roll = random.random()
    if roll < 0.70:
        print("🎲 Pilih: BERITA (70%)")
        ok = post_berita()
        if not ok:
            print("   ↪️  Fallback ke panduan...")
            return post("game")
        return ok
    else:
        print("🎲 Pilih: PANDUAN (30%)")
        return post("game")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 auto_blog_v2.py [mixed|berita|game|review|film] [topik]")
        sys.exit(1)
    mode = sys.argv[1]
    if mode == "mixed":
        ok = post_mixed()
        sys.exit(0 if ok else 1)
    if mode == "berita":
        ok = post_berita()
        sys.exit(0 if ok else 1)
    if mode not in TOPICS:
        print(f"Mode harus: mixed | berita | {list(TOPICS.keys())}")
        sys.exit(1)
    custom = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
    post(mode, custom)
