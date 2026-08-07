<div align="center">

# 🚀 Article Expert (article-skills)

**专为高质量微信公众号深度创作、商业/技术/情感分析、上市企业财报审读与短视频合成打造的工业级 AI Agent 技能库**

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)
![Architecture](https://img.shields.io/badge/Architecture-S0--S7%20Phased%20Workflow-orange.svg)
![Agent Framework](https://img.shields.io/badge/Agent-Google%20Antigravity-purple.svg)

<p align="center">
  <a href="#-项目特色">项目特色</a> •
  <a href="#-技能矩阵">技能矩阵</a> •
  <a href="#-流水线工作流-s0s7">流水线工作流</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-关注公众号">关注公众号</a>
</p>

---

</div>

## 💡 项目特色

`article-expert` 是一套严谨、模块化且高水准的 AI Agent Skill 体系。区别于常规的简单文本拼接生成，本技能库建立了**强约束的因果下潜机制、真实网页证据链落盘与自动化校验收据门禁**：

* 🧠 **5~7 层因果深度下潜**：拒绝泛泛而谈与名词堆砌，沿“事实入口 ➔ 表面答案失效 ➔ 核心下潜 ➔ 规律照明 ➔ 现实回升”路线推演，培育独特认知火花（Spark）。
* 📸 **CDP 浏览器真实证据链落盘**：内置真实浏览器 CDP 协议抓取，将强事实、数据口径与引用回查快照落盘保存，杜绝虚构与幻觉。
* 🎨 **微信排版美学与高上下文 Visual 语法**：内置 54KB+ 专属 `markdown_to_wechat_html.py` 渲染引擎，并提供“现实场景 + 白色微 3D 信息图”的极佳配图与封面提示词系统。
* 🛡️ **严格的阶段门禁收据（Stage Receipts）**：S0~S7 各阶段绑定 Python 确定性校验脚本，只有通过上一阶段校验生成 `stageX_receipt.json`，Agent 方可推进至下一阶段。

---

## 🧰 技能矩阵

项目包含 7 大专业 Agent 技能模块，各司其职，无缝协作：

| 技能名称 (Skill ID) | 核心定位与适用场景 | 关键交付产物与特色 |
| :--- | :--- | :--- |
| ✍️ [**`wechat-article`**](file:///Users/elonmar/GitHub/article-expert/wechat-article) | **通用中文深度公众号文章** | 适用于文化、哲理、社会观察与通用认知主题。提供 5-7 层深度因果推演与内联 HTML 排版。 |
| 💻 [**`tech-article`**](file:///Users/elonmar/GitHub/article-expert/tech-article) | **技术讲解与实操 Playbook** | 覆盖 AI/LLM/Agent、软件工程、架构及 API。强调机制原理解析、精确版本锚定与无死角实操/排障闭环。 |
| 📊 [**`business-article`**](file:///Users/elonmar/GitHub/article-expert/business-article) | **科技商业与业务投资分析** | 深入拆解商业机制、变现路径、单位经济性（UE）、利润质量、竞争壁垒及资本预期（非买卖建议）。 |
| 🕯️ [**`midlife-article`**](file:///Users/elonmar/GitHub/article-expert/midlife-article) | **中年人生认知与情感叙事** | 专注 35+ 人生经历（职业、代际、婚姻家庭、身体健康）。结合故事下潜与东西方哲学照明，拒绝流量焦虑。 |
| 📈 [**`equity-fundamentals-review`**](file:///Users/elonmar/GitHub/article-expert/equity-fundamentals-review) | **美/A股上市公司基本面审读** | 面向 SEC EDGAR / 巨潮 CNINFO 官方财报与业绩会，提供审计级研究判断及五色视觉信号系统（🟢🔴🟡🔵⚪）。 |
| 🎨 [**`codex-image-gen`**](file:///Users/elonmar/GitHub/article-expert/codex-image-gen) | **Codex 高质图像生成** | 基于本地 Codex CLI（驱动 `gpt-image-2` / `gpt-5.4-mini`），支持自定义 Prompt、比例（3:4/16:9）与自动重试。 |
| 🎙️ [**`narrated-video`**](file:///Users/elonmar/GitHub/article-expert/narrated-video) | **画音同步纵向短视频合成** | 自动匹配编号配图与 Edge TTS 旁白语音，生成 0.6s 优雅交叉淡化转场与 3:4 纵向 MP4 成片。 |

---

## 🔄 流水线工作流 (S0~S7)

完整的深度文章创作遵循严格的 8 阶段递进流程：

```text
[S0 选题门禁] ──> [S1 见事与底座] ──> [S2 机制链/Spark] ──> [S3 验证与悟道致用]
                                                                  │
[S7 短视频口播] <── [S6 标题与封面] <── [S5 章节高上下文配图] <── [S4 定稿与HTML排版]
```

1. **S0 选题确认**：评估检索与收藏价值，确定 3 个高质量读者候选问题。
2. **S1 见事与底座**：确定 `article_profile` 模式，完成强事实搜索与 CDP 网页快照保存。
3. **S2 机制与 Spark 生长**：多轮因果推演，形成机制导图，在最低点培育 Spark。
4. **S3 验证与致用**：复核下潜有效性，进行跨周期规律总结（哲学照明）与现实行动指南设计。
5. **S4 成文与 HTML 转换**：两遍精修成文，自动转化为微信公众号专属 HTML 格式。
6. **S5 正文配图提示词**：每个 `##` 章节生成一条包含双层视觉表达的 3:4 高上下文提示词。
7. **S6 标题、封面与摘要**：生成同频高点击力标题、2.35:1 封面提示词与 Digest 摘要。
8. **S7 口播与短视频（可选）**：配套生成 3-5 分钟逐图旁白文案、TTS 音频与短视频。

---

## ⚡ 快速开始

### 1. 环境依赖
确保本地安装 Python 3.10+、Codex CLI（如需图片生成）及 FFmpeg（如需视频合成）：

```bash
# 验证 Python 环境
python3 --version
```

### 2. 阶段校验脚本调用示例
每个技能子目录都提供独立的阶段校验脚本：

```bash
# 以 business-article 技能为例运行阶段 1 校验
python3 skills/business-article/scripts/validate_stage.py --stage 1 --topic-dir ~/wechat_articles/topics/demo_topic
```

---

## 📱 关注公众号

如果您对 **AI Agent 落地实践、大模型技术演进、商业底层拆解与深度内容创作** 感兴趣，欢迎关注我们的官方微信公众号！

<div align="center">

<img src="gzh_code.jpg" width="280" alt="微信公众号二维码" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">

<br>

**👇 扫描上方二维码，关注公众号「文章专家」**

*获取最新 AI Agent 深度洞察、排版实战干货与优质原创好文！*

</div>
