# 输入与输出协议

## 标准目录

用户只提供一个绝对`video/`目录：

```text
[topic]/video/
├── narration_segments.jsonl
├── audio_manifest.json
├── images/
│   ├── section_01.png
│   └── section_02.png
└── audio/
    ├── section_01.mp3
    └── section_02.mp3
```

三个文章技能的S7负责生成旁白、MP3和音频清单，并预留空的`images/`。用户唯一需要手工完成的动作，是把生成好的正文图片放入`images/`并保持编号对应。

调用：

```bash
python skills/narrated-video/scripts/build_narrated_video.py \
  /absolute/topic/path/video
```

成片和附属文件写回该`video/`目录。

## 旁白JSONL

每行一个片段对象，至少包含：

```json
{
  "id": "section_01",
  "order": 1,
  "narration": "送入语音合成的完整旁白",
  "audio_file": "video/audio/section_01.mp3"
}
```

规则：

- `id`只能包含字母、数字、下划线和短横线；
- `order`从1开始连续递增，JSONL行序与其一致；
- `narration`必须与音频实际朗读内容一致；
- 路径既可相对于主题目录写成`video/audio/...`，也可相对于当前`video/`目录写成`audio/...`，脚本会安全解析；
- `section_01`、`1`、`01`和`001`可按尾部数字匹配；
- 同一编号找到多个图片或音频时视为歧义，必须停止；
- 正式文章流水线必须保留JSONL，不以文件名猜测代替明确清单。

## 图片

支持PNG、JPG、JPEG和WEBP。图片统一放入`images/`。

- 优先使用与`id`完全相同的文件名，如`section_01.png`；
- 也允许使用相同尾部编号，如`1.png`；
- 默认画布为`1080×1440`；
- 当前片段内图片完全静止，不平移、不滚动、不缩放、不漂浮；
- 图片完整适配画布，不拉伸、不强裁切；
- 非3:4图片以中性留白补齐，不使用会干扰信息阅读的动态背景；
- 源图建议达到`1080×1440`，放大超过1.5倍应先处理原图；
- 对含中文、数字、代码和信息结构的图片，超分后必须逐字复核。

## 音频

支持MP3、M4A、WAV和AAC。音频放入`audio/`，真实时长必须由`ffprobe`读取。画面切换点和总片长以音频实际时长为准，不使用清单中的预计时长替代测量。

## 转场

默认在音频边界前约0.6秒开始交叉淡化到下一张图。下一段旁白仍从真实音频边界开始，因此视觉转场不会造成音频重叠、缺字或提前切断。

单张图片内部没有动画。片段过短时自动缩短交叉淡化时间，防止转场占据主要内容。

## 输出

所有正式产物写回用户提供的`video/`目录：

- `final_video.mp4`：3:4纵向成片；
- `video_timeline.json`：每段图片、音频、起止时间和转场信息；
- `video_build_report.json`：输入数量、画布、帧率、静态画面策略、编码、总时长和验收结果。
