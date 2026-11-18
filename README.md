# Dreamy Elsewhere 🌙 — Automatisierte 5-Auswahl-Reels

Ein autonomer Instagram-Reel-Produktionsablauf für **@dreamy_elsewhere** mit **einem selbst entwickelten Thema und fünf eigenständigen kreativen Varianten pro Reel**. Keine Wiederholung aus einem fixen Themenpool und keine generelle Festlegung auf Schlafzimmer/Cozy-Hütten.

## Feste Zeitfenster (Europe/Berlin)
- **17.11.–14.12.2026:** 4 Reels täglich, Veröffentlichung 08:00, 12:30, 17:30, 21:30 Uhr; Produktionsagent 07:00, 11:00, 16:00, 19:00.
- **Ab 15.12.2026:** 2 Reels täglich, Veröffentlichung 12:30 und 20:30 Uhr; Produktionsagent nur 11:00 und 19:00.
- Bereits existierende Manifest- und Video-Slot-IDs werden nicht dupliziert.

## Aktueller Creative-Workflow (seit 18.11.2026 S3)

1. ChatGPT-Automation **Dreamy Elsewhere Autoproduktion** liest `docs/scene-diversity-policy.md`, historische `assets/creative_plans/*.json` und ältere `docs/media/*.json`.
2. Der Agent erfindet eine neue englische Wahlfrage, z.B. zu Essen, Historie, Transport, fantasievollen Orten oder anderen **frei entwickelten Themen**. Er plant fünf klar unterscheidbare Varianten. Der alte `config.json.legacy_topics`-Pool dient ausschließlich als historische Kompatibilität und wird **nicht** für neue Posts rotiert.
3. **Vor den Bildern** wird ein neuer `assets/creative_plans/YYYY-MM-DD_Sx.json` mit `topic`, `theme_category` und fünf `variants` (`label`, `brief`, `image_prompt`) auf GitHub gespeichert. Diese Datei ist zugleich das **dauerhafte, wachsende kreative Gedächtnis**. Bei Teilausfall wird derselbe Plan wiederaufgenommen.
4. Fünf **wirklich unabhängige** fotorealistische 9:16-Originalbilder werden generiert, eines pro Brief. Keine Collage, kein Zuschneiden aus Bildmontagen, keine bereits in den Quellbildern eingebrannte Schrift. Keine subjektive AI-Qualitätsbewertung; nur native Quelldateigröße (mind. 800×1400), Lesbarkeit, eindeutige Dateien und Nutzbarkeit werden technisch geprüft.
5. Die fünf Dateien kommen über `files__manage_library` in den privaten Drive-Ordner `Dreamy Elsewhere - Bildproduktion/incoming/YYYY-MM-DD_Sx/`. Ein anschließend erstelltes GitHub-Manifest `assets/drive_manifests/YYYY-MM-DD_Sx.json` mit fünf echten Drive-Datei-IDs triggert `.github/workflows/dreamy-pipeline.yml`.
6. Die Pipeline importiert die privaten Bilder, liest den **exakt passenden Kreativplan**, erstellt ein 15-Sekunden-MP4 mit eingebetteter lizenzierter Musik und fünf je 3 Sekunden langen Bildszenen. **1080×1920, 30 FPS, H.264 CRF17**. Der Renderer `src/render.py` schreibt selbst die englische Themenfrage in eleganter **Gold-/Creme-Serifenschrift** oben und eine goldkonturierte Plakette mit **01–05 und Variantenname** unten. Grundlage ist der erfolgreich getestete `Choose Your Ride`-Look.
7. Die getrennte **Dreamy Elsewhere — Automatic Buffer Queue** verarbeitet ausschließlich fertige Dreamy-MP4s, verifiziert den exakten IG-Account und plant/veröffentlicht zum definierten Slot. Deduplication per `DEYYYYMMDDSx`-Marker; keine anderen Marken.

## Konzepttest vs. echtes Reel
- **Konzepttest:** Übersichtscollage zum schnellen Vergleichen von Ideen ist erlaubt, wird aber nicht zur Framequelle eines Reels.
- **Reel:** fünf unabhängige echte 9:16-Originaldateien mit native-resolutions-Prüfung. Keine nachträglich vergrößerten Collage-Panels.

## Technische Tests
- `.github/workflows/render-layout-smoke.yml`: 1080×1920 Full-Bleed, technisch korrektes H.264-Segment.
- `.github/workflows/open-theme-reel-smoke.yml`: neue freie Themenplanung, Variantenschrift, Bildquellen und 15-s-H264/AAC-Test ohne Veröffentlichung.
- `tools/choose_your_ride_demo.py`: separat gerendertes Test-Reel; nicht im Instagram-Publishing enthalten. Demo unter `docs/demos/choose_your_ride_15s.mp4`.

## Nicht verhandelbare Grenzen
- Keine subjektive AI-Bildfreigabe, kein Blockieren eines technisch fertigen Posts wegen ästhetischem Urteil.
- Keine aus Collagen ausgeschnittenen hochskalierten Einzelbilder.
- Keine Quell-/Musikrechte erfinden und keine nicht bestätigten Instagram-Veröffentlichungen als erfolgreich melden.
- Keine Änderungen an Blinkpuzz, Vibsnaxx oder Professor Wheel. Die Bridge nutzt nur bestehenden Zugriff, um **@dreamy_elsewhere** zu bedienen.
