# Recherche: Gibt es ein fertiges Repo für GTA-6-Streamer-Shorts?

Stand: 17.11.2026

## Ergebnis in einem Satz

Es gibt kein Repo, das genau unseren Ablauf abdeckt (Twitch/YouTube-Streamer → virale Momente finden → 9:16-Short → automatischer Upload auf einen eigenen Kanal). Es gibt aber gute, MIT-lizenzierte Bausteine. Empfehlung: eine eigene, schlanke Pipeline als Skill bauen und die bewährten Teile (yt-dlp, faster-whisper, ffmpeg, Twitch-Helix-API, YouTube-Data-API) direkt nutzen. Die Highlight-Logik von `AI-Youtube-Shorts-Generator` dient als Vorlage.

## Geprüfte Repos

| Repo | Sterne | Lizenz | Was es kann | Passt für uns? |
|---|---|---|---|---|
| zhouxiaoka/autoclip | ~10.600 | MIT | Desktop-App: langes Video → Shorts mit Untertiteln und Cover. Fokus Podcasts, Interviews, chinesische Plattformen | Nein. Schwergewichtige App mit GUI, nicht für Gaming, kein YouTube-Upload |
| modelscope/FunClip | ~6.600 | MIT | Transkription + LLM-Schnitt nach Text | Nein. Rein sprachbasiert, Gaming-Momente ohne Sprache fallen durch |
| Anil-matcha/AI-Youtube-Shorts-Generator | ~6.200 | MIT | YouTube-URL → Whisper → LLM bewertet Viralität → 9:16-Clips mit Gesichts-Crop. CLI und Python-Bibliothek, `--mode local` ohne Bezahl-API | Teilweise. Gute Vorlage für den Bewertungs-Prompt und den Crop. Standardmodus hängt an einer kommerziellen API (MuAPI), kein Upload, kein Twitch |
| offish/twitchtube | ~620 | MIT | Meistgesehene Twitch-Clips einer Kategorie holen, zusammenschneiden, auf YouTube hochladen | Teilweise. Genau unsere Quelle (Twitch-Clips nach Views), aber Compilations statt Shorts, wird gerade umgeschrieben, letzter Push 07/2025 |
| ContentAutomation/TwitchCompilationCreator | ~280 | – | Twitch-Compilations | Nein. Seit 2022 tot |
| artbyjazi/autoclip | ~360 | MIT | Lokaler Clipper mit Sprecher-Tracking | Nein. Sprachfokus, kein Upload |
| rushindrasinha/youtube-shorts-pipeline | ~2.400 | – | News → Skript → KI-Bilder → Voiceover → Upload | Nein. Erzeugt eigene Inhalte, kein Clipping. Höchstens Upload-Teil als Referenz |

## Vorsicht

- `ColinGPT9/clips-studio` und `ColinGPT9/Grand-Theft-Auto-6-Clips-Kitty-Plugin`: neue Konten, „GTA 6"-Köder zwei Tage vor Release, Sterne ohne Nutzungsspuren. Das ist das typische Muster von Malware-Repos. Nicht klonen, nicht ausführen.
- Viele Repos mit 0 bis 10 Sternen und Namen wie „autoclip-studio" sind Kopien voneinander. Nicht verwenden.

## Warum Gaming anders ist als Podcasts

Fast alle großen Clipper wählen Momente über das Transkript aus. Bei GTA sind die besten Momente oft ohne Sprache: Unfälle, Verfolgungsjagden, Bugs, Schreie, Lachen. Bessere Signale:

1. **Twitch-Clips nach Views.** Zuschauer haben den Moment schon geclippt. Die Helix-API (`GET /helix/clips?game_id=…&started_at=…`) liefert die meistgesehenen Clips einer Kategorie der letzten 24 Stunden. Das ist das stärkste und billigste Viralitätssignal.
2. **Chat-Spitzen in VODs.** Viele Nachrichten pro Sekunde, viele „LUL"/„KEKW" = Highlight.
3. **Audio-Spitzen.** Lautstärke-Sprünge (Schreien, Lachen).
4. **Transkript + LLM** als letzter Filter für Kontext, Hook und Titel.

## Erreichbarkeit aus dieser Umgebung (getestet)

| Dienst | Erreichbar |
|---|---|
| Twitch Helix API, Twitch GQL | ja (401/400 = Server antwortet, Login fehlt) |
| YouTube-Webseite | ja |
| YouTube Data API Upload, Google OAuth | ja |
| ffmpeg, Python 3.13 | installiert |
| yt-dlp | nicht installiert, per pip möglich |

Hinweis: YouTube blockiert Downloads aus Rechenzentrums-IPs häufig („Sign in to confirm you're not a bot"). Twitch-Clips lassen sich in der Regel problemlos laden.

## Vorgeschlagene Agenten

| Agent | Aufgabe |
|---|---|
| Scout | Holt täglich Kandidaten: Top-Twitch-Clips der Kategorie GTA VI, neue Highlight-Videos der Ziel-Streamer |
| Kurator | Bewertet Kandidaten (Views, Länge, Hook in den ersten 2 s, Dubletten, Streamer auf der Erlaubt-Liste) und wählt die besten aus |
| Cutter | Lädt, schneidet auf 15–45 s, baut 9:16 (Facecam oben, Gameplay unten), brennt Untertitel ein, Quellen-Credit im Bild |
| Texter | Titel, Beschreibung mit Credit-Link zum Streamer, Hashtags |
| Prüfer | Schaut Frames und Ton an, prüft Regeln (Länge, Lautheit, Text lesbar, Credit vorhanden) |
| Publisher | Lädt über die YouTube Data API hoch, plant Uhrzeit, führt Logbuch |
| Analyst | Liest täglich die Zahlen der eigenen Shorts und passt die Bewertung des Kurators an |

## Offene Punkte

Siehe Fragenliste im Chat. Bevor Code entsteht, müssen vor allem Rechte, Hosting und YouTube-API-Zugang geklärt sein.
