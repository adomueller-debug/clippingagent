# ClippingAgent auf dem Mac einrichten

Der Mac übernimmt den ganzen Tageslauf: Clips suchen, schneiden, auf YouTube **privat** und bei TikTok als **Entwurf** hochladen. Öffentlich wird ein Short erst, wenn du im Chat „Ja“ sagst. Das ist derselbe Ablauf wie beim YouTubeAgent.

Warum auf dem Mac und nicht in der Cloud: Die Videos sind zu groß fürs Repository, der Upload läuft über deinen angemeldeten Browser, und YouTube-Streams (IShowSpeed) lassen sich vom Mac aus laden.

Vieles ist vom YouTubeAgent schon da: Homebrew, ffmpeg, Python, yt-dlp, gh, die Claude-App, Claude in Chrome und der Weck-Zeitplan um 08:55 Uhr.

---

## 1. Repository holen (einmalig)

Im Terminal:

```bash
cd ~
git clone -b claude/happy-shannon-fczdyb https://github.com/adomueller-debug/clippingagent.git
cd clippingagent
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Test, ob Schneiden und Untertitel laufen (lädt beim ersten Mal das Untertitel-Modell, ca. 500 MB):

```bash
.venv/bin/python pipeline/schneiden.py \
  --url https://www.twitch.tv/papaplatte/clip/BashfulIntelligentTortoiseNerfRedBlaster-r8zIPLvDk_0VgN9d \
  --out arbeit/test/mac --sprache de --facecam 0.797,0.33,0.177,0.267
open arbeit/test/mac/short.mp4
```

Test für YouTube (IShowSpeed):

```bash
.venv/bin/python pipeline/youtube_highlights.py https://www.youtube.com/watch?v=o0UeucVxYCA --anzahl 3
```

Kommt eine Liste mit `highlights`, funktioniert es.

## 2. Kanal und TikTok-Konto anlegen

1. Den neuen YouTube-Kanal anlegen, am besten als zweiten Kanal unter deinem Google-Konto (YouTube → Profilbild → „Kanal erstellen“ bzw. „Kanal wechseln“ → „Kanal hinzufügen“).
2. Ein eigenes TikTok-Konto für den Kanal anlegen.
3. In Chrome bei beiden anmelden. Bei TikTok heißt das: im Konto des neuen Kanals, nicht im Unfathomd-Konto. Hast du beide TikTok-Konten, vor dem Lauf auf das richtige wechseln.
4. In `config/kanal.json` unter `upload` eintragen (oder Claude sagen, dass es das eintragen soll):
   ```json
   "youtube_kanalname": "Chat Went Crazy",
   "tiktok_konto": "@chatwentcrazy"
   ```
   Solange dort `null` steht, lädt der Mac nichts hoch. Das schützt davor, dass Clips auf Unfathomd landen.

## 3. Claude Code auf den Ordner zeigen

Claude-Desktop-App → Claude Code → Ordner `~/clippingagent` wählen. Der Skill `tagesproduktion` liegt im Repository und wird automatisch erkannt.

## 4. Geplante Aufgabe anlegen

In der Claude-Desktop-App eine geplante Aufgabe anlegen:

- **Name:** ClippingAgent: Tagesproduktion
- **Ordner:** `~/clippingagent`
- **Zeit:** täglich 09:40 Uhr (nach dem Unfathomd-Upload um 09:10 Uhr, der Mac ist ab 08:55 Uhr wach)
- **Auftrag:**

> Tagesproduktion für heute starten. Erst `git pull`. Folge dem Skill `tagesproduktion` Schritt für Schritt, wir sind auf dem Mac. ANZAHL = 5 Shorts, gemischt aus deutschen und englischen Streamern, inklusive YouTube-Streams von IShowSpeed. Gibt es keine Clips zum Spiel, nicht auf ein anderes Spiel ausweichen: kurz melden und beenden. Danach alle neuen Shorts nach `.claude/skills/tagesproduktion/upload-mac.md` auf YouTube privat und bei TikTok als Entwurf hochladen, Sendeplätze zuordnen, committen, pushen und mir die Liste schicken. Nichts veröffentlichen, bevor ich Ja sage.

Den Weck-Zeitplan nicht neu setzen: `pmset repeat` kennt nur einen Termin, und der um 08:55 Uhr reicht für beide Agenten.

## 5. Die Cloud-Aufgabe abschalten

Sobald der erste Lauf am Mac geklappt hat, Claude in der Cloud-Unterhaltung sagen: „Schalte die Cloud-Tagesproduktion ab.“ Sonst suchen Mac und Cloud jeden Tag dieselben Clips aus.

## 6. Freigeben

Nach dem Lauf meldet sich Claude mit der Liste. Du antwortest in der Sitzung des Laufs (auch per Handy über die Claude-App):

> Ja

(alle wie geplant), oder `Ja, 1 3 4` (nur diese), oder `Ja, 2 sofort`.

Dann plant Claude die Shorts in YouTube Studio und TikTok auf ihre Sendeplätze ein (Standard 18:00 bis 20:00 Uhr im 30-Minuten-Takt).

## Checkliste

- [ ] Repository unter `~/clippingagent`, `.venv` installiert, beide Tests laufen
- [ ] YouTube-Kanal und TikTok-Konto angelegt, in Chrome angemeldet
- [ ] `youtube_kanalname` und `tiktok_konto` in `config/kanal.json` eingetragen
- [ ] Claude Code zeigt auf `~/clippingagent`
- [ ] Geplante Aufgabe „ClippingAgent: Tagesproduktion“ um 09:40 Uhr angelegt
- [ ] Erster Lauf am Mac geklappt → Cloud-Aufgabe abgeschaltet
