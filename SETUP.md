# Einrichtung – Dreamy Elsewhere

Der laufende Blinkpuzz-Account und Vibsnaxx bleiben vollständig unangetastet.

## Bereits bereitgestellt
- `config.json` – vier tägliche Posting-Slots 17.11.–14.12.2026, danach zwei.
- `src/render.py` – aus je fünf geeigneten Fotos ein 1080×1920-Reel erstellen.
- `src/publish.py` – Buffer-Abgleich ausschließlich mit `@dreamy_elsewhere`.
- `.github/workflows/dreamy-pipeline.yml` – derzeit nur **manueller Testmodus**, ohne Zeitplan.

## Noch erforderlich
1. **Verfügbare Bildquelle**: GitHub Actions kann nicht direkt den Bildgenerator
   eines ChatGPT-Chats auslösen. Es fehlen die fortlaufend erstellten fünf Bilder pro Reel.
2. **Musikquelle**: Der bevorzugte Song benötigt eine zulässige Veröffentlichungsroute.
   Ohne rechtmäßig nutzbare Tondatei wird NICHT veröffentlicht.
3. **Buffer-API-Zugang**: Repository `Settings > Secrets and variables > Actions`,
   neues Secret `BUFFER_API_KEY` – Wert niemals in eine Repo-Datei oder diesen Chat schreiben.
4. **Prüflauf**: `Actions > Dreamy Elsewhere — Prepare and verify > Run workflow`.
   Ohne Buffer-Secret wird nur lokal geprüft, **nichts** veröffentlicht.
5. **Medienhosting**: Später GitHub Pages unter `Settings > Pages` auf
   `GitHub Actions` umstellen und Deployment aktivieren.
6. **Automatische Ausführung und Veröffentlichung** werden erst eingeschaltet,
   wenn die fehlende Bildquelle und Musikroute wirklich funktionieren.

## Sicherheitsregel
Keine subjektive Qualitätsbewertung. Nur technische Mindestauflösung, Dateiformat,
Vorhandensein aller fünf Bilder und erfolgreiche Videoerstellung. Buffer wird nur für
den **exakt zugeordneten Instagram-Kanal** angesprochen.

Das Repository hat am Ende des Namens einen Bindestrich:
`lucadimichele-svg/dreamy-elsewhere-automation-`.
