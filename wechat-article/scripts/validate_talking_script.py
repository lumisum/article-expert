#!/usr/bin/env python3
"""Validate the optional Stage 7 direct-to-camera talking script."""

from __future__ import annotations

import argparse
import json
import re

from validation_lib import (
    STAGE3_RECEIPT,
    article_route_key,
    fail,
    load_json,
    require_receipt,
    resolve_topic_dir,
    validate_article_profile,
)

DEFAULT_MIN_SECONDS = 240
MAX_SECONDS = 300
HANZI_PER_SECOND = 4.0
LATIN_WORDS_PER_SECOND = 2.5


def estimate_duration_seconds(text: str) -> float:
    hanzi = len(re.findall(r"[\u3400-\u9fff]", text))
    latin_words = len(re.findall(r"\b[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)*\b", text))
    sentence_pauses = len(re.findall(r"[。！？!?；;]", text)) * 0.32
    short_pauses = len(re.findall(r"[，、：:]", text)) * 0.12
    paragraph_pauses = max(0, len(re.findall(r"\n\s*\n", text))) * 0.35
    return hanzi / HANZI_PER_SECOND + latin_words / LATIN_WORDS_PER_SECOND + sentence_pauses + short_pauses + paragraph_pauses


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir")
    parser.add_argument(
        "--min-seconds",
        type=int,
        default=DEFAULT_MIN_SECONDS,
        help="Minimum estimated duration; use 180 only when the user explicitly requests a 3-minute script.",
    )
    args = parser.parse_args()
    topic_dir = resolve_topic_dir(args.topic_dir, "video/talking_script.txt")
    path = topic_dir / "video" / "talking_script.txt"
    pack_path = topic_dir / "research" / "source_pack.json"
    for required in (path, pack_path):
        if not required.is_file():
            fail(f"Missing Stage 7 file: {required}")
    pack = load_json(pack_path)
    if not isinstance(pack, dict):
        fail("source_pack.json must be an object.")
    article_profile = validate_article_profile(pack)
    stage3 = require_receipt(topic_dir, STAGE3_RECEIPT, next_stage="Stage 7 talking script")
    if stage3.get("article_route") != article_route_key(article_profile):
        fail("Stage 7 source material does not match the current article route.")

    text = path.read_text(encoding="utf-8").strip()
    if not text or not re.search(r"[\u3400-\u9fff]", text):
        fail("talking_script.txt must contain Chinese spoken text.")
    if re.search(r"^#{1,6}\s", text, flags=re.MULTILINE) or "```" in text or "**" in text:
        fail("talking_script.txt must not contain Markdown formatting.")
    if re.search(r"^\s*(?:[-*+]\s+|\d+[.)、]\s*)", text, flags=re.MULTILINE):
        fail("talking_script.txt must be continuous spoken prose, not a list.")
    if re.search(r"https?://|www\.", text, flags=re.IGNORECASE):
        fail("talking_script.txt must not contain URLs.")

    estimated_seconds = estimate_duration_seconds(text)
    if not args.min_seconds <= estimated_seconds <= MAX_SECONDS:
        fail(
            "talking_script.txt estimated duration is "
            f"{estimated_seconds:.1f}s; expected {args.min_seconds}-{MAX_SECONDS}s at normal speech speed."
        )

    print(json.dumps({
        "stage": "stage7_talking_script",
        "topic_dir": str(topic_dir),
        "estimated_duration_seconds": round(estimated_seconds, 1),
        "estimated_duration_minutes": round(estimated_seconds / 60, 2),
        "article_mode": article_profile["mode"],
        "article_subtype": article_profile["subtype"],
        "status": "passed",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
