"""Modelo de eventos de restricción geotécnica.

Responsabilidad: Representar bloqueos temporales causados por restricciones.
"""

from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class BloqueoGeotecnico:
    """Representa un bloqueo temporal por restricción geotécnica (R1).

    Cuando un pilote se ejecuta, todos sus vecinos (dentro del radio crítico)
    se bloquean durante un tiempo mínimo (tiempo_restriccion_h).

    Atributos:
        pilote_id: ID del pilote que está bloqueado.
        pilote_que_bloquea_id: ID del pilote ejecutado que causó el bloqueo.
        tiempo_inicio: datetime cuando comienza el bloqueo (ejecución del causante).
        tiempo_restriccion_h: Duración del bloqueo en horas.

    Propiedades:
        tiempo_fin: datetime cuando se libera el bloqueo.

    Métodos:
        esta_activo(tiempo_actual): ¿El bloqueo sigue vigente?
    """

    pilote_id: str
    pilote_que_bloquea_id: str
    tiempo_inicio: datetime
    tiempo_restriccion_h: float

    @property
    def tiempo_fin(self) -> datetime:
        """Calcula el momento en que expira el bloqueo.

        Returns:
            datetime cuando se libera automáticamente el bloqueo.
        """
        return self.tiempo_inicio + timedelta(hours=self.tiempo_restriccion_h)

    def esta_activo(self, tiempo_actual: datetime) -> bool:
        """Verifica si el bloqueo está activo en un momento dado.

        Args:
            tiempo_actual: datetime del momento a verificar.

        Returns:
            True si tiempo_actual < tiempo_fin, False en caso contrario.
        """
        return tiempo_actual < self.tiempo_fin

    def horas_restantes(self, tiempo_actual: datetime) -> float:
        """Calcula horas restantes hasta la liberación.

        Args:
            tiempo_actual: datetime del momento actual.

        Returns:
            Horas restantes (0 si ya expiró, puede ser negativo si tiempo_actual > tiempo_fin).
        """
        delta = self.tiempo_fin - tiempo_actual
        return delta.total_seconds() / 3600
