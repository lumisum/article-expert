# S5：正文配图提示词

只生成正文配图提示词，不生成图片。每个大章节一张，不生成global、opening或closing图。

## 统一视觉

- 比例严格为3:4，按竖向画幅组织上、中、下三层；
- 保留`white_material_micro_3d`高上下文骨架，并使用`cool_porcelain_tech`专属配色；
- 主背景固定为冷瓷白`#EEF3F6`，通过冷白、浅钢灰、磨砂玻璃、半透明层板和精密接触阴影形成洁净实验室与开发工具般的空间，不使用纯白空底或大面积深色科技背景；
- 电光蓝`#1677FF`负责主数据流和关键动作，青绿`#11A8A5`负责成功状态与有效路径，靛紫`#6256D9`负责分支与抽象层，珊瑚红`#E25B5B`只用于错误、阻塞和风险；
- 每张图都同时包含可识别的技术操作场景与信息解释层；信息解释层由全文一次性选择为`micro_3d_info_cards`或`micro_3d_editorial_illustration`，不得章节间混用；
- 场景固定在上部，约占30%至35%；信息层固定在下部，约占65%至70%；
- 上方三分之一呈现读者正在操作或观察的真实设备、界面、代码、终端、错误状态或系统现场；下方三分之二使用白色材质微3D信息卡，或用富配色微3D编辑插画概括机制、数据流、步骤或故障路径；
- 中间保留约8%至15%的融合过渡带，不使用横线、色块边界、上下分栏或两张图硬拼；
- 信息层必须解释本章一个具体问题；信息卡可使用架构流、数据流、时序、分层、对比、生命周期或排障路径，插画则只用一个原创技术物理隐喻概括其中的决定性机制；
- 信息卡模式使用七至十二个有职责的视觉元素；插画模式只使用四至七个有职责的元素，其中一个是承担隐喻的主物件；两种模式都使用一个主色和三至四个辅助色；
- 充分利用画幅高度，不把元素挤在中间；
- 只出现准确中文，专有技术名词确需保留时可以使用原始拼写；
- 不用抽象芯片、发光大脑、漂浮图标或无意义代码雨代替机制。

## 全文信息层视觉系统（先于单张图选择）

先通读所有章节，写入`assets/image_visual_system.json`：

```json
{
  "version": "article_information_visual_system_v1",
  "information_visual_mode": "micro_3d_info_cards|micro_3d_editorial_illustration",
  "selection_signals": ["至少两条来自全文的选择依据"],
  "selection_reason": "为何这一篇文章整体更适合此方式",
  "article_visual_thesis": "整组配图共同传达的技术判断",
  "uniformity_rule": "所有正文配图必须使用同一information_visual_mode，不得混用"
}
```

逐章判断“精确机制需求”与“具身理解需求”。若至少半数关键章节需要读者准确跟随多步数据流、接口关系、时序、代码状态、参数对比或排障分支，使用`micro_3d_info_cards`。若至少半数关键章节的核心障碍是理解一个机制的直觉、状态变化、操作后果或单一关键动作，且没有核心章节依赖复杂精确架构，使用`micro_3d_editorial_illustration`。证据势均力敌时选择信息卡。

插画模式借鉴“单一认知动作 + 新鲜物理隐喻 + 稀疏标注”的编辑插画方法，而不是复刻外部固定角色、单色手绘线稿、纯白底或既有案例。下部信息层仍是`cool_porcelain_tech`的微3D空间：一个厚实圆角的设备、端口、线缆、容器或怪而成立的工具承担隐喻；电光蓝、青绿、靛紫、珊瑚红分别承担主动作、有效路径、抽象分支和错误风险，色彩丰富但只服务状态。

## 上下层的自然过渡

- **共享主体**：上方场景中的设备、屏幕、代码行、终端输出、接口、数据包或错误状态至少有一个跨越过渡带，并成为下方信息结构的入口；
- **色彩迁移**：下方以冷瓷白`#EEF3F6`、浅钢灰和半透明信息块为主体，只继承上方一至两个点睛色区分输入、状态、风险和结果；颜色逐渐降低饱和度和面积；
- **光线延续**：上下使用同一主光方向、色温、高光、接触阴影和环境遮蔽，让信息块像真实存在于操作场景的延伸空间中；
- **透视延续**：桌面、屏幕、机柜、设备边缘或数据轨迹的透视线继续进入下方，镜头高度和消失点保持一致；
- **材质转化**：信息卡模式中，上方真实技术对象在过渡带逐渐剖开、展开或简化成白色微3D模型、节点、卡块和路径；插画模式中，它生长为一个厚实圆角、带倒角和接触阴影的微3D技术隐喻场景，不能突然变成扁平手绘或平面流程图；
- **白色信息优先**：信息卡模式以下方白色立体卡块、层板、管道、节点、端口和剖面为主体；插画模式保留冷瓷白基底，但让三至四种领域色分布在关键对象、路径与状态上，避免大面积无语义彩色底板。

每张图必须完整说明：

- 技术主体和辅助元素的形态、尺度、朝向、空间位置与交互关系；
- 3:4画布的上中下、左右、前中后景、安全边距、留白用途和视觉动线；
- 镜头高度、观察角度、透视强弱和焦点位置；
- 哑光塑料、磨砂玻璃、阳极金属、屏幕、纸张或设备表面的厚度、倒角、接缝、粗糙度、透光与反射；
- 主光、补光、接触阴影、环境遮蔽和高光方向；
- 接口、端口、状态灯、代码行、错误标记、卡槽和设备边缘等服务技术理解的微观细节；
- 主色及三至四个辅助色分别承载的状态、路径、风险和结果；
- 信息卡模式使用三至五个准确中文短标签的实体载体、位置、层级和指向关系；插画模式只用零至三个短标签，避免把隐喻重新写成说明书。

## 章节适配

每条提示词必须先回答：

1. 本章读者在做什么或观察什么；
2. 哪个机制最难理解；
3. 画面怎样把操作现场与内部机制对应起来；
4. 读者看图后能少误解什么。

`technical_explainer`偏向结构、数据和因果；`hands_on_playbook`偏向界面、代码、终端、错误信号和修复路径，但都必须保留信息层。

## 输出

写入`assets/image_prompts.jsonl`，每行一个JSON对象：

```json
{
  "id": "section_1",
  "section_title": "章节标题",
  "visual_role": "hybrid_context_info",
  "aspect_ratio": "3:4",
  "style_profile": "white_material_micro_3d",
  "layout_ratio": "scene_30_info_70|scene_33_info_67|scene_35_info_65",
  "scene_position": "top_third",
  "information_position": "lower_two_thirds",
  "palette_profile": "cool_porcelain_tech",
  "background_color": "冷瓷白 #EEF3F6",
  "background_material": "冷白与浅钢灰层次、磨砂玻璃、半透明层板和精密接触阴影",
  "information_form": "architecture_flow/data_flow/sequence/layers/comparison/lifecycle/troubleshooting_path",
  "information_visual_mode": "micro_3d_info_cards|micro_3d_editorial_illustration",
  "information_rendering": "本章信息层怎样以全文选定模式呈现",
  "editorial_illustration_structure": "仅插画模式：action_metaphor|state_tableau|before_after_tableau|route_metaphor|layered_tableau|relationship_tableau",
  "editorial_metaphor": "仅插画模式：一个由本章技术对象支持的原创物理隐喻",
  "editorial_action": "仅插画模式：设备、数据或操作者承担的关键动作",
  "editorial_color_roles": "仅插画模式：四种技术色如何服务主动作、路径、分支和风险",
  "article_context": "本章前因后果",
  "reader_action_or_observation": "操作场景",
  "scene_layer": "上部设备、界面、代码、终端或错误状态的真实技术现场",
  "information_question": "这张图要解释的问题",
  "information_layer": "白色微3D信息卡或富配色微3D编辑插画中的机制、步骤和关系",
  "visual_bridge": "场景如何与信息层连接",
  "shared_anchor": "跨越两层的设备、代码、接口、数据或错误状态",
  "transition_plan": "8%至15%融合带中，技术场景怎样剖开、展开或转化为信息结构",
  "transition_color_plan": "上方场景颜色怎样自然迁移到下方白色信息块",
  "transition_light_plan": "上下如何共享主光、色温、高光和接触阴影",
  "transition_perspective_plan": "透视线、镜头高度和消失点怎样连续",
  "accent_color": "电光蓝 #1677FF",
  "supporting_colors": ["青绿 #11A8A5", "靛紫 #6256D9", "珊瑚红 #E25B5B"],
  "visual_elements": ["具体元素一", "具体元素二", "具体元素三", "具体元素四", "具体元素五", "具体元素六", "具体元素七"],
  "ratio_composition_plan": "如何充分使用3:4竖幅",
  "composition": "上中下、左右、前中后景和视觉动线",
  "detail_density_plan": "主体、辅助信息、留白和细节密度",
  "camera_plan": "镜头高度、观察角度、透视强弱和焦点位置",
  "material_detail_plan": "材质、厚度、倒角、接缝、粗糙度和透光反射",
  "lighting_plan": "主光、补光、接触阴影、环境遮蔽和高光方向",
  "surface_detail_plan": "服务技术理解的接口、状态灯、代码和设备细节",
  "color_plan": "主色与辅助色的信息分工",
  "chinese_labels": ["中文短标签", "中文短标签", "中文短标签"],
  "negative_constraints": "避免的误读和空洞元素",
  "prompt": "超过700个非空白字符的完整高上下文中文提示词"
}
```

`prompt`必须独立可用，写清上三分之一真实技术场景、下三分之二由`information_visual_mode`指定的微3D信息层、融合过渡带、技术背景、共享主体、机制、构图、镜头、同向光线、连续透视、材质转化、微观细节、`cool_porcelain_tech`配色及`#EEF3F6`主背景、颜色迁移、中文标签、信息层级和禁区。插画模式必须补充原创技术物理隐喻、关键动作、富配色和`#1677FF`、`#11A8A5`、`#6256D9`、`#E25B5B`的语义分工、微3D厚度与细微手作感，并明确禁止固定外部角色、纯白扁平手绘和套用外部案例。长度必须超过700个非空白字符，建议保持在900至1200个非空白字符，不能靠重复形容词凑长度。
