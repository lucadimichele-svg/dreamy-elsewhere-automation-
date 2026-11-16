# Drive → GitHub: Fünf-Bilder-Übergabe

Die Google-Drive-Ordner bleiben **privat**. Eine geplante ChatGPT-Aufgabe
lädt fünf Originalbilder in den Drive-Unterordner `incoming/YYYY-MM-DD_SX`.
Anschließend liest sie jede Bilddatei über den verbundenen Drive-Zugang,
übergibt deren echte Binärdaten über `GitHub.create_blob` an dieses Repo
und notiert die fünf zurückgegebenen Blob-SHAs.

Beispiel für `assets/drive_manifests/2026-11-17_S1.json`:

```json
{
  "date": "2026-11-17",
  "slot": "S1",
  "drive_folder_id": "EXACT_ACTUAL_FOLDER_ID",
  "files": [
    {"name":"01.png","drive_id":"EXACT_DRIVE_FILE_ID_01","blob_sha":"40_HEX_CHARS"},
    {"name":"02.png","drive_id":"EXACT_DRIVE_FILE_ID_02","blob_sha":"40_HEX_CHARS"},
    {"name":"03.png","drive_id":"EXACT_DRIVE_FILE_ID_03","blob_sha":"40_HEX_CHARS"},
    {"name":"04.png","drive_id":"EXACT_DRIVE_FILE_ID_04","blob_sha":"40_HEX_CHARS"},
    {"name":"05.png","drive_id":"EXACT_DRIVE_FILE_ID_05","blob_sha":"40_HEX_CHARS"}
  ]
}
```

**Platzhalter, keine gültigen IDs.** Erst nachdem alle fünf echten Uploads
und alle fünf `create_blob`-Aufrufe erfolgreich waren, die JSON-Datei in
GitHub erzeugen. Das löst den Workflow `dreamy-pipeline.yml` aus.

GitHub Actions liest die fünf Bild-Blobs anhand ihrer SHA, kontrolliert
tatsächliche Bilddaten, Auflösung und Reihenfolge und rendert ein Reel.
Die Ausgangsbilder werden nicht in die dauerhafte Git-Historie committed.
GitHub garantiert allerdings keine unbegrenzte Aufbewahrung unreferenzierter
Blobs; die Verarbeitung muss zeitnah erfolgen.

**Datenschutz:** Der Drive-Ordner bleibt privat. Die SHA-IDs stehen jedoch in
einem öffentlichen GitHub-Repository; jemand mit der SHA kann möglicherweise
die entsprechende Bildkopie abrufen. Keine vertraulichen Bilder verwenden.

**Keine Löschung im Importprozess.** Drive-Bilder bleiben erhalten, bis ein
unabhängiger Cleanup-Prozess die tatsächliche Instagram-Veröffentlichung
bestätigt hat und mindestens 24 Stunden vergangen sind.

Das Import-Workflow testet derzeit nur die technisch sichere Produktionsstrecke;
automatische Veröffentlichung wird separat aktiviert.
