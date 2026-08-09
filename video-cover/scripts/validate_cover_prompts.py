#!/usr/bin/env python3
"""Validate the minimal video-cover JSONL output without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {"platform", "size", "aspect_ratio", "core_prompt_points", "prompt"}
PRESETS = {
    "微信视频号竖版": ("1080x1260", "6:7"),
    "微信视频号横版": ("1920x1080", "16:9"),
    "今日头条横版": ("1920x1080", "16:9"),
    "B站横版": ("1920x1080", "16:9"),
    "B站旧式兼容": ("1146x717", "about 16:10"),
    "抖音竖屏": ("1080x1920", "9:16"),
    "抖音主页封面": ("1080x1440", "3:4"),
    "快手竖屏": ("1080x1920", "9:16"),
    "小红书视频封面": ("1080x1440", "3:4"),
    "西瓜视频横版": ("1920x1080", "16:9"),
    "YouTube横版": ("1280x720", "16:9"),
}
BACKGROUND_HEXES = {"#F3F4F1", "#EEF3F6", "#F2F1ED"}
SIZE_RE = re.compile(r"^[1-9][0-9]{2,4}x[1-9][0-9]{2,4}$")


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def nonspace(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def require_text(item: dict[str, Any], key: str, owner: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"{owner}.{key} must be a non-empty string")
    return value.strip()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"file not found: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid JSONL at line {line_number}: {exc}")
        if not isinstance(value, dict):
            fail(f"line {line_number} must be a JSON object")
        rows.append(value)
    if not rows:
        fail("JSONL must contain at least one non-empty row")
    return rows


def validate_row(item: dict[str, Any], index: int) -> tuple[str, str]:
    owner = f"row[{index}]"
    fields = set(item)
    if fields != REQUIRED_FIELDS:
        missing = sorted(REQUIRED_FIELDS - fields)
        extra = sorted(fields - REQUIRED_FIELDS)
        fail(f"{owner} must use exactly five fields; missing={missing}, extra={extra}")

    platform = require_text(item, "platform", owner)
    size = require_text(item, "size", owner)
    ratio = require_text(item, "aspect_ratio", owner)
    prompt = require_text(item, "prompt", owner)
    if not SIZE_RE.fullmatch(size):
        fail(f"{owner}.size must use WIDTHxHEIGHT with ASCII x")
    if platform in PRESETS and (size, ratio) != PRESETS[platform]:
        fail(f"{owner} must match preset {PRESETS[platform]}")

    points = item.get("core_prompt_points")
    if not isinstance(points, list) or not 4 <= len(points) <= 8:
        fail(f"{owner}.core_prompt_points must contain four to eight strings")
    if any(not isinstance(point, str) or not point.strip() for point in points):
        fail(f"{owner}.core_prompt_points must contain only non-empty strings")
    joined_points = " ".join(points)
    for required in ("60%", "40%", "真实", "纲要"):
        if required not in joined_points:
            fail(f"{owner}.core_prompt_points must include {required}")
    if not any(value in joined_points.upper() for value in BACKGROUND_HEXES):
        fail(f"{owner}.core_prompt_points must include a supported style background HEX")

    if nonspace(prompt) <= 700:
        fail(f"{owner}.prompt must exceed 700 non-whitespace characters")
    for required in (size, ratio, "60%", "40%", "真实", "纲要"):
        if required not in prompt:
            fail(f"{owner}.prompt must include {required}")
    if not any(value in prompt.upper() for value in BACKGROUND_HEXES):
        fail(f"{owner}.prompt must include a supported style background HEX")
    if not re.search(r"(?:2|二)\s*(?:至|到|[-—~～])\s*(?:4|四)\s*个", prompt):
        fail(f"{owner}.prompt must limit outline information to two to four nodes")
    return platform, size


def validate(path: Path) -> dict[str, Any]:
    rows = load_jsonl(path)
    keys = [validate_row(item, index) for index, item in enumerate(rows)]
    if len(set(keys)) != len(keys):
        fail("platform and size pairs must be unique")
    return {
        "status": "ok",
        "variants": len(rows),
        "platforms": [item["platform"] for item in rows],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.jsonl)
    except (OSError, ValidationError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
