---
name: codex-image-gen
description: 用于生成高质量的图片，支持自定义提示词、图片比例、保存路径、图片名称及执行模型。用于文章配图、社交媒体内容创作等场景。
beneva_skill_manifest: MANIFEST.yaml
---

# codex-image-gen

使用本地 Codex CLI 驱动的 `gpt-image-2` 模型生成高质量图片，并支持自定义图片提示词、图片比例、保存路径、图片名称及执行模型。

## 前置条件 (Prerequisites)

- **系统必须安装 `codex` 命令行工具**。技能在执行时会自动检测该工具的存在性。如果未安装，将直接返回失败并提示安装说明。

## 核心配置与默认规则

该技能允许调用方完全自定义以下关键属性：
1. **图片提示词 (Prompt)**: 必需参数，描述生成图片的具体画面内容。
2. **图片比例 (Aspect Ratio)**: 可选，默认比例为 `1:1`（可设为 `16:9`、`4:3` 等）。
3. **保存路径 (Save Path)**: 可选，默认为当前工作目录。
4. **图片名称 (Filename)**: 可选，默认为按当前毫秒级时间戳生成的 `img_<timestamp_ms>.png`。
5. **执行模型 (Model)**: 可选，**默认使用 `gpt-5.4-mini` 模型**。

---

## 核心脚本与使用方式

图片生成的核心 Python 逻辑保存在 `scripts/codex_image_gen.py` 中。

### 1. 命令行调用 (CLI)
可以在终端中通过传入参数定制生成：
```bash
python skills/codex-image-gen/scripts/codex_image_gen.py \
  --prompt "一只可爱的熊猫在吃竹子" \
  --save-path "/Users/elonmar/wechat_articles/assets" \
  --filename "panda.png" \
  --aspect-ratio "16:9" \
  --model "gpt-5.4-mini"
```

### 2. Python 模块调用
```python
from scripts.codex_image_gen import codex_image_gen_skill

result = codex_image_gen_skill(
    prompt="一只可爱的熊猫在吃竹子",
    save_path="/Users/elonmar/wechat_articles/assets",
    filename="panda.png",
    aspect_ratio="16:9",
    model="gpt-5.4-mini"  # 默认使用 gpt-5.4-mini
)

if result["success"]:
    print(f"图片成功保存至: {result['file_path']}")
else:
    print(f"生成失败: {result['error']}, 原因/错误类型: {result['reason']}")
```

---

## 输入参数参考表

| 参数名 | 类型 | 是否必填 | 默认值 | 描述 |
|---|---|---|---|---|
| `prompt` | `str` | 是 | - | 生成图片的画面提示词。 |
| `save_path` | `str` | 否 | `os.getcwd()` | 图片保存的目标文件夹目录。 |
| `filename` | `str` | 否 | `img_<timestamp_ms>.png` | 保存的目标图片文件名。 |
| `aspect_ratio` | `str` | 否 | `"1:1"` | 图片的比例规格（如 `"1:1"`, `"16:9"`, `"4:3"`）。 |
| `model` | `str` | 否 | `"gpt-5.4-mini"` | 调用 Codex 时使用的模型。 |

## 返回值说明
返回一个 dict 字典，包含以下字段：
- `success` (bool): 表示生成是否成功。
- `file_path` (str, 仅在 success 为 True 时存在): 生成的图片的绝对路径。
- `error` (str, 仅在 success 为 False 时存在): 失败的报错/错误信息。
- `reason` (str, 仅在 success 为 False 时存在): 失败的具体类型：
  - `"CODEX_NOT_INSTALLED"`: 本地未安装 `codex` 命令行工具
  - `"RATE_LIMIT"`: 频率限制 (429 / Rate limit)
  - `"TOKEN_EXHAUSTED"`: 额度/Token 耗尽
  - `"UNKNOWN"`: 超时或其他未知错误
