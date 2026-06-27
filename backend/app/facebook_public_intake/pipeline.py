"""Public Facebook intake pipeline orchestrator.

Flow: discovery → screenshot capture → OCR extraction → dedup → intake API.
"""

import os
import json
import time
import logging
from datetime import datetime
from dataclasses import dataclass, field

from .config import PublicIntakeConfig
from .discovery import CandidateGroup, get_seed_groups, mark_checked, to_dict as group_to_dict
from .screenshotter import PublicScreenshotter, ScreenshotResult
from .ocr_extractor import OCRExtractor, ExtractedCandidate
from .deduplicator import Deduplicator

logger = logging.getLogger("sezonski.public_intake.pipeline")


@dataclass
class PipelineResult:
    run_id: str = field(default_factory=lambda: f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    finished_at: str = ""
    dry_run: bool = True
    groups_checked: int = 0
    public_groups_found: int = 0
    login_required_groups: int = 0
    blocked_groups: int = 0
    screenshots_created: int = 0
    ocr_candidates_found: int = 0
    candidates_sent_to_intake: int = 0
    queue_items_created: int = 0
    duplicates_skipped: int = 0
    groups_detail: list[dict] = field(default_factory=list)
    candidates: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "dry_run": self.dry_run,
            "groups_checked": self.groups_checked,
            "public_groups_found": self.public_groups_found,
            "login_required_groups": self.login_required_groups,
            "blocked_groups": self.blocked_groups,
            "screenshots_created": self.screenshots_created,
            "ocr_candidates_found": self.ocr_candidates_found,
            "candidates_sent_to_intake": self.candidates_sent_to_intake,
            "queue_items_created": self.queue_items_created,
            "duplicates_skipped": self.duplicates_skipped,
            "groups_detail": self.groups_detail,
            "candidates": self.candidates,
            "errors": self.errors,
        }


class PublicIntakePipeline:
    """Orchestrates the full public Facebook intake pipeline."""

    def __init__(self, config: PublicIntakeConfig | None = None):
        self.config = config or PublicIntakeConfig()
        self.screenshotter = PublicScreenshotter(self.config)
        self.extractor = OCRExtractor(self.config)
        self.deduplicator = Deduplicator()
        # For API intake integration, lazy init
        self._intake_fn = None

    def run(self, max_groups: int | None = None, dry_run: bool | None = None) -> PipelineResult:
        """Run the full pipeline: discover → screenshot → extract → dedup → intake."""
        if dry_run is not None:
            self.config.dry_run = dry_run

        result = PipelineResult(dry_run=self.config.dry_run)

        # ── Pre-flight safety check ──────────────────────────────────────────
        ok, reason = self.config.can_proceed()
        if not ok:
            result.errors.append(f"SAFETY BLOCK: {reason}")
            result.finished_at = datetime.utcnow().isoformat()
            return result

        max_g = max_groups or self.config.max_groups_per_run
        logger.info(f"Starting public intake pipeline (dry_run={self.config.dry_run}, max_groups={max_g})")

        # ── Step 1: Discovery ────────────────────────────────────────────────
        groups = get_seed_groups(max_g)
        result.groups_checked = len(groups)

        # ── Step 2: Screenshot + Extract per group ───────────────────────────
        for group in groups:
            logger.info(f"Processing: {group.group_name} ({group.url})")
            group_detail = group_to_dict(group)

            if self.config.dry_run:
                # Dry run — mark as "would check"
                mark_checked(group, "public")
                result.public_groups_found += 1
                group_detail["access_status"] = "public"
                group_detail["screenshots"] = ["[DRY RUN — would capture]"]
                group_detail["candidates_found"] = "[DRY RUN — would extract]"
                result.groups_detail.append(group_detail)
                continue

            # Real run — capture screenshots
            screenshots = self.screenshotter.capture(
                url=group.url,
                group_name=group.group_name,
                max_screenshots=self.config.max_screenshots_per_group,
            )

            # Determine access status from results
            if not screenshots or all(not s.success for s in screenshots):
                if any("login_required" in (s.error or "") for s in screenshots):
                    mark_checked(group, "login_required")
                    result.login_required_groups += 1
                    group_detail["access_status"] = "login_required"
                else:
                    mark_checked(group, "blocked")
                    result.blocked_groups += 1
                    group_detail["access_status"] = "blocked"
                group_detail["screenshots"] = [s.to_dict() for s in screenshots]
                result.groups_detail.append(group_detail)
                continue

            mark_checked(group, "public")
            result.public_groups_found += 1
            result.screenshots_created += len([s for s in screenshots if s.success])
            group_detail["access_status"] = "public"
            group_detail["screenshots"] = [s.to_dict() for s in screenshots]

            # ── Step 3: Extract text candidates ──────────────────────────────
            candidates = self.extractor.extract_from_screenshots(
                screenshot_results=screenshots,
                group_name=group.group_name,
                source_url=group.url,
            )
            result.ocr_candidates_found += len(candidates)
            group_detail["candidates_found"] = len(candidates)

            # ── Step 4: Deduplicate ──────────────────────────────────────────
            new_candidates = []
            for c in candidates:
                if not self.deduplicator.is_duplicate(c.raw_text, c.source_url):
                    self.deduplicator.mark_seen(c.raw_text, c.source_url)
                    new_candidates.append(c)
                else:
                    result.duplicates_skipped += 1

            # ── Step 5: Send to intake API ───────────────────────────────────
            for c in new_candidates:
                intake_result = self._send_to_intake(c)
                if intake_result:
                    result.candidates_sent_to_intake += 1
                    if intake_result.get("action_id"):
                        result.queue_items_created += 1
                result.candidates.append(c.to_dict())

            result.groups_detail.append(group_detail)

            # Rate limit between groups
            if group != groups[-1]:
                time.sleep(self.config.min_delay_between_groups_seconds)

        # ── Cleanup ─────────────────────────────────────────────────────────
        self.screenshotter.close()

        # Save extracted candidates to file
        if not self.config.dry_run and result.ocr_candidates_found > 0:
            all_candidates = [
                ExtractedCandidate(
                    source_url=c["source_url"],
                    group_name=c["group_name"],
                    screenshot_path=c["screenshot_path"],
                    raw_text=c["raw_text"],
                )
                for c in result.candidates
            ]
            if all_candidates:
                self.extractor.save_candidates(all_candidates)

        result.finished_at = datetime.utcnow().isoformat()
        logger.info(
            f"Pipeline complete: {result.public_groups_found} public, "
            f"{result.screenshots_created} screenshots, "
            f"{result.ocr_candidates_found} candidates, "
            f"{result.candidates_sent_to_intake} sent to intake, "
            f"{result.queue_items_created} queue items, "
            f"{result.duplicates_skipped} duplicates skipped"
        )
        return result

    def _send_to_intake(self, candidate: ExtractedCandidate) -> dict | None:
        """Send an extracted candidate to the TASK 009 intake endpoint."""
        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would send to intake: {candidate.raw_text[:100]}...")
            return {"status": "dry_run", "action_id": None}

        try:
            import httpx
            intake_url = "http://127.0.0.1:8000/api/intake/manual"
            payload = {
                "source": "facebook_public_screenshot",
                "text": candidate.raw_text,
                "source_url": candidate.source_url,
                "language": "sr",
            }
            resp = httpx.post(intake_url, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Sent to intake: {candidate.candidate_id} → action_id={data.get('action_id')}")
                return data
            else:
                logger.warning(f"Intake returned {resp.status_code}: {resp.text[:200]}")
                return None
        except Exception as e:
            logger.warning(f"Intake request failed (server may not be running): {e}")
            return None
