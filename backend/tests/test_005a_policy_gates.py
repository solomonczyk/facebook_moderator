"""Test policy gates: all dangerous gates disabled by default."""

import sys
sys.path.insert(0, '.')

from app.runtime_agent.config import RuntimeConfig
from app.runtime_agent.policy import PolicyEngine


def test_all_gates_disabled_by_default():
    cfg = RuntimeConfig()
    assert cfg.facebook_account_worker_enabled is False
    assert cfg.facebook_auto_reply_enabled is False
    assert cfg.facebook_auto_post_enabled is False
    assert cfg.facebook_auto_comment_enabled is False
    assert cfg.facebook_auto_message_enabled is False
    assert cfg.captcha_bypass_enabled is False
    assert cfg.stealth_browser_enabled is False
    assert cfg.fake_account_enabled is False
    assert cfg.review_auto_publish_enabled is False
    assert cfg.production_accepted is False


def test_hard_forbidden_always_false():
    cfg = RuntimeConfig()
    engine = PolicyEngine(cfg)
    assert engine.is_hard_forbidden("captcha_bypass") is True
    assert engine.is_hard_forbidden("stealth_evasion") is True
    assert engine.is_hard_forbidden("fake_accounts") is True
    assert engine.is_hard_forbidden("credential_extraction") is True
    assert engine.is_hard_forbidden("fake_vacancies") is True
    assert engine.is_hard_forbidden("fake_reviews") is True


def test_auto_post_blocked_by_default():
    engine = PolicyEngine(RuntimeConfig())
    assert engine.can_auto_post() is False


def test_auto_reply_blocked_by_default():
    engine = PolicyEngine(RuntimeConfig())
    assert engine.can_auto_reply() is False


def test_operator_approval_required():
    engine = PolicyEngine(RuntimeConfig())
    assert engine.requires_operator_approval("publish_own_group_post") is True
    assert engine.requires_operator_approval("reply_to_comment") is True
    assert engine.requires_operator_approval("create_digest_post") is True


if __name__ == '__main__':
    test_all_gates_disabled_by_default()
    test_hard_forbidden_always_false()
    test_auto_post_blocked_by_default()
    test_auto_reply_blocked_by_default()
    test_operator_approval_required()
    print("[PASS] All policy gates tests passed")
