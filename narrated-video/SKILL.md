---
name: narrated-video
description: 将一个标准video目录中的编号图片和逐段旁白音频直接合成为专业3:4纵向MP4视频。适用于tech-article、midlife-article和businvet-article的视频素材交接、静态图片展示、图片切换转场，以及生成时间轴和合成报告。
---

# narrated-video

用户只提供一个`video/`目录。本技能按旁白清单匹配图片和音频，以音频真实时长建立时间轴，生成3:4纵向成片。

开始前必须完整读取`references/input_contract.md`。

## 标准输入

`tech-article`、`midlife-article`和`businvet-article`的S7会准备除图片外的全部素材：

```text
[topic]/video/
├── narration_segments.jsonl
├── audio_manifest.json
├── images/                       # 用户只在这里放入同编号图片
│   ├── section_01.png
│   └── section_02.png
└── audio/
    ├── section_01.mp3
    └── section_02.mp3
```

图片可以使用`1`、`2`、`3`等阿拉伯数字，也可以使用旁白ID，如`section_01`。脚本根据ID尾部数字匹配两种命名；同一编号出现多个候选时必须停止，不能任意选取。

## 工作流

1. 读取`narration_segments.jsonl`，按`order`确定顺序；
2. 从`images/`和`audio/`匹配同编号素材；
3. 检查图片像素尺寸、宽高比和放大风险；
4. 使用`ffprobe`读取每段音频真实时长；
5. 将每张3:4图片完整放入同画幅纵向画布，当前音频播放期间画面保持静止；
6. 相邻图片之间使用约0.6秒交叉淡化，只改变画面，不重叠、不截断旁白；
7. 由FFmpeg合成H.264/AAC视频；
8. 在同一个`video/`目录输出MP4、时间轴和构建报告；
9. 验证分辨率、音视频流、总时长、片段数量和图片画质风险。

## 画面原则

- 默认输出`1080×1440`、`3:4`纵向视频；
- 单张图片在本段旁白期间不平移、不滚动、不缩放、不漂浮；
- 图片不拉伸、不强裁切，上方场景与下方信息图完整可见；
- 比例不足时使用克制的中性留白补齐，不制造虚化运动背景；
- 3:4图片建议不低于`1080×1440`；常见`1024×1365`只需轻微缩放；
- 需要放大时使用Lanczos高质量缩放和轻量锐化，但不能凭空恢复细节；
- 放大超过1.5倍属于明显风险，应优先对原图做AI超分；
- 含中文、数字、代码或信息结构的图片在超分后必须人工复核；
- 转场只使用克制的交叉淡化，不使用推拉、炫光、旋转或无关特效；
- 中间文件只写入临时目录，素材目录保持清楚。

## 执行

```bash
python skills/narrated-video/scripts/build_narrated_video.py \
  /absolute/topic/path/video
```

常用可选参数：

```bash
--output /absolute/path/to/final_video.mp4
--width 1080
--height 1440
--transition-duration 0.6
--image-quality-policy strict
--overwrite
```

默认`best-effort`模式会完成合成，并把每张图的原始尺寸、放大倍数和风险写入报告。发布级成片建议使用`strict`；任何图片需要放大超过1.5倍时先停止并处理原图。

输出写回用户提供的`video/`目录：

```text
final_video.mp4
video_timeline.json
video_build_report.json
```

## 完成定义

只有以下条件全部满足才可宣布完成：

- 图片、音频和旁白数量一致，编号连续、无重复、无歧义；
- 每张图片与同编号旁白、音频表达同一段内容；
- 每张图片的原始尺寸、放大倍数和画质等级已记录；
- 每段静态画面持续到对应音频结束，成片总时长与音频总时长基本一致；
- 相邻画面完成交叉淡化，旁白连续且不被转场截断；
- MP4包含H.264视频流与AAC音频流，分辨率和时长通过检测；
- 时间轴和构建报告均已写入输入目录。
