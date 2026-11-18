# Dreamy Elsewhere — verbindliche offene Themen- und Reel-Produktion

## Grundprinzip (ab 18.11.2026 S3)

**EIN neues gemeinsames Thema + FÜNF kreative, eigenständige Varianten dieses Themas.**

Es gibt KEINEN begrenzten, regelmäßig rotierenden Themenpool mehr. Dreamy Elsewhere ist kein Account, der nur Schlafzimmer, Hütten oder gemütliche Aussichtszimmer produziert. "Dreamy" bedeutet einladend, faszinierend, atmosphärisch und fantasievoll; es ist keine Pflicht zu Betten, Fenstern, Bergen oder "Cozy Room" in jedem Bild.

Mögliche Gegenstände eines Themas: Frühstück, Festessen, Dessert, königliche Throne, Fahrzeuge, magische Portale, verlorene Städte, Bäder, versteckte Bibliotheken, Märkte, außergewöhnliche Unterkünfte, Gärten, Festivals, historische und futuristische Erlebnisse. Dies ist nur Inspiration: **nie als fertige Pflichtliste interpretieren**. Erfinde auch Themen, die hier nicht stehen.

Die fünf Varianten müssen auf die *gleiche* Wahlfrage antworten, dürfen aber in Epoche, Architektur, Kultur, Technik, Material, Schauplatz, Bildstimmung und Fantasie weit auseinander liegen.

Gute Beispiele (nicht als schablonenhafte Dauerthemen wiederholen):
- **Choose your feast:** mittelalterliches Festmahl / antikes Rom / pharaonisches Ägypten / japanisches Kaiserdinner / futuristisches Dinner.
- **Choose your ride:** Belle-Époque-Zug / fliegendes Piratenschiff / Luftschiff / magische Kutsche / Raumschiff.
- **Which lost city would you explore?:** Atlantis / verschollene Maya-Stadt / Kristallstadt / Wüstenmetropole / schwebende Stadt.

## Verbindliche Reihenfolge

1. **Echtes aktuelles Slotdatum bestimmen**; alte `assets/drive_manifests/YYYY-MM-DD_Sx.json` und `docs/media/YYYY-MM-DD_Sx.json` zuerst prüfen. Fertige Slots niemals doppelt erzeugen.
2. **Themenhistorie lesen:** Alle oder mindestens die jüngsten 40 Einträge unter `assets/creative_plans/`, außerdem vorhandene `docs/media/*.json` der alten Reels. Themen UND die fünf Varianten beachten. Nicht nur den letzten Beitrag ansehen; aktuelle Wiederholungen möglichst vermeiden. Historische Ähnlichkeit ist ein Ideationssignal, **kein nachträgliches Verbot oder Veröffentlichungsgate**.
3. **Offen ein Thema entwickeln.** Keine Modulo-/Index-Auswahl aus `config.json`; `legacy_topics` ist ausschließlich ein Kompatibilitätsarchiv für die vor der Umstellung bereits erzeugten Reels. Eine neue Frage plus eine frei gewählte `theme_category` definieren, z.B. `food/history`, `fantasy/transport`, `exploration/mythology` oder eine völlig neue Kategorie.
4. **Vor Generierung genau fünf Varianten planen** — jeweils eindeutiger Labelname, eine konkrete Szenenbeschreibung und ein Prompt für **genau dieses eine** Bild. Gleiche Themafrage, aber fünf unterschiedliche kreative Ansätze. Das Objekt selbst (Essen, Fahrzeug, Stadt etc.) muss deutlich erkennbar sein; keine reflexartige Wiederholung von Betten/Glaskuppeln/Unterwasser-Suiten.
5. **Kreativplan zuerst dauerhaft sichern** im Repository auf Main als `assets/creative_plans/YYYY-MM-DD_Sx.json`. Die plan Datei ist gleichzeitig unser wachsendes Gedächtnis und die verbindliche Quelle für Theme/Variantenschrift im Renderer. Wenn ein Plan nach einem Teilausfall bereits existiert, genau diesen Plan wiederverwenden, **keinen anderen Themenentwurf erfinden**. Ein existierender Plan allein bedeutet noch nicht, dass die Produktion fertig ist.
6. **Fünf originale Einzelbilder generieren:** pro Variante ein eigener, voneinander unabhängiger image_gen-Aufruf mit nur ihrem einzelnen Bildmotiv. Kein Sammelprompt, keine Referenz auf frühere generierte Bilder und keine Collage. Keine Nummerierung/Schrift im Quellbild; das macht erst GitHub. Wenn der Bildgenerator ungewollt eine Collage erzeugt, denselben EINEN Bildprompt erneut als isolierte Einzelaufnahme versuchen, niemals daraus Panel-Crops herausschneiden.
7. **Nur technische Prüfung:** fünf unterscheidbare echte Dateien, gültige PNGs, tatsächliche native Originalabmessungen >=800x1400, brauchbares Hochformat (9:16), korrekte Reihenfolge/IDs und kein byte-identisches Duplikat. Keine subjektive Ästhetikbewertung, kein KI-Scorer, keine manuelle Freigabe. Selbst wenn ein fertiges echtes Einzelbild ästhetisch ähnlich wirkt, immer fortfahren.
8. Fünf Quellbilder nach privatem Drive in `incoming/YYYY-MM-DD_Sx/01.png` bis `05.png` hochladen, echte Drive-IDs prüfen, dann einmalig `assets/drive_manifests/YYYY-MM-DD_Sx.json` anlegen. Bestehende Pipeline importiert, rendert MP4 mit Musik, die getrennte Buffer-Bridge veröffentlicht exakt **@dreamy_elsewhere**. Andere Marken niemals anfassen.
9. Dokumentiere Thema, Kategorie und die fünf Varianten im Kreativplan sowie im Ausgabe-Manifest. Überprüfe technische Erfolge, erfinde keine Veröffentlichungsbestätigungen.

## Exaktes Kreativplan-Format

`assets/creative_plans/YYYY-MM-DD_Sx.json`:

```json
{
  "date": "2026-11-19",
  "slot": "S1",
  "topic": "Which magical vehicle would you take?",
  "theme_category": "fantasy/transport",
  "variants": [
    {"label": "VINTAGE LUXURY TRAIN", "brief": "Ornate steam train crossing a stone viaduct at dawn", "image_prompt": "Photorealistic vertical portrait of one luxury steam locomotive..."},
    {"label": "FLYING PIRATE SHIP", "brief": "Wooden pirate sailing ship high above sunset clouds", "image_prompt": "Photorealistic vertical portrait of one airborne pirate ship..."},
    {"label": "LUXURY AIRSHIP", "brief": "Art Deco Zeppelin above a historic metropolis", "image_prompt": "Photorealistic vertical portrait of one airship..."},
    {"label": "ENCHANTED CARRIAGE", "brief": "Gilded horse carriage in moonlit forest", "image_prompt": "Photorealistic vertical portrait of one magical horse carriage..."},
    {"label": "STARLIGHT CRUISER", "brief": "Futuristic spacecraft beside a ringed planet", "image_prompt": "Photorealistic vertical portrait of one spaceship..."}
  ]
}
```

Dieses JSON zeigt nur die Struktur. **Die Varianten des Beispielthemas sind bereits im Test verwendet worden und sollen nicht ungefragt als neue reguläre Reel-Idee wiederholt werden.**

Technische Grenzen: `topic` 8–92 Zeichen; `theme_category` 3–70 Zeichen und frei wählbar; genau fünf `variants`; jeweils `label` 3–36 Zeichen, `brief` 12–800 Zeichen, `image_prompt` möglichst konkret und nur zu EINEM Motiv. Prüfe nach dem Anlegen mit `src/creative_plan.py` oder dem dort beschriebenen Schema. Das Validieren einer JSON-Struktur ist keine subjektive Qualitätskontrolle.

## Verbindliche Bildprompts

Jeder Bildprompt muss nur EIN Motiv beschreiben. Nie „Bild 3 von 5“, „ähnlich wie die vorherigen“ oder Aufzählung der anderen vier Orte/Fahrzeuge. Ein eigenständiger 9:16-Quellbildprompt endet sinnvollerweise:

> One single continuous, full-frame vertical 9:16 photorealistic scene. No text, no typography, no logo, no labels, no split screen, no collage, no montage, no panels, no borders, no image grid, no watermark.

Keine aus Collagen ausgeschnittenen und hochskalierten Frames. Keine unbewiesene angeblich native 4K-Qualität. Höchste tatsächlich verfügbare native Hochformatauflösung anstreben, aber nicht behaupten, künstliche Hochskalierung mache echte Details.

## Reel-Design (ab Umstellung)

Nutze **das erfolgreiche Choose-Your-Ride-Muster** in `src/render.py`:
- fünf Einzelbilder, jeweils drei Sekunden, 15 Sekunden total;
- 1080x1920, 30 FPS, H.264 CRF17 und eingebettete bereits vorhandene lizenzierte Musik;
- oben eleganter gold/cremefarbener Serifentitel mit der *tatsächlichen* Themenfrage;
- unten eine dezent dunkle, goldkonturierte Variantenplakette: `01` bis `05` sowie die **individuelle Variantenbezeichnung** aus dem Kreativplan;
- **KEINE** fertig beschrifteten Bilder an das Rendering übergeben, keine Zahlen oder Überschriften durch image_gen einbrennen;
- Instagram-Safe-Areas beachten, das Quellmotiv vollflächig ohne Seitenstreifen;
- kein gesprochenes Roboter-Voiceover, keine notwendige manuelle Vorschau/Bestätigung.

## Veröffentlichungs- und Sicherheitsschranken

- Keine subjektive Bildbewertung oder blockierende Freigabe. Historische Theme-Wiederholung rechtzeitig durch kreative Neuwahl vermeiden, nicht einen technisch vollständigen Post aus ästhetischen Gründen abbrechen.
- Technische Fehler konkret melden (beschädigte/fehlende Quelldateien, fehlender Kreativplan bei neuen Slots, ungültige Dateien, Auth-/Netzwerkfehler); keine stillen Erfolge.
- Produktionsplan: 17.11.–14.12.2026 vier tägliche Posts (08:00, 12:30, 17:30, 21:30); ab 15.12.2026 zwei (12:30, 20:30), Europe/Berlin.
- Nur Dreamy Elsewhere, nicht Blinkpuzz, Vibsnaxx oder Professor Wheel. Beibehaltung des bestehenden geschützten GitHub/Drive/Buffer-Wegs.
