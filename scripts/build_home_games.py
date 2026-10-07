#!/usr/bin/env python3
"""Bikin games-home.json: subset ringan untuk render awal homepage.
Ambil N game pertama, deskripsi dipotong (buat kartu/modal enteng).
Full 421 game tetap di games.json (di-load idle di background)."""
import json, os, sys

N = 72  # lebih dari cukup: 24 (Semua Game) + 24 (terpopuler) + 24 (rekomendasi)
MAX_DESC = 160

repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(repo, "games.json")
out = os.path.join(repo, "games-home.json")

d = json.load(open(src, encoding="utf-8"))
games = d if isinstance(d, list) else d.get("games", [])

subset = []
for g in games[:N]:
    item = {
        "id": g.get("id", ""),
        "title": g.get("title", ""),
        "url": g.get("url", ""),
        "category": g.get("category", ""),
        "thumb": g.get("thumb", ""),
        "source": g.get("source", ""),
    }
    desc = g.get("description", "") or ""
    item["description"] = desc[:MAX_DESC]
    subset.append(item)

json.dump(subset, open(out, "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))

full_kb = os.path.getsize(src) / 1024
home_kb = os.path.getsize(out) / 1024
print(f"games-home.json: {len(subset)} game, {home_kb:.1f} KB "
      f"(full {full_kb:.1f} KB, hemat {100*(1-home_kb/full_kb):.0f}%)")
