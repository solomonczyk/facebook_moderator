"""Test worker config: gates, validation, own-group detection."""

import sys
sys.path.insert(0, '.')

from app.account_worker.config import WorkerConfig


def test_worker_disabled_by_default():
    cfg = WorkerConfig()
    assert cfg.own_group_worker_enabled is False


def test_dangerous_gates_disabled():
    cfg = WorkerConfig()
    assert cfg.auto_post_enabled is False
    assert cfg.auto_comment_enabled is False
    assert cfg.auto_message_enabled is False
    assert cfg.captcha_bypass_enabled is False
    assert cfg.stealth_browser_enabled is False
    assert cfg.fake_account_enabled is False


def test_cannot_start_without_url():
    cfg = WorkerConfig()
    cfg.own_group_worker_enabled = True
    allowed, blockers = cfg.can_start()
    assert allowed is False
    assert any("url" in b.lower() for b in blockers)


def test_cannot_start_with_dangerous_gates():
    cfg = WorkerConfig()
    cfg.own_group_worker_enabled = True
    cfg.own_group_url = "https://www.facebook.com/groups/992369183697618"
    cfg.auto_post_enabled = True
    allowed, blockers = cfg.can_start()
    assert allowed is False
    assert any("auto_post" in b for b in blockers)


def test_can_start_when_all_gates_ok():
    cfg = WorkerConfig()
    cfg.own_group_worker_enabled = True
    cfg.own_group_url = "https://www.facebook.com/groups/992369183697618"
    allowed, blockers = cfg.can_start()
    assert allowed is True
    assert len(blockers) == 0


def test_is_own_group_matches():
    cfg = WorkerConfig()
    cfg.own_group_url = "https://www.facebook.com/groups/992369183697618"
    assert cfg.is_own_group("https://www.facebook.com/groups/992369183697618/posts/123") is True


def test_is_own_group_rejects_external():
    cfg = WorkerConfig()
    cfg.own_group_url = "https://www.facebook.com/groups/992369183697618"
    assert cfg.is_own_group("https://www.facebook.com/groups/999999999999/posts/456") is False


if __name__ == '__main__':
    test_worker_disabled_by_default()
    test_dangerous_gates_disabled()
    test_cannot_start_without_url()
    test_cannot_start_with_dangerous_gates()
    test_can_start_when_all_gates_ok()
    test_is_own_group_matches()
    test_is_own_group_rejects_external()
    print("[PASS] All worker config tests passed")
