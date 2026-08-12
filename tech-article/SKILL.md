---
name: tech-article
description: 专业的技术类微信公众号文章全流程创作技能。覆盖 AI/LLM/Agent、软件工程、底层架构、API及开发工具的深度技术讲解（Technical Explainer）与可复现实操指南（Hands-on Playbook）。强调机制原理解析、精确版本锚定、真实施障排障路径及无死角代码/实操闭环。商业投资分析请转business-article。
---

# tech-article

把一个技术问题讲透，并把“看懂”变成“能做、能验、能排障、能优化”。

## 适用边界

本技能只处理两类文章：

1. **技术讲解 `technical_explainer`**：解释一个模型、协议、框架、产品能力或工程机制怎样工作，帮助读者形成准确心智模型并作出技术选择。
2. **实操抄作业 `hands_on_playbook`**：从真实目标、阻力、失败、修复、验证和优化出发，交付读者可以复现的实施路径。

主题核心是公司业务模式、产业竞争、资本预期或业务投资判断时，使用`business-article`。主题核心是三十五岁以后的人生经历与认知时，使用`novel-expert`。一般非技术公众号文章使用`wechat-article`。

## 核心标准

1. **先确定读者任务**：文章必须回答“读者想完成什么、现在卡在哪里、读完后能多做成什么”。
2. **机制先于术语**：从输入、处理、状态、输出、边界和失败条件解释技术，不用名词堆砌代替理解。
3. **证据接近源头**：优先官方文档、规范、源码、仓库、论文、发布说明和可复现实验；二手文章只用于发现线索。
4. **版本必须钉住**：涉及接口、配置、命令、行为或性能时，记录版本、日期、平台和前置条件。
5. **实操必须闭环**：每个小目标都走“想做什么 → 卡在哪 → 怎么解决 → 如何验证 → 后续怎么优化”。
6. **代码必须诚实**：可运行代码与伪代码明确区分；不得虚构API、参数、输出、性能数字或兼容性。
7. **失败路径不可省略**：至少说明一个高概率错误、识别信号、原因和修复办法。
8. **作者带路**：文章像懂技术的人陪读者一起做，不像说明书、研究报告、发布会复述或AI拼接稿。
9. **帮助必须兑现**：标题、导读、正文和结尾都自然落到读者能够获得的判断、能力、效率或风险规避。
10. **后台有来源，前台无脚手架**：最终文章不放脚注、引用编号、资料清单和内部标记；确需引用原话时直接使用准确中文。
11. **视觉保持高上下文**：正文图上部约三分之一呈现读者正在操作或观察的真实技术场景，下部约三分之二使用白色材质微3D信息块解释机制、步骤和故障路径；封面左半呈现真实技术场景，右半呈现白色微3D核心信息图。上下或左右两层都必须通过共同主体、色彩、光线和透视自然连接，每条最终提示词必须超过700个非空白字符。
12. **声音来自真实取舍**：活人感来自作者实际掌握的材料、验证过程、判断变化和不确定边界，不靠口头禅、粗口、假装亲测或固定反转句式。

## 阶段纪律

严格按阶段执行。开始任何阶段前，必须完整读取该阶段参考文件和`references/author.md`，不得凭记忆补写。阶段产物通过校验后才能进入下一阶段。

| 阶段 | 必读文件 | 核心产物 | 校验 |
|---|---|---|---|
| S0 选题 | `references/stage0.md` | 三个读者会主动搜索的技术问题 | `validate_stage.py --stage 0` |
| S1 技术底座 | `references/stage1.md` | 技术蓝图、逐篇说话位置、可叙事材料与证据包 | `validate_stage.py --stage 1` |
| S2 机制与复现 | `references/stage2.md` | 技术思维导图、机制链、实施链与Spark | `validate_stage.py --stage 2` |
| S3 技术审校 | `references/stage3.md` | 独立机制审校、复现审校与读者作业单 | `validate_stage.py --stage 3` |
| S4 成文排版 | `references/stage4.md` | 两遍成文后的定稿Markdown与可复制HTML | `validate_stage.py --stage 4` |
| S5 正文配图 | `references/stage5.md` | 每个大章节一条3:4配图提示词 | `validate_stage.py --stage 5` |
| S6 标题封面 | `references/stage6.md` | 标题、2.35:1文章封面、跨平台视频封面JSONL与摘要 | `validate_stage.py --stage 6` |
| S7 逐图旁白与语音，可选 | `references/stage7.md` | 与正文配图逐一对应的旁白、Edge TTS音频、时长清单与待放图片目录 | `validate_stage.py --stage 7` |

用户要求“完整公众号文章”时，必须依次完成S0至S6；用户已经明确主题时可跳过S0。S7仅在用户明确需要逐图视频旁白或配套语音时执行。用户在定稿后提出疑问或修改建议时，回到相关阶段补充研究或重做推理，再重新执行受影响阶段的校验，不得只做表面润色。

## 工作目录

所有正式产物只能写入操作系统当前登录用户的：

`/Users/<login-user>/wechat_articles/topics/[topic_id]/`

S0临时扫描写入：

`/Users/<login-user>/wechat_articles/tech_scans/[scan_id]/`

禁止写入沙盒目录、项目仓库、字面量`~/`目录或`topics/_stage*`。使用`scripts/path_utils.py`解析真实用户目录。

## 阶段事务

每个阶段执行：

1. 读取前序回执并确认未过期；
2. 读取本阶段参考文件；
3. 完成研究、推理或写作；
4. 写入约定产物；
5. 运行`python skills/tech-article/scripts/validate_stage.py --stage N --topic-dir /absolute/topic/path`；
6. 只有看到`PASS`和新回执后才宣布阶段完成。

S0使用`--scan-dir`。校验脚本只负责结构、路径、证据链、版本边界、复现链和最终文件完整性；文章洞察、语言魅力与标题点击力必须由模型按参考文件审读。

## 研究与工具

- 检索入口优先Google，再进入官方原始链接；对登录页、动态页和需要浏览器渲染的页面，使用随技能提供的CDP脚本。
- CDP端点由Beneva环境变量或脚本默认的`127.0.0.1:19222`发现，不在提示词和业务脚本中另写浏览器端口。
- S1至S3都可以继续搜索和补抓页面，不能把S1误认为唯一研究阶段。
- 抓取页面保存到当前主题的`research/raw_pages/`，并在证据包中列出实际选用文件。
- S4的`final_article_copy.html`只能由`scripts/markdown_to_wechat_html.py`从`final_article.md`生成，禁止LLM手写HTML或另造模板。
- S5和S6只生成配图提示词，不生成真实图片。

## 完成定义

完整交付至少包含：

- `research/tech_blueprint.json`
- `research/source_pack.json`
- `research/raw_pages/`
- `article/technical_mindmap.md`
- `article/final_article.md`
- `article/final_article_copy.html`
- `article/final_article_digest.txt`
- `assets/image_prompts.jsonl`
- `assets/title_cover_package.json`
- `assets/video_cover_prompts.jsonl`
- S1至S6阶段回执

执行S7时额外交付：

- `video/narration_segments.jsonl`
- `video/images/`，预留给用户放入同编号正文图片
- `video/audio/section_1.mp3`至`section_N.mp3`
- `video/audio_manifest.json`
- S7阶段回执

S7通过后，用户只需把S5生成的正文图片按对应ID放入`video/images/`。随后整个`video/`目录可由`narrated-video`直接消费；本技能不合成MP4。

最终向用户报告时，说明文章模式、读者获得的实际帮助、验证过的技术环境、各阶段状态和最终HTML绝对路径。
