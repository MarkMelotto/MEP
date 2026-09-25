# MEP

> **Note:** This README was written by AI (Claude), based on reading the code
> in this repository. It may contain inaccuracies. Check the scripts themselves
> for the definitive behaviour.

Code for my Master End Project (MEP): post-processing and setup scripts for CFD simulations (ANSYS Fluent) of a
triple-jet mixing case, including liquid-metal (lead-bismuth eutectic, LBE)
mixed-convection cases. Most of the tools either run against **Tecplot 360**
through PyTecplot, or generate Tecplot equation strings to paste into its
*Data > Alter > Specify Equations* dialog.

## Requirements

- Python 3
- `numpy`, `pandas`
- [`pytecplot`](https://pypi.org/project/pytecplot/) and a Tecplot 360 licence
  for the scripts that talk to Tecplot directly

For the PyTecplot scripts, first enable connections in Tecplot 360:
*Scripting > PyTecplot Connections… > Accept connections* (default port 7600).

## Contents

### Tecplot automation (PyTecplot)

| File | Purpose |
|---|---|
| `derived_variables.py` | Computes normalised and turbulence-derived variables in the loaded dataset. It detects the turbulence model (RANS, DES/DDES SST, LES/DES SA) from the available variables and skips any equation whose inputs are missing. Options include `--dry-run`, `--zones`, `--model`, `--eps` and `--prune`. |
| `dissipation_scales.py` | Runs only the dissipation / length-scale tail of the `derived_variables.py` chain, starting at `{dvdz}`. |
| `tecplot_z_averages.ipynb` | Notebook that computes spanwise (z) averages directly in a running Tecplot session. It auto-detects stations from the `…xh<N>` zone names and interpolates slices by position, so slices with different point counts can be averaged. |
| `tecplot_average/TimeAverage.py` | Time-averages a strand of zones. It needs `tpmath.py` and `tputils.py` from the same folder, which come from [Tecplot's handyscripts](https://github.com/Tecplot/handyscripts). |

### Equation-string generators

These print Tecplot equations (e.g. `{u_avg_z} = ({u}[12] + {u}[13] + …)/N`)
to copy into Tecplot. Zone indices, excluded slices and variable names are
hard-coded at the top of each script, so edit them for each case.

| File | Purpose |
|---|---|
| `tecplot averager.py` | Spanwise averages over a range of slice zones, excluding z/h = 0. |
| `tecplot averager_LBE.py` | Same idea for the LBE cases at several x/h stations. |
| `forced_fine.py`, `streamwise forced.py` | Averaging variants for the forced-convection cases, with lists of slice zones to skip. |
| `differencer.py` | Differences between cases (e.g. Boussinesq vs. no-gravity) at each x/h station. |
| `v2.py` | Averages of the length-scale ratios `l_c_over_eta` and `l_c_corsin`. |

### Case setup and quick calculations

| File | Purpose |
|---|---|
| `main.py` | Reynolds, Grashof and Richardson numbers for the sodium and LBE cases, using temperature-dependent property correlations. |
| `LBE.py` | Grid spacing and the largest stable time step for conduction in LBE. |
| `precursor_cold_left.py`, `precursor_cold_right.py`, `precursor_test.py`, `precursor_change.py` | Shift the coordinates in Fluent inlet profile files (`Profile_cold_*.prof`) from a precursor simulation so they line up with the main domain. The first three keep a `.original` backup of each file. `precursor_change.py` edits in place with no backup. |

## Notes

- Several scripts contain absolute paths such as `X:/ANSYS results/...`.
  Change them before running on another machine.
- Tecplot zone indices in the equation generators are 1-based and specific to
  each dataset.
