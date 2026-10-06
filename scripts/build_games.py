#!/usr/bin/env python3
"""
build_games.py — Ambil katalog game dari GamePix + GameMonetize, gabung & simpan
ke games.json untuk di-cache server-side (agar load pertama website instan).

Jalankan harian via cron:  python3 scripts/build_games.py
Output: games.json (di root repo)
"""
import json, sys, urllib.parse, urllib.request, socket, html, re, time, os

socket.setdefaulttimeout(15)
GP_SID = "MUGAR"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "games.json")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JuraGameBot/1.0)"}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def clean(s):
    if not s:
        return ""
    s = html.unescape(str(s))
    return re.sub(r"\s+", " ", s).strip()


def slugify(s):
    s = clean(s).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:60] or "game"


def safe_thumb(g):
    for k in ("image", "thumbnail", "thumb", "banner_image", "imageUrl"):
        v = g.get(k)
        if v:
            return clean(v)
    return ""


def main():
    games = []
    seen = set()

    # --- GamePix (paginated: ambil 5 halaman x 24 = ~120) ---
    for page in range(1, 6):
        try:
            url = f"https://feeds.gamepix.com/v2/json?sid={GP_SID}&pagination=24&page={page}"
            data = fetch(url)
            items = data.get("items") or data.get("data") or []
            for g in items:
                t = clean(g.get("title"))
                if not t or t.lower() in seen:
                    continue
                seen.add(t.lower())
                games.append({
                    "id": g.get("id") or slugify(t),
                    "title": t,
                    "url": g.get("url") or "",
                    "category": clean(g.get("category")) or "Arcade",
                    "thumb": safe_thumb(g),
                    "description": clean(g.get("description")),
                    "source": "GP",
                })
            print(f"  GamePix page {page}: +{len(items)}", file=sys.stderr)
        except Exception as e:
            print(f"  GamePix page {page} ERROR: {e}", file=sys.stderr)
        time.sleep(0.3)

    # --- GameMonetize (ambil 300) ---
    try:
        gm = fetch("https://rss.gamemonetize.com/rssfeed.php?format=json&category=All&type=html5&amount=300")
        hits = gm if isinstance(gm, list) else (gm.get("segments", [{}])[0].get("hits", []) if isinstance(gm, dict) else [])
        for g in hits:
            t = clean(g.get("title"))
            if not t or t.lower() in seen:
                continue
            seen.add(t.lower())
            games.append({
                "id": g.get("id") or slugify(t),
                "title": t,
                "url": g.get("url") or "",
                "category": clean(g.get("category")) or "Arcade",
                "thumb": safe_thumb(g),
                "description": clean(g.get("description")),
                "source": "GM",
            })
        print(f"  GameMonetize: +{len(hits)}", file=sys.stderr)
    except Exception as e:
        print(f"  GameMonetize ERROR: {e}", file=sys.stderr)

    # Buang yang URL-nya kosong / bukan http(s)
    games = [g for g in games if re.match(r"^https?://", g.get("url") or "")]
    # Bersihkan HTML di deskripsi
    for g in games:
        g["description"] = re.sub(r"<[^>]+>", "", g["description"])[:400]

    if len(games) < 20:
        print(f"PERINGATAN: hanya {len(games)} game — kemungkinan API gagal. Tidak menimpa games.json.", file=sys.stderr)
        sys.exit(1)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(games, f, ensure_ascii=False, separators=(",", ":"))
    print(f"OK: {len(games)} game ditulis ke {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
