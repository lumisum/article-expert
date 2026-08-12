# S5：成熟彩色叙事插画微3D连续连环画

每个`##`章节生成一条3:4竖图提示词，只产出提示词，不生成真实图片。开始前完整读取`cast-bible.json`和`article_profile.narrative_mode`。所有正文图必须共同构成一部苏美与凝香主演的连续文章连环画，每张图既是独立可读的一幕，也是上一幕的结果和下一幕的视觉伏笔。

## 不可变目标

- 固定使用`sunlit_mature_narrative_illustration_micro_3d`，不再在信息卡、写实摄影与插画之间选择；
- 每张图100%使用一个完整的全画幅叙事场景；只允许一条嵌入荧幕边框的短场景文字，禁止独立信息层、信息卡、流程图、PPT和多行说明；
- 全画幅内部按视觉权重大致分配：65%人物关系与动作、25%嵌入场景的隐喻物件和环境、8%窄幅荧幕边框短句、2%留白与下一幕钩子；这是同一场景中的视觉权重，不是分栏；
- 苏美与凝香是固定男女主角，两人的外观、服装系统、声音对应的表情习惯、标志物和内容搭档关系必须逐字服从`cast-bible.json`；
- 每一幕只呈现`scene_plan.characters_present`真正需要的人物。可以是双主角、单主角加配角、多人物现场或主角单人特写，不得为了模板强塞未在该幕行动的人；
- 配角逐项服从S1的`supporting_cast`，同一篇内外观、关系、说话方式和服装连续，不能生成没有进入蓝图的路人型“第三主角”；
- 用人物正在经历的事件、动作、空间和原创生活隐喻重新讲一遍本章认识，而不是给段落配一张氛围图；
- 相邻图片至少通过两个连续元素连接，例如同一物件、未完成动作、视线、门、道路、光线、天气或颜色；
- 让读者产生翻到下一幕的欲望，但不得依靠恐惧、羞辱、性化、猎奇或虚假逆袭制造刺激。

## 画风：阳光成熟彩色叙事插画微3D

把整组图片设计成原创的成人向彩色叙事绘本连环画：约65%成熟插画化造型负责清晰的表情、手势、色彩分区和叙事取舍，约25%微3D负责圆润体积、材质厚度、半透明层和柔和接触阴影，约10%现实生活锚点只负责正常成年人体比例、可信空间尺度和日常物件逻辑。使用明亮高调光线、可见手绘笔触、纸张颗粒、色块层次和柔和边缘建立可触摸的世界。人物不是照片、真人摄影、电影剧照或AI写真，也不是幼儿绘本、Q版、大眼动画脸、扁平线稿或塑料玩偶。

现实主义只属于故事事实和空间逻辑，不属于渲染方式。人物脸部保留成熟年龄感，但必须有经过绘画提炼的轮廓、色彩和表情；不渲染皮肤毛孔、镜头眩光、摄影棚打光、强景深虚化或电影级真实质感。每一幕都应让读者一眼认出“同一部成人小说插画”，而不是误以为真人剧照。

使用温暖手绘动画电影的通透自然光、丰富环境色、克制奇想和富有空气感的景深，但不引用或模仿任何特定创作者、角色或作品。镜头必须有真实的前景遮挡、中景人物关系、远景空气透视和清晰的焦点转移；微3D只增强体积与接触阴影，不能把手绘插画渲染成摄影棚里的CG真人。

## 荧幕式叙事边框与短句

每张正文图都使用同一套细窄的“荧幕式叙事边框”：像电影画幅、旧放映幕或精装绘本的内嵌画框，厚度控制在画幅的6%至10%，与画面色彩和手绘纹理一体化，不是白色信息卡、气泡、海报或PPT边栏。

边框内只放一条4至14个非空白字符的短场景文字。它可以是未完成动作、人物当下的心里话、关键物件线索或时间感，不是段落摘要、知识结论、金句或完整道理。每幕生成`caption_text`、`caption_role`和`caption_frame_position`；文字优先直接呈现为准确中文，同时保留后期叠字备用，确保模型文字偶发失真时仍能用同一短句补上。

文字位置只能是`bottom_frame`或`top_frame`，避开人物脸部、关键动作、标题、核心物件和下一幕钩子。除了这条短句，画面其余任何区域均不得出现文字、数字、招牌字、对话框或乱码。

阳光和希望是基础情绪，不是只在结尾出现的奖励。主角默认眼神明亮、面部放松、肩颈舒展、动作开放；困境主要通过空间阻力、关系距离、物件重量、道路和光线表达，不能让人物从头到尾皱眉受苦。整组至少70%的画面使用自然微笑、温暖笑意、轻松专注或自信笑容；最多两幕可以不笑，但只能平静清醒、专注思考，不能愁容满面、嘴角下垂、眼神空洞、弯腰缩肩或呈现受害者姿态。

阳光不等于每一幕复制同一张笑脸。苏美与凝香必须分别拥有一条可辨认的表情弧：开场的警觉、好奇或礼貌笑意，压力中的笑意收住与视线回避，最低点的平静绷紧，认知转折时的微怔、抬眼或呼吸变化，行动后的释然，以及结尾明亮稳定的笑容。相邻两幕至少改变眉眼、嘴角、视线、呼吸、肩颈和身体朝向中的三项；同一幕的两个人也必须形成“一个先察觉、一个还在掩饰”“一个微怔、一个安静等待”等回应或反差，禁止统一微笑、统一惊讶和模板化表情。

每一幕都要有：

1. 一秒可读的人物动作；
2. 一个由文章事实支持的核心物件或生活隐喻；
3. 清晰的前景、中景、背景和视觉动线；
4. 一处高纯度焦点色作为视觉奖励；
5. 一个未完成动作、画外视线、半开的门、延伸道路或画面边缘物件，形成下一幕钩子；
6. 经得起停留观看的生活微细节，但不能让背景抢走主动作。

“让人看着上瘾”来自连续的识别与奖励：读者每一幕先认出同一个人和延续物，再发现它发生了新变化；镜头在远景、中景、近景、俯视和低机位之间有节奏地切换；每两至三幕出现一次合乎文章含义的尺度变化、空间剖开、路径实体化或物件转化。禁止每张都用同一构图，也禁止为了新奇让故事失真。

## 阳光色彩系统

使用`sunlit_chromatic_midlife_story`，彩色丰富、明亮温暖但不彩虹化。每幕只选一个主色、两个至四个辅助色和必要中性色；颜色必须承担叙事职责：

- 暖日米白`#FFF4DC`：呼吸、留白和生活光；
- 晴空蓝`#5F9ED1`：清醒、开阔和判断；
- 珊瑚橙`#E77A64`：体温、行动和重新接触生活；
- 柔莓红`#B85C74`：冲突、代价和仍有生命力的情绪；
- 新叶绿`#78A96B`：秩序、修复和可行动空间；
- 向日葵黄`#F2C14E`：发现、转折和下一步；
- 薰衣草紫`#8B7BB8`：记忆、矛盾和未完成感；
- 湖青`#4AA5A4`：连接、理解和关系重新流动。

全文颜色也要讲故事，但任何阶段都不能灰暗压抑：开场以暖日米白、晴空蓝和珊瑚橙建立亲和力；下潜阶段只降低背景饱和度，人物肤色、眼神高光和一处希望色必须保留；转折处让向日葵黄或湖青穿过画面；回升阶段逐幕增加新叶绿与珊瑚橙；结尾达到丰富、稳定、透气的平衡，不能突然变成金光成功海报。

## 先写整篇故事圣经

先通读全文和全部章节，再写`assets/image_story_bible.json`。不要先逐章生成提示词。故事圣经是人物、世界、色彩、母题和分镜连续性的唯一真相源：

```json
{
  "version": "novel_serial_illustration_v2",
  "visual_mode": "sunlit_mature_narrative_illustration_micro_3d",
  "series_format": "continuous_full_bleed_picture_story",
  "visual_meaning_core": "与hidden_meaning一致的导演秘密，只通过动作、代价和关系反馈呈现，不在画面解释",
  "series_logline": "苏美与凝香从核心对话或故事走到现实回升的一句话视觉故事",
  "narrative_mode": "novel_story",
  "episode_core": "与S1一致的核心对话、核心事件或未闭合动作",
  "cast_mode": "fixed_leads_dynamic_supporting_cast",
  "cast_selection_reason": "midlife固定内容角色苏美与凝香",
  "protagonist_continuity_signature": "与cast-bible.json中苏美appearance_signature逐字一致",
  "secondary_protagonist_signature": "与cast-bible.json中凝香appearance_signature逐字一致",
  "character_bible": {
    "identity": "固定角色苏美及其本篇动态认识位置",
    "face_hair_signature": "不可漂移的脸型、五官、肤色、发型、发色",
    "body_and_age_signature": "不可漂移的年龄感、身高比例、体态和动作习惯",
    "wardrobe_system": "固定服装轮廓与3至5个衣着色；换装必须由时间或场景支持",
    "signature_object": "贯穿全文并会发生变化的个人物件",
    "expression_and_gesture_range": "以自然微笑、明亮眼神和开放姿态为主，严肃幕也保持平静清醒与生命力",
    "forbidden_drift": "禁止换脸、年龄漂移、发型突变、体型突变、网红脸、性感化和无缘由换装"
  },
  "secondary_character_bible": {
    "identity": "固定成年中国男性角色凝香及其本篇动态认识位置",
    "face_hair_signature": "不可漂移的男性脸型、五官、肤色、发型、发色",
    "body_and_age_signature": "不可漂移的年龄感、身高比例、体态和动作习惯",
    "wardrobe_system": "固定服装轮廓与颜色系统",
    "signature_object": "属于男性角色并参与对话的连续物件",
    "expression_and_gesture_range": "阳光、克制、可回应的表情与动作范围",
    "forbidden_drift": "禁止换脸、性格漂移、霸总模板、油腻化和工具人化"
  },
  "supporting_character_bible": [
    {
      "id": "C01",
      "name": "与S1 supporting_cast一致",
      "continuity_signature": "由appearance_boundary转成同篇不可漂移的外观、年龄区间、服装与标志动作",
      "relationship_signature": "与两位主角及核心事件的稳定关系",
      "forbidden_drift": "禁止换脸、功能漂移、工具人化和无依据身份变化"
    }
  ],
  "relationship_arc": {
    "relationship_type": "文章事实支持的关系类型",
    "source_basis": "关系与性别设定来自哪类原文事实",
    "initial_distance": "开场的身体距离、视线和动作关系",
    "nonverbal_dialogue_language": "眼神、身体朝向、空间距离、递物、并肩、错身等无文字对话语法",
    "turning_exchange": "转折幕两人真正完成的动作回应",
    "final_relationship_state": "结尾关系怎样变化但不虚假圆满",
    "forbidden_invention": "禁止凭空恋爱化、性别刻板化、冲突升级和虚假和解"
  },
  "composition_contract": {
    "scene_coverage": "full_frame_100_percent_story_scene",
    "human_relationship_action_weight": 65,
    "embedded_metaphor_environment_weight": 25,
    "caption_frame_weight": 8,
    "breathing_transition_hook_weight": 2,
    "independent_information_layer_weight": 0
  },
  "caption_frame_contract": {
    "frame_style": "cinematic_story_caption_frame",
    "frame_coverage_percent": 8,
    "frame_position_options": ["top_frame", "bottom_frame"],
    "caption_length_range": "4-14 Chinese non-space chars",
    "caption_content_rule": "unfinished action, inner whisper, object clue, or time echo; never a lesson or summary",
    "text_rendering_rule": "direct_exact_chinese_preferred_with_overlay_fallback",
    "other_text_policy": "no_text_outside_caption_frame"
  },
  "world_bible": {
    "setting_logic": "地点、时间和生活空间如何连续",
    "material_language": "手绘纹理、纸张颗粒、微3D厚度和真实材质规则",
    "camera_language": "镜头远近、机位和节奏规则",
    "lighting_continuity": "主光方向、时间推进与阴影规则",
    "time_progression": "整篇故事经过的时间及可见变化",
    "cinematic_depth_rule": "前景遮挡、中景人物关系、远景空气透视和清晰焦点转移；插画化景深不摄影化",
    "caption_frame_visual_rule": "窄幅荧幕式边框与手绘纹理、环境色一体，不得成为信息卡或海报边栏"
  },
  "emotional_direction": {
    "tone": "sunlit_hopeful_without_denial",
    "sunny_panel_ratio_target": 0.7,
    "max_non_smiling_panels": 2,
    "expression_baseline": "明亮眼神、放松面部、自然微笑或轻松专注",
    "difficult_scene_rule": "可以不笑，但必须平静清醒、身体有力量，困境由环境和物件表达",
    "hope_carrier": "每幕至少一个可见的希望载体：光、颜色、动作、关系回应或前方路径",
    "forbidden_expression": "禁止连续皱眉、愁容满面、嘴角下垂、空洞眼神、弯腰缩肩和受害者脸",
    "expression_arc": "开场警觉或好奇—压力中克制—转折时微怔—行动后释然—结尾明亮稳定",
    "sumei_expression_progression": "逐幕写清苏美眉眼、嘴角、视线、呼吸与肩颈怎样变化",
    "kaidi_expression_progression": "逐幕写清凝香眉眼、嘴角、视线、呼吸与肩颈怎样变化",
    "contrast_rule": "同一幕两人表情必须互相回应但不复制",
    "micro_expression_rule": "相邻两幕至少改变眉眼、嘴角、视线、呼吸、肩颈和朝向中的三项",
    "no_flat_repetition": "禁止连续复用同一笑型、眼神、嘴角和身体姿态"
  },
  "palette_bible": {
    "profile": "sunlit_chromatic_midlife_story",
    "colors": ["暖日米白 #FFF4DC", "晴空蓝 #5F9ED1", "珊瑚橙 #E77A64", "柔莓红 #B85C74", "新叶绿 #78A96B", "向日葵黄 #F2C14E", "薰衣草紫 #8B7BB8", "湖青 #4AA5A4"],
    "opening_phase": "开场暖冷对照",
    "descent_phase": "下潜阶段的降饱和与阴影加深",
    "turning_phase": "转折色第一次穿过画面",
    "rebound_phase": "回升色逐幕增加但保留现实阴影",
    "integration_phase": "结尾丰富、稳定、透气的平衡",
    "color_discipline": "每幕一个主色、两个至四个辅助色，所有颜色服务叙事"
  },
  "recurring_motif": {
    "motif_name": "贯穿全文的原创视觉母题名称",
    "initial_state": "母题在第一幕的状态",
    "transform_rule": "它怎样随认识变化而变化",
    "final_state": "母题在最后一幕的状态"
  },
  "continuity_rules": ["至少五条可执行连续性规则"],
  "storyboard": [
    {
      "image_id": "section_01",
      "section_title": "章节标题",
      "story_phase": "opening|pressure|descent|low_point|turning|rebound|integration",
      "beat_type": "opening_hook|inciting_pressure|deepening_conflict|choice_or_cost|low_point|recognition|turning_action|rebound_step|integration|afterglow",
      "story_function": "这一幕在整部连环画中的职责",
      "visible_action": "画面中真正发生的动作",
      "visual_metaphor": "由本章事实支持的一个生活隐喻",
      "caption_text": "4至14字的未完成动作、心里话、物件线索或时间回声",
      "caption_role": "event_hook|inner_whisper|object_clue|time_echo",
      "caption_frame_position": "top_frame|bottom_frame",
      "continuity_token_in": "第一幕为SERIES_START，其余等于上一幕的continuity_token_out",
      "continuity_token_out": "最后一幕为SERIES_END，其余为传给下一幕的唯一连接令牌",
      "carryover_elements": ["至少两个与相邻画面共享的元素"],
      "transition_method": "match_object|continued_motion|gaze_bridge|color_relay|light_relay|spatial_threshold|time_echo|scale_metaphor",
      "sunny_expression": true,
      "smile_type": "soft_smile|bright_smile|relieved_smile|confident_smile|playful_smile|calm_focus|quiet_reflection",
      "hope_level": 1,
      "facial_expression": "本幕具体而自然的明亮表情",
      "characters_present": ["苏美", "凝香", "配角姓名或稳定称谓"],
      "lead_visibility": "both|sumei_only|ningxiang_only",
      "sumei_expression": "苏美本幕眉眼、嘴角、呼吸、视线和肩颈的具体状态",
      "kaidi_expression": "凝香本幕眉眼、嘴角、呼吸、视线和肩颈的具体状态",
      "character_expression_relationship": "本幕可见人物的表情怎样形成回应或反差",
      "micro_expression_change": "相较上一幕至少三项可见变化；第一幕写INITIAL_EXPRESSION",
      "expression_link_from_previous": "上一幕表情动作怎样在本幕继续或改变；第一幕写SERIES_START",
      "body_openness": "肩颈、手臂、躯干和步态怎样体现生命力",
      "hope_signal": "本幕可见的光、颜色、行动、回应或前方路径",
      "character_blocking": "本幕可见人物的位置、距离、朝向、动作主次和环境关系",
      "nonverbal_dialogue": "通过眼神、动作、空间或共享物件完成的无文字交流",
      "relationship_beat": "关系或内在关系在本幕发生的一个微小变化",
      "shared_action": "本幕可见人物彼此接续的动作；单人特写写人物与环境的动作关系",
      "next_panel_hook": "促使读者想看下一幕的未完成视觉问题",
      "color_arc_role": "本幕怎样推进全文颜色弧线"
    }
  ]
}
```

两套主角签名必须逐字复制`cast-bible.json`，`cast_mode`固定为`fixed_leads_dynamic_supporting_cast`。`relationship_arc.relationship_type`固定以“长期内容搭档与朋友”为基础，不得根据文章主题临时改成情侣、夫妻或暧昧关系。另建`supporting_character_bible`数组，与S1的配角顺序一致；没有配角时为空数组。

## 文章级选角与人物连续性

苏美与凝香必须像跨文章不换演员的固定角色：逐字复用两套外观签名与服装系统，分别保留湖青色布袋和暖铜边深色笔记本。每篇可以根据地点和天气增加合理外层服装，但不能改变基础轮廓、标志色和标志物。

两人是长期内容搭档和朋友，不是默认情侣。视觉上不得长期形成苏美受伤、凝香解释或拯救的性别分工；谁先看见、谁先误判、谁追问、谁完成动作必须与S1的`role_assignment`一致。

人物组合完全服从剧情。每幕至少有苏美或凝香一位主角在场，配角只在该幕确有行动时出现；不要求双主角固定同框。人物之间的“对话”通过眼神、身体朝向、空间距离、递交物件、错身、并肩、共同劳动和动作接续表达，不使用文字或对话框，也不能每幕都面对面站着。

## 连续分镜

- 每个章节只选一个`visible_action`和一个`visual_metaphor`，动作必须发生，不能摆拍；
- 第一幕立即给出人物、处境和未闭合问题；最后一幕完成现实回升，但保留生活仍会继续的开放感；
- 顺序必须从`opening`进入`pressure/descent/low_point`，再经过`turning`、`rebound`到`integration`，不得在最低点之前提前治愈；
- 相邻两幕的`continuity_token`必须首尾相接，并共享至少两个`carryover_elements`；
- 使用物件匹配剪辑、动作延续、视线桥接、颜色接力、光线接力、空间门槛、时间回声或尺度隐喻完成转场；
- 每幕明确`previous_panel_callback`和`next_panel_hook`。钩子是视觉上的未完成问题，不是耸动文案；
- 全文至少70%的幕将`sunny_expression`设为`true`；第一幕、转折幕、回升幕和结尾幕必须为`true`，非微笑幕最多两张且只能出现在压力、下潜或最低点；
- `hope_level`使用1至5整数表示可见希望强度：开场至少3，转折至少3，回升至少4，结尾固定5。希望强度可以下降再回升，但不能把人物画成失去生命力；
- 微笑必须与事件匹配：困难时可用轻微温暖笑意或轻松专注，转折后使用释然、自信或明亮笑容，禁止所有章节复制同一个僵硬笑脸；
- 相邻两幕不得使用相同`smile_type`；整组至少出现三种不同笑型或平静专注状态；
- 每幕分别填写`sumei_expression`与`kaidi_expression`，两项都要具体到眉眼、嘴角、呼吸、视线和肩颈，不得只写“开心、难过、复杂、若有所思”；
- `character_expression_relationship`必须说明本幕可见人物的表情怎样互相捕捉、错开或回应；`micro_expression_change`必须明确相较上一幕改变的至少三项，禁止相邻两幕复用同一组表情描述；
- 每幕写明`characters_present`和`lead_visibility`，人物组合必须与该幕事件一致；每幕必须给出不同的`nonverbal_dialogue`和`shared_action`，禁止重复面对面站立；
- 若文章不是时间顺序，仍以同一主角的象征性现实旅程重组分镜，但不得改写事实、凭空增加创伤、冲突或成功。

## 把思想画进事件

不再设置独立信息层。将本章最重要的因果、选择、时间或关系转成可见事件：门槛高低、路的分叉、绳结松紧、容器漏水、影子长度、物件重量、空间距离、重复动作、逐渐展开的地图等。隐喻必须能逐项解释正文判断，并由人物动作触发；禁止只在背景放一个象征物。

画面只允许荧幕边框内的一条短场景文字：不使用信息框、对话框、旁白框、标题、标签、英文、数字、乱码、水印或装饰字。短句只为读者指出正在发生的情绪或动作，不承担解释观点的任务；所有更深的理解仍要通过人物关系、动作、物件、空间、色彩和光线完成。隐藏意义必须由行动、代价和关系反馈呈现，不画哲学家肖像、古籍、阴阳符号或文化拼贴。

## 输出

在`final_article.md`每个`##`章节内插入且只插入一个`<!-- IMAGE:section_01 -->`。标记必须位于本章有意义的引入段之后；章节数、标记数、故事板幕数和JSONL行数必须完全相等。

写入`assets/image_prompts.jsonl`，每行：

```json
{
  "image_id": "section_01",
  "section_index": 1,
  "section_title": "章节标题",
  "visual_role": "serial_story_panel",
  "aspect_ratio": "3:4",
  "story_phase": "opening|pressure|descent|low_point|turning|rebound|integration",
  "beat_type": "opening_hook|inciting_pressure|deepening_conflict|choice_or_cost|low_point|recognition|turning_action|rebound_step|integration|afterglow",
  "article_context": "本章前因后果及与上一章、下一章的关系",
  "panel_meaning": "这一幕让读者通过人物行为自行体会的变化，不写成观点",
  "narrative_mode": "novel_story，与article_profile一致",
  "cast_mode": "fixed_leads_dynamic_supporting_cast",
  "subject_profile": "fixed_leads_with_scene_required_supporting_cast",
  "protagonist_continuity_signature": "与故事圣经逐字一致",
  "secondary_protagonist_signature": "与cast-bible.json中凝香appearance_signature逐字一致",
  "character_state": "本幕开始时的身体、情绪和认识状态",
  "wardrobe_continuity": "服装怎样承接上一幕或为何合理变化",
  "characters_present": ["苏美", "凝香", "配角姓名或稳定称谓"],
  "lead_visibility": "both|sumei_only|ningxiang_only",
  "supporting_characters": "本幕实际出现的配角及连续性签名；没有则写none",
  "visible_action": "正在发生且尚未完成的动作",
  "emotional_shift": "本幕前后发生的细微情绪或认识变化",
  "visual_metaphor": "由本章事实支持的原创生活隐喻",
  "meaning_embodiment": "本幕隐藏意义怎样完全嵌入人物、动作、物件和空间",
  "caption_text": "4至14字的未完成动作、心里话、物件线索或时间回声",
  "caption_role": "event_hook|inner_whisper|object_clue|time_echo",
  "caption_frame_position": "top_frame|bottom_frame",
  "caption_frame_style": "cinematic_story_caption_frame",
  "caption_rendering": "direct_exact_chinese_preferred_with_overlay_fallback",
  "recurring_motif_state": "全文视觉母题在本幕的状态",
  "continuity_token_in": "与上一幕连接的令牌",
  "continuity_token_out": "传给下一幕的令牌",
  "previous_panel_callback": "读者能认出的上一幕动作、物件或颜色",
  "next_panel_hook": "下一幕将回答的未完成视觉问题",
  "carryover_elements": ["连续元素一", "连续元素二"],
  "transition_method": "match_object|continued_motion|gaze_bridge|color_relay|light_relay|spatial_threshold|time_echo|scale_metaphor",
  "sunny_expression": true,
  "smile_type": "soft_smile|bright_smile|relieved_smile|confident_smile|playful_smile|calm_focus|quiet_reflection",
  "hope_level": 3,
  "facial_expression": "明亮眼神、放松面部与符合本幕的自然笑意或平静专注",
  "sumei_expression": "苏美本幕眉眼、嘴角、呼吸、视线和肩颈的具体状态",
  "kaidi_expression": "凝香本幕眉眼、嘴角、呼吸、视线和肩颈的具体状态",
  "character_expression_relationship": "本幕所有可见人物的表情怎样形成回应或反差",
  "micro_expression_change": "相较上一幕至少三项可见变化；第一幕写INITIAL_EXPRESSION",
  "expression_link_from_previous": "上一幕表情动作怎样在本幕继续或改变；第一幕写SERIES_START",
  "body_openness": "肩颈、手臂、躯干和步态怎样保持开放与生命力",
  "hope_signal": "本幕可见的光、颜色、行动、关系回应或前方路径",
  "character_blocking": "人物的位置、距离、朝向、动作主次和环境关系",
  "nonverbal_dialogue": "眼神、身体朝向、距离、递物或动作接续形成的无文字对话",
  "relationship_beat": "关系或内在关系在本幕发生的一个变化",
  "shared_action": "本幕可见人物共同或接续的动作；单人特写写人物与环境的动作关系",
  "scene_coverage": "full_frame_100_percent_story_scene",
  "camera_plan": "景别、机位、镜头节奏和焦点",
  "composition": "完整3:4全画幅叙事构图和视线动线",
  "depth_layers": "前景、中景、背景及遮挡关系",
  "lighting_plan": "承接前一幕并推进时间的光线",
  "style_profile": "sunlit_mature_narrative_illustration_micro_3d",
  "palette_profile": "sunlit_chromatic_midlife_story",
  "dominant_color": "主色名称 #RRGGBB",
  "supporting_colors": ["辅助色一 #RRGGBB", "辅助色二 #RRGGBB"],
  "color_arc_role": "本幕颜色怎样推进下潜、转折或回升",
  "texture_plan": "手绘笔触、纸张颗粒和生活材质",
  "micro_3d_plan": "圆润体积、厚度、接缝、半透明层与接触阴影",
  "text_policy": "story_caption_frame_only",
  "negative_constraints": "禁止非边框文字、数字、乱码、信息卡、分栏、PPT、换脸、摆拍、统一表情、重复笑脸、愁容满面、空泛氛围、无依据情节、写实摄影、真人写真、电影剧照、photorealistic、cinematic still、皮肤毛孔、摄影棚打光、强景深虚化",
  "prompt": "超过900个非空白字符的完整独立中文提示词"
}
```

每条`prompt`必须能够独立生成该幕，同时写入叙事模式、`fixed_leads_dynamic_supporting_cast`、本幕`characters_present`、所有可见人物的连续签名、人物站位、无文字对话、关系节拍、共享动作、连续令牌、上一幕回声、下一幕钩子、重复母题状态、原创隐喻、`caption_text`、`caption_role`、`caption_frame_position`、`caption_frame_style`、`caption_rendering`、100%全画幅3:4场景、成熟彩色叙事插画、手绘笔触、微3D材质、前中后景镜头、光线、插画化空气景深、主辅HEX颜色、可见人物表情关系、相邻幕微表情变化、身体开放度、希望载体和禁区。提示词必须明确包含“固定男女主角”“按剧情加入配角”“连环画”“成熟叙事插画”“彩色插画”“手绘笔触”“微3D”“阳光和希望”“明亮眼神”“表情变化”“100%全画幅场景”“胶片式叙事边框”“边框内准确中文”“除边框短句外画面无文字”“禁止非边框文字”“禁止愁容满面”“禁止统一表情”“禁止信息卡”“禁止写实摄影”“禁止真人写真”“禁止电影剧照”“禁止photorealistic”“禁止cinematic still”和`sunlit_mature_narrative_illustration_micro_3d`；`sunny_expression=true`时还必须包含“自然微笑”，否则必须包含“平静清醒”。不得把未出场主角强塞进画面，不得复述字段凑长度，不得生成多格漫画页，不得引用或模仿外部固定角色、作者或作品画风。
