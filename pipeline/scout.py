#!/usr/bin/env python3
"""Scout: sammelt Clips der konfigurierten Streamer (Twitch und Kick) und filtert nach Spiel.

Twitch über yt-dlp, Kick über die öffentliche Clip-API. Kein Developer-Account nötig.
Ergebnis: JSON-Liste nach Views sortiert, ohne bereits verwendete Clips.

  python pipeline/scout.py                                  # Muster/Zeitraum aus config/kanal.json
  python pipeline/scout.py --spiele '\\bgrand theft auto v\\b' --zeitraum 7d
"""
import argparse
import json
import re
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KICK_ZEIT = {"24hr": "day", "7d": "week", "30d": "month", "all": "all"}


def ytdlp_json(args, timeout=120):
    r = subprocess.run(["yt-dlp", "--no-warnings", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[-300:])
    return json.loads(r.stdout)


def twitch_clips(s, zeitraum, limit):
    url = f"https://www.twitch.tv/{s['login']}/clips?filter=clips&range={zeitraum}"
    entries = ytdlp_json(["--flat-playlist", "--playlist-end", str(limit), "-J", url]).get("entries") or []

    def details(e):
        try:
            d = ytdlp_json(["-j", "--skip-download", e["url"]])
        except Exception as ex:
            print(f"[scout] {e['url']}: {ex}", file=sys.stderr)
            return None
        return {
            "id": f"twitch:{e['id']}", "url": e["url"], "titel_quelle": e.get("title"),
            "views": e.get("view_count") or 0, "dauer_s": e.get("duration"),
            "spiel": (d.get("categories") or [""])[0],
            "erstellt": datetime.fromtimestamp(e["timestamp"], timezone.utc).isoformat() if e.get("timestamp") else None,
        }

    with ThreadPoolExecutor(6) as pool:
        return [c for c in pool.map(details, entries) if c]


def kick_clips(s, zeitraum, limit):
    url = f"https://kick.com/api/v2/channels/{s['login']}/clips?sort=view&time={KICK_ZEIT[zeitraum]}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        clips = json.load(r).get("clips") or []
    return [{
        "id": f"kick:{c['id']}", "url": f"https://kick.com/{s['login']}/clips/{c['id']}",
        "titel_quelle": c.get("title"), "views": c.get("views") or c.get("view_count") or 0,
        "dauer_s": c.get("duration"), "spiel": (c.get("category") or {}).get("name", ""),
        "erstellt": c.get("created_at"),
    } for c in clips[:limit]]


QUELLEN = {"twitch": twitch_clips, "kick": kick_clips}


def main():
    cfg = json.loads((ROOT / "config/kanal.json").read_text())
    ap = argparse.ArgumentParser()
    ap.add_argument("--spiele", nargs="*", default=cfg["spiele_muster"], help="Regex-Muster für den Spielnamen")
    ap.add_argument("--zeitraum", default=cfg["zeitraum"], choices=list(KICK_ZEIT))
    ap.add_argument("--pro-streamer", type=int, default=15, help="wie viele Top-Clips pro Streamer prüfen")
    ap.add_argument("--sprache", choices=["de", "en"], help="nur Streamer dieser Sprache")
    ap.add_argument("--out", default=str(ROOT / "arbeit/kandidaten.json"))
    a = ap.parse_args()

    verwendet_pfad = ROOT / "daten/verwendet.json"
    verwendet = set(json.loads(verwendet_pfad.read_text())) if verwendet_pfad.exists() else set()
    muster = [re.compile(m, re.I) for m in a.spiele]

    kandidaten, geprueft = [], 0
    for s in cfg["streamer"]:
        if not s.get("aktiv", True) or (a.sprache and s["sprache"] != a.sprache):
            continue
        try:
            clips = QUELLEN[s["plattform"]](s, a.zeitraum, a.pro_streamer)
        except Exception as ex:  # ein Streamer darf den Lauf nicht abbrechen
            print(f"[scout] {s['plattform']}/{s['login']}: {ex}", file=sys.stderr)
            continue
        geprueft += len(clips)
        for c in clips:
            dauer = c["dauer_s"] or 0
            if (c["id"] in verwendet or not any(m.search(c["spiel"] or "") for m in muster)
                    or not cfg["min_dauer_s"] <= dauer <= cfg["max_dauer_s"]):
                continue
            kandidaten.append({**c, "streamer": s["name"], "plattform": s["plattform"], "login": s["login"],
                               "sprache": s["sprache"], "facecam": s.get("facecam")})

    kandidaten.sort(key=lambda k: k["views"], reverse=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(kandidaten, ensure_ascii=False, indent=2))
    print(f"[scout] {geprueft} Clips geprüft, {len(kandidaten)} passend -> {a.out}")
    for k in kandidaten[:25]:
        print(f"  {k['views']:>7}  {k['sprache']} {k['streamer']:<13} {k['dauer_s']:>5}s  {(k['titel_quelle'] or '')[:55]}")


if __name__ == "__main__":
    main()
