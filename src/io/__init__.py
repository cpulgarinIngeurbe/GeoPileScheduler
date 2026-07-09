"""Módulo io: Lectura y escritura de datos (Excel, exportación)."""

from src.io.loader import load_project
from src.io.validator import validate_project_data

__all__ = [
    "load_project",
    "validate_project_data",
]
