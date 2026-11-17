#!/usr/bin/env python3
"""Scout: sammelt Twitch-Clips der konfigurierten Streamer und filtert nach Spiel.

Nutzt yt-dlp (kein Twitch-Developer-Account nötig). Ergebnis ist eine JSON-Liste,
nach Views sortiert, ohne bereits verwendete Clips.

  python pipeline/scout.py                       # Spiele/Zeitraum aus config/kanal.json
  python pipeline/scout.py --spiele "Grand Theft Auto V" --zeitraum 7d
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ytdlp_json(args, timeout=120):
    r = subprocess.run(["yt-dlp", "--no-warnings", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[-300:])
    return json.loads(r.stdout)


def clips_auflisten(login, zeitraum, limit):
    url = f"https://www.twitch.tv/{login}/clips?filter=clips&range={zeitraum}"
    d = ytdlp_json(["--flat-playlist", "--playlist-end", str(limit), "-J", url])
    return d.get("entries") or []


def details(url):
    d = ytdlp_json(["-j", "--skip-download", url])
    return {
        "categories": d.get("categories") or [],
        "channel": d.get("channel"),
        "clipper": d.get("uploader"),
        "portrait": any(str(f.get("format_id", "")).startswith("portrait") for f in d.get("formats", [])),
    }


def main():
    cfg = json.loads((ROOT / "config/kanal.json").read_text())
    ap = argparse.ArgumentParser()
    ap.add_argument("--spiele", nargs="*", default=cfg["spiele"])
    ap.add_argument("--zeitraum", default=cfg["zeitraum"], choices=["24hr", "7d", "30d", "all"])
    ap.add_argument("--pro-streamer", type=int, default=15, help="wie viele Top-Clips pro Streamer prüfen")
    ap.add_argument("--out", default=str(ROOT / "arbeit/kandidaten.json"))
    a = ap.parse_args()

    verwendet_pfad = ROOT / "daten/verwendet.json"
    verwendet = set(json.loads(verwendet_pfad.read_text())) if verwendet_pfad.exists() else set()
    spiele = {s.lower() for s in a.spiele}

    roh = []
    for s in cfg["streamer"]:
        try:
            for e in clips_auflisten(s["twitch"], a.zeitraum, a.pro_streamer):
                if e["id"] in verwendet:
                    continue
                dauer = e.get("duration") or 0
                if not (cfg["min_dauer_s"] <= dauer <= cfg["max_dauer_s"]):
                    continue
                roh.append((s, e))
        except Exception as ex:  # ein Streamer darf den Lauf nicht abbrechen
            print(f"[scout] {s['twitch']}: {ex}", file=sys.stderr)

    def pruefen(item):
        s, e = item
        try:
            return s, e, details(e["url"])
        except Exception as ex:
            print(f"[scout] {e['url']}: {ex}", file=sys.stderr)
            return s, e, None

    kandidaten = []
    with ThreadPoolExecutor(6) as pool:
        for s, e, d in pool.map(pruefen, roh):
            if not d or not spiele & {c.lower() for c in d["categories"]}:
                continue
            kandidaten.append({
                "id": e["id"],
                "url": e["url"],
                "streamer": s["name"],
                "twitch": s["twitch"],
                "sprache": s["sprache"],
                "titel_twitch": e.get("title"),
                "views": e.get("view_count") or 0,
                "dauer_s": e.get("duration"),
                "spiel": d["categories"][0],
                "erstellt": datetime.fromtimestamp(e["timestamp"], timezone.utc).isoformat() if e.get("timestamp") else None,
                "geclippt_von": d["clipper"],
                "thumbnail": e.get("thumbnail"),
            })

    kandidaten.sort(key=lambda k: k["views"], reverse=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(kandidaten, ensure_ascii=False, indent=2))
    print(f"[scout] {len(roh)} Clips geprüft, {len(kandidaten)} passend -> {a.out}")
    for k in kandidaten[:20]:
        print(f"  {k['views']:>7}  {k['streamer']:<13} {k['dauer_s']:>4}s  {k['titel_twitch'][:60]}")


if __name__ == "__main__":
    main()
