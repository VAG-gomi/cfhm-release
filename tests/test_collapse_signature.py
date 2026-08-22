from __future__ import annotations

from cfhm import CFHMModel, generate_world


def test_bound_fit_reproduces_documented_collapse_signature() -> None:
    world = generate_world(1000, "A1")
    model = CFHMModel(seed=world["torch_seed"])
    model.fit(world, epochs=50, lambda1=0.01)
    amplitudes = model.transmission_amplitudes()
    assert all(value <= 0.05 for value in amplitudes.values()), amplitudes
