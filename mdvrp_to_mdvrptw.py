#author@blackcontractor90

import math
import argparse
import os
import sys


# ── Parsing ────────────────────────────────────────────────────────────────────

def parse_file(path):
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]

    h = lines[0].split()
    if len(h) < 3:
        raise ValueError(f"Header must have at least 3 values (type n t), got: {lines[0]!r}")

    prob_type = int(h[0])
    n         = int(h[1])   # number of customers
    t         = int(h[2])   # number of depots

    # Depot capacity lines
    depot_caps = []
    for i in range(1, 1 + t):
        p = lines[i].split()
        depot_caps.append((int(p[0]), int(p[1])))   # (max_duration, max_load)

    # Node lines: customers first, then depots
    # Cordeau spec: i  x  y  d  q  f  a  list  e  l
    node_start = 1 + t
    customers, depots = [], {}

    for i in range(node_start, node_start + n + t):
        p = lines[i].split()
        node = {
            'id': int(p[0]),
            'x':  float(p[1]),
            'y':  float(p[2]),
            'd':  int(p[3]),       # service duration (often 0 in MDVRP)
            'q':  int(p[4]),       # demand
        }
        if i < node_start + n:
            customers.append(node)
        else:
            depots[node['id']] = node

    depot_list = list(depots.values())
    return prob_type, n, t, depot_caps, customers, depot_list


# ── Geometry ───────────────────────────────────────────────────────────────────

def euclid(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def nearest_depot_tt(cx, cy, depots):
    return min(euclid(cx, cy, d['x'], d['y']) for d in depots)


# ── Conversion ─────────────────────────────────────────────────────────────────

def convert(prob_type, n, t, depot_caps, customers, depots,
            service_time=10, tmax=None, style='wide', half_width=None):
    """
    Parameters
    ----------
    service_time : int
        Service duration assigned to every customer (minutes/units).
    tmax : int or None
        Planning horizon. If None, auto-computed as ceil(max_nearest_tt * 3).
    style : str
        'wide'   → half_width = T_max / 2        (pr06-pr10 convention)
        'narrow' → half_width = max(30, T_max*0.15)  (pr01-pr05 convention)
        'custom' → half_width must be supplied explicitly
    half_width : float or None
        Used only when style='custom'.
    """

    # Compute T_max
    max_tt = max(nearest_depot_tt(c['x'], c['y'], depots) for c in customers)
    if tmax is None:
        tmax = math.ceil(max_tt * 3)

    # Compute half-width
    if style == 'wide':
        hw = tmax / 2
    elif style == 'narrow':
        hw = max(30, tmax * 0.15)
    elif style == 'custom':
        if half_width is None:
            raise ValueError("style='custom' requires --half-width to be set.")
        hw = half_width
    else:
        raise ValueError(f"Unknown style: {style!r}. Choose wide | narrow | custom.")

    out = []

    # Header: type=6 (MDVRPTW), vehicles=4 (preserved), n, t
    out.append(f"6 4 {n} {t}")

    # Depot capacity lines
    for D, Q in depot_caps:
        real_D = tmax if D == 0 else D
        out.append(f"{real_D} {Q}")

    # Customer lines: i  x  y  d  q  f  a  list  e  l
    for c in customers:
        tt  = nearest_depot_tt(c['x'], c['y'], depots)
        e   = max(0,    math.floor(tt - hw))
        l   = min(tmax, math.ceil (tt + hw))
        out.append(
            f"  {c['id']:3d}   {c['x']:7.2f}   {c['y']:7.2f}"
            f"   {service_time:3d}   {c['q']:3d}"
            f"   1   1   1   {e:4d}   {l:4d}"
        )

    # Depot lines: svc=0, demand=0, e=0, l=T_max
    for d in depots:
        out.append(
            f"  {d['id']:3d}   {d['x']:7.2f}   {d['y']:7.2f}"
            f"     0     0   0   0   0      0   {tmax:4d}"
        )

    return "\n".join(out) + "\n", tmax, hw


# ── Summary ────────────────────────────────────────────────────────────────────

def print_summary(input_path, output_path, n, t, tmax, hw, service_time, style):
    print()
    print("=" * 52)
    print("  MDVRP → MDVRPTW Conversion Summary")
    print("=" * 52)
    print(f"  Input file     : {input_path}")
    print(f"  Output file    : {output_path}")
    print(f"  Customers      : {n}")
    print(f"  Depots         : {t}")
    print(f"  Problem type   : 2 (MDVRP) → 6 (MDVRPTW)")
    print(f"  T_max          : {tmax}")
    print(f"  Service time   : {service_time}")
    print(f"  Window style   : {style}")
    print(f"  Half-width     : {hw:.1f}")
    print(f"  Travel time    : Euclidean distance (speed = 1)")
    print("=" * 52)
    print()


# ── CLI ────────────────────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        description="Convert a Cordeau MDVRP (type 2) file to MDVRPTW (type 6).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", help="Path to the input MDVRP file")
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: <input>_mdvrptw.txt)"
    )
    parser.add_argument(
        "--service-time", type=int, default=10, metavar="INT",
        help="Service duration per customer node (default: 10)"
    )
    parser.add_argument(
        "--tmax", type=int, default=None, metavar="INT",
        help="Planning horizon T_max. If omitted, auto = ceil(max_nearest_tt * 3)"
    )
    parser.add_argument(
        "--style", choices=["wide", "narrow", "custom"], default="wide",
        help=(
            "Time window style: "
            "'wide' = T_max/2 half-width (pr06-pr10), "
            "'narrow' = max(30, T_max*0.15) (pr01-pr05), "
            "'custom' = set --half-width manually (default: wide)"
        )
    )
    parser.add_argument(
        "--half-width", type=float, default=None, metavar="FLOAT",
        help="Half-width of time windows when --style=custom"
    )
    return parser


def main():
    parser = build_parser()
    args   = parser.parse_args()

    # Input path
    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"Error: file not found: {input_path!r}", file=sys.stderr)
        sys.exit(1)

    # Output path
    if args.output:
        output_path = args.output
    else:
        base = os.path.splitext(input_path)[0]
        output_path = base + "_mdvrptw.txt"

    # Parse
    try:
        prob_type, n, t, depot_caps, customers, depots = parse_file(input_path)
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)

    if prob_type not in (2, 6):
        print(f"Warning: expected type 2 (MDVRP), got type {prob_type}. Proceeding anyway.")

    # Convert
    try:
        text, tmax, hw = convert(
            prob_type, n, t, depot_caps, customers, depots,
            service_time=args.service_time,
            tmax=args.tmax,
            style=args.style,
            half_width=args.half_width,
        )
    except Exception as e:
        print(f"Conversion error: {e}", file=sys.stderr)
        sys.exit(1)

    # Write
    with open(output_path, "w") as f:
        f.write(text)

    print_summary(input_path, output_path, n, t, tmax, hw,
                  args.service_time, args.style)
    print(f"  Done. Saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
