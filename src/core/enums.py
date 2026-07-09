"""Enumeraciones para GeoPile Scheduler.

Define todos los tipos enumerados del sistema.
"""

from enum import Enum


class ModoInicio(Enum):
    """Modos de inicio para equipos.

    Atributos:
        AUTO: Sistema optimiza automáticamente el pilote de inicio.
        MANUAL: Usuario especifica manualmente el pilote de inicio.
    """

    AUTO = "AUTO"
    MANUAL = "MANUAL"


class ModoFin(Enum):
    """Modos de finalización para equipos.

    Atributos:
        AUTO: Sistema optimiza automáticamente el pilote de finalización.
        MANUAL: Usuario especifica manualmente el pilote de finalización.
    """

    AUTO = "AUTO"
    MANUAL = "MANUAL"


class EstadoPilote(Enum):
    """Estados posibles de un pilote durante la simulación.

    Transiciones:
        Pendiente → Disponible → Asignado → Ejecutado → (bloqueador)
        Disponible → Bloqueado → Disponible (temporal)

    Atributos:
        PENDIENTE: Pilote no procesado aún.
        DISPONIBLE: Pilote puede ser asignado (no bloqueado).
        ASIGNADO: Pilote asignado a un equipo, en espera de ejecución.
        EJECUTADO: Pilote completamente ejecutado.
        BLOQUEADO: Pilote bloqueado por restricción geotécnica temporal.
    """

    PENDIENTE = "Pendiente"
    DISPONIBLE = "Disponible"
    ASIGNADO = "Asignado"
    EJECUTADO = "Ejecutado"
    BLOQUEADO = "Bloqueado"
