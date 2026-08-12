# S1：人事与见事

先确认这是谁的故事、发生了什么、为什么与中年有关，再把材料收束成由苏美与凝香担任固定男女主角的现实主义小说故事，最后补必要资料。完整读取`story-logic.md`与`cast-bible.json`；先建立现实逻辑，再设计悬念和情绪。`narrative_mode`固定为`novel_story`，不再进行模式选择；不得临时改写两位主角的身份、声音或关系，剧情需要家人、同事、医生、邻居、朋友或其他人物时，可以自由增加配角。

## 蓝图

写入`research/novel_blueprint.json`：

```json
{
  "topic_id": "topic-id",
  "central_event": "一个不可替代的生活事件",
  "central_question": "全文只回答的一个问题",
  "hidden_meaning": "导演在后台把握的一层人物意义或人性张力，可以不是完整观点，绝不写成标题或口号",
  "meaning_expression": "implicit_action|light_narration，默认implicit_action",
  "intended_reader": "哪类中年读者最容易认出这个生活处境",
  "reader_recognition": "读者会在哪个具体瞬间觉得自己也站在现场",
  "emotional_truth": "故事必须诚实承认、不能被鸡汤覆盖的复杂感受",
  "intended_aftertaste": "结尾希望留下的情绪温度、未尽问题或关系余波，不规定读者必须改变",
  "narrative_mode": "novel_story",
  "narrative_mode_reason": "固定采用小说故事；说明本题如何通过事件、环境、旁白和必要对话获得沉浸感",
  "episode_core": "本篇唯一的核心对话、核心事件或未闭合动作",
  "role_assignment": "本篇谁先看见、谁先误判、谁追问、谁完成行动，禁止固定女感性男理性",
  "supporting_cast": [
    {
      "id": "C01",
      "name": "配角在正文中使用的姓名或稳定称谓",
      "gender_age": "剧情真正需要的性别与年龄区间，不做无关装饰",
      "relation_to_leads": "与苏美、凝香及核心事件的关系",
      "story_function": "只有这个人物能够造成、阻止、见证或回应的剧情作用",
      "appearance_boundary": "材料支持的外观与服装边界；未知就保持克制",
      "speech_signature": "符合身份、关系和当下压力的说话习惯",
      "basis_ids": ["U01"]
    }
  ],
  "opening_contract": {
    "time": "读者在开场自然得知的具体时间或时段",
    "place": "人物能够真实行动的具体地点",
    "people_present": "开场在场人物及彼此关系",
    "trigger_event": "正文开始前刚发生或正在发生、迫使人物面对核心话题的一件事",
    "visible_first_action": "人物面对触发事件做出的第一个可见动作，不是心理概括",
    "unresolved_question": "读者此刻真正想知道结果的一个问题",
    "carry_anchor": "会从开场带到结尾的消息、物件、请求、决定或未完成动作；使用可在正文原样复现的短语",
    "ending_payoff": "结尾怎样以行动、反馈或关系变化回应开场，不用口头保证代替发生"
  },
  "reality_logic_contract": {
    "chronology": "列出事件的日期、时段、间隔、通勤与作息；学校、工作日、就医和出行必须相容",
    "knowledge_map": "逐人说明开场知道什么、不知道什么、从何得知、何时改变；任何人不得无来源知道答案",
    "money_and_objects": "关键金额、收入、债务、物件所有权、账户归属、保管位置和每次流向；数字规模与生活成本相容",
    "institutional_process": "银行、医院、公司、学校、平台或法律程序怎样真实运作；情节不能依赖不存在的权限或流程",
    "motivation_and_alternatives": "人物为什么选择当前做法而不采用更直接的办法；列出被放弃的明显选项及其现实代价",
    "causal_necessity": "触发如何逼出摩擦、摩擦如何逼出选择、选择如何造成回应；删除任一关键环节会断在哪里",
    "setup_and_payoff": "每个关键物件、数字、人物和异常行为在何处埋下、何处发挥作用；反转必须回看时早有依据",
    "resolution_cost": "结尾人物实际失去、承担、交出或改变什么；问题不能因一句解释、一次电话或偶然好消息自动解决"
  },
  "story_arc": [
    {
      "phase": "trigger",
      "event": "触发事件怎样把两个人卷入问题",
      "visible_action": "读者能够看见或听见的动作",
      "emotional_change": "人物关系或认识怎样改变",
      "basis_ids": ["U01"]
    },
    {
      "phase": "friction",
      "event": "误判、回避、立场差异或现实阻力怎样让事情变难",
      "visible_action": "读者能够看见或听见的动作",
      "emotional_change": "人物关系或认识怎样改变",
      "basis_ids": ["U01"]
    },
    {
      "phase": "choice",
      "event": "至少一人当场完成什么有代价的选择",
      "visible_action": "读者能够看见或听见的动作",
      "emotional_change": "人物关系或认识怎样改变",
      "basis_ids": ["U01"]
    },
    {
      "phase": "payoff",
      "event": "环境、对方或两人的关系给出什么真实反馈",
      "visible_action": "读者能够看见或听见的动作",
      "emotional_change": "人物关系或认识怎样改变",
      "basis_ids": ["U01"]
    }
  ],
  "knowledge_action_arc": {
    "claimed_belief": "人物嘴上相信或以为自己相信什么",
    "habitual_action": "现实压力出现时，他实际上总会怎么做",
    "knowing_doing_gap": "他说的、知道的与真正行动之间有什么裂缝",
    "consequence": "这种行动造成什么现实或关系后果",
    "embodied_realization": "哪个事实让旧做法再也维持不下去，不写顿悟台词",
    "costly_choice": "人物为新认识付出什么代价并完成什么可见选择",
    "final_action_proof": "结尾哪个行动证明人物真的懂了，即使没有一句总结",
    "reader_inference": "读者从行动与反馈中会自行意识到什么"
  },
  "micro_detail_plan": {
    "opening_sensory_signal": "触发事件发生时读者先听见、看见或触到什么",
    "first_defense_leak": "人物嘴上回避时，哪个声音、表情或动作泄露真实反应",
    "involuntary_body_response": "最低点附近不受控制的细小身体变化",
    "attention_shift": "人物目光或注意力从什么移到什么，意味着什么改变",
    "before_choice_hesitation": "行动前一秒，手、呼吸、句尾或人物距离发生什么",
    "after_choice_feedback": "行动发生后，环境、对方或身体先给出什么反馈",
    "closing_environment_echo": "结尾哪个声音、光线或物件状态回应开场但不替人物总结"
  },
  "adaptation_boundary": "真实材料怎样进入以两位固定主角为中心、可含必要配角的叙事，哪些细节不得虚构或冒充亲历",
  "oral_anchor": "用户口述中的核心现场或none",
  "narrative_position": {
    "speaker_relation": "作者、口述者与这件事的真实关系",
    "trigger_to_write": "哪个动作、结果或未解心结促使现在写",
    "known_from_life": "哪些内容由亲历、原话或可核对结果支撑",
    "reflection_boundary": "哪些属于后来理解、作者推断或仍未想通",
    "unresolved_human_question": "作者愿意与人物一起承受、但不强行回答的人性问题"
  },
  "story_materials": [
    {
      "id": "M01",
      "kind": "scene|action|quote|choice|conflict|consequence|later_change|boundary",
      "content": "能够推动故事或认知变化的具体材料",
      "basis_ids": ["U01"],
      "narrative_role": "它让人物、关系或判断发生了什么变化"
    }
  ],
  "evidence_policy": "oral_only|authoritative_required",
  "evidence_reason": "为什么本题可以只用口述，或为什么必须补权威资料",
  "research_gaps": ["必须补足的事实或边界"],
  "visual_world": "人物、空间、季节、物件和情绪基调"
}
```

这些读者字段只帮助作者选择观察距离，不是转化漏斗，也不规定读者必须得到一个答案、方法或行动清单。

## 材料分层

写入`research/source_pack.json`：

```json
{
  "topic_id": "topic-id",
  "article_profile": {
    "mode": "midlife_novel",
    "narrative_mode": "novel_story",
    "core_audience": "35岁以后的人",
    "source_anchor": "user_oral或observed_life",
    "visual_mode": "midlife_editorial",
    "narrative_contract": {
      "lead_cast_ids": ["sumei", "kaidi"],
      "supporting_cast_policy": "as_story_requires_with_evidence_and_continuity",
      "series_label": "苏美 × 凝香｜中年故事",
      "episode_core": "与蓝图完全一致的核心对话或核心故事",
      "role_assignment": "与蓝图完全一致的本篇动态角色分工",
      "source_transformation": "真实材料如何转成苏美与凝香可以承载的情境",
      "adaptation_boundary": "与蓝图完全一致的事实和虚构边界",
      "performance_focus": "通过作者旁白自然写入声音、表情、视线、身体动作、空间关系、环境变化、心理波动与关系变化",
      "spoken_words_priority": "story_first_dialogue_as_action",
      "body_style_contract": "novel_paragraphs_only",
      "meaning_delivery": "action_consequence_choice_feedback",
      "explicit_lesson_policy": "implicit_by_default_optional_single_light_narration",
      "story_priority": "embodied_action_first_no_lesson_required",
      "opening_rule": "time_place_people_trigger_action_unresolved_within_first_10_percent",
      "closure_rule": "opening_trigger_returns_as_visible_action_or_feedback"
    },
    "resonance_contract": {
      "recognition_scene": "读者会在哪个生活瞬间认出自己",
      "emotional_truth": "与蓝图一致、不能被励志话覆盖的复杂感受",
      "character_dignity_boundary": "人物即使做错也不能怎样被羞辱、标签化或工具化",
      "responsibility_boundary": "故事不能替人物逃掉哪些现实选择与后果",
      "intended_aftertaste": "与蓝图一致的情绪温度、未尽问题或关系余波",
      "background_assumption": "正文默认读者只具备哪些日常经验，不要求哪些专业背景"
    }
  },
  "user_materials": [
    {
      "id": "U01",
      "material_type": "oral",
      "scene": "发生在哪里",
      "people": "涉及谁",
      "action_or_quote": "动作、犹豫或原话",
      "meaning_boundary": "它只能证明什么"
    }
  ],
  "observation_cards": [
    {
      "id": "O01",
      "role": "life_context|fact|counter_signal|boundary",
      "claim": "资料能支持的最小事实",
      "source_url": "https://...",
      "raw_page_source": "research/raw_pages/...",
      "supporting_quote": "可回查短引文",
      "publish_boundary": "正文最多怎样说"
    }
  ],
  "fact_conflicts": [],
  "known_unknowns": [],
  "selected_source_files": []
}
```

## 研究原则

- 大段用户口述存在时，它是叙事中心；外部资料负责校准，不抢叙事权。
- 全文固定使用`novel_story`。材料较分散时收窄事件、重排时间或减少支线；不得用播客、访谈、对谈、问答或说明文兜底。
- 苏美与凝香是固定男女主角，不是用户、作者或口述者本人。可以让他们讨论、复演或映照真实材料，但不得把用户没有提供的天气、神态、对白、诊断、冲突和结局写成真实发生。
- 配角按剧情需要自由增加，不设“只能两个人”的限制；但每位配角必须进入`supporting_cast`，拥有不可替代的事件作用、稳定称谓、说话方式与材料边界。删掉不影响事件因果的配角应删除。
- 小说若对人物和场景做保护性转译，必须在`adaptation_boundary`中说清；不得借角色台词、旁白或心理描写扩大事实范围。
- 每篇重新分配两人的认识位置：谁先看见、谁先误判、谁追问、谁行动必须由本题决定，不能长期让苏美负责感受、凝香负责解释。
- 研究既要确认困难，也要寻找真实的改善条件、保护因素、反例和可行动窗口；不能只收集衰退、失去和失败材料。
- 优先补中年处境、代际关系、现实选择、反例和边界。
- 只写个人感受、关系和选择，且不依赖外部事实时，可选择`oral_only`。
- 涉及健康、疾病、诊断、治疗、心理干预、法律、财务或其他高风险判断时，必须选择`authoritative_required`，保存至少两份具有不同上游的权威原始页面。
- `observation_cards`只能记录真实打开并保存的页面。没有检索时保持空数组，禁止创建空URL、空快照或凭常识补出的占位观察卡。
- 医学或心理资料只解释必要事实和适用边界，不把资料包堆成科普文章。
- 在线检索先用Google发现国外原始页面，再通过CDP保存正文。
- 搜索结果页、AI摘要和二手拼接页不作为证据。
- 没有强事实需要核验时，不为网页数量制造研究。
- 用户、医生、亲友或作者的转述只证明“有人这样说过”，除非具有可核对材料，否则不能升级为诊断原因或普遍规律。

`resonance_contract`只是小说的观察与尊严边界：正文从`recognition_scene`进入，诚实承认`emotional_truth`，不羞辱人物，也不替人物逃避后果。它不能演变成“读者读完必须学会什么”的效果合同。

## 开场与故事弧

`opening_contract`必须让一件事先发生，不能只提供氛围。时间与地点不必像字幕一样生硬报出，但读者在正文前10%必须无需猜测就知道：何时、何地、谁在场、刚发生什么、人物做了什么、问题为什么悬而未决。

`carry_anchor`选择能够真实贯穿的短锚点，例如“输入框里的好”“没有签字的申请表”“父亲打来的第三通电话”。它必须在开场出现，在中段影响一次选择，并在结尾获得回应。只重复一个意象、不改变人物行动，不算贯穿。

`story_arc`固定且仅按以下顺序写四项：

1. `trigger`：触发事件把两个人卷入问题；
2. `friction`：误判、回避、立场差异或现实阻力让事情变难；
3. `choice`：至少一人当场完成一个有代价的可见选择；
4. `payoff`：环境、对方或两人的关系给出真实反馈，哪怕结果并不圆满。

四拍都必须有材料依据。材料不足以支持完整四拍时，收窄事件、降低结局强度或缩短文章；不得用编造的争吵、巧合、反转、成功或和解补齐戏剧性。小说必须由动作和后果推进，不能让两个人坐在场景里讨论一个抽象问题。

`reality_logic_contract`不是背景资料摘要，而是小说成立的地基。必须把时间、知情状态、金钱、物件和现实流程写到能够逐项核对的程度；“大概合理”“读者不会注意”都不算完成。只要关键线索依赖人物突然想起、配角一次性交代答案、陌生电话送来真相或现实机构提供不存在的权限，就收窄或重构事件。悬念可以来自人物误判，但事实本身不能含糊。

`micro_detail_plan`不是辞藻清单，而是情绪变化的证据链。每项细节必须能回答“它让读者看见人物的判断、关系或选择发生了什么变化”；删除后毫无损失的咖啡香、夜色、雨丝和灯光不进入计划。用户材料没有支持具体细节时，只能使用不改变事实的当下观察或明确的保护性转译，不得伪造亲历。

`story_materials`不按数量凑齐，必须能组成一段真实的人生过程：发生了什么，人怎样选择或迟疑，关系与处境怎样变化，后来付出什么代价或得到什么新理解。至少要覆盖触发、摩擦、选择和回应四种叙事作用；只有抽象感悟、同一观点的多种说法和未经提供的典型场景，不能托住新的正文段落。材料不足时收窄问题或缩短文章，不用假细节补“人味”。

`supporting_cast`允许为空，也允许按剧情需要增加多名配角，不设置固定人数。新增人物不是为了让画面热闹：他必须能造成、阻止、见证或回应一个不可替代的事件变化，并拥有明确材料依据；同一功能可以由已有角色承担时不另加人。

`hidden_meaning`只服务导演与审计，不是待发布观点，也不必能够压缩成一句道理。它可以是一层关系认识、一种未完全解决的人性张力，或一个由行动证明的生存选择。优先选择`implicit_action`：通过`knowledge_action_arc`让开场旧行动与结尾新行动形成可见差异。只有事实容易被误读时才使用`light_narration`，并在S3重新证明这句旁白不可替代。

S1不建立机制链，不引用哲学，不写正文。结束前只确认事件能够持续、人物必须行动、事实边界清楚、情感真实没有被预设结论压扁；不得预先规划读者必须获得的观点、方法或改变。
