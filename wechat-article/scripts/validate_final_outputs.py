#!/usr/bin/env python3
"""Validate deterministic Stage 4 article and HTML requirements."""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from markdown_to_wechat_html import parse_blocks, write_wechat_html
from validation_lib import (
    MIN_QUOTE_CHARS,
    STAGE1_RECEIPT,
    STAGE2_RECEIPT,
    STAGE3_RECEIPT,
    fail,
    has_quantitative_signal,
    load_json,
    markdown_shape,
    nonspace_len,
    normalize_evidence_text,
    reject_search_snapshot,
    require_list,
    require_object,
    require_receipt,
    require_string,
    resolve_topic_dir,
    section_length_stats,
    validate_numeric_claims,
    validate_article_profile,
    article_route_key,
    validate_spark_development,
)


MIN_ARTICLE_SANITY_CHARS = 1800
MIN_MAJOR_SECTIONS = 3
MAX_MAJOR_SECTIONS = 9
DATA_MARKER_RE = re.compile(
    r"^<!--\s*DATA:(N\d{2,}(?:\s*,\s*N\d{2,})*)\s*-->$",
    flags=re.IGNORECASE,
)
USER_MARKER_RE = re.compile(
    r"^<!--\s*USER:(U\d{2,}(?:\s*,\s*U\d{2,})*)\s*-->$",
    flags=re.IGNORECASE,
)
NON_CONTENT_BLOCK_RE = re.compile(
    r"^(?:#{1,6}\s+|<!--\s*(?:DESCENT:|SPARK:|REBOUND|IMAGE:)|"
    r"\[IMAGE_PLACEHOLDER:|[-*_]{3,}\s*$)",
    flags=re.IGNORECASE,
)
ANY_DATA_COMMENT_RE = re.compile(
    r"<!--\s*DATA:[^>]*-->",
    flags=re.IGNORECASE,
)
ANY_CONSTRUCTION_COMMENT_RE = re.compile(
    r"<!--\s*(?:DATA:[^>]*|USER:[^>]*|DESCENT:[^>]*|SPARK:[^>]*|REBOUND|IMAGE:[^>]*)\s*-->",
    flags=re.IGNORECASE,
)
FOOTNOTE_REFERENCE_RE = re.compile(r"\[\^[^\]\n]+\]")
FOOTNOTE_DEFINITION_RE = re.compile(r"(?m)^\s*\[\^[^\]\n]+\]:")


def source_path(topic_dir: Path, value: str, owner: str) -> Path:
    raw_root = (topic_dir / "research" / "raw_pages").resolve()
    path = Path(value)
    if not path.is_absolute():
        path = topic_dir / path
    path = path.resolve()
    try:
        path.relative_to(raw_root)
    except ValueError:
        fail(f"{owner} must point inside {raw_root}: {path}")
    if not path.is_file():
        fail(f"{owner} does not exist: {path}")
    return path


def host_of(url: str) -> str:
    return (urlparse(url).netloc or "").lower().removeprefix("www.")


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


def validate_article_numeric_markers(
    final: str,
    numeric_claims: dict[str, dict[str, object]],
    user_material_ids: set[str],
) -> int:
    """Require every publishable quantitative block to bind to verified ledger wording."""
    for marker in ANY_DATA_COMMENT_RE.findall(final):
        if not DATA_MARKER_RE.fullmatch(marker.strip()):
            fail(
                "final_article.md DATA markers may reference numeric ledger IDs only "
                "(for example <!-- DATA:N01 -->); O/M/W/P IDs are forbidden."
            )
    for line in final.splitlines():
        markers = ANY_CONSTRUCTION_COMMENT_RE.findall(line)
        if markers and line.strip() not in {marker.strip() for marker in markers}:
            fail(
                "Construction markers must occupy their own line and cannot be "
                "attached to visible prose."
            )
    scrubbed_lines: list[str] = []
    in_code = False
    fence_char = ""
    fence_len = 0
    for line in final.splitlines():
        stripped = line.strip()
        if in_code:
            if re.fullmatch(rf"{re.escape(fence_char)}{{{fence_len},}}\s*", stripped):
                in_code = False
            continue
        fence = re.fullmatch(r"(`{3,}|~{3,})(?:.*)", stripped)
        if fence:
            token = fence.group(1)
            in_code = True
            fence_char = token[0]
            fence_len = len(token)
            continue
        scrubbed_lines.append(line)

    blocks = [
        block.strip()
        for block in re.split(r"\n\s*\n", "\n".join(scrubbed_lines))
        if block.strip()
    ]
    pending_ids: list[str] | None = None
    pending_user_ids: list[str] | None = None
    checked_blocks = 0
    for block in blocks:
        marker = DATA_MARKER_RE.fullmatch(block)
        if marker:
            if pending_ids is not None:
                fail("A DATA marker must directly precede one quantitative content block.")
            pending_ids = [
                value.strip().upper() for value in marker.group(1).split(",")
            ]
            unknown = sorted(set(pending_ids) - set(numeric_claims))
            if unknown:
                fail("final_article.md DATA marker contains unknown IDs: " + ", ".join(unknown))
            continue
        user_marker = USER_MARKER_RE.fullmatch(block)
        if user_marker:
            if pending_user_ids is not None or pending_ids is not None:
                fail("A USER marker must directly precede one personal narrative block.")
            pending_user_ids = [
                value.strip().upper() for value in user_marker.group(1).split(",")
            ]
            unknown = sorted(set(pending_user_ids) - user_material_ids)
            if unknown:
                fail("final_article.md USER marker contains unknown IDs: " + ", ".join(unknown))
            continue

        if NON_CONTENT_BLOCK_RE.match(block):
            if pending_ids is not None or pending_user_ids is not None:
                fail("A DATA or USER marker cannot point to a heading, image marker or construction marker.")
            continue

        quantitative = has_quantitative_signal(block)
        if quantitative and not pending_ids and not pending_user_ids:
            excerpt = re.sub(r"\s+", " ", block)[:100]
            fail(
                "final_article.md contains an unverified quantitative block. "
                f"Add a checked DATA marker before it: {excerpt}"
            )
        if pending_ids and not quantitative:
            fail("A DATA marker must directly precede a block containing a factual figure.")
        if pending_ids:
            normalized_block = normalize_numeric_text(block)
            for claim_id in pending_ids:
                claim = numeric_claims[claim_id]
                allowed = str(claim["allowed_wording"]).strip().lower()
                if allowed == "omit":
                    fail(f"final_article.md uses {claim_id}, but that figure must be omitted.")
                publish_text = normalize_numeric_text(str(claim["publish_text"]))
                if publish_text not in normalized_block:
                    fail(
                        f"final_article.md block marked {claim_id} does not contain its "
                        f"verified publish_text: {claim['publish_text']}"
                    )
            checked_blocks += 1
            pending_ids = None
        if pending_user_ids is not None:
            pending_user_ids = None
    if pending_ids is not None:
        fail("final_article.md ends with a DATA marker that has no supported block.")
    if pending_user_ids is not None:
        fail("final_article.md ends with a USER marker that has no supported block.")
    return checked_blocks


def validate_article_spark_marker(
    final: str,
    spark_id: str,
    publish_thesis: str,
    last_descent_start: int,
    rebound_start: int,
) -> None:
    spark_markers = list(
        re.finditer(r"<!--\s*SPARK:(S\d+)\s*-->", final, flags=re.IGNORECASE)
    )
    if len(spark_markers) != 1:
        fail("final_article.md must contain exactly one <!-- SPARK:SXX --> marker.")
    spark_marker = spark_markers[0]
    if spark_marker.group(1).upper() != spark_id:
        fail("final_article.md Spark marker must match spark_verdict.spark_id.")
    if not last_descent_start < spark_marker.start() < rebound_start:
        fail(
            "final_article.md Spark marker must appear after the deepest descent "
            "and before REBOUND."
        )
    after_spark = final[spark_marker.end():]
    thesis_block_match = re.match(
        r"\s*\n\s*\n([^\n](?:.*?))(?=\n\s*\n|\Z)",
        after_spark,
        re.DOTALL,
    )
    if not thesis_block_match:
        fail("final_article.md Spark marker must directly precede the thesis paragraph.")
    thesis_block = thesis_block_match.group(1).strip()
    if thesis_block.startswith(("#", "<!--", "[IMAGE_PLACEHOLDER:")):
        fail("final_article.md Spark marker must directly precede a substantive paragraph.")
    normalized_thesis = re.sub(r"[\s*_`]+", "", publish_thesis)
    normalized_block = re.sub(r"[\s*_`]+", "", thesis_block)
    if normalized_thesis not in normalized_block:
        fail(
            "The paragraph after the Spark marker must contain "
            "spark_verdict.publish_thesis verbatim."
        )


def validate_insight_research(
    topic_dir: Path,
) -> tuple[int, int, dict[str, dict[str, object]], set[str], dict[str, object], str, str]:
    pack = load_json(topic_dir / "research" / "source_pack.json")
    if not isinstance(pack, dict):
        fail("source_pack.json must be an object.")
    article_profile = validate_article_profile(pack)
    numeric_claims = validate_numeric_claims(topic_dir, pack)
    user_materials = pack.get("user_materials", [])
    if not isinstance(user_materials, list):
        fail("source_pack.json.user_materials must be a list when present.")
    user_material_ids = {
        str(material.get("id") or "").strip().upper()
        for material in user_materials
        if isinstance(material, dict) and str(material.get("id") or "").strip()
    }
    if len(user_material_ids) != len(user_materials) or any(
        not re.fullmatch(r"U\d{2,}", value) for value in user_material_ids
    ):
        fail("source_pack.json.user_materials must contain unique U01-style IDs.")
    mechanism_ids = {
        str(card.get("id") or "").strip().upper()
        for card in pack.get("mechanism_cards", [])
        if isinstance(card, dict)
    }
    spine = pack.get("descent_spine")
    if not isinstance(spine, list) or len(spine) < 2:
        fail("source_pack.json.descent_spine must contain the validated Stage 2 chain.")
    spine_ids = [
        str(layer.get("mechanism_id") or "").strip().upper()
        for layer in spine
        if isinstance(layer, dict)
    ]
    _, spark, spark_rounds = validate_spark_development(
        pack,
        mechanism_ids,
        set(spine_ids[-2:]),
    )
    source_spark_id = str(spark["id"]).strip().upper()

    claim_audit = pack.get("claim_evidence_audit")
    if not isinstance(claim_audit, list) or len(claim_audit) != len(spine_ids):
        fail(
            "source_pack.json.claim_evidence_audit must review every "
            "main-spine mechanism exactly once."
        )
    audited_ids: list[str] = []
    for index, audit in enumerate(claim_audit):
        owner = f"claim_evidence_audit[{index}]"
        if not isinstance(audit, dict):
            fail(f"{owner} must be an object.")
        mechanism_id = require_string(audit, "mechanism_id", owner).upper()
        for key in (
            "supported_core",
            "unsupported_extension",
            "publish_boundary",
            "decision",
        ):
            require_string(audit, key, owner)
        decision = str(audit["decision"]).strip().lower()
        if decision not in {"supported", "qualified", "return_to_s2"}:
            fail(f"{owner}.decision must be supported, qualified or return_to_s2.")
        if decision == "return_to_s2":
            fail(f"{owner} requires a return to Stage 2.")
        audited_ids.append(mechanism_id)
    if audited_ids != spine_ids:
        fail(
            "claim_evidence_audit must follow the main descent spine exactly; "
            f"expected {spine_ids}, found {audited_ids}."
        )

    wisdom = pack.get("wisdom_candidates", [])
    if not isinstance(wisdom, list):
        fail("wisdom_candidates must be a list when present.")
    wisdom_ids: set[str] = set()
    used_wisdom_paths: set[Path] = set()
    used_wisdom_urls: set[str] = set()
    for index, candidate in enumerate(wisdom):
        owner = f"wisdom_candidates[{index}]"
        if not isinstance(candidate, dict):
            fail(f"{owner} must be an object.")
        for key in (
            "id",
            "research_stage",
            "knowledge_role",
            "tradition",
            "thinker_or_text",
            "source_url",
            "raw_page_source",
            "description_type",
            "source_authority",
            "source_identity_check",
            "chinese_description",
            "original_context",
            "mechanism_connection",
            "spark_relation",
            "spark_effect",
            "important_difference",
            "fit",
            "use_decision",
        ):
            require_string(candidate, key, owner)
        if str(candidate["research_stage"]).strip().lower() != "s3":
            fail(f"{owner}.research_stage must be s3.")
        if str(candidate["knowledge_role"]).strip().lower() != "wisdom":
            fail(f"{owner}.knowledge_role must be wisdom.")
        tradition = str(candidate["tradition"]).strip().lower()
        if tradition not in {"eastern", "western"}:
            fail(f"{owner}.tradition must be eastern or western.")
        if str(candidate["description_type"]).strip().lower() not in {
            "direct_quote",
            "faithful_paraphrase",
        }:
            fail(f"{owner}.description_type must be direct_quote or faithful_paraphrase.")
        authority = str(candidate["source_authority"]).strip().lower()
        if authority not in {"primary_text", "scholarly_translation", "analysis"}:
            fail(
                f"{owner}.source_authority must be primary_text, "
                "scholarly_translation or analysis."
            )
        if (
            str(candidate["description_type"]).strip().lower() == "direct_quote"
            and authority == "analysis"
            and str(candidate["use_decision"]).strip().lower() == "use"
        ):
            fail(f"{owner} cannot publish a direct quote from an analysis-only source.")
        if str(candidate["fit"]).strip().lower() not in {"strong", "partial", "weak"}:
            fail(f"{owner}.fit must be strong, partial or weak.")
        if str(candidate["spark_relation"]).strip().lower() not in {
            "support",
            "oppose",
            "qualify",
            "parallel",
        }:
            fail(
                f"{owner}.spark_relation must be support, oppose, qualify or parallel."
            )
        if str(candidate["use_decision"]).strip().lower() not in {"use", "reserve", "skip"}:
            fail(f"{owner}.use_decision must be use, reserve or skip.")
        if not host_of(str(candidate["source_url"])):
            fail(f"{owner}.source_url must include a domain.")
        path = source_path(
            topic_dir,
            str(candidate["raw_page_source"]),
            f"{owner}.raw_page_source",
        )
        reject_search_snapshot(path, f"{owner}.raw_page_source")
        if str(candidate["use_decision"]).strip().lower() == "use":
            source_url = str(candidate["source_url"]).strip()
            if path in used_wisdom_paths or source_url in used_wisdom_urls:
                fail(
                    "Every used wisdom candidate must have its own source page "
                    "and concrete source URL."
                )
            used_wisdom_paths.add(path)
            used_wisdom_urls.add(source_url)
        wisdom_ids.add(str(candidate["id"]).strip().upper())
    practice_cards = pack.get("practice_cards", [])
    if not isinstance(practice_cards, list):
        fail("practice_cards must be a list when present.")
    practice_ids: set[str] = set()
    for index, card in enumerate(practice_cards):
        owner = f"practice_cards[{index}]"
        if not isinstance(card, dict):
            fail(f"{owner} must be an object.")
        for key in (
            "id",
            "research_stage",
            "knowledge_role",
            "claim",
            "source_url",
            "raw_page_source",
            "supporting_quote",
            "use",
        ):
            require_string(card, key, owner)
        if str(card["research_stage"]).strip().lower() != "s3":
            fail(f"{owner}.research_stage must be s3.")
        if str(card["knowledge_role"]).strip().lower() != "practice":
            fail(f"{owner}.knowledge_role must be practice.")
        if not host_of(str(card["source_url"])):
            fail(f"{owner}.source_url must include a domain.")
        path = source_path(topic_dir, str(card["raw_page_source"]), f"{owner}.raw_page_source")
        reject_search_snapshot(path, f"{owner}.raw_page_source")
        quote = normalize_evidence_text(str(card["supporting_quote"]))
        if len(quote) < MIN_QUOTE_CHARS:
            fail(f"{owner}.supporting_quote is too short.")
        raw_text = normalize_evidence_text(path.read_text(encoding="utf-8", errors="replace"))
        if quote not in raw_text:
            fail(f"{owner}.supporting_quote was not found in {path}.")
        practice_ids.add(str(card["id"]).strip().upper())

    synthesis = require_object(pack, "wisdom_synthesis", "source_pack.json")
    for key in (
        "portable_principle",
        "eastern_lens",
        "western_lens",
        "tension_between_lenses",
        "return_to_reality",
    ):
        require_string(synthesis, key, "wisdom_synthesis")

    design = pack.get("practice_design")
    if not isinstance(design, dict):
        fail("source_pack.json.practice_design must be an object.")
    for key in ("reader_scene", "decision_or_action", "validation", "boundary"):
        require_string(design, key, "practice_design")
    steps = require_list(design, "steps_or_signals", "practice_design")
    if len(steps) < 2 or any(not isinstance(value, str) or not value.strip() for value in steps):
        fail("practice_design.steps_or_signals must contain at least 2 non-empty items.")
    evidence_ids = require_list(design, "evidence_ids", "practice_design")
    if any(not isinstance(value, str) or not value.strip() for value in evidence_ids):
        fail("practice_design.evidence_ids must contain non-empty IDs.")
    known_ids = {
        str(card.get("id") or "").strip().upper()
        for key in ("observation_cards", "mechanism_cards")
        for card in pack.get(key, [])
        if isinstance(card, dict)
    } | wisdom_ids | practice_ids
    unknown = sorted({str(value).strip().upper() for value in evidence_ids} - known_ids)
    if unknown:
        fail("practice_design.evidence_ids contains unknown IDs: " + ", ".join(unknown))

    descent_audit = pack.get("descent_audit")
    if not isinstance(descent_audit, list) or len(descent_audit) != len(spine_ids) - 1:
        fail(
            "source_pack.json.descent_audit must contain exactly one review for "
            "each adjacent descent transition."
        )
    for index, audit in enumerate(descent_audit, start=1):
        owner = f"descent_audit[{index - 1}]"
        if not isinstance(audit, dict):
            fail(f"{owner} must be an object.")
        if audit.get("from_level") != index or audit.get("to_level") != index + 1:
            fail(f"{owner} must review L{index} -> L{index + 1}.")
        for key in (
            "question_link",
            "cause_effect_check",
            "reverse_causality_test",
            "reader_language_check",
            "explanation_shift",
            "judgment_change",
            "evidence_check",
            "deletion_test",
            "boundary_check",
            "decision",
        ):
            require_string(audit, key, owner)
        if str(audit["decision"]).strip().lower() != "valid":
            fail(f"{owner}.decision is not valid; return to Stage 2.")

    verdict = require_object(pack, "spark_verdict", "source_pack.json")
    for key in (
        "spark_id",
        "decision",
        "depth_retained",
        "breadth_retained",
        "refined_question",
        "final_judgment",
        "publish_thesis",
        "strongest_counterargument",
        "response",
        "boundary",
        "philosophy_result",
        "reader_change",
        "article_role",
        "reframe_reason",
    ):
        require_string(verdict, key, "spark_verdict")
    spark_id = str(verdict["spark_id"]).strip().upper()
    if spark_id != source_spark_id:
        fail("spark_verdict.spark_id must match source_pack.json.spark.id.")
    decision = str(verdict["decision"]).strip().lower()
    if decision not in {"validated", "reframed"}:
        fail("spark_verdict.decision must be validated or reframed.")
    reviewed_rounds = verdict.get("reviewed_round_orders")
    expected_rounds = list(range(1, len(spark_rounds) + 1))
    if reviewed_rounds != expected_rounds:
        fail(
            "spark_verdict.reviewed_round_orders must include every Spark "
            f"development round in order: {expected_rounds}."
        )
    reviewed_levels = verdict.get("reviewed_descent_levels")
    expected_levels = list(range(1, len(spine_ids) + 1))
    if reviewed_levels != expected_levels:
        fail(
            "spark_verdict.reviewed_descent_levels must include every descent "
            f"level in order: {expected_levels}."
        )
    publish_thesis = str(verdict["publish_thesis"]).strip()
    if has_quantitative_signal(publish_thesis):
        fail("spark_verdict.publish_thesis must be a conceptual judgment without factual figures.")

    verdict_mechanisms = verdict.get("mechanism_basis_ids")
    if not isinstance(verdict_mechanisms, list) or not verdict_mechanisms:
        fail("spark_verdict.mechanism_basis_ids must be a non-empty list.")
    verdict_mechanism_ids = {
        str(value).strip().upper()
        for value in verdict_mechanisms
        if str(value).strip()
    }
    unknown_mechanisms = sorted(verdict_mechanism_ids - mechanism_ids)
    if unknown_mechanisms:
        fail(
            "spark_verdict.mechanism_basis_ids contains unknown IDs: "
            + ", ".join(unknown_mechanisms)
        )
    if not verdict_mechanism_ids & set(spine_ids[-2:]):
        fail("spark_verdict must remain connected to one of the two deepest mechanisms.")

    supporting_values = verdict.get("supporting_evidence_ids")
    if not isinstance(supporting_values, list) or not supporting_values:
        fail("spark_verdict.supporting_evidence_ids must be a non-empty list.")
    supporting_ids = {
        str(value).strip().upper()
        for value in supporting_values
        if str(value).strip()
    }
    unknown_support = sorted(supporting_ids - known_ids)
    if unknown_support:
        fail(
            "spark_verdict.supporting_evidence_ids contains unknown IDs: "
            + ", ".join(unknown_support)
        )

    verdict_wisdom = verdict.get("wisdom_ids")
    if not isinstance(verdict_wisdom, list):
        fail("spark_verdict.wisdom_ids must be a list, including when empty.")
    selected_wisdom_ids = {
        str(value).strip().upper()
        for value in verdict_wisdom
        if str(value).strip()
    }
    unknown_wisdom = sorted(selected_wisdom_ids - wisdom_ids)
    if unknown_wisdom:
        fail("spark_verdict.wisdom_ids contains unknown IDs: " + ", ".join(unknown_wisdom))

    return (
        len(wisdom),
        len(practice_cards),
        numeric_claims,
        user_material_ids,
        article_profile,
        spark_id,
        publish_thesis,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir")
    args = parser.parse_args()
    topic_dir = resolve_topic_dir(args.topic_dir, "article/final_article.md")
    require_receipt(topic_dir, STAGE1_RECEIPT, next_stage="Stage 4 article")
    stage2_receipt = require_receipt(topic_dir, STAGE2_RECEIPT, next_stage="Stage 4 article")
    stage3_receipt = require_receipt(topic_dir, STAGE3_RECEIPT, next_stage="Stage 4 article")
    if int(stage2_receipt.get("descent_levels") or 0) < 5:
        fail("Stage 2 receipt is missing a validated 5+ level descent spine.")
    (
        wisdom_count,
        practice_card_count,
        numeric_claims,
        user_material_ids,
        article_profile,
        spark_id,
        publish_thesis,
    ) = validate_insight_research(topic_dir)
    for label, receipt in (("Stage 2", stage2_receipt), ("Stage 3", stage3_receipt)):
        if (
            receipt.get("article_mode") != article_profile["mode"]
            or receipt.get("article_subtype") != article_profile["subtype"]
        ):
            fail(f"{label} receipt does not match the current article_profile.")
        if receipt.get("article_route") != article_route_key(article_profile):
            fail(f"{label} receipt does not match the full article route.")
    if str(stage2_receipt.get("spark_id") or "").strip().upper() != spark_id:
        fail("Stage 2 receipt does not match the current Spark. Revalidate Stage 2.")
    if str(stage3_receipt.get("spark_id") or "").strip().upper() != spark_id:
        fail("Stage 3 receipt does not match the current Spark. Revalidate Stage 3.")
    article_dir = topic_dir / "article"
    mindmap_path = article_dir / "article_mindmap.md"
    final_path = article_dir / "final_article.md"
    for path in (mindmap_path, final_path):
        if not path.is_file():
            fail(f"Missing Stage 4 file: {path}")

    mindmap_chars = nonspace_len(mindmap_path.read_text(encoding="utf-8"))
    final = final_path.read_text(encoding="utf-8")
    if FOOTNOTE_REFERENCE_RE.search(final) or FOOTNOTE_DEFINITION_RE.search(final):
        fail(
            "final_article.md must not contain footnote references or definitions; "
            "keep source traceability in research/source_pack.json."
        )
    numeric_blocks = validate_article_numeric_markers(
        final,
        numeric_claims,
        user_material_ids,
    )
    if re.search(r"(?m)^#{2,6}\s+L\d+\s*[·:：—-]", final):
        fail("final_article.md must follow the descent levels without exposing L1-Lx construction labels.")
    expected_spine_ids = stage2_receipt.get("descent_spine_ids")
    if not isinstance(expected_spine_ids, list) or any(
        not isinstance(value, str) or not value.strip() for value in expected_spine_ids
    ):
        fail("Stage 2 receipt is missing descent_spine_ids.")
    descent_tags = re.findall(
        r"<!--\s*DESCENT:L(\d+):(M\d+)\s*-->",
        final,
        flags=re.IGNORECASE,
    )
    expected_tags = [
        (str(index), str(mechanism_id).strip().upper())
        for index, mechanism_id in enumerate(expected_spine_ids, start=1)
    ]
    normalized_tags = [(level, mechanism_id.upper()) for level, mechanism_id in descent_tags]
    if normalized_tags != expected_tags:
        fail(
            "final_article.md descent markers must follow the validated Stage 2 spine exactly; "
            f"expected {expected_tags}, found {normalized_tags}."
        )
    rebound_markers = list(re.finditer(r"<!--\s*REBOUND\s*-->", final, flags=re.IGNORECASE))
    if len(rebound_markers) != 1:
        fail("final_article.md must contain exactly one <!-- REBOUND --> marker.")
    last_descent = list(
        re.finditer(r"<!--\s*DESCENT:L\d+:M\d+\s*-->", final, flags=re.IGNORECASE)
    )[-1]
    if rebound_markers[0].start() <= last_descent.start():
        fail("final_article.md REBOUND marker must appear after the deepest descent marker.")
    validate_article_spark_marker(
        final,
        spark_id,
        publish_thesis,
        last_descent.start(),
        rebound_markers[0].start(),
    )
    final_chars = nonspace_len(final)
    if final_chars < MIN_ARTICLE_SANITY_CHARS:
        fail(
            f"final_article.md has only {final_chars} non-whitespace characters; "
            f"below the structural sanity floor of {MIN_ARTICLE_SANITY_CHARS}."
        )
    _, sections = markdown_shape(final, "final_article.md")
    if not MIN_MAJOR_SECTIONS <= sections <= MAX_MAJOR_SECTIONS:
        fail(
            f"final_article.md has {sections} major sections; "
            f"expected a structurally plausible {MIN_MAJOR_SECTIONS}-{MAX_MAJOR_SECTIONS}."
        )
    voice = section_length_stats(final)
    parsed_blocks = parse_blocks(final)
    semantic_formats: set[str] = set()
    quote_blocks = [
        (index, lines)
        for index, (block_type, lines) in enumerate(parsed_blocks)
        if block_type == "quote"
    ]
    last_quote_index = quote_blocks[-1][0] if quote_blocks else -1
    for index, (block_type, lines) in enumerate(parsed_blocks):
        if block_type == "heading" and lines[0].strip().startswith("### "):
            semantic_formats.add("subsection")
        elif block_type == "paragraph":
            text = " ".join(lines).strip()
            if re.fullmatch(r"\*\*(?s:.+)\*\*", text):
                semantic_formats.add("punch")
        elif block_type == "quote":
            text = "\n".join(lines)
            item_count = len(
                re.findall(r"(?:^|\n)\s*(?:[-*]\s+|\d+[\.．、\)]\s*)\S+", text)
            )
            if not (index == last_quote_index and item_count >= 1):
                semantic_formats.add("quote")
        elif block_type in {"list", "table", "code"}:
            semantic_formats.add(block_type)
    # Always rebuild HTML so Stage 4 cannot "pass md only" and skip the paste file.
    copy_path = write_wechat_html(topic_dir, quiet=True)
    copy_html = copy_path.read_text(encoding="utf-8")
    if re.search(
        r"(?:<!--|&lt;!--)\s*(?:DATA:|USER:|IMAGE:|DESCENT:|SPARK:|REBOUND)",
        copy_html,
        flags=re.IGNORECASE,
    ):
        fail("final_article_copy.html leaked a construction marker into visible HTML.")
    if FOOTNOTE_REFERENCE_RE.search(copy_html) or FOOTNOTE_DEFINITION_RE.search(copy_html):
        fail("final_article_copy.html leaked publishing footnotes.")
    visible_chars = nonspace_len(re.sub(r"<[^>]+>", "", copy_html))
    if visible_chars < int(final_chars * 0.55):
        fail("final_article_copy.html appears incomplete compared with final_article.md.")
    if "font-size: 15px; line-height: 1.9" not in copy_html:
        fail("final_article_copy.html must contain the 15px body style.")
    font_sizes = set(re.findall(r"font-size:\s*([^;]+);", copy_html))
    visible_font_sizes = {value.strip() for value in font_sizes if value.strip() != "0"}
    if visible_font_sizes != {"15px"}:
        fail(
            "final_article_copy.html must render all visible text at 15px; "
            f"found: {sorted(visible_font_sizes)}."
        )
    if 'data-wa-format="section-title"' not in copy_html:
        fail("final_article_copy.html is missing section-title formatting.")
    expected_theme = str(article_profile["mode"]).replace("_", "-")
    if f'data-wa-theme="{expected_theme}"' not in copy_html:
        fail(f"final_article_copy.html must use data-wa-theme={expected_theme}.")
    if article_profile["mode"] == "life_insight" and (
        'data-wa-variant="life-editorial"' not in copy_html
        or 'data-wa-variant="life-timeline"' not in copy_html
    ):
        fail("life_insight HTML must use its dedicated editorial title and timeline sections.")
    if 'data-wa-format="section-badge"' not in copy_html:
        fail("final_article_copy.html section titles must use circular section-badge numbers.")
    if ">SECTION<" in copy_html or ">SECTION</span>" in copy_html:
        fail("final_article_copy.html must not render SECTION labels on chapter titles.")
    if "【01】" in copy_html or "【1】" in copy_html:
        fail("final_article_copy.html must not use 【NN】 bracket chapter badges.")
    if 'data-wa-format="opening-lead"' not in copy_html:
        fail(
            "final_article_copy.html is missing opening-lead card "
            "(the first substantive paragraph should render as a rounded lead card)."
        )
    has_reader_questions = 'data-wa-format="reader-questions"' in copy_html
    has_reader_invite = 'data-wa-format="reader-invite"' in copy_html
    if has_reader_questions != has_reader_invite:
        fail("final_article_copy.html reader questions and reader invite must appear together.")
    question_count = copy_html.count('data-wa-format="reader-question"')
    if has_reader_questions and not 1 <= question_count <= 3:
        fail(
            f"final_article_copy.html interaction block must list 1-3 short reader questions; "
            f"found {question_count}."
        )
    forbidden_css = ("background-color:", "background-image:", "linear-gradient(")
    hits = [value for value in forbidden_css if value in copy_html]
    if hits:
        fail(f"final_article_copy.html contains non-portable visual CSS: {', '.join(hits)}")

    code_blocks = [lines for block_type, lines in parse_blocks(final) if block_type == "code"]
    rendered_code_blocks = copy_html.count('data-wa-format="code-block"')
    if rendered_code_blocks != len(code_blocks):
        fail(
            "final_article_copy.html code block count does not match final_article.md: "
            f"expected {len(code_blocks)}, got {rendered_code_blocks}."
        )
    if code_blocks and (
        'data-wa-format="code-block"' not in copy_html
        or 'data-wa-code-language=' not in copy_html
        or 'data-wa-code-line=' not in copy_html
    ):
        fail("final_article_copy.html code blocks must use the inline language-header and per-line component.")
    rendered_code_lines = copy_html.count("data-wa-code-line=")
    expected_code_lines = sum(max(1, len(lines) - 1) for lines in code_blocks)
    if rendered_code_lines != expected_code_lines:
        fail(
            "final_article_copy.html code line count does not match final_article.md: "
            f"expected {expected_code_lines}, got {rendered_code_lines}."
        )
    rendered_line_fragments = re.findall(
        r'<span\s+data-wa-code-text="true"[^>]*>(.*?)</span></p>', copy_html, flags=re.DOTALL
    )
    rendered_plain_lines = [html_lib.unescape(re.sub(r"<[^>]+>", "", fragment)) for fragment in rendered_line_fragments]
    expected_plain_lines = []
    for lines in code_blocks:
        expected_plain_lines.extend([line.replace("\t", "    ") for line in lines[1:]] or [""])
    if rendered_plain_lines != expected_plain_lines:
        fail("final_article_copy.html code content or line order was changed during formatting.")

    print(json.dumps({
        "stage": "stage4_article",
        "topic_dir": str(topic_dir),
        "mindmap_chars": mindmap_chars,
        "final_chars": final_chars,
        "major_sections": sections,
        "code_blocks": len(code_blocks),
        "wisdom_candidates": wisdom_count,
        "practice_cards": practice_card_count,
        "numeric_claims": len(numeric_claims),
        "article_mode": article_profile["mode"],
        "article_subtype": article_profile["subtype"],
        "article_route": article_route_key(article_profile),
        "verified_numeric_blocks": numeric_blocks,
        "spark_id": spark_id,
        "section_stats": voice,
        "semantic_formats": sorted(semantic_formats),
        "breath_paragraphs": copy_html.count('data-wa-format="breath"'),
        "status": "passed",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
