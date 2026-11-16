# Dreamy Elsewhere — Musikquelle

Gewählter Titel: **Vastness** von **Andrew Ev** (3:50), angeboten bei Mixkit.
Quelle: https://mixkit.co/free-stock-music/ambient/
Lizenz: https://mixkit.co/license/modal/musicFree/

Die Mixkit Stock Music Free License erlaubt die Nutzung der Musik in kommerziellen und
nichtkommerziellen Social-Media-Videos. Die isolierte Weiterverbreitung einer MP3
als eigenständiger Download ist nicht Teil unseres Workflows. Wir veröffentlichen
nur die damit vertonten Reel-MP4s.

**Private Ablage:** Google Drive, Dreamy Elsewhere - Bildproduktion / licensed-audio
https://drive.google.com/drive/folders/1yghmnkIr6vyN8Ok-WYjgdiZaqh8OQx2Y

**Technik:** Der Renderer akzeptiert `DREAMY_AUDIO_PATH` oder eine beim Renderlauf
vorhandene `assets/audio/background.mp3`, `.m4a` oder `.wav`. GitHub Actions muss
die tatsächlich lizenzierte Datei vor dem Rendern temporär bereitstellen.
Ohne verfügbare Audiodatei schlägt die Produktion absichtlich fehl. Es wird kein
stummes Reel als fertig markiert.

**Noch offen:** Die originale Mixkit-MP3 ist noch nicht im privaten Drive-Ordner
angekommen; der dauerhafte sichere Abruf beim GitHub-Runner muss anschließend
verbunden und mit einer fertigen MP4 geprüft werden. Kein Instagram-Publishing
aktivieren, bevor Bildimport, Audiomuxing, Hosting und Buffer-Queue geprüft sind.
