# Stage 1：见事事实底座

进入本阶段前完整读取本文件。用户已经确认主题或直接提供主题、URL后执行。本阶段只回答发生了什么、哪些已经确认、哪些互相冲突、哪些仍然未知。

产物写入：

```text
${REAL_USER_HOME}/wechat_articles/topics/[topic_id]/research/
├── raw_pages/
├── research_blueprint.json
├── source_pack.json
└── stage1_receipt.json
```

用户给定URL只是入口，不是事实全貌。S1不研究哲学，不设计方法，不预设文章结论，不安排章节。

## 执行顺序

1. **预分析文章类型**：先读用户材料，识别`article_profile`，写清为什么属于该类型。大段生活人生口述优先进入`life_insight`；科技主题再区分事件型商业/投资判断与个人实操型技术分享。无法归类时先收窄中心问题，不能用`general`逃避选择。
2. **规划素材分布**：在搜索前生成`research/research_blueprint.json`，量化四类素材的目标比例、卡片范围、研究问题、来源偏好和停止条件；同时确定数字材料上限、预期网页数量和明确排除项。
3. **预分析校验**：运行`validate_research_blueprint.py`。失败时只修蓝图，不打开搜索页面；通过后文章路由锁定。
4. **Google优先发现**：通过当前CDP打开Google，按蓝图中的`search_tracks`逐条检索。外部在线素材只从国外网站、国际机构、海外大学、原始论文、官方资料或国外可靠媒体获取。
5. **进入原始页面**：从Google结果进入官方公告、原始数据、当事方材料、可靠报道和能暴露争议的讨论；必要垂直站点用于补充，不绕过Google直接凑来源。Google搜索页、AI概览和搜索摘要只用于发现链接，永不进入观察卡或精选来源。
6. **优先一手**：关键时间、数字、主体行为、产品状态和原话优先保存官方或原始页面；二手材料只用于发现线索、补充现场和记录争议。
7. **抓取落盘**：使用`scripts/cdp_capture_pages.py`保存原始页面到`research/raw_pages/`，不得硬编码浏览器端口；脚本必须同时生成或更新`research/raw_pages/cdp_capture_manifest.json`。
8. **动态纠偏**：每完成一批抓取，对照蓝图统计素材角色；某类达到停止条件就停止，同类材料过量时不得继续抓取。出现新事实足以改变文章类型时，停止搜索、回到步骤1重建蓝图，而不是在原路由下偷偷换题。
9. **事实核对**：区分事实、解释、传闻和未知，记录来源冲突与证据强弱。所有准备进入文章的数字先完成下方“数字事实账本”。
10. **口述建账**：用户提供口述、聊天、笔记或亲历材料时，逐条写入`user_materials`；保留用户实际表达的范围，不替用户补记忆、补诊断或补因果。
11. **建立索引**：写入`source_pack.json`，其中`article_profile`必须与预分析蓝图完全一致，只保存文章路由、观察事实、用户材料、读者问题、冲突、未知、信任边界和精选来源。
12. **校验准出**：运行S1准出脚本并生成当前有效的`stage1_receipt.json`。

抓取可以分批执行；`cdp_capture_pages.py`会把每一批结果追加到同一个清单。每批执行后立即检查脚本输出：

- `pages[].status`必须为`captured`；
- `pages[].path`对应文件必须真实存在且具有可阅读正文；
- 失败页面先重试或更换原始来源，不能用搜索摘要、记忆或一段手工整理文字代替；
- `source_pack.json.raw_page_source`和`selected_source_files`只能引用成功抓取清单中的文件。

在至少6份页面成功落盘且有效素材累计不少于20KB前，不得创建`source_pack.json`，更不得宣布S1完成。

## research_blueprint.json

这是搜索前的路线与预算，不是文章提纲、结论或额外报告。它必须先于网页检索完成：

```json
{
  "blueprint_id": "RB01",
  "topic_id": "topic-id",
  "article_mode": "life_insight",
  "article_subtype": "oral_life_insight",
  "source_anchor": "user_oral",
  "visual_mode": "human_scene",
  "core_audience": "35岁以后、正在重新理解身体、时间、父母和选择的人",
  "core_delivery": "借真实经历形成可迁移但有边界的人生判断",
  "type_rationale": "为什么本篇属于这一类型，而不是医学科普或其它类型",
  "central_question": "本轮见事需要围绕哪一个问题建立事实底座",
  "planned_page_range": {"min": 6, "max": 10},
  "planned_card_range": {"min": 6, "max": 10},
  "numeric_card_max_share": 0.4,
  "material_plan": [
    {
      "material_role": "topic_fact",
      "target_share": 0.2,
      "minimum_cards": 1,
      "maximum_cards": 2,
      "research_questions": ["故事入口有哪些必须核验的外部事实"],
      "preferred_sources": ["国外专业机构或原始指南"],
      "stop_condition": "已经足以守住事实边界，不再扩充同类科普"
    },
    {
      "material_role": "reader_context",
      "target_share": 0.5,
      "minimum_cards": 3,
      "maximum_cards": 5,
      "research_questions": ["目标读者真实承担着哪些与中心问题直接相关的处境"],
      "preferred_sources": ["国外纵向研究、调查、访谈或真实案例"],
      "stop_condition": "至少两个独立来源呈现了相关处境和个体差异"
    },
    {
      "material_role": "counter_signal",
      "target_share": 0.15,
      "minimum_cards": 1,
      "maximum_cards": 2,
      "research_questions": ["谁没有沿着中心直觉发展，为什么这个反例重要"],
      "preferred_sources": ["反向研究、对照样本或不同人生路径"],
      "stop_condition": "已经找到足以限制泛化的反向事实"
    },
    {
      "material_role": "boundary_fact",
      "target_share": 0.15,
      "minimum_cards": 1,
      "maximum_cards": 2,
      "research_questions": ["个人经历不能证明什么，哪些问题需要专业判断"],
      "preferred_sources": ["国外权威指南、研究限制或专业边界"],
      "stop_condition": "核心边界已经明确"
    }
  ],
  "search_tracks": [
    {
      "id": "Q01",
      "material_role": "reader_context",
      "question": "本条检索要确认什么现实处境",
      "google_queries": ["英文Google查询一", "英文Google查询二"],
      "evidence_goal": "需要得到哪种可回查事实",
      "stop_condition": "什么时候停止本条检索"
    }
  ],
  "excluded_material": ["与中心问题无关的行业规模", "重复科普", "Google摘要"]
}
```

四类`target_share`之和必须为1。实际`search_tracks`至少4条，并覆盖蓝图要求的素材角色；上例只展示字段形状，不代表完整条数。比例由文章类型和中心问题决定，不照抄示例；人生认知类必须把`reader_context`设为最大素材块，`topic_fact`不得超过35%，反例与边界合计不少于20%，数字观察卡上限不得超过50%。

## 人生认知素材配比

`life_insight`的中心对象是人到中年正在经历什么，不是触发故事的医学、产品或行业知识。S1仍然只收集“见事”，但事实必须分成不同角色：

1. **`topic_fact`**：核验个人故事入口涉及的外部事实，例如疾病边界、事件时间或具体行为后果。它只负责防止事实写错，不能成为素材主体。
2. **`reader_context`**：观察35岁以后读者真实承担的身体变化、父母老去、子女责任、职业选择、时间感、关系变化、照护压力、后悔与修复空间等处境。优先采用纵向研究、调查、访谈、真实案例和能够保留个人差异的材料。
3. **`counter_signal`**：记录与中心直觉相反的人群、路径或结果，防止把年龄、后悔和醒悟写成宿命。
4. **`boundary_fact`**：说明哪些情况不能由个人经历推出，或哪些问题需要专业判断。

人生认知类至少满足：

- `reader_context`观察卡不少于2张，并来自至少2份不同页面；
- `counter_signal`或`boundary_fact`不少于1张；
- `topic_fact`不能超过全部观察卡的一半；
- 带`numeric_claim_ids`的观察卡不能超过全部观察卡的一半；
- 精选来源中至少包含2份`reader_context`页面，以及1份`counter_signal`或`boundary_fact`页面。

这不是要求用心理学解释中年。S1只记录“哪些中年处境被观察到、哪些个体并不符合、哪些边界不能跨越”；为什么如此留给S2。牙齿、疾病或其它专业科普通常保留一至两组最强事实即可，其余检索预算优先用于当前文章真正要解释的人生处境。

## 必须回答

- 发生了什么；
- 关键主体分别做了什么；
- 时间线和关键数字是什么；
- 哪些事实已经确认；
- 哪些来源相互冲突；
- 哪些仍然未知；
- 哪个中心问题值得S2继续追问。

核心事实有一手支撑，重要冲突与未知已记录，材料跨至少三个域名，读者问题具体到一件事时停止。有效快照通常6–10份；`selected_source_files`选最强3–8份且跨域。

## 硬边界

- 不回答“为什么”，只记录待解释现象和会影响判断的事实。
- 不写机制命题、哲学候选、实践方法、文章路线、章节目录、作者语气、标题或正文。
- `research_focus`和`reader_problem.question`只能围绕一个中心问题。
- `observation_cards.use`说明它确认哪项事实或争议，不写第几章。
- 不把搜索摘要、百科、媒体转载或评论自动标成一手来源。
- 不把URL、网站名称、搜索结果标题或模型整理的摘要字符串写进`raw_page_source`冒充文件路径。
- 不得手工创建、复制或编辑`stage1_receipt.json`；该文件只能由准出脚本写入。
- 用户口述是叙事意义上的一手材料，不是外部可验证事实。它可以支持“我当时怎样想、怎样做、医生当时怎样告诉我”等第一人称叙述；不能单独支持疾病诊断、群体比例、医学机制、他人内心或“所有人都会如此”。
- 用户说出大致时间、年龄、金额或次数时可以忠实保留为个人经历，但必须标明其为口述范围；精确到会改变公共判断的数字仍需外部核验。

## source_pack.json

S1创建该文件；S2、S3只在各自字段中追加研究，不建立第二套素材包。

```json
{
  "topic_id": "topic-id",
  "article_profile": {
    "mode": "life_insight",
    "subtype": "oral_life_insight",
    "source_anchor": "user_oral",
    "core_audience": "35岁以后、开始重新理解时间、关系、责任与选择的人",
    "core_delivery": "借一段真实经历形成可迁移但有边界的人生判断",
    "visual_mode": "human_scene"
  },
  "selected_topic": {
    "title": "确认主题",
    "research_focus": "S2需要继续解释的一个中心问题"
  },
  "reader_problem": {
    "reader": "具体读者",
    "situation": "读者遇到这件事的现实场景",
    "question": "读者真正想问的问题",
    "search_query": "读者会主动输入的自然问句",
    "expected_change": "希望形成的理解、判断或行动变化"
  },
  "user_materials": [
    {
      "id": "U01",
      "material_type": "oral_history",
      "provided_by": "user",
      "claim": "用户实际讲述的经历、观察或原话",
      "time_scope": "用户给出的时间范围；未给出则写unknown",
      "certainty": "approximate",
      "permitted_use": "first_person_narrative",
      "boundary": "仅证明用户如此讲述，不证明外部诊断、因果或普遍规律"
    }
  ],
  "observation_cards": [
    {
      "id": "O01",
      "research_stage": "s1",
      "knowledge_role": "observation",
      "material_role": "reader_context",
      "claim": "已确认的事实",
      "source_type": "primary",
      "source_url": "https://...",
      "raw_page_source": "research/raw_pages/example.md",
      "supporting_quote": "可回查短引文",
      "confidence": "high",
      "use": "确认哪项事实或争议",
      "numeric_claim_ids": ["N01"]
    }
  ],
  "numeric_claims": [
    {
      "id": "N01",
      "claim": "经过多方比对的数字事实",
      "value_text": "49.00",
      "publish_text": "49.00元/股",
      "unit": "元/股",
      "as_of": "2026-07-27收盘",
      "scope": "收盘价，不是盘中最高价或发行价",
      "risk_level": "core",
      "calculation": "not_derived；若为换算或比例则写完整公式与输入",
      "comparison_result": "matched",
      "allowed_wording": "exact",
      "independence_note": "两处来源如何独立，是否属于同一稿件转载",
      "sources": [
        {
          "source_url": "https://...",
          "raw_page_source": "research/raw_pages/official.md",
          "source_type": "primary",
          "supporting_quote": "可回查原文",
          "role": "primary_basis"
        },
        {
          "source_url": "https://...",
          "raw_page_source": "research/raw_pages/independent.md",
          "source_type": "analysis",
          "supporting_quote": "独立核对原文",
          "role": "independent_check"
        }
      ]
    }
  ],
  "fact_conflicts": ["来源之间存在的冲突"],
  "known_unknowns": ["当前仍未知的信息"],
  "trust_boundaries": ["当前事实底座不能证明什么"],
  "selected_source_files": ["research/raw_pages/example.md"]
}
```

## 字段纪律

- 观察卡统一使用`research_stage: s1`和`knowledge_role: observation`。
- `material_role`只能是`topic_fact`、`reader_context`、`counter_signal`或`boundary_fact`；它描述材料在事实底座中的作用，不代表正文栏目。
- `source_type`只能是`primary`、`community`或`analysis`；只有官方、原始数据、当事方原文或直接材料才是`primary`。
- 引文必须在对应快照中命中，URL必须指向具体页面。
- 观察卡出现数字、百分比、金额、日期、排名、市场份额、倍数或技术尺寸时，必须填写`numeric_claim_ids`并指向已完成比对的数字事实。
- `fact_conflicts`、`known_unknowns`、`trust_boundaries`至少各有一项；未发现时明确记录“当前未发现”。
- JSON使用UTF-8、`ensure_ascii=False`和`indent=2`。
- `user_materials`为可选数组；存在时ID使用`U01`格式，`material_type`使用`oral_history`、`user_note`或`user_quote`，`certainty`使用`exact`或`approximate`，`permitted_use`固定为`first_person_narrative`。
- `user_materials`不填写`source_url`或`raw_page_source`，不计入观察卡数量、网页数量、来源域名、独立来源或数字交叉验证。外部研究仍必须独立完成。
- `article_profile.mode`只能是`life_insight`或`technology`。`life_insight`固定搭配`oral_life_insight`、`user_oral`和`human_scene`；`technology`使用`event_business_investment`+`external_event`+`tech_business_scene`，或`practical_playbook`+`personal_practice`+`tech_playbook_scene`。
- `life_insight`必须有非空`user_materials`，核心受众明确为35岁以后；外部材料用于核验事实、挑战机制和建立边界，不能盖过用户口述成为文章主角。
- `life_insight`的资料包必须通过“人生认知素材配比”，不能靠增加同类科普页面满足网页、字节或观察卡门槛。

## 数字事实账本

数字不能只因为“两个网页都这么写”就算交叉验证。转载、通稿和聚合页可能来自同一个错误源，必须判断来源独立性。

每个准备进入正文、标题、封面文字或digest的数字必须记录：

- **值与单位**：人民币/美元、亿元/万亿元、元/股、百分比/百分点不能混用；
- **时间**：盘中、开盘、收盘、季度、年度、预测期必须明确；
- **范围与分母**：总股本还是流通股，销售额份额还是出货量/产能份额，公司整体还是业务分部；
- **计算方式**：汇率日期、换算公式、同比/环比基期、估值口径；
- **至少两个独立来源**：核心数字至少一个是一手来源；另一个来源必须独立核对，不是同稿转载；
- **比对结果**：`matched`、`range`、`conflict`或`proprietary_estimate`；
- **允许写法**：`exact`、`range`、`attributed`或`omit`。
- **发布原文**：`publish_text`记录正文准许出现的完整数字表述，包含不可省略的单位或范围；正文不能自行换算、改写或拼接成另一个数字。

遇到冲突不得平均、不得静默挑选：

- 口径一致且误差可解释，写统一值或明确范围；
- 口径不同，正文必须带上时间、分母或范围；
- 无法解释的冲突，`allowed_wording`设为`omit`，不得进入文章；
- 机构独家预测必须写成归因表述，并找第二来源提供上下文，不能写成已经发生的事实。

市值比较必须比较同一种权益口径，不能把上市公司整体市值与未独立上市的业务分部“市值”直接比较。换手率必须说明分母；市场份额必须同时说明时间、统计对象和销售额/出货量/产能口径。

## 准出

```bash
python skills/wechat-article/scripts/validate_research_blueprint.py --topic-dir /absolute/topic/path
python skills/wechat-article/scripts/validate_research_outputs.py --topic-dir /absolute/topic/path
```

通过后必须存在`research/stage1_receipt.json`，否则不得进入S2。
脚本失败时，即使目录里已经存在一份收据，也视为S1未完成。
