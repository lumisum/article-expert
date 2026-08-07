# S1：技术底座

S1回答三个问题：读者任务是什么，技术对象在什么环境中成立，哪些原始证据足以支撑后续解释与复现。

## 预分析

先识别文章模式：

- `technical_explainer`：主要交付准确心智模型、方案差异和选型边界；
- `hands_on_playbook`：主要交付可复现的实施、验证、排障与优化路径。

明确目标读者的起点、期望结果、平台、语言、框架、版本、依赖、权限和成本边界。缺失信息列入`research_gaps`，不得自行补造。

## 搜索与取证

优先使用Google发现线索，再进入原始页面。证据优先级：

1. 规范、官方文档、官方源码仓库和发布说明；
2. 论文、作者说明、维护者讨论和可复现实验；
3. 真实问题单、变更记录和高质量技术复盘；
4. 二手教程和媒体文章仅作线索。

动态页通过`scripts/cdp_capture_pages.py`保存到当前主题`research/raw_pages/`。实际选用的原始页面正文合计不得少于20KB，并至少覆盖技术定义、版本行为、关键机制、实际用法和已知边界；若涉及性能数字，必须保存比较条件。

## 输出

写入`research/tech_blueprint.json`：

```json
{
  "topic_id": "topic-id",
  "article_mode": "technical_explainer 或 hands_on_playbook",
  "technical_subject": "要讲的技术对象",
  "core_reader": "读者画像与已有基础",
  "reader_job": "读者真正要完成的任务",
  "starting_state": "开始前所处状态",
  "promised_outcome": "文章能够诚实交付的结果",
  "environment_scope": "平台、语言、框架和版本范围",
  "success_observation": "看到什么才算完成或真正看懂",
  "reader_help": ["理解、选择、实施、排障、优化或规避风险中的具体帮助"],
  "narrative_position": {
    "author_relation": "作者如何接触、使用、调试或研究这个技术对象",
    "trigger_to_write": "哪次现象、失败、变化或疑问促使现在写",
    "verified_knowledge": "哪些内容由亲测、源码、文档或可复现实验支撑",
    "inference_boundary": "哪些只是推断、类比或尚未验证",
    "judgment_at_stake": "作者真正想帮助读者修正或完成的判断"
  },
  "narrative_materials": [
    {
      "id": "M01",
      "kind": "goal|operation|observation|failure|diagnosis|repair|result|boundary",
      "content": "能够托住一个正文推进动作的具体材料",
      "evidence_ids": ["E01"],
      "narrative_role": "它让文章从什么问题推进到什么问题"
    }
  ],
  "research_gaps": [],
  "visual_world": "后续配图需要识别的产品、界面、代码或系统对象"
}
```

写入`research/source_pack.json`：

```json
{
  "topic_id": "topic-id",
  "article_profile": {
    "mode": "technical_explainer 或 hands_on_playbook",
    "core_audience": "目标读者",
    "source_anchor": "官方原始来源类型",
    "visual_mode": "technical_micro3d"
  },
  "primary_sources": [
    {
      "id": "E01",
      "source_type": "official_docs/source_code/spec/paper/release_notes/issue",
      "title": "来源标题",
      "url": "原始链接",
      "snapshot_file": "research/raw_pages/...",
      "claim": "它能证明什么",
      "version_or_date": "适用版本或日期",
      "boundary": "它不能证明什么"
    }
  ],
  "technical_claims": [
    {
      "id": "C01",
      "claim": "后文需要解释或使用的技术事实",
      "evidence_ids": ["E01"],
      "environment": "成立环境",
      "confidence": "confirmed/conditional/unresolved"
    }
  ],
  "numeric_claims": [
    {
      "id": "N01",
      "publish_text": "正文允许使用的完整数字表述",
      "metric_context": "任务、样本、硬件、版本、时间、单位和比较条件",
      "evidence_ids": ["E01", "E02"],
      "status": "exact/attributed/omit"
    }
  ],
  "author_experience": [],
  "fact_conflicts": [],
  "known_unknowns": [],
  "selected_source_files": ["research/raw_pages/..."]
}
```

关键接口、命令和版本行为必须至少有一个原始来源。性能、比例、规模、成本、排名和benchmark等外部数字进入`numeric_claims`；确定表述至少绑定两个独立来源，无法交叉核验时只能保留归因或标记`omit`。S1可以留下未知，但不能把未知写成事实。

`narrative_materials`不按数量凑配额。它们必须足以形成一条真实过程：技术讲解至少能从可观察现象走到机制、边界和选择，实操文章至少能从目标走到操作、受阻、定位、修复和验收。只有概念分类、功能列表或同一结论的多种说法，不算新的叙事材料。材料不足时继续研究、缩小题目或缩短文章，不虚构运行现场和失败经历。
