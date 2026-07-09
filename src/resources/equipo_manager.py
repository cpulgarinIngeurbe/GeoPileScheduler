"""Gestor de estado de todos los equipos.

Responsabilidad: Centralizar gestión de estados y eventos de equipos.
"""

from datetime import datetime
from typing import Dict, List

from src.core.models import Proyecto
from src.geometry.engine import MotorGeometrico
from src.resources.equipo_state import EstadoEquipo
from src.resources.event_model import (
    EventoEquipo,
    EventoInicioTrabajo,
    EventoFinTrabajo,
    EventoCambioUnidad,
    EventoResetDiario,
)
from src.resources.performance_calculator import (
    calcular_tiempo_ejecucion,
    calcular_tiempo_cambio_unidad,
    distancia_entre_unidades_aproximada,
)


class EquipoManager:
    """Gestor centralizado de estado de todos los equipos."""

    def __init__(self, proyecto: Proyecto, motor_geometrico: MotorGeometrico):
        self.proyecto = proyecto
        self.motor_geometrico = motor_geometrico
        self.estados: Dict[str, EstadoEquipo] = {}
        self.historico_eventos: List[EventoEquipo] = []

    def inicializar(self) -> None:
        """Inicializa estados de todos los equipos."""
        for equipo in self.proyecto.equipos.values():
            # Determinar unidad inicial
            unidad_inicial_id = list(self.proyecto.unidades.keys())[0]
            asignaciones = [a for a in self.proyecto.asignaciones if a.equipo_id == equipo.id]
            if asignaciones:
                unidad_inicial_id = asignaciones[0].unidad_id

            # Obtener posición inicial
            unidad = self.proyecto.unidades[unidad_inicial_id]
            pilote_inicial = list(unidad.pilotes.values())[0] if unidad.pilotes else None
            posicion = (pilote_inicial.x, pilote_inicial.y) if pilote_inicial else (0.0, 0.0)

            # Crear estado
            self.estados[equipo.id] = EstadoEquipo(
                equipo_id=equipo.id,
                nombre=equipo.nombre,
                unidad_actual_id=unidad_inicial_id,
                rendimiento_pilotes_dia=equipo.rendimiento_pilotes_dia,
                posicion_actual=posicion,
            )

    def asignar_pilote(
        self, equipo_id: str, pilote_id: str, tiempo_inicio: datetime
    ) -> EventoInicioTrabajo:
        """Asigna un pilote a un equipo."""
        if equipo_id not in self.estados:
            raise ValueError(f"Equipo '{equipo_id}' no existe")

        estado = self.estados[equipo_id]
        pilote = self.proyecto.obtener_pilote(pilote_id)
        if not pilote:
            raise ValueError(f"Pilote '{pilote_id}' no existe")

        # Actualizar estado
        tiempo_ejecucion = calcular_tiempo_ejecucion(estado.rendimiento_pilotes_dia)
        tiempo_fin_estimado = tiempo_inicio + tiempo_ejecucion

        estado.pilote_actual_id = pilote_id
        estado.posicion_actual = (pilote.x, pilote.y)
        estado.tiempo_ocupacion_inicio = tiempo_inicio
        estado.tiempo_ocupacion_fin_estimado = tiempo_fin_estimado

        # Crear evento
        evento = EventoInicioTrabajo(
            equipo_id=equipo_id,
            tiempo=tiempo_inicio,
            pilote_id=pilote_id,
            unidad_id=pilote.unidad_id,
            tiempo_estimado_finalizacion=tiempo_fin_estimado,
        )
        self.historico_eventos.append(evento)

        return evento

    def finalizar_pilote(self, equipo_id: str, tiempo_finalizacion: datetime) -> EventoFinTrabajo:
        """Marca pilote como terminado por el equipo."""
        if equipo_id not in self.estados:
            raise ValueError(f"Equipo '{equipo_id}' no existe")

        estado = self.estados[equipo_id]
        if not estado.pilote_actual_id:
            raise ValueError(f"Equipo '{equipo_id}' no tiene pilote asignado")

        pilote_id = estado.pilote_actual_id
        pilote = self.proyecto.obtener_pilote(pilote_id)

        # Calcular tiempo trabajado
        tiempo_trabajado = tiempo_finalizacion - estado.tiempo_ocupacion_inicio
        estado.tiempo_trabajo_hoy += tiempo_trabajado
        estado.pilotes_ejecutados_hoy += 1

        # Liberar equipo
        estado.pilote_actual_id = None
        estado.tiempo_ocupacion_inicio = None
        estado.tiempo_ocupacion_fin_estimado = None

        # Crear evento
        evento = EventoFinTrabajo(
            equipo_id=equipo_id,
            tiempo=tiempo_finalizacion,
            pilote_id=pilote_id,
            unidad_id=pilote.unidad_id,
            tiempo_ejecucion=tiempo_trabajado,
        )
        self.historico_eventos.append(evento)

        return evento

    def cambiar_unidad(
        self, equipo_id: str, unidad_destino_id: str, tiempo_inicio: datetime
    ) -> EventoCambioUnidad:
        """Equipo se desplaza a otra unidad."""
        if equipo_id not in self.estados:
            raise ValueError(f"Equipo '{equipo_id}' no existe")
        if unidad_destino_id not in self.proyecto.unidades:
            raise ValueError(f"Unidad '{unidad_destino_id}' no existe")

        estado = self.estados[equipo_id]
        unidad_origen = self.proyecto.unidades[estado.unidad_actual_id]
        unidad_destino = self.proyecto.unidades[unidad_destino_id]

        # Calcular distancia y tiempo
        distancia_km = distancia_entre_unidades_aproximada(
            [(p.x, p.y) for p in unidad_origen.pilotes.values()],
            [(p.x, p.y) for p in unidad_destino.pilotes.values()],
        )
        tiempo_desplazamiento = calcular_tiempo_cambio_unidad(distancia_km)

        # Actualizar estado
        estado.unidad_actual_id = unidad_destino_id
        estado.distancia_recorrida_hoy += distancia_km
        estado.tiempo_espera_hoy += tiempo_desplazamiento

        # Actualizar posición a primer pilote de nueva unidad
        if unidad_destino.pilotes:
            primer_pilote = list(unidad_destino.pilotes.values())[0]
            estado.posicion_actual = (primer_pilote.x, primer_pilote.y)

        # Crear evento
        evento = EventoCambioUnidad(
            equipo_id=equipo_id,
            tiempo=tiempo_inicio,
            unidad_origen_id=estado.unidad_actual_id,
            unidad_destino_id=unidad_destino_id,
            distancia_desplazamiento=distancia_km,
            tiempo_desplazamiento=tiempo_desplazamiento,
        )
        self.historico_eventos.append(evento)

        return evento

    def get_estado(self, equipo_id: str) -> EstadoEquipo:
        """Obtiene estado de un equipo."""
        if equipo_id not in self.estados:
            raise ValueError(f"Equipo '{equipo_id}' no existe")
        return self.estados[equipo_id]

    def get_equipos_disponibles(self, unidad_id: str | None = None) -> List[str]:
        """Obtiene IDs de equipos libres."""
        disponibles = [eid for eid, estado in self.estados.items() if estado.esta_libre]

        if unidad_id:
            disponibles = [eid for eid in disponibles if self.estados[eid].unidad_actual_id == unidad_id]

        return sorted(disponibles)

    def get_equipos_en_unidad(self, unidad_id: str) -> List[str]:
        """Obtiene todos los equipos en una unidad."""
        return sorted([eid for eid, estado in self.estados.items() if estado.unidad_actual_id == unidad_id])

    def get_estadisticas_equipos(self) -> dict:
        """Obtiene estadísticas globales de todos los equipos."""
        total_pilotes = sum(e.pilotes_ejecutados_hoy for e in self.estados.values())
        distancia_total = sum(e.distancia_recorrida_hoy for e in self.estados.values())

        return {
            "num_equipos": len(self.estados),
            "equipos_libres": len(self.get_equipos_disponibles()),
            "equipos_ocupados": len([e for e in self.estados.values() if e.esta_ocupado]),
            "total_pilotes_ejecutados": total_pilotes,
            "distancia_total_recorrida": distancia_total,
            "utilization_promedio": sum(
                e.utilization_rate() for e in self.estados.values()
            ) / len(self.estados) if self.estados else 0,
        }

    def reset_diario(self) -> None:
        """Reinicia contadores para nueva jornada."""
        for estado in self.estados.values():
            estado.reset_diario()

        self.historico_eventos.append(
            EventoResetDiario(equipo_id="SISTEMA", tiempo=datetime.now())
        )
