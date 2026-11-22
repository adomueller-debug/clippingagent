# ClippingAgent auf dem Mac einrichten

Der Mac übernimmt den ganzen Tageslauf: Clips suchen, schneiden, auf YouTube **privat** hochladen. TikTok-Shorts werden erst zu ihrem Sendeplatz einzeln hochgeladen und sofort gepostet. Öffentlich wird ein Short erst, wenn du im Chat „Ja“ sagst. Das ist derselbe Ablauf wie beim YouTubeAgent.

Warum auf dem Mac und nicht in der Cloud: Die Videos sind zu groß fürs Repository, der Upload läuft über deinen angemeldeten Browser, und YouTube-Streams (IShowSpeed) lassen sich vom Mac aus laden.

Vieles ist vom YouTubeAgent schon da: Homebrew, ffmpeg, Python, yt-dlp, gh, die Claude-App, Claude in Chrome und der Weck-Zeitplan um 08:55 Uhr.

---

## 1. Repository holen (einmalig)

Im Terminal:

```bash
cd ~
git clone -b claude/happy-shannon-fczdyb https://github.com/adomueller-debug/clippingagent.git
cd clippingagent
brew install ffmpeg-full
/opt/homebrew/bin/python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

- **Python 3.12 statt `python3`:** Das System-Python von macOS (3.9) ist zu alt für yt-dlp 2026.
- **`ffmpeg-full`:** Homebrews normales `ffmpeg` (ab 9.0) hat kein libass, kann also keine Untertitel einbrennen, und scheitert beim Laden von YouTube-Abschnitten an der TLS-Prüfung. Die Pipeline nimmt `ffmpeg-full` automatisch, wenn es installiert ist.

Test, ob Schneiden und Untertitel laufen (lädt beim ersten Mal das Untertitel-Modell, ca. 500 MB):

```bash
.venv/bin/python pipeline/schneiden.py \
  --url 'https://www.twitch.tv/papaplatte/clip/BashfulIntelligentTortoiseNerfRedBlaster-r8zIPLvDk_0VgN9d' \
  --out arbeit/test/mac --sprache de --facecam 0.797,0.33,0.177,0.267
open arbeit/test/mac/short.mp4
```

Test für YouTube (IShowSpeed):

```bash
.venv/bin/python pipeline/youtube_highlights.py 'https://www.youtube.com/watch?v=5CPAtEmHAio' --anzahl 3
```

Kommt eine Liste mit `highlights`, funktioniert es. URLs in Anführungszeichen setzen, sonst bricht zsh am `?` ab. Viele IShowSpeed-Streams haben bei YouTube keine „Meistgesehen“-Kurve. Dann meldet das Skript `keine Most-Replayed-Daten`, und das ist kein Fehler.

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

> Tagesproduktion für heute starten. Erst `git pull`. Folge dem Skill `tagesproduktion` Schritt für Schritt, wir sind auf dem Mac. ANZAHL = 10 Shorts zur Auswahl, etwa 7 englische und 3 deutsche, inklusive YouTube-Streams von IShowSpeed. Gibt es keine Clips zum Spiel, nicht auf ein anderes Spiel ausweichen: kurz melden und beenden. Danach alle neuen Shorts nach `.claude/skills/tagesproduktion/upload-mac.md` auf YouTube privat hochladen, YouTube- und TikTok-Sendeplätze zuordnen, committen, pushen und mir die Liste mit den TikTok-Texten schicken. Zu TikTok morgens nichts hochladen: jeder TikTok-Short wird nach meinem Ja einzeln zu seinem Sendeplatz hochgeladen und sofort gepostet. Jeder TikTok-Text und jede Hashtag-Kombination muss sich von den anderen unterscheiden, kein #fyp oder #viral. Nichts veröffentlichen, bevor ich Ja sage.

Den Weck-Zeitplan nicht neu setzen: `pmset repeat` kennt nur einen Termin, und der um 08:55 Uhr reicht für beide Agenten.

## 5. Die Cloud-Aufgabe abschalten

Sobald der erste Lauf am Mac geklappt hat, Claude in der Cloud-Unterhaltung sagen: „Schalte die Cloud-Tagesproduktion ab.“ Sonst suchen Mac und Cloud jeden Tag dieselben Clips aus.

## 6. Freigeben

Nach dem Lauf meldet sich Claude mit der Liste. Du antwortest in der Sitzung des Laufs (auch per Handy über die Claude-App):

> Ja

(alle wie geplant), oder `Ja, 1 3 4` (nur diese), oder `Ja, 2 sofort`.

Dann plant Claude die Shorts in YouTube Studio ein (Standard 18:00 bis 20:00 Uhr im 30-Minuten-Takt) und legt für jeden TikTok-Short eine einmalige Aufgabe zu seinem TikTok-Sendeplatz an (Standard 13, 15, 17, 19, 21 Uhr). Die lädt den Short dann hoch und postet ihn sofort.

## Checkliste

- [x] Repository unter `~/clippingagent`, `.venv` installiert, beide Tests laufen
- [ ] YouTube-Kanal und TikTok-Konto angelegt, in Chrome angemeldet
- [ ] `youtube_kanalname` und `tiktok_konto` in `config/kanal.json` eingetragen
- [x] Claude Code zeigt auf `~/clippingagent`
- [ ] Geplante Aufgabe „ClippingAgent: Tagesproduktion“ um 09:40 Uhr angelegt
- [ ] Erster Lauf am Mac geklappt → Cloud-Aufgabe abgeschaltet
