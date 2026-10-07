#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate sitemap.xml LOKAL (di repo) dengan <lastmod> dari tanggal file.
Sertakan: homepage, blog index, artikel blog, halaman statis, halaman kategori.
Jalankan: python3 tools/gen_sitemap_local.py
"""
import os, json, re, datetime

BASE = "https://juragame.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def mtime_iso(path):
    if os.path.exists(path):
        ts = os.path.getmtime(path)
        return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")


def slugify(t):
    t = t.lower().strip()
    t = re.sub(r'[^\w\s-]', '', t)
    t = re.sub(r'[\s_]+', '-', t)
    return re.sub(r'-+', '-', t)[:60].strip('-')


entries = []  # (loc, priority, changefreq, lastmod)

# Homepage
entries.append((f"{BASE}/", "1.0", "daily", mtime_iso(os.path.join(ROOT, "index.html"))))
# Blog index
entries.append((f"{BASE}/blog/", "0.8", "daily", mtime_iso(os.path.join(ROOT, "blog", "index.html"))))

# Halaman statis
for p in ["about", "redaksi", "contact", "privacy", "disclaimer", "terms"]:
    f = os.path.join(ROOT, f"{p}.html")
    entries.append((f"{BASE}/{p}", "0.5", "monthly", mtime_iso(f)))

# Halaman penulis (E-E-A-T) — /penulis/<slug>
pen_dir = os.path.join(ROOT, "penulis")
if os.path.isdir(pen_dir):
    for fn in sorted(os.listdir(pen_dir)):
        if fn.endswith(".html"):
            f = os.path.join(pen_dir, fn)
            entries.append((f"{BASE}/penulis/{fn[:-5]}", "0.5", "monthly", mtime_iso(f)))

# Artikel blog (dari articles-index.json / articles.json)
arts_path = os.path.join(ROOT, "articles-index.json")
if not os.path.exists(arts_path):
    arts_path = os.path.join(ROOT, "articles.json")
articles = []
if os.path.exists(arts_path):
    with open(arts_path, encoding="utf-8") as fh:
        articles = json.load(fh)
if isinstance(articles, dict):
    articles = articles.get("articles", [])

seen = set()
for a in articles:
    s = a.get('slug') or slugify(a.get('title', ''))
    if not s or s in seen:
        continue
    seen.add(s)
    f = os.path.join(ROOT, "blog", f"{s}.html")
    entries.append((f"{BASE}/blog/{s}", "0.7", "weekly", mtime_iso(f)))

# Halaman kategori (kalau ada)
cat_dir = os.path.join(ROOT, "game")
if os.path.isdir(cat_dir):
    for fn in sorted(os.listdir(cat_dir)):
        if fn.endswith(".html"):
            f = os.path.join(cat_dir, fn)
            entries.append((f"{BASE}/game/{fn[:-5]}", "0.8", "weekly", mtime_iso(f)))

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, pri, freq, lm in entries:
    lines.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lm}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>")
lines.append('</urlset>')

out = os.path.join(ROOT, "sitemap.xml")
with open(out, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")
print(f"✅ sitemap.xml: {len(entries)} URL (dengan lastmod)")
