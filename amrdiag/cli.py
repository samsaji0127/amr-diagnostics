"""Command line interface: python -m amrdiag <command>."""
import argparse
import csv
import sys

from .encoder import detect_stalls, simulate_encoder
from .lidar import analyze_scan, simulate_scan


def _print_lidar(name, rep):
    status = "OK  " if rep.healthy else "FAIL"
    print(f"[{status}] {name}: {rep.valid}/{rep.total} valid, dropout {rep.dropout_pct}%, "
          f"spikes {rep.spikes}, range {rep.min_range:.2f}-{rep.max_range:.2f} m")


def _print_stalls(name, stalls):
    if not stalls:
        print(f"[OK  ] {name}: no stalls")
    for s in stalls:
        print(f"[FAIL] {name}: stall {s.start_t}s -> {s.end_t}s ({s.duration}s, {s.samples} samples)")


def cmd_demo(_):
    print("== LiDAR ==")
    _print_lidar("clean scan", analyze_scan(simulate_scan()))
    _print_lidar("15% dropout", analyze_scan(simulate_scan(dropout=0.15)))
    _print_lidar("12 spikes", analyze_scan(simulate_scan(spikes=12)))
    print("\n== Encoder ==")
    _print_stalls("healthy run", detect_stalls(simulate_encoder(stall_at=None)))
    _print_stalls("frozen counter", detect_stalls(simulate_encoder()))
    return 0


def cmd_lidar(args):
    with open(args.file) as f:
        ranges = [float(row[0]) for row in csv.reader(f) if row]
    rep = analyze_scan(ranges)
    _print_lidar(args.file, rep)
    return 0 if rep.healthy else 1


def cmd_encoder(args):
    with open(args.file) as f:
        rows = [(float(t), float(c), int(k)) for t, c, k in csv.reader(f)]
    stalls = detect_stalls(rows, min_samples=args.min_samples)
    _print_stalls(args.file, stalls)
    return 1 if stalls else 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="amrdiag", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="run on simulated data").set_defaults(fn=cmd_demo)
    l = sub.add_parser("lidar", help="analyze CSV with one range per line")
    l.add_argument("file")
    l.set_defaults(fn=cmd_lidar)
    e = sub.add_parser("encoder", help="analyze CSV with columns t,cmd_vel,ticks")
    e.add_argument("file")
    e.add_argument("--min-samples", type=int, default=5)
    e.set_defaults(fn=cmd_encoder)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
