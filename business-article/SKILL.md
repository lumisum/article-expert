---
name: business-article
description: 深度科技商业与业务投资分析类微信公众号文章创作技能。从科技事件与产业信号出发，深入拆解商业机制、变现路径、单位经济性（UE）、利润质量、竞争壁垒及资本预期。交付严谨客观的商业认知与验证框架（非个性化投资买卖建议）。纯技术实操请转tech-article。
---

# business-article

## 目标

从一个科技事件、公司动作、产品变化或产业信号出发，沿客户行为、交易结构、收入质量、成本曲线、资本投入、竞争反应和产业权力逐层下潜，最终讲清利润为什么产生、现金为什么留下、超额回报为什么可能持续，以及资本究竟在提前定价什么。

科技只是一枚投入水面的石子，正文研究的是它激起的商业传导。文章不替读者下注，而是帮助读者看懂一门生意怎样运转，并建立能够被后续事实验证或推翻的判断。

## 适用边界

只处理以下公众号文章：

- 科技事件背后的商业机制与利益结构；
- 公司、产品、平台或基础设施的业务模式；
- 客户价值、变现路径、单位经济性与增长质量；
- 产业链位置、竞争格局、渠道、供给与监管约束；
- 资本预期、估值叙事、风险变量与业务投资观察；
- 科技变化对企业经营者、从业者和普通投资观察者的现实影响。

纯技术讲解、教程、代码、架构、排障和操作手册使用`tech-article`。三十五岁以后的人生认知使用`midlife-article`。其它一般主题使用`wechat-article`。本技能不生成股票代码清单、收益承诺、仓位建议、买入卖出点或个性化财务建议。

## 不可变契约

1. **只回答一个底层商业问题**：科技事件必须迅速退场，全文围绕利润来源、价值归属或资本回报中的一个核心矛盾推进。
2. **数字先锁口径**：金额、比例、增速、份额、估值和排名必须锁定日期、单位、币种、范围、分母及独立来源；无法核对就不写确定值。
3. **深度来自因果**：下一层必须是上一层的因，上一层是下一层在现实中出现的果；并列行业知识不算下潜。
4. **技术价值不等于商业价值**：必须追踪技术变化怎样传导到客户行为、交易、收入、成本、利润、现金流、竞争与资本回报。
5. **只培育一个Spark**：围绕同一问题完成加深、拓宽、反证和收束，不建立观点候选池。
6. **必须寻找反方路径**：至少检查“技术成功但商业失败”或“商业增长并非来自技术优势”中的一条。
7. **悟道提炼跨周期规律**：理论和哲学只用于提高解释力，不为权威感排队引用。
8. **致用交付观察框架**：读者获得关键变量、验证信号、反向证据、情景分支和停止判断，而不是买卖指令。
9. **视觉让关系可见**：正文图上部约三分之一呈现真实产品、客户或产业场景，下部约三分之二用白色材质微3D信息块解释价值、因果和判断；两层通过共同主体、色彩、光线和透视自然连接。封面继续沿用`wechat-article`的高上下文标准，每条最终提示词必须超过700个非空白字符。每章一张3:4提示词，至少使用两种视觉角色；只生成提示词，不生成图片。
10. **标题封面共同完成点击**：封面左半呈现熟悉业务场景，右半用白色微3D核心信息图讲清价值关系与阅读回报，中间自然融合；让陌生读者一眼看懂主体、商业冲突和帮助，正文必须真实兑现。
11. **利润是商业逻辑的验尸台**：收入、订单、用户、融资和估值都不能替代利润质量；必须解释增长需要吞下什么成本、资本与风险。
12. **价值创造不等于价值捕获**：必须说明客户得到什么、谁愿意付款、公司为何能拿走一部分价值，以及这部分价值为何不会被上下游或竞争者夺走。
13. **声音来自商业取舍**：活人感来自作者怎样选择事实、追问数字、承认未知并修正判断，不靠投资圈口头禅、虚构内幕、固定反转或表演式第一人称。

商业深度只读取`references/business_depth.md`，具体作者人格与语言只读取`references/author.md`。

## 流水线

完整文章依次完成S0-S6，S7逐图旁白与语音可选。用户已经给定事件、公司、产品、URL或业务问题时从S1开始；用户要求完整公众号文章时必须走到S6。

| 阶段 | 必读文件 | 核心产出 | 校验 |
|---|---|---|---|
| S0 选题 | `references/stage0.md` | 三个科技商业候选问题 | `validate_stage.py --stage 0` |
| S1 见事与商业底座 | `references/stage1.md` + `business_depth.md` | 商业蓝图、逐篇说话位置、可叙事材料、数字与经济事实底座 | `validate_stage.py --stage 1` |
| S2 商业发动机与Spark | `references/stage2.md` + `business_depth.md` + `author.md` | 利润树、五至七层因果主链、导图、一个Spark | `validate_stage.py --stage 2` |
| S3 利润审计、悟道与观察 | `references/stage3.md` + `business_depth.md` + `author.md` | 因果与经济性复核、规律对照、观察框架 | `validate_stage.py --stage 3` |
| S4 成文与HTML | `references/stage4.md` + `business_depth.md` + `author.md` | 两遍成文后的定稿Markdown与可复制HTML | `validate_stage.py --stage 4` |
| S5 正文配图 | `references/stage5.md` | 每章一条3:4配图提示词 | `validate_stage.py --stage 5` |
| S6 标题封面摘要 | `references/stage6.md` | 标题、2.35:1封面提示词、digest | `validate_stage.py --stage 6` |
| S7 逐图旁白与语音，可选 | `references/stage7.md` + `business_depth.md` + `author.md` | 每张正文图五至六句旁白、Edge TTS音频、时长清单与待放图片目录 | `validate_stage.py --stage 7` |

进入每个阶段前必须完整读取对应参考文件。不得凭记忆复述流程，也不得跳过阶段收据直接写最终文章。

## 阶段职责

- **S0只选问题**，不预写结论。
- **S1只确认事件及商业事实底座**，同时盘点客户、付款、收入、成本、资本投入和产业位置已有何种证据与未知，不提前下结论。
- **S2建立商业发动机、利润树和因果深井并培育一个Spark**，必须继续搜索经济机制与行业结构材料，不写正文。
- **S3逐层审核因果、利润形成、现金转换、产业价值分配和资本预期，完成跨周期规律与观察设计**，不写正文。
- **S4把已验证的认知链写成文章**，不临时创造新数字和新判断。
- **S5只做正文图提示词**，用不同视觉角色解释业务关系。
- **S6独立完成标题、封面和摘要**，不改变文章核心判断。
- **S7围绕S5逐图重组连续商业口语叙事并生成同编号语音**，不生成图片、不合成视频。

## 工作目录

```text
${REAL_USER_HOME}/wechat_articles/topics/[topic_id]/
├── research/
│   ├── business_blueprint.json
│   ├── source_pack.json
│   ├── raw_pages/
│   └── stage1_receipt.json
├── article/
│   ├── business_mindmap.md
│   ├── stage2_receipt.json
│   ├── stage3_receipt.json
│   ├── final_article.md
│   ├── final_article_copy.html
│   ├── final_article_digest.txt
│   └── stage4_receipt.json
├── assets/
│   ├── image_prompts.jsonl
│   ├── title_cover_package.json
│   ├── stage5_receipt.json
│   └── stage6_receipt.json
└── video/
    ├── narration_segments.jsonl
    ├── audio_manifest.json
    ├── images/
    ├── audio/
    │   └── section_01.mp3
    └── stage7_receipt.json
```

S0使用`${REAL_USER_HOME}/wechat_articles/business_scans/[scan_id]/`，不把候选扫描文件放进正式主题目录。

## 执行纪律

- 阶段完成后立即运行对应校验；失败时停在当前阶段。
- 收据只能由`validate_stage.py`生成，并绑定当前协议版本。
- `final_article_copy.html`只能由`scripts/markdown_to_wechat_html.py`从`final_article.md`生成。
- HTML不泄漏DATA、DESCENT、SPARK、REBOUND或IMAGE施工标记。
- 在线研究先用Google发现国外原始页面，再通过CDP保存真实页面；搜索摘要不进入证据池。研究不能在产品发布信息处停止，必须继续追到客户、定价、成本、资本开支、竞争与产业链证据。
- 财报、公告、监管文件、公司投资者关系材料和原始数据优先于媒体转述。
- 公司陈述只证明公司这样披露过，不自动证明市场接受、竞争优势或未来兑现。
- 不生成流程未声明的报告和临时说明文件。
- S7通过后，用户只需把S5正文图片按对应ID放入`video/images/`；整个`video/`目录随后可由`narrated-video`直接消费。
