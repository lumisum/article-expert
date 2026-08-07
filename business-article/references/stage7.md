# S7：逐图旁白与语音

S7可选。它为S5的每一张正文配图生成一段贴图旁白，并调用系统已有的Edge TTS能力生成同编号MP3。S7不生成图片，也不合成视频。

## 准入与目录

开始前完整读取：

- `references/author.md`
- `references/business_depth.md`
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

整组旁白必须独立讲清一个商业问题，而不是压缩文章或复述科技新闻：

1. 第一段从熟悉的公司动作、产品场景或反常业务结果进入，迅速说明这件事为什么与钱、客户或行业位置有关；
2. 中间各段承接上一张图留下的问题，沿客户价值、付费、收入、成本、利润、现金、竞争和资本预期逐步推进；
3. 每段只讲当前图片最适合讲透的一层关系，上方真实业务场景与下方白色微3D信息结构共同参与解释；
4. 必须分清技术价值、客户价值与公司能捕获的价值，不把融资、订单、用户或估值直接说成利润；
5. 最后一段完成验证信号、反方路径或观察边界的收束，不给买卖建议；需要导流时只自然提示文章中有更完整的证据与推演。

视频应当不看文章也能听懂，文章也不依赖视频才能成立。

## 每段旁白

每张图对应五至六个完整中文句子。句数是主要长度标准，不为了凑字数拆短句，也不把多个独立判断用逗号硬塞成一句。

- 从画面上方的产品、客户、交易、产线或产业现场切入；
- 沿共享主体进入下方信息层，用口语讲清一条价值流、因果链、利润关系或判断信号；
- 像真正研究过这门生意的人在和朋友拆账，观点明确、心态平和，不像财经播报、路演、研报摘要或投资推荐；
- 网络感来自真实商业反差和清楚判断，不靠堆热词、固定段子或粗俗表达；
- 只保留理解商业结果所必需的技术细节；
- 数字必须与文章已验证的口径一致，不新增预测、收益承诺或确定性结论；
- 不反复说“看这张图”，不逐项朗读标签，也不描述无关的颜色与材质。

## 段间连续性

- 除第一段外，每段开头必须接住上一段的结果、疑问或尚未解释的经济后果；
- 除最后一段外，每段结尾必须自然留下下一张图要继续追问的客户行为、成本、利润或竞争问题；
- 不使用“接下来我们看”“下面进入下一部分”这类空过渡；
- 不在换图时重讲主题、复述标题或重复观看收益；
- 相邻段的人物、公司、业务对象、时间和因果方向必须连续；
- 先设计`transition_in`和`transition_out`，再把它们自然写进旁白；这两个字段不单独朗读。

## 旁白协议

写入`video/narration_segments.jsonl`，每行一张图：

```json
{
  "id": "section_01",
  "order": 1,
  "image_prompt_id": "section_01",
  "section_title": "与S5完全一致的章节标题",
  "image_meaning": "这张图要让观众理解的一层商业关系",
  "visual_anchor": "旁白所指向的业务对象、共享主体和信息结构",
  "narration_goal": "听完本段后观众获得的判断能力",
  "transition_in": "怎样承接上一段；第一段说明怎样开场",
  "transition_out": "怎样交给下一段；最后一段说明怎样收束",
  "narration": "五至六个完整中文句子的可直接朗读旁白",
  "audio_file": "video/audio/section_01.mp3"
}
```

要求：

- 行数、顺序、`id`、`image_prompt_id`和`section_title`与S5严格对应；
- `narration`只含实际朗读内容，不写Markdown、舞台提示、镜头指令、时间码或字段说明；
- 全部写完后连续朗读，修复重复开场、主体跳变、数字口径漂移、因果断裂和机械过渡。

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

`python skills/businvet-article/scripts/validate_stage.py --stage 7 --topic-dir /absolute/topic/path`

通过后，向用户明确列出`video/images/`所期待的图片ID。用户把同编号PNG、JPG、JPEG或WEBP放入该目录后，可直接把整个`video/`目录交给`narrated-video`：

`python skills/narrated-video/scripts/build_narrated_video.py /absolute/topic/path/video`
