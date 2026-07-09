#!/usr/bin/env python3
"""
DEMOSTRACIÓN COMPLETA DE GeoPile Scheduler

Este script muestra cómo:
1. Cargar un proyecto desde Excel
2. Ejecutar los tres optimizadores
3. Comparar resultados
4. Simular la mejor solución
5. Generar reportes y visualizaciones

ESTRUCTURA:
-----------
data/input/           <- Archivos de entrada (Excel)
  ├─ caso_prueba_3.xlsx
  ├─ caso_prueba_5.xlsx
  └─ caso_prueba_6.xlsx

output/               <- Archivos de salida (HTML, reportes)
  ├─ reporte.txt
  └─ *.html (gráficos)

USO:
----
python demo.py                    # Usar caso_prueba_5.xlsx por defecto
python demo.py caso_prueba_6.xlsx # Usar archivo específico
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Importar módulos
from src.io.loader import load_project
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones
from src.resources import MotorRecursos
from src.simulation import MotorSimulacion
from src.optimization.comparator import ComparadorOptimizadores
from src.optimization.solution_validator import validar_solucion
from src.simulation.statistics import generar_estadisticas_completas
from src.simulation.visualizations import (
    plot_progression,
    plot_equipment_utilization,
    plot_event_histogram,
)


def crear_carpeta_output():
    """Crear carpeta output si no existe."""
    Path("output").mkdir(exist_ok=True)


def main():
    # Obtener archivo de entrada
    if len(sys.argv) > 1:
        archivo_entrada = sys.argv[1]
    else:
        archivo_entrada = "data/input/caso_prueba_5.xlsx"

    print("\n" + "=" * 80)
    print("GEOPILE SCHEDULER - DEMOSTRACIÓN COMPLETA")
    print("=" * 80)
    print(f"\nArchivo de entrada: {archivo_entrada}")
    print(f"Tiempo de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    crear_carpeta_output()

    # ========================================================================
    # PASO 1: CARGAR PROYECTO
    # ========================================================================
    print("\n" + "-" * 80)
    print("[1] CARGAR PROYECTO DESDE EXCEL")
    print("-" * 80)

    try:
        proyecto = load_project(archivo_entrada)
        print(f"[OK] Proyecto cargado: {proyecto.nombre}")
        print(f"     - Pilotes: {len(proyecto.pilotes)}")
        print(f"     - Equipos: {len(proyecto.equipos)}")
        print(f"     - Unidades: {len(proyecto.unidades)}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

    # ========================================================================
    # PASO 2: CALCULAR GEOMETRÍA
    # ========================================================================
    print("\n" + "-" * 80)
    print("[2] CALCULAR GEOMETRÍA ESPACIAL")
    print("-" * 80)

    try:
        motor_geo = MotorGeometrico(proyecto)
        motor_geo.calcular()
        print("[OK] Geometría calculada")
        print(f"     - Matriz distancias: {motor_geo.distance_matrix.shape}")
        print(f"     - Grafo espacial: {motor_geo.spatial_graph.number_of_nodes()} nodos")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

    # ========================================================================
    # PASO 3: INICIALIZAR RESTRICCIONES
    # ========================================================================
    print("\n" + "-" * 80)
    print("[3] INICIALIZAR RESTRICCIONES GEOTÉCNICAS")
    print("-" * 80)

    try:
        motor_rest = MotorRestricciones(proyecto, motor_geo)
        motor_rest.inicializar()
        print("[OK] Restricciones inicializadas")
        print(f"     - Radio crítico: {proyecto.radio_critico_m}m")
        print(f"     - Tiempo restricción: {proyecto.tiempo_restriccion_h}h")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

    # ========================================================================
    # PASO 4: EJECUTAR OPTIMIZADORES
    # ========================================================================
    print("\n" + "-" * 80)
    print("[4] EJECUTAR ALGORITMOS DE OPTIMIZACIÓN")
    print("-" * 80)

    try:
        comparador = ComparadorOptimizadores(proyecto, motor_geo, motor_rest)
        comparacion = comparador.ejecutar_todos()

        print("\n[RESULTADOS DE OPTIMIZACIÓN]")
        print("-" * 80)
        for solucion in sorted(
            comparacion.soluciones,
            key=lambda s: s.score_multiobjetivo,
            reverse=True
        ):
            print(f"\n{solucion.nombre_optimizador}:")
            print(f"  Score:         {solucion.score_multiobjetivo:.1f}/100")
            print(f"  Makespan:      {solucion.makespan:.1f} horas")
            print(f"  Asignaciones:  {len(solucion.asignaciones)} pilotes")
            print(f"  Tiempo ejecución: {solucion.tiempo_ejecucion:.3f} segundos")

        if not comparacion.mejor_solucion:
            print("[ERROR] No se obtuvo solución")
            return False

        print(f"\n[GANADOR] {comparacion.mejor_solucion.nombre_optimizador}")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

    # ========================================================================
    # PASO 5: VALIDAR SOLUCIONES
    # ========================================================================
    print("\n" + "-" * 80)
    print("[5] VALIDAR SOLUCIONES")
    print("-" * 80)

    for solucion in comparacion.soluciones:
        reporte = validar_solucion(proyecto, solucion)
        estado = "VALIDA" if reporte.es_valida else "INVALIDA"
        print(f"{solucion.nombre_optimizador:<30} {estado}")

    # ========================================================================
    # PASO 6: SIMULAR MEJOR SOLUCIÓN
    # ========================================================================
    print("\n" + "-" * 80)
    print("[6] SIMULAR MEJOR SOLUCIÓN")
    print("-" * 80)

    try:
        motor_rec = MotorRecursos(proyecto, motor_geo)
        motor_rec.inicializar()

        motor_sim = MotorSimulacion(proyecto, motor_geo, motor_rest, motor_rec)
        motor_sim.inicializar()
        motor_sim.ejecutar()

        progreso = motor_sim.get_progreso()
        timeline = motor_sim.get_timeline()

        print("[OK] Simulación completada")
        print(f"     - Progreso: {progreso['progreso_porcentaje']:.1f}%")
        print(f"     - Pilotes ejecutados: {progreso['pilotes_ejecutados']}")
        print(f"     - Eventos procesados: {progreso['eventos_procesados']}")
        print(f"     - Duración total: {timeline.get('duracion_horas', 0):.1f}h")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

    # ========================================================================
    # PASO 7: GENERAR ESTADÍSTICAS
    # ========================================================================
    print("\n" + "-" * 80)
    print("[7] ESTADÍSTICAS FINALES")
    print("-" * 80)

    try:
        stats = generar_estadisticas_completas(proyecto, motor_sim)
        print(f"Makespan:           {stats.makespan:.1f}h")
        print(f"Pilotes ejecutados: {stats.pilotes_ejecutados}")
        print(f"Equipos utilizados: {stats.equipos_utilizados}")
        print(f"Utilización prom:   {stats.utilization_promedio:.1f}%")
        print(f"Eficiencia espacial: {stats.eficiencia_espacial:.1f}%")

    except Exception as e:
        print(f"[ERROR] {str(e)}")

    # ========================================================================
    # PASO 8: GENERAR VISUALIZACIONES
    # ========================================================================
    print("\n" + "-" * 80)
    print("[8] GENERAR VISUALIZACIONES")
    print("-" * 80)

    try:
        plot_progression(motor_sim, "output/01_progreso.html")
        print("[OK] output/01_progreso.html")

        plot_equipment_utilization(motor_sim, "output/02_utilizacion.html")
        print("[OK] output/02_utilizacion.html")

        plot_event_histogram(motor_sim, "output/03_eventos.html")
        print("[OK] output/03_eventos.html")

    except Exception as e:
        print(f"[WARNING] Error generando visualizaciones: {str(e)}")

    # ========================================================================
    # PASO 9: GENERAR REPORTE FINAL
    # ========================================================================
    print("\n" + "-" * 80)
    print("[9] GENERAR REPORTE FINAL")
    print("-" * 80)

    try:
        with open("output/reporte_completo.txt", "w") as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE COMPLETO DE GEOPILE SCHEDULER\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Proyecto: {proyecto.nombre}\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Archivo entrada: {archivo_entrada}\n\n")

            f.write("DATOS DEL PROYECTO:\n")
            f.write(f"  Pilotes: {len(proyecto.pilotes)}\n")
            f.write(f"  Equipos: {len(proyecto.equipos)}\n")
            f.write(f"  Unidades: {len(proyecto.unidades)}\n")
            f.write(f"  Radio crítico: {proyecto.radio_critico_m}m\n\n")

            f.write("RESULTADOS DE OPTIMIZACIÓN:\n")
            for solucion in sorted(
                comparacion.soluciones,
                key=lambda s: s.score_multiobjetivo,
                reverse=True
            ):
                f.write(f"\n  {solucion.nombre_optimizador}:\n")
                f.write(f"    Score: {solucion.score_multiobjetivo:.1f}\n")
                f.write(f"    Makespan: {solucion.makespan:.1f}h\n")
                f.write(f"    Tiempo: {solucion.tiempo_ejecucion:.3f}s\n")

            f.write("\n" + "=" * 80 + "\n")

        print("[OK] output/reporte_completo.txt")

    except Exception as e:
        print(f"[WARNING] Error escribiendo reporte: {str(e)}")

    # ========================================================================
    # RESUMEN FINAL
    # ========================================================================
    print("\n" + "=" * 80)
    print("EJECUCIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    print("\nARCHIVOS GENERADOS EN output/:")
    print("  - 01_progreso.html         (Gráfico de progreso)")
    print("  - 02_utilizacion.html      (Utilización de equipos)")
    print("  - 03_eventos.html          (Distribución de eventos)")
    print("  - reporte_completo.txt     (Reporte en texto)")
    print("\nPara ver los gráficos, abre los archivos HTML en tu navegador")
    print("=" * 80 + "\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
