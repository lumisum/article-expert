# Platform canvas presets

These are production working canvases, not promises that every platform surface always renders the full asset. Platform apps change upload limits, grid crops, recommendation cards, and UI overlays. Prefer a user-provided current specification; otherwise use these presets and verify the live publisher before final export.

Last reviewed: 2026-08-09.

## Preset table

| Preset ID | Platform and surface | Canvas | Ratio | Layout default | Critical safe zone |
|---|---|---:|---:|---|---|
| `wechat_channels_portrait` | 微信视频号竖版/主页兼容 | 1080×1260 | 6:7 | upper human scene 50%, lower outline info 50% | center 80% width × 78% height; keep title and face away from top/bottom 11% |
| `wechat_channels_landscape` | 微信视频号横版 | 1920×1080 | 16:9 | left human scene 50%, right outline info 50% | center 76% width × 78% height; make the 6:7 center crop understandable |
| `toutiao_landscape` | 今日头条横版视频 | 1920×1080 | 16:9 | left human scene 50%, right outline info 50% | center 82% width × 78% height; reserve edge space for card crops |
| `bilibili_landscape` | B站普通横版视频 | 1920×1080 | 16:9 | left human scene 50%, right outline info 50% | center 82% width × 80% height; keep title within two lines |
| `bilibili_legacy_16_10` | B站旧式/兼容封面画布 | 1146×717 | about 16:10 | left human scene 50%, right outline info 50% | center 82% width × 80% height; check 16:9 crop survival |
| `douyin_portrait` | 抖音竖屏视频 | 1080×1920 | 9:16 | upper human scene 50%, lower outline info 50% | center 82% width; avoid top 12%, bottom 20%, and right 12% UI risk |
| `douyin_grid_cover` | 抖音主页封面导出 | 1080×1440 | 3:4 | upper human scene 50%, lower outline info 50% | center 82% width × 80% height; preserve center square/grid crop |
| `kuaishou_portrait` | 快手竖屏视频 | 1080×1920 | 9:16 | upper human scene 50%, lower outline info 50% | center 82% width; avoid top 12%, bottom 20%, and right 12% UI risk |
| `xiaohongshu_portrait` | 小红书视频/笔记封面 | 1080×1440 | 3:4 | upper human scene 50%, lower outline info 50% | center 84% width × 82% height; keep face and title in upper-middle core |
| `xigua_landscape` | 西瓜视频横版 | 1920×1080 | 16:9 | left human scene 50%, right outline info 50% | center 82% width × 78% height |
| `youtube_landscape` | YouTube thumbnail | 1280×720 | 16:9 | left human scene 50%, right outline info 50% | center 86% width × 82% height; use very short text |
| `custom` | 用户指定平台或画布 | user supplied | user supplied | choose by orientation | record explicit safe zone and override source |

## Evidence and confidence notes

- Today Toutiao's creator help encourages landscape video ratios including 16:9, 18:9, and 21:9; this skill uses 1920×1080 as a practical high-resolution 16:9 canvas: <https://baike.toutiao.com/detail/211/212/217>.
- A WeChat Channels industry guide documents 1080×1260 for portrait and 1080×608 for landscape, while noting that landscape content may be adjusted to a 6:7 homepage view: <https://static.marketup.cn/resource/marketup/www/0a627663eddf45d3b120d7532b03c716.pdf>. Use 1920×1080 as the higher-resolution landscape working canvas while protecting the central 6:7 crop.
- A Bilibili-hosted creator tutorial records the older 1146×717 cover canvas: <https://www.bilibili.com/video/BV1bh411o7Y8/>. Because contemporary cards commonly use 16:9, keep both the 16:9 primary preset and the 16:10 compatibility preset, then inspect the live upload preview.

These notes explain the preset choices; they do not override a current uploader's displayed requirement.

## Adaptation rules

### Landscape

- Place the enlarged realistic human scene in the left 50% and the low-density white micro-3D outline in the right 50%.
- Keep a 10% to 15% blended center region, never a vertical divider.
- Put headline text in the sparse information side or central safe zone without covering the subject or shared anchor.
- Make the center crop retain the subject identity, one conflict cue, and the headline's essential words.

### Portrait

- Place the enlarged realistic human scene in the upper 50% and the low-density white micro-3D outline in the lower 50%.
- Keep a 10% to 15% blended transition where the shared anchor descends, unfolds, or transforms.
- Place the headline in the upper-middle or information-layer safe zone, not against UI-risk edges.
- Preserve the face or recognizable object, the title keyword, and one explanatory result in center square and 3:4 crops.

### One master across platforms

- Keep the thesis, subject identity, shared anchor, semantic color roles, and headline keywords constant.
- Redesign spatial relationships per ratio; do not stretch or blindly crop.
- Allow edge details and secondary labels to disappear.
- Never allow the subject face, product identity, conflict evidence, or core headline words to depend on the outer 10% to 20%.
