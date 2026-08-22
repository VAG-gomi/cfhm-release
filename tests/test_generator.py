from __future__ import annotations

import numpy as np

from cfhm import generate_world


def test_generator_is_deterministic_and_hits_bound_anchors() -> None:
    a1_first = generate_world(1000, "A1")
    a1_second = generate_world(1000, "A1")
    for key in ("features_raw", "features_std", "events", "labels"):
        np.testing.assert_array_equal(a1_first[key], a1_second[key])
    assert a1_first["gamma_calibrated"] == -4.02490234375
    assert abs(a1_first["train_rate"] - 0.04004807692307692) <= 1e-9
    a2 = generate_world(1000, "A2")
    assert a2["gamma_calibrated"] == -3.712158203125
