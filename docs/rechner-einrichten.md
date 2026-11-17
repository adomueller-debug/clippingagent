# Eigenen Rechner für YouTube-Clips einrichten

YouTube blockiert Downloads aus der Cloud. Deshalb holt die tägliche Session IShowSpeeds YouTube-Streams über deinen Rechner. Der Rechner muss dafür um 08:40 Uhr an sein und die Claude-Desktop-App muss laufen.

## 1. Programme installieren (einmalig)

**Mac** (mit Homebrew):
```bash
brew install python ffmpeg git
```

**Windows** (PowerShell):
```powershell
winget install Python.Python.3.12 Gyan.FFmpeg Git.Git
```

## 2. Repo holen und Pakete installieren

Im Terminal in einen Ordner deiner Wahl wechseln, z. B. `Dokumente`, nicht direkt den Benutzerordner:
```bash
git clone -b claude/happy-shannon-fczdyb https://github.com/adomueller-debug/clippingagent.git
cd clippingagent
pip install -r requirements.txt
```

Test (darf ein paar Sekunden dauern):
```bash
python pipeline/youtube_highlights.py https://www.youtube.com/watch?v=o0UeucVxYCA --anzahl 3
```
Kommt eine Liste mit `highlights`, funktioniert es.

## 3. Ordner für Claude freigeben

Claude-Desktop-App → Einstellungen → Claude Code → Remote Control → den Ordner `clippingagent` hinzufügen.

Danach in der Unterhaltung Bescheid sagen. Claude fragt dann einmal nach der Erlaubnis, den Ordner zu nutzen.

## Wo die Shorts landen

Shorts aus YouTube-Streams liegen danach auf deinem Rechner unter `clippingagent/ausgabe/<Datum>/`. Alle anderen (Twitch, Kick) bekommst du wie bisher als Datei in der Unterhaltung.
