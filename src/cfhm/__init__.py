"""CFHM — Contagion-Fragility Hazard Model research artifact."""

from .model import CFHMModel, FitReport
from .worlds import WorldDict, generate_world

__version__ = "0.1.0"

__all__ = ["CFHMModel", "FitReport", "WorldDict", "generate_world", "__version__"]
