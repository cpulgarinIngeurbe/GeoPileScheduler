"""Construcción del grafo espacial basado en radio crítico.

Responsabilidad: Crear grafo donde nodos son pilotes y aristas conectan
pilotes dentro del radio crítico geotécnico.
"""

import networkx as nx
import numpy as np

from src.core.models import Proyecto
from src.geometry.distance_matrix import (
    calculate_distance_matrix,
    get_pilote_index_map,
)


def build_spatial_graph(
    proyecto: Proyecto, distance_matrix: np.ndarray | None = None
) -> nx.Graph:
    """Construye grafo espacial del proyecto.

    Crea un grafo donde:
    - Nodos: IDs de todos los pilotes
    - Aristas: Entre pilotes si distancia ≤ radio_critico_m
    - Pesos de aristas: Distancia euclidiana

    Args:
        proyecto: Objeto Proyecto.
        distance_matrix: Matriz pre-calculada (opcional). Si es None, se calcula.

    Returns:
        NetworkX Graph no dirigido.

    Raises:
        ValueError: Si proyecto no contiene pilotes.
    """
    if proyecto.num_pilotes == 0:
        raise ValueError("Proyecto no contiene pilotes")

    # Calcular matriz de distancias si no se proporciona
    if distance_matrix is None:
        distance_matrix = calculate_distance_matrix(proyecto)

    # Crear grafo vacío
    graph = nx.Graph()

    # Obtener mapeo de IDs a índices
    pilote_index_map = get_pilote_index_map(proyecto)
    pilotes_id = list(pilote_index_map.keys())
    n_pilotes = len(pilotes_id)

    # Agregar todos los pilotes como nodos
    graph.add_nodes_from(pilotes_id)

    # Agregar aristas si distancia ≤ radio_crítico
    radio_critico = proyecto.radio_critico_m

    for i in range(n_pilotes):
        for j in range(i + 1, n_pilotes):  # Evitar duplicados (i+1 porque es no dirigido)
            distancia = distance_matrix[i, j]

            if distancia <= radio_critico:
                pilote_i = pilotes_id[i]
                pilote_j = pilotes_id[j]
                # Agregar arista con peso (distancia)
                graph.add_edge(pilote_i, pilote_j, weight=distancia)

    return graph


def get_neighbors(graph: nx.Graph, pilote_id: str) -> list:
    """Obtiene vecinos directos de un pilote en el grafo.

    Args:
        graph: Grafo espacial.
        pilote_id: ID del pilote.

    Returns:
        Lista de IDs de pilotes vecinos.

    Raises:
        ValueError: Si pilote_id no existe en el grafo.
    """
    if pilote_id not in graph:
        raise ValueError(f"Pilote '{pilote_id}' no existe en el grafo")

    return list(graph.neighbors(pilote_id))


def get_edge_weight(graph: nx.Graph, pilote_id1: str, pilote_id2: str) -> float:
    """Obtiene peso (distancia) de una arista.

    Args:
        graph: Grafo espacial.
        pilote_id1: ID del primer pilote.
        pilote_id2: ID del segundo pilote.

    Returns:
        Distancia entre los pilotes.

    Raises:
        ValueError: Si la arista no existe.
    """
    if not graph.has_edge(pilote_id1, pilote_id2):
        raise ValueError(f"No hay arista entre {pilote_id1} y {pilote_id2}")

    return graph[pilote_id1][pilote_id2]["weight"]


def graph_stats(graph: nx.Graph) -> dict:
    """Calcula estadísticas del grafo.

    Args:
        graph: Grafo espacial.

    Returns:
        Diccionario con estadísticas.
    """
    return {
        "num_nodos": graph.number_of_nodes(),
        "num_aristas": graph.number_of_edges(),
        "densidad": nx.density(graph),
        "num_componentes_conexas": nx.number_connected_components(graph),
        "grado_promedio": sum(dict(graph.degree()).values()) / graph.number_of_nodes()
        if graph.number_of_nodes() > 0
        else 0,
    }
