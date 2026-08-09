---
name: video-cover
description: Generate a JSONL file of high-context Chinese video-cover image prompts and text-overlay plans for WeChat Channels, Toutiao, Bilibili, Douyin, Kuaishou, Xiaohongshu, Xigua Video, YouTube, and custom canvases. Use when Codex needs to design, adapt, or batch-produce video thumbnail or cover prompts across landscape, portrait, and multi-platform sizes while reusing the midlife, technology, or business scene-to-white-micro-3D visual styles from this repository. Generate prompts and specifications only; do not generate the image unless the user separately asks for image generation.
---

# Video Cover Prompt Generation

Turn a video topic, script, transcript, article, or title into platform-ready cover prompts. Reuse the three source families without flattening their domain differences: life-story empathy, technical mechanism, and business value relationships.

## Required references

Read these files before drafting:

1. Read [references/style-profiles.md](references/style-profiles.md) to select and execute a visual family.
2. Read [references/platform-presets.md](references/platform-presets.md) for every requested platform and canvas.
3. Read [references/output-contract.md](references/output-contract.md) before writing the deliverables.

If a user supplies a current platform upload specification, prefer it over the bundled working preset and record the override. Treat platform dimensions as revisable product behavior, not timeless facts.

## Workflow

### 1. Establish the cover contract

Extract or infer only what the source supports:

- video topic and one-sentence thesis;
- target viewer and the familiar object, situation, or problem they recognize;
- conflict, unanswered question, or visible stakes;
- concrete payoff the video actually delivers;
- named products, people, interfaces, numbers, and claims that may appear;
- requested platforms, orientations, and title wording.

Never invent a metric, quote, result, product UI, or emotional event to strengthen click appeal. When the title is absent, create three to five candidates, compare recognition, tension, payoff clarity, fidelity, thumbnail readability, and non-misleadingness, then select one.

### 2. Select one style family

Choose exactly one primary family per cover set:

- `pearl_mist_midlife` for life choices, relationships, wellbeing, personal experience, and reflective stories;
- `cool_porcelain_tech` for tools, code, devices, workflows, mechanisms, and troubleshooting;
- `capital_paper_business` for companies, products, customers, cost, profit, competition, industry structure, and capital expectations.

Do not mix palettes merely for variety. If the subject genuinely crosses domains, choose the family that expresses the video's promised payoff, then borrow at most one semantic device from another family without borrowing its palette.

### 3. Build one visual thesis

Make the cover communicate one idea at thumbnail size:

`recognizable subject + unresolved action or conflict + visible explanatory payoff`

Use the shared `scene_to_white_micro_3d` backbone:

- devote 60% of the canvas to a large, realistic, recognizable scene captured as a credible moment rather than a staged poster;
- devote only 40% of the canvas to a low-density white-material micro-3D outline that summarizes the video's single key relationship;
- transform a shared person, object, path, interface, product, or action into that concise outline structure;
- preserve color, lighting, perspective, material, and subject continuity through a soft 10% to 15% transition zone;
- keep one absolute subject, one relationship, and one visible result;
- use colored accents for meaning, not decoration;
- reject split-screen collage, generic icon clouds, empty atmosphere, and flat presentation diagrams.

For landscape canvases, use a strict 60:40 left-scene/right-information composition. For portrait canvases, use a strict 60:40 upper-scene/lower-information composition. A diagonal or depth-based transition is acceptable only when the scene still owns about 60% of the visual weight and the shared anchor remains obvious.

Treat the information layer as an outline, not a full explanation. Use two to four information nodes, zero to three short labels, one relationship, and one conclusion. Do not reproduce the video's complete causal chain, architecture, timeline, value model, or argument on the cover.

### 4. Design the master before variants

Create one `master_concept` independent of pixel size. Place the subject, headline keywords, shared anchor, information structure, and semantic colors before adapting crops.

For every platform variant:

- use the exact preset canvas or a recorded user override;
- redesign the composition for that aspect ratio instead of merely saying “crop”;
- place all irreplaceable content inside the preset safe zone;
- keep faces, product identities, conflict evidence, and headline keywords out of UI-risk edges;
- state what survives center crop, grid crop, and small-card display;
- keep the first-read title to one or two short lines; move nuance into an optional subtitle;
- run a one-second read and thumbnail test.

Do not claim one canvas is universally optimal across all surfaces of a platform. When one asset must serve multiple surfaces, prioritize semantic survival over edge decoration.

### 5. Write executable prompts

Write one independent Chinese prompt per variant with more than 700 non-whitespace characters, normally 900 to 1200. Every prompt must specify:

- exact pixel dimensions and aspect ratio;
- platform use case and safe-zone behavior;
- a verifiably realistic scene, subject geometry, active gesture, conflict, environmental traces, and visible payoff;
- the strict 60% scene / 40% outline-information proportion and the shared anchor;
- transition of color, light, perspective, and material;
- foreground, middle ground, background, camera, focus, and visual path;
- surfaces, thickness, bevels, seams, translucency, shadows, and micro-details;
- the selected palette with exact HEX values and semantic roles;
- headline placement, line count, hierarchy, contrast, and crop survival;
- two to four information nodes and zero to three short Chinese labels only when they improve comprehension;
- explicit negative constraints tied to likely failure modes.

When a generator renders Chinese unreliably, make the complete prompt reserve a clean title area that can receive text in post-production. Do not add a second near-duplicate prompt field. Do not put pseudo-Chinese, random English, watermarks, platform logos, or QR codes into the image.

### 6. Deliver one JSONL source of truth

Write `assets/video_cover_prompts.jsonl` as the required core output. Write exactly one JSON object per requested platform and canvas, one physical line per object, in the requested platform order.

Keep every row deliberately small and use exactly these five fields:

- `platform`: canonical platform and surface name;
- `size`: pixel dimensions in `WIDTHxHEIGHT` form;
- `aspect_ratio`: display ratio;
- `core_prompt_points`: four to eight concise strings covering composition, scene realism, outline information, style, title/safe zone, crop survival, or negative constraints;
- `prompt`: the single complete, independently executable Chinese cover-image prompt.

Do not repeat topic analysis, title candidates, audience, QA, palette objects, element arrays, identifiers, schema versions, or a second text-free prompt in every row. Put the necessary result of those decisions into `core_prompt_points` and `prompt` instead.

Do not wrap the rows in a JSON array or parent object. Do not write a separate JSON package. Create `video_cover_prompts.md` only when the user explicitly asks for a readable preview; it is never the source of truth.

Validate the JSONL file:

```bash
python3 scripts/validate_cover_prompts.py path/to/assets/video_cover_prompts.jsonl
```

Fix every error before handoff. Mention that platform presets are working canvases and recommend checking the live publisher when upload requirements matter.

## Boundaries

- Generate prompts and layout specifications only by default.
- If the user asks to create actual covers, invoke the appropriate image-generation workflow after producing the validated prompt package.
- Do not use copyrighted logos, celebrity likenesses, or unlicensed source imagery unless the user has the rights and explicitly requests them.
- Avoid misleading before/after claims, fake screenshots, fabricated earnings, investment promises, medical certainty, fear manipulation, sexualized subjects, and illegible text density.
