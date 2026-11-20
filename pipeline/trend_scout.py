#!/usr/bin/env python3
"""Trend-Scout: Was wird in GTA 6 gerade NEU entdeckt, und was hat noch kaum jemand gezeigt?

Drei Quellen, nur Metadaten (nichts wird heruntergeladen):
1. Kick: meistgesehene Clips der ganzen GTA-VI-Kategorie (alle Streamer, auch kleine).
2. YouTube-Suche nach Entdeckungs-Begriffen (diese Woche, nach Aufrufen): welche Themen laufen,
   und wie viele Videos es schon dazu gibt (Sättigung).
3. Unsere Kandidaten (arbeit/kandidaten.json): Clips, deren Titel nach Entdeckung klingt.

  python pipeline/trend_scout.py
  python pipeline/trend_scout.py --pruefe "area 51" "airport"   # Sättigung einzelner Themen
Ergebnis: arbeit/trends.json und eine Übersicht auf der Konsole.
"""
import json
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SUCHEN = ["gta 6 secret", "gta 6 easter egg", "gta 6 found", "gta 6 hidden", "gta 6 glitch",
          "gta 6 first time", "gta 6 you can", "gta 6 never seen", "gta 6 geheim", "gta 6 entdeckt"]
ENTDECKUNG = re.compile(
    r"found|find|secret|hidden|easter|glitch|bug|ufo|alien|bigfoot|ghost|bunker|airport|plane|"
    r"never|first time|discover|you can|didn.?t know|insane detail|location|island|"
    r"gefunden|entdeck|geheim|versteckt|flughafen|zum ersten mal|wusste|krass", re.I)
STOP = set("gta 6 vi the a an in of to and i my is it this you your for on with all what how that are "
           "can be at from so just ever most only new first found secret secrets hidden easter eggs egg "
           "glitch things things details gta6 grand theft auto 2026 ps5 game games time playing day part launch stream "
            "gameplay know need walkthrough pro commentary everything full insane best guide tips how missed "
            "you'll won't want miss get early don't there didn't can't mind blowing crazy most so far still "
            "every here why when who has have get got gets rich money spots guns powerful items weapons "
            "features only edition ultimate settings change tell doesn't".split())


def ytdlp_json(args, timeout=180):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings", *args], capture_output=True, text=True,
                       timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[-200:])
    return json.loads(r.stdout)


def kick_kategorie(liste):
    req = urllib.request.Request("https://kick.com/api/v2/categories/grand-theft-auto-vi/clips?sort=view&time=day",
                                 headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        clips = json.load(r).get("clips") or []
    out = []
    for c in clips:
        login = (c.get("channel") or {}).get("slug") or ""
        out.append({"id": f"kick:{c['id']}", "url": f"https://kick.com/{login}/clips/{c['id']}", "streamer": login,
                    "auf_liste": login in liste, "views": c.get("views") or c.get("view_count") or 0,
                    "dauer_s": c.get("duration"), "titel": c.get("title")})
    return out


def youtube_suche(q):
    url = "https://www.youtube.com/results?search_query=" + q.replace(" ", "+") + "&sp=CAMSAggD"  # Aufrufe, diese Woche
    try:
        return ytdlp_json(["--flat-playlist", "--playlist-end", "25", "-J", url]).get("entries") or []
    except Exception as ex:
        print(f"[trend] YouTube '{q}': {ex}", file=sys.stderr)
        return []


def saettigung(thema):
    """Wie oft wurde ein Thema diese Woche schon auf YouTube gezeigt? (Anzahl Videos mit dem Begriff im Titel, Aufrufe)"""
    es = youtube_suche(f"gta 6 {thema}")
    passend = [e for e in es if all(w in (e.get("title") or "").lower() for w in thema.lower().split())]
    return len(passend), sum(e.get("view_count") or 0 for e in passend), [e.get("title") for e in passend[:5]]


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--pruefe":
        for thema in sys.argv[2:]:
            n, v, beispiele = saettigung(thema)
            stufe = "NEU (kaum gezeigt)" if n <= 2 else "läuft schon" if n <= 8 else "gesättigt"
            print(f"{thema!r}: {n} Videos diese Woche, {v} Aufrufe -> {stufe}")
            for b in beispiele:
                print(f"    - {b}")
        return
    cfg = json.loads((ROOT / "config/kanal.json").read_text())
    liste = {s["login"] for s in cfg["streamer"]}

    try:
        kick = kick_kategorie(liste)
    except Exception as ex:
        print(f"[trend] Kick: {ex}", file=sys.stderr)
        kick = []

    with ThreadPoolExecutor(3) as pool:
        treffer = [e for es in pool.map(youtube_suche, SUCHEN) for e in es]
    videos = {e["id"]: e for e in treffer if e.get("id")}.values()

    # Themen = auffällige Wörter und Wortpaare in Titeln der Entdeckungs-Videos, gewichtet nach Aufrufen
    themen, anzahl = Counter(), Counter()
    for e in videos:
        if not ENTDECKUNG.search(e.get("title") or ""):
            continue
        worte = [w for w in re.findall(r"[a-zäöüß']+", (e.get("title") or "").lower()) if w not in STOP and len(w) > 2]
        for t in set(worte + [" ".join(p) for p in zip(worte, worte[1:])]):
            themen[t] += e.get("view_count") or 0
            anzahl[t] += 1
    top_themen = [{"thema": t, "aufrufe": v, "videos": anzahl[t]} for t, v in themen.most_common(40) if anzahl[t] >= 1]

    eigene = []
    kp = ROOT / "arbeit/kandidaten.json"
    if kp.exists():
        for k in json.loads(kp.read_text()):
            if ENTDECKUNG.search(k.get("titel_quelle") or ""):
                eigene.append({"id": k["id"], "streamer": k["streamer"], "views": k["views"], "titel": k["titel_quelle"],
                               "url": k["url"], "dauer_s": k.get("dauer_s")})

    ergebnis = {"kick_kategorie": kick, "youtube_entdeckungen": sorted(
        [{"titel": e.get("title"), "kanal": e.get("channel"), "views": e.get("view_count") or 0,
          "url": f"https://www.youtube.com/watch?v={e['id']}"} for e in videos], key=lambda x: -x["views"]),
        "themen": top_themen, "eigene_entdeckungen": eigene}
    (ROOT / "arbeit").mkdir(exist_ok=True)
    (ROOT / "arbeit/trends.json").write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2))

    print(f"[trend] Kick-Kategorie (24 h): {len(kick)} Clips")
    for c in kick[:12]:
        print(f"  {c['views']:>7}  {c['streamer'][:16]:<16} {'Liste' if c['auf_liste'] else 'NEU  '} {str(c['dauer_s']):>4}s  {(c['titel'] or '')[:50]}")
    livestream = re.compile(r"(playing|played|plays).{0,20}first time|first time playing|launch stream|marathon", re.I)
    entdeckt = [v for v in ergebnis["youtube_entdeckungen"]
                if ENTDECKUNG.search(v["titel"] or "") and not livestream.search(v["titel"] or "")]
    print(f"\n[trend] Entdeckungs-Videos diese Woche ({len(entdeckt)} von {len(videos)}), nach Aufrufen:")
    print("        Themen daraus ableiten: Was wird gerade entdeckt? Wie oft wurde es schon gezeigt?")
    for v in entdeckt[:40]:
        print(f"  {v['views']:>9}  {(v['kanal'] or '')[:16]:<16} {(v['titel'] or '')[:85]}")
    print(f"\n[trend] Entdeckungs-Clips unserer Streamer: {len(eigene)}")
    for k in sorted(eigene, key=lambda x: -x["views"])[:20]:
        print(f"  {k['views']:>7}  {k['streamer'][:14]:<14} {str(k['dauer_s']):>4}s  {k['titel'][:60]}")


if __name__ == "__main__":
    main()
