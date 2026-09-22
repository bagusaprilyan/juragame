#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news_fetcher.py — Ambil berita game terbaru dari RSS feed terpercaya.

Fitur:
  - Ambil dari 6 sumber (IGN, GameSpot, Eurogamer, VGC, PC Gamer, Gamebrott)
  - Normalisasi judul, ringkasan, tanggal, link sumber, gambar
  - Dedupe: hindari berita yang sudah pernah dipakai
  - Pilih berita paling "layak" (ada ringkasan, judul jelas, belum dipakai)

Usage:
  python3 news_fetcher.py                    # tampilkan 10 berita terbaru
  python3 news_fetcher.py --pick             # pilih 1 berita terbaik (JSON)
  python3 news_fetcher.py --mark <link>      # tandai berita sudah dipakai
"""
import sys, os, re, json, html, random, urllib.request, urllib.error
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
USED_FILE = os.path.join(HERE, "work", "news_used.json")
os.makedirs(os.path.dirname(USED_FILE), exist_ok=True)

UA = "Mozilla/5.0 (compatible; JuraGameBot/1.0; +https://juragame.com)"

FEEDS = [
    {"name": "GameSpot",   "url": "https://www.gamespot.com/feeds/game-news/",        "lang": "en"},
    {"name": "VGC",        "url": "https://www.videogameschronicle.com/feed/",        "lang": "en"},
    {"name": "Eurogamer",  "url": "https://www.eurogamer.net/feed",                   "lang": "en"},
    {"name": "Gamebrott",  "url": "https://gamebrott.com/feed/",                      "lang": "id"},
    {"name": "IGN",        "url": "https://feeds.feedburner.com/ign/games-all",       "lang": "en"},
]


def article_text(url, max_chars=4000):
    """Ambil teks isi artikel dari URL (untuk bahan tulis ulang)."""
    try:
        raw = _fetch(url, timeout=25)
    except Exception as e:
        return ""
    # Buang script/style
    raw = re.sub(r"<(script|style|nav|header|footer|aside)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    # Ambil paragraf
    paras = re.findall(r"<p[^>]*>(.*?)</p>", raw, re.S | re.I)
    text = " ".join(_clean(p) for p in paras)
    text = re.sub(r"\s+", " ", text).strip()
    # Buang boilerplate umum
    for junk in ["Sign up for the newsletter", "Subscribe to", "Sign in", "Log in",
                 "Read more:", "Follow us", "Advertisement", "Comments"]:
        text = text.replace(junk, " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def _fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def _clean(t):
    """Bersihkan HTML entity & tag dari teks."""
    if not t:
        return ""
    t = html.unescape(t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def _parse_rss(xml, source):
    """Parser RSS/Atom sederhana → list dict."""
    items = []
    # RSS <item>
    for block in re.findall(r"<item[\s>].*?</item>", xml, re.S):
        def g(tag):
            m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", block, re.S)
            return m.group(1) if m else ""
        title = _clean(g("title"))
        link = _clean(g("link")) or _clean(re.search(r"<guid[^>]*>(.*?)</guid>", block, re.S).group(1) if re.search(r"<guid[^>]*>(.*?)</guid>", block, re.S) else "")
        desc = _clean(g("description")) or _clean(g("content:encoded"))
        date = _clean(g("pubDate")) or _clean(g("dc:date"))
        img = ""
        mm = re.search(r'<media:content[^>]+url="([^"]+)"', block) or \
             re.search(r'<enclosure[^>]+url="([^"]+)"', block) or \
             re.search(r'<img[^>]+src="([^"]+)"', block)
        if mm:
            img = mm.group(1)
        if title and link:
            items.append({"title": title, "link": link, "summary": desc,
                          "date": date, "image": img, "source": source})
    # Atom <entry>
    for block in re.findall(r"<entry[\s>].*?</entry>", xml, re.S):
        def g(tag):
            m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", block, re.S)
            return m.group(1) if m else ""
        title = _clean(g("title"))
        link = ""
        lm = re.search(r'<link[^>]+href="([^"]+)"', block)
        if lm:
            link = lm.group(1)
        desc = _clean(g("summary")) or _clean(g("content"))
        date = _clean(g("updated")) or _clean(g("published"))
        img = ""
        mm = re.search(r'<media:content[^>]+url="([^"]+)"', block) or re.search(r'<img[^>]+src="([^"]+)"', block)
        if mm:
            img = mm.group(1)
        if title and link:
            items.append({"title": title, "link": link, "summary": desc,
                          "date": date, "image": img, "source": source})
    return items


def fetch_all(verbose=True):
    """Ambil semua berita dari semua feed."""
    all_items = []
    for f in FEEDS:
        try:
            xml = _fetch(f["url"])
            items = _parse_rss(xml, f["name"])
            for it in items:
                it["lang"] = f["lang"]
            all_items.extend(items)
            if verbose:
                print(f"  ✅ {f['name']}: {len(items)} berita")
        except Exception as e:
            if verbose:
                print(f"  ❌ {f['name']}: {str(e)[:60]}")
    return all_items


def _load_used():
    try:
        with open(USED_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def _title_key(t):
    """Kunci pembanding judul (buang tanda baca & case)."""
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()[:60]


def mark_used(link, title=""):
    used = _load_used()
    used.append({"link": link, "title": title, "at": datetime.now(timezone.utc).isoformat()})
    used = used[-500:]
    with open(USED_FILE, "w") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)


def score(item):
    """Nilai kelayakan berita (makin tinggi makin baik)."""
    s = 0
    if len(item.get("summary", "")) > 120:
        s += 3
    elif len(item.get("summary", "")) > 60:
        s += 1
    if item.get("image"):
        s += 2
    if item.get("lang") == "id":
        s += 2            # berita Indonesia lebih relevan
    t = item.get("title", "")
    if 25 <= len(t) <= 110:
        s += 2            # judul tidak terlalu pendek/panjang
    # Kata kunci menarik
    hot = ["update", "patch", "rilis", "release", "launch", "sequel", "remake",
           "announce", "trailer", "beta", "free", "gratis", "dlc", "collab",
           "sale", "mobile", "nintendo", "playstation", "xbox", "steam"]
    for kw in hot:
        if kw in t.lower():
            s += 1
    return s


def pick_one(exclude_keys=None, verbose=True):
    """Pilih 1 berita terbaik yang belum pernah dipakai."""
    exclude_keys = exclude_keys or set()
    items = fetch_all(verbose=verbose)
    if not items:
        return None

    used = _load_used()
    used_links = {u["link"] for u in used}
    used_titles = {_title_key(u.get("title", "")) for u in used if u.get("title")}

    fresh = []
    for it in items:
        if it["link"] in used_links:
            continue
        tk = _title_key(it["title"])
        if tk in used_titles or tk in exclude_keys:
            continue
        # Buang judul yang sangat pendek/kosong
        if len(it["title"]) < 15:
            continue
        fresh.append(it)

    if not fresh:
        return None

    # Ambil 5 terbaik, lalu pilih acak (variasi)
    fresh.sort(key=score, reverse=True)
    top = fresh[:5]
    return random.choice(top)


if __name__ == "__main__":
    if "--mark" in sys.argv:
        idx = sys.argv.index("--mark")
        link = sys.argv[idx + 1]
        title = sys.argv[idx + 2] if len(sys.argv) > idx + 2 else ""
        mark_used(link, title)
        print(f"✅ Ditandai dipakai: {link[:70]}")
    elif "--pick" in sys.argv:
        it = pick_one(verbose=(len(sys.argv) < 3 or "--quiet" not in sys.argv))
        if it:
            print(json.dumps(it, ensure_ascii=False, indent=2))
        else:
            print("{}")
    else:
        items = fetch_all()
        print(f"\nTotal: {len(items)} berita")
        items.sort(key=score, reverse=True)
        print("\n=== 10 BERITA TERBAIK ===")
        for i, it in enumerate(items[:10], 1):
            print(f"{i}. [{it['source']}] {it['title'][:80]}")
            print(f"   {it['link'][:90]}")
            print(f"   skor={score(it)} | ringkasan={len(it.get('summary',''))} char | img={'ya' if it.get('image') else 'tidak'}")
