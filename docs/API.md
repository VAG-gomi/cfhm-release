# CFHM Public API

CFHM is a negative-result research artifact. The package exposes the smallest public surface required by SPEC-C1.

## `generate_world`

```python
from cfhm import generate_world
world = generate_world(seed=1000, arm="A1")
```

Signature:

```python
generate_world(seed: int, arm: str) -> WorldDict
```

`arm` must be `"A1"` or `"A2"`. The returned dictionary contains the calibrated intercept and kappa, true and visible typed-edge graphs, raw and standardized feature matrices, events and labels, ground-truth parameters, maintainer information, the forced-event mask, rate-calibration trace, and deterministic seed keys.

The bound shape fields are:

| Field | Shape or type |
|---|---|
| `features_raw` | `(200, 9)` NumPy array |
| `features_std` | `(200, 9)` NumPy array |
| `events` | `(200, 130)` integer array |
| `labels` | `(200,)` integer array |
| `b_truth` | `(3, 3)` array, ordered major/minor/advisory by tap |
| `c_truth` | `(200,)` array |
| `true_graph` / `visible_graph` | dictionaries with `src`, `dst`, and `typ` arrays |
| `maintainers` | five indices for A2; empty for A1 |

## `CFHMModel`

```python
from cfhm import CFHMModel
model = CFHMModel(n_nodes=200, seed=1484812508)
report = model.fit(world, epochs=50, lambda1=0.01)
```

Constructor:

```python
CFHMModel(n_nodes: int = 200, seed: int | None = None)
```

The constructor creates the 9→16→1 fragility MLP, a `(3, 3)` raw transmission parameter matrix initialized at `-4.0`, and a 200-element raw fragility-history vector initialized at `-4.0`. Transmission rows are reparameterized as `(0.95 / 3) * sigmoid(raw_b)`, so each row is nonnegative and capped at `0.95` in the structural representation.

### `fit`

```python
fit(world: WorldDict, epochs: int = 50, lambda1: float = 0.01) -> FitReport
```

Fits the teacher-forced model on target weeks 2 through 104 using one Adam step per epoch, learning rate `1e-3`, binary cross-entropy, L1 penalty on the transmission matrix, and MLP L2 penalty `1e-4`. It sorts no external data because the world dictionary is already deterministic and bound. The returned `FitReport` records epochs, penalty, environment count, target steps, and elapsed time.

### `forecast_hazard_mass`

```python
forecast_hazard_mass() -> numpy.ndarray
```

Returns a length-200 array of 26-week ex-ante hazard masses. Training-state accumulators are frozen at week 104, and event feedback is propagated as `n=0` through the test window.

### `transmission_amplitudes`

```python
transmission_amplitudes() -> dict[str, float]
```

Returns the tap-summed transmission rows under the keys `major`, `minor`, and `advisory`. The D4 collapse gate requires all three values to be at most `0.05` for the bound seed-1000 A1 fit.

### `spectral_radius`

```python
spectral_radius() -> float
```

Returns the maximum tap-summed transmission row. The D3 structural constraint requires it to be at most `0.95 + 1e-9`.

## Fit guard

Calling a fitted-model operation before `fit` raises:

```text
RuntimeError: model not fitted: call fit() first
```

This guard is intentional. The package does not silently train or fabricate a result when the model has not been fitted.

## Scope

The API reproduces the audited negative-result regime. It is not a working hazard predictor and is not validated on real-world data.
