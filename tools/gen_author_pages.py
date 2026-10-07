#!/usr/bin/env python3
"""
gen_author_pages.py — Bikin halaman Redaksi (/redaksi) + Penulis (/penulis/bagus-aprilyan)
untuk memperkuat E-E-A-T (wajah manusia) demi lolos AdSense "low value content".
"""
import os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AUTHOR = {
    "name": "Bagus Aprilyan",
    "slug": "bagus-aprilyan",
    "role": "Pendiri & Editor",
    "bio": ("Bagus Aprilyan adalah pendiri Jura Game. Ia menekuni dunia game kasual berbasis "
            "browser sejak lama dan fokus membahas game yang ringan, gratis, serta bisa langsung "
            "dimainkan tanpa install. Selain menulis, ia mengurus kurasi katalog game dan "
            "memastikan setiap judul yang tampil layak dimainkan."),
    "email": "redaksi@juragame.com",
}

HEAD = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://juragame.com/{slug}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="https://juragame.com/{slug}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Jura Game">
<meta name="theme-color" content="#0a0f22">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="/css/tailwind.css">
<style>
  body{{background:#0a0f22;color:#cbd5e1;font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;line-height:1.7}}
  .wrap{{max-width:820px;margin:0 auto;padding:24px 20px 64px}}
  nav.top{{display:flex;gap:16px;font-size:.85rem;margin-bottom:28px}}
  nav.top a{{color:#94a3b8;text-decoration:none}}
  nav.top a:hover{{color:#fff}}
  h1{{color:#fff;font-weight:900;font-size:2rem;margin:0 0 .3rem}}
  h2{{color:#fff;font-weight:800;font-size:1.25rem;margin:2rem 0 .6rem}}
  a{{color:#a78bfa}}
  .card{{background:#0f172a;border:1px solid #1e293b;border-radius:16px;padding:20px;margin:16px 0}}
  .avatar{{width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#3b82f6);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900;font-size:1.5rem;flex-shrink:0}}
  .role{{color:#a78bfa;font-weight:700;font-size:.85rem;text-transform:uppercase;letter-spacing:.05em}}
  footer{{border-top:1px solid #1e293b;margin-top:48px;padding-top:20px;font-size:.8rem;color:#64748b;text-align:center}}
</style>
</head>
<body>
<div class="wrap">
<nav class="top">
  <a href="/">&larr; Jura Game</a>
  <a href="/blog/">Blog</a>
  <a href="/redaksi">Redaksi</a>
  <a href="/contact">Kontak</a>
</nav>
"""

FOOT = """<footer>
  <p>Jura Game &mdash; portal game gratis, mainkan langsung di browser tanpa install.</p>
  <p>&copy; 2026 Jura Game.</p>
</footer>
</div>
</body>
</html>
"""


def build_redaksi():
    a = AUTHOR
    body = f"""<h1>Redaksi Jura Game</h1>
<p>Jura Game dikelola oleh tim kecil yang fokus pada satu hal: menyajikan game gratis yang benar-benar bisa dimainkan langsung di browser. Kami mengurasi konten, menjaga kualitas katalog, dan menulis panduan yang jujur untuk pembaca.</p>

<h2>Tim Kami</h2>
<div class="card">
  <div style="display:flex;gap:16px;align-items:flex-start">
    <div class="avatar">BA</div>
    <div>
      <h3 style="color:#fff;margin:0 0 2px;font-size:1.1rem"><a href="/penulis/{a['slug']}" style="color:#fff;text-decoration:none">{a['name']}</a></h3>
      <div class="role">{a['role']}</div>
      <p style="margin:.6rem 0 0">{a['bio']}</p>
      <p style="margin:.5rem 0 0"><a href="/penulis/{a['slug']}">Lihat profil lengkap &rarr;</a></p>
    </div>
  </div>
</div>

<h2>Standar Konten</h2>
<p>Setiap artikel dan rekomendasi di Jura Game disusun dengan prinsip berikut:</p>
<ul>
  <li><strong>Akurat &amp; dapat diverifikasi</strong> &mdash; kami menyebut nama game yang benar-benar tersedia dan bisa dimainkan, bukan rumor.</li>
  <li><strong>Berguna bagi pembaca</strong> &mdash; fokus pada penjelasan gameplay nyata, bukan sekadar opini tanpa dasar.</li>
  <li><strong>Diperbarui berkala</strong> &mdash; katalog game dan artikel kami tinjau ulang agar tetap relevan.</li>
</ul>

<h2>Kontak Redaksi</h2>
<p>Pertanyaan, koreksi, atau kerja sama: <a href="mailto:{a['email']}">{a['email']}</a> &mdash; atau lewat halaman <a href="/contact">Kontak</a>.</p>
"""
    open(os.path.join(ROOT, "redaksi.html"), "w", encoding="utf-8").write(
        HEAD.format(title="Redaksi — Jura Game", desc="Kenali tim redaksi di balik Jura Game: siapa yang menulis, mengurasi, dan menjaga kualitas konten game gratis kami.", slug="redaksi")
        + body + FOOT)
    print("✅ redaksi.html")


def build_author():
    a = AUTHOR
    body = f"""<h1>{a['name']}</h1>
<div class="role">{a['role']} &middot; Jura Game</div>

<div class="card" style="margin-top:20px">
  <div style="display:flex;gap:16px;align-items:flex-start">
    <div class="avatar">BA</div>
    <div>
      <p style="margin:0">{a['bio']}</p>
      <p style="margin:.8rem 0 0"><strong>Fokus liputan:</strong> game browser gratis, game kasual ringan, rekomendasi game tanpa install, dan panduan bermain untuk pemula.</p>
      <p style="margin:.5rem 0 0"><strong>Kontak:</strong> <a href="mailto:{a['email']}">{a['email']}</a></p>
    </div>
  </div>
</div>

<h2>Artikel oleh {a['name']}</h2>
<p>Seluruh artikel di <a href="/blog/">blog Jura Game</a> ditulis dan dikurasi oleh {a['name']} bersama tim redaksi. Kami membahas rekomendasi game, tips bermain, dan berita seputar dunia game gratis yang bisa dimainkan langsung di browser.</p>
<p><a href="/blog/">Lihat semua artikel &rarr;</a></p>
"""
    os.makedirs(os.path.join(ROOT, "penulis"), exist_ok=True)
    open(os.path.join(ROOT, f"penulis/{a['slug']}.html"), "w", encoding="utf-8").write(
        HEAD.format(title=f"{a['name']} — Penulis Jura Game", desc=f"Profil {a['name']}, {a['role']} di Jura Game. Penulis konten game gratis berbasis browser.", slug=f"penulis/{a['slug']}")
        + body + FOOT)
    print("✅ penulis/%s.html" % a['slug'])


if __name__ == "__main__":
    build_redaksi()
    build_author()
    print("Selesai: halaman Redaksi + Penulis dibuat.")
