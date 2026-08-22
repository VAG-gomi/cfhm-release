from __future__ import annotations

from cfhm import CFHMModel, generate_world


def test_spectral_radius_cap_holds_after_fit() -> None:
    world = generate_world(1000, "A1")
    model = CFHMModel(seed=world["torch_seed"])
    model.fit(world, epochs=1, lambda1=0.01)
    assert model.spectral_radius() <= 0.95 + 1e-9
