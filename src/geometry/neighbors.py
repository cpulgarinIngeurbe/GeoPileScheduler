"""Identificación de vecinos para cada pilote.

Responsabilidad: Generar diccionario de vecinos (pilotes dentro del radio crítico).
"""

from typing import Dict, List

import networkx as nx

from src.core.models import Proyecto
from src.geometry.spatial_graph import build_spatial_graph


def identify_neighbors(
    proyecto: Proyecto, spatial_graph: nx.Graph | None = None
) -> Dict[str, List[str]]:
    """Identifica vecinos de cada pilote dentro del radio crítico.

    Crea diccionario donde cada pilote mapea a lista de pilotes vecinos
    (ordenados alfabéticamente por consistencia).

    Args:
        proyecto: Objeto Proyecto.
        spatial_graph: Grafo espacial pre-construido (opcional).

    Returns:
        Diccionario {pilote_id: [vecino_1, vecino_2, ...]}.
        Las listas de vecinos están ordenadas alfabéticamente.

    Raises:
        ValueError: Si proyecto no contiene pilotes.
    """
    if proyecto.num_pilotes == 0:
        raise ValueError("Proyecto no contiene pilotes")

    # Construir grafo si no se proporciona
    if spatial_graph is None:
        spatial_graph = build_spatial_graph(proyecto)

    # Crear diccionario de vecinos
    neighbors_dict: Dict[str, List[str]] = {}

    # Para cada pilote en el proyecto
    for unidad_id in proyecto.unidades:
        unidad = proyecto.unidades[unidad_id]
        for pilote_id in unidad.pilotes:
            # Obtener vecinos del grafo
            vecinos_raw = list(spatial_graph.neighbors(pilote_id))
            # Ordenar alfabéticamente para consistencia
            vecinos_ordenados = sorted(vecinos_raw)
            neighbors_dict[pilote_id] = vecinos_ordenados

    return neighbors_dict


def get_neighbors_for_pilote(
    neighbors_dict: Dict[str, List[str]], pilote_id: str
) -> List[str]:
    """Obtiene lista de vecinos para un pilote.

    Args:
        neighbors_dict: Diccionario de vecinos (output de identify_neighbors).
        pilote_id: ID del pilote.

    Returns:
        Lista de IDs de pilotes vecinos.

    Raises:
        KeyError: Si pilote_id no existe.
    """
    if pilote_id not in neighbors_dict:
        raise KeyError(f"Pilote '{pilote_id}' no encontrado en diccionario de vecinos")

    return neighbors_dict[pilote_id]


def neighbor_statistics(neighbors_dict: Dict[str, List[str]]) -> dict:
    """Calcula estadísticas sobre vecindad.

    Args:
        neighbors_dict: Diccionario de vecinos.

    Returns:
        Diccionario con estadísticas.
    """
    num_vecinos_lista = [len(vecinos) for vecinos in neighbors_dict.values()]

    if not num_vecinos_lista:
        return {
            "num_pilotes": 0,
            "promedio_vecinos": 0.0,
            "min_vecinos": 0,
            "max_vecinos": 0,
            "pilotes_sin_vecinos": 0,
        }

    return {
        "num_pilotes": len(neighbors_dict),
        "promedio_vecinos": sum(num_vecinos_lista) / len(num_vecinos_lista),
        "min_vecinos": min(num_vecinos_lista),
        "max_vecinos": max(num_vecinos_lista),
        "pilotes_sin_vecinos": sum(1 for n in num_vecinos_lista if n == 0),
    }
