#!/usr/bin/env python3
"""Script de validación para FASE 1 - Base del Proyecto.

Valida que el sistema pueda:
1. Leer archivo Excel CASO 1
2. Validar datos
3. Construir modelo interno
4. Generar resumen estadístico
"""

import sys
from pathlib import Path

# Añadir src/ al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

from src.io.loader import load_project
from src.utils.project_summary import print_project_summary, summarize_project


def main():
    """Ejecuta validación de FASE 1."""
    print("\n" + "=" * 70)
    print("VALIDACIÓN DE FASE 1 - BASE DEL PROYECTO")
    print("=" * 70)

    # Rutas
    test_file = "data/input/caso_prueba_1.xlsx"

    # Paso 1: Verificar que el archivo existe
    print("\n[1/4] Verificando archivo de prueba...")
    if not Path(test_file).exists():
        print(f"❌ Archivo no encontrado: {test_file}")
        print("     Ejecutar primero: python create_test_case_1.py")
        return False

    print(f"✅ Archivo encontrado: {test_file}")

    # Paso 2: Cargar proyecto
    print("\n[2/4] Cargando proyecto desde Excel...")
    try:
        proyecto = load_project(test_file)
        print(f"✅ Proyecto cargado correctamente")
    except Exception as e:
        print(f"❌ Error al cargar proyecto:")
        print(f"     {str(e)}")
        return False

    # Paso 3: Validar contenido
    print("\n[3/4] Validando contenido del proyecto...")
    validaciones = [
        ("Nombre del proyecto", proyecto.nombre, "Caso Prueba 1 - Pilotaje Simple"),
        ("Número de unidades", proyecto.num_unidades, 1),
        ("Número de equipos", proyecto.num_equipos, 1),
        ("Número de pilotes", proyecto.num_pilotes, 5),
        ("Radio crítico", proyecto.radio_critico_m, 10.0),
        ("Tiempo restricción", proyecto.tiempo_restriccion_h, 24.0),
    ]

    all_valid = True
    for desc, actual, esperado in validaciones:
        if actual == esperado:
            print(f"   ✅ {desc}: {actual}")
        else:
            print(f"   ❌ {desc}: esperado {esperado}, recibido {actual}")
            all_valid = False

    if not all_valid:
        return False

    # Paso 4: Generar resumen
    print("\n[4/4] Generando resumen estadístico...")
    try:
        summary = summarize_project(proyecto)
        print(f"✅ Resumen generado correctamente")
        print(f"   - Claves en resumen: {len(summary)} elementos")
    except Exception as e:
        print(f"❌ Error al generar resumen:")
        print(f"     {str(e)}")
        return False

    # Salida detallada
    print()
    print_project_summary(proyecto)

    # Resumen final
    print("=" * 70)
    print("✅ FASE 1 COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\nArtifactos generados:")
    print("   • src/core/models.py - Modelos de datos")
    print("   • src/core/enums.py - Enumeraciones")
    print("   • src/io/loader.py - Cargador Excel")
    print("   • src/io/validator.py - Validador")
    print("   • src/utils/project_summary.py - Resumen")
    print("\nPróximo paso: FASE 2 (Motor Geométrico)")
    print("=" * 70 + "\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
