from amrdiag.lidar import analyze_scan, simulate_scan


def test_clean_scan_is_healthy():
    rep = analyze_scan(simulate_scan())
    assert rep.healthy and rep.dropout_pct == 0


def test_dropout_detected():
    rep = analyze_scan(simulate_scan(dropout=0.2))
    assert rep.dropout_pct == 20.0 and not rep.healthy


def test_spikes_detected():
    rep = analyze_scan(simulate_scan(spikes=15))
    assert rep.spikes >= 10 and not rep.healthy


def test_all_invalid():
    rep = analyze_scan([float("nan")] * 10)
    assert rep.valid == 0 and rep.dropout_pct == 100.0
