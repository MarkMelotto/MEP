"""Mark the RANS and LES regions of an SST-DES / SST-DDES run in Tecplot 360.

Follows the ANSYS Fluent Theory Guide for SST-based DES:

    L_t   = sqrt(k)/(beta* omega)
    des : F_DES = max(L_t/(C_des Delta), 1)
    ddes: F_DES = max(L_t/(C_des Delta) (1 - F2), 1),   F2 = tanh(arg2^2)
          arg2  = max(2 sqrt(k)/(beta* omega y), 500 nu/(y^2 omega))

Fluent's delayed option shields with the SST blending function F2, not with
Spalart's f_d / r_d.  Both modes write {L_t}, {F_DES} and {LES_mode} (1 where
F_DES > 1, i.e. LES; 0 = RANS), so the results stay comparable.  Needs
{Turbulent Kinetic Energy}, {Specific Dissipation Rate} and, for ddes,
{Distance to wall}.  Constants (DELTA, C_DES, BETA_STAR, NU) are at the top of
derived_variables.py.

usage:

    > python des_mode.py                 # asks DES or DDES
    > python des_mode.py --mode des
    > python des_mode.py --mode ddes
    > python des_mode.py --mode ddes --dry-run   # just print the equations
    > python des_mode.py --mode des --zones 1-4,7

Enable "Scripting -> PyTecplot Connections" in the Tecplot 360 GUI before
running without --dry-run.
"""
import argparse

from derived_variables import add_common_arguments, mode_equations, run


CHOICES = {"1": "des", "2": "ddes"}


def ask_mode():
    """Ask for the DES formulation until a valid choice is given."""
    print("Which formulation?\n  1) DES\n  2) DDES")
    while True:
        answer = input("Choice [1-2]: ").strip().lower()
        if answer in CHOICES:
            return CHOICES[answer]
        if answer in CHOICES.values():
            return answer
        print("Please enter 1 or 2.")


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
    parser.add_argument("--mode", choices=["des", "ddes"],
                        help="DES or DDES formulation (asked if not given)")
    args = parser.parse_args()
    mode = args.mode or ask_mode()
    print(f"Formulation    : SST-{mode.upper()}")

    result = run(args, chain=lambda model, eps: mode_equations(model, eps, mode))
    if result is not None and "LES_mode" in result[2]:
        report_les_fraction(*result[:2])


if __name__ == "__main__":
    main()
