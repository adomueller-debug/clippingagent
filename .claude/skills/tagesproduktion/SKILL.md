---
name: tagesproduktion
description: Tägliche Produktion der Streamer-Shorts. Holt die besten neuen Twitch-Clips der konfigurierten Streamer zum aktuellen Spiel, schneidet sie auf 9:16 mit Untertiteln, schreibt Titel und Beschreibung und legt alles zur Freigabe vor. Verwenden, wenn der tägliche Lauf startet oder der Nutzer „Tagesproduktion“, „neue Shorts“ oder „heutige Clips“ sagt.
---

# Tagesproduktion

Arbeitsverzeichnis ist die Wurzel dieses Repos. Kanal-Regeln stehen in `docs/kanal-regeln.md`, die Streamer-Liste in `config/kanal.json`.

## 0. Vorbereitung

```bash
pip install -q -r requirements.txt
```

`ffmpeg` muss vorhanden sein. Das Untertitel-Modell (faster-whisper „small“) lädt beim ersten Lauf von huggingface.co.

## 1. Scout: Kandidaten holen

```bash
python pipeline/scout.py            # Spiele und Zeitraum aus config/kanal.json
```

Ergebnis: `arbeit/kandidaten.json`, nach Views sortiert, schon verwendete Clips sind ausgeschlossen.
Bei weniger als 5 Kandidaten: mit `--zeitraum 7d` erneut laufen lassen.

## 2. Kurator: Auswahl

Wähle `ANZAHL` Clips aus (Standard 5, steht im Auftrag des Laufs). Regeln:

- Höchstens 2 Clips pro Streamer und Tag. Lieber Abwechslung als nur der Clip mit den meisten Views.
- Bevorzugen: Reaktion + Ereignis im selben Clip (Unfall, Tod, Schreck, Bug, Lachkrampf, Streit).
- Aussortieren: Ton kaputt, nur Chat-Lesen, Werbung, Ladebildschirm, nichts passiert in den ersten 3 s.
- Beim Kurator reicht der Twitch-Titel nicht immer. Im Zweifel `--nur-quellbild` laufen lassen und die Bilder ansehen.

## 3. Cutter: pro Clip

Ordner: `ausgabe/JJJJ-MM-TT/NN-kurzname/`.

1. Quellbild mit Raster holen und ansehen:
   ```bash
   python pipeline/schneiden.py --url URL --out ORDNER --nur-quellbild
   ```
   Das gelbe Raster hat 10-%-Schritte. Facecam-Box als `x,y,breite,hoehe` in Anteilen ablesen (eng an der Cam, ohne Chat und Overlays).
   Steht für den Streamer in `config/kanal.json` schon eine Box, sie nur prüfen. Wenn keine Facecam sichtbar ist: ohne `--facecam` schneiden (Layout blur).
2. Schneiden:
   ```bash
   python pipeline/schneiden.py --url URL --out ORDNER --sprache de --facecam 0.797,0.33,0.177,0.267
   ```
3. `ORDNER/worte.json` lesen. Wenn der Clip mit Leerlauf beginnt oder nach der Pointe weiterläuft: mit `--start`/`--ende` neu schneiden (die Quelle wird wiederverwendet). Ziel: der Moment beginnt in den ersten 2 s, die Pointe sitzt am Ende.
4. Neue Facecam-Boxen in `config/kanal.json` beim Streamer eintragen.

## 4. Prüfer

Die vier Bilder in `ORDNER/pruefung/` ansehen. Prüfen:

- Facecam zeigt das Gesicht, nicht abgeschnitten, kein Chat-Rest.
- Untertitel lesbar und nicht über dem Gesicht.
- Gameplay zeigt das Geschehen (bei Bedarf eine andere Facecam-Box oder das Blur-Layout).
- Untertitel-Text gegen `worte.json` auf grobe Fehler prüfen. Beleidigungen bleiben, wie sie gesagt wurden (wir ändern nichts am Inhalt).

Bei einem Fehler: korrigieren und neu schneiden. Nach 2 Fehlversuchen den Clip verwerfen.

## 5. Texter: `ORDNER/upload.md`

```markdown
# <Titel>

- Quelle: <Twitch-URL>
- Streamer: <Name> (https://twitch.tv/<login>)
- Spiel: <Spiel>
- Sprache: <de|en>
- Länge: <s>

## Titel
<max. 70 Zeichen, Sprache des Clips, Streamername vorne, konkret was passiert, höchstens ein Emoji>

## Beschreibung
<1 Satz, was passiert>

🎥 Streamer: <Name> – https://twitch.tv/<login>
Clip mit Erlaubnis des Streamers.

#<spiel> #<streamer> #shorts

## Tags
<kommagetrennt>
```

Titelregeln stehen in `docs/kanal-regeln.md`.

## 6. Abschluss

1. Clip-IDs in `daten/verwendet.json` eintragen (auch die verworfenen).
2. Eine Zeile pro Short in `daten/log.tsv`: `datum	id	streamer	titel	status`.
3. `upload.md`, `worte.json`, `pruefung/` und die Datenänderungen committen und pushen. Videos werden nicht committed (`.gitignore`).
4. **Phase 1 (Freigabe):** dem Nutzer jeden `short.mp4` mit `SendUserFile` schicken, zusammen mit Titel und Nummer. Nichts hochladen, bevor der Nutzer zugestimmt hat.
5. **Phase 2 (automatisch):** gibt es erst, wenn der Nutzer sie freischaltet. Dann lädt `pipeline/youtube_upload.py` hoch (noch nicht gebaut).
