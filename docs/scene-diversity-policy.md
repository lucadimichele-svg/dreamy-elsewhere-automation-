## Korrektur: Kernmotiv zählt, nicht die exakte Kulisse (20.11.2026)

Ein dokumentierter Ausfall am 20.11.2026 S2: Bei `Which enchanted door would you open?` wurden erzeugte, klar sichtbare Türen abgelehnt, weil die Kulisse Wald/Wüste statt des geplanten Unterwassertempels war. Das war zu streng. **Künftig gelten ausschließlich das gemeinsame `core_subject` und seine tatsächliche Präsenz als Hauptmotiv als harte inhaltliche Pflicht.** Eine erkennbare Tür ist beim Türen-Reel gültig, auch wenn ihre Material- oder Ortsbeschreibung von `must_show` abweicht. Dasselbe gilt für Brücken, Desserts, Fahrzeuge usw. Die übrigen Promptdetails dienen als kreative Zielvorgabe und nicht als Abbruchgrund.

Wenn das echte Bild den Kerngegenstand korrekt zeigt, aber die konkrete Variante nicht: **Vor dem Drive-Manifest das Variantenlabel und die Bildbeschreibung passend zur tatsächlichen Aufnahme anpassen** (`CORAL GATE` wird bei deutlich sichtbarer Wald-Tür bspw. `ENCHANTED FOREST GATE`). Kreativplan, fünf Label-Audits und Renderer bleiben dadurch konsistent. Nicht künstlich behaupten, eine Bronzetür in einem Unterwassertempel zu zeigen, wenn es real eine Waldtür ist. Niemals wegen eines unterschiedlichen Hintergrunds die gesamte Produktion stoppen. Eine Szene, die gar keine erkennbare Tür zeigt, bleibt dagegen eindeutig falsch und wird durch einen neuen isolierten Kernobjekt-Prompt ersetzt. Technische Probleme wie Collagen und nicht echte Einzelbilder bleiben verboten. Ästhetische KI-Bewertungen bleiben vollständig abgeschaltet.

---
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

## Schutz gegen themenfremde Generatorbilder (ab 20.11.2026 S2)

**Reales Problem belegt:** Das Reel `2026-11-19_S4` plante fünf Brücken. In den tatsächlichen Drive-Originalen zeigt nur `01.png` eindeutig die geplante Glasbrücke. `02.png` ist ein Höhlenbecken mit Wasserfall statt Lava-Brücke, `03.png` eine verzierte Terrasse mit einer entfernten Brücke statt fokussierter Lotus-Brücke, `04.png` eine nächtliche Aussichtsterrasse statt futuristischer Sky-Rail-Brücke, `05.png` eine antike Theater-/Ruinenlandschaft statt lebender Wurzelbrücke. Alle Dateien waren gültig und verschieden; diese Art **Inhaltsfehler** wurde bislang unbemerkt publiziert.

**Das ist kein Geschmackstest:** Ein Reel über fünf Brücken darf nicht aus fünf zufälligen hübschen Orten bestehen. Der im Plan definierte Gegenstand muss in jedem einzelnen Quellbild **tatsächlich als Hauptmotiv sichtbar** sein. Nicht: "schön genug?", "passt mir die Stimmung?", "künstlerisch gut?" Sondern allein: **"Zeigt das Bild eindeutig die angekündigte Sache?"**

### Neues Kreativplan-Format für neue Slots ab 2026-11-20 S2

Ergänze in `assets/creative_plans/YYYY-MM-DD_Sx.json`:
- `core_subject`: Ein frei gewählter, konkret sichtbarer gemeinsamer Gegenstand, zum Beispiel `bridge`, `dessert`, `book-filled library`, `flying vehicle`. Der Gegenstand darf NICHT bloß eine Stimmung oder Umgebung sein.
- Bei **jeder** der genau fünf Varianten `must_show`: ein konkreter, beobachtbarer Satz zum Hauptobjekt, z.B. `A long black basalt stone bridge spans the glowing lava channel; bridge deck and both endpoints visible`. `image_prompt` muss dieses Hauptobjekt nachweisbar ausdrücklich erwähnen.

### Zwingende objektbezogene Bilderzeugung

1. Den geplanten **`must_show`-Gegenstand an den ANFANG** jedes isolierten Einzelbild-Prompts stellen. Nicht zuerst Wald, Blumen, Lounge, Wolken, Palast, Bett, Materialästhetik oder dekorative Aussicht beschreiben.
2. **Bilddominanz:** Der Gegenstand muss zentral, groß und gut erkennbar sein. Aus einem Brücken-Plan darf nicht bloß eine Terrasse werden, von der aus weit entfernt eine winzige Brücke sichtbar ist. Schreibe konkrete Blickrichtung und Rahmen, z.B. `The bridge itself is the unmistakable main subject, spanning the center of the portrait composition, both ends clearly visible.` Entsprechend bei Dessert, Fahrzeug, Bibliothek usw.
3. Vor weiterer Produktion **JEDES generierte Originalbild anschauen** und ausschließlich den dargestellten Hauptgegenstand mit dem geplanten `must_show` abgleichen. Technisch gültige, aber themenfremde Bilder als inhaltlichen Fehlschlag ansehen. **Keinerlei ästhetischen Scorer, Geschmacksurteil oder allgemeine KI-Freigabeschleife**.
4. Bei Nichtübereinstimmung maximal **zwei** isolierte Nachversuche nur für dieses Bild, dabei den Prompt kürzer und objektzentrierter machen; keine Referenzen auf vorige Bildausgaben, kein Bearbeiten oder Ausschneiden vorheriger Bilder, keine Collagen. Falls weiterhin kein objektkorrektes Original entsteht, **keinen irreführenden themenfremden Reel veröffentlichen**. Den tatsächlichen technischen Produktionsausfall melden und andere Slots nicht verändern. Diese Inhaltsprüfung ist eine harte Einschränkung nur für nachweislich falsch abgebildete Themengegenstände und ersetzt **nicht** die verbotene subjektive KI-Qualitätsbewertung.
5. Für jedes tatsächlich visuell geprüfte, richtige Quellbild eine kurze wahrheitsgetreue `observed_subject`-Beschreibung verfassen, `subject_visible: true` und `subject_dominant: true` setzen und den **SHA256 des endgültig zum Drive hochgeladenen PNG-Byteinhalts** berechnen. Keine sichtbare Präsenz behaupten, wenn der Gegenstand nur im Prompt vorkommt.

### Neues Audit-JSON (vor Upload-Manifest committen)

`assets/scene_audits/YYYY-MM-DD_Sx.json`:

```json
{
  "date": "2026-11-20",
  "slot": "S2",
  "topic": "Which extraordinary bridge would you cross?",
  "core_subject": "bridge",
  "files": [
    {
      "name": "01.png",
      "label": "THE GLASS ABYSS",
      "must_show": "Transparent glass bridge spanning a canyon as the central main subject",
      "sha256": "64-hex-stellen-durch-reale-berechnete-dateipruefsumme-ersetzen",
      "subject_visible": true,
      "subject_dominant": true,
      "observed_subject": "A long glass suspension bridge is clearly visible from its near end across the canyon"
    }
  ]
}
```

Das Muster zeigt **nur die Struktur**; tatsächlich sind **genau fünf** Einträge nötig und die SHA256-Werte müssen aus den echten Originaldateien stammen. Das `must_show` muss exakt mit dem jeweiligen Kreativplan übereinstimmen, `label` ebenfalls. Audit-Commit **vor** `assets/drive_manifests/KEY.json`, damit der Renderer-Pipeline schon ein Audit vorliegt. Die Import-Pipeline `src/private_drive_import.py` prüft, ob das Audit genau zum Plan passt, und vergleicht die SHA256 gegen die **wirklich von Drive importierten** PNG-Bytes. Bei Abweichung wird nicht gerendert. Dadurch wird ein falsch zugeordnetes oder nachträglich geändertes Bild nicht unbemerkt veröffentlicht.

**Ehrliche Grenze:** Die maschinelle SHA-/JSON-Prüfung kann nicht beurteilen, ob im Bild wirklich eine Brücke zu sehen ist. Die eigentliche Sichtprüfung geschieht durch den Bildproduktionsagenten beim Betrachten jedes echten Bildes, nicht allein anhand der schriftlichen Prompts oder Labels. Diese Prüfung ist zwingend, aber nicht unfehlbar. Keine Erfolgsbehauptung bei nicht tatsächlich durchgeführter Sichtprüfung.

Die bestehenden bis einschließlich `2026-11-20_S1` produzierten oder bereits veröffentlichten Reels bleiben von dieser zusätzlichen Schranke unberührt. Nichts nachträglich löschen, ersetzen oder doppelt publizieren, ohne dass der Nutzer es verlangt.
