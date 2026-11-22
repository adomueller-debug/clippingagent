# Kanal-Regeln (Entwurf)

## Name: Vorschläge

Der Name soll breiter sein als GTA, in Deutsch und Englisch funktionieren und sagen, was man bekommt: den Moment, in dem der Stream eskaliert.

| Name | Handle | Warum |
|---|---|---|
| **Chat Went Crazy** | @chatwentcrazy | Beschreibt genau den Moment, den wir clippen. Twitch-Sprache, die auch deutsche Zuschauer kennen. **Empfehlung** |
| Peak Stream | @peakstream | „Peak" ist Jugendsprache in beiden Sprachen. Kurz, Spiel-unabhängig |
| Clip Rush | @cliprush | Tempo, viele Clips am Tag. Neutral |
| Stream Eskaliert | @streameskaliert | Sehr klar für Deutsche, für englische Clips schwächer |
| Minus Aura | @minusaura | Aktueller Slang (kommt sogar im Testclip vor), kann aber schnell altern |

Die Verfügbarkeit der Handles muss beim Anlegen des Kanals geprüft werden.

## Look

- Farben: Schwarz, Weiß, Signalgelb `#FFE500`. Das Gelb ist auch die Farbe des gerade gesprochenen Worts in den Untertiteln. So erkennt man den Kanal im Feed wieder.
- Schrift: Anton (schon im Repo, `assets/fonts/`).
- Profilbild: gelbes Chat-Sprechblasen-Symbol mit „!!" auf Schwarz.
- Shorts: Facecam oben, Gameplay unten, Untertitel auf der Naht. Kein Logo, kein Intro, kein Outro.

## Titel und Texte

Siehe `docs/tiktok-analyse.md` und Schritt 5 im Skill `tagesproduktion`. Kurz:

- **TikTok:** 2–8 Wörter, macht neugierig, 0–2 Emoji, dann 3–5 Hashtags (siehe „TikTok-Hashtags“). Jeder Text anders gebaut, nie `#fyp`/`#viral`. Kein Credit-Satz.
- **YouTube:** Titel im Stil A („Meme“: „Monte did Schradin dirty 😭😭“) oder Stil B („Satz“: „Kai Cenat Gets Chased By The Cops In GTA VI 😭🚨“), abwechselnd, um zu testen. Beschreibung nur Hashtags.
- **Hook-Zeile im Video:** Streamer + was passiert, 3–8 Wörter, ohne Emoji.

## TikTok-Hashtags

3–5 pro Short, jedes Mal neu zusammengestellt:

- **Spiel (genau 1, abwechseln):** `#gta6`, `#gtavi`, `#grandtheftauto6`, `#gta6gameplay`, `#gta6clips`
- **Streamer (1):** der Name, wie die Community ihn schreibt, z. B. `#montanablack`, `#kaicenat`, `#papaplatte`
- **Inhalt (1–2, passend zum Clip):** z. B. `#gta6funny`, `#gta6fails`, `#twitchclips`, `#streamerclips`, `#gamingclips`, `#gta6memes`, oder ein Wort für das Geschehen (`#polizei`, `#flugzeug`, `#bankraub`)
- **Optional Sprache/Region (0–1):** `#twitchde`, `#deutschegamer` bei deutschen Clips
- **Nie:** `#fyp`, `#foryou`, `#foryoupage`, `#viral`, `#fürdich`, `#trending`. Sie bringen nichts und gelten als Spam-Signal.

## TikTok-Posten

- Jeden Short **direkt veröffentlichen** („Posten“), nicht in TikTok planen und nicht mehrere auf Vorrat hochladen. Am 21.11. wurden 10 Clips in 4 Minuten hochgeladen und 9 davon geplant. Die geplanten bekamen 0–4 Aufrufe, der direkt gepostete 269.
- Hochladen und Posten passieren im selben Moment, zum Sendeplatz.
- Höchstens 3 Posts am Tag, mindestens 3 Stunden Abstand (`upload.tiktok_sendeplaetze` in `config/kanal.json`: 12:00, 17:00, 21:00). Grenzwertige Shorts (`- Plattform: nur YouTube`) nie zu TikTok.

## Rhythmus

- Lauf jeden Morgen um 08:40 Uhr (Europe/Berlin): 10 Shorts zur Auswahl, etwa 7 englische und 3 deutsche. Der Nutzer wählt aus; empfohlen sind 3–5 Uploads pro Tag.
- Hochladen über den Tag verteilt: YouTube mindestens 2 Stunden Abstand, TikTok höchstens 3 am Tag mit mindestens 3 Stunden Abstand (Sendeplätze in `config/kanal.json`).
- Höchstens 2 Shorts pro Streamer und Tag.
- Nie einen Moment hochladen, den der Streamer oder ein Clip-Kanal schon gepostet hat (TikTok spielt Kopien nicht aus).

## Messen

Pro Short protokollieren: Streamer, Länge, Layout, Titelform, Uhrzeit. Nach 2 Wochen auswerten: welche Streamer, welche Länge, welche Titel funktionieren.
