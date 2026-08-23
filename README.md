# CFHM — Contagion-Fragility Hazard Model

> **RESEARCH ARTIFACT: documents a negative result. The contagion transmission channel does not train in the shipped regime — it remains at initialization. See docs/AUTOPSY.md. Not a working hazard predictor.**

CFHM is a research artifact for studying transmission ranking in dependency networks. Its purpose is to predict which node suffers the next adverse event and to rank single-node removals by predicted total-hazard reduction using observational event logs and a declared dependency graph.

## What this package is

This package preserves the audited F1-v2 pipeline and SPEC-002 component autopsy as a reproducible negative result. The shipped regime uses a 200-node typed-edge graph, 104 training weeks, 26 ex-ante forecast weeks, a 9-feature fragility model, and a bounded three-type transmission channel. The result is not a working hazard predictor.

The evidence is synthetic only. F1-v1 was void by design because its rate gate was unsatisfiable. F1-v2 reached an inconclusive stability-gate outcome after the intercept repair. The SPEC-002 autopsy classified the channel as channel-inert, architecture-overhead, and regime-starved: the learned transmission amplitudes remain near initialization, while the oracle signal is rankable.

## Canonical model location

The actual reusable CFHM implementation is in [`src/cfhm/model.py`](src/cfhm/model.py). The package world generator is [`src/cfhm/worlds.py`](src/cfhm/worlds.py), the package metrics are in [`src/cfhm/metrics.py`](src/cfhm/metrics.py), and the public exports are in [`src/cfhm/__init__.py`](src/cfhm/__init__.py). The actual F1-v2 experiment runner is [`research/source/run_experiment.py`](research/source/run_experiment.py), and the actual SPEC-002 autopsy runner is [`research/f1_v2_autopsy/run_autopsy.py`](research/f1_v2_autopsy/run_autopsy.py).

## Installation

Use Python 3.12 or newer in a clean environment:

```bash
python -m pip install .
```

The runtime pins match the certified MAF environment:

```text
numpy==2.5.1
pandas==3.0.5
scipy==1.18.0
torch==2.13.0
```

## Public API

```python
from cfhm import CFHMModel, generate_world

world = generate_world(1000, "A1")
model = CFHMModel(n_nodes=200, seed=world["torch_seed"])
fit_report = model.fit(world, epochs=50, lambda1=0.01)
forecast = model.forecast_hazard_mass()
amplitudes = model.transmission_amplitudes()
```

`generate_world(seed, arm)` accepts `arm` equal to `"A1"` or `"A2"` and returns the bound world dictionary. `CFHMModel.fit` implements the teacher-forced 50-epoch loop. `forecast_hazard_mass` freezes the training state and propagates with ex-ante `n=0` feedback. `transmission_amplitudes` returns the three tap-summed channel amplitudes, and `spectral_radius` reports the structural cap quantity.

## Scientific gate

The most important test is D4. On `generate_world(1000, "A1")`, a full bound fit with 50 epochs and `lambda1=0.01` must produce all three transmission amplitudes at or below `0.05`. If any amplitude exceeds `0.05`, the collapse has revived and the package must halt rather than tune or repair the result.

## Evidence and documentation

- [`docs/AUTOPSY.md`](docs/AUTOPSY.md) reproduces the bound Section 0 narrative verbatim.
- [`docs/EMPIRICAL_RECORD.md`](docs/EMPIRICAL_RECORD.md) presents the three-stage record.
- [`docs/FAVORABLE_REGIME.md`](docs/FAVORABLE_REGIME.md) records a future favorable-regime hypothesis as **UNTESTED**, not as a result.
- [`docs/API.md`](docs/API.md) defines the public API.
- [`data/autopsy_rows.csv`](data/autopsy_rows.csv) contains the 400-row SPEC-002 T1 table.
- [`examples/reproduce_collapse.py`](examples/reproduce_collapse.py) runs the D4 collapse signature.
- [`verification/VERIFY.md`](verification/VERIFY.md) records the acceptance battery and its outcome.
- [`spec/`](spec/) contains the authored specification chain and this SPEC-C1 document.

## Reproduction

Run the package tests with:

```bash
python -m pytest
```

Run the collapse example with:

```bash
python examples/reproduce_collapse.py
```

The package is intentionally not presented as a deployment-ready predictor. Its value is in preserving a negative result, its root cause, its exact boundary conditions, and the evidence needed to reproduce or challenge that result.

## Repository family

`cfhm-release` is the canonical source repository and the only canonical home of the reusable CFHM model. The other repositories are separate mirrors and evidence views, not branches and not independent model implementations:

- [`cfhm-software`](https://github.com/VAG-gomi/cfhm-software) — software-only mirror.
- [`cfhm-spec-c1-evidence`](https://github.com/VAG-gomi/cfhm-spec-c1-evidence) — original SPEC-C1 evidence view.
- [`cfhm-evidence-bank`](https://github.com/VAG-gomi/cfhm-evidence-bank) — complete evidence-bank view.

## Preserved research execution

The canonical repository also preserves the actual historical execution under [`research/`](research/):

- [`research/source/run_experiment.py`](research/source/run_experiment.py) — actual F1-v2 experiment runner.
- [`research/source/score_metrics.py`](research/source/score_metrics.py) — actual F1-v2 metric runner.
- [`research/f1_v2/`](research/f1_v2/) — complete F1-v2 output tree.
- [`research/f1_v2_autopsy/`](research/f1_v2_autopsy/) — complete SPEC-002 autopsy tree.
- [`research/spec/`](research/spec/) — preserved authored specification chain.

The package-level `ARTIFACT_MANIFEST.sha256` verifies the 30-file `cfhm` package at the repository root. The research trees retain separately scoped manifests; any manifest or provenance correction is recorded in `DEVIATIONS.md`, while historical model source, raw evidence, configurations, logs, and results remain byte-unchanged.

## Provenance boundary

All pre-existing project trees remain outside this new package root and are byte-immutable. The SPEC-C1 package is built on branch `cfhm-artifact` from the recorded current HEAD. Tooling failures are recorded in `DEVIATIONS.md`; scientific failures in D1–D4 halt execution without author-approved repair.

## License

MIT. See [`LICENSE`](LICENSE).
