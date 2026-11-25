"""
Sweep parameters_social_network.a_chi and record HHI and fleet car age.

"""
import sys

import numpy as np

from package.generating_data.sweep_hhi_age_gen import (
    load_base_params,
    parse_seeds,
    run_and_plot,
)

PARAM_NAME = "a_chi"
SUBDICT = "parameters_social_network"
PARAM_LABEL = r"$a_\chi$"

# 10 values, endpoints included. The SBI calibration prior range.
A_CHI_LIST = np.linspace(0.8, 2.0, 10)

SEEDS = 64


def _precheck(base_params, values):
    """
    Reject an infeasible grid, and measure the stream confound the docstring warns
    about, before 640 runs are launched rather than after reading a puzzling plot.

    """
    a_lo = float(np.min(values))
    if a_lo <= 0:
        raise ValueError(
            f"a_chi grid reaches {a_lo:.6g}, but the Beta distribution requires "
            f"a_chi > 0. Raise the bottom of the grid."
        )

    seed_inputs = base_params["seed_inputs"]
    psn = base_params["parameters_social_network"]
    b_chi, n = psn["b_chi"], psn["num_individuals"]

    base_a = load_base_params()["parameters_social_network"]["a_chi"]

    def draw(a):
        """gen_chi's Step 1 draw, plus the first uniform left for everything after it."""
        rs = np.random.RandomState(seed_inputs)
        chi = rs.beta(a, b_chi, size=n)
        return chi, float(rs.random_sample())

    chi_base, _ = draw(base_a)

    print(f"a_chi grid {a_lo:.4g} to {float(np.max(values)):.4g} at b_chi = "
          f"{b_chi:.4g}, seed_inputs = {seed_inputs}, calibrated a_chi = {base_a:.4g}")
    print("stream confound, see _precheck docstring. corr_id near 0 with corr_rank "
          "near 1 means the same distribution over re-randomised individuals;")
    print("a different next_u on each row means each row has its own NK landscape.")
    print(f"{'a_chi':>10}{'corr_rank':>11}{'corr_id':>9}{'next_u':>9}")
    next_us = []
    for value in values:
        chi, next_u = draw(float(value))
        next_us.append(next_u)
        print(f"{float(value):>10.4g}"
              f"{np.corrcoef(np.sort(chi), np.sort(chi_base))[0, 1]:>11.3f}"
              f"{np.corrcoef(chi, chi_base)[0, 1]:>9.3f}{next_u:>9.4f}")
    print(f"{len(set(next_us))} of {len(next_us)} rows have a distinct next_u; a "
          f"stream-stable sampler would give 1\n")


if __name__ == "__main__":
    run_and_plot(PARAM_NAME, SUBDICT, A_CHI_LIST, PARAM_LABEL,
                 parse_seeds(sys.argv[1:], SEEDS), precheck=_precheck)
