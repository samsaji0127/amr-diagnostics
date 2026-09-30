"""Wheel-encoder stall detection."""
from dataclasses import dataclass


@dataclass
class Stall:
    start_t: float
    end_t: float
    samples: int

    @property
    def duration(self) -> float:
        return round(self.end_t - self.start_t, 3)


def detect_stalls(samples, cmd_threshold=0.05, min_samples=5):
    """Find windows where the robot is commanded to move but encoder ticks don't change.

    samples: list of (t, cmd_vel, ticks) tuples, time-ordered.
    Returns a list of Stall for every run of >= min_samples frozen readings."""
    stalls, run_start, run_len, last_t = [], None, 0, None
    for i in range(1, len(samples)):
        t, cmd, ticks = samples[i]
        frozen = abs(cmd) > cmd_threshold and ticks == samples[i - 1][2]
        if frozen:
            if run_len == 0:
                run_start = samples[i - 1][0]
            run_len += 1
            last_t = t
        else:
            if run_len >= min_samples:
                stalls.append(Stall(run_start, last_t, run_len))
            run_len = 0
    if run_len >= min_samples:
        stalls.append(Stall(run_start, last_t, run_len))
    return stalls


def simulate_encoder(duration=10.0, hz=20, stall_at=(4.0, 6.0), ticks_per_s=100):
    """Constant-velocity run with a frozen-counter fault between stall_at times."""
    out, ticks = [], 0
    for i in range(int(duration * hz)):
        t = round(i / hz, 3)
        if not (stall_at and stall_at[0] <= t < stall_at[1]):
            ticks += ticks_per_s // hz
        out.append((t, 0.5, ticks))
    return out
