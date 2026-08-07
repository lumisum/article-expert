#!/usr/bin/env python3
"""Validate compact Stage 6 title, cover and digest outputs."""

from __future__ import annotations

import argparse
import json
import re

from markdown_to_wechat_html import write_wechat_html
from validation_lib import (
    STAGE3_RECEIPT,
    article_route_key,
    fail,
    has_quantitative_signal,
    load_json,
    nonspace_len,
    require_object,
    require_receipt,
    require_string,
    resolve_topic_dir,
    validate_numeric_claims,
    validate_article_profile,
)

MIN_DIGEST_CHARS = 500
MAX_DIGEST_CHARS = 900
MIN_COVER_PROMPT_CHARS = 1000


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


def validate_packaged_numeric_text(
    payload: dict[str, object],
    key: str,
    text: str,
    owner: str,
    numeric_claims: dict[str, dict[str, object]],
    *,
    title_mode: bool = False,
) -> list[str]:
    values = payload.get(key)
    if not isinstance(values, list):
        fail(f"{owner}.{key} must be a list, including when empty.")
    ids = [str(value).strip().upper() for value in values if str(value).strip()]
    if has_quantitative_signal(text) and not ids:
        fail(f"{owner} contains a factual figure but {key} is empty.")
    if ids and not has_quantitative_signal(text):
        fail(f"{owner}.{key} must be empty when the text contains no factual figure.")
    unknown = sorted(set(ids) - set(numeric_claims))
    if unknown:
        fail(f"{owner}.{key} contains unknown IDs: {', '.join(unknown)}")
    normalized = normalize_numeric_text(text)
    for claim_id in ids:
        claim = numeric_claims[claim_id]
        allowed = str(claim["allowed_wording"]).strip().lower()
        if allowed == "omit" or (title_mode and allowed not in {"exact", "range"}):
            fail(f"{owner} cannot use {claim_id} with allowed_wording={allowed}.")
        publish_text = normalize_numeric_text(str(claim["publish_text"]))
        if publish_text not in normalized:
            fail(
                f"{owner} does not contain {claim_id}'s verified publish_text: "
                f"{claim['publish_text']}"
            )
    return ids


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir")
    args = parser.parse_args()
    topic_dir = resolve_topic_dir(args.topic_dir, "assets/title_cover_package.json")
    article_dir = topic_dir / "article"
    assets_dir = topic_dir / "assets"
    final_path = article_dir / "final_article.md"
    digest_path = article_dir / "final_article_digest.txt"
    image_prompts_path = assets_dir / "image_prompts.jsonl"
    for path in (final_path, digest_path, image_prompts_path):
        if not path.is_file():
            fail(f"Missing Stage 6 file: {path}")

    package = load_json(assets_dir / "title_cover_package.json")
    if not isinstance(package, dict) or package.get("stage") != "title_cover":
        fail('title_cover_package.json.stage must be "title_cover".')
    reader_search_query = require_string(package, "reader_search_query", "title_cover_package")
    require_string(package, "shared_click_hook", "title_cover_package")
    for key in ("familiar_anchor", "hard_tension", "depth_gap", "reader_stake", "promise_evidence"):
        require_string(package, key, "title_cover_package")
    audience = require_object(package, "audience_expansion", "title_cover_package")
    for key in (
        "core_audience",
        "adjacent_audience",
        "broad_audience",
        "expansion_bridge",
        "overreach_boundary",
    ):
        require_string(audience, key, "audience_expansion")
    pack = load_json(topic_dir / "research" / "source_pack.json")
    if not isinstance(pack, dict):
        fail("source_pack.json must be an object.")
    article_profile = validate_article_profile(pack)
    stage3 = require_receipt(topic_dir, STAGE3_RECEIPT, next_stage="Stage 6 title and cover")
    if stage3.get("article_route") != article_route_key(article_profile):
        fail("Stage 6 article profile does not match the validated article route.")
    expected_visual_mode = str(article_profile["visual_mode"])
    expected_style_profile = (
        "white_cinematic_human_micro_3d"
        if expected_visual_mode == "human_scene"
        else "white_material_micro_3d"
    )
    if package.get("visual_mode") != expected_visual_mode:
        fail(f"title_cover_package.visual_mode must be {expected_visual_mode}.")
    if package.get("article_mode") != article_profile["mode"]:
        fail("title_cover_package.article_mode must match source_pack.json.article_profile.")
    if package.get("article_subtype") != article_profile["subtype"]:
        fail("title_cover_package.article_subtype must match source_pack.json.article_profile.")
    numeric_claims = validate_numeric_claims(topic_dir, pack)
    spark_verdict = require_object(pack, "spark_verdict", "source_pack.json")
    expected_spark_id = require_string(
        spark_verdict,
        "spark_id",
        "source_pack.json.spark_verdict",
    ).upper()
    packaged_spark_id = require_string(
        package,
        "spark_id",
        "title_cover_package",
    ).upper()
    if packaged_spark_id != expected_spark_id:
        fail("title_cover_package.spark_id must match source_pack.json.spark_verdict.")
    require_string(package, "spark_to_click_hook", "title_cover_package")
    require_string(package, "spark_visual_translation", "title_cover_package")
    problem = require_object(pack, "reader_problem", "source_pack.json")
    expected_query = require_string(problem, "search_query", "source_pack.json.reader_problem")
    if reader_search_query != expected_query:
        fail("title_cover_package.reader_search_query must match source_pack.json.reader_problem.search_query.")
    candidates = package.get("title_candidates")
    if not isinstance(candidates, list) or len(candidates) != 3:
        fail("title_candidates must contain exactly 3 items.")
    titles: set[str] = set()
    for index, item in enumerate(candidates):
        owner = f"title_candidates[{index}]"
        if not isinstance(item, dict):
            fail(f"{owner} must be an object.")
        for key in (
            "title",
            "naming_approach",
            "audience_scope",
            "familiarity",
            "hardness",
            "depth_signal",
            "reader_stake",
            "why_it_clicks",
            "trust_check",
            "spark_expression",
        ):
            require_string(item, key, owner)
        title = str(item["title"]).strip()
        if title in titles:
            fail(f"Duplicate title candidate: {title}")
        if not re.search(r"[\u4e00-\u9fff]", title):
            fail(f"{owner}.title must contain Chinese text.")
        validate_packaged_numeric_text(
            item,
            "numeric_claim_ids",
            title,
            owner,
            numeric_claims,
            title_mode=True,
        )
        titles.add(title)
    selected_title = require_string(package, "selected_title", "title_cover_package")
    require_string(package, "selected_reason", "title_cover_package")
    if selected_title not in titles:
        fail("selected_title must be one of the three title candidates.")

    cover = require_object(package, "cover_prompt", "title_cover_package")
    if cover.get("image_id") != "cover" or cover.get("image_type") != "cover":
        fail("cover_prompt must use image_id=cover and image_type=cover.")
    if cover.get("canvas_size") != "900x383" or cover.get("aspect_ratio") != "2.35:1":
        fail("cover_prompt must use canvas_size=900x383 and aspect_ratio=2.35:1.")
    if cover.get("visual_mode") != expected_visual_mode:
        fail(f"cover_prompt.visual_mode must be {expected_visual_mode}.")
    if cover.get("style_profile") != expected_style_profile:
        fail(f"cover_prompt.style_profile must be {expected_style_profile}.")
    accent = require_string(cover, "accent_color", "cover_prompt")
    if "#" not in accent:
        fail("cover_prompt.accent_color must include a hex value.")
    colors = cover.get("supporting_colors")
    if not isinstance(colors, list) or not 3 <= len(colors) <= 4:
        fail("cover_prompt.supporting_colors must contain 3-4 colors.")
    if any(not isinstance(color, str) or "#" not in color for color in colors):
        fail("cover_prompt.supporting_colors must include names and hex values.")
    elements = cover.get("visual_elements")
    if not isinstance(elements, list) or not 7 <= len(elements) <= 11:
        fail("cover_prompt.visual_elements must contain 7-11 concrete elements.")
    if any(not isinstance(value, str) or not value.strip() or not re.search(r"[\u4e00-\u9fff]", value) for value in elements):
        fail("cover_prompt.visual_elements must contain concrete Chinese elements.")
    cover_keys = (
        "cover_subject", "cover_action", "cover_visible_stakes", "cover_click_trigger",
        "one_second_read", "thumbnail_test",
        "ratio_composition_plan", "composition_plan", "detail_density_plan",
        "camera_plan", "material_detail_plan", "lighting_plan", "atmosphere_plan",
        "surface_detail_plan",
        "visual_hierarchy", "color_plan", "cover_text_strategy", "center_safe_zone_plan",
    )
    for key in cover_keys:
        require_string(cover, key, "cover_prompt")
    prompt = require_string(cover, "image_prompt", "cover_prompt")
    require_string(cover, "output_filename", "cover_prompt")
    prompt_chars = nonspace_len(prompt)
    if prompt_chars < MIN_COVER_PROMPT_CHARS:
        fail(f"cover_prompt.image_prompt must contain at least {MIN_COVER_PROMPT_CHARS} non-space characters.")
    for term in ("900x383", "2.35:1", "白色"):
        if term not in prompt and term.replace(" ", "") not in prompt:
            fail(f'cover_prompt.image_prompt must mention "{term}".')
    if "微3D" not in prompt and "微 3D" not in prompt:
        fail("cover_prompt.image_prompt must specify the micro 3D style.")
    if selected_title not in prompt:
        fail("cover_prompt.image_prompt must include the selected Chinese title.")
    if cover.get("image_status") != "pending" or cover.get("attempts") != 0:
        fail("cover_prompt must start with image_status=pending and attempts=0.")

    final = final_path.read_text(encoding="utf-8")
    if selected_title not in final[:300]:
        fail("selected_title must be synchronized to final_article.md.")
    copy_path = write_wechat_html(topic_dir, quiet=True)
    html = copy_path.read_text(encoding="utf-8")
    if selected_title not in html or 'data-wa-format="opening-lead"' not in html:
        fail(
            "final_article_copy.html missing selected_title or opening-lead after rebuild; "
            "check title sync and that the article has a substantive opening paragraph."
        )

    digest = digest_path.read_text(encoding="utf-8").strip()
    digest_chars = nonspace_len(digest)
    if not MIN_DIGEST_CHARS <= digest_chars <= MAX_DIGEST_CHARS:
        fail(f"final_article_digest.txt must contain {MIN_DIGEST_CHARS}-{MAX_DIGEST_CHARS} non-space characters.")
    if re.search(r"^#{1,6}\s", digest, flags=re.MULTILINE) or "**" in digest:
        fail("final_article_digest.txt must be plain text without Markdown formatting.")
    if not re.search(r"[\u4e00-\u9fff]", digest):
        fail("final_article_digest.txt must be Chinese.")
    digest_numeric_ids = validate_packaged_numeric_text(
        package,
        "digest_numeric_claim_ids",
        digest,
        "title_cover_package",
        numeric_claims,
    )

    print(json.dumps({"stage": "stage6_title_cover", "topic_dir": str(topic_dir), "spark_id": packaged_spark_id, "title_candidates": 3, "selected_title": selected_title, "digest_chars": digest_chars, "digest_numeric_claims": len(digest_numeric_ids), "status": "passed"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
