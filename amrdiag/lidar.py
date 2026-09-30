"""LiDAR scan health analysis."""
import math
import random
from dataclasses import dataclass


@dataclass
class ScanReport:
    total: int
    valid: int
    dropout_pct: float
    spikes: int
    min_range: float
    max_range: float
    mean_range: float

    @property
    def healthy(self) -> bool:
        return self.dropout_pct < 10.0 and self.spikes < max(3, self.total * 0.02)


def analyze_scan(ranges, range_min=0.05, range_max=25.0, spike_jump=2.0) -> ScanReport:
    """Analyze one scan. Invalid = NaN/inf/out of [range_min, range_max].
    A spike is a beam that differs from both neighbours by more than
    `spike_jump` metres (an isolated outlier)."""
    valid_flags = [
        isinstance(r, (int, float)) and math.isfinite(r) and range_min <= r <= range_max
        for r in ranges
    ]
    vals = [r for r, ok in zip(ranges, valid_flags) if ok]
    total = len(ranges)
    if not vals:
        return ScanReport(total, 0, 100.0 if total else 0.0, 0, 0.0, 0.0, 0.0)

    spikes = 0
    for i in range(1, total - 1):
        if valid_flags[i - 1] and valid_flags[i] and valid_flags[i + 1]:
            a, b, c = ranges[i - 1], ranges[i], ranges[i + 1]
            if abs(b - a) > spike_jump and abs(b - c) > spike_jump:
                spikes += 1

    return ScanReport(
        total=total,
        valid=len(vals),
        dropout_pct=round(100.0 * (total - len(vals)) / total, 2),
        spikes=spikes,
        min_range=min(vals),
        max_range=max(vals),
        mean_range=round(sum(vals) / len(vals), 3),
    )


def simulate_scan(n=360, dropout=0.0, spikes=0, seed=1):
    """Synthetic scan with optional faults injected."""
    rng = random.Random(seed)
    scan = [4.0 + 1.5 * abs(math.sin(math.radians(i))) + rng.uniform(-0.02, 0.02) for i in range(n)]
    for i in rng.sample(range(n), int(n * dropout)):
        scan[i] = float("inf")
    for i in rng.sample(range(1, n - 1), spikes):
        scan[i] += 8.0
    return scan
