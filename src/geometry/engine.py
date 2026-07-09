"""Motor Geométrico - Orquestador de operaciones espaciales.

Responsabilidad: Encapsular toda la funcionalidad geométrica en una interfaz
clara e integrada.
"""

from typing import Dict, List, Optional
import numpy as np
import networkx as nx
import plotly.graph_objects as go

from src.core.models import Proyecto
from src.geometry.distance_matrix import (
    calculate_distance_matrix,
    get_pilote_index_map,
)
from src.geometry.spatial_graph import build_spatial_graph, get_neighbors as graph_neighbors
from src.geometry.neighbors import identify_neighbors, neighbor_statistics
from src.geometry.visualizations import (
    plot_distance_heatmap,
    plot_project_geometry,
    plot_distance_distribution,
)


class MotorGeometrico:
    """Orquestador del motor geométrico del proyecto.

    Encapsula:
    - Cálculo de matriz de distancias
    - Construcción de grafo espacial
    - Identificación de vecinos
    - Visualizaciones

    Attributes:
        proyecto: Objeto Proyecto.
        distance_matrix: Matriz N×N de distancias (None hasta calcular).
        spatial_graph: Grafo espacial (None hasta calcular).
        neighbors: Dict de vecinos por pilote (None hasta calcular).
        pilote_index_map: Mapeo ID → índice en matriz (None hasta calcular).
    """

    def __init__(self, proyecto: Proyecto):
        """Inicializa motor geométrico.

        Args:
            proyecto: Objeto Proyecto con pilotes cargados.

        Raises:
            ValueError: Si proyecto no contiene pilotes.
        """
        if proyecto.num_pilotes == 0:
            raise ValueError("Proyecto debe contener al menos un pilote")

        self.proyecto = proyecto
        self.distance_matrix: Optional[np.ndarray] = None
        self.spatial_graph: Optional[nx.Graph] = None
        self.neighbors: Optional[Dict[str, List[str]]] = None
        self.pilote_index_map: Optional[Dict[str, int]] = None

    def calcular(self) -> None:
        """Ejecuta todas las operaciones del motor geométrico.

        Calcula:
        1. Matriz de distancias
        2. Mapeo de índices
        3. Grafo espacial
        4. Vecinos de cada pilote
        """
        # Calcular matriz de distancias
        self.distance_matrix = calculate_distance_matrix(self.proyecto)

        # Obtener mapeo de índices
        self.pilote_index_map = get_pilote_index_map(self.proyecto)

        # Construir grafo espacial
        self.spatial_graph = build_spatial_graph(self.proyecto, self.distance_matrix)

        # Identificar vecinos
        self.neighbors = identify_neighbors(self.proyecto, self.spatial_graph)

    def _validar_calculado(self) -> None:
        """Valida que el motor haya sido calculado.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
        """
        if self.distance_matrix is None or self.spatial_graph is None:
            raise RuntimeError("Debe ejecutar calcular() antes de usar el motor")

    # ========== Métodos de consulta de distancias ==========

    def get_distancia(self, pilote_id1: str, pilote_id2: str) -> float:
        """Obtiene distancia entre dos pilotes.

        Args:
            pilote_id1: ID del primer pilote.
            pilote_id2: ID del segundo pilote.

        Returns:
            Distancia euclidiana en metros.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
            ValueError: Si algún pilote no existe.
        """
        self._validar_calculado()

        if pilote_id1 not in self.pilote_index_map:
            raise ValueError(f"Pilote '{pilote_id1}' no existe")
        if pilote_id2 not in self.pilote_index_map:
            raise ValueError(f"Pilote '{pilote_id2}' no existe")

        idx1 = self.pilote_index_map[pilote_id1]
        idx2 = self.pilote_index_map[pilote_id2]

        return float(self.distance_matrix[idx1, idx2])

    # ========== Métodos de consulta de grafo ==========

    def get_vecinos(self, pilote_id: str) -> List[str]:
        """Obtiene vecinos de un pilote dentro del radio crítico.

        Args:
            pilote_id: ID del pilote.

        Returns:
            Lista de IDs de pilotes vecinos (ordenados alfabéticamente).

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
            ValueError: Si pilote no existe.
        """
        self._validar_calculado()

        if pilote_id not in self.neighbors:
            raise ValueError(f"Pilote '{pilote_id}' no existe")

        return self.neighbors[pilote_id]

    def hay_relacion_geotecnica(self, pilote_id1: str, pilote_id2: str) -> bool:
        """Verifica si dos pilotes están relacionados geotécnicamente.

        Args:
            pilote_id1: ID del primer pilote.
            pilote_id2: ID del segundo pilote.

        Returns:
            True si distancia ≤ radio_crítico, False en caso contrario.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
        """
        self._validar_calculado()

        try:
            distancia = self.get_distancia(pilote_id1, pilote_id2)
            return distancia <= self.proyecto.radio_critico_m
        except ValueError:
            return False

    # ========== Métodos de estadísticas ==========

    def get_estadisticas_geometria(self) -> dict:
        """Obtiene estadísticas de la geometría del proyecto.

        Returns:
            Diccionario con estadísticas.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
        """
        self._validar_calculado()

        stats = {
            "num_pilotes": self.proyecto.num_pilotes,
            "radio_critico_m": self.proyecto.radio_critico_m,
            "distancia_minima": float(np.min(self.distance_matrix[self.distance_matrix > 0])),
            "distancia_maxima": float(np.max(self.distance_matrix)),
            "distancia_promedio": float(
                np.mean(self.distance_matrix[np.triu_indices_from(self.distance_matrix, k=1)])
            ),
        }

        # Estadísticas del grafo
        stats["num_aristas_grafo"] = self.spatial_graph.number_of_edges()
        stats["densidad_grafo"] = nx.density(self.spatial_graph)

        # Estadísticas de vecinos
        stats.update(neighbor_statistics(self.neighbors))

        return stats

    # ========== Métodos de visualización ==========

    def plot_heatmap(self) -> go.Figure:
        """Genera heatmap interactivo de matriz de distancias.

        Returns:
            plotly.graph_objects.Figure.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
        """
        self._validar_calculado()
        return plot_distance_heatmap(self.proyecto, self.distance_matrix)

    def plot_geometry(self) -> go.Figure:
        """Genera visualización interactiva de geometría del proyecto.

        Returns:
            plotly.graph_objects.Figure.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
        """
        self._validar_calculado()
        return plot_project_geometry(self.proyecto, self.spatial_graph)

    def plot_distance_distribution(self) -> go.Figure:
        """Genera histograma de distribución de distancias.

        Returns:
            plotly.graph_objects.Figure.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
        """
        self._validar_calculado()
        return plot_distance_distribution(self.distance_matrix)

    def export_heatmap_html(self, filepath: str) -> None:
        """Exporta heatmap a archivo HTML.

        Args:
            filepath: Ruta del archivo HTML.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
        """
        fig = self.plot_heatmap()
        fig.write_html(filepath)

    def export_geometry_html(self, filepath: str) -> None:
        """Exporta visualización de geometría a archivo HTML.

        Args:
            filepath: Ruta del archivo HTML.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
        """
        fig = self.plot_geometry()
        fig.write_html(filepath)

    def export_distribution_html(self, filepath: str) -> None:
        """Exporta distribución de distancias a archivo HTML.

        Args:
            filepath: Ruta del archivo HTML.

        Raises:
            RuntimeError: Si no se ha ejecutado calcular().
        """
        fig = self.plot_distance_distribution()
        fig.write_html(filepath)
