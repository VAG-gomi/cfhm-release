"""Deterministic metrics and state helpers for the CFHM research artifact."""
from __future__ import annotations

from typing import Mapping

import numpy as np

from .worlds import N, TAPS


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def rank_desc(scores: np.ndarray) -> np.ndarray:
    scores = np.asarray(scores, dtype=float)
    return np.lexsort((np.arange(scores.size), -scores))


def precision_at(labels: np.ndarray, scores: np.ndarray, k: int) -> float:
    labels = np.asarray(labels, dtype=int)
    order = rank_desc(np.asarray(scores, dtype=float))
    kk = min(int(k), labels.size)
    return float(labels[order[:kk]].mean()) if kk else float("nan")


def _binary_auroc(labels: np.ndarray, scores: np.ndarray) -> float:
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    pos = labels == 1
    neg = labels == 0
    if not pos.any() or not neg.any():
        return float("nan")
    order = np.lexsort((np.arange(scores.size), scores))
    ranks = np.empty(scores.size, dtype=float)
    ranks[order] = np.arange(1, scores.size + 1, dtype=float)
    u = ranks[pos].sum() - pos.sum() * (pos.sum() + 1) / 2.0
    return float(u / (pos.sum() * neg.sum()))


def metric_triplet(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    return {
        "precision_at_25": precision_at(labels, scores, 25),
        "precision_at_10": precision_at(labels, scores, 10),
        "auroc": _binary_auroc(labels, scores),
    }


def model_states(events: np.ndarray, weeks: int) -> tuple[np.ndarray, np.ndarray]:
    events = np.asarray(events)
    e = np.zeros((N, weeks + 1, 3), dtype=float)
    r = np.zeros((N, weeks + 1), dtype=float)
    for k in range(1, weeks + 1):
        e[:, k, :] = TAPS[None, :] * e[:, k - 1, :] + events[:, k - 1, None]
        r[:, k] = 0.7 * r[:, k - 1] + events[:, k - 1]
    return e, r


def summarize_transmission(b: np.ndarray) -> dict[str, float]:
    values = np.asarray(b, dtype=float).sum(axis=1)
    return {name: float(values[i]) for i, name in enumerate(("major", "minor", "advisory"))}


__all__ = ["metric_triplet", "model_states", "precision_at", "rank_desc", "sigmoid", "summarize_transmission"]
