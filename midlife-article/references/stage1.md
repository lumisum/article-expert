# S1：人事与见事

先确认这是谁的故事、发生了什么、为什么与中年有关，再决定需要补什么资料。

## 蓝图

写入`research/midlife_blueprint.json`：

```json
{
  "topic_id": "topic-id",
  "central_event": "一个不可替代的生活事件",
  "central_question": "全文只回答的一个问题",
  "core_reader": "处在什么人生阶段的读者",
  "reader_pain": "他最不愿承认的现实",
  "reader_help": "读完具体改变什么",
  "reader_before": "读前最真实的心理负担和错误判断",
  "reader_after": "读后更清醒、更稳定且仍愿意行动的状态",
  "oral_anchor": "用户口述中的核心现场或none",
  "narrative_position": {
    "speaker_relation": "作者、口述者与这件事的真实关系",
    "trigger_to_write": "哪个动作、结果或未解心结促使现在写",
    "known_from_life": "哪些内容由亲历、原话或可核对结果支撑",
    "reflection_boundary": "哪些属于后来理解、作者推断或仍未想通",
    "judgment_at_stake": "作者愿意承担且希望帮助读者看清的判断"
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

`reader_pain`只定义入口，`reader_help`定义文章最终交付。不得先写一个强烈痛点，再用与因果无关的鼓励收尾。

## 材料分层

写入`research/source_pack.json`：

```json
{
  "topic_id": "topic-id",
  "article_profile": {
    "mode": "midlife_insight",
    "core_audience": "35岁以后的人",
    "source_anchor": "user_oral或observed_life",
    "visual_mode": "midlife_editorial",
    "help_contract": {
      "primary_help": "本篇唯一的主要帮助",
      "current_constraint": "读者正在面对且不能被粉饰的现实约束",
      "restored_capacity": "读完后恢复或提高的判断、能力、关系或秩序",
      "agency_window": "因果链中仍可由读者影响的环节",
      "confidence_basis": "信心建立在哪些事实、机制和可验证反馈上",
      "first_realistic_step": "不依赖情绪高涨即可开始的第一步",
      "anti_anxiety_boundary": "哪些恐吓、羞辱或灾难化表述不能使用"
    },
    "reader_contract": {
      "recognition_scene": "读者会在哪个生活瞬间认出自己",
      "permission_to_release": "可以放下哪种没有依据的自责、羞耻或内耗",
      "responsibility_to_keep": "仍然需要面对的选择、关系或现实责任",
      "likely_share_recipient": "最可能转给哪一种具体关系中的人",
      "shareable_understanding": "文章替读者说清哪句难以当面表达的话",
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

`reader_contract`不是营销画像，而是后续写作的减负边界：正文从`recognition_scene`进入，用读者已经拥有的生活经验解释问题；`permission_to_release`与`responsibility_to_keep`必须同时存在，避免文章滑向自责或逃避。

`story_materials`不按数量凑齐，必须能组成一段真实的人生过程：发生了什么，人怎样选择或迟疑，关系与处境怎样变化，后来付出什么代价或得到什么新理解。只有抽象感悟、同一观点的多种说法和未经提供的典型场景，不能托住新的正文段落。材料不足时收窄问题或缩短文章，不用假细节补“人味”。

S1不建立机制链，不引用哲学，不写正文。S1结束前必须确认`reader_help`与`help_contract.primary_help`一致，并确认`reader_before`能够经由因果、许可边界和现实动作自然转变为`reader_after`。
