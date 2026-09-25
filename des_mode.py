"""Check where a DES / DDES run is in LES mode and where in RANS (SST) mode.

Adds {Mode_DES} and/or {Mode_DDES} to the dataset: 1 = LES mode, 0 = RANS
mode.  DES97 simply takes the smaller of the RANS length scale
sqrt(k)/(beta* omega) and C_DES * l_c.  DDES additionally shields the boundary
layer with f_d = 1 - tanh((8 r_d)^3), so it needs {Turbulent Viscosity} and
{Distance to wall} on top of {Turbulent Kinetic Energy} and
{Specific Dissipation Rate}.  Equations whose inputs are missing are reported
and skipped.  Constants are at the top of derived_variables.py.

usage:

    > python des_mode.py                   # asks DES / DDES / both
    > python des_mode.py --variant ddes    # only DDES, no question
    > python des_mode.py --dry-run         # just print the equations
    > python des_mode.py --zones 1-4,7

Enable "Scripting -> PyTecplot Connections" in the Tecplot 360 GUI before
running without --dry-run.
"""
import argparse

from derived_variables import add_common_arguments, mode_equations, run


CHOICES = {"1": "des", "2": "ddes", "3": "both"}


def ask_variant():
    """Ask which mode check to compute until a valid choice is given."""
    print("Which mode check?\n  1) DES\n  2) DDES\n  3) both")
    while True:
        answer = input("Choice [1-3]: ").strip().lower()
        if answer in CHOICES:
            return CHOICES[answer]
        if answer in CHOICES.values():
            return answer
        print("Please enter 1, 2 or 3.")


def main():
    parser = add_common_arguments(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--variant", choices=["des", "ddes", "both"],
                        help="which mode check to compute (asked if not given)")
    args = parser.parse_args()
    variant = args.variant or ask_variant()
    variants = ("des", "ddes") if variant == "both" else (variant,)
    run(args, chain=lambda model, eps: mode_equations(model, eps, variants))


if __name__ == "__main__":
    main()
