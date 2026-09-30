from amrdiag.bms import analyze_bms, simulate_bms


def test_healthy_pack():
    rep = analyze_bms(simulate_bms())
    assert rep.healthy() and rep.sags == []
    assert 40 <= rep.resistance_mohm <= 60


def test_weak_pack_sags_under_load():
    rep = analyze_bms(simulate_bms(weak_after=(4.0, 250.0)))
    assert rep.sags and rep.min_voltage < 42.0
    assert not rep.healthy()


def test_high_resistance_without_sag():
    rep = analyze_bms(simulate_bms(r_mohm=150.0))
    assert rep.sags == [] and rep.resistance_mohm > 120
    assert not rep.healthy()


def test_empty_input():
    rep = analyze_bms([])
    assert rep.sags == [] and rep.resistance_mohm == 0.0
