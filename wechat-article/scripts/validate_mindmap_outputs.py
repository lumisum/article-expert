#!/usr/bin/env python3
"""Validate Stage 2 mechanism research and mechanism mindmap structure."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from validation_lib import (
    MIN_QUOTE_CHARS,
    STAGE1_RECEIPT,
    STAGE2_RECEIPT,
    STAGE3_RECEIPT,
    clear_receipt,
    fail,
    load_json,
    nonspace_len,
    normalize_evidence_text,
    reject_search_snapshot,
    require_list,
    require_receipt,
    require_string,
    resolve_topic_dir,
    validate_numeric_claims,
    validate_numeric_refs,
    validate_article_profile,
    article_route_key,
    validate_spark_development,
    write_receipt,
)

MIN_MINDMAP_CHARS = 1200
MIN_MECHANISM_CARDS = 3
MIN_MECHANISM_DOMAINS = 2
EVIDENCE_ID_RE = re.compile(r"(?<![A-Z0-9])[OM]\d{2,}(?![A-Z0-9])")
IMAGE_PLACEHOLDER_RE = re.compile(r"<!--\s*IMAGE:")
DEPTH_LABEL_RE = re.compile(r"(?m)^#{3,6}\s+L(\d+)\s*[·:：—-]\s*\S+")
COORDINATE_REF_RE = re.compile(r"(?<![A-Z0-9])C\d{2,}(?![A-Z0-9])")
SPARK_REF_RE = re.compile(r"(?<![A-Z0-9])S\d{2,}(?![A-Z0-9])")


def host_of(url: str) -> str:
    host = (urlparse(url).netloc or "").lower()
    return host.removeprefix("www.")


def has_heading(text: str, keyword: str) -> bool:
    return any(
        keyword in re.sub(r"^#+\s*", "", line).strip()
        for line in text.splitlines()
        if line.startswith("#")
    )


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir")
    args = parser.parse_args()
    topic_dir = resolve_topic_dir(args.topic_dir, "article/article_mindmap.md")
    stage1 = require_receipt(topic_dir, STAGE1_RECEIPT, next_stage="Stage 2 mechanism research")
    clear_receipt(topic_dir, STAGE2_RECEIPT)
    clear_receipt(topic_dir, STAGE3_RECEIPT)

    pack = load_json(topic_dir / "research" / "source_pack.json")
    if not isinstance(pack, dict):
        fail("source_pack.json must be an object.")
    article_profile = validate_article_profile(pack)
    if (
        stage1.get("article_mode") != article_profile["mode"]
        or stage1.get("article_subtype") != article_profile["subtype"]
    ):
        fail("Stage 1 receipt does not match the current article_profile. Revalidate Stage 1.")
    if stage1.get("article_route") != article_route_key(article_profile):
        fail("Stage 1 receipt does not match the full article route. Revalidate Stage 1.")
    observations = require_list(pack, "observation_cards", "source_pack.json")
    numeric_claims = validate_numeric_claims(topic_dir, pack)
    if int(stage1.get("observation_cards") or 0) != len(observations):
        fail("Stage 1 receipt does not match current observation_cards. Revalidate Stage 1.")

    cards = pack.get("mechanism_cards")
    if not isinstance(cards, list) or len(cards) < MIN_MECHANISM_CARDS:
        fail(
            f"mechanism_cards must contain at least {MIN_MECHANISM_CARDS} items; "
            f"found {0 if not isinstance(cards, list) else len(cards)}."
        )
    mechanism_ids: set[str] = set()
    mechanism_hosts: set[str] = set()
    mechanism_page_hosts: dict[Path, set[str]] = {}
    mechanism_depths: dict[str, int] = {}
    mechanism_parents: dict[str, str] = {}
    for index, card in enumerate(cards):
        owner = f"mechanism_cards[{index}]"
        if not isinstance(card, dict):
            fail(f"{owner} must be an object.")
        for key in (
            "id",
            "research_stage",
            "knowledge_role",
            "question_answered",
            "mechanism_claim",
            "explains",
            "explanatory_level",
            "deeper_question_or_stop",
            "source_type",
            "source_url",
            "raw_page_source",
            "supporting_quote",
            "confidence",
            "counterpoint_or_boundary",
        ):
            require_string(card, key, owner)
        depth_level = card.get("depth_level")
        if not isinstance(depth_level, int) or isinstance(depth_level, bool) or depth_level < 1:
            fail(f"{owner}.depth_level must be a positive integer.")
        parent_id = require_string(card, "parent_mechanism_id", owner).strip().upper()
        if str(card["research_stage"]).strip().lower() != "s2":
            fail(f"{owner}.research_stage must be s2.")
        if str(card["knowledge_role"]).strip().lower() != "mechanism":
            fail(f"{owner}.knowledge_role must be mechanism.")
        if card["source_type"] not in {"primary", "community", "analysis"}:
            fail(f"{owner}.source_type must be primary, community or analysis.")
        card_id = str(card["id"]).strip().upper()
        if card_id in mechanism_ids:
            fail(f"Duplicate mechanism id: {card_id}")
        mechanism_ids.add(card_id)
        mechanism_depths[card_id] = depth_level
        mechanism_parents[card_id] = parent_id
        host = host_of(str(card["source_url"]))
        if not host:
            fail(f"{owner}.source_url must include a domain.")
        mechanism_hosts.add(host)
        path = source_path(topic_dir, str(card["raw_page_source"]), f"{owner}.raw_page_source")
        reject_search_snapshot(path, f"{owner}.raw_page_source")
        mechanism_page_hosts.setdefault(path, set()).add(host)
        quote = normalize_evidence_text(str(card["supporting_quote"]))
        if len(quote) < MIN_QUOTE_CHARS:
            fail(f"{owner}.supporting_quote is too short.")
        raw_text = normalize_evidence_text(path.read_text(encoding="utf-8", errors="replace"))
        if quote not in raw_text:
            fail(f"{owner}.supporting_quote was not found in {path}.")
        validate_numeric_refs(
            card,
            owner,
            " ".join(
                str(card.get(key) or "")
                for key in (
                    "question_answered",
                    "mechanism_claim",
                    "explains",
                    "supporting_quote",
                    "counterpoint_or_boundary",
                )
            ),
            numeric_claims,
        )

    reused_pages = {
        str(path): sorted(hosts)
        for path, hosts in mechanism_page_hosts.items()
        if len(hosts) > 1
    }
    if reused_pages:
        fail(
            "One mechanism snapshot cannot represent several source domains: "
            + json.dumps(reused_pages, ensure_ascii=False)
        )

    if len(mechanism_hosts) < MIN_MECHANISM_DOMAINS:
        fail(
            f"mechanism_cards must span at least {MIN_MECHANISM_DOMAINS} domains; "
            f"found {len(mechanism_hosts)}."
        )
    source_files = require_list(pack, "mechanism_source_files", "source_pack.json")
    for index, value in enumerate(source_files):
        path = source_path(topic_dir, str(value), f"mechanism_source_files[{index}]")
        reject_search_snapshot(path, f"mechanism_source_files[{index}]")
    rounds = require_list(pack, "mechanism_research_rounds", "source_pack.json")
    for index, research_round in enumerate(rounds):
        owner = f"mechanism_research_rounds[{index}]"
        if not isinstance(research_round, dict):
            fail(f"{owner} must be an object.")
        for key in ("question", "result", "depth_gain", "remaining_gap"):
            require_string(research_round, key, owner)

    spine = require_list(pack, "descent_spine", "source_pack.json")
    if not 5 <= len(spine) <= 7:
        fail(f"descent_spine must contain 5-7 ordered levels; found {len(spine)}.")
    expected_levels = list(range(1, len(spine) + 1))
    spine_ids: list[str] = []
    for index, layer in enumerate(spine, start=1):
        owner = f"descent_spine[{index - 1}]"
        if not isinstance(layer, dict):
            fail(f"{owner} must be an object.")
        if layer.get("order") != index or layer.get("depth_level") != index:
            fail(f"{owner}.order and depth_level must both equal {index}.")
        for key in (
            "mechanism_id",
            "layer_label",
            "move_type",
            "depth_domain",
            "explains_level",
            "cause_effect_link",
            "reverse_causality_test",
            "reader_facing_expression",
            "question",
            "answer",
            "insufficiency",
            "explanation_shift",
            "judgment_delta",
            "reader_stake",
            "counterexample_or_boundary",
            "next_question_or_stop",
        ):
            require_string(layer, key, owner)
        if str(layer["move_type"]).strip().lower() not in {
            "causal_deepen",
            "constraint_deepen",
            "feedback_deepen",
            "tradeoff_deepen",
            "boundary_deepen",
        }:
            fail(f"{owner}.move_type is not a valid downward explanatory move.")
        expected_explains_level = "ROOT" if index == 1 else f"L{index - 1}"
        if str(layer["explains_level"]).strip().upper() != expected_explains_level:
            fail(
                f"{owner}.explains_level must be {expected_explains_level}; "
                "the main spine may only explain the immediately preceding level."
            )
        mechanism_id = str(layer["mechanism_id"]).strip().upper()
        if mechanism_id not in mechanism_ids:
            fail(f"{owner}.mechanism_id is unknown: {mechanism_id}")
        if mechanism_id in spine_ids:
            fail(f"descent_spine repeats mechanism_id: {mechanism_id}")
        if mechanism_depths[mechanism_id] != index:
            fail(
                f"{owner}.mechanism_id {mechanism_id} has depth_level "
                f"{mechanism_depths[mechanism_id]}, expected {index}."
            )
        expected_parent = "ROOT" if index == 1 else spine_ids[-1]
        if mechanism_parents[mechanism_id] != expected_parent:
            fail(
                f"{mechanism_id}.parent_mechanism_id must be {expected_parent} "
                f"on the main descent spine."
            )
        spine_ids.append(mechanism_id)

    layer_labels = [str(layer["layer_label"]).strip() for layer in spine]
    layer_questions = [str(layer["question"]).strip() for layer in spine]
    layer_answers = [str(layer["answer"]).strip() for layer in spine]
    explanation_shifts = [str(layer["explanation_shift"]).strip() for layer in spine]
    judgment_deltas = [str(layer["judgment_delta"]).strip() for layer in spine]
    if len(set(layer_labels)) != len(layer_labels):
        fail("descent_spine.layer_label values must be distinct.")
    if len(set(layer_questions)) != len(layer_questions):
        fail("descent_spine.question values must be distinct; repeated questions are not descent.")
    if len(set(layer_answers)) != len(layer_answers):
        fail("descent_spine.answer values must be distinct; repeated answers are not descent.")
    if len(set(explanation_shifts)) != len(explanation_shifts):
        fail("descent_spine.explanation_shift values must be distinct.")
    if len(set(judgment_deltas)) != len(judgment_deltas):
        fail("descent_spine.judgment_delta values must be distinct.")
    if article_profile["mode"] == "life_insight":
        life_domains = {"time", "relationship", "identity", "tradeoff"}
        depth_domains = {
            str(layer["depth_domain"]).strip().lower() for layer in spine
        }
        deepest_domains = {
            str(layer["depth_domain"]).strip().lower() for layer in spine[-2:]
        }
        if len(depth_domains & life_domains) < 2:
            fail(
                "life_insight descent_spine must reach at least two of time, "
                "relationship, identity or tradeoff."
            )
        if not deepest_domains & life_domains:
            fail(
                "At least one of the two deepest life_insight levels must enter "
                "time, relationship, identity or tradeoff."
            )

    coordinate_map, spark, spark_rounds = validate_spark_development(
        pack,
        mechanism_ids,
        set(spine_ids[-2:]),
    )
    spark_id = str(spark["id"]).strip().upper()

    mindmap_path = topic_dir / "article" / "article_mindmap.md"
    if not mindmap_path.is_file():
        fail(f"Missing Stage 2 mechanism mindmap: {mindmap_path}")
    text = mindmap_path.read_text(encoding="utf-8")
    chars = nonspace_len(text)
    if chars < MIN_MINDMAP_CHARS:
        fail(
            f"article_mindmap.md has {chars} non-whitespace characters; "
            f"expected at least {MIN_MINDMAP_CHARS}."
        )
    if IMAGE_PLACEHOLDER_RE.search(text):
        fail("article_mindmap.md must not contain image placeholders.")
    required_headings = (
        "事实基线",
        "中心问题",
        "初始机制假设",
        "定向补研",
        "核心机制链",
        "认知下潜链",
        "替代解释与反例",
        "最低点",
        "认知坐标",
        "Spark多轮生长",
        "适用边界与未决问题",
        "读者关系",
        "回升接口",
    )
    missing = [heading for heading in required_headings if not has_heading(text, heading)]
    if missing:
        fail("article_mindmap.md is missing required headings: " + ", ".join(missing))
    if "```mermaid" not in text:
        fail("article_mindmap.md must include a Mermaid mechanism diagram.")
    labeled_levels = [int(value) for value in DEPTH_LABEL_RE.findall(text)]
    if labeled_levels != expected_levels:
        fail(
            "article_mindmap.md depth labels must appear once and in order as "
            f"L1-L{len(spine)}; found {labeled_levels}."
        )

    known_ids = {
        str(card.get("id") or "").strip().upper()
        for card in observations + cards
        if isinstance(card, dict)
    }
    cited = {match.group(0).upper() for match in EVIDENCE_ID_RE.finditer(text)}
    known_cited = sorted(cited & known_ids)
    if len(known_cited) < 4:
        fail(
            f"article_mindmap.md cites only {len(known_cited)} known O/M evidence IDs; "
            "expected at least 4."
        )
    if not any(evidence_id.startswith("M") for evidence_id in known_cited):
        fail("article_mindmap.md must cite mechanism evidence IDs, not observations alone.")
    cited_coordinates = {
        match.group(0).upper() for match in COORDINATE_REF_RE.finditer(text)
    }
    if cited_coordinates != set(coordinate_map):
        fail(
            "article_mindmap.md must include every coordinate ID as defined; "
            f"expected {sorted(coordinate_map)}, found {sorted(cited_coordinates)}."
        )
    cited_sparks = {match.group(0).upper() for match in SPARK_REF_RE.finditer(text)}
    if cited_sparks != {spark_id}:
        fail(
            "article_mindmap.md must include the single Spark ID; "
            f"expected {[spark_id]}, found {sorted(cited_sparks)}."
        )

    receipt = write_receipt(
        topic_dir,
        STAGE2_RECEIPT,
        {
            "stage": "stage2_mechanism",
            "topic_dir": str(topic_dir),
            "mindmap_chars": chars,
            "mechanism_cards": len(cards),
            "mechanism_domains": sorted(mechanism_hosts),
            "research_rounds": len(rounds),
            "descent_levels": len(spine),
            "deepest_mechanism_id": spine_ids[-1],
            "descent_spine_ids": spine_ids,
            "coordinate_ids": sorted(coordinate_map),
            "spark_id": spark_id,
            "article_mode": article_profile["mode"],
            "article_subtype": article_profile["subtype"],
            "article_route": article_route_key(article_profile),
            "spark_rounds": len(spark_rounds),
            "numeric_claims": len(numeric_claims),
            "cited_evidence_ids": known_cited,
            "upstream_stage1_receipt": STAGE1_RECEIPT,
        },
    )
    print(
        json.dumps(
            {
                "stage": "stage2_mechanism",
                "topic_dir": str(topic_dir),
                "mindmap_chars": chars,
                "mechanism_cards": len(cards),
                "mechanism_domains": sorted(mechanism_hosts),
                "research_rounds": len(rounds),
                "descent_levels": len(spine),
                "deepest_mechanism_id": spine_ids[-1],
                "descent_spine_ids": spine_ids,
                "coordinates": len(coordinate_map),
                "spark_id": spark_id,
                "article_route": article_route_key(article_profile),
                "spark_rounds": len(spark_rounds),
                "numeric_claims": len(numeric_claims),
                "receipt": str(receipt),
                "status": "passed",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
