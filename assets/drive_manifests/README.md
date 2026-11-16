# Dreamy Elsewhere: Google Drive image manifests

The scheduled ChatGPT production task should upload five separate original
images into the **dedicated** Google Drive `incoming/YYYY-MM-DD_SX` folder.

Each Reel is represented by a single JSON manifest, only after five uploads
have returned confirmed Drive file IDs:

```json
{
  "date": "2026-11-17",
  "slot": "S1",
  "folder_id": "ACTUAL_DRIVE_FOLDER_ID",
  "files": [
    {"name":"01.png","id":"ACTUAL_FILE_ID_1"},
    {"name":"02.png","id":"ACTUAL_FILE_ID_2"},
    {"name":"03.png","id":"ACTUAL_FILE_ID_3"},
    {"name":"04.png","id":"ACTUAL_FILE_ID_4"},
    {"name":"05.png","id":"ACTUAL_FILE_ID_5"}
  ]
}
```

These are examples, **not actual file IDs**. Use the exact returned upload
file IDs. Do not write a manifest while any upload is incomplete.

Do not place a secret, OAuth token, or service-account credential in a
manifest. The current importer needs the FIVE individual image links to
be accessible to GitHub's runner. The Drive `incoming` folder is presently
**private**, and import has not yet been tested end-to-end. Do not expose
the whole Drive account. Public sharing of only a dedicated image inbox
would require the owner's informed decision.

The importer is read-only: it does not move or delete Drive originals.
Images are not removed until successful publication has been verified
separately and the cleanup rules have been tested.
