# Dreamy Elsewhere – verbindliche Methode für abwechslungsreiche Reel-Motive

Diese Produktionsregel gilt **für jedes neue Reel von @dreamy_elsewhere**. Sie ergänzt die bestehenden Vorgaben für Slot, Musik, Layout, Upload und Veröffentlichung. Das jeweilige Oberthema wird unverändert aus `config.json` und der Slot-Logik in `src/render.py` bestimmt.

## Phase 1: Fünf Welten festlegen – bevor ein Bild generiert wird

1. Bestimme die englische Auswahlfrage des Reels. Das Oberthema verbindet alle fünf Motive.
2. Plane **fünf unterschiedliche eigenständige Motivwelten**. Wähle für jedes Motiv getrennt:
   - Ort und geografische Umgebung,
   - Architektur oder Rückzugsort,
   - Kamerastandpunkt und Bildausschnitt,
   - zentralen Blickfang,
   - Tageszeit/Licht/Wetter,
   - charakteristische Materialien und Farben.
3. Nutze als Ideenpool etwa Unterwasser-Suite, Regenwald-Baumhaus, Nordlicht-Glaskuppel, Wüsten-Oase, mediterranes Klippenhaus, Vulkan-Lodge, versteckte Höhlenwohnung, Seehaus, modernes Stadt-Penthouse oder japanisches Ryokan. **Das sind keine fünf stets wiederkehrenden Standardszenen.** Wechsle die Kombination über die Reels hinweg passend zum Thema.
4. Plane nach Möglichkeit **höchstens zwei Motive derselben visuellen Familie**; idealerweise fünf verschiedene. Nicht fünf Betten in ähnlichen Berghütten. Das ist eine **Vorgabe zur Ideenplanung, KEIN nachträgliches subjektives Stopp- oder Freigabekriterium**.

## Phase 2: Fünf separat formulierte Prompts und fünf getrennte Generierungen

1. Erzeuge **jedes Bild einzeln mit einem eigenen image_gen-Aufruf**. Kein gemeinsamer Sammelprompt, kein `n=5` für ein Motiv und kein "zeige diese fünf Orte".
2. **Entscheidend gegen Collagen:** In **jedem einzelnen Bildprompt ausschließlich EINE einzige Szene beschreiben**. Keine Angaben wie "Bild 2 von 5", "five-location series", "compare the five destinations", "other four scenes" oder überhaupt eine Aufzählung weiterer Motivwelten. Dadurch wird verhindert, dass das Bildmodell ein Poster, Raster oder eine Collage interpretiert.
3. Jeder Prompt formuliert positiv, was **in diesem einen Bild** zu sehen sein soll. Keine Anweisungen über andere Szenen oder Inhalte anderer Bilder in demselben Prompt.
4. Verbindlicher Prompt-Abschluss (Englisch): **"One single continuous, full-frame vertical 9:16 photorealistic scene. No text, no typography, no logo, no labels, no split screen, no collage, no montage, no panels, no borders, no image grid, no watermark."**
5. Die fünf Prompts sollen **gezielt unterschiedliche** Standpunkte, Architekturen, Aussichten, Stimmungen und Lichtfarben haben; die Bildqualität soll scharf, detailliert, atmosphärisch und materialrealistisch sein. Cozy & Dreamy bleibt das verbindende Thema.
6. **Nur Bilddateien generieren.** Der GitHub-Renderer fügt englische Frage und dezente Nummerierung `01 / 05` usw. erst danach hinzu. Das Bildmodell darf keine Schrift, Nummern oder Instagram-Oberfläche einfügen.

### Prompt-Schablone: exakt ein Motiv

"Photorealistic high-detail vertical 9:16 photograph of [ONE SPECIFIC COZY DREAM LOCATION]. [EXACT UNIQUE ARCHITECTURE AND MATERIALS]. Camera positioned [SPECIFIC SINGLE VIEWPOINT], looking toward [ONE MAIN FOCAL POINT]. [UNIQUE LIGHT AND ATMOSPHERE], realistic rich textures, inviting warmth, believable construction, cinematic but natural. One single continuous, full-frame vertical 9:16 photorealistic scene. No text, no typography, no logo, no labels, no split screen, no collage, no montage, no panels, no borders, no image grid, no watermark."

## Phase 3: Technischer Durchlauf, keine subjektive Sperre

- Ziel: fünf wirklich getrennte, lesbare Bilddateien `01.png` bis `05.png`, je ein Vollbildmotiv. Auflösung höchstmöglich nativ; nach erforderlichem 9:16-Crop **höchstens einmal hochwertig** auf 1080×1920 skalieren. Bilder niemals strecken.
- Prüfe nur **technische** Kriterien: fünf tatsächliche Dateien, lesbares PNG, Abmessungen, korrekte Vollbildkomposition ohne technisch angelegte Mehrfachpanel-Raster, Dateizuordnung, Drive-Zugriff, Manifest und Renderer.
- Falls das Modell trotz Einzelprompt tatsächlich eine **Collage/Poster/Rasterdatei statt eines Einzelbildes** erzeugt, gilt das als **technisches Ausgabemedium-Problem**, nicht als ästhetische Kritik: einmal denselben Einzelort mit der obigen Schablone ohne Serienwörter neu erzeugen. **Nicht** wieder einen Sammelprompt verwenden. Keine endlosen Wiederholungsschleifen.
- **Niemals abbrechen, nur weil die Bilder subjektiv zu ähnlich, zu gewöhnlich oder nicht schön genug erscheinen.** Eine schwache, aber technisch gültige Einzelbildszene ist besser als ein ausgefallener Post.
- Bei technisch gültigen Einzelbildern die fünf Originale privat nach Google Drive übertragen, reale IDs im GitHub-Manifest speichern und den bestehenden GitHub-/Buffer-Prozess unverändert fortsetzen. Keine ästhetische Freigabe, keine zusätzlichen Qualitäts-Scorer, keine manuelle Rückfrage.

## Konten- und Betriebsschutz

Nur **@dreamy_elsewhere**, Repository `lucadimichele-svg/dreamy-elsewhere-automation-`, private Google-Drive-Ablage. Bereits vorhandene Slot-Manifeste und fertige Videos nicht duplizieren. Keine Änderungen an Blinkpuzz, Vibsnaxx oder Professor Wheel. Kein stillschweigendes Erfinden eines erfolgreichen Uploads oder Instagram-Posts.

**Merksatz:** Erst fünf deutlich unterschiedliche Orte **planen**, dann fünf **einzelne** Bildaufnahmen generieren, schließlich technisch verarbeiten und veröffentlichen – **ohne subjektive Blockade**.
