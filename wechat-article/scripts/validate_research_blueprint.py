#!/usr/bin/env python3
"""Validate the Stage 1 pre-analysis route and material allocation."""

from __future__ import annotations

import argparse
import json

from validation_lib import resolve_topic_dir, validate_research_blueprint


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir")
    args = parser.parse_args()
    topic_dir = resolve_topic_dir(args.topic_dir, "research/research_blueprint.json")
    blueprint = validate_research_blueprint(topic_dir)
    print(
        json.dumps(
            {
                "stage": "stage1_preanalysis",
                "topic_dir": str(topic_dir),
                "blueprint_id": blueprint["blueprint_id"],
                "article_route": blueprint["_article_route"],
                "planned_page_range": blueprint["planned_page_range"],
                "planned_card_range": blueprint["planned_card_range"],
                "material_targets": {
                    role: plan["target_share"]
                    for role, plan in blueprint["_material_plan_map"].items()
                },
                "status": "passed",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
