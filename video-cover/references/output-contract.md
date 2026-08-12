# Minimal JSONL output contract

Write the required output to `assets/video_cover_prompts.jsonl` in UTF-8. Each physical line is one platform cover. Do not use a surrounding array, header, comment, or multi-line JSON object.

## Exact row shape

Use exactly five fields—no more and no fewer:

```json
{"platform":"微信视频号竖版","size":"1080x1260","aspect_ratio":"6:7","core_prompt_points":["构图：真实人物场景与纲要信息严格50:50","人物场景：放大人物、脸或手及未完成动作，用动作演出标题隐喻","纲要信息：只用2至4个大型节点、一条关系和一个结论","风格：pearl_mist_midlife，珍珠雾白#F3F4F1及雨蓝、暖铜等语义色","标题与安全区：核心标题不超过两行，保留中心裁切","禁区：拒绝摆拍、无人物、密集图表、小字、硬分栏、乱码和平台标志"],"prompt":"超过700个非空白字符的完整中文封面图片提示词"}
```

## Field rules

- `platform`: use the canonical name from `platform-presets.md`; use a clear user-provided name for a custom platform.
- `size`: use ASCII `x`, for example `1920x1080`; do not use `×`, spaces, or nested width/height fields.
- `aspect_ratio`: use the preset value such as `16:9`, `6:7`, `9:16`, `3:4`, or `about 16:10`.
- `core_prompt_points`: use 4 to 8 concise strings. Collectively cover the strict 50:50 construction, concrete human-scene realism, title-linked active metaphor, low-density outline, selected style and background HEX, title/safe zone or crop survival, and important negative constraints.
- `prompt`: write one complete Chinese prompt longer than 700 non-whitespace characters. Include the exact size and ratio, a real human scene and outline information each occupying 50%, readable face or hands, a title-linked unfinished action, 2 to 4 large information nodes, one relationship, one conclusion, selected style background HEX, title area, safe zone/crop behavior, and negative constraints.

Do not add IDs, indexes, schema versions, topic summaries, audiences, title candidates, QA fields, nested canvas objects, separate palette objects, visual-element arrays, or a duplicate `text_free_prompt`. The full prompt is the executable source of truth; the core points are only its compact index.

## Canonical platform rows

| `platform` | `size` | `aspect_ratio` |
|---|---:|---:|
| 微信视频号竖版 | 1080x1260 | 6:7 |
| 微信视频号横版 | 1920x1080 | 16:9 |
| 今日头条横版 | 1920x1080 | 16:9 |
| B站横版 | 1920x1080 | 16:9 |
| B站旧式兼容 | 1146x717 | about 16:10 |
| 抖音竖屏 | 1080x1920 | 9:16 |
| 抖音主页封面 | 1080x1440 | 3:4 |
| 快手竖屏 | 1080x1920 | 9:16 |
| 小红书视频封面 | 1080x1440 | 3:4 |
| 西瓜视频横版 | 1920x1080 | 16:9 |
| YouTube横版 | 1280x720 | 16:9 |

## Cross-row rules

- Use one row per requested platform and canvas.
- Keep the title, visual thesis, absolute subject, primary style, and semantic color roles consistent inside each row's prompt.
- Redesign spatial composition, safe zone, crop behavior, and title placement for each ratio.
- Reject duplicate `platform` plus `size` pairs.
- Create a Markdown preview only when explicitly requested; JSONL remains the only source of truth.
