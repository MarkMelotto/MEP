"""Run only the dissipation / length-scale tail of the derived-variable chain.

Same equations, constants and options as derived_variables.py, but it starts at
{dvdz} and assumes {small_u}, {small_v}, {small_w} and the gradients up to
{dvdy} are already in the dataset.  Anything still missing is reported and
skipped, so run derived_variables.py instead if you want the whole chain.

usage:

    > python dissipation_scales.py              # execute on all zones
    > python dissipation_scales.py --dry-run    # just print the equations
    > python dissipation_scales.py --zones 1-4,7
    > python dissipation_scales.py --eps 1e-12
"""
import argparse

from derived_variables import add_common_arguments, run

# The chain is executed from here to the end of the list.
START_AT = "dvdz"


def tail(equations):
    """Drop everything before START_AT."""
    names = [name for name, _ in equations]
    return equations[names.index(START_AT):]


def main():
    parser = add_common_arguments(argparse.ArgumentParser(description=__doc__))
    run(parser.parse_args(), subset=tail)


if __name__ == "__main__":
    main()
