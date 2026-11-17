# Dreamy Elsewhere 🌙

Autonomer Instagram-Reel-Workflow für @dreamy_elsewhere.

## Zeitplan
- 17.11.–14.12.2026: vier Reels täglich, Ziele 08:00, 12:30, 17:30, 21:30 (Europe/Berlin).
- Ab 15.12.2026: zwei Reels täglich, 12:30 und 20:30.
- Aktive ChatGPT-Bildproduktion um 07:00, 11:00, 16:00, 19:00; ab 15.12. sind 07:00 und 16:00 ausgesetzt.

## Produktionskette
1. ChatGPT-Automation „Dreamy Elsewhere Autoproduktion“ generiert pro Slot fünf verschiedene fotorealistische 9:16-Motive, überprüft nur Dateilesbarkeit und Mindestauflösung, und lädt die fünf PNGs in den privaten Google Drive-Ordner Dreamy Elsewhere - Bildproduktion/incoming/YYYY-MM-DD_SX/ hoch.
2. Die Automation legt ein echtes Drive-Datei-ID-Manifest unter assets/drive_manifests/ im GitHub-Repo an. Dadurch startet GitHub Actions dreamy-pipeline.yml automatisch.
3. GitHub lädt die Bilder privat per Google-Servicekonto, bindet die Soundtrack-Datei aus licensed-audio ein und rendert die 15-Sekunden-MP4 in docs/media/.
4. Eine getrennte GitHub-Action „Dreamy Elsewhere — Automatic Buffer Queue“ prüft stündlich die fertigen Reels, verifiziert exakt Instagram @dreamy_elsewhere und nutzt Buffer, um zu publizieren oder für die konfigurierten Slots einzuplanen. Dreamy-ID-Marker verhindern Duplikate.
5. Der Buffer-API-Schlüssel bleibt geschützt in einem vorhandenen separaten GitHub-Repository; der Dreamy-Bridge-Workflow verändert keine anderen Instagram-Kanäle oder deren bestehende Jobs.

## Freigabe und Status
- Keine subjektive KI-Bildbewertung, keine manuelle ästhetische Freigabeschleife, keine automatische Löschung der Drive-Originale.
- 17.11.2026: Der erste echte Reel wurde durch Buffer mit Status sent bestätigt: https://www.instagram.com/reel/Df0sr4dD_6z/
- 17.11.2026: Automatischer Buffer-Queue-Test erfolgreich: exakt @dreamy_elsewhere verifiziert, keine Doppelveröffentlichung.
- Der erste komplett unbeaufsichtigte Bildproduktionslauf ist noch ausstehend. Nur nach erfolgtem Lauf darf die gesamte unbeaufsichtigte Strecke als erprobt bezeichnet werden.

## Repository
Der exakte Repo-Name hat einen abschließenden Bindestrich: dreamy-elsewhere-automation-.
