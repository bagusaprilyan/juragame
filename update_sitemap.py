#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Perbarui sitemap.xml juragame.com — sertakan halaman statis + semua artikel blog."""
import json, base64, os, re, urllib.request, urllib.error

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = "bagusaprilyan/juragame"
BASE = "https://juragame.com"
API = f"https://api.github.com/repos/{REPO}/contents"
GH = {"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "HermesAgent", "Content-Type": "application/json"}


def gh_get(path):
    req = urllib.request.Request(f"{API}/{path}", headers=GH)
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
    payload = {"message": message, "content": base64.b64encode(content.encode()).decode()}
    if sha:
        payload["sha"] = sha
    req = urllib.request.Request(f"{API}/{path}", data=json.dumps(payload).encode(), method="PUT", headers=GH)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def slugify(t):
    t = t.lower().strip()
    t = re.sub(r'[^\w\s-]', '', t)
    t = re.sub(r'[\s_]+', '-', t)
    return re.sub(r'-+', '-', t)[:60].strip('-')


arts_raw, _ = gh_get("articles.json")
articles = json.loads(arts_raw) if arts_raw else []

entries = [
    (f"{BASE}/", "1.0", "daily"),
    (f"{BASE}/blog/", "0.8", "daily"),
]
for p in ["about", "contact", "privacy", "disclaimer", "terms"]:
    entries.append((f"{BASE}/{p}.html", "0.5", "monthly"))
for a in articles:
    s = a.get('slug') or slugify(a['title'])
    entries.append((f"{BASE}/blog/{s}.html", "0.7", "weekly"))

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, pri, freq in entries:
    lines.append(f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>")
lines.append('</urlset>')

gh_put("sitemap.xml", "\n".join(lines), "Update sitemap: halaman statis + artikel")
print(f"✅ sitemap.xml diperbarui: {len(entries)} URL")
