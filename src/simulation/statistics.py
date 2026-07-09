"""Calculadores de estadísticas y métricas de simulación."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.core.models import Proyecto

from .engine import MotorSimulacion
from .event_model import EventoSimulacion, TipoEvento


@dataclass
class EstadisticasSimulacion:
    """Estadísticas completas de una simulación."""

    tiempo_total_horas: float
    pilotes_ejecutados: int
    equipos_utilizados: int
    makespan: float
    utilization_promedio: float = 0.0
    eficiencia_espacial: float = 0.0
    distancia_total_km: float = 0.0
    eventos_totales: int = 0
    metricas_adicionales: dict = field(default_factory=dict)

    def resumen(self) -> str:
        """Generar resumen string de estadísticas."""
        return (
            f"Tiempo Total: {self.tiempo_total_horas:.1f}h | "
            f"Pilotes: {self.pilotes_ejecutados} | "
            f"Equipos: {self.equipos_utilizados} | "
            f"Makespan: {self.makespan:.1f}h | "
            f"Utilización: {self.utilization_promedio:.1f}%"
        )


def calcular_tiempo_total(motor_sim: MotorSimulacion) -> float:
    """Calcular duración total de simulación en horas.

    Args:
        motor_sim: MotorSimulacion con historial

    Returns:
        Duración en horas
    """
    timeline = motor_sim.get_timeline()
    return timeline.get("duracion_horas", 0.0)


def calcular_utilization_equipos(motor_sim: MotorSimulacion) -> dict[str, float]:
    """Calcular utilización de cada equipo.

    Args:
        motor_sim: MotorSimulacion con historial

    Returns:
        Dict {equipo_id: porcentaje_utilizacion}
    """
    utilization = {}
    eventos_inicio = [
        e
        for e in motor_sim.historial_eventos
        if e.tipo == TipoEvento.ASIGNACION_PILOTE
    ]
    eventos_fin = [
        e for e in motor_sim.historial_eventos if e.tipo == TipoEvento.FIN_EJECUCION
    ]

    # Agrupar por equipo
    equipos = set(e.datos.get("equipo_id") for e in eventos_fin)
    for equipo_id in equipos:
        eventos_eq = [e for e in eventos_fin if e.datos.get("equipo_id") == equipo_id]
        if eventos_eq:
            utilization[equipo_id] = len(eventos_eq)

    return utilization


def calcular_makespan(motor_sim: MotorSimulacion) -> float:
    """Calcular makespan (tiempo total del proyecto).

    Args:
        motor_sim: MotorSimulacion con historial

    Returns:
        Makespan en horas
    """
    if not motor_sim.historial_eventos:
        return 0.0

    timeline = motor_sim.get_timeline()
    return timeline.get("duracion_horas", 0.0)


def calcular_eficiencia_espacial(
    proyecto: Proyecto,
    motor_sim: MotorSimulacion,
) -> float:
    """Calcular eficiencia espacial (distancia productiva / distancia total).

    Args:
        proyecto: Proyecto
        motor_sim: MotorSimulacion con historial

    Returns:
        Porcentaje de eficiencia espacial (0-100)
    """
    eventos_ejecucion = [
        e
        for e in motor_sim.historial_eventos
        if e.tipo == TipoEvento.FIN_EJECUCION
    ]

    if not eventos_ejecucion:
        return 0.0

    # Calcular distancia entre pilotes ejecutados en secuencia
    distancia_productiva = 0.0
    pilotes_ejecutados = []

    for evento in eventos_ejecucion:
        pilote_id = evento.datos.get("pilote_id")
        if pilote_id and pilote_id in proyecto.pilotes:
            pilotes_ejecutados.append(pilote_id)

    # Distancia entre secuencia de pilotes
    for i in range(1, len(pilotes_ejecutados)):
        p1 = proyecto.pilotes[pilotes_ejecutados[i - 1]]
        p2 = proyecto.pilotes[pilotes_ejecutados[i]]
        distancia_productiva += p1.distancia_a(p2)

    if distancia_productiva == 0:
        return 100.0

    distancia_total = distancia_productiva  # Simplificación

    if distancia_total == 0:
        return 100.0

    return (distancia_productiva / distancia_total) * 100


def calcular_utilization_promedio(motor_sim: MotorSimulacion, proyecto: Proyecto) -> float:
    """Calcular utilización promedio de todos los equipos.

    Args:
        motor_sim: MotorSimulacion con historial
        proyecto: Proyecto

    Returns:
        Porcentaje promedio de utilización
    """
    utilization = calcular_utilization_equipos(motor_sim)

    if not utilization:
        return 0.0

    tiempo_total = calcular_tiempo_total(motor_sim)
    if tiempo_total == 0:
        return 0.0

    # Horas de trabajo por equipo
    horas_trabajo = sum(utilization.values()) * 4  # Asumiendo 4h por pilote

    # Utilización = (horas trabajo / (equipos * 8h)) * 100
    tiempo_disponible = len(utilization) * 8  # 8 horas por día

    if tiempo_disponible == 0:
        return 0.0

    return (horas_trabajo / tiempo_disponible) * 100


def calcular_secuencia_ejecucion(motor_sim: MotorSimulacion) -> list[str]:
    """Obtener secuencia de pilotes ejecutados.

    Args:
        motor_sim: MotorSimulacion con historial

    Returns:
        Lista de IDs de pilotes en orden de ejecución
    """
    eventos_ejecucion = [
        e
        for e in motor_sim.historial_eventos
        if e.tipo == TipoEvento.FIN_EJECUCION
    ]

    secuencia = []
    for evento in eventos_ejecucion:
        pilote_id = evento.datos.get("pilote_id")
        if pilote_id:
            secuencia.append(pilote_id)

    return secuencia


def generar_estadisticas_completas(
    proyecto: Proyecto,
    motor_sim: MotorSimulacion,
) -> EstadisticasSimulacion:
    """Generar estadísticas completas de simulación.

    Args:
        proyecto: Proyecto
        motor_sim: MotorSimulacion con historial

    Returns:
        EstadisticasSimulacion con todas las métricas
    """
    tiempo_total = calcular_tiempo_total(motor_sim)
    makespan = calcular_makespan(motor_sim)
    utilization = calcular_utilization_equipos(motor_sim)
    utilization_promedio = calcular_utilization_promedio(motor_sim, proyecto)
    eficiencia_espacial = calcular_eficiencia_espacial(proyecto, motor_sim)
    secuencia = calcular_secuencia_ejecucion(motor_sim)

    metricas_adicionales = {
        "secuencia_pilotes": secuencia,
        "utilization_por_equipo": utilization,
    }

    return EstadisticasSimulacion(
        tiempo_total_horas=tiempo_total,
        pilotes_ejecutados=len(secuencia),
        equipos_utilizados=len(utilization),
        makespan=makespan,
        utilization_promedio=utilization_promedio,
        eficiencia_espacial=eficiencia_espacial,
        eventos_totales=len(motor_sim.historial_eventos),
        metricas_adicionales=metricas_adicionales,
    )
