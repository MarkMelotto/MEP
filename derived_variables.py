"""Compute the normalized / turbulence derived variables in Tecplot 360.

The script reads the dataset's variable list first, works out which turbulence
model the case came from, and only runs the equations whose inputs are actually
present.  Equations that cannot be satisfied are reported and skipped rather
than raising.

This covers the general variables (coordinates, theta, normalized velocities,
RMS values, turbulent fluxes, {uv} and k).  The slow dissipation / eta /
l_c_corsin chain is run separately with dissipation_scales.py.

usage:

    > python derived_variables.py                    # execute on all zones
    > python derived_variables.py --dry-run          # print the equations
    > python derived_variables.py --dry-run --model les
    > python derived_variables.py --zones 1-4,7
    > python derived_variables.py --prune            # drop unused variables

Enable "Scripting -> PyTecplot Connections" in the Tecplot 360 GUI before
running without --dry-run.

Pruning
-------
The variables no equation reads are listed on every run.  --prune deletes them
from the dataset before the chain starts; X, Y, Z and anything in --keep are
never touched, and the list is confirmed before anything goes (--yes skips the
prompt).  Deletions only affect the dataset loaded in the session; the file on
disk is unchanged until you save it.

Turbulence model detection
--------------------------
    {Turbulent Kinetic Energy} only ........ RANS               -> {k_RANS}
    {Turbulent Kinetic Energy} + SGS ....... DES/DDES SST       -> {k_DES_SST}
    SGS only ............................... LES or DES/DDES SA -> {k_tot}

LES and DES/DDES SA carry the same variables (k_SGS + k_res), so they cannot be
told apart from the dataset alone.  Pass --model les or --model des_sa to get
{k_LES} or {k_DES_SA} instead of the neutral {k_tot}.
"""
import argparse
import re

# ---------------------------------------------------------------- constants
H = 0.015                  # channel height / normalizing length [m]
U_REF = 0.085421165466     # bulk / jet velocity [m/s]
T_REF = 493.15             # reference (inlet) temperature [K]
T_HOT = 529.5              # hot wall temperature [K]
T_COLD = 474.98            # cold wall temperature [K]
NU = 2.18601847e-7         # kinematic viscosity [m2/s]
PR = 0.025                 # Prandtl number [-]
L_C = 0.00225              # characteristic (cell/probe) length [m]

# DES / DDES RANS-LES region check (des_mode.py); also uses NU above
DELTA = 0.00225            # grid spacing, max(dx, dy, dz) of the uniform grid [m]
KAPPA = 0.4187             # von Karman constant (SA-DDES r_d)
BETA_STAR = 0.09           # SST beta*
C_DES_SA = 0.65            # SA-DES constant
C_DES_SST = 0.61           # Fluent's single SST value (not the 0.78/0.61 F1 blend)
# LBE density, not in the dataset: rho = 11065 - 1.293*T  [kg/m3]
DENSITY = "11065 - 1.293*{Static Temperature}"

# Temperature scale: (T_hot - T_ref) - 2*(T_cold - T_ref).  Written out as an
# expression instead of a pre-multiplied float so the equations stay readable.
DT = f"(({T_HOT}-{T_REF})-2*({T_COLD}-{T_REF}))"

# Dataset variables that decide which turbulence model produced the case.
TKE_VAR = "Turbulent Kinetic Energy"
SGS_VAR = "SV_SGS_TKE_MEAN"

# Detected case -> (label, total-k variable, its equation).
MODELS = {
    "rans": ("RANS",
             "k_RANS", "{k_RANS} = {k_res} + {TKE}"),
    "des_sst": ("DES/DDES SST",
                "k_DES_SST", "{k_DES_SST} = {k_res} + {TKE} + {k_SGS}"),
    "des_sa": ("DES/DDES SA",
               "k_DES_SA", "{k_DES_SA} = {k_res} + {k_SGS}"),
    "les": ("LES",
            "k_LES", "{k_LES} = {k_res} + {k_SGS}"),
    "sgs_only": ("LES or DES/DDES SA (SGS only, ambiguous)",
                 "k_tot", "{k_tot} = {k_res} + {k_SGS}"),
}

# Never deleted by --prune, on top of whatever --keep names.
PROTECTED = ["X", "Y", "Z"]


def detect_model(available):
    """Pick a model key from the variables present in the dataset."""
    lower = {name.lower() for name in available}
    has_tke = TKE_VAR.lower() in lower
    has_sgs = SGS_VAR.lower() in lower
    if has_tke and has_sgs:
        return "des_sst"
    if has_tke:
        return "rans"
    if has_sgs:
        return "sgs_only"
    return None


def model_variables(model):
    """The variable list a given model's dataset is expected to carry."""
    variables = ["X", "Y", "Z", "Static Temperature", "Mean Static Temperature",
                 "RMS Static Temperature"]
    for axis in ("X", "Y", "Z"):
        variables += [f"{axis} Velocity", f"Mean {axis} Velocity",
                      f"RMS {axis} Velocity"]
    if model in ("rans", "des_sst"):
        variables += [TKE_VAR, "Specific Dissipation Rate"]
    if model in ("rans", "des_sst", "des_sa"):
        variables += ["Distance from Wall", "Turbulent Viscosity"]
    if model in ("des_sst", "des_sa", "les", "sgs_only"):
        variables.append(SGS_VAR)
    return variables


def general_equations(model, eps=0.0):
    """The general chain as an ordered list of (variable name, equation) pairs.

    Everything is listed here; plan() drops whatever the dataset cannot feed.
    The dissipation / length-scale chain lives in scale_equations() and is run
    by dissipation_scales.py, since it is by far the slowest part.
    """
    eqs = []

    # -- coordinates ------------------------------------------------------
    for axis in ("x", "y", "z"):
        eqs.append((f"{axis}/h", "{%s/h} = {%s}/%s" % (axis, axis.upper(), H)))

    # -- normalized temperature and velocity ------------------------------
    eqs.append(("theta",
                "{theta} = ({Static Temperature} - %s)/%s" % (T_REF, DT)))
    eqs.append(("normalized_u", "{normalized_u} = {X Velocity}/%s" % U_REF))
    eqs.append(("theta_rms", "{theta_rms} = {RMS Static Temperature}/%s" % DT))
    eqs.append(("u_rms", "{u_rms} = {RMS X Velocity}/%s" % U_REF))
    eqs.append(("v_rms", "{v_rms} = {RMS Y Velocity}/%s" % U_REF))

    # -- velocity and temperature fluctuations ----------------------------
    # Built here rather than inline, since the fluxes and {uv} reuse them.
    eqs += velocity_fluctuations(("u", "v"))
    eqs.append(("small_theta",
                "{small_theta} = {Mean Static Temperature} - {Static Temperature}"))

    # -- turbulent heat fluxes and shear stress ---------------------------
    for small in ("u", "v"):
        eqs.append((f"{small}_theta",
                    "{%s_theta} = ({small_%s}/%s) * ({small_theta}/%s)"
                    % (small, small, U_REF, DT)))
    eqs.append(("uv", "{uv} = ({small_u}/%s)*({small_v}/%s)" % (U_REF, U_REF)))

    # -- resolved / modelled / total turbulent kinetic energy -------------
    eqs.append(("k_res",
                "{k_res} = 0.5*(({RMS X Velocity}/%s)**2"
                " + ({RMS Y Velocity}/%s)**2"
                " + ({RMS Z Velocity}/%s)**2)" % (U_REF, U_REF, U_REF)))
    eqs.append(("TKE", "{TKE} = {%s}/(%s)**2" % (TKE_VAR, U_REF)))
    eqs.append(("k_SGS", "{k_SGS} = {%s}/(%s)**2" % (SGS_VAR, U_REF)))
    if model is not None:
        _, total_k, total_k_equation = MODELS[model]
        eqs.append((total_k, total_k_equation))

    return eqs


def velocity_fluctuations(components):
    """{small_u} etc., shared by both chains."""
    caps = {"u": "X", "v": "Y", "w": "Z"}
    return [(f"small_{small}",
             "{small_%s} = {Mean %s Velocity}-{%s Velocity}"
             % (small, caps[small], caps[small]))
            for small in components]


def scale_equations(model=None, eps=0.0):
    """Everything {eta} and {l_c_corsin} need, starting from the raw data."""
    eqs = velocity_fluctuations(("u", "v", "w"))

    # -- fluctuation gradients --------------------------------------------
    for small in ("u", "v", "w"):
        for axis in ("x", "y", "z"):
            eqs.append((f"d{small}d{axis}",
                        "{d%sd%s} = dd%s({small_%s})" % (small, axis, axis, small)))

    # -- pseudo-dissipation, nu * (du_i/dx_j)(du_i/dx_j) ------------------
    grads = " + ".join("{d%sd%s}**2" % (s, a)
                       for s in ("u", "v", "w") for a in ("x", "y", "z"))
    eqs.append(("dissipation", "{dissipation} = %s * (%s)" % (NU, grads)))

    # -- Kolmogorov and Obukhov-Corrsin scales ----------------------------
    # 1/4 and -3/4 are written as decimals so Tecplot cannot do integer math.
    denominator = "{dissipation}" if not eps else "({dissipation} + %s)" % eps
    eqs.append(("eta", "{eta} = ((%s)**3 / %s)**0.25" % (NU, denominator)))
    eqs.append(("Pr", "{Pr} = %s" % PR))
    eqs.append(("eta_theta", "{eta_theta} = {eta}*{Pr}**(-0.75)"))
    eqs.append(("l_c", "{l_c} = %s" % L_C))
    eqs.append(("l_c_over_eta", "{l_c_over_eta} = {l_c} / {eta}"))
    eqs.append(("l_c_corsin", "{l_c_corsin} = {l_c}/{eta_theta}"))

    return eqs


MODES = ("sa-des", "sa-ddes", "sst-des", "sst-ddes")


def tanh(x):
    """tanh(x) in exp form, since Tecplot's equation engine has no tanh.

    Written with exp(-2x) so it cannot overflow; only valid for x >= 0,
    which holds for both callers ((8 r_d)**3 and arg2**2).
    """
    return "((1 - exp(-2*(%s)))/(1 + exp(-2*(%s))))" % (x, x)


def mode_equations(model=None, eps=0.0, mode="sst-des"):
    """RANS / LES regions of a hybrid run, one of MODES.

    Follows the ANSYS Fluent Theory Guide.  Every mode ends in {LES_mode}
    (1 = LES, 0 = RANS) and creates only the variables it needs.  SA-DDES is
    shielded with Spalart's f_d, SST-DDES with the SST blending function F2.
    """
    if mode.startswith("sa-"):
        return sa_mode_equations(mode)
    return sst_mode_equations(mode)


def sa_mode_equations(mode):
    """SA-DES / SA-DDES: the model uses d_tilde instead of the wall distance d."""
    d = "{Distance from Wall}"
    les_scale = "(%s*%s)" % (C_DES_SA, DELTA)
    eqs = []

    if mode == "sa-ddes":
        # -- r_d needs the KINEMATIC nu_t; Fluent writes dynamic mu_t -------
        eqs.append(("Density", "{Density} = %s" % DENSITY))
        eqs.append(("nu_t", "{nu_t} = {Turbulent Viscosity}/({Density} + 1e-30)"))
        # -- sqrt(U_i,j U_i,j) from the instantaneous velocities -----------
        grads = " + ".join("dd%s({%s Velocity})**2" % (a, c)
                           for c in ("X", "Y", "Z") for a in ("x", "y", "z"))
        eqs.append(("grad", "{grad} = sqrt(%s)" % grads))
        eqs.append(("r_d",
                    "{r_d} = min(5, ({nu_t} + %s)/({grad}*%s**2*%s**2 + 1e-30))"
                    % (NU, KAPPA, d)))
        # -- shielding: f_d ~ 0 inside the boundary layer, ~1 outside -------
        eqs.append(("f_d", "{f_d} = 1 - %s" % tanh("(8*{r_d})**3")))
        eqs.append(("d_tilde",
                    "{d_tilde} = %s - {f_d}*max(0, %s - %s)" % (d, d, les_scale)))
    else:
        eqs.append(("d_tilde", "{d_tilde} = min(%s, %s)" % (d, les_scale)))

    # -- 1 where d_tilde < d (LES), 0 where d_tilde = d (RANS) --------------
    eqs.append(("LES_mode",
                "{LES_mode} = max(0, min(1, (%s - {d_tilde})/1e-9))" % d))
    return eqs


def sst_mode_equations(mode):
    """SST-DES / SST-DDES: F_DES multiplies the k destruction term."""
    k, omega, d = ("{Turbulent Kinetic Energy}", "{Specific Dissipation Rate}",
                   "{Distance from Wall}")
    les_scale = "(%s*%s)" % (C_DES_SST, DELTA)

    # -- SST turbulent length scale, sqrt(k)/(beta* omega) ----------------
    eqs = [("L_t", "{L_t} = sqrt(%s)/(%s*%s + 1e-30)" % (k, BETA_STAR, omega))]

    if mode == "sst-ddes":
        # -- shielding with the SST blending function F2 (not f_d) ----------
        # arg2 capped at 10 to keep arg2**2 moderate
        eqs.append(("arg2",
                    "{arg2} = min(10, max(2*sqrt(%s)/(%s*%s*%s + 1e-30),"
                    " 500*%s/(%s**2*%s + 1e-30)))"
                    % (k, BETA_STAR, omega, d, NU, d, omega)))
        eqs.append(("F2", "{F2} = %s" % tanh("{arg2}**2")))
        eqs.append(("F_DES",
                    "{F_DES} = max({L_t}/%s*(1 - {F2}), 1)" % les_scale))
    else:
        eqs.append(("F_DES", "{F_DES} = max({L_t}/%s, 1)" % les_scale))

    # -- 1 where F_DES > 1 (LES), 0 where F_DES = 1 (RANS) -----------------
    eqs.append(("LES_mode", "{LES_mode} = max(0, min(1, ({F_DES}-1)/1e-9))"))
    return eqs


def plan(equations, available):
    """Split the equations into the ones the dataset can feed and the rest.

    Inputs are read straight out of the equation text, so an equation is kept
    only once every {name} on its right hand side either exists in the dataset
    or is produced by an earlier equation that was kept.  Names are matched
    case-insensitively and rewritten to the dataset's own spelling.
    """
    lookup = {name.lower(): name for name in available}
    kept, skipped = [], []
    for name, equation in equations:
        names = re.findall(r"\{([^}]+)\}", equation)
        inputs = names[1:]
        missing = [n for n in inputs if n.lower() not in lookup]
        if missing:
            skipped.append((name, missing))
            continue
        for requested in set(inputs):
            actual = lookup[requested.lower()]
            if actual != requested:
                equation = equation.replace("{%s}" % requested, "{%s}" % actual)
        kept.append((name, equation))
        lookup.setdefault(name.lower(), name)
    return kept, skipped


def equation_inputs(equation):
    """The {names} an equation reads, i.e. everything but its left hand side."""
    return re.findall(r"\{([^}]+)\}", equation)[1:]


def unused_variables(reference, available, protect):
    """The dataset variables no equation reads and none of them produces.

    `reference` is always every chain, even when only one is being run: the
    others have usually already been written into the dataset, and those
    results (and their inputs) must not be mistaken for variables nobody wants.
    """
    protect = {name.lower() for name in protect}
    produced = {name.lower() for name, _ in reference}
    used = {name.lower()
            for _, equation in reference for name in equation_inputs(equation)}
    return [name for name in available
            if name.lower() not in used | produced | protect]


def report_unused(unused):
    if not unused:
        print("Unused         : none\n")
        return
    print(f"Unused         : {len(unused)} variables")
    for name in sorted(unused):
        print(f"    {name}")
    print()


def parse_zones(spec):
    """'1-4,7' -> [0, 1, 2, 3, 6]  (input is 1-based like the Tecplot GUI)."""
    if not spec:
        return None
    indices = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            first, last = (int(v) for v in part.split("-"))
            indices += list(range(first, last + 1))
        else:
            indices.append(int(part))
    return [i - 1 for i in indices]


def report_plan(model, kept, skipped):
    label = MODELS[model][0] if model else "unknown (no TKE and no SGS variable)"
    print(f"Detected model : {label}")
    print(f"Computing      : {len(kept)} variables")
    if skipped:
        print(f"Skipping       : {len(skipped)} (inputs not in this dataset)")
        for name, missing in skipped:
            print(f"    {name:<26} needs {', '.join(missing)}")
    print()


def add_common_arguments(parser):
    parser.add_argument("--dry-run", action="store_true",
                        help="print the equations instead of executing them")
    parser.add_argument("--zones", default=None,
                        help="1-based zone list, e.g. '1-4,7' (default: all)")
    parser.add_argument("--model", default="auto",
                        choices=["auto"] + sorted(MODELS),
                        help="override the detected turbulence model")
    parser.add_argument("--no-ignore-divide-by-zero", dest="ignore_divide_by_zero",
                        action="store_false",
                        help="let Tecplot raise on divide by zero instead of clamping")
    parser.add_argument("--prune", action="store_true",
                        help="delete the unused variables from the dataset")
    parser.add_argument("--keep", nargs="+", default=[], metavar="VAR",
                        help="variables --prune must leave alone (X, Y, Z always are)")
    parser.add_argument("--yes", action="store_true",
                        help="do not ask for confirmation before deleting")
    parser.set_defaults(ignore_divide_by_zero=True)
    return parser


def load_dataset(path):
    """Load a .plt / .szplt / .dat file, replacing the active frame's data."""
    import tecplot as tp
    from tecplot.constant import ReadDataOption
    if path.lower().endswith(".szplt"):
        tp.data.load_tecplot_szl(path, read_data_option=ReadDataOption.Replace)
    else:
        tp.data.load_tecplot(path, read_data_option=ReadDataOption.Replace)


def run(args, chain=general_equations):
    """Plan and execute one chain (general, scale or mode equations)."""
    eps = getattr(args, "eps", 0.0)
    if args.dry_run:
        model = None if args.model == "auto" else args.model
        available = model_variables(model or "des_sst")
        model = model or detect_model(available)
        dataset = None
    else:
        import tecplot as tp
        tp.session.connect()
        if getattr(args, "input", None):
            load_dataset(args.input)
        dataset = tp.active_frame().dataset
        available = list(dataset.variable_names)
        model = detect_model(available) if args.model == "auto" else args.model
        print(f"Dataset        : {len(available)} variables")

    # Every chain, kept aside so that pruning judges "unused" against every
    # equation rather than only the ones this run happens to execute.
    reference = (general_equations(model, eps) + scale_equations(model, eps)
                 + mode_equations(model, eps, "sa-ddes")
                 + mode_equations(model, eps, "sst-ddes"))
    kept, skipped = plan(chain(model, eps), available)
    report_plan(model, kept, skipped)

    if args.dry_run:
        for _, equation in kept:
            print(equation)
        return

    import tecplot as tp
    from tecplot.constant import ValueLocation

    zone_indices = parse_zones(args.zones)
    zones = None if zone_indices is None else [dataset.zone(i) for i in zone_indices]

    unused = unused_variables(reference, available, PROTECTED + args.keep)
    report_unused(unused)

    if args.prune and unused:
        if args.yes or input("Delete them? [y/N] ").strip().lower() == "y":
            dataset.delete_variables(*[dataset.variable(n) for n in unused])
            print(f"Deleted {len(unused)} variables.\n")
        else:
            print("Nothing was deleted.\n")

    with tp.session.suspend():
        for name, equation in kept:
            print(f"{name:<26} {equation}")
            tp.data.operate.execute_equation(
                equation, zones=zones, value_location=ValueLocation.Nodal,
                ignore_divide_by_zero=args.ignore_divide_by_zero)

    print(f"\nDone - {len(kept)} variables computed on "
          f"{'all zones' if zones is None else str(len(zones)) + ' zone(s)'}.")


def main():
    args = add_common_arguments(
        argparse.ArgumentParser(description=__doc__)).parse_args()
    run(args)


if __name__ == "__main__":
    main()
