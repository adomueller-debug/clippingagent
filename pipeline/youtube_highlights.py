#!/usr/bin/env python3
"""YouTube-Highlights: findet in einem langen Stream die meistgesehenen Stellen ("Most Replayed").

Läuft auf dem Rechner des Nutzers (YouTube blockiert Downloads aus der Cloud).
Lädt nichts herunter, liest nur die Metadaten. Ergebnis: Abschnitte für schneiden.py --bereich.

  python pipeline/youtube_highlights.py https://www.youtube.com/watch?v=ID --anzahl 5
"""
import argparse
import json
import subprocess
import sys


def metadaten(url):
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-warnings", "-j", "--skip-download", url],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"yt-dlp: {r.stderr.strip()[-400:]}")
    return json.loads(r.stdout)


def spitzen(heatmap, anzahl, abstand):
    """Höchste Heatmap-Werte, mindestens `abstand` Sekunden auseinander."""
    gewaehlt = []
    for h in sorted(heatmap, key=lambda x: -x["value"]):
        mitte = (h["start_time"] + h["end_time"]) / 2
        if all(abs(mitte - g["mitte"]) >= abstand for g in gewaehlt):
            gewaehlt.append({"mitte": mitte, "wert": round(h["value"], 3)})
        if len(gewaehlt) >= anzahl:
            break
    return gewaehlt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--anzahl", type=int, default=5)
    ap.add_argument("--vorlauf", type=float, default=35, help="Sekunden vor der Spitze laden")
    ap.add_argument("--nachlauf", type=float, default=25, help="Sekunden nach der Spitze laden")
    ap.add_argument("--abstand", type=float, default=180, help="Mindestabstand zwischen zwei Spitzen")
    a = ap.parse_args()

    d = metadaten(a.url)
    heatmap = d.get("heatmap") or []
    dauer = d.get("duration") or 0
    if not heatmap:
        print(json.dumps({"id": d["id"], "titel": d.get("title"), "fehler": "keine Most-Replayed-Daten (Stream zu neu?)"},
                         ensure_ascii=False))
        sys.exit(2)

    # Der Anfang (Intro/Warten) ist oft "most replayed", weil alle dort einsteigen: überspringen
    heatmap = [h for h in heatmap if h["start_time"] > 120]
    ergebnis = []
    for s in spitzen(heatmap, a.anzahl, a.abstand):
        start = max(0, s["mitte"] - a.vorlauf)
        ende = min(dauer, s["mitte"] + a.nachlauf)
        ergebnis.append({
            "id": f"youtube:{d['id']}@{int(s['mitte'])}",
            "url": d.get("webpage_url") or a.url,
            "bereich": f"{start:.0f}-{ende:.0f}",
            "spitze_s": int(s["mitte"]),
            "wert": s["wert"],
        })
    print(json.dumps({"id": d["id"], "titel": d.get("title"), "dauer_s": dauer,
                      "views": d.get("view_count"), "highlights": ergebnis}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
