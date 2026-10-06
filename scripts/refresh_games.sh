#!/bin/bash
# refresh_games.sh — Cron harian: perbarui games.json lalu commit+push ke GitHub
# Tambahkan ke crontab:
#   15 3 * * * /home/ubuntu/juragame_cron/refresh_games.sh >> /home/ubuntu/juragame_cron/refresh.log 2>&1
set -e
REPO="/home/ubuntu/juragame_cron/repo"
cd "$REPO"
git pull --ff-only origin main || git pull --ff-only origin master || true
python3 scripts/build_games.py
if ! git diff --quiet -- games.json; then
  git config user.name "Bagusaprilyan"
  git config user.email "bagoesigner@gmail.com"
  git add games.json
  git commit -m "chore: refresh katalog game ($(date +%Y-%m-%d))" || true
  git push origin HEAD
  echo "[$(date)] games.json diperbarui & dipush"
else
  echo "[$(date)] tidak ada perubahan"
fi
