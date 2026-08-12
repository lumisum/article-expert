#!/usr/bin/env python3
"""Deterministic stage gates for the tech-article workflow."""

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
from urllib.parse import urlparse

from markdown_to_wechat_html import write_wechat_html
from path_utils import (
    ensure_topic_dir,
    expand_user_path,
    reject_literal_tilde,
    wechat_workspace_root,
)


CONTRACT_VERSION = 2
IMAGE_PROMPT_VERSION = 4
COVER_PROMPT_VERSION = 4
NARRATION_VERSION = 5
VISUAL_PALETTE_PROFILE = "cool_porcelain_tech"
VISUAL_BACKGROUND_HEX = "#EEF3F6"
ARTICLE_MODES = {"technical_explainer", "hands_on_playbook"}
SOURCE_TYPES = {
    "official_docs",
    "source_code",
    "spec",
    "paper",
    "release_notes",
    "issue",
}
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


def require_list(
    value: Any,
    owner: str,
    *,
    allow_empty: bool = False,
    minimum: int | None = None,
) -> list[Any]:
    if not isinstance(value, list):
        fail(f"{owner} must be a list.")
    if not allow_empty and not value:
        fail(f"{owner} must not be empty.")
    if minimum is not None and len(value) < minimum:
        fail(f"{owner} must contain at least {minimum} items.")
    return value


def require_text(obj: dict[str, Any], key: str, owner: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"{owner}.{key} must be a non-empty string.")
    return value.strip()


def require_text_list(
    obj: dict[str, Any],
    key: str,
    owner: str,
    *,
    allow_empty: bool = False,
    minimum: int | None = None,
) -> list[str]:
    values = require_list(
        obj.get(key),
        f"{owner}.{key}",
        allow_empty=allow_empty,
        minimum=minimum,
    )
    if any(not isinstance(value, str) or not value.strip() for value in values):
        fail(f"{owner}.{key} must contain only non-empty strings.")
    return [value.strip() for value in values]


def nonspace(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else ""


def selected_payload(pack: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: pack.get(key) for key in keys}


def article_layout_payload(path: Path) -> dict[str, Any]:
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


def article_without_title_hash(path: Path) -> str:
    if not path.is_file():
        return ""
    markdown = path.read_text(encoding="utf-8")
    markdown = re.sub(r"(?m)^#\s+.+$", "# [TITLE]", markdown, count=1)
    return hashlib.sha256(markdown.encode("utf-8")).hexdigest()


def stage_signature(topic_dir: Path, stage: int) -> str:
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"),
        "source_pack.json",
    )
    if stage == 1:
        blueprint = load_json(topic_dir / "research" / "tech_blueprint.json")
        selected_files = pack.get("selected_source_files")
        source_hashes = {}
        if isinstance(selected_files, list):
            source_hashes = {
                str(relative): file_hash(topic_dir / str(relative))
                for relative in selected_files
            }
        return canonical_hash(
            {
                "blueprint": blueprint,
                "source_files": source_hashes,
                **selected_payload(
                    pack,
                    (
                        "topic_id",
                        "article_profile",
                        "primary_sources",
                        "technical_claims",
                        "numeric_claims",
                        "author_experience",
                        "fact_conflicts",
                        "known_unknowns",
                        "selected_source_files",
                    ),
                ),
            }
        )
    if stage == 2:
        return canonical_hash(
            {
                "upstream_stage1": stage_signature(topic_dir, 1),
                **selected_payload(
                    pack,
                    (
                        "mechanism_chain",
                        "implementation_path",
                        "comparison_frame",
                        "spark",
                        "spark_rounds",
                        "article_route",
                    ),
                ),
                "mindmap": file_hash(topic_dir / "article" / "technical_mindmap.md"),
            }
        )
    if stage == 3:
        return canonical_hash(
            {
                "upstream_stage2": stage_signature(topic_dir, 2),
                **selected_payload(
                    pack,
                    (
                        "mechanism_audit",
                        "reproduction_audit",
                        "spark_verdict",
                        "reader_playbook",
                        "article_boundaries",
                    ),
                ),
            }
        )
    if stage == 4:
        return canonical_hash(
            {
                "upstream_stage3": stage_signature(topic_dir, 3),
                "markdown": file_hash(topic_dir / "article" / "final_article.md"),
                "html": file_hash(topic_dir / "article" / "final_article_copy.html"),
            }
        )
    if stage == 5:
        return canonical_hash(
            {
                "image_prompt_version": IMAGE_PROMPT_VERSION,
                "upstream_stage3": stage_signature(topic_dir, 3),
                # S6 may replace only the H1 title. Body edits still invalidate
                # the prompts even when section names remain unchanged.
                "article_without_title": article_without_title_hash(
                    topic_dir / "article" / "final_article.md"
                ),
                "layout": article_layout_payload(
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
                "upstream_stage3": stage_signature(topic_dir, 3),
                "markdown": file_hash(topic_dir / "article" / "final_article.md"),
                "html": file_hash(topic_dir / "article" / "final_article_copy.html"),
                "prompts": file_hash(
                    topic_dir / "assets" / "image_prompts.jsonl"
                ),
                "package": file_hash(
                    topic_dir / "assets" / "title_cover_package.json"
                ),
                "video_covers": file_hash(
                    topic_dir / "assets" / "video_cover_prompts.jsonl"
                ),
                "digest": file_hash(
                    topic_dir / "article" / "final_article_digest.txt"
                ),
            }
        )
    prompts = load_jsonl(topic_dir / "assets" / "image_prompts.jsonl")
    audio_hashes = {
        require_text(item, "id", "image_prompt"):
        file_hash(
            topic_dir
            / "video"
            / "audio"
            / f"{require_text(item, 'id', 'image_prompt')}.mp3"
        )
        for item in prompts
    }
    return canonical_hash(
        {
            "narration_version": NARRATION_VERSION,
            "upstream_stage6": stage_signature(topic_dir, 6),
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


def write_receipt(topic_dir: Path, stage: int, details: dict[str, Any]) -> Path:
    path = topic_dir / RECEIPTS[stage]
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "stage": stage,
        "contract_version": CONTRACT_VERSION,
        "status": "passed",
        "signature": stage_signature(topic_dir, stage),
        "validated_at": datetime.now(timezone.utc).isoformat(),
        **details,
    }
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def require_receipt(topic_dir: Path, stage: int) -> None:
    path = topic_dir / RECEIPTS[stage]
    data = require_object(load_json(path), str(path))
    if (
        data.get("stage") != stage
        or data.get("contract_version") != CONTRACT_VERSION
        or data.get("status") != "passed"
    ):
        fail(f"{path} is not a current passed receipt.")
    if data.get("signature") != stage_signature(topic_dir, stage):
        fail(f"{path} is stale. Re-run Stage {stage}.")


def validate_mode(value: str, owner: str) -> str:
    if value not in ARTICLE_MODES:
        fail(f"{owner} must be one of: {', '.join(sorted(ARTICLE_MODES))}.")
    return value


def validate_stage0(scan_dir: Path) -> dict[str, Any]:
    scan_dir = scan_dir.resolve()
    reject_literal_tilde(scan_dir)
    expected_root = (wechat_workspace_root() / "tech_scans").resolve()
    try:
        relative = scan_dir.relative_to(expected_root)
    except ValueError:
        fail(f"Stage 0 scan directory must live under {expected_root}.")
    if len(relative.parts) != 1:
        fail("Stage 0 scan directory must identify exactly one scan.")

    path = scan_dir / "research" / "topic_candidates.json"
    data = require_object(load_json(path), "topic_candidates.json")
    require_text(data, "scan_id", "topic_candidates")
    candidates = require_list(
        data.get("candidates"),
        "topic_candidates.candidates",
    )
    if len(candidates) != 3:
        fail("Stage 0 must produce exactly three candidates.")
    ids: set[str] = set()
    for index, value in enumerate(candidates):
        owner = f"candidates[{index}]"
        item = require_object(value, owner)
        candidate_id = require_text(item, "id", owner)
        if candidate_id in ids:
            fail(f"Duplicate candidate id: {candidate_id}")
        ids.add(candidate_id)
        validate_mode(require_text(item, "article_mode", owner), f"{owner}.article_mode")
        for key in (
            "familiar_subject",
            "reader_problem",
            "practical_payoff",
            "technical_depth",
            "reproducible_result",
            "primary_source_plan",
            "traffic_reason",
            "risk",
        ):
            require_text(item, key, owner)
        require_text_list(item, "reader_search_language", owner)
    return {"candidates": 3, "path": str(path)}


def validate_stage1(topic_dir: Path) -> dict[str, Any]:
    blueprint = require_object(
        load_json(topic_dir / "research" / "tech_blueprint.json"),
        "tech_blueprint.json",
    )
    for key in (
        "topic_id",
        "technical_subject",
        "core_reader",
        "reader_job",
        "starting_state",
        "promised_outcome",
        "environment_scope",
        "success_observation",
        "visual_world",
    ):
        require_text(blueprint, key, "tech_blueprint")
    blueprint_mode = validate_mode(
        require_text(blueprint, "article_mode", "tech_blueprint"),
        "tech_blueprint.article_mode",
    )
    require_text_list(blueprint, "reader_help", "tech_blueprint", minimum=2)
    narrative_position = require_object(
        blueprint.get("narrative_position"),
        "tech_blueprint.narrative_position",
    )
    for key in (
        "author_relation",
        "trigger_to_write",
        "verified_knowledge",
        "inference_boundary",
        "judgment_at_stake",
    ):
        require_text(narrative_position, key, "tech_blueprint.narrative_position")
    narrative_materials = require_list(
        blueprint.get("narrative_materials"),
        "tech_blueprint.narrative_materials",
        minimum=1,
    )
    material_evidence: list[tuple[str, list[str]]] = []
    allowed_material_kinds = {
        "goal",
        "operation",
        "observation",
        "failure",
        "diagnosis",
        "repair",
        "result",
        "boundary",
    }
    material_ids: set[str] = set()
    for index, value in enumerate(narrative_materials):
        owner = f"tech_blueprint.narrative_materials[{index}]"
        material = require_object(value, owner)
        material_id = require_text(material, "id", owner)
        if material_id in material_ids:
            fail(f"Duplicate narrative material id: {material_id}")
        material_ids.add(material_id)
        if require_text(material, "kind", owner) not in allowed_material_kinds:
            fail(f"{owner}.kind is invalid.")
        for key in ("content", "narrative_role"):
            require_text(material, key, owner)
        material_evidence.append(
            (
                owner,
                require_text_list(
                    material,
                    "evidence_ids",
                    owner,
                ),
            )
        )
    require_text_list(
        blueprint,
        "research_gaps",
        "tech_blueprint",
        allow_empty=True,
    )

    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"),
        "source_pack.json",
    )
    if require_text(pack, "topic_id", "source_pack") != require_text(
        blueprint, "topic_id", "tech_blueprint"
    ):
        fail("source_pack.topic_id must match tech_blueprint.topic_id.")
    profile = require_object(pack.get("article_profile"), "article_profile")
    mode = validate_mode(
        require_text(profile, "mode", "article_profile"),
        "article_profile.mode",
    )
    if mode != blueprint_mode:
        fail("article mode must match between blueprint and source pack.")
    for key in ("core_audience", "source_anchor", "visual_mode"):
        require_text(profile, key, "article_profile")

    sources = require_list(
        pack.get("primary_sources"),
        "source_pack.primary_sources",
        minimum=3,
    )
    source_ids: set[str] = set()
    domains: set[str] = set()
    original_count = 0
    for index, value in enumerate(sources):
        owner = f"primary_sources[{index}]"
        source = require_object(value, owner)
        source_id = require_text(source, "id", owner)
        if source_id in source_ids:
            fail(f"Duplicate source id: {source_id}")
        source_ids.add(source_id)
        source_type = require_text(source, "source_type", owner)
        if source_type not in SOURCE_TYPES:
            fail(f"{owner}.source_type is not an accepted primary source type.")
        original_count += 1
        for key in (
            "title",
            "url",
            "snapshot_file",
            "claim",
            "version_or_date",
            "boundary",
        ):
            require_text(source, key, owner)
        parsed = urlparse(source["url"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            fail(f"{owner}.url must be an HTTP(S) URL.")
        domains.add(parsed.netloc.lower())
        snapshot = topic_dir / source["snapshot_file"]
        if not snapshot.is_file():
            fail(f"Missing source snapshot: {snapshot}")
        try:
            snapshot.resolve().relative_to(
                (topic_dir / "research" / "raw_pages").resolve()
            )
        except ValueError:
            fail(f"{owner}.snapshot_file must live under research/raw_pages/.")
    if original_count < 3 or len(domains) < 2:
        fail("Stage 1 needs at least three primary sources across two domains.")
    for owner, evidence_ids in material_evidence:
        unknown = set(evidence_ids) - source_ids
        if unknown:
            fail(f"{owner} references unknown evidence ids: {sorted(unknown)}")

    claims = require_list(
        pack.get("technical_claims"),
        "source_pack.technical_claims",
        minimum=3,
    )
    claim_ids: set[str] = set()
    for index, value in enumerate(claims):
        owner = f"technical_claims[{index}]"
        claim = require_object(value, owner)
        claim_id = require_text(claim, "id", owner)
        if claim_id in claim_ids:
            fail(f"Duplicate technical claim id: {claim_id}")
        claim_ids.add(claim_id)
        for key in ("claim", "environment", "confidence"):
            require_text(claim, key, owner)
        evidence_ids = require_text_list(claim, "evidence_ids", owner)
        unknown = set(evidence_ids) - source_ids
        if unknown:
            fail(f"{owner} references unknown evidence ids: {sorted(unknown)}")

    require_list(
        pack.get("author_experience"),
        "source_pack.author_experience",
        allow_empty=True,
    )
    require_list(
        pack.get("fact_conflicts"),
        "source_pack.fact_conflicts",
        allow_empty=True,
    )
    require_list(
        pack.get("known_unknowns"),
        "source_pack.known_unknowns",
        allow_empty=True,
    )
    selected = require_text_list(
        pack,
        "selected_source_files",
        "source_pack",
        minimum=3,
    )
    if set(selected) - {source["snapshot_file"] for source in sources}:
        fail("selected_source_files must refer to declared primary source snapshots.")
    selected_bytes = sum((topic_dir / relative).stat().st_size for relative in selected)
    if selected_bytes < 20 * 1024:
        fail("Selected raw page snapshots must contain at least 20KB in total.")

    numeric_claims = require_list(
        pack.get("numeric_claims"),
        "source_pack.numeric_claims",
        allow_empty=True,
    )
    numeric_ids: set[str] = set()
    for index, value in enumerate(numeric_claims):
        owner = f"numeric_claims[{index}]"
        claim = require_object(value, owner)
        claim_id = require_text(claim, "id", owner)
        if claim_id in numeric_ids:
            fail(f"Duplicate numeric claim id: {claim_id}")
        numeric_ids.add(claim_id)
        for key in ("publish_text", "metric_context", "status"):
            require_text(claim, key, owner)
        if claim["status"] not in {"exact", "attributed", "omit"}:
            fail(f"{owner}.status must be exact, attributed, or omit.")
        evidence_ids = require_text_list(claim, "evidence_ids", owner)
        if set(evidence_ids) - source_ids:
            fail(f"{owner} references unknown evidence ids.")
        if claim["status"] == "exact" and len(set(evidence_ids)) < 2:
            fail(f"{owner} exact numeric claim needs two independent sources.")
    return {
        "mode": mode,
        "sources": len(sources),
        "claims": len(claims),
        "numeric_claims": len(numeric_claims),
        "domains": len(domains),
        "selected_bytes": selected_bytes,
        "narrative_materials": len(narrative_materials),
    }


def validate_stage2(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 1)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"),
        "source_pack.json",
    )
    source_ids = {
        require_text(require_object(value, "primary_source"), "id", "primary_source")
        for value in require_list(pack.get("primary_sources"), "primary_sources")
    }

    chain = require_list(
        pack.get("mechanism_chain"),
        "source_pack.mechanism_chain",
        minimum=5,
    )
    if len(chain) > 7:
        fail("mechanism_chain must stay between five and seven levels.")
    levels: list[int] = []
    for index, value in enumerate(chain):
        owner = f"mechanism_chain[{index}]"
        item = require_object(value, owner)
        level = item.get("level")
        if not isinstance(level, int):
            fail(f"{owner}.level must be an integer.")
        levels.append(level)
        for key in (
            "reader_question",
            "mechanism",
            "input_state_output",
            "boundary",
            "next_question",
        ):
            require_text(item, key, owner)
        evidence_ids = require_text_list(item, "evidence_ids", owner)
        if set(evidence_ids) - source_ids:
            fail(f"{owner} references unknown evidence ids.")
    if levels != list(range(1, len(chain) + 1)):
        fail("mechanism_chain.level must increase continuously from 1.")

    path = require_list(
        pack.get("implementation_path"),
        "source_pack.implementation_path",
        minimum=1,
    )
    mode = require_text(
        require_object(pack.get("article_profile"), "article_profile"),
        "mode",
        "article_profile",
    )
    if mode == "hands_on_playbook" and len(path) < 3:
        fail("hands_on_playbook needs at least three implementation steps.")
    for index, value in enumerate(path):
        owner = f"implementation_path[{index}]"
        item = require_object(value, owner)
        for key in (
            "id",
            "goal",
            "action",
            "expected_observation",
            "failure_signal",
            "diagnosis",
            "fix",
            "optimization",
        ):
            require_text(item, key, owner)
        evidence_ids = require_text_list(item, "evidence_ids", owner)
        if set(evidence_ids) - source_ids:
            fail(f"{owner} references unknown evidence ids.")

    require_list(pack.get("comparison_frame"), "source_pack.comparison_frame")
    spark = require_object(pack.get("spark"), "source_pack.spark")
    for key in ("question", "insight", "reader_change", "boundary"):
        require_text(spark, key, "spark")
    rounds = require_list(
        pack.get("spark_rounds"),
        "source_pack.spark_rounds",
    )
    if len(rounds) != 4:
        fail("spark_rounds must contain exactly four rounds.")
    for index, value in enumerate(rounds):
        owner = f"spark_rounds[{index}]"
        item = require_object(value, owner)
        for key in ("round", "question", "finding", "effect_on_spark"):
            require_text(item, key, owner)
    require_list(pack.get("article_route"), "source_pack.article_route", minimum=5)

    mindmap_path = topic_dir / "article" / "technical_mindmap.md"
    if not mindmap_path.is_file():
        fail(f"Missing file: {mindmap_path}")
    if nonspace(mindmap_path.read_text(encoding="utf-8")) < 1200:
        fail("technical_mindmap.md is too thin for Stage 2.")
    return {
        "mechanism_levels": len(chain),
        "implementation_steps": len(path),
        "spark_rounds": 4,
    }


def validate_stage3(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 2)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"),
        "source_pack.json",
    )
    chain = require_list(pack.get("mechanism_chain"), "mechanism_chain")
    mechanism_audit = require_list(
        pack.get("mechanism_audit"),
        "source_pack.mechanism_audit",
    )
    if len(mechanism_audit) != len(chain):
        fail("mechanism_audit must cover every mechanism level.")
    for index, value in enumerate(mechanism_audit):
        owner = f"mechanism_audit[{index}]"
        item = require_object(value, owner)
        for key in (
            "level",
            "causal_answer",
            "environment_check",
            "evidence_check",
            "boundary_check",
            "verdict",
        ):
            if key == "level":
                if not isinstance(item.get(key), int):
                    fail(f"{owner}.level must be an integer.")
            else:
                require_text(item, key, owner)

    implementation = require_list(pack.get("implementation_path"), "implementation_path")
    reproduction = require_list(
        pack.get("reproduction_audit"),
        "source_pack.reproduction_audit",
    )
    if len(reproduction) != len(implementation):
        fail("reproduction_audit must cover every implementation step.")
    for index, value in enumerate(reproduction):
        owner = f"reproduction_audit[{index}]"
        item = require_object(value, owner)
        for key in (
            "step_id",
            "prerequisites",
            "command_or_code_check",
            "expected_result_check",
            "failure_path_check",
            "safety_check",
            "verification_level",
            "verdict",
        ):
            require_text(item, key, owner)

    verdict = require_object(pack.get("spark_verdict"), "spark_verdict")
    for key in ("status", "surviving_insight", "counterexample", "boundary"):
        require_text(verdict, key, "spark_verdict")
    playbook = require_object(pack.get("reader_playbook"), "reader_playbook")
    for key in (
        "goal",
        "prerequisites",
        "minimal_path",
        "verification",
        "common_failures",
        "optimization",
        "stop_conditions",
    ):
        if key in {"minimal_path", "common_failures"}:
            require_list(playbook.get(key), f"reader_playbook.{key}")
        else:
            require_text(playbook, key, "reader_playbook")
    require_list(pack.get("article_boundaries"), "source_pack.article_boundaries")
    return {
        "mechanism_audits": len(mechanism_audit),
        "reproduction_audits": len(reproduction),
    }


def markdown_sections(markdown: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"(?m)^##\s+(.+?)\s*$", markdown)
    ]


def validate_stage4(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 3)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"),
        "source_pack.json",
    )
    mode = require_text(
        require_object(pack.get("article_profile"), "article_profile"),
        "mode",
        "article_profile",
    )
    path = topic_dir / "article" / "final_article.md"
    if not path.is_file():
        fail(f"Missing file: {path}")
    markdown = path.read_text(encoding="utf-8")
    if len(re.findall(r"(?m)^#\s+.+$", markdown)) != 1:
        fail("final_article.md must contain exactly one H1 title.")
    sections = markdown_sections(markdown)
    if not 5 <= len(sections) <= 7:
        fail("final_article.md must contain five to seven major sections.")
    markers = re.findall(r"<!--\s*IMAGE:(section_\d+)\s*-->", markdown)
    expected = [f"section_{index}" for index in range(1, len(sections) + 1)]
    if markers != expected:
        fail("Each major section needs one ordered IMAGE:section_N marker.")
    if re.search(r"\[\^[^\]]+\]", markdown):
        fail("Publishing footnote markers are not allowed.")
    numeric_claims = require_list(
        pack.get("numeric_claims"),
        "source_pack.numeric_claims",
        allow_empty=True,
    )
    numeric_by_id = {
        require_text(require_object(value, "numeric_claim"), "id", "numeric_claim"):
        require_object(value, "numeric_claim")
        for value in numeric_claims
    }
    marker_ids = {
        marker
        for group in re.findall(
            r"<!--\s*DATA:([N\d,\s]+)\s*-->",
            markdown,
        )
        for marker in re.findall(r"N\d+", group)
    }
    if marker_ids - set(numeric_by_id):
        fail("final_article.md contains unknown DATA markers.")
    if any(numeric_by_id[marker]["status"] == "omit" for marker in marker_ids):
        fail("Numeric claims marked omit cannot be published.")
    if re.search(r"(?m)^\s*##\s*第\s*[一二三四五六七八九十\d]+\s*[章节]", markdown):
        fail("Do not use formal 第N章 section labels.")
    if mode == "hands_on_playbook":
        code_blocks = re.findall(r"(?ms)^```([A-Za-z0-9_+#.-]+)\s*\n.*?^```", markdown)
        if not code_blocks:
            fail("hands_on_playbook needs at least one language-labelled code block.")
    html_path = write_wechat_html(topic_dir, quiet=True)
    html = html_path.read_text(encoding="utf-8")
    if re.search(r"<!--[\s\S]*?-->", html):
        fail("final_article_copy.html contains construction comments.")
    if re.search(r"\[\^[^\]]+\]", html):
        fail("final_article_copy.html contains publishing footnotes.")
    font_sizes = set(re.findall(r"font-size:\s*([^;\"']+)", html))
    if font_sizes - {"15px", "12px", "0"}:
        fail(f"Unexpected HTML font sizes: {sorted(font_sizes)}")
    if "data-wa-format=\"code-block\"" in html:
        if "data-wa-code-line=" not in html:
            fail("Rendered code blocks must include line structure.")
        code_lines = re.findall(
            r'<p data-wa-code-line="\d+"[^>]*style="([^"]+)"',
            html,
        )
        if not code_lines or any("font-size: 12px" not in style for style in code_lines):
            fail("Rendered code lines must use 12px text.")
    return {
        "mode": mode,
        "sections": len(sections),
        "characters": nonspace(markdown),
        "html": str(html_path),
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        fail(f"Missing JSONL file: {path}")
    items: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            items.append(require_object(json.loads(line), f"{path}:{number}"))
        except json.JSONDecodeError as exc:
            fail(f"Invalid JSONL at {path}:{number}: {exc}")
    if not items:
        fail(f"{path} must not be empty.")
    return items


def validate_stage5(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 4)
    markdown = (topic_dir / "article" / "final_article.md").read_text(encoding="utf-8")
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
    prompts = load_jsonl(topic_dir / "assets" / "image_prompts.jsonl")
    if len(prompts) != len(sections):
        fail("Stage 5 needs exactly one prompt per major section.")
    expected_ids = [f"section_{index}" for index in range(1, len(sections) + 1)]
    actual_ids: list[str] = []
    for index, item in enumerate(prompts):
        owner = f"image_prompts[{index}]"
        image_id = require_text(item, "id", owner)
        actual_ids.append(image_id)
        if require_text(item, "section_title", owner) != sections[index]:
            fail(f"{owner}.section_title must match its article section.")
        if require_text(item, "visual_role", owner) != "hybrid_context_info":
            fail(f"{owner}.visual_role must be hybrid_context_info.")
        if require_text(item, "aspect_ratio", owner) != "3:4":
            fail(f"{owner}.aspect_ratio must be 3:4.")
        if require_text(item, "style_profile", owner) != "white_material_micro_3d":
            fail(f"{owner}.style_profile must be white_material_micro_3d.")
        layout = require_text(item, "layout_ratio", owner)
        if layout not in {
            "scene_30_info_70",
            "scene_33_info_67",
            "scene_35_info_65",
        }:
            fail(f"{owner}.layout_ratio must keep scene near 1/3 and information near 2/3.")
        for key in (
            "information_form",
            "information_visual_mode",
            "information_rendering",
            "article_context",
            "reader_action_or_observation",
            "scene_layer",
            "information_question",
            "information_layer",
            "visual_bridge",
            "scene_position",
            "information_position",
            "palette_profile",
            "background_color",
            "background_material",
            "shared_anchor",
            "transition_plan",
            "transition_color_plan",
            "transition_light_plan",
            "transition_perspective_plan",
            "accent_color",
            "ratio_composition_plan",
            "composition",
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
        if item["information_visual_mode"] != visual_mode:
            fail(f"{owner}.information_visual_mode must match image_visual_system.")
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
        if item["scene_position"] != "top_third":
            fail(f"{owner}.scene_position must be top_third.")
        if item["information_position"] != "lower_two_thirds":
            fail(f"{owner}.information_position must be lower_two_thirds.")
        if item["palette_profile"] != VISUAL_PALETTE_PROFILE:
            fail(f"{owner}.palette_profile must be {VISUAL_PALETTE_PROFILE}.")
        if VISUAL_BACKGROUND_HEX not in item["background_color"].upper():
            fail(
                f"{owner}.background_color must use the tech background "
                f"{VISUAL_BACKGROUND_HEX}."
            )
        if VISUAL_BACKGROUND_HEX not in item["prompt"].upper():
            fail(
                f"{owner}.prompt must explicitly carry the tech background "
                f"{VISUAL_BACKGROUND_HEX}."
            )
        if visual_mode not in item["prompt"]:
            fail(f"{owner}.prompt must explicitly carry {visual_mode}.")
        if visual_mode == "micro_3d_editorial_illustration":
            for required in ("微3D", "原创", "禁止固定角色", "富配色"):
                if required not in item["prompt"]:
                    fail(f"{owner}.prompt must include illustration constraint: {required}.")
        visual_elements = require_list(
            item.get("visual_elements"),
            f"{owner}.visual_elements",
        )
        min_elements, max_elements = (
            (7, 12)
            if visual_mode == "micro_3d_info_cards"
            else (4, 7)
        )
        if not min_elements <= len(visual_elements) <= max_elements or any(
            not isinstance(value, str) or not value.strip()
            for value in visual_elements
        ):
            fail(
                f"{owner}.visual_elements must contain {min_elements} to "
                f"{max_elements} items for {visual_mode}."
            )
        chinese_labels = require_list(
            item.get("chinese_labels"),
            f"{owner}.chinese_labels",
            allow_empty=visual_mode == "micro_3d_editorial_illustration",
        )
        min_labels, max_labels = (
            (3, 5)
            if visual_mode == "micro_3d_info_cards"
            else (0, 3)
        )
        if not min_labels <= len(chinese_labels) <= max_labels or any(
            not isinstance(value, str) or not value.strip()
            for value in chinese_labels
        ):
            fail(
                f"{owner}.chinese_labels must contain {min_labels} to "
                f"{max_labels} labels for {visual_mode}."
            )
        colors = require_text_list(item, "supporting_colors", owner, minimum=3)
        if len(colors) > 4:
            fail(f"{owner}.supporting_colors must contain three or four colors.")
        if visual_mode == "micro_3d_editorial_illustration":
            for color in [item["accent_color"], *colors]:
                match = re.search(r"#[0-9A-Fa-f]{6}\b", color)
                if match and match.group(0).upper() not in item["prompt"].upper():
                    fail(f"{owner}.prompt must use illustration color {match.group(0)}.")
        if nonspace(item["prompt"]) <= 700:
            fail(f"{owner}.prompt must exceed 700 non-space characters.")
    if actual_ids != expected_ids:
        fail("Image prompt ids must be ordered section_1 through section_N.")
    return {
        "prompts": len(prompts),
        "aspect_ratio": "3:4",
        "information_visual_mode": visual_mode,
        "image_prompt_version": IMAGE_PROMPT_VERSION,
    }


def validate_video_cover_prompts(topic_dir: Path, video_headline: str) -> int:
    rows = load_jsonl(topic_dir / "assets" / "video_cover_prompts.jsonl")
    required_rows = {
        "微信视频号横版": ("1920x1080", "16:9"),
        "今日头条横版": ("1920x1080", "16:9"),
        "B站横版": ("1920x1080", "16:9"),
    }
    platforms: set[str] = set()
    seen: set[tuple[str, str]] = set()
    exact_fields = {"platform", "size", "aspect_ratio", "core_prompt_points", "prompt"}
    for index, value in enumerate(rows):
        owner = f"video_cover_prompts[{index}]"
        item = require_object(value, owner)
        if set(item) != exact_fields:
            fail(f"{owner} must contain exactly the five video-cover fields.")
        platform = require_text(item, "platform", owner)
        size = require_text(item, "size", owner)
        ratio = require_text(item, "aspect_ratio", owner)
        prompt = require_text(item, "prompt", owner)
        points = require_list(item.get("core_prompt_points"), f"{owner}.core_prompt_points")
        if not 4 <= len(points) <= 8 or any(not isinstance(v, str) or not v.strip() for v in points):
            fail(f"{owner}.core_prompt_points must contain four to eight strings.")
        if platform in required_rows and (size, ratio) != required_rows[platform]:
            fail(f"{owner} must use the canonical landscape size and ratio.")
        joined_points = " ".join(points)
        for token in ("50:50", "人物", "真实", "纲要", "隐喻", VISUAL_BACKGROUND_HEX):
            if token not in joined_points:
                fail(f"{owner}.core_prompt_points must include: {token}")
        for token in ("50:50", "人物", "真实", "纲要", "隐喻", VISUAL_BACKGROUND_HEX, video_headline):
            if token not in prompt:
                fail(f"{owner} must carry the shared 50:50 human-scene entry contract: {token}")
        if nonspace(prompt) <= 700:
            fail(f"{owner}.prompt must exceed 700 non-whitespace characters.")
        key = (platform, size)
        if key in seen:
            fail("video-cover platform and size pairs must be unique.")
        seen.add(key)
        platforms.add(platform)
    missing = set(required_rows) - platforms
    if missing:
        fail(f"Missing default video-cover rows: {sorted(missing)}")
    return len(rows)


def validate_stage6(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 5)
    package = require_object(
        load_json(topic_dir / "assets" / "title_cover_package.json"),
        "title_cover_package.json",
    )
    candidates = require_list(
        package.get("title_candidates"),
        "title_cover_package.title_candidates",
        minimum=5,
    )
    titles: list[str] = []
    for index, value in enumerate(candidates):
        owner = f"title_candidates[{index}]"
        item = require_object(value, owner)
        titles.append(require_text(item, "title", owner))
        for key in (
            "search_phrase",
            "reader_hook",
            "promise",
            "curiosity",
            "fidelity",
            "visual_metaphor",
            "risk",
        ):
            require_text(item, key, owner)
    selected = require_text(package, "selected_title", "title_cover_package")
    if selected not in titles:
        fail("selected_title must be one of title_candidates.")
    require_text(package, "selection_reason", "title_cover_package")
    require_text(package, "title_cover_link", "title_cover_package")
    entry = require_object(package.get("entry_contract"), "title_cover_package.entry_contract")
    for key in (
        "click_core", "human_protagonist", "familiar_scene", "active_metaphor",
        "metaphor_mapping", "unresolved_question", "reader_payoff",
        "article_headline", "video_headline", "consistency_rule",
    ):
        require_text(entry, key, "entry_contract")
    if entry["article_headline"].strip() != selected:
        fail("entry_contract.article_headline must match selected_title.")
    if not 8 <= nonspace(entry["video_headline"]) <= 18:
        fail("entry_contract.video_headline must contain 8-18 non-whitespace characters.")
    cover = require_object(package.get("cover_prompt"), "cover_prompt")
    if require_text(cover, "aspect_ratio", "cover_prompt") != "2.35:1":
        fail("cover_prompt.aspect_ratio must be 2.35:1.")
    for key in (
        "style_profile",
        "cover_layout",
        "layout_ratio",
        "scene_position",
        "information_position",
        "palette_profile",
        "background_color",
        "background_material",
        "tech_subject",
        "human_subject",
        "human_action",
        "visual_metaphor",
        "metaphor_mapping",
        "face_hand_visibility",
        "reader_problem",
        "key_action",
        "visible_result",
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
    if cover["style_profile"] != "scene_to_white_micro_3d":
        fail("cover_prompt.style_profile must be scene_to_white_micro_3d.")
    if cover["palette_profile"] != VISUAL_PALETTE_PROFILE:
        fail(
            "cover_prompt.palette_profile must be "
            f"{VISUAL_PALETTE_PROFILE}."
        )
    if VISUAL_BACKGROUND_HEX not in cover["background_color"].upper():
        fail(
            "cover_prompt.background_color must use the tech background "
            f"{VISUAL_BACKGROUND_HEX}."
        )
    if VISUAL_BACKGROUND_HEX not in cover["prompt"].upper():
        fail(
            "cover_prompt.prompt must explicitly carry the tech background "
            f"{VISUAL_BACKGROUND_HEX}."
        )
    if cover["cover_layout"] != "left_scene_right_info":
        fail("cover_prompt.cover_layout must be left_scene_right_info.")
    if cover["layout_ratio"] != "scene_50_info_50":
        fail("cover_prompt.layout_ratio must be strict scene_50_info_50.")
    if cover["scene_position"] != "left_half":
        fail("cover_prompt.scene_position must be left_half.")
    if cover["information_position"] != "right_half":
        fail("cover_prompt.information_position must be right_half.")
    if cover["information_form"] not in {
        "mechanism_snapshot",
        "data_flow",
        "step_path",
        "troubleshooting_path",
        "before_after",
    }:
        fail("cover_prompt.information_form is invalid.")
    nodes = require_list(cover.get("information_nodes"), "cover_prompt.information_nodes")
    if not 2 <= len(nodes) <= 4 or any(not isinstance(v, str) or not v.strip() for v in nodes):
        fail("cover_prompt.information_nodes must contain two to four large nodes.")
    labels = require_list(
        cover.get("information_labels"),
        "cover_prompt.information_labels",
        allow_empty=True,
    )
    if len(labels) > 3 or any(not isinstance(v, str) or not v.strip() for v in labels):
        fail("cover_prompt.information_labels must contain zero to three short labels.")
    colors = require_text_list(cover, "supporting_colors", "cover_prompt", minimum=3)
    if len(colors) > 4:
        fail("cover_prompt.supporting_colors must contain three or four colors.")
    cover_elements = require_list(
        cover.get("visual_elements"),
        "cover_prompt.visual_elements",
    )
    if not 5 <= len(cover_elements) <= 8 or any(
        not isinstance(value, str) or not value.strip()
        for value in cover_elements
    ):
        fail("cover_prompt.visual_elements must contain five to eight items.")
    if nonspace(cover["prompt"]) <= 700:
        fail("cover_prompt.prompt must exceed 700 non-space characters.")
    video_covers = validate_video_cover_prompts(topic_dir, entry["video_headline"].strip())

    markdown_path = topic_dir / "article" / "final_article.md"
    markdown = markdown_path.read_text(encoding="utf-8")
    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", markdown)
    if not title_match or title_match.group(1).strip() != selected:
        fail("final_article.md H1 must match selected_title.")
    write_wechat_html(topic_dir, quiet=True)
    digest_path = topic_dir / "article" / "final_article_digest.txt"
    if not digest_path.is_file():
        fail(f"Missing file: {digest_path}")
    digest_chars = nonspace(digest_path.read_text(encoding="utf-8"))
    if not 500 <= digest_chars <= 800:
        fail("final_article_digest.txt must contain 500-800 non-space characters.")
    return {
        "title_candidates": len(candidates),
        "selected_title": selected,
        "digest_characters": digest_chars,
        "cover_prompt_version": COVER_PROMPT_VERSION,
        "video_covers": video_covers,
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
        require_text(item, "id", f"image_prompts[{index}]")
        for index, item in enumerate(prompts)
    ]
    total_characters = 0
    audio_paths: dict[str, Path] = {}
    for index, (prompt, segment) in enumerate(zip(prompts, segments), start=1):
        owner = f"narration_segments[{index - 1}]"
        expected_id = expected_ids[index - 1]
        segment_id = require_text(segment, "id", owner)
        if segment_id != expected_id:
            fail(f"{owner}.id must be {expected_id}.")
        order = segment.get("order")
        if isinstance(order, bool) or not isinstance(order, int) or order != index:
            fail(f"{owner}.order must be {index}.")
        if require_text(segment, "image_prompt_id", owner) != expected_id:
            fail(f"{owner}.image_prompt_id must match {expected_id}.")
        expected_title = require_text(
            prompt,
            "section_title",
            f"image_prompts[{index - 1}]",
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
        characters = nonspace(narration)
        sentence_count = len(
            [
                part
                for part in re.split(r"[。！？!?…]+", narration)
                if nonspace(part)
            ]
        )
        if not 5 <= sentence_count <= 6:
            fail(f"{owner}.narration must contain five or six complete sentences.")
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
        manifest.get("segments"),
        "audio_manifest.segments",
    )
    if len(manifest_segments) != len(expected_ids):
        fail("audio_manifest must contain exactly one entry per image prompt.")

    actual_total = 0.0
    for index, (expected_id, value) in enumerate(
        zip(expected_ids, manifest_segments),
        start=1,
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
            item.get("duration_seconds"),
            f"{owner}.duration_seconds",
        )
        measured_duration = probe_audio_duration(audio_paths[expected_id])
        if measured_duration is not None:
            tolerance = max(1.0, measured_duration * 0.03)
            if abs(declared_duration - measured_duration) > tolerance:
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

    return {
        "segments": len(segments),
        "characters": total_characters,
        "tts_engine": "edge_tts",
        "duration_seconds": round(actual_total, 2),
        "narration_version": NARRATION_VERSION,
        "images_directory": str(images_dir),
        "expected_image_ids": expected_ids,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a tech-article stage.")
    parser.add_argument("--stage", type=int, choices=range(0, 8), required=True)
    parser.add_argument("--topic-dir")
    parser.add_argument("--scan-dir")
    args = parser.parse_args()

    if args.stage == 0:
        if not args.scan_dir:
            fail("--scan-dir is required for Stage 0.")
        details = validate_stage0(expand_user_path(args.scan_dir))
        print(f"PASS Stage 0: {json.dumps(details, ensure_ascii=False)}")
        return 0

    if not args.topic_dir:
        fail("--topic-dir is required for Stage 1-7.")
    topic_dir = ensure_topic_dir(expand_user_path(args.topic_dir))
    validators = {
        1: validate_stage1,
        2: validate_stage2,
        3: validate_stage3,
        4: validate_stage4,
        5: validate_stage5,
        6: validate_stage6,
        7: validate_stage7,
    }
    details = validators[args.stage](topic_dir)
    receipt = write_receipt(topic_dir, args.stage, details)
    print(
        f"PASS Stage {args.stage}: "
        f"{json.dumps({**details, 'receipt': str(receipt)}, ensure_ascii=False)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
