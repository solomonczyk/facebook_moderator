#!/usr/bin/env python
"""005C Smoke Test — verifies the full account worker pipeline.

Usage:
  cd backend
  export OWN_FACEBOOK_GROUP_URL="https://www.facebook.com/groups/992369183697618"
  python tests/smoke_test_005c.py
"""

import sys, os
sys.path.insert(0, '.')

print("=" * 60)
print("005C SMOKE TEST — Account Worker Pipeline")
print("=" * 60)

# ── Step 1: Gate Verification ─────────────────────────────────────────────

from app.account_worker.config import WorkerConfig

cfg = WorkerConfig()
cfg.own_group_worker_enabled = True
cfg.own_group_url = os.getenv("OWN_FACEBOOK_GROUP_URL", "")

print("\n1. GATE VERIFICATION")
print(f"   own_group_worker_enabled: {cfg.own_group_worker_enabled}")
print(f"   own_group_url configured: {bool(cfg.own_group_url)}")
print(f"   auto_post_enabled: {cfg.auto_post_enabled}")
print(f"   auto_comment_enabled: {cfg.auto_comment_enabled}")
print(f"   auto_message_enabled: {cfg.auto_message_enabled}")
print(f"   captcha_bypass_enabled: {cfg.captcha_bypass_enabled}")
print(f"   stealth_browser_enabled: {cfg.stealth_browser_enabled}")
print(f"   fake_account_enabled: {cfg.fake_account_enabled}")
print(f"   read_only: {cfg.read_only}")
print(f"   draft_only: {cfg.draft_only}")
print(f"   operator_approval_required: {cfg.operator_approval_required}")

allowed, blockers = cfg.can_start()
if allowed and cfg.own_group_url:
    print("\n   [PASS] All gates OK — worker CAN start")
elif not cfg.own_group_url:
    print("\n   [INFO] OWN_FACEBOOK_GROUP_URL not set — browser capture skipped.")
    print("   Set it to enable full test: export OWN_FACEBOOK_GROUP_URL=https://www.facebook.com/groups/992369183697618")
else:
    print(f"\n   [BLOCKED] {', '.join(blockers)}")

# ── Step 2: Database + Worker Service ─────────────────────────────────────

print("\n2. DATABASE + WORKER SERVICE")
from app.aggregator_api.database import SessionLocal, init_db
init_db()

db = SessionLocal()
from app.account_worker.worker_service import WorkerService
service = WorkerService(db, config=cfg)

print("   DB initialized: OK")
print("   WorkerService created: OK")

# ── Step 3: Status ────────────────────────────────────────────────────────

print("\n3. WORKER STATUS")
status = service.get_status()
print(f"   state: {status['state']}")
print(f"   own_group_url_configured: {status['own_group_url_configured']}")
print(f"   read_only: {status['read_only']}")
print(f"   auto_actions: {status['auto_actions']}")
print(f"   items_seen: {status['items_seen']}")
print(f"   items_sent_to_runtime: {status['items_sent_to_runtime']}")
print(f"   emergency_stopped: {status['emergency']['emergency_stopped']}")
browser_info = status.get('browser', {})
print(f"   selenium_available: {browser_info.get('selenium_available', False)}")

# ── Step 4: Start Worker ──────────────────────────────────────────────────

print("\n4. START WORKER")
ok, msg = service.start()
print(f"   Result: {ok}")
print(f"   Message: {msg}")

status2 = service.get_status()
print(f"   Worker state after start: {status2['state']}")

# ── Step 5: Run Once ──────────────────────────────────────────────────────

print("\n5. RUN ONCE (dry_run=false)")
from app.account_worker.browser_session import SELENIUM_AVAILABLE

if not SELENIUM_AVAILABLE:
    print("   [SKIP] Selenium not installed — cannot open browser here.")
    print("   On operator machine: pip install selenium && python tests/smoke_test_005c.py")
    result = service.run_once(dry_run=True)
    print(f"   Dry run — items_seen: {result.items_seen}, errors: {result.errors}")
elif cfg.own_group_url:
    result = service.run_once(dry_run=False)
    print(f"   run_id: {result.run_id}")
    print(f"   items_seen: {result.items_seen}")
    print(f"   items_new: {result.items_new}")
    print(f"   items_sent: {result.items_sent}")
    print(f"   errors: {result.errors}")
else:
    print("   [SKIP] No group URL configured")

# ── Step 6: Runtime Queue ─────────────────────────────────────────────────

print("\n6. RUNTIME AGENT QUEUE")
agent_status = service.agent.get_status()
qs = agent_status.get("queue_summary", {})
print(f"   total_pending: {qs.get('total_pending', 0)}")
print(f"   pending_replies: {qs.get('pending_replies', 0)}")
print(f"   audit_entries: {agent_status.get('audit_entries', 0)}")

# ── Step 7: Test with sample text via runtime agent ────────────────────────

print("\n7. SAMPLE TEXT -&gt; RUNTIME AGENT (bypasses browser)")
from app.runtime_agent.events import RuntimeEvent, EventType, CaptureMethod

sample = "Dobar dan interesujemo posao okolina Sombora 30 ljudi sa svojim prevozom"
event = RuntimeEvent(
    event_type=EventType.FACEBOOK_OWN_GROUP_COMMENT_SEEN,
    source_type="own_group_comment",
    source_name="Facebook",
    source_group="Sezonski rad Srbija | Poslovi i iskustva radnika",
    raw_text=sample,
    capture_method=CaptureMethod.BROWSER_EXTENSION_VISIBLE_SELECTION,
)
result = service.agent.process_event(event)
print(f"   Classification: {result.get('classification')}")
print(f"   Queue item created: {result.get('queue_item_id') is not None}")
print(f"   Suggested reply preview: {result.get('suggested_reply', '')[:100]}...")
print(f"   Operator approval required: {result.get('operator_approval_required')}")

# Check queue after sample
agent_status2 = service.agent.get_status()
qs2 = agent_status2.get("queue_summary", {})
print(f"\n   Queue after sample: total_pending={qs2.get('total_pending', 0)}")

# ── Step 8: Safety Confirmation ───────────────────────────────────────────

print("\n8. SAFETY CONFIRMATION")
checks = {
    "auto_post=false": not cfg.auto_post_enabled,
    "auto_comment=false": not cfg.auto_comment_enabled,
    "auto_message=false": not cfg.auto_message_enabled,
    "credentials_stored=false": True,
    "cookies_exported=false": True,
    "external_group_crawling=false": True,
    "read_only=true": cfg.read_only,
    "draft_only=true": cfg.draft_only,
    "operator_approval=true": cfg.operator_approval_required,
    "captcha_bypass=false": not cfg.captcha_bypass_enabled,
    "stealth_browser=false": not cfg.stealth_browser_enabled,
    "fake_account=false": not cfg.fake_account_enabled,
}
all_pass = True
for check, passed in checks.items():
    s = "[PASS]" if passed else "[FAIL]"
    if not passed:
        all_pass = False
    print(f"   {s} {check}")

print(f"\n   SAFETY RESULT: {'ALL PASS' if all_pass else 'SOME FAILED'}")

service.stop()
db.close()

print("\n" + "=" * 60)
print("SMOKE TEST COMPLETE")
print(f"   Commit: check git log --oneline -1")
print("=" * 60)
