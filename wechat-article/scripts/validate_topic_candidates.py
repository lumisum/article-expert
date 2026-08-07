#!/usr/bin/env python3
"""Validate Stage 0 topic-candidate files and captured discovery pages."""

from __future__ import annotations

import argparse
import json

from validation_lib import fail, load_json, require_list, require_object, require_string, resolve_topic_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir")
    args = parser.parse_args()
    topic_dir = resolve_topic_dir(args.topic_dir, "research/topic_candidates.json")
    research_dir = topic_dir / "research"
    json_path = research_dir / "topic_candidates.json"
    md_path = research_dir / "topic_candidates.md"
    capture_dir = research_dir / "raw_pages"

    if not md_path.is_file():
        fail(f"Missing Stage 0 summary: {md_path}")
    if not capture_dir.is_dir():
        fail(f"Missing Stage 0 captures: {capture_dir}")
    captures = [p for p in capture_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".txt", ".html", ".htm"}]
    if len(captures) < 5:
        fail(f"Stage 0 requires at least 5 captured text pages, got {len(captures)}.")

    package = load_json(json_path)
    if not isinstance(package, dict) or package.get("stage") != "topic_candidates":
        fail('topic_candidates.json.stage must be "topic_candidates".')
    require_string(package, "scan_id", "topic_candidates.json")
    scan = require_object(package, "scan_summary", "topic_candidates.json")
    planned = scan.get("planned_url_count")
    successful = scan.get("successful_capture_count")
    if not isinstance(planned, int) or not 6 <= planned <= 10:
        fail("scan_summary.planned_url_count must be an integer from 6 to 10.")
    if not isinstance(successful, int) or successful < 5 or successful > min(planned, len(captures)):
        fail("scan_summary.successful_capture_count is inconsistent with captured files.")
    categories = require_list(scan, "source_categories", "scan_summary")
    if len({str(item).strip() for item in categories}) < 3:
        fail("scan_summary.source_categories must contain at least 3 distinct values.")

    candidates = package.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 3:
        fail("topic_candidates.json.candidates must contain exactly 3 items.")
    titles: set[str] = set()
    for index, candidate in enumerate(candidates, start=1):
        owner = f"candidates[{index - 1}]"
        if not isinstance(candidate, dict) or candidate.get("rank") != index:
            fail(f"{owner}.rank must be {index}.")
        for key in ("topic_id", "article_type", "topic_title", "material_anchor", "reader_problem", "reader_search_query", "reader_payoff", "evergreen_reason", "core_hook", "traffic_case"):
            require_string(candidate, key, owner)
        if candidate["article_type"] not in {
            "life_insight",
            "tech_event_business_investment",
            "tech_practical_playbook",
        }:
            fail(
                f"{owner}.article_type must be life_insight, "
                "tech_event_business_investment or tech_practical_playbook."
            )
        payoff_types = require_list(candidate, "payoff_types", owner)
        if not payoff_types or any(not isinstance(value, str) or not value.strip() for value in payoff_types):
            fail(f"{owner}.payoff_types must contain at least one non-empty value.")
        payoff = require_object(candidate, "payoff_detail", owner)
        for key in ("before_state", "after_state", "use_scene", "proof_basis", "boundary"):
            require_string(payoff, key, f"{owner}.payoff_detail")
        audience = require_object(candidate, "audience_expansion", owner)
        for key in (
            "core_audience",
            "adjacent_audience",
            "broad_audience",
            "familiar_entry",
            "overreach_boundary",
        ):
            require_string(audience, key, f"{owner}.audience_expansion")
        title = str(candidate["topic_title"]).strip()
        if title in titles:
            fail(f"Duplicate topic_title: {title}")
        titles.add(title)
        evidence = require_list(candidate, "evidence", owner)
        for evidence_index, item in enumerate(evidence):
            if not isinstance(item, dict):
                fail(f"{owner}.evidence[{evidence_index}] must be an object.")
            require_string(item, "url", f"{owner}.evidence[{evidence_index}]")
            require_string(item, "visible_signal", f"{owner}.evidence[{evidence_index}]")

    print(json.dumps({"stage": "stage0_topic_candidates", "scan_dir": str(topic_dir), "captured_pages": len(captures), "candidates": 3, "status": "passed"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
