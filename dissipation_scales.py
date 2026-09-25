"""Compute the Kolmogorov and Obukhov-Corrsin scales in Tecplot 360.

Split off from derived_variables.py because the gradients behind {dissipation}
make this by far the slowest chain.  It is self-contained: it builds
{small_u}, {small_v}, {small_w} and the nine fluctuation gradients itself, then
{dissipation}, {eta}, {eta_theta}, {l_c_over_eta} and {l_c_corsin}.  Options
are the same as derived_variables.py, plus --eps.

usage:

    > python dissipation_scales.py              # execute on all zones
    > python dissipation_scales.py --dry-run    # just print the equations
    > python dissipation_scales.py --zones 1-4,7
    > python dissipation_scales.py --eps 1e-12  # floor dissipation in {eta}

Enable "Scripting -> PyTecplot Connections" in the Tecplot 360 GUI before
running without --dry-run.

Divide by zero
--------------
{dissipation} is exactly zero wherever the resolved fluctuations have no
gradient (walls, symmetry planes), and {eta} divides by it.  By default the
engine clamps N/0 to the largest float, matching the "Ignore Divide by Zero"
checkbox in the GUI's Data Alter dialog; {eta} then reaches ~1e76 at those
nodes, which will flatten any contour range you put on it.  --eps X floors the
denominator instead so {eta} stays finite and plottable.
"""
import argparse

from derived_variables import add_common_arguments, run, scale_equations


def main():
    parser = add_common_arguments(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--eps", type=float, default=0.0,
                        help="floor added to {dissipation} in the {eta} equation "
                             "to keep eta finite where dissipation is zero")
    run(parser.parse_args(), chain=scale_equations)


if __name__ == "__main__":
    main()
