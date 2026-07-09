"""Visualizaciones interactivas con Plotly.

Responsabilidad: Generar visualizaciones gráficas del proyecto (heatmap, geometría).
"""

from typing import Tuple
import numpy as np
import plotly.graph_objects as go
import networkx as nx

from src.core.models import Proyecto
from src.geometry.distance_matrix import get_pilote_index_map


def plot_distance_heatmap(
    proyecto: Proyecto, distance_matrix: np.ndarray
) -> go.Figure:
    """Genera heatmap interactivo de matriz de distancias.

    Visualiza la matriz N×N de distancias entre pilotes con escala de colores.
    Los colores representan distancias (azul=cerca, rojo=lejos).

    Args:
        proyecto: Objeto Proyecto.
        distance_matrix: Matriz de distancias (N, N).

    Returns:
        plotly.graph_objects.Figure con heatmap interactivo.
    """
    # Obtener mapeo para etiquetar ejes
    pilote_index_map = get_pilote_index_map(proyecto)
    pilote_ids = list(pilote_index_map.keys())

    # Crear heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=distance_matrix,
            x=pilote_ids,
            y=pilote_ids,
            colorscale="Viridis",
            colorbar=dict(title="Distancia (m)"),
            hovertemplate="Pilote %{x} → %{y}: %{z:.2f} m<extra></extra>",
        )
    )

    # Actualizar layout
    fig.update_layout(
        title=f"Matriz de Distancias - {proyecto.nombre}",
        xaxis_title="Pilote",
        yaxis_title="Pilote",
        width=900,
        height=800,
        font=dict(size=10),
    )

    return fig


def plot_project_geometry(
    proyecto: Proyecto, spatial_graph: nx.Graph | None = None
) -> go.Figure:
    """Genera visualización interactiva de la geometría del proyecto.

    Muestra:
    - Pilotes como puntos (X, Y)
    - Líneas entre pilotes vecinos (aristas del grafo)
    - Colores por unidad estructural
    - Tamaño de marcador proporcional a número de vecinos

    Args:
        proyecto: Objeto Proyecto.
        spatial_graph: Grafo espacial pre-construido (opcional).

    Returns:
        plotly.graph_objects.Figure con visualización interactiva.
    """
    from src.geometry.spatial_graph import build_spatial_graph

    if spatial_graph is None:
        spatial_graph = build_spatial_graph(proyecto)

    # Crear figura
    fig = go.Figure()

    # Definir colores por unidad estructural
    color_map = {
        uid: f"hsl({i * 360 / len(proyecto.unidades)}, 70%, 50%)"
        for i, uid in enumerate(sorted(proyecto.unidades.keys()))
    }

    # Agregar aristas (líneas entre pilotes vecinos)
    for pilote_id1, pilote_id2 in spatial_graph.edges():
        # Obtener coordenadas
        pilote1 = proyecto.obtener_pilote(pilote_id1)
        pilote2 = proyecto.obtener_pilote(pilote_id2)

        if pilote1 and pilote2:
            fig.add_trace(
                go.Scatter(
                    x=[pilote1.x, pilote2.x],
                    y=[pilote1.y, pilote2.y],
                    mode="lines",
                    line=dict(color="rgba(100, 100, 100, 0.3)", width=1),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

    # Agregar pilotes (puntos)
    for unidad_id in sorted(proyecto.unidades.keys()):
        unidad = proyecto.unidades[unidad_id]
        xs = []
        ys = []
        texts = []
        sizes = []
        pilote_ids = []

        for pilote_id in sorted(unidad.pilotes.keys()):
            pilote = unidad.pilotes[pilote_id]
            xs.append(pilote.x)
            ys.append(pilote.y)

            # Número de vecinos determina tamaño
            num_vecinos = len(list(spatial_graph.neighbors(pilote_id)))
            tamaño = 8 + num_vecinos * 2  # Tamaño base + proporcional a vecinos

            sizes.append(tamaño)
            texts.append(
                f"<b>{pilote_id}</b><br>({pilote.x:.2f}, {pilote.y:.2f})<br>Unidad: {unidad.nombre}<br>Vecinos: {num_vecinos}"
            )
            pilote_ids.append(pilote_id)

        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                marker=dict(
                    size=sizes,
                    color=color_map[unidad_id],
                    line=dict(width=1, color="white"),
                    opacity=0.8,
                ),
                text=pilote_ids,
                textposition="top center",
                textfont=dict(size=8),
                hovertext=texts,
                hoverinfo="text",
                name=f"Unidad {unidad.nombre}",
                showlegend=True,
            )
        )

    # Actualizar layout
    fig.update_layout(
        title=f"Geometría del Proyecto - {proyecto.nombre}",
        xaxis_title="Coordenada X (m)",
        yaxis_title="Coordenada Y (m)",
        hovermode="closest",
        width=1000,
        height=800,
        template="plotly_white",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )

    return fig


def plot_distance_distribution(distance_matrix: np.ndarray) -> go.Figure:
    """Genera histograma de distribución de distancias.

    Args:
        distance_matrix: Matriz de distancias.

    Returns:
        plotly.graph_objects.Figure con histograma.
    """
    # Extraer distancias no nulas (triángulo superior)
    distancias = distance_matrix[np.triu_indices_from(distance_matrix, k=1)]

    fig = go.Figure(
        data=go.Histogram(
            x=distancias,
            nbinsx=30,
            name="Distancias",
            marker=dict(color="rgba(0, 100, 200, 0.7)"),
            hovertemplate="Rango: %{x}<br>Cantidad: %{y}<extra></extra>",
        )
    )

    fig.update_layout(
        title="Distribución de Distancias Entre Pilotes",
        xaxis_title="Distancia (m)",
        yaxis_title="Frecuencia",
        width=900,
        height=500,
        template="plotly_white",
    )

    return fig
