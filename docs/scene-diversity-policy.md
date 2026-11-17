# Dreamy Elsewhere — scene generation policy

Applies to every future five-image Reel. The topic is selected from config.json using the same offset and slot logic as src/render.py. This document governs IMAGE GENERATION, not rendering.

## Mandatory workflow
1. Derive the exact English topic from launch_date, day offset and slot.
2. Before generating images, define FIVE distinct scene briefs, each with its own **setting/geography, architectural type, camera viewpoint, primary focal object, lighting/weather treatment and composition**. Generate each image with a SEPARATE prompt, never five outputs from one shared prompt.
3. Every scene retains the same question/topic but must be an unmistakably different place. For rainy-night examples: forest log cabin; oceanfront modern glass house; urban penthouse; Scottish stone cottage; Japanese garden-facing ryokan. No more than one generic timber cabin/bedroom for that Reel.
4. Prompts must explicitly prohibit repeating the other four scenes' signature architecture and viewpoint. Favor broad variation in indoor/outdoor framing, close/wide shots, color temperature, materials and geography. For other topics, choose different relevant scene sets; do not reuse rainy-night locations mechanically.
5. Each output is one separate photorealistic full-bleed 9:16 portrait, no collage, captions, borders, people requirement or baked-in numbering. Use highest supported native portrait resolution, disclose actual dimensions.
6. Technical checks only: 5 distinct readable image files, valid dimensions, exact 9:16 crop and if necessary one Lanczos resize to 1080x1920. No subjective aesthetic scoring or approval gate.
7. Preserve existing src/render.py layout, 30fps H.264 CRF17 and licensed soundtrack handling. Never modify existing slots, manifests or publish to another account.
8. Check existing slot manifests before generating and reuse existing Drive files after partial failures. Only report upload, render and publishing statuses when actually verified.

## Prompt skeleton (one prompt per image)
"Photorealistic 9:16 portrait photograph, [EXACT TOPIC]. Scene [N] of a coherent five-location series: [UNIQUE GEOGRAPHY], [UNIQUE BUILDING/SPACE], [UNIQUE CAMERA POSITION AND LENS], [DISTINCT FOCAL POINT], [LIGHT AND WEATHER], [SPECIFIC MATERIALS]. This must NOT look like [other four scene archetypes]. Crisp realistic detail, plausible construction, full bleed. No text, no numbers, no collage, no frames, no bars."
