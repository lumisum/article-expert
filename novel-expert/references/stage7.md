# S7：小说多人有声版

S7可选。它把S4小说重组为与S5每张连环画对应的有声场景：自然旁白连接环境、动作和心理，苏美、凝香及实际开口的配角分别使用稳定音色，最后合并为每张图一个同编号MP3。它不是播客、访谈或轮流讲道理。

## 准入

完整读取`cast-bible.json`、`novel_blueprint.json`、`final_article.md`、`image_prompts.jsonl`以及S5、S6回执。创建`video/images/`、`video/audio/`、`video/narration_segments.jsonl`和`video/audio_manifest.json`。

说话者ID固定为：旁白`narrator`、苏美`sumei`、凝香`kaidi`，配角使用S1 ID的小写形式，如`C01`对应`c01`。不得新增蓝图之外的人物。

## 每图声音场景

- 每图一至六轮，按该幕真正需要的旁白和人物语言决定，不强求双主角轮流出现；
- 每轮一至三句，二十至一百四十个非空白字符；
- 同一人物不得连续三个轮次，除非中间是必要旁白；
- `performance_arc`说明声音、动作和关系怎样变化；
- `transition_in`和`transition_out`连接相邻画面；
- 不新增正文没有验证的事实、诊断、关系或普遍规律；
- 不使用“欢迎收听”“本期节目”“今天我们聊”等主持话术。

写入`video/narration_segments.jsonl`：

```json
{
  "id": "section_01",
  "order": 1,
  "image_prompt_id": "section_01",
  "section_title": "与S5一致",
  "image_meaning": "这张图真正讲什么",
  "visual_anchor": "本幕人物、动作和场景物件",
  "performance_arc": "本幕声音、动作和关系怎样变化",
  "transition_in": "怎样承接上一图",
  "transition_out": "怎样交给下一图",
  "turns": [
    {
      "turn_order": 1,
      "speaker_id": "narrator",
      "speaker_name": "旁白",
      "voice_direction": "克制、贴近人物的叙事声音",
      "facial_expression": "旁白写not_applicable；人物写表情与视线",
      "body_action": "旁白描述现场动作；人物写自己的动作和距离",
      "subtext": "没有直接说出的真正意思",
      "spoken_text": "一至三句实际朗读内容",
      "audio_file": "video/audio/section_01_01_narrator.mp3"
    },
    {
      "turn_order": 2,
      "speaker_id": "c01",
      "speaker_name": "配角姓名或稳定称谓",
      "voice_direction": "服从S1 speech_signature的同篇稳定表演",
      "facial_expression": "回应时的表情与视线",
      "body_action": "回应时的动作和距离变化",
      "subtext": "没有直接说出的真正意思",
      "spoken_text": "一至三句实际朗读内容",
      "audio_file": "video/audio/section_01_02_c01.mp3"
    }
  ],
  "merged_audio_file": "video/audio/section_01.mp3"
}
```

## 音色与合并

使用系统已有Edge TTS能力。苏美与凝香保持跨篇固定声音基线；旁白保持整篇一致；配角根据`gender_age`、关系与`speech_signature`选择同篇稳定音色。只为实际使用的`speaker_id`建立`voices`条目。

```json
{
  "tts_engine": "edge_tts",
  "voices": {
    "narrator": {
      "name": "实际旁白音色",
      "rate": "实际语速",
      "volume": "实际音量",
      "pitch": "实际音高"
    },
    "c01": {
      "name": "实际配角音色",
      "rate": "实际语速",
      "volume": "实际音量",
      "pitch": "实际音高"
    }
  },
  "segments": [
    {
      "id": "section_01",
      "image_prompt_id": "section_01",
      "merged_audio_file": "video/audio/section_01.mp3",
      "status": "success",
      "duration_seconds": 38.2,
      "turns": [
        {
          "turn_order": 1,
          "speaker_id": "narrator",
          "audio_file": "video/audio/section_01_01_narrator.mp3",
          "duration_seconds": 15.4
        }
      ]
    }
  ],
  "total_duration_seconds": 228.7
}
```

运行`python skills/novel-expert/scripts/validate_stage.py --stage 7 --topic-dir /absolute/topic/path`。通过后向用户列出`video/images/`期待的图片ID。逐轮音频保留为同篇角色声音资产，最终视频仍使用每图一个`section_XX.mp3`。
