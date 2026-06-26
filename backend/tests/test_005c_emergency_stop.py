"""Test emergency stop: prevents further runs."""

import sys
sys.path.insert(0, '.')

from app.account_worker.emergency_stop import EmergencyStop, WorkerEmergencyStopped


def test_not_stopped_by_default():
    es = EmergencyStop()
    assert es.is_stopped is False


def test_trigger_stops():
    es = EmergencyStop()
    es.trigger("test stop")
    assert es.is_stopped is True


def test_check_raises_when_stopped():
    es = EmergencyStop()
    es.trigger("test")
    try:
        es.check()
        assert False, "Should have raised"
    except WorkerEmergencyStopped:
        pass


def test_reset_clears():
    es = EmergencyStop()
    es.trigger("test")
    es.reset()
    assert es.is_stopped is False
    # Check should not raise
    es.check()


if __name__ == '__main__':
    test_not_stopped_by_default()
    test_trigger_stops()
    test_check_raises_when_stopped()
    test_reset_clears()
    print("[PASS] All emergency stop tests passed")
