"""Módulo de optimización."""

from .base_optimizer import BaseOptimizer, Solucion
from .greedy_optimizer import GreedyOptimizer

__all__ = [
    "BaseOptimizer",
    "Solucion",
    "GreedyOptimizer",
]
