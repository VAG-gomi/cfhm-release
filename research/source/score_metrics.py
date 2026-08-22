"""Shared scoring script for CFHM F1.

All methods use this module for ranking metrics. Ranking ties are resolved by
ascending node index, as bound by SPEC-001-R1.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

import numpy as np
from sklearn.metrics import roc_auc_score


def rank_desc(scores: np.ndarray) -> np.ndarray:
    """Return node indices ranked by descending score, then ascending index."""
    scores = np.asarray(scores, dtype=float)
    # lexsort uses the last key as primary: -score primary, index secondary.
    return np.lexsort((np.arange(scores.size), -np.nan_to_num(scores, nan=-np.inf)))


def precision_at(labels: np.ndarray, scores: np.ndarray, k: int) -> float:
    labels = np.asarray(labels, dtype=int)
    ranking = rank_desc(scores)
    return float(np.mean(labels[ranking[:k]]))


def metric_triplet(labels: np.ndarray, scores: np.ndarray) -> Mapping[str, float]:
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    if np.unique(labels).size < 2:
        auroc = float("nan")
    else:
        auroc = float(roc_auc_score(labels, scores))
    return {
        "precision_at_25": precision_at(labels, scores, 25),
        "precision_at_10": precision_at(labels, scores, 10),
        "auroc": auroc,
    }


def score_prediction_csv(path: str | Path) -> list[dict[str, object]]:
    import pandas as pd

    df = pd.read_csv(path)
    required = {"seed", "arm", "node", "label", "method_score"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(df.columns))}")
    rows: list[dict[str, object]] = []
    for (seed, arm, method), group in df.groupby(["seed", "arm", "method"], sort=True):
        metrics = metric_triplet(group["label"].to_numpy(), group["method_score"].to_numpy())
        rows.append({"seed": int(seed), "arm": str(arm), "method": str(method), **metrics})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Shared CFHM F1 scoring script")
    parser.add_argument("prediction_csv", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    rows = score_prediction_csv(args.prediction_csv)
    payload = json.dumps(rows, indent=2, allow_nan=True)
    if args.output_json:
        args.output_json.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
