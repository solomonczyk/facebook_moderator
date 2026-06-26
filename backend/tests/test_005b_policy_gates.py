"""Test intake policy gates: all dangerous modes disabled by default."""

import sys
sys.path.insert(0, '.')

from app.runtime_intake.config import IntakeConfig
from app.runtime_intake.own_group_visible_adapter import OwnGroupVisibleAdapter


def test_safe_modes_enabled_by_default():
    cfg = IntakeConfig()
    assert cfg.manual_paste_enabled is True
    assert cfg.clipboard_intake_enabled is True
    assert cfg.selected_text_extension_enabled is True


def test_guarded_modes_disabled_by_default():
    cfg = IntakeConfig()
    assert cfg.own_group_visible_intake_enabled is False
    assert cfg.external_group_visible_intake_enabled is False
    assert cfg.facebook_account_worker_enabled is False


def test_dangerous_gates_disabled():
    cfg = IntakeConfig()
    assert cfg.auto_reply_enabled is False
    assert cfg.auto_post_enabled is False
    assert cfg.auto_comment_enabled is False
    assert cfg.auto_message_enabled is False
    assert cfg.captcha_bypass_enabled is False
    assert cfg.stealth_browser_enabled is False
    assert cfg.fake_account_enabled is False
    assert cfg.production_accepted is False


def test_operator_approval_required():
    cfg = IntakeConfig()
    assert cfg.operator_approval_required is True
    assert cfg.draft_only_by_default is True


def test_own_group_adapter_disabled():
    cfg = IntakeConfig()
    adapter = OwnGroupVisibleAdapter(cfg)
    assert adapter.enabled is False
    result = adapter.capture("url", "group", ["block"])
    assert result["success"] is False
    assert "disabled" in result["error"]


if __name__ == '__main__':
    test_safe_modes_enabled_by_default()
    test_guarded_modes_disabled_by_default()
    test_dangerous_gates_disabled()
    test_operator_approval_required()
    test_own_group_adapter_disabled()
    print("[PASS] All policy gates tests passed")
