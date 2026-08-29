#!/usr/bin/env python3
"""
blog_post.py v2 — Posting artikel blog Jura Game ke GitHub (HTML statis)
Struktur repo:
  /index.html          <- Portal Game
  /sitemap.xml
  /blog/index.html     <- Katalog Blog
  /blog/<slug>.html    <- Artikel

Usage:
  python3 blog_post.py --ai "Topik artikel"
  python3 blog_post.py "Judul" "Isi artikel..." [--kategori "Tips Gaming"]
  python3 blog_post.py --list
"""
import json, base64, sys, os, re, urllib.request, urllib.error, yaml
from datetime import datetime

# ── Load Config ──────────────────────────────────────────────────
CONFIG_PATH = "/home/ubuntu/.hermes/profiles/saham/config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "bagusaprilyan/juragame"
BASE_URL = "https://juragame.vercel.app"
API = f"https://api.github.com/repos/{REPO}/contents"

AI_API_URL = config['model']['base_url'] + "/chat/completions"
AI_API_KEY = config['model']['api_key']
AI_MODEL = "hermes"

GH = {"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "HermesAgent", "Content-Type": "application/json"}

# ── Helpers ──────────────────────────────────────────────────────

def gh_get(path):
    """Baca file dari GitHub, return (content_str, sha) atau (None, None)."""
    url = f"{API}/{path}"
    req = urllib.request.Request(url, headers=GH)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
        content = base64.b64decode(d['content']).decode('utf-8')
        return content, d['sha']
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, None
        raise

def gh_put(path, content, message):
    """Tulis/overwrite file ke GitHub."""
    _, sha = gh_get(path)
    payload = {"message": message, "content": base64.b64encode(content.encode('utf-8')).decode('utf-8')}
    if sha:
        payload["sha"] = sha
    req = urllib.request.Request(f"{API}/{path}", data=json.dumps(payload).encode(), method="PUT", headers=GH)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def slugify(title):
    slug = title.lower().strip()
    rchar = re.compile(r'[^\w\s-]')
    rspace = re.compile(r'[\s_]+')
    rhyph = re.compile(r'-+')
    slug = rchar.sub('', slug)
    slug = rspace.sub('-', slug)
    slug = rhyph.sub('-', slug)
    return slug[:60].strip('-')

def md_to_html(md_text):
    """Konversi markdown-lite ke HTML sederhana."""
    lines = md_text.strip().split('\n')
    html_parts = []
    in_list = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            continue
        # Heading
        if line.startswith('### '):
            html_parts.append(f'<h3>{line[4:]}</h3>')
        elif line.startswith('## '):
            html_parts.append(f'<h2>{line[3:]}</h2>')
        elif line.startswith('# '):
            html_parts.append(f'<h2>{line[2:]}</h2>')
        # List item
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            html_parts.append(f'<li>{line[2:]}</li>')
        elif re.match(r'^\d+\.\s', line):
            if not in_list:
                html_parts.append('<ol>')
                in_list = True
            item_text = re.sub(r'^\d+\.\s', '', line)
            html_parts.append('<li>' + item_text + '</li>')
        else:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            html_parts.append(f'<p>{line}</p>')
    if in_list:
        html_parts.append('</ul>')

    html = '\n'.join(html_parts)
    # Bold & italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    return html

# ── Template ─────────────────────────────────────────────────────

ARTICLE_TEMPLATE = '''<!DOCTYPE html>
<html lang="id" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Jura Game Blog</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}, jura game, game html5, game gratis">
    <meta name="author" content="Admin Jura Game">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{cover_image}">
    <meta property="og:url" content="{url}">
    <link rel="canonical" href="{url}">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #020617; color: #f8fafc; }}
        .glass {{ background: rgba(15,23,42,0.85); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(255,255,255,0.08); }}
        .article-content h2 {{ color:#f8fafc; font-size:1.5rem; font-weight:800; margin:2rem 0 1rem; }}
        .article-content h3 {{ color:#f8fafc; font-size:1.25rem; font-weight:700; margin:1.5rem 0 0.75rem; }}
        .article-content p {{ color:#cbd5e1; line-height:1.8; margin-bottom:1.25rem; }}
        .article-content ul,.article-content ol {{ color:#cbd5e1; padding-left:1.5rem; margin-bottom:1.25rem; }}
        .article-content ul {{ list-style-type:disc; }}
        .article-content ol {{ list-style-type:decimal; }}
        .article-content li {{ margin-bottom:0.5rem; line-height:1.7; }}
        .article-content strong {{ color:#f8fafc; font-weight:700; }}
        .article-content a {{ color:#818cf8; text-decoration:underline; }}
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <!-- Header -->
    <header class="glass sticky top-0 z-40">
        <div class="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
            <a href="../index.html" class="flex items-center gap-2 group">
                <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center text-white font-bold shadow-lg shadow-indigo-600/30">J</div>
                <span class="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-pink-400">Jura game</span>
            </a>
            <a href="../index.html" class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-lg shadow-indigo-600/30">
                <i data-lucide="gamepad-2" class="w-4 h-4"></i> Main Game
            </a>
        </div>
    </header>

    <!-- Content -->
    <main class="max-w-3xl mx-auto px-4 py-8 flex-grow space-y-6">

        <!-- Breadcrumb -->
        <nav class="flex items-center gap-2 text-xs text-slate-400">
            <a href="../index.html" class="hover:text-white transition">Beranda</a>
            <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
            <a href="index.html" class="hover:text-white transition">Blog</a>
            <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
            <span class="text-indigo-400 truncate">{title_short}</span>
        </nav>

        <!-- Article Header -->
        <header class="space-y-3">
            <div class="flex items-center gap-2">
                <span class="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-bold border border-indigo-500/30">{category}</span>
                <span class="text-xs text-slate-400">{date}</span>
            </div>
            <h1 class="text-2xl sm:text-4xl font-black text-white leading-tight">{title}</h1>
            <div class="flex items-center gap-2 text-xs text-slate-400 pt-1">
                <span>Ditulis oleh: <strong class="text-slate-200">Admin Jura</strong></span>
                <span>&bull;</span>
                <span>{read_time} Min Baca</span>
            </div>
        </header>

        <!-- Featured Image -->
        <div class="rounded-2xl overflow-hidden border border-slate-800 shadow-2xl aspect-[16/9] bg-slate-900">
            <img src="{cover_image}" alt="{title}" class="w-full h-full object-cover">
        </div>

        <!-- Ad Slot -->
        <div class="bg-slate-900/60 border border-dashed border-slate-800 rounded-xl p-4 text-center">
            <span class="text-[10px] text-slate-500 uppercase font-bold">Ruang Iklan Banner (AdSense Ready)</span>
        </div>

        <!-- Article Body -->
        <article class="article-content max-w-none text-slate-300 text-sm sm:text-base leading-relaxed space-y-4">
            {content}

            <!-- CTA -->
            <div class="my-6 p-6 rounded-2xl bg-gradient-to-r from-indigo-950/80 to-purple-950/80 border border-indigo-500/30 text-center space-y-3">
                <h3 class="text-lg font-bold text-white">Ingin Mencoba Game HTML5 Gratis?</h3>
                <p class="text-xs text-slate-300">Jelajahi ratusan koleksi game balapan, puzzle, dan aksi terbaik di Jura Game.</p>
                <a href="../index.html" class="inline-block px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-indigo-600/40">Mainkan Game Sekarang</a>
            </div>
        </article>

        <!-- Back -->
        <div class="border-t border-slate-800 pt-6">
            <a href="index.html" class="inline-flex items-center gap-2 text-xs font-bold text-indigo-400 hover:text-indigo-300">
                <i data-lucide="arrow-left" class="w-4 h-4"></i> Kembali ke Katalog Blog
            </a>
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800 bg-slate-900/50 py-6 text-center text-xs text-slate-500 mt-12">
        <p>&copy; 2026 Jura game. Portal Game Gratis Online &amp; Blog Informasi.</p>
    </footer>
    <script>if(window.lucide)lucide.createIcons();</script>
</body>
</html>'''

CARD_WITH_IMG = '''
            <!-- Article Card: {slug} -->
            <article class="article-card bg-slate-900/80 backdrop-blur border border-slate-800 rounded-3xl overflow-hidden shadow-xl hover:border-indigo-500/50 transition-all duration-300 flex flex-col">
                <a href="{slug}.html" class="block aspect-[16/9] overflow-hidden bg-slate-800 relative">
                    <img src="{cover_image}" alt="{title}" class="w-full h-full object-cover transition-transform duration-500">
                    <span class="absolute top-3 right-3 px-3 py-1 rounded-full bg-slate-900/90 text-indigo-300 text-[10px] font-bold border border-slate-700/80 backdrop-blur-md">{category}</span>
                </a>
                <div class="p-6 flex flex-col flex-grow space-y-4">
                    <div class="text-[11px] text-slate-400 font-semibold flex items-center gap-2">
                        <i data-lucide="calendar" class="w-3.5 h-3.5"></i> {date}
                    </div>
                    <a href="{slug}.html" class="block group">
                        <h2 class="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors line-clamp-2">{title}</h2>
                    </a>
                    <p class="text-slate-400 text-sm line-clamp-3 flex-grow">{excerpt}</p>
                    <a href="{slug}.html" class="inline-flex items-center gap-1 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors w-fit pt-2">
                        Baca Selengkapnya <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                    </a>
                </div>
            </article>
'''

CARD_NO_IMG = '''
            <!-- Article Card: {slug} -->
            <article class="article-card bg-slate-900/80 backdrop-blur border border-slate-800 rounded-3xl overflow-hidden shadow-xl hover:border-indigo-500/50 transition-all duration-300 flex flex-col">
                <div class="p-6 flex flex-col flex-grow space-y-4">
                    <div class="flex justify-between items-center">
                        <div class="text-[11px] text-slate-400 font-semibold flex items-center gap-2">
                            <i data-lucide="calendar" class="w-3.5 h-3.5"></i> {date}
                        </div>
                        <span class="px-3 py-1 rounded-full bg-slate-800 text-amber-300 text-[10px] font-bold border border-slate-700/80">{category}</span>
                    </div>
                    <a href="{slug}.html" class="block group">
                        <h2 class="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors line-clamp-2">{title}</h2>
                    </a>
                    <p class="text-slate-400 text-sm line-clamp-4 flex-grow">{excerpt}</p>
                    <a href="{slug}.html" class="inline-flex items-center gap-1 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors w-fit pt-2">
                        Baca Selengkapnya <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                    </a>
                </div>
            </article>
'''

COVER_IMAGES = [
    "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&q=80",
    "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&q=80",
    "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?w=800&q=80",
    "https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=800&q=80",
    "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800&q=80",
    "https://images.unsplash.com/photo-1552820728-8b83bb6b2b0f?w=800&q=80",
]

# ── Core Functions ───────────────────────────────────────────────

def ai_write(topic):
    payload = json.dumps({
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": "Kamu penulis blog game Indonesia. Gaya santai, asik, informatif. Tulis dalam Bahasa Indonesia. Gunakan heading (##), bold (**), dan list. Langsung isi tanpa judul."},
            {"role": "user", "content": f"Tulis artikel blog game tentang: {topic}. 3-5 paragraf, gunakan sub-heading dan list agar enak dibaca."}
        ],
        "max_tokens": 1500
    }).encode('utf-8')
    req = urllib.request.Request(AI_API_URL, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}"
    })
    full = ""
    with urllib.request.urlopen(req, timeout=90) as r:
        for line in r:
            ls = line.decode('utf-8').strip()
            if ls.startswith("data: ") and ls != "data: [DONE]":
                try:
                    d = json.loads(ls[6:])
                    delta = d['choices'][0].get('delta', {})
                    if 'content' in delta:
                        full += delta['content']
                except:
                    continue
    return full.strip()

def update_sitemap(slugs):
    """Generate sitemap.xml dari daftar slug artikel."""
    urls = [
        f"  <url><loc>{BASE_URL}/</loc><priority>1.0</priority></url>",
        f"  <url><loc>{BASE_URL}/blog/</loc><priority>0.8</priority></url>",
    ]
    for s in slugs:
        urls.append(f"  <url><loc>{BASE_URL}/blog/{s}.html</loc><priority>0.7</priority></url>")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join(urls) + '\n'
    sitemap += '</urlset>'
    gh_put("sitemap.xml", sitemap, "Update sitemap.xml")
    print("   📄 sitemap.xml updated")

def update_blog_index(articles):
    """Rebuild blog/index.html dari daftar artikel."""
    content, sha = gh_get("blog/index.html")
    if not content:
        print("   ⚠️ blog/index.html belum ada, skip")
        return

    # Generate cards
    cards = ""
    for a in articles:
        slug = a.get('slug', slugify(a['title']))
        has_img = bool(a.get('cover_image'))
        tpl = CARD_WITH_IMG if has_img else CARD_NO_IMG
        cards += tpl.format(
            slug=slug,
            title=a['title'],
            date=a['date'],
            category=a.get('category', 'Tips Gaming'),
            cover_image=a.get('cover_image', ''),
            excerpt=a.get('excerpt', a.get('body', '')[:150])
        )

    # Replace content between markers
    marker_start = "<!-- Articles Grid -->"
    marker_end = "<!-- Pagination"
    grid_start = content.find(marker_start)
    grid_end = content.find(marker_end)

    if grid_start == -1 or grid_end == -1:
        # Fallback: cari grid div
        grid_start = content.find('<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">')
        if grid_start == -1:
            print("   ⚠️ Tidak bisa menemukan grid di blog/index.html")
            return
        # Cari closing </div> dari grid
        depth = 0
        i = grid_start
        while i < len(content):
            if content[i:i+4] == '<div':
                depth += 1
            elif content[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    grid_end = i + 6
                    break
            i += 1

    new_grid = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">\n'
    new_grid += cards
    new_grid += '\n        </div>\n        \n        '

    new_content = content[:grid_start] + new_grid + content[grid_end:]
    gh_put("blog/index.html", new_content, "Update blog catalog")
    print("   📋 blog/index.html updated")

def add_article(title, body_md, category="Tips Gaming", cover_image=None):
    slug = slugify(title)
    date_str = datetime.now().strftime("%d %B %Y")
    read_time = max(2, len(body_md.split()) // 150)
    excerpt = re.sub(r'[*#_]', '', body_md)[:180].strip()
    content_html = md_to_html(body_md)

    if not cover_image:
        import random
        cover_image = random.choice(COVER_IMAGES)

    article_url = f"{BASE_URL}/blog/{slug}.html"
    description = excerpt[:160]

    # 1. Generate & push artikel HTML
    article_html = ARTICLE_TEMPLATE.format(
        title=title,
        title_short=title[:40] + "..." if len(title) > 40 else title,
        description=description,
        keywords=slug.replace('-', ', '),
        url=article_url,
        cover_image=cover_image,
        category=category,
        date=date_str,
        read_time=read_time,
        content=content_html
    )
    gh_put(f"blog/{slug}.html", article_html, f"Add article: {title[:50]}")
    print(f"   ✅ blog/{slug}.html pushed")

    # 2. Update articles.json
    articles, _ = gh_get("articles.json")
    articles = json.loads(articles) if articles else []
    article_data = {
        "slug": slug,
        "title": title,
        "body": body_md,
        "excerpt": excerpt,
        "date": date_str,
        "category": category,
        "cover_image": cover_image,
        "source": "ai" if len(sys.argv) > 1 and sys.argv[1] == "--ai" else "manual"
    }
    # Hapus duplikat slug lama
    articles = [a for a in articles if a.get('slug') != slug]
    articles.insert(0, article_data)
    gh_put("articles.json", json.dumps(articles, ensure_ascii=False, indent=2), f"Update articles.json: {title[:40]}")
    print(f"   📦 articles.json updated ({len(articles)} artikel)")

    # 3. Update blog/index.html
    update_blog_index(articles)

    # 4. Update sitemap
    slugs = [a.get('slug', slugify(a['title'])) for a in articles]
    update_sitemap(slugs)

    print(f"\n🎉 SELESAI! Artikel live di: {article_url}")
    print(f"   (Vercel butuh ~1-2 menit untuk deploy)")

def list_articles():
    articles, _ = gh_get("articles.json")
    if not articles:
        print("Belum ada artikel.")
        return
    articles = json.loads(articles)
    print(f"Total: {len(articles)} artikel")
    for a in articles:
        print(f"  [{a['date']}] {a['title']}")
        print(f"    -> {BASE_URL}/blog/{a.get('slug', slugify(a['title']))}.html")

# ── Main ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == "--list":
        list_articles()
    elif sys.argv[1] == "--ai" and len(sys.argv) >= 3:
        topic = " ".join(sys.argv[2:])
        print(f"✍️ AI menulis artikel: {topic}...")
        body = ai_write(topic)
        if not body:
            print("❌ AI tidak menghasilkan konten")
            sys.exit(1)
        print(f"   ✍️ {len(body)} karakter ditulis")
        add_article(topic, body, source="ai")
    elif len(sys.argv) >= 3:
        title = sys.argv[1]
        body = " ".join(sys.argv[2:])
        category = "Tips Gaming"
        if "--kategori" in sys.argv:
            idx = sys.argv.index("--kategori")
            if idx + 1 < len(sys.argv):
                category = sys.argv[idx + 1]
                # Remove from body
                body = " ".join([a for i, a in enumerate(sys.argv[2:]) if i != idx - 2 and i != idx - 1])
        add_article(title, body, category=category)
    else:
        print(__doc__)
