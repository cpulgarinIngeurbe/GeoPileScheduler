"""Cálculo de matriz de distancias euclidianas.

Responsabilidad: Construir matriz N×N de distancias entre todos los pilotes.
"""

from typing import List, Tuple
import numpy as np

from src.core.models import Proyecto


def calculate_distance_matrix(proyecto: Proyecto) -> np.ndarray:
    """Calcula matriz euclidiana de distancias entre pilotes.

    Construye una matriz D de N×N donde:
    - N = número total de pilotes
    - D[i,j] = distancia euclidiana entre pilote_i y pilote_j
    - D es simétrica: D[i,j] = D[j,i]
    - D[i,i] = 0

    Args:
        proyecto: Objeto Proyecto con pilotes cargados.

    Returns:
        numpy.ndarray de shape (N, N) con dtype=float64.

    Raises:
        ValueError: Si no hay pilotes en el proyecto.
    """
    if proyecto.num_pilotes == 0:
        raise ValueError("Proyecto no contiene pilotes")

    # Extraer coordenadas de todos los pilotes en orden consistente
    coordenadas = _extraer_coordenadas(proyecto)
    n_pilotes = len(coordenadas)

    # Calcular matriz de distancias usando vectorización numpy
    # Más eficiente que loops Python
    distance_matrix = _calcular_distancias_vectorizado(coordenadas)

    return distance_matrix


def _extraer_coordenadas(proyecto: Proyecto) -> List[Tuple[float, float]]:
    """Extrae coordenadas (X, Y) de todos los pilotes en orden.

    Args:
        proyecto: Objeto Proyecto.

    Returns:
        Lista de tuplas (x, y) ordenadas por ID de pilote.
    """
    coordenadas: List[Tuple[float, float]] = []

    # Iterar por unidades y pilotes para obtener orden consistente
    for unidad_id in sorted(proyecto.unidades.keys()):
        unidad = proyecto.unidades[unidad_id]
        for pilote_id in sorted(unidad.pilotes.keys()):
            pilote = unidad.pilotes[pilote_id]
            coordenadas.append((pilote.x, pilote.y))

    return coordenadas


def _calcular_distancias_vectorizado(coordenadas: List[Tuple[float, float]]) -> np.ndarray:
    """Calcula matriz de distancias usando numpy vectorizado.

    Implementa: D[i,j] = sqrt((x_i - x_j)² + (y_i - y_j)²)

    Args:
        coordenadas: Lista de (x, y).

    Returns:
        Matriz numpy (N, N) con distancias euclidianas.

    Algorithm:
        1. Convertir coordenadas a array numpy
        2. Usar broadcasting para calcular diferencias
        3. Aplicar fórmula euclidiana de forma vectorizada
    """
    # Convertir a array numpy (N, 2)
    coords = np.array(coordenadas, dtype=np.float64)

    # Usar broadcasting para calcular distancias
    # shape: (N, 1, 2) - (1, N, 2) -> (N, N, 2)
    diferencias = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]

    # Calcular distancia euclidiana: sqrt(dx² + dy²)
    # shape: (N, N)
    distance_matrix = np.sqrt(np.sum(diferencias ** 2, axis=2))

    return distance_matrix


def get_distance(distance_matrix: np.ndarray, idx_i: int, idx_j: int) -> float:
    """Obtiene distancia entre dos pilotes por índice.

    Args:
        distance_matrix: Matriz de distancias.
        idx_i: Índice del pilote i.
        idx_j: Índice del pilote j.

    Returns:
        Distancia entre pilotes.
    """
    return float(distance_matrix[idx_i, idx_j])


def get_pilote_index_map(proyecto: Proyecto) -> dict:
    """Crea mapeo de ID pilote → índice en matriz de distancias.

    Args:
        proyecto: Objeto Proyecto.

    Returns:
        Diccionario {pilote_id: índice_en_matriz}.

    Note:
        Importante: El índice debe coincidir con el orden usado en
        _extraer_coordenadas() para que las consultas sean correctas.
    """
    pilote_to_index: dict = {}
    idx = 0

    for unidad_id in sorted(proyecto.unidades.keys()):
        unidad = proyecto.unidades[unidad_id]
        for pilote_id in sorted(unidad.pilotes.keys()):
            pilote_to_index[pilote_id] = idx
            idx += 1

    return pilote_to_index
