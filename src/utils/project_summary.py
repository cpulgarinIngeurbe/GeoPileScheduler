"""Generador de resumen estadístico para GeoPile Scheduler.

Responsabilidad: Generar métricas y resumen del proyecto cargado.
"""

from typing import Dict, List, Any
from collections import defaultdict

from src.core.models import Proyecto


def summarize_project(proyecto: Proyecto) -> Dict[str, Any]:
    """Genera un resumen estadístico del proyecto.

    Args:
        proyecto: Objeto Proyecto a resumir.

    Returns:
        Diccionario con métricas del proyecto.
    """
    summary: Dict[str, Any] = {}

    # Información básica
    summary["nombre"] = proyecto.nombre
    summary["fecha_inicio"] = proyecto.fecha_inicio.strftime("%Y-%m-%d")
    summary["radio_critico_m"] = proyecto.radio_critico_m
    summary["tiempo_restriccion_h"] = proyecto.tiempo_restriccion_h

    # Conteos
    summary["num_unidades"] = proyecto.num_unidades
    summary["num_equipos"] = proyecto.num_equipos
    summary["num_pilotes"] = proyecto.num_pilotes

    # Detalles por unidad
    summary["pilotes_por_unidad"] = {
        unidad_id: unidad.num_pilotes for unidad_id, unidad in proyecto.unidades.items()
    }

    # Equipos por unidad
    equipos_por_unidad: Dict[str, List[str]] = defaultdict(list)
    for asignacion in proyecto.asignaciones:
        equipos_por_unidad[asignacion.unidad_id].append(asignacion.equipo_id)

    summary["equipos_por_unidad"] = dict(equipos_por_unidad)

    # Detalles de equipos
    summary["equipos_detalle"] = {
        equipo_id: {
            "nombre": equipo.nombre,
            "rendimiento_pilotes_dia": equipo.rendimiento_pilotes_dia,
            "modo_inicio": equipo.modo_inicio.value,
            "pilote_inicio": equipo.pilote_inicio,
            "modo_fin": equipo.modo_fin.value,
            "pilote_fin": equipo.pilote_fin,
        }
        for equipo_id, equipo in proyecto.equipos.items()
    }

    # Detalles de unidades
    summary["unidades_detalle"] = {
        unidad_id: {
            "nombre": unidad.nombre,
            "num_pilotes": unidad.num_pilotes,
        }
        for unidad_id, unidad in proyecto.unidades.items()
    }

    # Estadísticas de pilotes
    todas_las_coordenadas = [
        (p.x, p.y) for u in proyecto.unidades.values() for p in u.pilotes.values()
    ]
    if todas_las_coordenadas:
        xs = [x for x, y in todas_las_coordenadas]
        ys = [y for x, y in todas_las_coordenadas]
        summary["pilotes_stats"] = {
            "x_min": min(xs),
            "x_max": max(xs),
            "y_min": min(ys),
            "y_max": max(ys),
        }

    return summary


def print_project_summary(proyecto: Proyecto) -> None:
    """Imprime un resumen formateado del proyecto.

    Args:
        proyecto: Objeto Proyecto a resumir.
    """
    summary = summarize_project(proyecto)

    print("\n" + "=" * 70)
    print(f"RESUMEN DEL PROYECTO: {summary['nombre']}")
    print("=" * 70)

    print(f"\n📅 Fecha de inicio: {summary['fecha_inicio']}")
    print(f"🔴 Radio crítico: {summary['radio_critico_m']} m")
    print(f"⏱️  Tiempo restricción: {summary['tiempo_restriccion_h']} horas")

    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   • Unidades estructurales: {summary['num_unidades']}")
    print(f"   • Equipos: {summary['num_equipos']}")
    print(f"   • Total pilotes: {summary['num_pilotes']}")

    print(f"\n🏢 PILOTES POR UNIDAD:")
    for unidad_id, num_pilotes in summary["pilotes_por_unidad"].items():
        unidad_nombre = summary["unidades_detalle"][unidad_id]["nombre"]
        print(f"   • {unidad_nombre} ({unidad_id}): {num_pilotes} pilotes")

    print(f"\n🏗️  EQUIPOS:")
    for equipo_id, detalle in summary["equipos_detalle"].items():
        print(
            f"   • {detalle['nombre']} ({equipo_id}): {detalle['rendimiento_pilotes_dia']} pilotes/día"
        )
        print(
            f"     - Inicio: {detalle['modo_inicio']} {f'(pilote {detalle[\"pilote_inicio\"]})' if detalle['pilote_inicio'] else ''}"
        )
        print(
            f"     - Fin: {detalle['modo_fin']} {f'(pilote {detalle[\"pilote_fin\"]})' if detalle['pilote_fin'] else ''}"
        )

    print(f"\n🔗 ASIGNACIONES EQUIPO-UNIDAD:")
    for unidad_id, equipos in summary["equipos_por_unidad"].items():
        unidad_nombre = summary["unidades_detalle"][unidad_id]["nombre"]
        equipos_nombres = ", ".join(summary["equipos_detalle"][eid]["nombre"] for eid in equipos)
        print(f"   • {unidad_nombre}: {equipos_nombres}")

    if "pilotes_stats" in summary:
        stats = summary["pilotes_stats"]
        print(f"\n📍 RANGO DE COORDENADAS:")
        print(f"   • X: [{stats['x_min']}, {stats['x_max']}]")
        print(f"   • Y: [{stats['y_min']}, {stats['y_max']}]")

    print("\n" + "=" * 70 + "\n")
