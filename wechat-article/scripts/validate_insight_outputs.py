#!/usr/bin/env python3
"""Validate the dedicated Spark, wisdom and practice stage."""

from __future__ import annotations

import argparse
import json

from validate_final_outputs import validate_insight_research
from validation_lib import (
    STAGE1_RECEIPT,
    STAGE2_RECEIPT,
    STAGE3_RECEIPT,
    clear_receipt,
    fail,
    require_receipt,
    resolve_topic_dir,
    write_receipt,
    article_route_key,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic-dir")
    args = parser.parse_args()
    topic_dir = resolve_topic_dir(args.topic_dir, "research/source_pack.json")
    clear_receipt(topic_dir, STAGE3_RECEIPT)
    require_receipt(topic_dir, STAGE1_RECEIPT, next_stage="Stage 3 insight")
    stage2_receipt = require_receipt(
        topic_dir,
        STAGE2_RECEIPT,
        next_stage="Stage 3 insight",
    )
    (
        wisdom_count,
        practice_card_count,
        numeric_claims,
        user_material_ids,
        article_profile,
        spark_id,
        publish_thesis,
    ) = validate_insight_research(topic_dir)
    if str(stage2_receipt.get("spark_id") or "").strip().upper() != spark_id:
        fail("Stage 2 receipt does not match the current Spark.")
    if (
        stage2_receipt.get("article_mode") != article_profile["mode"]
        or stage2_receipt.get("article_subtype") != article_profile["subtype"]
    ):
        fail("Stage 2 receipt does not match the current article_profile.")
    if stage2_receipt.get("article_route") != article_route_key(article_profile):
        fail("Stage 2 receipt does not match the full article route.")

    receipt = write_receipt(
        topic_dir,
        STAGE3_RECEIPT,
        {
            "stage": "stage3_insight",
            "topic_dir": str(topic_dir),
            "spark_id": spark_id,
            "reviewed_descent_levels": int(stage2_receipt.get("descent_levels") or 0),
            "wisdom_candidates": wisdom_count,
            "practice_cards": practice_card_count,
            "numeric_claims": len(numeric_claims),
            "user_materials": len(user_material_ids),
            "article_mode": article_profile["mode"],
            "article_subtype": article_profile["subtype"],
            "article_route": article_route_key(article_profile),
            "publish_thesis": publish_thesis,
            "upstream_stage2_receipt": STAGE2_RECEIPT,
        },
    )
    print(
        json.dumps(
            {
                "stage": "stage3_insight",
                "topic_dir": str(topic_dir),
                "spark_id": spark_id,
                "reviewed_descent_levels": int(stage2_receipt.get("descent_levels") or 0),
                "wisdom_candidates": wisdom_count,
                "practice_cards": practice_card_count,
                "numeric_claims": len(numeric_claims),
                "article_mode": article_profile["mode"],
                "article_subtype": article_profile["subtype"],
                "article_route": article_route_key(article_profile),
                "receipt": str(receipt),
                "status": "passed",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
