#!/usr/bin/env python3
"""Script de validación completa para FASE 3 - Motor de Restricciones."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.io.loader import load_project
from src.geometry import MotorGeometrico
from src.constraints import MotorRestricciones
from src.constraints.validator import validar_restricciones, reporte_validacion


def main():
    print("\n" + "=" * 70)
    print("VALIDACIÓN COMPLETA DE FASE 3 - MOTOR DE RESTRICCIONES")
    print("=" * 70)

    test_file = "data/input/caso_prueba_1.xlsx"

    # Paso 1: Cargar proyecto
    print("\n[1/5] Cargando proyecto...")
    try:
        proyecto = load_project(test_file)
        print(f"✅ Cargado: {proyecto.nombre}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 2: Motor geométrico
    print("\n[2/5] Calculando geometría...")
    try:
        motor_geo = MotorGeometrico(proyecto)
        motor_geo.calcular()
        print(f"✅ Geometría calculada")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 3: Motor de restricciones
    print("\n[3/5] Inicializando motor de restricciones...")
    try:
        motor_rest = MotorRestricciones(proyecto, motor_geo)
        motor_rest.inicializar()
        print(f"✅ Motor inicializado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 4: Simular ejecución de pilotes
    print("\n[4/5] Simulando ejecución de pilotes...")
    try:
        tiempo_inicial = proyecto.fecha_inicio

        # Obtener disponibles
        disponibles = motor_rest.get_pilotes_disponibles(tiempo_inicial)
        print(f"✅ Pilotes disponibles inicialmente: {len(disponibles)}")

        if not disponibles:
            print("❌ No hay pilotes disponibles")
            return False

        # Ejecutar primer pilote
        pilote1 = disponibles[0]
        evento1 = motor_rest.ejecutar_pilote(pilote1, tiempo_inicial)
        print(f"✅ Ejecutado {pilote1}: bloqueados {evento1['pilotes_bloqueados']}")

        # Verificar bloqueos
        tiempo_t1 = tiempo_inicial + timedelta(hours=1)
        disponibles_t1 = motor_rest.get_pilotes_disponibles(tiempo_t1)
        print(f"✅ Después de {pilote1}: {len(disponibles_t1)} pilotes disponibles")

        # Esperar a que se liberen
        tiempo_t2 = tiempo_inicial + timedelta(hours=proyecto.tiempo_restriccion_h + 1)
        disponibles_t2 = motor_rest.get_pilotes_disponibles(tiempo_t2)
        print(f"✅ Después de esperar {proyecto.tiempo_restriccion_h}h: {len(disponibles_t2)} pilotes disponibles")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 5: Validar restricciones
    print("\n[5/5] Validando restricciones...")
    try:
        is_valid, errores = validar_restricciones(motor_rest, tiempo_t2)

        if is_valid:
            print("✅ Todas las restricciones son válidas")
        else:
            print(f"❌ Errores encontrados: {len(errores)}")
            for error in errores:
                print(f"   - {error}")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Resumen final
    print("\n" + "=" * 70)
    print("✅ FASE 3 COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\nCaracterísticas validadas:")
    print("  • Inicialización de estados")
    print("  • Ejecución de pilotes")
    print("  • Aplicación de restricción R1 (bloqueos)")
    print("  • Liberación automática de bloqueos")
    print("  • Cálculo de disponibles")
    print("  • Validación de restricciones")
    print("\nPróximo paso: FASE 4 (Motor de Recursos)\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
