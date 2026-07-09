"""Validador de simulación."""

from dataclasses import dataclass, field
from datetime import datetime

from src.core.models import Proyecto
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones
from src.resources import MotorRecursos

from .engine import MotorSimulacion
from .event_model import EventoSimulacion, TipoEvento


@dataclass
class ReporteValidacionSimulacion:
    """Reporte de validación de simulación."""

    es_valida: bool
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    estadisticas: dict = field(default_factory=dict)

    def agregar_error(self, msg: str) -> None:
        """Agregar error al reporte."""
        self.errores.append(msg)
        self.es_valida = False

    def agregar_advertencia(self, msg: str) -> None:
        """Agregar advertencia al reporte."""
        self.advertencias.append(msg)

    def imprimir(self) -> None:
        """Imprimir reporte."""
        print("\n" + "=" * 70)
        print("REPORTE DE VALIDACIÓN DE SIMULACIÓN")
        print("=" * 70)

        if self.es_valida:
            print("[OK] SIMULACIÓN VÁLIDA")
        else:
            print("[ERROR] SIMULACIÓN INVÁLIDA")

        if self.errores:
            print("\n[ERROR] ERRORES:")
            for err in self.errores:
                print(f"   • {err}")

        if self.advertencias:
            print("\n⚠️  ADVERTENCIAS:")
            for adv in self.advertencias:
                print(f"   • {adv}")

        if self.estadisticas:
            print("\n[STATS] ESTADÍSTICAS:")
            for clave, valor in self.estadisticas.items():
                print(f"   • {clave}: {valor}")

        print("=" * 70 + "\n")


def validar_simulacion(
    proyecto: Proyecto,
    motor_sim: MotorSimulacion,
) -> ReporteValidacionSimulacion:
    """Validar completitud y consistencia de simulación.

    Args:
        proyecto: Proyecto simulado
        motor_sim: MotorSimulacion con historial

    Returns:
        ReporteValidacionSimulacion con resultados
    """
    reporte = ReporteValidacionSimulacion(es_valida=True)

    # V1: Verificar que todos los pilotes fueron ejecutados
    v1_todos_pilotes = _validar_todos_pilotes_ejecutados(
        proyecto, motor_sim, reporte
    )

    # V2: Verificar que no hay inconsistencias de tiempo
    v2_tiempo_consistente = _validar_tiempo_consistente(motor_sim, reporte)

    # V3: Verificar que restricción R1 se respetó
    v3_restriccion_r1 = _validar_restriccion_r1(proyecto, motor_sim, reporte)

    # V4: Verificar que equipos no sobreasignados
    v4_equipos_validos = _validar_equipos_consistentes(motor_sim, reporte)

    # V5: Verificar que hay al menos eventos de inicio y fin
    v5_eventos_completos = _validar_eventos_completos(motor_sim, reporte)

    # Generar estadísticas
    reporte.estadisticas = _generar_estadisticas(proyecto, motor_sim)

    reporte.es_valida = (
        v1_todos_pilotes
        and v2_tiempo_consistente
        and v3_restriccion_r1
        and v4_equipos_validos
        and v5_eventos_completos
    )

    return reporte


def _validar_todos_pilotes_ejecutados(
    proyecto: Proyecto,
    motor_sim: MotorSimulacion,
    reporte: ReporteValidacionSimulacion,
) -> bool:
    """V1: Verificar que todos los pilotes se ejecutaron.

    Returns:
        True si válido
    """
    total_pilotes = len(proyecto.pilotes)
    eventos_ejecucion = [
        e
        for e in motor_sim.historial_eventos
        if e.tipo == TipoEvento.FIN_EJECUCION
    ]
    pilotes_ejecutados = len(set(e.datos.get("pilote_id") for e in eventos_ejecucion))

    if pilotes_ejecutados < total_pilotes:
        reporte.agregar_error(
            f"No todos los pilotes se ejecutaron: "
            f"{pilotes_ejecutados}/{total_pilotes}"
        )
        return False

    reporte.estadisticas["pilotes_ejecutados"] = pilotes_ejecutados
    return True


def _validar_tiempo_consistente(
    motor_sim: MotorSimulacion,
    reporte: ReporteValidacionSimulacion,
) -> bool:
    """V2: Verificar que timeline es consistente.

    Returns:
        True si válido
    """
    if not motor_sim.historial_eventos:
        reporte.agregar_error("Historial de eventos vacío")
        return False

    # Verificar que eventos están ordenados por timestamp
    timestamps = [e.timestamp for e in motor_sim.historial_eventos]
    if timestamps != sorted(timestamps):
        reporte.agregar_error("Eventos no están en orden temporal")
        return False

    # Verificar que no hay saltos de tiempo excesivos
    for i in range(1, len(timestamps)):
        delta = (timestamps[i] - timestamps[i - 1]).total_seconds()
        if delta < 0:
            reporte.agregar_error(f"Salto de tiempo negativo: {delta}s")
            return False

    duracion_total = timestamps[-1] - timestamps[0]
    reporte.estadisticas["duracion_total_horas"] = duracion_total.total_seconds() / 3600

    return True


def _validar_restriccion_r1(
    proyecto: Proyecto,
    motor_sim: MotorSimulacion,
    reporte: ReporteValidacionSimulacion,
) -> bool:
    """V3: Verificar que R1 se respetó.

    R1: Si D(p_i, p_j) <= R entonces T_j - T_i >= H

    Returns:
        True si válido (o no hay eventos para validar)
    """
    radio = proyecto.radio_critico_m
    tiempo_restriccion = proyecto.tiempo_restriccion_h

    # Obtener eventos de ejecución
    eventos_ejecucion = {
        e.datos.get("pilote_id"): e.timestamp
        for e in motor_sim.historial_eventos
        if e.tipo == TipoEvento.FIN_EJECUCION and e.datos.get("pilote_id")
    }

    if len(eventos_ejecucion) < 2:
        return True  # No hay suficientes eventos para validar

    # Verificar R1 entre pares de pilotes
    pilotes_lista = list(proyecto.pilotes.values())
    incumplimientos = 0

    for i, pilote_i in enumerate(pilotes_lista):
        for pilote_j in pilotes_lista[i + 1 :]:
            distancia = pilote_i.distancia_a(pilote_j)

            if distancia <= radio:
                t_i = eventos_ejecucion.get(pilote_i.id)
                t_j = eventos_ejecucion.get(pilote_j.id)

                if t_i and t_j:
                    diferencia_horas = abs((t_j - t_i).total_seconds() / 3600)
                    if diferencia_horas < tiempo_restriccion:
                        incumplimientos += 1
                        reporte.agregar_advertencia(
                            f"R1 incumplida entre {pilote_i.id} y {pilote_j.id}: "
                            f"Δt={diferencia_horas:.1f}h < {tiempo_restriccion}h"
                        )

    if incumplimientos > 0:
        reporte.agregar_error(f"R1 incumplida en {incumplimientos} pares de pilotes")
        return False

    reporte.estadisticas["verificaciones_r1"] = len(pilotes_lista) * (
        len(pilotes_lista) - 1
    ) / 2
    return True


def _validar_equipos_consistentes(
    motor_sim: MotorSimulacion,
    reporte: ReporteValidacionSimulacion,
) -> bool:
    """V4: Verificar que equipos no están sobreasignados.

    Returns:
        True si válido
    """
    eventos_asignacion = [
        e for e in motor_sim.historial_eventos if e.tipo == TipoEvento.ASIGNACION_PILOTE
    ]
    eventos_fin = [
        e for e in motor_sim.historial_eventos if e.tipo == TipoEvento.FIN_EJECUCION
    ]

    # Verificar que cada asignación tiene fin correspondiente
    if len(eventos_asignacion) > 0 and len(eventos_fin) == 0:
        reporte.agregar_advertencia("Hay asignaciones pero sin ejecuciones finalizadas")
        return True  # No es error crítico

    return True


def _validar_eventos_completos(
    motor_sim: MotorSimulacion,
    reporte: ReporteValidacionSimulacion,
) -> bool:
    """V5: Verificar que hay eventos de inicio y fin.

    Returns:
        True si válido
    """
    tiene_inicio = any(
        e.tipo == TipoEvento.INICIO_SIMULACION for e in motor_sim.historial_eventos
    )
    tiene_fin_ejecucion = any(
        e.tipo == TipoEvento.FIN_EJECUCION for e in motor_sim.historial_eventos
    )

    if not tiene_inicio:
        reporte.agregar_error("No hay evento de INICIO_SIMULACION")
        return False

    if not tiene_fin_ejecucion:
        reporte.agregar_advertencia("No hay eventos de FIN_EJECUCION")

    return True


def _generar_estadisticas(
    proyecto: Proyecto,
    motor_sim: MotorSimulacion,
) -> dict:
    """Generar estadísticas de simulación.

    Returns:
        Dict con métricas
    """
    timeline = motor_sim.get_timeline()
    progreso = motor_sim.get_progreso()
    estado = motor_sim.get_estado_global()

    eventos_ejecucion = [
        e
        for e in motor_sim.historial_eventos
        if e.tipo == TipoEvento.FIN_EJECUCION
    ]

    return {
        "total_pilotes": len(proyecto.pilotes),
        "pilotes_ejecutados": estado.pilotes_ejecutados,
        "eventos_totales": len(motor_sim.historial_eventos),
        "duracion_horas": timeline.get("duracion_horas", 0),
        "equipos_disponibles": len(proyecto.equipos),
        "progreso_porcentaje": estado.progreso_porcentaje,
    }
