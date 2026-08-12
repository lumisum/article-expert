# S3：小说可写性与边界审计

S3不写正文，不强制检索东西方哲学，也不生成Spark定论、发表命题或行动建议。完整读取`story-logic.md`。它负责确认：S2设计的小说能够仅凭人物行为浮现意义，时间、知情、金钱、物件、现实流程和选择代价可以逐项复盘，同时没有突破真实材料、制造焦虑或把角色变成作者的传声筒。

## 行动表达审计

向`research/source_pack.json`追加：

```json
{
  "story_audit": {
    "event_continuity": "触发、摩擦、选择、回应是否由前一步真实造成后一步",
    "action_meaning": "不引用任何观点句，仅描述哪些行动与后果让隐藏意义自然浮现",
    "knowledge_action_proof": "最终行为是否在相似压力下区别于开场行为",
    "choice_cost_real": "新选择是否真的付出时间、关系、机会、情绪或责任代价",
    "ending_feedback_real": "结尾是否获得环境、对方或关系的真实反馈，而非旁白宣布成长",
    "lead_character_agency": "苏美与凝香是否都拥有判断、行动或回应权",
    "supporting_character_integrity": "配角是否拥有可信动机和剧情作用，而不是观点工具、反面教材或一次性装置",
    "stereotype_check": "是否避免女性受伤、男性解释等固定分工",
    "factual_boundary": "哪些细节来自材料，哪些属于不改变事实的保护性转译",
    "invented_drama_removed": "删除了哪些无依据争吵、巧合、诊断、反转、成功或和解",
    "sermon_risk_removed": "删除或改写了哪些训诫、金句、完整观点台词和作者总结",
    "decision": "pass|return_to_s2"
  }
}
```

以下任一情况必须返回S2：

- 隐藏意义只能靠人物说出来，删掉台词后故事不再成立；
- 结尾只有“我懂了”“我以后会”，没有新的可见行为；
- 最终行动没有代价，人物只是选择了显而易见的正确答案；
- 两个场景之间只有主题相同，没有动作、后果或关系上的因果；
- 需要编造争吵、疾病恶化、突然成功或虚假和解才能完成弧线。

## 现实与因果逻辑审计

追加：

```json
{
  "logic_audit": {
    "chronology_verified": "逐段复盘时间、星期、时长、路程、作息，说明没有冲突",
    "knowledge_states_verified": "逐人复盘每个场景前后知道什么及来源，说明没有越权知情",
    "money_objects_verified": "逐项复盘金额、账户、债务、物件所有权、位置、状态和流向",
    "institutional_process_verified": "银行、医院、公司、学校等现实流程与权限怎样成立",
    "motivation_alternatives_verified": "人物为何不走最明显的捷径；当前选择与性格、关系和代价怎样一致",
    "causal_chain_verified": "每幕由上一幕的后果逼出，并真实改变下一幕可做的事",
    "setup_payoff_verified": "关键反转、物件和信息都已提前埋下，未回收装饰已删除",
    "resolution_cost_verified": "结尾改变付出了可观察代价，核心问题没有被一句话或偶然事件廉价解决",
    "convenience_devices_removed": "删除了哪些传话式配角、一次性电话、巧合、突然想起或集中说明",
    "decision": "pass|return_to_s2"
  }
}
```

审计必须写出本篇的具体证据，不能只填“合理”“已检查”“无问题”。任何一项解释不清即`return_to_s2`。人物可以误判，作者不能误算；悬念可以暂时遮住事实，因果不能靠遮住漏洞成立。

## 意义呈现设计

追加：

```json
{
  "meaning_design": {
    "hidden_meaning": "与S1和S2完全一致",
    "delivery_mode": "implicit_action|light_narration",
    "primary_action_evidence": "最关键的一个行动证据",
    "supporting_consequences": ["一至三个帮助读者推断意义的后果或关系反馈"],
    "reader_inference_path": "读者从开场误判到结尾行动会怎样自行得出认识",
    "optional_light_narration": "delivery_mode为implicit_action时固定none；否则只写一句不超过45字的轻旁白",
    "forbidden_direct_statement": "最不能进入标题、人物台词或作者总结的一句直白道理",
    "ending_image": "结尾停在哪个动作、物件、声音或人物距离上，不总结"
  }
}
```

默认使用`implicit_action`。只有涉及时间跳转、事实边界或容易产生实质误读时才允许`light_narration`；轻旁白只连接事实，不替读者下结论。

## 可选参考镜片

理论和哲学不再是流程门票。只有它们能够帮助作者理解人物、发现反证或收窄事实时，才追加零至三项：

```json
{
  "optional_reference_lenses": [
    {
      "id": "R01",
      "type": "life_observation|psychology|sociology|medical|philosophy|other",
      "use": "character_understanding|counterargument|factual_boundary|omit",
      "background_value": "它为人物理解、反证或事实边界增加的最小价值",
      "source_ids": ["O01"],
      "body_policy": "background_only|light_narration_allowed"
    }
  ]
}
```

数组允许为空。没有真实来源时不能创建引用。`background_only`不得在正文出现名称或转述；即使`light_narration_allowed`，也必须服从S4的一句轻旁白上限。

## 反焦虑与责任

追加：

```json
{
  "anti_anxiety_audit": {
    "difficulty_acknowledged": "小说诚实承认什么现实困难",
    "catastrophizing_removed": "删除或收窄哪些灾难化、羞辱性或宿命化设计",
    "character_dignity_preserved": "人物即使误判或失败，叙事怎样保留其复杂性和尊严",
    "responsibility_preserved": "人物仍需承担什么真实选择和后果",
    "agency_preserved": "哪一个行动环节仍可改变",
    "hope_carried_by_action": "希望怎样由行动与反馈成立，而不是由鼓励成立",
    "ending_emotional_temperature": "结尾留下怎样真实、有希望但不强迫乐观的情绪温度",
    "decision": "pass|return_to_s2"
  }
}
```

## 最终可写性门槛

追加：

```json
{
  "novel_readiness": {
    "single_event": true,
    "single_hidden_meaning": true,
    "action_causality_complete": true,
    "both_character_arcs_complete": true,
    "final_action_proves_change": true,
    "story_survives_without_lesson_sentence": true,
    "facts_within_boundary": true,
    "story_logic_verified": true,
    "non_sermon": true,
    "decision": "ready|return_to_s2"
  }
}
```

只有全部布尔项为`true`且`decision=ready`才能进入S4。所有内容写回`research/source_pack.json`，不得写入收据。
