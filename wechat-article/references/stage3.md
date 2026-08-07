# Stage 3：Spark验证、悟道与致用设计

进入本阶段前完整读取本文件和 `references/author.md`。S3不写正文、不设计标题、不处理排版；它只承担三项需要高认知投入的工作：

1. 独立验证并定型S2培育的唯一Spark；
2. 从机制最低点提炼可迁移规律，并用最合适的东西方哲学描述挑战、限定或照亮它；
3. 把规律转化为读者能够使用的判断、行动、观察信号或自我校正方法。

本阶段允许精准补研。通过CDP检索时先使用Google发现原典、论文、官方指南、实践案例、失败案例和反方材料，再进入原始页面保存；Google结果页和摘要不能作为证据。新增材料继续写入`research/raw_pages/`和同一个`source_pack.json`。

## 准入

必须存在：

- `research/stage1_receipt.json`
- `article/stage2_receipt.json`
- `research/source_pack.json`
- `article/article_mindmap.md`

完整读取S1观察卡、S2机制卡、`descent_spine`、`coordinate_map`、唯一`spark`、`spark_development_rounds`及对应原始页面。机制不清、相邻层只是换术语、Spark某轮只有措辞变化、最终问题没有继承收敛轮成果时，返回S2继续研究和生长。

同时读取`article_profile`并进行模式验收：

- `life_insight`：最终判断必须触及35岁以后读者真实承担的时间、关系、责任、身体、欲望或选择代价；它应当锋利到能击穿一种自我安慰，同时保留反例和个体边界。悟道可以借哲学照亮，但不能把鲜活人生重新讲成理论课。致用交付一个新的选择原则、识别信号或自我校正动作。
- `event_business_investment`：悟道落在商业与资本如何处理稀缺、风险和预期；致用交付观察变量、验证信号、反向证据和停止判断，不提供无边界投资建议。
- `practical_playbook`：悟道只保留能改善实践判断的最少规律；致用必须包含前置条件、连续步骤、失败分支、验收方法和版本边界，达到读者可以直接照做。

## 一、逐层复核下潜

先审`descent_spine`，再审Spark。对L1→L2直到最深层的每一次迁移逐项回答：

- 下一层是否直接承接了上一层尚未解释的问题；
- 是否更换了解释位置，而不只是更换术语、学科标签或情绪强度；
- 新答案具体改变、收窄或推翻了什么判断；
- 新证据是否足以支持这次迁移；
- 反例或边界是否被保留；
- 若删除这一层，后续结论是否仍然原样成立。若成立，这一层大概率是装饰而非下潜。
- 本层究竟是向下解释，还是并列补充、范围拓宽或换了一个例子；后三者不能判为有效主链。
- 下一层能否被明确写成上一层的原因，上一层能否被明确写成下一层造成、维持或限制的结果；
- 将相邻两层反向朗读为“因为下一层，所以出现上一层”时，是否准确、必要且没有偷换对象；
- `life_insight`的公开表述能否让没有专业背景的目标读者从生活经验直接理解；若必须先懂某个领域术语才懂文章，退回S2完成转译。

在`source_pack.json`追加：

```json
{
  "descent_audit": [
    {
      "from_level": 1,
      "to_level": 2,
      "question_link": "下一层怎样承接上一层未解决的问题",
      "cause_effect_check": "下一层是什么因，上一层是什么果，二者如何连接",
      "reverse_causality_test": "因为下一层，所以出现上一层；核对对象、方向和必要边界",
      "reader_language_check": "本层面向目标读者时是否已经脱离不必要的专业表达",
      "explanation_shift": "解释位置发生了什么真实迁移",
      "judgment_change": "读者判断因此发生了什么变化",
      "evidence_check": "哪些已有证据足以支持迁移",
      "deletion_test": "删除这一层会损失什么不可替代的解释",
      "boundary_check": "反例和适用边界是否仍被保留",
      "decision": "valid"
    }
  ]
}
```

`descent_audit`必须恰好覆盖全部相邻层，顺序连续。只有因果方向、反向朗读、语言转译、证据与删除测试同时成立，`decision`才可写`valid`。`decision`只能是`valid`或`return_to_s2`；任何一项为`return_to_s2`时立即退回S2，不得为了通过脚本改成`valid`。

## 二、逐卡审查证据范围

对主下潜链的每张机制卡做“原文—结论”审查。不能因为来源可靠，就让它替作者承担来源没有说过的结论：

```json
{
  "claim_evidence_audit": [
    {
      "mechanism_id": "M01",
      "supported_core": "对应原文能够直接或合理支持的最小机制结论",
      "unsupported_extension": "原结论中来源没有支持、只能删除或改为作者推断的部分；没有则写none",
      "publish_boundary": "正文最多允许怎样表述",
      "decision": "supported"
    }
  ]
}
```

必须逐张覆盖主链。`decision`只能是`supported`、`qualified`或`return_to_s2`。`qualified`表示保留机制但正文必须按`publish_boundary`收窄；任何`return_to_s2`都必须退回补研。来源只支持“延迟奖励需要更多审慎思考”，就不能扩写成具体脑区、神经通路或“必须亲身疼痛才能理解”。来源只讨论龋齿，也不能顺手证明高血压、脂肪肝和骨质疏松。

## 三、验证并定型Spark

逐轮复核：

- `deepen`是否进入更底层变量、约束、因果或隐藏假设；
- `broaden`是否检验跨对象、尺度、行业或时代的迁移；
- `challenge`是否使用足以击穿原判断的反例或替代解释；
- `converge`是否删除无证据扩张，并形成比种子问题更成熟的判断。

再完成机制、事实、反方、边界、读者和表达挑战。S3不得另造第二个Spark。原判断经得住挑战时写`validated`；核心问题仍成立但判断需要收窄或改写时写`reframed`；问题本身站不住时返回S2。

在`source_pack.json`追加：

```json
{
  "spark_verdict": {
    "spark_id": "S01",
    "decision": "validated",
    "reviewed_descent_levels": [1, 2, 3, 4, 5],
    "reviewed_round_orders": [1, 2, 3, 4, 5],
    "depth_retained": "最终保留的底层变量、约束、因果或隐藏假设",
    "breadth_retained": "确认成立和明确排除的迁移范围",
    "refined_question": "挑战后真正值得本文回答的问题",
    "final_judgment": "完整但有边界的作者判断",
    "publish_thesis": "正文必须原样兑现的一句简洁判断",
    "mechanism_basis_ids": ["M04", "M05"],
    "supporting_evidence_ids": ["O02", "M04", "W01"],
    "wisdom_ids": ["W01"],
    "strongest_counterargument": "最强反方",
    "response": "判断为何仍成立或因此怎样收窄",
    "boundary": "在哪些条件下不能使用",
    "philosophy_result": "哲学对照怎样支持、反对、限定或改写了判断",
    "reader_change": "读者因此改变什么理解、判断或行动",
    "article_role": "它怎样连接最低点、悟道和致用",
    "reframe_reason": "保留或改写的理由"
  }
}
```

`publish_thesis`不放事实数字，不写标题话术，不追求金句腔。

## 四、悟道

先从最低点和定型Spark提炼一条能够迁移到其他时代、行业或生活场景的规律，再寻找哲学材料。顺序不能颠倒。

优先比较最贴切的东方与西方描述：

- 东方可以来自《道德经》《庄子》《论语》《周易》《孙子兵法》、王阳明等；
- 西方可以来自古希腊哲学、斯多葛主义、康德、尼采、维特根斯坦、波普尔等；
- 只选择真正处理同一结构性问题的材料，不按名单凑人；
- 两方都贴切时并置并说明差异；只有一方贴切时只用一方；都牵强时由作者直接讲清规律，并记录放弃理由。

哲学不是装饰，也不能证明现代事实。它至少要完成`support`、`oppose`、`qualify`或`parallel`中的一种关系，最好能够暴露现代判断尚未处理的边界。

有外部哲学研究时追加`wisdom_candidates`：

```json
{
  "wisdom_candidates": [
    {
      "id": "W01",
      "research_stage": "s3",
      "knowledge_role": "wisdom",
      "tradition": "eastern",
      "thinker_or_text": "原典或思想",
      "source_url": "https://...",
      "raw_page_source": "research/raw_pages/wisdom-example.md",
      "description_type": "direct_quote",
      "source_authority": "primary_text",
      "source_identity_check": "页面确实对应这部原典、作者或可靠译注，而不是其它人物页面或拼接摘要",
      "chinese_description": "准确中文原文或忠实转述",
      "original_context": "原典实际处理的问题",
      "mechanism_connection": "它怎样连接最低点机制",
      "spark_relation": "qualify",
      "spark_effect": "它支持、反对、限定或改写Spark的哪一部分",
      "important_difference": "时代、对象和边界差异",
      "fit": "strong",
      "use_decision": "use"
    }
  ],
  "wisdom_synthesis": {
    "portable_principle": "从最低点提炼的可迁移规律",
    "eastern_lens": "东方描述怎样照亮或限定它；无合适材料时说明放弃理由",
    "western_lens": "西方描述怎样照亮或限定它；无合适材料时说明放弃理由",
    "tension_between_lenses": "两种视角之间最有价值的差异",
    "return_to_reality": "它怎样把读者从最低点带回现实"
  }
}
```

无论是否实际引用哲学原文，都必须生成`wisdom_synthesis`。正文最终使用人物姓名，仅限直接引用原话或主体识别确有必要。
`spark_relation`只能是`support`、`oppose`、`qualify`或`parallel`；`fit`只能是`strong`、`partial`或`weak`；`use_decision`只能是`use`、`reserve`或`skip`。
实际采用的智慧材料必须各自对应独立、可回查的原典或可靠译注页面；不能让庄子、孔子和尼采共同指向同一个百科页面或模型拼接文件。直接引文优先使用`primary_text`或`scholarly_translation`，`analysis`只能帮助理解，不能单独承担原话。

## 五、致用

致用不是一句“给我们的启示”，也不是固定三步法。根据题材选择最合适的交付形态：

- 技术类：动作、失败分支、验证方法和版本边界；
- 商业类：变量、取舍、观察指标和风险边界；
- 事件类：后续信号、判断条件和可能路径；
- 人生或哲理类：可观察场景、自我校正方式、支持边界和求助条件；
- 方法类：可执行步骤、有效信号和停止条件。

追加：

```json
{
  "practice_design": {
    "reader_scene": "读者在什么现实场景调用",
    "decision_or_action": "要改变的判断或行动",
    "steps_or_signals": ["少量但足够具体的动作或信号"],
    "validation": "如何判断它有效",
    "boundary": "何时不适用、何时停止或寻求专业支持",
    "evidence_ids": ["O01", "M04", "P01"]
  }
}
```

反思问题不能包装成诊断工具，经验建议不能包装成必然规律。涉及健康、法律、财务或安全时，必须检索可靠指南并明确专业边界。

个人经历类文章还要完成一次“从我到我们”的边界检查：

- 用户口述可以证明作者经历了什么、当时怎样理解，不能自动证明别人也会经历同一过程；
- 将个人经历上升为规律前，必须经过机制证据、最强反例和适用边界三重挑战；
- “只有、唯一、必然、所有人、只能靠吃亏”等排他结论，除非有极强证据，否则改写为条件判断或作者对自身经历的认识；
- 致用不能停在感悟。健康、法律、财务和安全主题至少交付一组来自可靠指南的现实动作、有效信号和寻求专业支持的边界。

## 六、S3停止条件

同时满足：

- Spark已经逐轮复核并形成最终判断；
- 五至七层下潜已经逐层复核，没有术语升级、分类切换或情绪加重冒充深度；
- 主链每张机制卡都完成证据范围审查，正文准许表述不越过原文；
- `refined_question`继承了收敛轮真正增加的认知，不退回种子问题；
- 已从最低点提炼可迁移规律；
- 东西方哲学材料被比较、采用或有理有据地放弃；
- 致用包含场景、动作或信号、验证和边界；
- 强事实、哲学引用和实践依据能够回查；
- S4仅凭这些材料就能成文，不需要边写边补核心思想。
- Spark、悟道和致用与`article_profile`属于同一模式，没有把人生文章做成科普，也没有把科技文章做成资讯总结。

## 准出

```bash
python skills/wechat-article/scripts/validate_insight_outputs.py --topic-dir /absolute/topic/path
```

通过后写入`article/stage3_receipt.json`。脚本只验证协议与证据连接，悟道是否贴切、致用是否真正有帮助仍由本文件指导LLM完成。
