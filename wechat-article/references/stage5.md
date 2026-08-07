# Stage 5：配图点位 + 正文配图提示词

进入本阶段前完整读取本文件。本阶段在**定稿文章已经作者化完成**之后执行：先分析最终正文，构思每章配图点并写入占位符，再生成高上下文提示词。本阶段只生成提示词，不生成图片。

每个 `##` 大章节对应一张 3:4 正文图，不生成 cover、global 或 closing 图。

Stage 2、Stage 3和Stage 4 **不应**预先埋占位符。若定稿里已有旧占位，先按本章规则重审位置与语义，再统一重写提示词。

## 执行顺序（强制）

1. **通读** `article/final_article.md`，按章节理解：每章作者判断、核心冲突、读者该带走什么。
2. **构思配图点**：每章选一处章内换气位置（通常在 2–4 个自然内容块之后，不紧贴 `##` 标题，不插进代码围栏中间），能托住该章最该被看见的机制/冲突/结果。
3. **写入占位符**：在 `final_article.md` 对应位置插入连续的 `<!-- IMAGE:section_XX -->`（从 `section_01` 起，数量 = `##` 章节数，一一对应、不可跳号）。
4. **生成** `assets/image_prompts.jsonl`：每行一张图，字段完整，提示词高上下文。
5. **重建 HTML**：运行 `markdown_to_wechat_html.py`，让 `final_article_copy.html` 同步出现占位节点。
6. **准出校验**。

## 高上下文原则

视觉提示词不能为了节省 token 而缩写。正文图的生成质量依赖完整的文章语境、信息目标、可视元素、空间构图、色彩分工和材质光影。每条提示词必须独立可用，不能假设图片模型读过文章或上一张图。

统一使用白色材质微 3D 编辑插图：明亮白色空间、细腻塑料/磨砂玻璃/金属与题材所需的自然材质、柔和真实阴影、清晰空间层次。技术与商业内容可以使用信息图关系；人生、文化和哲理内容可以使用具体场景、物件关系或克制的视觉隐喻。保留足够丰富的主题元素和颜色，不做空洞的抽象氛围图。

## 模式化视觉语言

先读取完整`article_profile`，继承文章类型、子类型和`visual_mode`；高上下文、3:4、每章一图和完整画布利用规则保持不变：

- `human_scene`：使用`white_cinematic_human_micro_3d`。每张图必须有一位或多位符合文章关系的成年人作为主要主体，优先呈现35–55岁人物；写清年龄感、姿态、目光、手部动作、人与空间或物件的距离，以及能暴露生活痕迹的具体场景。画面要有由文章决定的真实环境和可感知氛围，使用克制的电影式光线、空气层次和情绪色温。不能画成流程图、悬浮图标、数据看板或抽象物件拼盘，也不能只有背影和空房间。正文人生图默认不放文字；确有必要时只允许0–1个自然存在于便签、门牌、手机或物件表面的中文短语，禁止漂浮标签。
- `tech_business_scene`：使用`white_material_micro_3d`，以真实产品、企业角色、资金或价值流、竞争位置和结果关系构图；可以信息图化，但必须让商业关系一眼可见。
- `tech_playbook_scene`：使用`white_material_micro_3d`，以真实设备、界面、代码、连接、操作步骤、错误状态和验证结果构图；每张图帮助读者理解一个可执行动作，不做概念海报。

## 细腻度

白色系不等于纯白背景上摆放几个图标。每张图必须同时具有主体层、解释层和环境层，并在不拥挤的前提下加入能支撑真实感的微观细节。

- 为绝对主体和关键辅助物分别写清几何形态、尺度、朝向、空间位置、边缘处理、表面纹理、材质厚度、颜色和相互作用，不能只报元素名称。
- 白色空间使用冷暖不同的白、浅灰台面、半透明隔板、承托结构或空间框架建立层次；留白必须承担聚焦和分区作用，不能成为空洞背景。
- 材质至少体现哑光塑料、磨砂玻璃、阳极金属、纸张、织物或陶瓷中的合理组合，并描述倒角、接缝、厚薄、粗糙度、透光和反射差异。
- 明确镜头高度、观察角度、透视强弱和焦点位置。3:4 竖幅应利用完整高度形成纵深，不把所有元素缩在画面中央。
- 光照必须说明主光、补光、接触阴影、环境遮蔽和高光方向；物体要真正落在空间里，不能像无重量的贴纸。
- 微观细节用于证明功能和关系，例如接口、刻度、状态灯、轨道、卡槽、纸张边缘、玻璃厚度和局部磨损。细节必须来自本章内容，不添加无信息装饰。
- 中文标签要成为画面中的实体信息层，说明标签载体、位置、字号层级和指向关系，不能随机漂浮在物体旁边。

## 3:4 构图

- 上部建立主题与环境，中部呈现核心机制或动作，下部交付结果、代价或对比；
- 同时安排前景、中景、背景，明确左右宽度、安全边距、视觉动线和留白用途；
- 以一个主色建立章节识别，再用 3-4 个辅助色区分角色、阶段、关系、数据、情绪变化或结果；
- 使用 6-10 个可画的具体元素，围绕一个绝对主体和一条可见关系组织，不能只写抽象节点；
- 科技图使用3–5个中文短标签帮助读者看懂机制；`human_scene`使用0–1个场景内自然文字。所有画面文字必须是中文，每个标签不超过8个字；
- `human_scene`只使用`human_scene`或`editorial_scene`；`tech_business_scene`可选`hub_and_spoke`、`before_after`、`layer_stack`、`data_scene`或`mechanism_scene`；`tech_playbook_scene`可选`pipeline`、`cycle`、`before_after`、`layer_stack`或`mechanism_scene`。视觉类型服从本章内容，不跨模式混用。

## image_prompts.jsonl

每行一张图，字段必须完整：

```json
{
  "image_id": "section_01",
  "image_type": "section",
  "article_mode": "technology",
  "article_subtype": "practical_playbook",
  "section_title": "章节标题",
  "section_anchor": "这张图对应正文里的具体事实或机制",
  "aspect_ratio": "3:4",
  "style_profile": "white_material_micro_3d",
  "visual_mode": "tech_playbook_scene",
  "accent_color": "主色名称 #HEX",
  "supporting_colors": ["辅助色 #HEX", "辅助色 #HEX", "辅助色 #HEX"],
  "image_purpose": "为什么本章需要这张图",
  "visualized_point": "读者一眼必须看懂的核心判断",
  "core_conflict": "画面要呈现的冲突、变化或因果",
  "reader_takeaway": "看图后读者多懂什么",
  "numeric_claim_ids": [],
  "visual_elements": ["具体元素一", "具体元素二", "具体元素三", "具体元素四", "具体元素五", "具体元素六"],
  "diagram_type": "mechanism_scene",
  "ratio_composition_plan": "如何充分使用 3:4 竖幅",
  "composition_plan": "上中下、左右、前中后景、视觉动线与安全边距",
  "detail_density_plan": "主体、辅助信息、留白和细节密度",
  "camera_plan": "镜头高度、观察角度、透视强弱和焦点位置",
  "material_detail_plan": "主要元素的材质、厚度、倒角、接缝、粗糙度与透光反射",
  "lighting_plan": "主光、补光、接触阴影、环境遮蔽和高光方向",
  "atmosphere_plan": "人物情绪、空间空气感、时间感和综合色温；科技图写整体视觉气质",
  "surface_detail_plan": "服务内容理解的接口、刻度、卡槽、边缘与其他微观细节",
  "color_plan": "主色与辅助色分别表达什么信息",
  "chinese_labels": ["中文标签", "中文标签", "中文标签"],
  "required_text": "必须准确出现的中文文字",
  "image_prompt": "不少于 1000 个非空白字符的完整中文生成提示词",
  "image_status": "pending",
  "attempts": 0,
  "output_filename": "section_01.png"
}
```

`image_prompt` 必须把以上语境与视觉字段转写为连贯、可直接交给图片模型的中文指令，并明确：

1. 文章标题、本章标题与这张图在全文中的作用；
2. 核心判断、冲突和读者收益；
3. 6-10 个元素各自的形态、位置、尺度、朝向、材质、表面细节和关系；
4. 3:4 画布的上中下、前中后景、安全边距、镜头与焦点；
5. 主色和辅助色的信息分工，主光、补光、接触阴影、环境遮蔽与高光；
6. 材质厚度、倒角、接缝、粗糙度、透光反射和内容相关的微观细节；
7. 3-5 个中文标签的实体载体、位置、层级和指向关系；
8. 禁止英文、抽象光球、空洞背景、元素拥挤、主体过小、低对比、无信息装饰。

画面标签和视觉关系不得新造金额、比例、排名、年份或规模。确需可视化正文数字时，填写对应的`numeric_claim_ids`并严格使用账本`publish_text`；没有数字时保留空数组。

`image_id` 从 `section_01` 连续递增，数量和顺序与 `##` 章节完全一致。HTML 保持纯占位，不写本地图片路径。

## 产物

1. 更新后的 `article/final_article.md`（已插入配图占位符）
2. `assets/image_prompts.jsonl`
3. 重建后的 `article/final_article_copy.html`

## 准出

```bash
python skills/wechat-article/scripts/markdown_to_wechat_html.py --topic-dir /absolute/topic/path
python skills/wechat-article/scripts/validate_image_outputs.py --topic-dir /absolute/topic/path
```
