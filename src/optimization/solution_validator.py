"""Validador de soluciones de optimización."""

from dataclasses import dataclass, field

from src.core.models import Proyecto

from .base_optimizer import Solucion


@dataclass
class ReporteValidacionSolucion:
    """Reporte de validación de solución."""

    es_valida: bool
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    estadisticas: dict = field(default_factory=dict)

    def agregar_error(self, msg: str) -> None:
        """Agregar error."""
        self.errores.append(msg)
        self.es_valida = False

    def agregar_advertencia(self, msg: str) -> None:
        """Agregar advertencia."""
        self.advertencias.append(msg)

    def imprimir(self) -> None:
        """Imprimir reporte."""
        print("\n" + "=" * 70)
        print("REPORTE DE VALIDACIÓN DE SOLUCIÓN")
        print("=" * 70)

        if self.es_valida:
            print("✅ SOLUCIÓN VÁLIDA")
        else:
            print("❌ SOLUCIÓN INVÁLIDA")

        if self.errores:
            print("\n❌ ERRORES:")
            for err in self.errores:
                print(f"   • {err}")

        if self.advertencias:
            print("\n⚠️  ADVERTENCIAS:")
            for adv in self.advertencias:
                print(f"   • {adv}")

        if self.estadisticas:
            print("\n📊 ESTADÍSTICAS:")
            for clave, valor in self.estadisticas.items():
                print(f"   • {clave}: {valor}")

        print("=" * 70 + "\n")


def validar_solucion(
    proyecto: Proyecto,
    solucion: Solucion,
) -> ReporteValidacionSolucion:
    """Validar que una solución es correcta.

    Args:
        proyecto: Proyecto
        solucion: Solucion a validar

    Returns:
        ReporteValidacionSolucion con resultados
    """
    reporte = ReporteValidacionSolucion(es_valida=True)

    # V1: Todos los pilotes asignados
    v1 = _validar_pilotes_asignados(proyecto, solucion, reporte)

    # V2: Sin sobreasignación de equipos
    v2 = _validar_equipos_consistentes(proyecto, solucion, reporte)

    # V3: Timestamps consistentes
    v3 = _validar_timestamps_orden(solucion, reporte)

    # V4: Makespan positivo
    v4 = _validar_makespan_positivo(solucion, reporte)

    # V5: Score en rango 0-100
    v5 = _validar_score_rango(solucion, reporte)

    # Generar estadísticas
    reporte.estadisticas = _generar_estadisticas(proyecto, solucion)

    reporte.es_valida = v1 and v2 and v3 and v4 and v5

    return reporte


def _validar_pilotes_asignados(
    proyecto: Proyecto,
    solucion: Solucion,
    reporte: ReporteValidacionSolucion,
) -> bool:
    """V1: Verificar que todos los pilotes están asignados."""
    pilotes_asignados = set(a.pilote_id for a in solucion.asignaciones)
    pilotes_totales = set(proyecto.pilotes.keys())

    if pilotes_asignados != pilotes_totales:
        pilotes_faltantes = pilotes_totales - pilotes_asignados
        reporte.agregar_error(
            f"Pilotes no asignados: {pilotes_faltantes}"
        )
        return False

    reporte.estadisticas["pilotes_totales"] = len(pilotes_totales)
    reporte.estadisticas["pilotes_asignados"] = len(pilotes_asignados)
    return True


def _validar_equipos_consistentes(
    proyecto: Proyecto,
    solucion: Solucion,
    reporte: ReporteValidacionSolucion,
) -> bool:
    """V2: Verificar que no hay sobreasignación de equipos."""
    for equipo_id, equipo in proyecto.equipos.items():
        asignaciones_equipo = [
            a for a in solucion.asignaciones
            if a.equipo_id == equipo_id
        ]

        # Contar pilotes por día (rendimiento_pilotes_dia)
        # Simplificado: cada asignación es 1 pilote
        if len(asignaciones_equipo) > equipo.rendimiento_pilotes_dia * 100:
            reporte.agregar_advertencia(
                f"Equipo {equipo_id} podría estar sobreasignado: "
                f"{len(asignaciones_equipo)} pilotes"
            )

    reporte.estadisticas["equipos_total"] = len(proyecto.equipos)
    return True


def _validar_timestamps_orden(
    solucion: Solucion,
    reporte: ReporteValidacionSolucion,
) -> bool:
    """V3: Verificar que timestamps están en orden."""
    timestamps = [a.timestamp for a in solucion.asignaciones]

    if timestamps != sorted(timestamps):
        reporte.agregar_error("Timestamps no están en orden temporal")
        return False

    return True


def _validar_makespan_positivo(
    solucion: Solucion,
    reporte: ReporteValidacionSolucion,
) -> bool:
    """V4: Verificar que makespan es positivo."""
    if solucion.makespan < 0:
        reporte.agregar_error("Makespan no puede ser negativo")
        return False

    reporte.estadisticas["makespan_horas"] = f"{solucion.makespan:.1f}"
    return True


def _validar_score_rango(
    solucion: Solucion,
    reporte: ReporteValidacionSolucion,
) -> bool:
    """V5: Verificar que score está entre 0-100."""
    if not (0 <= solucion.score_multiobjetivo <= 100):
        reporte.agregar_error(
            f"Score debe estar entre 0-100, obtuvo {solucion.score_multiobjetivo}"
        )
        return False

    reporte.estadisticas["score"] = f"{solucion.score_multiobjetivo:.1f}"
    return True


def _generar_estadisticas(
    proyecto: Proyecto,
    solucion: Solucion,
) -> dict:
    """Generar estadísticas de la solución."""
    asignaciones_por_equipo = {}
    for asig in solucion.asignaciones:
        if asig.equipo_id not in asignaciones_por_equipo:
            asignaciones_por_equipo[asig.equipo_id] = 0
        asignaciones_por_equipo[asig.equipo_id] += 1

    return {
        "optimizador": solucion.nombre_optimizador,
        "asignaciones_total": len(solucion.asignaciones),
        "asignaciones_por_equipo": asignaciones_por_equipo,
        "tiempo_ejecucion_segundos": f"{solucion.tiempo_ejecucion:.2f}",
    }
