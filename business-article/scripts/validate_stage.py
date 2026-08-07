#!/usr/bin/env python3
"""Deterministic stage gates for the business-article workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from markdown_to_wechat_html import write_wechat_html
from path_utils import ensure_topic_dir, expand_user_path


CONTRACT_VERSION = 5
IMAGE_PROMPT_VERSION = 3
COVER_PROMPT_VERSION = 3
NARRATION_VERSION = 2
VISUAL_PALETTE_PROFILE = "capital_paper_business"
VISUAL_BACKGROUND_HEX = "#F2F1ED"
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


def visible_markdown_text(markdown: str) -> str:
    """Approximate reader-visible text without build and Markdown syntax."""
    text = re.sub(r"<!--[\s\S]*?-->", "", markdown)
    text = re.sub(r"(?m)^\s*\[\^[^\]\n]+\]:.*$", "", text)
    text = re.sub(r"\[\^[^\]\n]+\]", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s*(?:#{1,6}|>|[-+*]|\d+[.)])\s*", "", text)
    text = re.sub(r"(?m)^\s*[:|\-\s]+\s*$", "", text)
    text = re.sub(r"(?m)^\s*(?:```+|~~~+).*$", "", text)
    text = re.sub(r"[*_`~|]", "", text)
    return text


def visible_nonspace(markdown: str) -> int:
    return nonspace(visible_markdown_text(markdown))


def section_visible_lengths(markdown: str) -> list[tuple[str, int]]:
    matches = list(re.finditer(r"(?m)^##\s+(.+?)\s*$", markdown))
    result: list[tuple[str, int]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        result.append(
            (
                match.group(1).strip(),
                visible_nonspace(markdown[match.end() : end]),
            )
        )
    return result


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def stage1_payload(pack: dict[str, Any], blueprint: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "topic_id",
        "article_profile",
        "observation_cards",
        "numeric_claims",
        "business_fact_map",
        "fact_conflicts",
        "known_unknowns",
        "selected_source_files",
    )
    return {"blueprint": blueprint, **{key: pack.get(key) for key in keys}}


def stage2_payload(pack: dict[str, Any], mindmap: str) -> dict[str, Any]:
    return {
        "economic_engine": pack.get("economic_engine"),
        "causal_spine": pack.get("causal_spine"),
        "coordinates": pack.get("coordinates"),
        "spark": pack.get("spark"),
        "spark_rounds": pack.get("spark_rounds"),
        "mindmap": mindmap,
    }


def stage3_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "causal_audit": pack.get("causal_audit"),
        "economics_audit": pack.get("economics_audit"),
        "wisdom_candidates": pack.get("wisdom_candidates"),
        "spark_verdict": pack.get("spark_verdict"),
        "decision_design": pack.get("decision_design"),
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
            load_json(topic_dir / "research" / "business_blueprint.json"),
            "business_blueprint.json",
        )
        return canonical_hash(stage1_payload(pack, blueprint))
    if stage == 2:
        mindmap_path = topic_dir / "article" / "business_mindmap.md"
        if not mindmap_path.is_file():
            fail(f"Missing file: {mindmap_path}")
        return canonical_hash(stage2_payload(pack, mindmap_path.read_text(encoding="utf-8")))
    if stage == 3:
        return canonical_hash(stage3_payload(pack))
    if stage == 4:
        return canonical_hash(
            {
                "article": stage4_markdown_payload(
                    topic_dir / "article" / "final_article.md"
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
    if require_text(profile, "mode", "article_profile") != "business_investment":
        fail("article_profile.mode must be business_investment.")
    for key in ("core_audience", "source_anchor", "visual_mode"):
        require_text(profile, key, "article_profile")


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
            "familiar_subject",
            "trigger_signal",
            "central_business_question",
            "profit_question",
            "value_capture_conflict",
            "decision_payoff",
            "evidence_availability",
            "traffic_reason",
            "risk",
        ):
            require_text(candidate, key, f"candidates[{index}]")
        searches = require_list(
            candidate.get("reader_search_language"),
            f"candidates[{index}].reader_search_language",
        )
        if any(not isinstance(value, str) or not value.strip() for value in searches):
            fail(f"candidates[{index}].search_language contains an empty value.")
    return {"candidates": len(candidates), "path": str(path)}


def validate_stage1(topic_dir: Path) -> dict[str, Any]:
    blueprint = require_object(
        load_json(topic_dir / "research" / "business_blueprint.json"),
        "business_blueprint.json",
    )
    for key in (
        "topic_id",
        "trigger_event",
        "central_business_question",
        "core_reader",
        "reader_decision",
        "reader_help",
        "profit_question",
        "value_capture_conflict",
        "visual_world",
    ):
        require_text(blueprint, key, "business_blueprint")
    narrative_position = require_object(
        blueprint.get("narrative_position"),
        "business_blueprint.narrative_position",
    )
    for key in (
        "author_relation",
        "trigger_to_write",
        "known_basis",
        "inference_boundary",
        "judgment_at_stake",
    ):
        require_text(
            narrative_position,
            key,
            "business_blueprint.narrative_position",
        )
    narrative_materials = require_list(
        blueprint.get("narrative_materials"),
        "business_blueprint.narrative_materials",
        minimum=1,
    )
    material_evidence: list[tuple[str, list[str]]] = []
    allowed_material_kinds = {
        "event",
        "customer_action",
        "transaction",
        "revenue",
        "cost",
        "cash",
        "competition",
        "expectation",
        "counter_signal",
    }
    material_ids: set[str] = set()
    for index, value in enumerate(narrative_materials):
        owner = f"business_blueprint.narrative_materials[{index}]"
        material = require_object(value, owner)
        material_id = require_text(material, "id", owner)
        if material_id in material_ids:
            fail(f"Duplicate narrative material id: {material_id}")
        material_ids.add(material_id)
        if require_text(material, "kind", owner) not in allowed_material_kinds:
            fail(f"{owner}.kind is invalid.")
        for key in ("content", "narrative_role"):
            require_text(material, key, owner)
        evidence_values = require_list(
            material.get("evidence_ids"),
            f"{owner}.evidence_ids",
        )
        if any(
            not isinstance(item, str) or not item.strip()
            for item in evidence_values
        ):
            fail(f"{owner}.evidence_ids must contain non-empty strings.")
        material_evidence.append(
            (
                owner,
                [item.strip().upper() for item in evidence_values],
            )
        )
    require_list(
        blueprint.get("research_gaps"),
        "business_blueprint.research_gaps",
        allow_empty=True,
    )

    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"), "source_pack.json"
    )
    validate_profile(pack)
    if require_text(pack, "topic_id", "source_pack") != require_text(
        blueprint, "topic_id", "business_blueprint"
    ):
        fail("Blueprint and source_pack topic_id values do not match.")
    cards = require_list(
        pack.get("observation_cards"), "source_pack.observation_cards"
    )
    numeric_claims = require_list(
        pack.get("numeric_claims"), "source_pack.numeric_claims"
    )
    known_ids: set[str] = set()
    card_domains: dict[str, str] = {}
    for index, value in enumerate(cards):
        item = require_object(value, f"observation_cards[{index}]")
        item_id = require_text(item, "id", f"observation_cards[{index}]").upper()
        if not re.fullmatch(r"O\d{2}", item_id):
            fail(f"observation_cards[{index}].id must use O01-style numbering.")
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
        url = require_text(item, "source_url", f"observation_cards[{index}]")
        match = re.match(r"https?://([^/]+)", url)
        if not match:
            fail(f"observation_cards[{index}].source_url must be HTTP(S).")
        card_domains[item_id] = match.group(1).lower().removeprefix("www.")

    for index, value in enumerate(numeric_claims):
        owner = f"numeric_claims[{index}]"
        item = require_object(value, owner)
        item_id = require_text(item, "id", owner).upper()
        if not re.fullmatch(r"N\d{2}", item_id):
            fail(f"{owner}.id must use N01-style numbering.")
        if item_id in known_ids:
            fail(f"Duplicate evidence id: {item_id}")
        known_ids.add(item_id)
        for key in (
            "metric",
            "publish_text",
            "as_of_date",
            "unit",
            "scope",
            "denominator",
            "independence_note",
            "status",
            "calculation",
            "permitted_wording",
        ):
            require_text(item, key, owner)
        if item["status"] not in {"exact", "range", "attributed", "omit"}:
            fail(f"{owner}.status is invalid.")
        source_ids = [
            str(value).strip().upper()
            for value in require_list(item.get("source_ids"), f"{owner}.source_ids")
        ]
        if len(set(source_ids)) < 2:
            fail(f"{owner} must use at least two source ids.")
        unknown = set(source_ids) - set(card_domains)
        if unknown:
            fail(f"{owner} has unknown source ids: {sorted(unknown)}")
        independent_domains = {card_domains[source_id] for source_id in source_ids}
        if len(independent_domains) < 2:
            fail(f"{owner} must use at least two source domains.")
    for owner, source_ids in material_evidence:
        unknown = set(source_ids) - known_ids
        if unknown:
            fail(f"{owner} references unknown evidence ids: {sorted(unknown)}")
    for key in ("fact_conflicts", "known_unknowns", "selected_source_files"):
        require_list(pack.get(key), f"source_pack.{key}", allow_empty=True)

    fact_map = require_object(
        pack.get("business_fact_map"), "source_pack.business_fact_map"
    )
    required_fact_areas = (
        "customer_job",
        "payer_and_transaction",
        "revenue_evidence",
        "cost_and_capital_evidence",
        "competition_and_value_capture",
        "capital_expectation",
    )
    for area in required_fact_areas:
        item = require_object(fact_map.get(area), f"business_fact_map.{area}")
        known = require_text(item, "known", f"business_fact_map.{area}")
        area_evidence = [
            str(value).strip().upper()
            for value in require_list(
                item.get("evidence_ids"),
                f"business_fact_map.{area}.evidence_ids",
                allow_empty=True,
            )
        ]
        unknown = set(area_evidence) - known_ids
        if unknown:
            fail(
                f"business_fact_map.{area} has unknown evidence ids: "
                f"{sorted(unknown)}"
            )
        unknowns = require_list(
            item.get("unknowns"),
            f"business_fact_map.{area}.unknowns",
            allow_empty=True,
        )
        if known.lower() != "unknown" and not area_evidence:
            fail(
                f"business_fact_map.{area} needs evidence_ids or known=unknown."
            )
        if known.lower() == "unknown" and not unknowns:
            fail(
                f"business_fact_map.{area} marked unknown but has no explicit unknowns."
            )
    receipt = write_receipt(
        topic_dir,
        1,
        {
            "observation_cards": len(cards),
            "numeric_claims": len(numeric_claims),
            "business_fact_areas": len(required_fact_areas),
            "source_domains": len(set(card_domains.values())),
            "narrative_materials": len(narrative_materials),
        },
    )
    return {
        "observation_cards": len(cards),
        "numeric_claims": len(numeric_claims),
        "source_domains": len(set(card_domains.values())),
        "narrative_materials": len(narrative_materials),
        "receipt": str(receipt),
    }


def evidence_ids(pack: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for key in ("observation_cards", "numeric_claims"):
        for value in pack.get(key, []):
            if isinstance(value, dict) and value.get("id"):
                result.add(str(value["id"]).strip().upper())
    return result


def validate_stage2(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 1)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"), "source_pack.json"
    )
    validate_profile(pack)
    known = evidence_ids(pack)
    engine = require_object(
        pack.get("economic_engine"), "source_pack.economic_engine"
    )
    for key in (
        "technology_trigger",
        "scarcity_shift",
        "customer_value",
        "payer_logic",
        "revenue_equation",
        "revenue_quality",
        "cost_equation",
        "unit_economics",
        "capital_and_cash",
        "scale_behavior",
        "value_capture",
        "rent_distribution",
        "reinvestment_loop",
        "capital_expectation",
        "fatal_unknown",
    ):
        require_text(engine, key, "economic_engine")
    engine_evidence = {
        str(value).strip().upper()
        for value in require_list(
            engine.get("evidence_ids"), "economic_engine.evidence_ids"
        )
    }
    unknown_engine_evidence = engine_evidence - known
    if unknown_engine_evidence:
        fail(
            "economic_engine has unknown evidence ids: "
            f"{sorted(unknown_engine_evidence)}"
        )

    spine = require_list(pack.get("causal_spine"), "source_pack.causal_spine")
    if not 5 <= len(spine) <= 7:
        fail(f"causal_spine must contain 5-7 levels; found {len(spine)}.")
    causal_ids: list[str] = []
    valid_domains = {
        "customer",
        "product",
        "pricing",
        "revenue",
        "cost",
        "unit_economics",
        "cash_flow",
        "distribution",
        "supply",
        "competition",
        "industry_power",
        "regulation",
        "capital",
        "risk",
    }
    used_domains: list[str] = []
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
        domain = require_text(item, "domain", f"causal_spine[{index - 1}]").lower()
        if domain not in valid_domains:
            fail(f"causal_spine[{index - 1}].domain is invalid: {domain}")
        used_domains.append(domain)
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
            "next_question_or_stop",
        ):
            require_text(item, key, f"causal_spine[{index - 1}]")
        item_evidence = require_list(
            item.get("evidence_ids"),
            f"causal_spine[{index - 1}].evidence_ids",
        )
        unknown = {
            str(evidence).strip().upper() for evidence in item_evidence
        } - known
        if unknown:
            fail(f"causal_spine[{index - 1}] has unknown evidence: {sorted(unknown)}")
    if len(set(used_domains)) < 4:
        fail("causal_spine must cross at least four business domains.")
    if not set(used_domains) & {"pricing", "revenue"}:
        fail("causal_spine must reach pricing or revenue formation.")
    if not set(used_domains) & {"cost", "unit_economics", "cash_flow"}:
        fail("causal_spine must reach cost, unit economics or cash conversion.")
    if not set(used_domains[-3:]) & {
        "competition",
        "industry_power",
        "capital",
        "risk",
    }:
        fail(
            "The lower causal levels must reach industry power, competition, "
            "capital or risk."
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
    for key in ("question", "core_tension", "current_judgment", "strongest_counterpoint", "reader_relation"):
        require_text(spark, key, "spark")
    if set(str(value).upper() for value in require_list(spark.get("causal_basis_ids"), "spark.causal_basis_ids")) - set(causal_ids):
        fail("spark.causal_basis_ids contains an unknown causal level.")
    if set(str(value).upper() for value in require_list(spark.get("coordinate_ids"), "spark.coordinate_ids")) - coordinate_ids:
        fail("spark.coordinate_ids contains an unknown coordinate.")

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

    mindmap_path = topic_dir / "article" / "business_mindmap.md"
    if not mindmap_path.is_file() or nonspace(mindmap_path.read_text(encoding="utf-8")) < 1200:
        fail("business_mindmap.md is missing or too thin.")
    receipt = write_receipt(
        topic_dir,
        2,
        {
            "causal_levels": len(spine),
            "business_domains": len(set(used_domains)),
            "economic_engine": True,
            "spark_rounds": len(rounds),
            "spark_id": "S01",
        },
    )
    return {"causal_levels": len(spine), "spark_rounds": len(rounds), "receipt": str(receipt)}


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
        ):
            require_text(item, key, f"causal_audit[{index - 1}]")
        if require_text(item, "decision", f"causal_audit[{index - 1}]") != "valid":
            fail(f"causal_audit[{index - 1}] requires a return to Stage 2.")

    economics = require_object(
        pack.get("economics_audit"), "source_pack.economics_audit"
    )
    for key in (
        "customer_value_test",
        "revenue_identity_test",
        "revenue_quality_test",
        "profit_bridge_test",
        "cash_conversion_test",
        "unit_economics_test",
        "scale_test",
        "value_capture_test",
        "return_on_capital_test",
        "expectation_gap_test",
        "fatal_assumption",
    ):
        require_text(economics, key, "economics_audit")
    if require_text(economics, "decision", "economics_audit") != "valid":
        fail("economics_audit requires a return to Stage 2.")

    wisdom = require_list(pack.get("wisdom_candidates"), "source_pack.wisdom_candidates")
    used_wisdom = 0
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
        if item["use_decision"] == "use":
            used_wisdom += 1
            raw_path = topic_dir / item["raw_page_source"]
            if not raw_path.is_file():
                fail(f"Used wisdom source is missing: {raw_path}")
    if used_wisdom < 1:
        fail("Stage 3 must select at least one genuinely useful wisdom source.")

    verdict = require_object(pack.get("spark_verdict"), "source_pack.spark_verdict")
    for key in (
        "spark_id",
        "decision",
        "final_question",
        "final_judgment",
        "publish_thesis",
        "strongest_counterargument",
        "response",
        "boundary",
        "reader_change",
    ):
        require_text(verdict, key, "spark_verdict")
    if verdict["spark_id"].upper() != "S01" or verdict["decision"] not in {"validated", "reframed"}:
        fail("spark_verdict must validate or reframe S01.")

    decision = require_object(
        pack.get("decision_design"), "source_pack.decision_design"
    )
    for key in (
        "decision_scene",
        "core_principle",
        "delay_vs_destroy",
        "stop_condition",
        "boundary",
    ):
        require_text(decision, key, "decision_design")
    for key in (
        "key_variables",
        "leading_signals",
        "confirming_signals",
        "disconfirming_signals",
        "scenarios",
    ):
        values = require_list(decision.get(key), f"decision_design.{key}")
        if any(not isinstance(value, str) or not value.strip() for value in values):
            fail(f"decision_design.{key} contains an empty value.")
    if len(decision["scenarios"]) < 2:
        fail("decision_design.scenarios must contain at least two paths.")
    receipt = write_receipt(
        topic_dir,
        3,
        {
            "causal_audits": len(audits),
            "economics_audit": True,
            "used_wisdom": used_wisdom,
            "key_variables": len(decision["key_variables"]),
            "spark_id": "S01",
        },
    )
    return {"causal_audits": len(audits), "used_wisdom": used_wisdom, "receipt": str(receipt)}


def markdown_sections(markdown: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"(?m)^##\s+(.+?)\s*$", markdown)]


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
    visible_chars = visible_nonspace(markdown)
    if visible_chars < 3600:
        fail(
            "final_article.md needs at least 3600 reader-visible characters; "
            f"found {visible_chars}."
        )
    sections = markdown_sections(markdown)
    if not 5 <= len(sections) <= 7:
        fail(f"final_article.md needs 5-7 major sections; found {len(sections)}.")
    if re.search(r"(?m)^\s*\|.+\|\s*$", markdown):
        fail("final_article.md must not use Markdown tables.")
    section_lengths = section_visible_lengths(markdown)
    too_thin = [(title, length) for title, length in section_lengths if length < 350]
    if too_thin:
        fail(f"Major sections are too thin: {too_thin}")
    lengths = [length for _, length in section_lengths]
    if max(lengths) / min(lengths) > 2.2:
        fail(f"Major-section information is too uneven: {section_lengths}")
    numeric_claims = require_list(
        pack.get("numeric_claims"), "source_pack.numeric_claims"
    )
    numeric_map = {
        require_text(item, "id", f"numeric_claims[{index}]").upper(): item
        for index, item in enumerate(numeric_claims)
        if isinstance(item, dict)
    }
    data_markers = re.findall(
        r"<!--\s*DATA:([Nn]\d{2}(?:\s*,\s*[Nn]\d{2})*)\s*-->",
        markdown,
    )
    tagged_ids = {
        value.strip().upper()
        for marker in data_markers
        for value in marker.split(",")
    }
    unknown_data_ids = tagged_ids - set(numeric_map)
    if unknown_data_ids:
        fail(f"DATA markers reference unknown numeric claims: {sorted(unknown_data_ids)}")
    for claim_id, claim in numeric_map.items():
        publish_text = require_text(claim, "publish_text", f"numeric_claims.{claim_id}")
        status = require_text(claim, "status", f"numeric_claims.{claim_id}")
        if status == "omit" and publish_text in markdown:
            fail(f"{claim_id} has status=omit but its publish_text appears in the article.")
        if publish_text in markdown and claim_id not in tagged_ids:
            fail(f"{claim_id}.publish_text appears without a matching DATA marker.")
    for match in re.finditer(
        r"<!--\s*DATA:([Nn]\d{2}(?:\s*,\s*[Nn]\d{2})*)\s*-->",
        markdown,
    ):
        ids = [value.strip().upper() for value in match.group(1).split(",")]
        following = markdown[match.end() : match.end() + 1200]
        if not all(numeric_map[value]["publish_text"] in following for value in ids):
            fail("Each DATA marker must sit before a block containing its publish_text.")
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
    html_path = write_wechat_html(topic_dir, quiet=True)
    html = html_path.read_text(encoding="utf-8")
    if re.search(r"(?:DATA:|USER:|DESCENT:|SPARK:|REBOUND|IMAGE:)", html):
        fail("final_article_copy.html leaks construction markers.")
    if (
        'font-size: 15px' not in html
        or 'data-wa-theme="business-investment"' not in html
    ):
        fail("final_article_copy.html is not using the business 15px theme.")
    receipt = write_receipt(
        topic_dir,
        4,
        {
            "sections": len(sections),
            "visible_chars": visible_chars,
            "section_visible_chars": dict(section_lengths),
        },
    )
    return {
        "sections": len(sections),
        "visible_chars": visible_chars,
        "section_visible_chars": dict(section_lengths),
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
    markers = re.findall(r"<!--\s*IMAGE:(section_\d+)\s*-->", markdown)
    expected_ids = [f"section_{index:02d}" for index in range(1, len(sections) + 1)]
    if markers != expected_ids:
        fail(f"Image markers must appear once in section order: {expected_ids}.")
    prompts = load_jsonl(topic_dir / "assets" / "image_prompts.jsonl")
    if len(prompts) != len(sections):
        fail("image_prompts.jsonl must contain exactly one row per section.")
    roles: list[str] = []
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
        if role not in {"business_scene", "value_flow", "decision_signal"}:
            fail(
                f"{owner}.visual_role must be business_scene, "
                "value_flow or decision_signal."
            )
        roles.append(role)
        if require_text(item, "aspect_ratio", owner) != "3:4":
            fail(f"{owner}.aspect_ratio must be 3:4.")
        if require_text(item, "style_profile", owner) != "white_material_micro_3d":
            fail(f"{owner}.style_profile must be white_material_micro_3d.")
        for key in (
            "layout_ratio",
            "scene_position",
            "information_position",
            "palette_profile",
            "background_color",
            "background_material",
            "scene_layer",
            "information_question",
            "information_layer",
            "shared_anchor",
            "transition_plan",
            "transition_color_plan",
            "transition_light_plan",
            "transition_perspective_plan",
        ):
            require_text(item, key, owner)
        if item["layout_ratio"] not in {
            "scene_30_info_70",
            "scene_33_info_67",
            "scene_35_info_65",
        }:
            fail(f"{owner}.layout_ratio must keep scene near 1/3 and information near 2/3.")
        if item["scene_position"] != "top_third":
            fail(f"{owner}.scene_position must be top_third.")
        if item["information_position"] != "lower_two_thirds":
            fail(f"{owner}.information_position must be lower_two_thirds.")
        if item["palette_profile"] != VISUAL_PALETTE_PROFILE:
            fail(f"{owner}.palette_profile must be {VISUAL_PALETTE_PROFILE}.")
        if VISUAL_BACKGROUND_HEX not in item["background_color"].upper():
            fail(
                f"{owner}.background_color must use the business background "
                f"{VISUAL_BACKGROUND_HEX}."
            )
        if VISUAL_BACKGROUND_HEX not in item["prompt"].upper():
            fail(
                f"{owner}.prompt must explicitly carry the business background "
                f"{VISUAL_BACKGROUND_HEX}."
            )
        accent = require_text(item, "accent_color", owner)
        if not re.search(r"#[0-9A-Fa-f]{6}\b", accent):
            fail(f"{owner}.accent_color must include a six-digit HEX value.")
        supporting = require_list(item.get("supporting_colors"), f"{owner}.supporting_colors")
        if not 3 <= len(supporting) <= 4 or any(
            not isinstance(value, str)
            or not re.search(r"#[0-9A-Fa-f]{6}\b", value)
            for value in supporting
        ):
            fail(f"{owner}.supporting_colors must contain three or four HEX colors.")
        visual_elements = require_list(
            item.get("visual_elements"),
            f"{owner}.visual_elements",
        )
        if not 7 <= len(visual_elements) <= 11 or any(
            not isinstance(value, str) or not value.strip()
            for value in visual_elements
        ):
            fail(f"{owner}.visual_elements must contain seven to eleven items.")
        chinese_labels = require_list(
            item.get("chinese_labels"),
            f"{owner}.chinese_labels",
        )
        if not 2 <= len(chinese_labels) <= 5 or any(
            not isinstance(value, str) or not value.strip()
            for value in chinese_labels
        ):
            fail(f"{owner}.chinese_labels must contain two to five labels.")
        for key in (
            "article_context",
            "visual_thesis",
            "composition",
            "subjects",
            "ratio_composition_plan",
            "detail_density_plan",
            "camera_plan",
            "material_detail_plan",
            "lighting_plan",
            "surface_detail_plan",
            "color_plan",
            "negative_constraints",
            "prompt",
        ):
            require_text(item, key, owner)
        if nonspace(item["prompt"]) <= 700:
            fail(f"{owner}.prompt must exceed 700 non-whitespace characters.")
    role_counts = {role: roles.count(role) for role in set(roles)}
    if len(role_counts) < 2:
        fail("Body illustrations must use at least two visual roles.")
    if max(role_counts.values()) > (len(roles) + 1) // 2:
        fail("No visual role may dominate more than half of the body illustrations.")
    write_wechat_html(topic_dir, quiet=True)
    receipt = write_receipt(
        topic_dir,
        5,
        {
            "images": len(prompts),
            "visual_roles": role_counts,
            "image_prompt_version": IMAGE_PROMPT_VERSION,
        },
    )
    return {
        "images": len(prompts),
        "visual_roles": role_counts,
        "image_prompt_version": IMAGE_PROMPT_VERSION,
        "receipt": str(receipt),
    }


def validate_stage6(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 5)
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
        titles.append(require_text(item, "title", f"title_candidates[{index}]"))
        for key in ("reader_hook", "psychology", "promise", "risk"):
            require_text(item, key, f"title_candidates[{index}]")
    selected = require_text(package, "selected_title", "title_cover_package")
    if selected not in titles:
        fail("selected_title must be one of title_candidates.")
    for key in ("selection_reason", "title_cover_link"):
        require_text(package, key, "title_cover_package")
    markdown = (topic_dir / "article" / "final_article.md").read_text(encoding="utf-8")
    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", markdown)
    if not title_match or title_match.group(1).strip() != selected:
        fail("The Markdown H1 must match selected_title.")
    cover = require_object(package.get("cover_prompt"), "cover_prompt")
    for key in (
        "aspect_ratio",
        "style_profile",
        "cover_layout",
        "layout_ratio",
        "scene_position",
        "information_position",
        "palette_profile",
        "background_color",
        "background_material",
        "cover_subject",
        "cover_conflict",
        "cover_action",
        "cover_visible_stakes",
        "scene_layer",
        "information_question",
        "information_form",
        "information_layer",
        "shared_anchor",
        "transition_plan",
        "transition_color_plan",
        "transition_light_plan",
        "transition_perspective_plan",
        "one_second_read",
        "thumbnail_test",
        "headline_text",
        "safe_zone",
        "accent_color",
        "ratio_composition_plan",
        "composition_plan",
        "detail_density_plan",
        "camera_plan",
        "material_detail_plan",
        "lighting_plan",
        "surface_detail_plan",
        "visual_hierarchy",
        "color_plan",
        "cover_text_strategy",
        "center_safe_zone_plan",
        "crop_survival_plan",
        "prompt",
    ):
        require_text(cover, key, "cover_prompt")
    if cover["aspect_ratio"] != "2.35:1":
        fail("cover_prompt.aspect_ratio must be 2.35:1.")
    if cover["style_profile"] != "white_material_micro_3d":
        fail("cover_prompt.style_profile must be white_material_micro_3d.")
    if cover["palette_profile"] != VISUAL_PALETTE_PROFILE:
        fail(
            "cover_prompt.palette_profile must be "
            f"{VISUAL_PALETTE_PROFILE}."
        )
    if VISUAL_BACKGROUND_HEX not in cover["background_color"].upper():
        fail(
            "cover_prompt.background_color must use the business background "
            f"{VISUAL_BACKGROUND_HEX}."
        )
    if VISUAL_BACKGROUND_HEX not in cover["prompt"].upper():
        fail(
            "cover_prompt.prompt must explicitly carry the business background "
            f"{VISUAL_BACKGROUND_HEX}."
        )
    if cover["cover_layout"] != "left_scene_right_info":
        fail("cover_prompt.cover_layout must be left_scene_right_info.")
    if cover["layout_ratio"] not in {"scene_45_info_55", "scene_50_info_50"}:
        fail("cover_prompt.layout_ratio must keep the scene and information near half.")
    if cover["scene_position"] != "left_half":
        fail("cover_prompt.scene_position must be left_half.")
    if cover["information_position"] != "right_half":
        fail("cover_prompt.information_position must be right_half.")
    if cover["information_form"] not in {
        "value_flow",
        "cost_structure",
        "competition_map",
        "decision_signal",
        "before_after",
    }:
        fail("cover_prompt.information_form is invalid.")
    if cover["headline_text"] != selected:
        fail("cover_prompt.headline_text must match selected_title.")
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
        fail("cover_prompt.supporting_colors must contain three or four HEX colors.")
    cover_elements = require_list(
        cover.get("visual_elements"),
        "cover_prompt.visual_elements",
    )
    if not 7 <= len(cover_elements) <= 11 or any(
        not isinstance(value, str) or not value.strip()
        for value in cover_elements
    ):
        fail("cover_prompt.visual_elements must contain seven to eleven items.")
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
            "digest_chars": digest_chars,
            "cover_prompt_version": COVER_PROMPT_VERSION,
        },
    )
    return {
        "title_candidates": len(candidates),
        "selected_title": selected,
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
    parser = argparse.ArgumentParser(description="Validate a business-article stage.")
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
