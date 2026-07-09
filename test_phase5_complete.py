#!/usr/bin/env python3
"""Script de validación completa para FASE 5 - Motor de Simulación."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.io.loader import load_project
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones
from src.resources import MotorRecursos
from src.simulation import MotorSimulacion
from src.simulation.validator import validar_simulacion
from src.simulation.statistics import generar_estadisticas_completas
from src.simulation.visualizations import (
    plot_progression,
    plot_equipment_utilization,
    plot_event_histogram,
    generar_dashboard_simulacion,
)


def main():
    print("\n" + "=" * 70)
    print("VALIDACIÓN COMPLETA DE FASE 5 - MOTOR DE SIMULACIÓN")
    print("=" * 70)

    test_file = "data/input/caso_prueba_3.xlsx"

    # Paso 1: Cargar proyecto
    print("\n[1/6] Cargando proyecto...")
    try:
        proyecto = load_project(test_file)
        print(f"✅ Cargado: {proyecto.nombre}")
        print(f"   • Unidades: {len(proyecto.unidades_estructurales)}")
        print(f"   • Pilotes: {len(proyecto.pilotes)}")
        print(f"   • Equipos: {len(proyecto.equipos)}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 2: Motor geométrico
    print("\n[2/6] Calculando geometría...")
    try:
        motor_geo = MotorGeometrico(proyecto)
        motor_geo.calcular()
        print(f"✅ Geometría calculada")
        print(f"   • Distancia matriz: {motor_geo.distancia_matrix.shape}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 3: Motor de restricciones
    print("\n[3/6] Inicializando motor de restricciones...")
    try:
        motor_rest = MotorRestricciones(proyecto, motor_geo)
        motor_rest.inicializar()
        print(f"✅ Motor de restricciones inicializado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 4: Motor de recursos
    print("\n[4/6] Inicializando motor de recursos...")
    try:
        motor_rec = MotorRecursos(proyecto, motor_geo)
        motor_rec.inicializar()
        print(f"✅ Motor de recursos inicializado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 5: Motor de simulación
    print("\n[5/6] Ejecutando simulación...")
    try:
        motor_sim = MotorSimulacion(proyecto, motor_geo, motor_rest, motor_rec)
        if not motor_sim.inicializar():
            print("❌ No se pudo inicializar motor de simulación")
            return False

        if not motor_sim.ejecutar():
            print("❌ Error durante simulación")
            return False

        print(f"✅ Simulación completada")
        print(f"   • Pasos procesados: {motor_sim.total_pasos}")
        print(f"   • Eventos en historial: {len(motor_sim.historial_eventos)}")

        # Mostrar progreso
        progreso = motor_sim.get_progreso()
        print(f"   • Progreso: {progreso['progreso_porcentaje']:.1f}%")
        print(f"   • Pilotes ejecutados: {progreso['pilotes_ejecutados']}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 6: Validación y reportes
    print("\n[6/6] Validando y generando reportes...")
    try:
        # Validar
        reporte = validar_simulacion(proyecto, motor_sim)
        reporte.imprimir()

        if not reporte.es_valida:
            print("⚠️  Simulación tiene errores")
            return False

        # Estadísticas
        stats = generar_estadisticas_completas(proyecto, motor_sim)
        print(f"\n📊 Estadísticas:")
        print(f"   • {stats.resumen()}")

        # Visualizaciones
        print(f"\n📈 Generando visualizaciones...")
        plot_progression(motor_sim)
        print(f"   ✅ Progreso: output/progression.html")

        plot_equipment_utilization(motor_sim)
        print(f"   ✅ Utilización: output/utilization.html")

        plot_event_histogram(motor_sim)
        print(f"   ✅ Histograma: output/event_histogram.html")

        generar_dashboard_simulacion(proyecto, motor_sim)
        print(f"   ✅ Dashboard: output/dashboard_simulacion.html")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Resumen final
    print("\n" + "=" * 70)
    print("✅ FASE 5 COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\nCaracterísticas validadas:")
    print("  • Event model con tipos y severidad")
    print("  • Event queue ordenada por timestamp")
    print("  • Motor de simulación coordinador")
    print("  • Validador de restricciones")
    print("  • Estadísticas y métricas")
    print("  • Visualizaciones Plotly")
    print("\nPróximo paso: FASE 6 (Motor de Optimización)\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
