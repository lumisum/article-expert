# S7：逐图旁白与语音

S7可选。它为S5的每一张正文配图生成一段贴图旁白，并调用系统已有的Edge TTS能力生成同编号MP3。S7不生成图片，也不合成视频。

## 准入与目录

开始前完整读取：

- `references/author.md`
- `article/final_article.md`
- `assets/image_prompts.jsonl`
- `assets/title_cover_package.json`
- S5和S6回执

先创建：

```text
video/
├── images/                  # 留空，用户稍后放入同编号图片
├── audio/
├── narration_segments.jsonl
└── audio_manifest.json
```

旁白行数必须与S5正文配图数完全一致。图片、旁白和音频共享同一个S5 `image_id`；用户唯一需要手工完成的动作，是把生成好的图片以该ID命名后放入`video/images/`。

## 整组视频怎样成立

整组旁白必须独立讲清一个中年人生问题，不是把文章按章节缩写后朗读：

1. 第一段从一个熟悉的人、动作或生活瞬间进入，迅速点明这件小事为什么值得停下来；
2. 中间各段沿文章已经验证的因果链继续下潜，上一张图留下的疑问成为下一张图的入口；
3. 每段都让上方人物场景与下方白色微3D信息结构共同参与讲述，把生活里的果带向更深一层的因；
4. 哲学只在它能照亮当前选择时自然出现，不能朗诵名言或讲成知识课；
5. 最后一段完成选择、边界或余味的收束，需要导流时只自然提示文章中有更完整的故事与推演。

旁白同样采用“下潜后回升”的情绪曲线。前中段可以沉重，但不能连续煽动恐惧；最后几段要从最低点自然转向清醒、支点和行动，让观众在承认现实之后恢复信心，而不是突然换成励志语气。

视频应当不看文章也能听懂，文章也不依赖视频才能成立。

## 每段旁白

每张图对应五至六个完整中文句子。句数是主要长度标准，不为了凑字数拆短句，也不把多个独立意思用逗号硬塞成一句。

- 先抓住画面上方真实场景中的人、动作、关系或情绪变化；
- 再沿共同主体与视觉桥梁进入下方信息层，讲清因果、时间、选择或代价；
- 说话像一个经历过、想明白一些事情的人陪对方慢慢看，不像课程、鸡汤、朗诵或TTS说明；
- 立场清楚，心态平和，允许自然停顿、转折和少量语气词；
- 语言直白、有生活质感和余味，不堆理论名称、网络黑话、技术隐喻或固定金句；
- 不反复说“看这张图”，不描述无关的颜色、材质和装饰；
- 不新增文章没有验证的医学结论、普遍规律或人物事实。

## 段间连续性

- 除第一段外，每段开头必须接住上一段的结果、疑问、情绪或未完成的选择；
- 除最后一段外，每段结尾必须自然留下下一张图将继续追问的具体原因或现实后果；
- 不使用“接下来我们看”“下面进入下一部分”这类空过渡；
- 不在换图时重新介绍主题、复述标题或重复观看收益；
- 相邻两段连读时，人物指代、时间、关系与因果方向必须连续；
- 先设计`transition_in`和`transition_out`，再把它们自然写进旁白；这两个字段不单独朗读。

## 旁白协议

写入`video/narration_segments.jsonl`，每行一张图：

```json
{
  "id": "section_01",
  "order": 1,
  "image_prompt_id": "section_01",
  "section_title": "与S5完全一致的章节标题",
  "image_meaning": "这张图要让观众真正理解的人生含义",
  "visual_anchor": "旁白所指向的人物动作、生活物件和信息结构",
  "narration_goal": "听完本段后观众获得的判断或选择",
  "transition_in": "怎样承接上一段；第一段说明怎样开场",
  "transition_out": "怎样交给下一段；最后一段说明怎样收束",
  "narration": "五至六个完整中文句子的可直接朗读旁白",
  "audio_file": "video/audio/section_01.mp3"
}
```

要求：

- 行数、顺序、`id`、`image_prompt_id`和`section_title`与S5严格对应；
- `narration`只含实际朗读内容，不写Markdown、舞台提示、镜头指令、时间码或字段说明；
- 全部写完后从第一段连续朗读到最后一段，修复重复开场、对象跳变、因果断裂和机械过渡。

## Edge TTS

按编号串行调用系统已有的Edge TTS能力：

```text
video/audio/section_01.mp3
video/audio/section_02.mp3
```

- 使用用户指定或系统已配置的中文音色，不在技能中写死音色；
- 同一视频保持同一音色、语速、音量和音高；
- 每次只提交当前`narration`，当前段成功后才进入下一段；
- 失败只重试当前编号，不能跳号、重号或覆盖其它段；
- 每个MP3必须可读取且有实际时长。

## 音频清单

写入`video/audio_manifest.json`：

```json
{
  "tts_engine": "edge_tts",
  "voice": "实际使用的中文音色",
  "rate": "实际语速",
  "volume": "实际音量",
  "pitch": "实际音高",
  "segments": [
    {
      "id": "section_01",
      "image_prompt_id": "section_01",
      "audio_file": "video/audio/section_01.mp3",
      "status": "success",
      "duration_seconds": 38.2
    }
  ],
  "total_duration_seconds": 228.7
}
```

时长使用实际音频时长。清单顺序必须与S5图片顺序一致。

## 完成与交接

运行：

`python skills/midlife-article/scripts/validate_stage.py --stage 7 --topic-dir /absolute/topic/path`

通过后，向用户明确列出`video/images/`所期待的图片ID。用户把同编号PNG、JPG、JPEG或WEBP放入该目录后，可直接把整个`video/`目录交给`narrated-video`：

`python skills/narrated-video/scripts/build_narrated_video.py /absolute/topic/path/video`
