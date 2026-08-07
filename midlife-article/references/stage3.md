# S3：悟道与致用

S3先审因果，再审Spark，最后完成悟道与致用。不得写正文。

本阶段还要完成一次“帮助审计”：文章不是只让读者理解自己为什么痛苦，而是帮助他恢复一种能够继续生活的能力。信心必须来自看清可控边界和完成现实动作，不能来自空泛乐观。

## 因果审计

对每一对相邻层追加：

```json
{
  "causal_audit": [
    {
      "from_level": 1,
      "to_level": 2,
      "cause_effect_check": "下一层是什么因，上一层是什么果",
      "reverse_test": "因为下一层，所以出现上一层；为什么成立",
      "deletion_test": "删除下一层损失什么解释",
      "evidence_check": "证据能支持到哪里",
      "scope_check": "有没有把个人经历扩大成群体规律",
      "reader_language_check": "生活化表达是否独立成立",
      "agency_check": "这一层是否仍为读者保留真实行动空间",
      "decision": "valid|return_to_s2"
    }
  ]
}
```

出现并列关系、对象偷换、因果倒置、证据外推或只有术语升级时，必须返回S2。

当某层声称`general_pattern`却没有外部证据，或中心判断把改变描述成不可能时，也必须返回S2。

## 悟道

从`pre_philosophical_proposition`出发进行定向哲学研究，而不是先找名言再套故事。优先原典、可靠译本或可信学术介绍；真实打开页面并保存到`research/raw_pages/`，研究方法和页面保存要求沿用S1。

东方哲学是主要解释视角，必须找到并采用至少一项真正贴合的材料。西方哲学必须完成检索和比较，但只有确实增加补充、对照、反证或边界时才进入正文。

```json
{
  "wisdom_candidates": [
    {
      "id": "W01",
      "tradition": "eastern|western",
      "thinker_or_text": "原典或思想家",
      "source_url": "https://...",
      "raw_page_source": "research/raw_pages/...",
      "description_type": "direct_quote|faithful_paraphrase",
      "chinese_description": "准确中文",
      "original_context": "原本讨论什么",
      "causal_connection": "照亮主链哪一层",
      "important_difference": "不能硬套在哪里",
      "use_decision": "use|reserve|skip"
    }
  ]
}
```

每项候选必须核对原始语境与现实差异。候选与故事相似，不代表它证明了故事的因果。

## 哲学桥

追加`wisdom_synthesis`：

```json
{
  "wisdom_synthesis": {
    "life_proposition": "与S2前哲学人生命题完全一致",
    "eastern_core_id": "W01",
    "eastern_explanation": "东方哲学怎样照亮这个人生处境，而不是给它盖章",
    "western_candidate_id": "W02",
    "western_decision": "use|omit",
    "western_contribution_or_omission_reason": "增加了什么新维度，或为什么强行使用反而削弱文章",
    "east_west_relationship": "echo|contrast|boundary|complement",
    "relation_to_spark": "哲学照明怎样深化Spark，而不是偷偷换掉文章中心问题",
    "author_synthesis": "经过东西方照明与反证后，作者最终能够承担的新判断",
    "return_to_life": "用故事中的哪个人、动作、物件或未完成选择把哲理带回现实",
    "anti_pastiche_check": "为什么这不是故事后面粘贴两句名言"
  }
}
```

要求：

- `eastern_core_id`对应的东方材料必须标记为`use`；
- `western_candidate_id`必须对应一项真实研究过的西方材料；
- 西方材料若只重复东方结论，设为`omit`并说明原因；若提供新维度，设为`use`；
- `author_synthesis`必须比S2命题更进一步，也不能复制任何经典转述；
- `relation_to_spark`必须说明悟道如何深化原Spark；若哲学研究推翻了Spark，应先重构`spark_verdict`，不能在正文临时换题；
- `return_to_life`必须回到本篇真实故事，不能用抽象号召收尾；
- 文章最终表达的是作者的判断，不是经典替作者说话。

## Spark定型

追加`spark_verdict`：

```json
{
  "spark_verdict": {
    "spark_id": "S01",
    "decision": "validated|reframed",
    "final_question": "反证后仍成立的问题",
    "final_judgment": "作者能够承担的判断",
    "publish_thesis": "正文原样兑现的一句话",
    "claim_scope": "individual|common_tendency|general_pattern",
    "evidence_ids": ["U01", "O01"],
    "strongest_counterargument": "最强反方",
    "response": "判断怎样因此收窄",
    "boundary": "在哪里失效",
    "reader_change": "读者改变什么"
  }
}
```

## 判断与致用一致性

追加`thesis_practice_consistency`：

```json
{
  "thesis_practice_consistency": {
    "thesis_claim": "中心判断实际声称什么",
    "implied_world": "如果它完全成立，读者还能不能改变",
    "practice_mechanism": "致用动作具体绕过或改变因果链哪一层",
    "contradiction": "存在什么逻辑冲突；没有则写none并解释",
    "decision": "valid|return_to_s2"
  }
}
```

若文章先断言“只有付出代价才能改变”，随后又要求读者“在代价发生前改变”，属于直接矛盾，必须返回S2，不得用一句反例说明草草放行。

## 致用

追加`practice_design`：

```json
{
  "practice_design": {
    "primary_help": "与help_contract一致的主要帮助",
    "reader_scene": "读者何时需要它",
    "choice_principle": "新的选择原则",
    "restored_capacity": "读者恢复或提高什么能力、关系或生活秩序",
    "confidence_basis": "为什么有理由相信行动可能产生变化",
    "first_realistic_step": "环境不理想时也能开始的最小一步",
    "signals_or_actions": ["一个至三个现实信号或动作"],
    "mechanism_link": "这些动作具体改变因果链哪一层",
    "validation": "怎样知道它已经发生",
    "boundary": "何时不能使用"
  }
}
```

人生文章的致用可以很轻，但必须具体。不能只让读者“想一想”“珍惜当下”或寻找自己的抽象象征。

追加`anti_anxiety_audit`：

```json
{
  "anti_anxiety_audit": {
    "difficulty_acknowledged": "文章诚实承认了什么现实困难",
    "catastrophizing_removed": "删除或收窄了哪些灾难化、羞辱性或宿命化表达",
    "unnecessary_burden_released": "读者可以放下什么自责，以及因果依据是什么",
    "responsibility_preserved": "读者仍需承担什么，避免把安慰写成逃避",
    "relief_not_escape": "为什么这种许可不会否认代价或取消行动",
    "agency_preserved": "因果链在哪个环节保留了真实行动空间",
    "confidence_not_fabricated": "信心由哪些事实、机制和反馈支撑",
    "shareable_understanding": "哪项认识能替读者向一个具体关系对象说清难言之事",
    "expected_reader_state": "读完后希望读者获得的清醒、稳定与行动意愿",
    "decision": "pass|return_to_s2"
  }
}
```

`decision`不是`pass`时必须返回S2。若读完后的主要感受只是焦虑、内疚、被年龄审判或对未来失去信心，即使文章观点深刻也不合格。

完成一次阅读减负审计：

- 删除后不损害准确性的理论名称、背景介绍和重复论证应留在研究层；
- 每个核心概念都要有无需专业背景即可理解的生活表达；
- 每个段落只承担场景、动作、因果、判断或转折中的一个主要任务；
- 相邻两层之间必须留下读者自然会继续追问的问题，不能依靠章节标题硬切；
- `shareable_understanding`必须来自文章中心判断，不另造一句空泛金句。

涉及健康、疾病、治疗、戒断或心理危机时，致用只能在已核对的专业边界内表达，并明确何时应当寻求专业帮助；不能用想象中的恶化场景制造行动压力。

S3的`causal_audit`、`wisdom_candidates`、`wisdom_synthesis`、`spark_verdict`、`thesis_practice_consistency`、`practice_design`和`anti_anxiety_audit`全部追加回`research/source_pack.json`。不得把这些内容写进`stage3_receipt.json`；收据只能由校验脚本生成。
