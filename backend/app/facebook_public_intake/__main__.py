"""CLI entry point for public Facebook intake pipeline.

Usage:
    python -m app.facebook_public_intake --dry-run
    python -m app.facebook_public_intake --max-groups 5 --screenshots-per-group 3
    python -m app.facebook_public_intake --no-dry-run --max-groups 3
"""

import sys
import os
import json
import argparse
import logging

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("sezonski.public_intake")


def main():
    parser = argparse.ArgumentParser(
        description="Controlled public Facebook intake — discover, screenshot, extract, queue",
    )
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Dry run mode (default: True — no real screenshots)")
    parser.add_argument("--no-dry-run", action="store_true", default=False,
                        help="Disable dry run — actually capture screenshots")
    parser.add_argument("--max-groups", type=int, default=5,
                        help="Maximum groups to check (default: 5)")
    parser.add_argument("--screenshots-per-group", type=int, default=3,
                        help="Max screenshots per group (default: 3)")
    parser.add_argument("--output", type=str, default="",
                        help="Output JSON file path for results")
    parser.add_argument("--screenshot-dir", type=str, default="artifacts/screenshots",
                        help="Directory for screenshots")

    args = parser.parse_args()

    dry_run = not args.no_dry_run

    print("=" * 60)
    print("PUBLIC FACEBOOK INTAKE PIPELINE")
    print(f"  Dry run: {dry_run}")
    print(f"  Max groups: {args.max_groups}")
    print(f"  Screenshots per group: {args.screenshots_per_group}")
    print("=" * 60)

    from app.facebook_public_intake.config import PublicIntakeConfig
    from app.facebook_public_intake.pipeline import PublicIntakePipeline

    config = PublicIntakeConfig(
        dry_run=dry_run,
        max_groups_per_run=args.max_groups,
        max_screenshots_per_group=args.screenshots_per_group,
        screenshot_dir=args.screenshot_dir,
    )

    # Pre-flight check
    ok, reason = config.can_proceed()
    if not ok:
        print(f"\nSAFETY BLOCK: {reason}")
        print("Pipeline aborted. No Facebook access attempted.")
        sys.exit(1)

    print(f"Safety check: {reason}")
    print()

    # Run pipeline
    pipeline = PublicIntakePipeline(config)
    result = pipeline.run()

    # Print summary
    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"  Groups checked:       {result.groups_checked}")
    print(f"  Public groups found:  {result.public_groups_found}")
    print(f"  Login required:       {result.login_required_groups}")
    print(f"  Blocked:              {result.blocked_groups}")
    print(f"  Screenshots created:  {result.screenshots_created}")
    print(f"  Candidates found:     {result.ocr_candidates_found}")
    print(f"  Sent to intake:       {result.candidates_sent_to_intake}")
    print(f"  Queue items created:  {result.queue_items_created}")
    print(f"  Duplicates skipped:   {result.duplicates_skipped}")
    if result.errors:
        print(f"  Errors:               {len(result.errors)}")
        for e in result.errors:
            print(f"    - {e}")
    print()

    # Save results
    output_data = result.to_dict()
    output_path = args.output or f"artifacts/pipeline_result_{result.run_id}.json"
    os.makedirs(os.path.dirname(output_path) or "artifacts", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Full results saved to: {output_path}")

    # Group details
    print()
    for g in result.groups_detail:
        status_icon = "public" if g.get("access_status") == "public" else "blocked"
        print(f"  [{status_icon}] {g['group_name']}")
        print(f"         {g['url']}")
        if g.get("candidates_found"):
            print(f"         Candidates: {g['candidates_found']}")
        print()

    print("Pipeline complete. Operator approval required for all queue items.")


if __name__ == "__main__":
    main()
