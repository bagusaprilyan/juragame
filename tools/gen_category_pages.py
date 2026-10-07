#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator halaman kategori/pilar SEO untuk juragame.com.
Menghasilkan /game/<slug>.html — halaman landing yang menargetkan keyword
long-tail (mirip pola Poki.com /id/<kategori>), lengkap dengan:
  - H1 = keyword utama
  - daftar game (kartu pre-render, crawlable)
  - meta title/description, canonical, OG
  - structured data ItemList + BreadcrumbList
  - internal linking ke kategori lain + homepage

Jalankan: python3 tools/gen_category_pages.py
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://juragame.com"
TODAY = datetime.datetime.utcnow().strftime("%Y-%m-%d")

# Kategori -> definisi pilar
CATEGORIES = [
    {
        "slug": "puzzle",
        "title": "Game Puzzle Online Gratis",
        "h1": "Game Puzzle Online Gratis",
        "desc": "Kumpulan game puzzle online gratis paling seru — teka-teki, match-3, otak-atik logika, dan game asah otak yang bisa langsung dimainkan di browser tanpa download.",
        "match": ["puzzles", "puzzle", "match-3", "memory", "brain", "2048", "hidden-object", "block", "trivia", "math"],
    },
    {
        "slug": "arcade",
        "title": "Game Arcade Online Gratis",
        "h1": "Game Arcade Online Gratis",
        "desc": "Main game arcade online gratis — klasik, retro, tembak-tembakan, dan game cepat saji yang bikin nagih. Semua bisa dimainkan langsung di HP atau PC tanpa install.",
        "match": ["arcade", "retro", "clicker", "hypercasual", "hyper-casual", "casual", "runner", "snake", "fun", "addictive", "idle"],
    },
    {
        "slug": "balapan",
        "title": "Game Balapan Online Gratis (Racing)",
        "h1": "Game Balapan Online Gratis",
        "desc": "Deretan game balapan online gratis terbaik — mobil, motor, dan racing seru yang ringan untuk HP kentang. Mainkan langsung di browser tanpa download.",
        "match": ["racing", "car"],
    },
    {
        "slug": "tembak-tembakan",
        "title": "Game Tembak-Tembakan Online Gratis",
        "h1": "Game Tembak-Tembakan Online Gratis",
        "desc": "Kumpulan game tembak-tembakan online gratis — shooter, FPS, battle, dan game perang seru yang bisa langsung dimainkan di browser tanpa install.",
        "match": ["shooting", "shooter", "first-person-shooter", "battle", "tanks", "zombie"],
    },
    {
        "slug": "petualangan",
        "title": "Game Petualangan Online Gratis (Adventure)",
        "h1": "Game Petualangan Online Gratis",
        "desc": "Game petualangan (adventure) online gratis paling seru — jelajah dunia, selesaikan misi, dan tantangan seru langsung di browser tanpa download.",
        "match": ["adventure", "platformer", "strategy", "simulation", "building", "farming", "monster", "robots"],
    },
    {
        "slug": "olahraga",
        "title": "Game Olahraga Online Gratis (Sports)",
        "h1": "Game Olahraga Online Gratis",
        "desc": "Main game olahraga online gratis — sepak bola, basket, golf, dan sports seru yang ringan dan bisa dimainkan langsung di browser tanpa install.",
        "match": ["sports", "basketball", "soccer", "golf", "ball", "airplane"],
    },
    {
        "slug": "2-pemain",
        "title": "Game 2 Pemain Online Gratis (Multiplayer)",
        "h1": "Game 2 Pemain Online Gratis",
        "desc": "Game 2 pemain online gratis untuk dimainkan berdua dengan teman — multiplayer, fighting, dan game seru bareng di satu perangkat atau online.",
        "match": ["multiplayer", "fighting", "2-pemain", "io", "battle"],
    },
    {
        "slug": "game-io",
        "title": "Game .io Online Gratis",
        "h1": "Game .io Online Gratis",
        "desc": "Game .io online gratis paling seru dan kompetitif — sederhana tapi bikin nagih, bisa dimainkan langsung di browser tanpa download.",
        "match": ["io"],
    },
]

# Style inline ringkas (senada tema Aurora Glass)
STYLE = """
*{box-sizing:border-box}body{margin:0;background:#0a0f22;color:#e2e8f0;font-family:Inter,system-ui,-apple-system,sans-serif}
a{color:inherit;text-decoration:none}
.wrap{max-width:1100px;margin:0 auto;padding:20px}
header.top{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid #1e293b}
.logo{font-weight:900;font-size:1.25rem;background:linear-gradient(90deg,#a78bfa,#60a5fa);-webkit-background-clip:text;background-clip:text;color:transparent}
.nav a{margin-left:14px;font-size:.85rem;color:#94a3b8}.nav a:hover{color:#e2e8f0}
h1{font-size:1.9rem;line-height:1.15;margin:18px 0 8px;font-weight:900}
.grad{background:linear-gradient(90deg,#a78bfa,#60a5fa,#fbbf24);-webkit-background-clip:text;background-clip:text;color:transparent}
.lead{color:#94a3b8;font-size:.95rem;max-width:720px;margin-bottom:20px}
.crumbs{font-size:.78rem;color:#64748b;margin-top:10px}
.crumbs a{color:#818cf8}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin-top:10px}
.card{background:#111a33;border:1px solid #1e293b;border-radius:14px;overflow:hidden;transition:.2s}
.card:hover{transform:translateY(-3px);border-color:#6366f1}
.card img{width:100%;aspect-ratio:1;object-fit:cover;display:block;background:#0a0f22}
.card .t{padding:8px 10px;font-size:.8rem;font-weight:600;line-height:1.25}
.tags{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0}
.tags a{background:#1e293b;border:1px solid #334155;padding:6px 12px;border-radius:999px;font-size:.8rem}
.tags a:hover{background:#312e81;border-color:#6366f1}
footer{padding:26px 20px;color:#64748b;font-size:.8rem;text-align:center;border-top:1px solid #1e293b;margin-top:34px}
"""


def esc(s):
    return html.escape(str(s or ""))


def render(cat, games):
    cards = []
    for g in games:
        thumb = esc(g.get("thumb", ""))
        title = esc(g.get("title", ""))
        url = g.get("url", "")
        cards.append(
            f'<a class="card" href="/?open={esc(g.get("id",""))}" data-game-url="{esc(url)}">'
            f'<img src="{thumb}" alt="{title} - game online gratis" loading="lazy" decoding="async" width="150" height="150" '
            f'onerror="this.style.background=\'#1e293b\';this.removeAttribute(\'src\')">'
            f'<div class="t">{title}</div></a>'
        )
    cards_html = "\n".join(cards)

    # structured data
    items = []
    for i, g in enumerate(games[:50], 1):
        items.append({"@type": "ListItem", "position": i, "name": g.get("title", ""), "url": g.get("url", "")})
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": cat["title"],
                "description": cat["desc"],
                "url": f"{BASE}/game/{cat['slug']}",
                "inLanguage": "id",
                "isPartOf": {"@type": "WebSite", "name": "Jura Game", "url": f"{BASE}/"},
            },
            {
                "@type": "ItemList",
                "name": cat["h1"],
                "numberOfItems": len(games),
                "itemListElement": items,
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Beranda", "item": f"{BASE}/"},
                    {"@type": "ListItem", "position": 2, "name": cat["h1"], "item": f"{BASE}/game/{cat['slug']}"},
                ],
            },
        ],
    }

    tags_html = "\n".join(
        f'<a href="/game/{c["slug"]}">{esc(c["h1"])}</a>'
        for c in CATEGORIES if c["slug"] != cat["slug"]
    )

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(cat["title"])} | Jura Game</title>
<meta name="description" content="{esc(cat["desc"])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{BASE}/game/{cat['slug']}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(cat["h1"])}">
<meta property="og:description" content="{esc(cat["desc"])}">
<meta property="og:url" content="{BASE}/game/{cat['slug']}">
<meta property="og:site_name" content="Jura Game">
<meta name="theme-color" content="#0a0f22">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{STYLE}</style>
</head>
<body>
<header class="top">
  <a class="logo" href="/">Jura<span style="color:#60a5fa">Game</span></a>
  <nav class="nav">
    <a href="/">Beranda</a>
    <a href="/blog/">Blog</a>
    <a href="/about">Tentang</a>
    <a href="/contact">Kontak</a>
  </nav>
</header>
<main class="wrap">
  <div class="crumbs"><a href="/">Beranda</a> › {esc(cat["h1"])}</div>
  <h1>{esc(cat["h1"])} <span class="grad">Tanpa Download</span></h1>
  <p class="lead">{esc(cat["desc"])}</p>
  <h2 style="font-size:1.15rem;margin:8px 0 4px">Daftar {esc(cat["h1"])} ({len(games)} game)</h2>
  <div class="grid">
{cards_html}
  </div>
  <div class="tags">
{tags_html}
  </div>
</main>
<footer>
  <p>&copy; {datetime.datetime.utcnow().year} Jura Game — Main game online gratis tanpa download, langsung di browser.</p>
  <p><a href="/privacy">Kebijakan Privasi</a> · <a href="/terms">Syarat</a> · <a href="/contact">Kontak</a></p>
</footer>
</body>
</html>
"""


def main():
    d = json.load(open(os.path.join(ROOT, "games.json"), encoding="utf-8"))
    games = d if isinstance(d, list) else d.get("games", [])
    outdir = os.path.join(ROOT, "game")
    os.makedirs(outdir, exist_ok=True)

    total = 0
    for cat in CATEGORIES:
        match = set(cat["match"])
        sel = [g for g in games if (g.get("category") or "").lower() in match]
        if not sel:
            continue
        with open(os.path.join(outdir, f"{cat['slug']}.html"), "w", encoding="utf-8") as fh:
            fh.write(render(cat, sel))
        total += 1
        print(f"  /game/{cat['slug']}.html  ({len(sel)} game)")
    print(f"✅ {total} halaman kategori dibuat di /game/")


if __name__ == "__main__":
    main()
