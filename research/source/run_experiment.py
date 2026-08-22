"""SPEC-001 CFHM F1 execution script.

This implementation follows SPEC-001 and binding resolutions R1-R5. The code
keeps the world generator, model recursion, baselines, scoring, stability gate,
and verdict arithmetic explicit so raw artifacts can be audited.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from scipy.stats import kendalltau
from sklearn.linear_model import LogisticRegression

from score_metrics import metric_triplet, rank_desc


ROOT = Path(__file__).resolve().parent
SEEDS = list(range(1000, 1050))
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
LAMBDA_GRID = (1e-4, 1e-3, 1e-2)
KAPPA_PRIMARY = (0.25, 0.5, 1.0, 2.0, 4.0)
KAPPA_EXTENDED = (0.125, 8.0)
GAMMA = -3.2
METHODS = ("B1_in_degree", "B2_age_x_popularity", "B3_fragility_only", "B4_CFHM")


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git_value(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()
    except Exception as exc:
        return f"unavailable: {exc}"


def seed_keys(seed: int) -> dict[str, int]:
    """R16/R2 sanctioned SeedSequence child conversion."""
    children = np.random.SeedSequence(seed).spawn(6)
    names = ("world", "thinning", "maintainer", "dynamics", "model_init", "bootstrap")
    return {
        name: int(child.generate_state(1, dtype=np.uint32)[0])
        for name, child in zip(names, children)
    }


@dataclass
class EdgeTable:
    src: np.ndarray
    dst: np.ndarray
    typ: np.ndarray

    @property
    def size(self) -> int:
        return int(self.src.size)


@dataclass
class ArmData:
    seed: int
    arm: str
    graph_visible: EdgeTable
    graph_true: EdgeTable
    features_raw: np.ndarray
    features_std: np.ndarray
    events: np.ndarray
    labels: np.ndarray
    kappa: float | None
    gamma_final: float | None
    calibration_path: str
    train_rate: float | None
    rates_by_kappa: dict[str, float]
    fragility_truth: np.ndarray
    c_truth: np.ndarray
    b_truth: np.ndarray
    maintainers: np.ndarray
    status: str
    calibration_trace: list[dict[str, float | int | str]]


class CFHM(torch.nn.Module):
    def __init__(self, x: np.ndarray, edge_table: EdgeTable, torch_seed: int) -> None:
        super().__init__()
        torch.manual_seed(int(torch_seed))
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(9, 16),
            torch.nn.Tanh(),
            torch.nn.Linear(16, 1),
        )
        self.raw_b = torch.nn.Parameter(torch.full((3, 3), -4.0, dtype=torch.float64))
        self.raw_c = torch.nn.Parameter(torch.full((N,), -4.0, dtype=torch.float64))
        self.register_buffer("x", torch.as_tensor(x, dtype=torch.float64))
        self.register_buffer("edge_src", torch.as_tensor(edge_table.src, dtype=torch.long))
        self.register_buffer("edge_dst", torch.as_tensor(edge_table.dst, dtype=torch.long))
        self.register_buffer("edge_typ", torch.as_tensor(edge_table.typ, dtype=torch.long))
        self.double()

    def parameters_b(self) -> torch.Tensor:
        return (0.95 / 3.0) * torch.sigmoid(self.raw_b)

    def parameters_c(self) -> torch.Tensor:
        return 2.0 * torch.sigmoid(self.raw_c)

    def logits_from_states(self, e_states: torch.Tensor, r_states: torch.Tensor) -> torch.Tensor:
        # e_states: [N, time, 3], r_states: [N, time]. Time is the set of
        # state snapshots used to predict weeks 2..104 or future test weeks.
        a = self.mlp(self.x).squeeze(-1)
        b = self.parameters_b()
        e_by_edge = e_states[self.edge_src]  # [E, time, 3]
        edge_msg = (e_by_edge * b[self.edge_typ][:, None, :]).sum(dim=-1).transpose(0, 1)  # [time,E]
        msg = torch.zeros((e_states.shape[1], N), dtype=torch.float64)
        if self.edge_src.numel():
            msg.scatter_add_(1, self.edge_dst[None, :].expand(e_states.shape[1], -1), edge_msg)
        return a[None, :] + msg - self.parameters_c()[None, :] * r_states.transpose(0, 1)

    def forward_loss(
        self,
        e_states: torch.Tensor,
        r_states: torch.Tensor,
        targets: torch.Tensor,
        sample_weights: torch.Tensor | None,
        lambda_1: float,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        logits_tn = self.logits_from_states(e_states, r_states)
        logits = logits_tn.transpose(0, 1)
        nll = torch.nn.functional.binary_cross_entropy_with_logits(logits, targets, reduction="none")
        if sample_weights is None:
            nll_mean = nll.mean()
        else:
            w = sample_weights[:, None].expand_as(nll)
            nll_mean = (nll * w).sum() / w.sum().clamp_min(1.0)
        l1 = self.parameters_b().abs().sum()
        l2 = sum((p * p).sum() for p in self.mlp.parameters())
        loss = nll_mean + float(lambda_1) * l1 + 1e-4 * l2
        return loss, nll_mean, logits


def standardize_features(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.where(std > 0, std, 1.0)
    return (x - mean) / std, mean, std


def make_edge_table(src: list[int], dst: list[int], typ: list[int]) -> EdgeTable:
    return EdgeTable(np.asarray(src, dtype=np.int64), np.asarray(dst, dtype=np.int64), np.asarray(typ, dtype=np.int64))


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
) -> ArmData:
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
        return ArmData(seed, arm, visible_graph, true_graph, x_raw, x_std, np.zeros((N, T_TOTAL), dtype=np.int8), np.zeros(N, dtype=np.int8), None, None, "gamma-bisection-no-band", None, rates_by_kappa, fragility, c_truth, b_truth, maintainers, "RATE-EXCLUDED", calibration_trace)
    kappa, gamma_final, events, calibration_path, train_rate = selected
    labels = (events[:, T_TRAIN:T_TOTAL].sum(axis=1) >= 1).astype(np.int8)
    return ArmData(seed, arm, visible_graph, true_graph, x_raw, x_std, events, labels, kappa, gamma_final, calibration_path, train_rate, rates_by_kappa, fragility, c_truth, b_truth, maintainers, "ELIGIBLE", calibration_trace)


def model_states(events: np.ndarray, weeks: int) -> tuple[np.ndarray, np.ndarray]:
    e = np.zeros((N, weeks + 1, 3), dtype=float)
    r = np.zeros((N, weeks + 1), dtype=float)
    for k in range(1, weeks + 1):
        e[:, k, :] = TAPS[None, :] * e[:, k - 1, :] + events[:, k - 1, None]
        r[:, k] = 0.7 * r[:, k - 1] + events[:, k - 1]
    return e, r


def torch_fit(
    data: ArmData,
    lambda_1: float,
    epochs: int,
    torch_seed: int,
    fit_end_target_index: int,
    sample_weights: np.ndarray | None,
) -> tuple[CFHM, list[dict[str, Any]]]:
    e, r = model_states(data.events[:, :T_TRAIN], T_TRAIN)
    # Targets weeks 2..104, states after weeks 1..103.
    state_e = torch.as_tensor(e[:, 1:T_TRAIN, :], dtype=torch.float64)
    state_r = torch.as_tensor(r[:, 1:T_TRAIN], dtype=torch.float64)
    targets = torch.as_tensor(data.events[:, 1:T_TRAIN], dtype=torch.float64)
    model = CFHM(data.features_std, data.graph_visible, torch_seed)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    weights_t = None if sample_weights is None else torch.as_tensor(sample_weights, dtype=torch.float64)
    history: list[dict[str, Any]] = []
    # fit_end_target_index counts target rows from 0; e.g. 77 means weeks 2..78.
    for epoch in range(1, epochs + 1):
        optimizer.zero_grad(set_to_none=True)
        loss, nll, logits = model.forward_loss(
            state_e[:, :fit_end_target_index, :],
            state_r[:, :fit_end_target_index],
            targets[:, :fit_end_target_index],
            weights_t,
            lambda_1,
        )
        loss.backward()
        optimizer.step()
        with torch.no_grad():
            all_logits = model.logits_from_states(state_e, state_r).transpose(0, 1)
            val_nll = torch.nn.functional.binary_cross_entropy_with_logits(
                all_logits[:, fit_end_target_index:], targets[:, fit_end_target_index:], reduction="mean"
            )
        history.append({
            "epoch": epoch,
            "train_loss": float(loss.detach().cpu()),
            "train_nll": float(nll.detach().cpu()),
            "validation_nll": float(val_nll.detach().cpu()),
        })
    return model, history


def choose_lambda(data: ArmData, torch_seed: int) -> tuple[float, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    best: tuple[float, float] | None = None
    for lam in LAMBDA_GRID:
        model, history = torch_fit(data, lam, 50, torch_seed, 77, None)
        val = history[-1]["validation_nll"]
        rows.append({"lambda_1": lam, "validation_nll_final": val})
        candidate = (float(val), float(lam))
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best[1], rows


def forecast_cfhm(model: CFHM, data: ArmData) -> np.ndarray:
    # Freeze E,R at t=104 and propagate with n=0 through t=130.
    e, r = model_states(data.events[:, :T_TRAIN], T_TRAIN)
    current_e = e[:, T_TRAIN].copy()
    current_r = r[:, T_TRAIN].copy()
    hazards: list[np.ndarray] = []
    model.eval()
    with torch.no_grad():
        for _ in range(T_TEST):
            state_e = torch.as_tensor(current_e[:, None, :], dtype=torch.float64)
            state_r = torch.as_tensor(current_r[:, None], dtype=torch.float64)
            logits = model.logits_from_states(state_e, state_r)[0, :].cpu().numpy()
            hazards.append(np.asarray(sigmoid(logits), dtype=float))
            current_e *= TAPS[None, :]
            current_r *= 0.7
    return np.sum(np.stack(hazards, axis=1), axis=1)


def fit_b3(data: ArmData, multiplicities: np.ndarray | None = None) -> LogisticRegression:
    x_rows = np.repeat(data.features_std, T_TRAIN, axis=0)
    y_rows = data.events[:, :T_TRAIN].reshape(-1)
    weights = None if multiplicities is None else np.repeat(multiplicities, T_TRAIN)
    clf = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000)
    clf.fit(x_rows, y_rows, sample_weight=weights)
    return clf


def baseline_scores(data: ArmData) -> dict[str, np.ndarray]:
    indegree = distinct_in_degree(data.graph_visible)
    age = data.features_raw[:, 0]
    popularity_log = data.features_raw[:, 2]
    z_age = (age - age.mean()) / (age.std() if age.std() > 0 else 1.0)
    z_pop = (popularity_log - popularity_log.mean()) / (popularity_log.std() if popularity_log.std() > 0 else 1.0)
    b3 = fit_b3(data).predict_proba(data.features_std)[:, 1]
    return {
        "B1_in_degree": indegree,
        "B2_age_x_popularity": z_age + z_pop,
        "B3_fragility_only": b3,
    }


def bootstrap_stability(data: ArmData, lambda_1: float, torch_seed: int, rng_bootstrap: np.random.Generator) -> dict[str, Any]:
    full_model, _ = torch_fit(data, lambda_1, 50, torch_seed, 103, None)
    full_cfhm = forecast_cfhm(full_model, data)
    full_b3 = fit_b3(data)
    full_b3_scores = full_b3.predict_proba(data.features_std)[:, 1]
    full_cfhm_rank = rank_desc(full_cfhm)
    full_b3_rank = rank_desc(full_b3_scores)
    taus_cfhm: list[float] = []
    taus_b3: list[float] = []
    for rep in range(10):
        multiplicities = np.bincount(rng_bootstrap.integers(0, N, size=N), minlength=N).astype(float)
        boot_model, _ = torch_fit(data, lambda_1, 50, torch_seed, 103, multiplicities)
        boot_cfhm = forecast_cfhm(boot_model, data)
        boot_b3 = fit_b3(data, multiplicities).predict_proba(data.features_std)[:, 1]
        tau_cfhm = kendalltau(full_cfhm_rank, rank_desc(boot_cfhm)).statistic
        tau_b3 = kendalltau(full_b3_rank, rank_desc(boot_b3)).statistic
        taus_cfhm.append(float(tau_cfhm) if np.isfinite(tau_cfhm) else 0.0)
        taus_b3.append(float(tau_b3) if np.isfinite(tau_b3) else 0.0)
    return {
        "cfhm_taus": taus_cfhm,
        "b3_taus": taus_b3,
        "cfhm_mean_tau": float(np.mean(taus_cfhm)),
        "b3_mean_tau": float(np.mean(taus_b3)),
        "cfhm_gate": bool(np.mean(taus_cfhm) >= 0.5),
        "b3_gate": bool(np.mean(taus_b3) >= 0.5),
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=True) + "\n", encoding="utf-8")


def append_rows_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def save_arm_data(data: ArmData, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        seed=data.seed,
        arm=data.arm,
        visible_src=data.graph_visible.src,
        visible_dst=data.graph_visible.dst,
        visible_typ=data.graph_visible.typ,
        true_src=data.graph_true.src,
        true_dst=data.graph_true.dst,
        true_typ=data.graph_true.typ,
        features_raw=data.features_raw,
        features_std=data.features_std,
        events=data.events,
        labels=data.labels,
        kappa=np.nan if data.kappa is None else data.kappa,
        train_rate=np.nan if data.train_rate is None else data.train_rate,
        fragility_truth=data.fragility_truth,
        c_truth=data.c_truth,
        b_truth=data.b_truth,
        maintainers=data.maintainers,
        gamma_final=np.nan if data.gamma_final is None else data.gamma_final,
        calibration_path=data.calibration_path,
    )


def make_environment(root: Path) -> None:
    packages = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    payload = "".join([
        f"python={sys.version}\n",
        f"platform={platform.platform()}\n",
        f"numpy={np.__version__}\n",
        f"torch={torch.__version__}\n",
        f"git_commit={git_value(['rev-parse', 'HEAD'])}\n",
        "\n# pip freeze\n",
        packages,
    ])
    (root / "environment.txt").write_text(payload, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="1000:1049", help="inclusive range, e.g. 1000:1002")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--append", action="store_true", help="append seed range to an existing isolated v2 root")
    args = parser.parse_args()
    root = args.root.resolve()
    start, end = (int(v) for v in args.seeds.split(":"))
    seeds = list(range(start, end + 1))
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    for sub in ("configs", "data", "loss_curves", "predictions", "metrics", "logs", "plots"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    make_environment(root)
    command = " ".join([sys.executable, *sys.argv])
    all_metrics: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    status_rows: list[dict[str, Any]] = []
    pred_path = root / "predictions" / "per_seed_predictions.csv"
    loss_path = root / "loss_curves" / "full_loss_curves.csv"
    if args.append:
        if (root / "metrics" / "per_seed_metrics.json").exists():
            all_metrics = json.loads((root / "metrics" / "per_seed_metrics.json").read_text(encoding="utf-8"))
        if (root / "metrics" / "stability.csv").exists() and (root / "metrics" / "stability.csv").stat().st_size > 0:
            stability_rows = pd.read_csv(root / "metrics" / "stability.csv").to_dict(orient="records")
        if (root / "metrics" / "seed_status.json").exists():
            status_rows = json.loads((root / "metrics" / "seed_status.json").read_text(encoding="utf-8"))
    else:
        if pred_path.exists():
            pred_path.unlink()
        if loss_path.exists():
            loss_path.unlink()
    loss_fields = ["seed", "arm", "fit", "lambda_1", "epoch", "train_loss", "train_nll", "validation_nll"]
    pred_fields = ["seed", "arm", "status", "calibration_path", "selected_kappa", "selected_gamma", "train_rate", "node", "label", "method", "method_score"]
    for seed in seeds:
        keys = seed_keys(seed)
        rng_world = np.random.default_rng(keys["world"])
        rng_thinning = np.random.default_rng(keys["thinning"])
        rng_maintainer = np.random.default_rng(keys["maintainer"])
        rng_dynamics = np.random.default_rng(keys["dynamics"])
        rng_bootstrap = np.random.default_rng(keys["bootstrap"])
        # World graph and world-side variables are independently regenerated per arm
        # by resetting streams to the same authored seed-derived states so A1/A2 share
        # the same base graph/features/parameters before the arm-specific mechanisms.
        arm_data: dict[str, ArmData] = {}
        for arm in ("A1", "A2"):
            if arm == "A2":
                # R16 gives one stream per seed; use deterministic child-derived
                # substreams for the two independently generated arms without any
                # additional random source.
                arm_offset = 0
                arm_world = np.random.default_rng(keys["world"] + arm_offset)
                arm_thin = np.random.default_rng(keys["thinning"] + 17)
                arm_maint = np.random.default_rng(keys["maintainer"] + 23)
                arm_dyn = np.random.default_rng(keys["dynamics"] + 31)
            else:
                arm_world, arm_thin, arm_maint, arm_dyn = rng_world, rng_thinning, rng_maintainer, rng_dynamics
            data = simulate_world(
                seed=seed,
                arm=arm,
                rng_world=arm_world,
                rng_thinning=arm_thin,
                rng_maintainer=arm_maint,
                rng_dynamics=arm_dyn,
            )
            arm_data[arm] = data
            status_rows.append({
                "seed": seed,
                "arm": arm,
                "status": data.status,
                "calibration_path": data.calibration_path,
                "selected_kappa": data.kappa,
                "selected_gamma": data.gamma_final,
                "train_rate": data.train_rate,
                "rates_by_kappa": data.rates_by_kappa,
                "calibration_trace": data.calibration_trace,
                "true_edges": data.graph_true.size,
                "visible_edges": data.graph_visible.size,
                "maintainers": data.maintainers.tolist(),
            })
            write_json(root / "configs" / f"seed_{seed}_{arm}.json", {
                "spec": "SPEC-001 + SPEC-001-R1 + SPEC-001-R2 + SPEC-001-R3 + SPEC-001-R4 + SPEC-001-R5 + SPEC-001-R6 + SPEC-001-R7",
                "seed": seed,
                "arm": arm,
                "seed_keys": keys,
                "torch_seed": int(keys["world"] + 4000),
                "command": command,
                "status": data.status,
                "calibration_path": data.calibration_path,
                "selected_kappa": data.kappa,
                "selected_gamma": data.gamma_final,
                "kappa_candidates": [0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0],
                "gamma_fixed": GAMMA,
                "gamma_fallback_bounds": [-8.0, -1.0],
                "gamma_fallback_iterations": 12,
                "lambda_grid": list(LAMBDA_GRID),
                "epochs": 50,
                "learning_rate": 1e-3,
                "bootstrap_replicates": 10,
                "n": N,
                "t_train": T_TRAIN,
                "t_test": T_TEST,
                "spec_hashes": {
                    name: sha256_file(root / "spec" / name)
                    for name in ("SPEC-001-authored.txt", "SPEC-001-R1-authored.md", "SPEC-001-R2-authored.md", "SPEC-001-R3-authored.md", "SPEC-001-R4-authored.md", "SPEC-001-R5-authored.md", "SPEC-001-R6-authored.md", "SPEC-001-R7-authored.md")
                },
            })
            save_arm_data(data, root / "data" / f"seed_{seed}_{arm}.npz")
            if data.status != "ELIGIBLE":
                for node in range(N):
                    for method in METHODS:
                        append_rows_csv(pred_path, [{
                            "seed": seed, "arm": arm, "status": data.status,
                            "calibration_path": data.calibration_path, "selected_kappa": "", "selected_gamma": "", "train_rate": "", "node": node,
                            "label": "", "method": method, "method_score": "",
                        }], pred_fields)
                continue
            base_scores = baseline_scores(data)
            lambda_1, grid_rows = choose_lambda(data, int(keys["world"] + 4000))
            for row in grid_rows:
                append_rows_csv(root / "loss_curves" / "lambda_selection.csv", [{"seed": seed, "arm": arm, **row}], ["seed", "arm", "lambda_1", "validation_nll_final"])
            model, history = torch_fit(data, lambda_1, 50, int(keys["world"] + 4000), 103, None)
            for row in history:
                append_rows_csv(loss_path, [{"seed": seed, "arm": arm, "fit": "full_refit", "lambda_1": lambda_1, **row}], loss_fields)
            cfhm_score = forecast_cfhm(model, data)
            method_scores = {**base_scores, "B4_CFHM": cfhm_score}
            for method, scores in method_scores.items():
                metrics = metric_triplet(data.labels, scores)
                all_metrics.append({"seed": seed, "arm": arm, "method": method, **metrics, "lambda_1": lambda_1, "status": data.status, "calibration_path": data.calibration_path, "train_rate": data.train_rate, "selected_kappa": data.kappa, "selected_gamma": data.gamma_final})
                rows = []
                for node in range(N):
                    rows.append({"seed": seed, "arm": arm, "status": data.status, "calibration_path": data.calibration_path, "selected_kappa": data.kappa, "selected_gamma": data.gamma_final, "train_rate": data.train_rate, "node": node, "label": int(data.labels[node]), "method": method, "method_score": float(scores[node])})
                append_rows_csv(pred_path, rows, pred_fields)
            stability = bootstrap_stability(data, lambda_1, int(keys["world"] + 4000), rng_bootstrap)
            stability_rows.append({"seed": seed, "arm": arm, "lambda_1": lambda_1, **stability})
            write_json(root / "metrics" / f"stability_seed_{seed}_{arm}.json", stability)
            print(f"completed seed={seed} arm={arm} rate={data.train_rate:.5f} lambda={lambda_1:g}", flush=True)
    write_json(root / "metrics" / "per_seed_metrics.json", all_metrics)
    pd.DataFrame(all_metrics).to_csv(root / "metrics" / "per_seed_metrics.csv", index=False)
    pd.DataFrame(stability_rows).to_csv(root / "metrics" / "stability.csv", index=False)
    pd.DataFrame(status_rows).to_json(root / "metrics" / "seed_status.json", orient="records", indent=2)
    write_json(root / "metrics" / "seed_status.json", status_rows)
    eligible_metrics = pd.DataFrame(all_metrics)
    eligible_stability = pd.DataFrame(stability_rows)
    verdict: dict[str, Any] = {"spec": "SPEC-001", "arms": {}, "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    for arm in ("A1", "A2"):
        arm_status = [r for r in status_rows if r["arm"] == arm]
        eligible_seeds = [int(r["seed"]) for r in arm_status if r["status"] == "ELIGIBLE"]
        excluded = [int(r["seed"]) for r in arm_status if r["status"] != "ELIGIBLE"]
        arm_metrics = eligible_metrics[eligible_metrics["arm"] == arm] if not eligible_metrics.empty else pd.DataFrame()
        pass_rows = []
        kill_rows = []
        for seed in eligible_seeds:
            m = arm_metrics[arm_metrics["seed"] == seed].set_index("method")
            base = float(m.loc[["B1_in_degree", "B2_age_x_popularity", "B3_fragility_only"], "precision_at_25"].max())
            cfhm = float(m.loc["B4_CFHM", "precision_at_25"])
            rel_best = (cfhm - base) / max(base, 0.01)
            b3 = float(m.loc["B3_fragility_only", "precision_at_25"])
            rel_b3 = (cfhm - b3) / max(b3, 0.01)
            pass_rows.append({"seed": seed, "cfhm_p25": cfhm, "best_baseline_p25": base, "relative_improvement": rel_best, "pass_seed": bool(rel_best >= 0.20)})
            kill_rows.append({"seed": seed, "cfhm_p25": cfhm, "b3_p25": b3, "relative_improvement_vs_b3": rel_b3, "kill_b3_seed": bool(rel_b3 < 0.05)})
        pass_fraction = float(np.mean([r["pass_seed"] for r in pass_rows])) if pass_rows else float("nan")
        kill_fraction = float(np.mean([r["kill_b3_seed"] for r in kill_rows])) if kill_rows else float("nan")
        stab = eligible_stability[eligible_stability["arm"] == arm] if not eligible_stability.empty else pd.DataFrame()
        cfhm_stable = bool((stab["cfhm_gate"].all()) if not stab.empty else False)
        b3_stable = bool((stab["b3_gate"].all()) if not stab.empty else False)
        verdict["arms"][arm] = {
            "eligible_seeds": eligible_seeds,
            "rate_excluded_seeds": excluded,
            "n_eligible": len(eligible_seeds),
            "pass_seed_fraction": pass_fraction,
            "pass_criterion_met_before_stability": bool(pass_fraction >= 0.80) if pass_rows else False,
            "kill_b3_seed_fraction": kill_fraction,
            "kill_b3_criterion_met": bool(kill_fraction >= 0.50) if kill_rows else False,
            "cfhm_stability_gate_all_seeds": cfhm_stable,
            "b3_stability_gate_all_seeds": b3_stable,
            "per_seed_pass": pass_rows,
            "per_seed_kill_b3": kill_rows,
            "decision_grade": bool(cfhm_stable and b3_stable),
        }
    a2 = verdict["arms"]["A2"]
    if any(r["status"] != "ELIGIBLE" for r in status_rows):
        verdict["overall"] = "INCONCLUSIVE_RATE_EXCLUSIONS"
    elif not a2["decision_grade"]:
        verdict["overall"] = "INCONCLUSIVE_STABILITY_GATE"
    elif a2["kill_b3_criterion_met"]:
        verdict["overall"] = "KILL-B3"
    elif a2["pass_criterion_met_before_stability"]:
        verdict["overall"] = "PASS"
    else:
        verdict["overall"] = "INCONCLUSIVE_OR_FAIL"
    write_json(root / "metrics" / "verdict.json", verdict)
    (root / "metrics" / "verdict.md").write_text(render_verdict_md(verdict), encoding="utf-8")
    make_summary_plot(root, eligible_metrics)
    print(json.dumps({"overall": verdict["overall"], "arms": {a: {k: v for k, v in d.items() if k not in ("per_seed_pass", "per_seed_kill_b3")} for a, d in verdict["arms"].items()}}, indent=2, allow_nan=True))


def render_verdict_md(verdict: dict[str, Any]) -> str:
    lines = ["# SPEC-001 F1 Preregistered Verdict", "", f"**Overall status:** `{verdict['overall']}`", ""]
    for arm, payload in verdict["arms"].items():
        lines.extend([
            f"## {arm}", "",
            f"Eligible seeds: {payload['n_eligible']}.",
            f"Rate-excluded seeds: {payload['rate_excluded_seeds']}.",
            f"PASS fraction before stability: {payload['pass_seed_fraction']:.6f}.",
            f"KILL-B3 fraction: {payload['kill_b3_seed_fraction']:.6f}.",
            f"CFHM stability gate across eligible seeds: `{payload['cfhm_stability_gate_all_seeds']}`.",
            f"B3 stability gate across eligible seeds: `{payload['b3_stability_gate_all_seeds']}`.",
            f"Decision-grade: `{payload['decision_grade']}`.", "",
        ])
    lines.extend(["## Provenance note", "", "This verdict is derived from the raw per-seed predictions, labels, metrics, and stability records. The raw tables remain the evidence.", ""])
    return "\n".join(lines)


def make_summary_plot(root: Path, metrics: pd.DataFrame) -> None:
    if metrics.empty:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    summary = metrics.groupby(["arm", "method"], as_index=False)["precision_at_25"].mean()
    fig, ax = plt.subplots(figsize=(9, 5))
    for arm in ("A1", "A2"):
        sub = summary[summary["arm"] == arm]
        ax.bar([f"{arm}\n{m.replace('_', ' ')}" for m in sub["method"]], sub["precision_at_25"], label=arm)
    ax.set_ylabel("Mean Precision@25")
    ax.set_title("SPEC-001 F1 diagnostic: mean Precision@25 by arm and method")
    ax.tick_params(axis="x", labelrotation=25)
    fig.tight_layout()
    fig.savefig(root / "plots" / "mean_precision_at_25.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
