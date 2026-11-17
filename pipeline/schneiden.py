#!/usr/bin/env python3
"""Cutter: Twitch-Clip -> 9:16-Short mit eingebrannten Wort-Untertiteln.

Nichts Eigenes kommt dazu: nur Zuschnitt, Untertitel und Lautheits-Normalisierung.

  python pipeline/schneiden.py --url URL --out ausgabe/2026-11-19/01-slug --sprache de
  python pipeline/schneiden.py --url URL --out ... --facecam 0,0,0.25,0.3   # Layout split
  python pipeline/schneiden.py --url URL --out ... --start 3.5 --ende 27     # kürzen

Ergebnis im Ordner: short.mp4, quelle.mp4, worte.json, untertitel.ass, pruefung/*.jpg
"""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets/fonts"
W, H = 1080, 1920


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"Fehler: {' '.join(map(str, cmd[:3]))} ...\n{r.stderr[-1500:]}")
    return r.stdout


def laden(url, ziel):
    if not ziel.exists():
        run(["yt-dlp", "--no-warnings", "-f", "1080/720/best[height<=?1080]/best", "-o", str(ziel), url])


def probe(pfad):
    d = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(pfad)]))
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = map(int, v["r_frame_rate"].split("/"))
    return int(v["width"]), int(v["height"]), num / den, float(d["format"]["duration"])


def transkribieren(quelle, sprache, start, ende, modell):
    from faster_whisper import WhisperModel

    import numpy as np

    # Ton selbst mit ffmpeg dekodieren (16 kHz mono), umgeht PyAV-Versionskonflikte
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(quelle), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, dtype=np.float32)
    m = WhisperModel(modell, device="cpu", compute_type="int8")
    segs, info = m.transcribe(audio, language=sprache, word_timestamps=True, vad_filter=True,
                              condition_on_previous_text=False)
    worte = []
    for s in segs:
        for w in s.words or []:
            if w.end <= start or (ende and w.start >= ende):
                continue
            worte.append({"w": w.word.strip(), "s": round(max(w.start, start) - start, 3),
                          "e": round((min(w.end, ende) if ende else w.end) - start, 3)})
    return [w for w in worte if w["w"]], info.language


def bloecke(worte, max_worte=3, max_zeichen=16, pause=0.4):
    out, cur = [], []
    for w in worte:
        if cur and (len(cur) >= max_worte or pause < w["s"] - cur[-1]["e"]
                    or len(" ".join(x["w"] for x in cur + [w])) > max_zeichen
                    or cur[-1]["w"][-1:] in ".?!,"):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def ts(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def ass_datei(worte, y, pfad):
    kopf = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Anton,124,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,9,4,5,50,50,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    zeilen = []
    for b in bloecke(worte):
        for i, w in enumerate(b):
            ende = b[i + 1]["s"] if i + 1 < len(b) else max(w["e"], w["s"] + 0.25)
            text = " ".join(
                ("{\\c&H00E5FF&}" + x["w"].upper() + "{\\c&HFFFFFF&}") if j == i else x["w"].upper()
                for j, x in enumerate(b))
            zeilen.append(f"Dialogue: 0,{ts(w['s'])},{ts(ende)},Sub,,0,0,0,,{{\\pos({W // 2},{y})}}{text}")
    pfad.write_text(kopf + "\n".join(zeilen) + "\n")


def filter_graph(sw, sh, facecam, zoom):
    if facecam:
        fx, fy, fw, fh = facecam
        cw, ch = int(sw * fw) // 2 * 2, int(sh * fh) // 2 * 2
        top = min(int(W * ch / cw) // 2 * 2, 760)
        unten = H - top
        # Gameplay: mittlerer Ausschnitt im Seitenverhältnis des unteren Felds
        gw = min(sw, int(sh * W / unten)) // 2 * 2
        g = (f"[0:v]crop={cw}:{ch}:{int(sw * fx)}:{int(sh * fy)},scale={W}:{top}:force_original_aspect_ratio=increase,"
             f"crop={W}:{top}[cam];"
             f"[0:v]crop={gw}:{sh}:(iw-{gw})/2:0,scale={W}:{unten}[game];"
             f"[cam][game]vstack=inputs=2[v0]")
        return g, top  # Untertitel auf der Naht
    gw = int(sw / zoom) // 2 * 2
    fg_h = int(W * sh / gw) // 2 * 2
    g = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},gblur=sigma=40,eq=brightness=-0.12[bg];"
         f"[0:v]crop={gw}:{sh}:(iw-{gw})/2:0,scale={W}:{fg_h}[fg];"
         f"[bg][fg]overlay=0:(H-h)/2[v0]")
    return g, (H + fg_h) // 2 + 170  # Untertitel unter dem Bild


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sprache", default=None, help="de/en; leer = automatisch")
    ap.add_argument("--facecam", default=None, help="x,y,b,h als Anteile -> Layout split")
    ap.add_argument("--zoom", type=float, default=1.35, help="Layout blur: Ausschnitt-Zoom")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--ende", type=float, default=None)
    ap.add_argument("--modell", default="small")
    ap.add_argument("--ohne-untertitel", action="store_true")
    ap.add_argument("--nur-quellbild", action="store_true", help="nur laden und pruefung/quelle.jpg mit Raster schreiben")
    a = ap.parse_args()

    out = Path(a.out)
    (out / "pruefung").mkdir(parents=True, exist_ok=True)
    quelle = out / "quelle.mp4"
    laden(a.url, quelle)
    sw, sh, fps, dauer = probe(quelle)
    if a.nur_quellbild:
        # Raster in 10-%-Schritten, damit die Facecam-Box als Anteile ablesbar ist
        raster = ",".join(f"drawbox=x=iw*{i/10}:y=0:w=2:h=ih:color=yellow@0.6:t=fill,"
                          f"drawbox=x=0:y=ih*{i/10}:w=iw:h=2:color=yellow@0.6:t=fill" for i in range(1, 10))
        for t in (2, dauer / 2):
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.1f}", "-i", str(quelle), "-frames:v", "1",
                 "-vf", f"scale=960:-2,{raster}", str(out / "pruefung" / f"quelle_{int(t)}s.jpg")])
        print(json.dumps({"quelle": f"{sw}x{sh}", "dauer_s": dauer, "bilder": str(out / "pruefung")}))
        return
    ende = min(a.ende or dauer, dauer)

    facecam = [float(x) for x in a.facecam.split(",")] if a.facecam else None
    graph, sub_y = filter_graph(sw, sh, facecam, a.zoom)

    if a.ohne_untertitel:
        worte, sprache = [], a.sprache
        graph = graph.replace("[v0]", "[v]")
    else:
        worte, sprache = transkribieren(quelle, a.sprache, a.start, a.ende, a.modell)
        ass_datei(worte, sub_y, out / "untertitel.ass")
        graph += f";[v0]ass={out / 'untertitel.ass'}:fontsdir={FONT_DIR}[v]"
    (out / "worte.json").write_text(json.dumps({"sprache": sprache, "worte": worte}, ensure_ascii=False, indent=1))

    run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.start), "-to", str(ende), "-i", str(quelle),
         "-filter_complex", graph, "-map", "[v]", "-map", "0:a?",
         "-r", str(min(round(fps), 60)), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-maxrate", "10M", "-bufsize", "20M",
         "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
         "-ar", "48000", "-movflags", "+faststart", str(out / "short.mp4")])

    # Prüfbilder für den Prüfer-Agenten
    lang = ende - a.start
    for i, t in enumerate([0.5, lang * 0.33, lang * 0.66, max(lang - 1, 0)]):
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(out / "short.mp4"),
             "-frames:v", "1", "-vf", "scale=360:-2", str(out / "pruefung" / f"bild{i + 1}.jpg")])
    print(json.dumps({"short": str(out / "short.mp4"), "dauer_s": round(lang, 2), "quelle": f"{sw}x{sh}@{fps:.0f}",
                      "sprache": sprache, "worte": len(worte),
                      "layout": "split" if facecam else "blur"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
