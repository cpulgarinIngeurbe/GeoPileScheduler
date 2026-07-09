"""Modelo de eventos para simulación."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TipoEvento(Enum):
    """Tipos de eventos en simulación."""

    INICIO_SIMULACION = "INICIO_SIMULACION"
    FIN_SIMULACION = "FIN_SIMULACION"
    ASIGNACION_PILOTE = "ASIGNACION_PILOTE"
    INICIO_EJECUCION = "INICIO_EJECUCION"
    FIN_EJECUCION = "FIN_EJECUCION"
    BLOQUEO_PILOTE = "BLOQUEO_PILOTE"
    DESBLOQUEO_PILOTE = "DESBLOQUEO_PILOTE"
    CAMBIO_UNIDAD = "CAMBIO_UNIDAD"
    RESET_DIARIO = "RESET_DIARIO"
    REPORTE_PROGRESO = "REPORTE_PROGRESO"
    ERROR_RESTRICCION = "ERROR_RESTRICCION"


class NivelEvento(Enum):
    """Nivel de severidad de evento."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICO = "CRITICO"


@dataclass
class EventoSimulacion:
    """Evento de simulación."""

    tipo: TipoEvento
    timestamp: datetime
    entidad_id: str
    datos: dict[str, Any] = field(default_factory=dict)
    nivel: NivelEvento = NivelEvento.INFO

    def __post_init__(self) -> None:
        """Validar evento."""
        if not isinstance(self.tipo, TipoEvento):
            raise TypeError("tipo debe ser TipoEvento")
        if not isinstance(self.timestamp, datetime):
            raise TypeError("timestamp debe ser datetime")
        if not isinstance(self.entidad_id, str):
            raise TypeError("entidad_id debe ser str")
        if not isinstance(self.nivel, NivelEvento):
            raise TypeError("nivel debe ser NivelEvento")

    def __lt__(self, other: "EventoSimulacion") -> bool:
        """Comparación para ordenamiento por timestamp."""
        if not isinstance(other, EventoSimulacion):
            return NotImplemented
        return self.timestamp < other.timestamp

    def __le__(self, other: "EventoSimulacion") -> bool:
        """Comparación <=."""
        if not isinstance(other, EventoSimulacion):
            return NotImplemented
        return self.timestamp <= other.timestamp

    def __repr__(self) -> str:
        """Representación string."""
        return (
            f"EventoSimulacion("
            f"tipo={self.tipo.value}, "
            f"timestamp={self.timestamp}, "
            f"entidad_id={self.entidad_id}, "
            f"nivel={self.nivel.value}"
            f")"
        )
