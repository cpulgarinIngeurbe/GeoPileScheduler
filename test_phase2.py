#!/usr/bin/env python3
"""Script de validación para FASE 2 - Motor Geométrico.

Valida que el sistema pueda:
1. Calcular matriz de distancias
2. Construir grafo espacial
3. Identificar vecinos
4. Generar visualizaciones interactivas
"""

import sys
from pathlib import Path

# Añadir src/ al path
sys.path.insert(0, str(Path(__file__).parent))

from src.io.loader import load_project
from src.geometry import MotorGeometrico


def main():
    """Ejecuta validación de FASE 2."""
    print("\n" + "=" * 70)
    print("VALIDACIÓN DE FASE 2 - MOTOR GEOMÉTRICO")
    print("=" * 70)

    test_file = "data/input/caso_prueba_1.xlsx"

    # Paso 1: Cargar proyecto
    print("\n[1/6] Cargando proyecto...")
    try:
        proyecto = load_project(test_file)
        print(f"✅ Proyecto cargado: {proyecto.nombre}")
        print(f"     {proyecto.num_pilotes} pilotes, radio crítico {proyecto.radio_critico_m}m")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 2: Inicializar motor geométrico
    print("\n[2/6] Inicializando Motor Geométrico...")
    try:
        motor = MotorGeometrico(proyecto)
        print(f"✅ Motor inicializado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 3: Ejecutar cálculos
    print("\n[3/6] Calculando geometría...")
    try:
        motor.calcular()
        print(f"✅ Cálculos completados")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 4: Validar resultados
    print("\n[4/6] Validando resultados...")
    validaciones = [
        ("Matriz de distancias", motor.distance_matrix is not None),
        ("Matriz es (5, 5)", motor.distance_matrix.shape == (5, 5)),
        ("Grafo espacial", motor.spatial_graph is not None),
        ("Grafo tiene 5 nodos", motor.spatial_graph.number_of_nodes() == 5),
        ("Diccionario de vecinos", motor.neighbors is not None),
        ("Todos los pilotes en vecinos", len(motor.neighbors) == 5),
    ]

    all_valid = True
    for desc, resultado in validaciones:
        if resultado:
            print(f"   ✅ {desc}")
        else:
            print(f"   ❌ {desc}")
            all_valid = False

    if not all_valid:
        return False

    # Paso 5: Generar estadísticas
    print("\n[5/6] Generando estadísticas...")
    try:
        stats = motor.get_estadisticas_geometria()
        print(f"✅ Estadísticas generadas:")
        print(f"   • Distancia mínima: {stats['distancia_minima']:.2f} m")
        print(f"   • Distancia máxima: {stats['distancia_maxima']:.2f} m")
        print(f"   • Distancia promedio: {stats['distancia_promedio']:.2f} m")
        print(f"   • Aristas en grafo: {stats['num_aristas_grafo']}")
        print(f"   • Densidad del grafo: {stats['densidad_grafo']:.3f}")
        print(f"   • Pilotes sin vecinos: {stats['pilotes_sin_vecinos']}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 6: Generar visualizaciones
    print("\n[6/6] Generando visualizaciones...")
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Heatmap
        motor.export_heatmap_html(str(output_dir / "heatmap_distancias.html"))
        print(f"✅ Heatmap: data/output/heatmap_distancias.html")

        # Geometría
        motor.export_geometry_html(str(output_dir / "geometria_proyecto.html"))
        print(f"✅ Geometría: data/output/geometria_proyecto.html")

        # Distribución
        motor.export_distribution_html(str(output_dir / "distribucion_distancias.html"))
        print(f"✅ Distribución: data/output/distribucion_distancias.html")
    except Exception as e:
        print(f"❌ Error en visualizaciones: {str(e)}")
        return False

    # Ejemplo de uso de métodos
    print("\n[EXTRA] Ejemplos de uso del motor...")
    try:
        # Distancia entre pilotes
        d = motor.get_distancia("P_001", "P_002")
        print(f"✅ Distancia P_001 → P_002: {d:.2f} m")

        # Vecinos
        vecinos_p1 = motor.get_vecinos("P_001")
        print(f"✅ Vecinos de P_001: {vecinos_p1}")

        # Relación geotécnica
        tiene_relacion = motor.hay_relacion_geotecnica("P_001", "P_002")
        print(f"✅ ¿P_001 y P_002 tienen relación geotécnica? {tiene_relacion}")
    except Exception as e:
        print(f"❌ Error en ejemplos: {str(e)}")
        return False

    # Resumen final
    print("\n" + "=" * 70)
    print("✅ FASE 2 COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\nArchivos generados en data/output/:")
    print("  • heatmap_distancias.html")
    print("  • geometria_proyecto.html")
    print("  • distribucion_distancias.html")
    print("\nPróximo paso: FASE 3 (Motor de Restricciones)")
    print("=" * 70 + "\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
