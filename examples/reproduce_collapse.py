from __future__ import annotations

from cfhm import CFHMModel, generate_world


def main() -> int:
    world = generate_world(1000, "A1")
    model = CFHMModel(n_nodes=200, seed=world["torch_seed"])
    model.fit(world, epochs=50, lambda1=0.01)
    amplitudes = model.transmission_amplitudes()
    print("world=1000 arm=A1")
    print(f"gamma_calibrated={world['gamma_calibrated']:.12f}")
    print(f"train_rate={world['train_rate']:.12f}")
    print(f"transmission_amplitudes={amplitudes}")
    print(f"spectral_radius={model.spectral_radius():.12f}")
    print("collapse_signature=" + str(all(value <= 0.05 for value in amplitudes.values())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
