# Dreamy Elsewhere — aktuelle technische Einrichtung

**Account:** @dreamy_elsewhere · **Zeitzone:** Europe/Berlin

## Gewünschter Plan
- 17. November bis 14. Dezember 2026: vier Reels täglich (08:00, 12:30, 17:30, 21:30)
- Ab 15. Dezember: zwei Reels täglich (12:30, 20:30)
- Fünf eigenständige fotorealistische Cozy-/Dreamy-Bilder pro Reel, 1080×1920.
- Keine subjektive KI-Qualitätsbewertung.
- Keine weiteren kostenpflichtigen Abos.

## Realisierter Stand
1. Zeitgesteuerte ChatGPT-Bildgenerierung: separat getestet (fünf Bilder).
2. Drive: privater Projektordner und `incoming` / `used` existieren.
3. **Private Drive→GitHub-Blob-Übergabe:** Einzeltest erfolgreich.
   Drive-Files können authentifiziert gelesen und als Binär-Git-Blob
   hochgeladen werden, ohne den Drive-Ordner öffentlich zu teilen.
4. `src/blob_import.py`: GitHub Actions liest fünf SHA-Blobs anhand des
   Manifests `assets/drive_manifests/YYYY-MM-DD_SX.json` und verifiziert
   echte Bilddaten/Abmessungen.
5. `src/render.py`: rendert fünf Szenen zu einem 1080×1920-MP4.
6. `.github/workflows/dreamy-pipeline.yml`: startet durch den Commit
   eines vollständig ausgefüllten Manifests automatisch **nur** Import
   und Rendering, **keine Veröffentlichung**.
7. Buffer-Free-Bridge für den exakten Zielkanal liegt in der bestehenden
   Blinkpuzz-Repo als separater **read-only**-Prüfworkflow. Die
   produktive Blinkpuzz-Automation bleibt unverändert.

## Noch zu verifizieren
- Ein vollständiger fünfteiliger Produktionslauf
  ChatGPT → Drive → Blob → Manifest → GitHub Actions → MP4.
- GitHub-Pages-Hosting der fertigen MP4-Dateien.
- Unabhängige Queue-Befüllung für @dreamy_elsewhere über das vorhandene
  Buffer-Free-Secret (ohne @blinkpuzz zu verändern).
- Audio: Bevorzugt `Let Go — Ark Patrol (slowed)`; eine geeignete
  Nutzungs-/Automationsroute ist noch nicht bestätigt. Bis dahin kann
  die technisch erlaubte Variante als stummes Reel gerendert werden.
- Automatisches Löschen in Drive **erst nach tatsächlich bestätigter
  Veröffentlichung** und mindestens 24 Stunden Aufbewahrung.

## Sicherheits- und Speicherregel
Nie Bilddateien aus anderen Drive-Bereichen übernehmen oder löschen.
Drive-Bilder bleiben privat; ihre SHA-Adressen erscheinen im öffentlichen
GitHub-Repository. Die Blobkopien sind daher potentiell über SHA abrufbar.
Kein API-Schlüssel wird in GitHub-Dateien gespeichert. Originale fünf Bilder
werden nicht in die dauerhafte Git-Historie committed, sondern vom Runner
temporär abgerufen. Unreferenzierte Git-Objekte dürfen nicht als langfristige
Ablage betrachtet werden.

**Status:** Prototyp/Integrationstests, keine automatische Veröffentlichung
aktiviert. Reel-Produktion erst als erfolgreich melden, wenn der tatsächliche
Workflow grün ist und eine echte MP4-Datei vorliegt.

Repo-Name hat am Ende einen Bindestrich:
`lucadimichele-svg/dreamy-elsewhere-automation-`.
