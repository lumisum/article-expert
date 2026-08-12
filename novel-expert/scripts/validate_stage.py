#!/usr/bin/env python3
"""Deterministic stage gates for the novel-expert workflow."""

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


CONTRACT_VERSION = 18
RENDERER_VERSION = 11
ARTICLE_CONTRACT_VERSION = 12
IMAGE_PROMPT_VERSION = 17
COVER_PROMPT_VERSION = 13
NARRATION_VERSION = 6
VISUAL_PALETTE_PROFILE = "sunlit_chromatic_midlife_story"
SERIAL_ILLUSTRATION_STYLE = "sunlit_mature_narrative_illustration_micro_3d"
COVER_ILLUSTRATION_STYLE = "sunlit_mature_narrative_illustration_micro_3d_cover"
SERIAL_PALETTE_PROFILE = "sunlit_chromatic_midlife_story"
NARRATIVE_MODES = {"novel_story"}
CAST_BIBLE_PATH = Path(__file__).resolve().parent.parent / "references" / "cast-bible.json"
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


def load_cast_bible() -> dict[str, Any]:
    cast = require_object(load_json(CAST_BIBLE_PATH), "cast-bible.json")
    if cast.get("version") != "sumei_ningxiang_leads_v2":
        fail("cast-bible.json must use sumei_ningxiang_leads_v2.")
    if cast.get("lead_cast_ids") != ["sumei", "kaidi"]:
        fail("cast-bible.json must fix lead_cast_ids to sumei and kaidi.")
    supporting_policy = require_object(
        cast.get("supporting_cast_policy"),
        "cast-bible.supporting_cast_policy",
    )
    if supporting_policy.get("allowed") is not True:
        fail("cast-bible.supporting_cast_policy.allowed must be true.")
    for key in ("rule", "continuity_rule", "dignity_rule"):
        require_text(supporting_policy, key, "cast-bible.supporting_cast_policy")
    for cast_id, expected_name in (("sumei", "苏美"), ("kaidi", "凝香")):
        character = require_object(cast.get(cast_id), f"cast-bible.{cast_id}")
        if require_text(character, "name", f"cast-bible.{cast_id}") != expected_name:
            fail(f"cast-bible.{cast_id}.name must be {expected_name}.")
        for key in (
            "gender",
            "editorial_role",
            "appearance_signature",
            "wardrobe_signature",
            "voice_signature",
            "expression_signature",
            "gesture_signature",
            "forbidden_drift",
        ):
            require_text(character, key, f"cast-bible.{cast_id}")
    return cast


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


def stage2_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "story_core": pack.get("story_core"),
        "construction_logic": pack.get("construction_logic"),
        "action_causality": pack.get("action_causality"),
        "character_arcs": pack.get("character_arcs"),
        "scene_plan": pack.get("scene_plan"),
        "knowledge_action_alignment": pack.get("knowledge_action_alignment"),
    }


def stage3_payload(pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "story_audit": pack.get("story_audit"),
        "logic_audit": pack.get("logic_audit"),
        "meaning_design": pack.get("meaning_design"),
        "optional_reference_lenses": pack.get("optional_reference_lenses"),
        "anti_anxiety_audit": pack.get("anti_anxiety_audit"),
        "novel_readiness": pack.get("novel_readiness"),
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
            load_json(topic_dir / "research" / "novel_blueprint.json"),
            "novel_blueprint.json",
        )
        return canonical_hash(
            {
                "cast_bible": file_hash(CAST_BIBLE_PATH),
                "payload": stage1_payload(pack, blueprint),
            }
        )
    if stage == 2:
        return canonical_hash(stage2_payload(pack))
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
                "story_bible": file_hash(
                    topic_dir / "assets" / "image_story_bible.json"
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
                "video_covers": file_hash(topic_dir / "assets" / "video_cover_prompts.jsonl"),
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
    narration_segments = load_jsonl(
        topic_dir / "video" / "narration_segments.jsonl"
    )
    turn_audio_hashes: dict[str, str] = {}
    for segment_index, segment in enumerate(narration_segments):
        segment_id = require_text(segment, "id", f"narration_segments[{segment_index}]")
        for turn_index, value in enumerate(
            require_list(segment.get("turns"), f"narration_segments[{segment_index}].turns"),
            start=1,
        ):
            turn = require_object(value, f"narration_segments[{segment_index}].turns[{turn_index - 1}]")
            audio_file = require_text(turn, "audio_file", "narration_turn")
            turn_audio_hashes[f"{segment_id}:{turn_index}"] = file_hash(topic_dir / audio_file)
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
            "turn_audio_files": turn_audio_hashes,
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
    cast = load_cast_bible()
    profile = require_object(pack.get("article_profile"), "source_pack.article_profile")
    if require_text(profile, "mode", "article_profile") != "midlife_novel":
        fail("article_profile.mode must be midlife_novel.")
    narrative_mode = require_text(profile, "narrative_mode", "article_profile")
    if narrative_mode not in NARRATIVE_MODES:
        fail("article_profile.narrative_mode must be novel_story.")
    for key in ("core_audience", "source_anchor", "visual_mode"):
        require_text(profile, key, "article_profile")
    narrative_contract = require_object(
        profile.get("narrative_contract"),
        "article_profile.narrative_contract",
    )
    if narrative_contract.get("lead_cast_ids") != ["sumei", "kaidi"]:
        fail("article_profile.narrative_contract.lead_cast_ids must be [sumei, kaidi].")
    if require_text(
        narrative_contract,
        "supporting_cast_policy",
        "article_profile.narrative_contract",
    ) != "as_story_requires_with_evidence_and_continuity":
        fail(
            "article_profile.narrative_contract.supporting_cast_policy must be "
            "as_story_requires_with_evidence_and_continuity."
        )
    if require_text(
        narrative_contract,
        "series_label",
        "article_profile.narrative_contract",
    ) != cast["series_label"]:
        fail("article_profile.narrative_contract.series_label must match cast-bible.json.")
    for key in (
        "episode_core",
        "role_assignment",
        "source_transformation",
        "adaptation_boundary",
        "performance_focus",
    ):
        require_text(narrative_contract, key, "article_profile.narrative_contract")
    if require_text(
        narrative_contract,
        "spoken_words_priority",
        "article_profile.narrative_contract",
    ) != "story_first_dialogue_as_action":
        fail(
            "article_profile.narrative_contract.spoken_words_priority must be "
            "story_first_dialogue_as_action."
        )
    if require_text(
        narrative_contract,
        "body_style_contract",
        "article_profile.narrative_contract",
    ) != "novel_paragraphs_only":
        fail(
            "article_profile.narrative_contract.body_style_contract must be "
            "novel_paragraphs_only."
        )
    fixed_meaning_contract = {
        "meaning_delivery": "action_consequence_choice_feedback",
        "explicit_lesson_policy": "implicit_by_default_optional_single_light_narration",
    }
    for key, expected in fixed_meaning_contract.items():
        if require_text(
            narrative_contract,
            key,
            "article_profile.narrative_contract",
        ) != expected:
            fail(f"article_profile.narrative_contract.{key} must be {expected}.")
    fixed_story_contract = {
        "story_priority": "embodied_action_first_no_lesson_required",
        "opening_rule": "time_place_people_trigger_action_unresolved_within_first_10_percent",
        "closure_rule": "opening_trigger_returns_as_visible_action_or_feedback",
    }
    for key, expected in fixed_story_contract.items():
        if require_text(
            narrative_contract,
            key,
            "article_profile.narrative_contract",
        ) != expected:
            fail(
                f"article_profile.narrative_contract.{key} must be {expected}."
            )
    retired_profile_fields = [
        key
        for key in ("help_contract", "reader_contract")
        if profile.get(key) not in (None, {}, [])
    ]
    if retired_profile_fields:
        fail(
            "Remove retired article-style profile fields: "
            + ", ".join(retired_profile_fields)
        )
    resonance_contract = require_object(
        profile.get("resonance_contract"),
        "article_profile.resonance_contract",
    )
    for key in (
        "recognition_scene",
        "emotional_truth",
        "character_dignity_boundary",
        "responsibility_boundary",
        "intended_aftertaste",
        "background_assumption",
    ):
        require_text(resonance_contract, key, "article_profile.resonance_contract")


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
            "central_event",
            "hidden_meaning_candidate",
            "knowing_doing_gap",
            "costly_choice_potential",
            "final_action_proof_potential",
            "why_now",
            "oral_material_needed",
            "traffic_reason",
            "reader_recognition",
            "relationship_tension",
            "sensory_potential",
            "aftertaste_potential",
            "dignity_risk",
            "factual_risk",
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
        load_json(topic_dir / "research" / "novel_blueprint.json"),
        "novel_blueprint.json",
    )
    for key in (
        "topic_id",
        "central_event",
        "central_question",
        "hidden_meaning",
        "meaning_expression",
        "intended_reader",
        "reader_recognition",
        "emotional_truth",
        "intended_aftertaste",
        "oral_anchor",
        "narrative_mode",
        "narrative_mode_reason",
        "episode_core",
        "role_assignment",
        "adaptation_boundary",
        "evidence_policy",
        "evidence_reason",
        "visual_world",
    ):
        require_text(blueprint, key, "novel_blueprint")
    if blueprint["meaning_expression"] not in {"implicit_action", "light_narration"}:
        fail("novel_blueprint.meaning_expression must be implicit_action or light_narration.")
    retired_blueprint_fields = [
        key
        for key in ("core_reader", "reader_pain", "reader_help", "reader_before", "reader_after")
        if blueprint.get(key) not in (None, "", {}, [])
    ]
    if retired_blueprint_fields:
        fail(
            "Remove retired article-style blueprint fields: "
            + ", ".join(retired_blueprint_fields)
        )
    narrative_position = require_object(
        blueprint.get("narrative_position"),
        "novel_blueprint.narrative_position",
    )
    for key in (
        "speaker_relation",
        "trigger_to_write",
        "known_from_life",
        "reflection_boundary",
        "unresolved_human_question",
    ):
        require_text(
            narrative_position,
            key,
            "novel_blueprint.narrative_position",
        )
    opening_contract = require_object(
        blueprint.get("opening_contract"),
        "novel_blueprint.opening_contract",
    )
    for key in (
        "time",
        "place",
        "people_present",
        "trigger_event",
        "visible_first_action",
        "unresolved_question",
        "carry_anchor",
        "ending_payoff",
    ):
        require_text(opening_contract, key, "novel_blueprint.opening_contract")
    opening_time = require_text(
        opening_contract,
        "time",
        "novel_blueprint.opening_contract",
    )
    opening_place = require_text(
        opening_contract,
        "place",
        "novel_blueprint.opening_contract",
    )
    if not 2 <= nonspace(opening_time) <= 18:
        fail("novel_blueprint.opening_contract.time must be a reusable 2-18 character phrase.")
    if not 2 <= nonspace(opening_place) <= 20:
        fail("novel_blueprint.opening_contract.place must be a reusable 2-20 character phrase.")
    carry_anchor = require_text(
        opening_contract,
        "carry_anchor",
        "novel_blueprint.opening_contract",
    )
    if not 2 <= nonspace(carry_anchor) <= 24:
        fail("novel_blueprint.opening_contract.carry_anchor must contain 2-24 non-space characters.")
    reality_logic = require_object(
        blueprint.get("reality_logic_contract"),
        "novel_blueprint.reality_logic_contract",
    )
    for key in (
        "chronology",
        "knowledge_map",
        "money_and_objects",
        "institutional_process",
        "motivation_and_alternatives",
        "causal_necessity",
        "setup_and_payoff",
        "resolution_cost",
    ):
        require_text(reality_logic, key, "novel_blueprint.reality_logic_contract")
    story_arc = require_list(
        blueprint.get("story_arc"),
        "novel_blueprint.story_arc",
    )
    if len(story_arc) != 4:
        fail("novel_blueprint.story_arc must contain exactly four story beats.")
    story_arc_basis: list[tuple[str, list[str]]] = []
    expected_story_phases = ["trigger", "friction", "choice", "payoff"]
    for index, (value, expected_phase) in enumerate(zip(story_arc, expected_story_phases)):
        owner = f"novel_blueprint.story_arc[{index}]"
        beat = require_object(value, owner)
        if require_text(beat, "phase", owner) != expected_phase:
            fail(f"{owner}.phase must be {expected_phase}.")
        for key in ("event", "visible_action", "emotional_change"):
            require_text(beat, key, owner)
        basis_values = require_list(beat.get("basis_ids"), f"{owner}.basis_ids")
        if any(not isinstance(item, str) or not item.strip() for item in basis_values):
            fail(f"{owner}.basis_ids must contain non-empty strings.")
        story_arc_basis.append(
            (owner, [str(item).strip().upper() for item in basis_values])
        )
    knowledge_action_arc = require_object(
        blueprint.get("knowledge_action_arc"),
        "novel_blueprint.knowledge_action_arc",
    )
    for key in (
        "claimed_belief",
        "habitual_action",
        "knowing_doing_gap",
        "consequence",
        "embodied_realization",
        "costly_choice",
        "final_action_proof",
        "reader_inference",
    ):
        require_text(knowledge_action_arc, key, "novel_blueprint.knowledge_action_arc")
    micro_detail_plan = require_object(
        blueprint.get("micro_detail_plan"),
        "novel_blueprint.micro_detail_plan",
    )
    for key in (
        "opening_sensory_signal",
        "first_defense_leak",
        "involuntary_body_response",
        "attention_shift",
        "before_choice_hesitation",
        "after_choice_feedback",
        "closing_environment_echo",
    ):
        require_text(micro_detail_plan, key, "novel_blueprint.micro_detail_plan")
    supporting_cast = require_list(
        blueprint.get("supporting_cast"),
        "novel_blueprint.supporting_cast",
        allow_empty=True,
    )
    supporting_cast_basis: list[tuple[str, list[str]]] = []
    supporting_ids: set[str] = set()
    supporting_names: set[str] = set()
    for index, value in enumerate(supporting_cast, start=1):
        owner = f"novel_blueprint.supporting_cast[{index - 1}]"
        character = require_object(value, owner)
        character_id = require_text(character, "id", owner).upper()
        if character_id != f"C{index:02d}":
            fail(f"{owner}.id must be C{index:02d}.")
        name = require_text(character, "name", owner)
        if name in {"苏美", "凝香"} or name in supporting_names:
            fail(f"{owner}.name must be unique and cannot replace a fixed lead.")
        supporting_ids.add(character_id)
        supporting_names.add(name)
        for key in (
            "gender_age",
            "relation_to_leads",
            "story_function",
            "appearance_boundary",
            "speech_signature",
        ):
            require_text(character, key, owner)
        basis_values = require_list(character.get("basis_ids"), f"{owner}.basis_ids")
        if any(not isinstance(item, str) or not item.strip() for item in basis_values):
            fail(f"{owner}.basis_ids must contain non-empty strings.")
        supporting_cast_basis.append(
            (owner, [str(item).strip().upper() for item in basis_values])
        )
    story_materials = require_list(
        blueprint.get("story_materials"),
        "novel_blueprint.story_materials",
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
        owner = f"novel_blueprint.story_materials[{index}]"
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
            "novel_blueprint.evidence_policy must be oral_only "
            "or authoritative_required."
        )
    require_list(blueprint.get("research_gaps"), "novel_blueprint.research_gaps", allow_empty=True)

    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"), "source_pack.json"
    )
    validate_profile(pack)
    profile = require_object(pack.get("article_profile"), "source_pack.article_profile")
    narrative_contract = require_object(
        profile.get("narrative_contract"),
        "article_profile.narrative_contract",
    )
    blueprint_mode = require_text(blueprint, "narrative_mode", "novel_blueprint")
    if blueprint_mode not in NARRATIVE_MODES:
        fail("novel_blueprint.narrative_mode is invalid.")
    if blueprint_mode != require_text(profile, "narrative_mode", "article_profile"):
        fail("Blueprint and article_profile narrative_mode values do not match.")
    for blueprint_key, contract_key in (
        ("episode_core", "episode_core"),
        ("role_assignment", "role_assignment"),
        ("adaptation_boundary", "adaptation_boundary"),
    ):
        if require_text(blueprint, blueprint_key, "novel_blueprint") != require_text(
            narrative_contract,
            contract_key,
            "article_profile.narrative_contract",
        ):
            fail(
                f"novel_blueprint.{blueprint_key} must match "
                f"article_profile.narrative_contract.{contract_key}."
            )
    resonance_contract = require_object(
        profile.get("resonance_contract"),
        "article_profile.resonance_contract",
    )
    for blueprint_key, contract_key in (
        ("reader_recognition", "recognition_scene"),
        ("emotional_truth", "emotional_truth"),
        ("intended_aftertaste", "intended_aftertaste"),
    ):
        if require_text(blueprint, blueprint_key, "novel_blueprint") != require_text(
            resonance_contract,
            contract_key,
            "article_profile.resonance_contract",
        ):
            fail(
                f"novel_blueprint.{blueprint_key} must match "
                f"article_profile.resonance_contract.{contract_key}."
            )
    if require_text(pack, "topic_id", "source_pack") != require_text(
        blueprint, "topic_id", "novel_blueprint"
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
    for owner, basis_ids in story_arc_basis:
        unknown = set(basis_ids) - known_ids
        if unknown:
            fail(f"{owner} references unknown basis ids: {sorted(unknown)}")
    for owner, basis_ids in supporting_cast_basis:
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
            "story_beats": len(story_arc),
            "narrative_mode": blueprint_mode,
        },
    )
    return {
        "evidence_policy": evidence_policy,
        "user_materials": len(user_materials),
        "observation_cards": len(cards),
        "source_domains": len(source_domains),
        "story_materials": len(story_materials),
        "story_beats": len(story_arc),
        "narrative_mode": blueprint_mode,
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
    retired = (
        "causal_spine",
        "coordinates",
        "spark",
        "spark_rounds",
        "pre_philosophical_proposition",
    )
    stale = [key for key in retired if pack.get(key) not in (None, [], {})]
    if stale:
        fail("Remove retired analytical Stage 2 fields: " + ", ".join(stale))
    blueprint = require_object(
        load_json(topic_dir / "research" / "novel_blueprint.json"),
        "novel_blueprint.json",
    )
    hidden_meaning = require_text(blueprint, "hidden_meaning", "novel_blueprint")
    meaning_expression = require_text(
        blueprint, "meaning_expression", "novel_blueprint"
    )
    core = require_object(pack.get("story_core"), "source_pack.story_core")
    for key in (
        "hidden_meaning",
        "meaning_expression",
        "reader_discovery",
        "initial_misbelief",
        "surface_desire",
        "deeper_need",
        "stakes",
        "moral_tension",
        "turning_fact",
        "costly_choice",
        "final_action_proof",
        "ending_echo",
        "sermon_risk",
    ):
        require_text(core, key, "story_core")
    if core["hidden_meaning"] != hidden_meaning:
        fail("story_core.hidden_meaning must match the Stage 1 blueprint exactly.")
    if core["meaning_expression"] != meaning_expression:
        fail("story_core.meaning_expression must match the Stage 1 blueprint.")
    construction_logic = require_object(
        pack.get("construction_logic"), "source_pack.construction_logic"
    )
    selected_models = [
        str(item).strip()
        for item in require_list(
            construction_logic.get("model_ids"),
            "construction_logic.model_ids",
        )
    ]
    allowed_models = {
        "bias_corrected_by_evidence",
        "object_consequence_chain",
        "pressure_consequence_tightening",
        "symmetric_costly_actions",
        "detail_driven_inner_shift",
        "consistent_rule_world",
        "social_mechanism_repetition",
    }
    if not 1 <= len(selected_models) <= 2:
        fail("construction_logic.model_ids must select one or two logic models.")
    unknown_models = set(selected_models) - allowed_models
    if unknown_models:
        fail(f"construction_logic.model_ids contains invalid models: {sorted(unknown_models)}")
    if len(selected_models) != len(set(selected_models)):
        fail("construction_logic.model_ids cannot contain duplicates.")
    require_text(construction_logic, "why_this_combination", "construction_logic")
    supporting_cast = require_list(
        blueprint.get("supporting_cast"),
        "novel_blueprint.supporting_cast",
        allow_empty=True,
    )
    expected_supporting_ids = [
        require_text(item, "id", f"supporting_cast[{index}]").upper()
        for index, item in enumerate(supporting_cast)
    ]
    active_supporting_ids = [
        str(item).strip().upper()
        for item in require_list(
            core.get("active_supporting_cast_ids"),
            "story_core.active_supporting_cast_ids",
            allow_empty=True,
        )
    ]
    if active_supporting_ids != expected_supporting_ids:
        fail("story_core.active_supporting_cast_ids must match the Stage 1 supporting cast order.")
    allowed_character_names = {"苏美", "凝香"} | {
        require_text(item, "name", f"supporting_cast[{index}]")
        for index, item in enumerate(supporting_cast)
    }

    known_evidence = evidence_ids(pack)
    actions = require_list(pack.get("action_causality"), "source_pack.action_causality")
    if not 3 <= len(actions) <= 5:
        fail("action_causality must contain three to five visible action steps.")
    action_ids: list[str] = []
    phase_rank = {"trigger": 0, "friction": 1, "choice": 2, "payoff": 3}
    action_phases: list[str] = []
    for index, value in enumerate(actions, start=1):
        owner = f"action_causality[{index - 1}]"
        action = require_object(value, owner)
        if action.get("order") != index:
            fail(f"{owner}.order must equal {index}.")
        action_id = require_text(action, "id", owner).upper()
        if action_id != f"A{index:02d}":
            fail(f"{owner}.id must be A{index:02d}.")
        action_ids.append(action_id)
        phase = require_text(action, "story_phase", owner)
        if phase not in phase_rank:
            fail(f"{owner}.story_phase is invalid.")
        action_phases.append(phase)
        for key in (
            "pressure",
            "belief_before",
            "visible_action",
            "information_change",
            "cost_or_risk",
            "immediate_consequence",
            "relationship_shift",
            "new_pressure",
        ):
            require_text(action, key, owner)
        bases = {
            str(item).strip().upper()
            for item in require_list(action.get("basis_ids"), f"{owner}.basis_ids")
        }
        unknown = bases - known_evidence
        if unknown:
            fail(f"{owner}.basis_ids contains unknown evidence: {sorted(unknown)}")
        if index < len(actions) and action["new_pressure"].strip().upper() == "END":
            fail(f"{owner}.new_pressure cannot be END before the final action.")
        if index == len(actions) and action["new_pressure"].strip().upper() != "END":
            fail(f"{owner}.new_pressure must be END for the final action.")
    if [phase_rank[value] for value in action_phases] != sorted(
        phase_rank[value] for value in action_phases
    ):
        fail("action_causality story phases must move forward without reversal.")
    if not {"trigger", "choice", "payoff"} <= set(action_phases):
        fail("action_causality must include trigger, choice and payoff actions.")

    arcs = require_object(pack.get("character_arcs"), "source_pack.character_arcs")
    if set(arcs) != {"sumei", "kaidi"}:
        fail("character_arcs must contain the two fixed lead arcs: sumei and kaidi.")
    for cast_id in ("sumei", "kaidi"):
        arc = require_object(arcs.get(cast_id), f"character_arcs.{cast_id}")
        for key in (
            "start_position",
            "habitual_action",
            "contradiction_exposed",
            "choice_and_cost",
            "final_action_state",
        ):
            require_text(arc, key, f"character_arcs.{cast_id}")

    scenes = require_list(pack.get("scene_plan"), "source_pack.scene_plan")
    if not 4 <= len(scenes) <= 6:
        fail("scene_plan must contain four to six novel scenes.")
    scene_phases: list[str] = []
    used_action_ids: set[str] = set()
    titles: set[str] = set()
    for index, value in enumerate(scenes, start=1):
        owner = f"scene_plan[{index - 1}]"
        scene = require_object(value, owner)
        if scene.get("order") != index:
            fail(f"{owner}.order must equal {index}.")
        if require_text(scene, "scene_id", owner).upper() != f"SC{index:02d}":
            fail(f"{owner}.scene_id must be SC{index:02d}.")
        title = require_text(scene, "scene_title", owner)
        if title in titles:
            fail(f"Duplicate scene title: {title}")
        titles.add(title)
        phase = require_text(scene, "story_phase", owner)
        if phase not in phase_rank:
            fail(f"{owner}.story_phase is invalid.")
        scene_phases.append(phase)
        for key in (
            "time_place",
            "entry_state",
            "scene_goal",
            "knowledge_change",
            "causal_bridge",
            "reality_check",
            "sensory_anchor",
            "micro_change",
            "exit_pressure",
            "image_moment",
        ):
            require_text(scene, key, owner)
        characters_present = {
            str(item).strip()
            for item in require_list(scene.get("characters_present"), f"{owner}.characters_present")
            if isinstance(item, str) and item.strip()
        }
        if not characters_present:
            fail(f"{owner}.characters_present must contain at least one character.")
        unknown_characters = characters_present - allowed_character_names
        if unknown_characters:
            fail(f"{owner}.characters_present contains unknown characters: {sorted(unknown_characters)}")
        refs = {
            str(item).strip().upper()
            for item in require_list(scene.get("action_ids"), f"{owner}.action_ids")
        }
        unknown = refs - set(action_ids)
        if unknown:
            fail(f"{owner}.action_ids contains unknown actions: {sorted(unknown)}")
        used_action_ids |= refs
        if index < len(scenes) and scene["exit_pressure"].strip().upper() == "END":
            fail(f"{owner}.exit_pressure cannot be END before the final scene.")
        if index == len(scenes) and scene["exit_pressure"].strip().upper() != "END":
            fail(f"{owner}.exit_pressure must be END for the final scene.")
    if scene_phases[0] != "trigger" or scene_phases[-1] != "payoff":
        fail("scene_plan must begin with trigger and end with payoff.")
    if set(scene_phases) != set(phase_rank):
        fail("scene_plan must cover trigger, friction, choice and payoff.")
    if used_action_ids != set(action_ids):
        fail("Every action_causality id must be assigned to at least one scene.")

    alignment = require_object(
        pack.get("knowledge_action_alignment"),
        "source_pack.knowledge_action_alignment",
    )
    for key in (
        "claimed_or_assumed_knowledge",
        "old_action_evidence",
        "reality_correction",
        "new_choice_cost",
        "final_action_evidence",
        "verbal_explanation_reason",
    ):
        require_text(alignment, key, "knowledge_action_alignment")
    if not isinstance(alignment.get("verbal_explanation_needed"), bool):
        fail("knowledge_action_alignment.verbal_explanation_needed must be boolean.")
    if meaning_expression == "implicit_action" and alignment["verbal_explanation_needed"]:
        fail("implicit_action cannot require verbal explanation.")
    if meaning_expression == "light_narration" and not alignment["verbal_explanation_needed"]:
        fail("light_narration requires verbal_explanation_needed=true and a factual reason.")
    receipt = write_receipt(
        topic_dir,
        2,
        {
            "action_steps": len(actions),
            "scenes": len(scenes),
            "meaning_expression": meaning_expression,
            "construction_models": selected_models,
            "mindmap_required": False,
        },
    )
    return {
        "action_steps": len(actions),
        "scenes": len(scenes),
        "meaning_expression": meaning_expression,
        "construction_models": selected_models,
        "receipt": str(receipt),
    }


def validate_stage3(topic_dir: Path) -> dict[str, Any]:
    require_receipt(topic_dir, 1)
    require_receipt(topic_dir, 2)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"), "source_pack.json"
    )
    retired = (
        "causal_audit",
        "wisdom_candidates",
        "wisdom_synthesis",
        "spark_verdict",
        "thesis_practice_consistency",
        "practice_design",
    )
    stale = [key for key in retired if pack.get(key) not in (None, [], {})]
    if stale:
        fail("Remove retired analytical Stage 3 fields: " + ", ".join(stale))
    audit = require_object(pack.get("story_audit"), "source_pack.story_audit")
    for key in (
        "event_continuity",
        "action_meaning",
        "knowledge_action_proof",
        "choice_cost_real",
        "ending_feedback_real",
        "lead_character_agency",
        "supporting_character_integrity",
        "stereotype_check",
        "factual_boundary",
        "invented_drama_removed",
        "sermon_risk_removed",
    ):
        require_text(audit, key, "story_audit")
    if require_text(audit, "decision", "story_audit") != "pass":
        fail("story_audit requires a return to Stage 2.")
    logic_audit = require_object(pack.get("logic_audit"), "source_pack.logic_audit")
    for key in (
        "chronology_verified",
        "knowledge_states_verified",
        "money_objects_verified",
        "institutional_process_verified",
        "motivation_alternatives_verified",
        "causal_chain_verified",
        "setup_payoff_verified",
        "resolution_cost_verified",
        "convenience_devices_removed",
    ):
        require_text(logic_audit, key, "logic_audit")
    if require_text(logic_audit, "decision", "logic_audit") != "pass":
        fail("logic_audit requires a return to Stage 2.")
    core = require_object(pack.get("story_core"), "source_pack.story_core")
    meaning = require_object(pack.get("meaning_design"), "source_pack.meaning_design")
    for key in (
        "hidden_meaning",
        "delivery_mode",
        "primary_action_evidence",
        "reader_inference_path",
        "optional_light_narration",
        "forbidden_direct_statement",
        "ending_image",
    ):
        require_text(meaning, key, "meaning_design")
    if meaning["hidden_meaning"] != core["hidden_meaning"]:
        fail("meaning_design.hidden_meaning must match story_core exactly.")
    if meaning["delivery_mode"] != core["meaning_expression"]:
        fail("meaning_design.delivery_mode must match story_core.meaning_expression.")
    consequences = require_list(
        meaning.get("supporting_consequences"),
        "meaning_design.supporting_consequences",
    )
    if not 1 <= len(consequences) <= 3 or any(
        not isinstance(item, str) or not item.strip() for item in consequences
    ):
        fail("meaning_design.supporting_consequences must contain one to three texts.")
    optional_narration = meaning["optional_light_narration"].strip()
    if meaning["delivery_mode"] == "implicit_action":
        if optional_narration.lower() != "none":
            fail("implicit_action requires meaning_design.optional_light_narration=none.")
    elif meaning["delivery_mode"] == "light_narration":
        if optional_narration.lower() == "none" or nonspace(optional_narration) > 45:
            fail("light_narration requires one optional narration sentence of at most 45 characters.")
    else:
        fail("meaning_design.delivery_mode is invalid.")

    lenses = require_list(
        pack.get("optional_reference_lenses"),
        "source_pack.optional_reference_lenses",
        allow_empty=True,
    )
    if len(lenses) > 3:
        fail("optional_reference_lenses may contain at most three useful lenses.")
    known_observations = external_evidence_ids(pack)
    for index, value in enumerate(lenses, start=1):
        owner = f"optional_reference_lenses[{index - 1}]"
        lens = require_object(value, owner)
        if require_text(lens, "id", owner).upper() != f"R{index:02d}":
            fail(f"{owner}.id must be R{index:02d}.")
        if require_text(lens, "type", owner) not in {
            "life_observation", "psychology", "sociology", "medical", "philosophy", "other"
        }:
            fail(f"{owner}.type is invalid.")
        if require_text(lens, "use", owner) not in {
            "character_understanding", "counterargument", "factual_boundary", "omit"
        }:
            fail(f"{owner}.use is invalid.")
        require_text(lens, "background_value", owner)
        if require_text(lens, "body_policy", owner) not in {
            "background_only", "light_narration_allowed"
        }:
            fail(f"{owner}.body_policy is invalid.")
        source_ids = {
            str(item).strip().upper()
            for item in require_list(lens.get("source_ids"), f"{owner}.source_ids")
        }
        unknown = source_ids - known_observations
        if unknown:
            fail(f"{owner}.source_ids contains unknown observations: {sorted(unknown)}")

    anti = require_object(pack.get("anti_anxiety_audit"), "source_pack.anti_anxiety_audit")
    for key in (
        "difficulty_acknowledged",
        "catastrophizing_removed",
        "character_dignity_preserved",
        "responsibility_preserved",
        "agency_preserved",
        "hope_carried_by_action",
        "ending_emotional_temperature",
    ):
        require_text(anti, key, "anti_anxiety_audit")
    if require_text(anti, "decision", "anti_anxiety_audit") != "pass":
        fail("anti_anxiety_audit requires a return to Stage 2.")
    readiness = require_object(pack.get("novel_readiness"), "source_pack.novel_readiness")
    readiness_flags = (
        "single_event",
        "single_hidden_meaning",
        "action_causality_complete",
        "both_character_arcs_complete",
        "final_action_proves_change",
        "story_survives_without_lesson_sentence",
        "facts_within_boundary",
        "story_logic_verified",
        "non_sermon",
    )
    for key in readiness_flags:
        if readiness.get(key) is not True:
            fail(f"novel_readiness.{key} must be true.")
    if require_text(readiness, "decision", "novel_readiness") != "ready":
        fail("novel_readiness.decision must be ready.")
    receipt = write_receipt(
        topic_dir,
        3,
        {
            "story_audit": "pass",
            "logic_audit": "pass",
            "delivery_mode": meaning["delivery_mode"],
            "optional_reference_lenses": len(lenses),
            "anti_anxiety": "pass",
            "novel_readiness": "ready",
        },
    )
    return {
        "delivery_mode": meaning["delivery_mode"],
        "optional_reference_lenses": len(lenses),
        "novel_readiness": "ready",
        "logic_audit": "pass",
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


def markdown_narration_paragraphs(markdown: str) -> list[str]:
    """Return ordinary prose paragraphs, excluding headings and character dialogue."""
    clean = re.sub(r"<!--[\s\S]*?-->", "", markdown)
    paragraphs: list[str] = []
    for block in re.split(r"\n\s*\n", clean):
        text = " ".join(line.strip() for line in block.splitlines() if line.strip()).strip()
        if not text or text.startswith("#"):
            continue
        if re.fullmatch(r"[\u4e00-\u9fffA-Za-z·]{1,12}[：:].+", text, flags=re.DOTALL):
            continue
        if re.fullmatch(r"(?:<!--\s*IMAGE:[^>]+-->|\[IMAGE_PLACEHOLDER:[^\]]+\])", text):
            continue
        paragraphs.append(text)
    return paragraphs




def validate_stage4(topic_dir: Path) -> dict[str, Any]:
    for stage in (1, 2, 3):
        require_receipt(topic_dir, stage)
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"), "source_pack.json"
    )
    validate_profile(pack)
    profile = require_object(pack.get("article_profile"), "source_pack.article_profile")
    narrative_mode = require_text(profile, "narrative_mode", "article_profile")
    blueprint = require_object(
        load_json(topic_dir / "research" / "novel_blueprint.json"),
        "novel_blueprint.json",
    )
    opening = require_object(
        blueprint.get("opening_contract"), "novel_blueprint.opening_contract"
    )
    opening_time = require_text(opening, "time", "opening_contract")
    opening_place = require_text(opening, "place", "opening_contract")
    carry_anchor = require_text(opening, "carry_anchor", "opening_contract")
    supporting_cast = require_list(
        blueprint.get("supporting_cast"),
        "novel_blueprint.supporting_cast",
        allow_empty=True,
    )
    allowed_speakers = {"苏美", "凝香"} | {
        require_text(item, "name", f"supporting_cast[{index}]")
        for index, item in enumerate(supporting_cast)
    }
    core = require_object(pack.get("story_core"), "source_pack.story_core")
    actions = require_list(pack.get("action_causality"), "source_pack.action_causality")
    scenes = require_list(pack.get("scene_plan"), "source_pack.scene_plan")
    meaning = require_object(pack.get("meaning_design"), "source_pack.meaning_design")
    alignment = require_object(
        pack.get("knowledge_action_alignment"), "source_pack.knowledge_action_alignment"
    )
    md_path = topic_dir / "article" / "final_article.md"
    if not md_path.is_file():
        fail(f"Missing file: {md_path}")
    markdown = md_path.read_text(encoding="utf-8")
    visible_markdown = re.sub(r"<!--[\s\S]*?-->", "", markdown)
    visible_markdown = re.sub(r"(?m)^#{1,6}\s+.+?\s*$", "", visible_markdown)
    article_chars = nonspace(visible_markdown)
    if not 3000 <= article_chars <= 6000:
        fail("final_article.md must contain 3000-6000 visible non-space characters.")
    sections = markdown_sections(markdown)
    expected_titles = [
        require_text(scene, "scene_title", f"scene_plan[{index}]")
        for index, scene in enumerate(scenes)
    ]
    if sections != expected_titles:
        fail("Internal ## scene headings must exactly match scene_plan order and titles.")
    section_sizes = markdown_section_sizes(markdown)
    average_section_size = sum(section_sizes) / len(section_sizes)
    if min(section_sizes) < average_section_size * 0.45:
        fail("A planned novel scene is too thin to carry action, reaction and consequence.")
    if max(section_sizes) > average_section_size * 1.8:
        fail("One novel scene is carrying too much of the story; rebalance the scene plan.")

    story_matches = list(
        re.finditer(r"<!--\s*STORY:(TRIGGER|FRICTION|CHOICE|PAYOFF)\s*-->", markdown)
    )
    if [match.group(1) for match in story_matches] != [
        "TRIGGER", "FRICTION", "CHOICE", "PAYOFF"
    ]:
        fail("Story markers must appear exactly once in trigger, friction, choice, payoff order.")
    if story_matches[0].start() / max(1, len(markdown)) > 0.12:
        fail("STORY:TRIGGER must begin within the first 12% of the article.")
    if story_matches[-1].start() / max(1, len(markdown)) < 0.70:
        fail("STORY:PAYOFF must begin in the final 30% of the article.")
    phase_sizes: dict[str, int] = {}
    for index, match in enumerate(story_matches):
        phase = match.group(1).lower()
        end = story_matches[index + 1].start() if index + 1 < len(story_matches) else len(markdown)
        phase_text = re.sub(r"<!--[\s\S]*?-->", "", markdown[match.end():end])
        phase_sizes[phase] = nonspace(phase_text)
        minimum = {"trigger": 420, "friction": 900, "choice": 650, "payoff": 420}[phase]
        if phase_sizes[phase] < minimum:
            fail(f"STORY:{phase.upper()} needs at least {minimum} visible characters.")
        if not markdown_narration_paragraphs(phase_text):
            fail(f"STORY:{phase.upper()} needs natural author narration.")
    action_matches = list(re.finditer(r"<!--\s*ACTION:(A\d{2})\s*-->", markdown))
    expected_action_ids = [require_text(item, "id", "action_causality").upper() for item in actions]
    if [match.group(1).upper() for match in action_matches] != expected_action_ids:
        fail("ACTION markers must exactly match action_causality ids and order.")
    phase_bounds: dict[str, tuple[int, int]] = {}
    for index, match in enumerate(story_matches):
        end = story_matches[index + 1].start() if index + 1 < len(story_matches) else len(markdown)
        phase_bounds[match.group(1).lower()] = (match.end(), end)
    for index, (match, action) in enumerate(zip(action_matches, actions)):
        phase = require_text(action, "story_phase", f"action_causality[{index}]")
        start, end = phase_bounds[phase]
        if not start < match.start() < end:
            fail(f"ACTION:{expected_action_ids[index]} must appear inside STORY:{phase.upper()}.")

    def compact(text: str) -> str:
        return re.sub(r"[\s，。！？!?；;：“”\"'、,.：]+", "", text)

    for index, (match, action) in enumerate(zip(action_matches, actions)):
        end = action_matches[index + 1].start() if index + 1 < len(action_matches) else len(markdown)
        action_segment = re.sub(r"<!--[\s\S]*?-->", "", markdown[match.end():end])
        planned_action = require_text(action, "visible_action", f"action_causality[{index}]")
        if compact(planned_action) not in compact(action_segment):
            fail(f"ACTION:{expected_action_ids[index]} must visibly enact its planned visible_action.")
        planned_consequence = require_text(
            action, "immediate_consequence", f"action_causality[{index}]"
        )
        if compact(planned_consequence) not in compact(action_segment):
            fail(f"ACTION:{expected_action_ids[index]} must show its immediate consequence.")
    turn_markers = list(re.finditer(r"<!--\s*MEANING:TURN\s*-->", markdown))
    proof_markers = list(re.finditer(r"<!--\s*MEANING:PROOF\s*-->", markdown))
    if len(turn_markers) != 1 or len(proof_markers) != 1:
        fail("final_article.md needs exactly one MEANING:TURN and one MEANING:PROOF marker.")
    if not (
        story_matches[1].start()
        < turn_markers[0].start()
        < story_matches[2].start()
        < proof_markers[0].start()
        < story_matches[3].start()
    ):
        fail("Meaning markers must locate the embodied turn and final action proof.")
    proof_text = re.sub(
        r"<!--[\s\S]*?-->", "", markdown[proof_markers[0].end():story_matches[3].start()]
    )
    final_action = require_text(core, "final_action_proof", "story_core")
    if compact(final_action) not in compact(proof_text):
        fail("The block after MEANING:PROOF must enact story_core.final_action_proof.")
    retired_marker_pattern = (
        r"<!--\s*(?:DESCENT:|SPARK:|REBOUND\s*-->|WISDOM:|AUTHOR:SYNTHESIS|PRACTICE)"
    )
    if re.search(retired_marker_pattern, markdown):
        fail("final_article.md contains retired analytical construction markers.")

    visible_compact = compact(visible_markdown)
    quarter = max(1, len(visible_compact) // 4)
    for owner, value in (("time", opening_time), ("place", opening_place)):
        if compact(value) not in visible_compact[:quarter]:
            fail(f"opening_contract.{owner} must appear naturally in the opening quarter.")
    if compact(carry_anchor) not in visible_compact[:quarter]:
        fail("opening_contract.carry_anchor must appear in the opening quarter.")
    if compact(carry_anchor) not in visible_compact[-quarter:]:
        fail("opening_contract.carry_anchor must return in the closing quarter.")

    speaker_turns = re.findall(
        r"(?m)^([\u4e00-\u9fffA-Za-z·]{1,12})[：:]\s*(.+?)\s*$",
        visible_markdown,
    )
    unknown_speakers = {speaker for speaker, _ in speaker_turns} - allowed_speakers
    if unknown_speakers:
        fail(
            "Dialogue contains characters absent from supporting_cast: "
            + ", ".join(sorted(unknown_speakers))
        )
    speaker_counts = {
        name: sum(1 for speaker, _ in speaker_turns if speaker == name)
        for name in ("苏美", "凝香")
    }
    if min(speaker_counts.values()) < 2:
        fail("Both Sumei and Ningxiang need at least two indispensable dialogue paragraphs.")
    filler_turns = {"嗯", "嗯。", "哦", "哦。", "是吗", "是吗？", "然后呢", "然后呢？", "好吧", "好吧。", "对", "对。", "没事", "没事。"}
    for speaker, text in speaker_turns:
        length = nonspace(text)
        if length < 3 or length > 100:
            fail(f"{speaker} dialogue must contain 3-100 non-space characters.")
        if re.sub(r"\s+", "", text) in filler_turns:
            fail(f"{speaker} filler dialogue must be removed or embodied in narration.")
    performance_notes = re.findall(r"(?m)^\*([^*\n]{6,})\*\s*$", visible_markdown)
    if performance_notes:
        fail("Integrate performance notes into ordinary author narration.")
    if re.search(r"(?m)^〔[^〔〕\n]{2,}〕\s*$", visible_markdown):
        fail("Environment writing must be ordinary narration; remove the retired 〔environment〕 format.")
    narration_paragraphs = markdown_narration_paragraphs(markdown)
    if len(narration_paragraphs) < 20:
        fail("novel_story needs at least twenty narration paragraphs carrying scene and action.")
    environment_tokens = (
        "光", "灯", "影", "窗", "门", "风", "雨", "雪", "空气", "温度",
        "声音", "响", "安静", "桌", "椅", "地面", "墙", "房间", "街", "车",
    )
    environment_bearing = [
        paragraph
        for paragraph in narration_paragraphs
        if any(token in paragraph for token in environment_tokens)
    ]
    if len(environment_bearing) < 4:
        fail("At least four ordinary narration paragraphs must embody the changing environment.")
    narration_text = " ".join(narration_paragraphs)
    micro_domains = {
        "voice_or_breath": ("声音", "气息", "呼吸", "句尾", "嗓", "停顿"),
        "face_or_gaze": ("眼", "目光", "眉", "嘴角", "脸", "视线"),
        "hands_or_body": ("手", "指", "肩", "身体", "背", "脚", "膝"),
        "distance_or_direction": ("距离", "靠近", "退开", "转向", "侧身", "对面", "旁边"),
    }
    for domain, tokens in micro_domains.items():
        if not any(token in narration_text for token in tokens):
            fail(f"Author narration lacks embodied micro-detail domain: {domain}.")
    forbidden_syntax = {
        "bold emphasis": r"\*\*[^*\n]+\*\*",
        "italic emphasis": r"(?<!\*)\*[^*\n]+\*(?!\*)|(?<!_)_[^_\n]+_(?!_)",
        "inline code": r"`[^`\n]+`",
        "third-level heading": r"(?m)^###\s+",
        "blockquote": r"(?m)^>\s+",
        "list": r"(?m)^\s*(?:[-+]\s+|\d+\.\s+)",
        "table": r"(?m)^\s*\|.+\|\s*$",
        "code fence": r"(?m)^\s*(?:```|~~~)",
        "horizontal rule": r"(?m)^\s*(?:---+|___+|\*\*\*+)\s*$",
    }
    for label, pattern in forbidden_syntax.items():
        if re.search(pattern, visible_markdown):
            fail(f"Novel body only allows narration and character dialogue; remove {label}.")

    hidden_meaning = require_text(meaning, "hidden_meaning", "meaning_design")
    forbidden_statement = require_text(
        meaning, "forbidden_direct_statement", "meaning_design"
    )
    delivery_mode = require_text(meaning, "delivery_mode", "meaning_design")
    if compact(hidden_meaning) in visible_compact:
        fail("The hidden meaning must not be stated verbatim in the novel.")
    if compact(forbidden_statement) in visible_compact:
        fail("The forbidden direct lesson statement leaked into the novel.")
    optional_light = require_text(
        meaning, "optional_light_narration", "meaning_design"
    )
    if delivery_mode == "implicit_action":
        if optional_light.lower() != "none":
            fail("implicit_action must not define optional light narration.")
    else:
        if visible_compact.count(compact(optional_light)) != 1:
            fail("light_narration must appear exactly once as ordinary author narration.")
    sermon_patterns = (
        r"这(?:件事|一刻|个故事)?告诉我们",
        r"这说明(?:了)?",
        r"人到中年(?:就|要|应该|必须)",
        r"你要明白",
        r"我们应该",
        r"真正的[^。！？]{0,18}是",
    )
    if any(re.search(pattern, visible_markdown) for pattern in sermon_patterns):
        fail("The novel contains direct lesson or sermon language; express it through action.")
    if alignment.get("verbal_explanation_needed") is False and delivery_mode != "implicit_action":
        fail("meaning delivery contradicts knowledge_action_alignment.")

    html_path = write_wechat_html(topic_dir, quiet=True)
    html = html_path.read_text(encoding="utf-8")
    if re.search(
        r"(?:DATA:|USER:|STORY:|ACTION:|MEANING:|DESCENT:|SPARK:|REBOUND|WISDOM:|AUTHOR:|PRACTICE|IMAGE:)",
        html,
    ):
        fail("final_article_copy.html leaks construction markers.")
    expected_theme = f'midlife-{narrative_mode.replace("_", "-")}'
    if f'data-wa-theme="{expected_theme}"' not in html:
        fail("final_article_copy.html is not using the novel story theme.")
    rendered_dialogue = len(re.findall(r'data-wa-format="character-dialogue"', html))
    rendered_narration = len(re.findall(r'data-wa-format="author-narration"', html))
    if rendered_dialogue:
        fail("Novel HTML must not use special character-dialogue formatting.")
    expected_novel_paragraphs = len(narration_paragraphs) + len(speaker_turns)
    if rendered_narration != expected_novel_paragraphs:
        fail("HTML must render narration and direct speech as identical novel paragraphs.")
    formats = set(re.findall(r'data-wa-format="([^"]+)"', html))
    allowed = {"article-title", "author-narration"}
    if formats - allowed:
        fail("Novel HTML contains forbidden visible formats: " + ", ".join(sorted(formats - allowed)))
    receipt = write_receipt(
        topic_dir,
        4,
        {
            "sections": len(sections),
            "nonspace_chars": article_chars,
            "renderer_version": RENDERER_VERSION,
            "article_contract_version": ARTICLE_CONTRACT_VERSION,
            "narrative_mode": narrative_mode,
            "delivery_mode": delivery_mode,
            "action_markers": len(action_matches),
            "novel_paragraph_blocks": rendered_narration,
            "direct_speech_paragraphs": len(speaker_turns),
            "final_action_proof": "present",
            "story_phase_sizes": phase_sizes,
            "section_sizes": section_sizes,
        },
    )
    return {
        "sections": len(sections),
        "nonspace_chars": article_chars,
        "delivery_mode": delivery_mode,
        "action_markers": len(action_matches),
        "final_action_proof": "present",
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
    cast = load_cast_bible()
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"),
        "source_pack.json",
    )
    validate_profile(pack)
    profile = require_object(pack.get("article_profile"), "source_pack.article_profile")
    narrative_mode = require_text(profile, "narrative_mode", "article_profile")
    md_path = topic_dir / "article" / "final_article.md"
    markdown = md_path.read_text(encoding="utf-8")
    sections = markdown_sections(markdown)
    blueprint = require_object(
        load_json(topic_dir / "research" / "novel_blueprint.json"),
        "novel_blueprint.json",
    )
    supporting_cast = require_list(
        blueprint.get("supporting_cast"),
        "novel_blueprint.supporting_cast",
        allow_empty=True,
    )
    supporting_by_name = {
        require_text(item, "name", f"supporting_cast[{index}]"): item
        for index, item in enumerate(supporting_cast)
    }
    allowed_visual_characters = {"苏美", "凝香"} | set(supporting_by_name)
    bible = require_object(
        load_json(topic_dir / "assets" / "image_story_bible.json"),
        "image_story_bible.json",
    )
    for key in (
        "version",
        "visual_mode",
        "series_format",
        "visual_meaning_core",
        "series_logline",
        "protagonist_continuity_signature",
    ):
        require_text(bible, key, "image_story_bible")
    if bible["version"] != "novel_serial_illustration_v2":
        fail("image_story_bible.version must be novel_serial_illustration_v2.")
    if bible["visual_mode"] != SERIAL_ILLUSTRATION_STYLE:
        fail(f"image_story_bible.visual_mode must be {SERIAL_ILLUSTRATION_STYLE}.")
    if bible["series_format"] != "continuous_full_bleed_picture_story":
        fail("image_story_bible.series_format must be continuous_full_bleed_picture_story.")
    signature = bible["protagonist_continuity_signature"].strip()
    expected_sumei_signature = require_text(
        require_object(cast.get("sumei"), "cast-bible.sumei"),
        "appearance_signature",
        "cast-bible.sumei",
    )
    expected_kaidi_signature = require_text(
        require_object(cast.get("kaidi"), "cast-bible.kaidi"),
        "appearance_signature",
        "cast-bible.kaidi",
    )
    if signature != expected_sumei_signature:
        fail("protagonist_continuity_signature must match Sumei in cast-bible.json verbatim.")
    if require_text(bible, "narrative_mode", "image_story_bible") != narrative_mode:
        fail("image_story_bible.narrative_mode must match article_profile.narrative_mode.")
    require_text(bible, "episode_core", "image_story_bible")
    cast_mode = require_text(bible, "cast_mode", "image_story_bible")
    if cast_mode != "fixed_leads_dynamic_supporting_cast":
        fail("image_story_bible.cast_mode must be fixed_leads_dynamic_supporting_cast.")
    require_text(bible, "cast_selection_reason", "image_story_bible")
    secondary_signature = require_text(
        bible,
        "secondary_protagonist_signature",
        "image_story_bible",
    )
    if secondary_signature != expected_kaidi_signature:
        fail("secondary_protagonist_signature must match Kaidi in cast-bible.json verbatim.")

    character = require_object(bible.get("character_bible"), "image_story_bible.character_bible")
    for key in (
        "identity",
        "face_hair_signature",
        "body_and_age_signature",
        "wardrobe_system",
        "signature_object",
        "expression_and_gesture_range",
        "forbidden_drift",
    ):
        require_text(character, key, "character_bible")
    secondary_character = require_object(
        bible.get("secondary_character_bible"),
        "image_story_bible.secondary_character_bible",
    )
    for key in (
        "identity",
        "face_hair_signature",
        "body_and_age_signature",
        "wardrobe_system",
        "signature_object",
        "expression_and_gesture_range",
        "forbidden_drift",
    ):
        require_text(secondary_character, key, "secondary_character_bible")
    supporting_bible = require_list(
        bible.get("supporting_character_bible"),
        "image_story_bible.supporting_character_bible",
        allow_empty=True,
    )
    if len(supporting_bible) != len(supporting_cast):
        fail("supporting_character_bible must match the Stage 1 supporting cast count.")
    for index, (visual_value, source_value) in enumerate(zip(supporting_bible, supporting_cast)):
        owner = f"supporting_character_bible[{index}]"
        visual_character = require_object(visual_value, owner)
        if require_text(visual_character, "id", owner).upper() != require_text(
            source_value, "id", f"supporting_cast[{index}]"
        ).upper():
            fail(f"{owner}.id must match the Stage 1 supporting cast.")
        if require_text(visual_character, "name", owner) != require_text(
            source_value, "name", f"supporting_cast[{index}]"
        ):
            fail(f"{owner}.name must match the Stage 1 supporting cast.")
        for key in ("continuity_signature", "relationship_signature", "forbidden_drift"):
            require_text(visual_character, key, owner)
    relationship_arc = require_object(
        bible.get("relationship_arc"),
        "image_story_bible.relationship_arc",
    )
    for key in (
        "relationship_type",
        "source_basis",
        "initial_distance",
        "nonverbal_dialogue_language",
        "turning_exchange",
        "final_relationship_state",
        "forbidden_invention",
    ):
        require_text(relationship_arc, key, "relationship_arc")
    if not all(
        token in relationship_arc["relationship_type"]
        for token in ("搭档", "朋友")
    ):
        fail("relationship_arc.relationship_type must keep Sumei and Kaidi as partners and friends.")
    if "恋爱" not in relationship_arc["forbidden_invention"]:
        fail("relationship_arc.forbidden_invention must explicitly forbid invented romance.")
    composition_contract = require_object(
        bible.get("composition_contract"),
        "image_story_bible.composition_contract",
    )
    if composition_contract.get("scene_coverage") != "full_frame_100_percent_story_scene":
        fail("composition_contract.scene_coverage must be full_frame_100_percent_story_scene.")
    expected_weights = {
        "human_relationship_action_weight": 65,
        "embedded_metaphor_environment_weight": 25,
        "caption_frame_weight": 8,
        "breathing_transition_hook_weight": 2,
        "independent_information_layer_weight": 0,
    }
    for key, expected in expected_weights.items():
        if composition_contract.get(key) != expected:
            fail(f"composition_contract.{key} must equal {expected}.")
    caption_contract = require_object(
        bible.get("caption_frame_contract"),
        "image_story_bible.caption_frame_contract",
    )
    for key in (
        "frame_style",
        "caption_length_range",
        "caption_content_rule",
        "text_rendering_rule",
        "other_text_policy",
    ):
        require_text(caption_contract, key, "caption_frame_contract")
    if caption_contract["frame_style"] != "cinematic_story_caption_frame":
        fail("caption_frame_contract.frame_style must be cinematic_story_caption_frame.")
    if caption_contract.get("frame_coverage_percent") != 8:
        fail("caption_frame_contract.frame_coverage_percent must equal 8.")
    if caption_contract["caption_length_range"] != "4-14 Chinese non-space chars":
        fail("caption_frame_contract.caption_length_range must be 4-14 Chinese non-space chars.")
    if caption_contract["text_rendering_rule"] != "direct_exact_chinese_preferred_with_overlay_fallback":
        fail("caption_frame_contract.text_rendering_rule is invalid.")
    if caption_contract["other_text_policy"] != "no_text_outside_caption_frame":
        fail("caption_frame_contract.other_text_policy is invalid.")
    if require_list(
        caption_contract.get("frame_position_options"),
        "caption_frame_contract.frame_position_options",
    ) != ["top_frame", "bottom_frame"]:
        fail("caption_frame_contract.frame_position_options must be top_frame and bottom_frame.")
    world = require_object(bible.get("world_bible"), "image_story_bible.world_bible")
    for key in (
        "setting_logic",
        "material_language",
        "camera_language",
        "lighting_continuity",
        "time_progression",
        "cinematic_depth_rule",
        "caption_frame_visual_rule",
    ):
        require_text(world, key, "world_bible")
    emotional = require_object(
        bible.get("emotional_direction"),
        "image_story_bible.emotional_direction",
    )
    for key in (
        "tone",
        "expression_baseline",
        "difficult_scene_rule",
        "hope_carrier",
        "forbidden_expression",
        "expression_arc",
        "sumei_expression_progression",
        "kaidi_expression_progression",
        "contrast_rule",
        "micro_expression_rule",
        "no_flat_repetition",
    ):
        require_text(emotional, key, "emotional_direction")
    if emotional["tone"] != "sunlit_hopeful_without_denial":
        fail("emotional_direction.tone must be sunlit_hopeful_without_denial.")
    sunny_target = emotional.get("sunny_panel_ratio_target")
    if isinstance(sunny_target, bool) or not isinstance(sunny_target, (int, float)) or sunny_target < 0.7:
        fail("emotional_direction.sunny_panel_ratio_target must be at least 0.7.")
    max_non_smiling = emotional.get("max_non_smiling_panels")
    if (
        isinstance(max_non_smiling, bool)
        or not isinstance(max_non_smiling, int)
        or not 0 <= max_non_smiling <= 2
    ):
        fail("emotional_direction.max_non_smiling_panels must be an integer from 0 to 2.")
    palette = require_object(bible.get("palette_bible"), "image_story_bible.palette_bible")
    for key in (
        "profile",
        "opening_phase",
        "descent_phase",
        "turning_phase",
        "rebound_phase",
        "integration_phase",
        "color_discipline",
    ):
        require_text(palette, key, "palette_bible")
    if palette["profile"] != SERIAL_PALETTE_PROFILE:
        fail(f"palette_bible.profile must be {SERIAL_PALETTE_PROFILE}.")
    palette_colors = require_list(palette.get("colors"), "palette_bible.colors")
    if not 6 <= len(palette_colors) <= 9 or any(
        not isinstance(value, str) or not re.search(r"#[0-9A-Fa-f]{6}\b", value)
        for value in palette_colors
    ):
        fail("palette_bible.colors must contain six to nine named HEX colors.")
    palette_hexes = {
        re.search(r"#[0-9A-Fa-f]{6}\b", value).group(0).upper()
        for value in palette_colors
    }
    motif = require_object(bible.get("recurring_motif"), "image_story_bible.recurring_motif")
    for key in ("motif_name", "initial_state", "transform_rule", "final_state"):
        require_text(motif, key, "recurring_motif")
    motif_name = motif["motif_name"].strip()
    continuity_rules = require_list(
        bible.get("continuity_rules"),
        "image_story_bible.continuity_rules",
    )
    if not 5 <= len(continuity_rules) <= 12 or any(
        not isinstance(value, str) or not value.strip() for value in continuity_rules
    ):
        fail("continuity_rules must contain five to twelve executable rules.")

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

    storyboard = require_list(bible.get("storyboard"), "image_story_bible.storyboard")
    if len(storyboard) != len(sections):
        fail("image_story_bible.storyboard must contain exactly one panel per section.")
    prompts = load_jsonl(topic_dir / "assets" / "image_prompts.jsonl")
    if len(prompts) != len(sections):
        fail("image_prompts.jsonl must contain exactly one row per section.")

    phase_order = {
        "opening": 0,
        "pressure": 1,
        "descent": 2,
        "low_point": 3,
        "turning": 4,
        "rebound": 5,
        "integration": 6,
    }
    beat_types = {
        "opening_hook",
        "inciting_pressure",
        "deepening_conflict",
        "choice_or_cost",
        "low_point",
        "recognition",
        "turning_action",
        "rebound_step",
        "integration",
        "afterglow",
    }
    transition_methods = {
        "match_object",
        "continued_motion",
        "gaze_bridge",
        "color_relay",
        "light_relay",
        "spatial_threshold",
        "time_echo",
        "scale_metaphor",
    }
    story_phases: list[str] = []
    previous_out = ""
    previous_carry: set[str] = set()
    out_tokens: set[str] = set()
    visible_actions: set[str] = set()
    sunny_count = 0
    non_smiling_count = 0
    multi_character_count = 0
    nonverbal_dialogues: set[str] = set()
    smile_types_used: set[str] = set()
    expression_pairs: set[tuple[str, str]] = set()
    micro_expression_changes: set[str] = set()
    caption_texts: set[str] = set()
    previous_smile_type = ""
    previous_expression_pair: tuple[str, str] | None = None
    smiling_types = {
        "soft_smile",
        "bright_smile",
        "relieved_smile",
        "confident_smile",
        "playful_smile",
    }
    thoughtful_types = {"calm_focus", "quiet_reflection"}

    for index, (plan_value, item, section_title, image_id) in enumerate(
        zip(storyboard, prompts, sections, expected_ids), start=1
    ):
        plan_owner = f"storyboard[{index - 1}]"
        plan = require_object(plan_value, plan_owner)
        owner = f"image_prompts[{index - 1}]"
        for key in (
            "image_id",
            "section_title",
            "story_phase",
            "beat_type",
            "story_function",
            "visible_action",
            "visual_metaphor",
            "caption_text",
            "caption_role",
            "caption_frame_position",
            "continuity_token_in",
            "continuity_token_out",
            "transition_method",
            "smile_type",
            "facial_expression",
            "sumei_expression",
            "kaidi_expression",
            "character_expression_relationship",
            "micro_expression_change",
            "expression_link_from_previous",
            "body_openness",
            "hope_signal",
            "character_blocking",
            "nonverbal_dialogue",
            "relationship_beat",
            "shared_action",
            "next_panel_hook",
            "color_arc_role",
        ):
            require_text(plan, key, plan_owner)
        plan_characters = [
            str(value).strip()
            for value in require_list(plan.get("characters_present"), f"{plan_owner}.characters_present")
            if isinstance(value, str) and value.strip()
        ]
        if not plan_characters or len(set(plan_characters)) != len(plan_characters):
            fail(f"{plan_owner}.characters_present must contain unique character names.")
        unknown_plan_characters = set(plan_characters) - allowed_visual_characters
        if unknown_plan_characters:
            fail(f"{plan_owner}.characters_present contains unknown characters: {sorted(unknown_plan_characters)}")
        if not {"苏美", "凝香"} & set(plan_characters):
            fail(f"{plan_owner} must keep at least one fixed lead in the scene.")
        plan_lead_visibility = require_text(plan, "lead_visibility", plan_owner)
        expected_visibility = (
            "both" if {"苏美", "凝香"} <= set(plan_characters)
            else "sumei_only" if "苏美" in plan_characters
            else "ningxiang_only"
        )
        if plan_lead_visibility != expected_visibility:
            fail(f"{plan_owner}.lead_visibility must be {expected_visibility}.")
        plan_carry = require_list(plan.get("carryover_elements"), f"{plan_owner}.carryover_elements")
        if not 2 <= len(plan_carry) <= 4 or any(
            not isinstance(value, str) or not value.strip() for value in plan_carry
        ):
            fail(f"{plan_owner}.carryover_elements must contain two to four strings.")
        plan_sunny = plan.get("sunny_expression")
        if not isinstance(plan_sunny, bool):
            fail(f"{plan_owner}.sunny_expression must be boolean.")
        plan_hope = plan.get("hope_level")
        if isinstance(plan_hope, bool) or not isinstance(plan_hope, int) or not 1 <= plan_hope <= 5:
            fail(f"{plan_owner}.hope_level must be an integer from 1 to 5.")
        if require_text(item, "image_id", owner) != image_id:
            fail(f"{owner}.image_id must be {image_id}.")
        if item.get("section_index") != index:
            fail(f"{owner}.section_index must equal {index}.")
        if require_text(item, "section_title", owner) != section_title:
            fail(f"{owner}.section_title must match the Markdown heading.")
        role = require_text(item, "visual_role", owner)
        if role != "serial_story_panel":
            fail(f"{owner}.visual_role must be serial_story_panel.")
        if require_text(item, "aspect_ratio", owner) != "3:4":
            fail(f"{owner}.aspect_ratio must be 3:4.")
        for key in (
            "story_phase",
            "beat_type",
            "article_context",
            "panel_meaning",
            "narrative_mode",
            "subject_profile",
            "protagonist_continuity_signature",
            "cast_mode",
            "secondary_protagonist_signature",
            "character_state",
            "wardrobe_continuity",
            "supporting_characters",
            "visible_action",
            "emotional_shift",
            "visual_metaphor",
            "meaning_embodiment",
            "caption_text",
            "caption_role",
            "caption_frame_position",
            "caption_frame_style",
            "caption_rendering",
            "recurring_motif_state",
            "continuity_token_in",
            "continuity_token_out",
            "previous_panel_callback",
            "next_panel_hook",
            "transition_method",
            "smile_type",
            "facial_expression",
            "sumei_expression",
            "kaidi_expression",
            "character_expression_relationship",
            "micro_expression_change",
            "expression_link_from_previous",
            "body_openness",
            "hope_signal",
            "character_blocking",
            "nonverbal_dialogue",
            "relationship_beat",
            "shared_action",
            "camera_plan",
            "composition",
            "scene_coverage",
            "depth_layers",
            "lighting_plan",
            "style_profile",
            "palette_profile",
            "dominant_color",
            "color_arc_role",
            "texture_plan",
            "micro_3d_plan",
            "text_policy",
            "negative_constraints",
            "prompt",
        ):
            require_text(item, key, owner)

        for key in (
            "image_id",
            "section_title",
            "story_phase",
            "beat_type",
            "visible_action",
            "visual_metaphor",
            "caption_text",
            "caption_role",
            "caption_frame_position",
            "continuity_token_in",
            "continuity_token_out",
            "transition_method",
            "smile_type",
            "facial_expression",
            "sumei_expression",
            "kaidi_expression",
            "character_expression_relationship",
            "micro_expression_change",
            "expression_link_from_previous",
            "body_openness",
            "hope_signal",
            "character_blocking",
            "nonverbal_dialogue",
            "relationship_beat",
            "shared_action",
            "next_panel_hook",
            "color_arc_role",
        ):
            if item[key] != plan[key]:
                fail(f"{owner}.{key} must match {plan_owner}.{key}.")
        if not isinstance(item.get("sunny_expression"), bool):
            fail(f"{owner}.sunny_expression must be boolean.")
        if item.get("sunny_expression") is not plan_sunny:
            fail(f"{owner}.sunny_expression must match {plan_owner}.sunny_expression.")
        item_hope = item.get("hope_level")
        if isinstance(item_hope, bool) or not isinstance(item_hope, int) or not 1 <= item_hope <= 5:
            fail(f"{owner}.hope_level must be an integer from 1 to 5.")
        if item_hope != plan_hope:
            fail(f"{owner}.hope_level must match {plan_owner}.hope_level.")
        item_characters = [
            str(value).strip()
            for value in require_list(item.get("characters_present"), f"{owner}.characters_present")
            if isinstance(value, str) and value.strip()
        ]
        if item_characters != plan_characters:
            fail(f"{owner}.characters_present must match its storyboard panel.")
        if require_text(item, "lead_visibility", owner) != plan_lead_visibility:
            fail(f"{owner}.lead_visibility must match its storyboard panel.")
        carry = require_list(item.get("carryover_elements"), f"{owner}.carryover_elements")
        if carry != plan_carry:
            fail(f"{owner}.carryover_elements must match its storyboard panel.")
        if item["subject_profile"] != "fixed_leads_with_scene_required_supporting_cast":
            fail(f"{owner}.subject_profile must be fixed_leads_with_scene_required_supporting_cast.")
        if item["narrative_mode"] != narrative_mode:
            fail(f"{owner}.narrative_mode must match article_profile.narrative_mode.")
        if item["protagonist_continuity_signature"].strip() != signature:
            fail(f"{owner}.protagonist_continuity_signature must match the story bible verbatim.")
        if item["cast_mode"] != cast_mode:
            fail(f"{owner}.cast_mode must match the story bible.")
        if item["secondary_protagonist_signature"].strip() != secondary_signature:
            fail(
                f"{owner}.secondary_protagonist_signature must match "
                "the story bible verbatim."
            )
        if item["scene_coverage"] != "full_frame_100_percent_story_scene":
            fail(f"{owner}.scene_coverage must be full_frame_100_percent_story_scene.")
        caption_text = item["caption_text"].strip()
        if not 4 <= nonspace(caption_text) <= 14:
            fail(f"{owner}.caption_text must contain 4-14 non-space characters.")
        if any(token in caption_text for token in ("。", "！", "？", "!", "?")):
            fail(f"{owner}.caption_text must be a compact scene cue, not a full sentence or slogan.")
        caption_key = re.sub(r"\s+", "", caption_text)
        if caption_key in caption_texts:
            fail(f"{owner}.caption_text must not repeat across the serial story.")
        caption_texts.add(caption_key)
        if item["caption_role"] not in {"event_hook", "inner_whisper", "object_clue", "time_echo"}:
            fail(f"{owner}.caption_role is invalid.")
        if item["caption_frame_position"] not in {"top_frame", "bottom_frame"}:
            fail(f"{owner}.caption_frame_position must be top_frame or bottom_frame.")
        if item["caption_frame_style"] != "cinematic_story_caption_frame":
            fail(f"{owner}.caption_frame_style must be cinematic_story_caption_frame.")
        if item["caption_rendering"] != "direct_exact_chinese_preferred_with_overlay_fallback":
            fail(f"{owner}.caption_rendering is invalid.")
        for retired_key in (
            "information_layer",
            "information_form",
            "information_visual_mode",
            "layout_ratio",
            "scene_position",
            "information_position",
        ):
            if retired_key in item:
                fail(f"{owner} must not contain retired information-layer field: {retired_key}.")
        if item["style_profile"] != SERIAL_ILLUSTRATION_STYLE:
            fail(f"{owner}.style_profile must be {SERIAL_ILLUSTRATION_STYLE}.")
        if item["palette_profile"] != SERIAL_PALETTE_PROFILE:
            fail(f"{owner}.palette_profile must be {SERIAL_PALETTE_PROFILE}.")
        phase = item["story_phase"]
        if phase not in phase_order:
            fail(f"{owner}.story_phase is invalid.")
        story_phases.append(phase)
        if item["beat_type"] not in beat_types:
            fail(f"{owner}.beat_type is invalid.")
        if item["transition_method"] not in transition_methods:
            fail(f"{owner}.transition_method is invalid.")
        sunny = item["sunny_expression"]
        smile_type = item["smile_type"]
        if sunny:
            sunny_count += 1
            if smile_type not in smiling_types:
                fail(f"{owner}.smile_type must be a natural smile when sunny_expression is true.")
        else:
            non_smiling_count += 1
            if smile_type not in thoughtful_types:
                fail(f"{owner}.smile_type must be calm_focus or quiet_reflection when not smiling.")
            if phase not in {"pressure", "descent", "low_point"}:
                fail(f"{owner} may omit a smile only during pressure, descent, or low_point.")
        if previous_smile_type and smile_type == previous_smile_type:
            fail(f"{owner}.smile_type must change from the previous panel.")
        smile_types_used.add(smile_type)
        previous_smile_type = smile_type
        expression_feature_tokens = ("眼", "眉", "嘴", "呼吸", "视线", "肩", "颈")
        sumei_expression = item["sumei_expression"]
        kaidi_expression = item["kaidi_expression"]
        for character_name, field_name, expression in (
            ("苏美", "sumei_expression", sumei_expression),
            ("凝香", "kaidi_expression", kaidi_expression),
        ):
            if character_name not in item_characters:
                if expression != "not_visible":
                    fail(f"{owner}.{field_name} must be not_visible when {character_name} is absent.")
                continue
            covered = sum(token in expression for token in expression_feature_tokens)
            if covered < 4:
                fail(
                    f"{owner}.{field_name} must describe at least four "
                    "of brows/eyes, mouth, breath, gaze, and shoulders/neck."
                )
        expression_pair = (
            re.sub(r"\s+", "", sumei_expression),
            re.sub(r"\s+", "", kaidi_expression),
        )
        if plan_lead_visibility == "both" and expression_pair[0] == expression_pair[1]:
            fail(f"{owner} must give Sumei and Ningxiang distinct responsive expressions.")
        if expression_pair in expression_pairs:
            fail(f"{owner} repeats a previous dual-character expression pair.")
        if previous_expression_pair == expression_pair:
            fail(f"{owner} must visibly change both-character expression staging from the previous panel.")
        expression_pairs.add(expression_pair)
        previous_expression_pair = expression_pair
        expression_relationship = item["character_expression_relationship"]
        if any(name not in expression_relationship for name in item_characters):
            fail(f"{owner}.character_expression_relationship must name every visible character.")
        micro_change = item["micro_expression_change"].strip()
        expression_link = item["expression_link_from_previous"].strip()
        if index == 1:
            if micro_change != "INITIAL_EXPRESSION" or expression_link != "SERIES_START":
                fail(
                    "The opening panel must use INITIAL_EXPRESSION and SERIES_START for its expression arc."
                )
        else:
            covered = sum(token in micro_change for token in expression_feature_tokens)
            if covered < 3 or nonspace(micro_change) < 18:
                fail(
                    f"{owner}.micro_expression_change must name at least three concrete facial/body changes."
                )
            micro_key = re.sub(r"\s+", "", micro_change)
            if micro_key in micro_expression_changes:
                fail(f"{owner}.micro_expression_change must be unique across the serial story.")
            micro_expression_changes.add(micro_key)
            if nonspace(expression_link) < 12:
                fail(f"{owner}.expression_link_from_previous must explain the emotional carryover.")
        if phase in {"opening", "turning", "rebound", "integration"} and not sunny:
            fail(f"{owner} must show a sunny expression during {phase}.")
        hope_level = item["hope_level"]
        if phase == "opening" and hope_level < 3:
            fail(f"{owner}.hope_level must be at least 3 in opening.")
        if phase == "turning" and hope_level < 3:
            fail(f"{owner}.hope_level must be at least 3 in turning.")
        if phase == "rebound" and hope_level < 4:
            fail(f"{owner}.hope_level must be at least 4 in rebound.")
        if phase == "integration" and hope_level != 5:
            fail(f"{owner}.hope_level must be 5 in integration.")
        action_key = re.sub(r"\s+", "", item["visible_action"])
        if action_key in visible_actions:
            fail("Each serial panel needs a distinct visible action.")
        visible_actions.add(action_key)
        dialogue_key = re.sub(r"\s+", "", item["nonverbal_dialogue"])
        if dialogue_key in nonverbal_dialogues:
            fail("Each serial panel needs a distinct nonverbal dialogue beat.")
        nonverbal_dialogues.add(dialogue_key)
        if len(item_characters) > 1:
            multi_character_count += 1

        token_in = item["continuity_token_in"].strip()
        token_out = item["continuity_token_out"].strip()
        if index == 1:
            if token_in != "SERIES_START":
                fail("The first panel continuity_token_in must be SERIES_START.")
            if item["previous_panel_callback"].strip() != "series_opening":
                fail("The first panel previous_panel_callback must be series_opening.")
        elif token_in != previous_out:
            fail(f"{owner}.continuity_token_in must match the previous panel output token.")
        if index == len(prompts):
            if token_out != "SERIES_END":
                fail("The final panel continuity_token_out must be SERIES_END.")
            if item["next_panel_hook"].strip() != "series_resolution":
                fail("The final panel next_panel_hook must be series_resolution.")
        elif token_out == "SERIES_END":
            fail("Only the final panel may use SERIES_END.")
        if token_out in out_tokens:
            fail("continuity_token_out values must be unique.")
        out_tokens.add(token_out)
        carry_set = {str(value).strip() for value in carry}
        if index > 1 and len(previous_carry & carry_set) < 2:
            fail(f"{owner} must share at least two carryover elements with the previous panel.")
        previous_out = token_out
        previous_carry = carry_set

        if motif_name not in item["recurring_motif_state"]:
            fail(f"{owner}.recurring_motif_state must name the story bible motif.")
        if item["text_policy"] != "story_caption_frame_only":
            fail(f"{owner}.text_policy must be story_caption_frame_only.")
        dominant_match = re.search(r"#[0-9A-Fa-f]{6}\b", item["dominant_color"])
        if not dominant_match or dominant_match.group(0).upper() not in palette_hexes:
            fail(f"{owner}.dominant_color must use a story-bible palette HEX.")
        supporting = require_list(
            item.get("supporting_colors"),
            f"{owner}.supporting_colors",
        )
        if not 2 <= len(supporting) <= 4 or any(
            not isinstance(value, str)
            or not re.search(r"#[0-9A-Fa-f]{6}\b", value)
            or re.search(r"#[0-9A-Fa-f]{6}\b", value).group(0).upper() not in palette_hexes
            for value in supporting
        ):
            fail(f"{owner}.supporting_colors must contain two to four story-bible HEX colors.")

        prompt = item["prompt"]
        for required in (
            "连环画",
            "成熟叙事插画",
            "彩色插画",
            "手绘笔触",
            "微3D",
            "阳光和希望",
            "明亮眼神",
            "禁止愁容满面",
            "禁止信息卡",
            "禁止写实摄影",
            "禁止真人写真",
            "禁止电影剧照",
            "禁止photorealistic",
            "禁止cinematic still",
            "100%全画幅场景",
            "胶片式叙事边框",
            "边框内准确中文",
            "除边框短句外画面无文字",
            "禁止非边框文字",
            SERIAL_ILLUSTRATION_STYLE,
            cast_mode,
            narrative_mode,
            "固定男女主角",
            "按剧情加入配角",
            "表情变化",
            "禁止统一表情",
            motif_name,
            token_in,
            token_out,
            item["facial_expression"],
            item["character_expression_relationship"],
            item["micro_expression_change"],
            item["expression_link_from_previous"],
            item["body_openness"],
            item["hope_signal"],
            item["character_blocking"],
            item["nonverbal_dialogue"],
            item["relationship_beat"],
            item["shared_action"],
            item["caption_text"],
            item["caption_role"],
            item["caption_frame_position"],
            item["caption_frame_style"],
            item["caption_rendering"],
        ):
            if required not in prompt:
                fail(f"{owner}.prompt must include serial illustration constraint: {required}.")
        for character_name in item_characters:
            if character_name not in prompt:
                fail(f"{owner}.prompt must name visible character: {character_name}.")
        if "苏美" in item_characters:
            for visible_detail in (signature, item["sumei_expression"]):
                if visible_detail not in prompt:
                    fail(f"{owner}.prompt must include Sumei's visible continuity and expression.")
        if "凝香" in item_characters:
            for visible_detail in (secondary_signature, item["kaidi_expression"]):
                if visible_detail not in prompt:
                    fail(f"{owner}.prompt must include Ningxiang's visible continuity and expression.")
        for character_name in set(item_characters) & set(supporting_by_name):
            appearance = require_text(
                supporting_by_name[character_name],
                "appearance_boundary",
                f"supporting_cast.{character_name}",
            )
            if appearance not in prompt:
                fail(f"{owner}.prompt must include {character_name}'s appearance boundary.")
        expression_marker = "自然微笑" if sunny else "平静清醒"
        if expression_marker not in prompt:
            fail(f"{owner}.prompt must include expression marker: {expression_marker}.")
        if "愁容" not in item["negative_constraints"]:
            fail(f"{owner}.negative_constraints must explicitly forbid gloomy facial expressions.")
        if "统一表情" not in item["negative_constraints"]:
            fail(f"{owner}.negative_constraints must explicitly forbid flat repeated expressions.")
        if "非边框文字" not in item["negative_constraints"]:
            fail(f"{owner}.negative_constraints must explicitly forbid text outside the caption frame.")
        if "乱码" not in item["negative_constraints"]:
            fail(f"{owner}.negative_constraints must explicitly forbid garbled text.")
        if "信息卡" not in item["negative_constraints"]:
            fail(f"{owner}.negative_constraints must explicitly forbid information cards.")
        for negative in (
            "写实摄影", "真人写真", "电影剧照",
            "photorealistic", "cinematic still",
        ):
            if negative not in item["negative_constraints"]:
                fail(f"{owner}.negative_constraints must explicitly forbid {negative}.")
        for color in [item["dominant_color"], *supporting]:
            color_match = re.search(r"#[0-9A-Fa-f]{6}\b", color)
            if color_match and color_match.group(0).upper() not in prompt.upper():
                fail(f"{owner}.prompt must use panel color {color_match.group(0)}.")
        for forbidden in (
            "micro_3d_info_cards",
            "scene_30_info_70",
            "上三分之一",
            "下三分之二",
            "白色信息卡",
        ):
            if forbidden in prompt:
                fail(f"{owner}.prompt still contains retired split-layout language: {forbidden}.")
        if nonspace(prompt) <= 900:
            fail(f"{owner}.prompt must exceed 900 non-whitespace characters.")

    if len(smile_types_used) < 3:
        fail("The serial story needs at least three distinct smile or calm-focus expression types.")
    phase_values = [phase_order[value] for value in story_phases]
    if phase_values != sorted(phase_values):
        fail("Serial story phases must progress without moving backward.")
    if story_phases[0] != "opening" or story_phases[-1] != "integration":
        fail("The serial story must begin with opening and end with integration.")
    if not any(value in {"pressure", "descent", "low_point"} for value in story_phases):
        fail("The serial story needs a visible pressure or descent phase.")
    if "turning" not in story_phases or "rebound" not in story_phases:
        fail("The serial story must include both turning and rebound phases.")
    required_sunny = (len(prompts) * 7 + 9) // 10
    if sunny_count < required_sunny:
        fail(f"At least 70% of serial panels must be sunny; need {required_sunny}.")
    if non_smiling_count > max_non_smiling:
        fail("The serial story exceeds max_non_smiling_panels.")

    write_wechat_html(topic_dir, quiet=True)
    receipt = write_receipt(
        topic_dir,
        5,
        {
            "images": len(prompts),
            "serial_story_panels": len(prompts),
            "visual_mode": SERIAL_ILLUSTRATION_STYLE,
            "palette_profile": SERIAL_PALETTE_PROFILE,
            "recurring_motif": motif_name,
            "cast_mode": cast_mode,
            "narrative_mode": narrative_mode,
            "multi_character_panels": multi_character_count,
            "sunny_panels": sunny_count,
            "non_smiling_panels": non_smiling_count,
            "distinct_expression_types": len(smile_types_used),
            "distinct_expression_pairs": len(expression_pairs),
            "caption_frames": len(prompts),
            "image_prompt_version": IMAGE_PROMPT_VERSION,
        },
    )
    return {
        "images": len(prompts),
        "serial_story_panels": len(prompts),
        "visual_mode": SERIAL_ILLUSTRATION_STYLE,
        "palette_profile": SERIAL_PALETTE_PROFILE,
        "recurring_motif": motif_name,
        "cast_mode": cast_mode,
        "narrative_mode": narrative_mode,
        "multi_character_panels": multi_character_count,
        "sunny_panels": sunny_count,
        "non_smiling_panels": non_smiling_count,
        "distinct_expression_types": len(smile_types_used),
        "distinct_expression_pairs": len(expression_pairs),
        "caption_frames": len(prompts),
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


EVENT_TITLE_ACTION_TOKENS = (
    "收到", "发来", "打来", "响", "亮", "删", "按", "输入", "发送", "回复",
    "拿", "放", "关", "开", "停", "等", "走", "回", "说", "问", "递", "看",
    "签", "转", "推", "拉", "坐", "站", "离开", "沉默", "拨", "挂", "抬头",
)
EVENT_TITLE_CURIOSITY_TOKENS = (
    "？", "?", "为什么", "却", "还没", "没有", "迟迟", "突然", "刚要", "正要",
    "直到", "那天", "这次", "最后", "之后", "以后", "时", "后", "第三次",
)
ASSERTIVE_TITLE_PATTERNS = (
    r"人到中年",
    r"中年以后",
    r"请(?:主动)?",
    r"学会.+才",
    r"只有.+才",
    r"真正的.+是",
    r"真正.+才",
    r"不是.+而是",
    r"越.+越",
    r"本质(?:上)?(?:是|在于)",
    r"必须",
    r"应该",
)


def validate_eventized_headline(
    headline: str,
    owner: str,
    *,
    minimum_chars: int,
    maximum_chars: int,
) -> None:
    length = nonspace(headline)
    if not minimum_chars <= length <= maximum_chars:
        fail(
            f"{owner} must contain {minimum_chars}-{maximum_chars} non-space characters."
        )
    if any(re.search(pattern, headline) for pattern in ASSERTIVE_TITLE_PATTERNS):
        fail(f"{owner} is an assertion or advice; rewrite it as an unfinished event hook.")
    if not any(token in headline for token in EVENT_TITLE_ACTION_TOKENS):
        fail(f"{owner} must include a visible action or event word.")
    if not any(token in headline for token in EVENT_TITLE_CURIOSITY_TOKENS):
        fail(f"{owner} must preserve an unresolved curiosity signal.")


def validate_video_cover_prompts(
    topic_dir: Path,
    video_headline: str,
    cover_cast: list[str],
    cover_character_signatures: dict[str, str],
) -> int:
    rows = load_jsonl(topic_dir / "assets" / "video_cover_prompts.jsonl")
    required_rows = {
        "微信视频号横版": ("1920x1080", "16:9"),
        "今日头条横版": ("1920x1080", "16:9"),
        "B站横版": ("1920x1080", "16:9"),
    }
    seen: set[tuple[str, str]] = set()
    platforms: set[str] = set()
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
        for token in (
            "完整单场景", "自然标题留白", "成熟叙事插画", "事件", "未完成", "人物动作",
            "胶片式叙事边框", "标题不在边框内",
        ):
            if token not in joined_points:
                fail(f"{owner}.core_prompt_points must include: {token}")
        for token in (
            "完整单场景",
            "自然负空间",
            "事件化好奇引子",
            "尚未完成",
            "标题",
            "人物动作",
            "表情关系",
            "成熟叙事插画",
            "手绘笔触",
            "微3D",
            "禁止写实摄影",
            "禁止真人写真",
            "禁止电影剧照",
            "禁止photorealistic",
            "禁止cinematic still",
            COVER_ILLUSTRATION_STYLE,
            "禁止硬分栏",
            "禁止比例切分",
            "禁止信息卡",
            "胶片式叙事边框",
            "标题不在边框内",
            "禁止标题写在边框内",
            "禁止边框信息卡",
            video_headline,
        ):
            if token not in prompt:
                fail(f"{owner} must carry the integrated novel-scene cover contract: {token}")
        for character_name in cover_cast:
            if character_name not in prompt:
                fail(f"{owner}.prompt must preserve cover character: {character_name}")
            if cover_character_signatures[character_name] not in prompt:
                fail(f"{owner}.prompt must preserve {character_name}'s cover signature.")
        for retired in ("50:50", "70%", "30%", "scene_70_title_30", "dual_character_story_scene_with_title"):
            if retired in prompt:
                fail(f"{owner}.prompt contains retired split-cover language: {retired}")
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
    cast = load_cast_bible()
    pack = require_object(
        load_json(topic_dir / "research" / "source_pack.json"),
        "source_pack.json",
    )
    validate_profile(pack)
    meaning = require_object(pack.get("meaning_design"), "source_pack.meaning_design")
    hidden_meaning = require_text(meaning, "hidden_meaning", "meaning_design")
    forbidden_statement = require_text(
        meaning,
        "forbidden_direct_statement",
        "meaning_design",
    )

    def reject_revealed_meaning(headline: str, owner: str) -> None:
        normalized_headline = re.sub(r"\s+", "", headline)
        for label, value in (
            ("hidden meaning", hidden_meaning),
            ("forbidden direct statement", forbidden_statement),
        ):
            normalized_value = re.sub(r"\s+", "", value)
            if normalized_value and normalized_value in normalized_headline:
                fail(
                    f"{owner} reveals the {label}; use an eventized unresolved "
                    "moment instead of announcing the story's answer."
                )

    profile = require_object(pack.get("article_profile"), "source_pack.article_profile")
    narrative_mode = require_text(profile, "narrative_mode", "article_profile")
    narrative_contract = require_object(
        profile.get("narrative_contract"),
        "article_profile.narrative_contract",
    )
    blueprint = require_object(
        load_json(topic_dir / "research" / "novel_blueprint.json"),
        "novel_blueprint.json",
    )
    supporting_cast = require_list(
        blueprint.get("supporting_cast"),
        "novel_blueprint.supporting_cast",
        allow_empty=True,
    )
    supporting_by_name = {
        require_text(item, "name", f"supporting_cast[{index}]"): item
        for index, item in enumerate(supporting_cast)
    }
    allowed_cover_characters = {"苏美", "凝香"} | set(supporting_by_name)
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
        validate_eventized_headline(
            title,
            f"{owner}.title",
            minimum_chars=15,
            maximum_chars=32,
        )
        reject_revealed_meaning(title, f"{owner}.title")
        titles.append(title)
        for key in (
            "reader_hook",
            "psychology",
            "promise",
            "dignity_and_responsibility",
            "share_trigger",
            "event_snapshot",
            "curiosity_gap",
            "unresolved_state",
            "assertion_avoidance_check",
            "cover_moment",
            "core_dialogue_or_story",
            "visual_metaphor",
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
        "event_immediacy": 8,
        "tension": 7,
        "curiosity": 7,
        "unfinished_tension": 8,
        "fidelity": 8,
        "non_exploitative_tension": 8,
        "character_dignity": 8,
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
    if total_score < 80:
        fail("The selected title must score at least 80/100.")
    for key in ("selection_reason", "title_cover_link"):
        require_text(package, key, "title_cover_package")
    entry = require_object(package.get("entry_contract"), "title_cover_package.entry_contract")
    for key in (
        "click_core", "fixed_leads", "series_label", "human_protagonist", "familiar_scene",
        "core_dialogue_or_story", "active_metaphor",
        "metaphor_mapping", "unresolved_question", "story_payoff",
        "headline_type", "headline_event", "headline_unfinished_state", "assertion_avoidance",
        "article_headline", "video_headline", "consistency_rule",
    ):
        require_text(entry, key, "entry_contract")
    if entry["fixed_leads"] != "苏美与凝香":
        fail("entry_contract.fixed_leads must be 苏美与凝香.")
    cover_cast = [
        str(value).strip()
        for value in require_list(entry.get("cover_cast"), "entry_contract.cover_cast")
        if isinstance(value, str) and value.strip()
    ]
    if not cover_cast or len(cover_cast) != len(set(cover_cast)):
        fail("entry_contract.cover_cast must contain unique character names.")
    unknown_cover_cast = set(cover_cast) - allowed_cover_characters
    if unknown_cover_cast:
        fail(f"entry_contract.cover_cast contains unknown characters: {sorted(unknown_cover_cast)}")
    if not {"苏美", "凝香"} & set(cover_cast):
        fail("entry_contract.cover_cast must include at least one fixed lead.")
    if entry["series_label"] != cast["series_label"]:
        fail("entry_contract.series_label must match cast-bible.json.")
    if entry["headline_type"] != "eventized_curiosity_hook":
        fail("entry_contract.headline_type must be eventized_curiosity_hook.")
    if entry["article_headline"].strip() != selected:
        fail("entry_contract.article_headline must match selected_title.")
    validate_eventized_headline(
        entry["video_headline"],
        "entry_contract.video_headline",
        minimum_chars=8,
        maximum_chars=18,
    )
    reject_revealed_meaning(
        entry["video_headline"],
        "entry_contract.video_headline",
    )
    markdown = (topic_dir / "article" / "final_article.md").read_text(encoding="utf-8")
    title_match = re.search(r"(?m)^#\s+(.+?)\s*$", markdown)
    if not title_match or title_match.group(1).strip() != selected:
        fail("The Markdown H1 must match selected_title.")
    cover = require_object(package.get("cover_prompt"), "cover_prompt")
    for key in (
        "aspect_ratio",
        "narrative_mode",
        "cover_layout",
        "style_profile",
        "palette_profile",
        "accent_color",
        "episode_core",
        "core_dialogue_or_story",
        "scene_reconstruction",
        "lead_presence",
        "character_blocking",
        "frozen_story_moment",
        "expression_relationship",
        "unresolved_visual_question",
        "screen_frame_style",
        "screen_frame_coverage",
        "frame_text_policy",
        "title_integration",
        "natural_negative_space",
        "headline_text",
        "series_label",
        "lighting_plan",
        "crop_survival_plan",
        "one_second_read",
        "thumbnail_test",
        "negative_constraints",
        "prompt",
    ):
        require_text(cover, key, "cover_prompt")
    if cover["aspect_ratio"] != "2.35:1":
        fail("cover_prompt.aspect_ratio must be 2.35:1.")
    if cover["narrative_mode"] != narrative_mode:
        fail("cover_prompt.narrative_mode must match article_profile.narrative_mode.")
    if cover["cover_layout"] != "single_full_frame_novel_scene_with_integrated_title":
        fail("cover_prompt.cover_layout must be single_full_frame_novel_scene_with_integrated_title.")
    if cover["screen_frame_style"] != "cinematic_story_frame_no_caption":
        fail("cover_prompt.screen_frame_style must be cinematic_story_frame_no_caption.")
    if cover["screen_frame_coverage"] != "6%-10% narrow integrated border":
        fail("cover_prompt.screen_frame_coverage is invalid.")
    if cover["frame_text_policy"] != "title_must_not_be_inside_frame":
        fail("cover_prompt.frame_text_policy must keep the title outside the frame.")
    if cover["style_profile"] != COVER_ILLUSTRATION_STYLE:
        fail(f"cover_prompt.style_profile must be {COVER_ILLUSTRATION_STYLE}.")
    if cover["palette_profile"] != VISUAL_PALETTE_PROFILE:
        fail(
            "cover_prompt.palette_profile must be "
            f"{VISUAL_PALETTE_PROFILE}."
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
    expected_sumei = require_text(cast["sumei"], "appearance_signature", "cast-bible.sumei")
    expected_kaidi = require_text(cast["kaidi"], "appearance_signature", "cast-bible.kaidi")
    if cover["episode_core"] != narrative_contract["episode_core"]:
        fail("cover_prompt.episode_core must match article_profile.narrative_contract.")
    if cover["core_dialogue_or_story"] != entry["core_dialogue_or_story"]:
        fail("cover_prompt.core_dialogue_or_story must match entry_contract.")
    if cover["series_label"] != cast["series_label"]:
        fail("cover_prompt.series_label must match cast-bible.json.")
    if cover["headline_text"] != selected:
        fail("cover_prompt.headline_text must match selected_title.")
    characters_visible = [
        str(value).strip()
        for value in require_list(cover.get("characters_visible"), "cover_prompt.characters_visible")
        if isinstance(value, str) and value.strip()
    ]
    if characters_visible != cover_cast:
        fail("cover_prompt.characters_visible must exactly match entry_contract.cover_cast.")
    expected_lead_presence = (
        "both" if {"苏美", "凝香"} <= set(characters_visible)
        else "sumei" if "苏美" in characters_visible
        else "ningxiang"
    )
    if cover["lead_presence"] != expected_lead_presence:
        fail(f"cover_prompt.lead_presence must be {expected_lead_presence}.")
    signature_entries = require_list(
        cover.get("visible_character_signatures"),
        "cover_prompt.visible_character_signatures",
    )
    if len(signature_entries) != len(characters_visible):
        fail("visible_character_signatures must contain one entry per visible character.")
    prompt = cover["prompt"]
    cover_character_signatures: dict[str, str] = {}
    for index, (value, character_name) in enumerate(zip(signature_entries, characters_visible)):
        owner = f"cover_prompt.visible_character_signatures[{index}]"
        signature_entry = require_object(value, owner)
        if require_text(signature_entry, "name", owner) != character_name:
            fail(f"{owner}.name must follow characters_visible order.")
        character_signature = require_text(signature_entry, "signature", owner)
        cover_character_signatures[character_name] = character_signature
        performance = require_text(signature_entry, "performance", owner)
        if character_name == "苏美" and character_signature != expected_sumei:
            fail(f"{owner}.signature must match Sumei in cast-bible.json verbatim.")
        if character_name == "凝香" and character_signature != expected_kaidi:
            fail(f"{owner}.signature must match Ningxiang in cast-bible.json verbatim.")
        if character_name in supporting_by_name:
            appearance = require_text(
                supporting_by_name[character_name],
                "appearance_boundary",
                f"supporting_cast.{character_name}",
            )
            if appearance not in character_signature:
                fail(f"{owner}.signature must preserve the supporting character appearance boundary.")
        if sum(token in performance for token in ("眉", "眼", "嘴角", "呼吸", "视线", "肩")) < 4:
            fail(f"{owner}.performance must include at least four micro-expression/body domains.")
        for required in (character_name, character_signature, performance):
            if required not in prompt:
                fail(f"cover_prompt.prompt must include visible character detail: {required}")
    for token in (
        "完整单场景",
        "自然负空间",
        "标题",
        "事件化好奇引子",
        "尚未完成",
        "场景重现",
        "人物动作",
        "表情关系",
        "胶片式叙事边框",
        "标题不在边框内",
        "光线",
        "裁切",
        "成熟叙事插画",
        "手绘笔触",
        "微3D",
        "禁止写实摄影",
        "禁止真人写真",
        "禁止电影剧照",
        "禁止photorealistic",
        "禁止cinematic still",
        COVER_ILLUSTRATION_STYLE,
        selected,
        cover["frozen_story_moment"],
        cover["scene_reconstruction"],
        cover["expression_relationship"],
        cover["title_integration"],
        cover["natural_negative_space"],
        cover["unresolved_visual_question"],
        cover["screen_frame_style"],
        cover["screen_frame_coverage"],
        cover["frame_text_policy"],
        cover["negative_constraints"],
    ):
        if token not in prompt:
            fail(f"cover_prompt.prompt must include integrated novel-scene constraint: {token}")
    for required_negative in (
        "硬分栏", "比例切分", "信息卡", "标题板", "边框信息卡", "标题写在边框内", "拼贴",
        "写实摄影", "真人写真", "电影剧照", "photorealistic", "cinematic still",
    ):
        if required_negative not in cover["negative_constraints"]:
            fail(f"cover_prompt.negative_constraints must forbid: {required_negative}")
    for retired in (
        "50:50", "70%", "30%", "scene_70_title_30", "dual_character_story_scene_with_title",
    ):
        if retired in prompt:
            fail(f"cover_prompt.prompt contains retired split-cover language: {retired}")
    if nonspace(prompt) <= 700:
        fail("cover_prompt.prompt must exceed 700 non-whitespace characters.")
    video_covers = validate_video_cover_prompts(
        topic_dir,
        entry["video_headline"].strip(),
        cover_cast,
        cover_character_signatures,
    )
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
            "video_covers": video_covers,
        },
    )
    return {
        "title_candidates": len(candidates),
        "selected_title": selected,
        "title_score": total_score,
        "digest_chars": digest_chars,
        "cover_prompt_version": COVER_PROMPT_VERSION,
        "video_covers": video_covers,
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
    load_cast_bible()
    blueprint = require_object(
        load_json(topic_dir / "research" / "novel_blueprint.json"),
        "novel_blueprint.json",
    )
    supporting_cast = require_list(
        blueprint.get("supporting_cast"),
        "novel_blueprint.supporting_cast",
        allow_empty=True,
    )
    allowed_speakers = {"narrator": "旁白", "sumei": "苏美", "kaidi": "凝香"}
    for index, item in enumerate(supporting_cast):
        speaker_id = require_text(item, "id", f"supporting_cast[{index}]").lower()
        allowed_speakers[speaker_id] = require_text(item, "name", f"supporting_cast[{index}]")
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
    merged_audio_paths: dict[str, Path] = {}
    turn_audio_paths: dict[tuple[str, int], Path] = {}
    total_characters = 0
    total_turns = 0
    used_speaker_ids: set[str] = set()
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
            "performance_arc",
            "transition_in",
            "transition_out",
        ):
            require_text(segment, key, owner)
        turns = require_list(segment.get("turns"), f"{owner}.turns")
        if not 1 <= len(turns) <= 6:
            fail(f"{owner}.turns must contain one to six narration or character turns.")
        speakers_in_order: list[str] = []
        for turn_index, value in enumerate(turns, start=1):
            turn_owner = f"{owner}.turns[{turn_index - 1}]"
            turn = require_object(value, turn_owner)
            if turn.get("turn_order") != turn_index:
                fail(f"{turn_owner}.turn_order must equal {turn_index}.")
            speaker_id = require_text(turn, "speaker_id", turn_owner)
            expected_name = allowed_speakers.get(speaker_id)
            if expected_name is None:
                fail(f"{turn_owner}.speaker_id is absent from the novel cast.")
            if require_text(turn, "speaker_name", turn_owner) != expected_name:
                fail(f"{turn_owner}.speaker_name must match speaker_id.")
            speakers_in_order.append(speaker_id)
            used_speaker_ids.add(speaker_id)
            for key in (
                "voice_direction",
                "facial_expression",
                "body_action",
                "subtext",
            ):
                require_text(turn, key, turn_owner)
            spoken_text = require_text(turn, "spoken_text", turn_owner)
            sentence_count = len(
                [part for part in re.split(r"[。！？!?…]+", spoken_text) if nonspace(part)]
            )
            if not 1 <= sentence_count <= 3:
                fail(f"{turn_owner}.spoken_text must contain one to three sentences.")
            characters = nonspace(spoken_text)
            if not 20 <= characters <= 140:
                fail(f"{turn_owner}.spoken_text must contain 20-140 non-space characters.")
            total_characters += characters
            total_turns += 1
            expected_turn_audio = (
                f"video/audio/{expected_id}_{turn_index:02d}_{speaker_id}.mp3"
            )
            if require_text(turn, "audio_file", turn_owner) != expected_turn_audio:
                fail(f"{turn_owner}.audio_file must be {expected_turn_audio}.")
            turn_audio = topic_dir / expected_turn_audio
            if not turn_audio.is_file() or turn_audio.stat().st_size < 1024:
                fail(f"Missing or empty character TTS audio: {turn_audio}")
            turn_audio_paths[(expected_id, turn_index)] = turn_audio
        if any(
            speakers_in_order[position] == speakers_in_order[position + 1] == speakers_in_order[position + 2]
            for position in range(max(0, len(speakers_in_order) - 2))
        ):
            fail(f"{owner}.turns cannot give the same speaker three consecutive turns.")
        expected_merged = f"video/audio/{expected_id}.mp3"
        if require_text(segment, "merged_audio_file", owner) != expected_merged:
            fail(f"{owner}.merged_audio_file must be {expected_merged}.")
        merged_audio = topic_dir / expected_merged
        if not merged_audio.is_file() or merged_audio.stat().st_size < 1024:
            fail(f"Missing or empty merged novel-scene audio: {merged_audio}")
        merged_audio_paths[expected_id] = merged_audio

    manifest = require_object(
        load_json(topic_dir / "video" / "audio_manifest.json"),
        "audio_manifest.json",
    )
    if require_text(manifest, "tts_engine", "audio_manifest") != "edge_tts":
        fail("audio_manifest.tts_engine must be edge_tts.")
    voices = require_object(manifest.get("voices"), "audio_manifest.voices")
    if set(voices) != used_speaker_ids:
        fail("audio_manifest.voices must contain exactly the speakers used in narration segments.")
    for speaker_id in sorted(used_speaker_ids):
        voice = require_object(voices.get(speaker_id), f"audio_manifest.voices.{speaker_id}")
        for key in ("name", "rate", "volume", "pitch"):
            require_text(voice, key, f"audio_manifest.voices.{speaker_id}")
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
        if require_text(item, "merged_audio_file", owner) != expected_audio:
            fail(f"{owner}.merged_audio_file must be {expected_audio}.")
        if require_text(item, "status", owner) != "success":
            fail(f"{owner}.status must be success.")
        source_turns = require_list(segments[index - 1].get("turns"), f"narration_segments[{index - 1}].turns")
        manifest_turns = require_list(item.get("turns"), f"{owner}.turns")
        if len(manifest_turns) != len(source_turns):
            fail(f"{owner}.turns must match its narration segment.")
        for turn_index, (source_turn, manifest_value) in enumerate(
            zip(source_turns, manifest_turns), start=1
        ):
            turn_owner = f"{owner}.turns[{turn_index - 1}]"
            manifest_turn = require_object(manifest_value, turn_owner)
            speaker_id = require_text(source_turn, "speaker_id", "source_turn")
            if manifest_turn.get("turn_order") != turn_index:
                fail(f"{turn_owner}.turn_order must equal {turn_index}.")
            if require_text(manifest_turn, "speaker_id", turn_owner) != speaker_id:
                fail(f"{turn_owner}.speaker_id must match narration_segments.jsonl.")
            expected_turn_audio = f"video/audio/{expected_id}_{turn_index:02d}_{speaker_id}.mp3"
            if require_text(manifest_turn, "audio_file", turn_owner) != expected_turn_audio:
                fail(f"{turn_owner}.audio_file must be {expected_turn_audio}.")
            declared_turn_duration = require_positive_number(
                manifest_turn.get("duration_seconds"),
                f"{turn_owner}.duration_seconds",
            )
            measured_turn = probe_audio_duration(turn_audio_paths[(expected_id, turn_index)])
            if measured_turn is not None and abs(declared_turn_duration - measured_turn) > max(
                1.0, measured_turn * 0.03
            ):
                fail(f"{turn_owner}.duration_seconds does not match its MP3.")
        declared_duration = require_positive_number(
            item.get("duration_seconds"), f"{owner}.duration_seconds"
        )
        measured_duration = probe_audio_duration(merged_audio_paths[expected_id])
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
        "turns": total_turns,
        "characters": total_characters,
        "voices": sorted(used_speaker_ids),
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
    parser = argparse.ArgumentParser(description="Validate a novel-expert stage.")
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
