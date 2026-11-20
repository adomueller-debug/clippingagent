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

- **TikTok:** 2–6 Wörter, macht neugierig, 2–3 Emoji, dann `#fyp #viral #<streamer> #gta6 #<thema>`. Kein Beschreibungstext, kein Credit-Satz.
- **YouTube:** Titel im Stil A („Meme“: „Monte did Schradin dirty 😭😭“) oder Stil B („Satz“: „Kai Cenat Gets Chased By The Cops In GTA VI 😭🚨“), abwechselnd, um zu testen. Beschreibung nur Hashtags.
- **Hook-Zeile im Video:** Streamer + was passiert, 3–8 Wörter, ohne Emoji.

## Rhythmus

- Lauf jeden Morgen um 08:40 Uhr (Europe/Berlin): 10 Shorts zur Auswahl, etwa 7 englische und 3 deutsche. Der Nutzer wählt aus; empfohlen sind 3–5 Uploads pro Tag.
- Hochladen über den Tag verteilt, mindestens 2 Stunden Abstand (Sendeplätze in `config/kanal.json`).
- Höchstens 2 Shorts pro Streamer und Tag.
- Nie einen Moment hochladen, den der Streamer oder ein Clip-Kanal schon gepostet hat (TikTok spielt Kopien nicht aus).

## Messen

Pro Short protokollieren: Streamer, Länge, Layout, Titelform, Uhrzeit. Nach 2 Wochen auswerten: welche Streamer, welche Länge, welche Titel funktionieren.
