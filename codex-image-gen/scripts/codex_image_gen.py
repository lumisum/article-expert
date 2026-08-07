import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional


def codex_image_gen_skill(
    prompt: str,
    save_path: Optional[str] = None,
    filename: Optional[str] = None,
    aspect_ratio: str = "1:1",
    model: str = "gpt-5.4-mini",
) -> Dict[str, Any]:
    """Codex 图像生成 Skill (Python 版)

    通过本地 Codex 命令行调用 gpt-image-2 模型生成图片，自动识别额度耗尽与频次限制。
    """
    # 0. 前置检测：验证系统中是否安装了 codex
    import shutil
    if not shutil.which("codex"):
        return {
            "success": False,
            "error": "系统未安装 codex 命令行工具，请先安装 codex。",
            "reason": "CODEX_NOT_INSTALLED",
        }

    # 1. 默认参数初始化
    if save_path is None:
        save_path = os.getcwd()
    if filename is None:
        filename = f"img_{int(time.time() * 1000)}.png"

    # 2. 确保目标路径为绝对路径
    absolute_save_path = os.path.abspath(save_path)

    # 3. 组装内层给 gpt-image-2 的精细化指令
    inner_prompt = (
        f"使用内置 of image_gen 工具（gpt-image-2 模型），生成一张：{prompt}。"
        f"请严格确保图片尺寸比例为 {aspect_ratio}。"
        f"生成后，请直接将图片保存到当前目录，命名为 {filename}"
    )

    # 4. 对双引号进行安全转义，防止 Shell 解析错误
    escaped_inner_prompt = inner_prompt.replace('"', '\\"')

    # 5. 构建完整的 CLI 命令
    command = (
        f'codex exec -m {model} '
        f'--dangerously-bypass-approvals-and-sandbox '
        f'--cd "{absolute_save_path}" "{escaped_inner_prompt}"'
    )

    try:
        # 6. 执行命令并设定 2 分钟超时
        # 使用 shell=True 来保证转义和工作目录切换能正确被系统终端解析
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120,
        )

        return {
            "success": True,
            "file_path": os.path.join(absolute_save_path, filename),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Codex 命令执行超时（超过 120 秒）",
            "reason": "UNKNOWN",
        }

    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        message = str(e)
        reason = "UNKNOWN"

        # 7. 状态感知与熔断识别
        if "Rate limit" in stderr or "429" in stderr or "429" in message:
            reason = "RATE_LIMIT"
        elif "Token limit" in stderr or "insufficient" in stderr:
            reason = "TOKEN_EXHAUSTED"

        return {"success": False, "error": stderr or message, "reason": reason}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Codex Image Generation CLI Wrapper")
    parser.add_argument("--prompt", required=True, help="Image prompt")
    parser.add_argument("--save-path", help="Directory to save the generated image")
    parser.add_argument("--filename", help="Output filename")
    parser.add_argument("--aspect-ratio", default="1:1", help="Image aspect ratio (e.g. 1:1, 16:9)")
    parser.add_argument("--model", default="gpt-5.4-mini", help="Codex model to run")

    args = parser.parse_args()
    res = codex_image_gen_skill(
        prompt=args.prompt,
        save_path=args.save_path,
        filename=args.filename,
        aspect_ratio=args.aspect_ratio,
        model=args.model,
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if not res["success"]:
        sys.exit(1)
