# S0：技术选题

目标不是扫描宏大科技新闻，而是找到三个读者已经在搜索、工作中确实会卡住、文章能够交付明确结果的技术问题。

## 候选入口

- 新模型、框架、工具或接口出现后，读者不知道它到底解决什么；
- 同一任务存在几种方案，读者不知道怎样选择；
- 一个看似简单的配置、集成或排障问题反复消耗时间；
- 官方文档说清了功能，却没有说清真实落地路径；
- 作者完成过一次有复用价值的实践；
- 技术能力很热，但适用边界、成本或失败条件被忽略；
- 一个旧方案在新场景下重新变得有用。

优先选择搜索意图清楚、目标读者广、技术证据可得、结果可以验证的题目。不得用“某技术正在重塑未来”一类宏大叙事代替问题。

## 输出

写入`${REAL_USER_HOME}/wechat_articles/tech_scans/[scan_id]/research/topic_candidates.json`：

```json
{
  "scan_id": "tech-...",
  "candidates": [
    {
      "id": "T01",
      "article_mode": "technical_explainer 或 hands_on_playbook",
      "familiar_subject": "读者认识的工具、技术或现象",
      "reader_problem": "读者正在解决的具体问题",
      "reader_search_language": ["读者会主动输入的自然问题"],
      "practical_payoff": "读完能看懂、做成或避开什么",
      "technical_depth": "可以向下讲到哪一层机制",
      "reproducible_result": "可以观察或验收的结果",
      "primary_source_plan": "准备进入哪些官方原始来源",
      "traffic_reason": "为什么愿意点开、读完、收藏或转发",
      "risk": "最容易写成什么低价值形态"
    }
  ]
}
```

只能输出三个候选。校验通过后等待用户选择，不得自行同时为三个主题进入S1。
