"""Modelo de eventos relacionados con equipos de pilotaje.

Responsabilidad: Formalizar todos los eventos que pueden ocurrir a un equipo.
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional


@dataclass
class EventoEquipo:
    """Evento base para todos los eventos de equipos.

    Atributos:
        equipo_id: ID del equipo que causa el evento.
        tiempo: datetime del evento.
        tipo: Tipo de evento (inicio, fin, cambio_unidad, etc.).
    """

    equipo_id: str
    tiempo: datetime
    tipo: str


@dataclass
class EventoInicioTrabajo(EventoEquipo):
    """Equipo comienza a trabajar en un pilote.

    Atributos:
        pilote_id: ID del pilote siendo trabajado.
        unidad_id: ID de la unidad donde se trabaja.
        tiempo_estimado_finalizacion: Cuándo se espera terminar.
    """

    pilote_id: str
    unidad_id: str
    tiempo_estimado_finalizacion: datetime

    def __post_init__(self):
        self.tipo = "inicio_trabajo"


@dataclass
class EventoFinTrabajo(EventoEquipo):
    """Equipo termina de trabajar en un pilote.

    Atributos:
        pilote_id: ID del pilote completado.
        unidad_id: ID de la unidad.
        tiempo_ejecucion: Cuánto tardó en ejecutarse.
    """

    pilote_id: str
    unidad_id: str
    tiempo_ejecucion: timedelta

    def __post_init__(self):
        self.tipo = "fin_trabajo"


@dataclass
class EventoCambioUnidad(EventoEquipo):
    """Equipo se desplaza a otra unidad estructural.

    Atributos:
        unidad_origen_id: De dónde viene.
        unidad_destino_id: A dónde va.
        distancia_desplazamiento: Km desplazados (aproximado).
        tiempo_desplazamiento: Tiempo del cambio.
    """

    unidad_origen_id: str
    unidad_destino_id: str
    distancia_desplazamiento: float
    tiempo_desplazamiento: timedelta

    def __post_init__(self):
        self.tipo = "cambio_unidad"


@dataclass
class EventoResetDiario(EventoEquipo):
    """Reinicio de contadores diarios del equipo.

    Marca el inicio de una nueva jornada.
    """

    def __post_init__(self):
        self.tipo = "reset_diario"
