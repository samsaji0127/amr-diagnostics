"""Battery (BMS) voltage-sag and internal-resistance analysis."""
import random
from dataclasses import dataclass, field


@dataclass
class SagEvent:
    start_t: float
    end_t: float
    min_v: float


@dataclass
class BmsReport:
    min_voltage: float
    sags: list = field(default_factory=list)
    resistance_mohm: float = 0.0  # 90th percentile of step estimates

    def healthy(self, r_max_mohm=120.0) -> bool:
        return not self.sags and self.resistance_mohm <= r_max_mohm


def analyze_bms(samples, v_min=42.0, min_step_a=5.0) -> BmsReport:
    """samples: list of (t, voltage_V, current_A), time-ordered.

    Sag = contiguous run of samples below v_min.
    Resistance is estimated as -dV/dI across steps where current changes by
    at least min_step_a; the 90th percentile is reported so one noisy step
    doesn't dominate."""
    sags, run = [], None
    for t, v, _ in samples:
        if v < v_min:
            run = run or [t, t, v]
            run[1], run[2] = t, min(run[2], v)
        elif run:
            sags.append(SagEvent(*run))
            run = None
    if run:
        sags.append(SagEvent(*run))

    estimates = []
    for (_, v0, i0), (_, v1, i1) in zip(samples, samples[1:]):
        di = i1 - i0
        if abs(di) >= min_step_a:
            estimates.append(-(v1 - v0) / di * 1000.0)
    estimates.sort()
    r = estimates[int(0.9 * (len(estimates) - 1))] if estimates else 0.0

    return BmsReport(
        min_voltage=min((v for _, v, _ in samples), default=0.0),
        sags=sags,
        resistance_mohm=round(r, 1),
    )


def simulate_bms(duration=12.0, hz=10, ocv=48.0, r_mohm=50.0, weak_after=None, seed=1):
    """Pulsed-load discharge. weak_after=(t, r_mohm) raises resistance from time t."""
    rng = random.Random(seed)
    out = []
    for i in range(int(duration * hz)):
        t = round(i / hz, 3)
        current = 30.0 if (t % 5.0) < 1.0 and t >= 1.0 else 5.0
        r = weak_after[1] if weak_after and t >= weak_after[0] else r_mohm
        v = ocv - current * r / 1000.0 + rng.uniform(-0.01, 0.01)
        out.append((t, round(v, 3), current))
    return out
