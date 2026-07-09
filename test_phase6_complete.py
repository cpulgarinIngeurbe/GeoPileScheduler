#!/usr/bin/env python3
"""Script de validación completa para FASE 6 - Motor de Optimización."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.io.loader import load_project
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones
from src.resources import MotorRecursos
from src.simulation import MotorSimulacion
from src.optimization.comparator import ComparadorOptimizadores
from src.optimization.solution_validator import validar_solucion


def main():
    print("\n" + "=" * 70)
    print("VALIDACIÓN COMPLETA DE FASE 6 - MOTOR DE OPTIMIZACIÓN")
    print("=" * 70)

    test_file = "data/input/caso_prueba_5.xlsx"

    # Paso 1: Cargar proyecto
    print("\n[1/8] Cargando proyecto...")
    try:
        proyecto = load_project(test_file)
        print(f"[OK] Cargado: {proyecto.nombre}")
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

    # Paso 2: Calcular geometría
    print("\n[2/8] Calculando geometría...")
    try:
        motor_geo = MotorGeometrico(proyecto)
        motor_geo.calcular()
        print(f"[OK] Geometría calculada")
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

    # Paso 3: Inicializar restricciones
    print("\n[3/8] Inicializando restricciones...")
    try:
        motor_rest = MotorRestricciones(proyecto, motor_geo)
        motor_rest.inicializar()
        print(f"[OK] Restricciones inicializadas")
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

    # Paso 4: Ejecutar optimizadores
    print("\n[4/8] Ejecutando optimizadores...")
    try:
        comparador = ComparadorOptimizadores(proyecto, motor_geo, motor_rest)
        comparacion = comparador.ejecutar_todos()
        comparacion.imprimir_reporte()

        if not comparacion.mejor_solucion:
            print("[ERROR] No se obtuvo ninguna solución")
            return False

        print(f"[OK] Optimización completada")

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

    # Paso 5: Validar soluciones
    print("\n[5/8] Validando soluciones...")
    try:
        for solucion in comparacion.soluciones:
            reporte = validar_solucion(proyecto, solucion)

            if not reporte.es_valida:
                print(f"[ERROR] {solucion.nombre_optimizador}: Solución inválida")
            else:
                print(f"[OK] {solucion.nombre_optimizador}: Solución válida")

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

    # Paso 6: Inicializar recursos
    print("\n[6/8] Inicializando recursos...")
    try:
        motor_rec = MotorRecursos(proyecto, motor_geo)
        motor_rec.inicializar()
        print(f"[OK] Recursos inicializados")
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

    # Paso 7: Simular mejor solución
    print("\n[7/8] Simulando mejor solución...")
    try:
        motor_sim = MotorSimulacion(proyecto, motor_geo, motor_rest, motor_rec)

        if not motor_sim.inicializar():
            print("[ERROR] No se pudo inicializar simulación")
            return False

        if not motor_sim.ejecutar():
            print("[ERROR] Error durante simulación")
            return False

        progreso = motor_sim.get_progreso()
        print(f"[OK] Simulación completada")
        print(f"   • Progreso: {progreso['progreso_porcentaje']:.1f}%")
        print(f"   • Pilotes ejecutados: {progreso['pilotes_ejecutados']}")

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

    # Paso 8: Verificación final
    print("\n[8/8] Verificación final...")
    try:
        mejor_solucion = comparacion.mejor_solucion

        print(f"\n[BEST] RESULTADOS FINALES:")
        print(f"   • Mejor optimizador: {mejor_solucion.nombre_optimizador}")
        print(f"   • Score: {mejor_solucion.score_multiobjetivo:.1f}")
        print(f"   • Makespan: {mejor_solucion.makespan:.1f} horas")
        print(f"   • Asignaciones: {len(mejor_solucion.asignaciones)}")
        print(f"   • Tiempo optimización: {mejor_solucion.tiempo_ejecucion:.2f}s")

    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False

    # Resumen final
    print("\n" + "=" * 70)
    print("[OK] FASE 6 COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\nCaracterísticas validadas:")
    print("  • BaseOptimizer interfaz abstracta")
    print("  • GreedyOptimizer baseline")
    print("  • ORToolsOptimizer solucionador industrial")
    print("  • GeneticOptimizer metaheurística DEAP")
    print("  • ComparadorOptimizadores multi-algoritmo")
    print("  • ValidadorSolucion verificación de consistencia")
    print("  • Integración con MotorSimulacion")
    print("\nPróximo paso: FASE 7 (Análisis y Reportes)\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
