"""SPEC-002 CFHM component autopsy executor.

This module reads only the preserved F1-v2 NPZ/config artifacts, writes only to
f1_v2_autopsy/, evaluates the reproducibility gate before downstream variants,
and emits the specified evidence tables without applying author-only labels.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pandas as pd
import torch
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent
AUTO = ROOT / "f1_v2_autopsy"
V2 = ROOT / "f1_v2"
N = 200
T_TRAIN = 104
T_TEST = 26
T_TOTAL = T_TRAIN + T_TEST
TAPS = np.array([0.5, 0.8, 0.95], dtype=float)
LAMBDA_1 = 0.01
EPOCHS = 50
METHOD_VARIANTS = ("V-REFIT", "V-A0", "V-ORAC", "V-B3R")
EDGE_TYPES = ("major", "minor", "advisory")

# Import the existing F1-v2 model recursion and shared ranking implementation.
sys.path.insert(0, str(ROOT))
from run_experiment import metric_triplet, model_states, rank_desc  # noqa: E402
from score_metrics import precision_at  # noqa: E402


@dataclass
class SavedCase:
    seed: int
    arm: str
    npz_path: Path
    config_path: Path
    events: np.ndarray
    labels: np.ndarray
    features_raw: np.ndarray
    features_std: np.ndarray
    visible_src: np.ndarray
    visible_dst: np.ndarray
    visible_typ: np.ndarray
    fragility_truth: np.ndarray
    c_truth: np.ndarray
    b_truth: np.ndarray
    gamma: float
    kappa: float
    torch_seed: int


@dataclass
class FitResult:
    seed: int
    arm: str
    variant: str
    p_at_25: float
    b: np.ndarray | None
    spearman_rho: float | None
    duration_seconds: float


class TransmissionModel(torch.nn.Module):
    """CFHM-compatible model supporting fixed-zero, learned, and oracle base."""

    def __init__(
        self,
        x: np.ndarray,
        src: np.ndarray,
        dst: np.ndarray,
        typ: np.ndarray,
        torch_seed: int,
        *,
        base: np.ndarray | None = None,
        zero_channel: bool = False,
    ) -> None:
        super().__init__()
        torch.manual_seed(int(torch_seed))
        self.zero_channel = bool(zero_channel)
        if base is None:
            self.mlp = torch.nn.Sequential(
                torch.nn.Linear(9, 16),
                torch.nn.Tanh(),
                torch.nn.Linear(16, 1),
            )
            self.base = None
        else:
            self.mlp = None
            self.register_buffer("base_buffer", torch.as_tensor(base, dtype=torch.float64))
        if not self.zero_channel:
            self.raw_b = torch.nn.Parameter(torch.full((3, 3), -4.0, dtype=torch.float64))
        self.raw_c = torch.nn.Parameter(torch.full((N,), -4.0, dtype=torch.float64))
        self.register_buffer("x", torch.as_tensor(x, dtype=torch.float64))
        self.register_buffer("edge_src", torch.as_tensor(src, dtype=torch.long))
        self.register_buffer("edge_dst", torch.as_tensor(dst, dtype=torch.long))
        self.register_buffer("edge_typ", torch.as_tensor(typ, dtype=torch.long))
        self.double()

    def parameters_b(self) -> torch.Tensor:
        if self.zero_channel:
            return torch.zeros((3, 3), dtype=torch.float64, device=self.x.device)
        return (0.95 / 3.0) * torch.sigmoid(self.raw_b)

    def parameters_c(self) -> torch.Tensor:
        return 2.0 * torch.sigmoid(self.raw_c)

    def logits_from_states(self, e_states: torch.Tensor, r_states: torch.Tensor) -> torch.Tensor:
        if self.mlp is None:
            a = self.base_buffer
        else:
            a = self.mlp(self.x).squeeze(-1)
        b = self.parameters_b()
        e_by_edge = e_states[self.edge_src]
        edge_msg = (e_by_edge * b[self.edge_typ][:, None, :]).sum(dim=-1).transpose(0, 1)
        msg = torch.zeros((e_states.shape[1], N), dtype=torch.float64, device=e_states.device)
        if self.edge_src.numel():
            msg.scatter_add_(1, self.edge_dst[None, :].expand(e_states.shape[1], -1), edge_msg)
        return a[None, :] + msg - self.parameters_c()[None, :] * r_states.transpose(0, 1)

    def regularized_loss(
        self,
        state_e: torch.Tensor,
        state_r: torch.Tensor,
        targets: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        logits = self.logits_from_states(state_e, state_r).transpose(0, 1)
        nll = torch.nn.functional.binary_cross_entropy_with_logits(logits, targets, reduction="mean")
        l1 = self.parameters_b().abs().sum()
        l2 = torch.tensor(0.0, dtype=torch.float64)
        if self.mlp is not None:
            l2 = sum((p * p).sum() for p in self.mlp.parameters())
        return nll + LAMBDA_1 * l1 + 1e-4 * l2, logits


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def atomic_csv(path: Path, frame: pd.DataFrame, *, columns: list[str] | None = None) -> None:
    if columns is not None:
        frame = frame.reindex(columns=columns)
    buf = io.StringIO()
    frame.to_csv(buf, index=False, na_rep="")
    atomic_text(path, buf.getvalue())


def write_status(stage: str, cases_completed: int, note: str) -> None:
    atomic_text(
        AUTO / "STATUS.md",
        "# SPEC-002 STATUS\n\n"
        f"Stage: {stage}\n\n"
        f"Cases completed: {cases_completed}/100.\n\n"
        f"Note: {note}\n",
    )


def append_deviation(title: str, body: str) -> None:
    path = AUTO / "DEVIATIONS.md"
    with path.open("a", encoding="utf-8") as f:
        f.write(f"\n## {title}\n\n{body}\n")


def reset_generated_outputs() -> None:
    """Delete generated outputs at invocation start; preserve specs and ledger."""
    for name in ("AUTOPSY_ROWS.csv", "SUMMARY.csv", "D1_DELTAS.csv", "AUTOPSY_MANIFEST.sha256"):
        path = AUTO / name
        if path.exists():
            path.unlink()
    for name in ("results", "logs"):
        path = AUTO / name
        if path.exists():
            shutil.rmtree(path)
    (AUTO / "results").mkdir(parents=True, exist_ok=True)
    (AUTO / "logs").mkdir(parents=True, exist_ok=True)


def load_cases() -> list[SavedCase]:
    metrics = pd.read_csv(V2 / "metrics" / "per_seed_metrics.csv")
    stored = metrics[metrics["method"].eq("B4_CFHM")].set_index(["seed", "arm"])["precision_at_25"].to_dict()
    cases: list[SavedCase] = []
    errors: list[str] = []
    for seed in range(1000, 1050):
        for arm in ("A1", "A2"):
            npz_path = V2 / "data" / f"seed_{seed}_{arm}.npz"
            cfg_path = V2 / "configs" / f"seed_{seed}_{arm}.json"
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                with np.load(npz_path, allow_pickle=False) as z:
                    required = {
                        "events", "labels", "features_raw", "features_std", "visible_src",
                        "visible_dst", "visible_typ", "fragility_truth", "c_truth", "b_truth",
                    }
                    missing = sorted(required - set(z.files))
                    if missing:
                        raise ValueError(f"missing NPZ members: {missing}")
                    case = SavedCase(
                        seed=seed,
                        arm=arm,
                        npz_path=npz_path,
                        config_path=cfg_path,
                        events=np.asarray(z["events"], dtype=np.int8),
                        labels=np.asarray(z["labels"], dtype=np.int8),
                        features_raw=np.asarray(z["features_raw"], dtype=float),
                        features_std=np.asarray(z["features_std"], dtype=float),
                        visible_src=np.asarray(z["visible_src"], dtype=np.int64),
                        visible_dst=np.asarray(z["visible_dst"], dtype=np.int64),
                        visible_typ=np.asarray(z["visible_typ"], dtype=np.int64),
                        fragility_truth=np.asarray(z["fragility_truth"], dtype=float),
                        c_truth=np.asarray(z["c_truth"], dtype=float),
                        b_truth=np.asarray(z["b_truth"], dtype=float),
                        gamma=float(cfg["selected_gamma"]),
                        kappa=float(cfg["selected_kappa"]),
                        torch_seed=int(cfg["torch_seed"]),
                    )
                if (seed, arm) not in stored:
                    raise ValueError("stored B4 metric missing")
                cases.append(case)
            except Exception as exc:
                errors.append(f"seed={seed} arm={arm}: {type(exc).__name__}: {exc}")
    if errors:
        atomic_text(AUTO / "results" / "INPUT_ERRORS.txt", "\n".join(errors) + "\n")
        append_deviation("DEVIATION-017 — Input read failure", "\n".join(f"- {e}" for e in errors))
        raise RuntimeError("input read failure; see results/INPUT_ERRORS.txt")
    return cases


def make_data(case: SavedCase) -> SimpleNamespace:
    return SimpleNamespace(
        events=case.events,
        features_std=case.features_std,
        features_raw=case.features_raw,
        labels=case.labels,
        graph_visible=SimpleNamespace(src=case.visible_src, dst=case.visible_dst, typ=case.visible_typ),
    )


def fit_variant(case: SavedCase, variant: str) -> tuple[np.ndarray, np.ndarray | None, float]:
    data = make_data(case)
    e, r = model_states(data.events[:, :T_TRAIN], T_TRAIN)
    state_e = torch.as_tensor(e[:, 1:T_TRAIN, :], dtype=torch.float64)
    state_r = torch.as_tensor(r[:, 1:T_TRAIN], dtype=torch.float64)
    targets = torch.as_tensor(data.events[:, 1:T_TRAIN], dtype=torch.float64)
    base = None
    zero = variant == "V-A0"
    if variant == "V-ORAC":
        base = case.gamma + case.kappa * case.fragility_truth
    model = TransmissionModel(
        data.features_std,
        case.visible_src,
        case.visible_dst,
        case.visible_typ,
        case.torch_seed,
        base=base,
        zero_channel=zero,
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    started = time.monotonic()
    for _epoch in range(1, EPOCHS + 1):
        optimizer.zero_grad(set_to_none=True)
        loss, _logits = model.regularized_loss(state_e, state_r, targets)
        loss.backward()
        optimizer.step()
    duration = time.monotonic() - started
    if duration > 600.0:
        append_deviation(
            "DEVIATION-018 — Single fit exceeded ten minutes",
            f"seed={case.seed} arm={case.arm} variant={variant} duration_seconds={duration:.3f}",
        )
    with torch.no_grad():
        current_e = e[:, T_TRAIN].copy()
        current_r = r[:, T_TRAIN].copy()
        hazards: list[np.ndarray] = []
        model.eval()
        for _ in range(T_TEST):
            se = torch.as_tensor(current_e[:, None, :], dtype=torch.float64)
            sr = torch.as_tensor(current_r[:, None], dtype=torch.float64)
            logits = model.logits_from_states(se, sr)[0, :].cpu().numpy()
            hazards.append(1.0 / (1.0 + np.exp(-np.clip(logits, -60.0, 60.0))))
            current_e *= TAPS[None, :]
            current_r *= 0.7
        scores = np.sum(np.stack(hazards, axis=1), axis=1)
        b = None if variant in ("V-A0", "V-B3R") else model.parameters_b().cpu().numpy()
    return scores, b, duration


def fit_b3r(case: SavedCase) -> tuple[np.ndarray, float]:
    started = time.monotonic()
    clf = LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000)
    x_rows = np.repeat(case.features_std, T_TRAIN, axis=0)
    y_rows = case.events[:, :T_TRAIN].reshape(-1)
    clf.fit(x_rows, y_rows)
    scores = clf.predict_proba(case.features_std)[:, 1]
    duration = time.monotonic() - started
    if duration > 600.0:
        append_deviation(
            "DEVIATION-019 — B3 refit exceeded ten minutes",
            f"seed={case.seed} arm={case.arm} variant=V-B3R duration_seconds={duration:.3f}",
        )
    return scores, duration


def target_vector(case: SavedCase, variant: str) -> np.ndarray:
    if variant == "V-REFIT":
        return case.b_truth.reshape(-1)
    if variant == "V-ORAC":
        # Ground-truth per-type scalar is the sum of the three truth taps.
        return np.repeat(case.b_truth.sum(axis=1), 3)
    raise ValueError(variant)


def rho_for(b: np.ndarray, target: np.ndarray) -> float:
    value = spearmanr(b.reshape(-1), target.reshape(-1)).statistic
    return float(value) if np.isfinite(value) else float("nan")


def fit_to_row(case: SavedCase, variant: str, scores: np.ndarray, b: np.ndarray | None, duration: float) -> tuple[FitResult, dict[str, Any]]:
    p25 = precision_at(case.labels, scores, 25)
    rho = None
    if variant in ("V-REFIT", "V-ORAC") and b is not None:
        rho = rho_for(b, target_vector(case, variant))
    result = FitResult(case.seed, case.arm, variant, p25, b, rho, duration)
    row: dict[str, Any] = {
        "seed": case.seed,
        "arm": case.arm,
        "variant": variant,
        "p_at_25": p25,
        "S_major": None,
        "S_minor": None,
        "S_advisory": None,
        "spearman_rho": rho,
    }
    if variant in ("V-REFIT", "V-ORAC") and b is not None:
        row["S_major"] = float(b[0].sum())
        row["S_minor"] = float(b[1].sum())
        row["S_advisory"] = float(b[2].sum())
    return result, row


def read_stored_b4(case: SavedCase) -> float:
    metrics = pd.read_csv(V2 / "metrics" / "per_seed_metrics.csv")
    row = metrics[(metrics["seed"] == case.seed) & (metrics["arm"] == case.arm) & (metrics["method"] == "B4_CFHM")]
    if len(row) != 1:
        raise ValueError(f"stored B4 row count {len(row)}")
    return float(row.iloc[0]["precision_at_25"])


def write_manifest() -> None:
    manifest = AUTO / "AUTOPSY_MANIFEST.sha256"
    excluded = {manifest.name}
    lines: list[str] = []
    for path in sorted(AUTO.rglob("*")):
        if not path.is_file() or path.name in excluded or path.name.endswith(".tmp"):
            continue
        lines.append(f"{sha256_file(path)}  {path.relative_to(AUTO).as_posix()}")
    atomic_text(manifest, "\n".join(lines) + "\n")


def main() -> int:
    reset_generated_outputs()
    write_status("start: input audit and V-REFIT reproducibility stage", 0, "No downstream variant has been run.")
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    cases = load_cases()
    refit_rows: list[dict[str, Any]] = []
    refit_results: dict[tuple[int, str], FitResult] = {}
    deltas: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        scores, b, duration = fit_variant(case, "V-REFIT")
        result, row = fit_to_row(case, "V-REFIT", scores, b, duration)
        refit_results[(case.seed, case.arm)] = result
        refit_rows.append(row)
        stored = read_stored_b4(case)
        deltas.append({"seed": case.seed, "arm": case.arm, "p_at_25_refit": result.p_at_25, "p_at_25_v2stored_B4": stored, "delta_s": abs(result.p_at_25 - stored)})
        if index % 10 == 0:
            atomic_text(AUTO / "results" / "refit_progress.json", json.dumps({"cases_completed": index, "total": 100}, indent=2) + "\n")
    delta_df = pd.DataFrame(deltas).sort_values(["seed", "arm"])
    atomic_csv(AUTO / "D1_DELTAS.csv", delta_df, columns=["seed", "arm", "p_at_25_refit", "p_at_25_v2stored_B4", "delta_s"])
    pass_fraction = float((delta_df["delta_s"] <= 0.08).mean())
    worst_delta = float(delta_df["delta_s"].max())
    if pass_fraction < 0.90:
        append_deviation(
            "DEVIATION-020 — D1 reproducibility gate failed",
            f"d1_gate_pass_fraction={pass_fraction:.12g}; d1_worst_delta={worst_delta:.12g}; downstream variants were not run.",
        )
        write_status("completion: D1 gate failed; downstream stage halted", 100, "D1 deltas are transmitted; no downstream variant was run.")
        write_manifest()
        return 2

    rows: list[dict[str, Any]] = list(refit_rows)
    all_results: dict[tuple[int, str, str], FitResult] = {(r.seed, r.arm, r.variant): r for r in refit_results.values() for _ in [0]}
    # The preceding comprehension is intentionally replaced with explicit keys.
    all_results = {(r.seed, r.arm, "V-REFIT"): r for r in refit_results.values()}
    for index, case in enumerate(cases, start=1):
        for variant in ("V-A0", "V-ORAC"):
            scores, b, duration = fit_variant(case, variant)
            result, row = fit_to_row(case, variant, scores, b, duration)
            all_results[(case.seed, case.arm, variant)] = result
            rows.append(row)
        scores, duration = fit_b3r(case)
        result, row = fit_to_row(case, "V-B3R", scores, None, duration)
        all_results[(case.seed, case.arm, "V-B3R")] = result
        rows.append(row)
    row_df = pd.DataFrame(rows)
    row_df = row_df.sort_values(["seed", "arm", "variant"], key=lambda col: col.map({"A1": 0, "A2": 1, "V-REFIT": 0, "V-A0": 1, "V-ORAC": 2, "V-B3R": 3}).fillna(col))
    atomic_csv(AUTO / "AUTOPSY_ROWS.csv", row_df, columns=["seed", "arm", "variant", "p_at_25", "S_major", "S_minor", "S_advisory", "spearman_rho"])

    refit_df = row_df[row_df["variant"].eq("V-REFIT")].copy()
    a0_df = row_df[row_df["variant"].eq("V-A0")].copy()
    orac_df = row_df[row_df["variant"].eq("V-ORAC")].copy()
    b3_df = row_df[row_df["variant"].eq("V-B3R")].copy()
    gaps = {}
    oracle_lifts = {}
    oracle_b3_lifts = {}
    for arm in ("A1", "A2"):
        rr = refit_df[refit_df["arm"].eq(arm)].set_index("seed")
        aa = a0_df[a0_df["arm"].eq(arm)].set_index("seed")
        oo = orac_df[orac_df["arm"].eq(arm)].set_index("seed")
        bb = b3_df[b3_df["arm"].eq(arm)].set_index("seed")
        gaps[arm] = float(np.median(aa["p_at_25"] - rr["p_at_25"]))
        oracle_lifts[arm] = float(np.median(oo["p_at_25"] - rr["p_at_25"]))
        oracle_b3_lifts[arm] = float(np.median(oo["p_at_25"] - bb["p_at_25"]))
    sums = refit_df[["S_major", "S_minor", "S_advisory"]].to_numpy(dtype=float)
    collapse_fraction = float(np.all(sums <= 0.05, axis=1).mean())
    a2_refit = refit_df[refit_df["arm"].eq("A2")]
    amp_fraction = float(np.any(a2_refit[["S_major", "S_minor", "S_advisory"]].to_numpy(dtype=float) > 0.15, axis=1).mean())
    rho_median = float(a2_refit["spearman_rho"].median())
    summary_rows = [
        ("d1_gate_pass_fraction", pass_fraction),
        ("d1_worst_delta", worst_delta),
        ("g_A1", gaps["A1"]),
        ("g_A2", gaps["A2"]),
        ("collapse_fraction", collapse_fraction),
        ("amp_fraction", amp_fraction),
        ("rho_median_A2", rho_median),
        ("o_A1", oracle_lifts["A1"]),
        ("o_A2", oracle_lifts["A2"]),
        ("o_b3_A1", oracle_b3_lifts["A1"]),
        ("o_b3_A2", oracle_b3_lifts["A2"]),
    ]
    atomic_csv(AUTO / "SUMMARY.csv", pd.DataFrame(summary_rows, columns=["statistic", "value"]), columns=["statistic", "value"])
    atomic_text(AUTO / "results" / "execution_counts.json", json.dumps({"cases": 100, "fits": 400, "d1_gate_pass_fraction": pass_fraction}, indent=2) + "\n")
    write_status("completion: T1-T4 evidence generated", 100, "D1 passed; all four prescribed variants were fit for all 100 cases.")
    write_manifest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
