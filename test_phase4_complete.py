#!/usr/bin/env python3
"""Script de validación completa para FASE 4 - Motor de Recursos."""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from src.io.loader import load_project
from src.geometry import MotorGeometrico
from src.resources import MotorRecursos


def main():
    print("\n" + "=" * 70)
    print("VALIDACIÓN COMPLETA DE FASE 4 - MOTOR DE RECURSOS")
    print("=" * 70)

    test_file = "data/input/caso_prueba_3.xlsx"

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

    # Paso 3: Motor de recursos
    print("\n[3/5] Inicializando motor de recursos...")
    try:
        motor_rec = MotorRecursos(proyecto, motor_geo)
        motor_rec.inicializar()
        print(f"✅ Motor inicializado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 4: Simular asignación de trabajo
    print("\n[4/5] Simulando asignación de trabajo...")
    try:
        tiempo_inicial = proyecto.fecha_inicio

        # Verificar equipos disponibles
        disponibles = motor_rec.get_equipos_disponibles()
        print(f"✅ Equipos disponibles: {disponibles}")

        if not disponibles:
            print("❌ No hay equipos disponibles")
            return False

        # Asignar trabajo
        equipo = disponibles[0]
        evento = motor_rec.asignar_trabajo(equipo, "P_001", tiempo_inicial)
        print(f"✅ Asignado {equipo} al pilote P_001")

        # Verificar que equipo está ocupado
        estado = motor_rec.get_estado_equipo(equipo)
        if not estado.esta_ocupado:
            print(f"❌ Equipo debería estar ocupado")
            return False

        print(f"✅ Equipo {equipo} está ocupado")

        # Finalizar trabajo
        tiempo_fin = tiempo_inicial + timedelta(hours=4)
        evento_fin = motor_rec.finalizar_trabajo(equipo, tiempo_fin)
        print(f"✅ Trabajo finalizado en {evento_fin['tiempo_ejecucion']}")

        # Verificar que equipo está libre
        estado = motor_rec.get_estado_equipo(equipo)
        if estado.esta_libre:
            print(f"✅ Equipo {equipo} está libre nuevamente")
        else:
            print(f"❌ Equipo debería estar libre")
            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Paso 5: Verificar estadísticas
    print("\n[5/5] Verificando estadísticas...")
    try:
        stats = motor_rec.get_estadisticas_equipos()
        print(f"✅ Estadísticas:")
        print(f"   • Equipos: {stats['num_equipos']}")
        print(f"   • Libres: {stats['equipos_libres']}")
        print(f"   • Ocupados: {stats['equipos_ocupados']}")
        print(f"   • Pilotes ejecutados: {stats['total_pilotes_ejecutados']}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    # Resumen final
    print("\n" + "=" * 70)
    print("✅ FASE 4 COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\nCaracterísticas validadas:")
    print("  • Inicialización de equipos")
    print("  • Asignación de trabajo")
    print("  • Finalización de trabajo")
    print("  • Gestión de estados")
    print("  • Cálculo de estadísticas")
    print("\nPróximo paso: FASE 5 (Motor de Simulación)\n")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
