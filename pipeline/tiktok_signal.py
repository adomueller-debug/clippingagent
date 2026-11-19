#!/usr/bin/env python3
"""TikTok-Signal: welche Momente gehen auf den TikTok-Profilen der Streamer gerade viral?

Liest nur die öffentlichen Profile (Titel, Aufrufe). Lädt nichts herunter und lädt nichts hoch.
Der Kurator sucht die genannten Momente danach im Original-Clip auf Twitch/Kick.
Fertige TikTok-Edits anderer Accounts werden nie wiederverwendet.

  python pipeline/tiktok_signal.py                 # Posts der letzten 3 Tage
  python pipeline/tiktok_signal.py --tage 1 --muster gta
"""
import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def profil(handle, anzahl):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings", "--flat-playlist", "--playlist-end", str(anzahl),
                        "-J", f"https://www.tiktok.com/@{handle}"], capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        print(f"[tiktok] @{handle}: {r.stderr.strip()[-200:]}", file=sys.stderr)
        return []
    return json.loads(r.stdout).get("entries") or []


def main():
    cfg = json.loads((ROOT / "config/kanal.json").read_text())
    ap = argparse.ArgumentParser()
    ap.add_argument("--tage", type=float, default=3)
    ap.add_argument("--anzahl", type=int, default=15, help="neueste Posts pro Profil")
    ap.add_argument("--muster", default=r"gta|grand theft", help="Regex auf den Post-Titel; leer = alle")
    ap.add_argument("--out", default=str(ROOT / "arbeit/tiktok_signal.json"))
    a = ap.parse_args()

    grenze = datetime.now(timezone.utc) - timedelta(days=a.tage)
    muster = re.compile(a.muster, re.I) if a.muster else None
    streamer = [s for s in cfg["streamer"] if s.get("tiktok")]

    posts = []
    with ThreadPoolExecutor(3) as pool:
        for s, entries in zip(streamer, pool.map(lambda s: profil(s["tiktok"], a.anzahl), streamer)):
            for e in entries:
                # TikTok-IDs enthalten den Zeitpunkt in den oberen 32 Bit
                zeit = datetime.fromtimestamp(int(e["id"]) >> 32, timezone.utc)
                titel = e.get("title") or e.get("description") or ""
                if zeit < grenze or (muster and not muster.search(titel)):
                    continue
                posts.append({"streamer": s["name"], "sprache": s["sprache"], "views": e.get("view_count") or 0,
                              "zeit": zeit.isoformat(), "titel": titel, "url": e.get("url")})

    posts.sort(key=lambda p: -p["views"])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(posts, ensure_ascii=False, indent=2))
    print(f"[tiktok] {len(posts)} passende Posts -> {a.out}")
    for p in posts[:25]:
        print(f"  {p['views']:>9}  {p['streamer']:<13} {p['zeit'][5:16]}  {p['titel'][:70]}")


if __name__ == "__main__":
    main()
