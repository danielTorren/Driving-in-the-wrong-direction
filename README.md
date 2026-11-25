# Driving in the wrong direction? Modelling policy mixes for EV adoption

Replication code for an agent-based model (ABM) of the transition from internal
combustion engine vehicles (ICEVs) to electric vehicles (EVs), calibrated on
California, 2001–2023.

The model couples four submodules so that consumer adoption and firm innovation
co-evolve:

- **Discrete choice consumption**: heterogeneous car users compare the lifecycle
  utility (quality, range, lifecycle costs, lifecycle emissions) of their own car
  against new and used alternatives, and choose via a logit model.
- **Social imitation**: users only *consider* EVs once the share of EV owners in
  their Watts–Strogatz network neighbourhood passes an idiosyncratic
  innovativeness threshold.
- **Directed innovation**: manufacturers search parallel NK landscapes for ICEVs
  and EVs, choosing research direction and product mix by expected profit across
  consumer segments.
- **Used car market**: a single consolidated dealer prices used cars off the most
  similar new car with age-based depreciation, and scraps cars below scrap value.

Policy experiments evaluate five market-based instruments (carbon price,
electricity subsidy, new EV rebate, used EV rebate, and production subsidy)
individually and in pairs, over 2024–2035, with a post-policy projection to 2050.

---

## Installation

The project is managed with [uv](https://docs.astral.sh/uv/) and requires Python
3.13+.

```bash
uv sync
```

This installs a CPU-only build of PyTorch (only `sbi` needs it, for the
simulation-based-inference calibration) rather than the default CUDA build; see
the comments in `pyproject.toml`.

## Running

All scripts resolve config paths relative to the repository root and use absolute
imports, so run them as modules from the root:

```bash
uv run python -m package.generating_data.calibration_gen
```

Each `*_gen.py` script writes a timestamped directory under `results/` and most
call their matching `*_plot.py` immediately afterwards. `results/` is
git-ignored, so a fresh clone reproduces outputs by re-running the generators.

To explore a single run interactively, use `model_playground.ipynb`: load a
`base_params` dict from `package/constants/`, call `generate_data(base_params)`,
and inspect the returned controller.

---

## Reproducing the paper

Reproduction is two steps. First run the generator for a figure, which leaves a
timestamped folder under `results/`. Then paste that folder name into the `RUNS`
dict at the top of `package/paper_figures/build_figures.py` and run the builder,
which re-plots from the results folder, renumbers each PNG to its number in the
paper, and recomputes the two results tables:

```bash
uv run python -m package.paper_figures.build_figures --list          # what is ready, what is missing
uv run python -m package.paper_figures.build_figures --only 3,S6     # build a subset
```

`--list` is the quickest way to see which `RUNS` entries are still empty. The
builder writes into the manuscript directory (`docs/paper/`), which is not part
of this repository — without it, use `--no-tex` to produce the renumbered PNGs
alone, or take each figure straight from its results folder. See
`package/paper_figures/README.md` for the flags and the full figure manifest.

Runs use 64 Monte Carlo seeds and are parallelised over available cores with
`joblib`; the policy experiments are the expensive ones. Every `*.slurm` file
next to a generator is the cluster version of the same command.

### Manuscript figures and tables

| Paper output | Generate | Plot | Config |
|---|---|---|---|
| Fig. 2: calibration 2001–2023 (EV uptake and sales, prices, HHI, car age) | `generating_data.calibration_gen` | `plotting_data.calibration_plot` | `base_params_calibration.json` |
| Fig. 3: single-instrument grid search (100 intensities per instrument) | `analysis.vary_single_policy_gen` | `analysis.vary_single_policy_plot` | `base_params_vary_single_policy_gen.json`, `analysis/policy_bounds_vary_single_policy_gen.json` |
| Table 3: minimum single-policy intensity reaching 95% uptake, and its outcomes | `analysis.endogenous_policy_intensity_single_gen` | `analysis.endogenous_policy_intensity_single_plot` | `base_params_endogenous_policy_single_gen.json`, `analysis/policy_bounds_endog_single_gen.json` |
| Fig. 4: policy pairs achieving 94–96% uptake | `analysis.endogenous_policy_intensity_pair_gen` | `analysis.endogenous_policy_intensity_pair_plot` | `base_params_endogenous_policy_pair_gen.json`, `analysis/policy_bounds_vary_pair_policy_gen.json` |
| Fig. 5, Table 4: trajectories to 2050 after policy removal | `analysis.low_policy_intensity_gen` | `analysis.low_policy_intensity_plot` | reads pair- and single-analysis results folders (see note below) |
| Fig. 6: parameter distribution histograms | `generating_data.single_experiment_gen` | `plotting_data.single_experiment_plot` | inline `base_params` dict in the script |
| Fig. 7: EV uptake vs used car market capacity | `generating_data.vary_single_param_gen` | `plotting_data.vary_single_param_plot` | `base_params_vary_single.json`, `vary_single_max_num_cars_prop.json` |
| BAU reference outcomes | `analysis.BAU_outcomes_gen` | n/a | `base_params_endogenous_policy_pair_gen.json` |

Figure 1 is a hand-drawn model diagram, not model output.

### Supplementary figures

`package/supplementary_runs/` reproduces the supplementary material against the
current `package/constants/base_params_calibration.json`. Every script there is a
thin wrapper around generation and plotting code that already exists elsewhere in
`package/`; each file's docstring names the function it calls.

| Figure | What it shows | Script | Config |
|---|---|---|---|
| S1 | NPE posterior density for `a_chi`, `b_chi` | `calibration.sbi_single_seed_gen`, plotted by `supplementary_runs.fig01_posterior_plot` | `base_params_NN.json` |
| S5 | Simulated vs real-world ICE/EV price and range | `supplementary_runs.fig05_calibration_cars_gen` | `base_params_calibration.json` |
| S6 | 10-panel local sensitivity of EV uptake | `supplementary_runs.fig06_panels` (resumable) or `fig06_local_sensitivity_gen`, then `fig06_local_sensitivity_plot` | `base_params_vary_single.json`, `vary_single_*.json` |
| S7, S8 | Sobol first- and total-order indices, 6 outputs × 10 parameters | `supplementary_runs.fig07_08_sobol_gen` | `base_params_SA.json`, `variable_parameters_dict_SA.json` |
| S9, S10 | BAU EV uptake, emissions and elasticities over grid decarbonisation × electricity price | `supplementary_runs.fig09_10_bau_gen`, then `fig09_bau_timeseries_plot` and `fig10_bau_elasticity_plot` | `base_params_inputs_and_emissions.json`, `vary_sen_decarb.json`, `vary_sen_elec_price.json` |
| S11–S14 | EV uptake in 2035 over a behavioural parameter × a policy intensity | `supplementary_runs.fig11_14_policy_grid_gen <11\|12\|13\|14>` | `base_params_vary_policy_joint.json`, `vary_policy_*.json` |




## Repository layout

```text
├── model_playground.ipynb              # Interactive single-run exploration
├── pyproject.toml / uv.lock            # Dependencies (uv)
├── docs/
│   ├── code_narrative.tex / .pdf       # Extended walkthrough of the model code
│   └── forward_looking/                # Note on the forward-looking expectations extension
└── package/
    ├── model/                          # Core agent-based model
    ├── analysis/                       # Policy experiments (paper Section 4)
    ├── generating_data/                # Calibration, sensitivity and sweep runners
    ├── plotting_data/                  # Figure scripts for the above
    ├── paper_figures/                  # Renumbers figures and tables into the manuscript
    ├── supplementary_runs/             # Reproduces the supplementary figures
    ├── calibration/                    # Empirical data loading and SBI calibration
    ├── calibration_data/               # California input data (see Data sources)
    ├── constants/                      # base_params_*.json and vary_*.json configs
    └── resources/                      # Run harness and I/O helpers
```

### `package/model/`

| File | Role |
|---|---|
| `controller.py` | Orchestrates the monthly update sequence, exogenous input paths, and policy application |
| `socialNetworkUsers.py` | Car users: choice set construction, logit choice, imitation threshold update |
| `firm.py` | A single manufacturer: product mix, pricing, NK innovation |
| `firmManager.py` | Firm population and market segmentation |
| `nkModel_ICE.py`, `nkModel_EV.py` | NK technology landscapes for each drivetrain |
| `carModel.py` | A car design offered for sale (attribute vector plus price) |
| `personalCar.py` | An owned vehicle and its accumulated state |
| `secondHandMerchant.py` | Used car pricing, stock limits and scrapping |
| `VehicleUser.py` | Base user attributes |
| `centralizedIdGenerator.py` | Unique IDs across the simulation |

### `package/resources/`

- `run.py`: `generate_data()` builds and steps a controller for one parameter
  set; `load_in_controller()` resumes a calibrated controller for the policy
  period, so the 2001–2023 burn-in and calibration are computed once and reused
  across policy scenarios.
- `utility.py`: object save/load, run naming, directory creation, worker counts.

### Configuration

Each experiment loads a `base_params_*.json` from `package/constants/`. Runs are
divided into phases by timestep count: `duration_burn_in` (180, ICEV-only),
`duration_calibration` (276, 2001–2023) and `duration_future` (144, the 2024–2035
policy period, extended to 2050 for the stability analysis, and 0 for the
calibration and sensitivity configs that stop in 2023). All configurations use
`seed_repetitions` 64.

Policies live under `parameters_policies`, with `States` switching each instrument
on or off and `Values` giving its intensity. The `vary_*.json` files describe
parameter sweeps consumed by the sensitivity runners.

---


## Data sources

`package/calibration_data/` holds the California series used for calibration:
vehicle population and EV sales (California Energy Commission), gasoline and
residential electricity prices, grid emissions intensity, and CPI for conversion
to 2020 US dollars. `calibration_data_inputs.py` assembles these into the pickled
input object the model reads; `calibration_data_outputs.py` formats the observed
targets used for indirect calibration.

Full parameter values, units and sources are tabulated in the paper's Appendix B.
