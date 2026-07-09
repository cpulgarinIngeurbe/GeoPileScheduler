"""Validador de restricciones.

Responsabilidad: Verificar que las restricciones se cumplan correctamente.
"""

from datetime import datetime
from typing import List, Tuple

from src.core.enums import EstadoPilote
from src.constraints.engine import MotorRestricciones


def validar_restricciones(
    motor_restricciones: MotorRestricciones, tiempo_actual: datetime
) -> Tuple[bool, List[str]]:
    """Valida que todas las restricciones se cumplan.

    Args:
        motor_restricciones: MotorRestricciones para validar.
        tiempo_actual: Tiempo actual de simulación.

    Returns:
        Tupla (is_valid, errores).
    """
    errores: List[str] = []

    # V1: Validar transiciones de estado
    for pilote_id, estado in motor_restricciones.estado_manager.estados.items():
        if estado == EstadoPilote.EJECUTADO:
            # Validar que tiene bloqueos si vecinos existen
            vecinos = motor_restricciones.motor_geometrico.get_vecinos(pilote_id)
            if vecinos:
                for vecino_id in vecinos:
                    vecino_estado = motor_restricciones.estado_manager.get_estado(vecino_id)
                    # Vecino debe estar bloqueado o ejecutado
                    if vecino_estado not in [EstadoPilote.BLOQUEADO, EstadoPilote.EJECUTADO]:
                        errores.append(
                            f"Pilote {pilote_id} ejecutado pero vecino {vecino_id} no está bloqueado"
                        )

    # V2: Validar bloqueos activos
    for pilote_id in motor_restricciones.estado_manager.estados:
        bloqueos = motor_restricciones.estado_manager.get_bloqueos_activos(pilote_id, tiempo_actual)
        estado = motor_restricciones.estado_manager.get_estado(pilote_id)

        if bloqueos and estado != EstadoPilote.BLOQUEADO:
            errores.append(f"Pilote {pilote_id} tiene bloqueos pero estado es {estado.value}")

        if not bloqueos and estado == EstadoPilote.BLOQUEADO:
            errores.append(f"Pilote {pilote_id} está BLOQUEADO pero sin bloqueos activos")

    # V3: Validar disponibles
    disponibles = motor_restricciones.get_pilotes_disponibles(tiempo_actual)
    for pilote_id in disponibles:
        estado = motor_restricciones.estado_manager.get_estado(pilote_id)
        if estado not in [EstadoPilote.PENDIENTE, EstadoPilote.DISPONIBLE]:
            errores.append(f"Pilote {pilote_id} marcado disponible pero estado es {estado.value}")

    return (len(errores) == 0, errores)


def reporte_validacion(motor_restricciones: MotorRestricciones, tiempo_actual: datetime) -> str:
    """Genera reporte de validación legible.

    Args:
        motor_restricciones: Motor a validar.
        tiempo_actual: Tiempo actual.

    Returns:
        String con reporte.
    """
    is_valid, errores = validar_restricciones(motor_restricciones, tiempo_actual)

    reporte = f"""
Validación de Restricciones - {tiempo_actual.strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}
Estado: {'✅ VÁLIDO' if is_valid else '❌ INVÁLIDO'}

Errores encontrados: {len(errores)}
"""

    if errores:
        reporte += "\nDetalles:\n"
        for i, error in enumerate(errores, 1):
            reporte += f"  {i}. {error}\n"

    reporte += "=" * 60 + "\n"
    return reporte
