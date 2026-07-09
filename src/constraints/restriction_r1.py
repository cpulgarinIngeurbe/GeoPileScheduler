"""Aplicador de Restricción Geotécnica R1.

Responsabilidad: Cuando un pilote se ejecuta, bloquear todos sus vecinos
durante el tiempo mínimo de restricción.
"""

from datetime import datetime
from typing import List

from src.core.enums import EstadoPilote
from src.constraints.event_model import BloqueoGeotecnico
from src.constraints.pilote_state_manager import PiloteStateManager
from src.geometry.engine import MotorGeometrico
from src.core.models import Proyecto


def aplicar_restriccion_r1(
    pilote_ejecutado_id: str,
    motor_geometrico: MotorGeometrico,
    estado_manager: PiloteStateManager,
    proyecto: Proyecto,
    tiempo_ejecucion: datetime,
) -> List[str]:
    """Aplica restricción geotécnica R1 cuando se ejecuta un pilote.

    Restricción R1: Si D(p_i, p_j) ≤ R, entonces T_j - T_i ≥ H

    Cuando un pilote se ejecuta:
    1. Obtener todos sus vecinos (dentro del radio crítico)
    2. Para cada vecino:
       - Si está PENDIENTE o DISPONIBLE: bloquearlo
       - Cambiar su estado a BLOQUEADO
    3. Retornar lista de vecinos bloqueados

    Args:
        pilote_ejecutado_id: ID del pilote que acaba de ejecutarse.
        motor_geometrico: MotorGeometrico con geometría calculada.
        estado_manager: PiloteStateManager para actualizar estados.
        proyecto: Objeto Proyecto.
        tiempo_ejecucion: Datetime de ejecución (inicio del bloqueo).

    Returns:
        Lista de IDs de pilotes que fueron bloqueados.

    Raises:
        ValueError: Si pilote no existe o motor no está calculado.
    """
    # Validaciones
    if pilote_ejecutado_id not in estado_manager.estados:
        raise ValueError(f"Pilote '{pilote_ejecutado_id}' no existe")

    # Obtener vecinos del pilote que se acaba de ejecutar
    vecinos = motor_geometrico.get_vecinos(pilote_ejecutado_id)

    pilotes_bloqueados: List[str] = []

    # Procesar cada vecino
    for vecino_id in vecinos:
        # Obtener estado actual del vecino
        estado_vecino = estado_manager.get_estado(vecino_id)

        # Solo bloquear si está PENDIENTE o DISPONIBLE
        if estado_vecino in [EstadoPilote.PENDIENTE, EstadoPilote.DISPONIBLE]:
            # Crear bloqueo geotécnico
            bloqueo = BloqueoGeotecnico(
                pilote_id=vecino_id,
                pilote_que_bloquea_id=pilote_ejecutado_id,
                tiempo_inicio=tiempo_ejecucion,
                tiempo_restriccion_h=proyecto.tiempo_restriccion_h,
            )

            # Registrar bloqueo
            estado_manager.agregar_bloqueo(bloqueo)

            # Cambiar estado a BLOQUEADO
            estado_manager.set_estado(vecino_id, EstadoPilote.BLOQUEADO, tiempo_ejecucion)

            pilotes_bloqueados.append(vecino_id)

    return pilotes_bloqueados


def desbloquear_automaticamente(
    pilotes_bloqueados: List[str],
    estado_manager: PiloteStateManager,
    tiempo_actual: datetime,
) -> List[str]:
    """Desbloquea pilotes cuyo bloqueo ha expirado.

    Args:
        pilotes_bloqueados: Pilotes potencialmente desbloqueados.
        estado_manager: PiloteStateManager.
        tiempo_actual: Tiempo actual de simulación.

    Returns:
        Lista de IDs de pilotes efectivamente desbloqueados.
    """
    pilotes_desbloqueados: List[str] = []

    for pilote_id in pilotes_bloqueados:
        # Verificar si tiene bloqueos activos
        tiene_bloqueos = estado_manager.has_bloqueos_activos(pilote_id, tiempo_actual)

        if not tiene_bloqueos:
            # Cambiar estado a DISPONIBLE
            estado_actual = estado_manager.get_estado(pilote_id)
            if estado_actual == EstadoPilote.BLOQUEADO:
                estado_manager.set_estado(pilote_id, EstadoPilote.DISPONIBLE, tiempo_actual)
                pilotes_desbloqueados.append(pilote_id)

    return pilotes_desbloqueados
