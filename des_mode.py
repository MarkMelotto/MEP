"""Check where a DES / DDES run is in LES mode and where in RANS (SST) mode.

Adds {Mode_DES} and/or {Mode_DDES} to the dataset: 1 = LES mode, 0 = RANS
mode.  DES97 simply takes the smaller of the RANS length scale
sqrt(k)/(beta* omega) and C_DES * l_c.  DDES additionally shields the boundary
layer with f_d = 1 - tanh((8 r_d)^3), so it needs {Turbulent Viscosity} and
{Distance to wall} on top of {Turbulent Kinetic Energy} and
{Specific Dissipation Rate}.  Equations whose inputs are missing are reported
and skipped.  Constants are at the top of derived_variables.py.

usage:

    > python des_mode.py                   # DES and DDES, all zones
    > python des_mode.py --variant ddes    # only DDES
    > python des_mode.py --dry-run         # just print the equations
    > python des_mode.py --zones 1-4,7

Enable "Scripting -> PyTecplot Connections" in the Tecplot 360 GUI before
running without --dry-run.
"""
import argparse

from derived_variables import add_common_arguments, mode_equations, run


def main():
    parser = add_common_arguments(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--variant", choices=["des", "ddes", "both"],
                        default="both", help="which mode check to compute")
    args = parser.parse_args()
    variants = ("des", "ddes") if args.variant == "both" else (args.variant,)
    run(args, chain=lambda model, eps: mode_equations(model, eps, variants))


if __name__ == "__main__":
    main()
