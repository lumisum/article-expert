# Stage 0：读者问题选题

进入本阶段前完整读取本文件。本阶段只负责发现三个值得长期创作的读者问题，准出后等待用户选择；不建立文章结构，不预写正文结论，也不替S6确定最终标题。

## 工作目录

每次扫描使用独立目录：

```text
${REAL_USER_HOME}/wechat_articles/topic_scans/[scan_id]/
└── research/
    ├── topic_candidates.json
    ├── topic_candidates.md
    └── raw_pages/
```

`scan_id` 使用稳定、可区分的批次标识。不得把扫描文件放入尚未确认的主题目录，也不得使用字面量`~`。

## 发现方向

不追踪实时热点。寻找读者会长期搜索、反复遇到、值得收藏或转发的问题。题材可以是技术、商业、产品、行业、人生、文化、哲理或日常经验，新事件只作为理解常青问题的入口。

候选优先落入本技能的两条稳定主线：面向35岁以后读者的人生认知，或科技事件/科技实操。科技事件必须能够继续拆出商业、投资或产业判断；科技实操必须有形成可复制方案的可能。宏大科技叙事、纯新闻摘要、泛人生鸡汤和没有实践抓手的产品介绍不进入前三。

优先发现：

- 反复失败的任务和真实选择压力；
- 表面熟悉、底层机制容易误判的问题；
- 会造成时间、金钱、机会或判断损失的困境；
- 专业问题背后连接的普遍处境；
- 三个月后仍然值得搜索的内容。

## 信息扫描

1. 先通过当前CDP打开Google，围绕读者问题、常见失败、自然搜索问句和相邻表达执行多组检索。
2. 比较Google结果后进入原始页面，再按需要进入产品文档、官方帮助、GitHub issues、工程博客、Reddit、HN、可靠分析和真实讨论；垂直站点用于补充，不替代Google发现。
3. 使用`scripts/cdp_capture_pages.py`保存6–10个代表性原始页面，至少成功5个，覆盖官方/技术、用户讨论、独立分析中至少三类。
4. 页面写入本次扫描目录的`research/raw_pages/`；不得硬编码浏览器端口。Google搜索结果页和结果摘要只用于发现链接，不作为候选证据。
5. 流量判断不能只看圈内热度，要同时判断搜索、收藏、转发、受众扩张和信任风险。

## 候选判断

只保留最强三个。每个候选都要回答：

- 谁在什么场景反复遇到；
- 读者会主动搜索哪句话；
- 不解决会浪费、做错或错过什么；
- 文章能交付什么判断、步骤或观察方式；
- 三个月后为什么仍值得读；
- 核心读者、相邻读者和大众读者从哪里进入；
- 扩大受众到哪里会开始失真；
- 有哪些可继续研究的原始材料。

`topic_title`只负责让用户看懂候选，不预定最终标题。`article_type`使用`life_insight`、`tech_event_business_investment`或`tech_practical_playbook`，作为S1正式路由的初步判断。每个候选给出可用于S1目录的`topic_id`。

## topic_candidates.json

```json
{
  "stage": "topic_candidates",
  "scan_id": "scan-identifier",
  "scan_summary": {
    "planned_url_count": 8,
    "successful_capture_count": 6,
    "source_categories": ["官方与技术", "用户讨论", "独立分析"]
  },
  "candidates": [
    {
      "rank": 1,
      "topic_id": "stable-topic-id",
      "topic_title": "面向读者问题的候选主题",
      "article_type": "tech_practical_playbook",
      "material_anchor": "支撑问题的事件、案例、产品行为或讨论",
      "reader_problem": "具体读者、场景和问题",
      "reader_search_query": "读者会主动输入的自然搜索问句",
      "reader_payoff": "读者能够完成、避免、节省、选对或判断什么",
      "audience_expansion": {
        "core_audience": "原本就关心主题的人",
        "adjacent_audience": "面对相似矛盾的人",
        "broad_audience": "无需专业背景也能进入的人",
        "familiar_entry": "连接三层人群的熟悉处境",
        "overreach_boundary": "继续扩大就会失真的边界"
      },
      "payoff_types": ["judgment"],
      "payoff_detail": {
        "before_state": "当前卡点、损失或选择压力",
        "after_state": "读完后可观察的变化",
        "use_scene": "会在哪个现实任务中使用",
        "proof_basis": "收益由哪些事实或案例支撑",
        "boundary": "不适用条件与不能承诺的范围"
      },
      "evergreen_reason": "为什么三个月后仍值得读",
      "core_hook": "来自真实材料的冲突、代价或反差",
      "traffic_case": "搜索、收藏、转发潜力与最大风险",
      "evidence": [
        {"url": "https://...", "visible_signal": "页面中的关键信号"}
      ]
    }
  ]
}
```

`candidates`恰好三个。同步写`topic_candidates.md`，向用户展示三个候选并等待选择。

## 准出

```bash
python skills/wechat-article/scripts/validate_topic_candidates.py --topic-dir /absolute/scan/path
```
