# S2：商业发动机、因果下潜与单一Spark

完整读取`business_depth.md`、`author.md`、商业蓝图、事实卡、数字账本和原始页面。S2必须针对S1留下的商业缺口继续检索，直到能建立本题的商业发动机；不能只把技术原理分析得更细。

## 商业发动机

先追加`economic_engine`，再建立因果主链：

```json
{
  "economic_engine": {
    "technology_trigger": "科技变化只改变了什么条件",
    "scarcity_shift": "哪种稀缺性、机会成本或交易成本发生变化",
    "customer_value": "客户获得的可衡量收益、成本节省、风险降低或时间价值",
    "payer_logic": "谁付款、为什么现在付款、不付款的代价",
    "revenue_equation": "适合本题的收入驱动关系，未知项明确保留",
    "revenue_quality": "持续性、集中度、留存、议价、确认边界和一次性因素",
    "cost_equation": "直接成本、固定成本、履约成本和随规模变化的成本",
    "unit_economics": "单个客户、订单、产品或产能单位的边际收入、边际成本与回收逻辑",
    "capital_and_cash": "资本开支、营运资金、现金回收与继续增长所需资金",
    "scale_behavior": "规模扩大怎样改善或恶化经济性",
    "value_capture": "公司为何能从客户价值中留下利润",
    "rent_distribution": "客户、公司、供应商、渠道、平台和竞争者怎样分配产业利润",
    "reinvestment_loop": "利润或资本怎样反过来加强或削弱业务",
    "capital_expectation": "资本叙事隐含的增长、利润率、期限与成功前提",
    "fatal_unknown": "最可能让当前商业判断失效的未知项",
    "evidence_ids": ["O01", "N01"]
  }
}
```

不能用“市场空间很大”“用户会增长”“成本会下降”代替方程与传导关系。没有公开数据时写出变量关系和未知，不捏造精确值。

## 业务因果深井

围绕中心业务问题建立五至七层主链。科技只允许作为入口，主链必须进入利润形成与价值分配。每层从本篇真实情况中选择解释域，例如：

- 客户行为、采购者、使用者与付款者；
- 定价、交易结构、收入方程和收入质量；
- 交付成本、单位经济性、资本强度与现金回收；
- 渠道、供给、标准与生态位置；
- 竞争反应、议价权、经济租与产业利润分配；
- 再投资循环、资本预期、风险变量与错误定价。

这些不是固定章节，也不能机械各写一层。主链只保留真实因果：

1. 本层具体解释上一层哪个结果；
2. 能准确反向朗读“因为本层，所以出现上一层”；
3. 删除本层后，后续判断会失去关键解释；
4. 每层改变一次业务判断，而不是更换术语。

主链必须覆盖：

- 客户或付款逻辑；
- 收入或价值捕获；
- 成本、单位经济性或现金转换；
- 竞争、产业权力或资本预期。

如果五至七层仍主要由技术性能、产品功能和市场规模构成，S2未完成。

## source_pack追加

```json
{
  "causal_spine": [
    {
      "level": 1,
      "id": "C01",
      "explains_level": "ROOT",
      "domain": "customer|product|pricing|revenue|cost|unit_economics|cash_flow|distribution|supply|competition|industry_power|regulation|capital|risk",
      "effect": "上方需要解释的结果",
      "cause": "本层找到的业务原因",
      "cause_effect_link": "因怎样形成果",
      "reverse_test": "因为本层，所以出现上层",
      "evidence_ids": ["O01", "N01"],
      "reader_facing_expression": "普通商业读者能直接理解的说法",
      "judgment_change": "这一层改变了什么判断",
      "counterexample_or_boundary": "什么情况下不成立",
      "next_question_or_stop": "继续追问的原因或停止理由"
    }
  ],
  "coordinates": [
    {
      "id": "K01",
      "dimension": "稀缺、激励、规模、网络、控制权、预期或风险",
      "causal_basis_ids": ["C04", "C05"],
      "reader_connection": "与读者哪种经营或投资判断相连"
    }
  ],
  "spark": {
    "id": "S01",
    "question": "最低点附近真正值得追问的问题",
    "causal_basis_ids": ["C04", "C05"],
    "coordinate_ids": ["K01", "K02"],
    "core_tension": "两个不能同时忽略的业务现实",
    "current_judgment": "暂定判断",
    "strongest_counterpoint": "最强反方",
    "reader_relation": "为什么它会改变读者判断"
  },
  "spark_rounds": [
    {
      "order": 1,
      "focus": "deepen|broaden|challenge|converge",
      "question_before": "上一轮问题",
      "pressure": "本轮最强压力",
      "revision": "怎样修改判断而不是换题",
      "question_after": "下一轮问题",
      "judgment_after": "本轮后的判断"
    }
  ]
}
```

## 强制反方

至少建立并检验一条反方路径：

- 技术性能领先，但客户没有足够付费意愿；
- 收入增长，但交付成本或获客成本吞掉规模收益；
- 市场扩张，但公司无法保住产业链中的价值；
- 商业增长来自渠道、补贴或监管窗口，而非技术壁垒；
- 业务表现不错，但资本预期已经提前透支；
- 收入增长成立，但资本开支、营运资金或回收周期使股东回报不成立；
- 公司创造了客户价值，但供应商、平台、渠道或客户掌握议价权并拿走大部分利润。

## Spark

只培育一个Spark，完成至少四轮：

- `deepen`追到真正约束；
- `broaden`检查能否迁移到相邻公司或产业；
- `challenge`使用反方路径、数字冲突或替代解释击打；
- `converge`删除夸张、宿命和无法验证的预测。

Spark不能是“技术最终要商业化”“长期看好某赛道”一类空判断，也不能直接变成买卖建议。

## 思维导图

写入`article/business_mindmap.md`，包含：

- 事实与数字基线；
- 中心业务问题；
- 角色、价值流与利益冲突；
- 五至七层因果主链；
- 反方路径与边界；
- 最低点与资本预期；
- 认知坐标；
- Spark多轮生长；
- 悟道与投资观察接口；
- 商业发动机、利润树、现金回收与产业价值分配。
