from __future__ import annotations

import numpy as np

from cfhm import CFHMModel, generate_world
from cfhm.metrics import model_states


def test_undeclared_edges_have_structural_zero_excitation() -> None:
    world = generate_world(1000, "A1")
    empty_graph = {
        "src": np.empty(0, dtype=np.int64),
        "dst": np.empty(0, dtype=np.int64),
        "typ": np.empty(0, dtype=np.int64),
    }
    world["visible_graph"] = empty_graph
    model = CFHMModel(seed=world["torch_seed"])
    model.fit(world, epochs=1, lambda1=0.01)
    e, r = model_states(world["events"][:, :104], 104)
    import torch

    state_e = torch.as_tensor(e[:, 104:105, :], dtype=torch.float64)
    state_r = torch.as_tensor(r[:, 104:105], dtype=torch.float64)
    with torch.no_grad():
        masked = model._logits_from_states(state_e, state_r, include_transmission=True).cpu().numpy()
        do_masked = model._logits_from_states(state_e, state_r, include_transmission=False).cpu().numpy()
    np.testing.assert_array_equal(masked, do_masked)
