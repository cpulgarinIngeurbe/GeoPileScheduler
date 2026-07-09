"""Calculador de rendimiento y tiempos de equipos.

Responsabilidad: Calcular métricas de rendimiento, tiempos y distancias.
"""

from datetime import timedelta
from typing import List, Tuple

import numpy as np

from src.resources.equipo_state import EstadoEquipo


def calcular_tiempo_ejecucion(rendimiento_pilotes_dia: int) -> timedelta:
    """Calcula tiempo para ejecutar 1 pilote.

    Formula: tiempo = 8 horas / rendimiento_pilotes_dia

    Args:
        rendimiento_pilotes_dia: Pilotes ejecutables por jornada (8h).

    Returns:
        timedelta del tiempo por pilote.

    Raises:
        ValueError: Si rendimiento <= 0.
    """
    if rendimiento_pilotes_dia <= 0:
        raise ValueError("Rendimiento debe ser > 0")

    horas_por_pilote = 8.0 / rendimiento_pilotes_dia
    return timedelta(hours=horas_por_pilote)


def calcular_tiempo_cambio_unidad(distancia_km: float, velocidad_kmh: float = 5.0) -> timedelta:
    """Estima tiempo para cambiar de unidad estructural.

    Usa velocidad típica de desplazamiento de equipo = 5 km/h.

    Args:
        distancia_km: Distancia entre unidades en km.
        velocidad_kmh: Velocidad de desplazamiento (default 5 km/h).

    Returns:
        timedelta del tiempo de cambio.
    """
    if velocidad_kmh <= 0:
        raise ValueError("Velocidad debe ser > 0")

    horas = distancia_km / velocidad_kmh
    return timedelta(hours=horas)


def distancia_entre_unidades_aproximada(
    unidad1_pilotes: List[Tuple[float, float]],
    unidad2_pilotes: List[Tuple[float, float]],
) -> float:
    """Calcula distancia aproximada entre dos unidades.

    Usa el centroide de pilotes para estimar distancia.

    Args:
        unidad1_pilotes: Lista de (X, Y) de pilotes de unidad 1.
        unidad2_pilotes: Lista de (X, Y) de pilotes de unidad 2.

    Returns:
        Distancia aproximada en metros.
    """
    if not unidad1_pilotes or not unidad2_pilotes:
        return 0.0

    # Centroide de unidad 1
    centroide1 = (
        np.mean([p[0] for p in unidad1_pilotes]),
        np.mean([p[1] for p in unidad1_pilotes]),
    )

    # Centroide de unidad 2
    centroide2 = (
        np.mean([p[0] for p in unidad2_pilotes]),
        np.mean([p[1] for p in unidad2_pilotes]),
    )

    # Distancia euclidiana
    distancia_m = np.sqrt((centroide1[0] - centroide2[0]) ** 2 + (centroide1[1] - centroide2[1]) ** 2)
    distancia_km = distancia_m / 1000.0

    return distancia_km


def utilization_rate(estado_equipo: EstadoEquipo, horas_laborales: float = 8.0) -> float:
    """Calcula porcentaje de utilización del equipo.

    Args:
        estado_equipo: Estado actual del equipo.
        horas_laborales: Horas de la jornada (default 8).

    Returns:
        Porcentaje de utilización (0-100).
    """
    return estado_equipo.utilization_rate(horas_laborales)


def eficiencia_desplazamiento(estado_equipo: EstadoEquipo, distancia_trabajada: float) -> float:
    """Calcula eficiencia de desplazamiento (distancia productiva vs total).

    Args:
        estado_equipo: Estado actual del equipo.
        distancia_trabajada: Distancia entre pilotes trabajados.

    Returns:
        Eficiencia (0-1) donde 1 = perfecta.
    """
    if estado_equipo.distancia_recorrida_hoy <= 0:
        return 0.0

    return min(1.0, distancia_trabajada / estado_equipo.distancia_recorrida_hoy)
