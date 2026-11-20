---
name: tagesproduktion
description: Tägliche Produktion der Streamer-Shorts. Holt die besten neuen Twitch-Clips der konfigurierten Streamer zum aktuellen Spiel, schneidet sie auf 9:16 mit Untertiteln, schreibt Titel und Beschreibung und legt alles zur Freigabe vor. Verwenden, wenn der tägliche Lauf startet oder der Nutzer „Tagesproduktion“, „neue Shorts“ oder „heutige Clips“ sagt.
---

# Tagesproduktion

Arbeitsverzeichnis ist die Wurzel dieses Repos. Kanal-Regeln stehen in `docs/kanal-regeln.md`, die Streamer-Liste in `config/kanal.json`.

## 0. Vorbereitung

Erst `git pull`. Dann feststellen, wo der Lauf läuft:

- **Mac** (`uname` = Darwin): Python aus der venv nehmen, also überall `.venv/bin/python` statt `python`. Fehlt `.venv`: `python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt`. YouTube-Quellen (IShowSpeed) gehen hier direkt, Schritt 3b ohne Remote Control. Am Ende statt Schritt 6.4 den Upload nach `upload-mac.md`.
- **Cloud** (Linux-Container): `pip install -q -r requirements.txt`. YouTube-Quellen nur über den verbundenen Rechner (3b).

`ffmpeg` muss vorhanden sein. Das Untertitel-Modell (faster-whisper „small“) lädt beim ersten Lauf von huggingface.co.

## 1. Scout: Kandidaten holen

```bash
python pipeline/scout.py            # Spiele und Zeitraum aus config/kanal.json
```

Ergebnis: `arbeit/kandidaten.json`, nach Views sortiert, schon verwendete Clips sind ausgeschlossen. Quellen: Twitch (yt-dlp) und Kick (öffentliche API), je nach `plattform` in der Config.
Bei weniger als 5 Kandidaten: mit `--zeitraum 7d` erneut laufen lassen.
Gibt es auch dann keine Clips zum Spiel (z. B. vor dem Release), nicht auf ein anderes Spiel ausweichen: dem Nutzer kurz melden und den Lauf beenden.

## 1b. TikTok-Signal

```bash
python pipeline/tiktok_signal.py --tage 2
```

**Achtung, doppelt = tot:** Was ein Streamer schon selbst auf TikTok gepostet hat, spielt TikTok bei uns nicht aus (Zarbex Bigfoot: 1 Aufruf, Papaplatte Tankstelle: 0). Jeder Kandidat wird gegen diese Liste geprüft: Passt das Thema eines Clips zu einem TikTok-Post desselben Streamers aus den letzten 3 Tagen (z. B. „Big Foot?“ ↔ „BigFoot Sichtung in GTA 6“), fliegt er raus. Im Zweifel raus.

Zeigt außerdem, welche GTA-Posts auf den TikTok-Profilen der Streamer gerade die meisten Aufrufe haben. Daraus lernen wir die *Typen* von Momenten, die ziehen, und suchen ähnliche, noch nicht gepostete Momente. Vorrang haben Streamer, die selbst wenig GTA auf TikTok posten, und frische Clips der letzten Stunden. Geschnitten wird immer aus dem Original-Clip; TikTok-Videos werden nie heruntergeladen oder wiederverwendet.

## 2. Kurator: Auswahl

Wähle `ANZAHL` Clips aus (Standard 5, steht im Auftrag des Laufs). Grundlage ist `docs/tiktok-analyse.md`. Regeln:

- **Nur lustige oder besondere Momente.** Der Clip muss in einen dieser Typen passen, sonst raus, egal wie viele Views:
  1. Versehen / Fail („I didn't mean to“, „Not again“, „Bro missed“): stärkster Typ
  2. Tier-Begegnung (Hund, Katze, Hai, Alligator)
  3. Kreative Aktion (etwas, das sonst keiner macht)
  4. Chaos / Verfolgung / Unfall mit lauter Reaktion
  5. Drama aus der Story mit Reaktion des Streamers
  6. Sexy / Flirt / peinliche Begegnung: Kuss-Szenen (z. B. mit Lucia oder Mandy), Dates, Flirts, Strand, Dusche, Stripclub-Reaktionen, angedeutete Sex-Szenen ohne nackte Haut (Szene blendet ab, Geräusche, Bett-Szene bekleidet, vor allem die Reaktion des Streamers). Nacktheit **nur zensiert** (siehe unten). Nackte Szenen sind kein Muss: Kuss- und angedeutete Szenen haben Vorrang.
  7. Komische Begegnungen: schräge NPCs, Promi-Cameos (Drake, Bad Bunny), absurde Dialoge
  8. Sehr Außergewöhnliches: UFOs, Bigfoot, Bugs, Physik-Chaos, Dinge, die man nicht erwartet
  9. Streamer gegeneinander: einer legt den anderen rein, trollt ihn, fährt ihn um („Speed did Kai dirty“: 25 Mio.). Co-Streams (Monte + Schradin, Kai + Fanum) gezielt danach durchsuchen
  10. Das erste Mal: erste Reaktion auf etwas Neues im Spiel (Grafik-Moment, Lucia, Fahrzeug, Ort), aber nur mit starker Reaktion, nicht als ruhiger „erster Eindruck“
  11. Gespräch über GTA mit Pointe (z. B. „Fanum muss wegen GTA 6 Thanksgiving ausfallen lassen“: 2,2 Mio.). Auch ohne Spielbild, solange die Pointe im Clip sitzt
- Die Reaktion des Streamers muss sichtbar sein (Schrei, Lachen, Hände vors Gesicht, Fassungslosigkeit).
- Schwach und daher raus: Gespräche ohne Pointe, ruhiger „erster Eindruck“, Menüs, Ladebildschirme, Zwischensequenzen ohne Reaktion, reines Herumfahren.
- **Pointe ans Ende:** Der Short endet auf dem lustigsten Moment oder direkt danach („The ENDING 😂“: 7,4 Mio.). Kein Ausklingen. Das sorgt dafür, dass man bis zum Schluss schaut und neu startet.

- **10 Shorts pro Lauf als Auswahl.** Der Nutzer entscheidet, was hochgeht. Manuelle Läufe kommen obendrauf, Nummerierung im Tagesordner fortsetzen. Am Ende eine Empfehlung geben: die besten 3–5 für den Upload (TikTok verteilt den Testtopf sonst auf zu viele Videos), mit Sendeplätzen.
- Höchstens 2 Clips pro Streamer und Tag. Lieber Abwechslung als nur der Clip mit den meisten Views.
- Sprachen: etwa 7 englische, 3 deutsche Shorts. Englische Streamer haben die größere Reichweite; die US-Liste in `config/kanal.json` ist dafür erweitert (Marlon, JasonTheWeen, CaseOh, Stable Ronaldo, Jynxzi, RayAsianBoy, Agent 00, N3on, PlaqueBoyMax).
- Kick-Titel sind oft Tastatur-Gebrabbel. Dann zählen nur Views und das Quellbild.
- Aussortieren: Ton kaputt, nur Chat-Lesen, Werbung, Ladebildschirm, nichts passiert in den ersten 3 s.
- **Nacktheit und sexy Szenen:** erlaubt, wenn jede nackte Stelle (Po, Brust, Genitalbereich) mit `--zensur` verpixelt ist, über die ganze Zeit, in der sie zu sehen ist. Danach Prüfbilder im Sekundentakt ansehen (siehe Prüfer). Bewegt sich die Figur, mehrere Zensur-Boxen mit Zeitfenster setzen. Unterwäsche, Bikini, Tanga ohne Zensur sind okay, solange der Clip nicht nur darauf zoomt.
- Immer raus, auch bekleidet oder zensiert: deutlich sichtbare Sex-Bewegungen (Stoßbewegungen, Lapdance mit Berührung im Schritt). Angedeutet ja, gezeigt nein: Den Short dann vor der eindeutigen Stelle enden lassen (`--ende`) oder bei der Reaktion des Streamers bleiben. Ebenfalls raus: Gewalt gegen leicht bekleidete Figuren, Blut-Nahaufnahmen. Das löscht TikTok sofort. **Erlaubt** ist Slapstick im Spiel, auch mit Tieren, wenn es ein Versehen ist und nichts Blutiges zu sehen ist (Lacys Hund-Clip: 8,1 Mio. Aufrufe). Die Prüfbilder aus allen Teilen des Clips ansehen, nicht nur den Anfang.
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
   python pipeline/schneiden.py --url URL --out ORDNER --sprache de --facecam 0.797,0.33,0.177,0.267 \
     --hook "Papaplatte fällt auf den ältesten Trick rein"
   ```
   Nacktheit verpixeln: `--zensur x,y,b,h[,von,bis]` (Anteile im Quellbild wie bei der Facecam, Zeiten relativ zum Short), mehrfach möglich. Box großzügig wählen.
   **`--hook` ist Pflicht:** Streamer + was passiert, 3–8 Wörter, Sprache des Clips, ohne Emoji. Erscheint als weiße Box auf der Naht zwischen Facecam und Spiel. Verrät die Pointe nicht ganz („Lacy meets a dog in GTA 6“, „Die dümmste Verfolgungsjagd“).
   Untertitel rutschen bei gesetztem Hook ins untere Drittel. Hat der Stream schon Live-Untertitel: `--ohne-untertitel` (der Hook bleibt).
3. `ORDNER/worte.json` lesen. Wenn der Clip mit Leerlauf beginnt oder nach der Pointe weiterläuft: mit `--start`/`--ende` neu schneiden (die Quelle wird wiederverwendet). Ziel: der Moment beginnt in den ersten 2 s, die Pointe sitzt am Ende. **Ziellänge 7–20 s** (Median-Aufrufe bei 0–15 s: 652.000, bei über 60 s: 131.000). Über 30 s nur, wenn eine Geschichte trägt. Twitch-Clips sind meist 30–60 s: fast immer kürzen.
   `--sprache` ist die Sprache des Streamers aus der Config (`de` oder `en`).
4. Neue Facecam-Boxen in `config/kanal.json` beim Streamer eintragen.

## 3b. YouTube-Streams (IShowSpeed) – auf dem Rechner des Nutzers

Läuft der Lauf schon auf dem Mac: Punkt 1 entfällt, die Befehle laufen direkt (ohne `_host`), die Shorts werden wie alle anderen behandelt.

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

Bei Shorts mit `--zensur`: zusätzlich ein Bild pro Sekunde ziehen und jedes ansehen. Ist irgendwo unzensierte Nacktheit zu sehen, Box anpassen oder den Clip verwerfen.
```bash
ffmpeg -v error -i ORDNER/short.mp4 -vf fps=1,scale=270:-2,tile=6x3 ORDNER/pruefung/zensur-check.jpg
```

Die vier Bilder in `ORDNER/pruefung/` ansehen. Prüfen:

- Facecam zeigt das Gesicht, nicht abgeschnitten, kein Chat-Rest.
- Untertitel lesbar und nicht über dem Gesicht.
- Hat die Quelle schon eingebrannte Untertitel (z. B. bei einem Trailer, den der Streamer schaut) oder transkribiert Whisper vor allem fremden Ton statt des Streamers: mit `--ohne-untertitel` neu schneiden und das in `upload.md` vermerken.
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
- Moment-Typ: <Nummer und Name aus Schritt 2>
- Titelstil: <A Meme | B Satz>

## Hook
<Text der Hook-Zeile im Video>

## Titel
<YouTube: abwechselnd Stil A oder B, Stil in `upload.md` unter „Titelstil“ vermerken>
<A „Meme“ (wie Speedy Boykins): 2–6 Wörter, verrät nicht die Pointe, 2 gleiche Emoji: „Monte did Schradin dirty 😭😭“, „The ENDING 💀💀“>
<B „Satz“ (wie Kai Cenat Live): Streamer + was passiert, 40–90 Zeichen, 1–2 Emoji: „Kai Cenat Gets Chased By The Cops In GTA VI 😭🚨“>

## Beschreibung
#gta6 #<streamer> #shorts

## Tags
<kommagetrennt>

## TikTok
<2–6 Wörter, Ich-Form oder „Bro …“, macht neugierig statt die Pointe zu verraten><2–3 Emoji> #fyp #viral #<streamer> #gta6 #<thema>
```

Kein Beschreibungstext und kein Credit-Satz („mit Erlaubnis“), weder auf YouTube noch auf TikTok. Beispiele für TikTok: „I didn't mean to😢💔 #fyp #viral #lacy #gta6 #dog“, „Er musste es einfach tun😭💥 #fyp #viral #papaplatte #gta6 #explosion“.

Titelregeln stehen in `docs/kanal-regeln.md`.

## 6. Abschluss

1. Clip-IDs in `daten/verwendet.json` eintragen (auch die verworfenen).
2. Eine Zeile pro Short in `daten/log.tsv`: `datum	id	streamer	titel	status`.
3. `upload.md`, `worte.json`, `pruefung/` und die Datenänderungen committen und pushen. Videos werden nicht committed (`.gitignore`).
4. Dem Nutzer jeden `short.mp4` mit `SendUserFile` schicken (`status: proactive`). Die Caption enthält Nummer, Streamer und Titel. Danach eine Nachricht mit allen Titeln, Beschreibungen und Hashtags zum Kopieren.
5. **Cloud:** Hochladen macht der Nutzer selbst. Die Cloud-Session lädt nichts hoch.
   **Mac:** Statt `SendUserFile` direkt weiter mit `upload-mac.md` (privat bzw. Entwurf, veröffentlicht wird erst nach dem Ja des Nutzers).
6. Meldet der Nutzer etwas zurück (Short abgelehnt, Untertitel falsch), korrigieren, neu schicken und den Status in `daten/log.tsv` setzen.
