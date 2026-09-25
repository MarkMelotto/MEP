"""Mark where a hybrid RANS/LES run was in RANS and where in LES mode.

Follows the ANSYS Fluent Theory Guide for the four hybrid models:

    sa-des  : d_tilde = min(d, C_des_SA Delta)
    sa-ddes : d_tilde = d - f_d max(0, d - C_des_SA Delta)
              f_d = 1 - tanh((8 r_d)^3),  r_d = (nu_t + nu)/(|grad U| kappa^2 d^2)
    sst-des : F_DES = max(L_t/(C_des_SST Delta), 1),  L_t = sqrt(k)/(beta* omega)
    sst-ddes: F_DES = max(L_t/(C_des_SST Delta) (1 - F2), 1),  F2 = tanh(arg2^2)

SA-DDES is shielded with Spalart's f_d, SST-DDES with the SST blending function
F2.  Every mode writes {LES_mode} (1 = LES, 0 = RANS) plus only the variables
it needs.  SA-DDES converts Fluent's dynamic {Turbulent Viscosity} to nu_t with
the LBE density.  Constants are at the top of derived_variables.py.

usage:

    > python des_mode.py                                 # asks for the mode
    > python des_mode.py --mode sst-ddes
    > python des_mode.py --mode sa-ddes --input case.szplt
    > python des_mode.py --mode sa-des --dry-run         # just print the equations
    > python des_mode.py --mode sst-des --zones 1-4,7

Without --input the dataset already open in Tecplot is used; with it, the file
replaces the active frame's data.  Enable "Scripting -> PyTecplot Connections"
in the Tecplot 360 GUI before running without --dry-run.
"""
import argparse

from derived_variables import MODES, add_common_arguments, mode_equations, run


CHOICES = {str(i): mode for i, mode in enumerate(MODES, start=1)}


def ask_mode():
    """Ask for the hybrid model until a valid choice is given."""
    print("Which model?")
    for number, mode in CHOICES.items():
        print(f"  {number}) {mode.upper()}")
    while True:
        answer = input(f"Choice [1-{len(CHOICES)}]: ").strip().lower()
        if answer in CHOICES:
            return CHOICES[answer]
        if answer in MODES:
            return answer
        print(f"Please enter a number from 1 to {len(CHOICES)}.")


def report_les_fraction(dataset, zones):
    """Share of nodes with LES_mode = 1, over the zones that were computed."""
    zones = list(dataset.zones()) if zones is None else zones
    variable = dataset.variable("LES_mode")
    total = les = 0
    for zone in zones:
        values = variable.values(zone).as_numpy_array()
        total += values.size
        les += (values > 0.5).sum()
    print(f"LES mode       : {les} of {total} nodes ({100 * les / total:.1f} %)")


def main():
    parser = add_common_arguments(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--mode", choices=MODES,
                        help="hybrid model formulation (asked if not given)")
    parser.add_argument("--input", metavar="FILE",
                        help=".plt / .szplt / .dat to load (default: the "
                             "dataset already open in Tecplot)")
    args = parser.parse_args()
    mode = args.mode or ask_mode()
    print(f"Mode           : {mode.upper()}")
    print(f"Input          : {args.input or 'active Tecplot dataset'}")

    result = run(args, chain=lambda model, eps: mode_equations(model, eps, mode))
    if result is not None and "LES_mode" in result[2]:
        report_les_fraction(*result[:2])


if __name__ == "__main__":
    main()
