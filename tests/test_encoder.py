from amrdiag.encoder import detect_stalls, simulate_encoder


def test_healthy_run_has_no_stalls():
    assert detect_stalls(simulate_encoder(stall_at=None)) == []


def test_frozen_counter_found():
    stalls = detect_stalls(simulate_encoder(stall_at=(4.0, 6.0)))
    assert len(stalls) == 1
    assert 1.8 <= stalls[0].duration <= 2.1


def test_no_stall_when_not_commanded():
    rows = [(i / 20, 0.0, 100) for i in range(50)]
    assert detect_stalls(rows) == []
