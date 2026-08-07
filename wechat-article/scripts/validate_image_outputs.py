#!/usr/bin/env python3
"""Validate Stage 5 placeholders + section image prompts."""

from __future__ import annotations

import argparse
import json
import re
from typing import Any

from markdown_to_wechat_html import write_wechat_html
from validation_lib import (
    STAGE3_RECEIPT,
    article_route_key,
    fail,
    has_quantitative_signal,
    load_json,
    nonspace_len,
    require_string,
    require_receipt,
    resolve_topic_dir,
    validate_numeric_claims,
    validate_article_profile,
)

MIN_PROMPT_CHARS = 1000
STYLE_PROFILE = "white_material_micro_3d"
DIAGRAM_TYPES = {
    "pipeline", "cycle", "hub_and_spoke", "before_after",
    "layer_stack", "data_scene", "mechanism_scene", "human_scene",
    "editorial_scene", "symbolic_still_life", "spatial_metaphor",
}


def has_chinese(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def normalize_numeric_text(text: str) -> str:
    return (
        re.sub(r"\s+", "", text)
        .replace(",", "")
        .replace("，", "")
        .replace("％", "%")
        .replace("–", "-")
        .replace("—", "-")
        .lower()
    )


def validate_prompt(
    item: dict[str, Any],
    line_no: int,
    numeric_claims: dict[str, dict[str, Any]],
    expected_visual_mode: str,
    expected_style_profile: str,
    expected_article_mode: str,
    expected_article_subtype: str,
) -> str:
    owner = f"image_prompts.jsonl line {line_no}"
    image_id = require_string(item, "image_id", owner)
    if not re.fullmatch(r"section_\d{2}", image_id):
        fail(f"{owner}.image_id must match section_XX.")
    if item.get("image_type") != "section":
        fail(f'{image_id}.image_type must be "section".')
    if item.get("aspect_ratio") != "3:4":
        fail(f'{image_id}.aspect_ratio must be "3:4".')
    if item.get("visual_mode") != expected_visual_mode:
        fail(f'{image_id}.visual_mode must be "{expected_visual_mode}".')
    if item.get("article_mode") != expected_article_mode:
        fail(f'{image_id}.article_mode must be "{expected_article_mode}".')
    if item.get("article_subtype") != expected_article_subtype:
        fail(f'{image_id}.article_subtype must be "{expected_article_subtype}".')
    if item.get("style_profile") != expected_style_profile:
        fail(f'{image_id}.style_profile must be "{expected_style_profile}".')

    accent = require_string(item, "accent_color", image_id)
    if "#" not in accent:
        fail(f"{image_id}.accent_color must include a hex value.")
    colors = item.get("supporting_colors")
    if not isinstance(colors, list) or not 3 <= len(colors) <= 4:
        fail(f"{image_id}.supporting_colors must contain 3-4 colors.")
    if any(not isinstance(color, str) or "#" not in color for color in colors):
        fail(f"{image_id}.supporting_colors must include color names and hex values.")

    context_keys = (
        "section_title", "section_anchor", "image_purpose", "visualized_point",
        "core_conflict", "reader_takeaway", "ratio_composition_plan",
        "composition_plan", "detail_density_plan", "camera_plan",
        "material_detail_plan", "lighting_plan", "atmosphere_plan", "surface_detail_plan",
        "color_plan", "required_text",
    )
    for key in context_keys:
        value = require_string(item, key, image_id)
        if not has_chinese(value):
            fail(f"{image_id}.{key} must contain Chinese article context.")

    elements = item.get("visual_elements")
    if not isinstance(elements, list) or not 6 <= len(elements) <= 10:
        fail(f"{image_id}.visual_elements must contain 6-10 items.")
    if any(not isinstance(value, str) or not value.strip() or not has_chinese(value) for value in elements):
        fail(f"{image_id}.visual_elements must contain concrete Chinese elements.")
    if item.get("diagram_type") not in DIAGRAM_TYPES:
        fail(f"{image_id}.diagram_type must be one of {sorted(DIAGRAM_TYPES)}.")

    labels = item.get("chinese_labels")
    if not isinstance(labels, list):
        fail(f"{image_id}.chinese_labels must be a list.")
    if expected_visual_mode == "human_scene":
        if len(labels) > 1:
            fail(f"{image_id}.chinese_labels must contain 0-1 natural scene labels for human_scene.")
        if item.get("diagram_type") not in {"human_scene", "editorial_scene"}:
            fail(f"{image_id}.diagram_type must be human_scene or editorial_scene.")
    elif not 3 <= len(labels) <= 5:
        fail(f"{image_id}.chinese_labels must contain 3-5 items.")
    for label in labels:
        if not isinstance(label, str) or not has_chinese(label) or len(label.strip()) > 8:
            fail(f"{image_id}.chinese_labels must be short Chinese labels of at most 8 characters.")

    numeric_values = item.get("numeric_claim_ids")
    if not isinstance(numeric_values, list):
        fail(f"{image_id}.numeric_claim_ids must be a list, including when empty.")
    numeric_ids = [str(value).strip().upper() for value in numeric_values if str(value).strip()]
    numeric_surface = " ".join(
        [
            str(item.get("section_anchor") or ""),
            str(item.get("visualized_point") or ""),
            str(item.get("required_text") or ""),
            *[str(label) for label in labels],
        ]
    )
    if has_quantitative_signal(numeric_surface) and not numeric_ids:
        fail(f"{image_id} visualizes a factual figure but has no numeric_claim_ids.")
    unknown = sorted(set(numeric_ids) - set(numeric_claims))
    if unknown:
        fail(f"{image_id}.numeric_claim_ids contains unknown IDs: {', '.join(unknown)}")
    normalized_surface = normalize_numeric_text(numeric_surface)
    for claim_id in numeric_ids:
        claim = numeric_claims[claim_id]
        if str(claim["allowed_wording"]).strip().lower() == "omit":
            fail(f"{image_id} cannot visualize {claim_id}; allowed_wording is omit.")
        if normalize_numeric_text(str(claim["publish_text"])) not in normalized_surface:
            fail(
                f"{image_id} does not contain {claim_id}'s verified publish_text: "
                f"{claim['publish_text']}"
            )

    prompt = require_string(item, "image_prompt", image_id)
    if nonspace_len(prompt) < MIN_PROMPT_CHARS:
        fail(f"{image_id}.image_prompt must contain at least {MIN_PROMPT_CHARS} non-space characters.")
    for term in ("3:4", "白色"):
        if term not in prompt:
            fail(f'{image_id}.image_prompt must include "{term}".')
    if "微3D" not in prompt and "微 3D" not in prompt:
        fail(f"{image_id}.image_prompt must specify the micro 3D style.")
    if item.get("image_status") != "pending" or item.get("attempts") != 0:
        fail(f"{image_id} must start with image_status=pending and attempts=0.")
    require_string(item, "output_filename", image_id)
    return image_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir")
    args = parser.parse_args()
    topic_dir = resolve_topic_dir(args.topic_dir, "assets/image_prompts.jsonl")
    article_dir = topic_dir / "article"
    assets_dir = topic_dir / "assets"
    path = assets_dir / "image_prompts.jsonl"
    final_path = article_dir / "final_article.md"
    for required in (path, final_path):
        if not required.is_file():
            fail(f"Missing Stage 5 file: {required}")
    pack = load_json(topic_dir / "research" / "source_pack.json")
    if not isinstance(pack, dict):
        fail("source_pack.json must be an object.")
    article_profile = validate_article_profile(pack)
    stage3 = require_receipt(topic_dir, STAGE3_RECEIPT, next_stage="Stage 5 images")
    if stage3.get("article_route") != article_route_key(article_profile):
        fail("Stage 5 article profile does not match the validated article route.")
    expected_visual_mode = str(article_profile["visual_mode"])
    expected_style_profile = (
        "white_cinematic_human_micro_3d"
        if expected_visual_mode == "human_scene"
        else STYLE_PROFILE
    )
    numeric_claims = validate_numeric_claims(topic_dir, pack)
    scripts = [p.name for p in assets_dir.iterdir() if p.is_file() and p.suffix in {".py", ".sh", ".js", ".ts"}]
    if scripts:
        fail(f"assets/ must not contain scripts: {', '.join(scripts)}")

    ids: list[str] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"Invalid JSONL at line {line_no}: {exc}")
        if not isinstance(item, dict):
            fail(f"image_prompts.jsonl line {line_no} must be an object.")
        ids.append(
            validate_prompt(
                item,
                line_no,
                numeric_claims,
                expected_visual_mode,
                expected_style_profile,
                str(article_profile["mode"]),
                str(article_profile["subtype"]),
            )
        )

    final = final_path.read_text(encoding="utf-8")
    copy_path = write_wechat_html(topic_dir, quiet=True)
    html = copy_path.read_text(encoding="utf-8")
    sections = re.findall(r"^##\s+\S+", final, flags=re.MULTILINE)
    expected = [f"section_{index:02d}" for index in range(1, len(sections) + 1)]
    if ids != expected:
        fail(f"Prompt IDs must match section order: expected {expected}, got {ids}.")
    for image_id in ids:
        marker_re = re.compile(
            rf"<!--\s*IMAGE:{re.escape(image_id)}\s*-->",
            flags=re.IGNORECASE,
        )
        occurrences = marker_re.findall(final)
        standalone = re.findall(
            rf"(?m)^\s*<!--\s*IMAGE:{re.escape(image_id)}\s*-->\s*$",
            final,
            flags=re.IGNORECASE,
        )
        if len(occurrences) != 1 or len(standalone) != 1:
            fail(
                f"final_article.md must contain {image_id} exactly once and on "
                f"its own line; found {len(occurrences)} occurrence(s)."
            )
        if f'data-fp-image-placeholder="{image_id}"' not in html:
            fail(f"final_article_copy.html is missing {image_id} placeholder.")
        if html.count(f'data-fp-image-placeholder="{image_id}"') != 1:
            fail(f"final_article_copy.html must render {image_id} exactly once.")
    if "../assets/" in html:
        fail("final_article_copy.html must keep placeholders instead of local asset paths.")

    print(json.dumps({"stage": "stage5_images", "topic_dir": str(topic_dir), "section_image_count": len(ids), "status": "passed"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
