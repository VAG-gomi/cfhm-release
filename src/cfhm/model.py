"""The public CFHM model implementation.

The implementation is extracted from the preserved F1-v2 and SPEC-002
mechanics. The shipped artifact documents a negative result: under the bound
regime the learned transmission channel remains near its initialization.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch

from .worlds import T_TRAIN, T_TEST, TAPS, WorldDict


@dataclass(frozen=True)
class FitReport:
    """Bound fit metadata returned by :meth:`CFHMModel.fit`."""

    epochs: int
    lambda1: float
    environment_count: int
    target_steps: int
    duration_seconds: float


class CFHMModel(torch.nn.Module):
    """Typed-edge CFHM model with a structurally bounded transmission channel."""

    def __init__(
        self,
        n_nodes: int = 200,
        seed: int | None = None,
        total_weeks: int = T_TRAIN + T_TEST,
        train_weeks: int = T_TRAIN,
        test_weeks: int = T_TEST,
    ) -> None:
        if int(n_nodes) <= 0:
            raise ValueError("n_nodes must be positive")
        if int(total_weeks) <= 0 or int(train_weeks) <= 0 or int(test_weeks) <= 0:
            raise ValueError("week counts must be positive")
        if int(train_weeks) + int(test_weeks) != int(total_weeks):
            raise ValueError("train_weeks + test_weeks must equal total_weeks")
        super().__init__()
        if seed is not None:
            torch.manual_seed(int(seed))
        self.n_nodes = int(n_nodes)
        self.total_weeks = int(total_weeks)
        self.train_weeks = int(train_weeks)
        self.test_weeks = int(test_weeks)
        # G2.1(b): keep the certified MLP shape, with the input projection
        # replaced at fit time only when the observed feature width differs.
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(9, 16),
            torch.nn.Tanh(),
            torch.nn.Linear(16, 1),
        )
        self.raw_b = torch.nn.Parameter(torch.full((3, 3), -4.0, dtype=torch.float64))
        self.raw_c = torch.nn.Parameter(torch.full((self.n_nodes,), -4.0, dtype=torch.float64))
        self.register_buffer("x", torch.zeros((self.n_nodes, 9), dtype=torch.float64))
        self.register_buffer("edge_src", torch.empty((0,), dtype=torch.long))
        self.register_buffer("edge_dst", torch.empty((0,), dtype=torch.long))
        self.register_buffer("edge_typ", torch.empty((0,), dtype=torch.long))
        self.double()
        self._fitted = False
        self._fit_report: FitReport | None = None
        self._current_e: np.ndarray | None = None
        self._current_r: np.ndarray | None = None

    def parameters_b(self) -> torch.Tensor:
        """Return nonnegative per-edge-type/tap amplitudes with row sum <= 0.95."""
        return (0.95 / 3.0) * torch.sigmoid(self.raw_b)

    def parameters_c(self) -> torch.Tensor:
        """Return nonnegative fragility-history coefficients."""
        return 2.0 * torch.sigmoid(self.raw_c)

    @property
    def fit_report(self) -> FitReport:
        self._require_fitted()
        assert self._fit_report is not None
        return self._fit_report

    def _require_fitted(self) -> None:
        if not self._fitted:
            raise RuntimeError("model not fitted: call fit() first")

    def _logits_from_states(
        self,
        e_states: torch.Tensor,
        r_states: torch.Tensor,
        *,
        include_transmission: bool = True,
    ) -> torch.Tensor:
        """Compute [time, node] logits; transmission is omitted for the do-mask branch."""
        a = self.mlp(self.x).squeeze(-1)
        msg = torch.zeros((e_states.shape[1], self.n_nodes), dtype=torch.float64, device=e_states.device)
        if include_transmission and self.edge_src.numel():
            b = self.parameters_b()
            e_by_edge = e_states[self.edge_src]
            edge_msg = (e_by_edge * b[self.edge_typ][:, None, :]).sum(dim=-1).transpose(0, 1)
            msg.scatter_add_(1, self.edge_dst[None, :].expand(e_states.shape[1], -1), edge_msg)
        return a[None, :] + msg - self.parameters_c()[None, :] * r_states.transpose(0, 1)

    def _forward_loss(
        self,
        e_states: torch.Tensor,
        r_states: torch.Tensor,
        targets: torch.Tensor,
        lambda1: float,
    ) -> torch.Tensor:
        logits = self._logits_from_states(e_states, r_states, include_transmission=True).transpose(0, 1)
        nll = torch.nn.functional.binary_cross_entropy_with_logits(logits, targets, reduction="mean")
        l1 = self.parameters_b().abs().sum()
        l2 = sum((p * p).sum() for p in self.mlp.parameters())
        return nll + float(lambda1) * l1 + 1e-4 * l2

    def fit(self, world: WorldDict, epochs: int = 50, lambda1: float = 0.01) -> FitReport:
        """Fit the CFHM model using the bound teacher-forced F1-v2 loop."""
        if not isinstance(world, dict):
            raise TypeError("world must be a WorldDict")
        if "events" not in world or "features_std" not in world or "visible_graph" not in world:
            raise ValueError("world is missing required CFHM fields")
        events = np.asarray(world["events"], dtype=np.int8)
        features = np.asarray(world["features_std"], dtype=float)
        if events.shape != (self.n_nodes, self.total_weeks):
            raise ValueError(f"events must have shape {(self.n_nodes, self.total_weeks)}")
        if features.ndim != 2 or features.shape[0] != self.n_nodes or features.shape[1] <= 0:
            raise ValueError(f"features_std must have shape ({self.n_nodes}, feature_width)")
        graph = world["visible_graph"]
        if self.mlp[0].in_features != int(features.shape[1]):
            self.mlp = torch.nn.Sequential(
                torch.nn.Linear(int(features.shape[1]), 16),
                torch.nn.Tanh(),
                torch.nn.Linear(16, 1),
            ).double()
        self.x = torch.as_tensor(features, dtype=torch.float64)
        self.edge_src = torch.as_tensor(np.asarray(graph["src"], dtype=np.int64), dtype=torch.long)
        self.edge_dst = torch.as_tensor(np.asarray(graph["dst"], dtype=np.int64), dtype=torch.long)
        self.edge_typ = torch.as_tensor(np.asarray(graph["typ"], dtype=np.int64), dtype=torch.long)
        e, r = _model_states(events[:, :self.train_weeks], self.train_weeks)
        state_e = torch.as_tensor(e[:, 1:self.train_weeks, :], dtype=torch.float64)
        state_r = torch.as_tensor(r[:, 1:self.train_weeks], dtype=torch.float64)
        targets = torch.as_tensor(events[:, 1:self.train_weeks], dtype=torch.float64)
        optimizer = torch.optim.Adam(self.parameters(), lr=1e-3)
        start = time.perf_counter()
        for _ in range(int(epochs)):
            optimizer.zero_grad(set_to_none=True)
            loss = self._forward_loss(state_e, state_r, targets, float(lambda1))
            loss.backward()
            optimizer.step()
        self._current_e = e[:, self.train_weeks].copy()
        self._current_r = r[:, self.train_weeks].copy()
        self._fitted = True
        self._fit_report = FitReport(
            epochs=int(epochs),
            lambda1=float(lambda1),
            environment_count=self.n_nodes,
            target_steps=int(targets.shape[1]),
            duration_seconds=float(time.perf_counter() - start),
        )
        return self._fit_report

    def forecast_hazard_mass(self) -> np.ndarray:
        """Forecast ex ante through the test window with event feedback fixed to zero."""
        self._require_fitted()
        assert self._current_e is not None and self._current_r is not None
        current_e = self._current_e.copy()
        current_r = self._current_r.copy()
        hazards: list[np.ndarray] = []
        self.eval()
        with torch.no_grad():
            for _ in range(self.test_weeks):
                state_e = torch.as_tensor(current_e[:, None, :], dtype=torch.float64)
                state_r = torch.as_tensor(current_r[:, None], dtype=torch.float64)
                logits = self._logits_from_states(state_e, state_r, include_transmission=True)[0, :].cpu().numpy()
                hazards.append(np.asarray(_sigmoid(logits), dtype=float))
                current_e *= TAPS[None, :]
                current_r *= 0.7
        return np.sum(np.stack(hazards, axis=1), axis=1)

    def interventional_hazard_mass(self) -> np.ndarray:
        """Forecast with the transmission channel do-masked out."""
        self._require_fitted()
        assert self._current_e is not None and self._current_r is not None
        current_e = self._current_e.copy()
        current_r = self._current_r.copy()
        hazards: list[np.ndarray] = []
        self.eval()
        with torch.no_grad():
            for _ in range(self.test_weeks):
                state_e = torch.as_tensor(current_e[:, None, :], dtype=torch.float64)
                state_r = torch.as_tensor(current_r[:, None], dtype=torch.float64)
                logits = self._logits_from_states(state_e, state_r, include_transmission=False)[0, :].cpu().numpy()
                hazards.append(np.asarray(_sigmoid(logits), dtype=float))
                current_e *= TAPS[None, :]
                current_r *= 0.7
        return np.sum(np.stack(hazards, axis=1), axis=1)

    def transmission_amplitudes(self) -> dict[str, float]:
        """Return the three tap-summed transmission amplitudes."""
        self._require_fitted()
        values = self.parameters_b().detach().cpu().numpy().sum(axis=1)
        return {name: float(values[i]) for i, name in enumerate(("major", "minor", "advisory"))}

    def spectral_radius(self) -> float:
        """Return the structural maximum row sum of the typed transmission matrix."""
        self._require_fitted()
        return float(self.parameters_b().detach().sum(dim=1).max().cpu())


def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def _model_states(events: np.ndarray, weeks: int) -> tuple[np.ndarray, np.ndarray]:
    n_nodes = int(np.asarray(events).shape[0])
    e = np.zeros((n_nodes, weeks + 1, 3), dtype=float)
    r = np.zeros((n_nodes, weeks + 1), dtype=float)
    for k in range(1, weeks + 1):
        e[:, k, :] = TAPS[None, :] * e[:, k - 1, :] + events[:, k - 1, None]
        r[:, k] = 0.7 * r[:, k - 1] + events[:, k - 1]
    return e, r


__all__ = ["CFHMModel", "FitReport"]
