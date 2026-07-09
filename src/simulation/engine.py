"""Motor de simulación event-driven."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from src.core.models import Proyecto
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones
from src.resources import MotorRecursos

from .event_model import EventoSimulacion, TipoEvento, NivelEvento
from .event_queue import EventQueue


@dataclass
class EstadoGlobal:
    """Estado global de la simulación."""

    tiempo_actual: datetime
    pilotes_pendientes: int
    pilotes_disponibles: int
    pilotes_asignados: int
    pilotes_ejecutados: int
    equipos_libres: int
    equipos_ocupados: int
    progreso_porcentaje: float = 0.0


class MotorSimulacion:
    """Simulador event-driven que coordina los tres motores."""

    def __init__(
        self,
        proyecto: Proyecto,
        motor_geo: MotorGeometrico,
        motor_rest: MotorRestricciones,
        motor_rec: MotorRecursos,
    ) -> None:
        """Inicializar motor de simulación.

        Args:
            proyecto: Proyecto a simular
            motor_geo: MotorGeometrico inicializado
            motor_rest: MotorRestricciones inicializado
            motor_rec: MotorRecursos inicializado
        """
        self.proyecto = proyecto
        self.motor_geo = motor_geo
        self.motor_rest = motor_rest
        self.motor_rec = motor_rec

        self.event_queue = EventQueue()
        self.historial_eventos: list[EventoSimulacion] = []
        self.tiempo_actual = proyecto.fecha_inicio
        self.tiempo_fin: Optional[datetime] = None
        self.simulacion_activa = False
        self.total_pasos = 0

    def inicializar(self) -> bool:
        """Inicializar simulación.

        Returns:
            True si inicialización fue exitosa
        """
        try:
            # Verificar que los motores estén inicializados
            if self.motor_geo.distance_matrix is None:
                raise ValueError("MotorGeometrico no está inicializado")

            # Evento inicial
            evento_inicio = EventoSimulacion(
                tipo=TipoEvento.INICIO_SIMULACION,
                timestamp=self.tiempo_actual,
                entidad_id="SIMULACION",
                datos={"total_pilotes": len(self.proyecto.pilotes)},
            )
            self.event_queue.push(evento_inicio)
            self.historial_eventos.append(evento_inicio)

            self.simulacion_activa = True
            return True
        except Exception as e:
            print(f"[ERROR] Error inicializando simulación: {str(e)}")
            return False

    def ejecutar(self) -> bool:
        """Ejecutar simulación completa.

        Returns:
            True si simulación completó exitosamente
        """
        if not self.simulacion_activa:
            if not self.inicializar():
                return False

        try:
            max_pasos = len(self.proyecto.pilotes) * 100  # Límite de seguridad
            pasos = 0

            while not self.event_queue.empty() and pasos < max_pasos:
                evento, completada = self.ejecutar_paso()
                pasos += 1

                if completada:
                    break

            self.tiempo_fin = self.tiempo_actual
            self.simulacion_activa = False
            return True

        except Exception as e:
            print(f"[ERROR] Error ejecutando simulación: {str(e)}")
            return False

    def ejecutar_paso(self) -> tuple[Optional[EventoSimulacion], bool]:
        """Ejecutar un paso de simulación (procesar próximo evento).

        Returns:
            Tupla (evento procesado, ¿simulación completada?)
        """
        evento = self.event_queue.pop()
        if evento is None:
            return None, True

        self.tiempo_actual = evento.timestamp
        self.historial_eventos.append(evento)
        self.total_pasos += 1

        # Procesar según tipo
        if evento.tipo == TipoEvento.INICIO_SIMULACION:
            self._procesar_inicio()
        elif evento.tipo == TipoEvento.ASIGNACION_PILOTE:
            self._procesar_asignacion(evento)
        elif evento.tipo == TipoEvento.INICIO_EJECUCION:
            self._procesar_inicio_ejecucion(evento)
        elif evento.tipo == TipoEvento.FIN_EJECUCION:
            self._procesar_fin_ejecucion(evento)
        elif evento.tipo == TipoEvento.DESBLOQUEO_PILOTE:
            self._procesar_desbloqueo(evento)
        elif evento.tipo == TipoEvento.RESET_DIARIO:
            self._procesar_reset_diario(evento)

        # Verificar si simulación completada
        completada = self._verificar_fin()
        return evento, completada

    def _procesar_inicio(self) -> None:
        """Procesar evento INICIO_SIMULACION."""
        disponibles = self.motor_rest.get_pilotes_disponibles(self.tiempo_actual)
        if disponibles:
            for pilote_id in disponibles:
                evento = EventoSimulacion(
                    tipo=TipoEvento.ASIGNACION_PILOTE,
                    timestamp=self.tiempo_actual,
                    entidad_id=pilote_id,
                    datos={"pilote_id": pilote_id},
                )
                self.event_queue.push(evento)

    def _procesar_asignacion(self, evento: EventoSimulacion) -> None:
        """Procesar evento ASIGNACION_PILOTE."""
        try:
            pilote_id = evento.datos.get("pilote_id")
            equipos_libres = self.motor_rec.get_equipos_disponibles()

            if equipos_libres and pilote_id:
                equipo_id = equipos_libres[0]
                evento_inicio = self.motor_rec.asignar_trabajo(
                    equipo_id, pilote_id, self.tiempo_actual
                )
                if evento_inicio:
                    duracion_horas = evento_inicio.get("tiempo_ejecucion", 4)
                    evento_fin = EventoSimulacion(
                        tipo=TipoEvento.FIN_EJECUCION,
                        timestamp=self.tiempo_actual + timedelta(hours=duracion_horas),
                        entidad_id=equipo_id,
                        datos={
                            "equipo_id": equipo_id,
                            "pilote_id": pilote_id,
                        },
                    )
                    self.event_queue.push(evento_fin)
        except Exception as e:
            pass  # Ignorar errores en asignación

    def _procesar_inicio_ejecucion(self, evento: EventoSimulacion) -> None:
        """Procesar evento INICIO_EJECUCION."""
        pass  # Registrado por asignar_trabajo

    def _procesar_fin_ejecucion(self, evento: EventoSimulacion) -> None:
        """Procesar evento FIN_EJECUCION."""
        try:
            equipo_id = evento.datos.get("equipo_id")
            pilote_id = evento.datos.get("pilote_id")

            if equipo_id and pilote_id:
                evento_fin_dict = self.motor_rec.finalizar_trabajo(
                    equipo_id, self.tiempo_actual
                )
                self.motor_rest.ejecutar_pilote(pilote_id, self.tiempo_actual)

                # Agregar próximas asignaciones
                disponibles = self.motor_rest.get_pilotes_disponibles(self.tiempo_actual)
                for p_id in disponibles:
                    evento_asig = EventoSimulacion(
                        tipo=TipoEvento.ASIGNACION_PILOTE,
                        timestamp=self.tiempo_actual + timedelta(seconds=1),
                        entidad_id=p_id,
                        datos={"pilote_id": p_id},
                    )
                    self.event_queue.push(evento_asig)
        except Exception as e:
            pass  # Ignorar errores en fin de ejecución

    def _procesar_desbloqueo(self, evento: EventoSimulacion) -> None:
        """Procesar evento DESBLOQUEO_PILOTE."""
        pilote_id = evento.datos.get("pilote_id")
        if pilote_id:
            self.motor_rest.actualizar_tiempo(self.tiempo_actual)

    def _procesar_reset_diario(self, evento: EventoSimulacion) -> None:
        """Procesar evento RESET_DIARIO."""
        self.motor_rec._reset_diario_all()

    def _verificar_fin(self) -> bool:
        """Verificar si simulación debe terminar.

        Returns:
            True si todos los pilotes están ejecutados
        """
        stats = self.motor_rec.get_estadisticas_equipos()
        total_pilotes = len(self.proyecto.pilotes)
        return stats["total_pilotes_ejecutados"] >= total_pilotes

    def get_estado_global(self) -> EstadoGlobal:
        """Obtener estado actual de simulación.

        Returns:
            EstadoGlobal con métricas
        """
        try:
            stats_rest = self.motor_rest.get_estadisticas_restricciones(self.tiempo_actual)
        except:
            stats_rest = {}
        stats_rec = self.motor_rec.get_estadisticas_equipos()

        total_pilotes = len(self.proyecto.pilotes)
        pilotes_ejecutados = stats_rec["total_pilotes_ejecutados"]
        progreso = (pilotes_ejecutados / total_pilotes * 100) if total_pilotes > 0 else 0

        return EstadoGlobal(
            tiempo_actual=self.tiempo_actual,
            pilotes_pendientes=total_pilotes - pilotes_ejecutados,
            pilotes_disponibles=len(
                self.motor_rest.get_pilotes_disponibles(self.tiempo_actual)
            ),
            pilotes_asignados=stats_rest.get("pilotes_asignados", 0),
            pilotes_ejecutados=pilotes_ejecutados,
            equipos_libres=stats_rec["equipos_libres"],
            equipos_ocupados=stats_rec["equipos_ocupados"],
            progreso_porcentaje=progreso,
        )

    def get_progreso(self) -> dict[str, any]:
        """Obtener progreso actual.

        Returns:
            Dict con métricas de progreso
        """
        estado = self.get_estado_global()
        return {
            "tiempo_actual": estado.tiempo_actual,
            "progreso_porcentaje": estado.progreso_porcentaje,
            "pilotes_ejecutados": estado.pilotes_ejecutados,
            "pilotes_pendientes": estado.pilotes_pendientes,
            "equipos_libres": estado.equipos_libres,
            "equipos_ocupados": estado.equipos_ocupados,
            "eventos_procesados": self.total_pasos,
            "eventos_pendientes": self.event_queue.size(),
        }

    def get_eventos_historial(self) -> list[EventoSimulacion]:
        """Obtener historial completo de eventos.

        Returns:
            Lista de eventos en orden temporal
        """
        return self.historial_eventos.copy()

    def get_timeline(self) -> dict[str, any]:
        """Obtener timeline de ejecución.

        Returns:
            Dict con información temporal
        """
        if not self.historial_eventos:
            return {}

        primer_evento = self.historial_eventos[0].timestamp
        ultimo_evento = self.historial_eventos[-1].timestamp
        duracion = ultimo_evento - primer_evento

        return {
            "inicio": primer_evento,
            "fin": ultimo_evento,
            "duracion_total": duracion,
            "duracion_horas": duracion.total_seconds() / 3600,
            "eventos_totales": len(self.historial_eventos),
        }
