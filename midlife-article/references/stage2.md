# S2：因果下潜与单一Spark

完整读取`author.md`、S1蓝图、口述材料和直接相关页面。S2只做思考，不写正文。

## 因果深井

围绕中心事件建立五至七层主链：

- L1解释表面现象为什么发生；
- L2必须解释L1的原因；
- L3必须解释L2的原因；
- 依此向下；
- 最低点抵达无法绕开的时间结构、关系约束、责任转移、欲望冲突、身份变化或选择代价。

每一层都做三项测试：

1. **正向**：本层具体解释上一层什么结果；
2. **反向**：能否准确说“因为本层，所以出现上一层”；
3. **删除**：删除本层后，上一层是否失去关键解释。

下潜不是为了证明人生无解。每深入一层，都要同时检查这一层揭示了什么新的可控与不可控边界。若下潜最终只剩宿命感，说明因果链没有找到真正的作用点，必须继续分析或收窄判断。

只能说“还有另一个方面”的内容是支线，不进入主链。

每次从个人经历向群体规律推进，还要回答：

- 这句话只适用于当事人、常见于部分人，还是准备表述为一般规律；
- 支撑它的是口述事实、外部证据、作者推断，还是三者共同作用；
- 因果强度只能说“可能”“较可能”还是已有充分依据；
- 读者在哪个环节仍有改变结果的空间；
- 最强反例会把结论收窄到哪里。

只有用户口述不能独立支撑“一般规律”。准备从个人经历推向群体判断时，必须补充外部证据；补不到就把表述收窄回个人经验。

## source_pack追加

```json
{
  "causal_spine": [
    {
      "level": 1,
      "id": "C01",
      "explains_level": "ROOT",
      "effect": "上方需要解释的结果",
      "cause": "本层找到的原因",
      "cause_effect_link": "因怎样产生果",
      "reverse_test": "因为本层，所以出现上层",
      "evidence_ids": ["U01", "O01"],
      "claim_scope": "individual|common_tendency|general_pattern",
      "evidence_grade": "oral_fact|external_fact|reasoned_inference|mixed",
      "causal_strength": "possible|probable|strong",
      "reader_facing_expression": "中年读者凭生活经验即可理解的说法",
      "judgment_change": "这一层改变了什么判断",
      "counterexample_or_boundary": "什么情况不成立",
      "agency_window": "读者仍能在哪个环节改变结果",
      "universalization_risk": "从个例外推时最容易夸大什么",
      "next_question_or_stop": "继续追问的原因或停止理由"
    }
  ],
  "coordinates": [
    {
      "id": "K01",
      "dimension": "时间、关系、责任、身份、欲望或选择",
      "causal_basis_ids": ["C04", "C05"],
      "reader_connection": "与读者哪种现实处境相连"
    }
  ],
  "spark": {
    "id": "S01",
    "question": "最低点附近真正值得追问的问题",
    "causal_basis_ids": ["C04", "C05"],
    "coordinate_ids": ["K01", "K02"],
    "core_tension": "两个不能同时回避的现实",
    "current_judgment": "暂定判断",
    "strongest_counterpoint": "最强反方",
    "agency_path": "如果判断成立，读者仍如何提前改变",
    "confidence_basis": "这种改变为什么不是自我安慰",
    "unnecessary_self_blame": "因果链证明读者不必再把什么全部归咎于自己",
    "responsibility_to_keep": "理解原因以后仍不能交给命运或他人的责任",
    "logical_risk": "当前判断最可能与致用发生什么矛盾",
    "reader_relation": "为什么它与中年读者有关"
  },
  "pre_philosophical_proposition": {
    "story_basis_ids": ["U01", "C05"],
    "human_dilemma": "这个故事触碰了人怎样面对时间、关系、欲望或选择",
    "proposition": "尚未借助任何经典，由作者从因果最低点形成的人生命题",
    "why_deeper_than_advice": "它为什么不只是应该做什么",
    "open_philosophical_question": "仍需要东西方哲学帮助照亮或挑战的问题"
  },
  "spark_rounds": [
    {
      "order": 1,
      "focus": "deepen|broaden|challenge|converge",
      "question_before": "上一轮问题",
      "pressure": "本轮最强压力",
      "revision": "怎样修改而不是换题",
      "question_after": "下一轮问题",
      "judgment_after": "本轮后的判断"
    }
  ]
}
```

## Spark

只培育一个Spark，完成至少四轮：

- 至少一轮`deepen`；
- 一轮`broaden`检查能否迁移；
- 一轮`challenge`用反例击打；
- 最后一轮`converge`删除夸张与宿命。

Spark不能是“人到中年才懂”“经历使人成长”一类常识，也不能依靠一个传播比喻代替判断。

Spark不能把一种常见倾向写成人类注定如此，也不能在结论中关闭全部行动空间、随后又要求读者主动改变。若中心判断意味着任何行动都不可能奏效，必须返回因果链重新收窄判断。

Spark的锋利来自重新分配注意力和行动，不来自把处境说得更绝望。它必须让读者知道：哪些事情需要接受，哪些事情仍值得争取，为什么一个现实动作仍可能改变后续结果。

Spark还要形成一种有依据的许可感：因果链证明读者不必再为什么责怪自己，同时也证明理解原因以后仍要对什么负责。只有前者会变成逃避，只有后者会变成训诫；二者必须在同一个判断中成立。

## 前哲学人生命题

S2必须在不查找、不引用任何哲学名言的前提下，从最低点形成`pre_philosophical_proposition`。

- 它回答“这个真实故事究竟触碰了人怎样活着的问题”；
- 它必须比“应该珍惜、应该行动、不要拖延”再深一层；
- 它不是金句比赛，而是后续哲学研究要面对的问题；
- 它必须能由故事事实和因果主链独立推出，删除所有经典名称后仍然成立；
- 它保留一个尚未解决的张力，交给S3中的东西方哲学继续照亮和挑战。

## 思维导图

写入`article/causal_mindmap.md`，必须包括：

- 事实基线；
- 中心问题；
- 竞争解释；
- 五至七层因果主链；
- 反例与边界；
- 最低点；
- 认知坐标；
- Spark多轮生长；
- 读者关系；
- 悟道与致用接口。
- `help_contract`怎样通过因果链得到兑现，而不是在结尾临时追加安慰。
- `reader_contract`中的许可、责任和转发理解怎样由因果链自然产生。
- 前哲学人生命题及其故事依据。

导图可以记录研究术语，但每层必须同时留下`reader_facing_expression`。

`reader_facing_expression`必须属于人生、关系和生活语言。不得把技术系统、产品结构或机器运行方式当作解释人生的主载体；理论可以留在后台，但公开说法必须让没有专业背景的中年读者凭生活经验理解。
