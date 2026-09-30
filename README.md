# amr-diagnostics

Small, dependency-free Python toolkit for AMR validation:

- **LiDAR scan health**: dropout percentage, isolated range spikes, min/max/mean range
- **Wheel-encoder stall detection**: finds windows where velocity is commanded but ticks stay frozen

## Usage

```bash
python -m amrdiag demo                      # run on simulated data
python -m amrdiag lidar scan.csv            # one range (m) per line
python -m amrdiag encoder wheel.csv         # columns: t,cmd_vel,ticks
```

Exit code is `0` when healthy and `1` on a fault, so it drops straight into CI or a validation pipeline.

## Tests

```bash
pip install pytest
pytest -q
```
