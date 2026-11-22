# clippingagent

Automatische Streamer-Shorts (zum Start: GTA 6) für TikTok (@chatwntcrazy). Produziert wird täglich in der Cloud, gepostet wird von Hand.

| Teil | Datei |
|---|---|
| Ablauf für die tägliche Session | `.claude/skills/tagesproduktion/SKILL.md` |
| Streamer, Spiele | `config/kanal.json` |
| Scout (Twitch-Clips finden) | `pipeline/scout.py` |
| Cutter (9:16 + Untertitel) | `pipeline/schneiden.py` |
| Kanal-Regeln, Namensvorschläge | `docs/kanal-regeln.md` |
| Recherche bestehender Repos | `docs/01-recherche.md` |
| Bereits verwendete Clips, Log | `daten/` |
| Einrichtung auf dem Mac (Produktion + Upload) | `docs/mac-setup.md` |
| Upload-Ablauf am Mac | `.claude/skills/tagesproduktion/upload-mac.md` |

Einrichten: `pip install -r requirements.txt`, dazu wird `ffmpeg` gebraucht.
