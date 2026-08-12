# S2：小说内核与行动弧

S2不写正文，不建立五至七层概念因果，不制作思维导图，也不培育Spark。完整读取`story-logic.md`，选择一至两种构思逻辑；把S1的`hidden_meaning`翻译成读者能够亲眼看见、且在时间、知情、金钱、物件与现实流程上经得起复盘的行动、代价、关系变化和结尾证明。

## 核心原则

小说中的认知必须经过行动验证：

> 人物以为自己懂了什么 → 现实压力出现 → 旧行动暴露真实认知 → 后果使旧做法失效 → 人物承担代价作出新选择 → 最终行动证明认识改变。

人物说“我知道”“我明白”“我以后会”都不能作为证明。只有在同类压力再次出现时，他做出了不同选择，知与行才真正合一。

## 故事内核

向`research/source_pack.json`追加：

```json
{
  "story_core": {
    "hidden_meaning": "与S1完全一致、希望读者从行动中感到的一层意义或人性张力",
    "meaning_expression": "implicit_action|light_narration",
    "reader_discovery": "读者在哪个动作或后果发生时开始意识到它",
    "initial_misbelief": "主导开场行为的错误认识、保护性习惯或未完成认识",
    "surface_desire": "人物眼前想得到、避免或维持什么",
    "deeper_need": "人物真正需要学会承担、放下或看清什么",
    "stakes": "如果继续旧行动，会失去什么具体的人、关系、机会、时间或自我秩序",
    "moral_tension": "两种都具有代价的选择之间有什么真实张力",
    "turning_fact": "哪个已经发生的事实让旧认识无法继续自洽",
    "costly_choice": "人物愿意承担什么代价完成新选择",
    "final_action_proof": "结尾哪个可见行动证明认识已改变",
    "ending_echo": "环境、物件或关系如何回应开场但不替人物总结",
    "sermon_risk": "本题最容易被写成哪种训诫、金句或角色说教",
    "active_supporting_cast_ids": ["C01"]
  }
}
```

`hidden_meaning`是导演秘密，不是待插入正文的句子。`implicit_action`为默认；只有缺少一句轻旁白会让关键事实产生误读时，才选择`light_narration`。即使选择后者，也不预写金句，不允许人物直接宣布主题。

## 构思逻辑选择

追加：

```json
{
  "construction_logic": {
    "model_ids": ["bias_corrected_by_evidence", "object_consequence_chain"],
    "why_this_combination": "为什么这一个或两个模型适合本篇事件；不得只写作者或作品名称"
  }
}
```

只选择最适合本篇的一至两个模型，不拼盘。可选值与经典作品中的构建逻辑详见`story-logic.md`；它们只帮助设计因果，不进入正文，也不得要求模仿作家文风。

## 三至五步行动因果

追加`action_causality`，必须三至五项：

```json
{
  "action_causality": [
    {
      "id": "A01",
      "order": 1,
      "story_phase": "trigger|friction|choice|payoff",
      "pressure": "人物此刻受到的具体外部或关系压力",
      "belief_before": "这个动作背后的真实认识，不是人物口头声明",
      "visible_action": "人物真正做了什么",
      "information_change": "这一步让谁基于什么可靠来源新知道或误判了什么",
      "cost_or_risk": "人物完成动作时立即承担的现实、关系或尊严风险",
      "immediate_consequence": "环境或对方立即给出什么反馈",
      "relationship_shift": "距离、信任、责任或误解怎样变化",
      "new_pressure": "这个结果怎样逼出下一步；最后一步写END",
      "basis_ids": ["U01"]
    }
  ]
}
```

每一步必须是“因为这样做，所以发生了什么”，不能是并列心理概念。上一项的`immediate_consequence`或`new_pressure`必须真实造成下一项的`pressure`；新信息必须有来源，新选择必须有代价。只有感受变化、没有外部动作与反馈，不算行动因果。

## 两位固定主角的人物弧

追加：

```json
{
  "character_arcs": {
    "sumei": {
      "start_position": "苏美开场怎样理解这件事",
      "habitual_action": "她在压力下惯常怎样做",
      "contradiction_exposed": "哪个后果暴露知与行的裂缝",
      "choice_and_cost": "她完成或见证什么有代价的选择",
      "final_action_state": "结尾她的行为、身体和关系位置怎样变化"
    },
    "kaidi": {
      "start_position": "凝香开场怎样理解这件事",
      "habitual_action": "他在压力下惯常怎样做",
      "contradiction_exposed": "哪个后果暴露知与行的裂缝",
      "choice_and_cost": "他完成或见证什么有代价的选择",
      "final_action_state": "结尾他的行为、身体和关系位置怎样变化"
    }
  }
}
```

两人都要变化，但不必同样幅度。禁止固定苏美负责受伤、凝香负责解释；一个人可以先行动，另一个人也必须通过回应、承认误判、停止干预或承担关系后果完成自己的弧。

## 场景计划

追加四至六幕`scene_plan`：

```json
{
  "scene_plan": [
    {
      "scene_id": "SC01",
      "order": 1,
      "scene_title": "来自地点、动作或关系变化的内部标题",
      "story_phase": "trigger|friction|choice|payoff",
      "time_place": "具体时空",
      "entry_state": "人物进入本幕时正在做什么、关系处于什么状态",
      "scene_goal": "本幕必须发生的一个变化",
      "characters_present": ["苏美", "凝香", "配角姓名或稳定称谓"],
      "action_ids": ["A01"],
      "knowledge_change": "本幕前后每个关键人物的知情或误判发生什么变化，来源是什么",
      "causal_bridge": "上一幕哪个结果迫使本幕发生，本幕又怎样逼出下一幕",
      "reality_check": "本幕涉及的时间、路程、金额、物件状态或现实流程怎样成立；无相关项时说明none及原因",
      "sensory_anchor": "影响动作的声音、光线、温度、气味或物件",
      "micro_change": "表情、呼吸、视线、身体距离或心理的可观察变化",
      "exit_pressure": "本幕结尾留下什么必须继续处理的问题；最后一幕写END",
      "image_moment": "最适合成为本幕连环画的一秒"
    }
  ]
}
```

场景不是观点章节。每一幕必须改变人物下一步能做什么；删掉仍不影响故事因果的场景应删除。配角不能只负责递送答案，电话、巧合、突然想起和一次性证词不能替代主角的观察、选择与代价。

## 知行合一检查

追加：

```json
{
  "knowledge_action_alignment": {
    "claimed_or_assumed_knowledge": "人物以为自己已经懂得什么",
    "old_action_evidence": "哪些行为证明他其实没有真正做到",
    "reality_correction": "现实怎样反驳旧行动",
    "new_choice_cost": "新行动为什么不轻松",
    "final_action_evidence": "结尾行为怎样证明认识真正进入行动",
    "verbal_explanation_needed": false,
    "verbal_explanation_reason": "不需要则说明行动为何足够；需要则说明一句轻旁白防止什么事实误读"
  }
}
```

`verbal_explanation_needed`默认`false`。不能因为担心读者“看不懂”就让角色解释隐藏意义；应先加强行动差异、代价和反馈。

所有内容写回`research/source_pack.json`。S2不生成`causal_mindmap.md`或其它附加文档，收据只能由校验器生成。
