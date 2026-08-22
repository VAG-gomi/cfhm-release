"""Deterministic CFHM F1 world generation.

This module is a package-level extraction of the preserved F1-v2 world
construction semantics. It does not read or modify any historical evidence
artifacts.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, TypedDict

import numpy as np

N = 200
T_TRAIN = 104
T_TEST = 26
T_TOTAL = T_TRAIN + T_TEST
TAPS = np.array([0.5, 0.8, 0.95], dtype=float)
EDGE_TYPES = ("major", "minor", "advisory")
EDGE_PROBS = np.array([0.04, 0.08, 0.05], dtype=float)
TYPE_TO_INT = {name: i for i, name in enumerate(EDGE_TYPES)}
TYPE_MU = np.array([0.30, 0.15, 0.08], dtype=float)
TAP_SHARES = np.array([0.50, 0.35, 0.15], dtype=float)
GAMMA = -3.2


class WorldDict(TypedDict, total=False):
    seed: int
    arm: str
    seed_keys: dict[str, int]
    gamma_calibrated: float
    kappa: float
    true_graph: dict[str, np.ndarray]
    visible_graph: dict[str, np.ndarray]
    features_raw: np.ndarray
    features_std: np.ndarray
    feature_mean: np.ndarray
    feature_std: np.ndarray
    events: np.ndarray
    labels: np.ndarray
    b_truth: np.ndarray
    c_truth: np.ndarray
    fragility_truth: np.ndarray
    maintainers: np.ndarray
    force_mask: np.ndarray
    train_rate: float
    status: str
    calibration_path: str
    rates_by_kappa: dict[str, float]
    calibration_trace: list[dict[str, float | int | str]]
    torch_seed: int


@dataclass(frozen=True)
class EdgeTable:
    src: np.ndarray
    dst: np.ndarray
    typ: np.ndarray

    @property
    def size(self) -> int:
        return int(self.src.size)


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def seed_keys(seed: int) -> dict[str, int]:
    """R16/R2 sanctioned SeedSequence child conversion."""
    children = np.random.SeedSequence(seed).spawn(6)
    names = ("world", "thinning", "maintainer", "dynamics", "model_init", "bootstrap")
    return {
        name: int(child.generate_state(1, dtype=np.uint32)[0])
        for name, child in zip(names, children)
    }


def make_edge_table(src: list[int] | np.ndarray, dst: list[int] | np.ndarray, typ: list[int] | np.ndarray) -> EdgeTable:
    return EdgeTable(
        np.asarray(src, dtype=np.int64),
        np.asarray(dst, dtype=np.int64),
        np.asarray(typ, dtype=np.int64),
    )


def _graph_dict(graph: EdgeTable) -> dict[str, np.ndarray]:
    return {
        "src": graph.src.copy(),
        "dst": graph.dst.copy(),
        "typ": graph.typ.copy(),
    }


def _graph_from_dict(graph: dict[str, np.ndarray]) -> EdgeTable:
    return make_edge_table(graph["src"], graph["dst"], graph["typ"])


def generate_true_graph(rng_world: np.random.Generator) -> EdgeTable:
    src: list[int] = []
    dst: list[int] = []
    typ: list[int] = []
    # R3-003: lexicographic ordered pairs, type order major/minor/advisory.
    for i in range(N):
        for j in range(i + 1, N):
            draws = rng_world.random(3) < EDGE_PROBS
            for t in range(3):
                if bool(draws[t]):
                    src.append(i)
                    dst.append(j)
                    typ.append(t)
    return make_edge_table(src, dst, typ)


def thin_graph(true_graph: EdgeTable, rng_thinning: np.random.Generator) -> EdgeTable:
    count = int(math.floor(0.85 * true_graph.size))
    if count == true_graph.size:
        keep = np.arange(true_graph.size)
    else:
        keep = np.sort(rng_thinning.choice(true_graph.size, size=count, replace=False))
    return EdgeTable(true_graph.src[keep], true_graph.dst[keep], true_graph.typ[keep])


def distinct_in_degree(graph: EdgeTable) -> np.ndarray:
    sets = [set() for _ in range(N)]
    for s, d in zip(graph.src.tolist(), graph.dst.tolist()):
        sets[int(d)].add(int(s))
    return np.asarray([len(v) for v in sets], dtype=float)


def distinct_children_out_degree(graph: EdgeTable) -> np.ndarray:
    sets = [set() for _ in range(N)]
    for s, d in zip(graph.src.tolist(), graph.dst.tolist()):
        sets[int(s)].add(int(d))
    return np.asarray([len(v) for v in sets], dtype=float)


def generate_features(graph_visible: EdgeTable, rng_world: np.random.Generator) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    # Feature generation follows R-005: age, popularity, complexity, field,
    # with model-visible distinct in-degree as the second feature.
    age = rng_world.uniform(0.5, 20.0, size=N)
    popularity = rng_world.lognormal(0.0, 1.0, size=N)
    complexity = rng_world.uniform(0.0, 1.0, size=N)
    field = rng_world.integers(0, 5, size=N)
    indegree = distinct_in_degree(graph_visible)
    x = np.column_stack(
        [
            np.log(age),
            indegree,
            np.log(popularity),
            complexity,
            (field[:, None] == np.arange(5)[None, :]).astype(float),
        ]
    )
    return x, {"age": age, "popularity": popularity, "complexity": complexity, "field": field, "indegree": indegree}


def prepare_maintainer_mask(true_graph: EdgeTable, rng_maintainer: np.random.Generator, total_weeks: int) -> tuple[np.ndarray, np.ndarray]:
    outdegree = distinct_children_out_degree(true_graph)
    candidates = np.lexsort((np.arange(N), -outdegree))[:30]
    maintainers = np.sort(rng_maintainer.choice(candidates, size=5, replace=False))
    fire = rng_maintainer.random((5, total_weeks)) < (1.0 / 26.0)
    force = np.zeros((N, total_weeks), dtype=bool)
    # Each firing maintainer independently flips a p=0.5 coin per child.
    children_by_maintainer = {int(m): set() for m in maintainers.tolist()}
    for s, d in zip(true_graph.src.tolist(), true_graph.dst.tolist()):
        if int(s) in children_by_maintainer:
            children_by_maintainer[int(s)].add(int(d))
    for mi, maintainer in enumerate(maintainers.tolist()):
        children = sorted(children_by_maintainer[int(maintainer)])
        if not children:
            continue
        coins = rng_maintainer.random((len(children), total_weeks)) < 0.5
        force[np.asarray(children)[:, None], np.arange(total_weeks)[None, :]] |= coins & fire[mi][None, :]
    return maintainers, force


def truth_accumulators(events: np.ndarray, total_weeks: int) -> tuple[np.ndarray, np.ndarray]:
    # State index k contains the state after event week k (zero-based event
    # index k-1); predictions for week k+1 use state index k.
    e = np.zeros((N, total_weeks + 1, 3), dtype=float)
    r = np.zeros((N, total_weeks + 1), dtype=float)
    for k in range(1, total_weeks + 1):
        e[:, k, :] = TAPS[None, :] * e[:, k - 1, :] + events[:, k - 1, None]
        r[:, k] = 0.7 * r[:, k - 1] + events[:, k - 1]
    return e, r


def powerlaw_states(events: np.ndarray, total_weeks: int) -> np.ndarray:
    state = np.zeros((N, total_weeks + 1), dtype=float)
    weights = np.asarray([(1.0 + s) ** -1.5 for s in range(1, 53)], dtype=float)
    for k in range(1, total_weeks + 1):
        max_s = min(52, k)
        # state[k] = sum_{s=1..52} w_s n[k-s].
        state[:, k] = (events[:, k - max_s : k][:, ::-1] * weights[:max_s][None, :]).sum(axis=1)
    return state


def edge_message_truth_a1(e_state: np.ndarray, graph: EdgeTable, b_truth: np.ndarray) -> np.ndarray:
    msg = np.zeros(N, dtype=float)
    for s, d, t in zip(graph.src.tolist(), graph.dst.tolist(), graph.typ.tolist()):
        msg[int(d)] += float(np.dot(b_truth[int(t)], e_state[int(s)]))
    return msg


def edge_message_truth_a2(pl_state: np.ndarray, graph: EdgeTable, b_truth: np.ndarray) -> np.ndarray:
    msg = np.zeros(N, dtype=float)
    scalar_b = b_truth.sum(axis=1)
    for s, d, t in zip(graph.src.tolist(), graph.dst.tolist(), graph.typ.tolist()):
        msg[int(d)] += float(scalar_b[int(t)] * pl_state[int(s)])
    return msg


def simulate_events_for_params(
    *,
    arm: str,
    true_graph: EdgeTable,
    fragility: np.ndarray,
    c_truth: np.ndarray,
    b_truth: np.ndarray,
    force_mask: np.ndarray,
    uniform_events: np.ndarray,
    kappa: float,
    gamma: float,
) -> tuple[np.ndarray, float]:
    events = np.zeros((N, T_TOTAL), dtype=np.int8)
    for week in range(T_TOTAL):
        e_state, r_state = truth_accumulators(events, week)
        if arm == "A1":
            msg = edge_message_truth_a1(e_state[:, week], true_graph, b_truth)
        else:
            pl = powerlaw_states(events, week)
            msg = edge_message_truth_a2(pl[:, week], true_graph, b_truth)
        hazard = sigmoid(gamma + kappa * fragility + msg - c_truth * r_state[:, week])
        events[:, week] = (uniform_events[:, week] < hazard).astype(np.int8)
        if arm == "A2":
            events[force_mask[:, week], week] = 1
    return events, float(events[:, :T_TRAIN].mean())


def simulate_world(
    *,
    seed: int,
    arm: str,
    rng_world: np.random.Generator,
    rng_thinning: np.random.Generator,
    rng_maintainer: np.random.Generator,
    rng_dynamics: np.random.Generator,
) -> WorldDict:
    true_graph = generate_true_graph(rng_world)
    visible_graph = true_graph if arm == "A1" else thin_graph(true_graph, rng_thinning)
    x_raw, feature_parts = generate_features(visible_graph, rng_world)
    x_std, xmean, xstd = standardize_features(x_raw)
    # Ground-truth parameters in the authored order.
    w_base = rng_world.normal(0.0, 1.0, size=9) / math.sqrt(9.0)
    fragility_noise = rng_world.normal(0.0, 0.3, size=N)
    c_truth = rng_world.uniform(0.2, 1.0, size=N)
    b_truth = np.empty((3, 3), dtype=float)
    for t in range(3):
        scalar = rng_world.lognormal(math.log(TYPE_MU[t]), 0.2)
        b_truth[t] = scalar * TAP_SHARES
    fragility = x_std @ w_base + fragility_noise
    maintainers = np.asarray([], dtype=np.int64)
    force_mask = np.zeros((N, T_TOTAL), dtype=bool)
    if arm == "A2":
        maintainers, force_mask = prepare_maintainer_mask(true_graph, rng_maintainer, T_TOTAL)
    uniform_events = rng_dynamics.random((N, T_TOTAL))
    rates_by_kappa: dict[str, float] = {}
    calibration_trace: list[dict[str, float | int | str]] = []
    selected: tuple[float, float, np.ndarray, str, float] | None = None
    kappas = (0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
    # R6-002 primary path: fixed gamma and smallest kappa in the rate band.
    for kappa in kappas:
        events, rate = simulate_events_for_params(
            arm=arm, true_graph=true_graph, fragility=fragility, c_truth=c_truth,
            b_truth=b_truth, force_mask=force_mask, uniform_events=uniform_events,
            kappa=float(kappa), gamma=GAMMA,
        )
        rates_by_kappa[str(kappa)] = rate
        calibration_trace.append({"path": "kappa-ladder", "kappa": float(kappa), "gamma": GAMMA, "train_rate": rate})
        if selected is None and 0.03 <= rate <= 0.05:
            selected = (float(kappa), GAMMA, events.copy(), "kappa-ladder", rate)
    if selected is None:
        # R6-002 deterministic fallback: 12 midpoint iterations, kappa=1.0.
        gamma_lo, gamma_hi = -8.0, -1.0
        fallback_candidates: list[tuple[float, float, np.ndarray]] = []
        for iteration in range(1, 13):
            gamma_mid = (gamma_lo + gamma_hi) / 2.0
            events, rate = simulate_events_for_params(
                arm=arm, true_graph=true_graph, fragility=fragility, c_truth=c_truth,
                b_truth=b_truth, force_mask=force_mask, uniform_events=uniform_events,
                kappa=1.0, gamma=gamma_mid,
            )
            calibration_trace.append({"path": "gamma-bisection", "iteration": iteration, "kappa": 1.0, "gamma": gamma_mid, "train_rate": rate})
            if 0.03 <= rate <= 0.05:
                fallback_candidates.append((abs(rate - 0.04), gamma_mid, events.copy()))
            if rate < 0.04:
                gamma_lo = gamma_mid
            else:
                gamma_hi = gamma_mid
        if fallback_candidates:
            _, gamma_final, events_final = min(fallback_candidates, key=lambda x: (x[0], x[1]))
            final_rate = float(events_final[:, :T_TRAIN].mean())
            selected = (1.0, float(gamma_final), events_final, "gamma-bisection", final_rate)
    if selected is None:
        return {
            "seed": seed, "arm": arm, "seed_keys": seed_keys(seed),
            "gamma_calibrated": float("nan"), "kappa": float("nan"),
            "true_graph": _graph_dict(true_graph), "visible_graph": _graph_dict(visible_graph),
            "features_raw": x_raw, "features_std": x_std, "feature_mean": xmean, "feature_std": xstd,
            "events": np.zeros((N, T_TOTAL), dtype=np.int8), "labels": np.zeros(N, dtype=np.int8),
            "b_truth": b_truth, "c_truth": c_truth, "fragility_truth": fragility,
            "maintainers": maintainers, "force_mask": force_mask,
            "train_rate": float("nan"), "status": "RATE-EXCLUDED",
            "calibration_path": "gamma-bisection-no-band", "rates_by_kappa": rates_by_kappa,
            "calibration_trace": calibration_trace,
        }
    kappa, gamma_final, events, calibration_path, train_rate = selected
    labels = (events[:, T_TRAIN:T_TOTAL].sum(axis=1) >= 1).astype(np.int8)
    return {
        "seed": seed, "arm": arm, "seed_keys": seed_keys(seed),
        "gamma_calibrated": float(gamma_final), "kappa": float(kappa),
        "true_graph": _graph_dict(true_graph), "visible_graph": _graph_dict(visible_graph),
        "features_raw": x_raw, "features_std": x_std, "feature_mean": xmean, "feature_std": xstd,
        "events": events, "labels": labels, "b_truth": b_truth, "c_truth": c_truth,
        "fragility_truth": fragility, "maintainers": maintainers, "force_mask": force_mask,
        "train_rate": float(train_rate), "status": "ELIGIBLE", "calibration_path": calibration_path,
        "rates_by_kappa": rates_by_kappa, "calibration_trace": calibration_trace,
    }


def standardize_features(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.where(std > 0, std, 1.0)
    return (x - mean) / std, mean, std


def generate_world(seed: int, arm: str) -> WorldDict:
    """Generate one deterministic A1 or A2 world under the bound streams."""
    if not isinstance(seed, (int, np.integer)):
        raise TypeError("seed must be an integer")
    if arm not in ("A1", "A2"):
        raise ValueError("arm must be one of {'A1', 'A2'}")
    keys = seed_keys(int(seed))
    if arm == "A1":
        rng_world = np.random.default_rng(keys["world"])
        rng_thinning = np.random.default_rng(keys["thinning"])
        rng_maintainer = np.random.default_rng(keys["maintainer"])
        rng_dynamics = np.random.default_rng(keys["dynamics"])
    else:
        # R5-001: shared base-world stream; independent arm-specific streams.
        rng_world = np.random.default_rng(keys["world"])
        rng_thinning = np.random.default_rng(keys["thinning"] + 17)
        rng_maintainer = np.random.default_rng(keys["maintainer"] + 23)
        rng_dynamics = np.random.default_rng(keys["dynamics"] + 31)
    world = simulate_world(
        seed=int(seed), arm=arm, rng_world=rng_world,
        rng_thinning=rng_thinning, rng_maintainer=rng_maintainer,
        rng_dynamics=rng_dynamics,
    )
    world["seed_keys"] = keys
    world["torch_seed"] = int(keys["world"] + 4000)
    return world


__all__ = ["WorldDict", "EdgeTable", "generate_world", "seed_keys", "standardize_features"]
