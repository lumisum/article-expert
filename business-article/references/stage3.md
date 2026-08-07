# S3：利润审计、悟道与业务投资观察

S3先审因果，再审商业发动机和利润形成，最后审Spark并完成跨周期规律和观察框架。不得写正文。

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
      "evidence_check": "证据与数字支持到哪里",
      "scope_check": "公司、业务和产业范围是否偷换",
      "decision": "valid|return_to_s2"
    }
  ]
}
```

出现因果倒置、对象偷换、口径混用、估值代替业务、技术指标代替客户价值或只有术语升级时，返回S2。

## 经济性审计

追加：

```json
{
  "economics_audit": {
    "customer_value_test": "客户收益是否足以支持采用与付款",
    "revenue_identity_test": "价格、数量、频率、留存和结构能否解释收入",
    "revenue_quality_test": "增长是否可持续，是否依赖集中客户、并购、补贴或一次性因素",
    "profit_bridge_test": "收入经过哪些直接成本和固定成本后才能成为经营利润",
    "cash_conversion_test": "利润怎样变成现金，资本开支与营运资金吞掉多少",
    "unit_economics_test": "边际收入、边际成本、获客或交付投入与回收关系",
    "scale_test": "规模扩大改善还是恶化利润率、周转与资本效率",
    "value_capture_test": "公司为何能保住利润，谁可能夺走它",
    "return_on_capital_test": "新增投入能否形成超过资本成本的可持续回报；无法量化时写清未知",
    "expectation_gap_test": "资本预期比已兑现业务多假设了什么",
    "fatal_assumption": "哪一个前提失效会破坏整条商业逻辑",
    "decision": "valid|return_to_s2"
  }
}
```

任何一项不能回答时，可以保留`unknown`，但必须说明缺失会怎样限制结论。以融资、估值、订单、市场空间或技术领先替代利润与现金时，返回S2。

## 悟道

从最低点提炼跨公司、跨周期仍有解释力的规律。优先寻找真正能够解释利润、激励、竞争与资本的经济学或商业理论；东西方哲学只在能把这条规律照得更深时使用，而不是替代商业分析：

```json
{
  "wisdom_candidates": [
    {
      "id": "W01",
      "tradition": "business|economic|eastern|western",
      "thinker_or_text": "理论、原典或思想家",
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

规律可以来自激励、稀缺、规模、反馈、网络效应、控制权、可选性、安全边际或预期，但不得为了使用概念而重写事实。正文只采用真正增加解释力的最少材料。

## Spark定型

追加`spark_verdict`：

```json
{
  "spark_verdict": {
    "spark_id": "S01",
    "decision": "validated|reframed",
    "final_question": "反证后仍成立的问题",
    "final_judgment": "作者能够承担的业务判断",
    "publish_thesis": "正文原样兑现的一句话",
    "strongest_counterargument": "最强反方",
    "response": "判断怎样因此收窄",
    "boundary": "在哪里失效",
    "reader_change": "读者改变什么判断"
  }
}
```

## 业务投资观察

追加`decision_design`：

```json
{
  "decision_design": {
    "decision_scene": "读者何时使用这套判断",
    "core_principle": "新的观察原则",
    "key_variables": ["按客户价值、收入、利润、现金、竞争和资本效率排序的关键变量"],
    "leading_signals": ["业务结果出现前可以观察的领先信号"],
    "confirming_signals": ["支持判断的业务兑现信号"],
    "disconfirming_signals": ["会让判断延期或直接失效的反向证据"],
    "scenarios": ["至少两种可能路径"],
    "delay_vs_destroy": "区分哪些变量只推迟兑现，哪些会破坏商业逻辑",
    "stop_condition": "何时停止沿用当前判断",
    "boundary": "不适用范围"
  }
}
```

致用必须提高判断质量，不提供股票、仓位、价格点位或收益承诺。
