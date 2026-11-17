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

Ergebnis: `arbeit/kandidaten.json`, nach Views sortiert, schon verwendete Clips sind ausgeschlossen. Quellen: Twitch (yt-dlp) und Kick (öffentliche API), je nach `plattform` in der Config.
Bei weniger als 5 Kandidaten: mit `--zeitraum 7d` erneut laufen lassen.
Gibt es auch dann keine Clips zum Spiel (z. B. vor dem Release), nicht auf ein anderes Spiel ausweichen: dem Nutzer kurz melden und den Lauf beenden.

## 2. Kurator: Auswahl

Wähle `ANZAHL` Clips aus (Standard 5, steht im Auftrag des Laufs). Regeln:

- Höchstens 2 Clips pro Streamer und Tag. Lieber Abwechslung als nur der Clip mit den meisten Views.
- Beide Sprachen mischen: ungefähr die Hälfte deutsche, die Hälfte englische Streamer, solange beide genug gute Clips haben.
- Kick-Titel sind oft Tastatur-Gebrabbel. Dann zählen nur Views und das Quellbild.
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
3. `ORDNER/worte.json` lesen. Wenn der Clip mit Leerlauf beginnt oder nach der Pointe weiterläuft: mit `--start`/`--ende` neu schneiden (die Quelle wird wiederverwendet). Ziel: der Moment beginnt in den ersten 2 s, die Pointe sitzt am Ende. Shorts sind höchstens 60 s lang; längere Clips (oft bei Kick) immer kürzen.
   `--sprache` ist die Sprache des Streamers aus der Config (`de` oder `en`).
4. Neue Facecam-Boxen in `config/kanal.json` beim Streamer eintragen.

## 3b. YouTube-Streams (IShowSpeed) – auf dem Rechner des Nutzers

Kandidaten mit `"typ": "youtube_stream"` sind ganze Streams. YouTube blockiert Downloads aus der Cloud, deshalb läuft dieser Teil auf dem Rechner des Nutzers (Remote Control, siehe `docs/rechner-einrichten.md`).

1. `list_computer_folders` aufrufen. Ist der Ordner `clippingagent` online, mit `request_computer_folder` verbinden (ist die Session schon verbunden, direkt weiter). Ist der Rechner offline: YouTube heute überspringen und das in der Abschlussmeldung sagen.
2. Alle folgenden Befehle mit `_host` auf dem Rechner ausführen, im Ordner `clippingagent`:
   ```bash
   git pull
   python pipeline/youtube_highlights.py URL --anzahl 3
   ```
   Liefert Abschnitte (`bereich`) um die meistgesehenen Stellen. Exit-Code 2 = noch keine Most-Replayed-Daten: Stream morgen erneut versuchen, nicht als verwendet markieren.
3. Höchstens 2 Abschnitte pro Stream schneiden, wie in Schritt 3, aber mit `--bereich`:
   ```bash
   python pipeline/schneiden.py --url URL --bereich 5120-5180 --out ausgabe/JJJJ-MM-TT/NN-kurzname --nur-quellbild
   python pipeline/schneiden.py --url URL --bereich 5120-5180 --out ausgabe/JJJJ-MM-TT/NN-kurzname --sprache en [--facecam ...]
   ```
   Speed streamt oft draußen oder als Vollbild-Kamera. Dann ohne `--facecam` (Layout blur) schneiden.
4. Prüfbilder mit `Read` und `_host` ansehen. Die fertigen Shorts bleiben auf dem Rechner des Nutzers: in der Abschlussmeldung den Pfad nennen statt `SendUserFile`.
5. `upload.md` wie in Schritt 5 schreiben. In `daten/verwendet.json` die Stream-ID (`youtube:ID`) eintragen, sobald der Stream bearbeitet ist.

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

- Quelle: <Clip-URL>
- Streamer: <Name> (https://twitch.tv/<login> bzw. https://kick.com/<login>)
- Spiel: <Spiel>
- Sprache: <de|en>
- Länge: <s>

## Titel
<max. 70 Zeichen, Sprache des Clips, Streamername vorne, konkret was passiert, höchstens ein Emoji>

## Beschreibung
<1 Satz, was passiert>

🎥 Streamer: <Name> – <Kanal-URL>
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
4. Dem Nutzer jeden `short.mp4` mit `SendUserFile` schicken (`status: proactive`). Die Caption enthält Nummer, Streamer und Titel. Danach eine Nachricht mit allen Titeln, Beschreibungen und Hashtags zum Kopieren.
5. Hochladen macht der Nutzer selbst, abends zwischen 18 und 20 Uhr, auf YouTube, TikTok und Instagram. Die Session lädt nichts hoch.
6. Meldet der Nutzer etwas zurück (Short abgelehnt, Untertitel falsch), korrigieren, neu schicken und den Status in `daten/log.tsv` setzen.
