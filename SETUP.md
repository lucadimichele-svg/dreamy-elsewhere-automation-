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
3. **Buffer-API-Zugang**: Buffer Free erlaubt nur einen persönlichen API-Schlüssel. Der vorhandene Schlüssel wird **nicht rotiert** und nicht in dieses Repository kopiert. Stattdessen enthält `lucadimichele-svg/blinkpuzz-automation` einen **neuen, isolierten**, ausschließlich manuellen und lesenden Prüf-Workflow `.github/workflows/dreamy-buffer-bridge.yml`. Er nutzt das bestehende `BUFFER_API_KEY`-Secret dort, checkt den Code von Dreamy Elsewhere aus und verifiziert ausschließlich den exakt passenden Instagram-Kanal `@dreamy_elsewhere`. Vorhandene Blinkpuzz-Workflows werden nicht verändert.
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
