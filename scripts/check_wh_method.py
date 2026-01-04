import argparse
import sys
import numpy as np

def check_method(n, p, n_eff=None, small_n=60, med_n=120, dist_thresh=5.0):
    if n_eff is None:
        n_eff = float(n)

    dist_from_top = n_eff * (1 - p)

    print("-" * 40)
    print(f"Configuration:")
    print(f"  Sample Size (N)     : {n}")
    print(f"  Effective N (N_eff) : {n_eff}")
    print(f"  Target Percentile   : {p}")
    print(f"  Thresholds          : Small N<={small_n}, Med N<={med_n}, D<={dist_thresh}")
    print("-" * 40)
    print(f"Calculations:")
    print(f"  Distance from Top (D) = {n_eff:.2f} * (1 - {p:.2f}) = {dist_from_top:.4f}")

    is_small = (n_eff <= small_n and dist_from_top <= dist_thresh)
    is_med = (small_n < n_eff <= med_n and dist_from_top <= dist_thresh)

    print("-" * 40)
    print(f"Decision Logic:")
    print(f"  Small Trigger? {is_small}  (N_eff <= {small_n} AND D <= {dist_thresh})")
    print(f"  Med Trigger?   {is_med}  (N_eff > {small_n} AND <= {med_n} AND D <= {dist_thresh})")

    if is_small or is_med:
        method = "Chi-Square Correction (Conservative)"
    else:
        method = "Standard Wilson-Hazen (Normal Approx)"

    print("-" * 40)
    print(f"RESULT: {method}")
    print("-" * 40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check which statistical method will be used.")
    parser.add_argument("-n", type=int, required=True, help="Sample Size")
    parser.add_argument("-p", type=float, required=True, help="Target Percentile (0-1)")
    parser.add_argument("--neff", type=float, help="Effective Sample Size (defaults to n)")
    parser.add_argument("--small", type=int, default=60, help="Small N threshold")
    parser.add_argument("--med", type=int, default=120, help="Medium N threshold")
    parser.add_argument("--dist", type=float, default=5.0, help="Distance threshold")

    args = parser.parse_args()
    check_method(args.n, args.p, args.neff, args.small, args.med, args.dist)
