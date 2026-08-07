#!/usr/bin/env python3
"""Validate the Stage 1 observation archive and fact-only source pack."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from validation_lib import (
    MAX_SELECTED_SOURCE_FILES,
    MIN_EVIDENCE_CARDS,
    MIN_EVIDENCE_DOMAINS,
    MIN_QUOTE_CHARS,
    MIN_RAW_PAGE_BYTES,
    MIN_RAW_PAGE_FILES,
    MIN_SELECTED_SOURCE_FILES,
    STAGE1_RECEIPT,
    STAGE2_RECEIPT,
    STAGE3_RECEIPT,
    clear_receipt,
    fail,
    load_json,
    normalize_evidence_text,
    reject_search_snapshot,
    require_list,
    require_object,
    require_string,
    resolve_topic_dir,
    validate_numeric_claims,
    validate_numeric_refs,
    validate_article_profile,
    article_route_key,
    validate_research_blueprint,
    write_receipt,
)


def source_path(topic_dir: Path, raw_root: Path, value: str, owner: str) -> Path:
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
    host = (urlparse(url).netloc or "").lower()
    return host.removeprefix("www.")


def is_google_host(host: str) -> bool:
    host = host.lower().removeprefix("www.")
    return host.startswith("google.") or ".google." in host


def is_google_search_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    return is_google_host(host) and parsed.path.rstrip("/") == "/search"


def validate_capture_manifest(raw_root: Path) -> dict[Path, set[str]]:
    manifest_path = raw_root / "cdp_capture_manifest.json"
    manifest = load_json(manifest_path)
    if not isinstance(manifest, list):
        fail(f"{manifest_path} must contain a list of CDP capture records.")
    captured_pages: dict[Path, set[str]] = {}
    for index, item in enumerate(manifest):
        if not isinstance(item, dict) or item.get("status") != "captured":
            continue
        value = item.get("path")
        if not isinstance(value, str) or not value.strip():
            fail(f"cdp_capture_manifest.json[{index}].path must be a non-empty string.")
        path = Path(value)
        if not path.is_absolute():
            path = raw_root / path
        path = path.resolve()
        try:
            path.relative_to(raw_root)
        except ValueError:
            fail(
                f"cdp_capture_manifest.json[{index}].path must stay inside "
                f"{raw_root}: {path}"
            )
        if not path.is_file():
            fail(f"Captured page listed in the CDP manifest does not exist: {path}")
        hosts = captured_pages.setdefault(path, set())
        for key in ("url", "final_url"):
            value = item.get(key)
            if isinstance(value, str):
                host = host_of(value)
                if host:
                    hosts.add(host)
    if len(captured_pages) < MIN_RAW_PAGE_FILES:
        fail(
            f"Stage 1 requires at least {MIN_RAW_PAGE_FILES} successfully captured "
            f"CDP pages; found {len(captured_pages)} in {manifest_path}."
        )
    return captured_pages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir")
    args = parser.parse_args()
    topic_dir = resolve_topic_dir(args.topic_dir, "research/raw_pages")
    clear_receipt(topic_dir, STAGE1_RECEIPT)
    clear_receipt(topic_dir, STAGE2_RECEIPT)
    clear_receipt(topic_dir, STAGE3_RECEIPT)

    raw_root = (topic_dir / "research" / "raw_pages").resolve()
    if not raw_root.is_dir():
        fail(f"Missing raw_pages directory: {raw_root}. Stage 1 must capture facts before indexing them.")
    raw_files = [
        path
        for path in raw_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".html", ".htm"}
    ]
    if len(raw_files) < MIN_RAW_PAGE_FILES:
        fail(
            f"Stage 1 requires at least {MIN_RAW_PAGE_FILES} saved fact pages; "
            f"found {len(raw_files)}."
        )
    raw_page_bytes = sum(path.stat().st_size for path in raw_files)
    if raw_page_bytes < MIN_RAW_PAGE_BYTES:
        fail(
            f"Stage 1 requires at least {MIN_RAW_PAGE_BYTES} bytes of saved page "
            f"material; found {raw_page_bytes}."
        )
    captured_pages = validate_capture_manifest(raw_root)
    captured_paths = set(captured_pages)

    pack_path = topic_dir / "research" / "source_pack.json"
    pack = load_json(pack_path)
    if not isinstance(pack, dict):
        fail("source_pack.json must be an object.")
    require_string(pack, "topic_id", "source_pack.json")
    article_profile = validate_article_profile(pack)
    blueprint = validate_research_blueprint(topic_dir)
    if str(pack["topic_id"]).strip() != str(blueprint["topic_id"]).strip():
        fail("source_pack.json.topic_id must match research_blueprint.topic_id.")
    if article_route_key(article_profile) != blueprint["_article_route"]:
        fail("source_pack.json.article_profile must match the pre-search research_blueprint.")
    if str(article_profile["core_audience"]).strip() != str(blueprint["core_audience"]).strip():
        fail("article_profile.core_audience must match research_blueprint.")
    if str(article_profile["core_delivery"]).strip() != str(blueprint["core_delivery"]).strip():
        fail("article_profile.core_delivery must match research_blueprint.")
    selected_topic = require_object(pack, "selected_topic", "source_pack.json")
    require_string(selected_topic, "title", "selected_topic")
    require_string(selected_topic, "research_focus", "selected_topic")

    reader_problem = require_object(pack, "reader_problem", "source_pack.json")
    for key in ("reader", "situation", "question", "search_query", "expected_change"):
        require_string(reader_problem, key, "reader_problem")
    numeric_claims = validate_numeric_claims(topic_dir, pack)
    user_materials = pack.get("user_materials", [])
    if not isinstance(user_materials, list):
        fail("source_pack.json.user_materials must be a list when present.")
    user_material_ids: set[str] = set()
    for index, material in enumerate(user_materials):
        owner = f"user_materials[{index}]"
        if not isinstance(material, dict):
            fail(f"{owner} must be an object.")
        for key in (
            "id",
            "material_type",
            "provided_by",
            "claim",
            "time_scope",
            "certainty",
            "permitted_use",
            "boundary",
        ):
            require_string(material, key, owner)
        material_id = str(material["id"]).strip().upper()
        if not re.fullmatch(r"U\d{2,}", material_id):
            fail(f"{owner}.id must use the U01 form.")
        if material_id in user_material_ids:
            fail(f"Duplicate user material id: {material_id}")
        user_material_ids.add(material_id)
        if str(material["material_type"]).strip().lower() not in {
            "oral_history",
            "user_note",
            "user_quote",
        }:
            fail(f"{owner}.material_type must be oral_history, user_note or user_quote.")
        if str(material["provided_by"]).strip().lower() != "user":
            fail(f"{owner}.provided_by must be user.")
        if str(material["certainty"]).strip().lower() not in {"exact", "approximate"}:
            fail(f"{owner}.certainty must be exact or approximate.")
        if str(material["permitted_use"]).strip().lower() != "first_person_narrative":
            fail(f"{owner}.permitted_use must be first_person_narrative.")

    cards = pack.get("observation_cards")
    if not isinstance(cards, list) or len(cards) < MIN_EVIDENCE_CARDS:
        fail(
            f"observation_cards must contain at least {MIN_EVIDENCE_CARDS} items; "
            f"found {0 if not isinstance(cards, list) else len(cards)}."
        )
    ids: set[str] = set()
    card_hosts: set[str] = set()
    primary_count = 0
    material_role_counts = {
        "topic_fact": 0,
        "reader_context": 0,
        "counter_signal": 0,
        "boundary_fact": 0,
    }
    role_paths: dict[str, set[Path]] = {
        role: set() for role in material_role_counts
    }
    numeric_card_count = 0
    page_hosts: dict[Path, set[str]] = {}
    for index, card in enumerate(cards):
        owner = f"observation_cards[{index}]"
        if not isinstance(card, dict):
            fail(f"{owner} must be an object.")
        for key in (
            "id",
            "research_stage",
            "knowledge_role",
            "material_role",
            "claim",
            "source_type",
            "source_url",
            "raw_page_source",
            "supporting_quote",
            "confidence",
            "use",
        ):
            require_string(card, key, owner)
        if str(card["research_stage"]).strip().lower() != "s1":
            fail(f"{owner}.research_stage must be s1.")
        if str(card["knowledge_role"]).strip().lower() != "observation":
            fail(f"{owner}.knowledge_role must be observation.")
        material_role = str(card["material_role"]).strip().lower()
        if material_role not in material_role_counts:
            fail(
                f"{owner}.material_role must be topic_fact, reader_context, "
                "counter_signal or boundary_fact."
            )
        material_role_counts[material_role] += 1
        if card["source_type"] not in {"primary", "community", "analysis"}:
            fail(f"{owner}.source_type must be primary, community or analysis.")
        primary_count += int(card["source_type"] == "primary")
        card_id = str(card["id"]).strip()
        if card_id in ids:
            fail(f"Duplicate observation id: {card_id}")
        ids.add(card_id)
        host = host_of(str(card["source_url"]))
        if not host:
            fail(f"{owner}.source_url must be a concrete URL with a domain.")
        if is_google_search_url(str(card["source_url"])):
            fail(f"{owner}.source_url is a Google search page, not source evidence.")
        parsed_url = urlparse(str(card["source_url"]))
        path_segments = [segment for segment in parsed_url.path.split("/") if segment]
        if card["source_type"] == "primary" and (
            len(path_segments) < 2 or len(path_segments[-1]) < 3
        ):
            fail(
                f"{owner}.source_url must identify a concrete primary page, "
                "not a site root or listing page."
            )
        card_hosts.add(host)
        path = source_path(topic_dir, raw_root, str(card["raw_page_source"]), f"{owner}.raw_page_source")
        if path not in captured_paths:
            fail(
                f"{owner}.raw_page_source was not produced by a successful CDP "
                f"capture recorded in {raw_root / 'cdp_capture_manifest.json'}."
            )
        if host not in captured_pages[path]:
            fail(
                f"{owner}.source_url host {host} does not match the page actually "
                f"captured at {path}: {sorted(captured_pages[path])}."
            )
        reject_search_snapshot(path, f"{owner}.raw_page_source")
        role_paths[material_role].add(path)
        page_hosts.setdefault(path, set()).add(host)
        quote = normalize_evidence_text(str(card["supporting_quote"]))
        if len(quote) < MIN_QUOTE_CHARS:
            fail(f"{owner}.supporting_quote is too short for reliable lookup.")
        raw_text = normalize_evidence_text(path.read_text(encoding="utf-8", errors="replace"))
        if quote not in raw_text:
            fail(f"{owner}.supporting_quote was not found in {path}.")
        numeric_ids = validate_numeric_refs(
            card,
            owner,
            " ".join(
                str(card.get(key) or "")
                for key in ("claim", "supporting_quote", "use")
            ),
            numeric_claims,
        )
        numeric_card_count += int(bool(numeric_ids))

    reused = {
        str(path): sorted(hosts)
        for path, hosts in page_hosts.items()
        if len(hosts) > 1
    }
    if reused:
        fail(
            "One raw-page snapshot cannot represent several source domains: "
            + json.dumps(reused, ensure_ascii=False)
        )

    if len(card_hosts) < MIN_EVIDENCE_DOMAINS:
        fail(
            f"observation_cards must cite at least {MIN_EVIDENCE_DOMAINS} domains; "
            f"found {len(card_hosts)}."
        )
    if primary_count < 2:
        fail("observation_cards must contain at least 2 cards explicitly classified as primary.")

    if article_profile["mode"] == "life_insight":
        if material_role_counts["reader_context"] < 2 or len(role_paths["reader_context"]) < 2:
            fail(
                "life_insight requires at least 2 reader_context observation cards "
                "from 2 distinct pages about readers' real midlife conditions."
            )
        if (
            material_role_counts["counter_signal"]
            + material_role_counts["boundary_fact"]
            < 1
        ):
            fail("life_insight requires at least one counter_signal or boundary_fact card.")
        if material_role_counts["topic_fact"] > len(cards) // 2:
            fail(
                "life_insight topic_fact cards cannot exceed half of observation_cards; "
                "professional background facts must not dominate a life article."
            )
        if numeric_card_count > len(cards) // 2:
            fail(
                "life_insight numeric observation cards cannot exceed half of "
                "observation_cards; data must support rather than dominate the life material."
            )
    plan_map = blueprint["_material_plan_map"]
    for role, plan in plan_map.items():
        count = material_role_counts[role]
        if not int(plan["minimum_cards"]) <= count <= int(plan["maximum_cards"]):
            fail(
                f"{role} produced {count} cards; research_blueprint requires "
                f"{plan['minimum_cards']}-{plan['maximum_cards']}."
            )
    if numeric_card_count / len(cards) > float(blueprint["numeric_card_max_share"]):
        fail(
            "numeric observation-card share exceeds "
            "research_blueprint.numeric_card_max_share."
        )

    for key in ("fact_conflicts", "known_unknowns", "trust_boundaries"):
        values = require_list(pack, key, "source_pack.json")
        if any(not isinstance(value, str) or not value.strip() for value in values):
            fail(f"{key} must contain non-empty strings.")

    selected_files = require_list(pack, "selected_source_files", "source_pack.json")
    if not MIN_SELECTED_SOURCE_FILES <= len(selected_files) <= MAX_SELECTED_SOURCE_FILES:
        fail(
            f"selected_source_files must contain {MIN_SELECTED_SOURCE_FILES}-"
            f"{MAX_SELECTED_SOURCE_FILES} items; found {len(selected_files)}."
        )
    resolved = [
        source_path(topic_dir, raw_root, str(value), f"selected_source_files[{index}]")
        for index, value in enumerate(selected_files)
    ]
    for index, path in enumerate(resolved):
        if path not in captured_paths:
            fail(
                f"selected_source_files[{index}] was not produced by a successful "
                "CDP capture."
            )
        reject_search_snapshot(path, f"selected_source_files[{index}]")
        captured_urls = [
            url
            for url in captured_pages[path]
            if url
        ]
        if any(is_google_host(host) for host in captured_urls):
            fail(
                f"selected_source_files[{index}] is a Google page; "
                "open and save the original source instead."
            )
    if len(set(resolved)) != len(resolved):
        fail("selected_source_files must not contain duplicates.")
    selected_set = set(resolved)
    selected_hosts = {
        host_of(str(card["source_url"]))
        for card in cards
        if source_path(
            topic_dir,
            raw_root,
            str(card["raw_page_source"]),
            "observation_cards.raw_page_source",
        )
        in selected_set
    }
    if len(selected_hosts) < MIN_EVIDENCE_DOMAINS:
        fail(
            f"selected_source_files must cover at least {MIN_EVIDENCE_DOMAINS} domains; "
            f"found {len(selected_hosts)}."
        )
    if article_profile["mode"] == "life_insight":
        selected_reader_context = role_paths["reader_context"] & selected_set
        selected_limits = (
            role_paths["counter_signal"] | role_paths["boundary_fact"]
        ) & selected_set
        if len(selected_reader_context) < 2:
            fail(
                "life_insight selected_source_files must include at least "
                "2 reader_context pages."
            )
        if not selected_limits:
            fail(
                "life_insight selected_source_files must include a counter_signal "
                "or boundary_fact page."
            )

    receipt = write_receipt(
        topic_dir,
        STAGE1_RECEIPT,
        {
            "stage": "stage1_observation",
            "topic_dir": str(topic_dir),
            "raw_pages_files": len(raw_files),
            "raw_pages_bytes": raw_page_bytes,
            "captured_pages": len(captured_paths),
            "capture_manifest": "research/raw_pages/cdp_capture_manifest.json",
            "observation_cards": len(cards),
            "observation_domains": sorted(card_hosts),
            "primary_cards": primary_count,
            "material_role_counts": material_role_counts,
            "numeric_observation_cards": numeric_card_count,
            "selected_source_files": len(resolved),
            "selected_domains": sorted(selected_hosts),
            "numeric_claims": len(numeric_claims),
            "user_materials": len(user_materials),
            "article_mode": article_profile["mode"],
            "article_subtype": article_profile["subtype"],
            "visual_mode": article_profile["visual_mode"],
            "article_route": article_route_key(article_profile),
            "research_blueprint_id": blueprint["blueprint_id"],
        },
    )
    print(
        json.dumps(
            {
                "stage": "stage1_observation",
                "topic_dir": str(topic_dir),
                "observation_cards": len(cards),
                "observation_domains": sorted(card_hosts),
                "primary_cards": primary_count,
                "material_role_counts": material_role_counts,
                "numeric_observation_cards": numeric_card_count,
                "numeric_claims": len(numeric_claims),
                "user_materials": len(user_materials),
                "article_mode": article_profile["mode"],
                "article_subtype": article_profile["subtype"],
                "article_route": article_route_key(article_profile),
                "research_blueprint_id": blueprint["blueprint_id"],
                "receipt": str(receipt),
                "status": "passed",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
