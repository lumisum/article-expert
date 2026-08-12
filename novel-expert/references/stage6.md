# S6：事件标题与完整小说场景封面

标题、文章封面和视频封面只聚焦`episode_core`中一个正在发生且尚未结束的事件瞬间。封面不是文章结构图，也不按左右、上下或百分比切分；它是一张能够独立代表本篇小说的完整场景，标题自然进入场景留白。

## 统一入口合同

三个入口共享同一个事件、人物组合、未完成动作、视觉问题和正文兑现。苏美与凝香是固定男女主角，但封面只选择核心场景真正需要的人物：至少一位固定主角在场，另一位主角和S1配角按剧情决定是否出现。不得为了品牌模板强塞无关人物。

S3中的`hidden_meaning`和`forbidden_direct_statement`是导演手记，不是入口文案。标题不得发表观点、总结道理或提前宣布答案；封面不得使用信息卡、流程图、知识节点、PPT、硬分栏、独立色块标题板或人物抠图拼贴。

## 标题

围绕同一个事件瞬间生成至少五个候选。每个候选必须包含一个可见动作或事件词，以及问号、反常转折、未完成动作、意外停顿或时间节点中的一种好奇信号。

- 文章标题十五至三十二个非空白字符；视频短标题八至十八个；
- 像小说开头，不像文章结论、建议、摘要或哲理口号；
- 不出现`hidden_meaning`或`forbidden_direct_statement`的逐字内容，也不改写成近义观点；
- 可以使用角色名，但陌生配角名不能成为唯一点击理由；
- 不使用虚假数字、年龄羞辱、关系恐吓和灾难化；
- 标题承诺必须由正文中的同一事件真实兑现。

最终标题按`familiarity`、`self_relevance`、`event_immediacy`、`tension`、`curiosity`、`unfinished_tension`、`fidelity`、`non_exploitative_tension`、`character_dignity`、`share_impulse`评分，最低80/100；事件临场感与未完成张力分别不得低于8分。

## 文章封面

- 固定2.35:1横向比例；
- 100%是一张连贯、真实、可进入的小说场景，不设“场景区”和“标题区”比例；
- 冻结正文最能代表主题、人物关系与未完成张力的一秒，不把多个章节拼在一起；
- 至少一位固定主角可辨认；另一位主角及配角只在核心场景真实需要时出现；
- 所有可见人物逐一写清外观连续性、动作、视线、呼吸、眉眼、嘴角、肩颈、彼此距离和场景关系；
- 标题利用墙面、窗外雾光、天空、桌面上方、走廊纵深等场景原生负空间自然叠加，不生成白色信息板、色块卡片或人工切开的空白半边；
- 标题是画面中的出版设计层，不让人物手持文字，不在道具、招牌、手机或纸张中生成乱码；
- 封面同样使用与正文一致的细窄荧幕式叙事边框，约占画幅6%至10%，边框必须融入环境色、纸张颗粒和手绘纹理；它只承接观看感与画幅，不承载标题或另一条文案；
- 标题必须留在场景原生负空间，绝不写进边框。这样边框是“进入小说现场的银幕”，标题仍是读者先读到的事件引子；
- 封面与正文连环画固定共用成熟彩色叙事插画微3D：约65%插画化造型、25%微3D材质、10%现实生活锚点；人物与空间应像成人小说的彩色绘本，而不是照片、真人写真或电影剧照；
- 使用可见手绘笔触、纸张颗粒、色块层次、柔和边缘与克制的微3D体积。采用温暖手绘动画电影般的通透自然光、丰富环境色、克制奇想与空气透视；以真实前景遮挡、中景人物关系、远景空间和清晰焦点转移形成镜头感。现实生活只用于成年人比例、空间尺度与物件逻辑，禁止皮肤毛孔、摄影棚打光、镜头眩光和摄影式强景深虚化；
- 缩略图仍能读出一个主要动作、至少一张关键面孔、标题关键词和未完成问题；
- 只生成提示词，不生成图片。

## 视频封面

写入`assets/video_cover_prompts.jsonl`，默认包含微信视频号横版、今日头条横版和B站横版。每行只能包含`platform`、`size`、`aspect_ratio`、`core_prompt_points`和`prompt`。

视频封面复用文章封面的同一场景、人物组合、动作、表情关系、成熟叙事插画微3D画风、细窄荧幕式叙事边框和短标题，只调整裁切与安全范围。标题保留在自然负空间，绝不写进边框；边框不另放文字。禁止重新创造冲突、强塞双主角、按比例切出标题区、使用信息框、小字摘要、写实摄影、真人写真或电影剧照。

## 输出

写入`assets/title_cover_package.json`：

```json
{
  "title_candidates": [
    {
      "title": "候选标题",
      "reader_hook": "吸引哪类人",
      "psychology": "为什么会点",
      "promise": "正文怎样兑现",
      "dignity_and_responsibility": "怎样不羞辱人物，同时不替人物逃避后果",
      "share_trigger": "为什么会想转给谁",
      "event_snapshot": "标题冻结的正在发生的事件瞬间",
      "curiosity_gap": "点击前尚不知道什么",
      "unresolved_state": "哪个动作、回应或结果仍未完成",
      "assertion_avoidance_check": "为什么它不是观点、建议、结论或哲理口号",
      "cover_moment": "封面冻结在哪一秒、哪些人物在场以及张力来自哪里",
      "core_dialogue_or_story": "标题聚焦的唯一核心对话或故事动作",
      "visual_metaphor": "场景怎样自然承载主题，不使用信息图",
      "risk": "可能造成什么误读",
      "evidence_basis_ids": ["U01"]
    }
  ],
  "selected_title": "最终标题",
  "selection_scores": {
    "familiarity": 8,
    "self_relevance": 8,
    "event_immediacy": 8,
    "tension": 8,
    "curiosity": 8,
    "unfinished_tension": 8,
    "fidelity": 8,
    "non_exploitative_tension": 8,
    "character_dignity": 8,
    "share_impulse": 8
  },
  "selection_reason": "为什么覆盖面和兑现度最好",
  "title_cover_link": "标题与封面共享的事件瞬间",
  "entry_contract": {
    "click_core": "三个入口共同承诺的一个问题",
    "fixed_leads": "苏美与凝香",
    "cover_cast": ["苏美", "配角姓名或稳定称谓"],
    "series_label": "苏美 × 凝香｜中年故事",
    "human_protagonist": "封面中哪位主角成为读者进入故事的视角",
    "familiar_scene": "陌生读者一眼能认出的现场",
    "core_dialogue_or_story": "唯一核心对话或故事动作",
    "active_metaphor": "正在发生但尚未完成的动作或场景隐喻",
    "metaphor_mapping": "动作、物件与隐藏意义的关系",
    "unresolved_question": "正文才能回答的缺口",
    "story_payoff": "正文怎样兑现事件、人物变化与结尾余味",
    "headline_type": "eventized_curiosity_hook",
    "headline_event": "标题使用的可见动作或事件",
    "headline_unfinished_state": "尚未完成的动作、回应或结果",
    "assertion_avoidance": "标题为什么没有提前给出观点和答案",
    "article_headline": "与selected_title完全一致",
    "video_headline": "同一点击核下八至十八字短标题",
    "consistency_rule": "三个入口不得更换事件、人物组合、动作、冲突或点击理由"
  },
  "cover_prompt": {
    "aspect_ratio": "2.35:1",
    "narrative_mode": "novel_story",
    "cover_layout": "single_full_frame_novel_scene_with_integrated_title",
    "style_profile": "sunlit_mature_narrative_illustration_micro_3d_cover",
    "palette_profile": "sunlit_chromatic_midlife_story",
    "accent_color": "雨蓝 #526A7A",
    "supporting_colors": ["珊瑚橙 #E77A64", "晴空蓝 #5F9ED1", "湖青 #4AA5A4", "暖铜 #B67850"],
    "episode_core": "与S1一致",
    "core_dialogue_or_story": "封面只重现的那一个动作或事件",
    "scene_reconstruction": "时间、地点、前中后景、核心物件和正在发生的动作",
    "characters_visible": ["苏美", "配角姓名或稳定称谓"],
    "lead_presence": "sumei|ningxiang|both",
    "visible_character_signatures": [
      {
        "name": "苏美",
        "signature": "固定主角逐字外观签名或配角同篇连续签名",
        "performance": "本秒的动作、眉眼、嘴角、呼吸、视线、肩颈和身体方向"
      }
    ],
    "character_blocking": "所有可见人物的位置、距离、朝向和动作主次",
    "frozen_story_moment": "答案出现前最有代表性的一秒",
    "expression_relationship": "可见人物之间不同但互相作用的表情关系",
    "unresolved_visual_question": "不读标题也能感到的未完成问题",
    "screen_frame_style": "cinematic_story_frame_no_caption",
    "screen_frame_coverage": "6%-10% narrow integrated border",
    "frame_text_policy": "title_must_not_be_inside_frame",
    "title_integration": "标题怎样进入场景原生负空间而不形成信息板",
    "natural_negative_space": "墙面、天空、窗光、纵深或其它真实留白",
    "headline_text": "与最终标题一致",
    "series_label": "苏美 × 凝香｜中年故事",
    "lighting_plan": "统一时间与空间中的主光、环境光和阴影",
    "crop_survival_plan": "不同裁切下怎样保留核心动作、关键人物和标题",
    "one_second_read": "一秒读出的场景、人物、动作与缺口",
    "thumbnail_test": "缩小后仍保留的面孔、动作、标题关键词和张力",
    "negative_constraints": "禁止硬分栏、比例切分、信息卡、标题板、边框信息卡、标题写在边框内、拼贴、多场景、乱码、换脸、人物工具化、文字堆积、写实摄影、真人写真、电影剧照、photorealistic、cinematic still、皮肤毛孔、摄影棚打光、镜头眩光和强景深虚化",
    "prompt": "超过700个非空白字符的完整中文提示词"
  }
}
```

`characters_visible`必须与`entry_contract.cover_cast`完全一致，且至少包含苏美或凝香。`visible_character_signatures`逐人对应：主角签名逐字服从`cast-bible.json`，配角签名必须服从S1的`appearance_boundary`。封面`prompt`必须包含完整单场景、标题、自然负空间、胶片式叙事边框、标题不在边框内、事件化好奇引子、尚未完成、场景重现、所有可见人物及签名、动作、表情关系、前中后景、光线、插画化空气景深、裁切策略、成熟叙事插画、手绘笔触、微3D材质和禁区；并明确禁止硬分栏、百分比切分、信息卡、边框信息卡、标题写在边框内、写实摄影、真人写真、电影剧照、photorealistic和cinematic still。

写入`article/final_article_digest.txt`，五百至八百个非空白字符，用自然网络短评说明本期发生了什么、主要人物怎样被卷入以及读者将经历怎样的情绪与余味，不复述全文。
