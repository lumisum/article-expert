#!/usr/bin/env python3
"""Deterministic stage gates for the midlife-article workflow."""

from __future__ import annotations

import argparse
import hashlib
import html as html_module
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from markdown_to_wechat_html import write_wechat_html
from path_utils import ensure_topic_dir, expand_user_path


CONTRACT_VERSION = 6
RENDERER_VERSION = 6
ARTICLE_CONTRACT_VERSION = 2
IMAGE_PROMPT_VERSION = 7
COVER_PROMPT_VERSION = 5
NARRATION_VERSION = 2
VISUAL_PALETTE_PROFILE = "pearl_mist_midlife"
VISUAL_BACKGROUND_HEX = "#F3F4F1"
RECEIPTS = {
    1: "research/stage1_receipt.json",
    2: "article/stage2_receipt.json",
    3: "article/stage3_receipt.json",
    4: "article/stage4_receipt.json",
    5: "assets/stage5_receipt.json",
    6: "assets/stage6_receipt.json",
    7: "video/stage7_receipt.json",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> Any:
    if not path.is_file():
        fail(f"Missing JSON file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")


def require_object(value: Any, owner: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{owner} must be an object.")
    return value


def require_list(value: Any, owner: str, *, allow_empty: bool = False) -> list[Any]:
    if not isinstance(value, list) or (not allow_empty and not value):
        fail(f"{owner} must be a {'list' if allow_empty else 'non-empty list'}.")
    return value


def require_text(obj: dict[str, Any], key: str, owner: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"{owner}.{key} must be a non-empty string.")
    return value.strip()


def nonspace(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def stage1_payload(pack: dict[str, Any], blueprint: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "topic_id",
        "article_profile",
        "user_materials",
        "observation_cards",
        "fact_conflicts",
        "known_unknowns",
        "selected_source_files",
    )
    return {"blueprint": blueprint, **{key: pack.get(key) for key in keys}}


def stage2_payload(pack: dict[str, Any], mindmap: str) -> dict[str, Any]:
    return {
        "causal_spine": pack.get("causal_spine"),
        "coordinates": pack.get("coordinates"),
        "spark": pack.get("spark"),
        "pre_philosophical_proposition": pack.get(
            "pre_philosophical_proposition"
        ),
        "spark_rounds": pack.get("spark_rounds"),
        "mindmap": mindmap,
    }


def stage3_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "causal_audit": pack.get("causal_audit"),
        "wisdom_candidates": pack.get("wisdom_candidates"),
        "wisdom_synthesis": pack.get("wisdom_synthesis"),
        "spark_verdict": pack.get("spark_verdict"),
        "thesis_practice_consistency": pack.get("thesis_practice_consistency"),
        "practice_design": pack.get("practice_design"),
        "anti_anxiety_audit": pack.get("anti_anxiety_audit"),
    }


def file_hash(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage4_markdown_payload(path: Path) -> str:
    if not path.is_file():
        return ""
    markdown = path.read_text(encoding="utf-8")
    markdown = re.sub(r"(?m)^#\s+.+$", "# [TITLE]", markdown, count=1)
    markdown = re.sub(r"(?m)^\s*<!--\s*IMAGE:section_\d+\s*-->\s*$", "", markdown)
    return re.sub(r"\s+", " ", markdown).strip()


def stage5_layout_payload(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    markdown = path.read_text(encoding="utf-8")
    return {
        "sections": markdown_sections(markdown),
        "image_markers": re.findall(
            r"<!--\s*IMAGE:(section_\d+)\s*-->",
            markdown,
        ),
    }


def receipt_signature(topic_dir: Path, stage: int) -> str:
    pack_path = topic_dir / "research" / "source_pack.json"
    pack = require_object(load_json(pack_path), "source_pack.json")
    if stage == 1:
        blueprint = require_object(
            load_json(topic_dir / "research" / "midlife_blueprint.json"),
            "midlife_blueprint.json",
        )
        return canonical_hash(stage1_payload(pack, blueprint))
    if stage == 2:
        mindmap_path = topic_dir / "article" / "causal_mindmap.md"
        if not mindmap_path.is_file():
            fail(f"Missing file: {mindmap_path}")
        return canonical_hash(stage2_payload(pack, mindmap_path.read_text(encoding="utf-8")))
    if stage == 3:
        return canonical_hash(stage3_payload(pack))
    if stage == 4:
        return canonical_hash(
            {
                "renderer_version": RENDERER_VERSION,
                "article_contract_version": ARTICLE_CONTRACT_VERSION,
                "article": stage4_markdown_payload(
                    topic_dir / "article" / "final_article.md"
                ),
                "html": file_hash(
                    topic_dir / "article" / "final_article_copy.html"
                ),
            }
        )
    if stage == 5:
        return canonical_hash(
            {
                "image_prompt_version": IMAGE_PROMPT_VERSION,
                "layout": stage5_layout_payload(
                    topic_dir / "article" / "final_article.md"
                ),
                "visual_system": file_hash(
                    topic_dir / "assets" / "image_visual_system.json"
                ),
                "prompts": file_hash(topic_dir / "assets" / "image_prompts.jsonl"),
            }
        )
    if stage == 6:
        return canonical_hash(
            {
                "cover_prompt_version": COVER_PROMPT_VERSION,
                "md": file_hash(topic_dir / "article" / "final_article.md"),
                "package": file_hash(topic_dir / "assets" / "title_cover_package.json"),
                "digest": file_hash(topic_dir / "article" / "final_article_digest.txt"),
            }
        )
    prompts = load_jsonl(topic_dir / "assets" / "image_prompts.jsonl")
    audio_hashes = {
        require_text(item, "image_id", "image_prompt"): file_hash(
            topic_dir
            / "video"
            / "audio"
            / f"{require_text(item, 'image_id', 'image_prompt')}.mp3"
        )
        for item in prompts
    }
    return canonical_hash(
        {
            "narration_version": NARRATION_VERSION,
            "upstream_stage6": receipt_signature(topic_dir, 6),
            "image_prompts": file_hash(
                topic_dir / "assets" / "image_prompts.jsonl"
            ),
            "narration_segments": file_hash(
                topic_dir / "video" / "narration_segments.jsonl"
            ),
            "audio_manifest": file_hash(
                topic_dir / "video" / "audio_manifest.json"
            ),
            "audio_files": audio_hashes,
        }
    )


def write_receipt(topic_dir: Path, stage: int, extra: dict[str, Any]) -> Path:
    relative = RECEIPTS[stage]
    path = topic_dir / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "stage": stage,
        "contract_version": CONTRACT_VERSION,
        "status": "passed",
        "signature": receipt_signature(topic_dir, stage),
        "validated_at": datetime.now(timezone.utc).isoformat(),
        **extra,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def require_receipt(topic_dir: Path, stage: int) -> dict[str, Any]:
    path = topic_dir / RECEIPTS[stage]
    data = require_object(load_json(path), str(path))
    if (
        data.get("stage") != stage
        or data.get("status") != "passed"
        or data.get("contract_version") != CONTRACT_VERSION
    ):
        fail(f"{path} is not a current passed receipt.")
    if data.get("signature") != receipt_signature(topic_dir, stage):
        fail(f"{path} is stale. Re-run Stage {stage}.")
    return data


def validate_profile(pack: dict[str, Any]) -> None:
    profile = require_object(pack.get("article_profile"), "source_pack.article_profile")
    if require_text(profile, "mode", "article_profile") != "midlife_insight":
        fail("article_profile.mode must be midlife_insight.")
    for key in ("core_audience", "source_anchor", "visual_mode"):
        require_text(profile, key, "article_profile")
    help_contract = require_object(
        profile.get("help_contract"),
        "article_profile.help_contract",
    )
    for key in (
        "primary_help",
        "current_constraint",
        "restored_capacity",
        "agency_window",
        "confidence_basis",
        "first_realistic_step",
        "anti_anxiety_boundary",
    ):
        require_text(help_contract, key, "article_profile.help_contract")
    reader_contract = require_object(
        profile.get("reader_contract"),
        "article_profile.reader_contract",
    )
    for key in (
        "recognition_scene",
        "permission_to_release",
        "responsibility_to_keep",
        "likely_share_recipient",
        "shareable_understanding",
        "background_assumption",
    ):
        require_text(reader_contract, key, "article_profile.reader_contract")


def validate_stage0(scan_dir: Path) -> dict[str, Any]:
    path = scan_dir / "research" / "topic_candidates.json"
    data = require_object(load_json(path), "topic_candidates.json")
    candidates = require_list(data.get("candidates"), "topic_candidates.candidates")
    if len(candidates) != 3:
        fail("Stage 0 must produce exactly three candidates.")
    ids: set[str] = set()
    for index, item in enumerate(candidates):
        candidate = require_object(item, f"candidates[{index}]")
        candidate_id = require_text(candidate, "id", f"candidates[{index}]")
        if candidate_id in ids:
            fail(f"Duplicate candidate id: {candidate_id}")
        ids.add(candidate_id)
        for key in (
            "reader_scene",
            "central_question",
            "why_now",
            "oral_material_needed",
            "traffic_reason",
            "reader_recognition",
            "permission_need",
            "share_recipient",
            "share_reason",
            "primary_help",
            "confidence_path",
            "anxiety_risk",
            "risk",
        ):
            require_text(candidate, key, f"candidates[{index}]")
        searches = require_list(
            candidate.get("search_language"), f"candidates[{index}].search_language"
        )
        if any(not isinstance(value, str) or not value.strip() for value in searches):
            fail(f"candidates[{index}].search_language contains an empty value.")
    return {"candidates": len(candidates), "path": str(path)}


def validate_stage1(topic_dir: Path) -> dict[str, Any]:
    blueprint = require_object(
        load_json(topic_dir / "research" / "midlife_blueprint.json"),
        "midlife_blueprint.json",
    )
    for key in (
        "topic_id",
        "central_event",
        "central_question",
        "core_reader",
        "reader_pain",
        "reader_help",
        "reader_before",
        "reader_after",
        "oral_anchor",
        "evidence_policy",
        "evidence_reason",
        "visual_world",
    ):
        require_text(blueprint, key, "midlife_blueprint")
    narrative_position = require_object(
        blueprint.get("narrative_position"),
        "midlife_blueprint.narrative_position",
    )
    for key in (
        "speaker_relation",
        "trigger_to_write",
        "known_from_life",
        "reflection_boundary",
        "judgment_at_stake",
    ):
        require_text(
            narrative_position,
            key,
            "midlife_blueprint.narrative_position",
        )
    story_materials = require_list(
        blueprint.get("story_materials"),
        "midlife_blueprint.story_materials",
        minimum=1,
    )
    material_basis: list[tuple[str, list[str]]] = []
    allowed_material_kinds = {
        "scene",
        "action",
        "quote",
        "choice",
        "conflict",
        "consequence",
        "later_change",
        "boundary",
    }
    material_ids: set[str] = set()
    for index, value in enumerate(story_materials):
        owner = f"midlife_blueprint.story_materials[{index}]"
        material = require_object(value, owner)
        material_id = require_text(material, "id", owner)
        if material_id in material_ids:
            fail(f"Duplicate story material id: {material_id}")
        material_ids.add(material_id)
        if require_text(material, "kind", owner) not in allowed_material_kinds:
            fail(f"{owner}.kind is invalid.")
        for key in ("content", "narrative_role"):
            require_text(material, key, owner)
        basis_values = require_list(
            material.get("basis_ids"),
            f"{owner}.basis_ids",
        )
        if any(
            not isinstance(item, str) or not item.strip()
            for item in basis_values
        ):
            fail(f"{owner}.basis_ids must contain non-empty strings.")
        material_basis.append(
            (
                owner,
                [item.strip().upper() for item in basis_values],
            )
        )
    evidence_policy = blueprint["evidence_policy"]
    if evidence_policy not in {"oral_only", "authoritative_required"}:
        fail(
            "midlife_blueprint.evidence_policy must be oral_only "
            "or authoritative_required."
        )
    require_list(blueprint.get("research_gaps"), "midlife_blueprint.research_gaps", allow_empty=True)

    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"), "source_pack.json"
    )
    validate_profile(pack)
    help_contract = require_object(
        require_object(
            pack.get("article_profile"),
            "source_pack.article_profile",
        ).get("help_contract"),
        "article_profile.help_contract",
    )
    if require_text(blueprint, "reader_help", "midlife_blueprint") != require_text(
        help_contract,
        "primary_help",
        "article_profile.help_contract",
    ):
        fail("midlife_blueprint.reader_help must equal help_contract.primary_help.")
    if require_text(pack, "topic_id", "source_pack") != require_text(
        blueprint, "topic_id", "midlife_blueprint"
    ):
        fail("Blueprint and source_pack topic_id values do not match.")
    user_materials = require_list(
        pack.get("user_materials"), "source_pack.user_materials", allow_empty=True
    )
    cards = require_list(
        pack.get("observation_cards"), "source_pack.observation_cards", allow_empty=True
    )
    if not user_materials and not cards:
        fail("Stage 1 needs user material or observation evidence.")
    known_ids: set[str] = set()
    source_domains: set[str] = set()
    card_roles: set[str] = set()
    for index, value in enumerate(user_materials):
        item = require_object(value, f"user_materials[{index}]")
        item_id = require_text(item, "id", f"user_materials[{index}]").upper()
        if item_id in known_ids:
            fail(f"Duplicate evidence id: {item_id}")
        known_ids.add(item_id)
        for key in ("material_type", "scene", "people", "action_or_quote", "meaning_boundary"):
            require_text(item, key, f"user_materials[{index}]")
    for index, value in enumerate(cards):
        item = require_object(value, f"observation_cards[{index}]")
        item_id = require_text(item, "id", f"observation_cards[{index}]").upper()
        if item_id in known_ids:
            fail(f"Duplicate evidence id: {item_id}")
        known_ids.add(item_id)
        for key in (
            "role",
            "claim",
            "source_url",
            "raw_page_source",
            "supporting_quote",
            "publish_boundary",
        ):
            require_text(item, key, f"observation_cards[{index}]")
        raw_path = topic_dir / require_text(
            item, "raw_page_source", f"observation_cards[{index}]"
        )
        if not raw_path.is_file():
            fail(f"Observation card points to a missing raw page: {raw_path}")
        source_url = require_text(item, "source_url", f"observation_cards[{index}]")
        parsed = urlparse(source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            fail(f"observation_cards[{index}].source_url must be HTTP(S).")
        source_domains.add(parsed.netloc.lower().removeprefix("www."))
        card_roles.add(require_text(item, "role", f"observation_cards[{index}]"))
    for owner, basis_ids in material_basis:
        unknown = set(basis_ids) - known_ids
        if unknown:
            fail(f"{owner} references unknown basis ids: {sorted(unknown)}")
    for key in ("fact_conflicts", "known_unknowns", "selected_source_files"):
        require_list(pack.get(key), f"source_pack.{key}", allow_empty=True)
    for value in pack.get("selected_source_files", []):
        if not isinstance(value, str) or not value.strip():
            fail("source_pack.selected_source_files contains an empty value.")
        if not (topic_dir / value).is_file():
            fail(f"selected_source_files points to a missing file: {value}")
    if evidence_policy == "authoritative_required":
        if len(cards) < 2 or len(source_domains) < 2:
            fail(
                "authoritative_required needs at least two observation cards "
                "from different source domains."
            )
        if "fact" not in card_roles or not card_roles & {"boundary", "counter_signal"}:
            fail(
                "authoritative_required needs both factual support and "
                "a boundary or counter-signal card."
            )
    receipt = write_receipt(
        topic_dir,
        1,
        {
            "evidence_policy": evidence_policy,
            "user_materials": len(user_materials),
            "observation_cards": len(cards),
            "source_domains": len(source_domains),
            "story_materials": len(story_materials),
        },
    )
    return {
        "evidence_policy": evidence_policy,
        "user_materials": len(user_materials),
        "observation_cards": len(cards),
        "source_domains": len(source_domains),
        "story_materials": len(story_materials),
        "receipt": str(receipt),
    }


def evidence_ids(pack: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for key in ("user_materials", "observation_cards"):
        for value in pack.get(key, []):
            if isinstance(value, dict) and value.get("id"):
                result.add(str(value["id"]).strip().upper())
    return result


def external_evidence_ids(pack: dict[str, Any]) -> set[str]:
    return {
        str(value["id"]).strip().upper()
        for value in pack.get("observation_cards", [])
        if isinstance(value, dict) and value.get("id")
    }


def validate_stage2(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 1)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"), "source_pack.json"
    )
    validate_profile(pack)
    spine = require_list(pack.get("causal_spine"), "source_pack.causal_spine")
    if not 5 <= len(spine) <= 7:
        fail(f"causal_spine must contain 5-7 levels; found {len(spine)}.")
    known = evidence_ids(pack)
    external_ids = external_evidence_ids(pack)
    causal_ids: list[str] = []
    for index, value in enumerate(spine, start=1):
        item = require_object(value, f"causal_spine[{index - 1}]")
        if item.get("level") != index:
            fail(f"causal_spine[{index - 1}].level must equal {index}.")
        causal_id = require_text(item, "id", f"causal_spine[{index - 1}]").upper()
        if not re.fullmatch(r"C\d{2}", causal_id):
            fail(f"causal_spine[{index - 1}].id must use C01-style numbering.")
        if causal_id in causal_ids:
            fail(f"Duplicate causal level id: {causal_id}")
        causal_ids.append(causal_id)
        expected = "ROOT" if index == 1 else f"L{index - 1}"
        if require_text(item, "explains_level", f"causal_spine[{index - 1}]").upper() != expected:
            fail(f"causal_spine[{index - 1}].explains_level must be {expected}.")
        for key in (
            "effect",
            "cause",
            "cause_effect_link",
            "reverse_test",
            "reader_facing_expression",
            "judgment_change",
            "counterexample_or_boundary",
            "agency_window",
            "universalization_risk",
            "next_question_or_stop",
        ):
            require_text(item, key, f"causal_spine[{index - 1}]")
        claim_scope = require_text(
            item, "claim_scope", f"causal_spine[{index - 1}]"
        )
        if claim_scope not in {"individual", "common_tendency", "general_pattern"}:
            fail(f"causal_spine[{index - 1}].claim_scope is invalid.")
        evidence_grade = require_text(
            item, "evidence_grade", f"causal_spine[{index - 1}]"
        )
        if evidence_grade not in {
            "oral_fact",
            "external_fact",
            "reasoned_inference",
            "mixed",
        }:
            fail(f"causal_spine[{index - 1}].evidence_grade is invalid.")
        causal_strength = require_text(
            item, "causal_strength", f"causal_spine[{index - 1}]"
        )
        if causal_strength not in {"possible", "probable", "strong"}:
            fail(f"causal_spine[{index - 1}].causal_strength is invalid.")
        item_evidence = require_list(
            item.get("evidence_ids"),
            f"causal_spine[{index - 1}].evidence_ids",
        )
        normalized_evidence = {
            str(evidence).strip().upper() for evidence in item_evidence
        }
        unknown = normalized_evidence - known
        if unknown:
            fail(f"causal_spine[{index - 1}] has unknown evidence: {sorted(unknown)}")
        if claim_scope != "individual" and not normalized_evidence & external_ids:
            fail(
                f"causal_spine[{index - 1}] expands beyond the individual "
                "without external evidence."
            )

    coordinates = require_list(pack.get("coordinates"), "source_pack.coordinates")
    if not 2 <= len(coordinates) <= 6:
        fail("coordinates must contain 2-6 items.")
    coordinate_ids: set[str] = set()
    for index, value in enumerate(coordinates):
        item = require_object(value, f"coordinates[{index}]")
        coordinate_ids.add(require_text(item, "id", f"coordinates[{index}]").upper())
        for key in ("dimension", "reader_connection"):
            require_text(item, key, f"coordinates[{index}]")
        bases = require_list(item.get("causal_basis_ids"), f"coordinates[{index}].causal_basis_ids")
        if set(str(value).upper() for value in bases) - set(causal_ids):
            fail(f"coordinates[{index}] references an unknown causal level.")

    spark = require_object(pack.get("spark"), "source_pack.spark")
    if require_text(spark, "id", "spark").upper() != "S01":
        fail("The workflow permits exactly one Spark with id S01.")
    for key in (
        "question",
        "core_tension",
        "current_judgment",
        "strongest_counterpoint",
        "agency_path",
        "confidence_basis",
        "unnecessary_self_blame",
        "responsibility_to_keep",
        "logical_risk",
        "reader_relation",
    ):
        require_text(spark, key, "spark")
    if set(str(value).upper() for value in require_list(spark.get("causal_basis_ids"), "spark.causal_basis_ids")) - set(causal_ids):
        fail("spark.causal_basis_ids contains an unknown causal level.")
    if set(str(value).upper() for value in require_list(spark.get("coordinate_ids"), "spark.coordinate_ids")) - coordinate_ids:
        fail("spark.coordinate_ids contains an unknown coordinate.")

    proposition = require_object(
        pack.get("pre_philosophical_proposition"),
        "source_pack.pre_philosophical_proposition",
    )
    for key in (
        "human_dilemma",
        "proposition",
        "why_deeper_than_advice",
        "open_philosophical_question",
    ):
        require_text(proposition, key, "pre_philosophical_proposition")
    proposition_bases = {
        str(value).strip().upper()
        for value in require_list(
            proposition.get("story_basis_ids"),
            "pre_philosophical_proposition.story_basis_ids",
        )
    }
    known_proposition_bases = known | set(causal_ids)
    unknown_proposition_bases = proposition_bases - known_proposition_bases
    if unknown_proposition_bases:
        fail(
            "pre_philosophical_proposition has unknown story basis ids: "
            f"{sorted(unknown_proposition_bases)}"
        )
    if not proposition_bases & known or not proposition_bases & set(causal_ids):
        fail(
            "pre_philosophical_proposition must be grounded in both story "
            "evidence and the causal spine."
        )

    rounds = require_list(pack.get("spark_rounds"), "source_pack.spark_rounds")
    if not 4 <= len(rounds) <= 6:
        fail("spark_rounds must contain 4-6 rounds.")
    focuses: set[str] = set()
    previous_after = ""
    for index, value in enumerate(rounds, start=1):
        item = require_object(value, f"spark_rounds[{index - 1}]")
        if item.get("order") != index:
            fail(f"spark_rounds[{index - 1}].order must equal {index}.")
        focus = require_text(item, "focus", f"spark_rounds[{index - 1}]").lower()
        if focus not in {"deepen", "broaden", "challenge", "converge"}:
            fail(f"Unknown Spark focus: {focus}")
        focuses.add(focus)
        for key in ("question_before", "pressure", "revision", "question_after", "judgment_after"):
            require_text(item, key, f"spark_rounds[{index - 1}]")
        if index > 1 and item["question_before"].strip() != previous_after:
            fail("Adjacent Spark rounds must preserve question continuity.")
        previous_after = item["question_after"].strip()
    if not {"deepen", "broaden", "challenge", "converge"} <= focuses:
        fail("spark_rounds must include deepen, broaden, challenge and converge.")
    if rounds[-1]["judgment_after"].strip() != spark["current_judgment"].strip():
        fail("The last Spark judgment must match spark.current_judgment.")

    mindmap_path = topic_dir / "article" / "causal_mindmap.md"
    if not mindmap_path.is_file() or nonspace(mindmap_path.read_text(encoding="utf-8")) < 1200:
        fail("causal_mindmap.md is missing or too thin.")
    receipt = write_receipt(
        topic_dir,
        2,
        {
            "causal_levels": len(spine),
            "spark_rounds": len(rounds),
            "spark_id": "S01",
            "life_proposition": proposition["proposition"],
        },
    )
    return {
        "causal_levels": len(spine),
        "spark_rounds": len(rounds),
        "life_proposition": proposition["proposition"],
        "receipt": str(receipt),
    }


def validate_stage3(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 1)
    require_receipt(topic_dir, 2)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"), "source_pack.json"
    )
    spine = require_list(pack.get("causal_spine"), "source_pack.causal_spine")
    audits = require_list(pack.get("causal_audit"), "source_pack.causal_audit")
    if len(audits) != len(spine) - 1:
        fail("causal_audit must review every adjacent causal transition.")
    for index, value in enumerate(audits, start=1):
        item = require_object(value, f"causal_audit[{index - 1}]")
        if item.get("from_level") != index or item.get("to_level") != index + 1:
            fail(f"causal_audit[{index - 1}] must review L{index}->L{index + 1}.")
        for key in (
            "cause_effect_check",
            "reverse_test",
            "deletion_test",
            "evidence_check",
            "scope_check",
            "reader_language_check",
            "agency_check",
        ):
            require_text(item, key, f"causal_audit[{index - 1}]")
        if require_text(item, "decision", f"causal_audit[{index - 1}]") != "valid":
            fail(f"causal_audit[{index - 1}] requires a return to Stage 2.")

    wisdom = require_list(pack.get("wisdom_candidates"), "source_pack.wisdom_candidates")
    used_wisdom_ids: set[str] = set()
    eastern_used_ids: set[str] = set()
    western_candidate_ids: set[str] = set()
    wisdom_by_id: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(wisdom):
        item = require_object(value, f"wisdom_candidates[{index}]")
        for key in (
            "id",
            "tradition",
            "thinker_or_text",
            "source_url",
            "raw_page_source",
            "description_type",
            "chinese_description",
            "original_context",
            "causal_connection",
            "important_difference",
            "use_decision",
        ):
            require_text(item, key, f"wisdom_candidates[{index}]")
        wisdom_id = item["id"].strip().upper()
        if not re.fullmatch(r"W\d{2}", wisdom_id):
            fail(f"wisdom_candidates[{index}].id must use W01-style numbering.")
        if wisdom_id in wisdom_by_id:
            fail(f"Duplicate wisdom candidate id: {wisdom_id}")
        wisdom_by_id[wisdom_id] = item
        tradition = item["tradition"].strip().lower()
        if tradition not in {"eastern", "western"}:
            fail(f"wisdom_candidates[{index}].tradition is invalid.")
        description_type = item["description_type"].strip().lower()
        if description_type not in {"direct_quote", "faithful_paraphrase"}:
            fail(f"wisdom_candidates[{index}].description_type is invalid.")
        decision = item["use_decision"].strip().lower()
        if decision not in {"use", "reserve", "skip"}:
            fail(f"wisdom_candidates[{index}].use_decision is invalid.")
        parsed_source = urlparse(item["source_url"])
        if parsed_source.scheme not in {"http", "https"} or not parsed_source.netloc:
            fail(f"wisdom_candidates[{index}].source_url must be HTTP(S).")
        raw_path = topic_dir / item["raw_page_source"]
        if not raw_path.is_file():
            fail(f"Researched wisdom source is missing: {raw_path}")
        if tradition == "western":
            western_candidate_ids.add(wisdom_id)
        if decision == "use":
            used_wisdom_ids.add(wisdom_id)
            if tradition == "eastern":
                eastern_used_ids.add(wisdom_id)
    if not eastern_used_ids:
        fail("Stage 3 must use at least one genuinely useful Eastern wisdom source.")
    if not western_candidate_ids:
        fail("Stage 3 must research and evaluate at least one Western wisdom source.")

    proposition = require_object(
        pack.get("pre_philosophical_proposition"),
        "source_pack.pre_philosophical_proposition",
    )
    life_proposition = require_text(
        proposition,
        "proposition",
        "pre_philosophical_proposition",
    )
    synthesis = require_object(
        pack.get("wisdom_synthesis"),
        "source_pack.wisdom_synthesis",
    )
    for key in (
        "life_proposition",
        "eastern_core_id",
        "eastern_explanation",
        "western_candidate_id",
        "western_decision",
        "western_contribution_or_omission_reason",
        "east_west_relationship",
        "relation_to_spark",
        "author_synthesis",
        "return_to_life",
        "anti_pastiche_check",
    ):
        require_text(synthesis, key, "wisdom_synthesis")
    if synthesis["life_proposition"].strip() != life_proposition:
        fail(
            "wisdom_synthesis.life_proposition must exactly preserve the "
            "Stage 2 pre-philosophical proposition."
        )
    eastern_core_id = synthesis["eastern_core_id"].strip().upper()
    if eastern_core_id not in eastern_used_ids:
        fail("wisdom_synthesis.eastern_core_id must reference a used Eastern source.")
    western_candidate_id = synthesis["western_candidate_id"].strip().upper()
    if western_candidate_id not in western_candidate_ids:
        fail(
            "wisdom_synthesis.western_candidate_id must reference a researched "
            "Western source."
        )
    western_decision = synthesis["western_decision"].strip().lower()
    if western_decision not in {"use", "omit"}:
        fail("wisdom_synthesis.western_decision must be use or omit.")
    western_source_decision = (
        wisdom_by_id[western_candidate_id]["use_decision"].strip().lower()
    )
    if western_decision == "use" and western_source_decision != "use":
        fail("A used Western synthesis source must have use_decision=use.")
    if western_decision == "omit" and western_source_decision == "use":
        fail("An omitted Western synthesis source cannot have use_decision=use.")
    relationship = synthesis["east_west_relationship"].strip().lower()
    if relationship not in {"echo", "contrast", "boundary", "complement"}:
        fail("wisdom_synthesis.east_west_relationship is invalid.")

    def normalized_idea(text: str) -> str:
        return re.sub(r"[\s，。！？!?；;：“”\"'、,.：]+", "", text)

    author_idea = normalized_idea(synthesis["author_synthesis"])
    borrowed_ideas = {
        normalized_idea(life_proposition),
        *(
            normalized_idea(item["chinese_description"])
            for item in wisdom_by_id.values()
        ),
    }
    if author_idea in borrowed_ideas:
        fail(
            "wisdom_synthesis.author_synthesis must be the author's new "
            "judgment, not a copied proposition or classic description."
        )

    verdict = require_object(pack.get("spark_verdict"), "source_pack.spark_verdict")
    for key in (
        "spark_id",
        "decision",
        "final_question",
        "final_judgment",
        "publish_thesis",
        "claim_scope",
        "strongest_counterargument",
        "response",
        "boundary",
        "reader_change",
    ):
        require_text(verdict, key, "spark_verdict")
    if verdict["spark_id"].upper() != "S01" or verdict["decision"] not in {"validated", "reframed"}:
        fail("spark_verdict must validate or reframe S01.")
    if verdict["claim_scope"] not in {
        "individual",
        "common_tendency",
        "general_pattern",
    }:
        fail("spark_verdict.claim_scope is invalid.")
    verdict_evidence = {
        str(value).strip().upper()
        for value in require_list(
            verdict.get("evidence_ids"), "spark_verdict.evidence_ids"
        )
    }
    unknown_verdict_evidence = verdict_evidence - evidence_ids(pack)
    if unknown_verdict_evidence:
        fail(
            "spark_verdict has unknown evidence ids: "
            f"{sorted(unknown_verdict_evidence)}"
        )
    if (
        verdict["claim_scope"] != "individual"
        and not verdict_evidence & external_evidence_ids(pack)
    ):
        fail("A non-individual spark verdict requires external evidence.")

    consistency = require_object(
        pack.get("thesis_practice_consistency"),
        "source_pack.thesis_practice_consistency",
    )
    for key in (
        "thesis_claim",
        "implied_world",
        "practice_mechanism",
        "contradiction",
    ):
        require_text(consistency, key, "thesis_practice_consistency")
    if require_text(
        consistency, "decision", "thesis_practice_consistency"
    ) != "valid":
        fail("thesis_practice_consistency requires a return to Stage 2.")

    practice = require_object(pack.get("practice_design"), "source_pack.practice_design")
    for key in (
        "primary_help",
        "reader_scene",
        "choice_principle",
        "restored_capacity",
        "confidence_basis",
        "first_realistic_step",
        "mechanism_link",
        "validation",
        "boundary",
    ):
        require_text(practice, key, "practice_design")
    signals = require_list(practice.get("signals_or_actions"), "practice_design.signals_or_actions")
    if not 1 <= len(signals) <= 3 or any(
        not isinstance(value, str) or not value.strip() for value in signals
    ):
        fail("practice_design must contain 1-3 concrete signals or actions.")
    help_contract = require_object(
        require_object(
            pack.get("article_profile"),
            "source_pack.article_profile",
        ).get("help_contract"),
        "article_profile.help_contract",
    )
    if require_text(practice, "primary_help", "practice_design") != require_text(
        help_contract,
        "primary_help",
        "article_profile.help_contract",
    ):
        fail("practice_design.primary_help must match the Stage 1 help contract.")
    anti_anxiety = require_object(
        pack.get("anti_anxiety_audit"),
        "source_pack.anti_anxiety_audit",
    )
    for key in (
        "difficulty_acknowledged",
        "catastrophizing_removed",
        "unnecessary_burden_released",
        "responsibility_preserved",
        "relief_not_escape",
        "agency_preserved",
        "confidence_not_fabricated",
        "shareable_understanding",
        "expected_reader_state",
    ):
        require_text(anti_anxiety, key, "anti_anxiety_audit")
    if require_text(anti_anxiety, "decision", "anti_anxiety_audit") != "pass":
        fail("anti_anxiety_audit requires a return to Stage 2.")
    receipt = write_receipt(
        topic_dir,
        3,
        {
            "causal_audits": len(audits),
            "used_wisdom": len(used_wisdom_ids),
            "eastern_core_id": eastern_core_id,
            "western_decision": western_decision,
            "consistency": "valid",
            "anti_anxiety": "pass",
            "spark_id": "S01",
        },
    )
    return {
        "causal_audits": len(audits),
        "used_wisdom": len(used_wisdom_ids),
        "eastern_core_id": eastern_core_id,
        "western_decision": western_decision,
        "anti_anxiety": "pass",
        "receipt": str(receipt),
    }


def markdown_sections(markdown: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"(?m)^##\s+(.+?)\s*$", markdown)]


def markdown_section_sizes(markdown: str) -> list[int]:
    headings = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", markdown))
    sizes: list[int] = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(markdown)
        body = markdown[heading.end() : end]
        body = re.sub(r"<!--[\s\S]*?-->", "", body)
        sizes.append(nonspace(body))
    return sizes


def validate_stage4(topic_dir: Path) -> dict[str, Any]:
    for stage in (1, 2, 3):
        require_receipt(topic_dir, stage)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"), "source_pack.json"
    )
    md_path = topic_dir / "article" / "final_article.md"
    if not md_path.is_file():
        fail(f"Missing file: {md_path}")
    markdown = md_path.read_text(encoding="utf-8")
    article_chars = nonspace(markdown)
    if not 1800 <= article_chars <= 2600:
        fail(
            "final_article.md must contain 1800-2600 non-space characters "
            "for the concise midlife article format."
        )
    sections = markdown_sections(markdown)
    if not 4 <= len(sections) <= 6:
        fail(f"final_article.md needs 4-6 major sections; found {len(sections)}.")
    section_sizes = markdown_section_sizes(markdown)
    average_section_size = sum(section_sizes) / len(section_sizes)
    if min(section_sizes) < average_section_size * 0.55:
        fail(
            "Major sections are imbalanced: the shortest section is functioning "
            "as a transition instead of a full chapter."
        )
    if max(section_sizes) > average_section_size * 1.6:
        fail(
            "Major sections are imbalanced: one section is carrying too much of "
            "the article. Redistribute reasoning, wisdom, and practice."
        )
    spine = require_list(pack.get("causal_spine"), "source_pack.causal_spine")
    tags = re.findall(r"<!--\s*DESCENT:L(\d+):(C\d+)\s*-->", markdown)
    expected = [(str(index), str(item["id"]).upper()) for index, item in enumerate(spine, start=1)]
    if [(level, item_id.upper()) for level, item_id in tags] != expected:
        fail(f"Descent markers must match the causal spine: {expected}.")
    spark = require_object(pack.get("spark_verdict"), "source_pack.spark_verdict")
    spark_markers = list(re.finditer(r"<!--\s*SPARK:S01\s*-->", markdown))
    rebound = list(re.finditer(r"<!--\s*REBOUND\s*-->", markdown))
    if len(spark_markers) != 1 or len(rebound) != 1:
        fail("final_article.md needs exactly one SPARK:S01 and one REBOUND marker.")
    between = markdown[spark_markers[0].end() : rebound[0].start()]
    if re.sub(r"[\s*_`]+", "", spark["publish_thesis"]) not in re.sub(
        r"[\s*_`]+", "", between
    ):
        fail("The block after SPARK:S01 must contain publish_thesis verbatim.")
    if rebound[0].start() <= spark_markers[0].start():
        fail("REBOUND must follow SPARK:S01.")
    synthesis = require_object(
        pack.get("wisdom_synthesis"),
        "source_pack.wisdom_synthesis",
    )
    eastern_core_id = require_text(
        synthesis,
        "eastern_core_id",
        "wisdom_synthesis",
    ).upper()
    western_candidate_id = require_text(
        synthesis,
        "western_candidate_id",
        "wisdom_synthesis",
    ).upper()
    western_decision = require_text(
        synthesis,
        "western_decision",
        "wisdom_synthesis",
    ).lower()
    east_markers = list(
        re.finditer(
            rf"<!--\s*WISDOM:EAST:{re.escape(eastern_core_id)}\s*-->",
            markdown,
        )
    )
    all_east_markers = list(
        re.finditer(r"<!--\s*WISDOM:EAST:W\d{2}\s*-->", markdown)
    )
    if len(east_markers) != 1 or len(all_east_markers) != 1:
        fail(
            "final_article.md must contain exactly one Eastern wisdom marker "
            "matching wisdom_synthesis.eastern_core_id."
        )
    all_west_markers = list(
        re.finditer(r"<!--\s*WISDOM:WEST:W\d{2}\s*-->", markdown)
    )
    if western_decision == "use":
        west_markers = list(
            re.finditer(
                rf"<!--\s*WISDOM:WEST:{re.escape(western_candidate_id)}\s*-->",
                markdown,
            )
        )
        if len(west_markers) != 1 or len(all_west_markers) != 1:
            fail(
                "A used Western source needs exactly one matching wisdom marker."
            )
        west_position = west_markers[0].start()
    else:
        if all_west_markers:
            fail("Omitted Western wisdom must not leave a marker in the article.")
        west_position = east_markers[0].start()
    author_markers = list(
        re.finditer(r"<!--\s*AUTHOR:SYNTHESIS\s*-->", markdown)
    )
    if len(author_markers) != 1:
        fail("final_article.md needs exactly one AUTHOR:SYNTHESIS marker.")
    practice_markers = list(
        re.finditer(r"<!--\s*PRACTICE\s*-->", markdown)
    )
    if len(practice_markers) != 1:
        fail("final_article.md needs exactly one PRACTICE marker.")
    if not (
        rebound[0].start()
        < east_markers[0].start()
        <= west_position
        < author_markers[0].start()
        < practice_markers[0].start()
    ):
        fail(
            "The philosophy bridge must follow REBOUND in this order: "
            "Eastern lens, optional Western lens, author synthesis."
        )
    eastern_bridge = markdown[
        east_markers[0].end() :
        (west_position if western_decision == "use" else author_markers[0].start())
    ]
    if nonspace(re.sub(r"<!--[\s\S]*?-->", "", eastern_bridge)) < 60:
        fail(
            "The Eastern philosophy bridge is too thin to explain context, "
            "connection, and boundary."
        )
    if western_decision == "use":
        western_bridge = markdown[
            west_markers[0].end() : author_markers[0].start()
        ]
        if nonspace(re.sub(r"<!--[\s\S]*?-->", "", western_bridge)) < 60:
            fail(
                "The used Western philosophy bridge is too thin to add a "
                "distinct dimension."
            )
    synthesis_tail = markdown[author_markers[0].end() :]
    if re.sub(r"[\s*_`]+", "", synthesis["author_synthesis"]) not in re.sub(
        r"[\s*_`]+", "", synthesis_tail
    ):
        fail(
            "The block after AUTHOR:SYNTHESIS must contain "
            "wisdom_synthesis.author_synthesis verbatim."
        )
    html_path = write_wechat_html(topic_dir, quiet=True)
    html = html_path.read_text(encoding="utf-8")
    if re.search(
        r"(?:DATA:|USER:|DESCENT:|SPARK:|REBOUND|WISDOM:|AUTHOR:|PRACTICE|IMAGE:|@@WA_(?:PHASE|FEATURE)_)",
        html,
    ):
        fail("final_article_copy.html leaks construction markers.")
    if 'font-size: 15px' not in html or 'data-wa-theme="midlife-insight"' not in html:
        fail("final_article_copy.html is not using the midlife 15px theme.")
    oversized_fonts = [
        int(size)
        for size in re.findall(r"font-size:\s*(\d+)px", html)
        if int(size) > 18
    ]
    if oversized_fonts:
        fail(
            "final_article_copy.html contains visible text larger than the "
            "midlife 18px hierarchy ceiling."
        )
    sentence_lines = len(
        re.findall(r'data-wa-format="sentence-line"', html)
    )
    if sentence_lines < nonspace(markdown) / 38:
        fail(
            "final_article_copy.html does not contain enough sentence-led body "
            "lines for midlife reading rhythm."
        )
    line_html = re.findall(
        r'<p data-wa-format="sentence-line"[^>]*>(.*?)</p>',
        html,
        flags=re.DOTALL,
    )
    line_lengths = [
        nonspace(html_module.unescape(re.sub(r"<[^>]+>", "", value)))
        for value in line_html
    ]
    if line_lengths:
        overlong = sum(length > 56 for length in line_lengths)
        if overlong / len(line_lengths) > 0.10:
            fail(
                "Too many sentence-led paragraphs are still long compound "
                "sentences. Rewrite them into complete shorter thoughts."
            )
    receipt = write_receipt(
        topic_dir,
        4,
        {
            "sections": len(sections),
            "nonspace_chars": nonspace(markdown),
            "renderer_version": RENDERER_VERSION,
            "article_contract_version": ARTICLE_CONTRACT_VERSION,
            "sentence_lines": sentence_lines,
            "section_sizes": section_sizes,
            "eastern_core_id": eastern_core_id,
            "western_decision": western_decision,
        },
    )
    return {
        "sections": len(sections),
        "nonspace_chars": nonspace(markdown),
        "sentence_lines": sentence_lines,
        "section_sizes": section_sizes,
        "eastern_core_id": eastern_core_id,
        "western_decision": western_decision,
        "receipt": str(receipt),
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"Missing JSONL file: {path}")
    result: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"Invalid JSONL at {path}:{line_number}: {exc}")
        result.append(require_object(value, f"{path}:{line_number}"))
    return result


def validate_stage5(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 4)
    md_path = topic_dir / "article" / "final_article.md"
    markdown = md_path.read_text(encoding="utf-8")
    sections = markdown_sections(markdown)
    visual_system = require_object(
        load_json(topic_dir / "assets" / "image_visual_system.json"),
        "image_visual_system.json",
    )
    for key in (
        "version",
        "information_visual_mode",
        "selection_reason",
        "article_visual_thesis",
        "uniformity_rule",
    ):
        require_text(visual_system, key, "image_visual_system")
    if visual_system["version"] != "article_information_visual_system_v1":
        fail("image_visual_system.version must be article_information_visual_system_v1.")
    visual_mode = visual_system["information_visual_mode"]
    if visual_mode not in {"micro_3d_info_cards", "micro_3d_editorial_illustration"}:
        fail("image_visual_system.information_visual_mode is invalid.")
    signals = require_list(visual_system.get("selection_signals"), "image_visual_system.selection_signals")
    if not 2 <= len(signals) <= 5 or any(
        not isinstance(value, str) or not value.strip() for value in signals
    ):
        fail("image_visual_system.selection_signals must contain two to five non-empty strings.")
    heading_matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", markdown))
    marker_matches = list(
        re.finditer(r"<!--\s*IMAGE:(section_\d+)\s*-->", markdown)
    )
    markers = [match.group(1) for match in marker_matches]
    expected_ids = [f"section_{index:02d}" for index in range(1, len(sections) + 1)]
    if markers != expected_ids:
        fail(f"Image markers must appear once in section order: {expected_ids}.")
    for index, (heading, image_id) in enumerate(
        zip(heading_matches, expected_ids)
    ):
        section_end = (
            heading_matches[index + 1].start()
            if index + 1 < len(heading_matches)
            else len(markdown)
        )
        in_section = [
            match
            for match in marker_matches
            if heading.end() < match.start() < section_end
        ]
        if len(in_section) != 1 or in_section[0].group(1) != image_id:
            fail(f"{image_id} must appear exactly once inside its own section.")
        lead_in = markdown[heading.end() : in_section[0].start()]
        if nonspace(lead_in) < 40:
            fail(
                f"{image_id} is too close to its section heading; "
                "place it after a meaningful lead-in paragraph."
            )
    prompts = load_jsonl(topic_dir / "assets" / "image_prompts.jsonl")
    if len(prompts) != len(sections):
        fail("image_prompts.jsonl must contain exactly one row per section.")
    for index, (item, section_title, image_id) in enumerate(
        zip(prompts, sections, expected_ids), start=1
    ):
        owner = f"image_prompts[{index - 1}]"
        if require_text(item, "image_id", owner) != image_id:
            fail(f"{owner}.image_id must be {image_id}.")
        if item.get("section_index") != index:
            fail(f"{owner}.section_index must equal {index}.")
        if require_text(item, "section_title", owner) != section_title:
            fail(f"{owner}.section_title must match the Markdown heading.")
        role = require_text(item, "visual_role", owner)
        if role != "hybrid_story_info":
            fail(f"{owner}.visual_role must be hybrid_story_info.")
        if require_text(item, "aspect_ratio", owner) != "3:4":
            fail(f"{owner}.aspect_ratio must be 3:4.")
        for key in (
            "article_context",
            "visual_thesis",
            "subject_profile",
            "female_character_design",
            "female_story_action",
            "scene_layer",
            "information_question",
            "information_form",
            "information_visual_mode",
            "information_rendering",
            "information_layer",
            "layout_ratio",
            "scene_position",
            "information_position",
            "palette_profile",
            "background_color",
            "background_material",
            "accent_color",
            "visual_bridge",
            "shared_anchor",
            "transition_plan",
            "transition_color_plan",
            "transition_light_plan",
            "transition_perspective_plan",
            "reader_takeaway",
            "composition",
            "subjects",
            "color_plan",
            "negative_constraints",
            "prompt",
        ):
            require_text(item, key, owner)
        if require_text(item, "information_visual_mode", owner) != visual_mode:
            fail(f"{owner}.information_visual_mode must match image_visual_system.")
        if visual_mode == "micro_3d_info_cards" and item["information_form"] not in {
            "causal_chain",
            "before_after",
            "timeline",
            "layers",
            "choice_path",
            "relationship_map",
        }:
            fail(f"{owner}.information_form is invalid.")
        if visual_mode == "micro_3d_editorial_illustration":
            for key in (
                "editorial_illustration_structure",
                "editorial_metaphor",
                "editorial_action",
                "editorial_color_roles",
            ):
                require_text(item, key, owner)
            if item["editorial_illustration_structure"] not in {
                "action_metaphor",
                "state_tableau",
                "before_after_tableau",
                "route_metaphor",
                "layered_tableau",
                "relationship_tableau",
            }:
                fail(f"{owner}.editorial_illustration_structure is invalid.")
        if item["subject_profile"] != "attractive_intellectual_woman_28_35":
            fail(
                f"{owner}.subject_profile must be "
                "attractive_intellectual_woman_28_35."
            )
        if item["layout_ratio"] not in {
            "scene_30_info_70",
            "scene_33_info_67",
            "scene_35_info_65",
        }:
            fail(
                f"{owner}.layout_ratio must keep the top scene near one third "
                "and the lower information layer near two thirds."
            )
        if item["scene_position"] != "top_third":
            fail(f"{owner}.scene_position must be top_third.")
        if item["information_position"] != "lower_two_thirds":
            fail(f"{owner}.information_position must be lower_two_thirds.")
        if item["palette_profile"] != VISUAL_PALETTE_PROFILE:
            fail(f"{owner}.palette_profile must be {VISUAL_PALETTE_PROFILE}.")
        if VISUAL_BACKGROUND_HEX not in item["background_color"].upper():
            fail(
                f"{owner}.background_color must use the midlife background "
                f"{VISUAL_BACKGROUND_HEX}."
            )
        if VISUAL_BACKGROUND_HEX not in item["prompt"].upper():
            fail(
                f"{owner}.prompt must explicitly carry the midlife background "
                f"{VISUAL_BACKGROUND_HEX}."
            )
        if visual_mode not in item["prompt"]:
            fail(f"{owner}.prompt must explicitly carry {visual_mode}.")
        if visual_mode == "micro_3d_editorial_illustration":
            for required in ("微3D", "原创", "禁止固定角色", "富配色"):
                if required not in item["prompt"]:
                    fail(f"{owner}.prompt must include illustration constraint: {required}.")
        if not re.search(r"#[0-9A-Fa-f]{6}\b", item["accent_color"]):
            fail(f"{owner}.accent_color must include a six-digit HEX value.")
        supporting = require_list(
            item.get("supporting_colors"),
            f"{owner}.supporting_colors",
        )
        if not 3 <= len(supporting) <= 4 or any(
            not isinstance(value, str)
            or not re.search(r"#[0-9A-Fa-f]{6}\b", value)
            for value in supporting
        ):
            fail(
                f"{owner}.supporting_colors must contain three or four HEX colors."
            )
        if visual_mode == "micro_3d_editorial_illustration":
            for color in [item["accent_color"], *supporting]:
                match = re.search(r"#[0-9A-Fa-f]{6}\b", color)
                if match and match.group(0).upper() not in item["prompt"].upper():
                    fail(f"{owner}.prompt must use illustration color {match.group(0)}.")
        if nonspace(item["prompt"]) <= 700:
            fail(f"{owner}.prompt must exceed 700 non-whitespace characters.")
    write_wechat_html(topic_dir, quiet=True)
    receipt = write_receipt(
        topic_dir,
        5,
        {
            "images": len(prompts),
            "hybrid_images": len(prompts),
            "information_visual_mode": visual_mode,
            "image_prompt_version": IMAGE_PROMPT_VERSION,
        },
    )
    return {
        "images": len(prompts),
        "hybrid_images": len(prompts),
        "information_visual_mode": visual_mode,
        "image_prompt_version": IMAGE_PROMPT_VERSION,
        "receipt": str(receipt),
    }


def title_evidence_text(pack: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key, fields in (
        (
            "user_materials",
            ("scene", "people", "action_or_quote", "meaning_boundary"),
        ),
        (
            "observation_cards",
            ("claim", "supporting_quote", "publish_boundary"),
        ),
    ):
        for value in pack.get(key, []):
            if not isinstance(value, dict) or not value.get("id"):
                continue
            item_id = str(value["id"]).strip().upper()
            result[item_id] = " ".join(
                str(value.get(field) or "") for field in fields
            )
    return result


def validate_stage6(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 5)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"),
        "source_pack.json",
    )
    title_sources = title_evidence_text(pack)
    package = require_object(
        load_json(topic_dir / "assets" / "title_cover_package.json"),
        "title_cover_package.json",
    )
    candidates = require_list(package.get("title_candidates"), "title_candidates")
    if len(candidates) < 5:
        fail("Stage 6 must compare at least five title candidates.")
    titles: list[str] = []
    for index, value in enumerate(candidates):
        item = require_object(value, f"title_candidates[{index}]")
        owner = f"title_candidates[{index}]"
        title = require_text(item, "title", owner)
        titles.append(title)
        for key in (
            "reader_hook",
            "psychology",
            "promise",
            "permission_without_escape",
            "share_trigger",
            "risk",
        ):
            require_text(item, key, owner)
        basis_ids = {
            str(value).strip().upper()
            for value in require_list(
                item.get("evidence_basis_ids"),
                f"{owner}.evidence_basis_ids",
            )
        }
        unknown_basis = basis_ids - set(title_sources)
        if unknown_basis:
            fail(f"{owner} has unknown evidence basis ids: {sorted(unknown_basis)}")
        basis_text = " ".join(title_sources[value] for value in basis_ids)
        numeric_tokens = re.findall(r"\d+(?:\.\d+)?", title)
        numeric_tokens += re.findall(
            r"[零〇一二两三四五六七八九十百千万]+"
            r"(?:岁|年|遍|次|天|个月|月|小时|分钟|元)",
            title,
        )
        for token in numeric_tokens:
            if token not in basis_text:
                fail(
                    f"{owner} uses numeric token {token!r} without verbatim "
                    "support in its evidence basis."
                )
    selected = require_text(package, "selected_title", "title_cover_package")
    if selected not in titles:
        fail("selected_title must be one of title_candidates.")
    scores = require_object(
        package.get("selection_scores"),
        "title_cover_package.selection_scores",
    )
    score_floors = {
        "familiarity": 8,
        "self_relevance": 8,
        "tension": 7,
        "curiosity": 7,
        "fidelity": 8,
        "help_clarity": 8,
        "non_exploitative_tension": 8,
        "permission_fit": 8,
        "share_impulse": 7,
    }
    total_score = 0
    for key, floor in score_floors.items():
        value = scores.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            fail(f"selection_scores.{key} must be numeric.")
        if not 0 <= value <= 10:
            fail(f"selection_scores.{key} must be between 0 and 10.")
        if value < floor:
            fail(
                f"selection_scores.{key} must be at least {floor}; "
                "rewrite the selected title."
            )
        total_score += value
    if total_score < 72:
        fail("The selected title must score at least 72/90.")
    for key in ("selection_reason", "title_cover_link"):
        require_text(package, key, "title_cover_package")
    markdown = (topic_dir / "article" / "final_article.md").read_text(encoding="utf-8")
    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", markdown)
    if not title_match or title_match.group(1).strip() != selected:
        fail("The Markdown H1 must match selected_title.")
    cover = require_object(package.get("cover_prompt"), "cover_prompt")
    for key in (
        "aspect_ratio",
        "cover_layout",
        "layout_ratio",
        "scene_position",
        "information_position",
        "style_profile",
        "palette_profile",
        "background_color",
        "background_material",
        "accent_color",
        "subject_profile",
        "female_character_design",
        "female_emotional_signal",
        "human_subject",
        "reader_mirror",
        "emotional_action",
        "cover_subject",
        "cover_conflict",
        "scene_layer",
        "information_question",
        "information_form",
        "information_layer",
        "shared_anchor",
        "transition_plan",
        "transition_color_plan",
        "transition_light_plan",
        "transition_perspective_plan",
        "headline_text",
        "safe_zone",
        "cover_text_strategy",
        "crop_survival_plan",
        "prompt",
    ):
        require_text(cover, key, "cover_prompt")
    if cover["aspect_ratio"] != "2.35:1":
        fail("cover_prompt.aspect_ratio must be 2.35:1.")
    if cover["cover_layout"] != "left_scene_right_info":
        fail("cover_prompt.cover_layout must be left_scene_right_info.")
    if cover["layout_ratio"] not in {"scene_45_info_55", "scene_50_info_50"}:
        fail("cover_prompt.layout_ratio must keep the scene and information near half.")
    if cover["scene_position"] != "left_half":
        fail("cover_prompt.scene_position must be left_half.")
    if cover["information_position"] != "right_half":
        fail("cover_prompt.information_position must be right_half.")
    if cover["style_profile"] != "scene_to_white_micro_3d":
        fail("cover_prompt.style_profile must be scene_to_white_micro_3d.")
    if cover["palette_profile"] != VISUAL_PALETTE_PROFILE:
        fail(
            "cover_prompt.palette_profile must be "
            f"{VISUAL_PALETTE_PROFILE}."
        )
    if VISUAL_BACKGROUND_HEX not in cover["background_color"].upper():
        fail(
            "cover_prompt.background_color must use the midlife background "
            f"{VISUAL_BACKGROUND_HEX}."
        )
    if VISUAL_BACKGROUND_HEX not in cover["prompt"].upper():
        fail(
            "cover_prompt.prompt must explicitly carry the midlife background "
            f"{VISUAL_BACKGROUND_HEX}."
        )
    if not re.search(r"#[0-9A-Fa-f]{6}\b", cover["accent_color"]):
        fail("cover_prompt.accent_color must include a six-digit HEX value.")
    cover_colors = require_list(
        cover.get("supporting_colors"),
        "cover_prompt.supporting_colors",
    )
    if not 3 <= len(cover_colors) <= 4 or any(
        not isinstance(value, str)
        or not re.search(r"#[0-9A-Fa-f]{6}\b", value)
        for value in cover_colors
    ):
        fail(
            "cover_prompt.supporting_colors must contain three or four HEX colors."
        )
    if cover["subject_profile"] != "attractive_intellectual_woman_28_35":
        fail(
            "cover_prompt.subject_profile must be "
            "attractive_intellectual_woman_28_35."
        )
    if cover["information_form"] not in {
        "causal_chain",
        "timeline",
        "before_after",
        "choice_path",
        "relationship_map",
    }:
        fail("cover_prompt.information_form is invalid.")
    if cover["headline_text"] != selected:
        fail("cover_prompt.headline_text must match selected_title.")
    if nonspace(cover["prompt"]) <= 700:
        fail("cover_prompt.prompt must exceed 700 non-whitespace characters.")
    digest_path = topic_dir / "article" / "final_article_digest.txt"
    if not digest_path.is_file():
        fail(f"Missing file: {digest_path}")
    digest_chars = nonspace(digest_path.read_text(encoding="utf-8"))
    if not 500 <= digest_chars <= 800:
        fail("final_article_digest.txt must contain 500-800 non-whitespace characters.")
    write_wechat_html(topic_dir, quiet=True)
    receipt = write_receipt(
        topic_dir,
        6,
        {
            "title_candidates": len(candidates),
            "selected_title": selected,
            "title_score": total_score,
            "digest_chars": digest_chars,
            "cover_prompt_version": COVER_PROMPT_VERSION,
        },
    )
    return {
        "title_candidates": len(candidates),
        "selected_title": selected,
        "title_score": total_score,
        "digest_chars": digest_chars,
        "cover_prompt_version": COVER_PROMPT_VERSION,
        "receipt": str(receipt),
    }


def probe_audio_duration(path: Path) -> float | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"Unreadable audio file: {path}")
    try:
        duration = float(result.stdout.strip())
    except ValueError:
        fail(f"Could not read audio duration: {path}")
    if duration <= 0:
        fail(f"Audio duration must be positive: {path}")
    return duration


def require_positive_number(value: Any, owner: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        fail(f"{owner} must be a positive number.")
    number = float(value)
    if number <= 0:
        fail(f"{owner} must be a positive number.")
    return number


def validate_stage7(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 6)
    prompts = load_jsonl(topic_dir / "assets" / "image_prompts.jsonl")
    segments = load_jsonl(topic_dir / "video" / "narration_segments.jsonl")
    images_dir = topic_dir / "video" / "images"
    if not images_dir.is_dir():
        fail("Stage 7 must create video/images/ for the user's numbered images.")
    if len(segments) != len(prompts):
        fail("Stage 7 needs exactly one narration segment per image prompt.")

    expected_ids = [
        require_text(item, "image_id", f"image_prompts[{index}]")
        for index, item in enumerate(prompts)
    ]
    audio_paths: dict[str, Path] = {}
    total_characters = 0
    for index, (prompt, segment) in enumerate(zip(prompts, segments), start=1):
        owner = f"narration_segments[{index - 1}]"
        expected_id = expected_ids[index - 1]
        if require_text(segment, "id", owner) != expected_id:
            fail(f"{owner}.id must be {expected_id}.")
        if segment.get("order") != index:
            fail(f"{owner}.order must be {index}.")
        if require_text(segment, "image_prompt_id", owner) != expected_id:
            fail(f"{owner}.image_prompt_id must be {expected_id}.")
        expected_title = require_text(
            prompt, "section_title", f"image_prompts[{index - 1}]"
        )
        if require_text(segment, "section_title", owner) != expected_title:
            fail(f"{owner}.section_title must match its image prompt.")
        for key in (
            "image_meaning",
            "visual_anchor",
            "narration_goal",
            "transition_in",
            "transition_out",
        ):
            require_text(segment, key, owner)
        narration = require_text(segment, "narration", owner)
        sentence_count = len(
            [
                part
                for part in re.split(r"[。！？!?…]+", narration)
                if nonspace(part)
            ]
        )
        if not 5 <= sentence_count <= 6:
            fail(f"{owner}.narration must contain five or six complete sentences.")
        characters = nonspace(narration)
        if not 90 <= characters <= 320:
            fail(
                f"{owner}.narration is implausibly short or long for five to six sentences."
            )
        total_characters += characters
        expected_audio = f"video/audio/{expected_id}.mp3"
        if require_text(segment, "audio_file", owner) != expected_audio:
            fail(f"{owner}.audio_file must be {expected_audio}.")
        audio_path = topic_dir / expected_audio
        if not audio_path.is_file() or audio_path.stat().st_size < 1024:
            fail(f"Missing or empty Edge TTS audio: {audio_path}")
        audio_paths[expected_id] = audio_path

    manifest = require_object(
        load_json(topic_dir / "video" / "audio_manifest.json"),
        "audio_manifest.json",
    )
    if require_text(manifest, "tts_engine", "audio_manifest") != "edge_tts":
        fail("audio_manifest.tts_engine must be edge_tts.")
    for key in ("voice", "rate", "volume", "pitch"):
        require_text(manifest, key, "audio_manifest")
    manifest_segments = require_list(
        manifest.get("segments"), "audio_manifest.segments"
    )
    if len(manifest_segments) != len(expected_ids):
        fail("audio_manifest must contain exactly one entry per image prompt.")

    actual_total = 0.0
    for index, (expected_id, value) in enumerate(
        zip(expected_ids, manifest_segments), start=1
    ):
        owner = f"audio_manifest.segments[{index - 1}]"
        item = require_object(value, owner)
        if require_text(item, "id", owner) != expected_id:
            fail(f"{owner}.id must be {expected_id}.")
        if require_text(item, "image_prompt_id", owner) != expected_id:
            fail(f"{owner}.image_prompt_id must be {expected_id}.")
        expected_audio = f"video/audio/{expected_id}.mp3"
        if require_text(item, "audio_file", owner) != expected_audio:
            fail(f"{owner}.audio_file must be {expected_audio}.")
        if require_text(item, "status", owner) != "success":
            fail(f"{owner}.status must be success.")
        declared_duration = require_positive_number(
            item.get("duration_seconds"), f"{owner}.duration_seconds"
        )
        measured_duration = probe_audio_duration(audio_paths[expected_id])
        if measured_duration is not None:
            if abs(declared_duration - measured_duration) > max(
                1.0, measured_duration * 0.03
            ):
                fail(f"{owner}.duration_seconds does not match the MP3.")
            actual_total += measured_duration
        else:
            actual_total += declared_duration

    declared_total = require_positive_number(
        manifest.get("total_duration_seconds"),
        "audio_manifest.total_duration_seconds",
    )
    if abs(declared_total - actual_total) > max(1.5, actual_total * 0.02):
        fail("audio_manifest.total_duration_seconds does not match its segments.")
    details = {
        "segments": len(segments),
        "characters": total_characters,
        "duration_seconds": round(actual_total, 2),
        "narration_version": NARRATION_VERSION,
        "images_directory": str(images_dir),
        "expected_image_ids": expected_ids,
    }
    receipt = write_receipt(topic_dir, 7, details)
    return {**details, "receipt": str(receipt)}


def resolve_topic_dir(value: str | None) -> Path:
    if not value:
        fail("--topic-dir is required for Stage 1-7.")
    return ensure_topic_dir(expand_user_path(value))


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a midlife-article stage.")
    parser.add_argument("--stage", type=int, choices=range(0, 8), required=True)
    parser.add_argument("--topic-dir")
    parser.add_argument("--scan-dir")
    args = parser.parse_args()

    if args.stage == 0:
        if not args.scan_dir:
            fail("--scan-dir is required for Stage 0.")
        result = validate_stage0(expand_user_path(args.scan_dir))
    else:
        topic_dir = resolve_topic_dir(args.topic_dir)
        validators = {
            1: validate_stage1,
            2: validate_stage2,
            3: validate_stage3,
            4: validate_stage4,
            5: validate_stage5,
            6: validate_stage6,
            7: validate_stage7,
        }
        result = validators[args.stage](topic_dir)
    print(
        json.dumps(
            {"stage": args.stage, "status": "passed", **result},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
