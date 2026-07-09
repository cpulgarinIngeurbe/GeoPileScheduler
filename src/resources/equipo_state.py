"""Modelo de estado dinámico de un equipo durante la simulación.

Responsabilidad: Representar estado actual de un equipo en cada momento.
"""

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass
class EstadoEquipo:
    """Estado dinámico de un equipo durante la simulación.

    Mantiene información en tiempo real de posición, trabajo actual,
    contadores diarios y métricas de rendimiento.

    Atributos:
        equipo_id: ID único del equipo.
        nombre: Nombre descriptivo.
        unidad_actual_id: ID de la unidad donde se encuentra.
        pilote_actual_id: ID del pilote siendo ejecutado (None si libre).
        posicion_actual: (X, Y) de ubicación actual.
        tiempo_ocupacion_inicio: Cuándo comenzó trabajo actual (None si libre).
        tiempo_ocupacion_fin_estimado: Cuándo terminará (None si libre).
        pilotes_ejecutados_hoy: Contador de pilotes ejecutados hoy.
        distancia_recorrida_hoy: Km desplazados hoy.
        tiempo_trabajo_hoy: Horas de trabajo hoy.
        tiempo_espera_hoy: Horas esperando hoy.
    """

    equipo_id: str
    nombre: str
    unidad_actual_id: str
    rendimiento_pilotes_dia: int
    pilote_actual_id: Optional[str] = None
    posicion_actual: Tuple[float, float] = (0.0, 0.0)
    tiempo_ocupacion_inicio: Optional[datetime] = None
    tiempo_ocupacion_fin_estimado: Optional[datetime] = None
    pilotes_ejecutados_hoy: int = 0
    distancia_recorrida_hoy: float = 0.0
    tiempo_trabajo_hoy: timedelta = field(default_factory=lambda: timedelta(0))
    tiempo_espera_hoy: timedelta = field(default_factory=lambda: timedelta(0))

    @property
    def esta_libre(self) -> bool:
        """¿El equipo está disponible (sin trabajo)? """
        return self.pilote_actual_id is None

    @property
    def esta_ocupado(self) -> bool:
        """¿El equipo está ejecutando un pilote?"""
        return self.pilote_actual_id is not None

    def porcentaje_rendimiento_diario(self) -> float:
        """Progreso del rendimiento diario (0-100%).

        Returns:
            Porcentaje de pilotes ejecutados vs rendimiento esperado.
        """
        if self.rendimiento_pilotes_dia <= 0:
            return 0.0
        return (self.pilotes_ejecutados_hoy / self.rendimiento_pilotes_dia) * 100

    def tiempo_total_hoy(self) -> timedelta:
        """Tiempo total utilizado en la jornada.

        Returns:
            tiempo_trabajo_hoy + tiempo_espera_hoy
        """
        return self.tiempo_trabajo_hoy + self.tiempo_espera_hoy

    def utilization_rate(self, horas_laborales: float = 8.0) -> float:
        """Porcentaje de utilización de la jornada.

        Args:
            horas_laborales: Horas de una jornada (default 8).

        Returns:
            Porcentaje de utilización (0-100).
        """
        tiempo_total_h = self.tiempo_total_hoy().total_seconds() / 3600
        return (tiempo_total_h / horas_laborales) * 100 if horas_laborales > 0 else 0.0

    def horas_trabajo_hoy(self) -> float:
        """Horas de trabajo ejecutado hoy.

        Returns:
            Horas totales.
        """
        return self.tiempo_trabajo_hoy.total_seconds() / 3600

    def horas_espera_hoy(self) -> float:
        """Horas de espera hoy.

        Returns:
            Horas totales.
        """
        return self.tiempo_espera_hoy.total_seconds() / 3600

    def reset_diario(self) -> None:
        """Reinicia contadores para nueva jornada."""
        self.pilotes_ejecutados_hoy = 0
        self.distancia_recorrida_hoy = 0.0
        self.tiempo_trabajo_hoy = timedelta(0)
        self.tiempo_espera_hoy = timedelta(0)
