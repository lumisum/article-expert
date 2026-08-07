# S1：见事与商业事实底座

先完整读取`business_depth.md`。确认发生了什么之后，立即判断还需要哪些商业事实，避免资料全部停留在产品功能、技术参数和市场宏大预测。S1不提前建立商业结论。

## 商业蓝图

写入`research/business_blueprint.json`：

```json
{
  "topic_id": "topic-id",
  "trigger_event": "一个明确事件或业务变化",
  "central_business_question": "全文只回答的一个问题",
  "core_reader": "经营者、从业者或普通投资观察者中的具体人群",
  "reader_decision": "读者需要改善的判断",
  "reader_help": "读完具体获得什么",
  "profit_question": "利润、现金流或资本回报中最需要解释的问题",
  "value_capture_conflict": "客户价值与公司价值捕获之间的矛盾",
  "narrative_position": {
    "author_relation": "作者从经营、产业或投资观察中的什么位置看本题",
    "trigger_to_write": "哪项事件、数字矛盾或客户变化促使现在写",
    "known_basis": "哪些事实来自披露、监管材料、客户证据或原始数据",
    "inference_boundary": "哪些属于作者推演，仍缺什么验证",
    "judgment_at_stake": "作者真正准备承担并允许后续事实推翻的判断"
  },
  "narrative_materials": [
    {
      "id": "M01",
      "kind": "event|customer_action|transaction|revenue|cost|cash|competition|expectation|counter_signal",
      "content": "能够推动商业叙事的一项具体材料",
      "evidence_ids": ["O01"],
      "narrative_role": "它把当前商业问题推进到哪里"
    }
  ],
  "research_gaps": ["仍需核对的事实、数字或边界"],
  "visual_world": "公司、产品、客户、价值流与产业场景"
}
```

## 事实材料

写入`research/source_pack.json`：

```json
{
  "topic_id": "topic-id",
  "article_profile": {
    "mode": "business_investment",
    "core_audience": "business_readers",
    "source_anchor": "external_event",
    "visual_mode": "tech_business_scene"
  },
  "observation_cards": [
    {
      "id": "O01",
      "role": "company_official|market_fact|customer_evidence|pricing|revenue|cost|capital_intensity|cash_flow|competition|industry_power|counter_signal|boundary",
      "claim": "页面能够支持的最小事实",
      "source_url": "https://...",
      "raw_page_source": "research/raw_pages/...",
      "supporting_quote": "可回查短引文",
      "publish_boundary": "正文最多怎样说"
    }
  ],
  "numeric_claims": [
    {
      "id": "N01",
      "metric": "数字衡量什么",
      "publish_text": "正文允许原样使用的数字表述",
      "as_of_date": "YYYY-MM-DD或明确报告期",
      "unit": "币种、数量或百分比单位",
      "scope": "公司、业务、产品、地区或市场范围",
      "denominator": "比例、增速或倍数的分母；不适用写none",
      "source_ids": ["O01", "O02"],
      "independence_note": "两个来源是否具有独立上游",
      "status": "exact|range|attributed|omit",
      "calculation": "原值或可复核公式",
      "permitted_wording": "能说到什么程度"
    }
  ],
  "business_fact_map": {
    "customer_job": {
      "known": "客户要完成的任务、原方案和不行动代价；未知则写unknown",
      "evidence_ids": ["O01"],
      "unknowns": []
    },
    "payer_and_transaction": {
      "known": "谁决策、谁使用、谁付款、按什么交易；未知则写unknown",
      "evidence_ids": ["O02"],
      "unknowns": []
    },
    "revenue_evidence": {
      "known": "价格、数量、频率、留存或收入结构的已知事实；未知则写unknown",
      "evidence_ids": ["O03", "N01"],
      "unknowns": []
    },
    "cost_and_capital_evidence": {
      "known": "直接成本、固定成本、资本开支、营运资金或履约负担；未知则写unknown",
      "evidence_ids": ["O04"],
      "unknowns": []
    },
    "competition_and_value_capture": {
      "known": "替代方案、议价位置、关键稀缺资源与利润归属；未知则写unknown",
      "evidence_ids": ["O05"],
      "unknowns": []
    },
    "capital_expectation": {
      "known": "融资或估值叙事隐含的业务前提；未知则写unknown",
      "evidence_ids": ["O06"],
      "unknowns": []
    }
  },
  "fact_conflicts": [],
  "known_unknowns": [],
  "selected_source_files": []
}
```

## 研究原则

- 优先公司公告、财报、投资者关系材料、监管文件、论文、原始数据与客户侧证据。
- 在线检索先用Google发现国外原始页面，再通过CDP保存正文。
- 搜索结果页、AI摘要、转载和同一通讯稿的不同分发页面不算独立证据。
- 至少同时保留支持当前叙事的材料和能够限制它的反向材料。
- 研究配额不按页面数量分配，按商业问题的缺口分配。技术和事件材料足够说明入口后，后续检索优先补客户、合同与价格、收入质量、直接成本、资本开支、现金转换、竞争反应和产业链议价证据。
- 财务数字必须区分收入、毛利、经营利润、净利润、经营现金流和自由现金流；订单、合同上限、融资与估值不能替代已经实现的收入或利润。
- 每个准备发布的数字至少绑定两个独立来源；无法独立交叉核验时使用归因、区间或`omit`。
- 锁定币种、日期、报告期、业务范围和分母，不混用出货量与销售额、收入与GMV、利润与现金流。
- 公司对未来的预测只能写成公司判断，不能升级为已发生事实。
- `narrative_materials`必须能形成实际商业传导，而不是事实堆放：事件怎样改变客户选择，交易怎样形成收入，收入需要吞下什么成本与资本，竞争与产业位置怎样改变价值归属。只有产品参数、市场规模预测或同一观点的多种解释，不能托住新的正文段落。
- 说话位置记录事实来路与推断边界，不预写投资结论。材料不足以形成商业过程时继续检索或缩小问题，不能用宏大趋势补齐叙事。

使用预置脚本保存页面：

```bash
python skills/businvet-article/scripts/cdp_capture_pages.py \
  --url https://primary-source.example/page \
  --out-dir /absolute/topic/research/raw_pages
```

S1不写壁垒、前景、投资结论、哲学材料或正文。找不到的商业事实必须进入`unknowns`，不能用行业预测补空白。
